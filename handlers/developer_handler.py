class DeveloperHandler:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification_manager = notification_manager

    async def show_dev_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ панели разработчика"""
        if update.effective_user.id != DEVELOPER_ID:
            return
            
        keyboard = [
            [InlineKeyboardButton("📋 Управление заявками", callback_data="dev_requests")],
            [InlineKeyboardButton("👥 Управление координаторами", callback_data="dev_coordinators")],
            [InlineKeyboardButton("📊 Системная статистика", callback_data="dev_stats")],
            [InlineKeyboardButton("⚙️ Настройки системы", callback_data="dev_settings")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_main")]
        ]
        
        await update.callback_query.message.edit_text(
            "👨‍💻 Панель разработчика\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_coordinator_requests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка заявок на статус координатора"""
        if update.effective_user.id != DEVELOPER_ID:
            return
            
        requests = await self.db.get_coordinator_requests(status='pending')
        if not requests:
            await update.callback_query.message.edit_text(
                "📋 Нет новых заявок на статус координатора",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="dev_panel")
                ]])
            )
            return

        keyboard = []
        text = "📋 Заявки на статус координатора:\n\n"
        
        for req in requests:
            text += (f"👤 {req['full_name']}\n"
                    f"📍 {req['region']}\n"
                    f"📱 {req['phone_number']}\n"
                    f"🏢 {req['team_name']}\n"
                    f"💼 {req['position']}\n"
                    f"🔍 Выездов: {req['search_count']}\n"
                    f"⏳ Опыт: {req['experience_years']} лет\n\n")
            
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ Одобрить {req['full_name']}", 
                    callback_data=f"approve_coord_{req['request_id']}"
                ),
                InlineKeyboardButton(
                    f"❌ Отклонить", 
                    callback_data=f"reject_coord_{req['request_id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="dev_panel")])
        
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_coordinator_request_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка действий с заявками координаторов"""
        query = update.callback_query
        action, request_id = query.data.split('_')[1:]
        request_id = int(request_id)

        if action == 'approve':
            # Одобряем заявку
            await self._approve_coordinator_request(request_id, update, context)
        elif action == 'reject':
            # Отклоняем заявку
            await self._reject_coordinator_request(request_id, update, context)

    async def _approve_coordinator_request(self, request_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Одобрение заявки на статус координатора"""
        request_data = await self.db.execute_query_fetchone(
            "SELECT * FROM coordinator_requests WHERE request_id = ?",
            (request_id,)
        )
        
        if not request_data:
            await update.callback_query.answer("Заявка не найдена")
            return

        # Обновляем статус заявки
        await self.db.execute_query(
            """UPDATE coordinator_requests 
               SET status = 'approved', 
                   processed_at = CURRENT_TIMESTAMP, 
                   processed_by = ? 
               WHERE request_id = ?""",
            (update.effective_user.id, request_id)
        )

        # Добавляем права координатора
        await self.db.execute_query(
            "UPDATE users SET is_coordinator = TRUE WHERE user_id = ?",
            (request_data['user_id'],)
        )

        # Уведомляем пользователя
        await context.bot.send_message(
            chat_id=request_data['user_id'],
            text=(
                "🎉 Поздравляем! Ваша заявка на статус Координатора одобрена!\n\n"
                "📝 Правила и ответственность Координатора:\n"
                "1. Вы несете ответственность за организацию и успешное завершение поисковых операций\n"
                "2. Создавайте новые группы только после тщательной подготовки\n"
                "3. Поддерживайте связь со всеми участниками группы\n"
                "4. Регулярно отправляйте отчеты о проделанной работе\n\n"
                "⚠️ Это большая ответственность. Мы уверены, что вы справитесь!"
            )
        )

    async def _reject_coordinator_request(self, request_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отклонение заявки на статус координатора"""
        request_data = await self.db.execute_query_fetchone(
            "SELECT * FROM coordinator_requests WHERE request_id = ?",
            (request_id,)
        )
        
        if not request_data:
            await update.callback_query.answer("Заявка не найдена")
            return

        # Обновляем статус заявки
        await self.db.execute_query(
            """UPDATE coordinator_requests 
               SET status = 'rejected', 
                   processed_at = CURRENT_TIMESTAMP, 
                   processed_by = ? 
               WHERE request_id = ?""",
            (update.effective_user.id, request_id)
        )

        # Уведомляем пользователя
        await context.bot.send_message(
            chat_id=request_data['user_id'],
            text=(
                "😕 К сожалению, ваша заявка на статус Координатора отклонена.\n\n"
                "⚠️ Получение статуса Координатора требует опыта работы в поисково-спасательных операциях.\n"
                "Мы рекомендуем вам продолжить участие в поисках и набраться опыта.\n\n"
                "Спасибо за вашу активность и поддержку проекта! 🚑🔍"
            )
        )
