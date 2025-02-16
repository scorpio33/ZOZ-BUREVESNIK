import sqlite3
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OfflineManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.offline_db_path = os.path.join(cache_dir, "offline_data.db")
        self.pending_sync = []
        self._init_offline_storage()

    def _init_offline_storage(self):
        """Инициализация локального хранилища"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        with sqlite3.connect(self.offline_db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS offline_routes (
                    route_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    points TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP,
                    synced INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS offline_maps (
                    tile_id TEXT PRIMARY KEY,
                    zoom_level INTEGER,
                    x INTEGER,
                    y INTEGER,
                    data BLOB,
                    downloaded_at TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    data TEXT,
                    created_at TIMESTAMP,
                    attempts INTEGER DEFAULT 0
                );
            """)

    def save_route(self, user_id: int, points: List[Dict], metadata: Dict) -> str:
        """Сохранение маршрута в офлайн-хранилище"""
        route_id = f"route_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with sqlite3.connect(self.offline_db_path) as conn:
            conn.execute(
                "INSERT INTO offline_routes (route_id, user_id, points, metadata, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (route_id, user_id, json.dumps(points), json.dumps(metadata), 
                 datetime.now().isoformat())
            )
        return route_id

    def get_offline_routes(self, user_id: int) -> List[Dict]:
        """Получение сохраненных маршрутов пользователя"""
        with sqlite3.connect(self.offline_db_path) as conn:
            cursor = conn.execute(
                "SELECT route_id, points, metadata, created_at FROM offline_routes "
                "WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            routes = []
            for row in cursor:
                routes.append({
                    'route_id': row[0],
                    'points': json.loads(row[1]),
                    'metadata': json.loads(row[2]),
                    'created_at': row[3]
                })
            return routes

    def add_to_sync_queue(self, type: str, data: Dict):
        """Добавление данных в очередь синхронизации"""
        with sqlite3.connect(self.offline_db_path) as conn:
            conn.execute(
                "INSERT INTO sync_queue (type, data, created_at) VALUES (?, ?, ?)",
                (type, json.dumps(data), datetime.now().isoformat())
            )

    async def sync_pending_data(self):
        """Синхронизация отложенных данных с сервером"""
        with sqlite3.connect(self.offline_db_path) as conn:
            cursor = conn.execute(
                "SELECT id, type, data FROM sync_queue WHERE attempts < 3"
            )
            for row in cursor:
                try:
                    # Здесь будет логика синхронизации с сервером
                    sync_id, sync_type, sync_data = row
                    # После успешной синхронизации удаляем запись
                    conn.execute("DELETE FROM sync_queue WHERE id = ?", (sync_id,))
                except Exception as e:
                    logger.error(f"Sync error for id {row[0]}: {e}")
                    conn.execute(
                        "UPDATE sync_queue SET attempts = attempts + 1 WHERE id = ?",
                        (row[0],)
                    )