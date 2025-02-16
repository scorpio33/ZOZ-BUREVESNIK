import time
import logging
from functools import wraps
from typing import Dict, List

logger = logging.getLogger(__name__)

class DatabaseMonitor:
    def __init__(self):
        self.query_stats: Dict[str, List[float]] = {}
        
    def monitor_query(self, query_name: str):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if query_name not in self.query_stats:
                        self.query_stats[query_name] = []
                    self.query_stats[query_name].append(execution_time)
                    
                    if execution_time > 1.0:  # Порог в 1 секунду
                        logger.warning(f"Slow query detected: {query_name} took {execution_time:.2f} seconds")
                    
                    return result
                except Exception as e:
                    logger.error(f"Query error in {query_name}: {str(e)}")
                    raise
            return wrapper
        return decorator

    def get_statistics(self) -> Dict:
        """Получение статистики по запросам"""
        stats = {}
        for query_name, times in self.query_stats.items():
            stats[query_name] = {
                'avg_time': sum(times) / len(times),
                'max_time': max(times),
                'min_time': min(times),
                'total_calls': len(times)
            }
        return stats