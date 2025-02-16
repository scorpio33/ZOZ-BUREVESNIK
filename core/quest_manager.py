from typing import Dict, List, Optional
from datetime import datetime
import logging
from config.quests import QUESTS, QUEST_CATEGORIES

logger = logging.getLogger(__name__)

class QuestManager:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification_manager = notification_manager

    async def create_quest(self, quest_data: Dict) -> Optional[int]:
        """Create new quest"""
        try:
            async with self.db.connection() as conn:
                cursor = await conn.execute("""
                    INSERT INTO quests (
                        title, 
                        description, 
                        reward_exp, 
                        required_level
                    ) VALUES (?, ?, ?, ?)
                    RETURNING quest_id
                """, (
                    quest_data['title'],
                    quest_data['description'],
                    quest_data['reward_exp'],
                    quest_data.get('required_level', 1)
                ))
                row = await cursor.fetchone()
                await conn.commit()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Error creating quest: {e}")
            return None

    async def update_quest_progress(self, user_id: int, quest_id: int, progress: int) -> bool:
        """Обновление прогресса квеста"""
        try:
            async with self.db.connection() as conn:
                await conn.execute("""
                    INSERT INTO user_quests (user_id, quest_id, progress)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id, quest_id) DO UPDATE SET progress = ?
                    """, (user_id, quest_id, progress, progress))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating quest progress: {e}")
            return False

    async def _complete_quest(self, user_id: int, quest_id: int) -> None:
        """Обработка завершения квеста"""
        try:
            quest_data = QUESTS.get(str(quest_id))
            if not quest_data:
                return

            # Начисляем награды
            await self.db.add_user_experience(user_id, quest_data['reward_exp'])
            if quest_data.get('reward_coins'):
                await self.db.add_user_coins(user_id, quest_data['reward_coins'])

            # Отправляем уведомление
            await self.notification_manager.send_notification(
                user_id,
                f"🎉 Поздравляем! Вы завершили квест '{quest_data['title']}'\n"
                f"Получено: {quest_data['reward_exp']} опыта"
            )

            # Обновляем статус квеста
            await self.db.update_quest_status(user_id, quest_id, 'completed')
            
        except Exception as e:
            logger.error(f"Error completing quest: {e}")
