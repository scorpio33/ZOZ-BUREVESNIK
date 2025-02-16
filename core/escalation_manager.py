from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EscalationManager:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification_manager = notification_manager
        self.escalation_levels = {
            1: "Повышенное внимание",
            2: "Срочное вмешательство",
            3: "Критическая ситуация"
        }

    async def check_pending_escalations(self, context):
        """Периодическая проверка задач на необходимость эскалации"""
        try:
            tasks = await self.db.get_pending_tasks()
            for task in tasks:
                await self._check_task_escalation(task)
        except Exception as e:
            logger.error(f"Error in escalation check: {e}")
    
    async def _check_task_escalation(self, task):
        """Проверка необходимости эскалации для конкретной задачи"""
        current_time = datetime.now()
        deadline = datetime.fromisoformat(task['deadline'])
        time_left = deadline - current_time
        
        if time_left < timedelta(hours=1) and task['status'] != 'completed':
            await self._escalate_task(task['task_id'], 3)
        elif time_left < timedelta(hours=3) and task['status'] != 'completed':
            await self._escalate_task(task['task_id'], 2)
    
    async def _escalate_task(self, task_id: int, level: int):
        """Эскалация задачи"""
        await self.db.create_escalation(task_id, level)
        task = await self.db.get_task(task_id)
        
        # Уведомляем координаторов
        message = (
            f"⚠️ Эскалация задачи #{task_id}\n"
            f"Уровень: {level}\n"
            f"Название: {task['title']}\n"
            f"Срочность: {'‼️' * level}"
        )
        await self.notification_manager.notify_coordinators(message)
