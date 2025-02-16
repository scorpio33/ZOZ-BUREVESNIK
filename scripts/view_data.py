import sqlite3

def view_database_content():
    """Просмотр содержимого базы данных"""
    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        
        # Список таблиц для проверки
        tables = ['users', 'operations', 'teams', 'search_sectors', 'live_positions']
        
        for table in tables:
            print(f"\n📋 Таблица {table}:")
            # Получаем названия столбцов
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            print("  └── Columns:", ", ".join(columns))
            
            # Получаем данные
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                print(f"  └── Data: {row}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при просмотре данных: {str(e)}")
        return False

if __name__ == "__main__":
    view_database_content()