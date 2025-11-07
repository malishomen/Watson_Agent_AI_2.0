# Test Python Integration
# Проверка интеграции Python с системой автоматизации

Write-Host "=== Python Integration Test ===" -ForegroundColor Cyan

# Проверка Python версий
Write-Host "Checking Python versions..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    exit 1
}

# Проверка пакетов
Write-Host "Checking Python packages..." -ForegroundColor Yellow

try {
    $testResult = python -c "import pyautogui, PIL, keyboard; print('All packages available')"
    Write-Host "✅ $testResult" -ForegroundColor Green
} catch {
    Write-Host "❌ Missing packages: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Проверка pyautogui функциональности
Write-Host "Testing pyautogui functionality..." -ForegroundColor Yellow

try {
    $testScript = @"
import pyautogui
import time

print("Testing pyautogui...")
print(f"Screen size: {pyautogui.size()}")
print(f"Mouse position: {pyautogui.position()}")
print("pyautogui is working correctly!")
"@
    
    $testScript | Out-File -FilePath "test_pyautogui.py" -Encoding UTF8
    python test_pyautogui.py
    Remove-Item "test_pyautogui.py" -ErrorAction SilentlyContinue
    
    Write-Host "✅ pyautogui functionality test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ pyautogui test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Проверка скриптов автоматизации
Write-Host "Checking automation scripts..." -ForegroundColor Yellow

$scripts = @(
    "start_cursor_automation_fixed.ps1",
    "cursor_automation_fixed.ps1"
)

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "✅ $script found" -ForegroundColor Green
    } else {
        Write-Host "❌ $script not found" -ForegroundColor Red
    }
}

# Финальный тест
Write-Host "=== Final Integration Test ===" -ForegroundColor Cyan

try {
    # Тест автоопределения Python
    function Get-PyCmd {
        $candidates = @("python","py -3.11","py -3.13","py -3")
        foreach($c in $candidates){
            try{
                $v = & $c --version 2>$null
                if($LASTEXITCODE -eq 0 -and $v){ return $c }
            }catch{}
        }
        return "python"
    }
    
    $PY = Get-PyCmd
    Write-Host "✅ Python selector: $PY" -ForegroundColor Green
    
    # Тест команды pytest
    $pytestTest = & $PY -c "import pytest; print('pytest available')"
    Write-Host "✅ pytest test: $pytestTest" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Integration test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "=== Python Integration Test Complete ===" -ForegroundColor Green
Write-Host "System ready for automation!" -ForegroundColor Cyan





