"""
Core data models for Coretx.

This module defines the fundamental data structures used throughout the system:
- Code entities (classes, functions, modules, etc.)
- Relationships between entities
- Query and analysis results
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import numpy as np


class EntityType(Enum):
    """Types of code entities that can be analyzed."""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    IMPORT = "import"
    INTERFACE = "interface"
    ENUM = "enum"
    STRUCT = "struct"
    NAMESPACE = "namespace"
    PACKAGE = "package"
    FILE = "file"
    DIRECTORY = "directory"


class RelationshipType(Enum):
    """Types of relationships between code entities."""
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    USES = "uses"
    DEFINES = "defines"
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    OVERRIDES = "overrides"
    REFERENCES = "references"
    INSTANTIATES = "instantiates"
    EXTENDS = "extends"
    ANNOTATED_WITH = "annotated_with"


@dataclass
class CodeEntity:
    """Represents a code entity in the knowledge graph."""
    id: str
    type: EntityType
    name: str
    path: str
    line_start: int
    line_end: int
    description: str = ""
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    content: str = ""
    language: str = ""
    
    def __post_init__(self) -> None:
        """Validate and normalize entity data."""
        if self.line_start < 0:
            self.line_start = 0
        if self.line_end < self.line_start:
            self.line_end = self.line_start
    
    @property
    def qualified_name(self) -> str:
        """Get the fully qualified name of the entity."""
        if self.metadata.get("namespace"):
            return f"{self.metadata['namespace']}.{self.name}"
        return self.name
    
    @property
    def size(self) -> int:
        """Get the size of the entity in lines."""
        return self.line_end - self.line_start + 1


@dataclass
class Relationship:
    """Represents a relationship between two code entities."""
    id: str
    type: RelationshipType
    source_id: str
    target_id: str
    description: str = ""
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    def __post_init__(self) -> None:
        """Validate relationship data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class FileContext:
    """Context information for a specific file."""
    path: str
    content: str
    entities: List[CodeEntity]
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    relevance_score: float = 1.0


@dataclass
class QueryResult:
    """Result of a natural language query."""
    summary: str
    code_context: str
    entities: List[CodeEntity]
    relationships: List[Relationship]
    confidence: float
    suggestions: List[str] = field(default_factory=list)
    files: List[FileContext] = field(default_factory=list)
    diagram: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextResult:
    """Result of context extraction for a specific problem."""
    minimal_closure: str
    files: List[FileContext]
    entry_points: List[CodeEntity]
    flow_diagram: str
    fix_suggestions: List[str] = field(default_factory=list)
    analysis_summary: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceResult:
    """Result of dependency tracing."""
    entity: CodeEntity
    dependencies: List[CodeEntity]
    dependents: List[CodeEntity]
    paths: List[List[CodeEntity]]
    depth: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisConfig:
    """Configuration for code analysis."""
    max_file_size: int = 1048576  # 1MB
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "*.test.js", "*.spec.py", "__pycache__", "node_modules", ".git"
    ])
    include_hidden: bool = False
    max_depth: int = 5
    similarity_threshold: float = 0.7
    include_external_deps: bool = False
    languages: Optional[List[str]] = None
    
    
@dataclass
class LLMConfig:
    """Configuration for LLM integration."""
    provider: str = "openai"
    model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30


@dataclass
class GraphStats:
    """Statistics about the knowledge graph."""
    total_entities: int
    total_relationships: int
    entity_counts: Dict[EntityType, int]
    relationship_counts: Dict[RelationshipType, int]
    language_breakdown: Dict[str, int]
    file_count: int
    total_lines: int
    analysis_time: float
    
    
class AnalysisError(Exception):
    """Base exception for analysis errors."""
    pass


class ParsingError(AnalysisError):
    """Exception raised when parsing fails."""
    pass


class GraphError(AnalysisError):
    """Exception raised during graph operations."""
    pass


class QueryError(AnalysisError):
    """Exception raised during query processing."""
    pass