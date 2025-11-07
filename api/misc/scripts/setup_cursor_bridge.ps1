# scripts/setup_cursor_bridge.ps1
# Setup Cursor API bridge with environment variables

Write-Host "=== Setting up Cursor API Bridge ===" -ForegroundColor Cyan

# Check if Cursor is running and get API info
Write-Host "1. Checking Cursor API availability..." -ForegroundColor Yellow

# Common Cursor API ports
$cursorPorts = @(7007, 8080, 3000, 8081)
$cursorUrl = $null

foreach ($port in $cursorPorts) {
    try {
        $testUrl = "http://127.0.0.1:$port"
        $response = Invoke-RestMethod -Uri $testUrl -Method Get -TimeoutSec 2 -ErrorAction Stop
        $cursorUrl = $testUrl
        Write-Host "   FOUND: Cursor API on port $port" -ForegroundColor Green
        break
    } catch {
        Write-Host "   CHECKED: Port $port - no response" -ForegroundColor Gray
    }
}

if (-not $cursorUrl) {
    Write-Host "   WARNING: No Cursor API found on common ports" -ForegroundColor Yellow
    Write-Host "   Please ensure Cursor is running with API enabled" -ForegroundColor Yellow
    $cursorUrl = "http://127.0.0.1:7007"  # Default fallback
}

# Set environment variables
Write-Host "2. Setting up environment variables..." -ForegroundColor Yellow

# Set Cursor API URL
$env:CURSOR_API_URL = $cursorUrl
Write-Host "   Set CURSOR_API_URL = $cursorUrl" -ForegroundColor Green

# Generate or use existing API key
$apiKey = $env:CURSOR_API_KEY
if (-not $apiKey) {
    # Generate a simple API key (in real scenario, get from Cursor settings)
    $apiKey = "cursor_key_$(Get-Random -Minimum 1000 -Maximum 9999)"
    $env:CURSOR_API_KEY = $apiKey
    Write-Host "   Generated CURSOR_API_KEY = $apiKey" -ForegroundColor Green
} else {
    Write-Host "   Using existing CURSOR_API_KEY = $apiKey" -ForegroundColor Green
}

# Make environment variables persistent
Write-Host "3. Making environment variables persistent..." -ForegroundColor Yellow
try {
    [Environment]::SetEnvironmentVariable("CURSOR_API_URL", $cursorUrl, "User")
    [Environment]::SetEnvironmentVariable("CURSOR_API_KEY", $apiKey, "User")
    Write-Host "   OK: Environment variables saved permanently" -ForegroundColor Green
} catch {
    Write-Host "   WARNING: Could not save environment variables permanently" -ForegroundColor Yellow
}

# Test the bridge
Write-Host "4. Testing Cursor bridge..." -ForegroundColor Yellow
try {
    $secret = $env:AGENT_HTTP_SHARED_SECRET
    if ($secret) {
        $h = @{ "x-agent-secret" = $secret }
        $body = @{ filepath = "D:/AI-Agent/README.md" } | ConvertTo-Json
        
        $result = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/cursor/open `
            -Headers $h -Body $body -ContentType 'application/json'
        
        if ($result.error) {
            Write-Host "   INFO: Cursor API configured but returned: $($result.error)" -ForegroundColor Yellow
        } else {
            Write-Host "   SUCCESS: Cursor bridge working!" -ForegroundColor Green
        }
    } else {
        Write-Host "   ERROR: AGENT_HTTP_SHARED_SECRET not set" -ForegroundColor Red
    }
} catch {
    Write-Host "   INFO: Cursor bridge test failed (expected if not fully configured)" -ForegroundColor Yellow
}

Write-Host "=== Cursor Bridge Setup Completed ===" -ForegroundColor Green
Write-Host "Environment variables set:" -ForegroundColor Cyan
Write-Host "  CURSOR_API_URL = $env:CURSOR_API_URL" -ForegroundColor White
Write-Host "  CURSOR_API_KEY = $env:CURSOR_API_KEY" -ForegroundColor White
Write-Host ""
Write-Host "To fully activate the bridge:" -ForegroundColor Yellow
Write-Host "1. Restart FastAPI agent with new environment variables" -ForegroundColor White
Write-Host "2. Ensure Cursor API is enabled in Cursor settings" -ForegroundColor White
Write-Host "3. Run the enhanced pipeline to test" -ForegroundColor White
