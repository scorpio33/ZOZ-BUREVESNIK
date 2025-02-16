from typing import Optional, List, Dict
from datetime import datetime
import json
import logging
from database.db_manager import DatabaseManager
from .notification_manager import NotificationManager
from .sector_manager import SectorManager
from .group_manager import GroupManager
from .task_manager import TaskManager

logger = logging.getLogger(__name__)

class CoordinationManager:
    def __init__(self, db_manager: DatabaseManager, notification_manager: NotificationManager):
        self.db = db_manager
        self.notification_manager = notification_manager
        self.task_manager = TaskManager(db_manager, notification_manager)

    async def create_operation(self, coordinator_id: int, data: Dict) -> Optional[int]:
        """Создание новой поисковой операции"""
        try:
            operation_id = await self.db.create_search_operation({
                'coordinator_id': coordinator_id,
                'title': data['title'],
                'description': data['description'],
                'start_location': data['location'],
                'search_area': data.get('search_area')
            })

            if operation_id:
                # Уведомляем координаторов
                await self.notification_manager.notify_coordinators(
                    f"🆕 Создана новая поисковая операция:\n"
                    f"'{data['title']}'\n"
                    f"Координатор: {data['coordinator_name']}"
                )
                
                # Создаём квест для участников
                await self._create_operation_quest(operation_id)
                
            return operation_id
        except Exception as e:
            logger.error(f"Error creating operation: {e}")
            return None

    async def get_active_operations(self, coordinator_id: Optional[int] = None) -> List[Dict]:
        """Получение списка активных поисковых операций"""
        try:
            operations = await self.db.get_active_operations(coordinator_id)
            for op in operations:
                op['location'] = json.loads(op['location'])
                op['groups'] = await self.group_manager.get_operation_groups(op['operation_id'])
                op['sectors'] = await self.sector_manager.get_operation_sectors(op['operation_id'])
            return operations
        except Exception as e:
            logger.error(f"Error getting active operations: {e}")
            return []

    async def assign_task(self, operation_id: int, task_data: Dict) -> Optional[int]:
        """Назначение задачи группе"""
        try:
            task_id = await self.task_manager.create_task({
                'operation_id': operation_id,
                'group_id': task_data['group_id'],
                'title': task_data['title'],
                'description': task_data['description'],
                'priority': task_data.get('priority', 'normal'),
                'deadline': task_data.get('deadline')
            })

            if task_id:
                await self.notification_manager.notify_group(
                    task_data['group_id'],
                    f"📋 Новая задача: {task_data['title']}\n"
                    f"Приоритет: {task_data.get('priority', 'normal')}"
                )

            return task_id
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return None

    async def complete_operation(self, operation_id: int) -> bool:
        """Завершение поисковой операции"""
        try:
            operation = await self.db.get_operation(operation_id)
            if not operation:
                return False

            # Обновляем статус операции
            await self.db.update_operation_status(operation_id, 'completed')

            # Начисляем опыт участникам
            groups = await self.db.get_operation_groups(operation_id)
            for group in groups:
                members = await self.db.get_group_members(group['group_id'])
                for member in members:
                    await self.db.add_user_experience(member['user_id'], 100)
                    await self.db.update_user_stats(
                        member['user_id'],
                        {'searches_completed': 1}
                    )

            # Уведомляем всех участников
            await self.notification_manager.notify_operation_members(
                operation_id,
                "✅ Поисковая операция успешно завершена!\n"
                "Благодарим за участие!"
            )

            return True
        except Exception as e:
            logger.error(f"Error completing operation: {e}")
            return False

    async def _handle_operation_completion(self, operation: Dict):
        """Обработка завершения операции"""
        try:
            # Начисляем опыт участникам
            groups = await self.group_manager.get_operation_groups(operation['operation_id'])
            for group in groups:
                members = await self.group_manager.get_group_members(group['group_id'])
                for member in members:
                    await self.db.add_user_experience(member['user_id'], 100)
                    await self.db.update_user_stats(member['user_id'], 
                        {'searches_completed': 1})
            
            # Обновляем статистику координатора
            await self.db.update_user_stats(operation['coordinator_id'], 
                {'coordinated_searches': 1})
            
            logger.info(f"Operation {operation['operation_id']} completed successfully")
            
        except Exception as e:
            logger.error(f"Error handling operation completion: {e}")

    async def _notify_group_members(self, group_id: int, message: str):
        """Отправка уведомления участникам группы"""
        try:
            members = await self.group_manager.get_group_members(group_id)
            for member in members:
                await self.db.create_notification(member['user_id'], message)
        except Exception as e:
            logger.error(f"Error notifying group members: {e}")

    async def coordinate_group(self, group_id: int, action: str, data: dict) -> bool:
        """Координация действий группы"""
        try:
            if action == 'assign_sector':
                return await self._assign_sector(group_id, data['sector_id'])
            elif action == 'update_status':
                return await self._update_group_status(group_id, data['status'])
            elif action == 'send_command':
                return await self._send_group_command(group_id, data['command'])
            elif action == 'request_report':
                return await self._request_group_report(group_id)
            return False
        except Exception as e:
            logger.error(f"Error coordinating group: {e}")
            return False

    async def _assign_sector(self, group_id: int, sector_id: int) -> bool:
        """Назначение сектора группе"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Проверяем, не занят ли сектор
                cursor.execute("""
                    SELECT status FROM search_sectors 
                    WHERE sector_id = ? AND status != 'completed'
                """, (sector_id,))
                
                if cursor.fetchone():
                    return False
                
                # Назначаем сектор группе
                cursor.execute("""
                    UPDATE operation_groups 
                    SET current_sector_id = ? 
                    WHERE group_id = ?
                """, (sector_id, group_id))
                
                # Обновляем статус сектора
                cursor.execute("""
                    UPDATE search_sectors 
                    SET status = 'in_progress', assigned_team = ? 
                    WHERE sector_id = ?
                """, (group_id, sector_id))
                
                # Уведомляем участников группы
                await self._notify_group_members(group_id, 
                    "🎯 Группе назначен новый сектор поиска!")
                
                return True
        except Exception as e:
            logger.error(f"Error assigning sector: {e}")
            return False

    async def _send_group_command(self, group_id: int, command: dict) -> bool:
        """Отправка команды группе"""
        try:
            command_id = await self.db.create_group_command({
                'group_id': group_id,
                'type': command['type'],
                'content': command['content'],
                'priority': command.get('priority', 'normal')
            })
            
            if command_id:
                # Уведомляем участников
                await self._notify_group_members(group_id,
                    f"⚠️ Новая команда: {command['content']}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error sending group command: {e}")
            return False

    async def create_task(self, operation_id: int, data: Dict) -> Optional[int]:
        """Создание новой задачи с приоритетом"""
        try:
            query = """
                INSERT INTO coordination_tasks (
                    operation_id, group_id, creator_id, title, description,
                    priority_level, deadline, estimated_time, resources_needed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING task_id
            """
            params = (
                operation_id,
                data.get('group_id'),
                data['creator_id'],
                data['title'],
                data.get('description', ''),
                data.get('priority_level', 1),
                data.get('deadline'),
                data.get('estimated_time'),
                json.dumps(data.get('resources_needed', {}))
            )
            
            task_id = await self.db.execute_query_fetchone(query, params)
            
            if task_id:
                await self._notify_task_creation(task_id, data)
            return task_id
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def update_task_progress(self, task_id: int, data: Dict) -> bool:
        """Обновление прогресса задачи"""
        try:
            # Добавляем запись о прогрессе
            progress_query = """
                INSERT INTO task_progress (
                    task_id, reporter_id, status_update,
                    progress_percentage, resources_used, location
                ) VALUES (?, ?, ?, ?, ?, ?)
            """
            progress_params = (
                task_id,
                data['reporter_id'],
                data.get('status_update', ''),
                data.get('progress_percentage', 0),
                json.dumps(data.get('resources_used', {})),
                json.dumps(data.get('location', {}))
            )
            await self.db.execute_query(progress_query, progress_params)

            # Обновляем основную задачу
            task_query = """
                UPDATE coordination_tasks
                SET completion_percentage = ?,
                    status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """
            task_params = (
                data.get('progress_percentage', 0),
                self._calculate_task_status(data.get('progress_percentage', 0)),
                task_id
            )
            await self.db.execute_query(task_query, task_params)

            await self._notify_task_update(task_id, data)
            return True
        except Exception as e:
            logger.error(f"Error updating task progress: {e}")
            return False

    async def assign_resources(self, operation_id: int, task_id: int, resources: List[Dict]) -> bool:
        """Назначение ресурсов для задачи"""
        try:
            for resource in resources:
                query = """
                    UPDATE operation_resources
                    SET assigned_to = ?,
                        status = 'in_use',
                        last_updated = CURRENT_TIMESTAMP
                    WHERE resource_id = ?
                    AND operation_id = ?
                    AND status = 'available'
                """
                params = (task_id, resource['resource_id'], operation_id)
                await self.db.execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"Error assigning resources: {e}")
            return False

    def _calculate_task_status(self, progress: int) -> str:
        """Расчет статуса задачи на основе прогресса"""
        if progress >= 100:
            return 'completed'
        elif progress > 0:
            return 'in_progress'
        return 'pending'

    async def _notify_task_creation(self, task_id: int, data: Dict) -> None:
        """Уведомление о создании задачи"""
        task = await self.get_task(task_id)
        if task:
            priority_emoji = {
                1: "🟢",  # Низкий
                2: "🟡",  # Средний
                3: "🔴",  # Высокий
                4: "⚡️"   # Критический
            }.get(task['priority_level'], "⚪️")

            message = (
                f"{priority_emoji} Новая задача: {task['title']}\n"
                f"Приоритет: {self._get_priority_name(task['priority_level'])}\n"
                f"Срок: {task.get('deadline', 'Не указан')}\n"
                f"Описание: {task.get('description', 'Нет описания')}"
            )
            
            if task.get('group_id'):
                await self.notification_manager.notify_group(task['group_id'], message)
            if task.get('assigned_to'):
                await self.notification_manager.notify_user(task['assigned_to'], message)

    def _get_priority_name(self, level: int) -> str:
        """Получение названия приоритета"""
        return {
            1: "Низкий",
            2: "Средний",
            3: "Высокий",
            4: "Критический"
        }.get(level, "Неизвестный")
