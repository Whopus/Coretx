# Coretx Examples

This document provides practical examples of using Coretx for various code analysis tasks.

## Basic Usage

### Analyzing a Python Project

```python
from coretx import Coretx

# Initialize Coretx
coretx = Coretx()

# Analyze a Python project
graph = coretx.analyze("./my-python-project")

# Get basic statistics
stats = coretx.get_stats()
print(f"Found {stats.total_entities} entities in {stats.total_files} files")
```

### Querying Code

```python
# Find all classes
result = coretx.query(graph, "Show me all classes")
for entity in result.entities:
    print(f"Class: {entity.name} in {entity.file_path}")

# Find database-related functions
result = coretx.query(graph, "Find all database functions")
print(f"Database functions: {len(result.entities)}")

# Find API endpoints
result = coretx.query(graph, "Show me all API endpoints and routes")
for entity in result.entities:
    print(f"Endpoint: {entity.name} - {entity.signature}")
```

## Advanced Analysis

### Dependency Tracing

```python
# Trace dependencies for a specific class
trace = coretx.trace(graph, "UserService")

print(f"Dependencies of UserService:")
for dep in trace.dependencies:
    print(f"  - {dep.name} ({dep.type})")

print(f"Things that depend on UserService:")
for dependent in trace.dependents:
    print(f"  - {dependent.name} ({dependent.type})")
```

### Context Extraction

```python
# Get context for debugging a specific issue
context = coretx.locate(graph, "Why is the user authentication failing?")

print("Minimal code closure:")
print(context.minimal_closure)

print("\nEntry points:")
for entry in context.entry_points:
    print(f"  - {entry.name} in {entry.file_path}")

print("\nSuggested fixes:")
for suggestion in context.fix_suggestions:
    print(f"  - {suggestion}")
```

## Language-Specific Examples

### JavaScript/TypeScript Project

```python
from coretx import Coretx, AnalysisConfig

# Configure for JavaScript/TypeScript
config = AnalysisConfig(
    include_patterns=["*.js", "*.ts", "*.jsx", "*.tsx"],
    exclude_patterns=["node_modules", "dist", "build"]
)

coretx = Coretx(analysis_config=config)
graph = coretx.analyze("./my-react-app")

# Find React components
result = coretx.query(graph, "Show me all React components")
for component in result.entities:
    print(f"Component: {component.name}")

# Find async functions
result = coretx.query(graph, "Find all async functions")
print(f"Found {len(result.entities)} async functions")
```

### Multi-Language Project

```python
# Analyze a full-stack project with Python backend and JS frontend
config = AnalysisConfig(
    include_patterns=["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"],
    exclude_patterns=["__pycache__", "node_modules", ".git", "venv"]
)

coretx = Coretx(analysis_config=config)
graph = coretx.analyze("./fullstack-project")

# Find API connections between frontend and backend
result = coretx.query(graph, "Show me API calls from frontend to backend")
print(f"API connections: {len(result.entities)}")
```

## Problem-Solving Scenarios

### Finding Security Issues

```python
# Look for potential security vulnerabilities
result = coretx.query(graph, "Find functions that handle user input without validation")

print("Potential security issues:")
for entity in result.entities:
    print(f"  - {entity.name} in {entity.file_path}:{entity.start_line}")
    if entity.docstring:
        print(f"    Description: {entity.docstring[:100]}...")
```

### Performance Analysis

```python
# Find performance bottlenecks
result = coretx.query(graph, "Show me functions with loops or heavy computations")

print("Potential performance bottlenecks:")
for entity in result.entities:
    print(f"  - {entity.name} ({entity.type})")
    
# Trace dependencies of critical functions
critical_functions = ["process_large_dataset", "calculate_metrics"]
for func_name in critical_functions:
    trace = coretx.trace(graph, func_name)
    print(f"\n{func_name} depends on {len(trace.dependencies)} other functions")
```

### Code Quality Assessment

```python
# Find functions without documentation
result = coretx.query(graph, "Find functions without docstrings")
print(f"Undocumented functions: {len(result.entities)}")

# Find large functions that might need refactoring
result = coretx.query(graph, "Show me functions with more than 50 lines")
print(f"Large functions: {len(result.entities)}")

# Find duplicate or similar code
result = coretx.query(graph, "Find similar or duplicate functions")
for entity in result.entities:
    print(f"  - {entity.name} (similarity score in metadata)")
```

## Integration Examples

### CI/CD Integration

```python
import sys
from coretx import Coretx

def analyze_code_quality(project_path):
    """Analyze code quality for CI/CD pipeline."""
    coretx = Coretx()
    graph = coretx.analyze(project_path)
    
    # Check for common issues
    issues = []
    
    # Find functions without documentation
    result = coretx.query(graph, "Find public functions without docstrings")
    if result.entities:
        issues.append(f"Found {len(result.entities)} undocumented public functions")
    
    # Find potential security issues
    result = coretx.query(graph, "Find functions that use eval or exec")
    if result.entities:
        issues.append(f"Found {len(result.entities)} functions using eval/exec")
    
    # Find large functions
    result = coretx.query(graph, "Find functions with more than 100 lines")
    if result.entities:
        issues.append(f"Found {len(result.entities)} functions over 100 lines")
    
    return issues

# Run analysis
issues = analyze_code_quality("./project")
if issues:
    print("Code quality issues found:")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)
else:
    print("Code quality check passed!")
```

