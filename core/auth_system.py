class AuthSystem:
    def __init__(self):
        self._authorized_users = set()
        
    async def initialize(self):
        """Initialize the authentication system"""
        pass
        
    async def authenticate(self, user_id: int, password: str) -> bool:
        """Authenticate a user with password"""
        # TODO: Implement actual password verification
        if password == "test_password":  # For testing purposes
            self._authorized_users.add(user_id)
            return True
        return False
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return user_id in self._authorized_users
    
    async def logout(self, user_id: int):
        """Log out a user"""
        self._authorized_users.discard(user_id)