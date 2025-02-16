import gpxpy
import gpxpy.gpx
import json
from datetime import datetime

class TrackExporter:
    def export_to_gpx(self, track_points):
        """Export track points to GPX format"""
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        
        for point in track_points:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(
                point['lat'],
                point['lon'],
                time=datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                if 'timestamp' in point else None
            ))
            
        return gpx.to_xml()
        
    def export_to_json(self, track_points):
        """Export track points to JSON format"""
        return json.dumps(track_points, indent=2)
