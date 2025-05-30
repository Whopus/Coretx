"""
LocAgent Kernel - A modular code localization engine.

This package provides a clean, engineered kernel for code localization using:
- Graph-based code analysis
- Hybrid retrieval (BM25 + graph search)
- LLM agents with specialized tools
- Minimal, composable architecture

Main Components:
- CodeLocator: Main interface for code localization
- GraphBuilder: Constructs code dependency graphs
- HybridRetriever: Combines text and structural search
- LocalizationAgent: LLM agent with code analysis tools
"""

from .core.locator import CodeLocator
from .core.graph import GraphBuilder, GraphSearcher, NodeType, EdgeType
from .core.retrieval import BM25Retriever, HybridRetriever
from .core.agent import LocalizationAgent, ToolRegistry
from .config import LocAgentConfig, GraphConfig, RetrievalConfig, AgentConfig
from .utils import setup_logger, load_config, save_config

__version__ = "1.0.0"
__author__ = "LocAgent Team"

# Main exports
__all__ = [
    # Main interface
    'CodeLocator',
    
    # Core components
    'GraphBuilder',
    'GraphSearcher', 
    'BM25Retriever',
    'HybridRetriever',
    'LocalizationAgent',
    'ToolRegistry',
    
    # Types
    'NodeType',
    'EdgeType',
    
    # Configuration
    'LocAgentConfig',
    'GraphConfig', 
    'RetrievalConfig',
    'AgentConfig',
    
    # Utilities
    'setup_logger',
    'load_config',
    'save_config'
]


def create_locator(repo_path: str, config_path: str = None, 
                  openai_api_key: str = None, openai_base_url: str = None, 
                  **kwargs) -> CodeLocator:
    """
    Convenience function to create and initialize a CodeLocator.
    
    Args:
        repo_path: Path to the repository to analyze
        config_path: Optional path to configuration file
        openai_api_key: OpenAI API key (overrides config file and environment)
        openai_base_url: OpenAI base URL (overrides config file)
        **kwargs: Additional configuration overrides
        
    Returns:
        Initialized CodeLocator instance
    """
    # Load configuration
    if config_path:
        config = load_config(config_path)
        if config is None:
            raise ValueError(f"Failed to load configuration from {config_path}")
    else:
        config = LocAgentConfig()
    
    # Apply OpenAI configuration if provided
    if openai_api_key is not None:
        config.agent.api_key = openai_api_key
    if openai_base_url is not None:
        config.agent.api_base = openai_base_url
    
    # Apply any other overrides
    if kwargs:
        from .utils.config_utils import merge_configs
        config = merge_configs(config, kwargs)
    
    # Create and initialize locator
    locator = CodeLocator(config)
    locator.initialize(repo_path)
    
    return locator


def quick_localize(repo_path: str, problem_description: str, 
                  model_name: str = "gpt-4", openai_api_key: str = None, 
                  openai_base_url: str = None, **kwargs) -> dict:
    """
    Quick localization function for simple use cases.
    
    Args:
        repo_path: Path to the repository
        problem_description: Description of the issue to locate
        model_name: LLM model to use
        openai_api_key: OpenAI API key (overrides environment)
        openai_base_url: OpenAI base URL (for custom endpoints)
        **kwargs: Additional configuration options
        
    Returns:
        Localization results
    """
    # Create configuration
    config = LocAgentConfig()
    config.agent.model_name = model_name
    
    # Apply OpenAI configuration if provided
    if openai_api_key is not None:
        config.agent.api_key = openai_api_key
    if openai_base_url is not None:
        config.agent.api_base = openai_base_url
    
    # Apply other overrides
    if kwargs:
        from .utils.config_utils import merge_configs
        config = merge_configs(config, kwargs)
    
    # Create and use locator
    locator = CodeLocator(config)
    locator.initialize(repo_path)
    
    return locator.localize(problem_description)