# Cursor Automation PowerShell Script
# Оркестратор для автоматизации Cursor Editor

param(
    [string]$ProjectPath = "D:\AI-Agent\fresh_start",
    [string]$Task = "Create web application",
    [string]$Secret = "test123",
    [int]$Timeout = 600
)

# UTF-8 настройки
[Console]::InputEncoding = [Text.UTF8Encoding]::UTF8
[Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path "automation.log" -Value $LogEntry -Encoding UTF8
}

function Start-API {
    """Запуск API агента"""
    try {
        Write-Log "Starting API Agent..." "INFO"
        
        # Проверяем, не запущен ли уже
        $apiProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
            Where-Object { $_.CommandLine -like "*uvicorn*" }
        
        if ($apiProcess) {
            Write-Log "API Agent already running (PID: $($apiProcess.Id))" "INFO"
            return $true
        }
        
        # Запускаем API
        $apiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "api.agent:app", "--host", "127.0.0.1", "--port", "8088" -PassThru -NoNewWindow
        Start-Sleep -Seconds 3
        
        Write-Log "API Agent started (PID: $($apiProcess.Id))" "SUCCESS"
        return $true
        
    } catch {
        Write-Log "Failed to start API Agent: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-Cursor {
    """Запуск Cursor Editor"""
    try {
        Write-Log "Starting Cursor..." "INFO"
        
        # Проверяем наличие Cursor
        $cursorCmd = Get-Command cursor -ErrorAction SilentlyContinue
        if (-not $cursorCmd) {
            throw "Cursor not found in PATH"
        }
        
        # Запускаем Cursor
        $cursorProcess = Start-Process -FilePath "cursor" -ArgumentList $ProjectPath -PassThru
        Start-Sleep -Seconds 5
        
        Write-Log "Cursor started (PID: $($cursorProcess.Id))" "SUCCESS"
        return $true
        
    } catch {
        Write-Log "Failed to start Cursor: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-Automation {
    """Запуск автоматизации"""
    try {
        Write-Log "Starting automation..." "INFO"
        
        # Запускаем Python скрипт автоматизации
        $pythonScript = "automation\cursor_automation.py"
        $pythonProcess = Start-Process -FilePath "python" -ArgumentList $pythonScript, $Task -PassThru -Wait
        
        if ($pythonProcess.ExitCode -eq 0) {
            Write-Log "Automation completed successfully" "SUCCESS"
            return $true
        } else {
            Write-Log "Automation failed with exit code: $($pythonProcess.ExitCode)" "ERROR"
            return $false
        }
        
    } catch {
        Write-Log "Failed to run automation: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Главная логика
Write-Log "=== CURSOR AUTOMATION STARTED ===" "INFO"
Write-Log "Project: $ProjectPath" "INFO"
Write-Log "Task: $Task" "INFO"
Write-Log "Timeout: $Timeout seconds" "INFO"

# Шаг 1: Запуск API
if (-not (Start-API)) {
    Write-Log "Failed to start API Agent" "ERROR"
    exit 1
}

# Шаг 2: Запуск Cursor
if (-not (Start-Cursor)) {
    Write-Log "Failed to start Cursor" "ERROR"
    exit 1
}

# Шаг 3: Запуск автоматизации
if (-not (Start-Automation)) {
    Write-Log "Failed to run automation" "ERROR"
    exit 1
}

Write-Log "=== AUTOMATION COMPLETED SUCCESSFULLY ===" "SUCCESS"





