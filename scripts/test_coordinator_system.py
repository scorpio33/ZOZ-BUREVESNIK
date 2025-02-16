import asyncio
from telegram import Update, User
from unittest.mock import AsyncMock, MagicMock
from database.db_manager import DatabaseManager
from handlers.coordinator_handler import CoordinatorHandler

async def test_coordinator_system():
    """Тестирование системы координаторов"""
    try:
        # Инициализация базы данных
        db = DatabaseManager('bot_database.db')
        await db.init_db()

        # Создаем тестового пользователя
        test_user = {
            'user_id': 123456789,
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User'
        }
        await db.create_user(test_user)

        # Создаем тестовую заявку
        test_request = {
            'user_id': test_user['user_id'],
            'full_name': 'John Doe',
            'region': 'Test Region',
            'phone': '+1234567890',
            'team_name': 'Test Team',
            'position': 'volunteer',
            'search_count': 10,
            'experience_time': '1 year'
        }

        # Сохраняем заявку
        request_id = await db.execute(
            """
            INSERT INTO coordinator_requests 
            (user_id, full_name, region, phone, team_name, position, search_count, experience_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING request_id
            """,
            (
                test_request['user_id'],
                test_request['full_name'],
                test_request['region'],
                test_request['phone'],
                test_request['team_name'],
                test_request['position'],
                test_request['search_count'],
                test_request['experience_time']
            )
        )

        print("✅ Test request created successfully")

        # Проверяем статус заявки
        request = await db.execute_query_fetchone(
            "SELECT * FROM coordinator_requests WHERE request_id = ?",
            (request_id,)
        )
        
        if request and request['status'] == 'pending':
            print("✅ Request status is correct")
        else:
            print("❌ Request status check failed")

        # Очищаем тестовые данные
        await db.execute("DELETE FROM coordinator_requests WHERE user_id = ?", (test_user['user_id'],))
        await db.execute("DELETE FROM users WHERE user_id = ?", (test_user['user_id'],))

        print("✅ Test completed successfully")
        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_coordinator_system())
    exit(0 if success else 1)