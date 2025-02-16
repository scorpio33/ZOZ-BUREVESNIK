import asyncio
from functools import wraps
from unittest.mock import AsyncMock

def async_test(func):
    """Decorator for async test methods"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper

class MockManager:
    """Base class for creating mock managers in tests"""
    def __init__(self):
        self.setup_mocks()

    def setup_mocks(self):
        """Setup mock methods"""
        for attr_name in dir(self):
            if not attr_name.startswith('_') and callable(getattr(self, attr_name)):
                setattr(self, attr_name, AsyncMock())

def setup_test_environment():
    """Setup common test environment"""
    if asyncio._get_running_loop() is not None:
        loop = asyncio._get_running_loop()
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop