import asyncpg
from typing import Optional
import asyncio

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        
    async def init_pool(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                user='your_user',
                password='your_password',
                database='your_database',
                host='localhost'
            )
        return self.pool

    async def close(self):
        if self.pool:
            await self.pool.close()