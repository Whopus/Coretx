"""
Language parser registry for managing multiple language parsers.
"""

from typing import Dict, List, Optional, Type
import os
import logging
from .base import LanguageParser, ParseResult

logger = logging.getLogger(__name__)


class LanguageRegistry:
    """Registry for managing language parsers."""
    
    def __init__(self):
        self._parsers: Dict[str, LanguageParser] = {}
        self._extension_map: Dict[str, str] = {}  # extension -> parser_name
        self._initialized = False
    
    def register_parser(self, name: str, parser: LanguageParser) -> None:
        """Register a language parser."""
        self._parsers[name] = parser
        
        # Update extension mapping
        for ext in parser.supported_extensions:
            if ext in self._extension_map:
                logger.warning(f"Extension {ext} already mapped to {self._extension_map[ext]}, overriding with {name}")
            self._extension_map[ext] = name
        
        logger.info(f"Registered parser '{name}' for extensions: {parser.supported_extensions}")
    
    def get_parser(self, name: str) -> Optional[LanguageParser]:
        """Get a parser by name."""
        return self._parsers.get(name)
    
    def get_parser_for_file(self, file_path: str) -> Optional[LanguageParser]:
        """Get the appropriate parser for a file."""
        if os.path.isdir(file_path):
            return None
        
        ext = os.path.splitext(file_path)[1].lower()
        parser_name = self._extension_map.get(ext)
        
        if parser_name:
            return self._parsers.get(parser_name)
        
        # Fallback: check all parsers
        for parser in self._parsers.values():
            if parser.can_parse(file_path):
                return parser
        
        return None
    
    def parse_file(self, file_path: str) -> List[ParseResult]:
        """Parse a file using the appropriate parser."""
        parser = self.get_parser_for_file(file_path)
        if not parser:
            logger.debug(f"No parser found for file: {file_path}")
            return []
        
        try:
            results = parser.parse_file(file_path)
            return parser.post_process_results(results)
        except Exception as e:
            logger.error(f"Error parsing file {file_path} with {parser.language_name}: {e}")
            return []
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions."""
        return list(self._extension_map.keys())
    
    def get_registered_parsers(self) -> Dict[str, Dict]:
        """Get information about all registered parsers."""
        return {
            name: parser.get_language_info() 
            for name, parser in self._parsers.items()
        }
    
    def initialize_default_parsers(self) -> None:
        """Initialize default language parsers."""
        if self._initialized:
            return
        
        try:
            # Import and register default parsers
            from .languages.python import PythonParser
            from .languages.javascript import JavaScriptParser
            from .languages.markdown import MarkdownParser
            from .languages.html import HTMLParser
            from .languages.css import CSSParser
            
            self.register_parser('python', PythonParser())
            self.register_parser('javascript', JavaScriptParser())
            self.register_parser('markdown', MarkdownParser())
            self.register_parser('html', HTMLParser())
            self.register_parser('css', CSSParser())
            
            self._initialized = True
            logger.info("Default language parsers initialized")
            
        except ImportError as e:
            logger.error(f"Failed to initialize default parsers: {e}")
    
    def clear(self) -> None:
        """Clear all registered parsers."""
        self._parsers.clear()
        self._extension_map.clear()
        self._initialized = False


# Global registry instance
registry = LanguageRegistry()