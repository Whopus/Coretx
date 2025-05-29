"""Generate HTML documentation for LocAgent Kernel."""

import os
import sys
from pathlib import Path
import inspect
import importlib
from typing import Dict, List, Any
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import locagent_kernel
    from locagent_kernel.core.graph import GraphBuilder, GraphSearcher, NodeType, EdgeType
    from locagent_kernel.core.retrieval import BM25Retriever, HybridRetriever
    from locagent_kernel.core.agent import LocalizationAgent, ToolRegistry
    from locagent_kernel.core.locator import CodeLocator
    from locagent_kernel.config import LocAgentConfig
except ImportError:
    # Create mock classes for documentation generation
    class MockClass:
        def __init__(self, name):
            self.__name__ = name
            self.__doc__ = f"Mock {name} class for documentation generation."
    
    GraphBuilder = MockClass("GraphBuilder")
    GraphSearcher = MockClass("GraphSearcher") 
    BM25Retriever = MockClass("BM25Retriever")
    HybridRetriever = MockClass("HybridRetriever")
    LocalizationAgent = MockClass("LocalizationAgent")
    ToolRegistry = MockClass("ToolRegistry")
    CodeLocator = MockClass("CodeLocator")
    LocAgentConfig = MockClass("LocAgentConfig")


def generate_html_template() -> str:
    """Generate base HTML template."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocAgent Kernel Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .header p {
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .nav {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        .nav a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        
        .nav a:hover {
            background-color: #f0f2ff;
        }
        
        .section {
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: #667eea;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        .section h3 {
            color: #495057;
            margin-top: 25px;
        }
        
        .code-block {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
        }
        
        .method {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }
        
        .method-name {
            font-weight: bold;
            color: #667eea;
            font-family: monospace;
        }
        
        .method-signature {
            color: #6c757d;
            font-family: monospace;
            font-size: 14px;
            margin: 5px 0;
        }
        
        .architecture-diagram {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }
        
        .component-box {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 5px;
            font-weight: 500;
        }
        
        .arrow {
            font-size: 20px;
            color: #6c757d;
            margin: 0 10px;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .feature-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .feature-card h4 {
            margin-top: 0;
            color: #667eea;
        }
        
        .toc {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .toc ul {
            list-style: none;
            padding-left: 20px;
        }
        
        .toc > ul {
            padding-left: 0;
        }
        
        .toc a {
            color: #667eea;
            text-decoration: none;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .nav ul {
                flex-direction: column;
            }
            
            .feature-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>LocAgent Kernel</h1>
        <p>A Modular Code Localization Engine</p>
    </div>
    
    <nav class="nav">
        <ul>
            <li><a href="#overview">Overview</a></li>
            <li><a href="#architecture">Architecture</a></li>
            <li><a href="#quick-start">Quick Start</a></li>
            <li><a href="#api-reference">API Reference</a></li>
            <li><a href="#examples">Examples</a></li>
            <li><a href="#configuration">Configuration</a></li>
        </ul>
    </nav>
    
    {content}
    
    <footer style="text-align: center; margin-top: 50px; padding: 20px; color: #6c757d;">
        <p>LocAgent Kernel Documentation - Generated automatically</p>
    </footer>
</body>
</html>
"""


def extract_class_info(cls) -> Dict[str, Any]:
    """Extract information from a class."""
    info = {
        'name': cls.__name__,
        'doc': inspect.getdoc(cls) or "No documentation available.",
        'methods': []
    }
    
    try:
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            if not name.startswith('_'):
                method_info = {
                    'name': name,
                    'signature': str(inspect.signature(method)),
                    'doc': inspect.getdoc(method) or "No documentation available."
                }
                info['methods'].append(method_info)
        
        for name, func in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                func_info = {
                    'name': name,
                    'signature': str(inspect.signature(func)),
                    'doc': inspect.getdoc(func) or "No documentation available."
                }
                info['methods'].append(func_info)
    except Exception:
        # For mock classes, add some example methods
        info['methods'] = [
            {
                'name': 'initialize',
                'signature': '(self, *args, **kwargs)',
                'doc': 'Initialize the component.'
            },
            {
                'name': 'process',
                'signature': '(self, data)',
                'doc': 'Process the input data.'
            }
        ]
    
    return info


