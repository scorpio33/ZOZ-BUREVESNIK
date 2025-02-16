import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Состояния разговора
(
    START,
    AUTH,
    MAIN_MENU,
    HELP_PROJECT,
    ABOUT,
    SEARCH,
    SETTINGS,
    MAP,
    COORDINATOR_REQUEST
) = range(9)

class Bot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        self.developer_id = int(os.getenv('DEVELOPER_ID', 991426127))
        self.developer_code = os.getenv('DEVELOPER_CODE', 'TRAMP708090')
        self.default_password = os.getenv('DEFAULT_PASSWORD', 'KREML')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data='auth')],
            [InlineKeyboardButton("💝 Помочь проекту", callback_data='help_project')],
            [InlineKeyboardButton("❓ О проекте", callback_data='about')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Добро пожаловать! Выберите действие:",
            reply_markup=reply_markup
        )
        return START

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        if query.data == 'auth':
            await query.message.edit_text("Введите пароль для доступа:")
            return AUTH
        elif query.data == 'help_project':
            keyboard = [
                [
                    InlineKeyboardButton("TON", callback_data='donate_ton'),
                    InlineKeyboardButton("USDT (TRC20)", callback_data='donate_usdt')
                ],
                [InlineKeyboardButton("« Назад", callback_data='back_to_start')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(
                "Выберите способ поддержки проекта:",
                reply_markup=reply_markup
            )
            return HELP_PROJECT
        # Добавьте остальные обработчики здесь

    async def run(self):
        """Запуск бота"""
        application = Application.builder().token(self.token).build()

        # Создаем ConversationHandler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                START: [
                    CallbackQueryHandler(self.button_handler)
                ],
                AUTH: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.check_password)
                ],
                # Добавьте остальные состояния
            },
            fallbacks=[CommandHandler('start', self.start)]
        )

        application.add_handler(conv_handler)
        
        # Запускаем бота
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = Bot()
    try:
        import asyncio
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
