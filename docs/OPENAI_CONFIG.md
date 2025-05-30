# OpenAI Configuration

This document describes how to configure OpenAI API settings in LocAgent Kernel.

## Overview

LocAgent Kernel now supports setting OpenAI API key and base URL through multiple methods:

1. **Function parameters** (highest priority)
2. **Configuration files**
3. **Environment variables** (lowest priority)

## Methods

### 1. Function Parameters

#### quick_localize()

```python
from locagent_kernel import quick_localize

results = quick_localize(
    repo_path="/path/to/repo",
    problem_description="Bug description",
    model_name="gpt-4",
    openai_api_key="your-api-key-here",
    openai_base_url="https://api.openai.com/v1"
)
```

#### create_locator()

```python
from locagent_kernel import create_locator

locator = create_locator(
    repo_path="/path/to/repo",
    openai_api_key="your-api-key-here",
    openai_base_url="https://api.openai.com/v1"
)

results = locator.localize("Bug description")
```

### 2. Configuration Files

Create a YAML configuration file:

```yaml
agent:
  model_name: "gpt-4"
  api_key: "your-api-key-here"
  api_base: "https://api.openai.com/v1"
  temperature: 0.1
```

Use with functions:

```python
from locagent_kernel import create_locator

locator = create_locator(
    repo_path="/path/to/repo",
    config_path="config.yaml"
)
```

### 3. Direct Configuration

```python
from locagent_kernel import LocAgentConfig, CodeLocator

config = LocAgentConfig()
config.agent.api_key = "your-api-key-here"
config.agent.api_base = "https://api.openai.com/v1"

locator = CodeLocator(config)
locator.initialize("/path/to/repo")
```

### 4. Command Line Interface

```bash
# Basic usage with OpenAI configuration
locagent localize /path/to/repo "Bug description" \
  --openai-api-key "your-api-key-here" \
  --openai-base-url "https://api.openai.com/v1"

# With configuration file
locagent localize /path/to/repo "Bug description" \
  --config config.yaml \
  --openai-api-key "override-key"  # Overrides config file
```

## Custom Endpoints

### Azure OpenAI

```python
results = quick_localize(
    repo_path="/path/to/repo",
    problem_description="Bug description",
    openai_api_key="your-azure-key",
    openai_base_url="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
)
```

### Other OpenAI-Compatible APIs

```python
results = quick_localize(
    repo_path="/path/to/repo",
    problem_description="Bug description",
    openai_api_key="your-api-key",
    openai_base_url="https://your-custom-endpoint.com/v1"
)
```

## Priority Order

When multiple configuration methods are used, the priority is:

1. **Function parameters** (highest)
2. **Configuration file settings**
3. **Environment variables** (`OPENAI_API_KEY`)

Function parameters will always override configuration file settings and environment variables.

## Environment Variables

The following environment variables are supported:

- `OPENAI_API_KEY`: OpenAI API key (used if not specified elsewhere)

## Examples

See `examples/basic_usage.py` for complete examples demonstrating all configuration methods.

## Security Notes

- Never commit API keys to version control
- Use environment variables or secure configuration management for production
- Function parameters are useful for testing and dynamic configuration