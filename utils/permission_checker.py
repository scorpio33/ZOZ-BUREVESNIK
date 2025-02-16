from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

def check_coordinator_permission(permission: str):
    """Декоратор для проверки прав координатора"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            
            # Проверяем наличие права у координатора
            has_permission = await self.db.execute_query_fetchone("""
                SELECT 1 FROM coordinator_permissions
                WHERE coordinator_id = ? AND permission = ?
            """, (user_id, permission))
            
            if not has_permission:
                await update.callback_query.answer(
                    "⚠️ У вас нет прав для выполнения этого действия",
                    show_alert=True
                )
                return
            
            return await func(self, update, context, *args, **kwargs)
        return wrapper
    return decorator

def check_coordinator_status(func):
    """Декоратор для проверки статуса координатора"""
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        is_coordinator = await self.db.execute_query_fetchone(
            "SELECT is_coordinator FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        if not is_coordinator or not is_coordinator['is_coordinator']:
            await update.callback_query.answer(
                "⚠️ Эта функция доступна только координаторам",
                show_alert=True
            )
            return
        
        return await func(self, update, context, *args, **kwargs)
    return wrapper
