from typing import Dict, Optional
import json
from datetime import datetime

class HintManager:
    def __init__(self):
        self.hints = {
            'search_create': {
                'title': '🔍 Создание поиска',
                'text': 'Для создания поиска укажите:\n'
                       '1. Название поисковой операции\n'
                       '2. Описание и детали\n'
                       '3. Место сбора (можно отправить геопозицию)\n'
                       '4. Время начала',
                'show_once': False
            },
            'map_usage': {
                'title': '🗺 Работа с картой',
                'text': 'На карте вы можете:\n'
                       '• Отмечать точки интереса\n'
                       '• Рисовать сектора поиска\n'
                       '• Отслеживать перемещение группы',
                'show_once': True
            },
            'coordinator_tools': {
                'title': '👥 Инструменты координатора',
                'text': 'Доступные функции:\n'
                       '• Управление группами\n'
                       '• Распределение задач\n'
                       '• Мониторинг активности',
                'show_once': False
            }
        }
        self.user_hints = {}  # История показанных подсказок

    async def show_hint(self, user_id: int, 
                       hint_key: str, 
                       context: Optional[Dict] = None) -> Optional[str]:
        """Показ подсказки пользователю"""
        if hint_key not in self.hints:
            return None
            
        hint = self.hints[hint_key]
        
        # Проверяем, показывали ли уже эту подсказку
        if hint['show_once']:
            user_hints = self.user_hints.get(user_id, [])
            if hint_key in user_hints:
                return None
            
            self.user_hints[user_id] = user_hints + [hint_key]
            
        # Формируем текст подсказки
        hint_text = f"💡 {hint['title']}\n\n{hint['text']}"
        
        # Добавляем контекстную информацию
        if context:
            hint_text = hint_text.format(**context)
            
        return hint_text

    def reset_hints(self, user_id: int):
        """Сброс истории показанных подсказок"""
        self.user_hints[user_id] = []