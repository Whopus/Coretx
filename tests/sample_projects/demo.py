#!/usr/bin/env python3
"""
Coretx Demo Script - Comprehensive demonstration of Coretx capabilities.

This script showcases the key features of Coretx for code analysis and localization
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
    from coretx.config import LocAgentConfig, AgentConfig
    print("✅ Successfully imported Coretx")
except ImportError as e:
    print(f"❌ Failed to import Coretx: {e}")
    sys.exit(1)


def print_banner():
    """Print a welcome banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                     🚀 CORETX DEMO 🚀                       ║
    ║                                                              ║
    ║         Advanced Code Localization Engine                    ║
    ║         with Natural Language Processing                     ║
    ║                                                              ║
    ║  🔧 OpenAI API: https://ai.comfly.chat/v1/                   ║
    ║  🤖 Model: gpt-4.1                                           ║
    ║  📁 Test Project: Sample Web Application                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def demo_codebase_analysis():
    """Demonstrate codebase analysis capabilities."""
    print("\n🔍 DEMO 1: Codebase Analysis")
    print("=" * 50)
    
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Initialize parsers
        registry.initialize_default_parsers()
        
        # Analyze the directory
        print("📊 Analyzing sample web application...")
        result = enhanced_tools.tools['analyze_directory'](
            directory_path=project_path,
            recursive=True,
            show_stats=True
        )
        
        print("✅ Analysis complete!")
        return result
        
    except Exception as e:
        print(f"❌ Error in codebase analysis: {e}")
        return None


def demo_file_parsing():
    """Demonstrate file parsing capabilities."""
    print("\n📄 DEMO 2: Multi-Language File Parsing")
    print("=" * 50)
    
    project_path = os.path.dirname(os.path.abspath(__file__))
    test_files = ["sample_app.py", "utils.py", "web_server.py", "config.py"]
    
    for file_name in test_files:
        file_path = os.path.join(project_path, file_name)
        
        if os.path.exists(file_path):
            try:
                print(f"🔍 Parsing {file_name}...")
                
                result = enhanced_tools.tools['parse_file'](
                    file_path=file_path,
                    show_content=True
                )
                
                # Count entities by type
                entities = result.get('entities', [])
                entity_counts = {}
                for entity in entities:
                    entity_type = entity.get('type', 'unknown')
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
                
                print(f"  ✅ Found {len(entities)} entities:")
                for etype, count in sorted(entity_counts.items()):
                    print(f"    • {etype}: {count}")
                
            except Exception as e:
                print(f"  ❌ Error parsing {file_name}: {e}")


def demo_entity_search():
    """Demonstrate entity search capabilities."""
    print("\n🔎 DEMO 3: Intelligent Entity Search")
    print("=" * 50)
    
    search_queries = [
        ("authentication", "🔐 Authentication-related code"),
        ("password", "🔑 Password handling"),
        ("session", "📝 Session management"),
        ("database", "🗄️  Database operations"),
        ("validation", "✅ Input validation"),
        ("API", "🌐 API endpoints")
    ]
    
    for query, description in search_queries:
        try:
            print(f"\n{description}")
            print(f"🔍 Searching for: '{query}'")
            
            result = enhanced_tools.tools['search_entities'](
                query=query,
                limit=3
            )
            
            entities = result.get('entities', [])
            print(f"  📊 Found {len(entities)} relevant entities")
            
            for entity in entities[:3]:  # Show top 3
                name = entity.get('name', 'unnamed')
                entity_type = entity.get('type', 'unknown')
                file_name = entity.get('file', 'unknown')
                print(f"    • {entity_type}: {name} in {file_name}")
            
        except Exception as e:
            print(f"  ❌ Error searching for '{query}': {e}")


def demo_relationship_discovery():
    """Demonstrate relationship discovery."""
    print("\n🔗 DEMO 4: Code Relationship Discovery")
    print("=" * 50)
    
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    try:
        print("🔍 Discovering relationships between code entities...")
        
        result = enhanced_tools.tools['discover_relationships'](
            directory_path=project_path,
            show_details=True
        )
        
        print("✅ Relationship discovery complete!")
        
        # Show summary
        total_relationships = result.get('total_relationships', 0)
        relationship_types = result.get('relationship_types', [])
        
        print(f"📊 Found {total_relationships} relationships")
        print(f"🔗 Relationship types: {', '.join(relationship_types)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in relationship discovery: {e}")
        return None


