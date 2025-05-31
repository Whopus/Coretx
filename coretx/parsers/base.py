"""
Base parser interface and common functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import tree_sitter
from pathlib import Path

from ..models import CodeEntity, Relationship, EntityType, RelationshipType, ParsingError


class BaseParser(ABC):
    """Base class for language-specific parsers."""
    
    def __init__(self, language: str):
        self.language = language
        self._parser = None
        self._tree_sitter_language = None
        
    @property
    @abstractmethod
    def file_extensions(self) -> List[str]:
        """File extensions this parser handles."""
        pass
    
    @property
    @abstractmethod
    def tree_sitter_language_name(self) -> str:
        """Name of the tree-sitter language."""
        pass
    
    def initialize(self) -> None:
        """Initialize the tree-sitter parser."""
        try:
            # Import the specific tree-sitter language
            language_module = __import__(
                f"tree_sitter_{self.tree_sitter_language_name}",
                fromlist=["language"]
            )
            self._tree_sitter_language = tree_sitter.Language(language_module.language())
            
            # Create parser
            self._parser = tree_sitter.Parser()
            self._parser.language = self._tree_sitter_language
            
        except ImportError as e:
            raise ParsingError(
                f"Tree-sitter language '{self.tree_sitter_language_name}' not available: {e}"
            )
    
    def parse_file(self, file_path: str) -> Tuple[List[CodeEntity], List[Relationship]]:
        """Parse a file and extract entities and relationships."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_content(content, file_path)
        except Exception as e:
            raise ParsingError(f"Failed to parse file {file_path}: {e}")
    
    def parse_content(self, content: str, file_path: str) -> Tuple[List[CodeEntity], List[Relationship]]:
        """Parse content and extract entities and relationships."""
        if not self._parser:
            self.initialize()
            
        try:
            # Parse with tree-sitter
            tree = self._parser.parse(content.encode('utf-8'))
            
            # Extract entities and relationships
            entities = self._extract_entities(tree.root_node, content, file_path)
            relationships = self._extract_relationships(tree.root_node, content, file_path, entities)
            
            return entities, relationships
            
        except Exception as e:
            raise ParsingError(f"Failed to parse content: {e}")
    
    @abstractmethod
    def _extract_entities(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract code entities from the AST."""
        pass
    
    @abstractmethod
    def _extract_relationships(
        self, 
        root_node, 
        content: str, 
        file_path: str, 
        entities: List[CodeEntity]
    ) -> List[Relationship]:
        """Extract relationships between entities."""
        pass
    
    def _get_node_text(self, node, content: str) -> str:
        """Get the text content of a tree-sitter node."""
        return content[node.start_byte:node.end_byte]
    
    def _get_line_numbers(self, node) -> Tuple[int, int]:
        """Get start and end line numbers for a node (1-indexed)."""
        return node.start_point[0] + 1, node.end_point[0] + 1
    
    def _create_entity_id(self, entity_type: EntityType, name: str, file_path: str, line: int) -> str:
        """Create a unique ID for an entity."""
        return f"{entity_type.value}:{Path(file_path).name}:{name}:{line}"
    
    def _create_relationship_id(self, source_id: str, target_id: str, rel_type: RelationshipType) -> str:
        """Create a unique ID for a relationship."""
        return f"{source_id}->{rel_type.value}->{target_id}"
    
    def _find_nodes_by_type(self, root_node, node_type: str) -> List:
        """Find all nodes of a specific type in the AST."""
        nodes = []
        
        def traverse(node):
            if node.type == node_type:
                nodes.append(node)
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return nodes
    
    def _get_parent_context(self, node, content: str) -> Optional[str]:
        """Get the parent context (class/namespace) for a node."""
        current = node.parent
        while current:
            if current.type in ['class_definition', 'class_declaration', 'namespace_definition']:
                # Find the name node
                for child in current.children:
                    if child.type in ['identifier', 'type_identifier']:
                        return self._get_node_text(child, content)
            current = current.parent
        return None
    
    def _extract_imports(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract import statements (common across languages)."""
        entities = []
        import_nodes = self._find_nodes_by_type(root_node, 'import_statement')
        
        for node in import_nodes:
            line_start, line_end = self._get_line_numbers(node)
            import_text = self._get_node_text(node, content)
            
            entity = CodeEntity(
                id=self._create_entity_id(EntityType.IMPORT, import_text, file_path, line_start),
                type=EntityType.IMPORT,
                name=import_text,
                path=file_path,
                line_start=line_start,
                line_end=line_end,
                content=import_text,
                language=self.language,
                metadata={"raw_import": import_text}
            )
            entities.append(entity)
        
        return entities
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file."""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.file_extensions