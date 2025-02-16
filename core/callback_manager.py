from typing import Dict, Callable, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.states import States
import logging

logger = logging.getLogger(__name__)

class CallbackManager:
    def __init__(self, handlers):
        """
        Initialize callback manager with handlers
        
        Структура callback_data:
        - auth_* -> auth_handler
        - help_* -> donation_handler
        - map_* -> map_handler
        - search_* -> search_handler
        - coord_* -> coordinator_handler
        - stats_* -> statistics_handler
        - quest_* -> quest_handler
        """
        self.handlers = handlers
        self.callback_routes = {
            'auth': ['login', 'recovery'],
            'help': ['project'],
            'about': ['project'],
            'main': ['menu'],
            'back': ['to_start'],
            'search': ['menu'],
            'stats': ['menu'],
            'settings': ['menu'],
            'map': ['menu']
        }
        logger.info(f"CallbackManager initialized with {len(self.handlers)} handlers")
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        data = query.data
        
        try:
            if data == "search_menu":
                await self._handle_search_menu(query, context)
            elif data == "stats_menu":
                await self._handle_stats_menu(query, context)
            elif data == "settings_menu":
                await self._handle_settings_menu(query, context)
            elif data == "map_menu":
                await self._handle_map_menu(query, context)
            else:
                # Существующая логика обработки других callback
                parts = data.split('_', 1)
                if len(parts) < 2:
                    await query.answer("⚠️ Неверный формат команды")
                    return
                    
                prefix, action = parts
                if prefix not in self.callback_routes or action not in self.callback_routes[prefix]:
                    await query.answer("⚠️ Неизвестная команда")
                    return
                    
                handler = self.handlers.get(prefix)
                if handler:
                    await handler.handle(update, context)
            
        except Exception as e:
            logger.error(f"Error in handle_callback: {str(e)}")
            await query.answer("⚠️ Произошла ошибка при обработке команды")
        
    async def _handle_auth_login(self, query, context):
        """Handle authorization login"""
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_start")]]
        await query.message.edit_text(
            "🔐 Введите пароль для доступа:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['state'] = States.WAITING_PASSWORD
        await query.answer()
        
    async def _handle_help_project(self, query, context):
        """Handle help project menu"""
        keyboard = [
            [
                InlineKeyboardButton("TON", callback_data="donate_ton"),
                InlineKeyboardButton("USDT (TRC20)", callback_data="donate_usdt")
            ],
            [InlineKeyboardButton("« Назад", callback_data="back_to_start")]
        ]
        await query.message.edit_text(
            "💝 Выберите способ поддержки проекта:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['state'] = States.HELP_PROJECT
        await query.answer()
        
    async def _handle_about_project(self, query, context):
        """Handle about project info"""
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_start")]]
        await query.message.edit_text(
            "ℹ️ О проекте:\n\n"
            "🔍 Search and Rescue Bot - это система для координации "
            "поисково-спасательных операций.\n\n"
            "Основные возможности:\n"
            "• Создание и управление поисковыми группами\n"
            "• Координация участников на местности\n"
            "• Отслеживание перемещений и маршрутов\n"
            "• Система уведомлений и оповещений\n\n"
            "📱 Версия: 1.0.0\n"
            "📞 Поддержка: @support_username",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['state'] = States.ABOUT
        await query.answer()

    async def _handle_back_to_start(self, query, context):
        """Handle back to start menu"""
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data="auth_login")],
            [InlineKeyboardButton("💝 Помочь проекту", callback_data="help_project")],
            [InlineKeyboardButton("❓ О проекте", callback_data="about_project")]
        ]
        await query.message.edit_text(
            "👋 Добро пожаловать в Search and Rescue Bot!\n\n"
            "🔍 Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['state'] = States.START
        await query.answer()

    async def _handle_search_menu(self, query, context):
        """Handle search menu callback"""
        keyboard = [
            [InlineKeyboardButton("🔍 Начать поиск", callback_data="search_start")],
            [InlineKeyboardButton("👥 Присоединиться", callback_data="search_join")],
            [InlineKeyboardButton("📍 Координация", callback_data="search_coord")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            "🗺 Меню поиска:\n\n"
            "• Создайте новую группу поиска\n"
            "• Присоединитесь к существующей группе\n"
            "• Перейдите в режим координации",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.answer()

    async def _handle_stats_menu(self, query, context):
        """Handle statistics menu callback"""
        keyboard = [
            [InlineKeyboardButton("📊 Личная статистика", callback_data="stats_personal")],
            [InlineKeyboardButton("📈 Общая статистика", callback_data="stats_global")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            "📊 Меню статистики:\n\n"
            "Выберите тип статистики для просмотра:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.answer()

    async def _handle_settings_menu(self, query, context):
        """Handle settings menu callback"""
        keyboard = [
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings_menu")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            "⚙️ Меню настроек:\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.answer()

    async def _handle_map_menu(self, query, context):
        """Handle map menu callback"""
        keyboard = [
            [InlineKeyboardButton("🗺️ Карта", callback_data="map_menu")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            "🗺️ Меню карты:\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.answer()
