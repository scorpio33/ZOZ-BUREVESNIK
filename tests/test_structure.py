from pathlib import Path

def test_project_structure():
    """Проверка структуры проекта"""
    root = Path(__file__).parent.parent
    src = root / 'src'
    
    # Проверяем наличие основных директорий
    assert src.exists(), "src directory not found"
    assert (src / 'core').exists(), "core directory not found"
    assert (src / 'handlers').exists(), "handlers directory not found"
    
    # Проверяем наличие основных файлов
    assert (src / 'core' / 'bot.py').exists(), "bot.py not found"
    assert (src / 'core' / 'states.py').exists(), "states.py not found"