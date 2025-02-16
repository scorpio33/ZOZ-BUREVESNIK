from typing import List, Dict, Optional
from datetime import datetime
import logging
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

class CommunicationManager:
    def __init__(self, bot: Bot, db_manager, notification_manager):
        self.bot = bot
        self.db = db_manager
        self.notification = notification_manager

    async def create_group_chat(self, group_id: int, name: str, chat_type: str = 'general') -> Optional[int]:
        """Создание группового чата"""
        try:
            chat_id = await self.db.execute_query_fetchone("""
                INSERT INTO group_chats (group_id, name, type)
                VALUES (?, ?, ?)
                RETURNING chat_id
            """, (group_id, name, chat_type))
            
            if chat_type == 'emergency':
                await self.notify_group_members(group_id, 
                    "🚨 Создан экстренный канал связи!\n"
                    "Все важные сообщения будут дублироваться здесь.")
            
            return chat_id
        except Exception as e:
            logger.error(f"Error creating group chat: {e}")
            return None

    async def send_message(self, chat_id: int, sender_id: int, content: str, 
                          message_type: str = 'text') -> Optional[int]:
        """Отправка сообщения в чат"""
        try:
            # Сохраняем сообщение в БД
            message_id = await self.db.execute_query_fetchone("""
                INSERT INTO messages (chat_id, sender_id, message_type, content)
                VALUES (?, ?, ?, ?)
                RETURNING message_id
            """, (chat_id, sender_id, message_type, content))

            # Получаем информацию о чате
            chat_info = await self.db.execute_query_fetchone("""
                SELECT gc.*, sg.name as group_name 
                FROM group_chats gc
                JOIN search_groups sg ON gc.group_id = sg.group_id
                WHERE gc.chat_id = ?
            """, (chat_id,))

            # Форматируем сообщение
            sender_info = await self.db.get_user(sender_id)
            formatted_message = (
                f"👤 {sender_info['full_name']}\n"
                f"📝 {content}\n"
                f"🕒 {datetime.now().strftime('%H:%M')}"
            )

            # Отправляем сообщение всем участникам группы
            await self.notify_chat_members(chat_id, formatted_message)

            # Если это экстренное сообщение
            if message_type == 'emergency':
                await self.handle_emergency_message(chat_info['group_id'], content, sender_id)

            return message_id
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None

    async def update_member_status(self, user_id: int, group_id: int, 
                                 status: str) -> bool:
        """Обновление статуса участника"""
        try:
            await self.db.execute_query("""
                INSERT INTO member_statuses (user_id, group_id, status)
                VALUES (?, ?, ?)
                ON CONFLICT (user_id, group_id) 
                DO UPDATE SET status = ?, last_updated = CURRENT_TIMESTAMP
            """, (user_id, group_id, status, status))

            # Уведомляем координатора группы
            if status == 'emergency':
                coordinator_id = await self.db.get_group_coordinator(group_id)
                user_info = await self.db.get_user(user_id)
                await self.notification.send_notification(
                    coordinator_id,
                    f"🚨 ВНИМАНИЕ! {user_info['full_name']} сообщает о чрезвычайной ситуации!"
                )

            return True
        except Exception as e:
            logger.error(f"Error updating member status: {e}")
            return False

    async def create_quick_command(self, group_id: int, command: str, 
                                 description: str, created_by: int) -> Optional[int]:
        """Создание быстрой команды"""
        try:
            return await self.db.execute_query_fetchone("""
                INSERT INTO quick_commands (group_id, command, description, created_by)
                VALUES (?, ?, ?, ?)
                RETURNING command_id
            """, (group_id, command, description, created_by))
        except Exception as e:
            logger.error(f"Error creating quick command: {e}")
            return None

    async def handle_emergency_message(self, group_id: int, content: str, sender_id: int):
        """Обработка экстренного сообщения"""
        try:
            # Получаем всех координаторов группы
            coordinators = await self.db.execute_query_fetchall("""
                SELECT user_id FROM group_members 
                WHERE group_id = ? AND role = 'coordinator'
            """, (group_id,))

            # Формируем экстренное сообщение
            sender_info = await self.db.get_user(sender_id)
            emergency_message = (
                "🚨 ЭКСТРЕННОЕ СООБЩЕНИЕ 🚨\n\n"
                f"От: {sender_info['full_name']}\n"
                f"Группа: {group_id}\n\n"
                f"Сообщение: {content}\n\n"
                "Требуется немедленное внимание!"
            )

            # Отправляем уведомления координаторам
            for coord in coordinators:
                await self.notification.send_notification(
                    coord['user_id'],
                    emergency_message,
                    level='critical'
                )

            # Обновляем статус отправителя
            await self.update_member_status(sender_id, group_id, 'emergency')

        except Exception as e:
            logger.error(f"Error handling emergency message: {e}")

    async def get_group_status(self, group_id: int) -> List[Dict]:
        """Получение статусов всех участников группы"""
        try:
            return await self.db.execute_query_fetchall("""
                SELECT 
                    u.user_id,
                    u.full_name,
                    ms.status,
                    ms.last_updated
                FROM users u
                JOIN member_statuses ms ON u.user_id = ms.user_id
                WHERE ms.group_id = ?
                ORDER BY ms.last_updated DESC
            """, (group_id,))
        except Exception as e:
            logger.error(f"Error getting group status: {e}")
            return []