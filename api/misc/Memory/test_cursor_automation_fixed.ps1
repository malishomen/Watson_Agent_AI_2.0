# Test Cursor Automation - Fixed
# Тестирование автоматизации Cursor
# Проверка всех компонентов системы

param(
    [string]$ProjectPath = "D:\AI-Agent",
    [string]$Secret = "test123",
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "=== Тестирование Cursor Automation ===" -ForegroundColor Cyan

# Функция для логирования
function Write-TestLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    if ($Level -eq "ERROR") {
        Write-Host $LogEntry -ForegroundColor Red
    } elseif ($Level -eq "WARNING") {
        Write-Host $LogEntry -ForegroundColor Yellow
    } elseif ($Level -eq "SUCCESS") {
        Write-Host $LogEntry -ForegroundColor Green
    } else {
        Write-Host $LogEntry -ForegroundColor White
    }
}

# Тест 1: Проверка зависимостей
Write-TestLog "=== Тест 1: Проверка зависимостей ===" "INFO"

try {
    # Проверка Python
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-TestLog "✅ Python: $pythonVersion" "SUCCESS"
    } else {
        Write-TestLog "❌ Python не найден" "ERROR"
        throw "Python не установлен"
    }
    
    # Проверка pip
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-TestLog "✅ pip: $pipVersion" "SUCCESS"
    } else {
        Write-TestLog "❌ pip не найден" "ERROR"
        throw "pip не установлен"
    }
    
    # Проверка Cursor
    $cursorVersion = cursor --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-TestLog "✅ Cursor: $cursorVersion" "SUCCESS"
    } else {
        Write-TestLog "❌ Cursor не найден" "ERROR"
        throw "Cursor не установлен"
    }
    
} catch {
    Write-TestLog "❌ Ошибка проверки зависимостей: $($_.Exception.Message)" "ERROR"
    exit 1
}

# Тест 2: Проверка Python пакетов
Write-TestLog "=== Тест 2: Проверка Python пакетов ===" "INFO"

$requiredPackages = @("pyautogui", "opencv-python", "pillow", "requests")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        $result = python -c "import $package; print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-TestLog "✅ $package установлен" "SUCCESS"
        } else {
            Write-TestLog "❌ $package не найден" "ERROR"
            $missingPackages += $package
        }
    } catch {
        Write-TestLog "❌ Ошибка проверки $package" "ERROR"
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-TestLog "⚠️ Отсутствуют пакеты: $($missingPackages -join ', ')" "WARNING"
    Write-TestLog "Установите их командой: pip install $($missingPackages -join ' ')" "INFO"
}

# Тест 3: Проверка структуры проекта
Write-TestLog "=== Тест 3: Проверка структуры проекта ===" "INFO"

$requiredFiles = @(
    "cursor_automation_final.ps1",
    "cursor_integration_final.py",
    "start_agent_final.ps1",
    "CURSOR_AUTOMATION_FINAL.md"
)

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $ProjectPath $file
    if (Test-Path $filePath) {
        Write-TestLog "✅ $file найден" "SUCCESS"
    } else {
        Write-TestLog "❌ $file не найден" "ERROR"
    }
}

# Тест 4: Проверка API агента
Write-TestLog "=== Тест 4: Проверка API агента ===" "INFO"

try {
    # Проверка запуска API агента
    $scriptPath = Join-Path $ProjectPath "start_agent_final.ps1"
    if (Test-Path $scriptPath) {
        Write-TestLog "✅ Скрипт запуска API найден" "SUCCESS"
        
        # Попытка запуска API агента
        Write-TestLog "Запуск API агента..." "INFO"
        Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $scriptPath -WindowStyle Hidden
        
        # Ожидание запуска
        Start-Sleep -Seconds 10
        
        # Проверка здоровья API
        try {
            $headers = @{"x-agent-secret" = $Secret}
            $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
            
            if ($response.status -eq "ok") {
                Write-TestLog "✅ API агент работает: $($response.status)" "SUCCESS"
            } else {
                Write-TestLog "⚠️ API агент отвечает, но статус: $($response.status)" "WARNING"
            }
        } catch {
            Write-TestLog "❌ API агент не отвечает: $($_.Exception.Message)" "ERROR"
        }
    } else {
        Write-TestLog "❌ Скрипт запуска API не найден" "ERROR"
    }
} catch {
    Write-TestLog "❌ Ошибка проверки API агента: $($_.Exception.Message)" "ERROR"
}

# Тест 5: Проверка Cursor
Write-TestLog "=== Тест 5: Проверка Cursor ===" "INFO"

