import logging
import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, token: str):
        """Initialize bot instance"""
        self.token = token
        self.application: Optional[Application] = None
        self._running = False

    async def initialize(self) -> None:
        """Initialize the application"""
        if not self.application:
            self.application = (
                ApplicationBuilder()
                .token(self.token)
                .build()
            )
            await self._register_handlers()
            await self.application.initialize()

    async def _register_handlers(self) -> None:
        """Register all message handlers"""
        if not self.application:
            return

        # Register error handler
        self.application.add_error_handler(self._error_handler)
        
        # Register command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        # Add other handlers here...

    async def start(self) -> None:
        """Start the bot"""
        try:
            await self.initialize()
            if not self.application:
                raise RuntimeError("Application not initialized")

            self._running = True
            logger.info("Starting bot...")
            
            # Start the bot properly
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            
            # Keep the bot running
            while self._running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the bot gracefully"""
        if not self.application:
            return

        try:
            self._running = False
            logger.info("Stopping bot...")

            # Stop the updater if it's running
            if self.application.updater and self.application.updater.running:
                await self.application.updater.stop()

            # Stop and shutdown the application
            await self.application.stop()
            await self.application.shutdown()
            
            logger.info("Bot stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
            raise

    async def _error_handler(
        self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle errors in the telegram bot"""
        logger.error(f"Update {update} caused error {context.error}")

    async def _start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /start command"""
        if not update.effective_chat:
            return
            
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Привет! Я бот для поиска."
        )
