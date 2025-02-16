from typing import Dict, List, Optional
from datetime import datetime
import logging
import numpy as np

logger = logging.getLogger(__name__)

class EfficiencyManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def calculate_operation_metrics(self, operation_id: int) -> Dict:
        """Расчет метрик эффективности операции"""
        try:
            # Получаем базовые данные операции
            operation = await self.db.fetch_one("""
                SELECT * FROM search_operations WHERE operation_id = ?
            """, (operation_id,))

            # Рассчитываем время реагирования
            response_time = await self._calculate_response_time(operation_id)
            
            # Рассчитываем эффективность координации
            coordination_score = await self._calculate_coordination_score(operation_id)
            
            # Рассчитываем эффективность использования ресурсов
            resource_efficiency = await self._calculate_resource_efficiency(operation_id)
            
            # Рассчитываем покрытие территории
            coverage_rate = await self._calculate_coverage_rate(operation_id)
            
            metrics = {
                'response_time': response_time,
                'coordination_score': coordination_score,
                'resource_efficiency': resource_efficiency,
                'coverage_rate': coverage_rate,
                'success_rate': 100 if operation['status'] == 'completed' else 0
            }
            
            # Сохраняем метрики
            await self._save_metrics(operation_id, metrics)
            
            return metrics

        except Exception as e:
            logger.error(f"Error calculating operation metrics: {e}")
            return None

    async def get_team_performance(self, team_id: int, operation_id: int) -> Dict:
        """Получение метрик эффективности команды"""
        try:
            return await self.db.fetch_one("""
                SELECT * FROM team_performance_metrics
                WHERE team_id = ? AND operation_id = ?
            """, (team_id, operation_id))
        except Exception as e:
            logger.error(f"Error getting team performance: {e}")
            return None

    async def _calculate_response_time(self, operation_id: int) -> int:
        """Расчет времени реагирования"""
        timestamps = await self.db.fetch_all("""
            SELECT event_type, timestamp 
            FROM operation_timestamps 
            WHERE operation_id = ?
            ORDER BY timestamp
        """, (operation_id,))
        
        start_time = None
        first_action_time = None
        
        for ts in timestamps:
            if ts['event_type'] == 'operation_start':
                start_time = datetime.fromisoformat(ts['timestamp'])
            elif ts['event_type'] == 'first_team_deployed' and not first_action_time:
                first_action_time = datetime.fromisoformat(ts['timestamp'])
                
        if start_time and first_action_time:
            return int((first_action_time - start_time).total_seconds() / 60)
        return 0

    async def _calculate_coordination_score(self, operation_id: int) -> float:
        """Расчет оценки координации"""
        # Учитываем различные факторы
        factors = await self._get_coordination_factors(operation_id)
        weights = {
            'task_completion': 0.4,
            'communication': 0.3,
            'team_sync': 0.3
        }
        
        score = sum(factors[k] * weights[k] for k in weights)
        return round(score, 2)

    async def generate_efficiency_report(self, operation_id: int) -> Dict:
        """Генерация полного отчета по эффективности"""
        try:
            metrics = await self.calculate_operation_metrics(operation_id)
            team_metrics = await self._get_team_metrics(operation_id)
            
            return {
                'operation_metrics': metrics,
                'team_metrics': team_metrics,
                'recommendations': await self._generate_recommendations(metrics),
                'trends': await self._analyze_trends(operation_id),
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating efficiency report: {e}")
            return None