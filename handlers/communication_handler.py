from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.communication_manager import CommunicationManager
import logging

logger = logging.getLogger(__name__)

class CommunicationHandler:
    def __init__(self, communication_manager: CommunicationManager):
        self.comm_manager = communication_manager

    async def show_communication_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню коммуникации"""
        query = update.callback_query
        await query.answer()

        group_id = context.user_data.get('current_group_id')
        if not group_id:
            await query.message.edit_text(
                "❌ Сначала выберите группу",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="main_menu")
                ]])
            )
            return

        keyboard = [
            [InlineKeyboardButton("💬 Групповой чат", callback_data=f"chat_{group_id}")],
            [InlineKeyboardButton("📢 Оповещения", callback_data=f"alerts_{group_id}")],
            [InlineKeyboardButton("⚡️ Быстрые команды", callback_data=f"quick_commands_{group_id}")],
            [InlineKeyboardButton("👥 Статусы участников", callback_data=f"members_status_{group_id}")],
            [InlineKeyboardButton("🚨 Экстренное сообщение", callback_data=f"emergency_{group_id}")],
            [InlineKeyboardButton("« Назад", callback_data="group_menu")]
        ]

        await query.message.edit_text(
            "📱 Меню коммуникации\n\n"
            "Выберите нужный раздел:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_status_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обновления статуса"""
        query = update.callback_query
        await query.answer()

        status = query.data.split('_')[1]
        group_id = context.user_data.get('current_group_id')
        user_id = update.effective_user.id

        if await self.comm_manager.update_member_status(user_id, group_id, status):
            status_emoji = {
                'active': '✅',
                'resting': '😴',
                'unavailable': '❌',
                'emergency': '🚨'
            }.get(status, '❓')

            await query.message.edit_text(
                f"{status_emoji} Ваш статус обновлен: {status}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="communication_menu")
                ]])
            )

    async def send_emergency_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправка экстренного сообщения"""
        query = update.callback_query
        await query.answer()

        context.user_data['state'] = 'waiting_emergency_message'
        
        await query.message.edit_text(
            "🚨 ЭКСТРЕННОЕ СООБЩЕНИЕ\n\n"
            "Опишите ситуацию. Сообщение будет немедленно отправлено всем координаторам "
            "и участникам группы.\n\n"
            "❗️ Используйте только в случае реальной необходимости!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Отмена", callback_data="communication_menu")
            ]])
        )

    async def handle_message_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка входящих сообщений"""
        state = context.user_data.get('state')
        if not state:
            return

        if state == 'waiting_emergency_message':
            group_id = context.user_data.get('current_group_id')
            content = update.message.text
            sender_id = update.effective_user.id

            # Создаем экстренный чат, если его нет
            chat_info = await self.comm_manager.get_or_create_emergency_chat(group_id)
            
            # Отправляем экстренное сообщение
            await self.comm_manager.send_message(
                chat_info['chat_id'],
                sender_id,
                content,
                message_type='emergency'
            )

            # Очищаем состояние
            context.user_data.pop('state', None)

            await update.message.reply_text(
                "🚨 Экстренное сообщение отправлено!\n"
                "Координаторы уведомлены.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« К меню связи", callback_data="communication_menu")
                ]])
            )