"""
Result formatters for beautiful display of Coretx data.
"""

from typing import List, Dict, Any, Optional, Tuple
import os
from datetime import datetime

try:
    from rich.table import Table
    from rich.tree import Tree
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.layout import Layout
    from rich.align import Align
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from ..extensions.base import ParseResult, EntityType
from ..extensions.connectors import Relationship, RelationshipType
from .console import console


class ResultFormatter:
    """Base formatter for Coretx results."""
    
    def __init__(self):
        self.console = console
    
    def format_entity(self, entity: ParseResult, show_content: bool = False) -> Any:
        """Format a single entity for display."""
        if not HAS_RICH:
            return self._format_entity_plain(entity, show_content)
        
        # Create entity info
        entity_info = []
        
        # Entity type and name
        type_style = f"entity.{entity.entity_type.value}"
        entity_info.append(f"[{type_style}]{entity.entity_type.value.upper()}[/{type_style}]: [bold]{entity.name}[/bold]")
        
        # File path and line info
        entity_info.append(f"[path]{entity.file_path}[/path]:[line]{entity.line_start}-{entity.line_end}[/line]")
        
        # Language info
        if entity.metadata and 'language' in entity.metadata:
            lang = entity.metadata['language']
            entity_info.append(f"Language: [language.{lang}]{lang}[/language.{lang}]")
        
        # Additional metadata
        if entity.metadata:
            for key, value in entity.metadata.items():
                if key != 'language' and value is not None:
                    entity_info.append(f"{key}: {value}")
        
        # Content preview
        if show_content and entity.content:
            content_preview = entity.content[:200] + "..." if len(entity.content) > 200 else entity.content
            
            # Try to syntax highlight based on language
            if entity.metadata and 'language' in entity.metadata:
                try:
                    syntax = Syntax(content_preview, entity.metadata['language'], theme="monokai", line_numbers=True)
                    entity_info.append(syntax)
                except:
                    entity_info.append(f"Content: {content_preview}")
            else:
                entity_info.append(f"Content: {content_preview}")
        
        return Panel("\n".join(str(info) for info in entity_info), 
                    title=f"{entity.entity_type.value}: {entity.name}",
                    border_style=type_style)
    
    def format_entities_table(self, entities: List[ParseResult], title: str = "Entities") -> Any:
        """Format entities as a table."""
        if not HAS_RICH:
            return self._format_entities_table_plain(entities, title)
        
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Name", style="bold", width=30)
        table.add_column("File", style="blue", width=40)
        table.add_column("Lines", style="green", width=10)
        table.add_column("Language", style="yellow", width=12)
        
        for entity in entities:
            entity_type = entity.entity_type.value
            name = entity.name[:27] + "..." if len(entity.name) > 30 else entity.name
            file_path = os.path.basename(entity.file_path)
            lines = f"{entity.line_start}-{entity.line_end}"
            language = entity.metadata.get('language', 'unknown') if entity.metadata else 'unknown'
            
            table.add_row(entity_type, name, file_path, lines, language)
        
        return table
    
    def format_entity_tree(self, entities: List[ParseResult], title: str = "Entity Tree") -> Any:
        """Format entities as a tree structure."""
        if not HAS_RICH:
            return self._format_entity_tree_plain(entities, title)
        
        tree = Tree(f"[bold blue]{title}[/bold blue]")
        
        # Group entities by file
        files = {}
        for entity in entities:
            if entity.file_path not in files:
                files[entity.file_path] = []
            files[entity.file_path].append(entity)
        
        for file_path, file_entities in files.items():
            file_node = tree.add(f"[blue]{os.path.basename(file_path)}[/blue]")
            
            # Group by entity type
            types = {}
            for entity in file_entities:
                if entity.entity_type not in types:
                    types[entity.entity_type] = []
                types[entity.entity_type].append(entity)
            
            for entity_type, type_entities in types.items():
                if entity_type == EntityType.FILE:
                    continue  # Skip file entities in tree
                
                type_style = f"entity.{entity_type.value}"
                type_node = file_node.add(f"[{type_style}]{entity_type.value.upper()}[/{type_style}]")
                
                for entity in type_entities:
                    entity_node = type_node.add(f"[bold]{entity.name}[/bold] [line]({entity.line_start}-{entity.line_end})[/line]")
        
        return tree
    
    def _format_entity_plain(self, entity: ParseResult, show_content: bool = False) -> str:
        """Plain text formatting for entity."""
        lines = [
            f"{entity.entity_type.value.upper()}: {entity.name}",
            f"File: {entity.file_path}:{entity.line_start}-{entity.line_end}"
        ]
        
        if entity.metadata and 'language' in entity.metadata:
            lines.append(f"Language: {entity.metadata['language']}")
        
        if show_content and entity.content:
            content_preview = entity.content[:200] + "..." if len(entity.content) > 200 else entity.content
            lines.append(f"Content: {content_preview}")
        
        return "\n".join(lines)
    
    def _format_entities_table_plain(self, entities: List[ParseResult], title: str) -> str:
        """Plain text table formatting."""
        lines = [f"\n{title}", "=" * len(title)]
        
        for entity in entities:
            lines.append(f"{entity.entity_type.value:12} {entity.name:30} {os.path.basename(entity.file_path):20} {entity.line_start}-{entity.line_end}")
        
        return "\n".join(lines)
    
    def _format_entity_tree_plain(self, entities: List[ParseResult], title: str) -> str:
        """Plain text tree formatting."""
        lines = [f"\n{title}", "=" * len(title)]
        
        # Group by file
        files = {}
        for entity in entities:
            if entity.file_path not in files:
                files[entity.file_path] = []
            files[entity.file_path].append(entity)
        
        for file_path, file_entities in files.items():
            lines.append(f"\n{os.path.basename(file_path)}")
            
            for entity in file_entities:
                if entity.entity_type != EntityType.FILE:
                    lines.append(f"  {entity.entity_type.value}: {entity.name} ({entity.line_start}-{entity.line_end})")
        
        return "\n".join(lines)


class SearchFormatter(ResultFormatter):
    """Formatter for search results."""
    
    def format_search_results(self, results: List[Dict[str, Any]], query: str) -> Any:
        """Format search results."""
        if not HAS_RICH:
            return self._format_search_results_plain(results, query)
        
        if not results:
            return Panel("[yellow]No results found[/yellow]", title=f"Search: {query}")
        
        table = Table(title=f"Search Results for: [bold]{query}[/bold]", show_header=True)
        table.add_column("Score", style="score", width=8)
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Name", style="bold", width=30)
        table.add_column("File", style="path", width=40)
        table.add_column("Lines", style="line", width=10)
        
        for result in results:
            score = f"{result.get('score', 0):.2f}"
            entity_type = result.get('type', 'unknown')
            name = result.get('name', 'unknown')
            file_path = result.get('path', 'unknown')
            
            # Truncate long names
            if len(name) > 27:
                name = name[:27] + "..."
            
            # Extract line info if available
            lines = "N/A"
            if 'line_start' in result and 'line_end' in result:
                lines = f"{result['line_start']}-{result['line_end']}"
            
            table.add_row(score, entity_type, name, os.path.basename(file_path), lines)
        
        return table
    
    def _format_search_results_plain(self, results: List[Dict[str, Any]], query: str) -> str:
        """Plain text search results formatting."""
        if not results:
            return f"\nNo results found for: {query}"
        
        lines = [f"\nSearch Results for: {query}", "=" * (20 + len(query))]
        
        for result in results:
            score = result.get('score', 0)
            entity_type = result.get('type', 'unknown')
            name = result.get('name', 'unknown')
            file_path = result.get('path', 'unknown')
            
            lines.append(f"{score:6.2f} {entity_type:12} {name:30} {os.path.basename(file_path)}")
        
        return "\n".join(lines)


