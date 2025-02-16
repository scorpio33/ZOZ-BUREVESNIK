import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class StatisticsManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback-запросов для статистики"""
        query = update.callback_query
        data = query.data

        if data == "stats":
            await self.show_statistics_menu(update, context)
        elif data == "personal_stats":
            await self.show_personal_statistics(update, context)
        elif data == "global_stats":
            await self.show_global_statistics(update, context)

    async def show_statistics_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню статистики"""
        keyboard = [
            [InlineKeyboardButton("📊 Личная статистика", callback_data="personal_stats")],
            [InlineKeyboardButton("🌍 Общая статистика", callback_data="global_stats")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        await update.callback_query.message.edit_text(
            "📊 Выберите тип статистики:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_personal_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать личную статистику"""
        user_id = update.effective_user.id
        # TODO: Получить статистику из базы данных
        stats_text = (
            "📊 Ваша статистика:\n\n"
            "🔍 Участие в поисках: 0\n"
            "👣 Пройдено км: 0\n"
            "⭐️ Уровень: 1\n"
            "✨ Опыт: 0/100"
        )
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="stats")]]
        await update.callback_query.message.edit_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_global_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать общую статистику"""
        # TODO: Получить общую статистику из базы данных
        stats_text = (
            "🌍 Общая статистика:\n\n"
            "👥 Всего пользователей: 0\n"
            "🔍 Активных поисков: 0\n"
            "✅ Завершённых поисков: 0\n"
            "📍 Отмеченных точек: 0"
        )
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="stats")]]
        await update.callback_query.message.edit_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
