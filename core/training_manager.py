from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TrainingManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def get_available_courses(self, user_id: int, level: int) -> List[Dict]:
        """Получение доступных курсов для пользователя"""
        try:
            return await self.db.fetch_all("""
                SELECT * FROM training_materials 
                WHERE required_level <= ? 
                AND id NOT IN (
                    SELECT material_id FROM user_training_progress 
                    WHERE user_id = ? AND completed = 1
                )
                ORDER BY required_level ASC
            """, (level, user_id))
        except Exception as e:
            logger.error(f"Error getting available courses: {e}")
            return []

    async def complete_course(self, user_id: int, material_id: int, score: int) -> bool:
        """Отметка о завершении курса"""
        try:
            await self.db.execute_query("""
                INSERT INTO user_training_progress 
                (user_id, material_id, score)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, material_id) DO UPDATE SET
                score = ?,
                completed_at = CURRENT_TIMESTAMP
            """, (user_id, material_id, score, score))
            return True
        except Exception as e:
            logger.error(f"Error completing course: {e}")
            return False

    async def get_course_progress(self, user_id: int) -> Dict:
        """Получение прогресса обучения пользователя"""
        try:
            return await self.db.fetch_one("""
                SELECT 
                    COUNT(CASE WHEN completed = 1 THEN 1 END) as completed_courses,
                    COUNT(*) as total_courses,
                    AVG(score) as avg_score
                FROM user_training_progress
                WHERE user_id = ?
            """, (user_id,))
        except Exception as e:
            logger.error(f"Error getting course progress: {e}")
            return None
