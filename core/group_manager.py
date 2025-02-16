from typing import List, Dict, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class GroupManager:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification = notification_manager

    async def create_group(self, operation_id: int, data: dict) -> Optional[int]:
        """Создание поисковой группы"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO search_groups 
                    (operation_id, name, leader_id, type, max_members, 
                     equipment_required, experience_required)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    RETURNING group_id
                """, (
                    operation_id,
                    data['name'],
                    data['leader_id'],
                    data.get('type', 'general'),
                    data.get('max_members', 10),
                    json.dumps(data.get('equipment_required', [])),
                    data.get('experience_required', 0)
                ))
                
                group_id = cursor.fetchone()[0]
                
                # Добавляем лидера как участника
                cursor.execute("""
                    INSERT INTO group_members 
                    (group_id, user_id, role, status)
                    VALUES (?, ?, 'leader', 'active')
                """, (group_id, data['leader_id']))
                
                return group_id
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            return None

    async def add_member(self, group_id: int, user_id: int, role: str = 'member') -> bool:
        """Добавление участника в группу"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO group_members 
                    (group_id, user_id, role, status)
                    VALUES (?, ?, ?, 'active')
                    ON CONFLICT (group_id, user_id) 
                    DO UPDATE SET role = ?, status = 'active'
                """, (group_id, user_id, role, role))
                
                await self.notification.notify_group(
                    group_id,
                    f"👤 Новый участник присоединился к группе!",
                    exclude_user_id=user_id
                )
                return True
        except Exception as e:
            logger.error(f"Error adding member: {e}")
            return False

    async def create_task(self, group_id: int, task_data: dict) -> Optional[int]:
        """Создание задания для группы"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO group_tasks 
                    (group_id, title, description, priority, assigned_to, 
                     location, deadline)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    RETURNING task_id
                """, (
                    group_id,
                    task_data['title'],
                    task_data.get('description', ''),
                    task_data.get('priority', 'normal'),
                    task_data.get('assigned_to'),
                    json.dumps(task_data.get('location', {})),
                    task_data.get('deadline')
                ))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def update_location(self, user_id: int, group_id: int, location: dict) -> bool:
        """Обновление местоположения участника"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE group_members 
                    SET last_location = ?,
                        last_active = CURRENT_TIMESTAMP
                    WHERE group_id = ? AND user_id = ?
                """, (json.dumps(location), group_id, user_id))
                
                cursor.execute("""
                    INSERT INTO location_history 
                    (user_id, group_id, location)
                    VALUES (?, ?, ?)
                """, (user_id, group_id, json.dumps(location)))
                
                return True
        except Exception as e:
            logger.error(f"Error updating location: {e}")
            return False

    async def send_message(self, from_group_id: int, data: dict) -> bool:
        """Отправка сообщения между группами"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO group_messages 
                    (from_group_id, to_group_id, sender_id, 
                     message_type, content, is_broadcast)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    from_group_id,
                    data.get('to_group_id'),
                    data['sender_id'],
                    data['message_type'],
                    data['content'],
                    data.get('is_broadcast', False)
                ))
                return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    async def get_group_members(self, group_id: int) -> List[Dict]:
        """Получение списка участников группы"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        u.user_id,
                        u.username,
                        u.full_name,
                        gm.role,
                        gm.status,
                        gm.last_location,
                        gm.last_active
                    FROM group_members gm
                    JOIN users u ON gm.user_id = u.user_id
                    WHERE gm.group_id = ?
                    ORDER BY gm.role DESC, u.full_name
                """, (group_id,))
                
                return [{
                    'user_id': row[0],
                    'username': row[1],
                    'full_name': row[2],
                    'role': row[3],
                    'status': row[4],
                    'last_location': json.loads(row[5]) if row[5] else None,
                    'last_active': row[6]
                } for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting group members: {e}")
            return []
