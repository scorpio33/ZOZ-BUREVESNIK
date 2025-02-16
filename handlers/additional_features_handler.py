from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class AdditionalFeaturesHandler:
    def __init__(self, db_manager, achievement_manager, rating_manager, training_manager):
        self.db = db_manager
        self.achievement_manager = achievement_manager
        self.rating_manager = rating_manager
        self.training_manager = training_manager

    async def show_achievements(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ достижений пользователя"""
        user_id = update.effective_user.id
        achievements = await self.achievement_manager.get_user_achievements(user_id)
        
        text = "🏆 Ваши достижения:\n\n"
        for ach in achievements:
            text += f"{ach['icon']} {ach['title']}\n{ach['description']}\n\n"
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="main_menu")]]
        
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ рейтинга пользователей"""
        top_users = await self.rating_manager.get_top_users(10)
        
        text = "🏅 Топ-10 участников:\n\n"
        for i, user in enumerate(top_users, 1):
            text += f"{i}. {user['full_name']}\n"
            text += f"   Рейтинг: {user['rating_points']}\n"
            text += f"   Операций: {user['total_operations']}\n\n"
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="main_menu")]]
        
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_training(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ обучающих материалов"""
        user_id = update.effective_user.id
        courses = await self.training_manager.get_available_courses(user_id)
        
        keyboard = []
        for course in courses:
            status = "✅ " if course['status'] == 'completed' else "📚 "
            keyboard.append([InlineKeyboardButton(
                f"{status}{course['title']} (Уровень {course['difficulty_level']})",
                callback_data=f"course_{course['material_id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="main_menu")])
        
        await update.callback_query.message.edit_text(
            "📚 Обучающие материалы\n"
            "Выберите курс для изучения:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )