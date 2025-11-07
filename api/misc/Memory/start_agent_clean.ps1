# Запуск AI-Agent API без проблем с кириллицей
Write-Host "🚀 Запуск AI-Agent API (чистая версия)" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Cyan

# Установка переменных окружения
$env:AGENT_HTTP_SHARED_SECRET = "test123"
$env:AGENT_API_BASE = "http://127.0.0.1:8088"

Write-Host "Переменные окружения установлены:" -ForegroundColor Yellow
Write-Host "AGENT_HTTP_SHARED_SECRET: $env:AGENT_HTTP_SHARED_SECRET" -ForegroundColor White
Write-Host "AGENT_API_BASE: $env:AGENT_API_BASE" -ForegroundColor White

# Проверка, не запущен ли уже API
Write-Host "`nПроверка существующих процессов..." -ForegroundColor Yellow
try {
    $existingProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*uvicorn*" -and $_.CommandLine -like "*8088*"
    }
    
    if ($existingProcess) {
        Write-Host "⚠️ API уже запущен (PID: $($existingProcess.Id))" -ForegroundColor Yellow
        Write-Host "Останавливаю существующий процесс..." -ForegroundColor Yellow
        Stop-Process -Id $existingProcess.Id -Force
        Start-Sleep -Seconds 2
    }
} catch {
    Write-Host "Процесс не найден, продолжаем запуск..." -ForegroundColor Cyan
}

# Переход в директорию AI-Agent
Write-Host "`nПереход в директорию AI-Agent..." -ForegroundColor Yellow
try {
    Set-Location "D:\AI-Agent"
    Write-Host "✅ Текущая директория: $(Get-Location)" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка перехода в директорию: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Запуск API через Start-Process (избегаем проблем с кириллицей)
Write-Host "`nЗапуск API агента..." -ForegroundColor Yellow
try {
    $processArgs = @(
        "-c",
        "uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"
    )
    
    $process = Start-Process -FilePath "python" -ArgumentList $processArgs -PassThru -NoNewWindow
    Write-Host "✅ API процесс запущен (PID: $($process.Id))" -ForegroundColor Green
    
    # Ждем запуска API
    Write-Host "`nОжидание запуска API (10 секунд)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Проверяем здоровье API
    Write-Host "`nПроверка здоровья API..." -ForegroundColor Yellow
    try {
        $headers = @{"x-agent-secret" = "test123"}
        $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
        Write-Host "✅ API Status: $($healthResponse.status)" -ForegroundColor Green
        Write-Host "🎉 API агент успешно запущен!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ API не отвечает, но процесс запущен" -ForegroundColor Yellow
        Write-Host "Попробуйте проверить позже: http://127.0.0.1:8088/health" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "❌ Ошибка запуска API: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n📋 Информация для использования:" -ForegroundColor Yellow
Write-Host "• API URL: http://127.0.0.1:8088" -ForegroundColor White
Write-Host "• Health Check: http://127.0.0.1:8088/health" -ForegroundColor White
Write-Host "• Secret Key: test123" -ForegroundColor White
Write-Host "• PID процесса: $($process.Id)" -ForegroundColor White

Write-Host "`n🎯 Для остановки API:" -ForegroundColor Yellow
Write-Host "Stop-Process -Id $($process.Id) -Force" -ForegroundColor Cyan

Write-Host "`n✅ Готово! API агент запущен без проблем с кириллицей!" -ForegroundColor Green

