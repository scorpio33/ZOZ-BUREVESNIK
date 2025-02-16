from typing import Any, Optional
import redis
import json

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.default_ttl = 3600  # 1 час

    async def get(self, key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        data = self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Сохранение данных в кэш"""
        ttl = ttl or self.default_ttl
        return self.redis.setex(key, ttl, json.dumps(value))

    async def invalidate(self, pattern: str) -> None:
        """Инвалидация кэша по паттерну"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)