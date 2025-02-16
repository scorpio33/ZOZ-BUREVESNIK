import csv
import json
import xlsxwriter
from typing import List, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskExporter:
    def __init__(self, db_manager):
        self.db = db_manager

    async def export_tasks(self, tasks: List[Dict], format: str = 'csv') -> Optional[bytes]:
        """Экспорт задач в различные форматы"""
        try:
            if format == 'csv':
                return await self._export_to_csv(tasks)
            elif format == 'xlsx':
                return await self._export_to_xlsx(tasks)
            elif format == 'json':
                return await self._export_to_json(tasks)
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            logger.error(f"Error exporting tasks: {e}")
            return None

    async def _export_to_csv(self, tasks: List[Dict]) -> bytes:
        """Экспорт в CSV формат"""
        output = []
        headers = ['ID', 'Название', 'Описание', 'Приоритет', 'Статус', 
                  'Создано', 'Срок', 'Исполнитель']
        
        output.append(','.join(headers))
        
        for task in tasks:
            row = [
                str(task['task_id']),
                task['title'],
                task['description'].replace(',', ';'),
                str(task['priority_level']),
                task['status'],
                task['created_at'],
                task.get('deadline', ''),
                task.get('assigned_to_name', '')
            ]
            output.append(','.join(row))
        
        return '\n'.join(output).encode('utf-8')

    async def _export_to_xlsx(self, tasks: List[Dict]) -> bytes:
        """Экспорт в Excel формат"""
        import io
        output = io.BytesIO()
        
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # Форматирование
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#CCCCCC'
        })
        
        # Заголовки
        headers = ['ID', 'Название', 'Описание', 'Приоритет', 'Статус', 
                  'Создано', 'Срок', 'Исполнитель']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Данные
        for row, task in enumerate(tasks, start=1):
            worksheet.write(row, 0, task['task_id'])
            worksheet.write(row, 1, task['title'])
            worksheet.write(row, 2, task['description'])
            worksheet.write(row, 3, task['priority_level'])
            worksheet.write(row, 4, task['status'])
            worksheet.write(row, 5, task['created_at'])
            worksheet.write(row, 6, task.get('deadline', ''))
            worksheet.write(row, 7, task.get('assigned_to_name', ''))
        
        workbook.close()
        return output.getvalue()

    async def _export_to_json(self, tasks: List[Dict]) -> bytes:
        """Экспорт в JSON формат"""
        return json.dumps(tasks, ensure_ascii=False, indent=2).encode('utf-8')