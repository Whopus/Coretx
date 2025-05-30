"""
Multi-language extension system for Coretx.

This module provides a universal extension system that allows Coretx to parse
and analyze code in multiple programming languages and file formats.
"""

from .base import LanguageParser, ParseResult, EntityType
from .registry import LanguageRegistry
from .connectors import CrossLanguageConnector

__all__ = [
    'LanguageParser',
    'ParseResult', 
    'EntityType',
    'LanguageRegistry',
    'CrossLanguageConnector'
]