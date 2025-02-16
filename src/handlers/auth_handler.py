from telegram import Update
from telegram.ext import ContextTypes
from src.core.states import States
from src.core.auth_manager import AuthManager

class AuthHandler:
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager

    async def handle_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle password input"""
        user_id = update.effective_user.id
        password = update.message.text

        is_valid = await self.auth_manager.verify_password(user_id, password)
        
        if is_valid:
            context.user_data['state'] = States.MAIN_MENU
            context.user_data['authorized'] = True  # Добавляем флаг авторизации
            await update.message.reply_text("✅ Авторизация успешна!")
            return States.MAIN_MENU
        else:
            await update.message.reply_text("❌ Неверный пароль. Попробуйте снова.")
            return States.WAITING_FOR_PASSWORD
