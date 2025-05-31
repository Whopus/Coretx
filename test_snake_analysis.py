#!/usr/bin/env python3
"""
Test Coretx analysis on the Snake Game project.
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def main():
    """Test Coretx on Snake Game."""
    console.print(Panel.fit("🐍 Coretx Snake Game Analysis", style="bold green"))
    
    # Set environment variables
    os.environ["OPENAI_API_KEY"] = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    os.environ["OPENAI_BASE_URL"] = "https://ai.comfly.chat/v1"
    
    try:
        from coretx import Coretx
        
        # Initialize Coretx
        console.print("\n🔧 Initializing Coretx...")
        ctx = Coretx(
            model="gpt-4.1",
            embedding_model="BAAI/bge-m3",
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_base_url=os.environ["OPENAI_BASE_URL"]
        )
        
        # Disable semantic analysis for speed
        ctx.analyzer.semantic_analyzer = None
        
        # Analyze snake game
        snake_path = "/workspace/snake_game"
        console.print(f"\n📊 Analyzing Snake Game at {snake_path}...")
        
        graph = ctx.analyze(snake_path)
        stats = graph.get_graph_stats()
        
        # Display analysis results
        console.print(Panel.fit("📈 Analysis Results", style="bold blue"))
        
        table = Table()
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Entities", str(stats.total_entities))
        table.add_row("Total Relationships", str(stats.total_relationships))
        table.add_row("Files Analyzed", str(stats.file_count))
        table.add_row("Total Lines", str(stats.total_lines))
        
        console.print(table)
        
        # Entity breakdown
        if stats.entity_counts:
            console.print("\n📋 Entity Breakdown:")
            entity_table = Table()
            entity_table.add_column("Type", style="cyan")
            entity_table.add_column("Count", style="white")
            
            for entity_type, count in stats.entity_counts.items():
                if count > 0:
                    entity_table.add_row(entity_type.value.title(), str(count))
            
            console.print(entity_table)
        
        # Test queries
        console.print(Panel.fit("🔍 Testing Queries", style="bold yellow"))
        
        test_queries = [
            "What classes are defined in this snake game?",
            "How does the snake movement work?",
            "What AI strategies are implemented?",
            "How is collision detection handled?",
            "What are the main game components?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            console.print(f"\n❓ Query {i}: {query}")
            try:
                result = ctx.query(graph, query)
                console.print(f"✅ Answer: {result.summary[:200]}...")
                console.print(f"🎯 Confidence: {result.confidence:.2f}")
                
                if result.entities:
                    console.print(f"📋 Found {len(result.entities)} relevant entities")
                    
            except Exception as e:
                console.print(f"❌ Query failed: {e}")
        
        # Test locate functionality
        console.print(Panel.fit("🎯 Testing Code Location", style="bold magenta"))
        
        locate_tests = [
            "Snake class implementation",
            "AI player strategies",
            "Game loop logic",
            "Collision detection code"
        ]
        
        for i, problem in enumerate(locate_tests, 1):
            console.print(f"\n🔍 Locate {i}: {problem}")
            try:
                result = ctx.locate(graph, problem)
                console.print(f"✅ Analysis: {result.analysis_summary[:150]}...")
                console.print(f"🎯 Confidence: {result.confidence:.2f}")
                
                if result.entry_points:
                    console.print(f"📍 Found {len(result.entry_points)} entry points")
                    
            except Exception as e:
                console.print(f"❌ Locate failed: {e}")
        
        # Test trace functionality
        console.print(Panel.fit("🔗 Testing Dependency Tracing", style="bold cyan"))
        
        trace_entities = ["Snake", "SnakeGame", "AIPlayer", "Food"]
        
        for entity in trace_entities:
            console.print(f"\n🔍 Tracing: {entity}")
            try:
                result = ctx.trace_dependencies(graph, entity, direction="both", max_depth=2)
                
                if result.entity:
                    console.print(f"✅ Found entity: {result.entity.type.value} {result.entity.name}")
                    console.print(f"📤 Dependencies: {len(result.dependencies)}")
                    console.print(f"📥 Dependents: {len(result.dependents)}")
                else:
                    console.print(f"❌ Entity '{entity}' not found")
                    
            except Exception as e:
                console.print(f"❌ Trace failed: {e}")
        
        console.print(Panel.fit("🎉 Snake Game Analysis Complete!", style="bold green"))
        
    except Exception as e:
        console.print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()