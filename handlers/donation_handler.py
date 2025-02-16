from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
import logging

logger = logging.getLogger(__name__)

class DonationHandler(BaseHandler):
    def __init__(self, db_manager):
        """
        Initialize DonationHandler
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(db_manager)
        self.donation_amounts = {
            'ton_5': {'amount': 5, 'currency': 'TON'},
            'ton_10': {'amount': 10, 'currency': 'TON'},
            'ton_15': {'amount': 15, 'currency': 'TON'},
            'usdt_5': {'amount': 5, 'currency': 'USDT'},
            'usdt_10': {'amount': 10, 'currency': 'USDT'},
            'usdt_15': {'amount': 15, 'currency': 'USDT'}
        }
        
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle donation-related callbacks"""
        query = update.callback_query
        data = query.data
        
        if data == "donate":
            return await self.show_donation_menu(update, context)
        elif data.startswith(("ton_", "usdt_")):
            return await self.process_donation(update, context, data)
        elif data == "donation_verify":
            return await self.verify_donation(update, context)
            
        return False
        
    async def show_donation_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show donation options menu"""
        keyboard = [
            [
                InlineKeyboardButton("5$ TON", callback_data="ton_5"),
                InlineKeyboardButton("10$ TON", callback_data="ton_10"),
                InlineKeyboardButton("15$ TON", callback_data="ton_15")
            ],
            [
                InlineKeyboardButton("5$ USDT", callback_data="usdt_5"),
                InlineKeyboardButton("10$ USDT", callback_data="usdt_10"),
                InlineKeyboardButton("15$ USDT", callback_data="usdt_15")
            ],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "💝 Выберите сумму и способ доната:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True
        
    async def process_donation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, donation_type: str):
        """Process selected donation amount"""
        donation_info = self.donation_amounts.get(donation_type)
        if not donation_info:
            return False
            
        amount = donation_info['amount']
        currency = donation_info['currency']
        wallet = "EQCcR3c7cKHHDHBEEYhPP3N-" if currency == 'TON' else "TRX8dHKb2U..."
        
        keyboard = [
            [InlineKeyboardButton("✅ Я оплатил", callback_data="donation_verify")],
            [InlineKeyboardButton("« Назад", callback_data="donate")]
        ]
        
        await update.callback_query.message.edit_text(
            f"💎 Оплата {amount}$ в {currency}\n\n"
            f"Кошелек: `{wallet}`\n\n"
            "После оплаты нажмите кнопку «Я оплатил»",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        context.user_data['donation'] = {
            'amount': amount,
            'currency': currency,
            'wallet': wallet
        }
        return True
        
    async def verify_donation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Verify donation payment"""
        donation_info = context.user_data.get('donation')
        if not donation_info:
            return False
            
        # Здесь должна быть проверка через API @CryptoBot
        # Пока просто имитируем успешную проверку
        success = True
        
        if success:
            keyboard = [[InlineKeyboardButton("« Главное меню", callback_data="main_menu")]]
            await update.callback_query.message.edit_text(
                "✅ Спасибо за поддержку проекта!\n\n"
                "Ваш статус обновлен.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            # Обновляем статус пользователя в БД
            user_id = update.effective_user.id
            await self.db_manager.update_user_status(user_id, "SILVER")
        else:
            keyboard = [
                [InlineKeyboardButton("↺ Попробовать снова", callback_data="donation_verify")],
                [InlineKeyboardButton("« Назад", callback_data="donate")]
            ]
            await update.callback_query.message.edit_text(
                "❌ Оплата не найдена. Попробуйте снова через несколько минут.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        return True
