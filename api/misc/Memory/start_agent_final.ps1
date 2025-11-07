# Запуск AI-Agent API (финальная версия без кириллицы)
Write-Host "Запуск AI-Agent API..." -ForegroundColor Green

# Установка переменных окружения
$env:AGENT_HTTP_SHARED_SECRET = "test123"
$env:AGENT_API_BASE = "http://127.0.0.1:8088"

# Переход в директорию
Set-Location "D:\AI-Agent"

# Запуск через Start-Process (избегаем кириллицу)
$processArgs = @(
    "-c",
    "uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"
)

$process = Start-Process -FilePath "python" -ArgumentList $processArgs -PassThru -NoNewWindow
Write-Host "API запущен (PID: $($process.Id))" -ForegroundColor Green

# Проверка здоровья
Start-Sleep -Seconds 5
try {
    $headers = @{"x-agent-secret" = "test123"}
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
    Write-Host "API Status: $($healthResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "API не отвечает, но процесс запущен" -ForegroundColor Yellow
}

Write-Host "Готово! Используйте Ctrl+Shift+P в Cursor для доступа к задачам" -ForegroundColor Cyan

