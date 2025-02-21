import logging
from telegram import Update
from telegram.ext import ApplicationBuilder
from core.bot import Bot
from core.handler_registry import HandlerRegistry

logger = logging.getLogger(__name__)

class BotApplication:
    def __init__(self, token: str):
        self.token = token
        self.application = None
        self.bot = None
        self.handler_registry = None
        
    async def setup(self):
        """Initialize bot and register handlers"""
        try:
            # Initialize application
            self.application = ApplicationBuilder().token(self.token).build()
            
            # Initialize bot
            self.bot = Bot(self.application)
            
            # Initialize and register handlers
            self.handler_registry = HandlerRegistry(self.bot)
            await self.handler_registry.register_all_handlers()
            
            logger.info("Bot setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during setup: {e}")
            raise

    async def start(self):
        """Start the bot"""
        try:
            if not self.bot:
                raise ValueError("Bot not initialized. Call setup() first")
                
            await self.bot.start()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
