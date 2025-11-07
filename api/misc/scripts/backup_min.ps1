# backup_min.ps1 - Бэкап "несгораемого минимума" AI-Agent
param(
    [string]$BackupDir = "D:\AI-Agent\Backups",
    [switch]$CleanOld = $false
)

# Настройка UTF-8
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$dst = "$BackupDir\agent-$timestamp.zip"

Write-Host "💾 Создание бэкапа AI-Agent..." -ForegroundColor Cyan
Write-Host "Время: $timestamp" -ForegroundColor Gray

# Создаем папку для бэкапов если не существует
if (-not (Test-Path $BackupDir)) {
    New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null
    Write-Host "✅ Создана папка для бэкапов: $BackupDir" -ForegroundColor Green
}

# Список критически важных файлов и папок
$paths = @(
    "D:\AI-Agent\api",
    "D:\AI-Agent\parsers", 
    "D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py",
    "D:\AI-Agent\Memory\agent_memory.sqlite",
    "D:\AI-Agent\scripts",
    "D:\AI-Agent\telegram_integration.py"
)

$existingPaths = @()
$missingPaths = @()

# Проверяем существование файлов
foreach ($path in $paths) {
    if (Test-Path $path) {
        $existingPaths += $path
        Write-Host "✅ Найден: $path" -ForegroundColor Green
    } else {
        $missingPaths += $path
        Write-Host "⚠️ Не найден: $path" -ForegroundColor Yellow
    }
}

if ($existingPaths.Count -eq 0) {
    Write-Host "❌ Не найдено ни одного файла для бэкапа!" -ForegroundColor Red
    exit 1
}

# Создаем бэкап
try {
    Write-Host "`n📦 Создание архива..." -ForegroundColor Cyan
    $existingPaths | Compress-Archive -DestinationPath $dst -Force
    
    $size = (Get-Item $dst).Length
    $sizeMB = [math]::Round($size / 1MB, 2)
    
    Write-Host "✅ Бэкап создан: $dst" -ForegroundColor Green
    Write-Host "📊 Размер: $sizeMB MB" -ForegroundColor Gray
    
    if ($missingPaths.Count -gt 0) {
        Write-Host "`n⚠️ Пропущенные файлы:" -ForegroundColor Yellow
        $missingPaths | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }
    
} catch {
    Write-Host "❌ Ошибка создания бэкапа: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Очистка старых бэкапов (если запрошено)
if ($CleanOld) {
    Write-Host "`n🧹 Очистка старых бэкапов..." -ForegroundColor Cyan
    try {
        $oldBackups = Get-ChildItem $BackupDir -Filter "agent-*.zip" | 
                      Sort-Object CreationTime -Descending | 
                      Select-Object -Skip 7  # Оставляем последние 7 бэкапов
        
        if ($oldBackups) {
            $oldBackups | Remove-Item -Force
            Write-Host "✅ Удалено $($oldBackups.Count) старых бэкапов" -ForegroundColor Green
        } else {
            Write-Host "ℹ️ Старых бэкапов для удаления не найдено" -ForegroundColor Gray
        }
    } catch {
        Write-Host "⚠️ Ошибка очистки старых бэкапов: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Показываем список всех бэкапов
Write-Host "`n📋 Все бэкапы:" -ForegroundColor Cyan
Get-ChildItem $BackupDir -Filter "agent-*.zip" | 
    Sort-Object CreationTime -Descending | 
    ForEach-Object { 
        $size = [math]::Round($_.Length / 1MB, 2)
        Write-Host "  $($_.Name) - $size MB - $($_.CreationTime)" -ForegroundColor Gray 
    }

Write-Host "`n🎯 Бэкап завершен успешно!" -ForegroundColor Green
Write-Host "💡 Для автоматического бэкапа добавьте в Планировщик задач:" -ForegroundColor Cyan
Write-Host "   .\scripts\backup_min.ps1 -CleanOld" -ForegroundColor Gray
