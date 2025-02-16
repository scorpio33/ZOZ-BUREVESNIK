from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ui.menu_descriptions import MENU_DESCRIPTIONS

class NavigationHandler:
    def __init__(self, menu_manager):
        self.menu_manager = menu_manager
        self.breadcrumbs = {}  # user_id: [menu_levels]
        
    async def handle_navigation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка навигации по меню"""
        query = update.callback_query
        user_id = update.effective_user.id
        callback_data = query.data
        
        # Обновляем путь навигации
        await self.update_breadcrumbs(user_id, callback_data)
        
        # Получаем соответствующее меню
        menu_text, keyboard = self.menu_manager.create_menu(
            menu_type=callback_data.replace('_menu', ''),
            is_developer=(user_id == context.bot_data.get('developer_id')),
            is_coordinator=context.user_data.get('is_coordinator', False),
            has_active_track=(user_id in context.bot_data.get('active_tracks', {}))
        )
        
        # Добавляем путь навигации к тексту меню
        breadcrumbs_text = self.get_breadcrumbs_text(user_id)
        full_text = f"{breadcrumbs_text}\n\n{menu_text}"
        
        await query.message.edit_text(
            full_text,
            reply_markup=keyboard
        )

    async def update_breadcrumbs(self, user_id: int, menu_type: str):
        """Обновление пути навигации"""
        if user_id not in self.breadcrumbs:
            self.breadcrumbs[user_id] = []
            
        # Очищаем путь при возврате в главное меню
        if menu_type == "main_menu":
            self.breadcrumbs[user_id] = []
        elif menu_type == "back":
            if self.breadcrumbs[user_id]:
                self.breadcrumbs[user_id].pop()
        else:
            menu_name = MENU_DESCRIPTIONS.get(menu_type.replace('_menu', ''), {}).get('title', menu_type)
            self.breadcrumbs[user_id].append(menu_name)

    def get_breadcrumbs_text(self, user_id: int) -> str:
        """Формирование текста навигации"""
        if user_id not in self.breadcrumbs or not self.breadcrumbs[user_id]:
            return "🏠 Главное меню"
        
        path = ["🏠"] + self.breadcrumbs[user_id]
        return " → ".join(path)
