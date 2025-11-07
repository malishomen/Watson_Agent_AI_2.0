[Console]::OutputEncoding = [Text.Encoding]::UTF8
$uri = "http://127.0.0.1:8088"
$secret = $env:AGENT_HTTP_SHARED_SECRET
if (-not $secret) { $secret = "test123" }

Write-Host "Проверка здоровья API..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod "$uri/health" -Headers @{"x-agent-secret"=$secret}
    Write-Host "✓ Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ API недоступен: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Тестирование агента с кириллицей..." -ForegroundColor Yellow
$body = @{ text="Проверка связи: кириллица ок?"; session="Smoke" } | ConvertTo-Json -Depth 5
try {
    $resp = Invoke-RestMethod -Uri "$uri/command" -Method Post `
      -Headers @{ "x-agent-secret"=$secret; "Content-Type"="application/json; charset=utf-8" } `
      -Body ([Text.Encoding]::UTF8.GetBytes($body))
    Write-Host "✓ Ответ агента: $($resp.result)" -ForegroundColor Green
} catch {
    Write-Host "✗ Ошибка агента: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "All tests passed successfully!" -ForegroundColor Cyan
