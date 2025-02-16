from src.core.database import DatabaseManager

class TaskManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_task(self, title: str, description: str, assigned_to: int):
        """Создание новой задачи"""
        pass

    async def complete_task(self, task_id: int):
        """Отметка задачи как выполненной"""
        pass

    async def get_user_tasks(self, user_id: int):
        """Получение списка задач пользователя"""
        pass
