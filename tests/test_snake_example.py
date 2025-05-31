#!/usr/bin/env python3
"""
Test Coretx functionality using the snake game example.
This test verifies that Coretx can properly analyze a real codebase.
"""

import unittest
import os
import tempfile
from pathlib import Path
from coretx import Coretx


class TestSnakeGameAnalysis(unittest.TestCase):
    """Test Coretx analysis of the snake game example."""
    
    def setUp(self):
        """Set up test environment."""
        self.snake_path = Path(__file__).parent.parent / "examples" / "snake_game"
        self.assertTrue(self.snake_path.exists(), f"Snake game example not found at {self.snake_path}")
        
        # Initialize Coretx for testing (without LLM)
        self.ctx = Coretx()
        # Disable semantic analyzer to avoid LLM calls
        self.ctx.semantic_analyzer = None
        
    def test_snake_game_analysis(self):
        """Test basic analysis of snake game codebase."""
        # Analyze the snake game
        graph = self.ctx.analyze(str(self.snake_path))
        
        # Verify analysis results
        self.assertIsNotNone(graph)
        self.assertGreater(len(graph.nodes), 0)
        self.assertGreater(len(graph.edges), 0)
        
        # Check for expected entities
        entity_names = [entity.name for entity in graph.nodes]
        
        # Should find key classes
        expected_classes = ["SnakeGame", "Snake", "Food", "AIPlayer"]
        for cls_name in expected_classes:
            self.assertIn(cls_name, entity_names, f"Expected class {cls_name} not found")
        
        # Should find key functions
        expected_functions = ["main", "run_human_game"]
        for func_name in expected_functions:
            self.assertIn(func_name, entity_names, f"Expected function {func_name} not found")
    
    def test_file_discovery(self):
        """Test that all expected files are discovered."""
        graph = self.ctx.analyze(str(self.snake_path))
        
        # Check that all Python files were found
        expected_modules = ["game", "ai_player", "utils", "main"]
        module_names = [entity.name for entity in graph.nodes if entity.type.value == "module"]
        
        for expected_module in expected_modules:
            self.assertIn(expected_module, module_names, 
                         f"Expected module {expected_module} not analyzed")
    
    def test_relationship_extraction(self):
        """Test that relationships are properly extracted."""
        graph = self.ctx.analyze(str(self.snake_path))
        
        # Should have containment relationships (modules contain classes/functions)
        containment_rels = [rel for rel in graph.edges 
                           if rel.type.value == "contains"]
        self.assertGreater(len(containment_rels), 0, "No containment relationships found")
    
    def test_entity_types(self):
        """Test that different entity types are found."""
        graph = self.ctx.analyze(str(self.snake_path))
        
        # Test finding classes by type
        classes = [e for e in graph.nodes if e.type.value == "class"]
        self.assertGreater(len(classes), 0, "No classes found")
        
        # Test finding functions by type
        functions = [e for e in graph.nodes if e.type.value == "function"]
        self.assertGreater(len(functions), 0, "No functions found")
        
        # Test finding specific entity by name
        snake_game = [e for e in graph.nodes if e.name == "SnakeGame"]
        self.assertGreater(len(snake_game), 0, "SnakeGame class not found")


if __name__ == "__main__":
    unittest.main()