def generate_overview_section() -> str:
    """Generate overview section."""
    return """
    <section id="overview" class="section">
        <h2>Overview</h2>
        
        <p>LocAgent Kernel is a modular, engineered implementation of code localization technology that combines graph-based code analysis with LLM agents for intelligent code understanding and bug localization.</p>
        
        <div class="feature-grid">
            <div class="feature-card">
                <h4>🔍 Graph-Based Analysis</h4>
                <p>Constructs comprehensive dependency graphs from source code, capturing relationships between files, classes, and functions.</p>
            </div>
            
            <div class="feature-card">
                <h4>🔎 Hybrid Retrieval</h4>
                <p>Combines BM25 text search with graph-based structural search for comprehensive code retrieval.</p>
            </div>
            
            <div class="feature-card">
                <h4>🤖 LLM Agents</h4>
                <p>Uses language models with specialized tools for intelligent code understanding and localization.</p>
            </div>
            
            <div class="feature-card">
                <h4>🧩 Modular Design</h4>
                <p>Clean separation of concerns with composable components that can be used independently.</p>
            </div>
        </div>
        
        <h3>Key Features</h3>
        <ul>
            <li><strong>Multi-language Support:</strong> Python, JavaScript, TypeScript, Java, C/C++</li>
            <li><strong>Flexible Configuration:</strong> YAML/JSON configuration with hierarchical settings</li>
            <li><strong>Caching System:</strong> Automatic caching of graphs and indices for performance</li>
            <li><strong>Tool System:</strong> Extensible tool registry for agent capabilities</li>
            <li><strong>CLI Interface:</strong> Command-line interface for easy integration</li>
        </ul>
    </section>
    """


def generate_architecture_section() -> str:
    """Generate architecture section."""
    return """
    <section id="architecture" class="section">
        <h2>Architecture</h2>
        
        <div class="architecture-diagram">
            <div style="margin-bottom: 20px;">
                <div class="component-box">Code Repository</div>
                <div class="arrow">↓</div>
                <div class="component-box">Graph Builder</div>
                <div class="arrow">→</div>
                <div class="component-box">Dependency Graph</div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <div class="component-box">BM25 Retriever</div>
                <div class="arrow">+</div>
                <div class="component-box">Graph Searcher</div>
                <div class="arrow">→</div>
                <div class="component-box">Hybrid Retriever</div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <div class="component-box">LLM Agent</div>
                <div class="arrow">+</div>
                <div class="component-box">Specialized Tools</div>
                <div class="arrow">→</div>
                <div class="component-box">Code Locator</div>
            </div>
        </div>
        
        <h3>Core Components</h3>
        
        <div class="method">
            <div class="method-name">GraphBuilder</div>
            <p>Constructs code dependency graphs by parsing source files and extracting entities (files, classes, functions) and their relationships (contains, inherits, invokes, imports).</p>
        </div>
        
        <div class="method">
            <div class="method-name">HybridRetriever</div>
            <p>Combines BM25 text-based search with graph-based structural search to provide comprehensive code retrieval capabilities.</p>
        </div>
        
        <div class="method">
            <div class="method-name">LocalizationAgent</div>
            <p>LLM agent with specialized tools for code analysis, capable of understanding problem descriptions and locating relevant code entities.</p>
        </div>
        
        <div class="method">
            <div class="method-name">CodeLocator</div>
            <p>Main orchestration interface that combines all components to provide a clean API for code localization tasks.</p>
        </div>
        
        <h3>Data Flow</h3>
        <ol>
            <li><strong>Graph Construction:</strong> Parse repository and build dependency graph</li>
            <li><strong>Index Building:</strong> Create BM25 text index and graph search indices</li>
            <li><strong>Problem Analysis:</strong> LLM agent analyzes problem description</li>
            <li><strong>Code Search:</strong> Use hybrid retrieval to find relevant entities</li>
            <li><strong>Result Synthesis:</strong> Agent synthesizes findings into localization results</li>
        </ol>
    </section>
    """


