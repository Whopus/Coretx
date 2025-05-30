"""Main code locator class - the kernel of LocAgent."""

import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

from ..graph import GraphBuilder, GraphSearcher
from ..retrieval import HybridRetriever
from ..agent import LocalizationAgent, ToolRegistry
from .tools import setup_localization_tools
from ...config import LocAgentConfig

logger = logging.getLogger(__name__)


class CodeLocator:
    """
    Main class for code localization using graph-guided LLM agents.
    
    This is the kernel of LocAgent that combines:
    - Code graph construction and search
    - Hybrid retrieval (BM25 + graph-based)
    - LLM agent with specialized tools
    """
    
    def __init__(self, config: LocAgentConfig):
        self.config = config
        
        # Core components
        self.graph_builder = GraphBuilder(config.graph)
        self.graph_searcher: Optional[GraphSearcher] = None
        self.retriever = HybridRetriever(config.retrieval)
        self.agent = LocalizationAgent(config.agent)
        self.tool_registry = ToolRegistry()
        
        # State
        self.graph = None
        self.repo_path: Optional[Path] = None
        self.is_initialized = False
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logging.getLogger().addHandler(file_handler)
    
    def initialize(self, repo_path: Union[str, Path], 
                  force_rebuild: bool = False) -> None:
        """
        Initialize the locator with a repository.
        
        Args:
            repo_path: Path to the repository to analyze
            force_rebuild: Whether to force rebuilding the graph and indices
        """
        self.repo_path = Path(repo_path)
        
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        logger.info(f"Initializing LocAgent for repository: {repo_path}")
        
        # Check for cached indices
        cache_dir = self._get_cache_dir()
        graph_cache = cache_dir / "graph.pkl"
        retrieval_cache = cache_dir / "retrieval"
        
        if not force_rebuild and graph_cache.exists() and retrieval_cache.exists():
            logger.info("Loading cached indices...")
            self._load_cached_indices(graph_cache, retrieval_cache)
        else:
            logger.info("Building indices from scratch...")
            self._build_indices()
            self._save_indices(graph_cache, retrieval_cache)
        
        # Setup tools for the agent
        setup_localization_tools(
            self.tool_registry,
            self.graph_searcher,
            self.retriever,
            self.repo_path
        )
        
        # Register tools with agent
        for name, tool_func in self.tool_registry.get_tools().items():
            self.agent.add_tool(name, tool_func)
        
        self.is_initialized = True
        logger.info("LocAgent initialization completed")
    
    def _get_cache_dir(self) -> Path:
        """Get cache directory for this repository."""
        if self.config.retrieval.cache_dir:
            cache_dir = self.config.retrieval.cache_dir
        else:
            cache_dir = self.config.work_dir / ".locagent_cache"
        
        # Create subdirectory based on repo path hash
        import hashlib
        repo_hash = hashlib.md5(str(self.repo_path).encode()).hexdigest()[:8]
        cache_dir = cache_dir / repo_hash
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        return cache_dir
    
    def _build_indices(self) -> None:
        """Build graph and retrieval indices."""
        # Build graph
        logger.info("Building code dependency graph...")
        self.graph = self.graph_builder.build_graph(self.repo_path)
        self.graph_searcher = GraphSearcher(self.graph, self.config.graph)
        
        # Print graph statistics
        stats = self.graph_builder.get_stats()
        logger.info(f"Graph built successfully:\n{stats}")
        
        # Build retrieval index
        logger.info("Building retrieval index...")
        self.retriever.build_index(self.graph, self.repo_path)
    
    def _save_indices(self, graph_cache: Path, retrieval_cache: Path) -> None:
        """Save indices to cache."""
        logger.info("Saving indices to cache...")
        
        # Save graph
        with open(graph_cache, 'wb') as f:
            pickle.dump(self.graph, f)
        
        # Save retrieval index
        retrieval_cache.mkdir(exist_ok=True)
        self.retriever.save_index(retrieval_cache)
    
    def _load_cached_indices(self, graph_cache: Path, retrieval_cache: Path) -> None:
        """Load indices from cache."""
        # Load graph
        with open(graph_cache, 'rb') as f:
            self.graph = pickle.load(f)
        
        self.graph_searcher = GraphSearcher(self.graph, self.config.graph)
        
        # Load retrieval index
        self.retriever.load_index(retrieval_cache, self.graph)
    
    def localize(self, problem_description: str, 
                repository_context: str = "") -> Dict[str, Any]:
        """
        Perform code localization for a given problem.
        
        Args:
            problem_description: Description of the issue/bug to locate
            repository_context: Additional context about the repository
            
        Returns:
            Dictionary containing localization results
        """
        if not self.is_initialized:
            raise ValueError("Locator not initialized. Call initialize() first.")
        
        logger.info("Starting code localization...")
        logger.debug(f"Problem: {problem_description}")
        
        # Use the agent to perform localization
        result = self.agent.localize_code(problem_description, repository_context)
        
        # Enhance results with additional analysis
        enhanced_result = self._enhance_localization_results(result)
        
        logger.info("Code localization completed")
        return enhanced_result
    
    def _enhance_localization_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance localization results with additional analysis."""
        localization_results = result.get('localization_results', {})
        
        # Add graph statistics
        if self.graph:
            stats = self.graph_builder.get_stats()
            result['graph_stats'] = stats.to_dict() if hasattr(stats, 'to_dict') else str(stats)
        
        # Add repository information
        result['repository_info'] = {
            'path': str(self.repo_path),
            'total_files': len(list(self.repo_path.rglob('*.py'))),
        }
        
        return result
    
    def search(self, query: str, search_type: str = "hybrid", 
              top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search the codebase using various methods.
        
        Args:
            query: Search query
            search_type: Type of search ("hybrid", "text", "graph", "structure")
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.is_initialized:
            raise ValueError("Locator not initialized. Call initialize() first.")
        
        return self.retriever.search(query, search_type, top_k)
    
    def get_entity_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a code entity."""
        if not self.graph_searcher:
            return None
        
        return self.graph_searcher.get_node_info(entity_id)
    
    def get_file_entities(self, file_path: str) -> List[str]:
        """Get all entities (classes, functions) in a file."""
        if not self.graph_searcher:
            return []
        
        return self.graph_searcher.get_file_entities(file_path)
    
    def find_related_entities(self, entity_id: str, 
                             relation_type: str = "all") -> List[Dict[str, Any]]:
        """Find entities related to a given entity."""
        if not self.retriever:
            return []
        
        return self.retriever.find_related_entities(entity_id, relation_type)
    
    def get_graph_stats(self) -> Optional[Dict[str, Any]]:
        """Get statistics about the code graph."""
        if not self.graph_builder:
            return None
        
        stats = self.graph_builder.get_stats()
        return {
            'total_nodes': stats.total_nodes,
            'total_edges': stats.total_edges,
            'node_counts': {nt.value: count for nt, count in stats.node_counts.items()},
            'edge_counts': {et.value: count for et, count in stats.edge_counts.items()},
            'max_depth': stats.max_depth
        }
    
    def export_graph(self, output_path: Path, format: str = "gexf") -> None:
        """Export the code graph to a file."""
        if not self.graph:
            raise ValueError("Graph not built")
        
        import networkx as nx
        
        if format.lower() == "gexf":
            nx.write_gexf(self.graph, output_path)
        elif format.lower() == "graphml":
            nx.write_graphml(self.graph, output_path)
        elif format.lower() == "json":
            from networkx.readwrite import json_graph
            import json
            
            graph_data = json_graph.node_link_data(self.graph)
            with open(output_path, 'w') as f:
                json.dump(graph_data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Graph exported to {output_path}")
    
    def clear_cache(self) -> None:
        """Clear cached indices."""
        cache_dir = self._get_cache_dir()
        
        import shutil
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            logger.info("Cache cleared")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for the agent."""
        return self.tool_registry.list_tools()