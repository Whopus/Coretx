# LocAgent Kernel

A modular, engineered kernel for code localization using graph-guided LLM agents.

## Overview

LocAgent Kernel is a clean, minimal implementation of code localization technology that combines:

- **Graph-based Code Analysis**: Constructs dependency graphs from source code
- **Hybrid Retrieval**: Combines BM25 text search with graph-based structural search  
- **LLM Agents**: Uses language models with specialized tools for code understanding
- **Modular Architecture**: Clean separation of concerns with composable components

## Architecture

```
LocAgent Kernel
├── Core Components
│   ├── Graph Builder     # Constructs code dependency graphs
│   ├── Graph Searcher    # Queries and navigates graphs
│   ├── BM25 Retriever    # Text-based code search
│   ├── Hybrid Retriever  # Combines text + graph search
│   ├── LLM Agent         # Language model with tools
│   └── Code Locator      # Main orchestration interface
├── Configuration        # Flexible configuration system
├── Tools               # Specialized agent tools for code analysis
└── Utilities           # File I/O, logging, config management
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd locagent_kernel

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

```python
from locagent_kernel import quick_localize

# Simple localization
results = quick_localize(
    repo_path="/path/to/your/repository",
    problem_description="Bug in user authentication with OAuth tokens",
    model_name="gpt-4"
)

print("Located files:", results['localization_results']['files'])
print("Located classes:", results['localization_results']['classes'])
print("Located functions:", results['localization_results']['functions'])
```

### Advanced Usage

```python
from locagent_kernel import CodeLocator, LocAgentConfig

# Create custom configuration
config = LocAgentConfig()
config.agent.model_name = "gpt-4"
config.agent.temperature = 0.1
config.retrieval.top_k = 15

# Initialize locator
locator = CodeLocator(config)
locator.initialize("/path/to/repository")

# Perform localization
results = locator.localize(
    problem_description="Memory leak in data processing pipeline",
    repository_context="Large Python web application with async processing"
)

# Search the codebase
search_results = locator.search("authentication", search_type="hybrid")

# Analyze specific entities
entity_info = locator.get_entity_info(search_results[0]['node_id'])
related_entities = locator.find_related_entities(entity_info['id'])
```

## Core Components

### CodeLocator

The main interface for code localization. Orchestrates all components and provides a clean API.

```python
from locagent_kernel import CodeLocator, LocAgentConfig

config = LocAgentConfig()
locator = CodeLocator(config)
locator.initialize("/path/to/repo")

# Localize code for a problem
results = locator.localize("Bug description here")

# Search the codebase  
search_results = locator.search("query", search_type="hybrid")

# Get repository statistics
stats = locator.get_graph_stats()
```

### Graph Builder

Constructs code dependency graphs by parsing source files and extracting entities and relationships.

```python
from locagent_kernel import GraphBuilder, GraphConfig

config = GraphConfig()
builder = GraphBuilder(config)
graph = builder.build_graph("/path/to/repo")

# Get statistics
stats = builder.get_stats()
print(f"Built graph with {stats.total_nodes} nodes and {stats.total_edges} edges")
```

### Hybrid Retriever

Combines BM25 text search with graph-based structural search for comprehensive code retrieval.

```python
from locagent_kernel import HybridRetriever, RetrievalConfig

config = RetrievalConfig()
retriever = HybridRetriever(config)
retriever.build_index(graph, repo_path)

# Different search types
text_results = retriever.search("authentication", search_type="text")
graph_results = retriever.search("OAuth", search_type="graph") 
hybrid_results = retriever.search("token validation", search_type="hybrid")
```

### LLM Agent

Specialized agent with tools for code analysis and localization.

```python
from locagent_kernel import LocalizationAgent, AgentConfig

config = AgentConfig()
config.model_name = "gpt-4"
agent = LocalizationAgent(config)

# Add tools (done automatically by CodeLocator)
# agent.add_tool("search_code", search_function)

# Perform localization
results = agent.localize_code(
    problem_description="Bug description",
    repository_context="Additional context"
)
```

## Configuration

LocAgent Kernel uses a hierarchical configuration system:

```python
from locagent_kernel import LocAgentConfig

