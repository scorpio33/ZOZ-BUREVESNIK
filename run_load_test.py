import asyncio
import logging
from tests.load_testing import main
from config.config import Config

# Проверяем наличие токена
config = Config()
if not config.TOKEN:
    logging.error("Bot token not found in config!")
    exit(1)

if __name__ == "__main__":
    asyncio.run(main())
