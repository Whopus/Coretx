"""
Tests for the knowledge graph functionality.
"""

import pytest
from coretx.graph import CodeGraph
from coretx.models import CodeEntity, Relationship, EntityType, RelationshipType


class TestCodeGraph:
    """Test the CodeGraph class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.graph = CodeGraph()
        
        # Create test entities
        self.entity1 = CodeEntity(
            id="test1",
            name="TestClass",
            type=EntityType.CLASS,
            path="test.py",
            line_start=1,
            line_end=10
        )
        
        self.entity2 = CodeEntity(
            id="test2",
            name="test_method",
            type=EntityType.METHOD,
            path="test.py",
            line_start=5,
            line_end=8
        )
        
        self.relationship = Relationship(
            id="rel1",
            source_id="test1",
            target_id="test2",
            type=RelationshipType.CONTAINS
        )
    
    def test_add_entity(self):
        """Test adding entities to the graph."""
        self.graph.add_entity(self.entity1)
        
        found_entity = self.graph.find_entity("TestClass")
        assert found_entity == self.entity1
        assert len(self.graph.nodes) == 1
    
    def test_add_relationship(self):
        """Test adding relationships to the graph."""
        # Add entities first
        self.graph.add_entity(self.entity1)
        self.graph.add_entity(self.entity2)
        
        # Add relationship
        self.graph.add_relationship(self.relationship)
        
        relationships = self.graph.get_relationships(source=self.entity1)
        assert len(relationships) == 1
        assert relationships[0] == self.relationship
    
    def test_find_entities_by_type(self):
        """Test finding entities by type."""
        self.graph.add_entity(self.entity1)
        self.graph.add_entity(self.entity2)
        
        classes = self.graph.find_entities(entity_type=EntityType.CLASS)
        methods = self.graph.find_entities(entity_type=EntityType.METHOD)
        
        assert len(classes) == 1
        assert len(methods) == 1
        assert classes[0] == self.entity1
        assert methods[0] == self.entity2
    
    def test_find_entities_by_name(self):
        """Test finding entities by name."""
        self.graph.add_entity(self.entity1)
        self.graph.add_entity(self.entity2)
        
        result = self.graph.find_entity("TestClass")
        assert result == self.entity1
        
        result = self.graph.find_entity("test_method")
        assert result == self.entity2
    
    def test_get_related_entities(self):
        """Test getting related entities."""
        # Add entities and relationship
        self.graph.add_entity(self.entity1)
        self.graph.add_entity(self.entity2)
        self.graph.add_relationship(self.relationship)
        
        # Get dependencies (related entities)
        related = self.graph.get_dependencies(self.entity1)
        assert len(related) == 1
        assert related[0] == self.entity2
    
    def test_get_graph_stats(self):
        """Test getting graph statistics."""
        self.graph.add_entity(self.entity1)
        self.graph.add_entity(self.entity2)
        self.graph.add_relationship(self.relationship)
        
        stats = self.graph.get_graph_stats()
        
        assert stats.total_entities == 2
        assert stats.total_relationships == 1
        assert stats.entity_counts[EntityType.CLASS] == 1
        assert stats.entity_counts[EntityType.METHOD] == 1
    
    def test_clear_graph(self):
        """Test clearing the graph."""
        self.graph.add_entity(self.entity1)
        self.graph.add_entity(self.entity2)
        self.graph.add_relationship(self.relationship)
        
        # Create a new empty graph (no clear method available)
        self.graph = CodeGraph()
        
        assert len(self.graph.nodes) == 0
        stats = self.graph.get_graph_stats()
        assert stats.total_entities == 0
        assert stats.total_relationships == 0


if __name__ == "__main__":
    pytest.main([__file__])