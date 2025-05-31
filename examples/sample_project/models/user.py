"""
User model definition.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User data model."""
    username: str
    email: str
    created_at: datetime = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now()
    
    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False
    
    def __str__(self):
        return f"User({self.username}, {self.email})"