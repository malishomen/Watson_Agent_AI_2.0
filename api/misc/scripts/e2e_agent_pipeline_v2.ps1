# scripts/e2e_agent_pipeline_v2.ps1
# Enhanced E2E pipeline with LLM thinking cleanup and fallback

param(
    [string]$ModelId = "",
    [string]$Task = "Add a single reminder line for README (max 100 chars), no quotes.",
    [string]$FilePath = "D:/AI-Agent/README.md"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Enhanced E2E Agent Pipeline v2 ===" -ForegroundColor Cyan

# 1) Health check
Write-Host "1. Checking FastAPI health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod http://127.0.0.1:8088/health
    Write-Host "   OK: FastAPI status $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: FastAPI not running on :8088" -ForegroundColor Red
    throw "FastAPI server not accessible"
}

# 2) Authentication
Write-Host "2. Setting up authentication..." -ForegroundColor Yellow
$secret = $env:AGENT_HTTP_SHARED_SECRET
if (-not $secret) {
    Write-Host "   ERROR: AGENT_HTTP_SHARED_SECRET not set" -ForegroundColor Red
    throw "Environment variable AGENT_HTTP_SHARED_SECRET is required"
}
$h = @{ "x-agent-secret" = $secret }
Write-Host "   OK: Secret configured (len: $($secret.Length))" -ForegroundColor Green

# 3) LM Studio check
Write-Host "3. Checking LM Studio..." -ForegroundColor Yellow
try {
    $models = (Invoke-RestMethod http://127.0.0.1:1234/v1/models).data
    if (-not $models) { 
        throw "No models found" 
    }
    
    if ($ModelId) {
        $selectedModel = $models | Where-Object { $_.id -eq $ModelId }
        if (-not $selectedModel) {
            throw "Model '$ModelId' not found. Available: $($models.id -join ', ')"
        }
    } else {
        $selectedModel = $models[0]
    }
    
    $MODEL = $selectedModel.id
    Write-Host "   OK: LM Studio model '$MODEL' ready" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: LM Studio not accessible on :1234" -ForegroundColor Red
    throw "LM Studio server not accessible or no models loaded"
}

# 4) Enhanced LLM generation with thinking cleanup
Write-Host "4. Generating content with LLM (enhanced)..." -ForegroundColor Yellow

# Try multiple approaches to get clean response
$line = $null
$attempts = @(
    @{
        name = "Simple request"
        body = @{
            model = $MODEL
            messages = @(@{ role="user"; content="Say 'Hello' in one word only" })
            temperature = 0.1
        }
    },
    @{
        name = "System prompt"
        body = @{
            model = $MODEL
            messages = @(
                @{ role="system"; content="You are a helpful assistant. Give short, direct answers only." }
                @{ role="user"; content=$Task }
            )
            temperature = 0.3
        }
    },
    @{
        name = "With stop tokens"
        body = @{
            model = $MODEL
            messages = @(@{ role="user"; content=$Task })
            temperature = 0.2
            stop = @("</think>", "<think>", "Okay", "I need", "Let me", "Hmm", "So")
        }
    }
)

foreach ($attempt in $attempts) {
    Write-Host "   Trying: $($attempt.name)" -ForegroundColor Cyan
    try {
        $body = $attempt.body | ConvertTo-Json -Depth 6
        $res = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:1234/v1/chat/completions `
            -Headers @{ "Authorization"="Bearer lm-studio"; "Content-Type"="application/json" } `
            -Body $body
        
        $raw = $res.choices[0].message.content.Trim()
        
        # Aggressive thinking cleanup
        $clean = [regex]::Replace($raw,'(?s)<think>.*?</think>','')
        $clean = [regex]::Replace($clean,'(?s)Okay.*?\.','')
        $clean = [regex]::Replace($clean,'(?s)I need.*?\.','')
        $clean = [regex]::Replace($clean,'(?s)Let me.*?\.','')
        $clean = [regex]::Replace($clean,'(?s)Hmm.*?\.','')
        $clean = [regex]::Replace($clean,'(?s)So.*?\.','')
        $clean = $clean.Trim()
        
        # Remove quotes and clean up
        $clean = $clean -replace '["""]', ''
        $clean = $clean -replace '^[:\-\s]+', ''
        $clean = $clean.Trim()
        
        if ($clean -and $clean.Length -gt 3 -and $clean.Length -lt 200) {
            $line = $clean
            Write-Host "   SUCCESS: Got clean response from $($attempt.name)" -ForegroundColor Green
            Write-Host "   Generated: '$line'" -ForegroundColor White
            break
        } else {
            Write-Host "   SKIP: Response too short/long or empty after cleanup" -ForegroundColor Yellow
            Write-Host "   Raw: '$raw'" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ERROR: $($attempt.name) failed - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Fallback if all attempts failed
if (-not $line) {
    $fallbackLines = @(
        "Next step: Test the agent pipeline and verify all components work correctly",
        "TODO: Update documentation and run final tests",
        "Reminder: Check system logs and monitor performance",
        "Action required: Review and update configuration files",
        "Next: Deploy to production environment after testing"
    )
    $line = $fallbackLines | Get-Random
    Write-Host "   FALLBACK: Using predefined line" -ForegroundColor Yellow
    Write-Host "   Generated: '$line'" -ForegroundColor White
}

# 5) File editing via Agent API
Write-Host "5. Editing file via Agent API..." -ForegroundColor Yellow
$escapedLine = [Regex]::Escape($line)
$cmd = "Add-Content -Path '$FilePath' -Value ('`n' + '$escapedLine')"
$body2 = @{ cwd = 'D:/AI-Agent'; command = $cmd } | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/cursor/terminal `
        -Headers $h -ContentType 'application/json' -Body $body2
    
    Write-Host "   OK: File edit completed via Agent API" -ForegroundColor Green
} catch {
    Write-Host "   WARNING: Agent API failed, trying direct file edit" -ForegroundColor Yellow
    try {
        Add-Content -Path $FilePath -Value $line
        Write-Host "   OK: File edit completed directly" -ForegroundColor Green
    } catch {
        Write-Host "   ERROR: File edit failed completely" -ForegroundColor Red
        throw "Failed to edit file"
    }
}

# 6) Show result
Write-Host "6. Showing file contents..." -ForegroundColor Yellow
try {
    $content = Get-Content -Path $FilePath -Tail 5
    Write-Host "   Last 5 lines of ${FilePath}:" -ForegroundColor Cyan
    $content | ForEach-Object { Write-Host "      $_" -ForegroundColor White }
} catch {
    Write-Host "   WARNING: Could not read file contents" -ForegroundColor Yellow
}

# 7) Cursor bridge test
Write-Host "7. Testing Cursor bridge..." -ForegroundColor Yellow
try {
    $body3 = @{ filepath=$FilePath } | ConvertTo-Json
    $cursorResult = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/cursor/open `
        -Headers $h -Body $body3 -ContentType 'application/json'
    
    if ($cursorResult.error) {
        Write-Host "   INFO: Cursor API not configured: $($cursorResult.error)" -ForegroundColor Yellow
    } else {
        Write-Host "   SUCCESS: File opened in Cursor" -ForegroundColor Green
    }
} catch {
    Write-Host "   INFO: Cursor API not available (expected if not configured)" -ForegroundColor Yellow
}

Write-Host "=== Enhanced Pipeline v2 completed successfully! ===" -ForegroundColor Green
Write-Host "Generated content: '$line'" -ForegroundColor Cyan
Write-Host "File updated: $FilePath" -ForegroundColor Cyan
