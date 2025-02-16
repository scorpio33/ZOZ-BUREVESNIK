import unittest
from unittest.mock import MagicMock, AsyncMock
from telegram import Update
from telegram.ext import ContextTypes
from handlers.analytics_handler import AnalyticsHandler

class TestAnalytics(unittest.TestCase):
    async def asyncSetUp(self):
        self.update = MagicMock(spec=Update)
        self.context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        self.db_manager = MagicMock()
        self.stats_manager = MagicMock()
        self.handler = AnalyticsHandler(self.db_manager, self.stats_manager)
        
        # Настройка моков
        self.update.effective_user.id = 123456789
        self.update.callback_query = MagicMock()
        self.update.callback_query.message = MagicMock()
        self.update.callback_query.message.edit_text = AsyncMock()
        
        # Настройка возвращаемых данных
        self.stats_manager.get_user_statistics = AsyncMock(return_value={
            'searches': 10,
            'distance': 100,
            'tasks_completed': 5
        })
        self.stats_manager.get_global_statistics = AsyncMock(return_value={
            'total_users': 100,
            'active_searches': 5,
            'total_distance': 1000
        })

    async def test_personal_statistics(self):
        self.update.callback_query.data = "personal_stats"
        result = await self.handler.handle_callback(self.update, self.context)
        self.assertTrue(result)
        self.stats_manager.get_user_statistics.assert_called_once()
        self.update.callback_query.message.edit_text.assert_called_once()

    async def test_global_statistics(self):
        self.update.callback_query.data = "global_stats"
        result = await self.handler.handle_callback(self.update, self.context)
        self.assertTrue(result)
        self.stats_manager.get_global_statistics.assert_called_once()
        self.update.callback_query.message.edit_text.assert_called_once()