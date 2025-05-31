#!/usr/bin/env python3
"""
Comprehensive Coretx Query Testing on Snake Game
Tests various query capabilities without LLM timeouts.
"""

import os
import sys
sys.path.insert(0, '/workspace/Coretx')

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from coretx import Coretx

def main():
    console = Console()
    
    console.print(Panel.fit("🐍 Coretx Snake Game Query Testing", style="bold green"))
    
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
        snake_path = "/workspace/Coretx/examples/snake_game"
        console.print(f"\n📊 Analyzing Snake Game at {snake_path}...")
        
        graph = ctx.analyze(snake_path)
        
        console.print(Panel.fit("🔍 Query Testing Results", style="bold blue"))
        
        # Test 1: Find all classes
        console.print("\n📦 Test 1: Find All Classes")
        classes = [e for e in graph._entities.values() if e.type.value == "class"]
        
        class_table = Table(title="Classes Found")
        class_table.add_column("Class Name", style="cyan")
        class_table.add_column("File", style="yellow")
        class_table.add_column("Lines", style="magenta")
        
        for cls in sorted(classes, key=lambda x: x.name):
            file_name = os.path.basename(cls.path)
            lines = f"{cls.line_start}-{cls.line_end}" if cls.line_end else str(cls.line_start)
            class_table.add_row(cls.name, file_name, lines)
        
        console.print(class_table)
        
        # Test 2: Find inheritance relationships
        console.print("\n🔗 Test 2: Find Inheritance Relationships")
        inheritance_rels = [r for r in graph._relationships.values() if r.type.value == "inherits"]
        
        if inheritance_rels:
            for rel in inheritance_rels:
                source = graph._entities.get(rel.source_id)
                target = graph._entities.get(rel.target_id)
                if source and target:
                    console.print(f"  • {source.name} inherits from {target.name}")
        else:
            console.print("  No inheritance relationships found")
        
        # Test 3: Find methods by class
        console.print("\n⚙️  Test 3: Methods by Class")
        
        # Group methods by their containing class
        methods_by_class = {}
        for entity in graph._entities.values():
            if entity.type.value == "method":
                # Find the class this method belongs to
                class_entity = None
                for cls in classes:
                    if (entity.path == cls.path and 
                        cls.line_start <= entity.line_start <= (cls.line_end or float('inf'))):
                        class_entity = cls
                        break
                
                if class_entity:
                    if class_entity.name not in methods_by_class:
                        methods_by_class[class_entity.name] = []
                    methods_by_class[class_entity.name].append(entity)
        
        for class_name, methods in sorted(methods_by_class.items()):
            console.print(f"\n📋 {class_name} ({len(methods)} methods):")
            for method in sorted(methods, key=lambda x: x.line_start):
                console.print(f"  • {method.name}() - line {method.line_start}")
        
        # Test 4: Find imports and dependencies
        console.print("\n📥 Test 4: Import Analysis")
        imports = [e for e in graph._entities.values() if e.type.value == "import"]
        
        import_table = Table(title="Imports by File")
        import_table.add_column("File", style="cyan")
        import_table.add_column("Import", style="yellow")
        
        for imp in sorted(imports, key=lambda x: (x.path, x.name)):
            file_name = os.path.basename(imp.path)
            import_table.add_row(file_name, imp.name)
        
        console.print(import_table)
        
        # Test 5: Find functions (non-method functions)
        console.print("\n🔧 Test 5: Standalone Functions")
        functions = [e for e in graph._entities.values() if e.type.value == "function"]
        
        if functions:
            func_table = Table(title="Standalone Functions")
            func_table.add_column("Function", style="cyan")
            func_table.add_column("File", style="yellow")
            func_table.add_column("Line", style="magenta")
            
            for func in sorted(functions, key=lambda x: x.name):
                file_name = os.path.basename(func.path)
                func_table.add_row(func.name, file_name, str(func.line_start))
            
            console.print(func_table)
        else:
            console.print("No standalone functions found")
        
        # Test 6: Code structure tree
        console.print("\n🌳 Test 6: Code Structure Tree")
        
        # Group entities by file
        files_structure = {}
        for entity in graph._entities.values():
            if entity.type.value != "import":  # Skip imports for cleaner view
                file_name = os.path.basename(entity.path)
                if file_name not in files_structure:
                    files_structure[file_name] = {"classes": [], "functions": [], "methods": []}
                
                if entity.type.value == "class":
                    files_structure[file_name]["classes"].append(entity)
                elif entity.type.value == "function":
                    files_structure[file_name]["functions"].append(entity)
                elif entity.type.value == "method":
                    files_structure[file_name]["methods"].append(entity)
        
        tree = Tree("🐍 Snake Game Structure")
        
        for file_name, structure in sorted(files_structure.items()):
            file_node = tree.add(f"📄 {file_name}")
            
            if structure["classes"]:
                classes_node = file_node.add("📦 Classes")
                for cls in sorted(structure["classes"], key=lambda x: x.line_start):
                    class_node = classes_node.add(f"{cls.name}")
                    
                    # Add methods for this class
                    class_methods = [m for m in structure["methods"] 
                                   if cls.line_start <= m.line_start <= (cls.line_end or float('inf'))]
                    if class_methods:
                        methods_node = class_node.add("⚙️ Methods")
                        for method in sorted(class_methods, key=lambda x: x.line_start):
                            methods_node.add(f"{method.name}()")
            
            if structure["functions"]:
                funcs_node = file_node.add("🔧 Functions")
                for func in sorted(structure["functions"], key=lambda x: x.line_start):
                    funcs_node.add(f"{func.name}()")
        
        console.print(tree)
        
        # Test 7: Relationship analysis
        console.print("\n🔗 Test 7: Relationship Analysis")
        
        rel_stats = {}
        for rel in graph._relationships.values():
            rel_type = rel.type.value
            rel_stats[rel_type] = rel_stats.get(rel_type, 0) + 1
        
        rel_table = Table(title="Relationship Statistics")
        rel_table.add_column("Relationship Type", style="cyan")
        rel_table.add_column("Count", style="magenta")
        rel_table.add_column("Description", style="yellow")
        
        descriptions = {
            "contains": "File/module contains entity",
            "inherits": "Class inheritance",
            "calls": "Function/method calls",
            "imports": "Import dependencies",
            "uses": "Entity usage"
        }
        
        for rel_type, count in sorted(rel_stats.items()):
            desc = descriptions.get(rel_type, "Other relationship")
            rel_table.add_row(rel_type.replace("_", " ").title(), str(count), desc)
        
        console.print(rel_table)
        
        # Test 8: Find specific patterns
        console.print("\n🎯 Test 8: Pattern Analysis")
        
        # Find AI-related classes
        ai_classes = [c for c in classes if "ai" in c.name.lower()]
        if ai_classes:
            console.print(f"\n🤖 AI-related classes ({len(ai_classes)}):")
            for cls in ai_classes:
                console.print(f"  • {cls.name}")
        
        # Find game-related classes
        game_classes = [c for c in classes if any(word in c.name.lower() 
                                                for word in ["game", "snake", "food", "score"])]
        if game_classes:
            console.print(f"\n🎮 Game-related classes ({len(game_classes)}):")
            for cls in game_classes:
                console.print(f"  • {cls.name}")
        
        # Find utility classes
        util_classes = [c for c in classes if any(word in c.name.lower() 
                                                for word in ["util", "config", "manager", "finder"])]
        if util_classes:
            console.print(f"\n🛠️  Utility classes ({len(util_classes)}):")
            for cls in util_classes:
                console.print(f"  • {cls.name}")
        
        console.print(f"\n✅ Query testing completed successfully!")
        console.print(f"📊 Analyzed {len(graph._entities)} entities and {len(graph._relationships)} relationships")
        
    except Exception as e:
        console.print(f"❌ Query testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()