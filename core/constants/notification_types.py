from enum import Enum

class NotificationType(Enum):
    URGENT = "urgent"         # Срочные сообщения
    SYSTEM = "system"         # Системные оповещения
    STATUS = "status"         # Статусные обновления
    REMINDER = "reminder"     # Напоминания
    INFO = "info"            # Информационные сообщения

# Эмодзи для каждого типа уведомления
NOTIFICATION_EMOJI = {
    NotificationType.URGENT: "🚨",
    NotificationType.SYSTEM: "⚙️",
    NotificationType.STATUS: "📊",
    NotificationType.REMINDER: "⏰",
    NotificationType.INFO: "ℹ️"
}

# Приоритеты по умолчанию для каждого типа
NOTIFICATION_PRIORITIES = {
    NotificationType.URGENT: 1,    # Высший приоритет
    NotificationType.SYSTEM: 2,    # Средний приоритет
    NotificationType.STATUS: 2,    # Средний приоритет
    NotificationType.REMINDER: 3,  # Низкий приоритет
    NotificationType.INFO: 3       # Низкий приоритет
}