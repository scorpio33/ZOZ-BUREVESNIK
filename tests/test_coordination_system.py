import pytest
from unittest.mock import AsyncMock

class TestCoordinationSystem:
    @pytest.fixture
    async def coordination_manager(self):
        manager = AsyncMock()
        manager.cleanup = AsyncMock()  # Добавляем метод cleanup
        yield manager
        await manager.cleanup()

    @pytest.mark.asyncio
    async def test_basic_functionality(self, coordination_manager):
        # тест
        pass
