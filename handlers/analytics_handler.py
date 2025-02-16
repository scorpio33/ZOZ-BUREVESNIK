from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class AnalyticsHandler:
    def __init__(self, analytics_manager, efficiency_manager):
        self.analytics = analytics_manager
        self.efficiency = efficiency_manager

    async def show_analytics_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню аналитики"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("📊 Текущие операции", callback_data="analytics_current")],
            [InlineKeyboardButton("📈 Статистика эффективности", callback_data="analytics_efficiency")],
            [InlineKeyboardButton("📋 Сравнительный анализ", callback_data="analytics_compare")],
            [InlineKeyboardButton("🗺 Анализ территорий", callback_data="analytics_areas")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            "📊 Аналитика и мониторинг\n\n"
            "Выберите тип анализа:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_operation_analytics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ аналитики операции"""
        query = update.callback_query
        operation_id = int(query.data.split('_')[2])
        
        analytics = await self.analytics.get_detailed_analytics(operation_id)
        if not analytics:
            await query.edit_message_text(
                "❌ Не удалось загрузить аналитику операции",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="analytics_menu")
                ]])
            )
            return

        # Формируем сообщение с аналитикой
        message = (
            "📊 Детальная аналитика операции\n\n"
            f"👥 Команд: {analytics['basic_info']['team_count']}\n"
            f"👤 Участников: {analytics['basic_info']['participant_count']}\n"
            f"🎯 Выполнение задач: {analytics['basic_info']['avg_task_completion']:.1f}%\n"
            f"🗺 Покрытие территории: {analytics['coverage_analysis']['total_coverage']:.1f}%\n"
            f"⏱ Среднее время реагирования: {analytics['basic_info']['avg_response_time']} мин\n\n"
            "📈 Эффективность команд:\n"
        )
        
        for team in analytics['team_analysis']:
            message += (
                f"└ {team['team_name']}: {team['coordination_score']:.1f}%\n"
                f"  ├ Покрытие: {team['coverage_area']:.1f} км²\n"
                f"  └ Выполнение задач: {team['task_completion_rate']:.1f}%\n"
            )

        keyboard = [
            [InlineKeyboardButton("📈 Графики", callback_data=f"analytics_graphs_{operation_id}")],
            [InlineKeyboardButton("📋 Полный отчет", callback_data=f"analytics_report_{operation_id}")],
            [InlineKeyboardButton("« Назад", callback_data="analytics_menu")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
