# Contributing to CoreCtx

Thank you for your interest in contributing to CoreCtx! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of code analysis and language models

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/CoreCtx.git
   cd CoreCtx
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Verify Setup**
   ```bash
   pytest
   ```

## 🔧 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- Write clean, well-documented code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=coretx

# Run specific test categories
pytest -m "not slow"
pytest -m integration
```

### 4. Code Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8

# Type checking
mypy locagent_kernel
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
# or
git commit -m "fix: resolve issue description"
```

### 6. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a Pull Request on GitHub.

## 📝 Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 88 characters

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `style:` for formatting changes
- `chore:` for maintenance tasks

### Documentation

- Use clear, concise docstrings
- Follow [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings
- Update README.md for user-facing changes
- Add examples for new features

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data and fixtures
└── conftest.py     # Pytest configuration
```

### Writing Tests

- Write tests for all new functionality
- Aim for high test coverage (>90%)
- Use descriptive test names
- Include edge cases and error conditions

### Test Categories

Mark tests with appropriate categories:

```python
import pytest

@pytest.mark.slow
def test_large_repository_analysis():
    """Test that takes significant time."""
    pass

@pytest.mark.integration
def test_openai_integration():
    """Test that requires external services."""
    pass
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Operating system
   - LocAgent Kernel version

2. **Reproduction Steps**
   - Minimal code example
   - Expected vs actual behavior
   - Error messages/stack traces

3. **Additional Context**
   - Repository characteristics (size, languages)
   - Configuration used
   - Any relevant logs

## 💡 Feature Requests

For new features, please:

1. **Check Existing Issues** - Avoid duplicates
2. **Describe the Use Case** - Why is this needed?
3. **Propose Implementation** - How should it work?
4. **Consider Alternatives** - Are there other solutions?

## 🏗️ Architecture Guidelines

### Core Principles

- **Modularity**: Keep components loosely coupled
- **Extensibility**: Design for easy extension
- **Performance**: Consider scalability from the start
- **Reliability**: Handle errors gracefully

### Adding New Language Support

1. Create parser in `core/parsers/`
2. Add language configuration
3. Update documentation
4. Add comprehensive tests

### Adding New LLM Providers

1. Implement provider interface
2. Add configuration options
3. Update CLI and API
4. Add integration tests

## 📚 Documentation

### Types of Documentation

- **API Documentation**: Docstrings and type hints
- **User Guide**: README.md and examples
- **Developer Guide**: Architecture and contribution docs
- **Configuration**: YAML examples and parameter docs

### Documentation Standards

- Keep examples up-to-date
- Include both basic and advanced usage
- Provide clear error messages
- Document configuration options thoroughly

## 🔒 Security

### Reporting Security Issues

Please report security vulnerabilities privately to the maintainers.

### Security Guidelines

- Never commit API keys or secrets
- Validate all user inputs
- Use secure defaults
- Follow OWASP guidelines

## 📋 Review Process

### Pull Request Requirements

- [ ] Tests pass
- [ ] Code coverage maintained
- [ ] Documentation updated
- [ ] Code style checks pass
- [ ] Commit messages follow convention
- [ ] No merge conflicts

### Review Criteria

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable and maintainable?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security concerns?
- **Documentation**: Is it properly documented?

## 🎯 Areas for Contribution

### High Priority

- Additional language parsers
- Performance optimizations
- Better error handling
- More comprehensive tests

### Medium Priority

- CLI improvements
- Configuration enhancements
- Documentation improvements
- Example repositories

### Low Priority

- Code style improvements
- Minor bug fixes
- Typo corrections

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Tag maintainers for review help

## 🙏 Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to LocAgent Kernel! 🚀