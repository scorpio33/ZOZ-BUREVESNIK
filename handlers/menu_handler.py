import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes
)

logger = logging.getLogger(__name__)

class MenuHandler:
    def __init__(self, menu_manager):
        self.menu_manager = menu_manager

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        menu_text, keyboard = self.menu_manager.create_menu("main")
        await query.message.edit_text(text=menu_text, reply_markup=keyboard)

    async def handle_search_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        menu_text, keyboard = self.menu_manager.create_menu("search")
        await query.message.edit_text(text=menu_text, reply_markup=keyboard)

    async def handle_start_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        menu_text, keyboard = self.menu_manager.create_menu("start")
        await query.message.edit_text(text=menu_text, reply_markup=keyboard)

    def get_handler(self):
        """Получение обработчика меню"""
        return CallbackQueryHandler(self.show_menu, pattern='^main_menu$')
