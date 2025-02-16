import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from database.db_manager import DatabaseManager
from core.map_manager import MapManager
from services.notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class CoordinatorHandler:
    # Состояния для ConversationHandler
    MENU, CREATE_OPERATION, ACTIVE_OPERATIONS, ASSIGN_TASKS = range(4)

    def __init__(self, db_manager: DatabaseManager, map_manager: MapManager, notification_manager: NotificationManager):
        self.db = db_manager
        self.map_manager = map_manager
        self.notification_manager = notification_manager

    async def show_coordinator_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню координатора"""
        keyboard = [
            [InlineKeyboardButton("🔍 Создать операцию", callback_data="coord_create_operation")],
            [InlineKeyboardButton("📋 Активные операции", callback_data="coord_active_operations")],
            [InlineKeyboardButton("👥 Управление группами", callback_data="coord_manage_groups")],
            [InlineKeyboardButton("📊 Статистика", callback_data="coord_statistics")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        text = "👨‍✈️ Меню координатора:\n\n" \
               "• Создание и управление поисковыми операциями\n" \
               "• Просмотр активных операций\n" \
               "• Управление группами\n" \
               "• Просмотр статистики"
        
        if update.callback_query:
            await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return self.MENU

    async def create_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание новой поисковой операции"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]
        await query.message.edit_text(
            "📝 Создание новой операции\n\n"
            "Введите название операции:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.CREATE_OPERATION

    async def handle_operation_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка названия операции"""
        operation_name = update.message.text
        user_id = update.effective_user.id
        
        # Создаем новую операцию в БД
        operation_id = await self.db.create_operation(user_id, operation_name)
        
        keyboard = [
            [InlineKeyboardButton("📍 Указать район поиска", callback_data=f"set_search_area_{operation_id}")],
            [InlineKeyboardButton("👥 Добавить участников", callback_data=f"add_members_{operation_id}")],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]
        
        await update.message.reply_text(
            f"✅ Операция '{operation_name}' создана!\n"
            f"ID операции: {operation_id}\n\n"
            "Выберите следующее действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.MENU

    async def show_active_operations(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ списка активных операций"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        operations = await self.db.get_active_operations(user_id)
        
        if not operations:
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="coord_menu")]]
            await query.message.edit_text(
                "📋 Активные операции отсутствуют",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return self.MENU
        
        text = "📋 Активные операции:\n\n"
        keyboard = []
        
        for op in operations:
            text += f"🔍 {op['name']} (ID: {op['id']})\n"
            keyboard.append([InlineKeyboardButton(
                f"📝 {op['name']}", 
                callback_data=f"view_operation_{op['id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="coord_menu")])
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return self.ACTIVE_OPERATIONS

    async def assign_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Назначение задач участникам"""
        query = update.callback_query
        await query.answer()
        
        operation_id = context.user_data.get('current_operation')
        if not operation_id:
            await query.message.edit_text(
                "❌ Операция не выбрана",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="coord_menu")
                ]])
            )
            return self.MENU
        
        members = await self.db.get_operation_members(operation_id)
        if not members:
            await query.message.edit_text(
                "❌ В операции нет участников",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="coord_menu")
                ]])
            )
            return self.MENU
        
        keyboard = []
        for member in members:
            keyboard.append([InlineKeyboardButton(
                f"👤 {member['name']}", 
                callback_data=f"assign_task_{member['id']}"
            )])
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="coord_menu")])
        
        await query.message.edit_text(
            "👥 Выберите участника для назначения задачи:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.ASSIGN_TASKS

    def get_handler(self):
        """Получение обработчика координатора"""
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.show_coordinator_menu, pattern='^coord_menu$')
            ],
            states={
                self.MENU: [
                    CallbackQueryHandler(self.create_operation, pattern='^coord_create_operation$'),
                    CallbackQueryHandler(self.show_active_operations, pattern='^coord_active_operations$'),
                    CallbackQueryHandler(self.assign_tasks, pattern='^coord_assign_tasks$')
                ],
                self.CREATE_OPERATION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_operation_name),
                    CallbackQueryHandler(self.show_coordinator_menu, pattern='^coord_menu$')
                ],
                self.ACTIVE_OPERATIONS: [
                    CallbackQueryHandler(self.show_coordinator_menu, pattern='^coord_menu$'),
                    CallbackQueryHandler(self.assign_tasks, pattern='^view_operation_\d+$')
                ],
                self.ASSIGN_TASKS: [
                    CallbackQueryHandler(self.show_coordinator_menu, pattern='^coord_menu$'),
                    CallbackQueryHandler(self.handle_task_assignment, pattern='^assign_task_\d+$')
                ]
            },
            fallbacks=[
                CallbackQueryHandler(self.show_coordinator_menu, pattern='^main_menu$')
            ],
            per_message=True
        )

    async def handle_task_assignment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка назначения задачи"""
        query = update.callback_query
        await query.answer()
        
        member_id = query.data.split('_')[-1]
        context.user_data['selected_member'] = member_id
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="coord_menu")]]
        await query.message.edit_text(
            "📝 Введите текст задачи для участника:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.ASSIGN_TASKS

    async def show_active_searches(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ активных поисков"""
        user_id = update.effective_user.id
        active_searches = self.coordination_manager.get_active_searches(coordinator_id=user_id)
        
        if not active_searches:
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="coord_menu")]]
            await update.callback_query.message.edit_text(
                "📋 У вас нет активных поисков.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        keyboard = []
        for search in active_searches:
            keyboard.append([
                InlineKeyboardButton(
                    f"🔍 {search['title']} (ID: {search['operation_id']})",
                    callback_data=f"view_search_{search['operation_id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="coord_menu")])
        
        await update.callback_query.message.edit_text(
            "📋 Активные поиски:\n"
            "Выберите поиск для управления:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_search_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, operation_id: int):
        """Показать детали поиска"""
        search = self.coordination_manager.get_search_details(operation_id)
        
        if not search:
            await update.callback_query.message.edit_text(
                f"❌ Поиск с ID {operation_id} не найден.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="coord_menu")
                ]])
            )
            return
        
        members = self.db.get_operation_members(operation_id)
        tasks = self.db.get_operation_tasks(operation_id)

        text = (
            f"🔍 Поиск: {search['title']}\n\n"
            f"📍 Начальная точка: {search['location']['latitude']}, {search['location']['longitude']}\n"
            f"👥 Участников: {len(members)}\n"
            f"📋 Активных задач: {len([t for t in tasks if t['status'] != 'completed'])}\n\n"
            "Выберите действие:"
        )

        keyboard = [
            [InlineKeyboardButton("👥 Управление участниками", callback_data=f"coord_members_{operation_id}")],
            [InlineKeyboardButton("📋 Управление задачами", callback_data=f"coord_tasks_{operation_id}")],
            [InlineKeyboardButton("📍 Обновить зону поиска", callback_data=f"coord_area_{operation_id}")],
            [InlineKeyboardButton("📊 Статистика", callback_data=f"coord_stats_{operation_id}")],
            [InlineKeyboardButton("✅ Завершить поиск", callback_data=f"coord_complete_{operation_id}")],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]

        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def manage_operation_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление участниками операции"""
        operation_id = int(update.callback_query.data.split('_')[-1])
        members = self.db.get_operation_members(operation_id)

        text = "👥 Управление участниками\n\n"
        keyboard = []

        for member in members:
            user = self.db.get_user(member['user_id'])
            status_emoji = "✅" if member['status'] == 'active' else "❌"
            text += f"{status_emoji} {user['username']} - {member['role']}\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"{'🔄 Деактивировать' if member['status'] == 'active' else '✅ Активировать'} {user['username']}", 
                    callback_data=f"coord_toggle_member_{operation_id}_{member['user_id']}"
                )
            ])

        keyboard.append([InlineKeyboardButton("➕ Добавить участника", callback_data=f"coord_add_member_{operation_id}")])
        keyboard.append([InlineKeyboardButton("« Назад", callback_data=f"coord_control_{operation_id}")])

        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def manage_operation_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление задачами операции"""
        operation_id = int(update.callback_query.data.split('_')[-1])
        tasks = self.db.get_operation_tasks(operation_id)

        text = "📋 Управление задачами\n\n"
        keyboard = []

        for task in tasks:
            status_emoji = {
                'pending': "⏳",
                'in_progress': "▶️",
                'completed': "✅"
            }.get(task['status'], "❓")
            
            text += f"{status_emoji} {task['title']}\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"Управление: {task['title']}", 
                    callback_data=f"coord_task_{operation_id}_{task['task_id']}"
                )
            ])

        keyboard.append([InlineKeyboardButton("➕ Создать задачу", callback_data=f"coord_create_task_{operation_id}")])
        keyboard.append([InlineKeyboardButton("« Назад", callback_data=f"coord_control_{operation_id}")])

        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def complete_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Завершение поисковой операции"""
        operation_id = int(update.callback_query.data.split('_')[-1])
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data=f"coord_confirm_complete_{operation_id}"),
                InlineKeyboardButton("❌ Отмена", callback_data=f"coord_control_{operation_id}")
            ]
        ]

        await update.callback_query.message.edit_text(
            "⚠️ Вы уверены, что хотите завершить операцию?\n"
            "Это действие нельзя отменить.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_coordinator_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать расширенную статистику координатора"""
        user_id = update.effective_user.id
        stats = await self.db.get_coordinator_statistics(user_id)
        
        if not stats:
            await update.callback_query.message.edit_text(
                "❌ Не удалось загрузить статистику.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="coord_menu")
                ]])
            )
            return

        # Форматируем основную статистику
        operations = stats['operations']
        recent = stats['recent']
        
        text = (
            "📊 <b>Ваша статистика координатора</b>\n\n"
            f"🔍 Всего операций: {operations['total_operations']}\n"
            f"✅ Успешно завершено: {operations['completed_operations']}\n"
            f"❌ Отменено: {operations['cancelled_operations']}\n"
            f"⭐️ Средний рейтинг: {operations['avg_success_rate']:.1f}%\n\n"
            
            "📈 <b>Средние показатели</b>\n"
            f"👥 Команд на операцию: {operations['avg_team_count']:.1f}\n"
            f"👤 Волонтёров на операцию: {operations['avg_volunteer_count']:.1f}\n\n"
            
            "🗓 <b>Статистика за последний месяц</b>\n"
            f"🔍 Операций: {recent['recent_operations']}\n"
            f"⭐️ Успешность: {recent['recent_success_rate']:.1f}%\n"
        )

        keyboard = [
            [InlineKeyboardButton("📋 История операций", callback_data="coord_stats_history")],
            [InlineKeyboardButton("📊 Детальный рейтинг", callback_data="coord_stats_rating")],
            [InlineKeyboardButton("📈 Графики", callback_data="coord_stats_graphs")],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]

        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    async def show_operation_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать историю операций координатора"""
        user_id = update.effective_user.id
        page = context.user_data.get('history_page', 0)
        ITEMS_PER_PAGE = 5
        
        operations = await self.db.get_coordinator_operation_history(
            user_id,
            limit=ITEMS_PER_PAGE,
            offset=page * ITEMS_PER_PAGE
        )
        
        if not operations:
            text = "📋 История операций пуста"
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="coord_stats")]]
        else:
            text = "📋 <b>История операций</b>\n\n"
            for op in operations:
                status_emoji = {
                    'completed': '✅',
                    'cancelled': '❌',
                    'active': '▶️'
                }.get(op['status'], '❓')
                
                text += (
                    f"{status_emoji} <b>{op['operation_title']}</b>\n"
                    f"📍 Локация: {op['operation_location']}\n"
                    f"👥 Групп: {op['groups_stats']['total_groups']}\n"
                    f"👤 Волонтёров: {op['groups_stats']['total_volunteers']}\n"
                    f"⭐️ Успешность: {op['success_rate']:.1f}%\n"
                    f"📅 {op['start_time']}\n\n"
                )

            # Кнопки пагинации
            keyboard = []
            if page > 0:
                keyboard.append([InlineKeyboardButton("⬅️ Предыдущие", callback_data="coord_stats_history_prev")])
            if len(operations) == ITEMS_PER_PAGE:
                keyboard.append([InlineKeyboardButton("➡️ Следующие", callback_data="coord_stats_history_next")])
            keyboard.append([InlineKeyboardButton("« Назад", callback_data="coord_stats")])

        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    async def show_rating_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детальную информацию о рейтинге"""
        user_id = update.effective_user.id
        rating = await self.db.get_coordinator_rating_details(user_id)
        
        if not rating:
            await update.callback_query.message.edit_text(
                "❌ Не удалось загрузить данные рейтинга",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="coord_stats")
                ]])
            )
            return

        text = (
            "📊 <b>Детальный рейтинг координатора</b>\n\n"
            f"🎯 Процент успешности: {rating['success_rate']:.1f}%\n"
            f"📈 Средний рейтинг операций: {rating['avg_success_rate']:.1f}\n\n"
            
            "<b>Показатели команд:</b>\n"
            f"👥 Среднее количество команд: {rating['avg_team_count']:.1f}\n"
            f"👤 Среднее количество волонтёров: {rating['avg_volunteer_count']:.1f}\n"
            f"📊 Максимум волонтёров: {rating['max_volunteer_count']}\n\n"
            
            "<b>Активность:</b>\n"
            f"🔍 Всего операций: {rating['total_operations']}\n"
            f"✅ Успешных операций: {rating['successful_operations']}\n"
            f"📅 Операций за 30 дней: {rating['recent_operations']}\n"
        )

        keyboard = [
            [InlineKeyboardButton("« Назад", callback_data="coord_stats")]
        ]

        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    async def handle_statistics_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback-запросов статистики"""
        query = update.callback_query
        data = query.data

        if data == "coord_stats":
            await self.show_coordinator_statistics(update, context)
        
        elif data == "coord_stats_history":
            context.user_data['history_page'] = 0
            await self.show_operation_history(update, context)
        
        elif data == "coord_stats_history_next":
            context.user_data['history_page'] = context.user_data.get('history_page', 0) + 1
            await self.show_operation_history(update, context)
        
        elif data == "coord_stats_history_prev":
            context.user_data['history_page'] = max(0, context.user_data.get('history_page', 0) - 1)
            await self.show_operation_history(update, context)
        
        elif data == "coord_stats_rating":
            await self.show_rating_details(update, context)
        
        elif data == "coord_stats_graphs":
            # Здесь можно добавить визуализацию статистики в виде графиков
            await query.answer("🔄 Функция находится в разработке")

    async def show_member_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню управления участниками"""
        keyboard = [
            [InlineKeyboardButton("➕ Добавить участника", callback_data="coord_add_member")],
            [InlineKeyboardButton("❌ Удалить участника", callback_data="coord_remove_member")],
            [InlineKeyboardButton("📋 Список участников", callback_data="coord_list_members")],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "👥 Управление участниками\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_active_operations(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать активные операции"""
        user_id = update.effective_user.id
        operations = self.db.get_active_operations(coordinator_id=user_id)
        
        if not operations:
            text = "🔍 У вас нет активных операций"
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="coord_menu")]]
        else:
            text = "🔍 Ваши активные операции:\n\n"
            keyboard = []
            for op in operations:
                text += f"📍 {op['title']}\n"
                keyboard.append([
                    InlineKeyboardButton(
                        f"Управлять: {op['title']}", 
                        callback_data=f"coord_manage_op_{op['operation_id']}"
                    )
                ])
            keyboard.append([InlineKeyboardButton("« Назад", callback_data="coord_menu")])
        
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def manage_search_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление поисковой операцией"""
        operation_id = int(update.callback_query.data.split('_')[-1])
        operation = await self.db.get_operation(operation_id)
        
        if not operation:
            await update.callback_query.message.edit_text(
                "❌ Операция не найдена",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="coord_menu")
                ]])
            )
            return

        # Получаем статистику операции
        stats = await self.stats_manager.get_operation_stats(operation_id)
        
        text = (
            f"📋 Операция: {operation['title']}\n"
            f"📍 Локация: {operation['location']}\n"
            f"👥 Участников: {stats['member_count']}\n"
            f"✅ Выполнено задач: {stats['completed_tasks']}/{stats['total_tasks']}\n"
            f"🗺 Исследовано секторов: {stats['completed_sectors']}/{stats['total_sectors']}"
        )

        keyboard = [
            [InlineKeyboardButton("👥 Управление участниками", callback_data=f"coord_members_{operation_id}")],
            [InlineKeyboardButton("📋 Управление задачами", callback_data=f"coord_tasks_{operation_id}")],
            [InlineKeyboardButton("🗺 Управление секторами", callback_data=f"coord_sectors_{operation_id}")],
            [InlineKeyboardButton("📊 Статистика", callback_data=f"coord_stats_{operation_id}")],
            [InlineKeyboardButton("✅ Завершить операцию", callback_data=f"coord_complete_{operation_id}")],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]

        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_coordination_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню координатора"""
        keyboard = [
            [InlineKeyboardButton("📋 Активные поиски", callback_data="coord_active_searches")],
            [InlineKeyboardButton("➕ Создать поиск", callback_data="coord_create_search")],
            [
                InlineKeyboardButton("🗺 Карта операции", callback_data="coord_map"),
                InlineKeyboardButton("📊 Статистика", callback_data="coord_stats")
            ],
            [InlineKeyboardButton("👥 Управление группами", callback_data="coord_manage_groups")],
            [InlineKeyboardButton("« Назад", callback_data="main_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "🎯 Меню координатора\n\n"
            "• Управляйте поисковыми операциями\n"
            "• Отслеживайте группы на карте\n"
            "• Просматривайте статистику\n"
            "• Координируйте действия участников",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_operation_map_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню карты операции"""
        query = update.callback_query
        operations = await self.db.get_active_operations(coordinator_id=update.effective_user.id)
        
        if not operations:
            await query.message.edit_text(
                "❌ У вас нет активных операций",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="coord_menu")
                ]])
            )
            return
        
        keyboard = []
        # Добавляем кнопки для каждой активной операции
        for op in operations:
            keyboard.append([
                InlineKeyboardButton(
                    f"🗺 {op['name']}", 
                    callback_data=f"coord_map_view_{op['id']}"
                )
            ])
        
        # Добавляем общие настройки карты
        keyboard.extend([
            [
                InlineKeyboardButton("⚙️ Настройки карты", callback_data="coord_map_settings"),
                InlineKeyboardButton("📍 Добавить точку", callback_data="coord_add_point")
            ],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ])
        
        await query.message.edit_text(
            "🗺 Карта операции\n\n"
            "Выберите операцию для просмотра карты или настройте параметры отображения:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_map_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Настройки карты"""
        keyboard = [
            [
                InlineKeyboardButton("🗺 Яндекс Карты", callback_data="map_type_yandex"),
                InlineKeyboardButton("🌍 OpenStreetMap", callback_data="map_type_osm")
            ],
            [
                InlineKeyboardButton("📡 Спутник", callback_data="map_type_satellite"),
                InlineKeyboardButton("🏷 Гибрид", callback_data="map_type_hybrid")
            ],
            [
                InlineKeyboardButton("📤 Экспорт", callback_data="map_export"),
                InlineKeyboardButton("📥 Импорт", callback_data="map_import")
            ],
            [InlineKeyboardButton("« Назад", callback_data="coord_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "⚙️ Настройки карты\n\n"
            "• Выберите тип карты\n"
            "• Экспортируйте или импортируйте данные\n"
            "• Настройте отображение слоев",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_map_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка экспорта карты"""
        query = update.callback_query
        operation_id = context.user_data.get('current_operation_id')
        
        if not operation_id:
            await query.answer("❌ Сначала выберите операцию")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("📍 GPX", callback_data=f"export_gpx_{operation_id}"),
                InlineKeyboardButton("🗺 KML", callback_data=f"export_kml_{operation_id}")
            ],
            [
                InlineKeyboardButton("📊 JSON", callback_data=f"export_json_{operation_id}"),
                InlineKeyboardButton("📑 CSV", callback_data=f"export_csv_{operation_id}")
            ],
            [InlineKeyboardButton("« Назад", callback_data="coord_map_settings")]
        ]
        
        await query.message.edit_text(
            "📤 Выберите формат экспорта:\n\n"
            "• GPX - для GPS-навигаторов\n"
            "• KML - для Google Earth\n"
            "• JSON - для интеграции\n"
            "• CSV - для таблиц",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def request_coordinator_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало процесса подачи заявки на статус координатора"""
        user_id = update.effective_user.id
        
        # Проверяем, нет ли уже активной заявки
        existing_request = await self.db.execute_query_fetchone(
            "SELECT status FROM coordinator_requests WHERE user_id = ?", 
            (user_id,)
        )
        
        if existing_request:
            if existing_request['status'] == 'pending':
                await update.callback_query.message.edit_text(
                    "⏳ У вас уже есть активная заявка на рассмотрении.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Назад", callback_data="settings_menu")
                    ]])
                )
                return
            elif existing_request['status'] == 'approved':
                await update.callback_query.message.edit_text(
                    "✅ Вы уже являетесь координатором!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Назад", callback_data="settings_menu")
                    ]])
                )
                return

        # Начинаем процесс подачи заявки
        context.user_data['coord_request_state'] = 'full_name'
        await update.callback_query.message.edit_text(
            "📝 Заявка на получение статуса координатора\n\n"
            "Для получения статуса координатора необходимо заполнить анкету.\n"
            "1️�� Введите ваше полное ФИО:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Отмена", callback_data="settings_menu")
            ]])
        )

    async def _request_region(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос региона"""
        context.user_data['coord_request_state'] = 'region'
        await update.message.reply_text(
            "2️⃣ Укажите вашу область и город:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Отмена", callback_data="settings_menu")
            ]])
        )

    async def _request_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос номера телефона"""
        context.user_data['coord_request_state'] = 'phone'
        await update.message.reply_text(
            "3️⃣ Укажите ваш контактный номер телефона:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Отмена", callback_data="settings_menu")
            ]])
        )

    async def _request_team(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос названия отряда"""
        context.user_data['coord_request_state'] = 'team'
        await update.message.reply_text(
            "4️⃣ Укажите название вашего поискового отряда:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Отмена", callback_data="settings_menu")
            ]])
        )

    async def _request_position(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос должности"""
        context.user_data['coord_request_state'] = 'position'
        keyboard = [
            [InlineKeyboardButton("Волонтёр", callback_data="position_volunteer")],
            [InlineKeyboardButton("Старший группы", callback_data="position_leader")],
            [InlineKeyboardButton("Помощник координатора", callback_data="position_assistant")],
            [InlineKeyboardButton("Координатор", callback_data="position_coordinator")],
            [InlineKeyboardButton("Отмена", callback_data="settings_menu")]
        ]
        await update.message.reply_text(
            "5️⃣ Выберите вашу текущую должность в отряде:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _request_experience(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос опыта"""
        context.user_data['coord_request_state'] = 'experience'
        await update.message.reply_text(
            "6️⃣ Укажите:\n"
            "- Количество выездов на поиски\n"
            "- Время работы в отряде\n\n"
            "Формат: количество_выездов, время_работы\n"
            "Пример: 15, 2 года",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Отмена", callback_data="settings_menu")
            ]])
        )

    async def handle_coordinator_request_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода данных для заявки на статус координатора"""
        user_id = update.effective_user.id
        message = update.message.text
        state = context.user_data.get('coord_request_state')

        if not state:
            return

        try:
            if state == 'full_name':
                context.user_data['coord_request'] = {'full_name': message}
                await self._request_region(update, context)
            elif state == 'region':
                context.user_data['coord_request']['region'] = message
                await self._request_phone(update, context)
            elif state == 'phone':
                context.user_data['coord_request']['phone'] = message
                await self._request_team(update, context)
            elif state == 'team':
                context.user_data['coord_request']['team'] = message
                await self._request_position(update, context)
            elif state == 'position':
                context.user_data['coord_request']['position'] = message
                await self._request_experience(update, context)
            elif state == 'experience':
                # Сохраняем заявку в базу данных
                await self._save_coordinator_request(update, context)
        except Exception as e:
            logger.error(f"Error in coordinator request: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке заявки. Попробуйте позже.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="settings_menu")
                ]])
            )

    async def _save_coordinator_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение заявки на статус координатора"""
        user_id = update.effective_user.id
        request_data = context.user_data.get('coord_request', {})
        
        await self.db.execute(
            """
            INSERT INTO coordinator_requests 
            (user_id, username, full_name, region, phone_number, team_name, 
             position, search_count, experience_years, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """,
            (user_id, update.effective_user.username, request_data.get('full_name'),
             request_data.get('region'), request_data.get('phone'),
             request_data.get('team'), request_data.get('position'),
             request_data.get('search_count', 0),
             request_data.get('experience_years', 0))
        )

        # Очищаем данные заявки
        context.user_data.pop('coord_request', None)
        context.user_data.pop('coord_request_state', None)

        # Уведомляем пользователя
        await update.message.reply_text(
            "✅ Ваша заявка на получение статуса координатора отправлена!\n"
            "Мы рассмотрим её в ближайшее время и сообщим о решении.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« В настройки", callback_data="settings_menu")
            ]])
        )

        # Уведомляем разработчика
        await self._notify_developer_about_request(update, context)

    async def _notify_developer_about_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Уведомление разработчика о новой заявке"""
        if not hasattr(context.bot, 'developer_id'):
            return
            
        await context.bot.send_message(
            chat_id=context.bot.developer_id,
            text=f"📋 Новая заявка на статус координатора!\n"
                 f"От: @{update.effective_user.username}\n"
                 f"ID: {update.effective_user.id}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("👀 Просмотреть заявки", callback_data="dev_requests")
            ]])
        )
