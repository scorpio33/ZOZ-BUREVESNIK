import logging
from typing import Dict, List, Optional
from database.database_manager import DatabaseManager

class ReportSystem:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    async def create_report(self, operation_id: int, report_data: Dict) -> Optional[int]:
        """Create operation report"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT INTO reports (operation_id, content, created_by)
                VALUES (?, ?, ?)
                """, (operation_id, report_data['content'], report_data['user_id']))
            self.db.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error creating report: {e}")
            return None

    async def get_operation_reports(self, operation_id: int) -> List[Dict]:
        """Get all reports for operation"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT * FROM reports 
                WHERE operation_id = ?
                ORDER BY created_at DESC
                """, (operation_id,))
            return [dict(zip([col[0] for col in cursor.description], row))
                   for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting reports: {e}")
            return []