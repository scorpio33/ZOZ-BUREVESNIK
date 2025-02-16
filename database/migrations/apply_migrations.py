import sqlite3
import logging
import os
from datetime import datetime

class DatabaseMigration:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('DatabaseMigration')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_migrations_table(self, conn):
        """Создание таблицы для отслеживания миграций"""
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applied_migrations (
                migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    def _get_applied_migrations(self, conn):
        """Получение списка уже применённых миграций"""
        cursor = conn.cursor()
        cursor.execute('SELECT filename FROM applied_migrations')
        return {row[0] for row in cursor.fetchall()}

    def apply_migrations(self):
        """Применение всех миграций"""
        try:
            conn = self._get_connection()
            self._create_migrations_table(conn)
            applied_migrations = self._get_applied_migrations(conn)
            
            # Порядок миграций
            migrations_order = [
                '01_update_passwords.sql',
                '02_group_updates.sql',
                '03_coordinator_system.sql',
                '04_group_system.sql',
                '05_coordination_system.sql',
                '06_coordinator_permissions.sql',
                '07_search_operations.sql',
                'task_system_update.sql',
                'task_system_extensions.sql',
                'sectors.sql'
            ]

            for migration_file in migrations_order:
                if migration_file in applied_migrations:
                    self.logger.info(f"Migration {migration_file} already applied")
                    continue

                try:
                    # Читаем файл миграции
                    with open(f'database/migrations/{migration_file}', 'r', encoding='utf-8') as f:
                        sql = f.read()

                    # Применяем миграцию
                    cursor = conn.cursor()
                    cursor.executescript(sql)
                    
                    # Записываем информацию о применённой миграции
                    cursor.execute(
                        'INSERT INTO applied_migrations (filename) VALUES (?)',
                        (migration_file,)
                    )
                    conn.commit()
                    
                    self.logger.info(f"Successfully applied migration: {migration_file}")
                
                except Exception as e:
                    self.logger.error(f"Error applying migration {migration_file}: {str(e)}")
                    conn.rollback()
                    raise

        except Exception as e:
            self.logger.error(f"Database migration failed: {str(e)}")
            raise
        finally:
            conn.close()

    def verify_migrations(self):
        """Проверка структуры базы данных после миграций"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Проверяем наличие всех необходимых таблиц
            tables_to_check = [
                'users', 'coordinator_requests', 'coordinator_permissions',
                'task_escalations', 'coordination_tasks', 'search_groups',
                'group_members', 'task_progress', 'task_notifications'
            ]
            
            for table in tables_to_check:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if not cursor.fetchone():
                    self.logger.error(f"Table {table} is missing!")
                else:
                    self.logger.info(f"Table {table} exists")
            
            self.logger.info("Database structure verification completed")
            
        except Exception as e:
            self.logger.error(f"Verification failed: {str(e)}")
            raise
        finally:
            conn.close()

if __name__ == "__main__":
    # Путь к базе данных
    DB_PATH = 'bot_database.db'
    
    migrator = DatabaseMigration(DB_PATH)
    
    try:
        # Применяем миграции
        migrator.apply_migrations()
        
        # Проверяем результат
        migrator.verify_migrations()
        
        print("\n✅ Migrations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
