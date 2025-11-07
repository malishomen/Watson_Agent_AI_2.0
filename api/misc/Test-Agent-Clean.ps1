[Console]::OutputEncoding = [Text.Encoding]::UTF8
$uri = "http://127.0.0.1:8088"
$secret = $env:AGENT_HTTP_SHARED_SECRET
if (-not $secret) { $secret = "test123" }

Write-Host "Checking API health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod "$uri/health" -Headers @{"x-agent-secret"=$secret}
    Write-Host "Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "API unavailable: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Testing agent with Cyrillic..." -ForegroundColor Yellow
$body = @{ text="Test: Cyrillic OK?"; session="Smoke" } | ConvertTo-Json -Depth 5
try {
    $resp = Invoke-RestMethod -Uri "$uri/command" -Method Post `
      -Headers @{ "x-agent-secret"=$secret; "Content-Type"="application/json; charset=utf-8" } `
      -Body ([Text.Encoding]::UTF8.GetBytes($body))
    Write-Host "Agent response: $($resp.result)" -ForegroundColor Green
} catch {
    Write-Host "Agent error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "All tests passed successfully!" -ForegroundColor Cyan
