class AuthHandler:
    def __init__(self, db_manager, notification_manager):
        self.db_manager = db_manager
        self.notification_manager = notification_manager

    async def register_user(self, user_id: int, password: str) -> bool:
        """Register new user"""
        try:
            password_hash = self._hash_password(password)
            await self.db_manager.execute(
                "INSERT INTO users (user_id, password_hash) VALUES (?, ?)",
                (user_id, password_hash)
            )
            return True
        except Exception:
            return False

    def _hash_password(self, password: str) -> str:
        """Hash password using secure method"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()