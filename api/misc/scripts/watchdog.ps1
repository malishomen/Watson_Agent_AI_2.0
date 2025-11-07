# watchdog.ps1 - Мониторинг и автоперезапуск AI-Agent API
param(
    [int]$CheckInterval = 10,
    [string]$LogFile = "D:\AI-Agent\Memory\watchdog.log"
)

# Настройка UTF-8
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

Write-Host "🐕 Watchdog запущен (интервал: ${CheckInterval}с)" -ForegroundColor Cyan
Write-Host "Лог: $LogFile" -ForegroundColor Gray

# Функция проверки API
function Test-API {
    try {
        $response = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 2
        return $response.status -eq "ok"
    } catch {
        return $false
    }
}

# Функция перезапуска API
function Restart-API {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] API недоступен -> перезапуск..." -ForegroundColor Yellow
    
    # Логирование
    "[$timestamp] API down -> restarting" | Add-Content $LogFile -Encoding UTF8
    
    # Остановка всех процессов Python/Uvicorn
    Get-Process | Where-Object {$_.ProcessName -match "python|uvicorn"} | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Небольшая пауза
    Start-Sleep 2
    
    # Запуск API в фоне
    Start-Process powershell -WindowStyle Hidden -ArgumentList @(
        "-NoProfile", "-Command",
        "cd D:\AI-Agent; D:\AI-Agent\venv\Scripts\Activate.ps1; `$env:AGENT_HTTP_SHARED_SECRET='$env:AGENT_HTTP_SHARED_SECRET'; uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"
    )
    
    Write-Host "[$timestamp] API перезапущен" -ForegroundColor Green
}

# Основной цикл мониторинга
$consecutive_failures = 0
$max_failures = 3

while ($true) {
    if (Test-API) {
        if ($consecutive_failures -gt 0) {
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            Write-Host "[$timestamp] ✅ API восстановлен" -ForegroundColor Green
            "[$timestamp] API recovered" | Add-Content $LogFile -Encoding UTF8
        }
        $consecutive_failures = 0
    } else {
        $consecutive_failures++
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] ❌ API недоступен (попытка $consecutive_failures/$max_failures)" -ForegroundColor Red
        
        if ($consecutive_failures -ge $max_failures) {
            Restart-API
            $consecutive_failures = 0
        }
    }
    
    Start-Sleep $CheckInterval
}
