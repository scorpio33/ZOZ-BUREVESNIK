import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from datetime import datetime
import gpxpy
import gpxpy.gpx
import logging

logger = logging.getLogger(__name__)

class DataExchangeService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.supported_formats = ['json', 'csv', 'gpx', 'kml']
        
    async def export_operation_data(self, operation_id: int, format: str) -> Optional[bytes]:
        """Экспорт данных операции"""
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}")
            
        operation_data = await self.db.get_operation_data(operation_id)
        if not operation_data:
            return None
            
        export_methods = {
            'json': self._export_json,
            'csv': self._export_csv,
            'gpx': self._export_gpx,
            'kml': self._export_kml
        }
        
        return export_methods[format](operation_data)
        
    def _export_json(self, data: Dict) -> bytes:
        """Экспорт в JSON"""
        return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        
    def _export_csv(self, data: Dict) -> bytes:
        """Экспорт в CSV"""
        output = []
        headers = ['timestamp', 'lat', 'lon', 'type', 'description']
        
        output.append(','.join(headers))
        for point in data['points']:
            row = [
                point['timestamp'],
                str(point['lat']),
                str(point['lon']),
                point['type'],
                point.get('description', '').replace(',', ';')
            ]
            output.append(','.join(row))
            
        return '\n'.join(output).encode('utf-8')
        
    def _export_gpx(self, data: Dict) -> bytes:
        """Экспорт в GPX"""
        gpx = gpxpy.gpx.GPX()
        
        # Создаем трек
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        
        # Создаем сегмент
        segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(segment)
        
        # Добавляем точки
        for point in data['points']:
            segment.points.append(gpxpy.gpx.GPXTrackPoint(
                latitude=point['lat'],
                longitude=point['lon'],
                time=datetime.fromisoformat(point['timestamp']),
                comment=point.get('description', '')
            ))
            
        # Добавляем путевые точки
        for waypoint in data.get('waypoints', []):
            gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(
                latitude=waypoint['lat'],
                longitude=waypoint['lon'],
                name=waypoint.get('name', ''),
                comment=waypoint.get('description', '')
            ))
            
        return gpx.to_xml().encode('utf-8')
        
    async def import_operation_data(self, file_content: bytes, format: str) -> bool:
        """Импорт данных операции"""
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}")
            
        import_methods = {
            'json': self._import_json,
            'csv': self._import_csv,
            'gpx': self._import_gpx,
            'kml': self._import_kml
        }
        
        return await import_methods[format](file_content)