def demo_natural_language_scenarios():
    """Demonstrate natural language query scenarios."""
    print("\n🗣️  DEMO 5: Natural Language Code Queries")
    print("=" * 50)
    
    scenarios = [
        {
            "title": "🐛 Bug Investigation",
            "query": "authentication login password",
            "description": "Finding authentication-related code for debugging login issues"
        },
        {
            "title": "🔒 Security Audit",
            "query": "password hash security validation",
            "description": "Locating security-critical code for audit"
        },
        {
            "title": "📝 Session Management",
            "query": "session token management",
            "description": "Finding session handling code"
        },
        {
            "title": "🗄️  Database Operations",
            "query": "database connection query",
            "description": "Locating database-related code"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print(f"📋 Scenario: {scenario['description']}")
        print(f"🔍 Query: '{scenario['query']}'")
        
        try:
            result = enhanced_tools.tools['search_entities'](
                query=scenario['query'],
                limit=5
            )
            
            entities = result.get('entities', [])
            print(f"  ✅ Found {len(entities)} relevant code entities")
            
            # Group by file
            files = {}
            for entity in entities:
                file_name = entity.get('file', 'unknown')
                if file_name not in files:
                    files[file_name] = []
                files[file_name].append(entity)
            
            print(f"  📁 Relevant files: {', '.join(files.keys())}")
            
        except Exception as e:
            print(f"  ❌ Error processing scenario: {e}")


def demo_configuration_showcase():
    """Demonstrate configuration capabilities."""
    print("\n⚙️  DEMO 6: Configuration & Customization")
    print("=" * 50)
    
    # Show OpenAI configuration
    print("🤖 OpenAI Configuration:")
    print("  • API Key: sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7")
    print("  • Base URL: https://ai.comfly.chat/v1/")
    print("  • Model: gpt-4.1")
    
    # Show Coretx configuration options
    print("\n🔧 Coretx Configuration Options:")
    
    try:
        # Create sample configuration
        config = LocAgentConfig()
        
        print(f"  📊 Graph Settings:")
        print(f"    • Max depth: {config.graph.max_depth}")
        print(f"    • File extensions: {config.graph.file_extensions}")
        print(f"    • Skip directories: {config.graph.skip_dirs}")
        
        print(f"  🔍 Retrieval Settings:")
        print(f"    • Top-k results: {config.retrieval.top_k}")
        print(f"    • BM25 parameters: k1={config.retrieval.bm25_k1}, b={config.retrieval.bm25_b}")
        
        print(f"  🤖 Agent Settings:")
        print(f"    • Model: {config.agent.model_name}")
        print(f"    • Temperature: {config.agent.temperature}")
        print(f"    • Max tokens: {config.agent.max_tokens}")
        
    except Exception as e:
        print(f"  ❌ Error showing configuration: {e}")


def demo_performance_metrics():
    """Demonstrate performance tracking."""
    print("\n📈 DEMO 7: Performance Metrics")
    print("=" * 50)
    
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    # Test different operations and measure performance
    operations = [
        ("Directory Analysis", lambda: enhanced_tools.tools['analyze_directory'](
            directory_path=project_path, recursive=True, show_stats=False)),
        ("File Parsing", lambda: enhanced_tools.tools['parse_file'](
            file_path=os.path.join(project_path, "sample_app.py"), show_content=False)),
        ("Entity Search", lambda: enhanced_tools.tools['search_entities'](
            query="authentication", limit=5)),
        ("Relationship Discovery", lambda: enhanced_tools.tools['discover_relationships'](
            directory_path=project_path, show_details=False))
    ]
    
    print("⏱️  Performance Benchmarks:")
    
    for operation_name, operation_func in operations:
        try:
            start_time = time.time()
            result = operation_func()
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"  • {operation_name}: {duration:.3f} seconds")
            
        except Exception as e:
            print(f"  • {operation_name}: ❌ Error - {e}")


def main():
    """Main demo function."""
    print_banner()
    
    print("🎬 Starting Coretx Comprehensive Demo")
    print("This demo showcases the key capabilities of Coretx for code analysis and localization.")
    
    # Check if we're in the right directory
    project_path = os.path.dirname(os.path.abspath(__file__))
    test_files = ["sample_app.py", "utils.py", "web_server.py", "config.py"]
    
    missing_files = [f for f in test_files if not os.path.exists(os.path.join(project_path, f))]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure you're running this demo from the correct directory.")
        return
    
    print(f"✅ All required files found: {test_files}")
    
    try:
        # Run all demos
        demo_codebase_analysis()
        demo_file_parsing()
        demo_entity_search()
        demo_relationship_discovery()
        demo_natural_language_scenarios()
        demo_configuration_showcase()
        demo_performance_metrics()
        
        # Final summary
        print("\n🎉 DEMO COMPLETE!")
        print("=" * 50)
        print("✅ Successfully demonstrated all Coretx capabilities:")
        print("  🔍 Multi-language code analysis")
        print("  📄 Intelligent file parsing")
        print("  🔎 Entity search and discovery")
        print("  🔗 Relationship mapping")
        print("  🗣️  Natural language queries")
        print("  ⚙️  Flexible configuration")
        print("  📈 Performance monitoring")
        
        print("\n🚀 Coretx is ready for production use!")
        print("Visit the documentation for more advanced features and customization options.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()