import hashlib
import secrets
import time
from typing import Optional

class SecurityManager:
    def __init__(self):
        self._failed_attempts = {}
        self._lockout_duration = 300  # 5 minutes
        self._max_attempts = 3
        
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, stored_hash: str, provided_password: str) -> bool:
        """Verify a password against its hash"""
        return self.hash_password(provided_password) == stored_hash
    
    def generate_verification_code(self, length: int = 6) -> str:
        """Generate a secure verification code"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    def check_brute_force(self, user_id: int) -> bool:
        """
        Check if user is locked out due to too many failed attempts
        Returns True if user can attempt login, False if locked out
        """
        if user_id not in self._failed_attempts:
            return True
            
        attempts, lockout_time = self._failed_attempts[user_id]
        
        if attempts >= self._max_attempts:
            if time.time() - lockout_time < self._lockout_duration:
                return False
            else:
                del self._failed_attempts[user_id]
                
        return True
    
    def record_failed_attempt(self, user_id: int):
        """Record a failed login attempt"""
        if user_id not in self._failed_attempts:
            self._failed_attempts[user_id] = [1, time.time()]
        else:
            attempts, _ = self._failed_attempts[user_id]
            self._failed_attempts[user_id] = [attempts + 1, time.time()]
    
    def reset_attempts(self, user_id: int):
        """Reset failed attempts counter for user"""
        if user_id in self._failed_attempts:
            del self._failed_attempts[user_id]