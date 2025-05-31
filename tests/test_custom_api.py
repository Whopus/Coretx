#!/usr/bin/env python3
"""
Test script for custom OpenAI-compatible API integration with Coretx.
Tests chat completions, embeddings, and full Coretx functionality.
"""

import os
import json
import requests
import numpy as np
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Set up environment
os.environ["OPENAI_API_KEY"] = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
os.environ["OPENAI_BASE_URL"] = "https://ai.comfly.chat/v1"

console = Console()

def test_basic_api_connectivity():
    """Test basic API connectivity with chat and embeddings."""
    console.print(Panel.fit("🔌 Testing API Connectivity", style="bold blue"))
    
    openai_base_url = "https://ai.comfly.chat/v1"
    openai_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    
    try:
        # Test chat completion
        console.print("\n🤖 Testing Chat Completion...")
        client = OpenAI(
            api_key=openai_api_key,  
            base_url=openai_base_url
        )
        
        response = client.chat.completions.create(
            model="gpt-4.1",
            stream=False,
            messages=[
                {'role': 'user', "content": [{"type":"text", "text":"Hello! Please respond with 'API connection successful'"}]}
            ]
        )
        
        chat_response = response.choices[0].message.content
        console.print(f"✅ Chat Response: {chat_response}")
        
        # Test embeddings
        console.print("\n🔢 Testing Embeddings...")
        embedding_url = f"{openai_base_url}/embeddings"
        
        payload = json.dumps({
            "model": "BAAI/bge-m3",
            "normalized": True,
            "embedding_type": "float",
            "input": "Test embedding for code analysis"
        })
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(embedding_url, headers=headers, data=payload)
        response.raise_for_status()
        
        embedding_data = response.json()
        embedding_vector = np.array(embedding_data["data"][0]["embedding"])
        console.print(f"✅ Embedding Shape: {embedding_vector.shape}")
        console.print(f"✅ Embedding Sample: {embedding_vector[:5]}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ API Test Failed: {e}")
        return False

def test_coretx_llm_integration():
    """Test Coretx LLM integration with custom API."""
    console.print(Panel.fit("🧠 Testing Coretx LLM Integration", style="bold green"))
    
    openai_base_url = "https://ai.comfly.chat/v1"
    openai_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    
    try:
        from coretx import Coretx
        from coretx.llm.client import LLMClient
        from coretx.llm.embeddings import EmbeddingEngine
        
        # Test LLM Client
        console.print("\n🔧 Testing LLM Client...")
        from coretx.models import LLMConfig
        
        llm_config = LLMConfig(
            model="gpt-4.1",
            embedding_model="BAAI/bge-m3",
            api_key=openai_api_key,
            api_base=openai_base_url
        )
        llm_client = LLMClient(llm_config)
        
        test_prompt = "Analyze this Python function: def hello(): return 'world'"
        response = llm_client.generate_completion(test_prompt)
        console.print(f"✅ LLM Response: {response[:100]}...")
        
        # Test Embeddings Engine
        console.print("\n🔢 Testing Embeddings Engine...")
        from coretx.llm.embeddings import EmbeddingEngine
        embeddings_engine = EmbeddingEngine(llm_client)
        
        test_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
        """
        
        # Generate embeddings directly
        embeddings = llm_client.generate_embeddings([test_code])
        embedding = np.array(embeddings[0])
        console.print(f"✅ Code Embedding Shape: {embedding.shape}")
        
        # Test similarity
        similar_code = """
def fib(num):
    if num <= 1:
        return num
    return fib(num-1) + fib(num-2)
        """
        
        embeddings2 = llm_client.generate_embeddings([similar_code])
        embedding2 = np.array(embeddings2[0])
        
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([embedding], [embedding2])[0][0]
        console.print(f"✅ Code Similarity: {similarity:.3f}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Coretx LLM Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_coretx_workflow():
    """Test complete Coretx workflow with LLM features."""
    console.print(Panel.fit("🚀 Testing Full Coretx Workflow", style="bold magenta"))
    
    openai_base_url = "https://ai.comfly.chat/v1"
    openai_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    
    try:
        from coretx import Coretx
        import tempfile
        import os
        
        # Create test project
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create sample Python file
            sample_file = os.path.join(temp_dir, "sample.py")
            with open(sample_file, 'w') as f:
                f.write("""
class DataProcessor:
    '''Processes data for analysis.'''
    
    def __init__(self, config):
        self.config = config
        
    def process_data(self, data):
        '''Process input data and return results.'''
        return self.transform(data)
        
    def transform(self, data):
        '''Transform data using configured rules.'''
        return [item.upper() for item in data]

