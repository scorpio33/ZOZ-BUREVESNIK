import asyncio
import aiohttp
import logging
import time
import psutil
from datetime import datetime
from typing import Dict, List, Any
from config.config import Config

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('LoadTester')

class LoadTester:
    def __init__(self):
        self.config = Config()
        self.bot_token = self.config.TOKEN
        self.base_url = f'https://api.telegram.org/bot{self.bot_token}'  # Изменено
        self.session = None
        self.batch_size = 5
        self.pool_delay = 2
        self.action_delay = 0.5
        self.active_users = 0
        self.max_users = 0
        self.retry_delays = {'default': 1, 'max_retries': 3}
        
        self.results = {
            'response_times': [],
            'errors': [],
            'pool_stats': {},
        }

    async def initialize_session(self):
        """Инициализация сессии"""
        self.session = aiohttp.ClientSession()
        logger.info("Session initialized")

    async def close_session(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            logger.info("Session closed")

    async def make_request(self, action_name: str, user_id: int, command: str, retry_timeout: int = 1):
        """Улучшенная обработка запросов"""
        start_time = time.time()
        retry_count = 0
        max_retries = self.retry_delays['max_retries']
        
        while retry_count < max_retries:
            try:
                url = f'{self.base_url}/sendMessage'
                data = {
                    'chat_id': user_id,
                    'text': f"Test command: {command}",
                    'parse_mode': 'HTML'
                }
                
                async with self.session.post(url, json=data, timeout=10) as response:
                    response_time = time.time() - start_time
                    self.results['response_times'].append(response_time)
                    
                    if response.status == 200:
                        logger.info(f"Success: {action_name} for user {user_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Request failed with status {response.status}: {error_text}")
                        self.results['errors'].append({
                            'action': action_name,
                            'user_id': user_id,
                            'status': response.status,
                            'error': error_text,
                            'time': datetime.now().isoformat()
                        })
                        return False
                        
            except Exception as e:
                logger.error(f"Request error: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(retry_timeout)
                
        return False

    async def simulate_user_actions(self, user_id: int):
        """Симуляция действий пользователя"""
        actions = [
            ('start', '/start'),
            ('help', '/help'),
            ('search', '/search'),
            ('map', '/map'),
            ('settings', '/settings')
        ]
        
        for action_name, command in actions:
            success = await self.make_request(action_name, user_id, command)
            if not success:
                logger.warning(f"Action {action_name} failed for user {user_id}")
            await asyncio.sleep(self.action_delay)

    async def run_user_pool(self, pool_number: int, start_user_id: int):
        """Запуск пула пользователей"""
        tasks = []
        pool_start_time = time.time()
        
        for i in range(self.batch_size):
            user_id = start_user_id + i
            tasks.append(self.simulate_user_actions(user_id))
            self.active_users += 1
            self.max_users = max(self.max_users, self.active_users)
        
        await asyncio.gather(*tasks)
        
        pool_end_time = time.time()
        self.results['pool_stats'][f'pool_{pool_number}'] = {
            'duration': pool_end_time - pool_start_time,
            'users': self.batch_size,
            'start_time': datetime.fromtimestamp(pool_start_time).strftime('%H:%M:%S'),
            'end_time': datetime.fromtimestamp(pool_end_time).strftime('%H:%M:%S')
        }
        
        self.active_users -= len(tasks)
        logger.info(f"Pool {pool_number} completed")

    async def run_load_test(self, total_users: int):
        """Запуск нагрузочного тестирования"""
        logger.info("\n=== Starting Base Load Test ===")
        await self.initialize_session()
        
        logger.info(f"Starting load test with {total_users} total users, {self.batch_size} concurrent users")
        
        num_pools = (total_users + self.batch_size - 1) // self.batch_size
        
        for i in range(num_pools):
            logger.info(f"Starting user pool {i+1}/{num_pools}")
            start_user_id = i * self.batch_size + 1
            await self.run_user_pool(i+1, start_user_id)
            await asyncio.sleep(self.pool_delay)
            await self.collect_system_metrics()
        
        self.analyze_results()
        await self.close_session()

    def analyze_results(self):
        """Расширенный анализ результатов"""
        if not self.results['response_times']:
            logger.warning("No response times recorded")
            return
            
        response_times = self.results['response_times']
        avg_response = sum(response_times) / len(response_times)
        max_response = max(response_times)
        min_response = min(response_times)
        
        # Добавляем перцентили
        sorted_times = sorted(response_times)
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        logger.info("\n=== Detailed Test Results ===")
        logger.info(f"Total Requests: {len(response_times)}")
        logger.info(f"Average Response Time: {avg_response:.2f}s")
        logger.info(f"Max Response Time: {max_response:.2f}s")
        logger.info(f"Min Response Time: {min_response:.2f}s")
        logger.info(f"95th Percentile: {p95:.2f}s")
        logger.info(f"99th Percentile: {p99:.2f}s")
        logger.info(f"Total Errors: {len(self.results['errors'])}")
        
        # Анализ по пулам
        logger.info("\n=== Pool Statistics ===")
        for pool_name, stats in self.results['pool_stats'].items():
            logger.info(f"{pool_name}:")
            logger.info(f"  Duration: {stats['duration']:.2f}s")
            logger.info(f"  Users: {stats['users']}")
            logger.info(f"  Time: {stats['start_time']} - {stats['end_time']}")

    async def monitor_performance(self):
        """Мониторинг производительности во время теста"""
        while True:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent}%")
            if memory_percent > 80:
                logger.warning(f"High memory usage: {memory_percent}%")
                
            await asyncio.sleep(1)

async def main():
    """Основная функция запуска тестирования"""
    tester = LoadTester()
    try:
        await tester.initialize_session()
        await tester.run_load_test(5)  # Тестируем с 5 пользователями
    finally:
        await tester.close_session()

if __name__ == "__main__":
    asyncio.run(main())
