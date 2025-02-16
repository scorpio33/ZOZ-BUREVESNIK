from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class SearchGroupManager:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification = notification_manager

    async def create_group(self, operation_id: int, data: Dict) -> Optional[int]:
        """Создание новой поисковой группы"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Проверяем квалификацию лидера
                cursor.execute("""
                    SELECT experience, qualifications 
                    FROM users 
                    WHERE user_id = ?
                """, (data['leader_id'],))
                
                leader_info = cursor.fetchone()
                if not leader_info or leader_info[0] < data.get('min_experience', 0):
                    return None
                
                # Создаем группу
                cursor.execute("""
                    INSERT INTO search_groups 
                    (operation_id, name, leader_id, type, max_members, 
                     equipment_required, experience_required, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'forming')
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
                    (group_id, user_id, role, status, joined_at)
                    VALUES (?, ?, 'leader', 'active', CURRENT_TIMESTAMP)
                """, (group_id, data['leader_id']))
                
                return group_id
        except Exception as e:
            logger.error(f"Error creating search group: {e}")
            return None

    async def add_member(self, group_id: int, user_id: int, role: str = 'member') -> bool:
        """Добавление участника в группу"""
        try:
            # Проверяем требования группы
            group_info = await self.get_group_info(group_id)
            user_info = await self.db.get_user_info(user_id)
            
            if not self._check_requirements(group_info, user_info):
                return False
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Проверяем количество участников
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM group_members 
                    WHERE group_id = ? AND status = 'active'
                """, (group_id,))
                
                if cursor.fetchone()[0] >= group_info['max_members']:
                    return False
                
                # Добавляем участника
                cursor.execute("""
                    INSERT INTO group_members 
                    (group_id, user_id, role, status, joined_at)
                    VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP)
                    ON CONFLICT (group_id, user_id) 
                    DO UPDATE SET status = 'active', role = ?
                """, (group_id, user_id, role, role))
                
                # Уведомляем лидера группы
                await self._notify_group_leader(
                    group_id,
                    f"👤 Новый участник присоединился к группе: {user_info['name']}"
                )
                
                return True
        except Exception as e:
            logger.error(f"Error adding group member: {e}")
            return False

    async def assign_task(self, group_id: int, task_data: Dict) -> bool:
        """Назначение задачи группе"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO group_tasks 
                    (group_id, title, description, priority, status, 
                     assigned_at, deadline, location)
                    VALUES (?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP, ?, ?)
                """, (
                    group_id,
                    task_data['title'],
                    task_data.get('description', ''),
                    task_data.get('priority', 'normal'),
                    task_data.get('deadline'),
                    json.dumps(task_data.get('location', {}))
                ))
                
                # Уведомляем всех участников группы
                await self._notify_group_members(
                    group_id,
                    f"📋 Новая задача: {task_data['title']}"
                )
                
                return True
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return False

    async def update_group_location(self, group_id: int, location: Dict) -> bool:
        """Обновление местоположения группы"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE search_groups 
                    SET current_location = ?,
                        location_updated_at = CURRENT_TIMESTAMP
                    WHERE group_id = ?
                """, (json.dumps(location), group_id))
                
                return True
        except Exception as e:
            logger.error(f"Error updating group location: {e}")
            return False

    def _check_requirements(self, group_info: Dict, user_info: Dict) -> bool:
        """Проверка соответствия участника требованиям группы"""
        # Проверка опыта
        if user_info['experience'] < group_info['experience_required']:
            return False
            
        # Проверка снаряжения
        required_equipment = set(json.loads(group_info['equipment_required']))
        user_equipment = set(json.loads(user_info['equipment']))
        if not required_equipment.issubset(user_equipment):
            return False
            
        return True