from datetime import datetime, timedelta
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class NotificationMonitoring:
    def __init__(self, db_manager):
        self.db = db_manager

    async def log_notification(self, notification_id: int, user_id: int, 
                             notification_type: str, status: str, 
                             error_message: str = None):
        """Логирование уведомления"""
        try:
            await self.db.execute(
                """INSERT INTO notification_stats 
                   (notification_id, user_id, type, status, error_message, delivery_time) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (notification_id, user_id, notification_type, status, 
                 error_message, datetime.now())
            )
        except Exception as e:
            logger.error(f"Error logging notification: {e}")

    async def mark_as_read(self, notification_id: int):
        """Отметка уведомления как прочитанного"""
        try:
            await self.db.execute(
                """UPDATE notification_stats 
                   SET read_time = CURRENT_TIMESTAMP 
                   WHERE notification_id = ?""",
                (notification_id,)
            )
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")

    async def get_delivery_stats(self, period: str = 'day') -> Dict:
        """Получение статистики доставки"""
        periods = {
            'day': 1,
            'week': 7,
            'month': 30
        }
        days = periods.get(period, 1)
        
        query = """
            SELECT 
                type,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(CASE WHEN read_time IS NOT NULL 
                    THEN strftime('%s', read_time) - strftime('%s', delivery_time) 
                    ELSE NULL END) as avg_read_time
            FROM notification_stats
            WHERE created_at >= datetime('now', ?, 'localtime')
            GROUP BY type
        """
        
        try:
            stats = await self.db.fetch_all(query, (f'-{days} days',))
            return {row['type']: dict(row) for row in stats}
        except Exception as e:
            logger.error(f"Error getting delivery stats: {e}")
            return {}

    async def generate_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Генерация отчета о проблемах"""
        query = """
            SELECT 
                type,
                status,
                error_message,
                COUNT(*) as count
            FROM notification_stats
            WHERE created_at BETWEEN ? AND ?
                AND status = 'failed'
            GROUP BY type, status, error_message
            ORDER BY count DESC
        """
        
        try:
            failures = await self.db.fetch_all(query, (start_date, end_date))
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'failures': [dict(row) for row in failures]
            }
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {}