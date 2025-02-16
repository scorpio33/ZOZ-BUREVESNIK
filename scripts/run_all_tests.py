import unittest
import sys
import os
import coverage
import logging
import json
from datetime import datetime
from pathlib import Path
import asyncio
import pytest

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TestRunner')

class TestReportManager:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.report_info_file = root_dir / 'test_report_location.json'
        self.coverage_dir = root_dir / 'coverage_report'
        
    def save_report_location(self, coverage_percentage: float):
        """Сохраняет информацию о местоположении отчета"""
        report_info = {
            'report_path': str(self.coverage_dir.absolute()),
            'timestamp': datetime.now().isoformat(),
            'coverage_percentage': coverage_percentage,
            'last_run': {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S')
            }
        }
        
        with open(self.report_info_file, 'w', encoding='utf-8') as f:
            json.dump(report_info, f, indent=2, ensure_ascii=False)
        
        # Создаем текстовый файл с путем для быстрого доступа
        with open(self.root_dir / 'coverage_report_path.txt', 'w', encoding='utf-8') as f:
            f.write(f"Подробный отчет о покрытии доступен в: {self.coverage_dir.absolute()}\n")
            f.write(f"Процент покрытия кода: {coverage_percentage:.1f}%\n")
            f.write(f"Время создания отчета: {report_info['last_run']['date']} {report_info['last_run']['time']}")

class AsyncTestRunner:
    def __init__(self):
        self.results = []
        self.failures = []
        self.errors = []
        self.tests_run = 0

    async def run_test(self, test):
        try:
            if hasattr(test, 'asyncSetUp'):
                await test.asyncSetUp()
            
            # Получаем все тестовые методы
            test_methods = [method for method in dir(test) if method.startswith('test_')]
            
            for method_name in test_methods:
                method = getattr(test, method_name)
                if asyncio.iscoroutinefunction(method):
                    try:
                        await method()
                        self.tests_run += 1
                    except AssertionError as e:
                        self.failures.append((f"{test.__class__.__name__}.{method_name}", str(e)))
                    except Exception as e:
                        self.errors.append((f"{test.__class__.__name__}.{method_name}", str(e)))
                else:
                    try:
                        method()
                        self.tests_run += 1
                    except AssertionError as e:
                        self.failures.append((f"{test.__class__.__name__}.{method_name}", str(e)))
                    except Exception as e:
                        self.errors.append((f"{test.__class__.__name__}.{method_name}", str(e)))

            if hasattr(test, 'asyncTearDown'):
                await test.asyncTearDown()
                
        except Exception as e:
            self.errors.append((test.__class__.__name__, str(e)))

def run_all_tests():
    """Запуск всех тестов проекта с отчетом о покрытии"""
    # Добавляем корневую директорию в PYTHONPATH
    root_dir = Path(__file__).parent.parent
    sys.path.append(str(root_dir))
    
    report_manager = TestReportManager(root_dir)
    
    logger.info("🚀 Начало тестирования")
    
    # Инициализация coverage
    cov = coverage.Coverage(
        branch=True,
        source=[str(root_dir / 'handlers'),
                str(root_dir / 'core'),
                str(root_dir / 'services')],
        omit=['*/__init__.py', '*/tests/*', '*/venv/*']
    )
    
    try:
        # Запуск coverage
        cov.start()
        
        # Создаем набор тестов
        loader = unittest.TestLoader()
        start_dir = str(Path(__file__).parent.parent / 'tests')
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        # Создаем асинхронный runner
        async_runner = AsyncTestRunner()
        
        # Запускаем тесты асинхронно
        async def run_suite():
            for test_case in suite:
                if isinstance(test_case, unittest.TestSuite):
                    for test in test_case:
                        await async_runner.run_test(test)
                else:
                    await async_runner.run_test(test_case)
        
        # Запускаем тесты
        asyncio.run(run_suite())
        
        # Останавливаем coverage
        cov.stop()
        
        # Выводим статистику тестов
        logger.info("\n=== 📊 Статистика тестирования ===")
        successful_tests = async_runner.tests_run - len(async_runner.failures) - len(async_runner.errors)
        logger.info(f"✅ Успешных тестов: {successful_tests}")
        logger.info(f"❌ Ошибок: {len(async_runner.failures)}")
        logger.info(f"⚠️ Исключений: {len(async_runner.errors)}")
        
        try:
            # Выводим отчет о покрытии
            logger.info("\n=== 📈 Отчет о покрытии кода ===")
            
            # Получаем процент покрытия через временный файл
            report_manager.coverage_dir.mkdir(exist_ok=True)
            percentage = cov.report(file=open(report_manager.coverage_dir / 'coverage.txt', 'w'))
            
            logger.info(f"Общий процент покрытия: {percentage:.1f}%")
            
            # Генерируем HTML отчет
            cov.html_report(directory=str(report_manager.coverage_dir))
            
            # Сохраняем информацию о местоположении отчета
            report_manager.save_report_location(percentage)
            
            logger.info(f"\nПодробный отчет о покрытии доступен в: {report_manager.coverage_dir.absolute()}")
            
            # Создаем детальный отчет о тестировании
            create_detailed_report(
                report_manager.coverage_dir,
                {
                    'total_tests': async_runner.tests_run,
                    'successful_tests': successful_tests,
                    'failures': len(async_runner.failures),
                    'errors': len(async_runner.errors),
                    'coverage_percentage': percentage,
                    'failures_details': [f"{name}: {error}" for name, error in async_runner.failures],
                    'errors_details': [f"{name}: {error}" for name, error in async_runner.errors]
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка при анализе покрытия кода: {e}")
            logger.exception(e)
        
        if async_runner.failures or async_runner.errors:
            logger.error("\n❌ Некоторые тесты завершились неудачно:")
            for name, error in async_runner.failures:
                logger.error(f"- Failure in {name}: {error}")
            for name, error in async_runner.errors:
                logger.error(f"- Error in {name}: {error}")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении тестов: {e}")
        return 1

def create_detailed_report(report_dir: Path, data: dict):
    """Создает подробный отчет о тестировании"""
    report_path = report_dir / 'detailed_test_report.html'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Детальный отчет о тестировании</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .success {{ background-color: #dff0d8; }}
            .warning {{ background-color: #fcf8e3; }}
            .error {{ background-color: #f2dede; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Отчет о тестировании</h1>
            <div class="status success">
                <h2>Общая статистика</h2>
                <p>Всего тестов: {data['total_tests']}</p>
                <p>Успешных тестов: {data['successful_tests']}</p>
                <p>Процент покрытия кода: {data['coverage_percentage']:.1f}%</p>
            </div>
            
            <div class="status warning">
                <h2>Ошибки и исключения</h2>
                <p>Количество ошибок: {data['failures']}</p>
                <p>Количество исключений: {data['errors']}</p>
            </div>
    """
    
    if data['failures_details'] or data['errors_details']:
        html_content += """
            <div class="status error">
                <h2>Детали ошибок</h2>
        """
        if data['failures_details']:
            html_content += "<h3>Ошибки:</h3><ul>"
            for failure in data['failures_details']:
                html_content += f"<li>{failure}</li>"
            html_content += "</ul>"
            
        if data['errors_details']:
            html_content += "<h3>Исключения:</h3><ul>"
            for error in data['errors_details']:
                html_content += f"<li>{error}</li>"
            html_content += "</ul>"
        html_content += "</div>"
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    sys.exit(run_all_tests())
