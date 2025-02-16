import logging
import asyncio
import traceback
from telegram import Update
from telegram.ext import (
    Application, 
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, token: str):
        """Initialize bot with token"""
        try:
            self.token = token
            self.application = None
            self._running = False
            self.default_password = "KREML"  # Move to config later
            logger.info("Bot initialized with token")
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}")
            raise

    async def start(self):
        """Start the bot with proper lifecycle management"""
        try:
            if not self.application:
                logger.info("Creating application instance...")
                self.application = (
                    ApplicationBuilder()
                    .token(self.token)
                    .build()
                )
                
                await self._register_handlers()
            
            self._running = True
            logger.info("Starting bot polling...")
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}\n{traceback.format_exc()}")
            raise

    async def stop(self):
        """Gracefully stop the bot"""
        if self.application and self._running:
            self._running = False
            logger.info("Stopping bot...")
            
            try:
                # Stop polling
                await self.application.stop_polling()
                
                # Wait for pending updates to be processed
                await asyncio.sleep(1)
                
                # Stop the application
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
            
            # Register command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            
            # Register callback query handlers
            self.application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Register message handlers
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handle_text
            ))
            
            # Register error handler
            self.application.add_error_handler(self.error_handler)
            
            logger.info("Handlers registered successfully")
        except Exception as e:
            logger.error(f"Error registering handlers: {str(e)}")
            raise

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages"""
        if 'awaiting_password' in context.user_data:
            await self.check_password(update, context)
        else:
            await update.message.reply_text(
                "Пожалуйста, используйте кнопки меню для навигации"
            )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        handlers = {
            'auth': self._handle_auth_callback,
            'help_project': self._handle_help_project,
            'about_project': self._handle_about_project,
            'back_to_start': self._handle_back_to_start
        }
        
        handler = handlers.get(query.data)
        if handler:
            await handler(query, context)

    async def check_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check entered password"""
        entered_password = update.message.text
        
        if entered_password == self.default_password:
            context.user_data.pop('awaiting_password', None)
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
        else:
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_start")]]
            await update.message.reply_text(
                "❌ Неверный пароль. Попробуйте снова или вернитесь в главное меню:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже."
            )

    # Callback handlers
    async def _handle_auth_callback(self, query, context):
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_start")]]
        await query.message.edit_text(
            "🔐 Введите пароль для доступа:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['awaiting_password'] = True

    async def _handle_help_project(self, query, context):
        keyboard = [
            [
                InlineKeyboardButton("TON", callback_data="donate_ton"),
                InlineKeyboardButton("USDT (TRC20)", callback_data="donate_usdt")
            ],
            [InlineKeyboardButton("« Назад", callback_data="back_to_start")]
        ]
        await query.message.edit_text(
            "💝 Выберите способ поддержки проекта:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _handle_about_project(self, query, context):
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_start")]]
        await query.message.edit_text(
            "ℹ️ О проекте:\n\n"
            "🔍 Search and Rescue Bot - система для координации "
            "поисково-спасательных операций.\n\n"
            "Основные возможности:\n"
            "• Создание и управление поисковыми группами\n"
            "• Координация участников на местности\n"
            "• Отслеживание перемещений и маршрутов\n"
            "• Система уведомлений и оповещений\n\n"
            "📱 Версия: 1.0.0\n"
            "📞 Поддержка: @support_username",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _handle_back_to_start(self, query, context):
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data="auth")],
            [InlineKeyboardButton("💝 Помочь проекту", callback_data="help_project")],
            [InlineKeyboardButton("❓ О проекте", callback_data="about_project")]
        ]
        await query.message.edit_text(
            "👋 Добро пожаловать в Поиск онлайн!\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