def generate_quick_start_section() -> str:
    """Generate quick start section."""
    return """
    <section id="quick-start" class="section">
        <h2>Quick Start</h2>
        
        <h3>Installation</h3>
        <div class="code-block">
# Clone the repository
git clone &lt;repository-url&gt;
cd locagent_kernel

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
        </div>
        
        <h3>Basic Usage</h3>
        <div class="code-block">
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
        </div>
        
        <h3>Advanced Usage</h3>
        <div class="code-block">
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
    repository_context="Large Python web application"
)

# Search the codebase
search_results = locator.search("authentication", search_type="hybrid")
        </div>
        
        <h3>Command Line Interface</h3>
        <div class="code-block">
# Quick localization
locagent localize /path/to/repo "Bug description"

# Search codebase
locagent search /path/to/repo "authentication" --type hybrid

# Initialize repository
locagent init /path/to/repo --config config.yaml

# Get statistics
locagent stats /path/to/repo
        </div>
    </section>
    """


def generate_api_reference_section() -> str:
    """Generate API reference section."""
    
    # Extract class information
    classes_info = {
        'CodeLocator': extract_class_info(CodeLocator),
        'GraphBuilder': extract_class_info(GraphBuilder),
        'HybridRetriever': extract_class_info(HybridRetriever),
        'LocalizationAgent': extract_class_info(LocalizationAgent),
        'LocAgentConfig': extract_class_info(LocAgentConfig)
    }
    
    content = """
    <section id="api-reference" class="section">
        <h2>API Reference</h2>
        
        <div class="toc">
            <h3>Classes</h3>
            <ul>
    """
    
    for class_name in classes_info:
        content += f'                <li><a href="#{class_name.lower()}">{class_name}</a></li>\n'
    
    content += """
            </ul>
        </div>
    """
    
    # Generate documentation for each class
    for class_name, class_info in classes_info.items():
        content += f"""
        <h3 id="{class_name.lower()}">{class_name}</h3>
        <p>{class_info['doc']}</p>
        
        <h4>Methods</h4>
        """
        
        for method in class_info['methods'][:10]:  # Limit to first 10 methods
            content += f"""
        <div class="method">
            <div class="method-name">{method['name']}</div>
            <div class="method-signature">{method['signature']}</div>
            <p>{method['doc']}</p>
        </div>
            """
    
    content += """
    </section>
    """
    
    return content


def generate_examples_section() -> str:
    """Generate examples section."""
    return """
    <section id="examples" class="section">
        <h2>Examples</h2>
        
        <h3>Basic Localization</h3>
        <div class="code-block">
from locagent_kernel import CodeLocator, LocAgentConfig

# Setup
config = LocAgentConfig()
locator = CodeLocator(config)
locator.initialize("/path/to/repository")

# Localize a bug
results = locator.localize(
    "There's a memory leak in the data processing pipeline"
)

# Print results
for file in results['localization_results']['files']:
    print(f"Relevant file: {file}")
        </div>
        
        <h3>Custom Configuration</h3>
        <div class="code-block">
from locagent_kernel import LocAgentConfig
from locagent_kernel.utils import save_config

# Create custom configuration
config = LocAgentConfig()

# Agent settings
config.agent.model_name = "gpt-3.5-turbo"
config.agent.temperature = 0.2
config.agent.max_tokens = 1500

# Retrieval settings
config.retrieval.top_k = 20
config.retrieval.bm25_k1 = 1.5

# Graph settings
config.graph.file_extensions = ['.py', '.js', '.ts']
config.graph.max_depth = 12

# Save configuration
save_config(config, "my_config.yaml")
        </div>
        
        <h3>Search and Analysis</h3>
        <div class="code-block">
# Different search types
text_results = locator.search("authentication", search_type="text")
graph_results = locator.search("OAuth", search_type="graph")
hybrid_results = locator.search("token validation", search_type="hybrid")

# Analyze specific entities
if hybrid_results:
    entity_id = hybrid_results[0]['node_id']
    entity_info = locator.get_entity_info(entity_id)
    related_entities = locator.find_related_entities(entity_id)
    
    print(f"Entity: {entity_info['attributes']['name']}")
    print(f"Related entities: {len(related_entities)}")
        </div>
        
        <h3>Working with Tools</h3>
        <div class="code-block">
from locagent_kernel.core.agent import ToolRegistry

# Create custom tool
registry = ToolRegistry()

@registry.register("custom_search", "Custom search functionality")
def custom_search(query: str, limit: int = 10) -> list:
    # Custom search implementation
    return []

# Get available tools
tools = registry.list_tools()
for tool in tools:
    print(f"Tool: {tool['name']} - {tool['description']}")
        </div>
    </section>
    """


