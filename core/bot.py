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
    def __init__(self, token: str):
        """Initialize bot with token"""
        self.token = token
        self.default_password = 'KREML'
        self.application = None
        logger.info("Bot initialized with token")

    async def start(self):
        """Start the bot"""
        try:
            # Initialize application
            self.application = Application.builder().token(self.token).build()
            
            # Register handlers
            self._register_handlers()
            
            # Start polling
            logger.info("Starting bot polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
        
    def _register_handlers(self):
        """Register all handlers"""
        # Message handler
        message_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_command)],
            states={
                States.START: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text)
                ],
                States.AUTH: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_auth)
                ],
                States.MAIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text)
                ]
            },
            fallbacks=[CommandHandler('start', self.start_command)],
            name="message_conversation",
            persistent=False  # Changed to False to avoid persistence issues
        )
        
        # Callback handler
        callback_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.button_callback, pattern='^.*$')],
            states={
                States.START: [
                    CallbackQueryHandler(self.button_callback, pattern='^.*$')
                ],
                States.AUTH: [
                    CallbackQueryHandler(self.button_callback, pattern='^.*$')
                ],
                States.MAIN_MENU: [
                    CallbackQueryHandler(self.button_callback, pattern='^.*$')
                ],
                States.HELP_PROJECT: [
                    CallbackQueryHandler(self.button_callback, pattern='^.*$')
                ],
                States.ABOUT: [
                    CallbackQueryHandler(self.button_callback, pattern='^.*$')
                ]
            },
            fallbacks=[CallbackQueryHandler(self.button_callback, pattern='^.*$')],
            name="callback_conversation",
            persistent=False  # Changed to False to avoid persistence issues
        )
        
        # Add handlers
        self.application.add_handler(message_handler)
        self.application.add_handler(callback_handler)
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Handlers registered successfully")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже."
            )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handle /start command"""
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
