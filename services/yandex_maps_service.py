import logging
from typing import Dict, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

class YandexMapsService:
    def __init__(self, api_key: str):
        """
        Инициализация сервиса Яндекс.Карт
        :param api_key: API ключ для доступа к сервису
        """
        self.api_key = api_key
        self.base_url = "https://api-maps.yandex.ru/2.1/"
        
    async def get_coordinates(self, address: str) -> Optional[Dict[str, float]]:
        """Получение координат по адресу"""
        try:
            params = {
                "apikey": self.api_key,
                "geocode": address,
                "format": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/geocode", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        coordinates = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                        lon, lat = map(float, coordinates.split())
                        return {"latitude": lat, "longitude": lon}
                    else:
                        logger.error(f"Yandex Maps API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting coordinates: {e}")
            return None

    async def get_static_map(self, coordinates: List[Dict[str, float]], zoom: int = 13) -> Optional[bytes]:
        """Получение статической карты с метками"""
        try:
            points = [f"{c['longitude']},{c['latitude']}" for c in coordinates]
            params = {
                "apikey": self.api_key,
                "ll": points[0],
                "z": zoom,
                "size": "650,450",
                "pt": "~".join([f"{p},pm2rdm" for p in points])
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/static", params=params) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"Error getting static map: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting static map: {e}")
            return None
