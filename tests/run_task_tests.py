import unittest
import asyncio
import sys
from pathlib import Path

def run_task_tests():
    """Запуск тестов системы задач"""
    # Добавляем корневую директорию в PYTHONPATH
    root_dir = Path(__file__).parent.parent
    sys.path.append(str(root_dir))
    
    # Загружаем тесты
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(Path(__file__).parent),
        pattern='test_task_*.py'
    )
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем код состояния
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_task_tests())