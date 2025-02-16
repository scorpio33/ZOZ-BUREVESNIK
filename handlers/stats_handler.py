import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base_handler import BaseHandler

logger = logging.getLogger(__name__)

class StatsHandler(BaseHandler):
    def __init__(self, db_manager, stats_manager):
        super().__init__(db_manager)
        self.stats_manager = stats_manager

    async def show_stats_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ меню статистики"""
        keyboard = [
            [InlineKeyboardButton("👤 Личная статистика", callback_data="personal_stats")],
            [InlineKeyboardButton("📊 Общая статистика", callback_data="global_stats")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_main")]
        ]
        
        await update.callback_query.message.edit_text(
            "📊 Статистика\n\n"
            "• Просмотр личных достижений\n"
            "• Общая статистика проекта",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def show_personal_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ личной статистики"""
        user_id = update.effective_user.id
        stats = await self.stats_manager.get_personal_stats(user_id)
        
        keyboard = [
            [InlineKeyboardButton("📈 Подробная статистика", callback_data="detailed_stats")],
            [InlineKeyboardButton("« Назад", callback_data="stats_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "👤 Личная статистика\n\n"
            f"🔍 Участие в поисках: {stats['search_count']}\n"
            f"📍 Пройдено км: {stats['total_distance']:.1f}\n"
            f"⭐️ Уровень: {stats['level']}\n"
            f"✨ Опыт: {stats['experience']}/{stats['next_level_exp']}\n"
            f"🏆 Достижения: {stats['achievements_count']}\n"
            f"👥 Помощь найдено: {stats['people_found']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def show_global_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ общей статистики"""
        stats = await self.stats_manager.get_global_stats()
        
        keyboard = [
            [InlineKeyboardButton("🏆 Топ участников", callback_data="top_users")],
            [InlineKeyboardButton("« Назад", callback_data="stats_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "📊 Общая статистика проекта\n\n"
            f"👥 Всего участников: {stats['total_users']}\n"
            f"🔍 Активных поисков: {stats['active_searches']}\n"
            f"✅ Завершено поисков: {stats['completed_searches']}\n"
            f"📍 Общий километраж: {stats['total_distance']:.1f} км\n"
            f"⭐️ Координаторов: {stats['coordinator_count']}\n"
            f"🏆 Найдено людей: {stats['total_found']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def show_detailed_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE