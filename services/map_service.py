import logging
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config.api_config import YANDEX_API_KEY, MAP_CENTER, MAP_ZOOM
import folium
from folium import plugins
import io
from PIL import Image
import numpy as np
import math
import aiohttp

logger = logging.getLogger(__name__)

class MapService:
    def __init__(self):
        self.api_key = YANDEX_API_KEY
        self.api_url = "https://api.maps.yandex.ru/2.1"
        
    async def get_address_by_coords(self, lat: float, lon: float) -> Optional[str]:
        """Получение адреса по координатам"""
        params = {
            "apikey": self.api_key,
            "format": "json",
            "geocode": f"{lon},{lat}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_url}/geocode", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["name"]
                return None

    def create_search_map(self, points: List[Dict], sectors: List[Dict]) -> str:
        """Создание карты с точками и секторами поиска"""
        m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM)
        
        # Добавляем точки
        for point in points:
            folium.Marker(
                location=[point["lat"], point["lon"]],
                popup=point["description"],
                icon=folium.Icon(color=point["color"], icon='info-sign')
            ).add_to(m)
        
        # Добавляем сектора поиска
        for sector in sectors:
            folium.Polygon(
                locations=sector["coordinates"],
                popup=sector["name"],
                color=sector["color"],
                fill=True
            ).add_to(m)
        
        return m._repr_html_()

    async def calculate_route(self, start: tuple, end: tuple) -> Optional[Dict]:
        """Расчет маршрута между точками"""
        params = {
            "apikey": self.api_key,
            "mode": "routes",
            "lang": "ru_RU",
            "waypoints": f"{start[0]},{start[1]}|{end[0]},{end[1]}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_url}/route", params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
