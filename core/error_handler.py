class ErrorHandler:
    def __init__(self, logger):
        self.logger = logger

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ошибок"""
        try:
            if update.callback_query:
                await update.callback_query.answer(
                    "Произошла ошибка. Попробуйте позже.",
                    show_alert=True
                )
            
            error = context.error
            self.logger.error(f"Update {update} caused error {error}")
            
            # Отправляем уведомление разработчику
            if context.bot_data.get('developer_id'):
                await context.bot.send_message(
                    chat_id=context.bot_data['developer_id'],
                    text=f"❌ Ошибка в боте:\n\n"
                         f"Update: {update}\n"
                         f"Error: {error}"
                )
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")