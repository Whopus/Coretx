"""
OpenAI Integration Tests for Coretx

Tests for OpenAI API integration, natural language processing, and LLM-powered code localization.
"""

import os
import sys
import tempfile
from pathlib import Path

# Import Coretx components
try:
    from coretx import LocAgentConfig, create_locator
    from coretx.config.settings import AgentConfig
    from coretx.core.extensions.registry import registry
    from coretx.core.agent.enhanced_tools import enhanced_tools
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure Coretx is properly installed")
    exit(1)


class OpenAIIntegrationTester:
    """Test class for OpenAI integration with Coretx."""
    
    def __init__(self):
        # Test configuration - can be overridden with environment variables
        self.api_key = os.getenv('CORETX_TEST_API_KEY', 'sk-test-key-placeholder')
        self.api_base = os.getenv('CORETX_TEST_API_BASE', 'https://api.openai.com/v1')
        self.model_name = os.getenv('CORETX_TEST_MODEL', 'gpt-4')
        
        # Sample project path
        self.sample_project_path = Path(__file__).parent.parent / "sample_projects"
        
    def test_openai_config_creation(self):
        """Test OpenAI configuration with custom settings."""
        print("🧪 Testing OpenAI configuration creation...")
        
        try:
            # Create agent config with custom OpenAI settings
            agent_config = AgentConfig(
                model_name=self.model_name,
                api_key=self.api_key,
                api_base=self.api_base,
                temperature=0.1,
                max_tokens=2048
            )
            
            assert agent_config.model_name == self.model_name
            assert agent_config.api_key == self.api_key
            assert agent_config.api_base == self.api_base
            assert agent_config.temperature == 0.1
            
            print("✅ OpenAI configuration created successfully")
            return True
            
        except Exception as e:
            print(f"❌ OpenAI configuration test failed: {e}")
            return False
    
    def test_locagent_with_openai(self):
        """Test LocAgent creation with OpenAI configuration."""
        print("🧪 Testing LocAgent with OpenAI configuration...")
        
        try:
            # Create full configuration
            config = LocAgentConfig()
            config.agent.model_name = self.model_name
            config.agent.api_key = self.api_key
            config.agent.api_base = self.api_base
            config.agent.temperature = 0.1
            
            # Create locator
            locator = create_locator(config)
            
            assert locator is not None
            assert locator.config.agent.model_name == self.model_name
            
            print("✅ LocAgent with OpenAI created successfully")
            return True
            
        except Exception as e:
            print(f"❌ LocAgent OpenAI test failed: {e}")
            return False
    
    def test_enhanced_tools_initialization(self):
        """Test enhanced tools system initialization."""
        print("🧪 Testing enhanced tools initialization...")
        
        try:
            # Initialize the multi-language system
            registry.initialize_default_parsers()
            
            # Check if enhanced tools are available
            assert 'analyze_directory' in enhanced_tools.tools
            assert 'parse_file' in enhanced_tools.tools
            assert 'search_entities' in enhanced_tools.tools
            assert 'discover_relationships' in enhanced_tools.tools
            
            print("✅ Enhanced tools initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Enhanced tools test failed: {e}")
            return False
    
    def test_sample_project_analysis(self):
        """Test analysis of sample project if available."""
        print("🧪 Testing sample project analysis...")
        
        try:
            if not self.sample_project_path.exists():
                print("⚠️  Sample project not found, skipping analysis test")
                return True
            
            # Test directory analysis
            result = enhanced_tools.tools['analyze_directory'](
                directory_path=str(self.sample_project_path),
                recursive=True,
                show_stats=False
            )
            
            assert 'entities' in result
            assert 'total_entities' in result
            assert result['total_entities'] > 0
            
            print(f"✅ Sample project analysis successful ({result['total_entities']} entities found)")
            return True
            
        except Exception as e:
            print(f"❌ Sample project analysis failed: {e}")
            return False
    
    def test_entity_search_functionality(self):
        """Test entity search functionality."""
        print("🧪 Testing entity search functionality...")
        
        try:
            if not self.sample_project_path.exists():
                print("⚠️  Sample project not found, skipping search test")
                return True
            
            # Test entity search
            search_queries = ["authentication", "password", "session"]
            
            for query in search_queries:
                result = enhanced_tools.tools['search_entities'](
                    query=query,
                    limit=5
                )
                
                assert 'entities' in result
                # Note: Results may be empty if no matching entities found
                
            print("✅ Entity search functionality working")
            return True
            
        except Exception as e:
            print(f"❌ Entity search test failed: {e}")
            return False
    
    def test_file_parsing_capabilities(self):
        """Test file parsing capabilities."""
        print("🧪 Testing file parsing capabilities...")
        
        try:
            if not self.sample_project_path.exists():
                print("⚠️  Sample project not found, skipping parsing test")
                return True
            
            # Find Python files in sample project
            python_files = list(self.sample_project_path.glob("*.py"))
            
            if not python_files:
                print("⚠️  No Python files found in sample project")
                return True
            
            # Test parsing first Python file
            test_file = python_files[0]
            result = enhanced_tools.tools['parse_file'](
                file_path=str(test_file),
                show_content=False
            )
            
            assert 'entities' in result
            assert 'file_info' in result
            
            print(f"✅ File parsing successful for {test_file.name}")
            return True
            
        except Exception as e:
            print(f"❌ File parsing test failed: {e}")
            return False
    
    def test_configuration_validation(self):
        """Test configuration validation with various settings."""
        print("🧪 Testing configuration validation...")
        
        try:
            # Test valid configurations
            valid_configs = [
                {"model_name": "gpt-4", "temperature": 0.0},
                {"model_name": "gpt-3.5-turbo", "temperature": 0.5},
                {"model_name": "gpt-4-turbo", "temperature": 1.0},
            ]
            
            for config_data in valid_configs:
                agent_config = AgentConfig(**config_data)
                assert agent_config.model_name == config_data["model_name"]
                assert agent_config.temperature == config_data["temperature"]
            
            print("✅ Configuration validation successful")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation test failed: {e}")
            return False


