# scripts\cursor_proxy_tests.ps1
$api = "http://127.0.0.1:8088"
$sec = $env:AGENT_API_SECRET

Write-Host "=== Testing Agent -> Cursor API ===" -ForegroundColor Cyan

# Open file
Write-Host "1. Opening file..." -ForegroundColor Yellow
try {
    $result = Invoke-WebRequest -Uri "$api/cursor/open" -Headers @{ 'x-agent-secret'=$sec } -Method POST -ContentType 'application/json' -Body (@{ filepath="D:\\AI-Agent\\README.md" } | ConvertTo-Json) | Select -Expand Content
    Write-Host "Result: $result" -ForegroundColor Green
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Insert text
Write-Host "2. Inserting text..." -ForegroundColor Yellow
try {
    $result = Invoke-WebRequest -Uri "$api/cursor/insert" -Headers @{ 'x-agent-secret'=$sec } -Method POST -ContentType 'application/json' -Body (@{ filepath="D:\\AI-Agent\\README.md"; position="end"; text="`nHello from Agent -> Cursor!" } | ConvertTo-Json) | Select -Expand Content
    Write-Host "Result: $result" -ForegroundColor Green
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Terminal
Write-Host "3. Running terminal command..." -ForegroundColor Yellow
try {
    $result = Invoke-WebRequest -Uri "$api/cursor/terminal" -Headers @{ 'x-agent-secret'=$sec } -Method POST -ContentType 'application/json' -Body (@{ cwd="D:\\AI-Agent"; command="dir" } | ConvertTo-Json) | Select -Expand Content
    Write-Host "Result: $result" -ForegroundColor Green
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "=== Testing completed ===" -ForegroundColor Cyan
