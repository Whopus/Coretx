"""
Cross-language relationship connectors for building relationships between different languages.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import os
import re
import logging

from .base import ParseResult, EntityType

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of relationships between code entities."""
    IMPORTS = "imports"
    INCLUDES = "includes"
    REFERENCES = "references"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    CALLS = "calls"
    USES = "uses"
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    LINKS_TO = "links_to"
    STYLES = "styles"  # CSS -> HTML
    SCRIPTS = "scripts"  # JS -> HTML
    DOCUMENTS = "documents"  # MD -> Code


@dataclass
class Relationship:
    """Represents a relationship between two entities."""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CrossLanguageConnector:
    """Manages relationships between different languages and file types."""
    
    def __init__(self):
        self.relationships: List[Relationship] = []
        self.entity_map: Dict[str, ParseResult] = {}
        
        # Define common file patterns for cross-language relationships
        self.web_patterns = {
            'css_in_html': re.compile(r'<link[^>]*href=["\']([^"\']*\.css)["\']', re.IGNORECASE),
            'js_in_html': re.compile(r'<script[^>]*src=["\']([^"\']*\.js)["\']', re.IGNORECASE),
            'inline_css': re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE),
            'inline_js': re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE),
        }
        
        self.import_patterns = {
            'python': [
                re.compile(r'from\s+([^\s]+)\s+import'),
                re.compile(r'import\s+([^\s,]+)'),
            ],
            'javascript': [
                re.compile(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'),
                re.compile(r'require\(["\']([^"\']+)["\']\)'),
            ]
        }
    
    def add_entity(self, entity: ParseResult) -> str:
        """Add an entity to the connector and return its ID."""
        entity_id = self._generate_entity_id(entity)
        self.entity_map[entity_id] = entity
        return entity_id
    
    def add_relationship(self, source_id: str, target_id: str, 
                        relationship_type: RelationshipType, 
                        metadata: Dict = None) -> None:
        """Add a relationship between two entities."""
        relationship = Relationship(source_id, target_id, relationship_type, metadata)
        self.relationships.append(relationship)
    
    def discover_relationships(self, entities: List[ParseResult], 
                             project_root: str) -> List[Relationship]:
        """Discover relationships between entities automatically."""
        # Clear existing relationships
        self.relationships.clear()
        self.entity_map.clear()
        
        # Add all entities to the map
        entity_ids = {}
        for entity in entities:
            entity_id = self.add_entity(entity)
            entity_ids[entity.file_path] = entity_id
        
        # Discover different types of relationships
        self._discover_import_relationships(entities, entity_ids, project_root)
        self._discover_web_relationships(entities, entity_ids, project_root)
        self._discover_documentation_relationships(entities, entity_ids, project_root)
        
        return self.relationships
    
    def _discover_import_relationships(self, entities: List[ParseResult], 
                                     entity_ids: Dict[str, str], 
                                     project_root: str) -> None:
        """Discover import/include relationships."""
        for entity in entities:
            if entity.entity_type != EntityType.FILE:
                continue
            
            try:
                with open(entity.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detect language and extract imports
                ext = os.path.splitext(entity.file_path)[1].lower()
                imports = self._extract_imports_by_extension(content, ext)
                
                source_id = entity_ids.get(entity.file_path)
                if not source_id:
                    continue
                
                for import_path in imports:
                    target_file = self._resolve_import_path(import_path, entity.file_path, project_root)
                    target_id = entity_ids.get(target_file)
                    
                    if target_id:
                        self.add_relationship(
                            source_id, target_id, RelationshipType.IMPORTS,
                            {'import_path': import_path}
                        )
            
            except Exception as e:
                logger.debug(f"Error discovering imports for {entity.file_path}: {e}")
    
    def _discover_web_relationships(self, entities: List[ParseResult], 
                                  entity_ids: Dict[str, str], 
                                  project_root: str) -> None:
        """Discover web-specific relationships (HTML -> CSS/JS)."""
        html_files = [e for e in entities if e.file_path.endswith('.html')]
        
        for html_entity in html_files:
            try:
                with open(html_entity.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                source_id = entity_ids.get(html_entity.file_path)
                if not source_id:
                    continue
                
                # Find CSS links
                css_matches = self.web_patterns['css_in_html'].findall(content)
                for css_path in css_matches:
                    target_file = self._resolve_web_path(css_path, html_entity.file_path, project_root)
                    target_id = entity_ids.get(target_file)
                    
                    if target_id:
                        self.add_relationship(
                            source_id, target_id, RelationshipType.STYLES,
                            {'css_path': css_path}
                        )
                
                # Find JS scripts
                js_matches = self.web_patterns['js_in_html'].findall(content)
                for js_path in js_matches:
                    target_file = self._resolve_web_path(js_path, html_entity.file_path, project_root)
                    target_id = entity_ids.get(target_file)
                    
                    if target_id:
                        self.add_relationship(
                            source_id, target_id, RelationshipType.SCRIPTS,
                            {'js_path': js_path}
                        )
            
            except Exception as e:
                logger.debug(f"Error discovering web relationships for {html_entity.file_path}: {e}")
    
    def _discover_documentation_relationships(self, entities: List[ParseResult], 
                                            entity_ids: Dict[str, str], 
                                            project_root: str) -> None:
        """Discover documentation relationships (MD -> Code)."""
        md_files = [e for e in entities if e.file_path.endswith('.md')]
        
        for md_entity in md_files:
            try:
                with open(md_entity.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                source_id = entity_ids.get(md_entity.file_path)
                if not source_id:
                    continue
                
                # Find code references in markdown
                code_refs = re.findall(r'`([^`]+\.(py|js|html|css))`', content)
                for ref, _ in code_refs:
                    target_file = self._resolve_doc_path(ref, md_entity.file_path, project_root)
                    target_id = entity_ids.get(target_file)
                    
                    if target_id:
                        self.add_relationship(
                            source_id, target_id, RelationshipType.DOCUMENTS,
                            {'reference': ref}
                        )
            
            except Exception as e:
                logger.debug(f"Error discovering doc relationships for {md_entity.file_path}: {e}")
    
    def _extract_imports_by_extension(self, content: str, ext: str) -> List[str]:
        """Extract imports based on file extension."""
        imports = []
        
        if ext == '.py':
            patterns = self.import_patterns.get('python', [])
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            patterns = self.import_patterns.get('javascript', [])
        else:
            return imports
        
        for pattern in patterns:
            matches = pattern.findall(content)
            imports.extend(matches)
        
        return imports
    
    def _resolve_import_path(self, import_path: str, source_file: str, project_root: str) -> Optional[str]:
        """Resolve an import path to an actual file path."""
        source_dir = os.path.dirname(source_file)
        
        # Try different resolution strategies
        candidates = []
        
        # Relative import
        if import_path.startswith('.'):
            candidates.append(os.path.join(source_dir, import_path))
        
        # Absolute import from project root
        candidates.append(os.path.join(project_root, import_path))
        
        # Add common extensions
        for candidate in candidates[:]:
            for ext in ['.py', '.js', '.jsx', '.ts', '.tsx']:
                candidates.append(candidate + ext)
        
        # Check which candidate exists
        for candidate in candidates:
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)
        
        return None
    
    def _resolve_web_path(self, web_path: str, source_file: str, project_root: str) -> Optional[str]:
        """Resolve a web path (CSS/JS) to an actual file path."""
        source_dir = os.path.dirname(source_file)
        
        # Remove leading slash for relative resolution
        if web_path.startswith('/'):
            candidate = os.path.join(project_root, web_path[1:])
        else:
            candidate = os.path.join(source_dir, web_path)
        
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
        
        return None
    
    def _resolve_doc_path(self, doc_path: str, source_file: str, project_root: str) -> Optional[str]:
        """Resolve a documentation reference to an actual file path."""
        return self._resolve_web_path(doc_path, source_file, project_root)
    
    def _generate_entity_id(self, entity: ParseResult) -> str:
        """Generate a unique ID for an entity."""
        return f"{entity.entity_type.value}:{entity.file_path}:{entity.name}:{entity.line_start}"
    
    def get_relationships_for_entity(self, entity_id: str) -> List[Relationship]:
        """Get all relationships for a specific entity."""
        return [r for r in self.relationships 
                if r.source_id == entity_id or r.target_id == entity_id]
    
    def get_relationships_by_type(self, relationship_type: RelationshipType) -> List[Relationship]:
        """Get all relationships of a specific type."""
        return [r for r in self.relationships if r.relationship_type == relationship_type]