class LocationPermissionManager:
    def __init__(self):
        self.permissions = {}

    async def grant_permission(self, user_id: int) -> bool:
        """Grant location permission to a user"""
        self.permissions[user_id] = True
        return True

    async def check_permission(self, user_id: int) -> bool:
        """Check if user has location permission"""
        return self.permissions.get(user_id, False)
