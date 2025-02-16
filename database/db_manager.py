import aiosqlite
import logging
from typing import Optional

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.pool = None

    async def init_pool(self):
        """Initialize database connection pool"""
        try:
            self.pool = await aiosqlite.connect(self.db_path)
            await self.create_tables()
            return True
        except Exception as e:
            logging.error(f"Failed to initialize database pool: {e}")
            return False

    async def create_tables(self):
        """Create necessary database tables"""
        async with self.pool as conn:
            await conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    status TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    assigned_to INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

    async def execute(self, query: str, params: tuple = ()):
        """Execute SQL query"""
        if not self.pool:
            await self.init_pool()
        async with self.pool as conn:
            await conn.execute(query, params)
            await conn.commit()

    async def fetchone(self, query: str, params: tuple = ()):
        """Fetch single row"""
        if not self.pool:
            await self.init_pool()
        async with self.pool as conn:
            async with conn.execute(query, params) as cursor:
                return await cursor.fetchone()

    async def fetchall(self, query: str, params: tuple = ()):
        """Fetch all rows"""
        if not self.pool:
            await self.init_pool()
        async with self.pool as conn:
            async with conn.execute(query, params) as cursor:
                return await cursor.fetchall()

    async def close(self):
        """Close database connection"""
        if self.pool:
            await self.pool.close()
            self.pool = None
