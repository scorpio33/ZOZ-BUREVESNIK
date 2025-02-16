from database.database_manager import DatabaseManager

class AuthManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def close_all_connections(self):
        """Close all database connections"""
        # This method is needed for test cleanup
        pass
