from typing import List, Tuple
import json
from datetime import datetime

class TrackCompressor:
    def compress_track(self, points: List[Tuple[float, float]], tolerance: float = 0.0001) -> List[Tuple[float, float]]:
        """
        Compress track by removing redundant points using Douglas-Peucker algorithm
        """
        if len(points) <= 2:
            return points
            
        # Find the point with the maximum distance
        dmax = 0
        index = 0
        for i in range(1, len(points) - 1):
            d = self._point_line_distance(points[i], points[0], points[-1])
            if d > dmax:
                index = i
                dmax = d
                
        # If max distance is greater than tolerance, recursively simplify
        if dmax > tolerance:
            # Recursive call
            rec_results1 = self.compress_track(points[:index + 1], tolerance)
            rec_results2 = self.compress_track(points[index:], tolerance)
            # Build the result list
            return rec_results1[:-1] + rec_results2
        else:
            return [points[0], points[-1]]
            
    def _point_line_distance(self, point: Tuple[float, float], 
                           line_start: Tuple[float, float], 
                           line_end: Tuple[float, float]) -> float:
        """Calculate the distance between a point and a line segment"""
        if line_start == line_end:
            return self._distance(point, line_start)
            
        n = abs((line_end[0] - line_start[0]) * (line_start[1] - point[1]) - 
                (line_start[0] - point[0]) * (line_end[1] - line_start[1]))
        d = ((line_end[0] - line_start[0]) ** 2 + (line_end[1] - line_start[1]) ** 2) ** 0.5
        
        return n / d
        
    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate the distance between two points"""
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

class TrackExporter:
    def export_to_gpx(self, points: List[Tuple[float, float]]) -> str:
        """Export track points to GPX format"""
        gpx = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<gpx version="1.1" creator="Track Exporter">',
            '<trk><trkseg>'
        ]
        
        for lat, lon in points:
            gpx.append(f'<trkpt lat="{lat}" lon="{lon}"></trkpt>')
            
        gpx.extend(['</trkseg></trk>', '</gpx>'])
        return '\n'.join(gpx)
        
    def export_to_json(self, points: List[Tuple[float, float]]) -> str:
        """
        Export track points to GeoJSON format
        Input: points as list of (lat, lon) tuples
        Output: GeoJSON string with coordinates in [lon, lat] format
        """
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon, lat] for lat, lon in points]  # Convert to GeoJSON [lon, lat] format
            },
            "properties": {
                "timestamp": datetime.now().isoformat()
            }
        }
        return json.dumps(feature, indent=2)
