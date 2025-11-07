<#
.SYNOPSIS
    Запускает полную систему Watson Agent (API + Telegram Bridge + Task Watcher)
    
.DESCRIPTION
    Автоматически запускает все компоненты системы:
    1. Watson API (port 8090)
    2. Telegram Bridge (long-polling)
    3. Task Watcher (inbox monitoring)
    
.EXAMPLE
    .\START_FULL_SYSTEM.ps1
#>

$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   🚀 WATSON AGENT - FULL SYSTEM START   " -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $PSCommandPath

# Функция для проверки процесса
function Test-ProcessRunning {
    param([string]$Pattern)
    $procs = Get-Process python -ErrorAction SilentlyContinue
    foreach ($p in $procs) {
        try {
            $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $($p.Id)").CommandLine
            if ($cmd -like "*$Pattern*") {
                return $p
            }
        } catch {}
    }
    return $null
}

# 1️⃣ Останавливаем старые процессы
Write-Host "1️⃣ Останавливаем старые процессы..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "   ✅ Очищено" -ForegroundColor Green
Write-Host ""

# 2️⃣ Запускаем Watson API
Write-Host "2️⃣ Запускаем Watson API..." -ForegroundColor Yellow
Push-Location $rootDir
try {
    & pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-WatsonApi.ps1 -Port 8090
    Write-Host "   ✅ Watson API: http://127.0.0.1:8090" -ForegroundColor Green
} finally {
    Pop-Location
}
Write-Host ""

# 3️⃣ Запускаем Telegram Bridge
Write-Host "3️⃣ Запускаем Telegram Bridge..." -ForegroundColor Yellow
Push-Location $rootDir
try {
    $telegramJob = Start-Process -FilePath "py" -ArgumentList "-3.11","-X","utf8","scripts\telegram_bridge.py" -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 3
    
    $proc = Test-ProcessRunning "telegram_bridge"
    if ($proc) {
        Write-Host "   ✅ Telegram Bridge running (PID: $($proc.Id))" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Telegram Bridge не запустился" -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}
Write-Host ""

# 4️⃣ Запускаем Task Watcher
Write-Host "4️⃣ Запускаем Task Watcher..." -ForegroundColor Yellow
Push-Location $rootDir
try {
    $watcherJob = Start-Process -FilePath "py" -ArgumentList "-3.11","-X","utf8","scripts\task_watcher.py" -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 3
    
    $proc = Test-ProcessRunning "task_watcher"
    if ($proc) {
        Write-Host "   ✅ Task Watcher running (PID: $($proc.Id))" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Task Watcher не запустился" -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}
Write-Host ""

# 5️⃣ Проверка статуса
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   📊 СТАТУС СИСТЕМЫ" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Watson API
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8090/health" -TimeoutSec 3
    if ($health.ok) {
        Write-Host "   ✅ Watson API: Running" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Watson API: Not OK" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Watson API: Not responding" -ForegroundColor Red
}

# Telegram Bridge
$tgProc = Test-ProcessRunning "telegram_bridge"
if ($tgProc) {
    Write-Host "   ✅ Telegram Bridge: Running (PID: $($tgProc.Id))" -ForegroundColor Green
} else {
    Write-Host "   ❌ Telegram Bridge: Not running" -ForegroundColor Red
}

# Task Watcher
$twProc = Test-ProcessRunning "task_watcher"
if ($twProc) {
    Write-Host "   ✅ Task Watcher: Running (PID: $($twProc.Id))" -ForegroundColor Green
} else {
    Write-Host "   ❌ Task Watcher: Not running" -ForegroundColor Red
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Переменные окружения
$useDelegate = [Environment]::GetEnvironmentVariable('WATSON_USE_CURSOR_DELEGATION','User')
if ($useDelegate -eq 'true') {
    Write-Host "   ℹ️ Cursor Delegation: ENABLED" -ForegroundColor Cyan
} else {
    Write-Host "   ℹ️ Cursor Delegation: DISABLED" -ForegroundColor Gray
    Write-Host "      Включить:" -ForegroundColor Gray
    Write-Host "      `$env:WATSON_USE_CURSOR_DELEGATION='true'" -ForegroundColor DarkGray
    Write-Host "      [Environment]::SetEnvironmentVariable('WATSON_USE_CURSOR_DELEGATION','true','User')" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "🎯 Система готова к работе!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Тестовая задача:" -ForegroundColor Yellow
Write-Host "   .\scripts\make_task.ps1 -Text 'Add logging to function X'" -ForegroundColor White
Write-Host ""

