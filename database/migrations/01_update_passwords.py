from database.auth_manager import AuthManager
from utils.password_utils import PasswordUtils

def migrate_passwords():
    """Миграция существующих паролей на новую систему хеширования"""
    auth_manager = AuthManager('bot_database.db')
    pwd_utils = PasswordUtils()
    
    with auth_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # Получаем всех пользователей
        cursor.execute("SELECT user_id, password_hash FROM users")
        users = cursor.fetchall()
        
        for user_id, old_hash in users:
            # Генерируем новый хеш и соль для существующего пароля
            new_hash, salt = pwd_utils.hash_password(old_hash)
            
            # Обновляем запись в базе
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, salt = ? 
                WHERE user_id = ?
            """, (new_hash, salt, user_id))
            
        conn.commit()

if __name__ == "__main__":
    migrate_passwords()