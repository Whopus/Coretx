"""Tools for code localization agents."""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

from ..graph import GraphSearcher, NodeType
from ..retrieval import HybridRetriever
from ..agent import ToolRegistry

logger = logging.getLogger(__name__)


def setup_localization_tools(registry: ToolRegistry, 
                           graph_searcher: GraphSearcher,
                           retriever: HybridRetriever,
                           repo_path: Path) -> None:
    """Setup all localization tools in the registry."""
    
    @registry.register("search_code", "Search for code entities using text or structural queries", "search")
    def search_code(query: str, search_type: str = "hybrid", top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for code entities using various methods.
        
        Args:
            query: Search query string
            search_type: Type of search - "hybrid", "text", "graph", or "structure"
            top_k: Maximum number of results to return
            
        Returns:
            List of search results with entity information
        """
        try:
            results = retriever.search(query, search_type, top_k)
            
            # Format results for better readability
            formatted_results = []
            for result in results:
                node_info = result['node_info']
                attrs = node_info['attributes']
                
                formatted_result = {
                    'entity_id': result['node_id'],
                    'name': attrs.get('name', 'Unknown'),
                    'type': attrs.get('type', 'Unknown'),
                    'path': attrs.get('path', ''),
                    'score': result['score'],
                    'search_method': result['search_type'],
                    'line_range': f"{attrs.get('line_start', '')}-{attrs.get('line_end', '')}" if attrs.get('line_start') else None
                }
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in search_code: {e}")
            return [{"error": str(e)}]
    
    @registry.register("get_entity_details", "Get detailed information about a specific code entity", "analysis")
    def get_entity_details(entity_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a code entity.
        
        Args:
            entity_id: ID of the entity to analyze
            
        Returns:
            Detailed entity information including relationships
        """
        try:
            node_info = graph_searcher.get_node_info(entity_id)
            if not node_info:
                return {"error": f"Entity {entity_id} not found"}
            
            attrs = node_info['attributes']
            
            # Format the response
            details = {
                'entity_id': entity_id,
                'name': attrs.get('name', 'Unknown'),
                'type': attrs.get('type', 'Unknown'),
                'path': attrs.get('path', ''),
                'line_range': {
                    'start': attrs.get('line_start'),
                    'end': attrs.get('line_end')
                },
                'docstring': attrs.get('docstring', ''),
                'dependencies': node_info.get('dependencies', {}),
                'dependents': node_info.get('dependents', {}),
                'contained_entities': node_info.get('contained_entities', []),
                'container': node_info.get('container')
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error in get_entity_details: {e}")
            return {"error": str(e)}
    
    @registry.register("search_by_type", "Search for entities of a specific type", "search")
    def search_by_type(entity_type: str, name_filter: str = "", top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Search for entities of a specific type.
        
        Args:
            entity_type: Type of entity - "file", "class", "function", or "directory"
            name_filter: Optional name filter to narrow results
            top_k: Maximum number of results
            
        Returns:
            List of entities of the specified type
        """
        try:
            results = retriever.search_by_entity_type(entity_type, name_filter, top_k)
            
            formatted_results = []
            for result in results:
                node_info = result['node_info']
                attrs = node_info['attributes']
                
                formatted_result = {
                    'entity_id': result['node_id'],
                    'name': attrs.get('name', 'Unknown'),
                    'type': attrs.get('type', 'Unknown'),
                    'path': attrs.get('path', ''),
                    'score': result['score']
                }
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in search_by_type: {e}")
            return [{"error": str(e)}]
    
    @registry.register("get_file_content", "Get the content of a source file", "content")
    def get_file_content(file_path: str, start_line: int = 1, end_line: int = -1) -> Dict[str, Any]:
        """
        Get the content of a source file.
        
        Args:
            file_path: Path to the file (relative to repository root)
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (-1 for end of file)
            
        Returns:
            File content and metadata
        """
        try:
            # Resolve file path
            if Path(file_path).is_absolute():
                full_path = Path(file_path)
            else:
                full_path = repo_path / file_path
            
            if not full_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply line range
            if end_line == -1:
                end_line = len(lines)
            
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            
            selected_lines = lines[start_idx:end_idx]
            
            return {
                'file_path': file_path,
                'total_lines': len(lines),
                'start_line': start_line,
                'end_line': end_idx,
                'content': ''.join(selected_lines),
                'line_numbers': list(range(start_line, end_idx + 1))
            }
            
        except Exception as e:
            logger.error(f"Error in get_file_content: {e}")
            return {"error": str(e)}
    
    @registry.register("get_function_definition", "Get the definition of a specific function", "content")
    def get_function_definition(function_name: str, file_path: str = "") -> Dict[str, Any]:
        """
        Get the definition of a specific function.
        
        Args:
            function_name: Name of the function
            file_path: Optional file path to narrow search
            
        Returns:
            Function definition and metadata
        """
        try:
            # Search for function
            if file_path:
                # Search within specific file
                file_entities = graph_searcher.get_file_entities(file_path)
                function_nodes = []
                for entity_id in file_entities:
                    node_info = graph_searcher.get_node_info(entity_id)
                    if (node_info and 
                        node_info['attributes'].get('type') == 'function' and
                        node_info['attributes'].get('name') == function_name):
                        function_nodes.append(entity_id)
            else:
                # Global search
                function_nodes = graph_searcher.search_by_name(function_name, NodeType.FUNCTION)
            
            if not function_nodes:
                return {"error": f"Function '{function_name}' not found"}
            
            # Get details for the first match
            function_id = function_nodes[0]
            node_info = graph_searcher.get_node_info(function_id)
            attrs = node_info['attributes']
            
            # Get function content
            func_file_path = attrs.get('path', '')
            start_line = attrs.get('line_start')
            end_line = attrs.get('line_end')
            
            content_result = get_file_content(func_file_path, start_line or 1, end_line or -1)
            
            return {
                'function_name': function_name,
                'entity_id': function_id,
                'file_path': func_file_path,
                'line_range': {'start': start_line, 'end': end_line},
                'docstring': attrs.get('docstring', ''),
                'arguments': attrs.get('args', []),
                'definition': content_result.get('content', ''),
                'dependencies': node_info.get('dependencies', {}),
                'multiple_matches': len(function_nodes) > 1,
                'total_matches': len(function_nodes)
            }
            
        except Exception as e:
            logger.error(f"Error in get_function_definition: {e}")
            return {"error": str(e)}
    
    @registry.register("get_class_definition", "Get the definition of a specific class", "content")
    def get_class_definition(class_name: str, file_path: str = "") -> Dict[str, Any]:
        """
        Get the definition of a specific class.
        
        Args:
            class_name: Name of the class
            file_path: Optional file path to narrow search
            
        Returns:
            Class definition and metadata
        """
        try:
            # Search for class
            if file_path:
                file_entities = graph_searcher.get_file_entities(file_path)
                class_nodes = []
                for entity_id in file_entities:
                    node_info = graph_searcher.get_node_info(entity_id)
                    if (node_info and 
                        node_info['attributes'].get('type') == 'class' and
                        node_info['attributes'].get('name') == class_name):
                        class_nodes.append(entity_id)
            else:
                class_nodes = graph_searcher.search_by_name(class_name, NodeType.CLASS)
            
            if not class_nodes:
                return {"error": f"Class '{class_name}' not found"}
            
            # Get details for the first match
            class_id = class_nodes[0]
            node_info = graph_searcher.get_node_info(class_id)
            attrs = node_info['attributes']
            
            # Get class methods
            contained_entities = node_info.get('contained_entities', [])
            methods = []
            for entity_id in contained_entities:
                method_info = graph_searcher.get_node_info(entity_id)
                if method_info and method_info['attributes'].get('type') == 'function':
                    methods.append({
                        'name': method_info['attributes'].get('name'),
                        'entity_id': entity_id,
                        'line_start': method_info['attributes'].get('line_start')
                    })
            
            # Get class content
            class_file_path = attrs.get('path', '')
            start_line = attrs.get('line_start')
            end_line = attrs.get('line_end')
            
            content_result = get_file_content(class_file_path, start_line or 1, end_line or -1)
            
            return {
                'class_name': class_name,
                'entity_id': class_id,
                'file_path': class_file_path,
                'line_range': {'start': start_line, 'end': end_line},
                'docstring': attrs.get('docstring', ''),
                'methods': methods,
                'definition': content_result.get('content', ''),
                'dependencies': node_info.get('dependencies', {}),
                'dependents': node_info.get('dependents', {}),
                'multiple_matches': len(class_nodes) > 1,
                'total_matches': len(class_nodes)
            }
            
        except Exception as e:
            logger.error(f"Error in get_class_definition: {e}")
            return {"error": str(e)}
    
    @registry.register("find_related_entities", "Find entities related to a given entity", "analysis")
    def find_related_entities(entity_id: str, relation_type: str = "all", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Find entities related to a given entity.
        
        Args:
            entity_id: ID of the source entity
            relation_type: Type of relationship - "all", "dependencies", "dependents", "contained", "container"
            max_results: Maximum number of results
            
        Returns:
            List of related entities
        """
        try:
            results = retriever.find_related_entities(entity_id, relation_type)
            
            formatted_results = []
            for result in results[:max_results]:
                node_info = result['node_info']
                attrs = node_info['attributes']
                
                formatted_result = {
                    'entity_id': result['node_id'],
                    'name': attrs.get('name', 'Unknown'),
                    'type': attrs.get('type', 'Unknown'),
                    'path': attrs.get('path', ''),
                    'relationship': relation_type
                }
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in find_related_entities: {e}")
            return [{"error": str(e)}]
    
    @registry.register("list_files", "List files in the repository", "navigation")
    def list_files(directory: str = "", file_extension: str = ".py", max_results: int = 50) -> List[Dict[str, Any]]:
        """
        List files in the repository.
        
        Args:
            directory: Directory to search in (relative to repo root)
            file_extension: File extension filter
            max_results: Maximum number of files to return
            
        Returns:
            List of files with metadata
        """
        try:
            search_path = repo_path / directory if directory else repo_path
            
            if not search_path.exists():
                return [{"error": f"Directory not found: {directory}"}]
            
            files = []
            for file_path in search_path.rglob(f"*{file_extension}"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(repo_path)
                    
                    # Get file stats
                    stat = file_path.stat()
                    
                    files.append({
                        'name': file_path.name,
                        'path': str(relative_path),
                        'size': stat.st_size,
                        'directory': str(relative_path.parent),
                        'extension': file_path.suffix
                    })
                    
                    if len(files) >= max_results:
                        break
            
            return files
            
        except Exception as e:
            logger.error(f"Error in list_files: {e}")
            return [{"error": str(e)}]
    
    @registry.register("analyze_dependencies", "Analyze dependencies for an entity", "analysis")
    def analyze_dependencies(entity_id: str) -> Dict[str, Any]:
        """
        Analyze dependencies for a code entity.
        
        Args:
            entity_id: ID of the entity to analyze
            
        Returns:
            Dependency analysis results
        """
        try:
            node_info = graph_searcher.get_node_info(entity_id)
            if not node_info:
                return {"error": f"Entity {entity_id} not found"}
            
            dependencies = node_info.get('dependencies', {})
            dependents = node_info.get('dependents', {})
            
            # Get detailed info for dependencies
            detailed_deps = {}
            for dep_type, dep_list in dependencies.items():
                detailed_deps[dep_type] = []
                for dep_id in dep_list:
                    dep_info = graph_searcher.get_node_info(dep_id)
                    if dep_info:
                        detailed_deps[dep_type].append({
                            'entity_id': dep_id,
                            'name': dep_info['attributes'].get('name'),
                            'type': dep_info['attributes'].get('type'),
                            'path': dep_info['attributes'].get('path')
                        })
            
            # Get detailed info for dependents
            detailed_dependents = {}
            for dep_type, dep_list in dependents.items():
                detailed_dependents[dep_type] = []
                for dep_id in dep_list:
                    dep_info = graph_searcher.get_node_info(dep_id)
                    if dep_info:
                        detailed_dependents[dep_type].append({
                            'entity_id': dep_id,
                            'name': dep_info['attributes'].get('name'),
                            'type': dep_info['attributes'].get('type'),
                            'path': dep_info['attributes'].get('path')
                        })
            
            return {
                'entity_id': entity_id,
                'entity_name': node_info['attributes'].get('name'),
                'dependencies': detailed_deps,
                'dependents': detailed_dependents,
                'dependency_count': sum(len(deps) for deps in dependencies.values()),
                'dependent_count': sum(len(deps) for deps in dependents.values())
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_dependencies: {e}")
            return {"error": str(e)}