"""
Rich console integration for Coretx.
"""

import sys
from typing import Any, Optional, Dict, List
import logging

try:
    from rich.console import Console
    from rich.theme import Theme
    from rich.style import Style
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    logging.warning("Rich library not available, falling back to basic console output")

logger = logging.getLogger(__name__)


class CoretxConsole:
    """Enhanced console with rich formatting for Coretx."""
    
    def __init__(self, force_terminal: Optional[bool] = None, width: Optional[int] = None):
        if HAS_RICH:
            # Define Coretx theme
            coretx_theme = Theme({
                "info": "cyan",
                "warning": "yellow",
                "error": "bold red",
                "success": "bold green",
                "highlight": "bold blue",
                "entity.file": "blue",
                "entity.class": "bold magenta",
                "entity.function": "bold cyan",
                "entity.method": "cyan",
                "entity.variable": "green",
                "entity.import": "yellow",
                "entity.heading": "bold white",
                "entity.link": "blue underline",
                "entity.html": "red",
                "entity.css": "purple",
                "language.python": "blue",
                "language.javascript": "yellow",
                "language.html": "red",
                "language.css": "purple",
                "language.markdown": "white",
                "score": "bold green",
                "path": "dim blue",
                "line": "dim white",
            })
            
            self.console = Console(
                theme=coretx_theme,
                force_terminal=force_terminal,
                width=width
            )
        else:
            self.console = None
    
    def print(self, *args, **kwargs) -> None:
        """Print with rich formatting if available."""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)
    
    def print_json(self, data: Any, **kwargs) -> None:
        """Print JSON with syntax highlighting."""
        if self.console:
            self.console.print_json(data, **kwargs)
        else:
            import json
            print(json.dumps(data, indent=2))
    
    def rule(self, title: str = "", **kwargs) -> None:
        """Print a horizontal rule."""
        if self.console:
            self.console.rule(title, **kwargs)
        else:
            print(f"\n{'=' * 50} {title} {'=' * 50}\n")
    
    def status(self, status: str, **kwargs):
        """Create a status context manager."""
        if self.console:
            return self.console.status(status, **kwargs)
        else:
            return _DummyStatus(status)
    
    def progress(self, **kwargs):
        """Create a progress context manager."""
        if self.console:
            from rich.progress import Progress
            return Progress(console=self.console, **kwargs)
        else:
            return _DummyProgress()
    
    def input(self, prompt: str = "", **kwargs) -> str:
        """Get user input with rich formatting."""
        if self.console:
            return self.console.input(prompt, **kwargs)
        else:
            return input(prompt)
    
    def confirm(self, question: str, default: bool = False) -> bool:
        """Ask for confirmation."""
        if self.console:
            from rich.prompt import Confirm
            return Confirm.ask(question, default=default, console=self.console)
        else:
            response = input(f"{question} ({'Y/n' if default else 'y/N'}): ").strip().lower()
            if not response:
                return default
            return response in ('y', 'yes', 'true', '1')
    
    def clear(self) -> None:
        """Clear the console."""
        if self.console:
            self.console.clear()
        else:
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def save_text(self, text: str, path: str) -> None:
        """Save console output to file."""
        if self.console:
            self.console.save_text(path)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
    
    def export_html(self, path: str, **kwargs) -> None:
        """Export console output as HTML."""
        if self.console:
            self.console.save_html(path, **kwargs)
        else:
            logger.warning("HTML export not available without rich library")
    
    def get_width(self) -> int:
        """Get console width."""
        if self.console:
            return self.console.width
        else:
            try:
                import shutil
                return shutil.get_terminal_size().columns
            except:
                return 80
    
    def get_height(self) -> int:
        """Get console height."""
        if self.console:
            return self.console.height
        else:
            try:
                import shutil
                return shutil.get_terminal_size().lines
            except:
                return 24


class _DummyStatus:
    """Dummy status context manager for when rich is not available."""
    
    def __init__(self, status: str):
        self.status = status
    
    def __enter__(self):
        print(f"Status: {self.status}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def update(self, status: str):
        print(f"Status: {status}")


class _DummyProgress:
    """Dummy progress context manager for when rich is not available."""
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def add_task(self, description: str, total: int = 100):
        print(f"Task: {description}")
        return 0
    
    def update(self, task_id: int, advance: int = 1, **kwargs):
        pass
    
    def advance(self, task_id: int, advance: int = 1):
        pass


# Global console instance
console = CoretxConsole()