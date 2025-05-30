"""
Language-specific parsers for the Coretx extension system.
"""

from .python import PythonParser
from .javascript import JavaScriptParser
from .markdown import MarkdownParser
from .html import HTMLParser
from .css import CSSParser

__all__ = [
    'PythonParser',
    'JavaScriptParser', 
    'MarkdownParser',
    'HTMLParser',
    'CSSParser'
]