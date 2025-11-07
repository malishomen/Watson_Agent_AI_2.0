# scripts/start_fastapi.ps1
# Запуск FastAPI агента с правильными переменными окружения

Write-Host "=== Starting FastAPI Agent ===" -ForegroundColor Cyan

# Остановка существующих процессов
Write-Host "1. Stopping existing processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -match "python|uvicorn"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Переход в директорию проекта
Write-Host "2. Changing to project directory..." -ForegroundColor Yellow
Set-Location "D:\AI-Agent"
Write-Host "   ✅ Current directory: $(Get-Location)" -ForegroundColor Green

# Активация виртуального окружения
Write-Host "3. Activating virtual environment..." -ForegroundColor Yellow
try {
    & "D:\AI-Agent\venv\Scripts\Activate.ps1"
    Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to activate virtual environment" -ForegroundColor Red
    throw "Virtual environment activation failed"
}

# Проверка переменной окружения
Write-Host "4. Checking environment variables..." -ForegroundColor Yellow
$secret = $env:AGENT_HTTP_SHARED_SECRET
if ($secret) {
    Write-Host "   ✅ AGENT_HTTP_SHARED_SECRET: $($secret.Substring(0,8))..." -ForegroundColor Green
} else {
    Write-Host "   ❌ AGENT_HTTP_SHARED_SECRET not set" -ForegroundColor Red
    Write-Host "   💡 Run: .\scripts\setup_environment.ps1 first" -ForegroundColor Yellow
    throw "Environment variable not set"
}

# Запуск FastAPI сервера
Write-Host "5. Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "   🚀 Starting uvicorn..." -ForegroundColor Cyan
Write-Host "   📡 Server will be available at: http://127.0.0.1:8088" -ForegroundColor Cyan
Write-Host "   🛑 Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White

try {
    uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload
} catch {
    Write-Host "   ❌ Failed to start FastAPI server" -ForegroundColor Red
    throw "FastAPI server startup failed"
}
