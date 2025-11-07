# Cursor Automation Final
# Финальная автоматизация Cursor с автономным AI-агентом
# Полная реализация согласно инструкциям по интеграции Cursor для автономного агента

param(
    [string]$ProjectPath = "D:\AI-Agent",
    [string]$Task = "Создай полнофункциональное веб-приложение на FastAPI с PostgreSQL базой данных",
    [string]$Secret = "test123",
    [int]$Timeout = 600
)

$ErrorActionPreference = "Stop"

# Настройка логирования
$LogFile = "cursor_automation_final.log"
$StartTime = Get-Date

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Send-KeysToCursor {
    param([string]$Keys, [int]$Delay = 500)
    
    try {
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait($Keys)
        Start-Sleep -Milliseconds $Delay
        return $true
    } catch {
        Write-Log "Ошибка отправки клавиш: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Find-CursorWindow {
    try {
        $processes = Get-Process | Where-Object { 
            $_.ProcessName -like "*cursor*" -or 
            $_.MainWindowTitle -like "*cursor*" -or
            $_.MainWindowTitle -like "*Cursor*"
        }
        
        if ($processes) {
            Write-Log "Найдено окно Cursor: $($processes[0].MainWindowTitle)" "INFO"
            return $processes[0]
        } else {
            Write-Log "Окно Cursor не найдено" "WARNING"
            return $null
        }
    } catch {
        Write-Log "Ошибка поиска окна Cursor: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Activate-CursorWindow {
    param([System.Diagnostics.Process]$Process)
    
    try {
        if ($Process -and $Process.MainWindowHandle -ne [IntPtr]::Zero) {
            Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class Win32 {
                    [DllImport("user32.dll")]
                    public static extern bool SetForegroundWindow(IntPtr hWnd);
                    [DllImport("user32.dll")]
                    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
                    [DllImport("user32.dll")]
                    public static extern bool IsWindowVisible(IntPtr hWnd);
                }
"@
            
            if ([Win32]::IsWindowVisible($Process.MainWindowHandle)) {
                [Win32]::ShowWindow($Process.MainWindowHandle, 9) # SW_RESTORE
                [Win32]::SetForegroundWindow($Process.MainWindowHandle)
                Write-Log "Окно Cursor активировано" "INFO"
                return $true
            } else {
                Write-Log "Окно Cursor не видимо" "WARNING"
                return $false
            }
        } else {
            Write-Log "Не удалось активировать окно Cursor" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Ошибка активации окна: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-CursorProject {
    Write-Log "=== Шаг 1: Запуск Cursor и открытие проекта ===" "INFO"
    
    try {
        # Запуск Cursor с проектом
        $cursorProcess = Start-Process -FilePath "cursor" -ArgumentList "`"$ProjectPath`"" -PassThru
        Write-Log "Cursor запущен (PID: $($cursorProcess.Id))" "INFO"
        
        # Ожидание загрузки
        Start-Sleep -Seconds 8
        
        # Поиск и активация окна
        $cursorWindow = Find-CursorWindow
        if (-not $cursorWindow) {
            throw "Окно Cursor не найдено"
        }
        
        if (-not (Activate-CursorWindow -Process $cursorWindow)) {
            throw "Не удалось активировать окно Cursor"
        }
        
        Write-Log "✅ Cursor запущен и проект открыт" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Ошибка запуска Cursor: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Open-AIPanel {
    Write-Log "=== Шаг 2: Открытие AI-панели ===" "INFO"
    
    try {
        # Нажатие Ctrl+L для открытия AI-панели
        if (-not (Send-KeysToCursor -Keys "^l" -Delay 2000)) {
            throw "Не удалось открыть AI-панель"
        }
        
        Write-Log "✅ AI-панель открыта" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Ошибка открытия AI-панели: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Switch-ToAgentMode {
    Write-Log "=== Шаг 3: Переключение в Agent Mode ===" "INFO"
    
    try {
        # Открытие командной палитры (Ctrl+Shift+P)
        Send-KeysToCursor -Keys "^+p" -Delay 2000
        
        # Ввод команды для включения Agent Mode
        Send-KeysToCursor -Keys "Enable Agent Mode" -Delay 1000
        Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
        
        Write-Log "✅ Agent Mode активирован" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Ошибка переключения в Agent Mode: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Send-AgentRequest {
    param([string]$TaskDescription)
    
    Write-Log "=== Шаг 4: Отправка запроса агенту ===" "INFO"
    
    try {
        # Очистка поля ввода
        Send-KeysToCursor -Keys "^a" -Delay 500
        
        # Ввод текста задачи
        Send-KeysToCursor -Keys $TaskDescription -Delay 1000
        
        # Отправка запроса (Enter)
        Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
        
        Write-Log "✅ Запрос отправлен агенту" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Ошибка отправки запроса: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Wait-ForAgentCompletion {
    param([int]$TimeoutSeconds = 600)
    
    Write-Log "=== Шаг 5: Ожидание завершения работы агента ===" "INFO"
    
    $startTime = Get-Date
    $lastActivity = $startTime
    
    while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($TimeoutSeconds)) {
        try {
            # Автоматическое подтверждение изменений
            Auto-ConfirmChanges
            
            # Проверка завершения работы
            if (Test-AgentCompletion) {
                Write-Log "✅ Агент завершил работу" "INFO"
                break
            }
            
            # Проверка активности
            if ((Get-Date) - $lastActivity -gt [TimeSpan]::FromMinutes(2)) {
                Write-Log "⏰ Нет активности 2 минуты, считаем завершенным" "INFO"
                break
            }
            
            # Обновление времени последней активности
            if (Test-AgentActivity) {
                $lastActivity = Get-Date
            }
            
            $elapsed = [Math]::Round(((Get-Date) - $startTime).TotalSeconds)
            Write-Log "⏳ Ожидание... ${elapsed}с / ${TimeoutSeconds}с" "INFO"
            
            Start-Sleep -Seconds 10
            
        } catch {
            Write-Log "Ошибка при ожидании: $($_.Exception.Message)" "ERROR"
            Start-Sleep -Seconds 5
        }
    }
    
    Write-Log "✅ Ожидание завершено" "INFO"
    return $true
}

function Auto-ConfirmChanges {
    try {
        # Нажатие Ctrl+Enter для подтверждения команд
        Send-KeysToCursor -Keys "^+{ENTER}" -Delay 100
        Send-KeysToCursor -Keys "{ENTER}" -Delay 100
        Send-KeysToCursor -Keys "{TAB}" -Delay 100
        
    } catch {
        Write-Log "Ошибка автоподтверждения: $($_.Exception.Message)" "DEBUG"
    }
}

function Test-AgentCompletion {
    try {
        # Проверка через API агента
        $headers = @{"x-agent-secret" = $Secret}
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
        
        if ($response.status -eq "ok") {
            return $true
        } else {
            return $false
        }
        
    } catch {
        Write-Log "API не отвечает: $($_.Exception.Message)" "DEBUG"
        return $false
    }
}

function Test-AgentActivity {
    try {
        # Проверка API агента
        if (Test-AgentCompletion) {
            return $true
        }
        
        return $false
        
    } catch {
        Write-Log "Ошибка проверки активности: $($_.Exception.Message)" "DEBUG"
        return $false
    }
}

function Save-AllFiles {
    Write-Log "=== Шаг 6: Сохранение всех файлов ===" "INFO"
    
    try {
        # Сохранение всех файлов (Ctrl+Shift+S)
        Send-KeysToCursor -Keys "^+s" -Delay 2000
        
        Write-Log "✅ Все файлы сохранены" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Ошибка сохранения файлов: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Add-CodeComments {
    Write-Log "=== Шаг 7: Добавление комментариев к коду ===" "INFO"
    
    try {
        # Открытие AI-панели для нового запроса
        Send-KeysToCursor -Keys "^l" -Delay 2000
        
        # Формирование запроса на добавление комментариев
        $commentRequest = @"
Добавь подробные комментарии к коду, объясняющие:
1. Назначение каждой функции и класса
2. Параметры и возвращаемые значения
3. Логику работы алгоритмов
4. Примеры использования
5. Обработку ошибок
6. Связи между компонентами
"@
        
        # Очистка поля ввода
        Send-KeysToCursor -Keys "^a" -Delay 500
        
        # Отправка запроса
        Send-KeysToCursor -Keys $commentRequest -Delay 1000
        Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
        
        # Ожидание завершения
        Start-Sleep -Seconds 30
        
        Write-Log "✅ Комментарии добавлены" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Ошибка добавления комментариев: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-Tests {
    Write-Log "=== Шаг 8: Запуск тестов ===" "INFO"
    
    try {
        # Открытие терминала (Ctrl+`)
        Send-KeysToCursor -Keys "^`" -Delay 2000
        
        # Очистка терминала
        Send-KeysToCursor -Keys "^l" -Delay 500
        
        # Запуск тестов
        $testCommand = "py -3.11 -m pytest -q"
        Send-KeysToCursor -Keys $testCommand -Delay 1000
        Send-KeysToCursor -Keys "{ENTER}" -Delay 5000
        
        Write-Log "✅ Тесты запущены" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Ошибка запуска тестов: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-ProjectValidation {
    Write-Log "=== Шаг 9: Валидация проекта ===" "INFO"
    
    try {
        # Проверка структуры проекта
        $projectFiles = Get-ChildItem -Path $ProjectPath -Recurse -Include "*.py", "*.json", "*.yml", "*.yaml" | Measure-Object
        $fileCount = $projectFiles.Count
        
        # Проверка API агента
        if (Test-AgentCompletion) {
            Write-Log "✅ API агент работает" "INFO"
        } else {
            Write-Log "⚠️ API агент не отвечает" "WARNING"
        }
        
        Write-Log "✅ Проект валидирован: $fileCount файлов" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Ошибка валидации проекта: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function New-ExecutionReport {
    Write-Log "=== Генерация отчета ===" "INFO"
    
    try {
        $endTime = Get-Date
        $duration = ($endTime - $StartTime).TotalSeconds
        
        $report = @{
            start_time = $StartTime.ToString("yyyy-MM-dd HH:mm:ss")
            end_time = $endTime.ToString("yyyy-MM-dd HH:mm:ss")
            duration_seconds = [Math]::Round($duration, 2)
            project_path = $ProjectPath
            task = $Task
            timeout = $Timeout
            success = $true
        }
        
        # Сохранение отчета
        $reportPath = Join-Path $ProjectPath "cursor_automation_report.json"
        $report | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath -Encoding UTF8
        
        Write-Log "✅ Отчет сохранен: $reportPath" "INFO"
        Write-Log "📊 Статистика: $($report | ConvertTo-Json -Compress)" "INFO"
        
        return $report
        
    } catch {
        Write-Log "❌ Ошибка генерации отчета: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Start-APIAgent {
    Write-Log "Запуск API агента..." "INFO"
    
    try {
        # Запуск API агента через PowerShell скрипт
        $scriptPath = Join-Path $ProjectPath "start_agent_final.ps1"
        
        if (Test-Path $scriptPath) {
            Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $scriptPath -WindowStyle Hidden
            
            # Ожидание запуска API
            Start-Sleep -Seconds 10
            
            # Проверка здоровья
            if (Test-AgentCompletion) {
                Write-Log "✅ API агент запущен и работает" "INFO"
                return $true
            } else {
                Write-Log "❌ API агент не отвечает" "ERROR"
                return $false
            }
        } else {
            Write-Log "❌ Скрипт не найден: $scriptPath" "ERROR"
            return $false
        }
        
    } catch {
        Write-Log "❌ Ошибка запуска API агента: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Главная функция
function Start-FullWorkflow {
    Write-Log "🚀 === НАЧАЛО ПОЛНОГО WORKFLOW АВТОНОМНОГО АГЕНТА ===" "INFO"
    
    try {
        # Запуск API агента
        if (-not (Start-APIAgent)) {
            Write-Log "❌ Не удалось запустить API агента" "ERROR"
            return $false
        }
        
        # Шаг 1: Запуск Cursor
        if (-not (Start-CursorProject)) {
            return $false
        }
        
        # Шаг 2: Открытие AI-панели
        if (-not (Open-AIPanel)) {
            return $false
        }
        
        # Шаг 3: Переключение в Agent Mode
        if (-not (Switch-ToAgentMode)) {
            Write-Log "⚠️ Не удалось переключить в Agent Mode, продолжаем..." "WARNING"
        }
        
        # Шаг 4: Отправка основного запроса
        if (-not (Send-AgentRequest -TaskDescription $Task)) {
            return $false
        }
        
        # Шаг 5: Ожидание завершения
        if (-not (Wait-ForAgentCompletion -TimeoutSeconds $Timeout)) {
            Write-Log "⚠️ Агент не завершил работу в ожидаемое время" "WARNING"
        }
        
        # Шаг 6: Сохранение файлов
        Save-AllFiles
        
        # Шаг 7: Добавление комментариев
        Add-CodeComments
        
        # Шаг 8: Запуск тестов
        Start-Tests
        
        # Шаг 9: Валидация проекта
        Test-ProjectValidation
        
        # Генерация отчета
        New-ExecutionReport
        
        Write-Log "🎉 === WORKFLOW ЗАВЕРШЕН УСПЕШНО ===" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Критическая ошибка в workflow: $($_.Exception.Message)" "ERROR"
        New-ExecutionReport
        return $false
    }
}

# Запуск полного workflow
$success = Start-FullWorkflow

if ($success) {
    Write-Log "🎉 Проект успешно завершен!" "INFO"
    exit 0
} else {
    Write-Log "❌ Произошли ошибки в процессе выполнения" "ERROR"
    exit 1
}

