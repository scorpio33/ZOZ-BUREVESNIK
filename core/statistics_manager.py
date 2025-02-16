from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class StatisticsManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def record_task_completion(self, task_id: int, start_time: datetime, 
                                   end_time: datetime) -> bool:
        """Запись статистики выполнения задачи"""
        try:
            # Получаем данные задачи
            task = await self.db.fetch_one(
                "SELECT estimated_time FROM coordination_tasks WHERE task_id = ?",
                (task_id,)
            )
            
            if not task:
                return False
            
            # Вычисляем фактическое время выполнения
            completion_time = int((end_time - start_time).total_seconds() / 60)
            
            # Вычисляем отклонение от оценки
            deviation = completion_time - task['estimated_time'] if task['estimated_time'] else 0
            
            # Записываем статистику
            query = """
                INSERT INTO task_statistics 
                (task_id, completion_time, actual_start_time, actual_end_time, deviation_from_estimate)
                VALUES (?, ?, ?, ?, ?)
            """
            await self.db.execute_query(query, (
                task_id, completion_time, start_time, end_time, deviation
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error recording task completion: {e}")
            return False

    async def get_user_statistics(self, user_id: int, period: str = 'week') -> Dict:
        """Получение статистики пользователя"""
        try:
            period_start = self._get_period_start(period)
            
            query = """
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                    AVG(s.completion_time) as avg_completion_time,
                    AVG(ABS(s.deviation_from_estimate)) as avg_deviation
                FROM coordination_tasks t
                LEFT JOIN task_statistics s ON t.task_id = s.task_id
                WHERE t.assigned_to = ? AND t.created_at >= ?
            """
            
            stats = await self.db.fetch_one(query, (user_id, period_start))
            
            # Дополнительная статистика по приоритетам
            priority_stats = await self._get_priority_statistics(user_id, period_start)
            
            return {
                'general': stats,
                'priorities': priority_stats,
                'period': period
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return None

    async def _get_priority_statistics(self, user_id: int, period_start: datetime) -> List[Dict]:
        """Получение статистики по приоритетам"""
        query = """
            SELECT 
                priority_level,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM coordination_tasks
            WHERE assigned_to = ? AND created_at >= ?
            GROUP BY priority_level
            ORDER BY priority_level DESC
        """
        return await self.db.fetch_all(query, (user_id, period_start))

    def _get_period_start(self, period: str) -> datetime:
        """Получение начальной даты периода"""
        now = datetime.now()
        if period == 'week':
            return now - timedelta(days=7)
        elif period == 'month':
            return now - timedelta(days=30)
        elif period == 'year':
            return now - timedelta(days=365)
        return now