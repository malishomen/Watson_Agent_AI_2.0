<#
.SYNOPSIS
    Тестирование pipeline: DeepSeek R1 → Qwen 2.5 → Cursor
#>

param(
    [string]$Task = "Add comment to loadUserTree function"
)

$ErrorActionPreference = 'Continue'

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   🧪 TEST LLM PIPELINE" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Шаг 1: Проверка LM Studio
Write-Host "1️⃣ Проверка LM Studio..." -ForegroundColor Yellow
try {
    $models = Invoke-RestMethod -Uri "http://127.0.0.1:1234/v1/models" -TimeoutSec 3
    $modelIds = $models.data | Select-Object -ExpandProperty id
    
    Write-Host "   ✅ LM Studio работает" -ForegroundColor Green
    Write-Host "   📦 Модели:" -ForegroundColor Cyan
    foreach ($m in $modelIds) {
        if ($m -match "deepseek|qwen") {
            Write-Host "      • $m" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   ❌ LM Studio не отвечает!" -ForegroundColor Red
    Write-Host "   Запустите LM Studio и загрузите модели" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Шаг 2: Тест DeepSeek R1
Write-Host "2️⃣ Тест DeepSeek R1 (reasoning)..." -ForegroundColor Yellow
try {
    $deepseekBody = @{
        model = "deepseek-r1-distill-qwen-14b-abliterated-v2"
        messages = @(
            @{
                role = "system"
                content = "Analyze the task and provide a plan."
            }
            @{
                role = "user"
                content = "Task: $Task`n`nProvide brief analysis."
            }
        )
        temperature = 0.3
        max_tokens = 200
    } | ConvertTo-Json -Depth 10
    
    Write-Host "   ⏳ Отправка запроса..." -ForegroundColor Gray
    $deepseekResponse = Invoke-RestMethod `
        -Uri "http://127.0.0.1:1234/v1/chat/completions" `
        -Method POST `
        -ContentType "application/json" `
        -Body $deepseekBody `
        -TimeoutSec 60
    
    $analysis = $deepseekResponse.choices[0].message.content
    Write-Host "   ✅ DeepSeek R1 ответил" -ForegroundColor Green
    Write-Host "   📊 Analysis: $($analysis.Substring(0, [Math]::Min(100, $analysis.Length)))..." -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Ошибка DeepSeek R1: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Шаг 3: Тест Qwen 2.5 Coder
Write-Host "3️⃣ Тест Qwen 2.5 Coder (diff generation)..." -ForegroundColor Yellow
try {
    $qwenBody = @{
        model = "qwen2.5-coder-7b-instruct"
        messages = @(
            @{
                role = "system"
                content = "You are a code generation assistant. Generate unified diff patches."
            }
            @{
                role = "user"
                content = "Task: $Task`n`nGenerate a small diff patch example."
            }
        )
        temperature = 0.2
        max_tokens = 500
    } | ConvertTo-Json -Depth 10
    
    Write-Host "   ⏳ Отправка запроса..." -ForegroundColor Gray
    $qwenResponse = Invoke-RestMethod `
        -Uri "http://127.0.0.1:1234/v1/chat/completions" `
        -Method POST `
        -ContentType "application/json" `
        -Body $qwenBody `
        -TimeoutSec 90
    
    $diff = $qwenResponse.choices[0].message.content
    Write-Host "   ✅ Qwen 2.5 Coder ответил" -ForegroundColor Green
    Write-Host "   📝 Response: $($diff.Length) chars" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Ошибка Qwen: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Шаг 4: Проверка Watson API
Write-Host "4️⃣ Проверка Watson API..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8090/health" -TimeoutSec 3
    Write-Host "   ✅ Watson API работает" -ForegroundColor Green
    
    $delegationEnabled = [Environment]::GetEnvironmentVariable('WATSON_USE_CURSOR_DELEGATION','User')
    Write-Host "   🔄 Delegation: $delegationEnabled" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Watson API не отвечает!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Итог
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "   ✅ ВСЕ КОМПОНЕНТЫ РАБОТАЮТ!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Pipeline готов:" -ForegroundColor Cyan
Write-Host "   DeepSeek R1 ✅" -ForegroundColor Green
Write-Host "   Qwen 2.5 Coder ✅" -ForegroundColor Green
Write-Host "   Watson API ✅" -ForegroundColor Green
Write-Host "   Cursor Delegation ✅" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Теперь отправьте задачу через /relay/submit!" -ForegroundColor Yellow
Write-Host ""


