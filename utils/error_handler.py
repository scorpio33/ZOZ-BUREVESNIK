import logging
from telegram import Update
from telegram.ext import ContextTypes

class ErrorHandler:
    def __init__(self, logger):
        self.logger = logger

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in bot updates"""
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "Произошла ошибка при обработке запроса. Попробуйте позже."
                )
            
            # Log the error
            self.logger.error(f"Update {update} caused error {context.error}")
            
            # Send error notification to developer
            if hasattr(context, 'bot_data') and context.bot_data.get('developer_id'):
                await context.bot.send_message(
                    chat_id=context.bot_data['developer_id'],
                    text=f"❌ Ошибка в боте:\n\n"
                         f"Update: {update}\n"
                         f"Error: {context.error}"
                )
                
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")

def setup_logging():
    """Настройка системы логирования"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('logs/bot.log'),
            logging.StreamHandler()
        ]
    )
