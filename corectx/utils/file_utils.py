"""File utility functions."""

from pathlib import Path
from typing import Optional, List, Union
import logging

logger = logging.getLogger(__name__)


def read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file
        encoding: File encoding
        
    Returns:
        File content or None if error
    """
    try:
        path = Path(file_path)
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def write_file(file_path: Union[str, Path], content: str, 
               encoding: str = 'utf-8', create_dirs: bool = True) -> bool:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        encoding: File encoding
        create_dirs: Whether to create parent directories
        
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return True
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return False


def ensure_dir(dir_path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists.
    
    Args:
        dir_path: Path to the directory
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {dir_path}: {e}")
        return False


def list_python_files(directory: Union[str, Path], 
                     recursive: bool = True) -> List[Path]:
    """
    List all Python files in a directory.
    
    Args:
        directory: Directory to search
        recursive: Whether to search recursively
        
    Returns:
        List of Python file paths
    """
    try:
        path = Path(directory)
        if not path.exists():
            return []
        
        if recursive:
            return list(path.rglob('*.py'))
        else:
            return list(path.glob('*.py'))
    except Exception as e:
        logger.error(f"Error listing Python files in {directory}: {e}")
        return []


def get_file_stats(file_path: Union[str, Path]) -> Optional[dict]:
    """
    Get file statistics.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file stats or None if error
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        stat = path.stat()
        
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'created': stat.st_ctime,
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'extension': path.suffix,
            'name': path.name,
            'parent': str(path.parent)
        }
    except Exception as e:
        logger.error(f"Error getting stats for {file_path}: {e}")
        return None


def find_files_by_pattern(directory: Union[str, Path], 
                         pattern: str, recursive: bool = True) -> List[Path]:
    """
    Find files matching a pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern to match
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    try:
        path = Path(directory)
        if not path.exists():
            return []
        
        if recursive:
            return list(path.rglob(pattern))
        else:
            return list(path.glob(pattern))
    except Exception as e:
        logger.error(f"Error finding files with pattern {pattern} in {directory}: {e}")
        return []