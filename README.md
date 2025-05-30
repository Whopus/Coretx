# Coretx

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Coretx is an advanced code localization engine that combines static analysis, dynamic graph construction, and LLM-powered reasoning to precisely identify relevant code sections for bug fixes, feature implementations, and code understanding tasks.

## 📖 About the Name

**coretx** is derived from the abbreviation of "**core context**". Its main function is to quickly construct a graph structure and relationship map of code folders, enabling fast content retrieval and the construction of the minimal logical closure for LLMs to understand the context and provide the most appropriate response.

## 📖 About the Name

**coretx** is derived from the abbreviation of "**core context**". Its main function is to quickly construct a graph structure and relationship map of code folders, enabling fast content retrieval and the construction of the minimal logical closure for LLMs to understand the context and provide the most appropriate response.

## 🚀 Features

- **Multi-Modal Code Analysis**: Combines AST parsing, dependency graphs, and semantic search
- **LLM Integration**: Supports OpenAI, Anthropic, and custom endpoints with flexible configuration
- **Language Support**: Python, JavaScript, TypeScript, Java, C/C++, and more
- **CLI Interface**: Easy-to-use command-line tools
- **Extensible Architecture**: Plugin-based design for custom analyzers
- **Flexible Configuration**: Multiple ways to configure API settings and behavior

## 🔧 Installation

### From PyPI (coming soon)
```bash
pip install coretx
```

### From Source
```bash
git clone https://github.com/Whopus/Coretx.git
cd Coretx
pip install -e .
```

## 🚀 Quick Start

### Python API

```python
from coretx import quick_localize

# Basic usage
results = quick_localize(
    repo_path="/path/to/your/repo",
    problem_description="Memory leak in user authentication"
)

# With custom OpenAI configuration
results = quick_localize(
    repo_path="/path/to/your/repo",
    problem_description="Bug in payment processing",
    openai_api_key="your-api-key",
    openai_base_url="https://api.openai.com/v1"
)

print("Relevant files:")
for file_path, relevance in results.items():
    print(f"  {file_path}: {relevance:.2f}")
```

### Command Line Interface

```bash
# Basic localization
coretx localize /path/to/repo "Bug in authentication system"

# With custom OpenAI configuration
coretx localize /path/to/repo "Memory leak" \
  --openai-api-key "your-key" \
  --openai-base-url "https://api.openai.com/v1"

# Using configuration file
coretx localize /path/to/repo "Bug description" --config config.yaml
```

## 📖 Documentation

### OpenAI Configuration

Coretx supports multiple ways to configure OpenAI API settings:

1. **Function Parameters** (highest priority)
2. **Configuration Files**
3. **Environment Variables** (lowest priority)

See [OPENAI_CONFIG.md](docs/OPENAI_CONFIG.md) for detailed configuration options.

### Architecture

```
Coretx
├── Core Components
│   ├── Graph Builder     # Constructs code dependency graphs
│   ├── Graph Searcher    # Queries and navigates graphs
│   ├── Hybrid Retriever  # Combines text and graph search
│   └── LLM Agent         # Reasoning and code understanding
├── Language Support
│   ├── Python Parser     # AST and dependency extraction
│   ├── JavaScript Parser # ES6+ and TypeScript support
│   ├── Java Parser       # Class and package analysis
│   └── C/C++ Parser      # Header and source analysis
└── Configuration
    ├── YAML Config       # Flexible configuration system
    ├── CLI Interface     # Command-line tools
    └── API Integration   # OpenAI, Anthropic, custom endpoints
```

## 🔧 Configuration

### Configuration File Example

```yaml
# config.yaml
agent:
  model_name: "gpt-4"
  api_key: "your-api-key-here"
  api_base: "https://api.openai.com/v1"
  temperature: 0.1

search:
  max_results: 50
  similarity_threshold: 0.7

graph:
  max_depth: 3
  include_tests: false
```

### Environment Variables

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

## 🧪 Examples

### Advanced Usage

```python
from coretx import create_locator, LocAgentConfig

# Create custom configuration
config = LocAgentConfig()
config.agent.model_name = "gpt-4"
config.agent.api_key = "your-key"
config.search.max_results = 100

# Create locator with custom config
locator = create_locator("/path/to/repo", config=config)

# Perform multiple localizations
bug_results = locator.localize("Authentication bug")
feature_results = locator.localize("Add payment integration")

# Get repository statistics
stats = locator.get_stats()
print(f"Files analyzed: {stats['total_files']}")
print(f"Dependencies found: {stats['total_dependencies']}")
```

### Custom Endpoints

```python
# Azure OpenAI
results = quick_localize(
    repo_path="/path/to/repo",
    problem_description="Bug description",
    openai_api_key="your-azure-key",
    openai_base_url="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
)

# Other OpenAI-compatible APIs
results = quick_localize(
    repo_path="/path/to/repo",
    problem_description="Bug description",
    openai_api_key="your-api-key",
    openai_base_url="https://your-custom-endpoint.com/v1"
)
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python tests/test_config.py
python tests/test_setup.py

# Run with coverage (if pytest-cov is installed)
pytest --cov=coretx tests/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Whopus/locagent-kernel.git
cd locagent-kernel

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Tree-sitter](https://tree-sitter.github.io/) for robust code parsing
- Powered by [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/) language models
- Uses [NetworkX](https://networkx.org/) for graph analysis
- Semantic search powered by [Sentence Transformers](https://www.sbert.net/)

## 📞 Support

- 📖 [Documentation](https://github.com/Whopus/locagent-kernel#readme)
- 🐛 [Issue Tracker](https://github.com/Whopus/locagent-kernel/issues)
- 💬 [Discussions](https://github.com/Whopus/locagent-kernel/discussions)

---