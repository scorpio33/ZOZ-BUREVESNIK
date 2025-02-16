import pytest
import asyncio
from core.auth_system import AuthSystem
from core.database import DatabaseManager

class TestLoad:
    @pytest.fixture(autouse=True)
    async def setup(self, event_loop):  # добавляем event_loop как параметр
        self.db = DatabaseManager()
        await self.db.initialize()
        yield
        await self.db.cleanup()

    @pytest.mark.asyncio
    async def test_auth_system(self):
        """Test auth system under load"""
        auth_system = AuthSystem(self.db)
        # Your test implementation
        assert True
