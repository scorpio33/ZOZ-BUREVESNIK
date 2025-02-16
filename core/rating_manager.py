from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RatingManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def update_rating(self, user_id: int, operation_data: Dict) -> bool:
        """Обновление рейтинга пользователя"""
        try:
            # Базовые очки за участие
            points = 10
            
            # Дополнительные очки за успешное завершение
            if operation_data.get('status') == 'successful':
                points += 20
            
            # Дополнительные очки за роль в операции
            if operation_data.get('role') == 'coordinator':
                points += 15
            elif operation_data.get('role') == 'team_leader':
                points += 10
                
            await self.db.execute_query("""
                INSERT INTO user_ratings (user_id, rating_points, total_operations)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                rating_points = rating_points + ?,
                total_operations = total_operations + 1,
                last_updated = CURRENT_TIMESTAMP
            """, (user_id, points, points))
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating rating: {e}")
            return False

    async def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Получение топ пользователей по рейтингу"""
        try:
            return await self.db.execute_query_fetchall("""
                SELECT u.username, u.full_name, r.rating_points, r.total_operations
                FROM user_ratings r
                JOIN users u ON r.user_id = u.user_id
                ORDER BY r.rating_points DESC
                LIMIT ?
            """, (limit,))
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            return []