class GraphFormatter(ResultFormatter):
    """Formatter for graph information."""
    
    def format_graph_stats(self, stats: Dict[str, Any]) -> Any:
        """Format graph statistics."""
        if not HAS_RICH:
            return self._format_graph_stats_plain(stats)
        
        # Create statistics table
        table = Table(title="Graph Statistics", show_header=True)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="bold green", width=15)
        table.add_column("Description", style="white", width=40)
        
        metrics = [
            ("Nodes", stats.get('nodes', 0), "Total number of entities"),
            ("Edges", stats.get('edges', 0), "Total number of relationships"),
            ("Files", stats.get('files', 0), "Number of files processed"),
            ("Languages", stats.get('languages', 0), "Number of programming languages"),
            ("Density", f"{stats.get('density', 0):.3f}", "Graph density (edges/possible_edges)"),
        ]
        
        for metric, value, description in metrics:
            table.add_row(metric, str(value), description)
        
        return table
    
    def format_relationships(self, relationships: List[Relationship]) -> Any:
        """Format relationship information."""
        if not HAS_RICH:
            return self._format_relationships_plain(relationships)
        
        if not relationships:
            return Panel("[yellow]No relationships found[/yellow]", title="Relationships")
        
        table = Table(title="Entity Relationships", show_header=True)
        table.add_column("Type", style="cyan", width=15)
        table.add_column("Source", style="bold", width=30)
        table.add_column("Target", style="bold", width=30)
        table.add_column("Metadata", style="dim", width=25)
        
        for rel in relationships:
            rel_type = rel.relationship_type.value
            source = rel.source_id.split(':')[-2] if ':' in rel.source_id else rel.source_id
            target = rel.target_id.split(':')[-2] if ':' in rel.target_id else rel.target_id
            metadata = str(rel.metadata) if rel.metadata else ""
            
            # Truncate long values
            if len(source) > 27:
                source = source[:27] + "..."
            if len(target) > 27:
                target = target[:27] + "..."
            if len(metadata) > 22:
                metadata = metadata[:22] + "..."
            
            table.add_row(rel_type, source, target, metadata)
        
        return table
    
    def format_language_breakdown(self, breakdown: Dict[str, int]) -> Any:
        """Format language breakdown."""
        if not HAS_RICH:
            return self._format_language_breakdown_plain(breakdown)
        
        table = Table(title="Language Breakdown", show_header=True)
        table.add_column("Language", style="cyan", width=15)
        table.add_column("Entities", style="bold green", width=10)
        table.add_column("Percentage", style="yellow", width=12)
        
        total = sum(breakdown.values())
        
        for language, count in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
            percentage = f"{(count/total)*100:.1f}%" if total > 0 else "0%"
            table.add_row(language, str(count), percentage)
        
        return table
    
    def _format_graph_stats_plain(self, stats: Dict[str, Any]) -> str:
        """Plain text graph statistics."""
        lines = [
            "\nGraph Statistics",
            "================",
            f"Nodes: {stats.get('nodes', 0)}",
            f"Edges: {stats.get('edges', 0)}",
            f"Files: {stats.get('files', 0)}",
            f"Languages: {stats.get('languages', 0)}",
            f"Density: {stats.get('density', 0):.3f}",
        ]
        return "\n".join(lines)
    
    def _format_relationships_plain(self, relationships: List[Relationship]) -> str:
        """Plain text relationships."""
        if not relationships:
            return "\nNo relationships found"
        
        lines = ["\nEntity Relationships", "==================="]
        
        for rel in relationships:
            lines.append(f"{rel.relationship_type.value}: {rel.source_id} -> {rel.target_id}")
        
        return "\n".join(lines)
    
    def _format_language_breakdown_plain(self, breakdown: Dict[str, int]) -> str:
        """Plain text language breakdown."""
        lines = ["\nLanguage Breakdown", "=================="]
        
        total = sum(breakdown.values())
        for language, count in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
            percentage = f"{(count/total)*100:.1f}%" if total > 0 else "0%"
            lines.append(f"{language:15} {count:6} ({percentage})")
        
        return "\n".join(lines)