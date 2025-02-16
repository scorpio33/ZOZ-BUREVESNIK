import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройки Yandex Maps
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "ваш_ключ_api")
MAP_UPDATE_INTERVAL = 30  # Интервал обновления в секундах
MAP_DEFAULT_ZOOM = 13
MAP_TILE_SIZE = (650, 450)

# Центр карты по умолчанию (Москва)
MAP_CENTER = [55.7558, 37.6173]
MAP_ZOOM = 10

# Настройки отслеживания
TRACKING_TIMEOUT = 3600  # Тайм-аут отслеживания в секундах
MIN_DISTANCE_DELTA = 10  # Минимальное изменение позиции в метрах для обновления
ACCURACY_THRESHOLD = 100  # Максимальная погрешность в метрах

# Настройки кэширования карт
CACHE_LIFETIME = 86400  # Время жизни кэша в секундах (24 часа)
MAX_CACHE_SIZE = 1024 * 1024 * 100  # Максимальный размер кэша (100 МБ)

# Настройки отображения
MAP_STYLES = {
    'default': 'map',
    'satellite': 'sat',
    'hybrid': 'sat,skl'
}

# Настройки маркеров
MARKER_COLORS = {
    'default': 'blue',
    'start': 'green',
    'finish': 'red',
    'point': 'orange',
    'user': 'purple'
}

# Настройки слоев
LAYER_OPTIONS = {
    'tracks': True,
    'points': True,
    'users': True,
    'sectors': True
}

# Лимиты API
API_REQUESTS_LIMIT = 500  # Максимальное количество запросов в день
API_REQUESTS_INTERVAL = 1  # Минимальный интервал между запросами в секундах

# Форматы экспорта
EXPORT_FORMATS = ['gpx', 'kml', 'geojson']
