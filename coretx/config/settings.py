"""Configuration settings for LocAgent Kernel."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class GraphConfig:
    """Configuration for graph construction."""
    
    # Node types
    node_types: List[str] = field(default_factory=lambda: [
        'directory', 'file', 'class', 'function'
    ])
    
    # Edge types  
    edge_types: List[str] = field(default_factory=lambda: [
        'contains', 'inherits', 'invokes', 'imports'
    ])
    
    # Skip directories
    skip_dirs: List[str] = field(default_factory=lambda: [
        '.git', '.github', '__pycache__', '.pytest_cache', 'node_modules'
    ])
    
    # File extensions to process
    file_extensions: List[str] = field(default_factory=lambda: [
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h'
    ])
    
    # Maximum depth for directory traversal
    max_depth: int = 10


@dataclass
class RetrievalConfig:
    """Configuration for retrieval systems."""
    
    # BM25 parameters
    bm25_k1: float = 1.2
    bm25_b: float = 0.75
    
    # Top-k results
    top_k: int = 10
    
    # Fuzzy matching threshold
    fuzzy_threshold: float = 0.8
    
    # Index cache directory
    cache_dir: Optional[Path] = None


@dataclass
class AgentConfig:
    """Configuration for LLM agent."""
    
    # Model configuration
    model_name: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 2048
    
    # API configuration
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    
    # Agent behavior
    max_iterations: int = 10
    timeout: int = 300  # seconds
    
    # Function calling
    use_function_calling: bool = True
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class LocAgentConfig:
    """Main configuration for LocAgent."""
    
    # Sub-configurations
    graph: GraphConfig = field(default_factory=GraphConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    
    # Working directory
    work_dir: Path = field(default_factory=lambda: Path.cwd())
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    # Performance
    num_processes: int = 1
    batch_size: int = 10
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'LocAgentConfig':
        """Create configuration from dictionary."""
        graph_config = GraphConfig(**config_dict.get('graph', {}))
        retrieval_config = RetrievalConfig(**config_dict.get('retrieval', {}))
        agent_config = AgentConfig(**config_dict.get('agent', {}))
        
        return cls(
            graph=graph_config,
            retrieval=retrieval_config,
            agent=agent_config,
            **{k: v for k, v in config_dict.items() 
               if k not in ['graph', 'retrieval', 'agent']}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'graph': self.graph.__dict__,
            'retrieval': self.retrieval.__dict__,
            'agent': self.agent.__dict__,
            'work_dir': str(self.work_dir),
            'log_level': self.log_level,
            'log_file': str(self.log_file) if self.log_file else None,
            'num_processes': self.num_processes,
            'batch_size': self.batch_size
        }