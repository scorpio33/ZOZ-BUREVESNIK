from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification = notification_manager

    async def add_resource(self, data: Dict) -> Optional[int]:
        """Добавление нового ресурса"""
        try:
            query = """
                INSERT INTO resources (
                    category_id, name, description, serial_number,
                    status, condition, purchase_date, next_maintenance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING resource_id
            """
            params = (
                data['category_id'],
                data['name'],
                data.get('description'),
                data.get('serial_number'),
                data.get('status', 'available'),
                data.get('condition', 'good'),
                data.get('purchase_date'),
                data.get('next_maintenance')
            )
            return await self.db.execute_query_fetchone(query, params)
        except Exception as e:
            logger.error(f"Error adding resource: {e}")
            return None

    async def checkout_resource(self, resource_id: int, user_id: int, group_id: int, 
                              operation_id: int, return_date: datetime) -> bool:
        """Выдача ресурса"""
        try:
            # Проверяем доступность ресурса
            resource = await self.db.execute_query_fetchone(
                "SELECT status, condition FROM resources WHERE resource_id = ?",
                (resource_id,)
            )
            
            if not resource or resource['status'] != 'available':
                return False

            # Создаем транзакцию выдачи
            await self.db.execute_query("""
                INSERT INTO resource_transactions (
                    resource_id, user_id, group_id, operation_id,
                    action, condition_before, checkout_date, expected_return_date
                ) VALUES (?, ?, ?, ?, 'checkout', ?, CURRENT_TIMESTAMP, ?)
            """, (resource_id, user_id, group_id, operation_id, 
                  resource['condition'], return_date))

            # Обновляем статус ресурса
            await self.db.execute_query(
                "UPDATE resources SET status = 'in_use' WHERE resource_id = ?",
                (resource_id,)
            )

            # Уведомляем о выдаче
            await self.notification.send_notification(
                user_id,
                f"📦 Вам выдано оборудование (ID: {resource_id})\n"
                f"Ожидаемая дата возврата: {return_date.strftime('%d.%m.%Y')}"
            )

            return True
        except Exception as e:
            logger.error(f"Error checking out resource: {e}")
            return False

    async def return_resource(self, resource_id: int, user_id: int, condition: str) -> bool:
        """Возврат ресурса"""
        try:
            # Находим транзакцию выдачи
            transaction = await self.db.execute_query_fetchone("""
                SELECT transaction_id, condition_before 
                FROM resource_transactions 
                WHERE resource_id = ? AND user_id = ? AND action = 'checkout'
                AND actual_return_date IS NULL
            """, (resource_id, user_id))

            if not transaction:
                return False

            # Обновляем транзакцию
            await self.db.execute_query("""
                UPDATE resource_transactions 
                SET actual_return_date = CURRENT_TIMESTAMP,
                    condition_after = ?
                WHERE transaction_id = ?
            """, (condition, transaction['transaction_id']))

            # Обновляем статус и состояние ресурса
            await self.db.execute_query("""
                UPDATE resources 
                SET status = 'available',
                    condition = ?,
                    last_maintenance = CASE 
                        WHEN condition = 'poor' THEN CURRENT_TIMESTAMP
                        ELSE last_maintenance
                    END
                WHERE resource_id = ?
            """, (condition, resource_id))

            return True
        except Exception as e:
            logger.error(f"Error returning resource: {e}")
            return False

    async def plan_resources(self, operation_id: int, requirements: List[Dict]) -> bool:
        """Планирование потребностей в ресурсах"""
        try:
            for req in requirements:
                await self.db.execute_query("""
                    INSERT INTO resource_planning (
                        operation_id, resource_category_id,
                        quantity_needed, priority, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    operation_id,
                    req['category_id'],
                    req['quantity'],
                    req.get('priority', 1),
                    req.get('notes')
                ))

            # Проверяем доступность ресурсов
            await self._check_resource_availability(operation_id)
            return True
        except Exception as e:
            logger.error(f"Error planning resources: {e}")
            return False

    async def _check_resource_availability(self, operation_id: int):
        """Проверка доступности ресурсов для операции"""
        try:
            plans = await self.db.execute_query_fetchall("""
                SELECT rp.*, rc.name as category_name
                FROM resource_planning rp
                JOIN resource_categories rc ON rp.resource_category_id = rc.category_id
                WHERE rp.operation_id = ? AND rp.status = 'pending'
            """, (operation_id,))

            for plan in plans:
                # Подсчет доступных ресурсов
                available = await self.db.execute_query_fetchone("""
                    SELECT COUNT(*) as count
                    FROM resources
                    WHERE category_id = ? AND status = 'available'
                """, (plan['resource_category_id'],))

                if available['count'] < plan['quantity_needed']:
                    # Уведомляем координаторов о нехватке ресурсов
                    await self.notification.notify_coordinators(
                        f"⚠️ Нехватка ресурсов для операции #{operation_id}\n"
                        f"Категория: {plan['category_name']}\n"
                        f"Требуется: {plan['quantity_needed']}\n"
                        f"Доступно: {available['count']}"
                    )

        except Exception as e:
            logger.error(f"Error checking resource availability: {e}")