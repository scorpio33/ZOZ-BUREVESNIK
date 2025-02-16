import logging
import asyncio
from typing import Optional
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from core.states import States

logger = logging.getLogger(__name__)

class BotExtensions:
    """Дополнительные улучшения для бота"""
    
    def __init__(self, db_manager, auth_manager):
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        
        # Настройка логирования
        self._setup_logging()
    
    def _setup_logging(self):
        """Настройка расширенного логирования"""
        file_handler = logging.FileHandler('bot.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    
    async def handle_state_timeout(self, context: ContextTypes.DEFAULT_TYPE):
        """Обработка таймаутов состояний"""
        job = context.job
        if 'user_id' in job.data and 'state' in job.data:
            user_id = job.data['user_id']
            state = job.data['state']
            
            if state in [States.AWAITING_AUTH, States.VERIFICATION_START]:
                # Сброс состояния и уведомление пользователя
                if context.user_data.get(str(user_id)):
                    context.user_data[str(user_id)]['state'] = States.START
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="⚠️ Время сессии истекло. Пожалуйста, начните заново."
                    )
                    
                    # Логируем событие
                    logger.info(f"Session timeout for user {user_id}")
    
    async def check_services(self) -> bool:
        """Проверка доступности всех сервисов"""
        try:
            # Проверка соединения с базой данных
            self.db_manager.check_connection()
            
            # Проверка авторизации
            self.auth_manager.check_connection()
            
            # Проверка файловой системы
            self._check_required_directories()
            
            logger.info("All services are available")
            return True
            
        except Exception as e:
            logger.error(f"Service check failed: {e}")
            return False
    
    def _check_required_directories(self):
        """Проверка и создание необходимых директорий"""
        import os
        
        required_dirs = ['temp', 'logs', 'data']
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
    
    async def monitor_user_activity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Мониторинг активности пользователей"""
        try:
            user_id = update.effective_user.id
            current_time = datetime.now()
            
            # Обновляем время последней активности
            if not context.user_data.get(str(user_id)):
                context.user_data[str(user_id)] = {}
            
            context.user_data[str(user_id)]['last_activity'] = current_time
            
            # Проверяем длительные сессии
            self._check_long_sessions(context, user_id, current_time)
            
        except Exception as e:
            logger.error(f"Error in activity monitoring: {e}")
    
    def _check_long_sessions(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, current_time: datetime):
        """Проверка длительных сессий"""
        user_data = context.user_data.get(str(user_id), {})
        last_activity = user_data.get('last_activity')
        
        if last_activity:
            # Если сессия длится более 2 часов
            time_diff = (current_time - last_activity).total_seconds() / 3600
            if time_diff > 2:
                logger.warning(f"Long session detected for user {user_id}: {time_diff:.2f} hours")