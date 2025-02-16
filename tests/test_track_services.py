import unittest
from services.track_services import TrackCompressor, TrackExporter
from typing import List, Tuple

class TestTrackServices(unittest.TestCase):
    def setUp(self):
        # Initialize test data with more points to make compression meaningful
        self.test_points: List[Tuple[float, float]] = [
            (55.7558, 37.6173),  # Moscow
            (55.7557, 37.6174),  # Very close point
            (55.7556, 37.6175),  # Very close point
            (55.7555, 37.6176),  # Very close point
            (55.7554, 37.6177),  # Very close point
            (55.7553, 37.6178),  # Very close point
            (55.7520, 37.6175),  # Slightly further point
            (55.7500, 37.6180),  # Further point
        ]
        
        # Initialize services
        self.compressor = TrackCompressor()
        self.exporter = TrackExporter()

    def test_track_compression(self):
        """Test that track compression reduces number of points"""
        compressed = self.compressor.compress_track(self.test_points, tolerance=0.001)
        self.assertLess(len(compressed), len(self.test_points), 
                       "Compression should reduce number of points")
        self.assertGreater(len(compressed), 0, 
                          "Compressed track should not be empty")

    def test_track_export_gpx(self):
        """Test GPX export functionality"""
        gpx_data = self.exporter.export_to_gpx(self.test_points)
        
        # Basic GPX format checks
        self.assertIn('<?xml version="1.0"', gpx_data)
        self.assertIn('<gpx', gpx_data)
        self.assertIn('<trk>', gpx_data)
        self.assertIn('<trkpt', gpx_data)
        
        # Check if all points are included
        for lat, lon in self.test_points:
            self.assertIn(f'lat="{lat}"', gpx_data)
            self.assertIn(f'lon="{lon}"', gpx_data)

    def test_track_export_json(self):
        """Test track export to JSON format"""
        # Create test coordinates in (lat, lon) format
        test_coords = [(55.7558, 37.6173), (55.7557, 37.6174)]
        
        # Export to JSON using the exporter instance
        json_data = self.exporter.export_to_json(test_coords)
        
        # Parse the JSON string to compare actual data structure
        import json
        parsed_json = json.loads(json_data)
        
        # Check if coordinates exist in the parsed JSON structure
        # GeoJSON uses [lon, lat] format
        expected_coords = [[37.6173, 55.7558], [37.6174, 55.7557]]
        self.assertEqual(
            parsed_json['geometry']['coordinates'],
            expected_coords,
            "Coordinates should be in GeoJSON format [lon, lat]"
        )
        
        # Verify GeoJSON structure
        self.assertEqual(parsed_json['type'], 'Feature')
        self.assertEqual(parsed_json['geometry']['type'], 'LineString')
        self.assertIn('timestamp', parsed_json['properties'])

if __name__ == '__main__':
    unittest.main()
