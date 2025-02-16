from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

class GPSHandler:
    def __init__(self):
        self.last_known_locations = {}  # user_id: {location, timestamp}
        self.signal_loss_timestamps = {}  # user_id: timestamp
        self.MAX_SIGNAL_LOSS_TIME = 300  # 5 минут
        
    def handle_location_update(self, user_id: int, location: Dict) -> Dict:
        """Обработка обновления локации с учетом возможной потери сигнала"""
        current_time = datetime.now()
        
        # Проверка валидности GPS данных
        if not self._is_valid_location(location):
            if user_id not in self.signal_loss_timestamps:
                self.signal_loss_timestamps[user_id] = current_time
            
            time_without_signal = (current_time - self.signal_loss_timestamps[user_id]).total_seconds()
            
            if time_without_signal > self.MAX_SIGNAL_LOSS_TIME:
                return {
                    'status': 'critical_signal_loss',
                    'last_known': self.last_known_locations.get(user_id),
                    'duration': time_without_signal
                }
            
            return {
                'status': 'signal_loss',
                'last_known': self.last_known_locations.get(user_id),
                'duration': time_without_signal
            }
        
        # Сигнал восстановлен
        if user_id in self.signal_loss_timestamps:
            del self.signal_loss_timestamps[user_id]
        
        # Обновляем последнюю известную локацию
        self.last_known_locations[user_id] = {
            'location': location,
            'timestamp': current_time
        }
        
        return {'status': 'ok', 'location': location}
    
    def _is_valid_location(self, location: Dict) -> bool:
        """Проверка валидности GPS данных"""
        required_fields = ['lat', 'lon', 'accuracy']
        if not all(field in location for field in required_fields):
            return False
        
        # Проверка разумности значений
        if not (-90 <= location['lat'] <= 90) or \
           not (-180 <= location['lon'] <= 180) or \
           location['accuracy'] > 100:  # метров
            return False
        
        return True