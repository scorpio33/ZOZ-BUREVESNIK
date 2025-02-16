import unittest
from unittest.mock import Mock, patch
from services.track_compression import TrackCompressor
from services.track_export import TrackExporter
# ... другие импорты

class TestTrackCompressor(unittest.TestCase):
    def setUp(self):
        self.compressor = TrackCompressor()

    def test_compress_track(self):
        test_points = [
            {"lat": 55.751244, "lon": 37.618423},
            {"lat": 55.751244, "lon": 37.618424},
            {"lat": 55.751245, "lon": 37.618425}
        ]
        
        compressed = self.compressor.compress_track(test_points)
        self.assertIsNotNone(compressed)
        self.assertLess(len(compressed), len(test_points))

class TestTrackExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = TrackExporter()

    def test_export_to_gpx(self):
        test_track = [
            {"lat": 55.751244, "lon": 37.618423, "timestamp": "2024-02-16T12:00:00Z"},
            {"lat": 55.751245, "lon": 37.618425, "timestamp": "2024-02-16T12:00:01Z"}
        ]
        
        gpx_data = self.exporter.export_to_gpx(test_track)
        self.assertIn("<?xml", gpx_data)
        self.assertIn("<gpx", gpx_data)