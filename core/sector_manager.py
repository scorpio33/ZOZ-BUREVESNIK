from typing import Dict, List, Optional
from datetime import datetime
import json
import logging
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from .notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class SectorManager:
    def __init__(self, db_manager, notification_manager: NotificationManager, map_service):
        self.db = db_manager
        self.notification_manager = notification_manager
        self.map_service = map_service

    async def create_sector(self, operation_id: int, data: Dict) -> Optional[int]:
        """Создание нового сектора с расширенными параметрами"""
        try:
            # Валидация границ сектора
            boundaries = data['boundaries']
            if len(boundaries) < 3:
                logger.error("Invalid sector boundaries: less than 3 points")
                return None

            polygon = Polygon(boundaries)
            if not polygon.is_valid:
                logger.error("Invalid polygon boundaries")
                return None

            # Создаем GeoJSON для границ
            geojson = {
                'type': 'Polygon',
                'coordinates': [boundaries + [boundaries[0]]]  # Замыкаем полигон
            }

            # Вычисляем сложность сектора на основе рельефа
            difficulty = await self._calculate_sector_difficulty(boundaries)

            sector_id = await self.db.execute("""
                INSERT INTO search_sectors 
                (operation_id, name, boundaries, priority, difficulty, 
                terrain_type, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
                RETURNING sector_id
            """, (
                operation_id,
                data['name'],
                json.dumps(geojson),
                data.get('priority', 1),
                difficulty,
                data.get('terrain_type', 'unknown')
            ))

            if sector_id:
                await self.notification_manager.notify_coordinators(
                    f"🆕 Создан новый сектор '{data['name']}' в операции #{operation_id}"
                )
                # Генерируем превью карты сектора
                await self.map_service.generate_sector_preview(sector_id, boundaries)

            return sector_id

        except Exception as e:
            logger.error(f"Error creating sector: {e}")
            return None

    def get_sector_coverage(self, sector_id: int) -> float:
        """Получение процента покрытия сектора"""
        try:
            # Получаем границы сектора
            sector = self.db.get_sector(sector_id)
            if not sector:
                return 0.0

            # Получаем все треки в этом секторе
            tracks = self.db.get_sector_tracks(sector_id)
            
            # Создаем полигон сектора
            sector_bounds = json.loads(sector['boundaries'])
            sector_polygon = Polygon(sector_bounds['coordinates'][0])
            
            # Создаем буферы для треков (покрытая область)
            covered_areas = []
            for track in tracks:
                points = json.loads(track['points_json'])
                track_line = [Point(p['lon'], p['lat']) for p in points]
                # Создаем буфер 50 метров вокруг каждой точки трека
                for point in track_line:
                    covered_areas.append(point.buffer(0.00045))  # ~50 метров

            if not covered_areas:
                return 0.0

            # Объединяем все покрытые области
            covered_union = unary_union(covered_areas)
            
            # Вычисляем процент покрытия
            coverage = (covered_union.intersection(sector_polygon).area / 
                      sector_polygon.area) * 100
            
            return min(100.0, coverage)
        except Exception as e:
            logger.error(f"Error calculating sector coverage: {e}")
            return 0.0

    async def update_sector_boundaries(self, sector_id: int, new_boundaries: List[tuple]) -> bool:
        """Обновление границ сектора"""
        try:
            polygon = Polygon(new_boundaries)
            if not polygon.is_valid:
                return False

            geojson = {
                'type': 'Polygon',
                'coordinates': [new_boundaries + [new_boundaries[0]]]
            }

            success = await self.db.execute("""
                UPDATE search_sectors 
                SET boundaries = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE sector_id = ?
            """, (json.dumps(geojson), sector_id))

            if success:
                await self.map_service.generate_sector_preview(sector_id, new_boundaries)
                await self.notification_manager.notify_sector_teams(
                    sector_id, 
                    "🔄 Границы сектора были обновлены"
                )

            return success

        except Exception as e:
            logger.error(f"Error updating sector boundaries: {e}")
            return False

    async def assign_team_to_sector(self, sector_id: int, team_id: int) -> bool:
        """Назначение команды на сектор"""
        try:
            # Проверяем, не занят ли сектор
            current_team = await self.db.fetchone(
                "SELECT assigned_team FROM search_sectors WHERE sector_id = ?",
                (sector_id,)
            )

            if current_team and current_team['assigned_team']:
                logger.warning(f"Sector {sector_id} already has assigned team")
                return False

            success = await self.db.execute("""
                UPDATE search_sectors 
                SET assigned_team = ?,
                    status = 'in_progress',
                    last_searched = CURRENT_TIMESTAMP
                WHERE sector_id = ?
            """, (team_id, sector_id))

            if success:
                await self.notification_manager.notify_team(
                    team_id,
                    f"📍 Ваша команда назначена на новый сектор"
                )

            return success

        except Exception as e:
            logger.error(f"Error assigning team to sector: {e}")
            return False

    async def update_sector_progress(self, sector_id: int, team_id: int, coverage: float) -> bool:
        """Обновление прогресса поиска в секторе"""
        try:
            await self.db.execute("""
                INSERT INTO sector_progress 
                (sector_id, team_id, coverage_percent, search_date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (sector_id, team_id, coverage))

            # Обновляем общий прогресс сектора
            total_coverage = await self._calculate_total_coverage(sector_id)
            await self.db.execute("""
                UPDATE search_sectors 
                SET progress = ?,
                    status = CASE WHEN ? >= 100 THEN 'completed' ELSE 'in_progress' END
                WHERE sector_id = ?
            """, (total_coverage, total_coverage, sector_id))

            return True

        except Exception as e:
            logger.error(f"Error updating sector progress: {e}")
            return False

    async def _calculate_sector_difficulty(self, boundaries: List[tuple]) -> str:
        """Расчет сложности сектора на основе рельефа"""
        try:
            # Здесь можно добавить интеграцию с API карт для получения данных о рельефе
            # Пока возвращаем стандартное значение
            return 'normal'
        except Exception as e:
            logger.error(f"Error calculating sector difficulty: {e}")
            return 'normal'

    async def _calculate_total_coverage(self, sector_id: int) -> float:
        """Расчет общего прогресса поиска в секторе"""
        try:
            result = await self.db.fetchone("""
                SELECT AVG(coverage_percent) as avg_coverage
                FROM sector_progress
                WHERE sector_id = ?
                GROUP BY sector_id
            """, (sector_id,))
            
            return result['avg_coverage'] if result else 0.0

        except Exception as e:
            logger.error(f"Error calculating total coverage: {e}")
            return 0.0
