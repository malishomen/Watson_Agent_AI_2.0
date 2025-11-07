# daily_health_check.ps1 - Ежедневные проверки здоровья AI-Agent
param(
    [switch]$Verbose = $false
)

# Настройка UTF-8
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "🔍 Ежедневная проверка AI-Agent - $timestamp" -ForegroundColor Cyan

$errors = @()
$warnings = @()

# 1) Проверка здоровья API
Write-Host "`n1️⃣ Проверка API..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 5
    if ($health.status -eq "ok") {
        Write-Host "✅ API доступен" -ForegroundColor Green
    } else {
        $errors += "API недоступен: неожиданный статус"
    }
} catch {
    $errors += "API недоступен: $($_.Exception.Message)"
}

# 2) Тест команды
Write-Host "`n2️⃣ Тест команды..." -ForegroundColor Yellow
try {
    $h = @{ "x-agent-secret" = $env:AGENT_HTTP_SHARED_SECRET }
    $body = @{ text = "где я"; session = "health-check" } | ConvertTo-Json -Compress
    $result = Invoke-RestMethod -Method Post http://127.0.0.1:8088/command -Headers $h -ContentType 'application/json; charset=utf-8' -Body $body -TimeoutSec 10
    
    if ($result.ok) {
        Write-Host "✅ Команда выполнена: $($result.normalized)" -ForegroundColor Green
    } else {
        $errors += "Команда не выполнена: $($result.result)"
    }
} catch {
    $errors += "Ошибка выполнения команды: $($_.Exception.Message)"
}

# 3) Проверка pending approvals
Write-Host "`n3️⃣ Проверка pending approvals..." -ForegroundColor Yellow
try {
    $h = @{ "x-agent-secret" = $env:AGENT_HTTP_SHARED_SECRET }
    $pending = Invoke-RestMethod -Method Get http://127.0.0.1:8088/approvals/pending -Headers $h -TimeoutSec 5
    
    if ($pending.Count -eq 0) {
        Write-Host "✅ Нет ожидающих подтверждения заявок" -ForegroundColor Green
    } else {
        $warnings += "Найдено $($pending.Count) ожидающих подтверждения заявок"
        Write-Host "⚠️ Найдено $($pending.Count) pending approvals" -ForegroundColor Yellow
        if ($Verbose) {
            $pending | ForEach-Object { Write-Host "  - $($_.id): $($_.action)" -ForegroundColor Gray }
        }
    }
} catch {
    $errors += "Ошибка получения pending approvals: $($_.Exception.Message)"
}

# 4) Проверка логов операций
Write-Host "`n4️⃣ Проверка логов..." -ForegroundColor Yellow
$logFile = "D:\AI-Agent\Memory\ops_log.csv"
if (Test-Path $logFile) {
    try {
        $lastOps = Get-Content $logFile | Select-Object -Last 5
        Write-Host "✅ Лог операций доступен (последние 5 записей):" -ForegroundColor Green
        if ($Verbose) {
            $lastOps | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        }
        
        # Проверка на ошибки в последних операциях
        $recentErrors = $lastOps | Where-Object { $_ -match "FAIL" }
        if ($recentErrors) {
            $warnings += "Найдены ошибки в последних операциях"
            Write-Host "⚠️ Найдены ошибки в логах" -ForegroundColor Yellow
        }
    } catch {
        $warnings += "Ошибка чтения лога операций"
    }
} else {
    $warnings += "Файл лога операций не найден"
}

# 5) Проверка процессов
Write-Host "`n5️⃣ Проверка процессов..." -ForegroundColor Yellow
$pythonProcesses = Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" }
if ($pythonProcesses) {
    Write-Host "✅ Найдено $($pythonProcesses.Count) Python/Uvicorn процессов" -ForegroundColor Green
    if ($Verbose) {
        $pythonProcesses | ForEach-Object { Write-Host "  - $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray }
    }
} else {
    $errors += "Не найдено процессов Python/Uvicorn"
}

# 6) Проверка порта
Write-Host "`n6️⃣ Проверка порта 8088..." -ForegroundColor Yellow
try {
    $portCheck = netstat -ano | findstr ":8088"
    if ($portCheck) {
        Write-Host "✅ Порт 8088 занят" -ForegroundColor Green
    } else {
        $errors += "Порт 8088 свободен"
    }
} catch {
    $warnings += "Ошибка проверки порта"
}

# Итоговый отчет
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "📊 ИТОГОВЫЙ ОТЧЕТ" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

if ($errors.Count -eq 0) {
    Write-Host "✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО" -ForegroundColor Green
} else {
    Write-Host "❌ НАЙДЕНЫ КРИТИЧЕСКИЕ ОШИБКИ:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}

if ($warnings.Count -gt 0) {
    Write-Host "`n⚠️ ПРЕДУПРЕЖДЕНИЯ:" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}

Write-Host "`n🕐 Проверка завершена: $timestamp" -ForegroundColor Gray

# Возвращаем код выхода
if ($errors.Count -gt 0) {
    exit 1
} else {
    exit 0
}
