import asyncio
import psutil
import logging
import aiohttp
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from collections import deque

@dataclass
class BotMetrics:
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_users: int
    response_time: float
    error_count: int
    db_size: int
    active_searches: int
    
class BotMonitor:
    def __init__(self, config_path: str = 'config/monitor_config.json'):
        self.config = self._load_config(config_path)
        self.metrics_history = deque(maxlen=1000)  # Хранить последние 1000 метрик
        self.alert_thresholds = self.config['alert_thresholds']
        self.process = psutil.Process()
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/monitor.log'),
                logging.StreamHandler()
            ]
        )
        
        # Создание директорий для метрик
        Path('metrics').mkdir(exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """Загрузка конфигурации мониторинга"""
        with open(config_path) as f:
            return json.load(f)

    async def collect_metrics(self) -> BotMetrics:
        """Сбор метрик бота"""
        try:
            # Системные метрики
            cpu = self.process.cpu_percent()
            memory = self.process.memory_info().rss / 1024 / 1024  # MB
            
            # Метрики бота через API
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config['bot_api_url']}/metrics") as response:
                    bot_metrics = await response.json()
            
            # Создание объекта метрик
            metrics = BotMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu,
                memory_usage=memory,
                active_users=bot_metrics['active_users'],
                response_time=bot_metrics['avg_response_time'],
                error_count=bot_metrics['error_count'],
                db_size=bot_metrics['database_size'],
                active_searches=bot_metrics['active_searches']
            )
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            logging.error(f"Error collecting metrics: {e}")
            return None

    def check_alerts(self, metrics: BotMetrics) -> List[str]:
        """Проверка метрик на превышение пороговых значений"""
        alerts = []
        
        if metrics.cpu_usage > self.alert_thresholds['cpu']:
            alerts.append(f"HIGH CPU USAGE: {metrics.cpu_usage}%")
            
        if metrics.memory_usage > self.alert_thresholds['memory']:
            alerts.append(f"HIGH MEMORY USAGE: {metrics.memory_usage}MB")
            
        if metrics.response_time > self.alert_thresholds['response_time']:
            alerts.append(f"HIGH RESPONSE TIME: {metrics.response_time}s")
            
        if metrics.error_count > self.alert_thresholds['errors']:
            alerts.append(f"HIGH ERROR COUNT: {metrics.error_count}")
            
        return alerts

    async def save_metrics(self, metrics: BotMetrics):
        """Сохранение метрик в файл"""
        date_str = metrics.timestamp.strftime('%Y-%m-%d')
        metrics_file = Path(f'metrics/bot_metrics_{date_str}.json')
        
        # Преобразование метрик в словарь
        metrics_dict = {
            'timestamp': metrics.timestamp.isoformat(),
            'cpu_usage': metrics.cpu_usage,
            'memory_usage': metrics.memory_usage,
            'active_users': metrics.active_users,
            'response_time': metrics.response_time,
            'error_count': metrics.error_count,
            'db_size': metrics.db_size,
            'active_searches': metrics.active_searches
        }
        
        # Добавление метрик в файл
        if metrics_file.exists():
            data = json.loads(metrics_file.read_text())
            data['metrics'].append(metrics_dict)
        else:
            data = {'metrics': [metrics_dict]}
            
        metrics_file.write_text(json.dumps(data, indent=2))

    async def monitor_loop(self):
        """Основной цикл мониторинга"""
        while True:
            try:
                # Сбор метрик
                metrics = await self.collect_metrics()
                if metrics:
                    # Проверка алертов
                    alerts = self.check_alerts(metrics)
                    for alert in alerts:
                        logging.warning(f"ALERT: {alert}")
                    
                    # Сохранение метрик
                    await self.save_metrics(metrics)
                    
                    # Вывод текущего состояния
                    logging.info(
                        f"Bot Status: CPU={metrics.cpu_usage:.1f}%, "
                        f"Memory={metrics.memory_usage:.1f}MB, "
                        f"Users={metrics.active_users}, "
                        f"Response={metrics.response_time:.3f}s"
                    )
                
                # Пауза между проверками
                await asyncio.sleep(self.config['check_interval'])
                
            except Exception as e:
                logging.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)

async def main():
    monitor = BotMonitor()
    await monitor.monitor_loop()

if __name__ == "__main__":
    asyncio.run(main())