import logging
import asyncio
from telegram import Update
from telegram.ext import Application, ApplicationBuilder
from contextlib import suppress

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, token: str):
        """Initialize bot with token"""
        try:
            self.token = token
            self.application = None
            self._running = False
            logger.info("Bot initialized with token")
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}")
            raise

    async def start(self):
        """Start the bot with proper lifecycle management"""
        try:
            # Create application instance if not exists
            if not self.application:
                logger.info("Creating application instance...")
                self.application = (
                    ApplicationBuilder()
                    .token(self.token)
                    .build()
                )
                
                logger.info("Registering handlers...")
                await self._register_handlers()
            
            logger.info("Initializing application...")
            await self.application.initialize()
            
            logger.info("Starting application...")
            await self.application.start()
            
            self._running = True
            logger.info("Bot started successfully")
            
            # Run polling in background task
            logger.info("Starting polling...")
            await self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                close_loop=False
            )
            
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        finally:
            if self._running:
                await self.stop()

    async def stop(self):
        """Gracefully stop the bot"""
        if self.application:
            self._running = False
            logger.info("Stopping bot...")
            
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Bot stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping bot: {str(e)}")
                raise

    async def _register_handlers(self):
        """Register all handlers"""
        try:
            if not self.application:
                raise RuntimeError("Application not initialized")
            
            # Register handlers here
            # self.application.add_handler(...)
            
            logger.info("Handlers registered successfully")
        except Exception as e:
            logger.error(f"Error registering handlers: {str(e)}")
            raise

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