def generate_configuration_section() -> str:
    """Generate configuration section."""
    return """
    <section id="configuration" class="section">
        <h2>Configuration</h2>
        
        <p>LocAgent Kernel uses a hierarchical configuration system with support for YAML and JSON formats.</p>
        
        <h3>Configuration Structure</h3>
        <div class="code-block">
# config.yaml
agent:
  model_name: "gpt-4"
  temperature: 0.1
  max_tokens: 2048
  api_key: null  # Set via environment variable
  max_iterations: 10
  timeout: 300

retrieval:
  top_k: 10
  bm25_k1: 1.2
  bm25_b: 0.75
  fuzzy_threshold: 0.8
  cache_dir: null

graph:
  node_types: ["directory", "file", "class", "function"]
  edge_types: ["contains", "inherits", "invokes", "imports"]
  file_extensions: [".py", ".js", ".ts", ".java"]
  max_depth: 10
  skip_dirs: [".git", "__pycache__", "node_modules"]

# General settings
work_dir: "."
log_level: "INFO"
log_file: null
num_processes: 1
batch_size: 10
        </div>
        
        <h3>Configuration Classes</h3>
        
        <div class="method">
            <div class="method-name">LocAgentConfig</div>
            <p>Main configuration class that contains all sub-configurations.</p>
        </div>
        
        <div class="method">
            <div class="method-name">AgentConfig</div>
            <p>Configuration for LLM agent behavior, including model selection, temperature, and API settings.</p>
        </div>
        
        <div class="method">
            <div class="method-name">RetrievalConfig</div>
            <p>Configuration for retrieval systems, including BM25 parameters and search settings.</p>
        </div>
        
        <div class="method">
            <div class="method-name">GraphConfig</div>
            <p>Configuration for graph construction, including file types, node types, and parsing settings.</p>
        </div>
        
        <h3>Loading and Saving Configuration</h3>
        <div class="code-block">
from locagent_kernel.utils import load_config, save_config

# Load from file
config = load_config("config.yaml")

# Modify configuration
config.agent.temperature = 0.2

# Save to file
save_config(config, "modified_config.yaml", format="yaml")
        </div>
        
        <h3>Environment Variables</h3>
        <ul>
            <li><code>OPENAI_API_KEY</code> - OpenAI API key for GPT models</li>
            <li><code>ANTHROPIC_API_KEY</code> - Anthropic API key for Claude models</li>
            <li><code>LOCAGENT_LOG_LEVEL</code> - Override log level</li>
            <li><code>LOCAGENT_CACHE_DIR</code> - Override cache directory</li>
        </ul>
    </section>
    """


def generate_documentation():
    """Generate complete HTML documentation."""
    
    # Generate all sections
    overview = generate_overview_section()
    architecture = generate_architecture_section()
    quick_start = generate_quick_start_section()
    api_reference = generate_api_reference_section()
    examples = generate_examples_section()
    configuration = generate_configuration_section()
    
    # Combine all content
    content = overview + architecture + quick_start + api_reference + examples + configuration
    
    # Generate final HTML
    template = generate_html_template()
    html = template.replace('{content}', content)
    
    return html


def main():
    """Main function to generate documentation."""
    print("Generating LocAgent Kernel documentation...")
    
    # Create docs directory
    docs_dir = Path(__file__).parent
    docs_dir.mkdir(exist_ok=True)
    
    # Generate HTML documentation
    html_content = generate_documentation()
    
    # Write to file
    output_path = docs_dir / "index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Documentation generated: {output_path}")
    print(f"Open file://{output_path.absolute()} in your browser to view the documentation.")


if __name__ == "__main__":
    main()