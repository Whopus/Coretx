# Coretx API Reference

## Core API

### Coretx Class

The main entry point for all Coretx functionality.

```python
from coretx import Coretx

# Initialize with default configuration
coretx = Coretx()

# Initialize with custom configuration
config = LLMConfig(provider="openai", api_key="your-key")
coretx = Coretx(llm_config=config)
```

#### Methods

##### `analyze(path: str) -> CodeGraph`

Analyze a codebase and build a knowledge graph.

```python
graph = coretx.analyze("/path/to/project")
print(f"Found {graph.entity_count} entities")
```

##### `query(graph: CodeGraph, query: str) -> QueryResult`

Query the codebase using natural language.

```python
result = coretx.query(graph, "Show me all database functions")
for entity in result.entities:
    print(f"- {entity.name} ({entity.type})")
```

##### `locate(graph: CodeGraph, problem: str) -> ContextResult`

Get minimal context for a specific problem.

```python
context = coretx.locate(graph, "How to fix the authentication bug?")
print(context.minimal_closure)
```

##### `trace(graph: CodeGraph, entity_name: str) -> TraceResult`

Trace dependencies for an entity.

```python
trace = coretx.trace(graph, "UserService")
print(f"Dependencies: {len(trace.dependencies)}")
print(f"Dependents: {len(trace.dependents)}")
```

##### `get_stats() -> GraphStats`

Get statistics about the knowledge graph.

```python
stats = coretx.get_stats()
print(f"Total entities: {stats.total_entities}")
print(f"Total relationships: {stats.total_relationships}")
```

## Data Models

### CodeEntity

Represents a code element (function, class, variable, etc.).

```python
@dataclass
class CodeEntity:
    id: str
    name: str
    type: EntityType
    file_path: str
    start_line: int
    end_line: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Relationship

Defines a connection between two entities.

```python
@dataclass
class Relationship:
    id: str
    source_id: str
    target_id: str
    type: RelationshipType
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### QueryResult

Result of a natural language query.

```python
@dataclass
class QueryResult:
    summary: str
    code_context: str
    entities: List[CodeEntity]
    relationships: List[Relationship]
    confidence: float
    suggestions: List[str] = field(default_factory=list)
    files: List[FileContext] = field(default_factory=list)
    diagram: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### ContextResult

Minimal closure for a specific problem.

```python
@dataclass
class ContextResult:
    minimal_closure: str
    files: List[FileContext]
    entry_points: List[CodeEntity]
    flow_diagram: str
    fix_suggestions: List[str] = field(default_factory=list)
    analysis_summary: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### TraceResult

Result of dependency tracing.

```python
@dataclass
class TraceResult:
    entity: CodeEntity
    dependencies: List[CodeEntity]
    dependents: List[CodeEntity]
    paths: List[List[CodeEntity]]
    depth: int
    metadata: Dict[str, Any] = field(default_factory=dict)
```

## Configuration

### LLMConfig

Configuration for LLM providers.

```python
@dataclass
class LLMConfig:
    provider: str = "openai"
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_tokens: int = 2000
    timeout: int = 30
    base_url: Optional[str] = None
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimensions: int = 1536
```

### AnalysisConfig

Configuration for code analysis.

```python
@dataclass
class AnalysisConfig:
    max_file_size: int = 1024 * 1024  # 1MB
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*.pyc", "__pycache__", ".git", "node_modules", ".env"
    ])
    include_patterns: List[str] = field(default_factory=lambda: [
        "*.py", "*.js", "*.ts", "*.jsx", "*.tsx"
    ])
    max_depth: int = 10
    follow_symlinks: bool = False
    enable_semantic_analysis: bool = True
    cache_embeddings: bool = True
```

## CLI Interface

### Basic Usage

```bash
# Analyze a project
coretx analyze /path/to/project

# Query the codebase
coretx query "Show me all API endpoints"

# Get context for a problem
coretx locate "How to fix the memory leak?"

# Trace dependencies
coretx trace "DatabaseManager"

# Get statistics
coretx stats
```

### Advanced Options

```bash
# Custom configuration
coretx analyze --config config.yaml /path/to/project

# Specific file types
coretx analyze --include "*.py,*.js" /path/to/project

# Exclude patterns
coretx analyze --exclude "test_*,*_test.py" /path/to/project

# Output format
coretx query --format json "Show me all classes"

# Verbose output
coretx analyze --verbose /path/to/project
```

## Examples

### Basic Analysis

```python
from coretx import Coretx

# Initialize
coretx = Coretx()

# Analyze project
graph = coretx.analyze("./my-project")

# Query for functions
result = coretx.query(graph, "Show me all async functions")
print(f"Found {len(result.entities)} async functions")

# Get context for a bug
context = coretx.locate(graph, "Why is the login failing?")
print(context.analysis_summary)
```

### Advanced Usage

```python
from coretx import Coretx, LLMConfig, AnalysisConfig

# Custom configuration
llm_config = LLMConfig(
    provider="openai",
    model="gpt-4",
    temperature=0.0
)

analysis_config = AnalysisConfig(
    include_patterns=["*.py", "*.js"],
    exclude_patterns=["test_*", "*_test.py"],
    enable_semantic_analysis=True
)

# Initialize with custom config
coretx = Coretx(
    llm_config=llm_config,
    analysis_config=analysis_config
)

# Analyze and query
graph = coretx.analyze("./complex-project")
result = coretx.query(graph, "Find all security vulnerabilities")

# Trace critical dependencies
trace = coretx.trace(graph, "AuthenticationService")
print(f"Critical dependencies: {len(trace.dependencies)}")
```

## Error Handling

```python
from coretx import Coretx, CoretxError

try:
    coretx = Coretx()
    graph = coretx.analyze("/invalid/path")
except CoretxError as e:
    print(f"Analysis failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Tips

1. **Use caching**: Enable embedding caching for repeated analysis
2. **Filter files**: Use include/exclude patterns to focus on relevant code
3. **Limit depth**: Set max_depth for large codebases
4. **Batch queries**: Process multiple queries on the same graph
5. **Async operations**: Use async methods for concurrent processing