class Bot:
    def __init__(self, db_manager, menu_manager, auth_manager):
        self.db_manager = db_manager
        self.menu_manager = menu_manager
        self.auth_manager = auth_manager

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        message = update.message
        if not message:
            return
            
        if 'awaiting_password' in context.user_data:
            return await self.auth_manager.check_password(update, context)
            
        # Default message handling
        await message.reply_text("Пожалуйста, используйте меню для навигации")