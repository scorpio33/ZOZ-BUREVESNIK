from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TeamManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def create_team(self, group_id: int, leader_id: int, name: str) -> Optional[int]:
        """Создание новой команды"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Создаем команду
                cursor.execute("""
                    INSERT INTO search_teams (group_id, leader_id, name)
                    VALUES (?, ?, ?)
                """, (group_id, leader_id, name))
                team_id = cursor.lastrowid
                
                # Добавляем лидера как участника
                cursor.execute("""
                    INSERT INTO team_members (team_id, user_id, role)
                    VALUES (?, ?, 'leader')
                """, (team_id, leader_id))
                
                return team_id
        except Exception as e:
            logger.error(f"Error creating team: {e}")
            return None

    async def add_team_member(self, team_id: int, user_id: int, role: str = 'member') -> bool:
        """Добавление участника в команду"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO team_members (team_id, user_id, role)
                    VALUES (?, ?, ?)
                """, (team_id, user_id, role))
                return True
        except Exception as e:
            logger.error(f"Error adding team member: {e}")
            return False

    async def get_team_members(self, team_id: int) -> List[Dict]:
        """Получение списка участников команды"""
        try:
            query = """
                SELECT tm.*, u.username, u.first_name, u.last_name
                FROM team_members tm
                JOIN users u ON tm.user_id = u.user_id
                WHERE tm.team_id = ?
            """
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (team_id,))
                members = cursor.fetchall()
                
                return [{
                    'user_id': member[1],
                    'role': member[2],
                    'username': member[4],
                    'first_name': member[5],
                    'last_name': member[6]
                } for member in members]
        except Exception as e:
            logger.error(f"Error getting team members: {e}")
            return []

    async def update_team_status(self, team_id: int, status: str) -> bool:
        """Обновление статуса команды"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE search_teams
                    SET status = ?
                    WHERE team_id = ?
                """, (status, team_id))
                return True
        except Exception as e:
            logger.error(f"Error updating team status: {e}")
            return False