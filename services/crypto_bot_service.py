import logging
import aiohttp
from typing import Optional, Dict
from config.settings import CRYPTO_BOT_API_KEY

logger = logging.getLogger(__name__)

class CryptoBotService:
    def __init__(self):
        self.api_url = "https://pay.crypt.bot/api"
        self.api_key = CRYPTO_BOT_API_KEY
        
    async def create_invoice(self, amount: float, currency: str, user_id: int) -> Optional[Dict]:
        """Создание инвойса для оплаты"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Crypto-Pay-API-Token": self.api_key}
                payload = {
                    "asset": currency,
                    "amount": str(amount),
                    "description": f"Donation {amount} {currency}",
                    "paid_btn_name": "callback",
                    "paid_btn_url": f"https://t.me/your_bot?start=payment_{user_id}",
                    "payload": {"user_id": user_id}
                }
                
                async with session.post(
                    f"{self.api_url}/createInvoice",
                    headers=headers,
                    json=payload
                ) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return None

    async def check_payment(self, invoice_id: str) -> bool:
        """Проверка статуса платежа"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Crypto-Pay-API-Token": self.api_key}
                async with session.get(
                    f"{self.api_url}/getInvoices",
                    headers=headers,
                    params={"invoice_ids": [invoice_id]}
                ) as response:
                    data = await response.json()
                    if data.get("ok") and data["result"]["items"]:
                        return data["result"]["items"][0]["status"] == "paid"
            return False
        except Exception as e:
            logger.error(f"Error checking payment: {e}")
            return False