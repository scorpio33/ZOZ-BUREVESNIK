from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.sector_manager import SectorManager
from core.states import States
import json
import logging

logger = logging.getLogger(__name__)

class SectorHandler:
    def __init__(self, sector_manager: SectorManager, map_service):
        self.sector_manager = sector_manager
        self.map_service = map_service

    async def show_sectors_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню управления секторами"""
        query = update.callback_query
        operation_id = context.user_data.get('current_operation_id')

        if not operation_id:
            await query.message.edit_text(
                "❌ Не выбрана активная операция",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="coord_menu")
                ]])
            )
            return

        keyboard = [
            [InlineKeyboardButton("➕ Создать сектор", callback_data="create_sector")],
            [InlineKeyboardButton("📋 Список секторов", callback_data="list_sectors")],
            [InlineKeyboardButton("🗺 Карта секторов", callback_data="map_sectors")],
            [InlineKeyboardButton("📊 Прогресс поиска", callback_data="search_progress")],
            [InlineKeyboardButton("« Назад", callback_data="operation_menu")]
        ]

        await query.message.edit_text(
            "🎯 Управление секторами поиска\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def start_sector_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс создания сектора"""
        query = update.callback_query
        context.user_data['state'] = States.ENTERING_SECTOR_NAME

        keyboard = [[InlineKeyboardButton("« Отмена", callback_data="sectors_menu")]]
        
        await query.message.edit_text(
            "📝 Создание нового сектора\n\n"
            "Введите название сектора:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_sector_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода данных сектора"""
        state = context.user_data.get('state')
        sector_data = context.user_data.get('sector_data', {})

        if state == States.ENTERING_SECTOR_NAME:
            sector_data['name'] = update.message.text
            context.user_data['state'] = States.ENTERING_SECTOR_BOUNDARIES
            context.user_data['sector_data'] = sector_data

            await update.message.reply_text(
                "📍 Отправьте координаты углов сектора.\n"
                "Формат: lat1,lon1;lat2,lon2;lat3,lon3\n"
                "Минимум 3 точки для создания полигона.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Отмена", callback_data="sectors_menu")
                ]])
            )

        elif state == States.ENTERING_SECTOR_BOUNDARIES:
            try:
                points = [
                    tuple(float(coord) for coord in point.split(','))
                    for point in update.message.text.split(';')
                ]

                if len(points) < 3:
                    await update.message.reply_text(
                        "❌ Необходимо минимум 3 точки для создания сектора"
                    )
                    return

                sector_data['boundaries'] = points
                operation_id = context.user_data.get('current_operation_id')

                sector_id = await self.sector_manager.create_sector(
                    operation_id=operation_id,
                    data=sector_data
                )

                if sector_id:
                    # Генерируем превью карты
                    map_image = await self.map_service.generate_sector_preview(points)
                    
                    await update.message.reply_photo(
                        map_image,
                        caption=f"✅ Сектор '{sector_data['name']}' успешно создан!"
                    )
                    
                    # Возвращаемся в меню секторов
                    await self.show_sectors_menu(update, context)
                else:
                    await update.message.reply_text(
                        "❌ Ошибка при создании сектора"
                    )

            except ValueError:
                await update.message.reply_text(
                    "❌ Неверный формат координат.\n"
                    "Используйте формат: lat1,lon1;lat2,lon2;lat3,lon3"
                )

    async def show_sector_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список секторов"""
        query = update.callback_query
        operation_id = context.user_data.get('current_operation_id')

        sectors = await self.sector_manager.get_operation_sectors(operation_id)
        
        if not sectors:
            await query.message.edit_text(
                "📋 Список секторов пуст",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="sectors_menu")
                ]])
            )
            return

        text = "📋 Список секторов:\n\n"
        keyboard = []

        for sector in sectors:
            status_emoji = {
                'pending': '⚪️',
                'in_progress': '🔵',
                'completed': '🟢'
            }.get(sector['status'], '⚪️')

            text += (f"{status_emoji} {sector['name']}\n"
                    f"Прогресс: {sector['progress']}%\n"
                    f"Статус: {sector['status']}\n\n")

            keyboard.append([
                InlineKeyboardButton(
                    f"📝 {sector['name']}", 
                    callback_data=f"sector_{sector['sector_id']}"
                )
            ])

        keyboard.append([InlineKeyboardButton("« Назад", callback_data="sectors_menu")])

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
