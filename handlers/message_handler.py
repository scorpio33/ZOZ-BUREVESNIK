import logging
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import DEVELOPER_ID

logger = logging.getLogger(__name__)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовых сообщений
    """
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Логируем входящее сообщение
    logger.info(f"Received message from user {user_id}: {message_text}")
    
    # Проверяем, находится ли пользователь в каком-либо состоянии
    user_state = context.user_data.get('state')
    
    if user_state:
        # Если пользователь находится в определенном состоянии,
        # передаем управление соответствующему обработчику
        await handle_state_message(update, context, user_state)
    else:
        # Если пользователь не в состоянии, обрабатываем как обычное сообщение
        await handle_regular_message(update, context)

async def handle_state_message(update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
    """
    Обработка сообщений в зависимости от состояния пользователя
    """
    message_text = update.message.text
    
    if state == 'AWAITING_PASSWORD':
        # Обработка ввода пароля
        await handle_password_input(update, context, message_text)
    elif state == 'AWAITING_LOCATION_NAME':
        # Обработка ввода названия локации
        await handle_location_name(update, context, message_text)
    # Добавьте другие состояния по мере необходимости

async def handle_regular_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка обычных сообщений (не в состоянии)
    """
    message_text = update.message.text
    user_id = update.effective_user.id
    
    # Пример обработки специальных команд для разработчика
    if user_id == DEVELOPER_ID:
        if message_text.startswith('/debug'):
            await handle_debug_command(update, context)
            return
    
    # По умолчанию отправляем сообщение о том, как использовать бота
    await update.message.reply_text(
        "Используйте команду /start для начала работы с ботом или /help для получения справки."
    )

async def handle_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE, password: str):
    """
    Обработка ввода пароля
    """
    # Здесь будет логика проверки пароля
    pass

async def handle_location_name(update: Update, context: ContextTypes.DEFAULT_TYPE, location_name: str):
    """
    Обработка ввода названия локации
    """
    # Здесь будет логика обработки названия локации
    pass

async def handle_debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка отладочных команд для разработчика
    """
    # Здесь будет логика отладки
    await update.message.reply_text("Debug mode activated")