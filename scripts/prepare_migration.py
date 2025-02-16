import os
import shutil
from pathlib import Path
import json
from datetime import datetime

class MigrationPreparation:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_backup(self):
        """Создание резервной копии данных"""
        backup_dir = self.base_path / "backups" / self.timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Копирование базы данных
        db_path = self.base_path / "database" / "bot.db"
        if db_path.exists():
            shutil.copy2(db_path, backup_dir / "bot.db")

        # Копирование файлов карт и кэша
        for directory in ["maps", "cache"]:
            src_dir = self.base_path / "storage" / directory
            if src_dir.exists():
                shutil.copytree(src_dir, backup_dir / directory)

        return str(backup_dir)

    def generate_migration_plan(self):
        """Создание плана миграции"""
        return {
            "steps": [
                {
                    "order": 1,
                    "action": "backup",
                    "description": "Create backup of all data"
                },
                {
                    "order": 2,
                    "action": "database",
                    "description": "Migrate SQLite to PostgreSQL"
                },
                {
                    "order": 3,
                    "action": "storage",
                    "description": "Move files to production storage"
                },
                {
                    "order": 4,
                    "action": "verify",
                    "description": "Verify data integrity"
                }
            ],
            "requirements": {
                "postgresql": ">=12.0",
                "storage_space": "Minimum 10GB",
                "memory": "Minimum 2GB RAM"
            }
        }

    def prepare(self):
        """Подготовка к миграции"""
        # Создаём бэкап
        backup_path = self.create_backup()
        
        # Генерируем план миграции
        migration_plan = self.generate_migration_plan()
        
        # Сохраняем информацию о подготовке
        info = {
            "timestamp": self.timestamp,
            "backup_path": str(backup_path),
            "migration_plan": migration_plan
        }
        
        with open(backup_path / "migration_info.json", "w") as f:
            json.dump(info, f, indent=4)
        
        return info