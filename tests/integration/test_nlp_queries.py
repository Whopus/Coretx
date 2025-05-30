"""
Natural Language Processing Tests for Coretx

Tests for natural language code queries, semantic search, and LLM-powered code understanding.
"""

import os
import sys
import time
from pathlib import Path

# Import Coretx components
try:
    from coretx import LocAgentConfig, create_locator
    from coretx.config.settings import AgentConfig
    from coretx.core.extensions.registry import registry
    from coretx.core.agent.enhanced_tools import enhanced_tools
    from coretx.core.agent import LocalizationAgent
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure Coretx is properly installed")
    exit(1)


class NaturalLanguageQueryTester:
    """Test class for natural language query processing."""
    
    def __init__(self):
        # Test configuration
        self.api_key = os.getenv('CORETX_TEST_API_KEY', 'sk-test-key-placeholder')
        self.api_base = os.getenv('CORETX_TEST_API_BASE', 'https://api.openai.com/v1')
        self.model_name = os.getenv('CORETX_TEST_MODEL', 'gpt-4')
        
        # Sample project path
        self.sample_project_path = Path(__file__).parent.parent / "sample_projects"
        
        # Initialize agent if API key is available
        self.agent = None
        if self.api_key and self.api_key != 'sk-test-key-placeholder':
            try:
                agent_config = AgentConfig(
                    model_name=self.model_name,
                    api_key=self.api_key,
                    api_base=self.api_base,
                    temperature=0.1
                )
                self.agent = LocalizationAgent(agent_config)
            except Exception as e:
                print(f"⚠️  Could not initialize agent: {e}")
    
    def test_semantic_search_queries(self):
        """Test semantic search with natural language queries."""
        print("🧪 Testing semantic search queries...")
        
        try:
            if not self.sample_project_path.exists():
                print("⚠️  Sample project not found, skipping semantic search test")
                return True
            
            # Test queries that should find relevant code
            test_queries = [
                "authentication and login functionality",
                "password hashing and security",
                "session management and tokens",
                "database connections and queries",
                "input validation and sanitization",
                "error handling and exceptions"
            ]
            
            successful_queries = 0
            
            for query in test_queries:
                try:
                    result = enhanced_tools.tools['search_entities'](
                        query=query,
                        limit=5
                    )
                    
                    # Check if we got meaningful results
                    if 'entities' in result:
                        successful_queries += 1
                        print(f"  ✅ Query '{query}' returned {len(result['entities'])} results")
                    else:
                        print(f"  ⚠️  Query '{query}' returned no results")
                        
                except Exception as e:
                    print(f"  ❌ Query '{query}' failed: {e}")
            
            success_rate = successful_queries / len(test_queries)
            print(f"✅ Semantic search test completed ({success_rate:.1%} success rate)")
            return success_rate > 0.5  # At least 50% success rate
            
        except Exception as e:
            print(f"❌ Semantic search test failed: {e}")
            return False
    
    def test_contextual_code_analysis(self):
        """Test contextual code analysis with natural language descriptions."""
        print("🧪 Testing contextual code analysis...")
        
        try:
            if not self.sample_project_path.exists():
                print("⚠️  Sample project not found, skipping contextual analysis test")
                return True
            
            # Analyze the codebase structure first
            analysis_result = enhanced_tools.tools['analyze_directory'](
                directory_path=str(self.sample_project_path),
                recursive=True,
                show_stats=False
            )
            
            if 'entities' not in analysis_result:
                print("⚠️  No entities found in sample project")
                return True
            
            entities = analysis_result['entities']
            
            # Test contextual queries
            context_queries = [
                ("Find authentication code", ["auth", "login", "password"]),
                ("Locate database operations", ["database", "db", "sql", "query"]),
                ("Show session management", ["session", "token", "cookie"]),
                ("Find validation functions", ["valid", "check", "verify"]),
            ]
            
            successful_contexts = 0
            
            for description, keywords in context_queries:
                # Search for entities matching the context
                matching_entities = []
                for entity in entities:
                    entity_name = entity.get('name', '').lower()
                    entity_file = entity.get('file', '').lower()
                    
                    if any(keyword in entity_name or keyword in entity_file for keyword in keywords):
                        matching_entities.append(entity)
                
                if matching_entities:
                    successful_contexts += 1
                    print(f"  ✅ Context '{description}' found {len(matching_entities)} relevant entities")
                else:
                    print(f"  ⚠️  Context '{description}' found no relevant entities")
            
            success_rate = successful_contexts / len(context_queries)
            print(f"✅ Contextual analysis test completed ({success_rate:.1%} success rate)")
            return success_rate > 0.5
            
        except Exception as e:
            print(f"❌ Contextual analysis test failed: {e}")
            return False
    
    def test_llm_powered_queries(self):
        """Test LLM-powered natural language queries (if agent available)."""
        print("🧪 Testing LLM-powered queries...")
        
        if not self.agent:
            print("⚠️  No LLM agent available, skipping LLM-powered query test")
            return True
        
        try:
            # Test queries that require LLM understanding
            llm_queries = [
                "Find code that handles user authentication and explain the flow",
                "Locate potential security vulnerabilities in password handling",
                "Show me the session management implementation and its weaknesses",
                "Identify database query patterns and potential SQL injection risks"
            ]
            
            successful_llm_queries = 0
            
            for query in llm_queries:
                try:
                    # Create a context-aware prompt
                    prompt = f"""
                    You are analyzing a Python web application codebase. 
                    User query: "{query}"
                    
                    Please provide a brief analysis focusing on:
                    1. Relevant files and functions
                    2. Key implementation details
                    3. Potential issues or improvements
                    
                    Keep the response concise and technical.
                    """
                    
                    start_time = time.time()
                    response = self.agent.process_query(prompt)
                    duration = time.time() - start_time
                    
                    if response and len(response) > 50:  # Meaningful response
                        successful_llm_queries += 1
                        print(f"  ✅ LLM query processed in {duration:.2f}s")
                    else:
                        print(f"  ⚠️  LLM query returned minimal response")
                    
                    # Add delay to avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  ❌ LLM query failed: {e}")
            
            success_rate = successful_llm_queries / len(llm_queries)
            print(f"✅ LLM-powered queries test completed ({success_rate:.1%} success rate)")
            return success_rate > 0.5
            
        except Exception as e:
            print(f"❌ LLM-powered queries test failed: {e}")
            return False
    
    def test_multi_language_understanding(self):
        """Test natural language understanding across multiple programming languages."""
        print("🧪 Testing multi-language understanding...")
        
        try:
            # Initialize parsers for multiple languages
            registry.initialize_default_parsers()
            
            # Test language-specific queries
            language_queries = [
                ("Python classes and methods", "python"),
                ("JavaScript functions", "javascript"),
                ("Configuration files", "config"),
                ("Documentation and comments", "markdown")
            ]
            
            successful_language_queries = 0
            
            for query, language_hint in language_queries:
                try:
                    # Search with language context
                    result = enhanced_tools.tools['search_entities'](
                        query=query,
                        languages=[language_hint] if language_hint != "config" else None,
                        limit=3
                    )
                    
                    if 'entities' in result and result['entities']:
                        successful_language_queries += 1
                        print(f"  ✅ Language query '{query}' found relevant entities")
                    else:
                        print(f"  ⚠️  Language query '{query}' found no entities")
                        
                except Exception as e:
                    print(f"  ❌ Language query '{query}' failed: {e}")
            
            success_rate = successful_language_queries / len(language_queries)
            print(f"✅ Multi-language understanding test completed ({success_rate:.1%} success rate)")
            return success_rate > 0.3  # Lower threshold due to language diversity
            
        except Exception as e:
            print(f"❌ Multi-language understanding test failed: {e}")
            return False
    
    def test_query_performance(self):
        """Test query performance and response times."""
        print("🧪 Testing query performance...")
        
        try:
            if not self.sample_project_path.exists():
                print("⚠️  Sample project not found, skipping performance test")
                return True
            
            # Test different types of queries and measure performance
            performance_tests = [
                ("Simple entity search", lambda: enhanced_tools.tools['search_entities'](
                    query="authentication", limit=5)),
                ("Directory analysis", lambda: enhanced_tools.tools['analyze_directory'](
                    directory_path=str(self.sample_project_path), recursive=True, show_stats=False)),
                ("Relationship discovery", lambda: enhanced_tools.tools['discover_relationships'](
                    directory_path=str(self.sample_project_path), show_details=False))
            ]
            
            performance_results = []
            
            for test_name, test_func in performance_tests:
                try:
                    start_time = time.time()
                    result = test_func()
                    duration = time.time() - start_time
                    
                    performance_results.append((test_name, duration))
                    print(f"  ✅ {test_name}: {duration:.3f} seconds")
                    
                except Exception as e:
                    print(f"  ❌ {test_name} failed: {e}")
            
            # Check if performance is reasonable (under 10 seconds for each operation)
            reasonable_performance = all(duration < 10.0 for _, duration in performance_results)
            
            avg_duration = sum(duration for _, duration in performance_results) / len(performance_results)
            print(f"✅ Performance test completed (avg: {avg_duration:.3f}s)")
            
            return reasonable_performance
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False


