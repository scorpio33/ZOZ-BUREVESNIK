import unittest
import sys
import os
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TestRunner')

def run_all_tests():
    """Запуск всех тестов проекта"""
    # Добавляем корневую директорию в PYTHONPATH
    root_dir = Path(__file__).parent.parent
    sys.path.append(str(root_dir))
    
    logger.info("🚀 Начало тестирования")
    
    # Создаем набор тестов
    loader = unittest.TestLoader()
    start_dir = str(Path(__file__).parent)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим статистику
    logger.info("\n=== 📊 Статистика тестирования ===")
    logger.info(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"❌ Ошибок: {len(result.failures)}")
    logger.info(f"⚠️ Исключений: {len(result.errors)}")
    
    # Возвращаем код завершения
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests())