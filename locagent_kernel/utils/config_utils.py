"""Configuration utility functions."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

from ..config import LocAgentConfig

logger = logging.getLogger(__name__)


def load_config(config_path: Union[str, Path]) -> Optional[LocAgentConfig]:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        LocAgentConfig instance or None if error
    """
    try:
        path = Path(config_path)
        if not path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            return None
        
        # Determine file format
        if path.suffix.lower() in ['.yaml', '.yml']:
            with open(path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
        elif path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
        else:
            logger.error(f"Unsupported configuration file format: {path.suffix}")
            return None
        
        return LocAgentConfig.from_dict(config_dict)
        
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        return None


def save_config(config: LocAgentConfig, config_path: Union[str, Path], 
               format: str = 'yaml') -> bool:
    """
    Save configuration to a file.
    
    Args:
        config: LocAgentConfig instance
        config_path: Path to save the configuration
        format: File format ('yaml' or 'json')
        
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = config.to_dict()
        
        if format.lower() in ['yaml', 'yml']:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        elif format.lower() == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2)
        else:
            logger.error(f"Unsupported format: {format}")
            return False
        
        logger.info(f"Configuration saved to {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving configuration to {config_path}: {e}")
        return False


def create_default_config() -> LocAgentConfig:
    """
    Create a default configuration.
    
    Returns:
        Default LocAgentConfig instance
    """
    return LocAgentConfig()


def merge_configs(base_config: LocAgentConfig, 
                 override_dict: Dict[str, Any]) -> LocAgentConfig:
    """
    Merge configuration with override values.
    
    Args:
        base_config: Base configuration
        override_dict: Dictionary with override values
        
    Returns:
        Merged configuration
    """
    # Convert base config to dict
    base_dict = base_config.to_dict()
    
    # Deep merge override values
    merged_dict = _deep_merge(base_dict, override_dict)
    
    return LocAgentConfig.from_dict(merged_dict)


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Override dictionary
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_config(config: LocAgentConfig) -> List[str]:
    """
    Validate configuration and return list of issues.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Validate work directory
    if not config.work_dir.exists():
        issues.append(f"Work directory does not exist: {config.work_dir}")
    
    # Validate agent configuration
    if not config.agent.model_name:
        issues.append("Agent model name is required")
    
    if config.agent.temperature < 0 or config.agent.temperature > 2:
        issues.append("Agent temperature should be between 0 and 2")
    
    if config.agent.max_tokens <= 0:
        issues.append("Agent max_tokens should be positive")
    
    # Validate retrieval configuration
    if config.retrieval.top_k <= 0:
        issues.append("Retrieval top_k should be positive")
    
    if config.retrieval.bm25_k1 <= 0:
        issues.append("BM25 k1 parameter should be positive")
    
    if config.retrieval.bm25_b < 0 or config.retrieval.bm25_b > 1:
        issues.append("BM25 b parameter should be between 0 and 1")
    
    # Validate graph configuration
    if not config.graph.file_extensions:
        issues.append("At least one file extension should be specified")
    
    if config.graph.max_depth <= 0:
        issues.append("Graph max_depth should be positive")
    
    return issues