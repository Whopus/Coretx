#!/usr/bin/env python3
"""
Coretx Basic Demo Script

This script demonstrates the core functionality of Coretx
without requiring LLM API keys.
"""

import os
import tempfile
from pathlib import Path
from coretx.graph import CodeGraph
from coretx.parsers import ParserRegistry
from coretx.utils.file_utils import FileScanner
# from coretx.utils.analyzer import CodeAnalyzer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

console = Console()

def create_sample_project():
    """Create a sample project for demonstration."""
    temp_dir = tempfile.mkdtemp(prefix="coretx_demo_")
    
    # Create Python files
    python_code = '''
"""User management module."""

import hashlib
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    """Represents a user in the system."""
    id: int
    username: str
    email: str
    password_hash: str
    
    def verify_password(self, password: str) -> bool:
        """Verify user password."""
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash

class UserService:
    """Service for managing users."""
    
    def __init__(self):
        self.users: List[User] = []
    
    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(
            id=len(self.users) + 1,
            username=username,
            email=email,
            password_hash=password_hash
        )
        self.users.append(user)
        return user
    
    def find_user(self, username: str) -> Optional[User]:
        """Find user by username."""
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user credentials."""
        user = self.find_user(username)
        if user:
            return user.verify_password(password)
        return False

def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()
'''
    
    js_code = '''
/**
 * Frontend user management
 */

class UserAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async createUser(userData) {
        const response = await fetch(`${this.baseUrl}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        return response.json();
    }
    
    async getUser(userId) {
        const response = await fetch(`${this.baseUrl}/users/${userId}`);
        return response.json();
    }
    
    async authenticateUser(username, password) {
        const response = await fetch(`${this.baseUrl}/auth`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        return response.json();
    }
}

function validateEmail(email) {
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return emailRegex.test(email);
}

export { UserAPI, validateEmail };
'''
    
    # Write files
    with open(os.path.join(temp_dir, "user_service.py"), "w") as f:
        f.write(python_code)
    
    with open(os.path.join(temp_dir, "user_api.js"), "w") as f:
        f.write(js_code)
    
    return temp_dir

def demo_basic_analysis():
    """Demonstrate basic code analysis without LLM."""
    console.print(Panel.fit("🔍 Basic Code Analysis (No LLM)", style="bold blue"))
    
    # Create sample project
    project_path = create_sample_project()
    console.print(f"Created sample project at: {project_path}")
    
    # Initialize components
    from coretx.models import AnalysisConfig
    graph = CodeGraph()
    config = AnalysisConfig()
    scanner = FileScanner(config)
    # analyzer = CodeAnalyzer()
    parser_registry = ParserRegistry()
    
    # Scan files
    console.print("\n📁 Scanning files...")
    files = scanner.scan_directory(Path(project_path))
    console.print(f"Found {len(files)} files")
    
    # Analyze files
    console.print("\n📊 Analyzing files...")
    all_entities = []
    all_relationships = []
    
    for file_path in files:
        try:
            # Get parser for file
            parser = parser_registry.get_parser_for_file(str(file_path))
            if not parser:
                console.print(f"No parser found for {file_path}")
                continue
                
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            console.print(f"Parsing {file_path} with {parser.__class__.__name__}")
            
            # Parse content
            entities, relationships = parser.parse_content(content, str(file_path))
            
            console.print(f"Found {len(entities)} entities and {len(relationships)} relationships")
            
            # Add to graph
            for entity in entities:
                graph.add_entity(entity)
                all_entities.append(entity)
            
            for relationship in relationships:
                graph.add_relationship(relationship)
                all_relationships.append(relationship)
                
        except Exception as e:
            console.print(f"Error parsing {file_path}: {e}")
            import traceback
            traceback.print_exc()
    
    # Get statistics
    stats = graph.get_graph_stats()
    
    # Display results in a table
    table = Table(title="Analysis Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Entities", str(stats.total_entities))
    table.add_row("Total Relationships", str(stats.total_relationships))
    table.add_row("Files Analyzed", str(len(files)))
    table.add_row("Python Files", str(len([f for f in files if str(f).endswith('.py')])))
    table.add_row("JavaScript Files", str(len([f for f in files if str(f).endswith('.js')])))
    
    console.print(table)
    
    return graph, all_entities, all_relationships, project_path

def demo_entity_exploration(graph, entities):
    """Demonstrate entity exploration."""
    console.print(Panel.fit("🔍 Entity Exploration", style="bold green"))
    
    # Group entities by type
    entity_types = {}
    for entity in entities:
        if entity.type not in entity_types:
            entity_types[entity.type] = []
        entity_types[entity.type].append(entity)
    
    # Display entities by type
    for entity_type, type_entities in entity_types.items():
        console.print(f"\n📋 {str(entity_type).upper()} ({len(type_entities)} found):")
        for entity in type_entities[:5]:  # Show first 5
            file_name = Path(entity.path).name
            console.print(f"  • {entity.name} in {file_name}:{entity.line_start}")
            if hasattr(entity, 'signature') and entity.signature:
                console.print(f"    Signature: {entity.signature}")
            elif entity.description:
                console.print(f"    Description: {entity.description[:50]}...")
        
        if len(type_entities) > 5:
            console.print(f"  ... and {len(type_entities) - 5} more")

