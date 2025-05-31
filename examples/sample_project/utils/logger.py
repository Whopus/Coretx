"""
Logging utility module.
"""

import logging
from datetime import datetime
from typing import Optional


class Logger:
    """Simple logging utility."""
    
    def __init__(self, name: str = "app", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)