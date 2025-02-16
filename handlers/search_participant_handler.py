from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DatabaseManager
from core.states import States

class SearchParticipantHandler:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def join_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Присоединение к существующему поиску"""
        await update.callback_query.message.edit_text(
            "Введите ID поиска для присоединения:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Отмена", callback_data="search_menu")
            ]])
        )
        context.user_data['state'] = States.ENTERING_SEARCH_ID

    async def handle_search_join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка присоединения к поиску"""
        try:
            search_id = int(update.message.text)
            search = await self.db.get_search(search_id)
            
            if not search:
                await update.message.reply_text(
                    "❌ Поиск не найден. Проверьте ID.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Назад", callback_data="search_menu")
                    ]])
                )
                return

            # Добавляем пользователя к поиску
            success = await self.db.add_search_participant(
                search_id=search_id,
                user_id=update.effective_user.id
            )

            if success:
                keyboard = [
                    [InlineKeyboardButton("📍 Отправить локацию", 
                                        callback_data=f"send_location_{search_id}")],
                    [InlineKeyboardButton("📋 Информация о поиске", 
                                        callback_data=f"search_info_{search_id}")],
                    [InlineKeyboardButton("« В меню поиска", 
                                        callback_data="search_menu")]
                ]
                await update.message.reply_text(
                    f"✅ Вы присоединились к поиску '{search['name']}'\n\n"
                    "Выберите действие:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка при присоединении к поиску.")

        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат ID. Введите числовое значение.")
