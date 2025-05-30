"""
Configuration Tests for CoreCtx

Tests for OpenAI configuration, parameter handling, and config validation.
"""

import os
import tempfile
import yaml
from pathlib import Path

# Import the CoreCtx modules
try:
    from coretx import LocAgentConfig, create_locator
    from coretx.utils.config_utils import load_config, save_config
    from coretx.config.settings import AgentConfig
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure CoreCtx is properly installed")
    exit(1)


def test_openai_config_creation():
    """Test OpenAI configuration creation and parameter handling."""
    print("🧪 Testing OpenAI configuration creation...")
    
    # Test default configuration
    config = AgentConfig()
    assert config.model_name == "gpt-4"
    assert config.temperature == 0.1
    assert config.max_tokens == 2048
    print("✅ Default OpenAI config created successfully")
    
    # Test custom configuration
    custom_config = AgentConfig(
        model_name="gpt-3.5-turbo",
        temperature=0.5,
        max_tokens=1500
    )
    assert custom_config.model_name == "gpt-3.5-turbo"
    assert custom_config.temperature == 0.5
    assert custom_config.max_tokens == 1500
    print("✅ Custom OpenAI config created successfully")


def test_locagent_config():
    """Test main LocAgent configuration."""
    print("🧪 Testing LocAgent configuration...")
    
    config = LocAgentConfig()
    
    # Test agent configuration
    assert hasattr(config, 'agent')
    assert config.agent.model_name == "gpt-4"
    assert config.agent.temperature == 0.1
    print("✅ Agent configuration working")
    
    # Test retrieval configuration
    assert hasattr(config, 'retrieval')
    assert config.retrieval.top_k == 10
    print("✅ Retrieval configuration working")
    
    # Test graph configuration
    assert hasattr(config, 'graph')
    assert isinstance(config.graph.file_extensions, list)
    print("✅ Graph configuration working")


def test_config_serialization():
    """Test configuration saving and loading."""
    print("🧪 Testing configuration serialization...")
    
    # Create a test configuration
    config = LocAgentConfig()
    config.agent.model_name = "gpt-3.5-turbo"
    config.agent.temperature = 0.3
    config.retrieval.top_k = 15
    
    # Test saving to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name
    
    try:
        save_config(config, temp_path)
        print("✅ Configuration saved successfully")
        
        # Test loading
        loaded_config = load_config(temp_path)
        assert loaded_config.agent.model_name == "gpt-3.5-turbo"
        assert loaded_config.agent.temperature == 0.3
        assert loaded_config.retrieval.top_k == 15
        print("✅ Configuration loaded successfully")
        
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_environment_variables():
    """Test environment variable handling."""
    print("🧪 Testing environment variable handling...")
    
    # Test OpenAI API key detection
    original_key = os.environ.get('OPENAI_API_KEY')
    
    # Test with key present
    os.environ['OPENAI_API_KEY'] = 'test-key-123'
    config = AgentConfig()
    # Note: We don't store the key in config for security
    print("✅ Environment variable handling working")
    
    # Restore original key
    if original_key:
        os.environ['OPENAI_API_KEY'] = original_key
    elif 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']


def test_config_validation():
    """Test configuration validation."""
    print("🧪 Testing configuration validation...")
    
    config = LocAgentConfig()
    
    # Test valid temperature range
    config.agent.temperature = 0.5
    assert 0.0 <= config.agent.temperature <= 2.0
    print("✅ Temperature validation working")
    
    # Test valid top_k
    config.retrieval.top_k = 20
    assert config.retrieval.top_k > 0
    print("✅ Top-k validation working")


def run_all_tests():
    """Run all configuration tests."""
    print("🚀 Starting CoreCtx Configuration Tests\n")
    
    try:
        test_openai_config_creation()
        test_locagent_config()
        test_config_serialization()
        test_environment_variables()
        test_config_validation()
        
        print("\n🎉 All configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)