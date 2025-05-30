"""
Base classes for language parsers in the Coretx extension system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Set
import os


class EntityType(Enum):
    """Types of code entities that can be extracted."""
    FILE = "file"
    DIRECTORY = "directory"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    IMPORT = "import"
    MODULE = "module"
    INTERFACE = "interface"
    ENUM = "enum"
    STRUCT = "struct"
    NAMESPACE = "namespace"
    
    # Web-specific entities
    HTML_ELEMENT = "html_element"
    CSS_RULE = "css_rule"
    CSS_SELECTOR = "css_selector"
    CSS_PROPERTY = "css_property"
    
    # Documentation entities
    HEADING = "heading"
    LINK = "link"
    CODE_BLOCK = "code_block"
    TEXT_SECTION = "text_section"


@dataclass
class ParseResult:
    """Result of parsing a code entity."""
    name: str
    entity_type: EntityType
    file_path: str
    line_start: int
    line_end: int
    content: str = ""
    docstring: Optional[str] = None
    metadata: Dict[str, Any] = None
    children: List['ParseResult'] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.children is None:
            self.children = []
        if self.dependencies is None:
            self.dependencies = []


class LanguageParser(ABC):
    """Base class for all language parsers."""
    
    def __init__(self):
        self.supported_extensions: Set[str] = set()
        self.language_name: str = ""
        self.parser_version: str = "1.0.0"
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file."""
        pass
    
    @abstractmethod
    def parse_file(self, file_path: str) -> List[ParseResult]:
        """Parse a file and extract code entities."""
        pass
    
    @abstractmethod
    def extract_dependencies(self, file_path: str) -> List[str]:
        """Extract file dependencies (imports, includes, etc.)."""
        pass
    
    def get_file_type(self, file_path: str) -> EntityType:
        """Determine the file type based on extension."""
        if os.path.isdir(file_path):
            return EntityType.DIRECTORY
        return EntityType.FILE
    
    def get_language_info(self) -> Dict[str, Any]:
        """Get information about this language parser."""
        return {
            'name': self.language_name,
            'version': self.parser_version,
            'supported_extensions': list(self.supported_extensions),
            'entity_types': [et.value for et in self.get_supported_entity_types()]
        }
    
    @abstractmethod
    def get_supported_entity_types(self) -> List[EntityType]:
        """Get the entity types this parser can extract."""
        pass
    
    def validate_parse_result(self, result: ParseResult) -> bool:
        """Validate a parse result."""
        if not result.name or not result.file_path:
            return False
        if result.line_start < 0 or result.line_end < result.line_start:
            return False
        return True
    
    def post_process_results(self, results: List[ParseResult]) -> List[ParseResult]:
        """Post-process parse results (override in subclasses if needed)."""
        return [r for r in results if self.validate_parse_result(r)]


class BaseFileParser(LanguageParser):
    """Base parser for simple file-based parsing."""
    
    def __init__(self, extensions: Set[str], language_name: str):
        super().__init__()
        self.supported_extensions = extensions
        self.language_name = language_name
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file extension is supported."""
        if os.path.isdir(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
    
    def extract_dependencies(self, file_path: str) -> List[str]:
        """Default implementation returns empty dependencies."""
        return []
    
    def get_supported_entity_types(self) -> List[EntityType]:
        """Default supported entity types."""
        return [EntityType.FILE]


class CodeParser(LanguageParser):
    """Base class for programming language parsers."""
    
    def get_supported_entity_types(self) -> List[EntityType]:
        """Common entity types for programming languages."""
        return [
            EntityType.FILE,
            EntityType.CLASS,
            EntityType.FUNCTION,
            EntityType.METHOD,
            EntityType.VARIABLE,
            EntityType.IMPORT,
            EntityType.MODULE
        ]
    
    def extract_imports(self, content: str) -> List[str]:
        """Extract import statements (to be implemented by subclasses)."""
        return []
    
    def extract_classes(self, content: str, file_path: str) -> List[ParseResult]:
        """Extract class definitions (to be implemented by subclasses)."""
        return []
    
    def extract_functions(self, content: str, file_path: str) -> List[ParseResult]:
        """Extract function definitions (to be implemented by subclasses)."""
        return []