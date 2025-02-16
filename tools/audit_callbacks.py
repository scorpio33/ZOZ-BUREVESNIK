import logging
from pathlib import Path
from core.callback_collector import CallbackCollector
from core.callback_audit import CallbackAudit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def audit_callbacks():
    collector = CallbackCollector()
    audit = CallbackAudit()
    
    # Список файлов для проверки
    files_to_check = [
        'handlers/menu_handler.py',
        'handlers/map_handler.py',
        'handlers/coordinator_handler.py',
        'handlers/auth_handler.py',
        'handlers/donation_handler.py',
        'handlers/quest_handler.py'
    ]
    
    # Собираем данные из всех файлов
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                collector.collect_from_menu_handler(content)
                collector.collect_from_handlers(content)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    # Анализируем результаты
    report = collector.get_report()
    
    # Выводим результаты
    logger.info("=== Callback Audit Results ===")
    logger.info(f"\nFound callbacks ({len(report['found_callbacks'])}):")
    for cb in sorted(report['found_callbacks']):
        logger.info(f"- {cb}")
    
    logger.info(f"\nImplemented handlers ({len(report['implemented_handlers'])}):")
    for handler in sorted(report['implemented_handlers']):
        logger.info(f"- {handler}")
    
    logger.info(f"\nMissing handlers ({len(report['missing_handlers'])}):")
    for missing in sorted(report['missing_handlers']):
        logger.info(f"- {missing}")

if __name__ == '__main__':
    audit_callbacks()