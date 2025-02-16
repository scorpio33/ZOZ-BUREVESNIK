import pytest
import asyncio
from unittest import TestCase

class BaseTestCase(TestCase):
    """Base test case class for all tests"""
    @classmethod
    def setUpClass(cls):
        """Set up any async class-level fixtures."""
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    @classmethod
    def tearDownClass(cls):
        """Clean up any async class-level fixtures."""
        cls.loop.close()
        asyncio.set_event_loop(None)

    async def asyncSetUp(self):
        """Set up any async instance-level fixtures."""
        pass

    async def asyncTearDown(self):
        """Clean up any async instance-level fixtures."""
        pass

# Alias for backward compatibility
AsyncTestCase = BaseTestCase

def async_test(coro):
    """Decorator for async test methods."""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper
