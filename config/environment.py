import os
from enum import Enum
from typing import Dict, Any
from pathlib import Path

class Environment(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

class EnvironmentConfig:
    def __init__(self):
        self.current_env = os.getenv("BOT_ENV", "local")
        self.base_path = Path(__file__).parent.parent

        self.configs = {
            "local": {
                "database": {
                    "type": "sqlite",
                    "path": str(self.base_path / "database" / "bot.db"),
                    "backup_path": str(self.base_path / "backups"),
                },
                "storage": {
                    "maps": str(self.base_path / "storage" / "maps"),
                    "cache": str(self.base_path / "storage" / "cache"),
                    "logs": str(self.base_path / "storage" / "logs"),
                },
                "logging": {
                    "level": "DEBUG",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "production": {
                "database": {
                    "type": "postgresql",
                    "host": os.getenv("DB_HOST", "localhost"),
                    "port": int(os.getenv("DB_PORT", 5432)),
                    "name": os.getenv("DB_NAME", "bot_db"),
                    "user": os.getenv("DB_USER", "bot_user"),
                    "password": os.getenv("DB_PASSWORD", ""),
                },
                "storage": {
                    "maps": "/var/www/bot/maps",
                    "cache": "/var/www/bot/cache",
                    "logs": "/var/www/bot/logs",
                },
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            }
        }

    def get_config(self) -> Dict[str, Any]:
        return self.configs.get(self.current_env, self.configs["local"])