import os
import asyncio
import signal
import logging
import traceback
from dotenv import load_dotenv
from core.bot import Bot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def shutdown(bot: Bot, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logger.info(f"Received exit signal {signal.name}")
    
    logger.info("Shutting down...")
    await bot.stop()

async def main() -> None:
    """Main function to run the bot"""
    try:
        # Load environment variables
        load_dotenv()
        token = os.getenv('BOT_TOKEN')
        
        if not token:
            raise ValueError("Bot token not found in environment variables")
        
        logger.info(f"Starting bot with token: {token[:5]}...")
        
        # Initialize bot
        bot = Bot(token)
        
        # Handle shutdown signals
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(shutdown(bot, sig))
            )
        
        # Start bot
        logger.info("Starting bot...")
        await bot.start()
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        if 'loop' in locals():
            loop.remove_signal_handler(signal.SIGTERM)
            loop.remove_signal_handler(signal.SIGINT)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
