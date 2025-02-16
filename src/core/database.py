import aiosqlite
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.initialized = False

    async def initialize(self):
        """Initialize database connection and create necessary tables"""
        if self.initialized:
            return
            
        # Initialize database connection
        self.connection = await self.create_connection()
        
        # Create tables if they don't exist
        await self.create_tables()
        
        self.initialized = True

    async def create_connection(self):
        """Create database connection"""
        # Здесь ваша логика подключения к базе данных
        pass

    async def create_tables(self):
        """Create necessary tables"""
        # Здесь SQL для создания таблиц
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                status TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Добавьте другие необходимые таблицы
        ]
        
        for query in queries:
            await self.execute(query)

    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def execute(self, query: str, *args):
        """Execute SQL query"""
        if not self.connection:
            await self.initialize()
        
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, args)
            await self.connection.commit()

    async def fetch(self, query: str, *args) -> List[Dict]:
        """Получение данных из базы"""
        if not self.connection:
            await self.initialize()
        async with self.connection.cursor() as cursor:
            return await cursor.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Fetch a single row from the database"""
        async with self.connection as conn:
            async with conn.execute(query, args) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None

    async def fetchval(self, query: str, *args) -> Optional[any]:
        """Fetch a single value from the database"""
        async with self.connection as conn:
            async with conn.execute(query, args) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    # Методы для работы с пользователями
    async def create_user(self, user_id: int, username: str = None) -> bool:
        """Создание нового пользователя"""
        query = """
            INSERT INTO users (user_id, username)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
            RETURNING user_id
        """
        result = await self.fetchrow(query, user_id, username)
        return result is not None

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        query = "SELECT * FROM users WHERE user_id = $1"
        return await self.fetchrow(query, user_id)

    # Методы для работы с координаторами
    async def create_coordinator_request(self, user_id: int, data: Dict) -> int:
        """Создание заявки на получение статуса координатора"""
        query = """
            INSERT INTO coordinator_requests (user_id, full_name, region, phone, team_name, position, experience)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING request_id
        """
        result = await self.fetchrow(
            query,
            user_id,
            data.get('full_name'),
            data.get('region'),
            data.get('phone'),
            data.get('team_name'),
            data.get('position'),
            data.get('experience')
        )
        return result['request_id']

    async def get_coordinator_requests(self) -> List[Dict]:
        """Получение всех заявок на статус координатора"""
        query = "SELECT * FROM coordinator_requests WHERE status = 'pending' ORDER BY created_at DESC"
        return await self.fetch(query)
