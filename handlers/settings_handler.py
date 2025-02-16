import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base_handler import BaseHandler
from core.states import States

logger = logging.getLogger(__name__)

class SettingsHandler(BaseHandler):
    def __init__(self, db_manager):
        super().__init__(db_manager)

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Основной обработчик для настроек
        """
        if update.callback_query:
            return await self.handle_settings_callback(update, context)
        return False

    async def handle_settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка callback запросов для настроек"""
        query = update.callback_query
        data = query.data

        try:
            if data == "settings":
                return await self.show_settings_menu(update, context)
            elif data == "profile_settings":
                return await self.show_profile_settings(update, context)
            else:
                await query.answer("Функция в разработке")
                return False

        except Exception as e:
            logger.error(f"Ошибка в обработчике настроек: {e}")
            await query.answer("Произошла ошибка")
            return False

    async def show_settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ меню настроек"""
        keyboard = [
            [InlineKeyboardButton("⚙️ Профиль", callback_data="profile_settings")],
            [InlineKeyboardButton("🔄 Смена доступа", callback_data="change_access")],
            [InlineKeyboardButton("📋 Запросить статус Координатора", callback_data="request_coordinator")],
            [InlineKeyboardButton("ℹ️ Квесты", callback_data="quests")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_main")]
        ]
        
        await update.callback_query.message.edit_text(
            "⚙️ Настройки\n\n"
            "• Управление профилем\n"
            "• Изменение доступа\n"
            "• Получение статуса координатора\n"
            "• Выполнение квестов",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def show_profile_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ настроек профиля"""
        user_id = update.effective_user.id
        user_data = await self.db.get_user_data(user_id)
        
        status = user_data.get('status', 'Участник')
        level = user_data.get('level', 1)
        experience = user_data.get('experience', 0)
        
        keyboard = [
            [InlineKeyboardButton("📝 Изменить имя", callback_data="change_name")],
            [InlineKeyboardButton("📱 Изменить контакты", callback_data="change_contacts")],
            [InlineKeyboardButton("« Назад", callback_data="settings_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            f"👤 Профиль\n\n"
            f"🏷 Статус: {status}\n"
            f"📊 Уровень: {level}\n"
            f"✨ Опыт: {experience}\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def handle_coordinator_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка запроса на получение статуса координатора"""
        user_id = update.effective_user.id
        
        # Проверяем, не является ли пользователь уже координатором
        if await self.db.is_coordinator(user_id):
            await update.callback_query.answer(
                "✅ Вы уже являетесь координатором",
                show_alert=True
            )
            return False
        
        # Проверяем, нет ли активной заявки
        if await self.db.has_active_coordinator_request(user_id):
            await update.callback_query.answer(
                "⏳ У вас уже есть активная заявка на рассмотрении",
                show_alert=True
            )
            return False
        
        keyboard = [
            [InlineKeyboardButton("« Отмена", callback_data="settings_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "📋 Заявка на статус Координатора\n\n"
            "Для получения статуса необходимо заполнить анкету:\n\n"
            "1️⃣ Введите ваше ФИО:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        context.user_data['state'] = States.COORDINATOR_REQUEST_NAME
        return True

    async def handle_coordinator_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка формы заявки на координатора"""
        state = context.user_data.get('state')
        user_id = update.effective_user.id
        message_text = update.message.text
        
        if state == States.COORDINATOR_REQUEST_NAME:
            context.user_data['coord_request'] = {'name': message_text}
            context.user_data['state'] = States.COORDINATOR_REQUEST_LOCATION
            
            await update.message.reply_text(
                "2️⃣ Укажите вашу область и город:"
            )
            return True
            
        elif state == States.COORDINATOR_REQUEST_LOCATION:
            context.user_data['coord_request']['location'] = message_text
            context.user_data['state'] = States.COORDINATOR_REQUEST_PHONE
            
            await update.message.reply_text(
                "3️⃣ Укажите номер для связи:"
            )
            return True
            
        # Добавьте остальные состояния формы...
        
        return False

    async def handle_access_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка смены доступа"""
        keyboard = [
            [InlineKeyboardButton("« Назад", callback_data="settings_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "🔐 Смена доступа\n\n"
            "Введите код разработчика:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        context.user_data['state'] = States.ENTERING_DEVELOPER_CODE
        return True

    async def handle_quests(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ доступных квестов"""
        user_id = update.effective_user.id
        available_quests = await self.db.get_available_quests(user_id)
        
        if not available_quests:
            await update.callback_query.message.edit_text(
                "📋 Квесты\n\n"
                "На данный момент нет доступных квестов",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="settings_menu")
                ]])
            )
            return True

        keyboard = []
        for quest in available_quests:
            keyboard.append([
                InlineKeyboardButton(
                    f"📜 {quest['title']} (+{quest['reward']} опыта)",
                    callback_data=f"quest_{quest['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="settings_menu")])
        
        await update.callback_query.message.edit_text(
            "📋 Доступные квесты:\n"
            "Выберите квест для просмотра деталей",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True
