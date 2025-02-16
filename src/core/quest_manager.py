from typing import Dict, List
from src.core.database import DatabaseManager

class QuestManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_quest(self, title: str, description: str, rewards: dict):
        """Создание нового квеста"""
        pass

    async def complete_quest(self, quest_id: int, user_id: int):
        """Выполнение квеста пользователем"""
        pass

    async def get_available_quests(self, user_id: int):
        """Получение списка доступных квестов"""
        pass
