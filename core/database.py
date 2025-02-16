import sqlite3
import aiosqlite
import asyncio
from typing import Optional

class DatabaseManager:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize database connection and create tables"""
        async with self._lock:
            if self.connection is None:
                self.connection = await aiosqlite.connect(self.db_path)
                await self.create_tables()

    async def create_tables(self) -> None:
        """Create all necessary tables"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                status TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS coordinator_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT,
                region TEXT,
                phone TEXT,
                team_name TEXT,
                position TEXT,
                experience INTEGER,
                work_time TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS search_groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                coordinator_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (coordinator_id) REFERENCES users(user_id)
            );
            """
        ]
        
        async with self._lock:
            for query in queries:
                await self.connection.execute(query)
            await self.connection.commit()

    async def execute(self, query: str, parameters: tuple = None) -> aiosqlite.Cursor:
        """Execute SQL query"""
        async with self._lock:
            if parameters:
                return await self.connection.execute(query, parameters)
            return await self.connection.execute(query)

    async def fetch_one(self, query: str, parameters: tuple = None) -> Optional[tuple]:
        """Fetch single record"""
        async with self._lock:
            cursor = await self.execute(query, parameters)
            return await cursor.fetchone()

    async def fetch_all(self, query: str, parameters: tuple = None) -> list:
        """Fetch all records"""
        async with self._lock:
            cursor = await self.execute(query, parameters)
            return await cursor.fetchall()

    async def commit(self) -> None:
        """Commit changes"""
        async with self._lock:
            await self.connection.commit()

    async def close(self) -> None:
        """Close database connection"""
        async with self._lock:
            if self.connection:
                await self.connection.close()
                self.connection = None
