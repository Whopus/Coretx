"""
Utility functions for the sample application.
"""

import re
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """Validate username format."""
    # Username should be 3-20 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None


def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent basic injection attacks."""
    if not isinstance(input_string, str):
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_json_safely(json_string: str) -> Optional[Dict]:
    """Safely parse JSON string."""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None


def generate_response(success: bool, data: Any = None, error: str = None) -> Dict:
    """Generate standardized API response."""
    response = {"success": success}
    
    if success and data is not None:
        response["data"] = data
    
    if not success and error:
        response["error"] = error
    
    response["timestamp"] = datetime.now().isoformat()
    
    return response


def calculate_password_strength(password: str) -> Dict:
    """Calculate password strength score."""
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 2
    elif len(password) >= 6:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long")
    
    # Character variety checks
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 2
    else:
        feedback.append("Add special characters")
    
    # Determine strength level
    if score >= 7:
        strength = "Strong"
    elif score >= 5:
        strength = "Medium"
    elif score >= 3:
        strength = "Weak"
    else:
        strength = "Very Weak"
    
    return {
        "score": score,
        "strength": strength,
        "feedback": feedback
    }


def rate_limit_check(user_id: int, action: str, max_attempts: int = 5, 
                    time_window: int = 300) -> bool:
    """
    Simple rate limiting check.
    In a real application, this would use Redis or similar.
    """
    # This is a simplified implementation
    # In production, you'd want to use a proper rate limiting solution
    import time
    
    # For demo purposes, we'll just return True
    # Real implementation would track attempts per user/action
    return True


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default configuration
            return {
                "database": {
                    "path": "app.db",
                    "timeout": 30
                },
                "session": {
                    "timeout_hours": 24,
                    "cleanup_interval": 3600
                },
                "security": {
                    "max_login_attempts": 5,
                    "lockout_duration": 900
                },
                "logging": {
                    "level": "INFO",
                    "file": "app.log"
                }
            }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


class DataValidator:
    """Validates various types of data."""
    
    @staticmethod
    def validate_user_data(data: Dict) -> List[str]:
        """Validate user registration/update data."""
        errors = []
        
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        
        if not validate_username(username):
            errors.append("Username must be 3-20 characters, alphanumeric and underscores only")
        
        if not validate_email(email):
            errors.append("Invalid email format")
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        return errors
    
    @staticmethod
    def validate_session_data(data: Dict) -> List[str]:
        """Validate session-related data."""
        errors = []
        
        session_token = data.get('session_token', '')
        
        if not session_token or len(session_token) < 10:
            errors.append("Invalid session token")
        
        return errors


# Example utility functions for testing
def create_test_data() -> Dict:
    """Create test data for development."""
    return {
        "users": [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123456"
            },
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123"
            }
        ]
    }


def cleanup_test_data():
    """Clean up test data."""
    import os
    
    test_files = ["app.db", "test.db", "app.log"]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")