from database.db_manager import DatabaseManager
from core.notification_manager import NotificationManager

class CoordinationManager:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager

    async def initialize(self):
        pass
