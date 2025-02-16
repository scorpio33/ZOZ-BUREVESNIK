from typing import List, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AchievementManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def check_achievements(self, user_id: int, action: str, data: Dict = None) -> List[Dict]:
        """Проверка и выдача достижений"""
        try:
            earned_achievements = []
            
            if action == 'operation_completed':
                # Проверяем достижения связанные с операциями
                earned = await self._check_operation_achievements(user_id, data)
                earned_achievements.extend(earned)
            
            elif action == 'training_completed':
                # Проверяем достижения связанные с обучением
                earned = await self._check_training_achievements(user_id, data)
                earned_achievements.extend(earned)
            
            # Выдаём заработанные достижения
            for achievement in earned_achievements:
                await self.grant_achievement(user_id, achievement['achievement_id'])
            
            return earned_achievements
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []

    async def grant_achievement(self, user_id: int, achievement_id: int) -> bool:
        """Выдача достижения пользователю"""
        try:
            await self.db.execute_query("""
                INSERT OR IGNORE INTO user_achievements (user_id, achievement_id)
                VALUES (?, ?)
            """, (user_id, achievement_id))
            return True
        except Exception as e:
            logger.error(f"Error granting achievement: {e}")
            return False

    async def get_user_achievements(self, user_id: int) -> List[Dict]:
        """Получение списка достижений пользователя"""
        try:
            return await self.db.execute_query_fetchall("""
                SELECT a.*, ua.earned_at
                FROM achievements a
                JOIN user_achievements ua ON a.achievement_id = ua.achievement_id
                WHERE ua.user_id = ?
                ORDER BY ua.earned_at DESC
            """, (user_id,))
        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return []