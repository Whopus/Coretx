# Coretx Test Execution Guide

## Quick Start

### Prerequisites
```bash
# Install Coretx and dependencies
pip install -e .
pip install pytest pytest-html

# Set up test environment (optional, for full testing)
export CORETX_TEST_API_KEY="your-openai-api-key"
export CORETX_TEST_API_BASE="https://api.openai.com/v1"
export CORETX_TEST_MODEL="gpt-4"
```

### Run All Tests
```bash
# Quick test run (basic functionality)
python -m pytest tests/ -v

# Comprehensive test suite
python tests/integration/test_comprehensive.py

# With custom OpenAI configuration
python tests/integration/test_comprehensive.py --custom-openai
```

## Test Categories

### 1. Unit Tests (Fast, No External Dependencies)

#### Configuration Tests
```bash
# Test configuration system
python tests/test_config.py

# Expected output: All configuration tests pass
# Duration: ~5 seconds
```

#### Setup Tests
```bash
# Test package installation and imports
python tests/test_setup.py

# Expected output: All setup tests pass
# Duration: ~3 seconds
```

### 2. Integration Tests (Requires Sample Project)

#### OpenAI Integration Tests
```bash
# Basic OpenAI integration (no API calls)
python tests/integration/test_openai_integration.py

# With custom configuration (may make API calls)
python tests/integration/test_openai_integration.py --custom

# Expected output: OpenAI configuration and integration tests pass
# Duration: ~10-30 seconds depending on API usage
```

#### Natural Language Processing Tests
```bash
# Basic NLP functionality
python tests/integration/test_nlp_queries.py

# Comprehensive NLP testing (requires API key)
python tests/integration/test_nlp_queries.py --comprehensive

# Expected output: NLP and semantic search tests pass
# Duration: ~15-60 seconds depending on API usage
```

### 3. Comprehensive Test Suite

#### Full Test Suite
```bash
# Complete test suite with reporting
python tests/integration/test_comprehensive.py

# With custom OpenAI configuration
python tests/integration/test_comprehensive.py --custom-openai

# Expected output: Complete test report with performance metrics
# Duration: ~30-120 seconds depending on configuration
```

## Test Configuration Options

### Environment Variables

```bash
# OpenAI API Configuration
export CORETX_TEST_API_KEY="sk-your-api-key-here"
export CORETX_TEST_API_BASE="https://api.openai.com/v1"  # or custom endpoint
export CORETX_TEST_MODEL="gpt-4"  # or gpt-3.5-turbo, gpt-4-turbo, etc.

# Test Behavior Configuration
export CORETX_TEST_TIMEOUT="30"  # Test timeout in seconds
export CORETX_TEST_VERBOSE="true"  # Enable verbose output
export CORETX_TEST_SKIP_SLOW="false"  # Skip slow tests
```

### Custom Configuration Example

```bash
# Example: Testing with custom OpenAI-compatible API
export CORETX_TEST_API_KEY="sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
export CORETX_TEST_API_BASE="https://ai.comfly.chat/v1/"
export CORETX_TEST_MODEL="gpt-4.1"

# Run comprehensive tests
python tests/integration/test_comprehensive.py --custom-openai
```

## Test Scenarios and Expected Results

### Scenario 1: Basic Functionality Verification

```bash
# Command
python tests/test_setup.py

# Expected Output
🚀 Starting CoreCtx Setup Tests

🧪 Testing package imports...
✅ Main package import successful
✅ Main functions import successful
✅ CLI module import successful

🧪 Testing configuration system...
✅ Configuration creation successful
✅ Configuration structure validation successful

🧪 Testing core components...
✅ Code locator creation successful

📊 Test Results: 6/6 tests passed
🎉 All setup tests passed!
```

### Scenario 2: Sample Project Analysis

```bash
# Command
python tests/integration/test_openai_integration.py

# Expected Output
🚀 Starting Coretx OpenAI Integration Tests

🧪 Testing OpenAI configuration creation...
✅ OpenAI configuration created successfully

🧪 Testing sample project analysis...
✅ Sample project analysis successful (387 entities found)

🧪 Testing entity search functionality...
✅ Entity search functionality working

📊 Test Results: 7/7 tests passed
🎉 All OpenAI integration tests passed!
```

### Scenario 3: Natural Language Query Processing

```bash
# Command (with API key configured)
python tests/integration/test_nlp_queries.py --comprehensive

# Expected Output
🔬 Comprehensive Natural Language Processing Test

🧪 Testing semantic search queries...
  ✅ Query 'authentication and login functionality' returned 5 results
  ✅ Query 'password hashing and security' returned 3 results
✅ Semantic search test completed (100.0% success rate)

🧪 Testing LLM-powered queries...
  ✅ LLM query processed in 2.34s
✅ LLM-powered queries test completed (100.0% success rate)

📊 Test Results: 5/5 tests passed
🎉 Natural language processing tests passed!
```

### Scenario 4: Comprehensive Test Suite

