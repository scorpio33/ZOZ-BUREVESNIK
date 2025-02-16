import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram.ext import Application
from core.bot import Bot
from core.application import BotApplication

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)

async def main() -> None:
    try:
        # Load environment variables
        load_dotenv()
        token = os.getenv('BOT_TOKEN')
        
        if not token:
            raise ValueError("Bot token not found in environment variables")
            
        # Initialize bot application
        bot_app = BotApplication(token)
        await bot_app.setup()
        await bot_app.start()
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
