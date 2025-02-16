from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class TrainingHandler:
    def __init__(self, training_manager):
        self.training_manager = training_manager

    async def show_training_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню обучения"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Получаем прогресс пользователя
        progress = await self.training_manager.get_course_progress(user_id)
        
        text = (
            "📚 Система обучения\n\n"
            f"✅ Завершено курсов: {progress['completed_courses']}/{progress['total_courses']}\n"
            f"📊 Средний балл: {progress['avg_score']:.1f}%\n"
            f"🏆 Всего очков: {progress['total_points']}\n\n"
            "Выберите действие:"
        )
        
        keyboard = [
            [InlineKeyboardButton("📖 Доступные курсы", callback_data="training_courses")],
            [InlineKeyboardButton("📊 Мой прогресс", callback_data="training_progress")],
            [InlineKeyboardButton("🏆 Рейтинг учеников", callback_data="training_leaderboard")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_available_courses(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ доступных курсов"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Получаем уровень пользователя
        user = await self.db.get_user(user_id)
        courses = await self.training_manager.get_available_courses(user_id, user['level'])
        
        if not courses:
            await query.message.edit_text(
                "📚 На данный момент нет доступных курсов для вашего уровня.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="training_menu")
                ]])
            )
            return

        text = "📚 Доступные курсы:\n\n"
        keyboard = []
        
        for course in courses:
            status_emoji = {
                'not_started': '⚪️',
                'in_progress': '🔵',
                'completed': '✅'
            }.get(course['status'], '⚪️')
            
            text += (f"{status_emoji} {course['title']}\n"
                    f"└ Уровень: {course['required_level']}, "
                    f"Очки: {course['points']}\n\n")
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_emoji} {course['title']}", 
                    callback_data=f"course_{course['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="training_menu")])
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )