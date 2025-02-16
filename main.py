import os
import sys
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

async def shutdown(bot: Bot):
    """Cleanup tasks tied to the service's shutdown."""
    logger.info("Shutting down...")
    
    try:
        # Stop the bot
        await bot.stop()
        
        # Cancel all running tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        
        logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Stop the event loop
        loop = asyncio.get_running_loop()
        loop.stop()
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        logger.error(traceback.format_exc())

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
        await shutdown(bot)

if __name__ == '__main__':
    try:
        if sys.platform == 'win32':
            # For Windows, use asyncio.run() which handles signals properly
            asyncio.run(main())
        else:
            # For Unix systems, we can use the traditional signal handlers
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(bot)))
            
            try:
                loop.run_until_complete(main())
            finally:
                loop.close()
                
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
