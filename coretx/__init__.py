"""
Coretx - Intelligent Code Context Engine

A lightweight kernel for building comprehensive knowledge graphs of your codebase,
enabling LLMs to understand and reason about code with minimal context.
"""

from .core import Coretx
from .graph import CodeGraph
from .models import (
    CodeEntity,
    Relationship,
    QueryResult,
    ContextResult,
    TraceResult,
    LLMConfig,
    AnalysisConfig,
    EntityType,
    RelationshipType,
)
from .parsers.registry import parser_registry

__version__ = "0.1.0"
__author__ = "Coretx Team"
__email__ = "team@coretx.dev"

__all__ = [
    "Coretx",
    "CodeGraph", 
    "CodeEntity",
    "Relationship",
    "QueryResult",
    "ContextResult",
    "TraceResult",
    "LLMConfig",
    "AnalysisConfig",
    "EntityType",
    "RelationshipType",
    "parser_registry",
]