# Update Repository Script for PowerShell
param (
    [string]$commitMessage = "update: Automatic repository update"
)

# Функция для вывода сообщений с цветом
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Проверка наличия изменений
Write-ColorOutput Green "📂 Checking repository status..."
$status = git status --porcelain
if ($status) {
    Write-ColorOutput Yellow "🔄 Changes detected. Starting update process..."
} else {
    Write-ColorOutput Green "✅ Repository is up to date. No changes detected."
    exit 0
}

# Проверка и создание .gitignore если его нет
if (-not (Test-Path .gitignore)) {
    Write-ColorOutput Yellow "Creating .gitignore file..."
    @"
# Virtual Environment
venv/
env/

# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite3

# Logs
*.log
.cache
.pytest_cache/
storage/logs/*
storage/cache/*
storage/maps/*
!storage/logs/.gitkeep
!storage/cache/.gitkeep
!storage/maps/.gitkeep

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"@ | Out-File -FilePath .gitignore -Encoding UTF8
}

# Настройка Git для работы с окончаниями строк
Write-ColorOutput Green "🔧 Configuring Git..."
git config --global core.autocrlf true

try {
    # Добавление всех изменений
    Write-ColorOutput Green "📦 Adding changes..."
    git add .

    # Создание коммита
    Write-ColorOutput Green "💾 Creating commit..."
    git commit -m $commitMessage

    # Получение текущей ветки
    $currentBranch = git rev-parse --abbrev-ref HEAD
    Write-ColorOutput Green "🌿 Current branch: $currentBranch"

    # Получение последних изменений с удаленного репозитория
    Write-ColorOutput Green "⬇️ Pulling latest changes..."
    git pull origin $currentBranch

    # Отправка изменений
    Write-ColorOutput Green "⬆️ Pushing changes..."
    git push origin $currentBranch

    Write-ColorOutput Green "✅ Repository successfully updated!"
} catch {
    Write-ColorOutput Red "❌ Error occurred during update process:"
    Write-ColorOutput Red $_.Exception.Message
    exit 1
}