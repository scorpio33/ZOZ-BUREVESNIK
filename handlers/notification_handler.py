import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class NotificationHandler:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def show_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать уведомления пользователя"""
        user_id = update.effective_user.id
        notifications = await self.db.get_user_notifications(user_id)
        
        if not notifications:
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="main_menu")]]
            await update.callback_query.message.edit_text(
                "📭 У вас нет новых уведомлений",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        text = "📬 Ваши уведомления:\n\n"
        keyboard = []
        
        for notif in notifications:
            text += f"• {notif['message']}\n"
            if not notif['read']:
                keyboard.append([InlineKeyboardButton(
                    f"✓ Прочитано ({notif['id']})", 
                    callback_data=f"notif_read_{notif['id']}"
                )])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="main_menu")])
        
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def mark_as_read(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отметить уведомление как прочитанное"""
        query = update.callback_query
        notification_id = int(query.data.split('_')[-1])
        
        await self.db.mark_notification_read(notification_id)
        await self.show_notifications(update, context)