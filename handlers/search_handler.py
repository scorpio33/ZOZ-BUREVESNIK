from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
import logging

logger = logging.getLogger(__name__)

class SearchHandler(BaseHandler):
    def __init__(self, db_manager, map_manager):
        """
        Initialize SearchHandler
        
        Args:
            db_manager: Database manager instance
            map_manager: Map manager instance
        """
        super().__init__(db_manager)
        self.map_manager = map_manager
        
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle search-related callbacks"""
        query = update.callback_query
        data = query.data
        
        if data == "search":
            return await self.show_search_menu(update, context)
        elif data == "start_search":
            return await self.start_new_search(update, context)
        elif data == "join_search":
            return await self.join_search(update, context)
        elif data == "coordination":
            return await self.show_coordination_menu(update, context)
            
        return False
        
    async def show_search_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show search options menu"""
        keyboard = [
            [InlineKeyboardButton("🔍 Начать поиск", callback_data="start_search")],
            [InlineKeyboardButton("👥 Присоединиться к поиску", callback_data="join_search")],
            [InlineKeyboardButton("📍 Координация", callback_data="coordination")],
            [InlineKeyboardButton("« Главное меню", callback_data="main_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "🗺 Меню поиска:\n\n"
            "• Создайте новую группу поиска\n"
            "• Присоединитесь к существующей группе\n"
            "• Перейдите в режим координации",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True