# Create default configuration
config = LocAgentConfig()

# Customize agent settings
config.agent.model_name = "gpt-4"
config.agent.temperature = 0.1
config.agent.max_tokens = 2048

# Customize retrieval settings
config.retrieval.top_k = 20
config.retrieval.bm25_k1 = 1.5

# Customize graph settings
config.graph.file_extensions = ['.py', '.js', '.ts']
config.graph.max_depth = 12

# Save/load configuration
from locagent_kernel.utils import save_config, load_config
save_config(config, "my_config.yaml")
loaded_config = load_config("my_config.yaml")
```

### Configuration File Example

```yaml
# config.yaml
agent:
  model_name: "gpt-4"
  temperature: 0.1
  max_tokens: 2048

retrieval:
  top_k: 15
  bm25_k1: 1.2
  bm25_b: 0.75

graph:
  file_extensions: [".py", ".js", ".ts"]
  max_depth: 10
  skip_dirs: [".git", "__pycache__", "node_modules"]
```

## Agent Tools

The LLM agent has access to specialized tools for code analysis:

- **search_code**: Search for code entities using text or structural queries
- **get_entity_details**: Get detailed information about specific code entities
- **search_by_type**: Search for entities of specific types (files, classes, functions)
- **get_file_content**: Retrieve source file content with line numbers
- **get_function_definition**: Get function definitions with metadata
- **get_class_definition**: Get class definitions with methods
- **find_related_entities**: Find entities related through dependencies
- **list_files**: List files in the repository
- **analyze_dependencies**: Analyze dependency relationships

## Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py`: Basic localization and search examples
- `config_example.yaml`: Example configuration file
- `advanced_usage.py`: Advanced features and customization

## API Reference

### CodeLocator

Main interface for code localization.

#### Methods

- `initialize(repo_path, force_rebuild=False)`: Initialize with a repository
- `localize(problem_description, repository_context="")`: Perform code localization
- `search(query, search_type="hybrid", top_k=10)`: Search the codebase
- `get_entity_info(entity_id)`: Get detailed entity information
- `get_file_entities(file_path)`: Get entities in a specific file
- `find_related_entities(entity_id, relation_type="all")`: Find related entities
- `get_graph_stats()`: Get graph statistics
- `export_graph(output_path, format="gexf")`: Export graph to file
- `clear_cache()`: Clear cached indices

### Configuration Classes

- `LocAgentConfig`: Main configuration
- `GraphConfig`: Graph construction settings
- `RetrievalConfig`: Retrieval system settings  
- `AgentConfig`: LLM agent settings

### Core Components

- `GraphBuilder`: Constructs dependency graphs
- `GraphSearcher`: Queries and navigates graphs
- `BM25Retriever`: Text-based search
- `HybridRetriever`: Combined text + graph search
- `LocalizationAgent`: LLM agent with tools
- `ToolRegistry`: Manages agent tools

## Performance

LocAgent Kernel is designed for efficiency:

- **Caching**: Automatically caches built graphs and indices
- **Incremental Updates**: Supports incremental graph updates
- **Parallel Processing**: Configurable parallel processing for large repositories
- **Memory Efficient**: Streaming processing for large codebases

## Supported Languages

Currently supports:
- Python (full support)
- JavaScript/TypeScript (basic support)
- Java (basic support)
- C/C++ (basic support)

Additional language support can be added by extending the graph builder.

## Requirements

- Python 3.8+
- NetworkX (graph processing)
- OpenAI API key (for LLM agent)
- Optional: Anthropic API key (for Claude models)

## Dependencies

```
networkx>=2.8
openai>=1.0.0
anthropic>=0.3.0  # optional
litellm>=1.0.0    # optional
pyyaml>=6.0
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Citation

If you use LocAgent Kernel in your research, please cite:

```bibtex
@software{locagent_kernel,
  title={LocAgent Kernel: A Modular Code Localization Engine},
  author={LocAgent Team},
  year={2024},
  url={https://github.com/your-org/locagent-kernel}
}
```