import logging
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters

logger = logging.getLogger(__name__)

class HandlerRegistry:
    def __init__(self, bot):
        self.bot = bot
        
    async def register_all_handlers(self):
        """Register all handlers"""
        try:
            # Register command handlers
            self.bot.application.add_handler(
                CommandHandler("start", self.bot.start_command)
            )
            
            # Register callback query handler
            self.bot.application.add_handler(
                CallbackQueryHandler(self.bot.button_callback)
            )
            
            # Register message handler
            self.bot.application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.bot.handle_message
                )
            )
            
            logger.info("All handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering handlers: {e}")
            raise
