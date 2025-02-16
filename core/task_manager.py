from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self, db_manager, notification_manager):
        self.db_manager = db_manager
        self.notification_manager = notification_manager

    async def create_task(self, task_data: dict) -> Optional[int]:
        """Create a new task"""
        try:
            query = """
                INSERT INTO tasks (operation_id, title, description, status, assigned_to)
                VALUES (?, ?, ?, ?, ?)
                RETURNING task_id
            """
            params = (
                task_data.get('operation_id'),
                task_data.get('title'),
                task_data.get('description'),
                task_data.get('status', 'pending'),
                task_data.get('assigned_to')
            )
            
            result = await self.db_manager.fetch_one(query, params)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def assign_task(self, task_id: int, user_id: int) -> bool:
        """Assign task to user"""
        try:
            await self.db_manager.execute(
                "UPDATE tasks SET assigned_to = ?, status = 'assigned' WHERE task_id = ?",
                (user_id, task_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return False

    async def get_task(self, task_id: int) -> Optional[Dict]:
        """Get task by ID"""
        try:
            result = await self.db_manager.fetch_one(
                "SELECT * FROM tasks WHERE task_id = ?",
                (task_id,)
            )
            if result:
                return {
                    'task_id': result[0],
                    'operation_id': result[1],
                    'title': result[2],
                    'description': result[3],
                    'status': result[4],
                    'assigned_to': result[5]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return None
