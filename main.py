import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from core.bot import Bot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

async def main():
    """Основная функция запуска бота"""
    try:
        # Получаем токен из переменных окружения
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("BOT_TOKEN not found in environment variables")
            return

        # Создаем приложение и бота
        application = ApplicationBuilder().token(token).build()
        bot = Bot(application)
        
        # Добавляем обработчик диалогов
        application.add_handler(bot.get_conversation_handler())
        
        # Запускаем бота
        logger.info("Starting bot...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

def run_bot():
    """Wrapper для запуска бота"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

if __name__ == '__main__':
    run_bot()
