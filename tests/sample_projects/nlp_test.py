#!/usr/bin/env python3
"""
Natural Language Processing test for Coretx with OpenAI integration.

This script demonstrates how to use Coretx for natural language code queries
using the provided OpenAI API configuration.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Coretx components
try:
    from coretx.core.extensions.registry import registry
    from coretx.core.agent.enhanced_tools import enhanced_tools
    from coretx.config import LocAgentConfig
    from coretx.core.agent import LocalizationAgent
    print("✅ Successfully imported Coretx components")
except ImportError as e:
    print(f"❌ Failed to import Coretx: {e}")
    sys.exit(1)


class NaturalLanguageCoretxTester:
    """Test class for natural language queries with Coretx."""
    
    def __init__(self):
        # OpenAI configuration as provided by the user
        self.openai_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
        self.openai_base_url = "https://ai.comfly.chat/v1/"
        self.model_name = "gpt-4.1"
        
        # Test project path
        self.test_project_path = os.path.dirname(os.path.abspath(__file__))
        
        print(f"🔧 Initialized Natural Language Coretx Tester")
        print(f"📁 Test project path: {self.test_project_path}")
        print(f"🤖 Model: {self.model_name}")
        print(f"🌐 API Base URL: {self.openai_base_url}")
        
        # Initialize the multi-language system
        try:
            registry.initialize_default_parsers()
            print("✅ Initialized multi-language parsers")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize parsers: {e}")
        
        # Setup agent configuration
        self.setup_agent()
    
    def setup_agent(self):
        """Setup the localization agent with OpenAI configuration."""
        try:
            # Create agent configuration
            from coretx.config import AgentConfig
            
            agent_config = AgentConfig(
                model_name=self.model_name,
                api_key=self.openai_api_key,
                api_base=self.openai_base_url,
                temperature=0.1,
                max_tokens=2048
            )
            
            # Create the localization agent
            self.agent = LocalizationAgent(agent_config)
            print("✅ Configured localization agent with OpenAI settings")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not setup agent: {e}")
            self.agent = None
    
    def analyze_codebase_structure(self):
        """Analyze the codebase structure first."""
        print(f"\n🏗️  Analyzing codebase structure...")
        
        try:
            # Get directory analysis
            result = enhanced_tools.tools['analyze_directory'](
                directory_path=self.test_project_path,
                recursive=True,
                show_stats=False  # Don't show stats to reduce output
            )
            
            # Extract key information
            entities = result.get('entities', [])
            
            # Group entities by type and file
            structure = {
                'files': {},
                'classes': [],
                'functions': [],
                'imports': []
            }
            
            for entity in entities:
                entity_type = entity.get('type', 'unknown')
                entity_name = entity.get('name', 'unnamed')
                entity_file = entity.get('file', 'unknown')
                
                if entity_type == 'file' and entity_file.endswith('.py'):
                    structure['files'][entity_name] = {
                        'path': entity_file,
                        'lines': entity.get('lines', 'unknown')
                    }
                elif entity_type == 'class':
                    structure['classes'].append({
                        'name': entity_name,
                        'file': entity_file,
                        'lines': entity.get('lines', 'unknown')
                    })
                elif entity_type in ['function', 'method']:
                    structure['functions'].append({
                        'name': entity_name,
                        'file': entity_file,
                        'lines': entity.get('lines', 'unknown')
                    })
                elif entity_type == 'import':
                    structure['imports'].append({
                        'name': entity_name,
                        'file': entity_file
                    })
            
            return structure
            
        except Exception as e:
            print(f"❌ Error analyzing codebase: {e}")
            return None
    
    def test_natural_language_query(self, query: str, context: dict = None):
        """Test a natural language query against the codebase."""
        print(f"\n🔍 Testing query: '{query}'")
        
        if not self.agent:
            print("❌ Agent not available, skipping natural language test")
            return {"success": False, "error": "Agent not configured"}
        
        try:
            start_time = time.time()
            
            # Prepare context information
            context_info = ""
            if context:
                context_info = f"""
                
Codebase Context:
- Files: {len(context.get('files', {}))} Python files
- Classes: {len(context.get('classes', []))} classes found
- Functions: {len(context.get('functions', []))} functions found
- Key files: {', '.join(list(context.get('files', {}).keys())[:5])}
"""
            
            # Create a comprehensive prompt
            prompt = f"""
You are analyzing a Python web application codebase. The user has asked: "{query}"

{context_info}

Please analyze the codebase and provide specific information about:
1. Which files are most relevant to this query
2. Which classes and functions should be examined
3. What specific code patterns or issues to look for
4. Any potential solutions or areas of concern

