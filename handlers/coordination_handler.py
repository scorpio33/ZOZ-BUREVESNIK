from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import json
from core.coordination_manager import CoordinationManager
from core.states import States
import logging

logger = logging.getLogger(__name__)

class CoordinationHandler:
    def __init__(self, coordination_manager, notification_manager):
        self.coordination_manager = coordination_manager
        self.notification_manager = notification_manager

    async def show_coordination_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ главного меню координации"""
        query = update.callback_query
        await query.answer()

        operation_id = context.user_data.get('current_operation_id')
        if not operation_id:
            await query.message.edit_text(
                "❌ Сначала выберите активную операцию",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="main_menu")
                ]])
            )
            return

        keyboard = [
            [InlineKeyboardButton("📋 Управление задачами", callback_data="coord_tasks")],
            [InlineKeyboardButton("🎯 Назначить ресурсы", callback_data="coord_resources")],
            [InlineKeyboardButton("📊 Отчеты и статистика", callback_data="coord_reports")],
            [InlineKeyboardButton("⚡️ Оперативное управление", callback_data="coord_operational")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]

        await query.message.edit_text(
            "🎯 Меню координации\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание новой задачи"""
        query = update.callback_query
        await query.answer()

        # Запрашиваем название задачи
        context.user_data['creating_task'] = True
        keyboard = [[InlineKeyboardButton("« Отмена", callback_data="coord_tasks")]]
        
        await query.message.edit_text(
            "📝 Создание новой задачи\n\n"
            "Введите название задачи:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return "AWAIT_TASK_TITLE"

    async def handle_task_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода названия задачи"""
        title = update.message.text
        context.user_data['task_title'] = title

        # Запрашиваем приоритет
        keyboard = [
            [
                InlineKeyboardButton("🟢 Низкий", callback_data="task_priority_1"),
                InlineKeyboardButton("🟡 Средний", callback_data="task_priority_2")
            ],
            [
                InlineKeyboardButton("🔴 Высокий", callback_data="task_priority_3"),
                InlineKeyboardButton("⚡️ Критический", callback_data="task_priority_4")
            ],
            [InlineKeyboardButton("« Отмена", callback_data="coord_tasks")]
        ]

        await update.message.reply_text(
            f"Задача: {title}\n\n"
            "Выберите приоритет задачи:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return "AWAIT_TASK_PRIORITY"

    async def handle_task_assignment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка назначения задачи"""
        query = update.callback_query
        task_data = context.user_data.get('temp_task_data', {})
        
        try:
            task_id = await self.coordination_manager.create_task(
                task_data['operation_id'],
                {
                    'group_id': task_data['group_id'],
                    'creator_id': update.effective_user.id,
                    'title': task_data['title'],
                    'description': task_data['description'],
                    'priority_level': task_data.get('priority', 2),
                    'deadline': task_data.get('deadline')
                }
            )
            
            await query.edit_message_text(
                "✅ Задача успешно создана и назначена группе.",
                reply_markup=self._get_task_management_keyboard(task_id)
            )
        except Exception as e:
            logger.error(f"Error in task assignment: {e}")
            await query.edit_message_text("❌ Ошибка при создании задачи.")

    async def handle_status_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обновления статуса"""
        query = update.callback_query
        data = query.data.split('_')
        task_id = int(data[2])
        new_status = data[3]
        
        success = await self.coordination_manager.update_task_progress(
            task_id,
            {
                'reporter_id': update.effective_user.id,
                'status_update': new_status,
                'progress_percentage': 100 if new_status == 'completed' else 50
            }
        )
        
        if success:
            await query.edit_message_text(
                f"✅ Статус задачи обновлен: {new_status}",
                reply_markup=self._get_task_management_keyboard(task_id)
            )
        else:
            await query.answer("❌ Ошибка при обновлении статуса")

    async def handle_escalation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка эскалации задачи"""
        query = update.callback_query
        task_id = int(query.data.split('_')[2])
        
        # Повышаем приоритет и уведомляем координаторов
        await self.coordination_manager.escalate_task(task_id)
        await self.notification_manager.notify_coordinators(
            f"⚠️ Эскалация задачи #{task_id}!\n"
            f"Требуется немедленное внимание!"
        )
        
        await query.edit_message_text(
            "🔔 Задача эскалирована координаторам",
            reply_markup=self._get_task_management_keyboard(task_id)
        )

    def _get_task_management_keyboard(self, task_id: int) -> InlineKeyboardMarkup:
        """Создание клавиатуры управления задачей"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Выполнено", callback_data=f"task_status_{task_id}_completed"),
                InlineKeyboardButton("🔄 В процессе", callback_data=f"task_status_{task_id}_in_progress")
            ],
            [
                InlineKeyboardButton("⚠️ Эскалация", callback_data=f"task_escalate_{task_id}"),
                InlineKeyboardButton("📋 Детали", callback_data=f"task_details_{task_id}")
            ],
            [InlineKeyboardButton("« Назад", callback_data="coordination_menu")]
        ])
