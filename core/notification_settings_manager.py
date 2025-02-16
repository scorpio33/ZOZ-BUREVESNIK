from datetime import datetime, time
import json
import logging
from typing import Dict, List, Optional
from core.constants.notification_settings import DEFAULT_SETTINGS, NotificationChannel, NotificationPreference

logger = logging.getLogger(__name__)

class NotificationSettingsManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def get_user_settings(self, user_id: int) -> Dict:
        """Получение настроек пользователя"""
        settings = await self.db.fetch_one(
            "SELECT settings FROM notification_settings WHERE user_id = ?",
            (user_id,)
        )
        return json.loads(settings['settings']) if settings else DEFAULT_SETTINGS

    async def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """Обновление настроек пользователя"""
        try:
            await self.db.execute(
                """INSERT INTO notification_settings (user_id, settings) 
                   VALUES (?, ?) 
                   ON CONFLICT(user_id) DO UPDATE SET 
                   settings = ?, updated_at = CURRENT_TIMESTAMP""",
                (user_id, json.dumps(settings), json.dumps(settings))
            )
            return True
        except Exception as e:
            logger.error(f"Error updating settings for user {user_id}: {e}")
            return False

    async def set_do_not_disturb(self, user_id: int, enabled: bool, 
                                start_time: Optional[time] = None, 
                                end_time: Optional[time] = None) -> bool:
        """Установка режима "Не беспокоить"""
        try:
            await self.db.execute(
                """INSERT INTO do_not_disturb (user_id, enabled, start_time, end_time) 
                   VALUES (?, ?, ?, ?) 
                   ON CONFLICT(user_id) DO UPDATE SET 
                   enabled = ?, start_time = ?, end_time = ?, updated_at = CURRENT_TIMESTAMP""",
                (user_id, enabled, start_time, end_time, enabled, start_time, end_time)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting DND for user {user_id}: {e}")
            return False

    async def can_send_notification(self, user_id: int, notification_type: str) -> bool:
        """Проверка возможности отправки уведомления"""
        settings = await self.get_user_settings(user_id)
        
        # Проверка фильтров
        if settings['filters'].get(notification_type) == NotificationPreference.DISABLED:
            return False

        # Проверка режима "Не беспокоить"
        if settings['do_not_disturb']['enabled']:
            current_time = datetime.now().time()
            start_time = datetime.strptime(settings['do_not_disturb']['start_time'], '%H:%M').time()
            end_time = datetime.strptime(settings['do_not_disturb']['end_time'], '%H:%M').time()
            
            if start_time <= current_time <= end_time:
                return notification_type == 'urgent'  # Пропускаем только срочные уведомления

        return True