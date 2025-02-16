from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class SearchOperationManager:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification = notification_manager

    async def create_operation(self, coordinator_id: int, data: Dict) -> Optional[int]:
        """Создание новой поисковой операции"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO search_operations 
                    (coordinator_id, title, description, status, location, search_area,
                     start_time, priority_level, missing_person_info)
                    VALUES (?, ?, ?, 'active', ?, ?, CURRENT_TIMESTAMP, ?, ?)
                    RETURNING operation_id
                """, (
                    coordinator_id,
                    data['title'],
                    data.get('description', ''),
                    json.dumps(data['location']),
                    json.dumps(data.get('search_area', {})),
                    data.get('priority', 'normal'),
                    json.dumps(data.get('missing_person', {}))
                ))
                
                operation_id = cursor.fetchone()[0]
                
                # Создаем начальные сектора поиска
                if data.get('sectors'):
                    for sector in data['sectors']:
                        cursor.execute("""
                            INSERT INTO search_sectors 
                            (operation_id, name, boundaries, priority, status)
                            VALUES (?, ?, ?, ?, 'pending')
                        """, (
                            operation_id,
                            sector['name'],
                            json.dumps(sector['boundaries']),
                            sector.get('priority', 'normal')
                        ))

                # Уведомляем координатора
                await self.notification.send_message(
                    coordinator_id,
                    f"🎯 Поисковая операция '{data['title']}' создана!\n"
                    f"ID операции: {operation_id}"
                )
                
                return operation_id
        except Exception as e:
            logger.error(f"Error creating search operation: {e}")
            return None

    async def get_operation_details(self, operation_id: int) -> Optional[Dict]:
        """Получение детальной информации о поисковой операции"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT o.*, 
                           COUNT(DISTINCT g.group_id) as group_count,
                           COUNT(DISTINCT gm.user_id) as participant_count,
                           COUNT(DISTINCT s.sector_id) as sector_count
                    FROM search_operations o
                    LEFT JOIN search_groups g ON g.operation_id = o.operation_id
                    LEFT JOIN group_members gm ON gm.group_id = g.group_id
                    LEFT JOIN search_sectors s ON s.operation_id = o.operation_id
                    WHERE o.operation_id = ?
                    GROUP BY o.operation_id
                """, (operation_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return {
                    'operation_id': row[0],
                    'coordinator_id': row[1],
                    'title': row[2],
                    'description': row[3],
                    'status': row[4],
                    'location': json.loads(row[5]),
                    'search_area': json.loads(row[6]),
                    'start_time': row[7],
                    'end_time': row[8],
                    'priority_level': row[9],
                    'missing_person_info': json.loads(row[10]),
                    'group_count': row[11],
                    'participant_count': row[12],
                    'sector_count': row[13]
                }
        except Exception as e:
            logger.error(f"Error getting operation details: {e}")
            return None

    async def update_operation_status(self, operation_id: int, new_status: str) -> bool:
        """Обновление статуса поисковой операции"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE search_operations 
                    SET status = ?,
                        end_time = CASE WHEN ? IN ('completed', 'cancelled') 
                                      THEN CURRENT_TIMESTAMP 
                                      ELSE end_time END
                    WHERE operation_id = ?
                """, (new_status, new_status, operation_id))
                
                # Уведомляем всех участников об изменении статуса
                await self._notify_operation_members(
                    operation_id,
                    f"⚠️ Статус поисковой операции изменен на: {new_status}"
                )
                
                return True
        except Exception as e:
            logger.error(f"Error updating operation status: {e}")
            return False

    async def _notify_operation_members(self, operation_id: int, message: str) -> None:
        """Уведомление всех участников операции"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT gm.user_id
                    FROM search_groups g
                    JOIN group_members gm ON gm.group_id = g.group_id
                    WHERE g.operation_id = ?
                """, (operation_id,))
                
                for row in cursor.fetchall():
                    await self.notification.send_message(row[0], message)
        except Exception as e:
            logger.error(f"Error notifying operation members: {e}")