```bash
# Command
python tests/integration/test_comprehensive.py --custom-openai

# Expected Output
╔══════════════════════════════════════════════════════════════╗
║                🧪 CORETX COMPREHENSIVE TEST SUITE 🧪         ║
║                                                              ║
║         Advanced Code Localization Engine Testing            ║
║         with Natural Language Processing                     ║
╚══════════════════════════════════════════════════════════════╝

🔧 Testing Environment Setup
🐍 Python version: 3.8.10
📦 Coretx package: Available
📁 Sample project: 4 Python files found
🔑 API Key: Configured (sk-Do6vjkCvmwTbWUoSD1E...)
✅ Environment setup validation completed

🧪 Basic Functionality Tests
1️⃣  Testing configuration creation...
   ✅ Configuration created successfully
2️⃣  Testing locator creation...
   ✅ Locator created successfully
✅ Basic functionality tests passed

🔗 Integration Tests
🤖 Running OpenAI Integration Tests...
   ✅ OpenAI integration tests passed
🗣️  Running Natural Language Processing Tests...
   ✅ NLP processing tests passed
📊 Integration Tests Summary: 2/2 passed (100.0%)

📈 Performance Tests
1️⃣  Testing directory analysis performance...
   ⏱️  Directory analysis: 0.045 seconds
2️⃣  Testing entity search performance...
   ⏱️  Entity search: 0.012 seconds
📊 Average operation time: 0.029 seconds
✅ Performance tests passed (good performance)

📋 Test Report Generation
📄 Test report saved to: tests/test_reports/comprehensive_test_report.json
⏱️  Total test duration: 45.67 seconds
📊 Overall success rate: 6/6

🎯 Final Test Summary
✅ Passed: 6
❌ Failed: 0
📊 Success Rate: 100.0%

🎉 Comprehensive test suite PASSED!
🚀 Coretx is ready for production use!
```

## Troubleshooting Common Issues

### Issue 1: Import Errors

```bash
# Problem
ImportError: No module named 'coretx'

# Solution
pip install -e .  # Install in development mode
# or
pip install coretx  # Install from PyPI
```

### Issue 2: Missing Sample Project

```bash
# Problem
⚠️  Sample project not found, skipping analysis test

# Solution
# Ensure sample project files are in tests/sample_projects/
ls tests/sample_projects/
# Should show: sample_app.py, utils.py, web_server.py, config.py
```

### Issue 3: API Key Issues

```bash
# Problem
⚠️  No LLM agent available, skipping LLM-powered query test

# Solution
export CORETX_TEST_API_KEY="your-actual-api-key"
export CORETX_TEST_API_BASE="https://api.openai.com/v1"
export CORETX_TEST_MODEL="gpt-4"
```

### Issue 4: Performance Issues

```bash
# Problem
❌ Performance tests failed (slow performance)

# Solution
# Check system resources
# Reduce test complexity
export CORETX_TEST_SKIP_SLOW="true"
```

### Issue 5: Network/API Issues

```bash
# Problem
❌ OpenAI integration tests failed: Connection timeout

# Solution
# Check internet connection
# Verify API endpoint
# Check API key validity
curl -H "Authorization: Bearer $CORETX_TEST_API_KEY" \
     "$CORETX_TEST_API_BASE/models"
```

## Test Output Interpretation

### Success Indicators
- ✅ Green checkmarks indicate passed tests
- 📊 Success rates above 80% are generally acceptable
- ⏱️ Performance metrics within expected ranges
- 🎉 Final success message

### Warning Indicators
- ⚠️ Yellow warnings indicate skipped or partially successful tests
- 📈 Performance metrics slightly above targets
- 🔧 Configuration issues that don't prevent testing

### Failure Indicators
- ❌ Red X marks indicate failed tests
- 💥 Exception traces
- 📉 Performance metrics significantly above targets
- 🚫 Critical configuration or setup issues

## Advanced Testing Options

### Custom Test Configuration

```python
# Create custom test configuration file: test_config.py
CUSTOM_CONFIG = {
    "api_key": "your-key",
    "api_base": "your-endpoint",
    "model_name": "your-model",
    "test_timeout": 60,
    "performance_threshold": 5.0,
    "skip_slow_tests": False
}
```

### Parallel Test Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
python -m pytest tests/ -n auto
```

### Test Coverage Analysis

```bash
# Generate coverage report
pip install pytest-cov
python -m pytest tests/ --cov=coretx --cov-report=html
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite
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
        run: |
          pip install -e .
          pip install pytest
      - name: Run tests
        run: python tests/integration/test_comprehensive.py
        env:
          CORETX_TEST_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Performance Benchmarks

### Expected Performance Ranges

| Operation | Fast | Acceptable | Slow |
|-----------|------|------------|------|
| Directory Analysis | < 1s | 1-5s | > 5s |
| Entity Search | < 0.1s | 0.1-1s | > 1s |
| File Parsing | < 0.1s | 0.1-0.5s | > 0.5s |
| NLP Query | < 5s | 5-15s | > 15s |

### Resource Usage Guidelines

| Resource | Normal | High | Critical |
|----------|--------|------|----------|
| Memory | < 200MB | 200-500MB | > 500MB |
| CPU | < 50% | 50-80% | > 80% |
| Network | < 10 requests/min | 10-30 requests/min | > 30 requests/min |

---

*This guide provides comprehensive instructions for executing Coretx tests and interpreting results. For additional support, refer to the main documentation or create an issue in the project repository.*