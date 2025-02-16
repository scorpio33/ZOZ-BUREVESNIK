import unittest
from unittest.mock import MagicMock, patch
import asyncio
from datetime import datetime
from core.report_system import ReportSystem
from database.db_manager import DatabaseManager
from tests.base_test import BaseTestCase
from core.statistics_manager import StatisticsManager

class TestReportSystem(unittest.TestCase):
    async def asyncSetUp(self):
        self.db = DatabaseManager(":memory:")
        await self.db.init_db()
        self.report_system = ReportSystem(self.db)
        
        # Create test operation
        self.test_operation_id = await self.db.create_operation({
            "name": "Test Operation",
            "status": "active"
        })

    async def test_generate_operation_report(self):
        """Test report generation"""
        report = await self.report_system.generate_operation_report(self.test_operation_id)
        self.assertIsNotNone(report)
        self.assertIn('operation', report)
        self.assertIn('statistics', report)

    async def test_export_report(self):
        """Test report export"""
        report_data = await self.report_system.generate_operation_report(self.test_operation_id)
        exported_data = await self.report_system.export_report(report_data, 'xlsx')
        self.assertIsNotNone(exported_data)

    async def test_archive_operation(self):
        """Test operation archiving"""
        success = await self.report_system.archive_operation(self.test_operation_id)
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
