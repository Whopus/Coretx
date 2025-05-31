#!/usr/bin/env python3
"""
Simple test of Coretx on Snake Game without semantic analysis or queries.
"""

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from coretx import Coretx

def main():
    console = Console()
    
    console.print(Panel.fit("🐍 Coretx Snake Game Analysis (Simple)", style="bold green"))
    
    try:
        # Initialize Coretx
        console.print("\n🔧 Initializing Coretx...")
        ctx = Coretx(
            model="gpt-4.1",
            embedding_model="BAAI/bge-m3",
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_base_url=os.environ["OPENAI_BASE_URL"]
        )
        
        # Disable semantic analysis for speed
        ctx.semantic_analyzer = None
        
        # Analyze snake game
        snake_path = "/workspace/snake_game"
        console.print(f"\n📊 Analyzing Snake Game at {snake_path}...")
        
        graph = ctx.analyze(snake_path)
        
        # Display results
        console.print(Panel.fit("📈 Analysis Results", style="bold blue"))
        
        stats = graph.get_graph_stats()
        
        # Main stats table
        table = Table(title="Graph Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Entities", str(stats.total_entities))
        table.add_row("Total Relationships", str(stats.total_relationships))
        table.add_row("Files Analyzed", str(len(graph.files)))
        table.add_row("Total Lines", str(stats.total_lines))
        
        console.print(table)
        
        # Entity breakdown
        entity_table = Table(title="Entity Breakdown")
        entity_table.add_column("Type", style="cyan")
        entity_table.add_column("Count", style="magenta")
        
        entity_counts = {}
        for entity in graph.entities.values():
            entity_type = entity.type.value
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        for entity_type, count in sorted(entity_counts.items()):
            entity_table.add_row(entity_type.title(), str(count))
        
        console.print(entity_table)
        
        # Show some sample entities
        console.print(Panel.fit("🔍 Sample Entities", style="bold yellow"))
        
        classes = [e for e in graph.entities.values() if e.type.value == "class"]
        functions = [e for e in graph.entities.values() if e.type.value == "function"]
        methods = [e for e in graph.entities.values() if e.type.value == "method"]
        
        if classes:
            console.print(f"\n📦 Classes ({len(classes)}):")
            for cls in classes[:10]:  # Show first 10
                console.print(f"  • {cls.name} ({cls.path}:{cls.line_start})")
        
        if functions:
            console.print(f"\n🔧 Functions ({len(functions)}):")
            for func in functions[:10]:  # Show first 10
                console.print(f"  • {func.name} ({func.path}:{func.line_start})")
        
        if methods:
            console.print(f"\n⚙️  Methods ({len(methods)}):")
            for method in methods[:10]:  # Show first 10
                console.print(f"  • {method.name} ({method.path}:{method.line_start})")
        
        # Show relationships
        console.print(Panel.fit("🔗 Sample Relationships", style="bold cyan"))
        
        rel_counts = {}
        for rel in graph.relationships.values():
            rel_type = rel.type.value
            rel_counts[rel_type] = rel_counts.get(rel_type, 0) + 1
        
        rel_table = Table(title="Relationship Types")
        rel_table.add_column("Type", style="cyan")
        rel_table.add_column("Count", style="magenta")
        
        for rel_type, count in sorted(rel_counts.items()):
            rel_table.add_row(rel_type.replace("_", " ").title(), str(count))
        
        console.print(rel_table)
        
        # Show some sample relationships
        sample_rels = list(graph.relationships.values())[:10]
        if sample_rels:
            console.print(f"\n🔗 Sample Relationships:")
            for rel in sample_rels:
                source = graph.entities.get(rel.source_id)
                target = graph.entities.get(rel.target_id)
                if source and target:
                    console.print(f"  • {source.name} --[{rel.type.value}]--> {target.name}")
        
        console.print(f"\n✅ Analysis completed successfully!")
        console.print(f"Graph saved to: {snake_path}/.coretx/graph.json")
        
    except Exception as e:
        console.print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()