def test_openai_integration():
    """Main test function for OpenAI integration."""
    print("🚀 Starting Coretx OpenAI Integration Tests\n")
    
    tester = OpenAIIntegrationTester()
    
    tests = [
        tester.test_openai_config_creation,
        tester.test_locagent_with_openai,
        tester.test_enhanced_tools_initialization,
        tester.test_sample_project_analysis,
        tester.test_entity_search_functionality,
        tester.test_file_parsing_capabilities,
        tester.test_configuration_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All OpenAI integration tests passed!")
        return True
    else:
        print("❌ Some OpenAI integration tests failed")
        return False


def run_with_custom_config():
    """Run tests with custom OpenAI configuration."""
    print("🔧 Custom OpenAI Configuration Test")
    print("=" * 50)
    
    # Example custom configuration
    custom_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    custom_api_base = "https://ai.comfly.chat/v1/"
    custom_model = "gpt-4.1"
    
    # Set environment variables for testing
    os.environ['CORETX_TEST_API_KEY'] = custom_api_key
    os.environ['CORETX_TEST_API_BASE'] = custom_api_base
    os.environ['CORETX_TEST_MODEL'] = custom_model
    
    print(f"🤖 Model: {custom_model}")
    print(f"🌐 API Base: {custom_api_base}")
    print(f"🔑 API Key: {custom_api_key[:20]}...")
    print()
    
    return test_openai_integration()


if __name__ == "__main__":
    # Check if custom config should be used
    if len(sys.argv) > 1 and sys.argv[1] == "--custom":
        success = run_with_custom_config()
    else:
        success = test_openai_integration()
    
    exit(0 if success else 1)