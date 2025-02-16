import os
from pathlib import Path

def create_project_structure():
    """Создание структуры проекта"""
    directories = [
        'core',
        'handlers',
        'utils',
        'services',
        'database',
        'config',
        'storage/maps',
        'storage/cache',
        'storage/logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        init_file = Path(directory) / '__init__.py'
        if not init_file.exists():
            init_file.touch()
        print(f"✓ Created directory and initialized: {directory}")

if __name__ == "__main__":
    create_project_structure()
