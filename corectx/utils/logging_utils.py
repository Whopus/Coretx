"""Logging utility functions."""

import logging
import sys
from pathlib import Path
from typing import Optional, Union


def setup_logger(name: str = "locagent", 
                level: str = "INFO",
                log_file: Optional[Union[str, Path]] = None,
                format_string: Optional[str] = None) -> logging.Logger:
    """
    Setup a logger with console and optional file output.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        format_string: Optional custom format string
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_level(logger: logging.Logger, level: str) -> None:
    """
    Set log level for a logger and all its handlers.
    
    Args:
        logger: Logger instance
        level: New log level
    """
    log_level = getattr(logging, level.upper())
    logger.setLevel(log_level)
    
    for handler in logger.handlers:
        handler.setLevel(log_level)


def add_file_handler(logger: logging.Logger, 
                    log_file: Union[str, Path],
                    level: str = "INFO",
                    format_string: Optional[str] = None) -> None:
    """
    Add a file handler to an existing logger.
    
    Args:
        logger: Logger instance
        log_file: Log file path
        level: Log level for the file handler
        format_string: Optional custom format string
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)


def create_performance_logger(name: str = "locagent.performance",
                            log_file: Optional[Union[str, Path]] = None) -> logging.Logger:
    """
    Create a logger specifically for performance metrics.
    
    Args:
        name: Logger name
        log_file: Optional log file path
        
    Returns:
        Performance logger
    """
    return setup_logger(
        name=name,
        level="INFO",
        log_file=log_file,
        format_string='%(asctime)s - PERF - %(message)s'
    )