def main():
    processor = DataProcessor({'mode': 'uppercase'})
    result = processor.process_data(['hello', 'world'])
    print(result)
                """)
            
            # Initialize Coretx with custom API settings
            console.print("\n🔧 Initializing Coretx...")
            ctx = Coretx(
                model="gpt-4.1",
                embedding_model="BAAI/bge-m3",
                openai_api_key=openai_api_key,
                openai_base_url=openai_base_url
            )
            
            # Analyze project
            console.print("\n📊 Analyzing project...")
            graph = ctx.analyze(temp_dir)
            
            stats = graph.get_graph_stats()
            console.print(f"✅ Found {stats.total_entities} entities")
            console.print(f"✅ Found {stats.total_relationships} relationships")
            
            # Test semantic analysis
            console.print("\n🧠 Testing semantic analysis...")
            query_result = ctx.query(graph, "What is the main purpose of this code?")
            console.print(f"✅ Query Result: {query_result.answer[:100]}...")
            
            # Test natural language query
            console.print("\n❓ Testing natural language query...")
            query_result2 = ctx.query(graph, "What classes are defined in this codebase?")
            console.print(f"✅ Query Result: {query_result2.answer[:100]}...")
            
            # Test context generation
            console.print("\n📝 Testing context generation...")
            context_result = ctx.locate(graph, "DataProcessor class implementation")
            console.print(f"✅ Context Length: {len(context_result.context)} characters")
            
            return True
            
    except Exception as e:
        console.print(f"❌ Full Workflow Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedding_graph_features():
    """Test embedding-based graph features."""
    console.print(Panel.fit("🕸️ Testing Embedding Graph Features", style="bold cyan"))
    
    openai_base_url = "https://ai.comfly.chat/v1"
    openai_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    
    try:
        from coretx import Coretx
        from coretx.llm.embeddings import EmbeddingEngine
        import tempfile
        import os
        
        # Create test project with multiple files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple related files
            files_content = {
                "user.py": """
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def get_profile(self):
        return {'name': self.name, 'email': self.email}
                """,
                "auth.py": """
from user import User

class AuthService:
    def authenticate(self, username, password):
        # Authentication logic
        return True
    
    def create_user(self, name, email):
        return User(name, email)
                """,
                "api.py": """
from auth import AuthService

class UserAPI:
    def __init__(self):
        self.auth = AuthService()
    
    def login(self, credentials):
        return self.auth.authenticate(credentials['user'], credentials['pass'])
                """
            }
            
            for filename, content in files_content.items():
                with open(os.path.join(temp_dir, filename), 'w') as f:
                    f.write(content)
            
            # Initialize Coretx and analyze
            console.print("\n🔧 Analyzing multi-file project...")
            ctx = Coretx(
                model="gpt-4.1",
                embedding_model="BAAI/bge-m3",
                openai_api_key=openai_api_key,
                openai_base_url=openai_base_url
            )
            graph = ctx.analyze(temp_dir)
            
            # Test embedding-based similarity
            console.print("\n🔍 Testing code similarity...")
            # Use the LLM client from Coretx
            llm_client = ctx.llm_client
            
            # Get entities
            entities = graph.find_entities_by_type("class")
            console.print(f"✅ Found {len(entities)} classes")
            
            # Calculate embeddings for classes
            if len(entities) >= 2:
                entity1, entity2 = entities[0], entities[1]
                
                # Get code snippets (simplified)
                code1 = f"class {entity1.name}:"
                code2 = f"class {entity2.name}:"
                
                emb1 = np.array(llm_client.generate_embeddings([code1])[0])
                emb2 = np.array(llm_client.generate_embeddings([code2])[0])
                
                from sklearn.metrics.pairwise import cosine_similarity
                similarity = cosine_similarity([emb1], [emb2])[0][0]
                console.print(f"✅ Class Similarity ({entity1.name} vs {entity2.name}): {similarity:.3f}")
            
            # Test semantic search
            console.print("\n🔎 Testing semantic search...")
            search_result = ctx.semantic_search("user authentication")
            console.print(f"✅ Semantic Search Results: {len(search_result)} matches")
            
            return True
            
    except Exception as e:
        console.print(f"❌ Embedding Graph Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    console.print(Panel.fit("🧪 Coretx Custom API Integration Tests", style="bold white"))
    
    results = []
    
    # Test 1: Basic API connectivity
    results.append(("API Connectivity", test_basic_api_connectivity()))
    
    # Test 2: Coretx LLM integration
    results.append(("LLM Integration", test_coretx_llm_integration()))
    
    # Test 3: Full workflow
    results.append(("Full Workflow", test_full_coretx_workflow()))
    
    # Test 4: Embedding graph features
    results.append(("Embedding Graph", test_embedding_graph_features()))
    
    # Summary
    console.print(Panel.fit("📊 Test Results Summary", style="bold yellow"))
    
    table = Table()
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="green")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        table.add_row(test_name, status)
    
    console.print(table)
    
    total_passed = sum(1 for _, success in results if success)
    console.print(f"\n🎯 Results: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        console.print(Panel.fit("🎉 All tests passed! Coretx is ready with custom API.", style="bold green"))
    else:
        console.print(Panel.fit("⚠️ Some tests failed. Check the output above.", style="bold red"))

if __name__ == "__main__":
    main()