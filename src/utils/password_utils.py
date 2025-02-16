import hashlib
import re

class PasswordUtils:
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
            
        patterns = [
            r'[A-Z]',  # At least one uppercase letter
            r'[a-z]',  # At least one lowercase letter
            r'[0-9]',  # At least one digit
            r'[!@#$%^&*(),.?":{}|<>]'  # At least one special character
        ]
        return all(re.search(pattern, password) for pattern in patterns)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        """Verify a password against its hash"""
        return stored_hash == hashlib.sha256(provided_password.encode()).hexdigest()
