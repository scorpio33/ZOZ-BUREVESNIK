from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.states import States
import logging
from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

class AuthHandler(BaseHandler):
    def __init__(self, db_manager):
        """Initialize AuthHandler with database manager"""
        import traceback
        logger.debug(f"AuthHandler initialization stack:\n{traceback.format_stack()}")
        super().__init__(db_manager)
        self.default_password = 'KREML'
        
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle auth-related callbacks"""
        query = update.callback_query
        data = query.data
        
        if data == "auth":
            return await self.start_auth(update, context)
        elif data == "auth_logout":
            return await self.logout(update, context)
        
        return False
        
    async def start_auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start authentication process"""
        await update.callback_query.message.edit_text(
            "🔐 Введите пароль для доступа:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад", callback_data="main_menu")
            ]])
        )
        context.user_data['state'] = States.WAITING_PASSWORD
        return True
        
    async def check_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check entered password"""
        if not update.message:
            return False
            
        entered_password = update.message.text
        
        if entered_password == self.default_password:
            context.user_data['authorized'] = True
            context.user_data['state'] = States.MAIN_MENU
            
            keyboard = [
                [InlineKeyboardButton("🗺 Поиск", callback_data="search_menu")],
                [InlineKeyboardButton("📊 Статистика", callback_data="stats_menu")],
                [InlineKeyboardButton("⚙️ Настройки", callback_data="settings_menu")],
                [InlineKeyboardButton("📍 Карта", callback_data="map_menu")]
            ]
            
            await update.message.reply_text(
                "✅ Авторизация успешна!\nВыберите действие:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return True
        else:
            await update.message.reply_text(
                "❌ Неверный пароль. Попробуйте снова или вернитесь в главное меню:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Главное меню", callback_data="main_menu")
                ]])
            )
            return False
            
    async def logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle logout"""
        context.user_data.clear()
        
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data="auth")],
            [InlineKeyboardButton("💝 Помочь проекту", callback_data="donate")],
            [InlineKeyboardButton("❓ О проекте", callback_data="about")]
        ]
        
        await update.callback_query.message.edit_text(
            "👋 Вы вышли из системы. Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True
