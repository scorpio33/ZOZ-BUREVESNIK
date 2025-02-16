import unittest
import pytest
from unittest.mock import AsyncMock

class TestNotificationSystem(unittest.TestCase):
    async def asyncSetUp(self):
        self.test_user_id = 123456789
        self.coordinator_id = 987654321
        self.notification_system = AsyncMock()

    @pytest.mark.asyncio
    async def test_send_notification(self):
        notification_data = {
            'user_id': self.test_user_id,
            'message': 'Test notification'
        }
        await self.notification_system.send_notification(notification_data)
        self.notification_system.send_notification.assert_called_once_with(notification_data)
