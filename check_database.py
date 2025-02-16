import sqlite3
import os

def execute_sql_file(db_path, sql_file):
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Читаем и выполняем SQL файл
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            cursor.executescript(sql_script)
        
        # Проверяем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Существующие таблицы:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Показываем структуру каждой таблицы
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.commit()
        print("\nSQL файл успешно выполнен!")
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = "bot_database.db"
    sql_file = "database/migrations/04_group_system.sql"
    
    if os.path.exists(sql_file):
        execute_sql_file(db_path, sql_file)
    else:
        print(f"Файл {sql_file} не найден!")