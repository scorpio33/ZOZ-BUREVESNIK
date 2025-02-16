from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class TaskManagementService:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification_manager = notification_manager
        
    async def create_task(self, data: Dict) -> Optional[int]:
        """Создание новой задачи"""
        try:
            if data.get('template_id'):
                template = await self.db.get_task_template(data['template_id'])
                if template:
                    data = {**template, **data}  # Применяем шаблон с возможностью переопределения
            
            task_id = await self.db.execute_query_fetchone("""
                INSERT INTO coordination_tasks (
                    operation_id, group_id, creator_id, title, description,
                    priority_level, deadline, estimated_time, template_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING task_id
            """, (
                data['operation_id'],
                data.get('group_id'),
                data['creator_id'],
                data['title'],
                data.get('description', ''),
                data.get('priority_level', 2),
                data.get('deadline'),
                data.get('estimated_time'),
                data.get('template_id')
            ))
            
            if task_id and data.get('deadline'):
                await self._create_reminders(task_id, data['deadline'])
            
            return task_id
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def _create_reminders(self, task_id: int, deadline: datetime) -> None:
        """Создание напоминаний для задачи"""
        reminders = [
            (deadline - timedelta(hours=24), 'before_deadline', '⚠️ Задача должна быть выполнена через 24 часа'),
            (deadline - timedelta(hours=2), 'before_deadline', '⚠️ Срочно! Осталось 2 часа'),
            (deadline - timedelta(minutes=30), 'before_deadline', '🚨 Критично! Осталось 30 минут')
        ]
        
        for reminder_time, reminder_type, reminder_text in reminders:
            await self.db.execute_query("""
                INSERT INTO task_reminders (task_id, reminder_time, reminder_type, reminder_text)
                VALUES (?, ?, ?, ?)
            """, (task_id, reminder_time, reminder_type, reminder_text))

    async def check_reminders(self) -> None:
        """Проверка и отправка напоминаний"""
        reminders = await self.db.execute_query_fetchall("""
            SELECT r.*, t.assigned_to, t.title
            FROM task_reminders r
            JOIN coordination_tasks t ON r.task_id = t.task_id
            WHERE r.is_sent = FALSE AND r.reminder_time <= CURRENT_TIMESTAMP
        """)
        
        for reminder in reminders:
            if reminder['assigned_to']:
                await self.notification_manager.send_notification(
                    reminder['assigned_to'],
                    f"{reminder['reminder_text']}\n"
                    f"Задача: {reminder['title']}"
                )
                
            await self.db.execute_query(
                "UPDATE task_reminders SET is_sent = TRUE WHERE reminder_id = ?",
                (reminder['reminder_id'],)
            )

    async def create_task_template(self, data: Dict) -> Optional[int]:
        """Создание шаблона задачи"""
        try:
            return await self.db.execute_query_fetchone("""
                INSERT INTO task_templates (
                    title, description, priority_level, estimated_time,
                    category, created_by
                ) VALUES (?, ?, ?, ?, ?, ?)
                RETURNING template_id
            """, (
                data['title'],
                data.get('description', ''),
                data.get('priority_level', 2),
                data.get('estimated_time'),
                data.get('category'),
                data['created_by']
            ))
        except Exception as e:
            logger.error(f"Error creating task template: {e}")
            return None