"""Authentication and user management for the Receipt Scanner application."""
import os
import json
from pathlib import Path
from typing import Optional

import bcrypt
from flask_login import UserMixin


class User(UserMixin):
    """User model for authentication."""
    
    def __init__(self, username: str):
        self.username = username
        self.id = username


class UserStore:
    """Simple file-based user storage with bcrypt password hashing."""
    
    def __init__(self, users_file: str):
        self.users_file = Path(users_file)
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users file with default admin if it doesn't exist."""
        if not self.users_file.exists():
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            # Get password from environment or use default
            default_password = os.environ.get("RECEIPT_SCANNER_PASSWORD", "admin123")
            default_username = os.environ.get("RECEIPT_SCANNER_USERNAME", "admin")
            
            # Hash the default password
            hashed = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
            
            users = {
                default_username: {
                    "password_hash": hashed.decode('utf-8')
                }
            }
            self.users_file.write_text(json.dumps(users, indent=2))
    
    def _load_users(self) -> dict:
        """Load users from file."""
        try:
            return json.loads(self.users_file.read_text())
        except json.JSONDecodeError as e:
            # Log error to help with debugging
            print(f"Warning: Failed to parse users file {self.users_file}: {e}")
            print("Starting with empty user database")
            return {}
        except FileNotFoundError:
            return {}
    
    def _save_users(self, users: dict):
        """Save users to file."""
        self.users_file.write_text(json.dumps(users, indent=2))
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify username and password combination."""
        users = self._load_users()
        if username not in users:
            return False
        
        stored_hash = users[username]["password_hash"].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username."""
        users = self._load_users()
        if username in users:
            return User(username)
        return None
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password."""
        users = self._load_users()
        if username not in users:
            return False
        
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        users[username]["password_hash"] = hashed.decode('utf-8')
        self._save_users(users)
        return True
