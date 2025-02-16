import logging
from src.core.database import DatabaseManager
from telegram import Bot

class NotificationManager:
    def __init__(self, db: DatabaseManager, bot: Bot = None):
        self.db = db
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    async def send_notification(self, user_id: int, message: str) -> bool:
        """Отправка уведомления пользователю"""
        try:
            if self.bot:
                await self.bot.send_message(chat_id=user_id, text=message)
            return True
        except Exception as e:
            self._logger.error(f"Failed to send notification: {e}")
            return False

    async def notify_coordinator_request_status(self, user_id: int, approved: bool):
        """Уведомление о статусе заявки на координатора"""
        if approved:
            message = (
                "🎉 Поздравляем! Ваша заявка на статус Координатора одобрена!\n\n"
                "📝 Правила и ответственность Координатора:\n"
                "1. Вы несете ответственность за организацию и успешное завершение поисковых операций.\n"
                "2. Создавайте новые группы только после тщательной подготовки.\n"
                "3. Поддерживайте связь со всеми участниками группы.\n"
                "4. Регулярно отправляйте отчеты о проделанной работе.\n\n"
                "⚠️ Это большая ответственность. Мы уверены, что вы справитесь!"
            )
        else:
            message = (
                "😕 К сожалению, ваша заявка на статус Координатора отклонена.\n\n"
                "⚠️ Получение статуса Координатора требует опыта работы в поисково-спасательных операциях.\n"
                "Мы рекомендуем вам продолжить участие в поисках и набраться опыта.\n\n"
                "Спасибо за вашу активность и поддержку проекта! 🚑🔍"
            )
        
        await self.send_notification(user_id, message)
