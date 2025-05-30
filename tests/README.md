# Coretx Test Suite

## Overview

This directory contains the comprehensive test suite for Coretx, an advanced code localization engine that combines static analysis, dynamic graph construction, and LLM-powered reasoning to identify relevant code sections for bug fixes, feature implementations, and code understanding tasks.

## Directory Structure

```
tests/
├── README.md                          # This file
├── __init__.py                        # Test package initialization
├── test_config.py                     # Configuration system tests
├── test_setup.py                      # Package setup and import tests
├── integration/                       # Integration tests
│   ├── __init__.py
│   ├── test_openai_integration.py     # OpenAI API integration tests
│   ├── test_nlp_queries.py           # Natural language processing tests
│   └── test_comprehensive.py         # Complete test suite runner
├── sample_projects/                   # Sample codebases for testing
│   ├── sample_app.py                  # Web application example
│   ├── utils.py                       # Utility functions
│   ├── web_server.py                  # HTTP server implementation
│   ├── config.py                      # Configuration management
│   ├── README.md                      # Sample project documentation
│   └── simple_coretx_results.json    # Test results data
├── test_plans/                       # Test documentation
│   ├── COMPREHENSIVE_TEST_PLAN.md     # Complete testing strategy
│   └── TEST_EXECUTION_GUIDE.md       # Test execution instructions
└── test_reports/                     # Generated test reports
    └── __init__.py
```

## Quick Start

### Prerequisites

```bash
# Install Coretx in development mode
cd /path/to/Coretx
pip install -e .

# Install test dependencies
pip install pytest pytest-html
```

### Run Basic Tests

```bash
# Run all unit tests
python -m pytest tests/test_*.py -v

# Run specific test files
python tests/test_config.py
python tests/test_setup.py
```

### Run Integration Tests

```bash
# Basic integration tests (no API required)
python tests/integration/test_openai_integration.py

# Natural language processing tests
python tests/integration/test_nlp_queries.py

# Complete comprehensive test suite
python tests/integration/test_comprehensive.py
```

### Run with Custom OpenAI Configuration

```bash
# Set environment variables
export CORETX_TEST_API_KEY="sk-Do6.."
export CORETX_TEST_API_BASE="https://ai.comfly.chat/v1/"
export CORETX_TEST_MODEL="gpt-4.1"

# Run comprehensive tests with custom config
python tests/integration/test_comprehensive.py --custom-openai
```

## Test Categories

### 1. Unit Tests

#### Configuration Tests (`test_config.py`)
Tests the configuration system including:
- OpenAI configuration creation and validation
- LocAgent configuration management
- Configuration serialization/deserialization
- Environment variable handling
- Parameter validation

**Run**: `python tests/test_config.py`

#### Setup Tests (`test_setup.py`)
Tests package installation and basic functionality:
- Package imports and module availability
- Configuration system initialization
- Core component creation
- Package structure validation
- CLI availability

**Run**: `python tests/test_setup.py`

### 2. Integration Tests

#### OpenAI Integration Tests (`integration/test_openai_integration.py`)
Tests OpenAI API integration and LLM functionality:
- OpenAI configuration with custom settings
- LocAgent creation with OpenAI backend
- Enhanced tools system initialization
- Sample project analysis capabilities
- Entity search and file parsing
- Configuration validation

**Run**: `python tests/integration/test_openai_integration.py`

**With Custom Config**: `python tests/integration/test_openai_integration.py --custom`

#### Natural Language Processing Tests (`integration/test_nlp_queries.py`)
Tests natural language query processing:
- Semantic search with natural language queries
- Contextual code analysis
- LLM-powered code understanding
- Multi-language support
- Query performance benchmarks

**Run**: `python tests/integration/test_nlp_queries.py`

**Comprehensive**: `python tests/integration/test_nlp_queries.py --comprehensive`

#### Comprehensive Test Suite (`integration/test_comprehensive.py`)
Complete test suite with reporting:
- Environment setup validation
- All integration tests orchestration
- Performance testing and benchmarks
- Detailed test report generation
- Success/failure analysis

**Run**: `python tests/integration/test_comprehensive.py`

**With Custom OpenAI**: `python tests/integration/test_comprehensive.py --custom-openai`

### 3. Sample Projects

The `sample_projects/` directory contains realistic code examples for testing:

- **`sample_app.py`**: Complete web application with authentication, user management, and security features
- **`utils.py`**: Utility functions for validation, hashing, and data processing
- **`web_server.py`**: HTTP server implementation with routing and middleware
- **`config.py`**: Configuration management with environment variables

These files provide a realistic codebase for testing Coretx's ability to:
- Locate authentication and security code
- Find database operations and queries
- Identify input validation and sanitization
- Discover session management and tokens
- Analyze error handling patterns

## Test Configuration

### Environment Variables

