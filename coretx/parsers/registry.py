"""
Parser registry for managing language-specific parsers.
"""

from typing import Dict, List, Optional, Type
from pathlib import Path

from .base import BaseParser
from ..models import ParsingError


class ParserRegistry:
    """Registry for managing and selecting appropriate parsers."""
    
    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}
        self._extension_map: Dict[str, str] = {}
        self._register_default_parsers()
    
    def register_parser(self, language: str, parser_class: Type[BaseParser]) -> None:
        """Register a parser for a specific language."""
        parser = parser_class(language)
        self._parsers[language] = parser
        
        # Update extension mapping
        for ext in parser.file_extensions:
            self._extension_map[ext] = language
    
    def get_parser(self, language: str) -> Optional[BaseParser]:
        """Get parser for a specific language."""
        return self._parsers.get(language)
    
    def get_parser_for_file(self, file_path: str) -> Optional[BaseParser]:
        """Get appropriate parser for a file based on its extension."""
        file_ext = Path(file_path).suffix.lower()
        language = self._extension_map.get(file_ext)
        
        if language:
            return self._parsers.get(language)
        return None
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect the programming language of a file."""
        file_ext = Path(file_path).suffix.lower()
        return self._extension_map.get(file_ext)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self._parsers.keys())
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return list(self._extension_map.keys())
    
    def _register_default_parsers(self) -> None:
        """Register default parsers for common languages."""
        try:
            from .python_parser import PythonParser
            self.register_parser("python", PythonParser)
        except ImportError:
            pass
        
        try:
            from .javascript_parser import JavaScriptParser
            self.register_parser("javascript", JavaScriptParser)
        except ImportError:
            pass
        
        try:
            from .typescript_parser import TypeScriptParser
            self.register_parser("typescript", TypeScriptParser)
        except ImportError:
            pass
    
    def parse_file(self, file_path: str) -> tuple:
        """Parse a file using the appropriate parser."""
        parser = self.get_parser_for_file(file_path)
        if not parser:
            raise ParsingError(f"No parser available for file: {file_path}")
        
        return parser.parse_file(file_path)
    
    def can_parse(self, file_path: str) -> bool:
        """Check if any parser can handle the given file."""
        return self.get_parser_for_file(file_path) is not None


# Global parser registry instance
parser_registry = ParserRegistry()