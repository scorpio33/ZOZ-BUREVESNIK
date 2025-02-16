from typing import Dict, List, Optional
from datetime import datetime
import json
import logging
from pathlib import Path
import csv
import xlsxwriter
from io import BytesIO

logger = logging.getLogger(__name__)

class ReportSystem:
    def __init__(self, db_manager, statistics_manager):
        self.db = db_manager
        self.stats = statistics_manager
        self.reports_dir = Path('data/reports')
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    async def generate_operation_report(self, operation_id: int) -> Dict:
        """Генерация подробного отчета по операции"""
        try:
            operation = await self.db.fetch_one("""
                SELECT * FROM search_operations 
                WHERE operation_id = ?
            """, (operation_id,))
            
            if not operation:
                return None

            # Сбор всех данных для отчета
            report_data = {
                "operation": operation,
                "statistics": await self._get_operation_statistics(operation_id),
                "participants": await self._get_participants_data(operation_id),
                "tasks": await self._get_tasks_data(operation_id),
                "tracks": await self._get_tracks_data(operation_id),
                "timeline": await self._get_operation_timeline(operation_id),
                "efficiency": await self._calculate_efficiency(operation_id),
                "generated_at": datetime.now().isoformat()
            }

            return report_data

        except Exception as e:
            logger.error(f"Error generating operation report: {e}")
            return None

    async def _get_operation_statistics(self, operation_id: int) -> Dict:
        """Сбор статистики по операции"""
        return {
            "total_participants": await self.db.count_participants(operation_id),
            "total_tasks": await self.db.count_tasks(operation_id),
            "completed_tasks": await self.db.count_completed_tasks(operation_id),
            "covered_area": await self.db.get_covered_area(operation_id),
            "total_distance": await self.db.get_total_distance(operation_id),
            "duration": await self.db.get_operation_duration(operation_id)
        }

    async def export_report(self, report_data: Dict, format: str = 'xlsx') -> bytes:
        """Экспорт отчета в различные форматы"""
        export_functions = {
            'xlsx': self._export_to_xlsx,
            'csv': self._export_to_csv,
            'json': self._export_to_json,
            'pdf': self._export_to_pdf
        }

        if format not in export_functions:
            raise ValueError(f"Unsupported format: {format}")

        return await export_functions[format](report_data)

    async def _export_to_xlsx(self, report_data: Dict) -> bytes:
        """Экспорт в Excel формат"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)

        # Форматирование
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'color': 'white'
        })

        # Основная информация
        self._write_operation_sheet(workbook, report_data, header_format)
        self._write_statistics_sheet(workbook, report_data, header_format)
        self._write_participants_sheet(workbook, report_data, header_format)
        self._write_tasks_sheet(workbook, report_data, header_format)

        workbook.close()
        output.seek(0)
        return output.getvalue()

    async def archive_operation(self, operation_id: int) -> bool:
        """Архивирование данных операции"""
        try:
            report_data = await self.generate_operation_report(operation_id)
            if not report_data:
                return False

            archive_dir = self.reports_dir / 'archives' / str(operation_id)
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Сохраняем в разных форматах
            for format in ['xlsx', 'json', 'pdf']:
                export_data = await self.export_report(report_data, format)
                with open(archive_dir / f'report.{format}', 'wb') as f:
                    f.write(export_data)

            # Архивируем треки
            await self._archive_tracks(operation_id, archive_dir)

            return True

        except Exception as e:
            logger.error(f"Error archiving operation: {e}")
            return False