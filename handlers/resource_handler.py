from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ResourceHandler:
    def __init__(self, resource_manager, permission_manager):
        self.resource_manager = resource_manager
        self.permission_manager = permission_manager

    async def show_resource_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню управления ресурсами"""
        query = update.callback_query
        await query.answer()

        keyboard = [
            [InlineKeyboardButton("📦 Выдача оборудования", callback_data="resource_checkout")],
            [InlineKeyboardButton("↩️ Возврат оборудования", callback_data="resource_return")],
            [InlineKeyboardButton("📋 Список ресурсов", callback_data="resource_list")],
            [InlineKeyboardButton("📊 Планирование", callback_data="resource_planning")],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]

        await query.message.edit_text(
            "🔧 Управление ресурсами\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def checkout_resource(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Процесс выдачи оборудования"""
        query = update.callback_query
        await query.answer()

        # Получаем список доступного оборудования
        resources = await self.resource_manager.get_available_resources()
        
        keyboard = []
        for resource in resources:
            keyboard.append([
                InlineKeyboardButton(
                    f"{resource['name']} (SN: {resource['serial_number']})",
                    callback_data=f"checkout_{resource['resource_id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="resource_menu")])

        await query.message.edit_text(
            "📦 Выдача оборудования\n"
            "Выберите оборудование для выдачи:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def confirm_checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение выдачи оборудования"""
        query = update.callback_query
        await query.answer()

        resource_id = int(query.data.split('_')[1])
        user_id = query.from_user.id
        
        # Получаем активную группу пользователя
        group_id = await self.resource_manager.get_user_active_group(user_id)
        if not group_id:
            await query.message.edit_text(
                "❌ Вы должны быть участником активной поисковой группы"
            )
            return

        # Устанавливаем ожидаемую дату возврата (например, через 24 часа)
        return_date = datetime.now() + timedelta(hours=24)

        # Выполняем выдачу
        success = await self.resource_manager.checkout_resource(
            resource_id, user_id, group_id, 
            context.user_data.get('operation_id'), return_date
        )

        if success:
            await query.message.edit_text(
                "✅ Оборудование успешно выдано!\n"
                f"Ожидаемая дата возврата: {return_date.strftime('%d.%m.%Y %H:%M')}"
            )
        else:
            await query.message.edit_text(
                "❌ Ошибка при выдаче оборудования"
            )

    async def return_resource(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Процесс возврата оборудования"""
        query = update.callback_query
        await query.answer()

        # Получаем список оборудования, выданного пользователю
        user_resources = await self.resource_manager.get_user_resources(query.from_user.id)
        
        keyboard = []
        for resource in user_resources:
            keyboard.append([
                InlineKeyboardButton(
                    f"{resource['name']} (Выдано: {resource['checkout_date']})",
                    callback_data=f"return_{resource['resource_id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="resource_menu")])

        await query.message.edit_text(
            "↩️ Возврат оборудования\n"
            "Выберите оборудование для возврата:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def confirm_return(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение возврата оборудования"""
        query = update.callback_query
        await query.answer()

        resource_id = int(query.data.split('_')[1])
        
        # Запрашиваем состояние оборудования
        keyboard = [
            [InlineKeyboardButton("✅ Хорошее", callback_data=f"condition_{resource_id}_good")],
            [InlineKeyboardButton("⚠️ Требует внимания", callback_data=f"condition_{resource_id}_fair")],
            [InlineKeyboardButton("❌ Повреждено", callback_data=f"condition_{resource_id}_damaged")],
            [InlineKeyboardButton("« Назад", callback_data="resource_return")]
        ]

        await query.message.edit_text(
            "Укажите состояние возвращаемого оборудования:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )