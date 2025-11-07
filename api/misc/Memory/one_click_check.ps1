# One-Click Check - Полная диагностика системы Watson Agent + Cursor Automation
# Проверка всех компонентов системы за один запуск

Write-Host "=== Watson Agent + Cursor Automation - One-Click Check ===" -ForegroundColor Cyan
Write-Host "Проверка всех компонентов системы..." -ForegroundColor Yellow

$results = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    components = @{}
    overall_status = "UNKNOWN"
}

# 1. Проверка LM Studio
Write-Host "`n1. Checking LM Studio..." -ForegroundColor Yellow
try {
    $lmResponse = Invoke-RestMethod -Uri "http://127.0.0.1:1234/v1/models" -TimeoutSec 5
    if ($lmResponse.data) {
        Write-Host "✅ LM Studio: Running with $($lmResponse.data.Count) models" -ForegroundColor Green
        $results.components.lm_studio = "✅ Running"
    } else {
        Write-Host "⚠️ LM Studio: Running but no models loaded" -ForegroundColor Yellow
        $results.components.lm_studio = "⚠️ No models"
    }
} catch {
    Write-Host "❌ LM Studio: Not running or not accessible" -ForegroundColor Red
    $results.components.lm_studio = "❌ Not running"
}

# 2. Проверка WatsonAgent API
Write-Host "`n2. Checking WatsonAgent API..." -ForegroundColor Yellow
try {
    $headers = @{"x-agent-secret" = "test123"}
    $apiResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
    if ($apiResponse.status -eq "ok") {
        Write-Host "✅ WatsonAgent API: Running and healthy" -ForegroundColor Green
        $results.components.watson_agent = "✅ Running"
    } else {
        Write-Host "⚠️ WatsonAgent API: Running but status: $($apiResponse.status)" -ForegroundColor Yellow
        $results.components.watson_agent = "⚠️ $($apiResponse.status)"
    }
} catch {
    Write-Host "❌ WatsonAgent API: Not running" -ForegroundColor Red
    $results.components.watson_agent = "❌ Not running"
}

# 3. Проверка Cursor CLI
Write-Host "`n3. Checking Cursor CLI..." -ForegroundColor Yellow
try {
    $cursorVersion = cursor --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Cursor CLI: $cursorVersion" -ForegroundColor Green
        $results.components.cursor_cli = "✅ Available"
    } else {
        Write-Host "❌ Cursor CLI: Not found" -ForegroundColor Red
        $results.components.cursor_cli = "❌ Not found"
    }
} catch {
    Write-Host "❌ Cursor CLI: Not found" -ForegroundColor Red
    $results.components.cursor_cli = "❌ Not found"
}

# 4. Проверка Python и пакетов
Write-Host "`n4. Checking Python and packages..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    $packageTest = python -c "import pyautogui, PIL, keyboard; print('All packages available')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python: $pythonVersion with all packages" -ForegroundColor Green
        $results.components.python = "✅ Ready"
    } else {
        Write-Host "❌ Python: Missing packages" -ForegroundColor Red
        $results.components.python = "❌ Missing packages"
    }
} catch {
    Write-Host "❌ Python: Not found" -ForegroundColor Red
    $results.components.python = "❌ Not found"
}

# 5. Проверка Docker
Write-Host "`n5. Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
        $results.components.docker = "✅ Available"
    } else {
        Write-Host "❌ Docker: Not found" -ForegroundColor Red
        $results.components.docker = "❌ Not found"
    }
} catch {
    Write-Host "❌ Docker: Not found" -ForegroundColor Red
    $results.components.docker = "❌ Not found"
}

# 6. Проверка файлов проекта
Write-Host "`n6. Checking project files..." -ForegroundColor Yellow
$requiredFiles = @(
    "start_cursor_automation_fixed.ps1",
    "cursor_automation_fixed.ps1",
    "start_windows_autorun.bat",
    "test_python_integration.ps1"
)

$filesStatus = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
        $filesStatus += "✅ $file"
    } else {
        Write-Host "❌ $file" -ForegroundColor Red
        $filesStatus += "❌ $file"
    }
}
$results.components.project_files = $filesStatus

# 7. Проверка автозапуска
Write-Host "`n7. Checking Windows autorun..." -ForegroundColor Yellow
try {
    $startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\WatsonAgent.lnk"
    if (Test-Path $startupPath) {
        Write-Host "✅ Autorun shortcut: Found" -ForegroundColor Green
        $results.components.autorun = "✅ Configured"
    } else {
        Write-Host "❌ Autorun shortcut: Not found" -ForegroundColor Red
        $results.components.autorun = "❌ Not configured"
    }
} catch {
    Write-Host "❌ Autorun: Error checking" -ForegroundColor Red
    $results.components.autorun = "❌ Error"
}

# 8. Мини-тест автоматизации (если все готово)
Write-Host "`n8. Running mini automation test..." -ForegroundColor Yellow

$readyForTest = $true
if ($results.components.lm_studio -notlike "✅*") { $readyForTest = $false }
if ($results.components.python -notlike "✅*") { $readyForTest = $false }
if ($results.components.cursor_cli -notlike "✅*") { $readyForTest = $false }

if ($readyForTest) {
    try {
        Write-Host "Running mini automation test..." -ForegroundColor Cyan
        $testResult = powershell -ExecutionPolicy Bypass -File "test_python_integration.ps1" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Mini automation test: Passed" -ForegroundColor Green
            $results.components.mini_test = "✅ Passed"
        } else {
            Write-Host "⚠️ Mini automation test: Issues detected" -ForegroundColor Yellow
            $results.components.mini_test = "⚠️ Issues"
        }
    } catch {
        Write-Host "❌ Mini automation test: Failed" -ForegroundColor Red
        $results.components.mini_test = "❌ Failed"
    }
} else {
    Write-Host "⚠️ Skipping mini test - prerequisites not met" -ForegroundColor Yellow
    $results.components.mini_test = "⚠️ Skipped"
}

# Финальная оценка
Write-Host "`n=== FINAL ASSESSMENT ===" -ForegroundColor Cyan

$criticalComponents = @("lm_studio", "python", "cursor_cli")
$criticalReady = $true
foreach ($component in $criticalComponents) {
    if ($results.components.$component -notlike "✅*") {
        $criticalReady = $false
        break
    }
}

if ($criticalReady) {
    $results.overall_status = "✅ READY"
    Write-Host "🎉 SYSTEM READY FOR AUTOMATION!" -ForegroundColor Green
    Write-Host "All critical components are working" -ForegroundColor Green
} else {
    $results.overall_status = "❌ NOT READY"
    Write-Host "⚠️ SYSTEM NEEDS ATTENTION" -ForegroundColor Red
    Write-Host "Some critical components are missing or not working" -ForegroundColor Red
}

# Сохранение отчета
$reportPath = "one_click_check_report.json"
$results | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host "`n📊 Detailed report saved: $reportPath" -ForegroundColor Cyan
Write-Host "📋 Summary:" -ForegroundColor Cyan

foreach ($component in $results.components.PSObject.Properties) {
    $status = $component.Value
    $name = $component.Name
    Write-Host "  $name`: $status" -ForegroundColor White
}

Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
if ($results.overall_status -eq "✅ READY") {
    Write-Host "  • Run: .\start_cursor_automation_fixed.ps1 -Task 'Create test app' -Timeout 300" -ForegroundColor Green
    Write-Host "  • Run: .\cursor_automation_fixed.ps1 -Task 'Create REST API' -Timeout 900" -ForegroundColor Green
} else {
    Write-Host "  • Fix missing components first" -ForegroundColor Red
    Write-Host "  • Run: .\setup_autorun.ps1" -ForegroundColor Yellow
}

Write-Host "`n=== One-Click Check Complete ===" -ForegroundColor Green





