"""
Sample application for testing Coretx code localization.
This is a simple web application with authentication and user management.
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class DatabaseManager:
    """Handles database operations for the application."""
    
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)


class PasswordManager:
    """Handles password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        # Note: This is a simplified example. In production, use bcrypt or similar.
        salt = "app_salt_2024"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return PasswordManager.hash_password(password) == password_hash


class SessionManager:
    """Manages user sessions and authentication tokens."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_session(self, user_id: int) -> str:
        """Create a new session for a user."""
        import secrets
        
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, session_token, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[int]:
        """Validate a session token and return user_id if valid."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id FROM sessions 
            WHERE session_token = ? AND expires_at > ?
        """, (session_token, datetime.now()))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def invalidate_session(self, session_token: str):
        """Invalidate a session token."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
        
        conn.commit()
        conn.close()


class UserManager:
    """Manages user operations like registration and authentication."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.session_manager = SessionManager(db_manager)
    
    def register_user(self, username: str, email: str, password: str) -> Dict:
        """Register a new user."""
        # Validate input
        if not username or not email or not password:
            return {"success": False, "error": "All fields are required"}
        
        if len(password) < 8:
            return {"success": False, "error": "Password must be at least 8 characters"}
        
        # Hash password
        password_hash = PasswordManager.hash_password(password)
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {"success": True, "user_id": user_id}
            
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return {"success": False, "error": "Username already exists"}
            elif "email" in str(e):
                return {"success": False, "error": "Email already exists"}
            else:
                return {"success": False, "error": "Registration failed"}
    
    def authenticate_user(self, username: str, password: str) -> Dict:
        """Authenticate a user and create a session."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, password_hash FROM users 
            WHERE username = ? AND is_active = TRUE
        """, (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"success": False, "error": "Invalid username or password"}
        
        user_id, stored_hash = result
        
        if not PasswordManager.verify_password(password, stored_hash):
            return {"success": False, "error": "Invalid username or password"}
        
        # Create session
        session_token = self.session_manager.create_session(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "session_token": session_token
        }
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile information."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, created_at, is_active
            FROM users WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "created_at": result[3],
                "is_active": result[4]
            }
        
        return None


class APIHandler:
    """Handles API requests for the web application."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.user_manager = UserManager(self.db_manager)
    
    def handle_register(self, request_data: Dict) -> Dict:
        """Handle user registration request."""
        username = request_data.get("username", "").strip()
        email = request_data.get("email", "").strip()
        password = request_data.get("password", "")
        
        return self.user_manager.register_user(username, email, password)
    
    def handle_login(self, request_data: Dict) -> Dict:
        """Handle user login request."""
        username = request_data.get("username", "").strip()
        password = request_data.get("password", "")
        
        return self.user_manager.authenticate_user(username, password)
    
    def handle_profile(self, session_token: str) -> Dict:
        """Handle profile request."""
        user_id = self.user_manager.session_manager.validate_session(session_token)
        
        if not user_id:
            return {"success": False, "error": "Invalid or expired session"}
        
        profile = self.user_manager.get_user_profile(user_id)
        
        if profile:
            return {"success": True, "profile": profile}
        else:
            return {"success": False, "error": "User not found"}
    
    def handle_logout(self, session_token: str) -> Dict:
        """Handle logout request."""
        self.user_manager.session_manager.invalidate_session(session_token)
        return {"success": True, "message": "Logged out successfully"}


# Example usage and testing
if __name__ == "__main__":
    # Initialize the application
    api = APIHandler()
    
    # Test user registration
    print("Testing user registration...")
    register_result = api.handle_register({
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    })
    print(f"Registration result: {register_result}")
    
    # Test user login
    print("\nTesting user login...")
    login_result = api.handle_login({
        "username": "testuser",
        "password": "securepassword123"
    })
    print(f"Login result: {login_result}")
    
    if login_result.get("success"):
        session_token = login_result["session_token"]
        
        # Test profile retrieval
        print("\nTesting profile retrieval...")
        profile_result = api.handle_profile(session_token)
        print(f"Profile result: {profile_result}")
        
        # Test logout
        print("\nTesting logout...")
        logout_result = api.handle_logout(session_token)
        print(f"Logout result: {logout_result}")