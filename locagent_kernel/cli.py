"""Command-line interface for LocAgent Kernel."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from . import CodeLocator, LocAgentConfig, quick_localize
from .utils import load_config, save_config, setup_logger


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="LocAgent Kernel - Code Localization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick localization
  locagent localize /path/to/repo "Bug in authentication"
  
  # Use custom configuration
  locagent localize /path/to/repo "Memory leak" --config config.yaml
  
  # Search codebase
  locagent search /path/to/repo "OAuth token" --type hybrid
  
  # Initialize repository (build indices)
  locagent init /path/to/repo --config config.yaml
  
  # Get repository statistics
  locagent stats /path/to/repo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Localize command
    localize_parser = subparsers.add_parser('localize', help='Perform code localization')
    localize_parser.add_argument('repo_path', help='Path to repository')
    localize_parser.add_argument('problem', help='Problem description')
    localize_parser.add_argument('--config', '-c', help='Configuration file path')
    localize_parser.add_argument('--model', '-m', default='gpt-4', help='LLM model name')
    localize_parser.add_argument('--output', '-o', help='Output file for results')
    localize_parser.add_argument('--context', help='Additional repository context')
    localize_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search codebase')
    search_parser.add_argument('repo_path', help='Path to repository')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', '-t', choices=['text', 'graph', 'hybrid', 'structure'], 
                              default='hybrid', help='Search type')
    search_parser.add_argument('--top-k', '-k', type=int, default=10, help='Number of results')
    search_parser.add_argument('--config', '-c', help='Configuration file path')
    search_parser.add_argument('--output', '-o', help='Output file for results')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize repository (build indices)')
    init_parser.add_argument('repo_path', help='Path to repository')
    init_parser.add_argument('--config', '-c', help='Configuration file path')
    init_parser.add_argument('--force', '-f', action='store_true', help='Force rebuild indices')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Get repository statistics')
    stats_parser.add_argument('repo_path', help='Path to repository')
    stats_parser.add_argument('--config', '-c', help='Configuration file path')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    # Create default config
    create_config_parser = config_subparsers.add_parser('create', help='Create default configuration')
    create_config_parser.add_argument('output_path', help='Output configuration file path')
    create_config_parser.add_argument('--format', choices=['yaml', 'json'], default='yaml', 
                                     help='Configuration format')
    
    # Validate config
    validate_config_parser = config_subparsers.add_parser('validate', help='Validate configuration')
    validate_config_parser.add_argument('config_path', help='Configuration file path')
    
    return parser


def load_configuration(config_path: Optional[str]) -> LocAgentConfig:
    """Load configuration from file or create default."""
    if config_path:
        config = load_config(config_path)
        if config is None:
            print(f"Error: Failed to load configuration from {config_path}")
            sys.exit(1)
        return config
    else:
        return LocAgentConfig()


def save_results(results: dict, output_path: str) -> None:
    """Save results to file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {output_path}")
    except Exception as e:
        print(f"Error saving results: {e}")


def cmd_localize(args) -> None:
    """Handle localize command."""
    print(f"Localizing code in {args.repo_path}")
    print(f"Problem: {args.problem}")
    
    if args.config:
        config = load_configuration(args.config)
        config.agent.model_name = args.model
        
        locator = CodeLocator(config)
        locator.initialize(args.repo_path)
        
        results = locator.localize(
            problem_description=args.problem,
            repository_context=args.context or ""
        )
    else:
        # Quick localization
        results = quick_localize(
            repo_path=args.repo_path,
            problem_description=args.problem,
            model_name=args.model
        )
    
    # Display results
    loc_results = results.get('localization_results', {})
    
    print("\n=== Localization Results ===")
    
    files = loc_results.get('files', [])
    if files:
        print(f"\nRelevant Files ({len(files)}):")
        for file in files:
            print(f"  • {file}")
    
    classes = loc_results.get('classes', [])
    if classes:
        print(f"\nRelevant Classes ({len(classes)}):")
        for cls in classes:
            print(f"  • {cls}")
    
    functions = loc_results.get('functions', [])
    if functions:
        print(f"\nRelevant Functions ({len(functions)}):")
        for func in functions:
            print(f"  • {func}")
    
    print(f"\nIterations: {results.get('iterations', 0)}")
    print(f"Total tokens: {results.get('total_tokens', 0)}")
    
    if args.verbose:
        print("\n=== Conversation History ===")
        for i, msg in enumerate(results.get('conversation', [])):
            print(f"\n{i+1}. {msg['role'].upper()}:")
            content = msg['content']
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"   {content}")
    
    # Save results if requested
    if args.output:
        save_results(results, args.output)


def cmd_search(args) -> None:
    """Handle search command."""
    print(f"Searching in {args.repo_path}")
    print(f"Query: {args.query}")
    print(f"Search type: {args.type}")
    
    config = load_configuration(args.config)
    
    locator = CodeLocator(config)
    locator.initialize(args.repo_path)
    
    results = locator.search(
        query=args.query,
        search_type=args.type,
        top_k=args.top_k
    )
    
    print(f"\n=== Search Results ({len(results)}) ===")
    
    for i, result in enumerate(results, 1):
        node_info = result['node_info']
        attrs = node_info['attributes']
        
        print(f"\n{i}. {attrs.get('name', 'Unknown')}")
        print(f"   Type: {attrs.get('type', 'Unknown')}")
        print(f"   Path: {attrs.get('path', '')}")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Method: {result['search_type']}")
        
        if attrs.get('line_start'):
            print(f"   Lines: {attrs['line_start']}-{attrs.get('line_end', '')}")
    
    # Save results if requested
    if args.output:
        save_results({'query': args.query, 'results': results}, args.output)


def cmd_init(args) -> None:
    """Handle init command."""
    print(f"Initializing repository: {args.repo_path}")
    
    config = load_configuration(args.config)
    
    locator = CodeLocator(config)
    locator.initialize(args.repo_path, force_rebuild=args.force)
    
    stats = locator.get_graph_stats()
    if stats:
        print(f"\nRepository initialized successfully!")
        print(f"Nodes: {stats['total_nodes']}")
        print(f"Edges: {stats['total_edges']}")
        print(f"Files: {stats['node_counts'].get('file', 0)}")
        print(f"Classes: {stats['node_counts'].get('class', 0)}")
        print(f"Functions: {stats['node_counts'].get('function', 0)}")


def cmd_stats(args) -> None:
    """Handle stats command."""
    print(f"Getting statistics for: {args.repo_path}")
    
    config = load_configuration(args.config)
    
    locator = CodeLocator(config)
    locator.initialize(args.repo_path)
    
    stats = locator.get_graph_stats()
    if stats:
        print(f"\n=== Repository Statistics ===")
        print(f"Total Nodes: {stats['total_nodes']}")
        print(f"Total Edges: {stats['total_edges']}")
        print(f"Max Depth: {stats['max_depth']}")
        
        print(f"\nNode Distribution:")
        for node_type, count in stats['node_counts'].items():
            print(f"  {node_type.capitalize()}: {count}")
        
        print(f"\nEdge Distribution:")
        for edge_type, count in stats['edge_counts'].items():
            print(f"  {edge_type.capitalize()}: {count}")


def cmd_config(args) -> None:
    """Handle config command."""
    if args.config_action == 'create':
        print(f"Creating default configuration: {args.output_path}")
        
        config = LocAgentConfig()
        success = save_config(config, args.output_path, args.format)
        
        if success:
            print(f"Default configuration saved to {args.output_path}")
        else:
            print("Error creating configuration file")
            sys.exit(1)
    
    elif args.config_action == 'validate':
        print(f"Validating configuration: {args.config_path}")
        
        config = load_config(args.config_path)
        if config is None:
            print("Error: Invalid configuration file")
            sys.exit(1)
        
        from .utils.config_utils import validate_config
        issues = validate_config(config)
        
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"  • {issue}")
            sys.exit(1)
        else:
            print("Configuration is valid!")


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    log_level = "DEBUG" if getattr(args, 'verbose', False) else "INFO"
    setup_logger(level=log_level)
    
    try:
        if args.command == 'localize':
            cmd_localize(args)
        elif args.command == 'search':
            cmd_search(args)
        elif args.command == 'init':
            cmd_init(args)
        elif args.command == 'stats':
            cmd_stats(args)
        elif args.command == 'config':
            cmd_config(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()