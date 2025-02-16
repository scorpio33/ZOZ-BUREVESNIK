from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class PermissionManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def check_report_permission(self, user_id: int, permission_type: str = 'view_reports') -> bool:
        """Проверка прав доступа к отчетам"""
        try:
            result = await self.db.fetch_one("""
                SELECT 1 FROM report_permissions 
                WHERE user_id = ? AND permission_type = ?
            """, (user_id, permission_type))
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking report permission: {e}")
            return False

    async def grant_permission(self, user_id: int, permission_type: str, granted_by: int) -> bool:
        """Выдача прав доступа"""
        try:
            await self.db.execute("""
                INSERT INTO report_permissions (user_id, permission_type, granted_by)
                VALUES (?, ?, ?)
            """, (user_id, permission_type, granted_by))
            return True
        except Exception as e:
            logger.error(f"Error granting permission: {e}")
            return False

    async def revoke_permission(self, user_id: int, permission_type: str) -> bool:
        """Отзыв прав доступа"""
        try:
            await self.db.execute("""
                DELETE FROM report_permissions 
                WHERE user_id = ? AND permission_type = ?
            """, (user_id, permission_type))
            return True
        except Exception as e:
            logger.error(f"Error revoking permission: {e}")
            return False

    async def get_user_permissions(self, user_id: int) -> List[str]:
        """Получение списка прав пользователя"""
        try:
            results = await self.db.fetch_all("""
                SELECT permission_type 
                FROM report_permissions 
                WHERE user_id = ?
            """, (user_id,))
            return [r['permission_type'] for r in results]
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []