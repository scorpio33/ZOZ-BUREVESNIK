import re
from typing import Optional
import requests
from config.settings import SMS_API_KEY

class PhoneUtils:
    def __init__(self):
        self.api_key = SMS_API_KEY
        self.phone_pattern = re.compile(r'^\+7\d{10}$')
        
    def validate_phone(self, phone: str) -> bool:
        """Валидация номера телефона"""
        if not phone:
            return False
        return bool(self.phone_pattern.match(phone))
        
    def format_phone(self, phone: str) -> str:
        """Форматирование номера телефона"""
        # Убираем все нецифровые символы
        digits = re.sub(r'\D', '', phone)
        
        # Если номер начинается с 8, заменяем на +7
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        
        # Если номер не начинается с 7, добавляем его
        if not digits.startswith('7'):
            digits = '7' + digits
        
        return f'+{digits}'
        
    def send_verification_code(self, phone: str, code: str) -> bool:
        """Отправка SMS с кодом подтверждения"""
        try:
            # Здесь должна быть интеграция с SMS-сервисом
            # Пример с использованием API
            response = requests.post(
                'https://api.sms.ru/sms/send',
                json={
                    'api_id': self.api_key,
                    'to': phone,
                    'msg': f'Ваш код подтверждения: {code}',
                    'json': 1
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
