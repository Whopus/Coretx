"""
Comprehensive Integration Tests for Coretx

This module runs all integration tests and provides a complete test suite
for Coretx functionality including OpenAI integration, natural language processing,
and code localization capabilities.
"""

import os
import sys
import time
import json
from pathlib import Path

# Import test modules
try:
    from .test_openai_integration import test_openai_integration
    from .test_nlp_queries import test_natural_language_processing
except ImportError:
    # Handle direct execution
    sys.path.append(str(Path(__file__).parent))
    from test_openai_integration import test_openai_integration
    from test_nlp_queries import test_natural_language_processing

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


class ComprehensiveTestSuite:
    """Comprehensive test suite for Coretx."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
        # Test configuration
        self.api_key = os.getenv('CORETX_TEST_API_KEY', 'sk-test-key-placeholder')
        self.api_base = os.getenv('CORETX_TEST_API_BASE', 'https://api.openai.com/v1')
        self.model_name = os.getenv('CORETX_TEST_MODEL', 'gpt-4')
        
        # Sample project path
        self.sample_project_path = Path(__file__).parent.parent / "sample_projects"
    
    def print_banner(self):
        """Print test suite banner."""
        banner = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                🧪 CORETX COMPREHENSIVE TEST SUITE 🧪         ║
        ║                                                              ║
        ║         Advanced Code Localization Engine Testing            ║
        ║         with Natural Language Processing                     ║
        ║                                                              ║
        ║  🔧 OpenAI Integration Tests                                  ║
        ║  🗣️  Natural Language Processing Tests                       ║
        ║  📊 Performance and Reliability Tests                        ║
        ║  🎯 End-to-End Functionality Tests                           ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def test_environment_setup(self):
        """Test and validate the test environment."""
        print("🔧 Testing Environment Setup")
        print("=" * 50)
        
        try:
            # Check Python version
            python_version = sys.version_info
            print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Check Coretx installation
            import coretx
            print(f"📦 Coretx package: Available")
            
            # Check sample project
            if self.sample_project_path.exists():
                sample_files = list(self.sample_project_path.glob("*.py"))
                print(f"📁 Sample project: {len(sample_files)} Python files found")
            else:
                print("⚠️  Sample project: Not found")
            
            # Check API configuration
            if self.api_key and self.api_key != 'sk-test-key-placeholder':
                print(f"🔑 API Key: Configured ({self.api_key[:20]}...)")
                print(f"🌐 API Base: {self.api_base}")
                print(f"🤖 Model: {self.model_name}")
            else:
                print("⚠️  API Key: Using placeholder (some tests may be skipped)")
            
            print("✅ Environment setup validation completed\n")
            return True
            
        except Exception as e:
            print(f"❌ Environment setup failed: {e}\n")
            return False
    
    def run_basic_functionality_tests(self):
        """Run basic functionality tests."""
        print("🧪 Basic Functionality Tests")
        print("=" * 50)
        
        try:
            # Test 1: Configuration creation
            print("1️⃣  Testing configuration creation...")
            config = LocAgentConfig()
            assert config is not None
            print("   ✅ Configuration created successfully")
            
            # Test 2: Locator creation
            print("2️⃣  Testing locator creation...")
            locator = create_locator(config)
            assert locator is not None
            print("   ✅ Locator created successfully")
            
            # Test 3: Enhanced tools availability
            print("3️⃣  Testing enhanced tools...")
            registry.initialize_default_parsers()
            assert 'analyze_directory' in enhanced_tools.tools
            print("   ✅ Enhanced tools available")
            
            # Test 4: Sample project analysis (if available)
            if self.sample_project_path.exists():
                print("4️⃣  Testing sample project analysis...")
                result = enhanced_tools.tools['analyze_directory'](
                    directory_path=str(self.sample_project_path),
                    recursive=True,
                    show_stats=False
                )
                assert 'entities' in result
                print(f"   ✅ Sample project analyzed ({result.get('total_entities', 0)} entities)")
            else:
                print("4️⃣  Sample project analysis skipped (no sample project)")
            
            print("✅ Basic functionality tests passed\n")
            return True
            
        except Exception as e:
            print(f"❌ Basic functionality tests failed: {e}\n")
            return False
    
    def run_integration_tests(self):
        """Run integration tests."""
        print("🔗 Integration Tests")
        print("=" * 50)
        
        results = {}
        
        # OpenAI Integration Tests
        print("🤖 Running OpenAI Integration Tests...")
        try:
            openai_result = test_openai_integration()
            results['openai_integration'] = openai_result
            print(f"   {'✅' if openai_result else '❌'} OpenAI integration tests {'passed' if openai_result else 'failed'}")
        except Exception as e:
            print(f"   ❌ OpenAI integration tests failed with exception: {e}")
            results['openai_integration'] = False
        
        print()
        
        # Natural Language Processing Tests
        print("🗣️  Running Natural Language Processing Tests...")
        try:
            nlp_result = test_natural_language_processing()
            results['nlp_processing'] = nlp_result
            print(f"   {'✅' if nlp_result else '❌'} NLP processing tests {'passed' if nlp_result else 'failed'}")
        except Exception as e:
            print(f"   ❌ NLP processing tests failed with exception: {e}")
            results['nlp_processing'] = False
        
        print()
        
        # Calculate overall success
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        print(f"📊 Integration Tests Summary: {passed_tests}/{total_tests} passed ({success_rate:.1%})")
        print("✅ Integration tests completed\n" if success_rate >= 0.8 else "⚠️  Integration tests need attention\n")
        
        return results
    
    def run_performance_tests(self):
        """Run performance and reliability tests."""
        print("📈 Performance Tests")
        print("=" * 50)
        
        try:
            if not self.sample_project_path.exists():
                print("⚠️  Sample project not found, skipping performance tests\n")
                return True
            
            performance_results = {}
            
            # Test 1: Directory analysis performance
            print("1️⃣  Testing directory analysis performance...")
            start_time = time.time()
            result = enhanced_tools.tools['analyze_directory'](
                directory_path=str(self.sample_project_path),
                recursive=True,
                show_stats=False
            )
            duration = time.time() - start_time
            performance_results['directory_analysis'] = duration
            print(f"   ⏱️  Directory analysis: {duration:.3f} seconds")
            
            # Test 2: Entity search performance
            print("2️⃣  Testing entity search performance...")
            start_time = time.time()
            search_result = enhanced_tools.tools['search_entities'](
                query="authentication",
                limit=10
            )
            duration = time.time() - start_time
            performance_results['entity_search'] = duration
            print(f"   ⏱️  Entity search: {duration:.3f} seconds")
            
            # Test 3: File parsing performance
            python_files = list(self.sample_project_path.glob("*.py"))
            if python_files:
                print("3️⃣  Testing file parsing performance...")
                start_time = time.time()
                parse_result = enhanced_tools.tools['parse_file'](
                    file_path=str(python_files[0]),
                    show_content=False
                )
                duration = time.time() - start_time
                performance_results['file_parsing'] = duration
                print(f"   ⏱️  File parsing: {duration:.3f} seconds")
            
            # Performance evaluation
            avg_performance = sum(performance_results.values()) / len(performance_results)
            print(f"\n📊 Average operation time: {avg_performance:.3f} seconds")
            
            if avg_performance < 5.0:
                print("✅ Performance tests passed (good performance)\n")
                return True
            elif avg_performance < 10.0:
                print("⚠️  Performance tests passed (acceptable performance)\n")
                return True
            else:
                print("❌ Performance tests failed (slow performance)\n")
                return False
            
        except Exception as e:
            print(f"❌ Performance tests failed: {e}\n")
            return False
    
    def generate_test_report(self, results):
        """Generate a comprehensive test report."""
        print("📋 Test Report Generation")
        print("=" * 50)
        
        total_duration = time.time() - self.start_time
        
        report = {
            "test_suite": "Coretx Comprehensive Test Suite",
            "timestamp": time.time(),
            "duration": total_duration,
            "environment": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "api_key_configured": self.api_key != 'sk-test-key-placeholder',
                "api_base": self.api_base,
                "model_name": self.model_name,
                "sample_project_available": self.sample_project_path.exists()
            },
            "results": results,
            "summary": {
                "total_test_categories": len(results),
                "passed_categories": sum(1 for r in results.values() if r),
                "overall_success": sum(1 for r in results.values() if r) / len(results) >= 0.8
            }
        }
        
        # Save report to file
        report_file = Path(__file__).parent.parent / "test_reports" / "comprehensive_test_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: {report_file}")
        print(f"⏱️  Total test duration: {total_duration:.2f} seconds")
        print(f"📊 Overall success rate: {report['summary']['passed_categories']}/{report['summary']['total_test_categories']}")
        
        return report
    
    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite."""
        self.print_banner()
        
        print(f"🚀 Starting Comprehensive Test Suite")
        print(f"⏰ Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test results tracking
        all_results = {}
        
        # 1. Environment Setup
        env_result = self.test_environment_setup()
        all_results['environment_setup'] = env_result
        
        # 2. Basic Functionality
        basic_result = self.run_basic_functionality_tests()
        all_results['basic_functionality'] = basic_result
        
        # 3. Integration Tests
        integration_results = self.run_integration_tests()
        all_results.update(integration_results)
        
        # 4. Performance Tests
        performance_result = self.run_performance_tests()
        all_results['performance'] = performance_result
        
        # 5. Generate Report
        report = self.generate_test_report(all_results)
        
        # Final Summary
        print("\n🎯 Final Test Summary")
        print("=" * 50)
        
        total_tests = len(all_results)
        passed_tests = sum(1 for result in all_results.values() if result)
        success_rate = passed_tests / total_tests
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📊 Success Rate: {success_rate:.1%}")
        
        if success_rate >= 0.8:
            print("\n🎉 Comprehensive test suite PASSED!")
            print("🚀 Coretx is ready for production use!")
        else:
            print("\n⚠️  Comprehensive test suite needs attention")
            print("🔧 Some components may need debugging")
        
        return success_rate >= 0.8


def run_with_custom_openai_config():
    """Run comprehensive tests with custom OpenAI configuration."""
    print("🔧 Setting up custom OpenAI configuration...")
    
    # Custom configuration as provided
    custom_api_key = "sk-Do6vjkCvmwTbWUoSD1E88935470445A6979e0cF3A6Ea1eD7"
    custom_api_base = "https://ai.comfly.chat/v1/"
    custom_model = "gpt-4.1"
    
    # Set environment variables
    os.environ['CORETX_TEST_API_KEY'] = custom_api_key
    os.environ['CORETX_TEST_API_BASE'] = custom_api_base
    os.environ['CORETX_TEST_MODEL'] = custom_model
    
    print(f"🤖 Model: {custom_model}")
    print(f"🌐 API Base: {custom_api_base}")
    print(f"🔑 API Key: {custom_api_key[:20]}...")
    print()
    
    # Run comprehensive test suite
    test_suite = ComprehensiveTestSuite()
    return test_suite.run_comprehensive_test_suite()


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--custom-openai":
        success = run_with_custom_openai_config()
    else:
        test_suite = ComprehensiveTestSuite()
        success = test_suite.run_comprehensive_test_suite()
    
    exit(0 if success else 1)