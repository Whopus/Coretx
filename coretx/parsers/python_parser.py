"""
Python-specific parser implementation.
"""

from typing import List, Dict, Any, Optional
import re

from .base import BaseParser
from ..models import CodeEntity, Relationship, EntityType, RelationshipType


class PythonParser(BaseParser):
    """Parser for Python source code."""
    
    @property
    def file_extensions(self) -> List[str]:
        return ['.py', '.pyw', '.pyi']
    
    @property
    def tree_sitter_language_name(self) -> str:
        return "python"
    
    def _extract_entities(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract Python entities from the AST."""
        entities = []
        
        # Extract module-level entity
        entities.append(self._create_module_entity(file_path, content))
        
        # Extract imports
        entities.extend(self._extract_python_imports(root_node, content, file_path))
        
        # Extract classes
        entities.extend(self._extract_classes(root_node, content, file_path))
        
        # Extract functions
        entities.extend(self._extract_functions(root_node, content, file_path))
        
        # Extract variables and constants
        entities.extend(self._extract_variables(root_node, content, file_path))
        
        return entities
    
    def _extract_relationships(
        self, 
        root_node, 
        content: str, 
        file_path: str, 
        entities: List[CodeEntity]
    ) -> List[Relationship]:
        """Extract relationships between Python entities."""
        relationships = []
        
        # Create entity lookup
        entity_lookup = {entity.name: entity for entity in entities}
        
        # Extract import relationships
        relationships.extend(self._extract_import_relationships(root_node, content, file_path, entities))
        
        # Extract inheritance relationships
        relationships.extend(self._extract_inheritance_relationships(root_node, content, file_path, entities))
        
        # Extract function call relationships
        relationships.extend(self._extract_call_relationships(root_node, content, file_path, entities))
        
        # Extract containment relationships
        relationships.extend(self._extract_containment_relationships(entities))
        
        return relationships
    
    def _create_module_entity(self, file_path: str, content: str) -> CodeEntity:
        """Create entity for the module itself."""
        from pathlib import Path
        
        module_name = Path(file_path).stem
        line_count = len(content.splitlines())
        
        # Extract module docstring
        docstring = self._extract_module_docstring(content)
        
        return CodeEntity(
            id=self._create_entity_id(EntityType.MODULE, module_name, file_path, 1),
            type=EntityType.MODULE,
            name=module_name,
            path=file_path,
            line_start=1,
            line_end=line_count,
            description=docstring or f"Python module: {module_name}",
            content=content,
            language=self.language,
            metadata={
                "is_package": file_path.endswith("__init__.py"),
                "line_count": line_count
            }
        )
    
    def _extract_python_imports(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract Python import statements."""
        entities = []
        
        # Find import statements
        import_nodes = self._find_nodes_by_type(root_node, 'import_statement')
        import_from_nodes = self._find_nodes_by_type(root_node, 'import_from_statement')
        
        for node in import_nodes + import_from_nodes:
            line_start, line_end = self._get_line_numbers(node)
            import_text = self._get_node_text(node, content).strip()
            
            # Parse import details
            imported_names = self._parse_import_names(node, content)
            
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
                    "imported_names": imported_names,
                    "import_type": node.type
                }
            )
            entities.append(entity)
        
        return entities
    
    def _extract_classes(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract Python class definitions."""
        entities = []
        class_nodes = self._find_nodes_by_type(root_node, 'class_definition')
        
        for node in class_nodes:
            line_start, line_end = self._get_line_numbers(node)
            
            # Get class name
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
            
            if not name_node:
                continue
                
            class_name = self._get_node_text(name_node, content)
            class_content = self._get_node_text(node, content)
            
            # Extract docstring
            docstring = self._extract_docstring(node, content)
            
            # Extract base classes
            base_classes = self._extract_base_classes(node, content)
            
            # Extract decorators
            decorators = self._extract_decorators(node, content)
            
            entity = CodeEntity(
                id=self._create_entity_id(EntityType.CLASS, class_name, file_path, line_start),
                type=EntityType.CLASS,
                name=class_name,
                path=file_path,
                line_start=line_start,
                line_end=line_end,
                description=docstring or f"Python class: {class_name}",
                content=class_content,
                language=self.language,
                metadata={
                    "base_classes": base_classes,
                    "decorators": decorators,
                    "is_abstract": "abc.ABC" in base_classes or any("abstract" in d for d in decorators)
                }
            )
            entities.append(entity)
            
            # Extract methods
            entities.extend(self._extract_methods(node, content, file_path, class_name))
        
        return entities
    
    def _extract_functions(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract Python function definitions (module-level)."""
        entities = []
        
        # Only get top-level functions (not methods)
        for child in root_node.children:
            if child.type == 'function_definition':
                entities.extend(self._extract_function_entity(child, content, file_path))
        
        return entities
    
    def _extract_methods(self, class_node, content: str, file_path: str, class_name: str) -> List[CodeEntity]:
        """Extract methods from a class."""
        entities = []
        method_nodes = self._find_nodes_by_type(class_node, 'function_definition')
        
        for node in method_nodes:
            method_entities = self._extract_function_entity(node, content, file_path, class_name)
            # Update type to METHOD for class methods
            for entity in method_entities:
                entity.type = EntityType.METHOD
                entity.metadata["parent_class"] = class_name
            entities.extend(method_entities)
        
        return entities
    
    def _extract_function_entity(self, node, content: str, file_path: str, parent_class: Optional[str] = None) -> List[CodeEntity]:
        """Extract a single function/method entity."""
        line_start, line_end = self._get_line_numbers(node)
        
        # Get function name
        name_node = None
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
                break
        
        if not name_node:
            return []
            
        func_name = self._get_node_text(name_node, content)
        func_content = self._get_node_text(node, content)
        
        # Extract docstring
        docstring = self._extract_docstring(node, content)
        
        # Extract parameters
        parameters = self._extract_function_parameters(node, content)
        
        # Extract decorators
        decorators = self._extract_decorators(node, content)
        
        # Determine function type
        entity_type = EntityType.METHOD if parent_class else EntityType.FUNCTION
        
        # Special method detection
        is_special = func_name.startswith('__') and func_name.endswith('__')
        is_private = func_name.startswith('_') and not is_special
        is_property = any('property' in d for d in decorators)
        
        entity = CodeEntity(
            id=self._create_entity_id(entity_type, func_name, file_path, line_start),
            type=entity_type,
            name=func_name,
            path=file_path,
            line_start=line_start,
            line_end=line_end,
            description=docstring or f"Python {entity_type.value}: {func_name}",
            content=func_content,
            language=self.language,
            metadata={
                "parameters": parameters,
                "decorators": decorators,
                "is_special": is_special,
                "is_private": is_private,
                "is_property": is_property,
                "parent_class": parent_class
            }
        )
        
        return [entity]
    
    def _extract_variables(self, root_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract module-level variables and constants."""
        entities = []
        
        # Find assignment statements at module level
        for child in root_node.children:
            if child.type == 'expression_statement':
                # Check if it's an assignment
                for grandchild in child.children:
                    if grandchild.type == 'assignment':
                        entities.extend(self._extract_assignment_variables(grandchild, content, file_path))
        
        return entities
    
    def _extract_assignment_variables(self, assignment_node, content: str, file_path: str) -> List[CodeEntity]:
        """Extract variables from assignment statements."""
        entities = []
        line_start, line_end = self._get_line_numbers(assignment_node)
        assignment_text = self._get_node_text(assignment_node, content)
        
        # Simple variable name extraction (left side of assignment)
        left_side = assignment_node.children[0] if assignment_node.children else None
        if left_side and left_side.type == 'identifier':
            var_name = self._get_node_text(left_side, content)
            
            # Determine if it's a constant (uppercase)
            is_constant = var_name.isupper()
            entity_type = EntityType.CONSTANT if is_constant else EntityType.VARIABLE
            
            entity = CodeEntity(
                id=self._create_entity_id(entity_type, var_name, file_path, line_start),
                type=entity_type,
                name=var_name,
                path=file_path,
                line_start=line_start,
                line_end=line_end,
                description=f"Python {entity_type.value}: {var_name}",
                content=assignment_text,
                language=self.language,
                metadata={
                    "assignment": assignment_text,
                    "is_constant": is_constant
                }
            )
            entities.append(entity)
        
        return entities
    
    def _extract_import_relationships(self, root_node, content: str, file_path: str, entities: List[CodeEntity]) -> List[Relationship]:
        """Extract import relationships."""
        relationships = []
        
        # Find the module entity
        module_entity = next((e for e in entities if e.type == EntityType.MODULE), None)
        if not module_entity:
            return relationships
        
        # Create relationships for each import
        import_entities = [e for e in entities if e.type == EntityType.IMPORT]
        for import_entity in import_entities:
            rel = Relationship(
                id=self._create_relationship_id(module_entity.id, import_entity.id, RelationshipType.CONTAINS),
                type=RelationshipType.CONTAINS,
                source_id=module_entity.id,
                target_id=import_entity.id,
                description=f"Module contains import: {import_entity.name}"
            )
            relationships.append(rel)
        
        return relationships
    
    def _extract_inheritance_relationships(self, root_node, content: str, file_path: str, entities: List[CodeEntity]) -> List[Relationship]:
        """Extract class inheritance relationships."""
        relationships = []
        class_entities = {e.name: e for e in entities if e.type == EntityType.CLASS}
        
        class_nodes = self._find_nodes_by_type(root_node, 'class_definition')
        for node in class_nodes:
            class_name = self._get_class_name(node, content)
            if not class_name or class_name not in class_entities:
                continue
                
            base_classes = self._extract_base_classes(node, content)
            for base_class in base_classes:
                if base_class in class_entities:
                    rel = Relationship(
                        id=self._create_relationship_id(
                            class_entities[class_name].id,
                            class_entities[base_class].id,
                            RelationshipType.INHERITS
                        ),
                        type=RelationshipType.INHERITS,
                        source_id=class_entities[class_name].id,
                        target_id=class_entities[base_class].id,
                        description=f"{class_name} inherits from {base_class}"
                    )
                    relationships.append(rel)
        
        return relationships
    
    def _extract_call_relationships(self, root_node, content: str, file_path: str, entities: List[CodeEntity]) -> List[Relationship]:
        """Extract function/method call relationships."""
        relationships = []
        
        # This is a simplified implementation
        # In practice, you'd want more sophisticated call graph analysis
        function_entities = {e.name: e for e in entities if e.type in [EntityType.FUNCTION, EntityType.METHOD]}
        
        call_nodes = self._find_nodes_by_type(root_node, 'call')
        for call_node in call_nodes:
            # Extract caller and callee information
            # This is simplified - real implementation would be more complex
            pass
        
        return relationships
    
    def _extract_containment_relationships(self, entities: List[CodeEntity]) -> List[Relationship]:
        """Extract containment relationships (module contains classes/functions, classes contain methods)."""
        relationships = []
        
        module_entity = next((e for e in entities if e.type == EntityType.MODULE), None)
        if not module_entity:
            return relationships
        
        # Module contains top-level entities
        for entity in entities:
            if entity.type in [EntityType.CLASS, EntityType.FUNCTION, EntityType.VARIABLE, EntityType.CONSTANT]:
                if not entity.metadata.get("parent_class"):  # Top-level entities
                    rel = Relationship(
                        id=self._create_relationship_id(module_entity.id, entity.id, RelationshipType.CONTAINS),
                        type=RelationshipType.CONTAINS,
                        source_id=module_entity.id,
                        target_id=entity.id,
                        description=f"Module contains {entity.type.value}: {entity.name}"
                    )
                    relationships.append(rel)
        
        # Classes contain methods
        class_entities = {e.name: e for e in entities if e.type == EntityType.CLASS}
        for entity in entities:
            if entity.type == EntityType.METHOD:
                parent_class = entity.metadata.get("parent_class")
                if parent_class and parent_class in class_entities:
                    rel = Relationship(
                        id=self._create_relationship_id(
                            class_entities[parent_class].id,
                            entity.id,
                            RelationshipType.CONTAINS
                        ),
                        type=RelationshipType.CONTAINS,
                        source_id=class_entities[parent_class].id,
                        target_id=entity.id,
                        description=f"Class {parent_class} contains method: {entity.name}"
                    )
                    relationships.append(rel)
        
        return relationships
    
    # Helper methods
    
    def _extract_module_docstring(self, content: str) -> Optional[str]:
        """Extract module-level docstring."""
        lines = content.strip().split('\n')
        if not lines:
            return None
            
        # Check for docstring at the beginning
        first_line = lines[0].strip()
        if first_line.startswith('"""') or first_line.startswith("'''"):
            quote = first_line[:3]
            if first_line.endswith(quote) and len(first_line) > 6:
                return first_line[3:-3].strip()
            else:
                # Multi-line docstring
                docstring_lines = [first_line[3:]]
                for line in lines[1:]:
                    if quote in line:
                        docstring_lines.append(line[:line.index(quote)])
                        break
                    docstring_lines.append(line)
                return '\n'.join(docstring_lines).strip()
        
        return None
    
    def _extract_docstring(self, node, content: str) -> Optional[str]:
        """Extract docstring from a function or class."""
        # Look for string literal as first statement in body
        for child in node.children:
            if child.type == 'block':
                for stmt in child.children:
                    if stmt.type == 'expression_statement':
                        for expr in stmt.children:
                            if expr.type == 'string':
                                docstring = self._get_node_text(expr, content)
                                # Remove quotes and clean up
                                if docstring.startswith('"""') or docstring.startswith("'''"):
                                    return docstring[3:-3].strip()
                                elif docstring.startswith('"') or docstring.startswith("'"):
                                    return docstring[1:-1].strip()
                                return docstring
                        break
                break
        return None
    
    def _extract_base_classes(self, class_node, content: str) -> List[str]:
        """Extract base classes from class definition."""
        base_classes = []
        
        for child in class_node.children:
            if child.type == 'argument_list':
                for arg in child.children:
                    if arg.type == 'identifier':
                        base_classes.append(self._get_node_text(arg, content))
        
        return base_classes
    
    def _extract_decorators(self, node, content: str) -> List[str]:
        """Extract decorators from a function or class."""
        decorators = []
        
        # Look for decorator nodes before the function/class
        current = node.prev_sibling
        while current and current.type == 'decorator':
            decorator_text = self._get_node_text(current, content)
            decorators.insert(0, decorator_text)  # Insert at beginning to maintain order
            current = current.prev_sibling
        
        return decorators
    
    def _extract_function_parameters(self, func_node, content: str) -> List[Dict[str, Any]]:
        """Extract function parameters."""
        parameters = []
        
        for child in func_node.children:
            if child.type == 'parameters':
                for param in child.children:
                    if param.type == 'identifier':
                        param_name = self._get_node_text(param, content)
                        parameters.append({
                            "name": param_name,
                            "type": None,  # Type hints would require more complex parsing
                            "default": None
                        })
        
        return parameters
    
    def _parse_import_names(self, import_node, content: str) -> List[str]:
        """Parse imported names from import statement."""
        names = []
        import_text = self._get_node_text(import_node, content)
        
        # Simple regex-based parsing (could be improved with AST traversal)
        if import_text.startswith('from'):
            # from module import name1, name2
            match = re.search(r'import\s+(.+)', import_text)
            if match:
                import_part = match.group(1)
                names = [name.strip() for name in import_part.split(',')]
        else:
            # import module1, module2
            match = re.search(r'import\s+(.+)', import_text)
            if match:
                import_part = match.group(1)
                names = [name.strip() for name in import_part.split(',')]
        
        return names
    
    def _get_class_name(self, class_node, content: str) -> Optional[str]:
        """Get class name from class definition node."""
        for child in class_node.children:
            if child.type == 'identifier':
                return self._get_node_text(child, content)
        return None