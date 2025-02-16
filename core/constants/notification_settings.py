from enum import Enum
from typing import Dict, List

class NotificationChannel(Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    SMS = "sms"

class NotificationPreference:
    ENABLED = "enabled"
    DISABLED = "disabled"
    PRIORITY_ONLY = "priority_only"

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "channels": [NotificationChannel.TELEGRAM],
    "do_not_disturb": {
        "enabled": False,
        "start_time": "23:00",
        "end_time": "07:00"
    },
    "filters": {
        "urgent": NotificationPreference.ENABLED,
        "system": NotificationPreference.ENABLED,
        "status": NotificationPreference.ENABLED,
        "reminder": NotificationPreference.ENABLED,
        "info": NotificationPreference.ENABLED
    },
    "intervals": {
        "min_delay": 0,  # минимальная задержка между уведомлениями (в секундах)
        "batch_size": 5  # максимальное количество уведомлений в одном пакете
    }
}