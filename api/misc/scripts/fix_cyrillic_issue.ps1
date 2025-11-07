# fix_cyrillic_issue.ps1 - Исправление проблемы с кириллическими символами
Write-Host "=== Исправление проблемы с кириллическими символами ===" -ForegroundColor Cyan

# 1. Проверяем текущие процессы Python
Write-Host "1. Проверяем запущенные процессы Python..." -ForegroundColor Yellow
$python_processes = Get-Process | Where-Object { $_.ProcessName -match "python|py" }
if ($python_processes) {
    Write-Host "Найдены процессы Python:" -ForegroundColor Red
    $python_processes | ForEach-Object { Write-Host "  PID: $($_.Id) - $($_.ProcessName)" -ForegroundColor Red }
    Write-Host "Останавливаем все процессы Python..." -ForegroundColor Yellow
    $python_processes | Stop-Process -Force
    Start-Sleep 2
}

# 2. Очищаем переменные окружения от кириллических символов
Write-Host "2. Очищаем переменные окружения..." -ForegroundColor Yellow
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:CHCP = "65001"

# 3. Создаем безопасные алиасы
Write-Host "3. Создаем безопасные алиасы..." -ForegroundColor Yellow
function Safe-Python {
    param([string]$Args = "")
    py -3.11 $Args
}

function Safe-Python3 {
    param([string]$Args = "")
    py -3.11 $Args
}

# 4. Проверяем доступность Python
Write-Host "4. Проверяем доступность Python..." -ForegroundColor Yellow
try {
    $version = py -3.11 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python доступен: $version" -ForegroundColor Green
    } else {
        Write-Host "❌ Python недоступен" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Ошибка при проверке Python: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 5. Тестируем безопасные команды
Write-Host "5. Тестируем безопасные команды..." -ForegroundColor Yellow
try {
    $test_result = py -3.11 -c "print('Python работает корректно')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Тест Python прошел успешно: $test_result" -ForegroundColor Green
    } else {
        Write-Host "❌ Тест Python не прошел: $test_result" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Ошибка при тестировании Python: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "=== Исправление завершено ===" -ForegroundColor Green
Write-Host "Теперь используйте команды:" -ForegroundColor Cyan
Write-Host "  py -3.11 -c 'команда'" -ForegroundColor White
Write-Host "  Safe-Python -Args 'команда'" -ForegroundColor White
Write-Host "  .\safe_python.ps1 -Command python -Args 'команда'" -ForegroundColor White
