#!/usr/bin/env python3
"""
Simple test script for Coretx using the enhanced tools system.

This script demonstrates how to use Coretx's multi-language analysis capabilities
with the provided OpenAI configuration.
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
    print("✅ Successfully imported Coretx components")
except ImportError as e:
    print(f"❌ Failed to import Coretx: {e}")
    sys.exit(1)


class SimpleCoretxTester:
    """Simple test class for Coretx enhanced tools."""
    
    def __init__(self):
        # OpenAI configuration as provided by the user
        self.openai_api_key = "sk-Do6.."
        self.openai_base_url = "https://ai.comfly.chat/v1/"
        self.model_name = "gpt-4.1"
        
        # Test project path
        self.test_project_path = os.path.dirname(os.path.abspath(__file__))
        
        print(f"🔧 Initialized Simple Coretx Tester")
        print(f"📁 Test project path: {self.test_project_path}")
        print(f"🤖 Model: {self.model_name}")
        print(f"🌐 API Base URL: {self.openai_base_url}")
        
        # Initialize the multi-language system
        try:
            registry.initialize_default_parsers()
            print("✅ Initialized multi-language parsers")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize parsers: {e}")
    
    def test_analyze_directory(self):
        """Test directory analysis with enhanced tools."""
        print(f"\n🔍 Testing directory analysis...")
        
        try:
            start_time = time.time()
            
            # Use the enhanced tools to analyze the directory
            result = enhanced_tools.tools['analyze_directory'](
                directory_path=self.test_project_path,
                recursive=True,
                show_stats=True
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Analysis completed in {duration:.2f} seconds")
            
            return {
                "success": True,
                "result": result,
                "duration": duration
            }
            
        except Exception as e:
            print(f"❌ Error in directory analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_parse_files(self):
        """Test parsing individual files."""
        print(f"\n📄 Testing file parsing...")
        
        test_files = ["sample_app.py", "utils.py", "web_server.py", "config.py"]
        results = {}
        
        for file_name in test_files:
            file_path = os.path.join(self.test_project_path, file_name)
            
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_name}")
                continue
            
            try:
                print(f"  📝 Parsing {file_name}...")
                
                start_time = time.time()
                
                result = enhanced_tools.tools['parse_file'](
                    file_path=file_path,
                    show_content=True
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[file_name] = {
                    "success": True,
                    "result": result,
                    "duration": duration
                }
                
                print(f"    ✅ Parsed in {duration:.2f} seconds")
                
            except Exception as e:
                print(f"    ❌ Error parsing {file_name}: {e}")
                results[file_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def test_search_entities(self):
        """Test entity search functionality."""
        print(f"\n🔎 Testing entity search...")
        
        search_queries = [
            "authentication",
            "password",
            "session",
            "database",
            "user",
            "login",
            "hash",
            "validate"
        ]
        
        results = {}
        
        for query in search_queries:
            try:
                print(f"  🔍 Searching for: '{query}'")
                
                start_time = time.time()
                
                result = enhanced_tools.tools['search_entities'](
                    query=query,
                    limit=5
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[query] = {
                    "success": True,
                    "result": result,
                    "duration": duration
                }
                
                print(f"    ✅ Found results in {duration:.2f} seconds")
                
            except Exception as e:
                print(f"    ❌ Error searching for '{query}': {e}")
                results[query] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def test_discover_relationships(self):
        """Test relationship discovery."""
        print(f"\n🔗 Testing relationship discovery...")
        
        try:
            start_time = time.time()
            
            result = enhanced_tools.tools['discover_relationships'](
                directory_path=self.test_project_path,
                show_details=True
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Discovery completed in {duration:.2f} seconds")
            
            return {
                "success": True,
                "result": result,
                "duration": duration
            }
            
        except Exception as e:
            print(f"❌ Error in relationship discovery: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def print_results_summary(self, results: dict, test_name: str):
        """Print a summary of test results."""
        print(f"\n📊 Summary for {test_name}:")
        print("=" * 50)
        
        if not results.get("success"):
            print(f"❌ Test failed: {results.get('error', 'Unknown error')}")
            return
        
        result_data = results.get("result", {})
        duration = results.get("duration", 0)
        
        print(f"✅ Test successful")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        # Print specific result information based on test type
        if "total_entities" in result_data:
            print(f"🎯 Total entities found: {result_data['total_entities']}")
        
        if "files_processed" in result_data:
            print(f"📁 Files processed: {result_data['files_processed']}")
        
        if "language_stats" in result_data:
            print(f"🌐 Languages detected: {list(result_data['language_stats'].keys())}")
        
        if "entities" in result_data:
            entities = result_data["entities"]
            print(f"🏗️  Entities found: {len(entities)}")
            
            # Group by type
            entity_types = {}
            for entity in entities[:10]:  # Show first 10
                entity_type = entity.get("type", "unknown")
                if entity_type not in entity_types:
                    entity_types[entity_type] = []
                entity_types[entity_type].append(entity.get("name", "unnamed"))
            
            for etype, names in entity_types.items():
                print(f"  {etype}: {', '.join(names[:3])}" + 
                      (f" (and {len(names)-3} more)" if len(names) > 3 else ""))
    
    def run_all_tests(self):
        """Run all available tests."""
        print("🚀 Starting Coretx Enhanced Tools Tests")
        print("=" * 60)
        
        all_results = {}
        
        # Test 1: Directory Analysis
        print("\n🧪 Test 1: Directory Analysis")
        print("-" * 30)
        dir_results = self.test_analyze_directory()
        self.print_results_summary(dir_results, "Directory Analysis")
        all_results["directory_analysis"] = dir_results
        
        # Test 2: File Parsing
        print("\n🧪 Test 2: File Parsing")
        print("-" * 30)
        file_results = self.test_parse_files()
        print(f"📄 Parsed {len(file_results)} files")
        successful_parses = sum(1 for r in file_results.values() if r.get("success"))
        print(f"✅ Successful parses: {successful_parses}/{len(file_results)}")
        all_results["file_parsing"] = file_results
        
        # Test 3: Entity Search
        print("\n🧪 Test 3: Entity Search")
        print("-" * 30)
        search_results = self.test_search_entities()
        successful_searches = sum(1 for r in search_results.values() if r.get("success"))
        print(f"🔍 Successful searches: {successful_searches}/{len(search_results)}")
        all_results["entity_search"] = search_results
        
        # Test 4: Relationship Discovery
        print("\n🧪 Test 4: Relationship Discovery")
        print("-" * 30)
        rel_results = self.test_discover_relationships()
        self.print_results_summary(rel_results, "Relationship Discovery")
        all_results["relationship_discovery"] = rel_results
        
        return all_results


def main():
    """Main function to run the simple Coretx tests."""
    
    print("🎉 Welcome to Simple Coretx Testing Suite")
    print("=" * 50)
    
    # Initialize tester
    tester = SimpleCoretxTester()
    
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
        # Run all tests
        results = tester.run_all_tests()
        
        # Save results to file
        results_file = os.path.join(tester.test_project_path, "simple_coretx_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        print("\n🎉 Simple Coretx testing completed!")
        
        # Print final summary
        print("\n📈 Final Summary:")
        print("=" * 30)
        
        total_tests = 0
        successful_tests = 0
        
        for test_name, test_result in results.items():
            if isinstance(test_result, dict) and "success" in test_result:
                total_tests += 1
                if test_result["success"]:
                    successful_tests += 1
            elif isinstance(test_result, dict):
                # For file parsing and entity search (multiple sub-tests)
                for sub_result in test_result.values():
                    if isinstance(sub_result, dict) and "success" in sub_result:
                        total_tests += 1
                        if sub_result["success"]:
                            successful_tests += 1
        
        print(f"✅ Successful tests: {successful_tests}")
        print(f"❌ Failed tests: {total_tests - successful_tests}")
        print(f"📊 Success rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
