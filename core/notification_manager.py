import logging
from datetime import datetime
from database.db_manager import DatabaseManager

class NotificationManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def send_notification(self, user_id: int, message: str, notification_type: str = 'info') -> bool:
        """Send notification to user"""
        try:
            query = """
                INSERT INTO notifications (user_id, message, type, created_at)
                VALUES (?, ?, ?, ?)
            """
            await self.db.conn.execute(query, (user_id, message, notification_type, datetime.now()))
            await self.db.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error sending notification: {e}")
            return False

    async def get_user_notifications(self, user_id: int, limit: int = 10) -> list:
        """Get user's notifications"""
        try:
            query = """
                SELECT * FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """
            cursor = await self.db.conn.execute(query, (user_id, limit))
            return await cursor.fetchall()
        except Exception as e:
            logging.error(f"Error getting notifications: {e}")
            return []
