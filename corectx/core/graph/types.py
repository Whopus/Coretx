"""Type definitions for graph components."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path


class NodeType(Enum):
    """Types of nodes in the code graph."""
    DIRECTORY = "directory"
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"


class EdgeType(Enum):
    """Types of edges in the code graph."""
    CONTAINS = "contains"
    INHERITS = "inherits"
    INVOKES = "invokes"
    IMPORTS = "imports"


@dataclass
class CodeNode:
    """Represents a node in the code graph."""
    
    id: str
    name: str
    node_type: NodeType
    path: Optional[Path] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_directory(self) -> bool:
        return self.node_type == NodeType.DIRECTORY
    
    @property
    def is_file(self) -> bool:
        return self.node_type == NodeType.FILE
    
    @property
    def is_class(self) -> bool:
        return self.node_type == NodeType.CLASS
    
    @property
    def is_function(self) -> bool:
        return self.node_type == NodeType.FUNCTION


@dataclass
class CodeEdge:
    """Represents an edge in the code graph."""
    
    source: str
    target: str
    edge_type: EdgeType
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class GraphStats:
    """Statistics about the code graph."""
    
    total_nodes: int
    total_edges: int
    node_counts: Dict[NodeType, int]
    edge_counts: Dict[EdgeType, int]
    max_depth: int
    
    def __str__(self) -> str:
        lines = [
            f"Graph Statistics:",
            f"  Total Nodes: {self.total_nodes}",
            f"  Total Edges: {self.total_edges}",
            f"  Max Depth: {self.max_depth}",
            f"  Node Distribution:"
        ]
        
        for node_type, count in self.node_counts.items():
            lines.append(f"    {node_type.value}: {count}")
        
        lines.append(f"  Edge Distribution:")
        for edge_type, count in self.edge_counts.items():
            lines.append(f"    {edge_type.value}: {count}")
        
        return "\n".join(lines)