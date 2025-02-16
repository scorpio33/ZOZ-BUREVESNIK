import hashlib
import os
import re

class PasswordUtils:
    def __init__(self):
        self.min_length = 8
        self.salt_length = 16
    
    def validate_password(self, password: str) -> bool:
        """Проверка пароля на соответствие требованиям безопасности"""
        if len(password) < self.min_length:
            return False
            
        # Должен содержать хотя бы одну цифру
        if not re.search(r"\d", password):
            return False
            
        # Должен содержать хотя бы одну букву
        if not re.search(r"[a-zA-Z]", password):
            return False
            
        return True
    
    def hash_password(self, password: str) -> tuple[str, str]:
        """Хеширование пароля с солью"""
        salt = os.urandom(self.salt_length).hex()
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return hashed, salt
    
    def verify_password(self, hashed: str, salt: str, password: str) -> bool:
        """Проверка пароля"""
        return hashed == hashlib.sha256((password + salt).encode()).hexdigest()
    
    def is_strong_password(self, password: str) -> bool:
        """Проверка на сложность пароля"""
        if len(password) < 8:
            return False
            
        # Должен содержать заглавные и строчные буквы
        if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password):
            return False
            
        # Должен содержать цифры
        if not re.search(r"\d", password):
            return False
            
        # Должен содержать специальные символы
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
            
        return True
