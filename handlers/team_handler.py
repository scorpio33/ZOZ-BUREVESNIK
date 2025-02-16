from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.team_manager import TeamManager
from core.states import States
import logging

logger = logging.getLogger(__name__)

class TeamHandler:
    def __init__(self, team_manager: TeamManager):
        self.team_manager = team_manager

    async def show_teams_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню управления командами"""
        query = update.callback_query
        group_id = context.user_data.get('current_group_id')
        
        if not group_id:
            await query.message.edit_text(
                "❌ Сначала выберите группу",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="search_menu")
                ]])
            )
            return

        keyboard = [
            [InlineKeyboardButton("👥 Создать команду", callback_data="team_create")],
            [InlineKeyboardButton("📋 Список команд", callback_data="team_list")],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]

        await query.message.edit_text(
            "👥 Управление командами\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def start_team_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало создания новой команды"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['team_creation'] = {}
        context.user_data['state'] = States.CREATING_TEAM
        
        await query.message.edit_text(
            "👥 Создание новой команды\n\n"
            "Введите название команды:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Отмена", callback_data="teams_menu")
            ]])
        )

    async def handle_team_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода данных команды"""
        state = context.user_data.get('state')
        
        if state == States.CREATING_TEAM:
            group_id = context.user_data.get('current_group_id')
            team_name = update.message.text
            leader_id = update.effective_user.id
            
            team_id = await self.team_manager.create_team(
                group_id=group_id,
                leader_id=leader_id,
                name=team_name
            )
            
            if team_id:
                await update.message.reply_text(
                    f"✅ Команда '{team_name}' успешно создана!\n"
                    f"Вы назначены лидером команды.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« К списку команд", callback_data="team_list")
                    ]])
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка при создании команды",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Назад", callback_data="teams_menu")
                    ]])
                )