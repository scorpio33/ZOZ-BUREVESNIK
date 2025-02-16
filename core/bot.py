import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, 
    Application, 
    ConversationHandler,
    CallbackQueryHandler, 
    MessageHandler, 
    CommandHandler,
    filters
)
from core.menu_system import MenuSystem

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)

# Определяем состояния
class States:
    START = 'START'
    AUTH = 'AUTH'
    HELP_PROJECT = 'HELP_PROJECT'
    ABOUT = 'ABOUT'
    MAIN_MENU = 'MAIN_MENU'

class Bot:
    def __init__(self, application: Application):
        """
        Инициализация бота
        Args:
            application: Экземпляр Application из python-telegram-bot
        """
        self.application = application
        self.menu_system = MenuSystem()
        self.default_password = 'KREML'
        logger.info("Bot initialized")
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """
        Обработчик команды /start
        Returns:
            str: Следующее состояние
        """
        try:
            keyboard = self.menu_system.get_start_keyboard()
            await update.message.reply_text(
                "👋 Добро пожаловать в Поиск онлайн - ваш персональный помощник в поисково-спасательных операциях.\n\n"
                "🔍 Здесь вы можете:\n"
                "- Участвовать в поисковых операциях\n"
                "- Координировать поисковые группы\n"
                "- Отслеживать свой прогресс\n"
                "- Проходить обучение\n\n"
                "Выберите действие в меню ниже:",
                reply_markup=keyboard
            )
            logger.info(f"User {update.effective_user.id} started the bot")
            return States.START
        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            await self._handle_error(update)
            return States.START

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """
        Обработчик нажатий на кнопки
        Returns:
            str: Следующее состояние
        """
        try:
            query = update.callback_query
            await query.answer()
            
            logger.info(f"Button callback received: {query.data} from user {query.from_user.id}")
            
            if query.data == 'auth':
                await query.message.edit_text(
                    "🔐 Введите пароль для доступа:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Назад", callback_data="back_to_start")
                    ]])
                )
                return States.AUTH
                
            elif query.data == 'back_to_start':
                keyboard = self.menu_system.get_start_keyboard()
                await query.message.edit_text(
                    "Выберите действие:",
                    reply_markup=keyboard
                )
                return States.START
                
        except Exception as e:
            logger.error(f"Error in button_callback: {e}")
            await self._handle_error(update)
            return States.START

    async def handle_auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """
        Обработчик ввода пароля
        Returns:
            str: Следующее состояние
        """
        try:
            if not update.message:
                return States.AUTH
                
            entered_password = update.message.text
            user_id = update.effective_user.id
            
            logger.info(f"Auth attempt from user {user_id}")
            
            if entered_password == self.default_password:
                context.user_data['authorized'] = True
                keyboard = self.menu_system.get_keyboard('main')
                await update.message.reply_text(
                    "✅ Авторизация успешна!\nВыберите действие:",
                    reply_markup=keyboard
                )
                logger.info(f"User {user_id} successfully authorized")
                return States.MAIN_MENU
            else:
                await update.message.reply_text(
                    "❌ Неверный пароль. Попробуйте снова или вернитесь в главное меню:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Главное меню", callback_data="back_to_start")
                    ]])
                )
                logger.warning(f"Failed auth attempt from user {user_id}")
                return States.AUTH
                
        except Exception as e:
            logger.error(f"Error in handle_auth: {e}")
            await self._handle_error(update)
            return States.AUTH

    async def _handle_error(self, update: Update):
        """Обработчик ошибок"""
        try:
            await update.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже или используйте /start"
            )
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

    def get_conversation_handler(self) -> ConversationHandler:
        """
        Создание и настройка ConversationHandler
        Returns:
            ConversationHandler: Настроенный обработчик диалогов
        """
        return ConversationHandler(
            entry_points=[CommandHandler('start', self.start_command)],
            states={
                States.START: [
                    CallbackQueryHandler(self.button_callback, pattern='^(auth|back_to_start)$')
                ],
                States.AUTH: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_auth),
                    CallbackQueryHandler(self.button_callback, pattern='^back_to_start$')
                ],
                States.MAIN_MENU: [
                    CallbackQueryHandler(self.button_callback)
                ],
            },
            fallbacks=[CommandHandler('start', self.start_command)],
            per_message=True,  # Важно для корректной работы CallbackQueryHandler
            per_chat=True
        )

    async def start(self):
        """Запуск бота"""
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
