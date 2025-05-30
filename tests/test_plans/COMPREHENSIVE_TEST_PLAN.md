# Coretx Comprehensive Test Plan

## Overview

This document outlines the comprehensive testing strategy for Coretx, an advanced code localization engine that combines static analysis, dynamic graph construction, and LLM-powered reasoning to identify relevant code sections for bug fixes, feature implementations, and code understanding tasks.

## Test Objectives

### Primary Objectives
1. **Functional Verification**: Ensure all core features work as expected
2. **Integration Testing**: Verify OpenAI API integration and LLM functionality
3. **Performance Validation**: Confirm acceptable response times and resource usage
4. **Reliability Assessment**: Test error handling and edge cases
5. **User Experience**: Validate natural language query processing

### Secondary Objectives
1. **Scalability Testing**: Test with various project sizes
2. **Multi-language Support**: Verify support for different programming languages
3. **Configuration Flexibility**: Test various configuration options
4. **Documentation Accuracy**: Ensure examples and documentation work correctly

## Test Categories

### 1. Unit Tests (`tests/test_*.py`)

#### Configuration Tests (`test_config.py`)
- **Purpose**: Test configuration creation, validation, and serialization
- **Coverage**:
  - OpenAI configuration creation
  - LocAgent configuration
  - Configuration serialization/deserialization
  - Environment variable handling
  - Configuration validation

#### Setup Tests (`test_setup.py`)
- **Purpose**: Test package installation and basic imports
- **Coverage**:
  - Package imports
  - Configuration system
  - Core components
  - Package structure
  - CLI availability
  - Version information

### 2. Integration Tests (`tests/integration/`)

#### OpenAI Integration Tests (`test_openai_integration.py`)
- **Purpose**: Test OpenAI API integration and LLM functionality
- **Coverage**:
  - OpenAI configuration with custom settings
  - LocAgent creation with OpenAI
  - Enhanced tools initialization
  - Sample project analysis
  - Entity search functionality
  - File parsing capabilities
  - Configuration validation

#### Natural Language Processing Tests (`test_nlp_queries.py`)
- **Purpose**: Test natural language query processing and semantic search
- **Coverage**:
  - Semantic search queries
  - Contextual code analysis
  - LLM-powered queries
  - Multi-language understanding
  - Query performance

#### Comprehensive Tests (`test_comprehensive.py`)
- **Purpose**: Run complete test suite with reporting
- **Coverage**:
  - Environment setup validation
  - Basic functionality tests
  - Integration test orchestration
  - Performance testing
  - Test report generation

### 3. Sample Projects (`tests/sample_projects/`)

#### Web Application Sample
- **Purpose**: Realistic codebase for testing
- **Components**:
  - `sample_app.py`: Complete web application with authentication
  - `utils.py`: Utility functions and helpers
  - `web_server.py`: HTTP server implementation
  - `config.py`: Configuration management
  - Documentation and test results

## Test Scenarios

### Scenario 1: Bug Investigation
**Objective**: Test ability to locate code related to specific bugs

**Test Cases**:
1. **Authentication Bug**: "Users can't log in with valid credentials"
   - Expected: Locate authentication functions, password verification, session management
   - Success Criteria: Identify relevant classes and methods within 5 seconds

2. **Performance Issue**: "Application is slow when loading user profiles"
   - Expected: Find database queries, caching logic, profile loading code
   - Success Criteria: Locate performance-critical code paths

3. **Security Vulnerability**: "Potential SQL injection in user input"
   - Expected: Identify input validation, database query construction
   - Success Criteria: Find all user input handling code

### Scenario 2: Feature Development
**Objective**: Test ability to understand existing code for new feature implementation

**Test Cases**:
1. **New Authentication Method**: "Add OAuth2 support"
   - Expected: Understand current authentication flow, identify integration points
   - Success Criteria: Map out authentication architecture

2. **API Enhancement**: "Add rate limiting to API endpoints"
   - Expected: Locate API handlers, middleware, request processing
   - Success Criteria: Identify all API entry points

### Scenario 3: Code Review and Audit
**Objective**: Test ability to analyze code quality and security

**Test Cases**:
1. **Security Audit**: "Review password handling security"
   - Expected: Find password hashing, storage, validation code
   - Success Criteria: Identify all password-related functions

2. **Code Quality Review**: "Find potential code smells"
   - Expected: Identify complex functions, duplicated code, poor patterns
   - Success Criteria: Highlight areas needing refactoring

## Test Configuration

