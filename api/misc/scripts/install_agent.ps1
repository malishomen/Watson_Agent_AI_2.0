# === AI-Agent Installer Baton ===
# Полная установка и запуск AI-Agent в один клик
param(
    [switch]$SkipBackup = $false,
    [switch]$SkipAutostart = $false
)

Write-Host "🚀 УСТАНОВКА И ЗАПУСК AI-AGENT" -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Gray

# 1. Чистка процессов
Write-Host "`n1️⃣ Очистка процессов..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep 2
Write-Host "✅ Процессы очищены" -ForegroundColor Green

# 2. Кодировка
Write-Host "`n2️⃣ Настройка UTF-8..." -ForegroundColor Yellow
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
Write-Host "✅ UTF-8 настроен" -ForegroundColor Green

# 3. Активация venv
Write-Host "`n3️⃣ Активация виртуального окружения..." -ForegroundColor Yellow
if (Test-Path "D:\AI-Agent\venv\Scripts\Activate.ps1") {
    & "D:\AI-Agent\venv\Scripts\Activate.ps1"
    Write-Host "✅ Виртуальное окружение активировано" -ForegroundColor Green
} else {
    Write-Host "❌ Виртуальное окружение не найдено!" -ForegroundColor Red
    Write-Host "Создайте venv: python -m venv D:\AI-Agent\venv" -ForegroundColor Yellow
    exit 1
}

# 4. Проверка пакетов
Write-Host "`n4️⃣ Проверка пакетов..." -ForegroundColor Yellow
try {
    pip install --upgrade fastapi uvicorn "pydantic<3" requests sqlite3
    Write-Host "✅ Пакеты обновлены" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Ошибка обновления пакетов: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 5. Секрет
Write-Host "`n5️⃣ Генерация секрета..." -ForegroundColor Yellow
$env:AGENT_HTTP_SHARED_SECRET = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
Write-Host "🔑 Секрет установлен ($($env:AGENT_HTTP_SHARED_SECRET.Length) символов)" -ForegroundColor Green

# 6. Бэкап (если не пропущен)
if (-not $SkipBackup) {
    Write-Host "`n6️⃣ Создание бэкапа..." -ForegroundColor Yellow
    try {
        & "D:\AI-Agent\scripts\backup_min.ps1" -CleanOld
        Write-Host "✅ Бэкап создан" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Ошибка бэкапа: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 7. Запуск API
Write-Host "`n7️⃣ Запуск API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd D:\AI-Agent; D:\AI-Agent\venv\Scripts\Activate.ps1; `$env:AGENT_HTTP_SHARED_SECRET='$env:AGENT_HTTP_SHARED_SECRET'; uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"
)

Start-Sleep 5

# 8. Проверка запуска
Write-Host "`n8️⃣ Проверка запуска..." -ForegroundColor Yellow
try {
    $res = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 10
    Write-Host "✅ Агент запущен: $($res.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка запуска: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Проверьте логи в окне uvicorn" -ForegroundColor Yellow
}

# 9. Настройка автозапуска (если не пропущен)
if (-not $SkipAutostart) {
    Write-Host "`n9️⃣ Настройка автозапуска..." -ForegroundColor Yellow
    try {
        & "D:\AI-Agent\scripts\setup_autostart.ps1"
        Write-Host "✅ Автозапуск настроен" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Ошибка настройки автозапуска: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 10. Запуск watchdog
Write-Host "`n🔟 Запуск watchdog..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-WindowStyle Hidden", "-Command",
    "cd D:\AI-Agent; .\scripts\watchdog.ps1"
)
Write-Host "✅ Watchdog запущен" -ForegroundColor Green

# 11. Финальная проверка
Write-Host "`n1️⃣1️⃣ Финальная проверка..." -ForegroundColor Yellow
try {
    $h = @{ "x-agent-secret" = $env:AGENT_HTTP_SHARED_SECRET }
    $body = @{ text = "где я"; session = "install-test" } | ConvertTo-Json -Compress
    $result = Invoke-RestMethod -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8' -TimeoutSec 10
    
    if ($result.ok) {
        Write-Host "✅ Команда выполнена: $($result.normalized)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Команда не выполнена: $($result.result)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Ошибка тестовой команды: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "🎯 AI-AGENT УСТАНОВЛЕН И ГОТОВ К БОЕВОМУ ИСПОЛЬЗОВАНИЮ!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n📋 СЛЕДУЮЩИЕ ШАГИ:" -ForegroundColor Cyan
Write-Host "• API: http://127.0.0.1:8088/health" -ForegroundColor Gray
Write-Host "• Команды: http://127.0.0.1:8088/command" -ForegroundColor Gray
Write-Host "• Approvals: http://127.0.0.1:8088/approvals/pending" -ForegroundColor Gray
Write-Host "• Секрет: $($env:AGENT_HTTP_SHARED_SECRET.Substring(0,8))..." -ForegroundColor Gray

Write-Host "`n🔧 УПРАВЛЕНИЕ:" -ForegroundColor Cyan
Write-Host "• Проверка: .\scripts\daily_health_check.ps1 -Verbose" -ForegroundColor Gray
Write-Host "• Диагностика: .\scripts\incident_playbook.ps1 -Action diagnose" -ForegroundColor Gray
Write-Host "• Перезапуск: .\scripts\incident_playbook.ps1 -Action restart" -ForegroundColor Gray
Write-Host "• Бэкап: .\scripts\backup_min.ps1 -CleanOld" -ForegroundColor Gray

Write-Host "`n🚀 СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!" -ForegroundColor Green
