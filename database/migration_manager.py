import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path
import json
import logging

class MigrationManager:
    def __init__(self, db_path: str = 'database/bot.db'):
        self.db_path = db_path
        self.migrations_path = Path('database/migrations')
        self.backups_path = Path('database/backups')
        self.logger = logging.getLogger('MigrationManager')
        
        # Создаём необходимые директории
        self.migrations_path.mkdir(parents=True, exist_ok=True)
        self.backups_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем таблицу версий
        self._init_version_table()

    def _init_version_table(self):
        """Инициализация таблицы версий"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS migrations_history (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    is_success BOOLEAN DEFAULT 1,
                    rollback_version TEXT
                )
            ''')

    def get_current_version(self) -> str:
        """Получение текущей версии базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT version FROM migrations_history 
                WHERE is_success = 1 
                ORDER BY applied_at DESC LIMIT 1
            ''')
            result = cursor.fetchone()
            return result[0] if result else '0.0.0'

    def create_backup(self) -> str:
        """Создание резервной копии базы данных"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backups_path / f'backup_{timestamp}.db'
        
        if os.path.exists(self.db_path):
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f'Created backup: {backup_path}')
            return str(backup_path)
        return ''

    def apply_migration(self, version: str, description: str = '') -> bool:
        """Применение миграции"""
        migration_file = self.migrations_path / f'v{version}.sql'
        if not migration_file.exists():
            self.logger.error(f'Migration file not found: {migration_file}')
            return False

        # Создаём резервную копию
        backup_path = self.create_backup()

        try:
            # Читаем SQL скрипт
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # Применяем миграцию
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(sql_script)
                
                # Записываем информацию о миграции
                conn.execute('''
                    INSERT INTO migrations_history (version, description, rollback_version)
                    VALUES (?, ?, ?)
                ''', (version, description, self.get_current_version()))
                
            self.logger.info(f'Successfully applied migration v{version}')
            return True

        except Exception as e:
            self.logger.error(f'Error applying migration v{version}: {str(e)}')
            # Восстанавливаем из бэкапа при ошибке
            if backup_path:
                shutil.copy2(backup_path, self.db_path)
                self.logger.info('Restored from backup')
            return False

    def rollback(self) -> bool:
        """Откат к предыдущей версии"""
        current_version = self.get_current_version()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT rollback_version FROM migrations_history 
                WHERE version = ? AND is_success = 1
            ''', (current_version,))
            result = cursor.fetchone()
            
            if not result:
                self.logger.error('No previous version found')
                return False
                
            rollback_version = result[0]
            rollback_file = self.migrations_path / f'v{rollback_version}_rollback.sql'
            
            if not rollback_file.exists():
                self.logger.error(f'Rollback file not found: {rollback_file}')
                return False

            # Создаём резервную копию
            backup_path = self.create_backup()

            try:
                # Применяем скрипт отката
                with open(rollback_file, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                conn.executescript(sql_script)
                
                # Обновляем историю миграций
                conn.execute('''
                    UPDATE migrations_history 
                    SET is_success = 0 
                    WHERE version = ?
                ''', (current_version,))
                
                self.logger.info(f'Successfully rolled back to v{rollback_version}')
                return True

            except Exception as e:
                self.logger.error(f'Error rolling back: {str(e)}')
                if backup_path:
                    shutil.copy2(backup_path, self.db_path)
                    self.logger.info('Restored from backup')
                return False

    def generate_test_data(self):
        """Генерация тестовых данных"""
        test_data_file = self.migrations_path / 'test_data.sql'
        if not test_data_file.exists():
            self.logger.error('Test data file not found')
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                with open(test_data_file, 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
            self.logger.info('Successfully generated test data')
            return True
        except Exception as e:
            self.logger.error(f'Error generating test data: {str(e)}')
            return False