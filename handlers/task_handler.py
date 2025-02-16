from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from utils.permission_checker import check_coordinator_permission

logger = logging.getLogger(__name__)

class TaskHandler:
    def __init__(self, task_service, notification_manager):
        self.task_service = task_service
        self.notification_manager = notification_manager

    async def show_task_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню управления задачами"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("📝 Создать задачу", callback_data="task_create")],
            [InlineKeyboardButton("📋 Активные задачи", callback_data="task_list_active")],
            [InlineKeyboardButton("✅ Завершенные задачи", callback_data="task_list_completed")],
            [InlineKeyboardButton("📑 Шаблоны задач", callback_data="task_templates")],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]
        
        await query.message.edit_text(
            "📋 Управление задачами\n\n"
            "• Создавайте новые задачи\n"
            "• Отслеживайте выполнение\n"
            "• Используйте шаблоны\n"
            "• Управляйте приоритетами",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @check_coordinator_permission('manage_tasks')
    async def create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание новой задачи (только для координаторов)"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("📝 Создать новую", callback_data="task_create_new")],
            [InlineKeyboardButton("📑 Использовать шаблон", callback_data="task_use_template")],
            [InlineKeyboardButton("« Назад", callback_data="task_menu")]
        ]
        
        await query.message.edit_text(
            "📝 Создание задачи\n\n"
            "Выберите способ создания:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_priority_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор приоритета задачи"""
        keyboard = [
            [
                InlineKeyboardButton("🟢 Низкий", callback_data="task_priority_1"),
                InlineKeyboardButton("🟡 Средний", callback_data="task_priority_2")
            ],
            [
                InlineKeyboardButton("🔴 Высокий", callback_data="task_priority_3"),
                InlineKeyboardButton("⚡️ Критический", callback_data="task_priority_4")
            ],
            [InlineKeyboardButton("« Назад", callback_data="task_create")]
        ]
        
        await update.callback_query.message.edit_text(
            "Выберите приоритет задачи:\n\n"
            "🟢 Низкий - обычная задача\n"
            "🟡 Средний - важная задача\n"
            "🔴 Высокий - срочная задача\n"
            "⚡️ Критический - требует немедленного внимания",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @check_coordinator_permission('manage_tasks')
    async def manage_task_templates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление шаблонами задач (только для координаторов)"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("📝 Создать шаблон", callback_data="template_create")],
            [InlineKeyboardButton("📋 Список шаблонов", callback_data="template_list")],
            [InlineKeyboardButton("« Назад", callback_data="task_menu")]
        ]
        
        await query.message.edit_text(
            "📑 Управление шаблонами задач\n\n"
            "• Создавайте новые шаблоны\n"
            "• Просматривайте существующие\n"
            "• Используйте для быстрого создания задач",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
