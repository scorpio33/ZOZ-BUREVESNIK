from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportHandler:
    def __init__(self, report_system):
        self.report_system = report_system

    async def show_reports_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню отчетов"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Текущие операции", callback_data="report_current"),
                InlineKeyboardButton("📈 Статистика", callback_data="report_stats")
            ],
            [
                InlineKeyboardButton("📑 Архив отчетов", callback_data="report_archive"),
                InlineKeyboardButton("📤 Экспорт данных", callback_data="report_export")
            ],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            "📊 Система отчетности\n\n"
            "Выберите необходимое действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def generate_operation_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Генерация отчета по операции"""
        query = update.callback_query
        operation_id = int(context.user_data.get('selected_operation'))
        
        # Отправляем сообщение о начале генерации
        message = await query.message.reply_text("⏳ Генерация отчета...")
        
        # Генерируем отчет
        report_data = await self.report_system.generate_operation_report(operation_id)
        
        if not report_data:
            await message.edit_text("❌ Не удалось сгенерировать отчет")
            return

        # Формируем текстовое представление отчета
        report_text = self._format_report_text(report_data)
        
        # Создаем клавиатуру для экспорта
        keyboard = [
            [
                InlineKeyboardButton("📥 Excel", callback_data=f"export_xlsx_{operation_id}"),
                InlineKeyboardButton("📄 PDF", callback_data=f"export_pdf_{operation_id}"),
                InlineKeyboardButton("📋 JSON", callback_data=f"export_json_{operation_id}")
            ],
            [InlineKeyboardButton("« Назад", callback_data="reports_menu")]
        ]

        await message.edit_text(
            report_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    def _format_report_text(self, report_data: dict) -> str:
        """Форматирование отчета для отображения в Telegram"""
        operation = report_data['operation']
        stats = report_data['statistics']
        
        return (
            f"📊 <b>Отчет по операции #{operation['operation_id']}</b>\n\n"
            f"📍 Локация: {operation['location']}\n"
            f"🕒 Начало: {operation['start_time']}\n"
            f"⏱ Длительность: {stats['duration']} часов\n\n"
            f"👥 Участников: {stats['total_participants']}\n"
            f"✅ Выполнено задач: {stats['completed_tasks']}/{stats['total_tasks']}\n"
            f"🗺 Покрытая территория: {stats['covered_area']} км²\n"
            f"👣 Общая дистанция: {stats['total_distance']} км\n\n"
            f"📈 Эффективность: {report_data['efficiency']['overall_score']}%\n"
        )