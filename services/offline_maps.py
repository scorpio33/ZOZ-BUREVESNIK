import os
import requests
from typing import List, Optional

class OfflineMapsManager:
    def __init__(self, maps_directory: str):
        self.maps_directory = maps_directory
        os.makedirs(maps_directory, exist_ok=True)
        
    def is_map_available(self, region_name: str) -> bool:
        """Check if map for given region is available"""
        map_path = os.path.join(self.maps_directory, f"{region_name}.map")
        return os.path.exists(map_path)
        
    def get_map_size(self, region_name: str) -> int:
        """Get size of map file for given region"""
        map_path = os.path.join(self.maps_directory, f"{region_name}.map")
        return os.path.getsize(map_path) if os.path.exists(map_path) else 0
        
    def list_available_regions(self) -> List[str]:
        """List all available map regions"""
        regions = []
        for file in os.listdir(self.maps_directory):
            if file.endswith('.map'):
                regions.append(file[:-4])  # Remove .map extension
        return regions
