from typing import List
import logging

logger = logging.getLogger(__name__)

class LocationPermissionManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def check_location_permission(self, user_id: int, permission_type: str) -> bool:
        """Проверка прав доступа к геолокации"""
        try:
            result = await self.db.execute_query_fetchone("""
                SELECT 1 FROM location_permissions 
                WHERE user_id = ? AND permission_type = ?
            """, (user_id, permission_type))
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking location permission: {e}")
            return False

    async def grant_location_permission(self, user_id: int, permission_type: str) -> bool:
        """Выдача прав доступа к геолокации"""
        try:
            await self.db.execute_query("""
                INSERT OR IGNORE INTO location_permissions (user_id, permission_type)
                VALUES (?, ?)
            """, (user_id, permission_type))
            return True
        except Exception as e:
            logger.error(f"Error granting location permission: {e}")
            return False

    async def get_user_location_permissions(self, user_id: int) -> List[str]:
        """Получение списка прав пользователя на геолокацию"""
        try:
            results = await self.db.execute_query_fetchall("""
                SELECT permission_type 
                FROM location_permissions 
                WHERE user_id = ?
            """, (user_id,))
            return [row['permission_type'] for row in results]
        except Exception as e:
            logger.error(f"Error getting user location permissions: {e}")
            return []