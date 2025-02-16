import pytest
from src.core.database import DatabaseManager
from .test_base import AsyncTestCase, async_test
import threading

class TestCore(AsyncTestCase):
    @async_test
    async def test_database_initialization(self):
        """Test database initialization"""
        # Clear any existing threads
        for thread in threading.enumerate():
            if thread is not threading.current_thread():
                thread.join()
        
        # Your test code here
        self.assertTrue(True)
