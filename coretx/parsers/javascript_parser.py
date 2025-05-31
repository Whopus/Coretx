"""
JavaScript-specific parser implementation.
"""

from typing import List, Dict, Any, Optional
from .base import BaseParser
from ..models import CodeEntity, Relationship, EntityType, RelationshipType


class JavaScriptParser(BaseParser):
    """Parser for JavaScript source code."""
    
    @property
    def file_extensions(self) -> List[str]:
        return ['.js', '.jsx', '.mjs']
    
    @property
    def tree_sitter_language_name(self) -> str:
        return "javascript"
    
    def _extract_entities(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract JavaScript entities from the AST."""
        entities = []
        
        # Extract module-level entity
        entities.append(self._create_module_entity(file_path, content))
        
        # Extract imports/requires
        entities.extend(self._extract_js_imports(root_node, content, file_path))
        
        # Extract functions
        entities.extend(self._extract_js_functions(root_node, content, file_path))
        
        # Extract classes
        entities.extend(self._extract_js_classes(root_node, content, file_path))
        
        # Extract variables
        entities.extend(self._extract_js_variables(root_node, content, file_path))
        
        return entities
    
    def _extract_relationships(
        self, 
        root_node, 
        content: str, 
        file_path: str, 
        entities: List[CodeEntity]
    ) -> List[Relationship]:
        """Extract relationships between JavaScript entities."""
        relationships = []
        
        # Extract containment relationships
        relationships.extend(self._extract_containment_relationships(entities))
        
        # Extract import relationships
        relationships.extend(self._extract_js_import_relationships(entities))
        
        return relationships
    
    def _create_module_entity(self, file_path: str, content: str) -> CodeEntity:
        """Create entity for the JavaScript module."""
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
            description=f"JavaScript module: {module_name}",
            content=content,
            language=self.language,
            metadata={
                "line_count": line_count,
                "is_es_module": "import " in content or "export " in content
            }
        )
    
    def _extract_js_imports(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract JavaScript import/require statements."""
        entities = []
        
        # ES6 imports
        import_nodes = self._find_nodes_by_type(root_node, 'import_statement')
        for node in import_nodes:
            entities.extend(self._create_import_entity(node, content, file_path, "es6_import"))
        
        # CommonJS requires (simplified detection)
        call_nodes = self._find_nodes_by_type(root_node, 'call_expression')
        for node in call_nodes:
            if self._is_require_call(node, content):
                entities.extend(self._create_import_entity(node, content, file_path, "commonjs_require"))
        
        return entities
    
    def _extract_js_functions(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract JavaScript function declarations."""
        entities = []
        
        # Function declarations
        func_nodes = self._find_nodes_by_type(root_node, 'function_declaration')
        for node in func_nodes:
            entities.extend(self._create_function_entity(node, content, file_path))
        
        # Arrow functions and function expressions (simplified)
        arrow_nodes = self._find_nodes_by_type(root_node, 'arrow_function')
        for node in arrow_nodes:
            entities.extend(self._create_function_entity(node, content, file_path, is_arrow=True))
        
        return entities
    
    def _extract_js_classes(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract JavaScript class declarations."""
        entities = []
        
        class_nodes = self._find_nodes_by_type(root_node, 'class_declaration')
        for node in class_nodes:
            entities.extend(self._create_class_entity(node, content, file_path))
        
        return entities
    
    def _extract_js_variables(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract JavaScript variable declarations."""
        entities = []
        
        # Variable declarations (var, let, const)
        var_nodes = self._find_nodes_by_type(root_node, 'variable_declaration')
        for node in var_nodes:
            entities.extend(self._create_variable_entities(node, content, file_path))
        
        return entities
    
    def _create_import_entity(self, node, content: str, file_path: str, import_type: str) -> List[CodeEntity]:
        """Create import entity from import/require node."""
        line_start, line_end = self._get_line_numbers(node)
        import_text = self._get_node_text(node, content).strip()
        
        entity = CodeEntity(
            id=self._create_entity_id(EntityType.IMPORT, import_text, file_path, line_start),
            type=EntityType.IMPORT,
            name=import_text,
            path=file_path,
            line_start=line_start,
            line_end=line_end,
            content=import_text,
            language=self.language,
            metadata={
                "import_type": import_type,
                "raw_import": import_text
            }
        )
        
        return [entity]
    
    def _create_function_entity(self, node, content: str, file_path: str, is_arrow: bool = False) -> List[CodeEntity]:
        """Create function entity from function node."""
        line_start, line_end = self._get_line_numbers(node)
        func_content = self._get_node_text(node, content)
        
        # Extract function name
        func_name = self._extract_js_function_name(node, content, is_arrow)
        if not func_name:
            func_name = f"anonymous_function_{line_start}"
        
        entity = CodeEntity(
            id=self._create_entity_id(EntityType.FUNCTION, func_name, file_path, line_start),
            type=EntityType.FUNCTION,
            name=func_name,
            path=file_path,
            line_start=line_start,
            line_end=line_end,
            description=f"JavaScript function: {func_name}",
            content=func_content,
            language=self.language,
            metadata={
                "is_arrow_function": is_arrow,
                "is_async": "async" in func_content[:50],  # Simple check
                "is_generator": "function*" in func_content[:50]
            }
        )
        
        return [entity]
    
    def _create_class_entity(self, node, content: str, file_path: str) -> List[CodeEntity]:
        """Create class entity from class node."""
        line_start, line_end = self._get_line_numbers(node)
        class_content = self._get_node_text(node, content)
        
        # Extract class name
        class_name = self._extract_js_class_name(node, content)
        if not class_name:
            return []
        
        entity = CodeEntity(
            id=self._create_entity_id(EntityType.CLASS, class_name, file_path, line_start),
            type=EntityType.CLASS,
            name=class_name,
            path=file_path,
            line_start=line_start,
            line_end=line_end,
            description=f"JavaScript class: {class_name}",
            content=class_content,
            language=self.language,
            metadata={
                "has_constructor": "constructor(" in class_content,
                "extends": self._extract_js_extends(node, content)
            }
        )
        
        return [entity]
    
    def _create_variable_entities(self, node, content: str, file_path: str) -> List[CodeEntity]:
        """Create variable entities from variable declaration node."""
        entities = []
        line_start, line_end = self._get_line_numbers(node)
        var_content = self._get_node_text(node, content)
        
        # Extract variable names (simplified)
        var_names = self._extract_js_variable_names(node, content)
        
        for var_name in var_names:
            # Determine if it's a constant
            is_constant = var_content.strip().startswith('const') or var_name.isupper()
            entity_type = EntityType.CONSTANT if is_constant else EntityType.VARIABLE
            
            entity = CodeEntity(
                id=self._create_entity_id(entity_type, var_name, file_path, line_start),
                type=entity_type,
                name=var_name,
                path=file_path,
                line_start=line_start,
                line_end=line_end,
                description=f"JavaScript {entity_type.value}: {var_name}",
                content=var_content,
                language=self.language,
                metadata={
                    "declaration_type": var_content.split()[0],  # var, let, const
                    "is_constant": is_constant
                }
            )
            entities.append(entity)
        
        return entities
    
    def _extract_containment_relationships(self, entities: List[CodeEntity]) -> List[Relationship]:
        """Extract containment relationships."""
        relationships = []
        
        module_entity = next((e for e in entities if e.type == EntityType.MODULE), None)
        if not module_entity:
            return relationships
        
        # Module contains top-level entities
        for entity in entities:
            if entity.type in [EntityType.CLASS, EntityType.FUNCTION, EntityType.VARIABLE, EntityType.CONSTANT, EntityType.IMPORT]:
                rel = Relationship(
                    id=self._create_relationship_id(module_entity.id, entity.id, RelationshipType.CONTAINS),
                    type=RelationshipType.CONTAINS,
                    source_id=module_entity.id,
                    target_id=entity.id,
                    description=f"Module contains {entity.type.value}: {entity.name}"
                )
                relationships.append(rel)
        
        return relationships
    
    def _extract_js_import_relationships(self, entities: List[CodeEntity]) -> List[Relationship]:
        """Extract import relationships."""
        # Simplified implementation
        return []
    
    # Helper methods
    
    def _is_require_call(self, node, content: str) -> bool:
        """Check if a call expression is a require() call."""
        node_text = self._get_node_text(node, content)
        return node_text.strip().startswith('require(')
    
    def _extract_js_function_name(self, node, content: str, is_arrow: bool) -> Optional[str]:
        """Extract function name from function node."""
        if is_arrow:
            # For arrow functions, look for assignment pattern
            parent = node.parent
            if parent and parent.type == 'variable_declarator':
                for child in parent.children:
                    if child.type == 'identifier':
                        return self._get_node_text(child, content)
            return None
        else:
            # For regular functions, find identifier child
            for child in node.children:
                if child.type == 'identifier':
                    return self._get_node_text(child, content)
        return None
    
    def _extract_js_class_name(self, node, content: str) -> Optional[str]:
        """Extract class name from class node."""
        for child in node.children:
            if child.type == 'identifier':
                return self._get_node_text(child, content)
        return None
    
    def _extract_js_extends(self, node, content: str) -> Optional[str]:
        """Extract extends clause from class."""
        for child in node.children:
            if child.type == 'class_heritage':
                for heritage_child in child.children:
                    if heritage_child.type == 'identifier':
                        return self._get_node_text(heritage_child, content)
        return None
    
    def _extract_js_variable_names(self, node, content: str) -> List[str]:
        """Extract variable names from variable declaration."""
        names = []
        
        # Find variable_declarator nodes
        declarators = self._find_nodes_by_type(node, 'variable_declarator')
        for declarator in declarators:
            for child in declarator.children:
                if child.type == 'identifier':
                    names.append(self._get_node_text(child, content))
                    break
        
        return names