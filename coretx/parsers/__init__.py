"""
Parser engine for multi-language code analysis.

This module provides universal parsing capabilities using Tree-sitter
with language-specific analyzers for extracting code entities and relationships.
"""

from .base import BaseParser
from .registry import ParserRegistry
from .python_parser import PythonParser
from .javascript_parser import JavaScriptParser
from .typescript_parser import TypeScriptParser

# Create global parser registry instance
parser_registry = ParserRegistry()

__all__ = [
    "BaseParser",
    "ParserRegistry", 
    "PythonParser",
    "JavaScriptParser",
    "TypeScriptParser",
    "parser_registry",
]