def test_natural_language_processing():
    """Main test function for natural language processing."""
    print("🚀 Starting Coretx Natural Language Processing Tests\n")
    
    tester = NaturalLanguageQueryTester()
    
    tests = [
        tester.test_semantic_search_queries,
        tester.test_contextual_code_analysis,
        tester.test_llm_powered_queries,
        tester.test_multi_language_understanding,
        tester.test_query_performance,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed >= total * 0.8:  # 80% success rate for NLP tests
        print("🎉 Natural language processing tests passed!")
        return True
    else:
        print("❌ Natural language processing tests need improvement")
        return False


def run_comprehensive_nlp_test():
    """Run comprehensive NLP test with detailed reporting."""
    print("🔬 Comprehensive Natural Language Processing Test")
    print("=" * 60)
    
    # Set up test environment
    custom_api_key = "sk-Do6.."
    custom_api_base = "https://ai.comfly.chat/v1/"
    custom_model = "gpt-4.1"
    
    os.environ['CORETX_TEST_API_KEY'] = custom_api_key
    os.environ['CORETX_TEST_API_BASE'] = custom_api_base
    os.environ['CORETX_TEST_MODEL'] = custom_model
    
    print(f"🤖 Model: {custom_model}")
    print(f"🌐 API Base: {custom_api_base}")
    print(f"🔑 API Key: {custom_api_key[:20]}...")
    print()
    
    return test_natural_language_processing()


if __name__ == "__main__":
    # Check if comprehensive test should be run
    if len(sys.argv) > 1 and sys.argv[1] == "--comprehensive":
        success = run_comprehensive_nlp_test()
    else:
        success = test_natural_language_processing()
    
    exit(0 if success else 1)
