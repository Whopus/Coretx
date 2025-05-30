# CoreCtx Documentation

This directory contains comprehensive documentation for the CoreCtx project.

## 📚 Documentation Files

### Core Documentation
- **[index.html](index.html)** - Interactive web documentation and API reference
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview and architecture
- **[FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)** - Detailed feature descriptions and capabilities

### Configuration & Setup
- **[OPENAI_CONFIG.md](OPENAI_CONFIG.md)** - OpenAI API configuration guide
- **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - GitHub repository setup instructions

### Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines and development workflow

## 🌐 Web Documentation

To view the interactive documentation:

```bash
# Start the documentation server
cd docs
python -m http.server 8000

# Or use the provided server script
python -c "import http.server; import socketserver; socketserver.TCPServer(('', 8000), http.server.SimpleHTTPRequestHandler).serve_forever()"
```

Then open: http://localhost:8000

## 📖 Quick Start

For immediate usage, see the main [README.md](../README.md) in the project root.

For detailed examples, check the [examples/](../examples/) directory.