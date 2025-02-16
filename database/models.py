import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Union

class DatabaseManager:
    def __init__(self, db_path: str = 'bot_database.db'):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

class SearchArea:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_area(self, operation_id: int, boundaries: Dict, metadata: Dict, created_by: int) -> int:
        """Создание новой поисковой области"""
        query = """
        INSERT INTO search_areas (operation_id, boundaries, metadata, created_by, status)
        VALUES (?, ?, ?, ?, 'active')
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                operation_id,
                json.dumps(boundaries),
                json.dumps(metadata),
                created_by
            ))
            return cursor.lastrowid

    def get_area(self, area_id: int) -> Optional[Dict]:
        """Получение информации о поисковой области"""
        query = "SELECT * FROM search_areas WHERE area_id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (area_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'area_id': row[0],
                    'operation_id': row[1],
                    'boundaries': json.loads(row[2]),
                    'metadata': json.loads(row[3]),
                    'created_at': row[4],
                    'updated_at': row[5],
                    'status': row[6],
                    'created_by': row[7]
                }
        return None

    def update_area_status(self, area_id: int, status: str) -> bool:
        """Обновление статуса поисковой области"""
        query = "UPDATE search_areas SET status = ? WHERE area_id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (status, area_id))
            return cursor.rowcount > 0

class GroupMember:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_member(self, user_id: int, group_id: int, role: str = 'member') -> bool:
        """Добавление участника в группу"""
        query = """
        INSERT INTO group_members (
            user_id, group_id, status, role, 
            last_update, joined_at, experience_level, 
            equipment_status
        )
        VALUES (?, ?, 'active', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 'ready')
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id, group_id, role))
                return True
        except sqlite3.IntegrityError:
            return False

    def update_location(self, user_id: int, group_id: int, location: Dict) -> bool:
        """Обновление местоположения участника"""
        query = """
        UPDATE group_members 
        SET last_location = ?, last_update = CURRENT_TIMESTAMP 
        WHERE user_id = ? AND group_id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (json.dumps(location), user_id, group_id))
            return cursor.rowcount > 0

    def get_group_members(self, group_id: int) -> List[Dict]:
        """Получение списка всех участников группы"""
        query = """
        SELECT gm.*, u.username 
        FROM group_members gm
        JOIN users u ON gm.user_id = u.user_id
        WHERE gm.group_id = ? AND gm.status = 'active'
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (group_id,))
            members = []
            for row in cursor.fetchall():
                members.append({
                    'user_id': row[0],
                    'group_id': row[1],
                    'status': row[2],
                    'role': row[3],
                    'last_location': json.loads(row[4]) if row[4] else None,
                    'last_update': row[5],
                    'joined_at': row[6],
                    'experience_level': row[7],
                    'equipment_status': row[8],
                    'notes': row[9],
                    'username': row[10]
                })
            return members

    def update_member_status(self, user_id: int, group_id: int, status: str) -> bool:
        """Обновление статуса участника группы"""
        query = """
        UPDATE group_members 
        SET status = ?, last_update = CURRENT_TIMESTAMP 
        WHERE user_id = ? AND group_id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (status, user_id, group_id))
            return cursor.rowcount > 0

# Пример использования:
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Работа с поисковыми областями
    search_area = SearchArea(db)
    area_id = search_area.create_area(
        operation_id=1,
        boundaries={
            "type": "Polygon",
            "coordinates": [[[30.0, 50.0], [30.1, 50.0], [30.1, 50.1], [30.0, 50.1], [30.0, 50.0]]]
        },
        metadata={"difficulty": "medium", "terrain": "forest"},
        created_by=1
    )
    print(f"Created area with ID: {area_id}")

    # Работа с участниками групп
    group_member = GroupMember(db)
    success = group_member.add_member(
        user_id=1,
        group_id=1,
        role='coordinator'
    )
    print(f"Added member: {success}")

    # Обновление местоположения
    location_updated = group_member.update_location(
        user_id=1,
        group_id=1,
        location={"lat": 50.0, "lon": 30.0}
    )
    print(f"Location updated: {location_updated}")