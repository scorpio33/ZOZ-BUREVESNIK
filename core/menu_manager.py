from typing import Dict, Any
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

class MenuManager:
    def __init__(self):
        self.current_menu = {}  # Store current menu state for each user
        
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🗺 Поиск", callback_data="search")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton("📍 Карта", callback_data="map")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Главное меню:", reply_markup=reply_markup)

    async def handle_menu_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "search":
            return await self.show_search_menu(update, context)
        elif query.data == "stats":
            return await self.show_stats_menu(update, context)
        elif query.data == "settings":
            return await self.show_settings_menu(update, context)
        elif query.data == "map":
            return await self.show_map_menu(update, context)
