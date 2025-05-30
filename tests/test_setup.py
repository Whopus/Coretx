"""
Setup and Integration Tests for CoreCtx

Tests for package installation, imports, and basic functionality.
"""

import sys
import importlib
from pathlib import Path


def test_package_imports():
    """Test that all main package components can be imported."""
    print("🧪 Testing package imports...")
    
    # Test main package import
    try:
        import coretx
        print("✅ Main package import successful")
    except ImportError as e:
        print(f"❌ Failed to import main package: {e}")
        return False
    
    # Test main functions import
    try:
        from coretx import quick_localize, create_locator, LocAgentConfig
        print("✅ Main functions import successful")
    except ImportError as e:
        print(f"❌ Failed to import main functions: {e}")
        return False
    
    # Test CLI module import
    try:
        import coretx.cli
        print("✅ CLI module import successful")
    except ImportError as e:
        print(f"❌ Failed to import CLI module: {e}")
        return False
    
    return True


def test_config_system():
    """Test configuration system functionality."""
    print("🧪 Testing configuration system...")
    
    try:
        from coretx import LocAgentConfig
        
        # Test config creation
        config = LocAgentConfig()
        print("✅ Configuration creation successful")
        
        # Test config attributes
        assert hasattr(config, 'agent'), "Missing agent config"
        assert hasattr(config, 'retrieval'), "Missing retrieval config"
        assert hasattr(config, 'graph'), "Missing graph config"
        print("✅ Configuration structure validation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        return False


def test_core_components():
    """Test that core components can be instantiated."""
    print("🧪 Testing core components...")
    
    try:
        from coretx import create_locator, LocAgentConfig
        
        # Test locator creation
        config = LocAgentConfig()
        locator = create_locator(config)
        print("✅ Code locator creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Core components test failed: {e}")
        return False


def test_package_structure():
    """Test package directory structure."""
    print("🧪 Testing package structure...")
    
    # Get package root
    try:
        import coretx
        package_root = Path(coretx.__file__).parent
        
        # Check for required directories
        required_dirs = ['config', 'core', 'utils']
        for dir_name in required_dirs:
            dir_path = package_root / dir_name
            if not dir_path.exists():
                print(f"❌ Missing required directory: {dir_name}")
                return False
        
        print("✅ Package structure validation successful")
        return True
        
    except Exception as e:
        print(f"❌ Package structure test failed: {e}")
        return False


def test_cli_availability():
    """Test CLI command availability."""
    print("🧪 Testing CLI availability...")
    
    try:
        import coretx.cli
        
        # Check if main function exists
        if hasattr(coretx.cli, 'main'):
            print("✅ CLI main function available")
            return True
        else:
            print("❌ CLI main function not found")
            return False
            
    except Exception as e:
        print(f"❌ CLI availability test failed: {e}")
        return False


def test_version_info():
    """Test version information."""
    print("🧪 Testing version information...")
    
    try:
        import coretx
        
        if hasattr(coretx, '__version__'):
            version = coretx.__version__
            print(f"✅ Package version: {version}")
        else:
            print("⚠️  No version information found")
        
        return True
        
    except Exception as e:
        print(f"❌ Version info test failed: {e}")
        return False


def run_all_tests():
    """Run all setup and integration tests."""
    print("🚀 Starting CoreCtx Setup Tests\n")
    
    tests = [
        test_package_imports,
        test_config_system,
        test_core_components,
        test_package_structure,
        test_cli_availability,
        test_version_info
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
        print("🎉 All setup tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)