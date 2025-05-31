# Coretx

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Coretx is an advanced multi-language code analysis engine that combines static analysis, dynamic graph construction, and LLM-powered reasoning to precisely identify relevant code sections for bug fixes, feature implementations, and code understanding tasks across diverse technology stacks.

## 📖 About the Name

**Coretx** is derived from the abbreviation of "**core context**". The name reflects the tool's primary mission: to quickly construct a comprehensive graph structure and relationship map of code repositories, enabling fast content retrieval and the construction of the minimal logical closure necessary for Large Language Models (LLMs) to understand the context and provide the most appropriate responses.

The "core" represents the essential, fundamental elements of a codebase, while "context" (abbreviated as "tx") emphasizes the relational understanding between different code components. Together, Coretx creates the contextual foundation that bridges human intent with machine understanding in code analysis tasks.

## 🚀 Key Features

### 🌐 Multi-Language Support
- **Programming Languages**: Python, JavaScript/TypeScript, Java, C/C++
- **Web Technologies**: HTML, CSS
- **Documentation**: Markdown
- **Configuration**: JSON, YAML, XML
- **Universal Extension System**: Easy to add support for new languages

### 🔍 Advanced Analysis Capabilities
- **AST-Based Parsing**: Deep structural analysis of code entities
- **Cross-Language Relationships**: Discovers connections between different file types
- **Dependency Graph Construction**: Maps imports, includes, and references
- **Semantic Entity Extraction**: Classes, functions, methods, variables, and more

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
| **Web Frontend** | HTML, CSS, SCSS, SASS, Less | `.html`, `.css` |
| **Documentation** | Markdown, reStructuredText | `.md`|
| **Configuration** | JSON, YAML, XML | `.json`, `.yaml`, `.yml`, `.xml` |


## 🚀 Quick Start

### Multi-Language Project Analysis

```python
from coretx import Coretx

# Initialize the multi-language system
Coretx.init(parser="auto")

# Analyze a directory with multiple languages
result = Coretx.ctx_dir(
    directory="/path/to/your/project",
    recursive=True,
    show_stats=True
)

print(f"Found {result['total_entities']} entities across {result['files_processed']} files")
print(f"Found {result['total_relationships']} entities across {result['files_processed']} files")
print(f"Languages detected: {list(result['language_stats'].keys())}")
```

### Parse Individual Files

```python
# Parse a Python file
python_result = Coretx.ctx_file(
    file_path="app.py",
    show_content=True
)

# Parse a JavaScript file
js_result = Coretx.ctx_file(
    file_path="script.js",
    show_content=True
)

# Parse an HTML file
html_result = Coretx.ctx_file(
    file_path="index.html",
    show_content=True
)
```

### Discover Cross-Language Relationships

```python
# Find relationships between different file types
relationships = Coretx.ctx_cross(
    directory="/path/to/your/project",
    show_details=True
)

print(f"Discovered {relationships['total_relationships']} relationships")
print("Relationship types:", relationships['relationship_types'])
```

### Code Localization

```python
from coretx import Coretx

# Initialize the multi-language system
Coretx.init(parser="auto")

# Initialize the code directory
result = Coretx.ctx_dir(
    directory="/path/to/your/project",
    recursive=True,
    show_stats=True
)

# Basic usage
result = Coretx.localize(
    path="/path/to/your/project",
    problem_description="Memory leak in user authentication"
)

# With custom OpenAI configuration
Coretx.init(
    parser="auto",
    openai_api_key="your-api-key",
    openai_base_url="base_url"
)
# or 
result = Coretx.localize(
    path="/path/to/your/project",
    problem_description="Bug in payment processing",
    openai_api_key="your-api-key",
    openai_base_url="base_url"
)
```

### Localization Result

#### 1. Problem Statement
Begin with a clear description of what users're trying to accomplish, what's not working, or what needs to be modified:
- "I need to add authentication to this API endpoint"
- "This function is throwing an error when processing large files"
- "I want to refactor this component to use hooks instead of classes"

#### 2. Minimal Logical Closure

##### Core Files First
Include the primary file(s) where the work needs to be done, showing:
```typescript
// src/api/users.controller.ts
export class UsersController {
  async getUser(id: string) {
    // Current implementation
  }
  
  // TODO: Add authentication here
  async updateUser(id: string, data: UserDto) {
    // ...
  }
}
```

##### Dependencies and Interfaces
Include just the relevant parts of imported files:
```typescript
// src/types/user.types.ts (relevant excerpt)
export interface User {
  id: string;
  email: string;
  role: UserRole;
}

export interface UserDto {
  email?: string;
  name?: string;
}
```

#### Project Structure Overview
A brief tree view helps llm understand the architecture:
```
src/
├── api/
│   ├── users.controller.ts    ← main file
│   └── auth.middleware.ts      ← related
├── services/
│   └── users.service.ts        ← dependency
├── types/
│   └── user.types.ts          ← interfaces
└── utils/
    └── validation.ts          ← if relevant
```

#### 3. Ideal Format and Organization

### Clear File Markers
```python
# === file: src/models/user.py ===
class User(BaseModel):
    id: int
    email: str
    
# === file: src/api/routes.py ===
@router.post("/users")
async def create_user(user: UserCreate):
    # implementation
```

### Include Relevant Configuration
If the issue involves configuration, show relevant excerpts:
```json
// package.json (relevant parts only)
{
  "dependencies": {
    "express": "^4.18.0",
    "typeorm": "^0.3.0"
  }
}
```



### Command Line Interface

```bash
# Init
coretx init --parser "auto" \
  --openai-api-key "your-key" \
  --openai-base-url "base_url"

# Analysis
coretx ctx_dir /path/to/repo

# Basic localization
coretx localize /path/to/repo "Bug in authentication system"

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
  model_name: "gpt-4.1"
  api_key: "your-api-key-here"
  api_base: "base_url"
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

## 🧪 Explain
Coretx will create a `.locator` folder in the directory that needs to be analyzed, which records the graph structure of the entire codebase as well as other analyzable information. coretx uses large language models to analyze the relationships between different nodes (such as classes and methods), and describes the logic layer and code layer in natural language. It then uses a text embedding model to convert these descriptions into embeddings, which are stored as relationships in the graph structure. When a query is made, the query is converted into an embedding, and then a minimal logical closure algorithm is used to index and construct an optimal contextual subgraph. All key information and content are extracted and output in an LLM-friendly format, making it easy to generate documentation or complete tasks.


## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.


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
