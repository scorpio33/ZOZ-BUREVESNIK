import unittest
import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем все тесты
from tests.test_quest_system import TestQuestSystem
from tests.test_coordination_system import TestCoordinationSystem
from tests.test_notification_system import TestNotificationSystem

def run_tests():
    """Запуск всех тестов"""
    # Создаем набор тестов
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQuestSystem))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCoordinationSystem))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNotificationSystem))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Возвращаем код завершения
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
