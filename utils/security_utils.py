import jwt
import random
import string
import smtplib
import logging
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, UTC
from typing import Optional
from config.settings import (
    JWT_SECRET_KEY, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    SESSION_TIMEOUT
)

logger = logging.getLogger(__name__)

class SecurityUtils:
    def __init__(self):
        self.session_timeout = SESSION_TIMEOUT
        self.code_length = 6
        self.max_attempts = 3
        self.blocked_duration = 1800

    @staticmethod
    def create_session_token(user_id: int, role: str) -> str:
        """Создание JWT токена сессии"""
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(seconds=SESSION_TIMEOUT)
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_session_token(token: str) -> Optional[dict]:
        """Проверка JWT токена"""
        try:
            return jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def format_block_time(self, seconds: int) -> str:
        """Форматирование времени блокировки"""
        minutes = seconds // 60
        return f"{minutes} минут" if minutes > 1 else "1 минуту"

    def get_remaining_block_time(self, blocked_until: datetime) -> int:
        """Получение оставшегося времени блокировки в секундах"""
        remaining = (blocked_until - datetime.now()).total_seconds()
        return max(0, int(remaining))

    def generate_verification_code(self) -> str:
        """Генерация случайного кода подтверждения"""
        return ''.join(random.choices(string.digits, k=self.code_length))

    def generate_token(self, length: int = 32) -> str:
        """Генерация случайного токена"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Отправка email с кодом подтверждения"""
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_sms(self, phone: str, message: str) -> bool:
        """Отправка SMS с кодом подтверждения"""
        try:
            # Пример использования SMS API (замените на ваш сервис)
            url = "https://api.sms-service.com/send"
            payload = {
                "api_key": SMS_API_KEY,
                "phone": phone,
                "message": message
            }
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully to {phone}")
                return True
            else:
                logger.error(f"SMS sending failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False

    def check_session_timeout(self, last_activity: datetime) -> bool:
        """Проверка таймаута сессии"""
        if not last_activity:
            return True
        
        elapsed = (datetime.now() - last_activity).total_seconds()
        return elapsed > self.session_timeout

    def should_block_user(self, attempts: int) -> bool:
        """Проверка необходимости блокировки пользователя"""
        return attempts >= self.max_attempts

    def get_remaining_block_time(self, blocked_until: datetime) -> int:
        """Получение оставшегося времени блокировки в секундах"""
        remaining = (blocked_until - datetime.now()).total_seconds()
        return max(0, int(remaining))
