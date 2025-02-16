import os
from datetime import timedelta
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Security settings
JWT_SECRET_KEY = "your-secret-key-here"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = 24 * 60 * 60
JWT_ACCESS_TOKEN_EXPIRE = timedelta(seconds=JWT_EXPIRATION_DELTA)
JWT_REFRESH_TOKEN_EXPIRE = timedelta(days=7)

# Bot settings
BOT_TOKEN = os.getenv('BOT_TOKEN')
DEVELOPER_ID = int(os.getenv('DEVELOPER_ID', 991426127))
DEVELOPER_CODE = os.getenv('DEVELOPER_CODE', 'TRAMP708090')
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD', 'KREML')

# Database settings
DATABASE_PATH = "bot_database.db"

# Email settings
SMTP_SERVER = os.getenv('SMTP_SERVER', "smtp.gmail.com")
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', "your-email@gmail.com")  # Изменено с USERNAME на USER
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', "your-app-password")

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'storage/logs/bot.log')

# Payment settings
PAYMENT_SETTINGS = {
    'TON_WALLET': os.getenv('TON_WALLET'),
    'USDT_WALLET': os.getenv('USDT_WALLET')
}

# API settings
CRYPTO_BOT_API_KEY = os.getenv('CRYPTO_BOT_API_KEY')
MAPS_API_KEY = os.getenv('MAPS_API_KEY')

# API Keys
SMS_API_KEY = "your_sms_api_key"  # Replace with actual key or environment variable

# Session settings
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hour by default
