from math import radians, sin, cos, sqrt, atan2

class TrackCompressor:
    def __init__(self, min_distance=10):
        self.min_distance = min_distance

    def distance(self, p1: dict, p2: dict) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371000  # Earth radius in meters
        
        lat1, lon1 = radians(float(p1['lat'])), radians(float(p1['lon']))
        lat2, lon2 = radians(float(p2['lat'])), radians(float(p2['lon']))
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    def compress_track(self, points: list) -> list:
        """Compress track points using Douglas-Peucker algorithm"""
        if len(points) < 3:
            return points
            
        result = [points[0]]
        
        for point in points[1:]:
            if self.distance(result[-1], point) >= self.min_distance:
                result.append(point)
                
        return result
