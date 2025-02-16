import asyncio
import aiohttp
import logging
import time
import psutil
from datetime import datetime
from typing import Dict, List, Optional
import json

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('LoadTester')

class LoadTester:
    def __init__(self, bot_token: str, base_url: str = "https://api.telegram.org"):
        self.bot_token = bot_token
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.results = {
            'response_times': [],
            'errors': [],
            'pools': {},
            'start_time': None,
            'end_time': None
        }
        self.test_users = [991426127]  # Ваш ID разработчика
        self.retry_delays = {
            'default': 1,
            'max_retries': 3
        }
        self.action_delay = 0.5

    async def initialize(self):
        """Инициализация сессии"""
        self.session = aiohttp.ClientSession()
        self.results['start_time'] = datetime.now()

    async def cleanup(self):
        """Очистка ресурсов"""
        if self.session:
            await self.session.close()
        self.results['end_time'] = datetime.now()

    async def monitor_performance(self):
        """Мониторинг производительности"""
        while True:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent}%")
            if memory_percent > 80:
                logger.warning(f"High memory usage: {memory_percent}%")
                
            await asyncio.sleep(1)

    async def make_request(self, action_name: str, user_id: int, command: str, retry_timeout: int = 1):
        """Выполнение запроса с улучшенной обработкой ошибок"""
        start_time = time.time()
        retry_count = 0
        max_retries = self.retry_delays['max_retries']
        
        while retry_count < max_retries:
            try:
                # Формируем полный URL для запроса
                url = f'{self.base_url}/bot{self.bot_token}/sendMessage'
                
                # Формируем текст сообщения в зависимости от команды
                message_text = self.get_command_message(command, user_id)
                
                async with self.session.post(
                    url,
                    json={
                        'chat_id': user_id,
                        'text': message_text,
                        'parse_mode': 'HTML'
                    },
                    timeout=10
                ) as response:
                    response_time = time.time() - start_time
                    self.results['response_times'].append(response_time)
                    
                    if response.status == 200:
                        logger.info(f"Success: {action_name} for user {user_id}")
                        return True
                    elif response.status == 429:  # Rate limit
                        response_json = await response.json()
                        retry_after = int(response_json.get('parameters', {}).get('retry_after', retry_timeout))
                        logger.warning(f"Rate limit hit, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        retry_count += 1
                    else:
                        error_data = await response.text()
                        logger.error(f"Request failed with status {response.status}: {error_data}")
                        self.results['errors'].append({
                            'action': action_name,
                            'user_id': user_id,
                            'status': response.status,
                            'error_data': error_data,
                            'time': datetime.now().isoformat()
                        })
                        return False
                        
            except Exception as e:
                logger.error(f"Request error: {str(e)}")
                self.results['errors'].append({
                    'action': action_name,
                    'user_id': user_id,
                    'error': str(e),
                    'time': datetime.now().isoformat()
                })
                await asyncio.sleep(retry_timeout)
                retry_count += 1
                
        return False

    def get_command_message(self, command: str, user_id: int) -> str:
        """Формирование текста сообщения для разных команд"""
        if command == '/start':
            return f"Добро пожаловать в тестовый бот! ID: {user_id}"
        elif command == '/help':
            return "Список доступных команд:\n/start - Начать\n/help - Помощь\n/search - Поиск\n/map - Карта\n/settings - Настройки"
        elif command == '/search':
            return "🔍 Меню поиска"
        elif command == '/map':
            return "🗺 Карта поиска"
        elif command == '/settings':
            return "⚙️ Настройки бота"
        return f"Выполнение команды: {command}"

    async def simulate_user_actions(self, user_id: int):
        """Симуляция действий пользователя"""
        actions = [
            ('start', '/start'),
            ('help', '/help'),
            ('search', '/search'),
            ('map', '/map'),
            ('settings', '/settings', {'retry_timeout': 5})
        ]
        
        for action_data in actions:
            action_name, command = action_data[:2]
            options = action_data[2] if len(action_data) > 2 else {}
            
            success = await self.make_request(
                action_name, 
                user_id, 
                command,
                retry_timeout=options.get('retry_timeout', self.retry_delays['default'])
            )
            if not success:
                logger.warning(f"Action {action_name} failed for user {user_id}")
            await asyncio.sleep(self.action_delay)

    async def run_user_pool(self, pool_id: int, users: List[int]):
        """Запуск пула пользователей"""
        pool_start = datetime.now()
        # Используем только существующих тестовых пользователей
        valid_users = [user for user in users if user in self.test_users]
        if not valid_users:
            logger.warning(f"No valid test users in pool {pool_id}")
            return
            
        tasks = [self.simulate_user_actions(user_id) for user_id in valid_users]
        await asyncio.gather(*tasks)
        pool_end = datetime.now()
        
        self.results['pools'][f'pool_{pool_id}'] = {
            'duration': (pool_end - pool_start).total_seconds(),
            'users': len(valid_users),
            'start_time': pool_start.strftime('%H:%M:%S'),
            'end_time': pool_end.strftime('%H:%M:%S')
        }
        
        logger.info(f"Pool {pool_id} completed with {len(valid_users)} valid users")

    def analyze_results(self):
        """Анализ результатов тестирования"""
        if not self.results['response_times']:
            logger.warning("No response times recorded")
            return
            
        response_times = self.results['response_times']
        avg_response = sum(response_times) / len(response_times)
        max_response = max(response_times)
        min_response = min(response_times)
        
        # Расчет перцентилей
        sorted_times = sorted(response_times)
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        logger.info("\n=== Test Results ===")
        logger.info(f"Total Requests: {len(response_times)}")
        logger.info(f"Average Response Time: {avg_response:.2f}s")
        logger.info(f"Max Response Time: {max_response:.2f}s")
        logger.info(f"Min Response Time: {min_response:.2f}s")
        logger.info(f"95th Percentile: {p95:.2f}s")
        logger.info(f"99th Percentile: {p99:.2f}s")
        logger.info(f"Total Errors: {len(self.results['errors'])}")
        
        logger.info("\n=== Pool Statistics ===")
        for pool_id, pool_data in self.results['pools'].items():
            logger.info(f"{pool_id}:")
            logger.info(f"  Duration: {pool_data['duration']:.2f}s")
            logger.info(f"  Users: {pool_data['users']}")
            logger.info(f"  Time: {pool_data['start_time']} - {pool_data['end_time']}")

    def save_results(self, filename: str = "load_test_results.json"):
        """Сохранение результатов в файл"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"Results saved to {filename}")

    async def initialize_user(self, user_id: int, max_retries: int = 3) -> bool:
        """Initialize user chat context before testing"""
        for attempt in range(max_retries):
            try:
                init_url = f"{self.base_url}/sendMessage"
                init_data = {
                    "chat_id": user_id,
                    "text": "/start",
                    "allow_creating_chat": True  # Allow creating new chat
                }
                async with self.session.post(init_url, json=init_data) as response:
                    if response.status == 200:
                        return True
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Initialization attempt {attempt + 1} failed for user {user_id}: {str(e)}")
        return False

    async def run_user_scenario(self, user_id: int):
        """Run test scenario for a single user"""
        # Initialize user first
        if not await self.initialize_user(user_id):
            logger.error(f"Failed to initialize user {user_id}")
            return

        # Continue with existing scenario
        for action in self.actions:
            await self.execute_action(action, user_id)
            await asyncio.sleep(self.delay)

async def main():
    """Основная функция запуска тестирования"""
    # Замените на реальный токен вашего бота
    bot_token = "YOUR_BOT_TOKEN"  
    tester = LoadTester(bot_token)
    
    try:
        await tester.initialize()
        
        # Запускаем мониторинг производительности
        monitor_task = asyncio.create_task(tester.monitor_performance())
        
        # Создаем пулы только с реальными тестовыми пользователями
        test_users = tester.test_users
        chunks = [test_users[i:i + 5] for i in range(0, len(test_users), 5)]
        
        for pool_id, users in enumerate(chunks, 1):
            await tester.run_user_pool(pool_id, users)
            await asyncio.sleep(2)
            
        monitor_task.cancel()
        tester.analyze_results()
        tester.save_results()
        
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
