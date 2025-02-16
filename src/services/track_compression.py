from math import radians, sin, cos, sqrt, atan2

class TrackCompressor:
    def __init__(self, min_distance: float = 0.01):  # 10 meters default
        self.min_distance = min_distance

    def distance(self, p1: tuple, p2: tuple) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in km
        lat1, lon1 = radians(p1[0]), radians(p1[1])
        lat2, lon2 = radians(p2[0]), radians(p2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def compress_track(self, points: list) -> list:
        """Compress track points using distance-based algorithm"""
        if len(points) < 2:
            return points
            
        result = [points[0]]
        
        for point in points[1:]:
            if self.distance(result[-1], point) >= self.min_distance:
                result.append(point)
                
        return result