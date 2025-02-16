import os
import hashlib
import requests
from typing import Tuple, List, Optional
import sqlite3
from datetime import datetime, timedelta
import threading

class MapCacheService:
    def __init__(self, cache_dir: str = "cache/maps"):
        self.cache_dir = cache_dir
        self.db_path = os.path.join(cache_dir, "tile_cache.db")
        self.cache_lock = threading.Lock()
        self.init_cache()
        
    def init_cache(self):
        """Инициализация кэша"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tiles (
                    tile_key TEXT PRIMARY KEY,
                    data BLOB,
                    timestamp DATETIME,
                    expires DATETIME
                )
            """)
    
    def get_tile(self, z: int, x: int, y: int, source: str = 'osm') -> bytes:
        """Получение тайла карты с учетом кэша"""
        tile_key = self._make_tile_key(z, x, y, source)
        
        with self.cache_lock:
            cached_tile = self._get_cached_tile(tile_key)
            if cached_tile:
                return cached_tile
            
            tile_data = self._download_tile(z, x, y, source)
            if tile_data:
                self._cache_tile(tile_key, tile_data)
                return tile_data
            
            return self._get_fallback_tile()
    
    def _make_tile_key(self, z: int, x: int, y: int, source: str) -> str:
        """Создание уникального ключа для тайла"""
        return hashlib.md5(f"{source}/{z}/{x}/{y}".encode()).hexdigest()
    
    def _get_cached_tile(self, tile_key: str) -> Optional[bytes]:
        """Получение тайла из кэша"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data, expires FROM tiles WHERE tile_key = ?", 
                (tile_key,)
            )
            result = cursor.fetchone()
            
            if result and result[1] and datetime.fromisoformat(result[1]) > datetime.now():
                return result[0]
        return None

    def _download_tile(self, z: int, x: int, y: int, source: str) -> Optional[bytes]:
        """Загрузка тайла с сервера"""
        try:
            url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Error downloading tile: {e}")
        return None

    def _cache_tile(self, tile_key: str, data: bytes, ttl: int = 86400):
        """Сохранение тайла в кэш"""
        expires = datetime.now() + timedelta(seconds=ttl)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tiles (tile_key, data, timestamp, expires) VALUES (?, ?, ?, ?)",
                (tile_key, data, datetime.now().isoformat(), expires.isoformat())
            )

    def _get_fallback_tile(self) -> bytes:
        """Получение резервного тайла при ошибке"""
        # Здесь можно вернуть пустой или дефолтный тайл
        return b''  # Пустой тайл
