import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from services.yandex_maps_service import YandexMapsService

logger = logging.getLogger(__name__)

class TrackingService:
    def __init__(self, db_manager, map_service: YandexMapsService):
        self.db = db_manager
        self.map_service = map_service
        self.active_tracks = {}  # user_id: track_data
        self.live_tracking = {}  # group_id: {user_id: location}

    async def start_tracking(self, user_id: int, group_id: int) -> bool:
        """Начало отслеживания пользователя"""
        try:
            track_id = await self.db.create_track(user_id, group_id)
            self.active_tracks[user_id] = {
                'track_id': track_id,
                'points': [],
                'start_time': datetime.now()
            }
            return True
        except Exception as e:
            logger.error(f"Error starting tracking: {e}")
            return False

    async def update_location(self, user_id: int, location: Dict) -> bool:
        """Обновление местоположения пользователя"""
        try:
            # Обновляем активный трек
            if user_id in self.active_tracks:
                track_data = self.active_tracks[user_id]
                track_data['points'].append({
                    'lat': location['latitude'],
                    'lon': location['longitude'],
                    'timestamp': datetime.now().isoformat()
                })
                
                # Сохраняем точку в БД
                await self.db.add_track_point(
                    track_data['track_id'],
                    location['latitude'],
                    location['longitude']
                )

            # Обновляем live-позицию в группе
            group_id = await self.db.get_user_active_group(user_id)
            if group_id:
                if group_id not in self.live_tracking:
                    self.live_tracking[group_id] = {}
                self.live_tracking[group_id][user_id] = location
                
                # Обновляем карту группы
                await self._update_group_map(group_id)
            
            return True
        except Exception as e:
            logger.error(f"Error updating location: {e}")
            return False

    async def _update_group_map(self, group_id: int):
        """Обновление карты группы"""
        try:
            if group_id in self.live_tracking:
                locations = self.live_tracking[group_id]
                map_data = await self.map_service.create_group_map(locations)
                
                # Сохраняем карту
                await self.db.update_group_map(group_id, map_data)
                
                # Уведомляем участников группы
                await self._notify_group_members(group_id, "Карта обновлена")
        except Exception as e:
            logger.error(f"Error updating group map: {e}")

    async def stop_tracking(self, user_id: int) -> Optional[Dict]:
        """Завершение отслеживания"""
        try:
            if user_id in self.active_tracks:
                track_data = self.active_tracks[user_id]
                
                # Сохраняем финальные данные трека
                await self.db.complete_track(
                    track_data['track_id'],
                    track_data['points']
                )
                
                # Генерируем статистику
                stats = await self._generate_track_stats(track_data)
                
                del self.active_tracks[user_id]
                return stats
            return None
        except Exception as e:
            logger.error(f"Error stopping tracking: {e}")
            return None