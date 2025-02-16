import sqlite3
import aiosqlite
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def init_tables(self):
        """Initialize database tables"""
        try:
            await self.execute_script("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    is_coordinator BOOLEAN DEFAULT FALSE,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    assigned_to INTEGER,
                    FOREIGN KEY (operation_id) REFERENCES operations(operation_id),
                    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
                );
            """)
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def connect(self):
        """Establish database connection"""
        if not self.connection:
            self.connection = await aiosqlite.connect(self.db_path)
            await self.init_tables()

    async def execute(self, query: str, params: tuple = ()) -> None:
        """Execute SQL query"""
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, params)
                await self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    async def execute_script(self, script: str) -> None:
        """Execute SQL script"""
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.executescript(script)
                await self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            raise

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Fetch single row"""
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch row: {e}")
            raise

    async def fetch_all(self, query: str, params: tuple = ()) -> List[tuple]:
        """Fetch all rows"""
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to fetch rows: {e}")
            raise

    async def create_user(self, user_data: Dict[str, Any]) -> None:
        """Create new user"""
        query = """
            INSERT INTO users (user_id, username, is_coordinator)
            VALUES (?, ?, ?)
        """
        params = (
            user_data['user_id'],
            user_data['username'],
            user_data.get('is_coordinator', False)
        )
        await self.execute(query, params)