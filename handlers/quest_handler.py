import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.quests import QUEST_CATEGORIES, QUESTS, LEVEL_THRESHOLDS, LEVEL_REWARDS
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class QuestHandler:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def show_quest_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню квестов"""
        user_id = update.effective_user.id
        user = await self.db.get_user(user_id)
        
        keyboard = []
        for category_id, category_name in QUEST_CATEGORIES.items():
            available_quests = await self._get_available_quests(user_id, category_id)
            if available_quests:
                keyboard.append([InlineKeyboardButton(
                    f"{category_name} ({len(available_quests)})", 
                    callback_data=f"quest_category_{category_id}"
                )])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="settings_menu")])
        
        text = (
            f"📋 Доступные квесты\n\n"
            f"Уровень: {user['level']}\n"
            f"Опыт: {user['experience']}/{LEVEL_THRESHOLDS[user['level'] + 1]}\n"
            f"Монеты: {user['coins']}\n\n"
            f"Выберите категорию квестов:"
        )
        
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_category_quests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать квесты выбранной категории"""
        query = update.callback_query
        category_id = query.data.split('_')[-1]
        user_id = update.effective_user.id
        
        available_quests = await self._get_available_quests(user_id, category_id)
        
        keyboard = []
        for quest in available_quests:
            status = await self._get_quest_status(user_id, quest['quest_id'])
            icon = self._get_status_icon(status)
            keyboard.append([InlineKeyboardButton(
                f"{icon} {quest['title']}", 
                callback_data=f"quest_view_{quest['quest_id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="quest_menu")])
        
        await query.message.edit_text(
            f"📋 {QUEST_CATEGORIES[category_id]}\n"
            f"Доступные задания:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_quest_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, quest_id: str):
        """Показать детали квеста"""
        quest = QUESTS[quest_id]
        user_id = update.effective_user.id
        status = await self._get_quest_status(user_id, quest_id)
        progress = await self._get_quest_progress(user_id, quest_id)
        
        keyboard = []
        if status == 'available':
            keyboard.append([InlineKeyboardButton("▶️ Начать", callback_data=f"quest_start_{quest_id}")])
        elif status == 'in_progress':
            keyboard.append([InlineKeyboardButton("✅ Завершить", callback_data=f"quest_complete_{quest_id}")])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data=f"quest_category_{quest['category']}")])
        
        text = (
            f"📋 {quest['title']}\n\n"
            f"{quest['description']}\n\n"
            f"💫 Награды:\n"
            f"• Опыт: {quest['reward_exp']}\n"
            f"• Монеты: {quest['reward_coins']}\n\n"
            f"📊 Прогресс: {progress}%\n"
            f"Статус: {self._get_status_text(status)}"
        )
        
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_quest_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка действий с квестами"""
        query = update.callback_query
        action = query.data.split('_')[1]
        quest_id = query.data.split('_')[2]
        user_id = update.effective_user.id
        
        if action == 'start':
            await self._start_quest(user_id, quest_id)
            await self.show_quest_details(update, context, quest_id)
        
        elif action == 'complete':
            if await self._check_quest_completion(user_id, quest_id):
                await self._complete_quest(user_id, quest_id)
                await self._show_completion_message(update, context, quest_id)
            else:
                await query.answer("❌ Условия выполнения не соблюдены")

    async def _get_available_quests(self, user_id: int, category: str) -> list:
        """Получить доступные квесты для пользователя"""
        user = await self.db.get_user(user_id)
        available = []
        
        for quest_id, quest in QUESTS.items():
            if quest['category'] == category and user['level'] >= quest['required_level']:
                available.append({**quest, 'quest_id': quest_id})
        
        return available

    async def _get_quest_status(self, user_id: int, quest_id: str) -> str:
        """Получить статус квеста"""
        return await self.db.get_quest_status(user_id, quest_id)

    async def _get_quest_progress(self, user_id: int, quest_id: str) -> int:
        """Получить прогресс выполнения квеста"""
        return await self.db.get_quest_progress(user_id, quest_id)

    def _get_status_icon(self, status: str) -> str:
        """Получить иконку статуса"""
        icons = {
            'available': '⭐️',
            'in_progress': '▶️',
            'completed': '✅',
            'failed': '❌'
        }
        return icons.get(status, '❓')

    def _get_status_text(self, status: str) -> str:
        """Получить текст статуса"""
        texts = {
            'available': 'Доступен',
            'in_progress': 'В процессе',
            'completed': 'Завершен',
            'failed': 'Провален'
        }
        return texts.get(status, 'Неизвестно')
