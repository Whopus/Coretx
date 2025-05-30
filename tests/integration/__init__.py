"""
Integration tests for Coretx.

This module contains comprehensive integration tests for Coretx functionality,
including OpenAI API integration, natural language processing, and end-to-end
code localization capabilities.
"""

from .test_openai_integration import test_openai_integration
from .test_nlp_queries import test_natural_language_processing
from .test_comprehensive import ComprehensiveTestSuite

__all__ = [
    'test_openai_integration',
    'test_natural_language_processing',
    'ComprehensiveTestSuite'
]