import unittest
import pytest
from unittest.mock import AsyncMock, MagicMock
from core.auth_handler import AuthHandler
from database.db_manager import DatabaseManager
from core.notification_manager import NotificationManager

class TestAuthHandler(unittest.TestCase):
    async def asyncSetUp(self):
        self.db_manager = DatabaseManager(":memory:")
        self.notification_manager = NotificationManager(self.db_manager)
        self.auth_handler = AuthHandler(
            self.db_manager,
            self.notification_manager
        )
        await self.db_manager.init_pool()
        yield
        await self.db_manager.close()

    @pytest.mark.asyncio
    async def test_auth_handler_initialization(self):
        assert self.auth_handler is not None
        assert self.auth_handler.db_manager == self.db_manager
