"""
Progress reporting utilities.
"""

import time
import sys
from typing import Optional


class ProgressReporter:
    """Simple progress reporter for terminal output."""
    
    def __init__(self, total: int, description: str = "Processing", 
                 show_percentage: bool = True, show_rate: bool = True):
        self.total = total
        self.description = description
        self.show_percentage = show_percentage
        self.show_rate = show_rate
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0
        
    def __enter__(self):
        self._print_progress()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._print_final()
    
    def update(self, increment: int = 1) -> None:
        """Update progress by increment."""
        self.current = min(self.current + increment, self.total)
        
        # Throttle updates to avoid too much output
        now = time.time()
        if now - self.last_update > 0.1:  # Update at most every 100ms
            self._print_progress()
            self.last_update = now
    
    def set_progress(self, current: int) -> None:
        """Set absolute progress."""
        self.current = min(current, self.total)
        self._print_progress()
    
    def _print_progress(self) -> None:
        """Print current progress."""
        if self.total == 0:
            return
        
        # Calculate percentage
        percentage = (self.current / self.total) * 100
        
        # Calculate rate
        elapsed = time.time() - self.start_time
        rate = self.current / elapsed if elapsed > 0 else 0
        
        # Build progress bar
        bar_width = 40
        filled = int(bar_width * self.current / self.total)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Build status line
        parts = [f"\r{self.description}: {bar}"]
        
        if self.show_percentage:
            parts.append(f" {percentage:.1f}%")
        
        parts.append(f" {self.current}/{self.total}")
        
        if self.show_rate and rate > 0:
            if rate >= 1:
                parts.append(f" ({rate:.1f}/s)")
            else:
                parts.append(f" ({1/rate:.1f}s/item)")
        
        # Estimate time remaining
        if rate > 0 and self.current > 0:
            remaining = (self.total - self.current) / rate
            if remaining < 60:
                parts.append(f" ETA: {remaining:.0f}s")
            elif remaining < 3600:
                parts.append(f" ETA: {remaining/60:.1f}m")
            else:
                parts.append(f" ETA: {remaining/3600:.1f}h")
        
        # Print without newline
        sys.stdout.write("".join(parts))
        sys.stdout.flush()
    
    def _print_final(self) -> None:
        """Print final completion message."""
        elapsed = time.time() - self.start_time
        rate = self.total / elapsed if elapsed > 0 else 0
        
        print(f"\n{self.description} completed: {self.total} items in {elapsed:.2f}s ({rate:.1f}/s)")


class SimpleProgress:
    """Even simpler progress indicator."""
    
    def __init__(self, description: str = "Processing"):
        self.description = description
        self.count = 0
        self.start_time = time.time()
    
    def __enter__(self):
        print(f"{self.description}...", end="", flush=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        print(f" done ({self.count} items, {elapsed:.2f}s)")
    
    def tick(self) -> None:
        """Increment counter and show progress."""
        self.count += 1
        if self.count % 10 == 0:
            print(".", end="", flush=True)