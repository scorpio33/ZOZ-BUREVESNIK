import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from telegram import Bot
import logging
from core.constants.notification_types import NotificationType, NOTIFICATION_EMOJI, NOTIFICATION_PRIORITIES

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, bot: Bot, db_manager):
        self.bot = bot
        self.db = db_manager
        self.queue_manager = NotificationQueueManager(self, db_manager)

    async def start(self):
        """Запуск менеджера уведомлений"""
        await self.queue_manager.start()

    async def stop(self):
        """Остановка менеджера уведомлений"""
        await self.queue_manager.stop()

    async def send_notification(self, user_id: int, message: str, 
                              priority: int = 2,
                              scheduled_time: Optional[datetime] = None) -> None:
        """Отправка уведомления через очередь"""
        await self.queue_manager.add_notification(
            user_id, message, priority, scheduled_time
        )

    async def notify_group(self, group_id: int, message: str, 
                          priority: int = 2,
                          exclude_user_id: Optional[int] = None) -> None:
        """Отправка уведомления группе через очередь"""
        await self.queue_manager.add_group_notification(
            group_id, message, priority, exclude_user_id
        )

    async def send_urgent_message(self, user_id: int, message: str):
        """Отправка срочного сообщения"""
        formatted_message = self._format_message(message, NotificationType.URGENT)
        await self.queue_manager.add_notification(
            user_id=user_id,
            message=formatted_message,
            priority=NOTIFICATION_PRIORITIES[NotificationType.URGENT],
            notification_type=NotificationType.URGENT
        )

    async def send_system_alert(self, user_id: int, message: str):
        """Отправка системного оповещения"""
        formatted_message = self._format_message(message, NotificationType.SYSTEM)
        await self.queue_manager.add_notification(
            user_id=user_id,
            message=formatted_message,
            priority=NOTIFICATION_PRIORITIES[NotificationType.SYSTEM],
            notification_type=NotificationType.SYSTEM
        )

    async def send_status_update(self, user_id: int, message: str):
        """Отправка статусного обновления"""
        formatted_message = self._format_message(message, NotificationType.STATUS)
        await self.queue_manager.add_notification(
            user_id=user_id,
            message=formatted_message,
            priority=NOTIFICATION_PRIORITIES[NotificationType.STATUS],
            notification_type=NotificationType.STATUS
        )

    async def set_reminder(self, user_id: int, message: str, remind_at: datetime):
        """Установка напоминания"""
        formatted_message = self._format_message(message, NotificationType.REMINDER)
        await self.queue_manager.add_notification(
            user_id=user_id,
            message=formatted_message,
            priority=NOTIFICATION_PRIORITIES[NotificationType.REMINDER],
            notification_type=NotificationType.REMINDER,
            scheduled_time=remind_at
        )

    async def send_info_message(self, user_id: int, message: str):
        """Отправка информационного сообщения"""
        formatted_message = self._format_message(message, NotificationType.INFO)
        await self.queue_manager.add_notification(
            user_id=user_id,
            message=formatted_message,
            priority=NOTIFICATION_PRIORITIES[NotificationType.INFO],
            notification_type=NotificationType.INFO
        )

    def _format_message(self, message: str, notification_type: NotificationType) -> str:
        """Форматирование сообщения в зависимости от типа"""
        emoji = NOTIFICATION_EMOJI[notification_type]
        return f"{emoji} {message}"

    async def send_group_status_update(self, group_id: int, message: str):
        """Отправка статусного обновления группе"""
        formatted_message = self._format_message(message, NotificationType.STATUS)
        await self.queue_manager.add_group_notification(
            group_id=group_id,
            message=formatted_message,
            priority=NOTIFICATION_PRIORITIES[NotificationType.STATUS],
            notification_type=NotificationType.STATUS
        )

    async def notify_location_update(self, group_id: int, user_id: int, 
                                   location: Dict) -> None:
        """Уведомление об обновлении местоположения участника"""
        try:
            user = await self.db.get_user(user_id)
            message = (
                f"📍 Обновление местоположения\n"
                f"Участник: {user['username'] or user['full_name']}\n"
                f"Координаты: {location['latitude']}, {location['longitude']}"
            )
            await self.notify_group(group_id, message, exclude_user_id=user_id)
        except Exception as e:
            logger.error(f"Error in location notification: {e}")

    async def notify_status_change(self, group_id: int, user_id: int, 
                                 new_status: str) -> None:
        """Уведомление об изменении статуса участника"""
        try:
            user = await self.db.get_user(user_id)
            status_emoji = {
                'active': '🟢',
                'resting': '🟡',
                'inactive': '🔴',
                'sos': '🆘'
            }
            
            message = (
                f"{status_emoji.get(new_status, '❓')} Изменение статуса\n"
                f"Участник: {user['username'] or user['full_name']}\n"
                f"Новый статус: {new_status}"
            )
            await self.notify_group(group_id, message)
        except Exception as e:
            logger.error(f"Error in status notification: {e}")
