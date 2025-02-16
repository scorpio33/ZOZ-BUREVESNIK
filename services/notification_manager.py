import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, bot: Bot, db_manager):
        self.bot = bot
        self.db = db_manager
        self.notification_queue = asyncio.Queue()
        self.notification_levels = {
            'info': '📝',
            'warning': '⚠️',
            'critical': '🚨',
            'success': '✅'
        }

    async def start(self):
        """Запуск обработчика очереди уведомлений"""
        asyncio.create_task(self._process_queue())

    async def stop(self):
        """Остановка менеджера уведомлений"""
        # Здесь можно добавить логику остановки обработчика
        pass

    async def _process_queue(self):
        """Обработка очереди уведомлений"""
        while True:
            try:
                notification = await self.notification_queue.get()
                await self._send_notification(notification)
                await asyncio.sleep(0.1)  # Небольшая задержка между отправками
            except Exception as e:
                logger.error(f"Error processing notification: {e}")

    async def _send_notification(self, notification: dict):
        """Отправка уведомления"""
        try:
            emoji = self.notification_levels.get(notification['level'], '📝')
            message = f"{emoji} {notification['message']}"
            
            keyboard = None
            if notification.get('buttons'):
                keyboard = InlineKeyboardMarkup(notification['buttons'])
            
            await self.bot.send_message(
                chat_id=notification['user_id'],
                text=message,
                parse_mode='HTML',
                reply_markup=keyboard
            )
            
            # Сохраняем в БД
            await self.db.create_notification(
                user_id=notification['user_id'],
                message=notification['message'],
                level=notification['level'],
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    async def notify_user(self, user_id: int, message: str, 
                         level: str = 'info',
                         buttons: List[List[InlineKeyboardButton]] = None):
        """Добавление уведомления в очередь"""
        await self.notification_queue.put({
            'user_id': user_id,
            'message': message,
            'level': level,
            'buttons': buttons
        })

    async def notify_group(self, group_id: int, message: str,
                          level: str = 'info',
                          exclude_user_id: Optional[int] = None):
        """Отправка уведомления всем участникам группы"""
        try:
            users = await self.db.get_group_users(group_id)
            for user in users:
                if user['user_id'] != exclude_user_id:
                    await self.notify_user(user['user_id'], message, level)
        except Exception as e:
            logger.error(f"Error sending group notification: {e}")

    async def notify_coordinators(self, message: str, level: str = 'info'):
        """Отправка уведомления всем координаторам"""
        try:
            coordinators = await self.db.get_coordinators()
            for coord in coordinators:
                await self.notify_user(coord['user_id'], message, level)
        except Exception as e:
            logger.error(f"Error sending coordinator notification: {e}")