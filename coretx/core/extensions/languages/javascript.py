"""
JavaScript language parser for extracting code entities.
"""

import os
import re
from typing import List, Set, Dict, Any
import logging

from ..base import CodeParser, ParseResult, EntityType

logger = logging.getLogger(__name__)


class JavaScriptParser(CodeParser):
    """Parser for JavaScript files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.js', '.jsx', '.ts', '.tsx', '.mjs'}
        self.language_name = "JavaScript"
        self.parser_version = "1.0.0"
        
        # Regex patterns for JavaScript parsing
        self.patterns = {
            'class': re.compile(r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{', re.MULTILINE),
            'function': re.compile(r'(?:function\s+(\w+)|(\w+)\s*:\s*function|(\w+)\s*=\s*function)\s*\([^)]*\)\s*{', re.MULTILINE),
            'arrow_function': re.compile(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]+)\s*=>\s*{?', re.MULTILINE),
            'method': re.compile(r'(\w+)\s*\([^)]*\)\s*{', re.MULTILINE),
            'variable': re.compile(r'(?:const|let|var)\s+(\w+)(?:\s*=\s*[^;]+)?;?', re.MULTILINE),
            'import': re.compile(r'import\s+(?:{[^}]+}|\w+|[^}]+)\s+from\s+["\']([^"\']+)["\']', re.MULTILINE),
            'require': re.compile(r'(?:const|let|var)\s+\w+\s*=\s*require\(["\']([^"\']+)["\']\)', re.MULTILINE),
            'export': re.compile(r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)', re.MULTILINE),
        }
        
        # Control structures to filter out
        self.control_structures = {
            'if', 'else', 'while', 'for', 'switch', 'case', 'default',
            'try', 'catch', 'finally', 'do', 'break', 'continue', 'return'
        }
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this is a JavaScript file."""
        if os.path.isdir(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
    
    def parse_file(self, file_path: str) -> List[ParseResult]:
        """Parse a JavaScript file and extract entities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            results = []
            lines = content.splitlines()
            
            # Add file entity
            file_result = ParseResult(
                name=os.path.basename(file_path),
                entity_type=EntityType.FILE,
                file_path=file_path,
                line_start=1,
                line_end=len(lines),
                content=content[:500] + "..." if len(content) > 500 else content,
                metadata={'language': 'javascript', 'size': len(content)}
            )
            results.append(file_result)
            
            # Extract different types of entities
            results.extend(self._extract_classes(content, file_path, lines))
            results.extend(self._extract_functions(content, file_path, lines))
            results.extend(self._extract_variables(content, file_path, lines))
            results.extend(self._extract_imports(content, file_path, lines))
            results.extend(self._extract_exports(content, file_path, lines))
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing JavaScript file {file_path}: {e}")
            return []
    
    def extract_dependencies(self, file_path: str) -> List[str]:
        """Extract JavaScript imports and requires."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Extract ES6 imports
            import_matches = self.patterns['import'].findall(content)
            dependencies.extend(import_matches)
            
            # Extract CommonJS requires
            require_matches = self.patterns['require'].findall(content)
            dependencies.extend(require_matches)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Error extracting dependencies from {file_path}: {e}")
            return []
    
    def _extract_classes(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract class definitions."""
        results = []
        
        for match in self.patterns['class'].finditer(content):
            class_name = match.group(1)
            extends_class = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            # Find class end
            end_line = self._find_block_end(content, match.end(), lines, line_num)
            
            result = ParseResult(
                name=class_name,
                entity_type=EntityType.CLASS,
                file_path=file_path,
                line_start=line_num,
                line_end=end_line,
                content=self._get_content_range(lines, line_num, end_line),
                metadata={
                    'extends': extends_class,
                    'language': 'javascript'
                }
            )
            results.append(result)
        
        return results
    
    def _extract_functions(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract function definitions."""
        results = []
        
        # Regular functions
        for match in self.patterns['function'].finditer(content):
            func_name = match.group(1) or match.group(2) or match.group(3)
            if not func_name or func_name in self.control_structures:
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            end_line = self._find_block_end(content, match.end(), lines, line_num)
            
            result = ParseResult(
                name=func_name,
                entity_type=EntityType.FUNCTION,
                file_path=file_path,
                line_start=line_num,
                line_end=end_line,
                content=self._get_content_range(lines, line_num, end_line),
                metadata={'type': 'function', 'language': 'javascript'}
            )
            results.append(result)
        
        # Arrow functions
        for match in self.patterns['arrow_function'].finditer(content):
            func_name = match.group(1)
            if not func_name or func_name in self.control_structures:
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            end_line = self._find_arrow_function_end(content, match.end(), lines, line_num)
            
            result = ParseResult(
                name=func_name,
                entity_type=EntityType.FUNCTION,
                file_path=file_path,
                line_start=line_num,
                line_end=end_line,
                content=self._get_content_range(lines, line_num, end_line),
                metadata={'type': 'arrow_function', 'language': 'javascript'}
            )
            results.append(result)
        
        return results
    
    def _extract_variables(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract variable declarations."""
        results = []
        
        for match in self.patterns['variable'].finditer(content):
            var_name = match.group(1)
            if not var_name or var_name in self.control_structures:
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            
            result = ParseResult(
                name=var_name,
                entity_type=EntityType.VARIABLE,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=lines[line_num - 1] if line_num <= len(lines) else "",
                metadata={'language': 'javascript'}
            )
            results.append(result)
        
        return results
    
    def _extract_imports(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract import statements."""
        results = []
        
        # ES6 imports
        for match in self.patterns['import'].finditer(content):
            import_path = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            result = ParseResult(
                name=import_path,
                entity_type=EntityType.IMPORT,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=lines[line_num - 1] if line_num <= len(lines) else "",
                metadata={'type': 'es6_import', 'language': 'javascript'}
            )
            results.append(result)
        
        # CommonJS requires
        for match in self.patterns['require'].finditer(content):
            require_path = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            result = ParseResult(
                name=require_path,
                entity_type=EntityType.IMPORT,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=lines[line_num - 1] if line_num <= len(lines) else "",
                metadata={'type': 'commonjs_require', 'language': 'javascript'}
            )
            results.append(result)
        
        return results
    
    def _extract_exports(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract export statements."""
        results = []
        
        for match in self.patterns['export'].finditer(content):
            export_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            result = ParseResult(
                name=export_name,
                entity_type=EntityType.MODULE,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=lines[line_num - 1] if line_num <= len(lines) else "",
                metadata={'type': 'export', 'language': 'javascript'}
            )
            results.append(result)
        
        return results
    
    def _find_block_end(self, content: str, start_pos: int, lines: List[str], start_line: int) -> int:
        """Find the end of a code block."""
        brace_count = 0
        pos = start_pos
        
        while pos < len(content):
            char = content[pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return content[:pos].count('\n') + 1
            pos += 1
        
        return min(start_line + 10, len(lines))  # Fallback
    
    def _find_arrow_function_end(self, content: str, start_pos: int, lines: List[str], start_line: int) -> int:
        """Find the end of an arrow function."""
        # Check if it's a single expression or block
        remaining = content[start_pos:].strip()
        
        if remaining.startswith('{'):
            return self._find_block_end(content, start_pos, lines, start_line)
        else:
            # Single expression, find the end of the line or semicolon
            semicolon_pos = content.find(';', start_pos)
            newline_pos = content.find('\n', start_pos)
            
            if semicolon_pos != -1 and (newline_pos == -1 or semicolon_pos < newline_pos):
                return content[:semicolon_pos].count('\n') + 1
            elif newline_pos != -1:
                return content[:newline_pos].count('\n') + 1
            else:
                return start_line
    
    def _get_content_range(self, lines: List[str], start_line: int, end_line: int) -> str:
        """Get content for a range of lines."""
        try:
            if start_line <= len(lines) and end_line <= len(lines):
                content_lines = lines[start_line - 1:end_line]
                content = '\n'.join(content_lines)
                
                # Truncate if too long
                if len(content) > 1000:
                    content = content[:1000] + "..."
                
                return content
        except:
            pass
        
        return ""