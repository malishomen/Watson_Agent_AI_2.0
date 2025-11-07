# Тестирование API (финальная версия без кириллицы)
Write-Host "Тестирование AI-Agent API..." -ForegroundColor Green

# Health check
Write-Host "1. Проверка здоровья API..." -ForegroundColor Yellow
try {
    $headers = @{"x-agent-secret" = "test123"}
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers
    Write-Host "Health check: $($healthResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Запустите API: .\start_agent_final.ps1" -ForegroundColor Yellow
    exit 1
}

# Command test
Write-Host "`n2. Тестирование команд..." -ForegroundColor Yellow
try {
    $headers = @{
        "x-agent-secret" = "test123"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        text = "где я"
        session = "Cursor"
    } | ConvertTo-Json -Compress
    
    $commandResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/command" -Method POST -Headers $headers -Body $body
    Write-Host "Command response:" -ForegroundColor Green
    Write-Host $($commandResponse | ConvertTo-Json -Depth 3) -ForegroundColor White
} catch {
    Write-Host "Command test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nТестирование завершено!" -ForegroundColor Green

