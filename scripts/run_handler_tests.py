import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from tests.test_handlers import TestHandlers
import unittest

async def run_handler_tests():
    """Запуск тестов обработчиков"""
    # Создаем тестовый класс
    test_class = TestHandlers()
    
    # Запускаем setup
    await test_class.asyncSetUp()
    
    # Запускаем тесты
    try:
        await test_class.test_statistics_menu()
        await test_class.test_personal_statistics()
        await test_class.test_global_statistics()
        await test_class.test_settings_menu()
        await test_class.test_profile_settings()
        print("✅ Все тесты успешно пройдены")
        return True
    except AssertionError as e:
        print(f"❌ Тест не пройден: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при выполнении тестов: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_handler_tests())
    sys.exit(0 if success else 1)