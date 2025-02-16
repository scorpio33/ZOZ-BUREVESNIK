from typing import List, Dict, Tuple
from datetime import datetime
import numpy as np
from math import ceil

class TrackAnalyzer:
    def __init__(self):
        self.MIN_SPEED = 0.5  # км/ч
        self.MAX_SPEED = 20.0  # км/ч
        
    def analyze_track(self, points: List[Dict]) -> Dict:
        """Полный анализ трека"""
        if len(points) < 2:
            return self._empty_stats()
            
        # Базовые метрики
        total_distance = self._calculate_total_distance(points)
        duration = self._calculate_duration(points)
        
        # Скорость и темп
        speeds = self._calculate_speeds(points)
        avg_speed = np.mean([s for s in speeds if self.MIN_SPEED <= s <= self.MAX_SPEED])
        max_speed = np.max(speeds)
        
        # Анализ высот
        elevations = [p.get('elevation', 0) for p in points if p.get('elevation')]
        if elevations:
            elevation_gain = sum(max(0, elevations[i] - elevations[i-1]) 
                               for i in range(1, len(elevations)))
            elevation_loss = sum(max(0, elevations[i-1] - elevations[i]) 
                               for i in range(1, len(elevations)))
        else:
            elevation_gain = elevation_loss = 0
            
        # Разбивка на сегменты
        segments = self._analyze_segments(points)
        
        return {
            'total_distance': round(total_distance, 2),  # км
            'duration': self._format_duration(duration),  # чч:мм:сс
            'moving_time': self._calculate_moving_time(points),  # чч:мм:сс
            'avg_speed': round(avg_speed, 1),  # км/ч
            'max_speed': round(max_speed, 1),  # км/ч
            'elevation_gain': round(elevation_gain, 1),  # м
            'elevation_loss': round(elevation_loss, 1),  # м
            'segments': segments,
            'pace': self._calculate_pace(total_distance, duration),  # мин/км
            'points_count': len(points),
            'start_time': points[0]['timestamp'],
            'end_time': points[-1]['timestamp']
        }
    
    def _analyze_segments(self, points: List[Dict]) -> List[Dict]:
        """Разбивка трека на сегменты по 1 км"""
        segments = []
        current_segment = []
        current_distance = 0
        
        for i in range(len(points) - 1):
            current_segment.append(points[i])
            distance = self._calculate_distance(points[i], points[i+1])
            current_distance += distance
            
            if current_distance >= 1.0:  # каждый километр
                segments.append({
                    'distance': round(current_distance, 2),
                    'time': self._calculate_segment_time(current_segment),
                    'avg_speed': self._calculate_segment_speed(current_segment),
                    'start_point': current_segment[0],
                    'end_point': current_segment[-1]
                })
                current_segment = []
                current_distance = 0
        
        return segments
    
    def _calculate_segment_time(self, segment: List[Dict]) -> str:
        """Расчет времени прохождения сегмента"""
        if not segment:
            return "00:00:00"
        
        start_time = datetime.fromisoformat(segment[0]['timestamp'])
        end_time = datetime.fromisoformat(segment[-1]['timestamp'])
        duration = (end_time - start_time).total_seconds()
        
        return self._format_duration(duration)
    
    def _calculate_segment_speed(self, segment: List[Dict]) -> float:
        """Расчет средней скорости на сегменте"""
        if len(segment) < 2:
            return 0.0
            
        distance = self._calculate_total_distance(segment)
        time = (datetime.fromisoformat(segment[-1]['timestamp']) - 
                datetime.fromisoformat(segment[0]['timestamp'])).total_seconds() / 3600
        
        return round(distance / time if time > 0 else 0, 1)
    
    def _empty_stats(self) -> Dict:
        """Пустые статистические данные"""
        return {
            'total_distance': 0,
            'duration': "00:00:00",
            'moving_time': "00:00:00",
            'avg_speed': 0,
            'max_speed': 0,
            'elevation_gain': 0,
            'elevation_loss': 0,
            'segments': [],
            'pace': "00:00",
            'points_count': 0,
            'start_time': None,
            'end_time': None
        }