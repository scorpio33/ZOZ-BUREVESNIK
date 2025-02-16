import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot settings
    TOKEN = os.getenv('BOT_TOKEN')
    DEVELOPER_ID = int(os.getenv('DEVELOPER_ID', 991426127))
    DEVELOPER_CODE = os.getenv('DEVELOPER_CODE', 'TRAMP708090')
    DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD', 'KREML')
    
    def __init__(self):
        if not self.TOKEN:
            raise ValueError("BOT_TOKEN environment variable is not set")
    
    # API Keys
    YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
    CRYPTO_BOT_API_KEY = os.getenv('CRYPTO_BOT_API_KEY')
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'bot_database.db')
    
    # Paths configuration
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MAPS_DIR = os.path.join(BASE_DIR, 'storage', 'maps')
    CACHE_DIR = os.path.join(BASE_DIR, 'storage', 'cache')
    LOGS_DIR = os.path.join(BASE_DIR, 'storage', 'logs')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Map settings
    MAP_DEFAULT_CENTER_LAT = float(os.getenv('MAP_DEFAULT_CENTER_LAT', '55.7558'))
    MAP_DEFAULT_CENTER_LON = float(os.getenv('MAP_DEFAULT_CENTER_LON', '37.6173'))
    MAP_DEFAULT_ZOOM = int(os.getenv('MAP_DEFAULT_ZOOM', '10'))
    
    # Payment settings
    TON_WALLET = os.getenv('TON_WALLET')
    USDT_WALLET = os.getenv('USDT_WALLET')