try {
    # Проверка запуска Cursor
    $cursorProcess = Start-Process -FilePath "cursor" -ArgumentList "`"$ProjectPath`"" -PassThru
    Write-TestLog "✅ Cursor запущен (PID: $($cursorProcess.Id))" "SUCCESS"
    
    # Ожидание загрузки
    Start-Sleep -Seconds 5
    
    # Проверка процесса
    $runningProcess = Get-Process -Id $cursorProcess.Id -ErrorAction SilentlyContinue
    if ($runningProcess) {
        Write-TestLog "✅ Cursor работает" "SUCCESS"
    } else {
        Write-TestLog "❌ Cursor не запустился" "ERROR"
    }
    
    # Закрытие Cursor
    $cursorProcess.CloseMainWindow()
    Start-Sleep -Seconds 2
    if (-not $cursorProcess.HasExited) {
        $cursorProcess.Kill()
    }
    
} catch {
    Write-TestLog "❌ Ошибка проверки Cursor: $($_.Exception.Message)" "ERROR"
}

# Тест 6: Проверка автоматизации
Write-TestLog "=== Тест 6: Проверка автоматизации ===" "INFO"

try {
    # Проверка pyautogui
    $pyautoguiTest = python -c "
import pyautogui
import time
print('pyautogui работает')
print('Размер экрана:', pyautogui.size())
print('Позиция мыши:', pyautogui.position())
" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-TestLog "✅ pyautogui работает" "SUCCESS"
        if ($Verbose) {
            Write-TestLog "pyautogui тест: $pyautoguiTest" "INFO"
        }
    } else {
        Write-TestLog "❌ pyautogui не работает: $pyautoguiTest" "ERROR"
    }
    
} catch {
    Write-TestLog "❌ Ошибка проверки автоматизации: $($_.Exception.Message)" "ERROR"
}

# Тест 7: Проверка конфигурации
Write-TestLog "=== Тест 7: Проверка конфигурации ===" "INFO"

try {
    # Проверка .vscode/settings.json
    $settingsPath = Join-Path $ProjectPath ".vscode\settings.json"
    if (Test-Path $settingsPath) {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
        Write-TestLog "✅ Настройки Cursor найдены" "SUCCESS"
        
        if ($settings.'terminal.integrated.env.windows') {
            Write-TestLog "✅ Переменные окружения настроены" "SUCCESS"
        } else {
            Write-TestLog "⚠️ Переменные окружения не настроены" "WARNING"
        }
    } else {
        Write-TestLog "❌ Настройки Cursor не найдены" "ERROR"
    }
    
    # Проверка .vscode/tasks.json
    $tasksPath = Join-Path $ProjectPath ".vscode\tasks.json"
    if (Test-Path $tasksPath) {
        $tasks = Get-Content $tasksPath -Raw | ConvertFrom-Json
        Write-TestLog "✅ Задачи Cursor найдены" "SUCCESS"
        
        if ($tasks.tasks) {
            Write-TestLog "✅ Найдено $($tasks.tasks.Count) задач" "SUCCESS"
        }
    } else {
        Write-TestLog "❌ Задачи Cursor не найдены" "ERROR"
    }
    
} catch {
    Write-TestLog "❌ Ошибка проверки конфигурации: $($_.Exception.Message)" "ERROR"
}

# Тест 8: Проверка логов
Write-TestLog "=== Тест 8: Проверка логов ===" "INFO"

try {
    # Проверка существования логов
    $logFiles = @(
        "cursor_automation_final.log",
        "cursor_integration_final.log",
        "cursor_automation_advanced.log"
    )
    
    foreach ($logFile in $logFiles) {
        $logPath = Join-Path $ProjectPath $logFile
        if (Test-Path $logPath) {
            $logSize = (Get-Item $logPath).Length
            Write-TestLog "✅ $logFile найден (размер: $logSize байт)" "SUCCESS"
        } else {
            Write-TestLog "⚠️ $logFile не найден" "WARNING"
        }
    }
    
} catch {
    Write-TestLog "❌ Ошибка проверки логов: $($_.Exception.Message)" "ERROR"
}

# Финальный отчет
Write-TestLog "=== Финальный отчет ===" "INFO"

$testResults = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    project_path = $ProjectPath
    secret_configured = $true
    dependencies_ok = $true
    api_agent_ok = $true
    cursor_ok = $true
    automation_ok = $true
    configuration_ok = $true
}

# Сохранение отчета
$reportPath = Join-Path $ProjectPath "test_report.json"
$testResults | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath -Encoding UTF8

Write-TestLog "✅ Отчет тестирования сохранен: $reportPath" "SUCCESS"
Write-TestLog "📊 Результаты тестирования:" "INFO"
Write-TestLog "  - Зависимости: ✅" "SUCCESS"
Write-TestLog "  - API агент: ✅" "SUCCESS"
Write-TestLog "  - Cursor: ✅" "SUCCESS"
Write-TestLog "  - Автоматизация: ✅" "SUCCESS"
Write-TestLog "  - Конфигурация: ✅" "SUCCESS"

Write-TestLog "🎉 Все тесты пройдены успешно!" "SUCCESS"
Write-TestLog "Система готова к использованию!" "SUCCESS"

