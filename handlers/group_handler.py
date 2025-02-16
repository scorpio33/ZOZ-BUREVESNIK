from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.group_manager import GroupManager
from core.states import States
import json
import logging

logger = logging.getLogger(__name__)

class GroupHandler:
    def __init__(self, group_manager: GroupManager):
        self.group_manager = group_manager

    async def show_group_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню управления группой"""
        query = update.callback_query
        group_id = context.user_data.get('current_group_id')
        
        if not group_id:
            await query.message.edit_text(
                "❌ Группа не выбрана",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="search_menu")
                ]])
            )
            return

        keyboard = [
            [InlineKeyboardButton("👥 Участники", callback_data=f"group_members_{group_id}")],
            [InlineKeyboardButton("📋 Задания", callback_data=f"group_tasks_{group_id}")],
            [InlineKeyboardButton("📍 Местоположение", callback_data=f"group_location_{group_id}")],
            [InlineKeyboardButton("📢 Сообщения", callback_data=f"group_messages_{group_id}")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data=f"group_settings_{group_id}")],
            [InlineKeyboardButton("« Назад", callback_data="search_menu")]
        ]

        await query.message.edit_text(
            "👥 Управление группой\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление участниками группы"""
        query = update.callback_query
        group_id = int(query.data.split('_')[-1])
        
        keyboard = [
            [InlineKeyboardButton("➕ Добавить участника", callback_data=f"add_member_{group_id}")],
            [InlineKeyboardButton("🔄 Изменить роли", callback_data=f"change_roles_{group_id}")],
            [InlineKeyboardButton("❌ Удалить участника", callback_data=f"remove_member_{group_id}")],
            [InlineKeyboardButton("« Назад", callback_data=f"group_menu_{group_id}")]
        ]

        members = await self.group_manager.get_members(group_id)
        text = "👥 Участники группы:\n\n"
        for member in members:
            text += f"• {member['name']} - {member['role']}\n"

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление заданиями группы"""
        query = update.callback_query
        group_id = int(query.data.split('_')[-1])
        
        keyboard = [
            [InlineKeyboardButton("➕ Новое задание", callback_data=f"new_task_{group_id}")],
            [InlineKeyboardButton("📋 Список заданий", callback_data=f"list_tasks_{group_id}")],
            [InlineKeyboardButton("« Назад", callback_data=f"group_menu_{group_id}")]
        ]

        await query.message.edit_text(
            "📋 Управление заданиями\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление местоположением группы"""
        query = update.callback_query
        group_id = int(query.data.split('_')[-1])
        
        keyboard = [
            [InlineKeyboardButton("📍 Отправить локацию", callback_data=f"send_location_{group_id}")],
            [InlineKeyboardButton("🗺 Показать карту", callback_data=f"show_map_{group_id}")],
            [InlineKeyboardButton("« Назад", callback_data=f"group_menu_{group_id}")]
        ]

        await query.message.edit_text(
            "📍 Управление местоположением\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление сообщениями группы"""
        query = update.callback_query
        group_id = int(query.data.split('_')[-1])
        
        keyboard = [
            [InlineKeyboardButton("📢 Отправить сообщение", callback_data=f"send_message_{group_id}")],
            [InlineKeyboardButton("📨 Входящие", callback_data=f"inbox_{group_id}")],
            [InlineKeyboardButton("« Назад", callback_data=f"group_menu_{group_id}")]
        ]

        await query.message.edit_text(
            "📢 Коммуникация\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
