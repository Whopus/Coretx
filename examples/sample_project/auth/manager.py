"""
Authentication manager module.
"""

import hashlib
import time
from typing import Optional


class AuthManager:
    """Manages user authentication."""
    
    def __init__(self):
        self.sessions = {}
        self.users_db = {}
    
    def initialize(self):
        """Initialize the authentication system."""
        print("Auth manager initialized")
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user with username and password."""
        if username not in self.users_db:
            return False
        
        stored_hash = self.users_db[username]['password_hash']
        password_hash = self._hash_password(password)
        
        return stored_hash == password_hash
    
    def create_session(self, username: str) -> str:
        """Create a session for authenticated user."""
        session_id = self._generate_session_id()
        self.sessions[session_id] = {
            'username': username,
            'created_at': time.time()
        }
        return session_id
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid
        return str(uuid.uuid4())