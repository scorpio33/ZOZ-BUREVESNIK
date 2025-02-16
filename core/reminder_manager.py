from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class ReminderManager:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification_manager = notification_manager
        self.active_reminders = {}
        self.check_interval = 60  # секунды

    async def start(self):
        """Запуск менеджера напоминаний"""
        asyncio.create_task(self._reminder_checker())

    async def _reminder_checker(self):
        """Периодическая проверка напоминаний"""
        while True:
            try:
                current_time = datetime.now()
                reminders = await self._get_pending_reminders(current_time)
                
                for reminder in reminders:
                    await self._process_reminder(reminder)
                    
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in reminder checker: {e}")
                await asyncio.sleep(self.check_interval)

    async def create_reminder(self, task_id: int, user_id: int, reminder_time: datetime, 
                            reminder_type: str = 'custom') -> Optional[int]:
        """Создание нового напоминания"""
        try:
            query = """
                INSERT INTO task_reminders (task_id, user_id, reminder_time, reminder_type)
                VALUES (?, ?, ?, ?)
            """
            reminder_id = await self.db.execute_query(
                query, 
                (task_id, user_id, reminder_time, reminder_type),
                return_id=True
            )
            return reminder_id
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            return None

    async def _get_pending_reminders(self, current_time: datetime) -> List[Dict]:
        """Получение всех непосланных напоминаний"""
        query = """
            SELECT r.*, t.title, t.description
            FROM task_reminders r
            JOIN coordination_tasks t ON r.task_id = t.task_id
            WHERE r.is_sent = FALSE AND r.reminder_time <= ?
        """
        return await self.db.fetch_all(query, (current_time,))

    async def _process_reminder(self, reminder: Dict):
        """Обработка напоминания"""
        try:
            # Отправляем уведомление
            message = self._format_reminder_message(reminder)
            await self.notification_manager.send_notification(
                reminder['user_id'],
                message
            )
            
            # Отмечаем напоминание как отправленное
            await self.db.execute_query(
                "UPDATE task_reminders SET is_sent = TRUE WHERE reminder_id = ?",
                (reminder['reminder_id'],)
            )
        except Exception as e:
            logger.error(f"Error processing reminder {reminder['reminder_id']}: {e}")

    def _format_reminder_message(self, reminder: Dict) -> str:
        """Форматирование сообщения напоминания"""
        return (
            f"⏰ Напоминание о задаче!\n\n"
            f"📋 {reminder['title']}\n"
            f"📝 {reminder['description']}\n\n"
            f"Время: {reminder['reminder_time'].strftime('%H:%M %d.%m.%Y')}"
        )