### OpenAI API Configuration
```python
# Test configuration for OpenAI integration
OPENAI_CONFIG = {
    "api_key": "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7",
    "base_url": "https://ai.comfly.chat/v1/",
    "model_name": "gpt-4.1",
    "temperature": 0.1,
    "max_tokens": 2048
}
```

### Test Environment Variables
```bash
# Required for comprehensive testing
export CORETX_TEST_API_KEY="sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
export CORETX_TEST_API_BASE="https://ai.comfly.chat/v1/"
export CORETX_TEST_MODEL="gpt-4.1"
```

## Performance Benchmarks

### Response Time Targets
- **Directory Analysis**: < 5 seconds for projects with < 100 files
- **Entity Search**: < 1 second for simple queries
- **File Parsing**: < 0.5 seconds per file
- **Natural Language Query**: < 10 seconds including LLM processing

### Resource Usage Targets
- **Memory Usage**: < 500MB for typical projects
- **CPU Usage**: < 80% during analysis
- **Network**: Minimal API calls, efficient batching

## Test Execution

### Running Individual Test Suites

```bash
# Basic configuration tests
python -m pytest tests/test_config.py -v

# Setup and installation tests
python tests/test_setup.py

# OpenAI integration tests
python tests/integration/test_openai_integration.py

# Natural language processing tests
python tests/integration/test_nlp_queries.py

# Comprehensive test suite
python tests/integration/test_comprehensive.py
```

### Running with Custom Configuration

```bash
# Run with custom OpenAI configuration
python tests/integration/test_openai_integration.py --custom
python tests/integration/test_nlp_queries.py --comprehensive
python tests/integration/test_comprehensive.py --custom-openai
```

### Automated Test Execution

```bash
# Run all tests with reporting
python -m pytest tests/ --html=test_report.html --self-contained-html

# Run comprehensive suite with custom config
CORETX_TEST_API_KEY="your-key" python tests/integration/test_comprehensive.py
```

## Success Criteria

### Minimum Acceptance Criteria
- **Unit Tests**: 100% pass rate
- **Integration Tests**: 80% pass rate (some may require API access)
- **Performance Tests**: Meet response time targets
- **Sample Project Analysis**: Successfully analyze all sample files

### Optimal Success Criteria
- **All Tests**: 95%+ pass rate
- **Performance**: Exceed response time targets by 50%
- **Natural Language Queries**: 90%+ accuracy in code localization
- **Multi-language Support**: Support for 5+ programming languages

## Test Data and Fixtures

### Sample Project Requirements
- **Realistic Codebase**: Representative of real-world applications
- **Multiple Languages**: Python, JavaScript, configuration files
- **Various Patterns**: Classes, functions, imports, documentation
- **Security Examples**: Authentication, validation, database operations

### Test Queries
- **Simple Queries**: Single keyword searches
- **Complex Queries**: Multi-concept natural language descriptions
- **Domain-Specific**: Security, performance, architecture queries
- **Edge Cases**: Ambiguous terms, typos, very long queries

## Reporting and Documentation

### Test Reports
- **Automated Reports**: JSON format with detailed results
- **Performance Metrics**: Response times, resource usage
- **Coverage Reports**: Code coverage and feature coverage
- **Failure Analysis**: Detailed error logs and debugging information

### Documentation Updates
- **Test Results**: Update README with latest test results
- **Performance Benchmarks**: Document current performance characteristics
- **Known Issues**: Track and document any test failures or limitations
- **Usage Examples**: Update examples based on test scenarios

## Continuous Integration

### CI/CD Pipeline Integration
```yaml
# Example GitHub Actions workflow
name: Coretx Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: python -m pytest tests/test_*.py
      - name: Run integration tests
        run: python tests/integration/test_comprehensive.py
        env:
          CORETX_TEST_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Quality Gates
- **Code Coverage**: Minimum 80% coverage
- **Performance Regression**: No more than 20% performance degradation
- **API Compatibility**: All existing APIs must remain functional
- **Documentation**: All new features must have corresponding tests

## Maintenance and Updates

### Regular Test Maintenance
- **Monthly**: Review and update test scenarios
- **Quarterly**: Performance benchmark updates
- **Release Cycle**: Comprehensive test suite execution
- **Annual**: Test strategy review and optimization

### Test Evolution
- **New Features**: Add corresponding test cases
- **Bug Fixes**: Add regression tests
- **Performance Improvements**: Update benchmarks
- **API Changes**: Update integration tests

---

*This test plan is designed to ensure Coretx meets the highest standards of quality, performance, and reliability for production use in code localization and analysis tasks.*