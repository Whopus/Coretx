"""
Command-line interface for Coretx.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from . import Coretx
from .models import LLMConfig, AnalysisConfig


console = Console()


@click.group()
@click.version_option()
def main():
    """Coretx - Intelligent Code Context Engine"""
    pass


@main.command()
@click.option('--api-key', help='OpenAI API key')
@click.option('--model', default='gpt-4', help='LLM model to use')
@click.option('--embedding-model', default='text-embedding-3-small', help='Embedding model to use')
def init(api_key: Optional[str], model: str, embedding_model: str):
    """Initialize Coretx configuration."""
    config_dir = Path.home() / '.coretx'
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / 'config.yaml'
    
    # Get API key
    if not api_key:
        api_key = click.prompt('OpenAI API Key', hide_input=True)
    
    # Create config
    config = {
        'llm': {
            'provider': 'openai',
            'api_key': api_key,
            'model': model,
            'embedding_model': embedding_model,
            'temperature': 0.1
        },
        'analysis': {
            'max_file_size': 1048576,
            'ignore_patterns': [
                '*.test.js',
                '*.spec.py',
                '__pycache__',
                'node_modules',
                '.git'
            ],
            'include_hidden': False
        },
        'output': {
            'syntax_highlighting': True,
            'max_context_size': 8000,
            'format': 'markdown'
        }
    }
    
    # Save config
    import yaml
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    console.print(f"✅ Configuration saved to {config_file}", style="green")


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--incremental', is_flag=True, help='Perform incremental analysis')
@click.option('--max-depth', type=int, default=5, help='Maximum analysis depth')
@click.option('--languages', help='Comma-separated list of languages to analyze')
@click.option('--output', help='Output file for graph export')
def analyze(path: str, incremental: bool, max_depth: int, languages: Optional[str], output: Optional[str]):
    """Analyze a codebase and build knowledge graph."""
    try:
        # Initialize Coretx
        ctx = _get_coretx_instance()
        
        # Parse languages
        language_list = None
        if languages:
            language_list = [lang.strip() for lang in languages.split(',')]
        
        # Show project info
        from .utils.file_utils import FileScanner
        scanner = FileScanner(AnalysisConfig())
        project_info = scanner.get_project_info(Path(path))
        
        _display_project_info(project_info)
        
        # Analyze
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing codebase...", total=None)
            
            graph = ctx.analyze(
                path,
                incremental=incremental,
                max_depth=max_depth,
                languages=language_list
            )
        
        # Display results
        stats = graph.get_graph_stats()
        _display_analysis_results(stats)
        
        # Export if requested
        if output:
            format_type = Path(output).suffix.lstrip('.')
            if format_type in ['json', 'graphml', 'gexf']:
                ctx.export_graph(graph, output, format_type)
                console.print(f"✅ Graph exported to {output}", style="green")
        
    except Exception as e:
        console.print(f"❌ Analysis failed: {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.argument('question')
@click.option('--max-results', type=int, default=10, help='Maximum number of results')
@click.option('--format', 'output_format', type=click.Choice(['text', 'json', 'markdown']), 
              default='text', help='Output format')
def query(path: str, question: str, max_results: int, output_format: str):
    """Query the codebase using natural language."""
    try:
        ctx = _get_coretx_instance()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing query...", total=None)
            result = ctx.query(path, question, max_results=max_results)
        
        _display_query_result(result, output_format)
        
    except Exception as e:
        console.print(f"❌ Query failed: {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.argument('problem')
@click.option('--format', 'output_format', type=click.Choice(['text', 'json', 'markdown']), 
              default='text', help='Output format')
def locate(path: str, problem: str, output_format: str):
    """Find relevant code for a specific problem."""
    try:
        ctx = _get_coretx_instance()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Locating code...", total=None)
            result = ctx.locate(path, problem)
        
        _display_context_result(result, output_format)
        
    except Exception as e:
        console.print(f"❌ Code location failed: {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.argument('entity')
@click.option('--direction', type=click.Choice(['forward', 'backward', 'both']), 
              default='both', help='Trace direction')
@click.option('--max-depth', type=int, default=3, help='Maximum trace depth')
def trace(path: str, entity: str, direction: str, max_depth: int):
    """Trace dependencies of a code entity."""
    try:
        ctx = _get_coretx_instance()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Tracing dependencies...", total=None)
            result = ctx.trace(path, entity, direction, max_depth)
        
        _display_trace_result(result)
        
    except Exception as e:
        console.print(f"❌ Dependency tracing failed: {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('path', type=click.Path(exists=True))
def interactive(path: str):
    """Start interactive query session."""
    try:
        ctx = _get_coretx_instance()
        
        # Load or analyze graph
        console.print("🔍 Loading knowledge graph...", style="blue")
        graph = ctx._load_or_analyze_graph(path)
        stats = graph.get_graph_stats()
        
        console.print(f"✅ Loaded graph with {stats.total_entities} entities", style="green")
        console.print("\n💡 Enter your questions (type 'exit' to quit, 'help' for commands)")
        
        while True:
            try:
                question = click.prompt("\n❓ Query", type=str)
                
                if question.lower() in ['exit', 'quit', 'q']:
                    break
                elif question.lower() == 'help':
                    _show_interactive_help()
                    continue
                elif question.lower().startswith('trace '):
                    entity_name = question[6:].strip()
                    result = ctx.trace(graph, entity_name)
                    _display_trace_result(result)
                elif question.lower().startswith('locate '):
                    problem = question[7:].strip()
                    result = ctx.locate(graph, problem)
                    _display_context_result(result, 'text')
                else:
                    result = ctx.query(graph, question)
                    _display_query_result(result, 'text')
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"❌ Error: {e}", style="red")
        
        console.print("\n👋 Goodbye!", style="blue")
        
    except Exception as e:
        console.print(f"❌ Interactive session failed: {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('path', type=click.Path(exists=True))
def stats(path: str):
    """Show statistics about the knowledge graph."""
    try:
        ctx = _get_coretx_instance()
        graph_stats = ctx.get_stats(path)
        _display_analysis_results(graph_stats)
        
    except Exception as e:
        console.print(f"❌ Failed to get stats: {e}", style="red")
        sys.exit(1)


def _get_coretx_instance() -> Coretx:
    """Get configured Coretx instance."""
    config_file = Path.home() / '.coretx' / 'config.yaml'
    
    if config_file.exists():
        return Coretx.from_config(str(config_file))
    else:
        # Use environment variables or defaults
        return Coretx(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            openai_base_url=os.getenv('OPENAI_BASE_URL'),
            model=os.getenv('CORETX_MODEL', 'gpt-4'),
            embedding_model=os.getenv('CORETX_EMBEDDING_MODEL', 'text-embedding-3-small')
        )


def _display_project_info(info: Dict[str, Any]) -> None:
    """Display project information."""
    table = Table(title="Project Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Path", info['path'])
    table.add_row("Name", info['name'])
    table.add_row("Total Files", str(info['total_files']))
    table.add_row("Supported Files", str(info['supported_files']))
    table.add_row("Size", f"{info['size_bytes'] / 1024 / 1024:.1f} MB")
    
    # Languages
    if info['languages']:
        lang_str = ", ".join(f"{lang} ({count})" for lang, count in info['languages'].items())
        table.add_row("Languages", lang_str)
    
    console.print(table)


def _display_analysis_results(stats) -> None:
    """Display analysis results."""
    # Main stats table
    table = Table(title="Analysis Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="white")
    
    table.add_row("Total Entities", str(stats.total_entities))
    table.add_row("Total Relationships", str(stats.total_relationships))
    table.add_row("Files Analyzed", str(stats.file_count))
    table.add_row("Total Lines", str(stats.total_lines))
    if stats.analysis_time > 0:
        table.add_row("Analysis Time", f"{stats.analysis_time:.2f}s")
    
    console.print(table)
    
    # Entity breakdown
    if stats.entity_counts:
        entity_table = Table(title="Entity Breakdown")
        entity_table.add_column("Type", style="cyan")
        entity_table.add_column("Count", style="white")
        
        for entity_type, count in stats.entity_counts.items():
            if count > 0:
                entity_table.add_row(entity_type.value.title(), str(count))
        
        console.print(entity_table)
    
    # Language breakdown
    if stats.language_breakdown:
        lang_table = Table(title="Language Breakdown")
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Files", style="white")
        
        for language, count in stats.language_breakdown.items():
            lang_table.add_row(language.title(), str(count))
        
        console.print(lang_table)


def _display_query_result(result, output_format: str) -> None:
    """Display query result."""
    if output_format == 'json':
        # Convert to JSON-serializable format
        data = {
            'summary': result.summary,
            'confidence': result.confidence,
            'entities': [{'name': e.name, 'type': e.type.value, 'path': e.path} for e in result.entities],
            'suggestions': result.suggestions
        }
        console.print(json.dumps(data, indent=2))
        return
    
    # Text/Markdown format
    console.print(Panel(result.summary, title="Answer", border_style="green"))
    
    if result.entities:
        console.print("\n📋 Relevant Entities:")
        for entity in result.entities[:5]:
            console.print(f"  • {entity.type.value}: {entity.name} ({entity.path})")
    
    if result.suggestions:
        console.print("\n💡 Suggestions:")
        for suggestion in result.suggestions:
            console.print(f"  • {suggestion}")
    
    console.print(f"\n🎯 Confidence: {result.confidence:.2f}")


def _display_context_result(result, output_format: str) -> None:
    """Display context result."""
    if output_format == 'json':
        data = {
            'analysis_summary': result.analysis_summary,
            'confidence': result.confidence,
            'entry_points': [{'name': e.name, 'type': e.type.value} for e in result.entry_points],
            'fix_suggestions': result.fix_suggestions
        }
        console.print(json.dumps(data, indent=2))
        return
    
    # Text format
    console.print(Panel(result.analysis_summary, title="Analysis Summary", border_style="blue"))
    
    if result.entry_points:
        console.print("\n🎯 Entry Points:")
        for entity in result.entry_points:
            console.print(f"  • {entity.type.value}: {entity.name}")
    
    if result.fix_suggestions:
        console.print("\n🔧 Fix Suggestions:")
        for suggestion in result.fix_suggestions:
            console.print(f"  • {suggestion}")
    
    console.print(f"\n📊 Confidence: {result.confidence:.2f}")
    
    # Show minimal closure (truncated)
    if result.minimal_closure:
        closure_preview = result.minimal_closure[:500] + "..." if len(result.minimal_closure) > 500 else result.minimal_closure
        console.print(Panel(closure_preview, title="Code Context (Preview)", border_style="yellow"))


def _display_trace_result(result) -> None:
    """Display trace result."""
    if not result.entity:
        console.print("❌ Entity not found", style="red")
        return
    
    console.print(f"🔍 Tracing: {result.entity.type.value} {result.entity.name}")
    
    if result.dependencies:
        console.print(f"\n⬇️  Dependencies ({len(result.dependencies)}):")
        for dep in result.dependencies[:10]:
            console.print(f"  • {dep.type.value}: {dep.name}")
        if len(result.dependencies) > 10:
            console.print(f"  ... and {len(result.dependencies) - 10} more")
    
    if result.dependents:
        console.print(f"\n⬆️  Dependents ({len(result.dependents)}):")
        for dep in result.dependents[:10]:
            console.print(f"  • {dep.type.value}: {dep.name}")
        if len(result.dependents) > 10:
            console.print(f"  ... and {len(result.dependents) - 10} more")


def _show_interactive_help() -> None:
    """Show interactive mode help."""
    help_text = """
🔍 Interactive Mode Commands:

• <question>        - Ask any question about the code
• trace <entity>    - Trace dependencies of an entity
• locate <problem>  - Find code relevant to a problem
• help             - Show this help
• exit/quit/q      - Exit interactive mode

Examples:
• "What does the authentication system do?"
• "trace UserService"
• "locate memory leak in payment processing"
"""
    console.print(Panel(help_text.strip(), title="Help", border_style="cyan"))


if __name__ == '__main__':
    main()