Be specific and reference actual file names, class names, and function names from the codebase.
"""
            
            # Use the agent to process the query
            response = self.agent.process_query(prompt)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Query processed in {duration:.2f} seconds")
            
            return {
                "success": True,
                "query": query,
                "response": response,
                "duration": duration
            }
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def test_code_search_with_context(self, search_terms: list, context: dict = None):
        """Test code search with natural language context."""
        print(f"\n🔎 Testing contextual code search...")
        
        results = {}
        
        for term in search_terms:
            try:
                print(f"  🔍 Searching for: '{term}'")
                
                start_time = time.time()
                
                # Search for entities
                search_result = enhanced_tools.tools['search_entities'](
                    query=term,
                    limit=5
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[term] = {
                    "success": True,
                    "result": search_result,
                    "duration": duration
                }
                
                print(f"    ✅ Found results in {duration:.2f} seconds")
                
            except Exception as e:
                print(f"    ❌ Error searching for '{term}': {e}")
                results[term] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def run_comprehensive_nlp_test(self):
        """Run a comprehensive natural language processing test."""
        print("🚀 Starting Comprehensive Natural Language Test")
        print("=" * 60)
        
        # Step 1: Analyze codebase structure
        print("\n📊 Step 1: Analyzing Codebase Structure")
        print("-" * 40)
        
        structure = self.analyze_codebase_structure()
        
        if structure:
            print(f"✅ Found {len(structure['files'])} Python files")
            print(f"✅ Found {len(structure['classes'])} classes")
            print(f"✅ Found {len(structure['functions'])} functions")
            
            # Show key components
            print("\n🏗️  Key Components:")
            for class_info in structure['classes'][:5]:
                print(f"  📦 Class: {class_info['name']} in {class_info['file']}")
            
            for func_info in structure['functions'][:5]:
                print(f"  ⚡ Function: {func_info['name']} in {func_info['file']}")
        
        # Step 2: Test natural language queries
        print("\n🗣️  Step 2: Testing Natural Language Queries")
        print("-" * 40)
        
        test_queries = [
            "Find code that handles user authentication and login",
            "Locate password hashing and security functions",
            "Show me session management and token handling code",
            "Find database connection and query code",
            "Locate input validation and sanitization functions",
            "Show me error handling and API response code"
        ]
        
        query_results = {}
        
        for query in test_queries:
            result = self.test_natural_language_query(query, structure)
            query_results[query] = result
            
            if result.get("success"):
                print(f"✅ Query processed successfully")
                # Print a brief summary of the response
                response = result.get("response", "")
                if isinstance(response, str) and len(response) > 200:
                    print(f"📝 Response preview: {response[:200]}...")
                else:
                    print(f"📝 Response: {response}")
            else:
                print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
            
            # Add delay between queries to avoid rate limiting
            time.sleep(2)
        
        # Step 3: Test contextual code search
        print("\n🔎 Step 3: Testing Contextual Code Search")
        print("-" * 40)
        
        search_terms = [
            "authentication",
            "password hash",
            "session token",
            "database connection",
            "user validation",
            "API endpoint"
        ]
        
        search_results = self.test_code_search_with_context(search_terms, structure)
        
        # Compile final results
        final_results = {
            "codebase_structure": structure,
            "natural_language_queries": query_results,
            "contextual_search": search_results,
            "test_metadata": {
                "model": self.model_name,
                "api_base": self.openai_base_url,
                "test_time": time.time(),
                "project_path": self.test_project_path
            }
        }
        
        return final_results
    
    def print_final_summary(self, results: dict):
        """Print a final summary of all test results."""
        print("\n📈 Final Test Summary")
        print("=" * 50)
        
        # Codebase analysis summary
        structure = results.get("codebase_structure", {})
        if structure:
            print(f"📊 Codebase Analysis:")
            print(f"  📁 Python files: {len(structure.get('files', {}))}")
            print(f"  📦 Classes: {len(structure.get('classes', []))}")
            print(f"  ⚡ Functions: {len(structure.get('functions', []))}")
        
        # Natural language queries summary
        nlp_results = results.get("natural_language_queries", {})
        successful_queries = sum(1 for r in nlp_results.values() if r.get("success"))
        total_queries = len(nlp_results)
        
        print(f"\n🗣️  Natural Language Queries:")
        print(f"  ✅ Successful: {successful_queries}/{total_queries}")
        print(f"  📊 Success rate: {(successful_queries/total_queries*100):.1f}%" if total_queries > 0 else "No queries")
        
        if successful_queries > 0:
            avg_duration = sum(r.get("duration", 0) for r in nlp_results.values() if r.get("success")) / successful_queries
            print(f"  ⏱️  Average duration: {avg_duration:.2f} seconds")
        
        # Search results summary
        search_results = results.get("contextual_search", {})
        successful_searches = sum(1 for r in search_results.values() if r.get("success"))
        total_searches = len(search_results)
        
        print(f"\n🔎 Contextual Search:")
        print(f"  ✅ Successful: {successful_searches}/{total_searches}")
        print(f"  📊 Success rate: {(successful_searches/total_searches*100):.1f}%" if total_searches > 0 else "No searches")
        
        # Overall success
        total_tests = total_queries + total_searches
        total_successful = successful_queries + successful_searches
        
        print(f"\n🎯 Overall Results:")
        print(f"  ✅ Total successful tests: {total_successful}")
        print(f"  ❌ Total failed tests: {total_tests - total_successful}")
        print(f"  📊 Overall success rate: {(total_successful/total_tests*100):.1f}%" if total_tests > 0 else "No tests")


def main():
    """Main function to run the natural language processing tests."""
    
    print("🎉 Welcome to Coretx Natural Language Testing Suite")
    print("=" * 60)
    
    # Initialize tester
    tester = NaturalLanguageCoretxTester()
    
    # Check if test files exist
    test_files = ["sample_app.py", "utils.py", "web_server.py", "config.py"]
    missing_files = []
    
    for file in test_files:
        file_path = os.path.join(tester.test_project_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return
    
    print(f"✅ All test files found: {test_files}")
    
    try:
        # Run comprehensive test
        print("\n🧪 Running Comprehensive Natural Language Processing Test...")
        results = tester.run_comprehensive_nlp_test()
        
        # Print final summary
        tester.print_final_summary(results)
        
        # Save results to file
        results_file = os.path.join(tester.test_project_path, "nlp_coretx_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        print("\n🎉 Natural Language Processing testing completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()