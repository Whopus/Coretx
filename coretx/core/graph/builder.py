"""Graph builder for constructing code dependency graphs."""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import networkx as nx
import logging

from .types import NodeType, EdgeType, CodeNode, CodeEdge, GraphStats
from ...config import GraphConfig

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builds a code dependency graph from a repository."""
    
    def __init__(self, config: GraphConfig):
        self.config = config
        self.graph = nx.MultiDiGraph()
        self.node_counter = 0
        self.nodes: Dict[str, CodeNode] = {}
        self.edges: List[CodeEdge] = []
    
    def build_graph(self, repo_path: Path) -> nx.MultiDiGraph:
        """Build a complete dependency graph from repository."""
        logger.info(f"Building graph for repository: {repo_path}")
        
        # Reset state
        self.graph.clear()
        self.node_counter = 0
        self.nodes.clear()
        self.edges.clear()
        
        # Build directory structure
        self._build_directory_structure(repo_path)
        
        # Parse source files and extract entities
        self._parse_source_files(repo_path)
        
        # Add all nodes and edges to graph
        self._construct_networkx_graph()
        
        logger.info(f"Graph construction completed: {len(self.nodes)} nodes, {len(self.edges)} edges")
        return self.graph
    
    def _build_directory_structure(self, repo_path: Path) -> None:
        """Build directory and file nodes."""
        for root, dirs, files in os.walk(repo_path):
            root_path = Path(root)
            
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
            
            # Create directory node
            if root_path != repo_path:
                dir_node = self._create_node(
                    name=root_path.name,
                    node_type=NodeType.DIRECTORY,
                    path=root_path
                )
                
                # Add contains edge from parent directory
                parent_path = root_path.parent
                parent_id = self._get_node_id_by_path(parent_path)
                if parent_id:
                    self._add_edge(parent_id, dir_node.id, EdgeType.CONTAINS)
            
            # Create file nodes
            for file in files:
                if self._should_process_file(file):
                    file_path = root_path / file
                    file_node = self._create_node(
                        name=file,
                        node_type=NodeType.FILE,
                        path=file_path
                    )
                    
                    # Add contains edge from directory
                    dir_id = self._get_node_id_by_path(root_path)
                    if dir_id:
                        self._add_edge(dir_id, file_node.id, EdgeType.CONTAINS)
    
    def _parse_source_files(self, repo_path: Path) -> None:
        """Parse source files to extract classes and functions."""
        # Create a list of file nodes to avoid modifying dict during iteration
        file_nodes = [node for node in self.nodes.values() if node.is_file and node.path]
        
        for node in file_nodes:
            try:
                if node.path.suffix == '.py':
                    self._parse_python_file(node)
                elif node.path.suffix == '.js':
                    self._parse_javascript_file(node)
                # Add more parsers for other languages as needed
            except Exception as e:
                logger.warning(f"Failed to parse {node.path}: {e}")
    
    def _parse_python_file(self, file_node: CodeNode) -> None:
        """Parse a single Python file."""
        try:
            with open(file_node.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle edge cases in code
            content = self._handle_code_edge_cases(content)
            tree = ast.parse(content)
            
            # Extract classes and functions
            visitor = CodeVisitor(file_node.id, self)
            visitor.visit(tree)
            
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning(f"Cannot parse {file_node.path}: {e}")
    
    def _parse_javascript_file(self, file_node: CodeNode) -> None:
        """Parse a single JavaScript file."""
        try:
            with open(file_node.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract functions and classes using regex patterns
            self._extract_js_functions(file_node, content)
            self._extract_js_classes(file_node, content)
            
        except (UnicodeDecodeError, IOError) as e:
            logger.warning(f"Cannot parse {file_node.path}: {e}")
    
    def _extract_js_functions(self, file_node: CodeNode, content: str) -> None:
        """Extract JavaScript functions using regex."""
        lines = content.split('\n')
        
        # Pattern for function declarations
        function_patterns = [
            r'^\s*function\s+(\w+)\s*\(',  # function name()
            r'^\s*const\s+(\w+)\s*=\s*function\s*\(',  # const name = function()
            r'^\s*let\s+(\w+)\s*=\s*function\s*\(',  # let name = function()
            r'^\s*var\s+(\w+)\s*=\s*function\s*\(',  # var name = function()
            r'^\s*(\w+)\s*:\s*function\s*\(',  # name: function() (object method)
            r'^\s*(\w+)\s*\([^)]*\)\s*{',  # name() { (arrow function style)
            r'^\s*const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',  # const name = () => {
            r'^\s*let\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',  # let name = () => {
            r'^\s*var\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',  # var name = () => {
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in function_patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    
                    # Find function end (simplified - just look for closing brace)
                    end_line = self._find_js_block_end(lines, line_num - 1)
                    
                    # Create function node
                    func_node = self._create_node(
                        name=func_name,
                        node_type=NodeType.FUNCTION,
                        path=file_node.path,
                        line_start=line_num,
                        line_end=end_line,
                        metadata={'language': 'javascript'}
                    )
                    
                    # Add contains edge from file
                    self._add_edge(file_node.id, func_node.id, EdgeType.CONTAINS)
                    break
    
    def _extract_js_classes(self, file_node: CodeNode, content: str) -> None:
        """Extract JavaScript classes using regex."""
        lines = content.split('\n')
        
        # Pattern for class declarations
        class_pattern = r'^\s*class\s+(\w+)'
        
        for line_num, line in enumerate(lines, 1):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                
                # Find class end
                end_line = self._find_js_block_end(lines, line_num - 1)
                
                # Create class node
                class_node = self._create_node(
                    name=class_name,
                    node_type=NodeType.CLASS,
                    path=file_node.path,
                    line_start=line_num,
                    line_end=end_line,
                    metadata={'language': 'javascript'}
                )
                
                # Add contains edge from file
                self._add_edge(file_node.id, class_node.id, EdgeType.CONTAINS)
                
                # Extract methods within the class
                self._extract_js_class_methods(class_node, lines, line_num - 1, end_line)
    
    def _extract_js_class_methods(self, class_node: CodeNode, lines: List[str], 
                                 start_line: int, end_line: int) -> None:
        """Extract methods from a JavaScript class."""
        method_patterns = [
            r'^\s*(\w+)\s*\([^)]*\)\s*{',  # methodName() {
            r'^\s*static\s+(\w+)\s*\([^)]*\)\s*{',  # static methodName() {
            r'^\s*async\s+(\w+)\s*\([^)]*\)\s*{',  # async methodName() {
            r'^\s*get\s+(\w+)\s*\(\s*\)\s*{',  # get propertyName() {
            r'^\s*set\s+(\w+)\s*\([^)]*\)\s*{',  # set propertyName() {
        ]
        
        for line_num in range(start_line + 1, min(end_line, len(lines))):
            line = lines[line_num]
            for pattern in method_patterns:
                match = re.search(pattern, line)
                if match:
                    method_name = match.group(1)
                    
                    # Skip constructor as it's not a regular method
                    if method_name == 'constructor':
                        continue
                    
                    # Find method end
                    method_end = self._find_js_block_end(lines, line_num)
                    
                    # Create method node
                    method_node = self._create_node(
                        name=method_name,
                        node_type=NodeType.FUNCTION,
                        path=class_node.path,
                        line_start=line_num + 1,
                        line_end=method_end,
                        metadata={'language': 'javascript', 'is_method': True}
                    )
                    
                    # Add contains edge from class
                    self._add_edge(class_node.id, method_node.id, EdgeType.CONTAINS)
                    break
    
    def _find_js_block_end(self, lines: List[str], start_line: int) -> int:
        """Find the end of a JavaScript block (simplified brace matching)."""
        brace_count = 0
        found_opening = False
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening = True
                elif char == '}':
                    brace_count -= 1
                    if found_opening and brace_count == 0:
                        return i + 1
        
        # If we can't find the end, return a reasonable estimate
        return min(start_line + 20, len(lines))
    
    def _handle_code_edge_cases(self, code: str) -> str:
        """Handle common parsing edge cases."""
        # Remove BOM
        code = code.replace('\ufeff', '')
        
        # Fix common syntax issues
        code = re.sub(r'except\s+([^,\s]+)\s*,\s*([^:]+):', r'except \1 as \2:', code)
        
        return code
    
    def _create_node(self, name: str, node_type: NodeType, 
                    path: Optional[Path] = None,
                    line_start: Optional[int] = None,
                    line_end: Optional[int] = None,
                    metadata: Optional[Dict] = None) -> CodeNode:
        """Create a new node."""
        node_id = f"{node_type.value}_{self.node_counter}"
        self.node_counter += 1
        
        node = CodeNode(
            id=node_id,
            name=name,
            node_type=node_type,
            path=path,
            line_start=line_start,
            line_end=line_end,
            metadata=metadata or {}
        )
        
        self.nodes[node_id] = node
        return node
    
    def _add_edge(self, source_id: str, target_id: str, edge_type: EdgeType,
                 metadata: Optional[Dict] = None) -> None:
        """Add an edge between nodes."""
        edge = CodeEdge(
            source=source_id,
            target=target_id,
            edge_type=edge_type,
            metadata=metadata or {}
        )
        self.edges.append(edge)
    
    def _get_node_id_by_path(self, path: Path) -> Optional[str]:
        """Get node ID by path."""
        for node_id, node in self.nodes.items():
            if node.path == path:
                return node_id
        return None
    
    def _should_skip_dir(self, dirname: str) -> bool:
        """Check if directory should be skipped."""
        return any(skip in dirname for skip in self.config.skip_dirs)
    
    def _should_process_file(self, filename: str) -> bool:
        """Check if file should be processed."""
        return any(filename.endswith(ext) for ext in self.config.file_extensions)
    
    def _construct_networkx_graph(self) -> None:
        """Construct NetworkX graph from nodes and edges."""
        # Add nodes
        for node in self.nodes.values():
            self.graph.add_node(
                node.id,
                name=node.name,
                type=node.node_type.value,
                path=str(node.path) if node.path else None,
                line_start=node.line_start,
                line_end=node.line_end,
                **node.metadata
            )
        
        # Add edges
        for edge in self.edges:
            self.graph.add_edge(
                edge.source,
                edge.target,
                type=edge.edge_type.value,
                **edge.metadata
            )
    
    def get_stats(self) -> GraphStats:
        """Get graph statistics."""
        node_counts = {nt: 0 for nt in NodeType}
        edge_counts = {et: 0 for et in EdgeType}
        
        for node in self.nodes.values():
            node_counts[node.node_type] += 1
        
        for edge in self.edges:
            edge_counts[edge.edge_type] += 1
        
        # Calculate max depth (simplified)
        max_depth = 0
        for node in self.nodes.values():
            if node.path:
                depth = len(node.path.parts)
                max_depth = max(max_depth, depth)
        
        return GraphStats(
            total_nodes=len(self.nodes),
            total_edges=len(self.edges),
            node_counts=node_counts,
            edge_counts=edge_counts,
            max_depth=max_depth
        )


class CodeVisitor(ast.NodeVisitor):
    """AST visitor for extracting code entities."""
    
    def __init__(self, file_node_id: str, builder: GraphBuilder):
        self.file_node_id = file_node_id
        self.builder = builder
        self.current_class = None
        self.imports = []
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        class_node = self.builder._create_node(
            name=node.name,
            node_type=NodeType.CLASS,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            metadata={'docstring': ast.get_docstring(node)}
        )
        
        # Add contains edge from file
        self.builder._add_edge(self.file_node_id, class_node.id, EdgeType.CONTAINS)
        
        # Add inheritance edges
        for base in node.bases:
            if isinstance(base, ast.Name):
                # Find base class node (simplified)
                base_class_id = self._find_class_by_name(base.id)
                if base_class_id:
                    self.builder._add_edge(class_node.id, base_class_id, EdgeType.INHERITS)
        
        # Visit class body
        old_class = self.current_class
        self.current_class = class_node.id
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        func_node = self.builder._create_node(
            name=node.name,
            node_type=NodeType.FUNCTION,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            metadata={
                'docstring': ast.get_docstring(node),
                'args': [arg.arg for arg in node.args.args]
            }
        )
        
        # Add contains edge from file or class
        parent_id = self.current_class or self.file_node_id
        self.builder._add_edge(parent_id, func_node.id, EdgeType.CONTAINS)
        
        # Extract function calls (simplified)
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                called_func_id = self._find_function_by_name(child.func.id)
                if called_func_id:
                    self.builder._add_edge(func_node.id, called_func_id, EdgeType.INVOKES)
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement."""
        for alias in node.names:
            self.imports.append(alias.name)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from import statement."""
        if node.module:
            for alias in node.names:
                imported_name = f"{node.module}.{alias.name}"
                self.imports.append(imported_name)
    
    def _find_class_by_name(self, name: str) -> Optional[str]:
        """Find class node by name (simplified)."""
        for node_id, node in self.builder.nodes.items():
            if node.is_class and node.name == name:
                return node_id
        return None
    
    def _find_function_by_name(self, name: str) -> Optional[str]:
        """Find function node by name (simplified)."""
        for node_id, node in self.builder.nodes.items():
            if node.is_function and node.name == name:
                return node_id
        return None