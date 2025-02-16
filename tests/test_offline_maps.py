import unittest
from unittest.mock import MagicMock
from services.offline_maps_manager import OfflineMapsManager

class TestOfflineMapsManager(unittest.TestCase):
    def setUp(self):
        self.maps_manager = OfflineMapsManager()
        
    def test_check_map_availability(self):
        """Test map availability check"""
        result = self.maps_manager.check_map_availability("test_region")
        self.assertIsInstance(result, bool)
        
    def test_list_available_regions(self):
        """Test listing available regions"""
        regions = self.maps_manager.list_available_regions()
        self.assertIsInstance(regions, list)
