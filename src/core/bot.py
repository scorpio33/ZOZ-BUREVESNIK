from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.core.auth_manager import AuthManager
from src.core.states import States
import logging

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = self.get_start_menu_keyboard()
        await update.message.reply_text(
            "Добро пожаловать! Выберите действие:",
            reply_markup=keyboard
        )
        context.user_data['state'] = States.INITIAL

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "main_menu":
            context.user_data['state'] = States.MAIN_MENU
            keyboard = self.get_main_menu_keyboard()
            await query.message.edit_text(
                "Главное меню:",
                reply_markup=keyboard
            )

    def get_start_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Create start menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data="auth_login")],
            [InlineKeyboardButton("💝 Помочь проекту", callback_data="help_project")],
            [InlineKeyboardButton("❓ О проекте", callback_data="about")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Create main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🗺 Поиск", callback_data="search_menu")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats_menu")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings_menu")],
            [InlineKeyboardButton("📍 Карта", callback_data="map_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
