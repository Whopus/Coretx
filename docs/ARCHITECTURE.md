# Coretx Architecture

Coretx is a lightweight kernel for building comprehensive knowledge graphs of your codebase, enabling LLMs to understand and reason about code with minimal context.

## Core Components

### 1. Data Models (`coretx/models.py`)

The foundation of Coretx is built on well-defined data structures:

- **CodeEntity**: Represents any code element (function, class, variable, etc.)
- **Relationship**: Defines connections between entities (calls, inherits, imports, etc.)
- **FileContext**: Captures file-level information and metadata
- **QueryResult**: Structured response to natural language queries
- **ContextResult**: Minimal closure for specific problems
- **TraceResult**: Dependency tracing results

### 2. Parser Engine (`coretx/parsers/`)

Multi-language parsing system using tree-sitter:

- **BaseParser**: Abstract interface for all language parsers
- **ParserRegistry**: Dynamic parser registration and discovery
- **PythonParser**: Python-specific AST analysis
- **JavaScriptParser**: JavaScript/TypeScript parsing
- **TypeScriptParser**: Enhanced TypeScript support

### 3. Knowledge Graph (`coretx/graph.py`)

NetworkX-based graph implementation:

- Entity and relationship management
- Graph traversal and analysis
- Statistical insights
- Efficient querying capabilities

### 4. LLM Integration (`coretx/llm/`)

Comprehensive AI-powered analysis:

- **LLMClient**: OpenAI API integration
- **EmbeddingsEngine**: Vector embeddings for semantic similarity
- **SemanticAnalyzer**: Code understanding and classification
- **QueryProcessor**: Natural language to code mapping

### 5. Core Engine (`coretx/core.py`)

Main orchestration layer:

- **Coretx**: Primary API class
- Project analysis coordination
- Query processing pipeline
- Context extraction
- Dependency tracing

### 6. Utilities (`coretx/utils/`)

Supporting infrastructure:

- **FileScanner**: Intelligent file discovery
- **CodeAnalyzer**: Static analysis utilities
- **Configuration**: Settings management

## Data Flow

```
Source Code → Parser → Entities/Relationships → Knowledge Graph → LLM Analysis → Results
```

1. **Scanning**: Discover relevant files in the codebase
2. **Parsing**: Extract entities and relationships using tree-sitter
3. **Graph Building**: Construct knowledge graph with NetworkX
4. **Semantic Analysis**: Enhance with LLM-powered insights
5. **Query Processing**: Answer questions about the codebase

## Key Features

### Intelligent Code Understanding

- Multi-language support (Python, JavaScript, TypeScript)
- Semantic relationship detection
- Context-aware analysis
- Dependency tracking

### Natural Language Interface

- Query code using plain English
- Get relevant context for specific problems
- Trace dependencies and relationships
- Generate fix suggestions

### Minimal Context Extraction

- Find minimal code closure for problems
- Identify entry points and critical paths
- Generate flow diagrams
- Provide actionable insights

## Extension Points

### Adding New Languages

1. Implement `BaseParser` interface
2. Register with `ParserRegistry`
3. Define language-specific patterns
4. Add tree-sitter grammar support

### Custom Analysis

1. Extend `SemanticAnalyzer`
2. Add domain-specific entity types
3. Define custom relationship types
4. Implement specialized queries

### LLM Providers

1. Implement `LLMClient` interface
2. Add provider-specific configuration
3. Handle authentication and rate limiting
4. Maintain consistent response format

## Performance Considerations

- Lazy loading of parsers and models
- Efficient graph traversal algorithms
- Caching of embeddings and analysis results
- Streaming for large codebases
- Parallel processing where applicable

## Configuration

Coretx supports flexible configuration through:

- Environment variables
- Configuration files (YAML/JSON)
- Runtime parameters
- Provider-specific settings

## Testing Strategy

Comprehensive test suite covering:

- Unit tests for all components
- Integration tests for workflows
- Parser accuracy validation
- LLM integration testing
- Performance benchmarks