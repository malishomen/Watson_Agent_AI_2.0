# scripts/e2e_agent_pipeline_fixed.ps1
# Сквозной прогон: LLM → Агент API → правка файла → (опционально) Cursor

param(
    [string]$ModelId = "",  # Если пустой - возьмет первую доступную модель
    [string]$Task = "Dobav v README.md odnu stroku-napominanie razrabotchiku o sleduyushem shage (ne bolee 100 simvolov).",
    [string]$FilePath = "D:/AI-Agent/README.md"
)

$ErrorActionPreference = "Stop"

Write-Host "=== E2E Agent Pipeline: LLM → Agent API → File Edit ===" -ForegroundColor Cyan

# 1) Проверка здоровья API
Write-Host "1. Checking FastAPI health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod http://127.0.0.1:8088/health
    Write-Host "   ✅ FastAPI: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ FastAPI not running on :8088" -ForegroundColor Red
    throw "FastAPI server not accessible"
}

# 2) Заголовок с секретом
Write-Host "2. Setting up authentication..." -ForegroundColor Yellow
$secret = $env:AGENT_HTTP_SHARED_SECRET
if (-not $secret) {
    Write-Host "   ❌ AGENT_HTTP_SHARED_SECRET not set" -ForegroundColor Red
    throw "Environment variable AGENT_HTTP_SHARED_SECRET is required"
}
$h = @{ "x-agent-secret" = $secret }
Write-Host "   ✅ Secret configured (len: $($secret.Length))" -ForegroundColor Green

# 3) Проверка LM Studio
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
    Write-Host "   ✅ LM Studio: Model '$MODEL' ready" -ForegroundColor Green
} catch {
    Write-Host "   ❌ LM Studio not accessible on :1234" -ForegroundColor Red
    throw "LM Studio server not accessible or no models loaded"
}

# 4) Сформировать задание для LLM
Write-Host "4. Generating content with LLM..." -ForegroundColor Yellow
$body = @{
    model = $MODEL
    messages = @(
        @{ role="system"; content="Otvechai odnoi strokoi, lyogkii delovoi ton. Bez kavychek." },
        @{ role="user"; content=$Task }
    )
    temperature = 0.5
} | ConvertTo-Json -Depth 6

try {
    $res = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:1234/v1/chat/completions `
        -Headers @{ "Authorization"="Bearer lm-studio"; "Content-Type"="application/json" } `
        -Body $body
    
    $line = $res.choices[0].message.content.Trim()
    if (-not $line) { 
        throw "LLM returned empty response" 
    }
    
    Write-Host "   ✅ LLM generated: '$line'" -ForegroundColor Green
} catch {
    Write-Host "   ❌ LLM generation failed" -ForegroundColor Red
    throw "Failed to generate content with LLM"
}

# 5) Правка файла через терминал-эндпоинт агента
Write-Host "5. Editing file via Agent API..." -ForegroundColor Yellow
$escapedLine = [Regex]::Escape($line).Replace('\\','\')
$cmd = "Add-Content -Path '$FilePath' -Value ('`n' + '$escapedLine')"
$body2 = @{ cwd = 'D:/AI-Agent'; command = $cmd } | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/cursor/terminal `
        -Headers $h -ContentType 'application/json' -Body $body2
    
    Write-Host "   ✅ File edit completed" -ForegroundColor Green
} catch {
    Write-Host "   ❌ File edit failed" -ForegroundColor Red
    throw "Failed to edit file via Agent API"
}

# 6) Показать результат
Write-Host "6. Showing file contents..." -ForegroundColor Yellow
try {
    $content = Get-Content -Path $FilePath -Tail 5
    Write-Host "   Last 5 lines of $FilePath:" -ForegroundColor Cyan
    $content | ForEach-Object { Write-Host "      $_" -ForegroundColor White }
} catch {
    Write-Host "   Warning: Could not read file contents" -ForegroundColor Yellow
}

# 7) (Опционально) Попытка открыть файл в Cursor
Write-Host "7. Attempting to open file in Cursor..." -ForegroundColor Yellow
try {
    $body3 = @{ filepath=$FilePath } | ConvertTo-Json
    $cursorResult = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/cursor/open `
        -Headers $h -Body $body3 -ContentType 'application/json'
    
    if ($cursorResult.error) {
        Write-Host "   Warning: Cursor API not configured: $($cursorResult.error)" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ File opened in Cursor" -ForegroundColor Green
    }
} catch {
    Write-Host "   Warning: Cursor API not available" -ForegroundColor Yellow
}

Write-Host "=== Pipeline completed successfully! ===" -ForegroundColor Green
Write-Host "Generated content: '$line'" -ForegroundColor Cyan
Write-Host "File updated: $FilePath" -ForegroundColor Cyan
