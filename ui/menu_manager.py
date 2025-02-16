from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Optional
import json

class MenuManager:
    def __init__(self):
        self.menu_cache = {}  # Кэш для хранения состояний меню
        
    def create_menu(self, menu_type: str, **kwargs) -> tuple:
        """Создание меню по типу"""
        if menu_type == "start":
            return self._create_start_menu()
        elif menu_type == "main":
            return self._create_main_menu(kwargs.get('is_coordinator', False))
        elif menu_type == "search":
            return self._create_search_menu(kwargs.get('is_coordinator', False))
        elif menu_type == "map":
            return self._create_map_menu(kwargs.get('has_active_track', False))
        elif menu_type == "settings":
            return self._create_settings_menu()
        elif menu_type == "stats":
            return self._create_stats_menu()
        
    def _create_start_menu(self) -> tuple:
        """Создание стартового меню"""
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data="auth_login")],
            [InlineKeyboardButton("💝 Помочь проекту", callback_data="help_project")],
            [InlineKeyboardButton("❓ О проекте", callback_data="help_about")]
        ]
        
        text = ("👋 Добро пожаловать в Search and Rescue Bot!\n\n"
                "🔍 Это поисково-спасательный бот для координации поисковых операций.\n\n"
                "🔐 Для доступа к функциям бота необходима авторизация.\n"
                "💝 Вы также можете поддержать проект или узнать больше о нас.")
        
        return text, InlineKeyboardMarkup(keyboard)

    def _create_main_menu(self, is_coordinator: bool = False) -> tuple:
        """Создание главного меню"""
        keyboard = [
            [InlineKeyboardButton("🗺 Поиск", callback_data="search_menu")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats_personal")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings_menu")],
            [InlineKeyboardButton("📍 Карта", callback_data="map_menu")]
        ]
        
        if is_coordinator:
            keyboard.insert(1, [
                InlineKeyboardButton("👨‍✈️ Координация", callback_data="coord_menu")
            ])
        
        text = ("🏠 Главное меню\n\n"
                "• 🗺 Поиск - управление поисковыми операциями\n"
                "• 📊 Статистика - просмотр данных и отчетов\n"
                "• ⚙️ Настройки - настройка профиля и доступа\n"
                "• 📍 Карта - работа с картой и треками")
        
        return text, InlineKeyboardMarkup(keyboard)

    def _create_search_menu(self, is_coordinator: bool = False) -> tuple:
        """Создание меню поиска"""
        keyboard = [
            [InlineKeyboardButton("🔍 Создать поиск", callback_data="search_start")],
            [InlineKeyboardButton("➕ Присоединиться к поиску", callback_data="search_join")],
            [InlineKeyboardButton("📋 Активные поиски", callback_data="search_list")]
        ]
        
        if is_coordinator:
            keyboard.insert(1, [
                InlineKeyboardButton("👥 Управление группой", callback_data="search_manage")
            ])
            
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="main_menu")])
        
        text = ("🗺 Меню поиска\n\n"
                "• Создавайте новые поисковые операции\n"
                "• Присоединяйтесь к существующим поискам\n"
                "• Управляйте группами и координируйте действия")
        
        return text, InlineKeyboardMarkup(keyboard)

    def _create_map_menu(self, has_active_track: bool = False) -> tuple:
        """Создание меню карты"""
        keyboard = [
            [InlineKeyboardButton("📍 Начать запись трека", callback_data="map_start_track")],
            [InlineKeyboardButton("📊 Мои треки", callback_data="map_my_tracks")],
            [InlineKeyboardButton("📍 Отправить местоположение", callback_data="map_send_location")],
            [InlineKeyboardButton("🗺 Карта онлайн", callback_data="map_online")]
        ]
        
        if has_active_track:
            keyboard.insert(1, [
                InlineKeyboardButton("⏹ Завершить запись трека", callback_data="map_stop_track")
            ])
            
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="main_menu")])
        
        text = ("📍 Меню карты\n\n"
                "• Записывайте треки своих маршрутов\n"
                "• Отправляйте свое местоположение\n"
                "• Следите за участниками поиска онлайн")
        
        return text, InlineKeyboardMarkup(keyboard)
