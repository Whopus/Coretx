"""
TypeScript-specific parser implementation.
"""

from typing import List, Dict, Any, Optional
from .javascript_parser import JavaScriptParser
from ..models import CodeEntity, Relationship, EntityType, RelationshipType


class TypeScriptParser(JavaScriptParser):
    """Parser for TypeScript source code."""
    
    @property
    def file_extensions(self) -> List[str]:
        return ['.ts', '.tsx']
    
    @property
    def tree_sitter_language_name(self) -> str:
        return "typescript"
    
    def _extract_entities(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract TypeScript entities from the AST."""
        entities = []
        
        # Get base JavaScript entities
        entities.extend(super()._extract_entities(root_node, content, file_path))
        
        # Extract TypeScript-specific entities
        entities.extend(self._extract_ts_interfaces(root_node, content, file_path))
        entities.extend(self._extract_ts_types(root_node, content, file_path))
        entities.extend(self._extract_ts_enums(root_node, content, file_path))
        
        return entities
    
    def _extract_ts_interfaces(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract TypeScript interface declarations."""
        entities = []
        
        interface_nodes = self._find_nodes_by_type(root_node, 'interface_declaration')
        for node in interface_nodes:
            line_start, line_end = self._get_line_numbers(node)
            interface_content = self._get_node_text(node, content)
            
            # Extract interface name
            interface_name = self._extract_ts_interface_name(node, content)
            if not interface_name:
                continue
            
            entity = CodeEntity(
                id=self._create_entity_id(EntityType.INTERFACE, interface_name, file_path, line_start),
                type=EntityType.INTERFACE,
                name=interface_name,
                path=file_path,
                line_start=line_start,
                line_end=line_end,
                description=f"TypeScript interface: {interface_name}",
                content=interface_content,
                language=self.language,
                metadata={
                    "extends": self._extract_ts_interface_extends(node, content),
                    "properties": self._extract_ts_interface_properties(node, content)
                }
            )
            entities.append(entity)
        
        return entities
    
    def _extract_ts_types(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract TypeScript type alias declarations."""
        entities = []
        
        type_nodes = self._find_nodes_by_type(root_node, 'type_alias_declaration')
        for node in type_nodes:
            line_start, line_end = self._get_line_numbers(node)
            type_content = self._get_node_text(node, content)
            
            # Extract type name
            type_name = self._extract_ts_type_name(node, content)
            if not type_name:
                continue
            
            entity = CodeEntity(
                id=self._create_entity_id(EntityType.INTERFACE, type_name, file_path, line_start),  # Using INTERFACE for types
                type=EntityType.INTERFACE,
                name=type_name,
                path=file_path,
                line_start=line_start,
                line_end=line_end,
                description=f"TypeScript type: {type_name}",
                content=type_content,
                language=self.language,
                metadata={
                    "is_type_alias": True,
                    "type_definition": type_content
                }
            )
            entities.append(entity)
        
        return entities
    
    def _extract_ts_enums(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract TypeScript enum declarations."""
        entities = []
        
        enum_nodes = self._find_nodes_by_type(root_node, 'enum_declaration')
        for node in enum_nodes:
            line_start, line_end = self._get_line_numbers(node)
            enum_content = self._get_node_text(node, content)
            
            # Extract enum name
            enum_name = self._extract_ts_enum_name(node, content)
            if not enum_name:
                continue
            
            entity = CodeEntity(
                id=self._create_entity_id(EntityType.ENUM, enum_name, file_path, line_start),
                type=EntityType.ENUM,
                name=enum_name,
                path=file_path,
                line_start=line_start,
                line_end=line_end,
                description=f"TypeScript enum: {enum_name}",
                content=enum_content,
                language=self.language,
                metadata={
                    "enum_members": self._extract_ts_enum_members(node, content),
                    "is_const_enum": "const enum" in enum_content[:20]
                }
            )
            entities.append(entity)
        
        return entities
    
    def _create_module_entity(self, file_path: str, content: str) -> CodeEntity:
        """Create entity for the TypeScript module."""
        from pathlib import Path
        
        module_name = Path(file_path).stem
        line_count = len(content.splitlines())
        
        return CodeEntity(
            id=self._create_entity_id(EntityType.MODULE, module_name, file_path, 1),
            type=EntityType.MODULE,
            name=module_name,
            path=file_path,
            line_start=1,
            line_end=line_count,
            description=f"TypeScript module: {module_name}",
            content=content,
            language=self.language,
            metadata={
                "line_count": line_count,
                "is_es_module": "import " in content or "export " in content,
                "has_types": any(keyword in content for keyword in ["interface", "type ", "enum"]),
                "is_declaration_file": file_path.endswith('.d.ts')
            }
        )
    
    # Helper methods for TypeScript-specific extraction
    
    def _extract_ts_interface_name(self, node, content: str) -> Optional[str]:
        """Extract interface name from interface declaration."""
        for child in node.children:
            if child.type == 'type_identifier':
                return self._get_node_text(child, content)
        return None
    
    def _extract_ts_interface_extends(self, node, content: str) -> List[str]:
        """Extract extends clause from interface."""
        extends = []
        for child in node.children:
            if child.type == 'extends_clause':
                # Find type identifiers in extends clause
                type_ids = self._find_nodes_by_type(child, 'type_identifier')
                for type_id in type_ids:
                    extends.append(self._get_node_text(type_id, content))
        return extends
    
    def _extract_ts_interface_properties(self, node, content: str) -> List[Dict[str, Any]]:
        """Extract properties from interface."""
        properties = []
        
        # Find object type body
        for child in node.children:
            if child.type == 'object_type':
                prop_sigs = self._find_nodes_by_type(child, 'property_signature')
                for prop_sig in prop_sigs:
                    prop_name = None
                    prop_type = None
                    
                    for prop_child in prop_sig.children:
                        if prop_child.type == 'property_identifier':
                            prop_name = self._get_node_text(prop_child, content)
                        elif prop_child.type in ['type_annotation', 'predefined_type']:
                            prop_type = self._get_node_text(prop_child, content)
                    
                    if prop_name:
                        properties.append({
                            "name": prop_name,
                            "type": prop_type,
                            "optional": "?" in self._get_node_text(prop_sig, content)
                        })
        
        return properties
    
    def _extract_ts_type_name(self, node, content: str) -> Optional[str]:
        """Extract type name from type alias declaration."""
        for child in node.children:
            if child.type == 'type_identifier':
                return self._get_node_text(child, content)
        return None
    
    def _extract_ts_enum_name(self, node, content: str) -> Optional[str]:
        """Extract enum name from enum declaration."""
        for child in node.children:
            if child.type == 'identifier':
                return self._get_node_text(child, content)
        return None
    
    def _extract_ts_enum_members(self, node, content: str) -> List[str]:
        """Extract enum members."""
        members = []
        
        # Find enum body
        for child in node.children:
            if child.type == 'enum_body':
                # Find property identifiers
                identifiers = self._find_nodes_by_type(child, 'property_identifier')
                for identifier in identifiers:
                    members.append(self._get_node_text(identifier, content))
        
        return members