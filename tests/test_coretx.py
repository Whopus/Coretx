#!/usr/bin/env python3
"""
Simple test script for Coretx functionality.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from coretx import Coretx
from coretx.models import LLMConfig


def test_basic_functionality():
    """Test basic Coretx functionality without LLM."""
    print("🧪 Testing basic Coretx functionality...")
    
    # Test without LLM (will skip semantic analysis)
    try:
        ctx = Coretx(
            openai_api_key="dummy-key",  # Won't be used for basic parsing
            model="gpt-4"
        )
        print("✅ Coretx instance created successfully")
    except Exception as e:
        print(f"❌ Failed to create Coretx instance: {e}")
        return False
    
    # Test file scanning
    sample_project = Path(__file__).parent / "examples" / "sample_project"
    if not sample_project.exists():
        print(f"❌ Sample project not found: {sample_project}")
        return False
    
    print(f"📁 Testing with sample project: {sample_project}")
    
    # Test parser registry
    from coretx.parsers.registry import parser_registry
    supported_langs = parser_registry.get_supported_languages()
    print(f"📝 Supported languages: {supported_langs}")
    
    # Test file scanning
    from coretx.utils.file_utils import FileScanner
    from coretx.models import AnalysisConfig
    
    scanner = FileScanner(AnalysisConfig())
    files = scanner.scan_directory(sample_project)
    print(f"📄 Found {len(files)} files to analyze")
    
    for file_path in files:
        print(f"  - {file_path}")
    
    # Test parsing individual files
    from coretx.parsers.python_parser import PythonParser
    
    python_parser = PythonParser("python")
    python_parser.initialize()
    
    for file_path in files:
        if file_path.suffix == '.py':
            print(f"\n🔍 Parsing {file_path.name}...")
            try:
                entities, relationships = python_parser.parse_file(str(file_path))
                print(f"  Found {len(entities)} entities and {len(relationships)} relationships")
                
                for entity in entities[:3]:  # Show first 3 entities
                    print(f"    • {entity.type.value}: {entity.name}")
                    
            except Exception as e:
                print(f"  ❌ Failed to parse: {e}")
    
    # Test graph creation
    from coretx.graph import CodeGraph
    
    print(f"\n📊 Testing graph creation...")
    graph = CodeGraph(str(sample_project))
    
    # Add some test entities
    from coretx.models import CodeEntity, EntityType
    
    test_entity = CodeEntity(
        id="test:main.py:Application:1",
        type=EntityType.CLASS,
        name="Application",
        path=str(sample_project / "main.py"),
        line_start=1,
        line_end=10,
        description="Test application class",
        language="python"
    )
    
    graph.add_entity(test_entity)
    print(f"✅ Added test entity to graph")
    
    stats = graph.get_graph_stats()
    print(f"📈 Graph stats: {stats.total_entities} entities, {stats.total_relationships} relationships")
    
    return True


def test_with_mock_llm():
    """Test with a mock LLM to avoid API calls."""
    print("\n🤖 Testing with mock LLM...")
    
    # Create a mock LLM client
    from coretx.llm.client import LLMClient
    from coretx.models import LLMConfig
    
    class MockLLMClient(LLMClient):
        def generate_completion(self, prompt, system_prompt=None, **kwargs):
            return "This is a mock response for testing."
        
        def generate_embeddings(self, texts):
            import numpy as np
            # Return mock embeddings
            return [np.random.rand(384).tolist() for _ in texts]
        
        def analyze_code_semantics(self, code, language, context=""):
            return {
                "purpose": f"Mock analysis of {language} code",
                "complexity": "medium",
                "key_concepts": ["testing", "mock"],
                "dependencies": [],
                "side_effects": [],
                "patterns": [],
                "quality_issues": []
            }
    
    # Test mock functionality
    config = LLMConfig(api_key="mock", model="mock")
    mock_client = MockLLMClient(config)
    
    try:
        response = mock_client.generate_completion("Test prompt")
        print(f"✅ Mock LLM response: {response}")
        
        embeddings = mock_client.generate_embeddings(["test text"])
        print(f"✅ Mock embeddings generated: {len(embeddings[0])} dimensions")
        
        analysis = mock_client.analyze_code_semantics("def test(): pass", "python")
        print(f"✅ Mock semantic analysis: {analysis['purpose']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock LLM test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Coretx tests...\n")
    
    success = True
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    # Test with mock LLM
    if not test_with_mock_llm():
        success = False
    
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)