def demo_graph_queries(graph):
    """Demonstrate graph querying capabilities."""
    console.print(Panel.fit("🔍 Graph Queries", style="bold yellow"))
    
    # Find entities by type using the correct method
    console.print("\n🔍 Finding classes:")
    classes = graph.find_entities(entity_type="class")
    for cls in classes:
        console.print(f"  • {cls.name} in {Path(cls.path).name}")
    
    console.print("\n🔍 Finding functions:")
    functions = graph.find_entities(entity_type="function")
    for func in functions[:5]:  # Show first 5
        console.print(f"  • {func.name} in {Path(func.path).name}")
    
    if len(functions) > 5:
        console.print(f"  ... and {len(functions) - 5} more")
    
    # Find entities by name pattern
    console.print("\n🔍 Finding entities with 'user' in name:")
    user_entities = [e for e in graph._entities.values() if 'user' in e.name.lower()]
    for entity in user_entities:
        console.print(f"  • {entity.name} ({entity.type}) in {Path(entity.path).name}")

def demo_relationships(graph, relationships):
    """Demonstrate relationship analysis."""
    console.print(Panel.fit("🕸️ Relationship Analysis", style="bold magenta"))
    
    # Group relationships by type
    rel_types = {}
    for rel in relationships:
        if rel.type not in rel_types:
            rel_types[rel.type] = []
        rel_types[rel.type].append(rel)
    
    # Display relationship statistics
    table = Table(title="Relationship Types")
    table.add_column("Type", style="cyan")
    table.add_column("Count", style="green")
    
    for rel_type, type_rels in rel_types.items():
        table.add_row(str(rel_type), str(len(type_rels)))
    
    console.print(table)
    
    # Show some example relationships
    console.print("\n🔗 Example Relationships:")
    for rel_type, type_rels in list(rel_types.items())[:3]:
        console.print(f"\n{str(rel_type).upper()}:")
        for rel in type_rels[:3]:  # Show first 3
            source = graph._entities.get(rel.source_id)
            target = graph._entities.get(rel.target_id)
            if source and target:
                console.print(f"  • {source.name} → {target.name}")

def demo_code_display(project_path):
    """Display sample code."""
    console.print(Panel.fit("📄 Sample Code", style="bold red"))
    
    # Show Python code
    python_file = os.path.join(project_path, "user_service.py")
    if os.path.exists(python_file):
        console.print("\n🐍 Python Code (user_service.py):")
        with open(python_file, "r") as f:
            code = f.read()
        
        # Show first 20 lines
        lines = code.split('\n')[:20]
        syntax = Syntax('\n'.join(lines) + '\n...', "python", theme="monokai", line_numbers=True)
        console.print(syntax)
    
    # Show JavaScript code
    js_file = os.path.join(project_path, "user_api.js")
    if os.path.exists(js_file):
        console.print("\n📜 JavaScript Code (user_api.js):")
        with open(js_file, "r") as f:
            code = f.read()
        
        # Show first 15 lines
        lines = code.split('\n')[:15]
        syntax = Syntax('\n'.join(lines) + '\n...', "javascript", theme="monokai", line_numbers=True)
        console.print(syntax)

def main():
    """Run the basic Coretx demonstration."""
    console.print(Panel.fit(
        "🌟 Coretx Basic Demonstration\n"
        "Core functionality without LLM features\n"
        "Parsing, Graph Building, and Analysis",
        style="bold blue"
    ))
    
    try:
        # Basic analysis
        graph, entities, relationships, project_path = demo_basic_analysis()
        
        # Entity exploration
        demo_entity_exploration(graph, entities)
        
        # Graph queries
        demo_graph_queries(graph)
        
        # Relationship analysis
        demo_relationships(graph, relationships)
        
        # Code display
        demo_code_display(project_path)
        
        console.print(Panel.fit(
            "✅ Basic Demonstration Complete!\n"
            "Coretx successfully parsed the codebase and\n"
            "built a comprehensive knowledge graph.\n\n"
            "For full LLM features, set OPENAI_API_KEY\n"
            "environment variable and run the full demo.",
            style="bold green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"❌ Demo failed: {e}",
            style="bold red"
        ))
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            import shutil
            if 'project_path' in locals():
                shutil.rmtree(project_path)
                console.print(f"\n🧹 Cleaned up temporary files")
        except Exception:
            pass

if __name__ == "__main__":
    main()