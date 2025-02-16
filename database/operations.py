async def get_activity_points(self, operation_id: int) -> List[Dict]:
    """Получение точек активности для тепловой карты"""
    query = """
        SELECT 
            latitude, 
            longitude, 
            COUNT(*) as weight
        FROM location_history
        WHERE operation_id = ? 
        AND timestamp >= datetime('now', '-24 hours')
        GROUP BY ROUND(latitude, 4), ROUND(longitude, 4)
    """
    return await self.execute_query(query, (operation_id,))

async def get_important_points(self, operation_id: int) -> List[Dict]:
    """Получение важных точек операции"""
    query = """
        SELECT *
        FROM important_points
        WHERE operation_id = ?
        ORDER BY priority DESC
    """
    return await self.execute_query(query, (operation_id,))