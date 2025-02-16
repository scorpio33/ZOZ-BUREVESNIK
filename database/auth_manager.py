from datetime import datetime, timedelta
from typing import Optional, Dict, List
import sqlite3
from utils.password_utils import PasswordUtils

class AuthManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._connections = set()
        self.pwd_utils = PasswordUtils()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        self._connections.add(conn)
        return conn

    def close_all_connections(self):
        """Закрывает все открытые соединения с базой данных"""
        for conn in self._connections:
            try:
                conn.close()
            except Exception:
                pass
        self._connections.clear()

    def register_user(self, user_id: int, password: str) -> bool:
        """Register a new user with password"""
        try:
            password_hash, salt = self.pwd_utils.hash_password(password)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (user_id, password_hash, salt)
                    VALUES (?, ?, ?)
                    """,
                    (user_id, password_hash, salt)
                )
                conn.commit()
                return True
        except Exception:
            return False

    def verify_user(self, user_id: int, password: str) -> bool:
        """Проверка пароля пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT password_hash, salt FROM users 
                WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            stored_hash, stored_salt = result
            return self.pwd_utils.verify_password(stored_hash, stored_salt, password)

    def update_password(self, user_id: int, new_password: str) -> bool:
        """Обновление пароля"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash, salt = self.pwd_utils.hash_password(new_password)
            cursor.execute("""
                UPDATE users SET password_hash = ?, salt = ? WHERE user_id = ?
            """, (password_hash, salt, user_id))
            return cursor.rowcount > 0

    def create_recovery_code(self, user_id: int) -> Optional[str]:
        """Создание кода восстановления"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            recovery_code = self.pwd_utils.generate_recovery_code()
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            cursor.execute("""
                INSERT OR REPLACE INTO password_recovery 
                (user_id, recovery_code, expires_at, attempts)
                VALUES (?, ?, ?, 0)
            """, (user_id, recovery_code, expires_at))
            
            return recovery_code if cursor.rowcount > 0 else None

    def verify_recovery_code(self, user_id: int, code: str) -> bool:
        """Проверка кода восстановления"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT recovery_code, expires_at, attempts 
                FROM password_recovery 
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
                
            stored_code, expires_at, attempts = result
            
            if attempts >= 3 or datetime.utcnow() > datetime.fromisoformat(expires_at):
                return False
                
            if stored_code != code:
                cursor.execute("""
                    UPDATE password_recovery 
                    SET attempts = attempts + 1 
                    WHERE user_id = ?
                """, (user_id,))
                return False
                
            return True
