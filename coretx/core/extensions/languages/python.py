"""
Python language parser for extracting code entities.
"""

import ast
import os
import re
from typing import List, Set
import logging

from ..base import CodeParser, ParseResult, EntityType

logger = logging.getLogger(__name__)


class PythonParser(CodeParser):
    """Parser for Python files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.py', '.pyw', '.pyi'}
        self.language_name = "Python"
        self.parser_version = "1.0.0"
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this is a Python file."""
        if os.path.isdir(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
    
    def parse_file(self, file_path: str) -> List[ParseResult]:
        """Parse a Python file and extract entities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with AST
            tree = ast.parse(content, filename=file_path)
            
            results = []
            
            # Add file entity
            file_result = ParseResult(
                name=os.path.basename(file_path),
                entity_type=EntityType.FILE,
                file_path=file_path,
                line_start=1,
                line_end=len(content.splitlines()),
                content=content[:500] + "..." if len(content) > 500 else content,
                metadata={'language': 'python', 'size': len(content)}
            )
            results.append(file_result)
            
            # Extract entities using AST visitor
            visitor = PythonASTVisitor(file_path, content.splitlines())
            visitor.visit(tree)
            results.extend(visitor.results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing Python file {file_path}: {e}")
            return []
    
    def extract_dependencies(self, file_path: str) -> List[str]:
        """Extract Python imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            return imports
            
        except Exception as e:
            logger.error(f"Error extracting dependencies from {file_path}: {e}")
            return []


class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor for extracting Python entities."""
    
    def __init__(self, file_path: str, lines: List[str]):
        self.file_path = file_path
        self.lines = lines
        self.results: List[ParseResult] = []
        self.current_class = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        docstring = self._get_docstring(node)
        
        result = ParseResult(
            name=node.name,
            entity_type=EntityType.CLASS,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=self._get_end_line(node),
            content=self._get_node_content(node),
            docstring=docstring,
            metadata={
                'bases': [self._get_name(base) for base in node.bases],
                'decorators': [self._get_name(dec) for dec in node.decorator_list]
            }
        )
        
        self.results.append(result)
        
        # Visit class methods
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        docstring = self._get_docstring(node)
        
        entity_type = EntityType.METHOD if self.current_class else EntityType.FUNCTION
        
        result = ParseResult(
            name=node.name,
            entity_type=entity_type,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=self._get_end_line(node),
            content=self._get_node_content(node),
            docstring=docstring,
            metadata={
                'args': [arg.arg for arg in node.args.args],
                'decorators': [self._get_name(dec) for dec in node.decorator_list],
                'class': self.current_class
            }
        )
        
        self.results.append(result)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        # Treat async functions the same as regular functions
        self.visit_FunctionDef(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Simple variable assignment
                result = ParseResult(
                    name=target.id,
                    entity_type=EntityType.VARIABLE,
                    file_path=self.file_path,
                    line_start=node.lineno,
                    line_end=node.lineno,
                    content=self._get_node_content(node),
                    metadata={
                        'class': self.current_class,
                        'type': self._infer_type(node.value)
                    }
                )
                self.results.append(result)
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for alias in node.names:
            result = ParseResult(
                name=alias.name,
                entity_type=EntityType.IMPORT,
                file_path=self.file_path,
                line_start=node.lineno,
                line_end=node.lineno,
                content=self._get_node_content(node),
                metadata={
                    'alias': alias.asname,
                    'type': 'import'
                }
            )
            self.results.append(result)
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from-import statements."""
        module = node.module or ''
        
        for alias in node.names:
            result = ParseResult(
                name=f"{module}.{alias.name}" if module else alias.name,
                entity_type=EntityType.IMPORT,
                file_path=self.file_path,
                line_start=node.lineno,
                line_end=node.lineno,
                content=self._get_node_content(node),
                metadata={
                    'module': module,
                    'name': alias.name,
                    'alias': alias.asname,
                    'type': 'from_import'
                }
            )
            self.results.append(result)
        
        self.generic_visit(node)
    
    def _get_docstring(self, node) -> str:
        """Extract docstring from a node."""
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return None
    
    def _get_end_line(self, node) -> int:
        """Get the end line of a node."""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno
        
        # Fallback: estimate based on body
        if hasattr(node, 'body') and node.body:
            last_node = node.body[-1]
            return self._get_end_line(last_node)
        
        return node.lineno
    
    def _get_node_content(self, node) -> str:
        """Get the source code content of a node."""
        try:
            start_line = node.lineno - 1
            end_line = self._get_end_line(node)
            
            if start_line < len(self.lines) and end_line <= len(self.lines):
                content_lines = self.lines[start_line:end_line]
                content = '\n'.join(content_lines)
                
                # Truncate if too long
                if len(content) > 1000:
                    content = content[:1000] + "..."
                
                return content
        except:
            pass
        
        return ""
    
    def _get_name(self, node) -> str:
        """Get the name from various node types."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return str(node)
    
    def _infer_type(self, node) -> str:
        """Infer the type of a value node."""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.Set):
            return "set"
        elif isinstance(node, ast.Tuple):
            return "tuple"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        else:
            return "unknown"