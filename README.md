# Coretx

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Coretx is an advanced multi-language code analysis engine that combines static analysis, dynamic graph construction, and LLM-powered reasoning to precisely identify relevant code sections for bug fixes, feature implementations, and code understanding tasks across diverse technology stacks.

## 📖 About the Name

**Coretx** is derived from the abbreviation of "**core context**". The name reflects the tool's primary mission: to quickly construct a comprehensive graph structure and relationship map of code repositories, enabling fast content retrieval and the construction of the minimal logical closure necessary for Large Language Models (LLMs) to understand the context and provide the most appropriate responses.

The "core" represents the essential, fundamental elements of a codebase, while "context" (abbreviated as "tx") emphasizes the relational understanding between different code components. Together, Coretx creates the contextual foundation that bridges human intent with machine understanding in code analysis tasks.

## 🚀 Key Features

### 🌐 Multi-Language Support
- **Programming Languages**: Python, JavaScript/TypeScript, Java, C/C++
- **Web Technologies**: HTML, CSS, SCSS/SASS, Less
- **Documentation**: Markdown, reStructuredText
- **Configuration**: JSON, YAML, XML
- **Universal Extension System**: Easy to add support for new languages

### 🔍 Advanced Analysis Capabilities
- **AST-Based Parsing**: Deep structural analysis of code entities
- **Cross-Language Relationships**: Discovers connections between different file types
- **Dependency Graph Construction**: Maps imports, includes, and references
- **Semantic Entity Extraction**: Classes, functions, methods, variables, and more
- **Web Asset Relationships**: CSS-HTML styling, JavaScript-HTML scripting connections

### 🎨 Rich Display & Visualization
- **Beautiful Console Output**: Rich formatting with colors, tables, and progress bars
- **Interactive Results**: Detailed entity information with syntax highlighting
- **Graph Statistics**: Comprehensive metrics and language breakdowns
- **Export Capabilities**: HTML, JSON, and text format outputs

### 🔧 Extensible Architecture
- **Plugin-Based Design**: Modular language parsers and analyzers
- **Custom Entity Types**: Support for domain-specific code patterns
- **Flexible Configuration**: Adaptable to different project structures
- **LLM Integration**: OpenAI, Anthropic, and custom endpoint support

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

## 🌐 Multi-Language Analysis

Coretx provides comprehensive support for analyzing projects with multiple programming languages and technologies. The universal extension system automatically detects file types and applies appropriate parsers.

### Supported Languages & Technologies

| Category | Languages/Technologies | File Extensions |
|----------|----------------------|-----------------|
| **Programming** | Python, JavaScript, TypeScript | `.py`, `.js`, `.ts`, `.jsx`, `.tsx` |
| **Web Frontend** | HTML, CSS, SCSS, SASS, Less | `.html`, `.css`, `.scss`, `.sass`, `.less` |
| **Documentation** | Markdown, reStructuredText | `.md`, `.rst`, `.markdown` |
| **Configuration** | JSON, YAML, XML | `.json`, `.yaml`, `.yml`, `.xml` |

### Entity Types Extracted

- **Code Entities**: Classes, functions, methods, variables, imports, modules
- **Web Entities**: HTML elements, CSS rules, selectors, properties
- **Documentation**: Headings, code blocks, links, text sections
- **Relationships**: Cross-language dependencies, styling connections, script references

## 🚀 Quick Start

### Multi-Language Project Analysis

```python
from coretx.core.extensions.registry import registry
from coretx.core.agent.enhanced_tools import enhanced_tools

# Initialize the multi-language system
registry.initialize_default_parsers()

# Analyze a directory with multiple languages
result = enhanced_tools.tools['analyze_directory'](
    directory_path="/path/to/your/project",
    recursive=True,
    show_stats=True
)

print(f"Found {result['total_entities']} entities across {result['files_processed']} files")
print(f"Languages detected: {list(result['language_stats'].keys())}")
```

### Parse Individual Files

```python
# Parse a Python file
python_result = enhanced_tools.tools['parse_file'](
    file_path="app.py",
    show_content=True
)

# Parse a JavaScript file
js_result = enhanced_tools.tools['parse_file'](
    file_path="script.js",
    show_content=True
)

# Parse an HTML file
html_result = enhanced_tools.tools['parse_file'](
    file_path="index.html",
    show_content=True
)
```

### Discover Cross-Language Relationships

```python
# Find relationships between different file types
relationships = enhanced_tools.tools['discover_relationships'](
    directory_path="/path/to/your/project",
    show_details=True
)

print(f"Discovered {relationships['total_relationships']} relationships")
print("Relationship types:", relationships['relationship_types'])
```

### Traditional Code Localization

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
git clone https://github.com/Whopus/Coretx.git
cd Coretx

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

- 📖 [Documentation](https://github.com/Whopus/Coretx#readme)
- 🐛 [Issue Tracker](https://github.com/Whopus/Coretx/issues)
- 💬 [Discussions](https://github.com/Whopus/Coretx/discussions)

---