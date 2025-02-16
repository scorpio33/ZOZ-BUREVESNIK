from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from queue import PriorityQueue
import logging

logger = logging.getLogger(__name__)

class NotificationQueueManager:
    def __init__(self, notification_manager, db_manager):
        self.notification_manager = notification_manager
        self.db = db_manager
        self.queue = PriorityQueue()
        self.retry_delays = [60, 300, 900]  # Retry after 1min, 5min, 15min
        self.is_running = False

    async def start(self):
        """Запуск обработчика очереди"""
        self.is_running = True
        asyncio.create_task(self._process_queue())

    async def stop(self):
        """Остановка обработчика очереди"""
        self.is_running = False

    async def add_notification(self, 
                             user_id: int, 
                             message: str, 
                             priority: int = 2,
                             scheduled_time: Optional[datetime] = None) -> int:
        """
        Добавление уведомления в очередь
        priority: 1 (высокий), 2 (средний), 3 (низкий)
        """
        try:
            notification_id = await self.db.execute_query("""
                INSERT INTO notification_queue 
                (user_id, message, priority, scheduled_time, status)
                VALUES (?, ?, ?, ?, 'pending')
                RETURNING id
            """, (user_id, message, priority, scheduled_time))

            self.queue.put((
                priority,
                notification_id,
                {
                    'user_id': user_id,
                    'message': message,
                    'scheduled_time': scheduled_time,
                    'retry_count': 0
                }
            ))

            return notification_id
        except Exception as e:
            logger.error(f"Error adding notification to queue: {e}")
            return None

    async def add_group_notification(self, 
                                   group_id: int, 
                                   message: str,
                                   priority: int = 2,
                                   exclude_user_id: Optional[int] = None):
        """Добавление группового уведомления"""
        try:
            members = await self.db.get_group_members(group_id)
            for member in members:
                if member['user_id'] != exclude_user_id:
                    await self.add_notification(
                        member['user_id'],
                        message,
                        priority
                    )
        except Exception as e:
            logger.error(f"Error adding group notification: {e}")

    async def _process_queue(self):
        """Обработка очереди уведомлений"""
        while self.is_running:
            try:
                if self.queue.empty():
                    await asyncio.sleep(1)
                    continue

                priority, notification_id, data = self.queue.get()
                current_time = datetime.now()

                # Проверка времени отправки для отложенных уведомлений
                if data.get('scheduled_time') and data['scheduled_time'] > current_time:
                    self.queue.put((priority, notification_id, data))
                    await asyncio.sleep(1)
                    continue

                success = await self._send_notification(data)
                
                if success:
                    await self._mark_as_sent(notification_id)
                else:
                    await self._handle_failed_notification(priority, notification_id, data)

            except Exception as e:
                logger.error(f"Error in queue processing: {e}")
                await asyncio.sleep(1)

    async def _send_notification(self, data: Dict) -> bool:
        """Отправка уведомления"""
        try:
            await self.notification_manager.send_notification(
                data['user_id'],
                data['message']
            )
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

    async def _handle_failed_notification(self, priority: int, 
                                        notification_id: int, 
                                        data: Dict):
        """Обработка неудачной отправки"""
        retry_count = data.get('retry_count', 0)
        
        if retry_count < len(self.retry_delays):
            # Планируем повторную попытку
            data['retry_count'] = retry_count + 1
            data['scheduled_time'] = datetime.now().timestamp() + self.retry_delays[retry_count]
            
            self.queue.put((priority + 1, notification_id, data))
            
            await self.db.execute_query("""
                UPDATE notification_queue 
                SET retry_count = ?, status = 'retry'
                WHERE id = ?
            """, (retry_count + 1, notification_id))
        else:
            # Помечаем как неудачное после всех попыток
            await self.db.execute_query("""
                UPDATE notification_queue 
                SET status = 'failed'
                WHERE id = ?
            """, (notification_id,))

    async def _mark_as_sent(self, notification_id: int):
        """Отметка уведомления как отправленного"""
        await self.db.execute_query("""
            UPDATE notification_queue 
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (notification_id,))