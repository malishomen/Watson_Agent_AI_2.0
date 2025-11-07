# Боевой тест AI-Agent
Write-Host "🚀 Запуск боевого теста AI-Agent" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Cyan

# Установка переменных
$env:AI_AGENT_HTTP_SECRET = "test123"
$env:AGENT_API_BASE = "http://127.0.0.1:8088"

Write-Host "`n📋 Результаты тестов:" -ForegroundColor Yellow

# Тест 1: Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Cyan
try {
    $headers = @{"x-agent-secret" = "test123"}
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
    Write-Host "✅ Health: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 2: Команда "где я"
Write-Host "`n2. Команда 'где я'..." -ForegroundColor Cyan
try {
    $headers = @{
        "x-agent-secret" = "test123"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        text = "где я"
        session = "TG"
    } | ConvertTo-Json -Compress
    
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/command" -Method POST -Headers $headers -Body $body -TimeoutSec 10
    Write-Host "✅ Команда: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "❌ Команда: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 3: LLM роутер
Write-Host "`n3. LLM роутер 'pong'..." -ForegroundColor Cyan
try {
    $headers = @{
        "x-agent-secret" = "test123"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        text = "ответь одним словом: pong"
        session = "TG"
    } | ConvertTo-Json -Compress
    
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/command" -Method POST -Headers $headers -Body $body -TimeoutSec 15
    Write-Host "✅ LLM: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "❌ LLM: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 4: Approvals
Write-Host "`n4. Approvals Pending..." -ForegroundColor Cyan
try {
    $headers = @{"x-agent-secret" = "test123"}
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/approvals/pending" -Headers $headers -TimeoutSec 5
    Write-Host "✅ Approvals: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "❌ Approvals: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 5: Project Validate
Write-Host "`n5. Project Validate..." -ForegroundColor Cyan
try {
    $headers = @{
        "x-agent-secret" = "test123"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        spec_path = "D:/AI-Agent/Projects/demo/ProjectSpec.yml"
    } | ConvertTo-Json -Compress
    
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/project/validate" -Method POST -Headers $headers -Body $body -TimeoutSec 10
    Write-Host "✅ Project Validate: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "❌ Project Validate: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Боевой тест завершен!" -ForegroundColor Green
Write-Host "Проверьте результаты выше и отправьте отчёт ✅/❌" -ForegroundColor Cyan