### Documentation Generation

```python
def generate_api_docs(project_path):
    """Generate API documentation from code analysis."""
    coretx = Coretx()
    graph = coretx.analyze(project_path)
    
    # Find all public API functions
    result = coretx.query(graph, "Find all public API functions and classes")
    
    docs = []
    for entity in result.entities:
        doc = {
            "name": entity.name,
            "type": entity.type,
            "file": entity.file_path,
            "signature": entity.signature,
            "description": entity.docstring or "No description available"
        }
        
        # Get dependencies
        trace = coretx.trace(graph, entity.name)
        doc["dependencies"] = [dep.name for dep in trace.dependencies]
        
        docs.append(doc)
    
    return docs

# Generate documentation
api_docs = generate_api_docs("./api-project")
for doc in api_docs:
    print(f"## {doc['name']}")
    print(f"**Type:** {doc['type']}")
    print(f"**File:** {doc['file']}")
    print(f"**Description:** {doc['description']}")
    if doc['dependencies']:
        print(f"**Dependencies:** {', '.join(doc['dependencies'])}")
    print()
```

### Code Migration Assistant

```python
def analyze_migration_impact(project_path, old_function, new_function):
    """Analyze the impact of migrating from old to new function."""
    coretx = Coretx()
    graph = coretx.analyze(project_path)
    
    # Find all usages of the old function
    result = coretx.query(graph, f"Find all calls to {old_function}")
    
    print(f"Migration impact analysis for {old_function} -> {new_function}:")
    print(f"Found {len(result.entities)} usages to update")
    
    # Trace dependencies
    trace = coretx.trace(graph, old_function)
    
    print(f"\nFunctions that will be affected:")
    for dependent in trace.dependents:
        print(f"  - {dependent.name} in {dependent.file_path}")
    
    # Get migration context
    context = coretx.locate(graph, f"How to migrate from {old_function} to {new_function}?")
    
    print(f"\nMigration suggestions:")
    for suggestion in context.fix_suggestions:
        print(f"  - {suggestion}")

# Analyze migration
analyze_migration_impact("./project", "old_auth_function", "new_auth_service")
```

## CLI Examples

### Basic CLI Usage

```bash
# Analyze a project
coretx analyze ./my-project

# Query for specific patterns
coretx query "Find all database connections"

# Get context for debugging
coretx locate "Why is the API returning 500 errors?"

# Trace dependencies
coretx trace "UserController"

# Get project statistics
coretx stats
```

### Advanced CLI Usage

```bash
# Analyze with custom patterns
coretx analyze --include "*.py,*.js" --exclude "test_*" ./project

# Output in JSON format
coretx query --format json "Find all classes" > classes.json

# Analyze specific directories
coretx analyze --max-depth 3 ./src

# Verbose output
coretx analyze --verbose ./project

# Save analysis results
coretx analyze --output analysis.json ./project
```

### Batch Processing

```bash
# Analyze multiple projects
for project in project1 project2 project3; do
    echo "Analyzing $project..."
    coretx analyze --output "${project}_analysis.json" "./$project"
done

# Generate reports for all projects
coretx report --input "*_analysis.json" --output summary_report.html
```

## Custom Extensions

### Adding Custom Queries

```python
from coretx import Coretx
from coretx.llm import QueryProcessor

class CustomQueryProcessor(QueryProcessor):
    def process_custom_query(self, graph, query):
        """Handle domain-specific queries."""
        if "microservice" in query.lower():
            # Custom logic for microservice analysis
            return self.find_microservice_patterns(graph)
        return super().process_query(graph, query)
    
    def find_microservice_patterns(self, graph):
        """Find microservice-specific patterns."""
        # Implementation for microservice analysis
        pass

# Use custom processor
coretx = Coretx()
coretx.query_processor = CustomQueryProcessor(coretx.llm_client)
```

### Custom Entity Types

```python
from coretx.models import EntityType

# Define custom entity types
class CustomEntityType(EntityType):
    MICROSERVICE = "microservice"
    API_GATEWAY = "api_gateway"
    DATABASE_SCHEMA = "database_schema"

# Use in custom parser
class CustomParser(BaseParser):
    def parse_content(self, content, file_path):
        entities = []
        # Custom parsing logic
        if self.is_microservice_file(file_path):
            entity = CodeEntity(
                id=f"ms_{file_path}",
                name=self.extract_service_name(content),
                type=CustomEntityType.MICROSERVICE,
                file_path=file_path,
                start_line=1,
                end_line=len(content.split('\n'))
            )
            entities.append(entity)
        return entities, []
```

These examples demonstrate the flexibility and power of Coretx for various code analysis scenarios. The system can be extended and customized to meet specific project needs while maintaining a clean and intuitive API.