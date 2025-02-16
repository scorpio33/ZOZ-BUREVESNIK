import json
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class MapManager:
    @staticmethod
    def create_geojson_feature(geometry: dict, properties: dict = None) -> dict:
        """Создание GeoJSON Feature"""
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties or {}
        }

    @staticmethod
    def create_sector_polygon(points: List[List[float]]) -> dict:
        """Создание полигона сектора"""
        return {
            "type": "Polygon",
            "coordinates": [points + [points[0]]]  # Замыкаем полигон
        }

    @staticmethod
    def point_in_polygon(point: List[float], polygon: List[List[float]]) -> bool:
        """Проверка, находится ли точка внутри полигона"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside