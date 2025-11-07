# setup_autostart.ps1 - Настройка автозапуска AI-Agent через Планировщик задач
param(
    [switch]$Remove = $false
)

# Настройка UTF-8
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

if ($Remove) {
    Write-Host "Удаление задачи автозапуска..." -ForegroundColor Yellow
    try {
        Unregister-ScheduledTask -TaskName "AI-Agent-API" -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host "✅ Задача удалена" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Задача не найдена или уже удалена" -ForegroundColor Yellow
    }
    exit 0
}

# Проверка секрета
if (-not $env:AGENT_HTTP_SHARED_SECRET) {
    Write-Host "❌ Ошибка: AGENT_HTTP_SHARED_SECRET не установлен" -ForegroundColor Red
    Write-Host "Установите переменную: `$env:AGENT_HTTP_SHARED_SECRET = 'ваш-секрет'" -ForegroundColor Cyan
    exit 1
}

Write-Host "Настройка автозапуска AI-Agent..." -ForegroundColor Cyan

# Создание действия
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument @(
    "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
    "cd D:\AI-Agent; D:\AI-Agent\venv\Scripts\Activate.ps1; `$env:AGENT_HTTP_SHARED_SECRET='$env:AGENT_HTTP_SHARED_SECRET'; uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"
)

# Создание триггера (при запуске системы)
$trigger = New-ScheduledTaskTrigger -AtStartup

# Настройки задачи (перезапуск при сбоях)
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Регистрация задачи
try {
    Register-ScheduledTask -TaskName "AI-Agent-API" -Action $action -Trigger $trigger -Settings $settings -Description "Local AI Agent API - Auto-start service" -Force
    Write-Host "✅ Задача зарегистрирована" -ForegroundColor Green
    
    # Запуск задачи
    Start-ScheduledTask -TaskName "AI-Agent-API"
    Write-Host "✅ Задача запущена" -ForegroundColor Green
    
    # Проверка статуса
    Start-Sleep 3
    $task = Get-ScheduledTask -TaskName "AI-Agent-API"
    Write-Host "Статус задачи: $($task.State)" -ForegroundColor Cyan
    
    # Проверка API
    Start-Sleep 5
    try {
        $response = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 5
        if ($response.status -eq "ok") {
            Write-Host "✅ API доступен: http://127.0.0.1:8088" -ForegroundColor Green
        } else {
            Write-Host "⚠️ API запущен, но статус неожиданный" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ API пока недоступен (возможно, еще запускается)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Ошибка при создании задачи: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎯 Готово! AI-Agent будет автоматически запускаться при старте системы." -ForegroundColor Green
Write-Host "Для удаления: .\scripts\setup_autostart.ps1 -Remove" -ForegroundColor Cyan
