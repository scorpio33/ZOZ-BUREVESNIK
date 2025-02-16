from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class NotificationSettingsHandler:
    def __init__(self, settings_manager, monitoring):
        self.settings_manager = settings_manager
        self.monitoring = monitoring

    async def show_settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню настроек уведомлений"""
        keyboard = [
            [InlineKeyboardButton("📱 Каналы доставки", callback_data="notif_channels")],
            [InlineKeyboardButton("🔕 Режим «Не беспокоить»", callback_data="notif_dnd")],
            [InlineKeyboardButton("🔍 Фильтры", callback_data="notif_filters")],
            [InlineKeyboardButton("⏱ Временные интервалы", callback_data="notif_intervals")],
            [InlineKeyboardButton("📊 Статистика", callback_data="notif_stats")],
            [InlineKeyboardButton("« Назад", callback_data="settings_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "⚙️ Настройки уведомлений\n\n"
            "Выберите раздел настроек:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_dnd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Настройка режима «Не беспокоить»"""
        query = update.callback_query
        user_id = query.from_user.id
        
        settings = await self.settings_manager.get_user_settings(user_id)
        dnd = settings['do_not_disturb']
        
        keyboard = [
            [InlineKeyboardButton(
                "🔕 Выключить" if dnd['enabled'] else "🔔 Включить",
                callback_data="notif_dnd_toggle"
            )],
            [
                InlineKeyboardButton("🌙 Начало", callback_data="notif_dnd_start"),
                InlineKeyboardButton("🌅 Конец", callback_data="notif_dnd_end")
            ],
            [InlineKeyboardButton("« Назад", callback_data="notif_settings")]
        ]
        
        status = "Включен" if dnd['enabled'] else "Выключен"
        await query.message.edit_text(
            f"🔕 Режим «Не беспокоить»\n\n"
            f"Статус: {status}\n"
            f"Время: {dnd['start_time']} - {dnd['end_time']}\n\n"
            f"В это время вы будете получать только срочные уведомления.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ статистики уведомлений"""
        query = update.callback_query
        user_id = query.from_user.id
        
        stats = await self.monitoring.get_delivery_stats('week')
        
        text = "📊 Статистика уведомлений за неделю:\n\n"
        for type_name, type_stats in stats.items():
            text += f"{type_name}:\n"
            text += f"✓ Доставлено: {type_stats['delivered']}\n"
            text += f"✗ Ошибок: {type_stats['failed']}\n"
            if type_stats['avg_read_time']:
                avg_time = round(type_stats['avg_read_time'] / 60, 1)
                text += f"⏱ Среднее время прочтения: {avg_time} мин\n"
            text += "\n"
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="notif_settings")]]
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )