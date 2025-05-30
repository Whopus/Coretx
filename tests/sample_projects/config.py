"""
Configuration settings for the sample application.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class."""
    
    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'app.db')
    DATABASE_TIMEOUT = int(os.getenv('DATABASE_TIMEOUT', '30'))
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PASSWORD_SALT = os.getenv('PASSWORD_SALT', 'app_salt_2024')
    
    # Session settings
    SESSION_TIMEOUT_HOURS = int(os.getenv('SESSION_TIMEOUT_HOURS', '24'))
    SESSION_CLEANUP_INTERVAL = int(os.getenv('SESSION_CLEANUP_INTERVAL', '3600'))
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    LOCKOUT_DURATION = int(os.getenv('LOCKOUT_DURATION', '900'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Server settings
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and not callable(getattr(cls, key))
        }


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    DATABASE_PATH = 'dev_app.db'
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    DATABASE_PATH = '/var/lib/app/app.db'
    LOG_LEVEL = 'WARNING'
    
    # Override with more secure defaults
    SESSION_TIMEOUT_HOURS = 8
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_DURATION = 1800


class TestConfig(Config):
    """Test configuration."""
    
    DEBUG = True
    DATABASE_PATH = ':memory:'  # In-memory database for tests
    LOG_LEVEL = 'ERROR'
    SESSION_TIMEOUT_HOURS = 1


def get_config(environment: str = None) -> Config:
    """Get configuration based on environment."""
    if environment is None:
        environment = os.getenv('APP_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'test': TestConfig
    }
    
    return config_map.get(environment, DevelopmentConfig)


# Application constants
APP_NAME = "Sample Application"
APP_VERSION = "1.0.0"
API_VERSION = "v1"

# Error messages
ERROR_MESSAGES = {
    'INVALID_CREDENTIALS': 'Invalid username or password',
    'USER_NOT_FOUND': 'User not found',
    'USER_EXISTS': 'User already exists',
    'INVALID_SESSION': 'Invalid or expired session',
    'PERMISSION_DENIED': 'Permission denied',
    'VALIDATION_ERROR': 'Validation error',
    'INTERNAL_ERROR': 'Internal server error',
    'RATE_LIMITED': 'Too many requests, please try again later'
}

# Success messages
SUCCESS_MESSAGES = {
    'USER_REGISTERED': 'User registered successfully',
    'LOGIN_SUCCESS': 'Login successful',
    'LOGOUT_SUCCESS': 'Logout successful',
    'PROFILE_UPDATED': 'Profile updated successfully',
    'PASSWORD_CHANGED': 'Password changed successfully'
}

# Validation rules
VALIDATION_RULES = {
    'username': {
        'min_length': 3,
        'max_length': 20,
        'pattern': r'^[a-zA-Z0-9_]+$',
        'message': 'Username must be 3-20 characters, alphanumeric and underscores only'
    },
    'email': {
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'message': 'Invalid email format'
    },
    'password': {
        'min_length': 8,
        'max_length': 128,
        'message': 'Password must be 8-128 characters long'
    }
}