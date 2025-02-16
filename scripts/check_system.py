import os
import sys
import sqlite3
from pathlib import Path
import importlib.util

def check_directories():
    """Проверка наличия необходимых директорий"""
    required_dirs = ['maps', 'previews', 'cache', 'logs']
    missing_dirs = []
    
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
    
    return missing_dirs

def check_dependencies():
    """Проверка установленных зависимостей"""
    required_packages = [
        'folium',
        'telegram',
        'dotenv',
        'aiohttp',
        'PIL',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    return missing_packages

def check_database():
    """Проверка структуры базы данных"""
    required_tables = [
        'live_positions',
        'search_sectors',
        'users',
        'operations',
        'teams'
    ]
    
    missing_tables = []
    
    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        
        for table in required_tables:
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table,))
            
            if not cursor.fetchone():
                missing_tables.append(table)
        
        conn.close()
    except Exception as e:
        return f"Database error: {e}"
    
    return missing_tables

def main():
    """Основная функция проверки"""
    print("Starting system check...\n")
    
    # Проверка директорий
    missing_dirs = check_directories()
    if missing_dirs:
        print("❌ Missing directories:")
        for directory in missing_dirs:
            print(f"  - {directory}")
        print("\nRun 'python scripts/setup.py' to create missing directories")
    else:
        print("✅ All required directories exist")
    
    # Проверка зависимостей
    print("\nChecking dependencies...")
    missing_packages = check_dependencies()
    if missing_packages:
        print("❌ Missing packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nRun 'pip install -r requirements.txt' to install missing packages")
    else:
        print("✅ All required packages are installed")
    
    # Проверка базы данных
    print("\nChecking database structure...")
    db_check = check_database()
    if isinstance(db_check, str):
        print(f"❌ Database error: {db_check}")
    elif db_check:
        print("❌ Missing tables:")
        for table in db_check:
            print(f"  - {table}")
        print("\nRun 'python scripts/setup.py' to apply migrations")
    else:
        print("✅ Database structure is correct")
    
    # Итоговый статус
    if not any([missing_dirs, missing_packages, db_check]):
        print("\n✅ All systems are ready!")
        return 0
    else:
        print("\n❌ Some components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())