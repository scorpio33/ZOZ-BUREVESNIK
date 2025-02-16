import logging
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

logger = logging.getLogger(__name__)

class States:
    START = 'START'
    AUTH = 'AUTH'
    HELP_PROJECT = 'HELP_PROJECT'
    ABOUT = 'ABOUT'
    MAIN_MENU = 'MAIN_MENU'

class Bot:
    def __init__(self, application: Application):
        """
        Initialize bot with required components
        Args:
            application: Application instance from python-telegram-bot
        """
        self.application = application
        self.default_password = 'KREML'
        
        # Register handlers
        self._register_handlers()
        logger.info("Bot initialized")
        
    def _register_handlers(self):
        """Register all necessary handlers"""
        # Обработчик для команд и текстовых сообщений
        message_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_command)],
            states={
                States.AUTH: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_auth)
                ],
                States.MAIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text)
                ]
            },
            fallbacks=[CommandHandler('start', self.start_command)],
            name="message_conversation",
            persistent=True,
            per_message=False
        )
        
        # Обработчик для callback-кнопок
        callback_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.button_callback)],
            states={
                States.START: [
                    CallbackQueryHandler(self.button_callback)
                ],
                States.AUTH: [
                    CallbackQueryHandler(self.button_callback)
                ],
                States.MAIN_MENU: [
                    CallbackQueryHandler(self.button_callback)
                ],
                States.HELP_PROJECT: [
                    CallbackQueryHandler(self.button_callback)
                ],
                States.ABOUT: [
                    CallbackQueryHandler(self.button_callback)
                ]
            },
            fallbacks=[CallbackQueryHandler(self.button_callback)],
            name="callback_conversation",
            persistent=True,
            per_message=True
        )
        
        # Регистрируем оба обработчика
        self.application.add_handler(message_handler)
        self.application.add_handler(callback_handler)
        
    async def start(self):
        """Start the bot"""
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")
            raise
        finally:
            if self.application:
                await self.application.stop()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Обработчик команды /start"""
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data='auth')],
            [InlineKeyboardButton("💝 Помочь проекту", callback_data='help_project')],
            [InlineKeyboardButton("❓ О проекте", callback_data='about_project')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👋 Добро пожаловать в Поиск онлайн!\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
        logger.info(f"User {update.effective_user.id} started the bot")
        return States.START

    async def handle_auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Обработчик ввода пароля"""
        entered_password = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Auth attempt from user {user_id}")
        
        if entered_password == self.default_password:
            context.user_data['authorized'] = True
            keyboard = [
                [InlineKeyboardButton("🗺 Поиск", callback_data='search_menu')],
                [InlineKeyboardButton("📊 Статистика", callback_data='stats_menu')],
                [InlineKeyboardButton("⚙️ Настройки", callback_data='settings_menu')],
                [InlineKeyboardButton("📍 Карта", callback_data='map_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "✅ Авторизация успешна!\nВыберите действие:",
                reply_markup=reply_markup
            )
            return States.MAIN_MENU
        else:
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_start")]]
            await update.message.reply_text(
                "❌ Неверный пароль. Попробуйте снова или вернитесь в главное меню:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return States.AUTH

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Обработчик текстовых сообщений в главном меню"""
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки меню для навигации"
        )
        return States.MAIN_MENU

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        logger.info(f"Button callback received: {query.data} from user {query.from_user.id}")
        
        # Обработка различных callback-данных
        handlers = {
            'auth': self._handle_auth_callback,
            'back_to_start': self._handle_back_to_start,
            'help_project': self._handle_help_project,
            'about_project': self._handle_about_project
        }
        
        handler = handlers.get(query.data)
        if handler:
            return await handler(query, context)
            
        return context.user_data.get('state', States.START)

    # Вспомогательные методы для обработки callback-ов
    async def _handle_auth_callback(self, query, context) -> str:
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_start")]]
        await query.message.edit_text(
            "🔐 Введите пароль для доступа:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return States.AUTH

    async def _handle_back_to_start(self, query, context) -> str:
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data='auth')],
            [InlineKeyboardButton("💝 Помочь проекту", callback_data='help_project')],
            [InlineKeyboardButton("❓ О проекте", callback_data='about_project')]
        ]
        await query.message.edit_text(
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return States.START

    # Остальные методы обработки callback-ов...
