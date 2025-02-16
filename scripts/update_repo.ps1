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

# Настройка Git для работы с окончаниями строк
Write-ColorOutput Green "🔧 Configuring Git..."
git config --global core.autocrlf false
git config --global core.eol lf

try {
    # Получение текущей ветки
    $currentBranch = git rev-parse --abbrev-ref HEAD
    Write-ColorOutput Green "🌿 Current branch: $currentBranch"

    # Добавление всех изменений
    Write-ColorOutput Green "📦 Adding changes..."
    git add .

    # Создание коммита
    Write-ColorOutput Green "💾 Creating commit..."
    git commit -m $commitMessage

    # Проверка существования удаленной ветки
    $remoteBranch = git ls-remote --heads origin $currentBranch
    if ($remoteBranch) {
        # Если ветка существует, делаем pull
        Write-ColorOutput Green "⬇️ Pulling latest changes..."
        git pull origin $currentBranch
    } else {
        Write-ColorOutput Yellow "📝 Remote branch doesn't exist. Skipping pull..."
    }

    # Отправка изменений
    Write-ColorOutput Green "⬆️ Pushing changes..."
    git push origin $currentBranch

    Write-ColorOutput Green "✅ Repository successfully updated!"
} catch {
    Write-ColorOutput Red "❌ Error occurred during update process:"
    Write-ColorOutput Red $_.Exception.Message
    exit 1
}
