# Скрипты автоматизации обновления репозитория

## Использование в Windows (PowerShell)

1. Запустите PowerShell от имени администратора
2. Перейдите в директорию проекта
3. Выполните скрипт:
```powershell
.\scripts\update_repo.ps1
```

С пользовательским сообщением коммита:
```powershell
.\scripts\update_repo.ps1 -commitMessage "feat: Add new features"
```

## Использование в Linux/Mac (Bash)

1. Сделайте скрипт исполняемым:
```bash
chmod +x scripts/update_repo.sh
```

2. Запустите скрипт:
```bash
./scripts/update_repo.sh
```

С пользовательским сообщением коммита:
```bash
./scripts/update_repo.sh "feat: Add new features"
```

## Возможные сообщения коммитов

- `feat: ` - новый функционал
- `fix: ` - исправление ошибок
- `docs: ` - обновление документации
- `style: ` - форматирование кода
- `refactor: ` - рефакторинг кода
- `test: ` - добавление тестов
- `chore: ` - обновление зависимостей