#!/usr/bin/env python3
"""
Coretx Demo Script

This script demonstrates the complete functionality of Coretx,
a lightweight kernel for building comprehensive knowledge graphs
of your codebase.
"""

import os
import tempfile
from pathlib import Path
from coretx import Coretx
from coretx.models import LLMConfig, AnalysisConfig
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
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
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
    """Demonstrate basic code analysis."""
    console.print(Panel.fit("🔍 Basic Code Analysis", style="bold blue"))
    
    # Create sample project
    project_path = create_sample_project()
    console.print(f"Created sample project at: {project_path}")
    
    # Initialize Coretx
    coretx = Coretx()
    
    # Analyze the project
    console.print("\n📊 Analyzing project...")
    graph = coretx.analyze(project_path)
    
    # Get statistics
    stats = coretx.get_stats()
    
    # Display results in a table
    table = Table(title="Analysis Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Entities", str(stats.total_entities))
    table.add_row("Total Relationships", str(stats.total_relationships))
    table.add_row("Files Analyzed", str(len(stats.files_analyzed)))
    table.add_row("Languages", ", ".join(stats.languages))
    
    console.print(table)
    
    return coretx, graph, project_path

def demo_querying(coretx, graph):
    """Demonstrate natural language querying."""
    console.print(Panel.fit("💬 Natural Language Querying", style="bold green"))
    
    queries = [
        "Show me all classes",
        "Find all functions that handle passwords",
        "Show me authentication-related code",
        "Find all async functions"
    ]
    
    for query in queries:
        console.print(f"\n🔍 Query: [bold]{query}[/bold]")
        
        try:
            result = coretx.query(graph, query)
            
            if result.entities:
                console.print(f"Found {len(result.entities)} entities:")
                for entity in result.entities[:3]:  # Show first 3
                    console.print(f"  • {entity.name} ({entity.type}) in {Path(entity.file_path).name}")
                
                if len(result.entities) > 3:
                    console.print(f"  ... and {len(result.entities) - 3} more")
            else:
                console.print("  No entities found")
                
            if result.summary:
                console.print(f"Summary: {result.summary}")
                
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")

def demo_context_extraction(coretx, graph):
    """Demonstrate context extraction for problem-solving."""
    console.print(Panel.fit("🎯 Context Extraction", style="bold yellow"))
    
    problems = [
        "How does user authentication work?",
        "Where is password hashing implemented?",
        "How to add email validation?"
    ]
    
    for problem in problems:
        console.print(f"\n🤔 Problem: [bold]{problem}[/bold]")
        
        try:
            context = coretx.locate(graph, problem)
            
            console.print("📋 Entry Points:")
            for entry in context.entry_points[:2]:  # Show first 2
                console.print(f"  • {entry.name} in {Path(entry.file_path).name}")
            
            if context.fix_suggestions:
                console.print("💡 Suggestions:")
                for suggestion in context.fix_suggestions[:2]:  # Show first 2
                    console.print(f"  • {suggestion}")
            
            if context.analysis_summary:
                console.print(f"📝 Summary: {context.analysis_summary}")
                
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")

def demo_dependency_tracing(coretx, graph):
    """Demonstrate dependency tracing."""
    console.print(Panel.fit("🕸️ Dependency Tracing", style="bold magenta"))
    
    # Get some entities to trace
    all_entities = []
    for entity_type in ["class", "function"]:
        result = coretx.query(graph, f"Show me all {entity_type}s")
        all_entities.extend(result.entities)
    
    if not all_entities:
        console.print("No entities found for tracing")
        return
    
    # Trace a few entities
    for entity in all_entities[:3]:
        console.print(f"\n🔍 Tracing: [bold]{entity.name}[/bold]")
        
        try:
            trace = coretx.trace(graph, entity.name)
            
            console.print(f"Dependencies: {len(trace.dependencies)}")
            for dep in trace.dependencies[:2]:  # Show first 2
                console.print(f"  ← {dep.name} ({dep.type})")
            
            console.print(f"Dependents: {len(trace.dependents)}")
            for dep in trace.dependents[:2]:  # Show first 2
                console.print(f"  → {dep.name} ({dep.type})")
                
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")

def demo_advanced_features(coretx, graph, project_path):
    """Demonstrate advanced features."""
    console.print(Panel.fit("🚀 Advanced Features", style="bold red"))
    
    # Show some code
    console.print("\n📄 Sample Code:")
    try:
        python_file = os.path.join(project_path, "user_service.py")
        with open(python_file, "r") as f:
            code = f.read()
        
        syntax = Syntax(code[:500] + "...", "python", theme="monokai", line_numbers=True)
        console.print(syntax)
    except Exception as e:
        console.print(f"[red]Error displaying code: {e}[/red]")
    
    # Advanced queries
    console.print("\n🔬 Advanced Analysis:")
    
    advanced_queries = [
        "Find potential security issues",
        "Show me all data classes",
        "Find functions that might need error handling"
    ]
    
    for query in advanced_queries:
        console.print(f"\n🔍 {query}:")
        try:
            result = coretx.query(graph, query)
            if result.entities:
                console.print(f"  Found {len(result.entities)} relevant entities")
            else:
                console.print("  No specific issues found")
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")

def main():
    """Run the complete Coretx demonstration."""
    console.print(Panel.fit(
        "🌟 Coretx Demonstration\n"
        "A lightweight kernel for building comprehensive\n"
        "knowledge graphs of your codebase",
        style="bold blue"
    ))
    
    try:
        # Basic analysis
        coretx, graph, project_path = demo_basic_analysis()
        
        # Natural language querying
        demo_querying(coretx, graph)
        
        # Context extraction
        demo_context_extraction(coretx, graph)
        
        # Dependency tracing
        demo_dependency_tracing(coretx, graph)
        
        # Advanced features
        demo_advanced_features(coretx, graph, project_path)
        
        console.print(Panel.fit(
            "✅ Demonstration Complete!\n"
            "Coretx successfully analyzed the codebase and\n"
            "demonstrated its core capabilities.",
            style="bold green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"❌ Demo failed: {e}\n"
            "This might be due to missing API keys or\n"
            "network connectivity issues.",
            style="bold red"
        ))
    
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