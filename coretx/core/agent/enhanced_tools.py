"""
Enhanced tools for Coretx agents using the multi-language extension system.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..extensions.registry import registry
from ..extensions.base import ParseResult, EntityType
from ..extensions.connectors import CrossLanguageConnector
from ..display.console import console
from ..display.formatters import ResultFormatter, SearchFormatter, GraphFormatter
from ..graph.searcher import GraphSearcher
from .tools import ToolRegistry

logger = logging.getLogger(__name__)

# Initialize the enhanced tool registry
enhanced_tools = ToolRegistry()

# Initialize formatters
result_formatter = ResultFormatter()
search_formatter = SearchFormatter()
graph_formatter = GraphFormatter()


@enhanced_tools.register(
    name="search_entities",
    description="Search for code entities across multiple languages",
    category="search"
)
def search_entities(query: str, entity_types: Optional[List[str]] = None, 
                   languages: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]:
    """
    Search for code entities using the multi-language extension system.
    
    Args:
        query: Search query string
        entity_types: Filter by entity types (class, function, variable, etc.)
        languages: Filter by programming languages (python, javascript, etc.)
        limit: Maximum number of results to return
    
    Returns:
        Dictionary containing search results and metadata
    """
    try:
        # Initialize parsers if not already done
        registry.initialize_default_parsers()
        
        # This is a placeholder - in a real implementation, you'd have a search index
        # For now, we'll return a structured response
        results = {
            'query': query,
            'results': [],
            'total_found': 0,
            'filters': {
                'entity_types': entity_types,
                'languages': languages
            },
            'supported_languages': list(registry.get_registered_parsers().keys()),
            'supported_extensions': registry.get_supported_extensions()
        }
        
        # Display results using rich formatting
        console.rule(f"[bold blue]Search Results for: {query}")
        console.print(search_formatter.format_search_results(results['results'], query))
        
        return results
        
    except Exception as e:
        logger.error(f"Error in search_entities: {e}")
        return {'error': str(e), 'query': query}


@enhanced_tools.register(
    name="parse_file",
    description="Parse a file using the appropriate language parser",
    category="parsing"
)
def parse_file(file_path: str, show_content: bool = False) -> Dict[str, Any]:
    """
    Parse a file and extract code entities using the multi-language system.
    
    Args:
        file_path: Path to the file to parse
        show_content: Whether to include content preview in results
    
    Returns:
        Dictionary containing parsed entities and metadata
    """
    try:
        # Initialize parsers
        registry.initialize_default_parsers()
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        # Parse the file
        entities = registry.parse_file(file_path)
        
        # Convert to serializable format
        results = []
        for entity in entities:
            entity_dict = {
                'name': entity.name,
                'type': entity.entity_type.value,
                'file_path': entity.file_path,
                'line_start': entity.line_start,
                'line_end': entity.line_end,
                'metadata': entity.metadata or {}
            }
            
            if show_content:
                entity_dict['content'] = entity.content
                entity_dict['docstring'] = entity.docstring
            
            results.append(entity_dict)
        
        # Get parser info
        parser = registry.get_parser_for_file(file_path)
        parser_info = parser.get_language_info() if parser else None
        
        response = {
            'file_path': file_path,
            'entities_found': len(results),
            'entities': results,
            'parser_used': parser_info
        }
        
        # Display results using rich formatting
        console.rule(f"[bold blue]Parsed File: {os.path.basename(file_path)}")
        
        if entities:
            # Show entities table
            console.print(result_formatter.format_entities_table(entities, f"Entities in {os.path.basename(file_path)}"))
            
            # Show detailed view if requested
            if show_content and len(entities) <= 5:  # Only show details for small files
                for entity in entities[:3]:  # Show first 3 entities
                    console.print(result_formatter.format_entity(entity, show_content=True))
        else:
            console.print("[yellow]No entities found in file[/yellow]")
        
        return response
        
    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {e}")
        return {'error': str(e), 'file_path': file_path}


@enhanced_tools.register(
    name="analyze_directory",
    description="Analyze a directory and extract entities from all supported files",
    category="analysis"
)
def analyze_directory(directory_path: str, recursive: bool = True, 
                     show_stats: bool = True) -> Dict[str, Any]:
    """
    Analyze a directory and extract entities from all supported files.
    
    Args:
        directory_path: Path to the directory to analyze
        recursive: Whether to analyze subdirectories
        show_stats: Whether to display statistics
    
    Returns:
        Dictionary containing analysis results and statistics
    """
    try:
        # Initialize parsers
        registry.initialize_default_parsers()
        
        if not os.path.isdir(directory_path):
            return {'error': f'Directory not found: {directory_path}'}
        
        all_entities = []
        files_processed = 0
        files_failed = 0
        language_stats = {}
        
        # Get supported extensions
        supported_extensions = registry.get_supported_extensions()
        
        with console.status("[bold green]Analyzing directory...") as status:
            # Walk through directory
            for root, dirs, files in os.walk(directory_path):
                if not recursive and root != directory_path:
                    break
                
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()
                    
                    if ext in supported_extensions:
                        status.update(f"[bold blue]Processing {file}...")
                        
                        try:
                            entities = registry.parse_file(file_path)
                            all_entities.extend(entities)
                            files_processed += 1
                            
                            # Update language stats
                            for entity in entities:
                                if entity.metadata and 'language' in entity.metadata:
                                    lang = entity.metadata['language']
                                    language_stats[lang] = language_stats.get(lang, 0) + 1
                        
                        except Exception as e:
                            logger.warning(f"Failed to process {file_path}: {e}")
                            files_failed += 1
        
        # Prepare response
        response = {
            'directory_path': directory_path,
            'files_processed': files_processed,
            'files_failed': files_failed,
            'total_entities': len(all_entities),
            'language_stats': language_stats,
            'entity_types': {},
            'supported_extensions': supported_extensions
        }
        
        # Count entity types
        for entity in all_entities:
            entity_type = entity.entity_type.value
            response['entity_types'][entity_type] = response['entity_types'].get(entity_type, 0) + 1
        
        # Display results
        if show_stats:
            console.rule(f"[bold blue]Directory Analysis: {os.path.basename(directory_path)}")
            
            # Show summary stats
            stats_table = graph_formatter.format_graph_stats({
                'nodes': len(all_entities),
                'files': files_processed,
                'languages': len(language_stats),
                'failed_files': files_failed
            })
            console.print(stats_table)
            
            # Show language breakdown
            if language_stats:
                console.print(graph_formatter.format_language_breakdown(language_stats))
            
            # Show entity tree for smaller directories
            if len(all_entities) <= 50:
                console.print(result_formatter.format_entity_tree(all_entities))
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing directory {directory_path}: {e}")
        return {'error': str(e), 'directory_path': directory_path}


@enhanced_tools.register(
    name="discover_relationships",
    description="Discover relationships between files and entities",
    category="analysis"
)
def discover_relationships(directory_path: str, show_details: bool = False) -> Dict[str, Any]:
    """
    Discover cross-language relationships between files and entities.
    
    Args:
        directory_path: Path to the directory to analyze
        show_details: Whether to show detailed relationship information
    
    Returns:
        Dictionary containing discovered relationships
    """
    try:
        # Initialize systems
        registry.initialize_default_parsers()
        connector = CrossLanguageConnector()
        
        if not os.path.isdir(directory_path):
            return {'error': f'Directory not found: {directory_path}'}
        
        # Parse all files in directory
        all_entities = []
        
        with console.status("[bold green]Discovering relationships...") as status:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        entities = registry.parse_file(file_path)
                        all_entities.extend(entities)
                    except Exception as e:
                        logger.debug(f"Failed to parse {file_path}: {e}")
            
            status.update("[bold blue]Analyzing relationships...")
            
            # Discover relationships
            relationships = connector.discover_relationships(all_entities, directory_path)
        
        # Prepare response
        response = {
            'directory_path': directory_path,
            'total_entities': len(all_entities),
            'total_relationships': len(relationships),
            'relationship_types': {},
            'relationships': []
        }
        
        # Count relationship types and prepare data
        for rel in relationships:
            rel_type = rel.relationship_type.value
            response['relationship_types'][rel_type] = response['relationship_types'].get(rel_type, 0) + 1
            
            if show_details:
                response['relationships'].append({
                    'type': rel_type,
                    'source': rel.source_id,
                    'target': rel.target_id,
                    'metadata': rel.metadata
                })
        
        # Display results
        console.rule("[bold blue]Relationship Discovery")
        
        if relationships:
            console.print(graph_formatter.format_relationships(relationships))
        else:
            console.print("[yellow]No relationships discovered[/yellow]")
        
        return response
        
    except Exception as e:
        logger.error(f"Error discovering relationships: {e}")
        return {'error': str(e), 'directory_path': directory_path}


@enhanced_tools.register(
    name="get_language_info",
    description="Get information about supported languages and parsers",
    category="info"
)
def get_language_info() -> Dict[str, Any]:
    """
    Get information about supported languages and their parsers.
    
    Returns:
        Dictionary containing language and parser information
    """
    try:
        # Initialize parsers
        registry.initialize_default_parsers()
        
        # Get parser information
        parsers_info = registry.get_registered_parsers()
        supported_extensions = registry.get_supported_extensions()
        
        response = {
            'total_parsers': len(parsers_info),
            'supported_extensions': supported_extensions,
            'parsers': parsers_info
        }
        
        # Display information
        console.rule("[bold blue]Supported Languages")
        
        # Create a table of languages
        from rich.table import Table
        
        table = Table(title="Language Support", show_header=True)
        table.add_column("Language", style="cyan", width=15)
        table.add_column("Extensions", style="green", width=20)
        table.add_column("Version", style="yellow", width=10)
        table.add_column("Entity Types", style="blue", width=30)
        
        for parser_name, parser_info in parsers_info.items():
            extensions = ", ".join(parser_info.get('supported_extensions', []))
            version = parser_info.get('version', 'N/A')
            entity_types = ", ".join(parser_info.get('entity_types', []))
            
            table.add_row(parser_name, extensions, version, entity_types)
        
        console.print(table)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting language info: {e}")
        return {'error': str(e)}


@enhanced_tools.register(
    name="show_entity_details",
    description="Show detailed information about a specific entity",
    category="info"
)
def show_entity_details(file_path: str, entity_name: str, 
                       entity_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Show detailed information about a specific entity.
    
    Args:
        file_path: Path to the file containing the entity
        entity_name: Name of the entity to show
        entity_type: Optional entity type filter
    
    Returns:
        Dictionary containing entity details
    """
    try:
        # Initialize parsers
        registry.initialize_default_parsers()
        
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        # Parse the file
        entities = registry.parse_file(file_path)
        
        # Find matching entities
        matches = []
        for entity in entities:
            if entity.name == entity_name:
                if entity_type is None or entity.entity_type.value == entity_type:
                    matches.append(entity)
        
        if not matches:
            return {
                'error': f'Entity "{entity_name}" not found in {file_path}',
                'available_entities': [e.name for e in entities]
            }
        
        # Prepare response
        response = {
            'file_path': file_path,
            'entity_name': entity_name,
            'matches_found': len(matches),
            'entities': []
        }
        
        for entity in matches:
            entity_dict = {
                'name': entity.name,
                'type': entity.entity_type.value,
                'line_start': entity.line_start,
                'line_end': entity.line_end,
                'content': entity.content,
                'docstring': entity.docstring,
                'metadata': entity.metadata or {}
            }
            response['entities'].append(entity_dict)
        
        # Display detailed information
        console.rule(f"[bold blue]Entity Details: {entity_name}")
        
        for entity in matches:
            console.print(result_formatter.format_entity(entity, show_content=True))
        
        return response
        
    except Exception as e:
        logger.error(f"Error showing entity details: {e}")
        return {'error': str(e), 'file_path': file_path, 'entity_name': entity_name}


# Export the enhanced tools registry
__all__ = ['enhanced_tools']