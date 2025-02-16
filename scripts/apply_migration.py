import sqlite3
import os
import sys
from pathlib import Path

def apply_migration(db_path: str, migration_file: str) -> bool:
    """Применяет миграцию к базе данных"""
    try:
        # Проверяем существование файлов
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            return False

        if not os.path.exists(migration_file):
            print(f"❌ Migration file not found: {migration_file}")
            return False

        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        
        try:
            # Читаем SQL-скрипт
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # Выполняем каждый запрос отдельно
            for statement in sql_script.split(';'):
                if statement.strip():
                    conn.execute(statement)
            
            conn.commit()
            print(f"✅ Migration {Path(migration_file).name} applied successfully")
            
            # Проверяем созданные таблицы
            cursor = conn.cursor()
            tables = ['users', 'operations', 'teams', 'live_positions', 'search_sectors']
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if cursor.fetchone():
                    print(f"✅ Table {table} created successfully")
                else:
                    print(f"❌ Table {table} creation failed")
            
            return True
            
        except sqlite3.Error as e:
            print(f"❌ SQLite error: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    # Пути к файлам
    db_path = 'bot_database.db'
    migration_file = 'database/migrations/001_core_tables.sql'

    # Применяем миграцию
    success = apply_migration(db_path, migration_file)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
