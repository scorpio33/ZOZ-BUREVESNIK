import os
import math
from typing import Tuple, List, Optional
import sqlite3
from datetime import datetime
import aiohttp
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

class OfflineMapsManager:
    def __init__(self):
        self.cache = {}
        
    def check_map_availability(self, region: str) -> bool:
        """Check if map for given region is available"""
        return region in self.cache
        
    def list_available_regions(self) -> list:
        """List all available map regions"""
        return list(self.cache.keys())
