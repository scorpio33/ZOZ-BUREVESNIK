import sqlite3
import datetime
import json

def adapt_datetime(dt):
    return dt.isoformat()

def create_test_data():
    """Создание тестовых данных для проверки функциональности"""
    try:
        sqlite3.register_adapter(datetime.datetime, adapt_datetime)
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        
        # Начинаем транзакцию
        conn.execute("BEGIN TRANSACTION")
        
        try:
            # 1. Создаем тестовых пользователей
            current_time = datetime.datetime.now().isoformat()
            test_users = [
                (991426127, 'developer', 'Developer', 'Admin', 'admin', current_time),
                (100001, 'coordinator1', 'John', 'Doe', 'coordinator', current_time),
                (100002, 'volunteer1', 'Jane', 'Smith', 'user', current_time)
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, test_users)
            
            # 2. Создаем тестовую операцию
            cursor.execute("""
                INSERT OR IGNORE INTO operations 
                (title, description, status, coordinator_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, ('Тестовый поиск', 'Тестовая поисковая операция', 'active', 100001, current_time))
            
            # Получаем ID созданной операции
            operation_id = cursor.lastrowid
            
            # 3. Создаем тестовую команду
            cursor.execute("""
                INSERT OR IGNORE INTO teams 
                (name, leader_id, operation_id, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, ('Тестовая команда', 100001, operation_id, 'active', current_time))
            
            # 4. Создаем тестовый сектор поиска
            test_coordinates = json.dumps({
                'type': 'Polygon',
                'coordinates': [[[30.0, 60.0], [30.1, 60.0], [30.1, 60.1], [30.0, 60.1], [30.0, 60.0]]]
            })
            
            cursor.execute("""
                INSERT OR IGNORE INTO search_sectors 
                (operation_id, name, coordinates, status)
                VALUES (?, ?, ?, ?)
            """, (operation_id, 'Тестовый сектор', test_coordinates, 'pending'))
            
            # 5. Создаем тестовую позицию
            cursor.execute("""
                INSERT OR IGNORE INTO live_positions 
                (user_id, latitude, longitude, accuracy, operation_id)
                VALUES (?, ?, ?, ?, ?)
            """, (100002, 30.05, 60.05, 10.0, operation_id))
            
            # Подтверждаем транзакцию
            conn.commit()
            print("✅ Тестовые данные успешно созданы")
            
            # Выводим статистику
            print("\nСтатистика базы данных:")
            tables = ['users', 'operations', 'teams', 'search_sectors', 'live_positions']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  └── {table}: {count} записей")
            
        except Exception as e:
            conn.rollback()
            raise e
            
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {str(e)}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    create_test_data()
