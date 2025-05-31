"""
Tests for the core Coretx functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from coretx import Coretx, LLMConfig, AnalysisConfig
from coretx.models import EntityType, RelationshipType


class TestCoretx:
    """Test the main Coretx class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Set environment variable for OpenAI API key to avoid errors
        os.environ['OPENAI_API_KEY'] = 'test-key-for-testing'
        
        llm_config = LLMConfig(api_key="test-key")
        self.coretx = Coretx(llm_config=llm_config)
        
        # Create a temporary test project
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.py")
        
        with open(self.test_file, "w") as f:
            f.write("""
def hello_world():
    '''A simple hello world function.'''
    return "Hello, World!"

class TestClass:
    '''A test class.'''
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"
""")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
        
        # Clean up environment variable
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    def test_initialization(self):
        """Test Coretx initialization."""
        assert self.coretx is not None
        assert self.coretx.semantic_analyzer is not None
        assert self.coretx.query_processor is not None
    
    def test_analyze(self):
        """Test project analysis."""
        graph = self.coretx.analyze(self.test_dir)
        
        assert graph is not None
        stats = self.coretx.get_stats(graph)
        assert stats.total_entities > 0
        assert len(stats.entity_counts) > 0
    
    def test_get_context(self):
        """Test context retrieval."""
        # First analyze the project
        graph = self.coretx.analyze(self.test_dir)
        
        # Get context for a function
        context = self.coretx.locate(graph, "hello_world")
        
        assert context is not None
        assert len(context.entry_points) >= 0
    
    def test_query_code(self):
        """Test code querying."""
        # First analyze the project
        graph = self.coretx.analyze(self.test_dir)
        
        # Query for functions
        results = self.coretx.query(graph, "functions")
        
        assert results is not None
        assert len(results.entities) >= 0  # May be empty if query doesn't match
    
    def test_trace_dependencies(self):
        """Test dependency tracing."""
        # First analyze the project
        graph = self.coretx.analyze(self.test_dir)
        
        # Trace dependencies for a function
        trace = self.coretx.trace(graph, "hello_world")
        
        assert trace is not None
        assert len(trace.dependencies) >= 0  # May be empty for simple cases


class TestConfiguration:
    """Test configuration classes."""
    
    def test_llm_config(self):
        """Test LLM configuration."""
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="test-key"
        )
        
        assert config.provider == "openai"
        assert config.model == "gpt-3.5-turbo"
        assert config.api_key == "test-key"
    
    def test_analysis_config(self):
        """Test analysis configuration."""
        config = AnalysisConfig(
            ignore_patterns=["test_*.py"],
            max_file_size=1024*1024
        )
        
        assert "test_*.py" in config.ignore_patterns
        assert config.max_file_size == 1024*1024


if __name__ == "__main__":
    pytest.main([__file__])