```bash
# OpenAI API Configuration (optional, for full testing)
export CORETX_TEST_API_KEY="your-openai-api-key"
export CORETX_TEST_API_BASE="https://api.openai.com/v1"  # or custom endpoint
export CORETX_TEST_MODEL="gpt-4"  # or gpt-3.5-turbo, gpt-4-turbo

# Test Behavior Configuration
export CORETX_TEST_TIMEOUT="30"      # Test timeout in seconds
export CORETX_TEST_VERBOSE="true"    # Enable verbose output
export CORETX_TEST_SKIP_SLOW="false" # Skip slow tests
```

### Custom Configuration Example

For testing with the provided OpenAI-compatible API:

```bash
export CORETX_TEST_API_KEY="sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
export CORETX_TEST_API_BASE="https://ai.comfly.chat/v1/"
export CORETX_TEST_MODEL="gpt-4.1"
```

## Expected Test Results

### Unit Tests
- **Configuration Tests**: 100% pass rate expected
- **Setup Tests**: 100% pass rate expected
- **Duration**: 5-10 seconds total

### Integration Tests
- **OpenAI Integration**: 80-100% pass rate (depends on API availability)
- **NLP Processing**: 80-100% pass rate (depends on sample project and API)
- **Duration**: 30-120 seconds depending on API usage

### Performance Benchmarks
- **Directory Analysis**: < 5 seconds for sample project
- **Entity Search**: < 1 second for simple queries
- **File Parsing**: < 0.5 seconds per file
- **Natural Language Query**: < 15 seconds including LLM processing

## Test Scenarios

### Scenario 1: Bug Investigation
Test Coretx's ability to locate code related to specific bugs:

```python
# Example queries that should succeed
queries = [
    "Users can't log in with valid credentials",
    "Application is slow when loading user profiles",
    "Potential SQL injection in user input",
    "Session tokens are not being validated properly"
]
```

### Scenario 2: Feature Development
Test understanding of existing code for new feature implementation:

```python
# Example development queries
queries = [
    "Add OAuth2 support to existing authentication",
    "Implement rate limiting for API endpoints",
    "Add password strength validation",
    "Create user role management system"
]
```

### Scenario 3: Security Audit
Test ability to identify security-related code:

```python
# Example security queries
queries = [
    "Find all password handling code",
    "Locate input validation functions",
    "Identify database query construction",
    "Show session management implementation"
]
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Solution: Install Coretx in development mode
   pip install -e .
   ```

2. **Missing Sample Project**
   ```bash
   # Check if sample files exist
   ls tests/sample_projects/
   # Should show: sample_app.py, utils.py, web_server.py, config.py
   ```

3. **API Key Issues**
   ```bash
   # Verify API key is set correctly
   echo $CORETX_TEST_API_KEY
   # Test API connectivity
   curl -H "Authorization: Bearer $CORETX_TEST_API_KEY" \
        "$CORETX_TEST_API_BASE/models"
   ```

4. **Performance Issues**
   ```bash
   # Skip slow tests if needed
   export CORETX_TEST_SKIP_SLOW="true"
   ```

### Debug Mode

For detailed debugging information:

```bash
# Enable verbose output
export CORETX_TEST_VERBOSE="true"

# Run with Python debugging
python -u tests/integration/test_comprehensive.py --custom-openai
```

## Contributing

### Adding New Tests

1. **Unit Tests**: Add to existing `test_*.py` files or create new ones
2. **Integration Tests**: Add to `integration/` directory
3. **Sample Code**: Add realistic examples to `sample_projects/`
4. **Documentation**: Update test plans and execution guides

### Test Guidelines

- **Naming**: Use descriptive test function names with `test_` prefix
- **Documentation**: Include docstrings explaining test purpose
- **Assertions**: Use clear assertions with meaningful error messages
- **Performance**: Include timing for performance-critical tests
- **Cleanup**: Ensure tests clean up any created resources

### Example Test Function

```python
def test_new_functionality():
    """Test description of what this test validates."""
    print("🧪 Testing new functionality...")
    
    try:
        # Test setup
        config = create_test_config()
        
        # Test execution
        result = perform_test_operation(config)
        
        # Assertions
        assert result is not None, "Result should not be None"
        assert result.success, f"Operation failed: {result.error}"
        
        print("✅ New functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ New functionality test failed: {e}")
        return False
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Coretx Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install pytest pytest-html pytest-cov
      - name: Run unit tests
        run: python -m pytest tests/test_*.py -v
      - name: Run integration tests
        run: python tests/integration/test_comprehensive.py
        env:
          CORETX_TEST_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CORETX_TEST_API_BASE: ${{ secrets.OPENAI_API_BASE }}
          CORETX_TEST_MODEL: ${{ secrets.OPENAI_MODEL }}
      - name: Generate coverage report
        run: python -m pytest tests/ --cov=coretx --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
```

## Support

For questions, issues, or contributions related to the test suite:

1. **Documentation**: Check the test plans in `test_plans/` directory
2. **Issues**: Create an issue in the main Coretx repository
3. **Discussions**: Use GitHub Discussions for questions
4. **Pull Requests**: Submit PRs with new tests or improvements

---

*This test suite ensures Coretx meets the highest standards of quality, performance, and reliability for production use in code localization and analysis tasks.*
