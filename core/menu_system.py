from dataclasses import dataclass
from typing import List, Dict, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

@dataclass
class MenuItem:
    text: str
    callback_data: str
    children: Optional[List['MenuItem']] = None

class MenuSystem:
    def __init__(self):
        self.menus: Dict[str, List[MenuItem]] = {
            'start': [
                MenuItem("🔐 Авторизация", "auth"),  # Изменено на "auth" для соответствия старой логике
                MenuItem("💝 Помочь проекту", "help_project"),
                MenuItem("❓ О проекте", "about")
            ],
            'main': [
                MenuItem("🗺 Поиск", "search_menu"),
                MenuItem("📊 Статистика", "stats_menu"),
                MenuItem("⚙️ Настройки", "settings_menu"),
                MenuItem("📍 Карта", "map_menu")
            ],
            'help_project': [
                MenuItem("💎 TON", "donate_ton"),
                MenuItem("💵 USDT", "donate_usdt"),
                MenuItem("« Назад", "back_to_start")
            ]
        }

    def get_start_keyboard(self) -> InlineKeyboardMarkup:
        """Get keyboard for start menu"""
        keyboard = []
        for item in self.menus['start']:
            keyboard.append([InlineKeyboardButton(item.text, callback_data=item.callback_data)])
        return InlineKeyboardMarkup(keyboard)

    def get_keyboard(self, menu_id: str) -> InlineKeyboardMarkup:
        """Get keyboard for specified menu"""
        if menu_id not in self.menus:
            return InlineKeyboardMarkup([[
                InlineKeyboardButton("« Главное меню", callback_data="back_to_start")
            ]])
        
        items = self.menus[menu_id]
        keyboard = []
        row = []
        
        for item in items:
            row.append(InlineKeyboardButton(item.text, callback_data=item.callback_data))
            if len(row) == 2:  # Максимум 2 кнопки в ряду
                keyboard.append(row)
                row = []
                
        if row:  # Добавляем оставшиеся кнопки
            keyboard.append(row)
            
        # Добавляем кнопку "Назад" для всех меню кроме стартового
        if menu_id != 'start':
            keyboard.append([InlineKeyboardButton("« Назад", callback_data="back_to_start")])
            
        return InlineKeyboardMarkup(keyboard)

    def get_menu_text(self, menu_id: str) -> str:
        """Get text for specified menu"""
        texts = {
            'start': "Добро пожаловать! Выберите действие:",
            'main': "Главное меню:",
            'search': "Меню поиска:",
            'stats': "Статистика:",
            'settings': "Настройки:",
            'map': "Карта:",
            'help_project': "Выберите способ поддержки проекта:",
            'about': "О проекте:"
        }
        return texts.get(menu_id, "Выберите действие:")
