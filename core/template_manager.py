from typing import List, Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def create_template(self, data: Dict) -> Optional[int]:
        """Создание нового шаблона задачи"""
        try:
            query = """
                INSERT INTO task_templates 
                (title, description, priority_level, estimated_time, category, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            template_id = await self.db.execute_query(
                query,
                (
                    data['title'],
                    data['description'],
                    data.get('priority_level', 1),
                    data.get('estimated_time'),
                    data.get('category'),
                    data['created_by']
                ),
                return_id=True
            )
            return template_id
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return None

    async def get_templates(self, category: str = None) -> List[Dict]:
        """Получение списка шаблонов"""
        try:
            query = """
                SELECT t.*, u.username as creator_name
                FROM task_templates t
                JOIN users u ON t.created_by = u.user_id
            """
            params = []
            
            if category:
                query += " WHERE t.category = ?"
                params.append(category)
                
            query += " ORDER BY t.created_at DESC"
            
            return await self.db.fetch_all(query, tuple(params))
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            return []

    async def create_task_from_template(self, template_id: int, data: Dict) -> Optional[int]:
        """Создание задачи из шаблона"""
        try:
            # Получаем шаблон
            template = await self.db.fetch_one(
                "SELECT * FROM task_templates WHERE template_id = ?",
                (template_id,)
            )
            
            if not template:
                return None
            
            # Создаем задачу на основе шаблона
            task_data = {
                'title': template['title'],
                'description': template['description'],
                'priority_level': template['priority_level'],
                'estimated_time': template['estimated_time'],
                **data  # Дополнительные данные для конкретной задачи
            }
            
            return await self.db.create_task(task_data)
        except Exception as e:
            logger.error(f"Error creating task from template: {e}")
            return None