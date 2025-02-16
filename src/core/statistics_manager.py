from database.db_manager import DatabaseManager

class StatisticsManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def get_user_statistics(self, user_id: int) -> dict:
        """Get statistics for a specific user"""
        query = """
            SELECT 
                COUNT(DISTINCT o.operation_id) as total_operations,
                SUM(t.distance) as total_distance,
                COUNT(DISTINCT q.quest_id) as completed_quests
            FROM operation_members om
            LEFT JOIN search_operations o ON om.operation_id = o.operation_id
            LEFT JOIN tracks t ON om.user_id = t.user_id
            LEFT JOIN completed_quests q ON om.user_id = q.user_id
            WHERE om.user_id = ?
        """
        return await self.db_manager.fetchone(query, (user_id,))