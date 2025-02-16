import unittest
from unittest.mock import MagicMock, AsyncMock
from tests.base_test import BaseTestCase
from database.db_manager import DatabaseManager
from core.auth_manager import AuthManager
from core.coordination_manager import CoordinationManager
from core.notification_manager import NotificationManager
from core.quest_manager import QuestManager
from core.map_service import MapService

class TestModules(unittest.TestCase):
    async def asyncSetUp(self):
        """Setup test environment"""
        # Initialize database
        self.db = DatabaseManager(":memory:")
        await self.db.init_db()
        
        # Initialize managers
        self.auth_manager = AuthManager(self.db)
        self.notification_manager = NotificationManager(self.db)
        self.coordination_manager = CoordinationManager(
            db_manager=self.db,
            notification_manager=self.notification_manager
        )
        self.quest_manager = QuestManager(self.db, self.notification_manager)
        
    async def test_auth_module(self):
        # Create test user
        test_user_id = 123456789
        test_password = "TestPass123!"
        
        # Register user
        result = await self.auth_manager.register_user(test_user_id, test_password)
        self.assertTrue(result)
        
        # Verify login
        auth_result = await self.auth_manager.verify_password(test_user_id, test_password)
        self.assertTrue(auth_result)

    async def test_coordination_module(self):
        notification_manager = NotificationManager(self.db)
        coord_manager = CoordinationManager(self.db, notification_manager)
        
        # Create test operation
        operation_data = {
            "location": "Test Location",
            "description": "Test Operation",
            "coordinator_id": 123456789
        }
        
        operation_id = await coord_manager.create_operation(operation_data)
        self.assertIsNotNone(operation_id)
        
        # Verify operation exists
        operation = await coord_manager.get_operation(operation_id)
        self.assertIsNotNone(operation)

    async def test_quest_module(self):
        """Тест модуля квестов"""
        # Create test quest
        quest_data = {
            'title': 'Test Quest',
            'description': 'Test Description',
            'reward_exp': 100,
            'required_level': 1
        }
        
        # Initialize quest tables
        await self.db.execute_script("""
            CREATE TABLE IF NOT EXISTS quests (
                quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                reward_exp INTEGER NOT NULL,
                required_level INTEGER DEFAULT 1
            );
            
            CREATE TABLE IF NOT EXISTS user_quests (
                user_id INTEGER,
                quest_id INTEGER,
                progress INTEGER DEFAULT 0,
                status TEXT DEFAULT 'not_started',
                PRIMARY KEY (user_id, quest_id)
            );
        """)
        
        quest_id = await self.quest_manager.create_quest(quest_data)
        self.assertIsNotNone(quest_id)
        
        # Test quest progress
        success = await self.quest_manager.update_quest_progress(
            self.test_user_id,
            quest_id,
            50
        )
        self.assertTrue(success)
