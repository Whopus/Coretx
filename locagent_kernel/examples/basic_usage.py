"""
Basic usage example for LocAgent Kernel.

This example demonstrates how to use the LocAgent Kernel for code localization.
"""

import os
from pathlib import Path
from locagent_kernel import CodeLocator, LocAgentConfig, quick_localize


def basic_localization_example():
    """Basic example of code localization."""
    
    # Example repository path (replace with actual path)
    repo_path = "/path/to/your/repository"
    
    # Problem description
    problem = """
    There's a bug where the user authentication fails when using OAuth tokens.
    The error message says 'Invalid token format' but the token looks correct.
    This might be related to token validation or parsing logic.
    """
    
    # Method 1: Quick localization (simplest)
    print("=== Quick Localization ===")
    try:
        results = quick_localize(
            repo_path=repo_path,
            problem_description=problem,
            model_name="gpt-4"
        )
        
        print("Localization Results:")
        for file in results['localization_results'].get('files', []):
            print(f"  File: {file}")
        
        for cls in results['localization_results'].get('classes', []):
            print(f"  Class: {cls}")
            
        for func in results['localization_results'].get('functions', []):
            print(f"  Function: {func}")
            
    except Exception as e:
        print(f"Quick localization failed: {e}")
    
    # Method 2: Full control with configuration
    print("\n=== Full Configuration Example ===")
    
    # Create custom configuration
    config = LocAgentConfig()
    config.agent.model_name = "gpt-4"
    config.agent.temperature = 0.1
    config.retrieval.top_k = 15
    config.graph.max_depth = 8
    
    # Create and initialize locator
    locator = CodeLocator(config)
    
    try:
        locator.initialize(repo_path)
        
        # Perform localization
        results = locator.localize(problem)
        
        print("Detailed Results:")
        print(f"  Iterations: {results['iterations']}")
        print(f"  Total tokens: {results['total_tokens']}")
        
        # Show conversation history
        print("\nAgent Conversation:")
        for msg in results['conversation'][-3:]:  # Last 3 messages
            print(f"  {msg['role']}: {msg['content'][:100]}...")
        
    except Exception as e:
        print(f"Full localization failed: {e}")


def search_example():
    """Example of using search functionality."""
    
    repo_path = "/path/to/your/repository"
    
    # Create locator
    config = LocAgentConfig()
    locator = CodeLocator(config)
    locator.initialize(repo_path)
    
    # Different types of searches
    print("=== Search Examples ===")
    
    # Text search
    text_results = locator.search("authentication", search_type="text", top_k=5)
    print(f"Text search found {len(text_results)} results")
    
    # Graph search
    graph_results = locator.search("OAuth", search_type="graph", top_k=5)
    print(f"Graph search found {len(graph_results)} results")
    
    # Hybrid search (default)
    hybrid_results = locator.search("token validation", top_k=10)
    print(f"Hybrid search found {len(hybrid_results)} results")
    
    # Show first result
    if hybrid_results:
        result = hybrid_results[0]
        print(f"\nTop result:")
        print(f"  Name: {result['node_info']['attributes']['name']}")
        print(f"  Type: {result['node_info']['attributes']['type']}")
        print(f"  Path: {result['node_info']['attributes']['path']}")
        print(f"  Score: {result['score']:.3f}")


def analysis_example():
    """Example of code analysis functionality."""
    
    repo_path = "/path/to/your/repository"
    
    config = LocAgentConfig()
    locator = CodeLocator(config)
    locator.initialize(repo_path)
    
    print("=== Analysis Examples ===")
    
    # Get repository statistics
    stats = locator.get_graph_stats()
    if stats:
        print(f"Repository has {stats['total_nodes']} nodes and {stats['total_edges']} edges")
        print(f"Node distribution: {stats['node_counts']}")
    
    # Find files in a specific directory
    files = locator.search("auth", search_type="structure", top_k=10)
    print(f"Found {len(files)} files related to 'auth'")
    
    # Analyze a specific entity (if found)
    if files:
        entity_id = files[0]['node_id']
        entity_info = locator.get_entity_info(entity_id)
        
        if entity_info:
            print(f"\nAnalyzing entity: {entity_info['attributes']['name']}")
            print(f"  Type: {entity_info['attributes']['type']}")
            print(f"  Dependencies: {len(entity_info.get('dependencies', {}))}")
            print(f"  Dependents: {len(entity_info.get('dependents', {}))}")
            
            # Find related entities
            related = locator.find_related_entities(entity_id, "dependencies")
            print(f"  Related entities: {len(related)}")


def configuration_example():
    """Example of different configuration options."""
    
    print("=== Configuration Examples ===")
    
    # Default configuration
    default_config = LocAgentConfig()
    print(f"Default model: {default_config.agent.model_name}")
    print(f"Default top_k: {default_config.retrieval.top_k}")
    
    # Custom configuration
    custom_config = LocAgentConfig()
    
    # Agent settings
    custom_config.agent.model_name = "gpt-3.5-turbo"
    custom_config.agent.temperature = 0.2
    custom_config.agent.max_tokens = 1500
    
    # Retrieval settings
    custom_config.retrieval.top_k = 20
    custom_config.retrieval.bm25_k1 = 1.5
    custom_config.retrieval.bm25_b = 0.8
    
    # Graph settings
    custom_config.graph.file_extensions = ['.py', '.js', '.ts']
    custom_config.graph.max_depth = 12
    custom_config.graph.skip_dirs.append('migrations')
    
    print(f"Custom model: {custom_config.agent.model_name}")
    print(f"Custom extensions: {custom_config.graph.file_extensions}")
    
    # Save configuration
    from locagent_kernel.utils import save_config
    save_config(custom_config, "my_config.yaml")
    print("Configuration saved to my_config.yaml")


if __name__ == "__main__":
    # Set your repository path here
    if len(os.sys.argv) > 1:
        repo_path = os.sys.argv[1]
        
        # Update the examples to use the provided path
        globals()['repo_path'] = repo_path
        
        print(f"Running examples with repository: {repo_path}")
        
        # Run examples
        basic_localization_example()
        search_example()
        analysis_example()
        configuration_example()
        
    else:
        print("Usage: python basic_usage.py <repository_path>")
        print("\nThis script demonstrates basic usage of LocAgent Kernel.")
        print("Please provide a path to a Python repository to analyze.")
        
        # Show configuration example anyway
        configuration_example()