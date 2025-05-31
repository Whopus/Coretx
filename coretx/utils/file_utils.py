"""
File scanning and filtering utilities.
"""

import os
from pathlib import Path
from typing import List, Set
import fnmatch
import logging

from ..models import AnalysisConfig


class FileScanner:
    """Scans directories for source code files."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.logger = logging.getLogger("coretx.scanner")
        
        # Compile ignore patterns
        self.ignore_patterns = set(config.ignore_patterns)
        
        # Default ignore patterns
        self.default_ignores = {
            "__pycache__",
            ".git",
            ".svn",
            ".hg",
            "node_modules",
            ".venv",
            "venv",
            ".env",
            "build",
            "dist",
            ".pytest_cache",
            ".mypy_cache",
            ".coverage",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "*.so",
            "*.dll",
            "*.dylib",
            "*.exe",
            "*.bin",
            "*.log",
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db"
        }
    
    def scan_directory(self, directory: Path) -> List[Path]:
        """Scan directory for source code files."""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            # Single file
            if self._should_include_file(directory):
                return [directory]
            else:
                return []
        
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                root_path = Path(root)
                
                # Filter directories
                dirs[:] = [d for d in dirs if self._should_include_directory(root_path / d)]
                
                # Process files
                for filename in filenames:
                    file_path = root_path / filename
                    
                    if self._should_include_file(file_path):
                        files.append(file_path)
                        
                        # Limit total files if needed
                        if len(files) >= 10000:  # Reasonable limit
                            self.logger.warning("Reached file limit (10,000), stopping scan")
                            return files
        
        except PermissionError as e:
            self.logger.warning(f"Permission denied accessing {directory}: {e}")
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
        
        self.logger.info(f"Found {len(files)} files in {directory}")
        return files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included in analysis."""
        # Check if file exists and is readable
        if not file_path.exists() or not file_path.is_file():
            return False
        
        # Check file size
        try:
            if file_path.stat().st_size > self.config.max_file_size:
                return False
        except OSError:
            return False
        
        # Check if hidden file
        if not self.config.include_hidden and file_path.name.startswith('.'):
            return False
        
        # Check ignore patterns
        if self._matches_ignore_patterns(file_path):
            return False
        
        # Check if it's a supported file type
        from ..parsers.registry import parser_registry
        return parser_registry.can_parse(str(file_path))
    
    def _should_include_directory(self, dir_path: Path) -> bool:
        """Check if a directory should be traversed."""
        # Check if hidden directory
        if not self.config.include_hidden and dir_path.name.startswith('.'):
            return False
        
        # Check ignore patterns
        if self._matches_ignore_patterns(dir_path):
            return False
        
        return True
    
    def _matches_ignore_patterns(self, path: Path) -> bool:
        """Check if path matches any ignore patterns."""
        path_str = str(path)
        path_name = path.name
        
        # Check against default ignores
        for pattern in self.default_ignores:
            if fnmatch.fnmatch(path_name, pattern) or fnmatch.fnmatch(path_str, pattern):
                return True
        
        # Check against configured ignores
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path_name, pattern) or fnmatch.fnmatch(path_str, pattern):
                return True
        
        return False
    
    def get_file_language(self, file_path: Path) -> str:
        """Detect the programming language of a file."""
        from ..parsers.registry import parser_registry
        return parser_registry.detect_language(str(file_path)) or "unknown"
    
    def filter_by_language(self, files: List[Path], languages: List[str]) -> List[Path]:
        """Filter files by programming language."""
        if not languages:
            return files
        
        filtered_files = []
        for file_path in files:
            file_language = self.get_file_language(file_path)
            if file_language in languages:
                filtered_files.append(file_path)
        
        return filtered_files
    
    def get_project_info(self, directory: Path) -> dict:
        """Get basic information about a project."""
        info = {
            "path": str(directory),
            "name": directory.name,
            "total_files": 0,
            "supported_files": 0,
            "languages": {},
            "size_bytes": 0
        }
        
        if not directory.exists():
            return info
        
        try:
            # Count all files
            for root, dirs, files in os.walk(directory):
                info["total_files"] += len(files)
                
                for filename in files:
                    file_path = Path(root) / filename
                    try:
                        info["size_bytes"] += file_path.stat().st_size
                    except OSError:
                        pass
            
            # Count supported files and languages
            supported_files = self.scan_directory(directory)
            info["supported_files"] = len(supported_files)
            
            for file_path in supported_files:
                language = self.get_file_language(file_path)
                info["languages"][language] = info["languages"].get(language, 0) + 1
        
        except Exception as e:
            logging.getLogger("coretx.scanner").error(f"Error getting project info: {e}")
        
        return info