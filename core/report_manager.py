import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import csv
import xlsxwriter
from io import BytesIO

logger = logging.getLogger(__name__)

class ReportManager:
    def __init__(self, db_manager, notification_manager):
        self.db = db_manager
        self.notification_manager = notification_manager
        self.reports_dir = Path('data/reports')
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    async def create_report(self, group_id: int, data: Dict) -> Optional[int]:
        """Создание отчета от группы"""
        try:
            report_data = {
                'group_id': group_id,
                'report_type': data['type'],
                'content': data['content'],
                'location': json.dumps(data.get('location', {})),
                'findings': json.dumps(data.get('findings', [])),
                'status': data.get('status', 'submitted'),
                'created_at': datetime.now().isoformat()
            }
            
            report_id = await self.db.execute_query("""
                INSERT INTO group_reports 
                (group_id, report_type, content, location, findings, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING report_id
            """, tuple(report_data.values()))

            if report_id:
                # Уведомляем координатора
                coordinator_id = await self.db.get_operation_coordinator(group_id)
                await self.notification_manager.send_notification(
                    coordinator_id,
                    f"📋 Новый отчет от группы #{group_id}\n"
                    f"Тип: {data['type']}\n"
                    f"Статус: {data['status']}"
                )
            
            return report_id
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            return None

    async def get_group_reports(self, group_id: int) -> List[Dict]:
        """Получение всех отчетов группы"""
        try:
            reports = await self.db.fetch_all("""
                SELECT r.*, g.name as group_name
                FROM group_reports r
                JOIN search_groups g ON r.group_id = g.group_id
                WHERE r.group_id = ?
                ORDER BY r.created_at DESC
            """, (group_id,))
            
            return [{
                **report,
                'location': json.loads(report['location']),
                'findings': json.loads(report['findings'])
            } for report in reports]
        except Exception as e:
            logger.error(f"Error getting group reports: {e}")
            return []

    async def update_report_status(self, report_id: int, status: str, comment: str = None) -> bool:
        """Обновление статуса отчета"""
        try:
            await self.db.execute_query("""
                UPDATE group_reports
                SET status = ?, coordinator_comment = ?
                WHERE report_id = ?
            """, (status, comment, report_id))
            
            # Уведомляем группу об обновлении статуса
            report = await self.db.fetch_one(
                "SELECT group_id FROM group_reports WHERE report_id = ?", 
                (report_id,)
            )
            
            if report:
                await self._notify_group_status_update(
                    report['group_id'], status, comment
                )
            
            return True
        except Exception as e:
            logger.error(f"Error updating report status: {e}")
            return False

    async def _notify_group_status_update(self, group_id: int, status: str, comment: str):
        """Уведомление группы об обновлении статуса отчета"""
        status_emoji = {
            'approved': '✅',
            'rejected': '❌',
            'pending': '⏳'
        }
        
        message = (
            f"{status_emoji.get(status, '❓')} Статус отчета обновлен\n"
            f"Новый статус: {status}\n"
        )
        if comment:
            message += f"Комментарий: {comment}"
            
        members = await self.db.get_group_members(group_id)
        for member in members:
            await self.notification_manager.send_notification(
                member['user_id'],
                message
            )

    async def generate_operation_report(self, operation_id: int) -> Dict:
        """Генерация отчета по операции"""
        try:
            # Получаем основную информацию об операции
            operation = await self.db.fetch_one("""
                SELECT * FROM search_operations 
                WHERE operation_id = ?
            """, (operation_id,))
            
            if not operation:
                return None

            # Получаем статистику по группам
            groups = await self.db.fetch_all("""
                SELECT g.*, COUNT(p.participant_id) as participants_count
                FROM search_groups g
                LEFT JOIN group_participants p ON g.group_id = p.group_id
                WHERE g.operation_id = ?
                GROUP BY g.group_id
            """, (operation_id,))

            # Получаем статистику по задачам
            tasks = await self.db.fetch_all("""
                SELECT t.*, COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
                       COUNT(*) as total_tasks
                FROM coordination_tasks t
                WHERE t.operation_id = ?
                GROUP BY t.status
            """, (operation_id,))

            return {
                "operation": operation,
                "groups": groups,
                "tasks": tasks,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating operation report: {e}")
            return None

    async def export_report(self, report_data: Dict, format: str = 'xlsx') -> Optional[bytes]:
        """Экспорт отчета в различные форматы"""
        try:
            if format == 'xlsx':
                return await self._export_to_xlsx(report_data)
            elif format == 'csv':
                return await self._export_to_csv(report_data)
            elif format == 'json':
                return json.dumps(report_data, indent=2).encode('utf-8')
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return None

    async def _export_to_xlsx(self, report_data: Dict) -> bytes:
        """Экспорт отчета в Excel формат"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)

        # Форматирование
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'color': 'white'
        })

        # Лист с основной информацией
        ws_main = workbook.add_worksheet('Основная информация')
        operation = report_data['operation']
        
        headers = ['ID', 'Название', 'Статус', 'Дата начала', 'Дата завершения']
        for col, header in enumerate(headers):
            ws_main.write(0, col, header, header_format)
            
        ws_main.write_row(1, 0, [
            operation['operation_id'],
            operation['name'],
            operation['status'],
            operation['start_date'],
            operation['end_date']
        ])

        # Лист с группами
        ws_groups = workbook.add_worksheet('Группы')
        group_headers = ['ID группы', 'Название', 'Участников', 'Статус']
        for col, header in enumerate(group_headers):
            ws_groups.write(0, col, header, header_format)

        for row, group in enumerate(report_data['groups'], 1):
            ws_groups.write_row(row, 0, [
                group['group_id'],
                group['name'],
                group['participants_count'],
                group['status']
            ])

        workbook.close()
        return output.getvalue()

    async def _export_to_csv(self, report_data: Dict) -> bytes:
        """Экспорт отчета в CSV формат"""
        output = BytesIO()
        writer = csv.writer(output)

        # Записываем основную информацию
        writer.writerow(['Operation Information'])
        writer.writerow(['ID', 'Name', 'Status', 'Start Date', 'End Date'])
        operation = report_data['operation']
        writer.writerow([
            operation['operation_id'],
            operation['name'],
            operation['status'],
            operation['start_date'],
            operation['end_date']
        ])

        # Записываем информацию о группах
        writer.writerow([])
        writer.writerow(['Groups Information'])
        writer.writerow(['Group ID', 'Name', 'Participants Count', 'Status'])
        for group in report_data['groups']:
            writer.writerow([
                group['group_id'],
                group['name'],
                group['participants_count'],
                group['status']
            ])

        return output.getvalue()

    async def archive_operation(self, operation_id: int) -> bool:
        """Архивирование информации об операции"""
        try:
            # Генерируем отчет
            report_data = await self.generate_operation_report(operation_id)
            if not report_data:
                return False

            # Создаем архивную директорию
            archive_dir = self.reports_dir / 'archives' / str(operation_id)
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Сохраняем отчет в JSON
            with open(archive_dir / 'report.json', 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            # Сохраняем отчет в Excel
            excel_data = await self._export_to_xlsx(report_data)
            with open(archive_dir / 'report.xlsx', 'wb') as f:
                f.write(excel_data)

            # Обновляем статус операции
            await self.db.execute("""
                UPDATE search_operations 
                SET status = 'archived', archived_at = ? 
                WHERE operation_id = ?
            """, (datetime.now().isoformat(), operation_id))

            return True
        except Exception as e:
            logger.error(f"Error archiving operation: {e}")
            return False
