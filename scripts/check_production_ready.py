import sys
import psutil
import requests
from pathlib import Path

class ProductionReadinessChecker:
    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []

    def check_system_resources(self):
        """Проверка системных ресурсов"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if memory.available < 2 * 1024 * 1024 * 1024:  # 2GB
            self.warnings.append("Low memory available")
            
        if disk.free < 10 * 1024 * 1024 * 1024:  # 10GB
            self.warnings.append("Low disk space")

    def check_database_size(self):
        """Проверка размера базы данных"""
        db_path = Path("database/bot.db")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            self.checks.append(f"Database size: {size_mb:.2f}MB")
            
            if size_mb > 100:
                self.warnings.append("Large database size - consider optimization")

    def check_api_dependencies(self):
        """Проверка доступности внешних API"""
        apis = {
            "Telegram": "https://api.telegram.org",
            "Maps": "https://api.maps.yandex.ru"
        }
        
        for name, url in apis.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.checks.append(f"{name} API: Available")
                else:
                    self.warnings.append(f"{name} API: Status {response.status_code}")
            except Exception as e:
                self.errors.append(f"{name} API: Connection error - {str(e)}")

    def run_checks(self):
        """Запуск всех проверок"""
        self.check_system_resources()
        self.check_database_size()
        self.check_api_dependencies()
        
        return {
            "checks": self.checks,
            "warnings": self.warnings,
            "errors": self.errors,
            "is_ready": len(self.errors) == 0
        }

def main():
    checker = ProductionReadinessChecker()
    results = checker.run_checks()
    
    print("\n=== Production Readiness Check ===\n")
    
    print("Checks:")
    for check in results["checks"]:
        print(f"✓ {check}")
        
    if results["warnings"]:
        print("\nWarnings:")
        for warning in results["warnings"]:
            print(f"⚠️ {warning}")
            
    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"❌ {error}")
            
    print(f"\nStatus: {'Ready' if results['is_ready'] else 'Not Ready'} for production")
    
    return 0 if results['is_ready'] else 1

if __name__ == "__main__":
    sys.exit(main())