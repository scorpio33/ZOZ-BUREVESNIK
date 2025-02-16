import os
import sys
import asyncio
import logging
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

async def main() -> None:
    """Main function to run the bot"""
    try:
        # Load environment variables
        load_dotenv()
        token = os.getenv('BOT_TOKEN')
        
        if not token:
            raise ValueError("Bot token not found in environment variables")
        
        logger.info(f"Starting bot with token: {token[:5]}...")
        
        # Initialize and start bot
        bot = Bot(token)
        await bot.start()
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        # Use asyncio.run() for proper event loop management
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
