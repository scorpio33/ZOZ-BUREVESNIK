import sys
import logging
from pathlib import Path
from database.migration_manager import MigrationManager

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('database/migrations.log')
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger('DatabaseUpdate')
    
    try:
        manager = MigrationManager()
        current_version = manager.get_current_version()
        
        # Получаем список всех миграций
        migrations_path = Path('database/migrations')
        available_migrations = sorted([
            f.stem[1:] for f in migrations_path.glob('v*.sql')
            if not f.stem.endswith('_rollback')
        ])
        
        if not available_migrations:
            logger.info('No migrations found')
            return 0
            
        # Находим миграции для применения
        to_apply = [v for v in available_migrations if v > current_version]
        
        if not to_apply:
            logger.info('Database is up to date')
            return 0
            
        logger.info(f'Current version: {current_version}')
        logger.info(f'Found {len(to_apply)} migrations to apply')
        
        # Применяем миграции
        for version in to_apply:
            logger.info(f'Applying migration v{version}...')
            if not manager.apply_migration(version):
                logger.error(f'Failed to apply migration v{version}')
                return 1
                
        logger.info('Database update completed successfully')
        return 0
        
    except Exception as e:
        logger.error(f'Update failed: {str(e)}')
        return 1

if __name__ == '__main__':
    sys.exit(main())