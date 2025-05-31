#!/usr/bin/env python3
"""
Quick test for Coretx custom API integration.
"""

import os
import sys
import tempfile
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_api_connectivity():
    """Test basic API connectivity."""
    console.print(Panel.fit("🔌 Testing API Connectivity", style="bold blue"))
    
    openai_base_url = "https://ai.comfly.chat/v1"
    openai_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    
    try:
        import openai
        
        # Set up client
        client = openai.OpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url
        )
        
        # Test chat completion
        console.print("\n🤖 Testing Chat Completion...")
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": "Say 'API connection successful'"}],
            max_tokens=10
        )
        console.print(f"✅ Chat Response: {response.choices[0].message.content}")
        
        # Test embeddings
        console.print("\n🔢 Testing Embeddings...")
        embedding_response = client.embeddings.create(
            model="BAAI/bge-m3",
            input="test text"
        )
        embedding = embedding_response.data[0].embedding
        console.print(f"✅ Embedding Shape: ({len(embedding)},)")
        console.print(f"✅ Embedding Sample: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ API Test Failed: {e}")
        return False

def test_coretx_basic():
    """Test basic Coretx functionality with custom API."""
    console.print(Panel.fit("🧠 Testing Coretx Basic", style="bold green"))
    
    openai_base_url = "https://ai.comfly.chat/v1"
    openai_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    
    try:
        from coretx import Coretx
        
        # Create test file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("""
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

def main():
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"Result: {result}")
""")
            
            # Initialize Coretx with custom API
            console.print("\n🔧 Initializing Coretx...")
            ctx = Coretx(
                llm_model="gpt-4.1",
                embedding_model="BAAI/bge-m3",
                openai_api_key=openai_api_key,
                openai_base_url=openai_base_url,
                enable_semantic_analysis=False  # Disable to speed up test
            )
            
            # Analyze project
            console.print("\n📊 Analyzing project...")
            graph = ctx.analyze(temp_dir)
            
            stats = graph.get_graph_stats()
            console.print(f"✅ Found {stats.total_entities} entities")
            console.print(f"✅ Found {stats.total_relationships} relationships")
            
            # Test query
            console.print("\n❓ Testing query...")
            query_result = ctx.query(graph, "What classes are defined?")
            console.print(f"✅ Query Summary: {query_result.summary[:100]}...")
            
            return True
            
    except Exception as e:
        console.print(f"❌ Coretx Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_client():
    """Test LLM client directly."""
    console.print(Panel.fit("🤖 Testing LLM Client", style="bold cyan"))
    
    openai_base_url = "https://ai.comfly.chat/v1"
    openai_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    
    try:
        from coretx.llm.client import LLMClient
        from coretx.models import LLMConfig
        
        # Create LLM client
        config = LLMConfig(
            model="gpt-4.1",
            embedding_model="BAAI/bge-m3",
            api_key=openai_api_key,
            api_base=openai_base_url
        )
        
        client = LLMClient(config)
        
        # Test text generation
        console.print("\n💬 Testing text generation...")
        response = client.generate_completion("Explain what a Python class is in one sentence.")
        console.print(f"✅ Response: {response[:100]}...")
        
        # Test embeddings
        console.print("\n🔢 Testing embeddings...")
        embeddings = client.generate_embeddings(["def hello(): return 'world'"])
        console.print(f"✅ Embedding Shape: ({len(embeddings[0])},)")
        
        return True
        
    except Exception as e:
        console.print(f"❌ LLM Client Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    console.print(Panel.fit("🧪 Coretx Quick API Tests", style="bold magenta"))
    
    # Set environment variables
    os.environ["OPENAI_API_KEY"] = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    os.environ["OPENAI_BASE_URL"] = "https://ai.comfly.chat/v1"
    
    # Run tests
    results = []
    results.append(("API Connectivity", test_api_connectivity()))
    results.append(("LLM Client", test_llm_client()))
    results.append(("Coretx Basic", test_coretx_basic()))
    
    # Show results
    console.print(Panel.fit("📊 Test Results Summary", style="bold yellow"))
    
    table = Table()
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="green")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        table.add_row(test_name, status)
        if result:
            passed += 1
    
    console.print(table)
    console.print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        console.print(Panel.fit("🎉 All tests passed! Custom API integration successful!", style="bold green"))
    else:
        console.print(Panel.fit("⚠️ Some tests failed. Check the output above.", style="bold red"))

if __name__ == "__main__":
    main()