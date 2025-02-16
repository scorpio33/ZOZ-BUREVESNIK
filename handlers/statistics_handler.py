from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base_handler import BaseHandler
import logging

logger = logging.getLogger(__name__)

class StatisticsHandler(BaseHandler):
    def __init__(self, db_manager, stats_manager):
        super().__init__(db_manager)
        self.stats_manager = stats_manager

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Основной обработчик для статистики
        """
        if update.callback_query:
            return await self.handle_statistics_callback(update, context)
        return False

    async def handle_statistics_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка callback запросов для статистики"""
        query = update.callback_query
        data = query.data

        try:
            if data == "statistics":
                return await self.show_statistics_menu(update, context)
            elif data == "personal_stats":
                return await self.show_personal_statistics(update, context)
            elif data == "global_stats":
                return await self.show_global_statistics(update, context)
            else:
                await query.answer("Функция в разработке")
                return False

        except Exception as e:
            logger.error(f"Ошибка в обработчике статистики: {e}")
            await query.answer("Произошла ошибка")
            return False

    async def show_statistics_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ меню статистики"""
        keyboard = [
            [InlineKeyboardButton("📊 Личная статистика", callback_data="personal_stats")],
            [InlineKeyboardButton("🌍 Общая статистика", callback_data="global_stats")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_main")]
        ]
        
        await update.callback_query.message.edit_text(
            "📊 Статистика\n\n"
            "• Личная статистика: ваши достижения и прогресс\n"
            "• Общая статистика: данные по всем поискам",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def show_personal_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ личной статистики"""
        stats = await self.stats_manager.get_user_statistics(update.effective_user.id)
        
        message = (
            "📊 Ваша статистика:\n\n"
            f"👤 Уровень: {stats.get('level', 1)}\n"
            f"⭐️ Опыт: {stats.get('experience', 0)}\n"
            f"🔍 Участие в поисках: {stats.get('searches', 0)}\n"
            f"📍 Пройдено км: {stats.get('distance', 0)}\n"
            f"✅ Выполнено задач: {stats.get('completed_tasks', 0)}"
        )
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="statistics")]]
        
        await update.callback_query.message.edit_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def show_global_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ общей статистики"""
        stats = await self.stats_manager.get_global_statistics()
        
        message = (
            "🌍 Общая статистика:\n\n"
            f"👥 Активных пользователей: {stats.get('active_users', 0)}\n"
            f"🔍 Всего поисков: {stats.get('total_searches', 0)}\n"
            f"✅ Успешных поисков: {stats.get('successful_searches', 0)}\n"
            f"📍 Общая дистанция: {stats.get('total_distance', 0)} км"
        )
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="statistics")]]
        
        await update.callback_query.message.edit_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True
