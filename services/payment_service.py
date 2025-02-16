import logging
import aiohttp
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, crypto_bot_token: str):
        self.api_token = crypto_bot_token
        self.base_url = "https://pay.crypt.bot/api"
        
    async def create_invoice(self, amount: float, currency: str) -> Optional[Dict]:
        """Создание инвойса для оплаты"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/createInvoice",
                    headers={"Crypto-Pay-API-Token": self.api_token},
                    json={
                        "asset": currency,
                        "amount": str(amount),
                        "description": "Support project",
                        "paid_btn_name": "callback",
                        "paid_btn_url": "https://t.me/your_bot?start=payment_verified"
                    }
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error creating invoice: {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"Payment service error: {e}")
            return None

    async def check_payment(self, invoice_id: str) -> bool:
        """Проверка статуса оплаты"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/getInvoices",
                    headers={"Crypto-Pay-API-Token": self.api_token},
                    params={"invoice_ids": invoice_id}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result", {}).get("status") == "paid"
                    return False
        except Exception as e:
            logger.error(f"Error checking payment: {e}")
            return False