import sqlite3
import sys

def check_database_structure():
    """Проверка структуры базы данных"""
    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()

        tables_to_check = [
            'users',
            'operations',
            'teams',
            'live_positions',
            'search_sectors'
        ]

        print("\nПроверка структуры базы данных:")
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                print(f"\n✅ Таблица {table}:")
                
                # Показываем структуру таблицы
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  └── {col[1]} ({col[2]})")
                    
                # Проверяем индексы
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=?", (table,))
                indexes = cursor.fetchall()
                if indexes:
                    print("  Индексы:")
                    for idx in indexes:
                        print(f"  └── {idx[0]}")
            else:
                print(f"❌ Таблица {table} отсутствует")

        conn.close()
        return True

    except Exception as e:
        print(f"Ошибка при проверке структуры: {str(e)}")
        return False

if __name__ == "__main__":
    if check_database_structure():
        print("\n✅ Проверка структуры базы данных завершена успешно")
        sys.exit(0)
    else:
        print("\n❌ Обнаружены проблемы со структурой базы данных")
        sys.exit(1)
