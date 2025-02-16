import unittest
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes

class AsyncTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures."""
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level fixtures."""
        try:
            # Cancel all running tasks
            pending = asyncio.all_tasks(cls.loop)
            for task in pending:
                task.cancel()
            
            if pending:
                cls.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
            cls.loop.run_until_complete(cls.loop.shutdown_asyncgens())
        finally:
            cls.loop.close()
            asyncio.set_event_loop(None)

    async def asyncSetUp(self):
        """Async setup method to be overridden by subclasses."""
        pass

    async def asyncTearDown(self):
        """Async teardown method to be overridden by subclasses."""
        pass

    def setUp(self):
        """Set up test fixtures."""
        self.loop.run_until_complete(self.asyncSetUp())

    def tearDown(self):
        """Clean up test fixtures."""
        self.loop.run_until_complete(self.asyncTearDown())

    def run_async(self, coro):
        """Helper method to run coroutines in tests."""
        return self.loop.run_until_complete(coro)

class BaseTestCase(unittest.TestCase):
    """Base test case class for all tests"""
    
    async def asyncSetUp(self):
        """Async setup method that runs before each test"""
        # Setup basic mocks
        self.update = MagicMock(spec=Update)
        self.context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Setup user mock
        self.user = MagicMock(spec=User)
        self.user.id = 123456789
        self.user.username = "test_user"
        self.user.first_name = "Test"
        self.user.last_name = "User"
        
        # Setup message mock
        self.message = AsyncMock(spec=Message)
        self.message.chat = MagicMock(spec=Chat)
        self.message.chat.id = self.user.id
        
        # Setup callback query mock
        self.callback_query = AsyncMock()
        self.callback_query.message = self.message
        self.callback_query.data = None
        
        # Link mocks together
        self.update.effective_user = self.user
        self.update.message = self.message
        self.update.callback_query = self.callback_query
        self.context.user_data = {}
        
        # Setup any additional required attributes
        self.bot_token = "test_token"
        self.db_url = "sqlite:///:memory:"

    def setUp(self):
        """Regular setup that runs before each test"""
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.asyncSetUp())

    async def asyncTearDown(self):
        """Async cleanup that runs after each test"""
        # Add any cleanup code here
        pass

    def tearDown(self):
        """Regular cleanup that runs after each test"""
        self.loop.run_until_complete(self.asyncTearDown())

    async def assertMessageSent(self, text=None, reply_markup=None):
        """Helper method to assert that a message was sent"""
        self.message.reply_text.assert_called()
        if text:
            self.message.reply_text.assert_called_with(
                text,
                reply_markup=reply_markup
            )

    async def assertCallbackAnswered(self, text=None):
        """Helper method to assert that a callback query was answered"""
        self.callback_query.answer.assert_called()
        if text:
            self.callback_query.answer.assert_called_with(text)
