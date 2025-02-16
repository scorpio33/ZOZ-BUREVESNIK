import pytest
from src.core.auth_manager import AuthManager

class TestLoad:
    @pytest.fixture
    async def auth_manager(self):
        manager = AuthManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()

    @pytest.mark.asyncio
    async def test_auth_system(self, auth_manager):
        assert auth_manager is not None
        # Add your auth system tests...
