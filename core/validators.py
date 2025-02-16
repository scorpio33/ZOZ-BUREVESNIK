from typing import Optional, Dict
import re
import phonenumbers

class DataValidator:
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Проверка корректности номера телефона"""
        try:
            parsed = phonenumbers.parse(phone, "RU")
            return phonenumbers.is_valid_number(parsed)
        except:
            return False

    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """Проверка корректности координат"""
        return -90 <= lat <= 90 and -180 <= lon <= 180

    @staticmethod
    def validate_search_data(data: Dict) -> Optional[str]:
        """Валидация данных поиска"""
        if not data.get('name'):
            return "Название поиска не может быть пустым"
        if len(data['name']) > 100:
            return "Название поиска слишком длинное"
        return None

    @staticmethod
    def validate_sector_boundaries(points: list) -> Optional[str]:
        """Валидация границ сектора"""
        if len(points) < 3:
            return "Необходимо минимум 3 точки для создания сектора"
        for lat, lon in points:
            if not DataValidator.validate_coordinates(lat, lon):
                return "Некорректные координаты"
        return None