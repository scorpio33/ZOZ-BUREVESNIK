from typing import Dict, Tuple, Optional, List
import aiohttp
import json
import os

class OfflineMapsManager:
    def __init__(self, cache_dir: str = "storage/maps"):
        self.cache_dir = cache_dir
        self.cache: Dict[str, str] = {}
        os.makedirs(cache_dir, exist_ok=True)

    async def get_map(self, coordinates: Tuple[float, float], zoom: int = 14) -> Optional[str]:
        """Get map for specific coordinates"""
        cache_key = f"{coordinates[0]}_{coordinates[1]}_{zoom}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            map_data = await self._download_map(coordinates, zoom)
            if map_data:
                self.cache[cache_key] = map_data
                return map_data
        except Exception as e:
            print(f"Error downloading map: {e}")
        return None

    async def _download_map(self, coordinates: Tuple[float, float], zoom: int) -> Optional[str]:
        """Download map from service"""
        try:
            async with aiohttp.ClientSession() as session:
                # Здесь будет реальная логика загрузки карт
                # Пока возвращаем тестовые данные
                return f"map_data_for_{coordinates[0]}_{coordinates[1]}_{zoom}"
        except Exception as e:
            print(f"Error in _download_map: {e}")
            return None

    def check_map_availability(self, region: str) -> bool:
        """Check if map for region is available"""
        cache_path = os.path.join(self.cache_dir, f"{region}.map")
        return os.path.exists(cache_path)

    async def download_region(self, region: str) -> bool:
        """Download map for entire region"""
        try:
            cache_path = os.path.join(self.cache_dir, f"{region}.map")
            with open(cache_path, 'w') as f:
                f.write("test_map_data")
            return True
        except Exception as e:
            print(f"Error downloading region: {e}")
            return False

    def list_available_regions(self) -> List[str]:
        """Get list of available regions"""
        try:
            files = os.listdir(self.cache_dir)
            return [f.replace('.map', '') for f in files if f.endswith('.map')]
        except Exception as e:
            print(f"Error listing regions: {e}")
            return []
