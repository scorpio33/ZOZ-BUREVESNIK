from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OperationAnalytics:
    total_area: float
    covered_area: float
    team_count: int
    participant_count: int
    task_completion_rate: float
    avg_response_time: float
    success_rate: float
    duration: int
    resource_utilization: float

class AnalyticsManager:
    def __init__(self, db_manager):
        self.db = db_manager

    async def get_detailed_analytics(self, operation_id: int) -> Dict:
        """Получение детальной аналитики операции"""
        try:
            # Базовая информация
            operation = await self.db.fetch_one("""
                SELECT * FROM operation_analytics WHERE operation_id = ?
            """, (operation_id,))
            
            # Временная линия событий
            timeline = await self._get_operation_timeline(operation_id)
            
            # Анализ эффективности команд
            team_analysis = await self._analyze_teams(operation_id)
            
            # Анализ покрытия территории
            coverage_analysis = await self._analyze_coverage(operation_id)
            
            # Анализ выполнения задач
            task_analysis = await self._analyze_tasks(operation_id)
            
            return {
                'basic_info': operation,
                'timeline': timeline,
                'team_analysis': team_analysis,
                'coverage_analysis': coverage_analysis,
                'task_analysis': task_analysis,
                'recommendations': await self._generate_recommendations(operation_id)
            }
        except Exception as e:
            logger.error(f"Error getting detailed analytics: {e}")
            return None

    async def generate_comparative_analysis(self, operation_ids: List[int]) -> Dict:
        """Сравнительный анализ нескольких операций"""
        try:
            operations_data = []
            for op_id in operation_ids:
                analytics = await self.get_detailed_analytics(op_id)
                if analytics:
                    operations_data.append(analytics)
            
            return {
                'operations': operations_data,
                'comparison': self._compare_operations(operations_data),
                'best_practices': await self._identify_best_practices(operations_data)
            }
        except Exception as e:
            logger.error(f"Error generating comparative analysis: {e}")
            return None

    async def _analyze_teams(self, operation_id: int) -> List[Dict]:
        """Анализ эффективности команд"""
        return await self.db.fetch_all("""
            SELECT 
                sg.group_id,
                sg.name as team_name,
                COUNT(DISTINCT gm.user_id) as member_count,
                tpm.coverage_area,
                tpm.task_completion_rate,
                tpm.coordination_score,
                tpm.response_time
            FROM search_groups sg
            LEFT JOIN group_members gm ON sg.group_id = gm.group_id
            LEFT JOIN team_performance_metrics tpm 
                ON sg.group_id = tpm.team_id 
                AND tpm.operation_id = sg.operation_id
            WHERE sg.operation_id = ?
            GROUP BY sg.group_id
        """, (operation_id,))

    async def _analyze_coverage(self, operation_id: int) -> Dict:
        """Анализ покрытия территории"""
        coverage_data = await self.db.fetch_all("""
            SELECT 
                sa.sector_id,
                sa.boundaries,
                sa.priority,
                sa.status,
                COUNT(DISTINCT t.track_id) as track_count,
                SUM(t.distance) as total_distance
            FROM search_areas sa
            LEFT JOIN tracks t ON ST_Intersects(sa.boundaries, t.path)
            WHERE sa.operation_id = ?
            GROUP BY sa.sector_id
        """, (operation_id,))
        
        return {
            'sectors': coverage_data,
            'total_coverage': self._calculate_total_coverage(coverage_data),
            'efficiency_score': self._calculate_coverage_efficiency(coverage_data)
        }
