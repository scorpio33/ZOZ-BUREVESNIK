import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from database.db_manager import DatabaseManager
from services.crypto_bot_service import CryptoBotService

logger = logging.getLogger(__name__)

class DonationManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.crypto_service = CryptoBotService()
        
        # Настройки статусов
        self.status_levels = {
            5: {"status": "Silver", "days": 30},
            10: {"status": "Gold", "days": 30},
            15: {"status": "VIP", "days": 30}
        }
        
        # Поддерживаемые валюты
        self.supported_currencies = {
            "TON": {"min_amount": 5, "max_amount": 1000},
            "USDT": {"min_amount": 5, "max_amount": 1000}
        }

    async def create_donation(self, user_id: int, amount: float, currency: str) -> Optional[Dict]:
        """Создание новой донации"""
        try:
            # Проверяем валидность суммы
            if not self._validate_amount(amount, currency):
                return None

            # Создаем инвойс через CryptoBot
            invoice = await self.crypto_service.create_invoice(amount, currency, user_id)
            if not invoice or not invoice.get("ok"):
                return None

            # Сохраняем информацию о донате в БД
            donation_id = await self.db.execute("""
                INSERT INTO donations (user_id, amount, currency, invoice_id, status)
                VALUES (?, ?, ?, ?, 'pending')
                RETURNING donation_id
            """, (user_id, amount, currency, invoice["result"]["invoice_id"]))

            return {
                "donation_id": donation_id,
                "invoice_id": invoice["result"]["invoice_id"],
                "pay_url": invoice["result"]["pay_url"]
            }
        except Exception as e:
            logger.error(f"Error creating donation: {e}")
            return None

    async def process_payment(self, invoice_id: str) -> bool:
        """Обработка успешного платежа"""
        try:
            # Проверяем статус платежа
            if not await self.crypto_service.check_payment(invoice_id):
                return False

            # Получаем информацию о донате
            donation = await self.db.fetchone("""
                SELECT * FROM donations 
                WHERE invoice_id = ? AND status = 'pending'
            """, (invoice_id,))
            
            if not donation:
                return False

            # Определяем новый статус пользователя
            new_status = self._determine_status(donation["amount"])
            expires_at = datetime.now() + timedelta(days=self.status_levels[donation["amount"]]["days"])

            # Обновляем статус пользователя
            await self.db.execute("""
                INSERT INTO user_status (user_id, status, valid_until)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                status = EXCLUDED.status,
                valid_until = EXCLUDED.valid_until
            """, (donation["user_id"], new_status, expires_at))

            # Обновляем статус доната
            await self.db.execute("""
                UPDATE donations 
                SET status = 'completed', updated_at = CURRENT_TIMESTAMP
                WHERE invoice_id = ?
            """, (invoice_id,))

            return True
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False

    def _validate_amount(self, amount: float, currency: str) -> bool:
        """Проверка валидности суммы доната"""
        if currency not in self.supported_currencies:
            return False
        
        limits = self.supported_currencies[currency]
        return limits["min_amount"] <= amount <= limits["max_amount"]

    def _determine_status(self, amount: float) -> str:
        """Определение статуса на основе суммы доната"""
        for level, info in sorted(self.status_levels.items(), reverse=True):
            if amount >= level:
                return info["status"]
        return "Silver"  # Минимальный статус по умолчанию