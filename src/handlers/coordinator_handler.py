from telegram import Update
from telegram.ext import ContextTypes
from src.core.database import DatabaseManager
from src.core.notification_manager import NotificationManager
import logging

class CoordinatorHandler:
    def __init__(self, db: DatabaseManager, notification_manager: NotificationManager):
        self.db = db
        self.notification_manager = notification_manager
        self._logger = logging.getLogger(__name__)

    async def handle_coordinator_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка заявки на получение статуса координатора"""
        user_id = update.effective_user.id
        
        # Проверяем, не подавал ли пользователь заявку ранее
        existing_request = await self.db.fetchrow(
            "SELECT * FROM coordinator_requests WHERE user_id = $1 AND status = 'pending'",
            user_id
        )
        
        if existing_request:
            await update.message.reply_text(
                "У вас уже есть активная заявка на получение статуса координатора. "
                "Пожалуйста, дождитесь её рассмотрения."
            )
            return

        # Начинаем процесс подачи заявки
        await update.message.reply_text(
            "Для получения статуса координатора, пожалуйста, ответьте на следующие вопросы:\n"
            "1. Ваше полное ФИО:"
        )
        context.user_data['coordinator_request'] = {'step': 1}

    async def process_coordinator_request_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка шагов заполнения заявки"""
        user_data = context.user_data.get('coordinator_request', {})
        step = user_data.get('step', 1)
        
        if step == 1:
            user_data['full_name'] = update.message.text
            await update.message.reply_text("2. Укажите вашу область и город:")
            user_data['step'] = 2
        elif step == 2:
            user_data['region'] = update.message.text
            await update.message.reply_text("3. Укажите номер телефона для связи:")
            user_data['step'] = 3
        # ... остальные шаги ...

        context.user_data['coordinator_request'] = user_data

    async def approve_coordinator_request(self, request_id: int):
        """Одобрение заявки на статус координатора"""
        try:
            # Обновляем статус заявки
            await self.db.execute(
                "UPDATE coordinator_requests SET status = 'approved' WHERE request_id = $1",
                request_id
            )
            
            # Получаем информацию о заявке
            request = await self.db.fetchrow(
                "SELECT user_id FROM coordinator_requests WHERE request_id = $1",
                request_id
            )
            
            if request:
                # Обновляем статус пользователя
                await self.db.execute(
                    "UPDATE users SET status = 'coordinator' WHERE user_id = $1",
                    request['user_id']
                )
                
                # Отправляем уведомление
                await self.notification_manager.notify_coordinator_request_status(
                    request['user_id'],
                    approved=True
                )
                
            return True
        except Exception as e:
            self._logger.error(f"Error approving coordinator request: {e}")
            return False

    async def reject_coordinator_request(self, request_id: int):
        """Отклонение заявки на статус координатора"""
        try:
            # Обновляем статус заявки
            await self.db.execute(
                "UPDATE coordinator_requests SET status = 'rejected' WHERE request_id = $1",
                request_id
            )
            
            # Получаем информацию о заявке
            request = await self.db.fetchrow(
                "SELECT user_id FROM coordinator_requests WHERE request_id = $1",
                request_id
            )
            
            if request:
                # Отправляем уведомление
                await self.notification_manager.notify_coordinator_request_status(
                    request['user_id'],
                    approved=False
                )
                
            return True
        except Exception as e:
            self._logger.error(f"Error rejecting coordinator request: {e}")
            return False
