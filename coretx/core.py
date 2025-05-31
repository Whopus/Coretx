"""
Core Coretx class - the main interface for the intelligent code context engine.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging

from .models import (
    LLMConfig, 
    AnalysisConfig, 
    QueryResult, 
    ContextResult, 
    TraceResult,
    GraphStats,
    AnalysisError
)
from .graph import CodeGraph
from .parsers.registry import parser_registry
from .llm.client import LLMClient
from .llm.embeddings import EmbeddingEngine
from .llm.semantic_analyzer import SemanticAnalyzer
from .llm.query_processor import QueryProcessor
from .analyzer import CodeAnalyzer


class Coretx:
    """
    Intelligent Code Context Engine.
    
    Main interface for building knowledge graphs of codebases and querying them
    with natural language to extract minimal, relevant context for LLMs.
    """
    
    def __init__(
        self,
        parser: str = "auto",
        openai_api_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        model: str = "gpt-4",
        embedding_model: str = "text-embedding-3-small",
        temperature: float = 0.1,
        cache_dir: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Coretx with LLM configuration.
        
        Args:
            parser: Parser type ("auto" for automatic detection)
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            openai_base_url: OpenAI API base URL (optional)
            model: LLM model to use
            embedding_model: Embedding model to use
            temperature: LLM temperature
            cache_dir: Directory for caching embeddings and graphs
            **kwargs: Additional configuration options
        """
        # Set up logging
        self._setup_logging()
        
        # Initialize LLM configuration
        self.llm_config = LLMConfig(
            model=model,
            embedding_model=embedding_model,
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
            api_base=openai_base_url or os.getenv("OPENAI_BASE_URL"),
            temperature=temperature,
            **{k: v for k, v in kwargs.items() if k in LLMConfig.__dataclass_fields__}
        )
        
        # Initialize analysis configuration
        self.analysis_config = AnalysisConfig(
            **{k: v for k, v in kwargs.items() if k in AnalysisConfig.__dataclass_fields__}
        )
        
        # Set up cache directory
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".coretx" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info("Coretx initialized successfully")
    
    def analyze(self, path: str, **options) -> CodeGraph:
        """
        Build a semantic knowledge graph of the codebase.
        
        Args:
            path: Path to the project directory or file
            **options: Analysis options (incremental, max_depth, etc.)
            
        Returns:
            CodeGraph: The constructed knowledge graph
        """
        start_time = time.time()
        project_path = Path(path).resolve()
        
        if not project_path.exists():
            raise AnalysisError(f"Path does not exist: {path}")
        
        self.logger.info(f"Starting analysis of: {project_path}")
        
        # Check for existing graph
        graph_cache_path = project_path / ".coretx" / "graph.json"
        if options.get("incremental", False) and graph_cache_path.exists():
            self.logger.info("Loading existing graph for incremental analysis")
            graph = CodeGraph.load_from_path(str(graph_cache_path))
        else:
            graph = CodeGraph(str(project_path))
        
        # Update analysis config with options
        config = self.analysis_config
        for key, value in options.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # Analyze the codebase
        analyzer = CodeAnalyzer(
            parser_registry=parser_registry,
            semantic_analyzer=self.semantic_analyzer,
            config=config
        )
        
        graph = analyzer.analyze_project(project_path, graph)
        
        # Save the graph
        graph_cache_path.parent.mkdir(parents=True, exist_ok=True)
        graph.save(str(graph_cache_path))
        
        analysis_time = time.time() - start_time
        stats = graph.get_graph_stats()
        stats.analysis_time = analysis_time
        
        self.logger.info(f"Analysis completed in {analysis_time:.2f}s")
        self.logger.info(f"Found {stats.total_entities} entities and {stats.total_relationships} relationships")
        
        return graph
    
    def query(self, graph_or_path: Union[CodeGraph, str], question: str, **options) -> QueryResult:
        """
        Query the codebase using natural language.
        
        Args:
            graph_or_path: CodeGraph instance or path to project
            question: Natural language question
            **options: Query options (max_results, etc.)
            
        Returns:
            QueryResult: Query results with relevant code and explanations
        """
        # Load graph if path provided
        if isinstance(graph_or_path, str):
            graph = self._load_or_analyze_graph(graph_or_path)
        else:
            graph = graph_or_path
        
        self.logger.info(f"Processing query: {question}")
        
        # Process the query
        result = self.query_processor.process_query(
            question, 
            graph, 
            max_results=options.get("max_results", 10)
        )
        
        self.logger.info(f"Query processed with confidence: {result.confidence:.2f}")
        return result
    
    def locate(self, graph_or_path: Union[CodeGraph, str], problem: str, **options) -> ContextResult:
        """
        Find minimal code context for a specific problem.
        
        Args:
            graph_or_path: CodeGraph instance or path to project
            problem: Problem description
            **options: Localization options
            
        Returns:
            ContextResult: Minimal code context for the problem
        """
        # Load graph if path provided
        if isinstance(graph_or_path, str):
            graph = self._load_or_analyze_graph(graph_or_path)
        else:
            graph = graph_or_path
        
        self.logger.info(f"Locating code for problem: {problem}")
        
        # Locate relevant code
        result = self.query_processor.locate_code(problem, graph)
        
        self.logger.info(f"Code located with confidence: {result.confidence:.2f}")
        return result
    
    def trace(self, graph_or_path: Union[CodeGraph, str], entity: str, 
             direction: str = "both", max_depth: int = 3) -> TraceResult:
        """
        Trace dependencies of a code entity.
        
        Args:
            graph_or_path: CodeGraph instance or path to project
            entity: Entity name to trace
            direction: "forward", "backward", or "both"
            max_depth: Maximum depth to trace
            
        Returns:
            TraceResult: Dependency trace results
        """
        # Load graph if path provided
        if isinstance(graph_or_path, str):
            graph = self._load_or_analyze_graph(graph_or_path)
        else:
            graph = graph_or_path
        
        self.logger.info(f"Tracing dependencies for: {entity}")
        
        # Trace dependencies
        result = self.query_processor.trace_dependencies(entity, graph, direction, max_depth)
        
        self.logger.info(f"Traced {len(result.dependencies)} dependencies and {len(result.dependents)} dependents")
        return result
    
    def get_stats(self, graph_or_path: Union[CodeGraph, str]) -> GraphStats:
        """
        Get statistics about the knowledge graph.
        
        Args:
            graph_or_path: CodeGraph instance or path to project
            
        Returns:
            GraphStats: Graph statistics
        """
        # Load graph if path provided
        if isinstance(graph_or_path, str):
            graph = self._load_or_analyze_graph(graph_or_path)
        else:
            graph = graph_or_path
        
        return graph.get_graph_stats()
    
    def export_graph(self, graph_or_path: Union[CodeGraph, str], 
                    output_path: str, format: str = "json") -> None:
        """
        Export the knowledge graph.
        
        Args:
            graph_or_path: CodeGraph instance or path to project
            output_path: Output file path
            format: Export format ("json", "graphml", "cytoscape")
        """
        # Load graph if path provided
        if isinstance(graph_or_path, str):
            graph = self._load_or_analyze_graph(graph_or_path)
        else:
            graph = graph_or_path
        
        if format in ["json", "pickle"]:
            graph.save(output_path, format)
        else:
            graph.export(output_path, format)
        
        self.logger.info(f"Graph exported to: {output_path}")
    
    def update_graph(self, graph: CodeGraph, changed_files: List[str]) -> CodeGraph:
        """
        Update graph with changes to specific files.
        
        Args:
            graph: Existing graph
            changed_files: List of changed file paths
            
        Returns:
            CodeGraph: Updated graph
        """
        self.logger.info(f"Updating graph with {len(changed_files)} changed files")
        
        analyzer = CodeAnalyzer(
            parser_registry=parser_registry,
            semantic_analyzer=self.semantic_analyzer,
            config=self.analysis_config
        )
        
        return analyzer.update_graph(graph, changed_files)
    
    def _initialize_components(self) -> None:
        """Initialize LLM and analysis components."""
        # Initialize LLM client
        self.llm_client = LLMClient(self.llm_config)
        
        # Initialize embedding engine
        self.embedding_engine = EmbeddingEngine(
            self.llm_client, 
            cache_dir=str(self.cache_dir / "embeddings")
        )
        
        # Initialize semantic analyzer
        self.semantic_analyzer = SemanticAnalyzer(
            self.llm_client, 
            self.embedding_engine
        )
        
        # Initialize query processor
        self.query_processor = QueryProcessor(
            self.llm_client, 
            self.embedding_engine
        )
    
    def _load_or_analyze_graph(self, path: str) -> CodeGraph:
        """Load existing graph or analyze project to create one."""
        project_path = Path(path).resolve()
        graph_cache_path = project_path / ".coretx" / "graph.json"
        
        if graph_cache_path.exists():
            self.logger.info(f"Loading existing graph from: {graph_cache_path}")
            return CodeGraph.load_from_path(str(graph_cache_path))
        else:
            self.logger.info(f"No existing graph found, analyzing project: {project_path}")
            return self.analyze(str(project_path))
    
    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        self.logger = logging.getLogger("coretx")
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @classmethod
    def from_config(cls, config_path: str) -> 'Coretx':
        """
        Create Coretx instance from configuration file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Coretx: Configured instance
        """
        import yaml
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Extract LLM config
        llm_config = config.get("llm", {})
        analysis_config = config.get("analysis", {})
        
        return cls(
            openai_api_key=llm_config.get("api_key"),
            openai_base_url=llm_config.get("api_base"),
            model=llm_config.get("model", "gpt-4"),
            embedding_model=llm_config.get("embedding_model", "text-embedding-3-small"),
            temperature=llm_config.get("temperature", 0.1),
            **analysis_config
        )