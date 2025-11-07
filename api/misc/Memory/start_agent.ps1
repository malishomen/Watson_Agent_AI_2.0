# Start AI-Agent API
# Установка переменных окружения
$env:AGENT_HTTP_SHARED_SECRET = "test123"
$env:AGENT_API_BASE = "http://127.0.0.1:8088"

Write-Host "Starting AI-Agent API..." -ForegroundColor Green
Write-Host "Secret: $env:AGENT_HTTP_SHARED_SECRET" -ForegroundColor Yellow
Write-Host "API Base: $env:AGENT_API_BASE" -ForegroundColor Yellow

# Переход в директорию AI-Agent
cd D:\AI-Agent

# Запуск API в новом окне PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"

Write-Host "API Agent started in background window!" -ForegroundColor Green
Write-Host "Check health: http://127.0.0.1:8088/health" -ForegroundColor Cyan

