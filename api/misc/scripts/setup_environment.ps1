# scripts/setup_environment.ps1
Write-Host "=== Setting up E2E Agent Pipeline Environment ===" -ForegroundColor Cyan

# 1) Генерация секрета для FastAPI
Write-Host "1. Generating FastAPI secret..." -ForegroundColor Yellow
$AG = [guid]::NewGuid().ToString('N')
setx AGENT_HTTP_SHARED_SECRET $AG
$env:AGENT_HTTP_SHARED_SECRET = $AG
Write-Host "    Secret generated: $($AG.Substring(0,8))..." -ForegroundColor Green

# 2) Настройка LM Studio
Write-Host "2. Configuring LM Studio API..." -ForegroundColor Yellow
setx OPENAI_API_BASE "http://127.0.0.1:1234/v1"
setx OPENAI_API_KEY  "lm-studio"
$env:OPENAI_API_BASE = "http://127.0.0.1:1234/v1"
$env:OPENAI_API_KEY  = "lm-studio"
Write-Host "    LM Studio API configured" -ForegroundColor Green

# 3) Проверка LM Studio
Write-Host "3. Checking LM Studio availability..." -ForegroundColor Yellow
try {
    $models = (Invoke-RestMethod http://127.0.0.1:1234/v1/models -ErrorAction Stop).data
    if ($models) {
        Write-Host "    LM Studio running with $($models.Count) model(s)" -ForegroundColor Green
        Write-Host "    Available models:" -ForegroundColor Cyan
        $models | ForEach-Object { Write-Host "      - $($_.id)" -ForegroundColor White }
    } else {
        Write-Host "    LM Studio running but no models loaded" -ForegroundColor Yellow
    }
} catch {
    Write-Host "    LM Studio not accessible on :1234" -ForegroundColor Red
    Write-Host "    Make sure LM Studio is running with server started" -ForegroundColor Yellow
}

# 4) Проверка FastAPI агента
Write-Host "4. Checking FastAPI agent..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod http://127.0.0.1:8088/health -ErrorAction Stop
    Write-Host "    FastAPI agent running" -ForegroundColor Green
} catch {
    Write-Host "    FastAPI agent not accessible on :8088" -ForegroundColor Red
    Write-Host "    Run: uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload" -ForegroundColor Yellow
}

# 5) Проверка файла README.md
Write-Host "5. Checking README.md..." -ForegroundColor Yellow
if (Test-Path "D:/AI-Agent/README.md") {
    Write-Host "    README.md exists" -ForegroundColor Green
} else {
    Write-Host "    README.md not found, creating..." -ForegroundColor Yellow
    New-Item -Path "D:/AI-Agent/README.md" -ItemType File -Force | Out-Null
    Add-Content -Path "D:/AI-Agent/README.md" -Value "# AI-Agent Project`n`nThis file will be updated by the E2E pipeline."
    Write-Host "    README.md created" -ForegroundColor Green
}

Write-Host "=== Environment setup completed! ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start LM Studio server (Menu  Server  Start)" -ForegroundColor White
Write-Host "2. Start FastAPI agent: uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload" -ForegroundColor White
Write-Host "3. Run pipeline: .\scripts\e2e_agent_pipeline.ps1" -ForegroundColor White
