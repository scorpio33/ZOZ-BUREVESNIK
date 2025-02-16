import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def setup_test_database():
    """Setup test database before each test."""
    # Add any global test setup here
    yield
    # Add any global test cleanup here
