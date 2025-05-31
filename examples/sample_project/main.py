"""
Sample Python project for testing Coretx.
"""

from auth.manager import AuthManager
from models.user import User
from utils.logger import Logger


class Application:
    """Main application class."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.logger = Logger()
        self.users = []
    
    def start(self):
        """Start the application."""
        self.logger.info("Application starting...")
        self.auth_manager.initialize()
        
    def create_user(self, username: str, email: str) -> User:
        """Create a new user."""
        user = User(username=username, email=email)
        self.users.append(user)
        self.logger.info(f"Created user: {username}")
        return user
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user."""
        return self.auth_manager.authenticate(username, password)


if __name__ == "__main__":
    app = Application()
    app.start()