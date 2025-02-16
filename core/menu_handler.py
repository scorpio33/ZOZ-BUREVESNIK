from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Tuple, Optional
from core.menu_manager import MenuManager
from core.states import States

class MenuHandler:
    def __init__(self):
        self.menu_manager = MenuManager()
        self._current_state = States.START
        
    @property
    def current_state(self):
        return self._current_state
        
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка команды /start"""
        text, keyboard = self.menu_manager.create_menu("start")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=keyboard
        )
        self._current_state = States.START
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка callback-запросов от кнопок меню"""
        query = update.callback_query
        callback_data = query.data
        
        # Dictionary mapping callbacks to their handlers
        handlers = {
            "auth_login": self._handle_auth_login,
            "help_project": self._handle_help_project,
            "about_project": self._handle_about_project,
            "back_to_main": self._handle_back_to_main,
            "search_menu": self._handle_search_menu,
            "main_menu": self._handle_main_menu,
        }
        
        handler = handlers.get(callback_data)
        if handler:
            await handler(query, context)
            await query.answer()
        else:
            await query.answer("⚠️ Неизвестная команда")
            self._current_state = States.ERROR
            
    async def _handle_auth_login(self, query, context) -> None:
        """Обработка нажатия кнопки авторизации"""
        text = "🔐 Введите пароль для доступа:"
        await query.edit_message_text(text)
        self._current_state = States.WAITING_FOR_PASSWORD
        context.user_data['state'] = States.WAITING_FOR_PASSWORD
        
    async def _handle_help_project(self, query, context) -> None:
        """Обработка нажатия кнопки помощи проекту"""
        text, keyboard = self.menu_manager.create_menu("help_project")
        await query.edit_message_text(text, reply_markup=keyboard)
        self._current_state = States.HELP_PROJECT
        context.user_data['state'] = States.HELP_PROJECT
        
    async def _handle_about_project(self, query, context) -> None:
        """Обработка нажатия кнопки о проекте"""
        text, keyboard = self.menu_manager.create_menu("about_project")
        await query.edit_message_text(text, reply_markup=keyboard)
        self._current_state = States.ABOUT_PROJECT
        context.user_data['state'] = States.ABOUT_PROJECT
        
    async def _handle_back_to_main(self, query, context) -> None:
        """Обработка возврата в главное меню"""
        text, keyboard = self.menu_manager.create_menu("main")
        await query.edit_message_text(text, reply_markup=keyboard)
        self._current_state = States.MAIN_MENU
        context.user_data['state'] = States.MAIN_MENU
        
    async def _handle_main_menu(self, query, context) -> None:
        """Обработка перехода в главное меню"""
        if context.user_data.get('authorized', False):
            text, keyboard = self.menu_manager.create_menu("main")
            await query.edit_message_text(text, reply_markup=keyboard)
            self._current_state = States.MAIN_MENU
            context.user_data['state'] = States.MAIN_MENU
        else:
            await query.answer("⚠️ Требуется авторизация")
            
    async def _handle_search_menu(self, query, context) -> None:
        """Обработка перехода в меню поиска"""
        if context.user_data.get('authorized', False):
            text, keyboard = self.menu_manager.create_menu("search")
            await query.edit_message_text(text, reply_markup=keyboard)
            self._current_state = States.SEARCH_MENU
            context.user_data['state'] = States.SEARCH_MENU
        else:
            await query.answer("⚠️ Требуется авторизация")
        
    async def _handle_unknown_callback(self, query) -> None:
        """Обработка неизвестного callback"""
        await query.answer("⚠️ Неизвестная команда")
        self._current_state = States.ERROR
