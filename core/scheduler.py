from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self, task_service):
        self.scheduler = AsyncIOScheduler()
        self.task_service = task_service

    def start(self):
        """Запуск планировщика"""
        # Проверка напоминаний каждые 5 минут
        self.scheduler.add_job(
            self.task_service.check_reminders,
            trigger=IntervalTrigger(minutes=5),
            id='check_reminders',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Task scheduler started")

    def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Task scheduler stopped")