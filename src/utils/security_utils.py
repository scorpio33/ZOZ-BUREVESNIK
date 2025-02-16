import hashlib
import secrets
import string
import jwt
from datetime import datetime, timezone, timedelta
from typing import Dict

class SecurityUtils:
    JWT_SECRET = "your-secret-key"  # In production, use environment variable
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a secure random token"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        """Verify a password against its hash"""
        return stored_hash == hashlib.sha256(provided_password.encode()).hexdigest()
    
    @staticmethod
    def generate_access_token(user_id: int) -> str:
        """Generate JWT access token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.now(timezone.utc) + timedelta(days=1)
        }
        return jwt.encode(payload, SecurityUtils.JWT_SECRET, algorithm='HS256')

    @staticmethod
    def validate_token(token: str) -> Dict:
        """Validate JWT token and return payload"""
        try:
            return jwt.decode(token, SecurityUtils.JWT_SECRET, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None
