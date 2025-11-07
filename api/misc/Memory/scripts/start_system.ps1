# Start System - Запуск всей системы AI Agent + Cursor Automation
# Главный скрипт для запуска всех компонентов

param(
    [string]$Task = "Create web application",
    [int]$Timeout = 600
)

# UTF-8 настройки
[Console]::InputEncoding = [Text.UTF8Encoding]::UTF8
[Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

function Write-SystemLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path "system.log" -Value $LogEntry -Encoding UTF8
}

function Test-Prerequisites {
    """Проверка предварительных условий"""
    Write-SystemLog "Checking prerequisites..." "INFO"
    
    $prerequisites = @{
        python = $false
        cursor = $false
        lm_studio = $false
    }
    
    # Проверка Python
    try {
        $pythonVersion = python --version
        Write-SystemLog "✅ Python: $pythonVersion" "SUCCESS"
        $prerequisites.python = $true
    } catch {
        Write-SystemLog "❌ Python not found" "ERROR"
    }
    
    # Проверка Cursor
    try {
        $cursorVersion = cmd /c "cursor --version" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-SystemLog "✅ Cursor: $cursorVersion" "SUCCESS"
            $prerequisites.cursor = $true
        } else {
            Write-SystemLog "❌ Cursor not found" "ERROR"
        }
    } catch {
        Write-SystemLog "❌ Cursor not found" "ERROR"
    }
    
    # Проверка LM Studio
    try {
        $lmResponse = Invoke-RestMethod -Uri "http://127.0.0.1:1234/v1/models" -TimeoutSec 5
        if ($lmResponse.data) {
            Write-SystemLog "✅ LM Studio: Running with $($lmResponse.data.Count) models" "SUCCESS"
            $prerequisites.lm_studio = $true
        } else {
            Write-SystemLog "⚠️ LM Studio: Running but no models" "WARNING"
        }
    } catch {
        Write-SystemLog "❌ LM Studio: Not running" "ERROR"
    }
    
    return $prerequisites
}

function Install-Dependencies {
    """Установка зависимостей"""
    Write-SystemLog "Installing dependencies..." "INFO"
    
    try {
        # Установка Python пакетов
        pip install -r requirements.txt
        Write-SystemLog "✅ Dependencies installed" "SUCCESS"
        return $true
    } catch {
        Write-SystemLog "❌ Failed to install dependencies: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-AllServices {
    """Запуск всех сервисов"""
    Write-SystemLog "Starting all services..." "INFO"
    
    try {
        # Запуск автоматизации Cursor
        $automationScript = "automation\cursor_automation.ps1"
        $automationArgs = @(
            "-ProjectPath", "D:\AI-Agent\Memory",
            "-Task", $Task,
            "-Timeout", $Timeout
        )
        
        Write-SystemLog "Starting Cursor automation..." "INFO"
        & $automationScript @automationArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-SystemLog "✅ All services started successfully" "SUCCESS"
            return $true
        } else {
            Write-SystemLog "❌ Failed to start services" "ERROR"
            return $false
        }
        
    } catch {
        Write-SystemLog "❌ Error starting services: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Главная логика
Write-SystemLog "=== AI AGENT + CURSOR AUTOMATION SYSTEM ===" "INFO"
Write-SystemLog "Starting fresh system..." "INFO"

# Проверка предварительных условий
$prerequisites = Test-Prerequisites

if (-not $prerequisites.python -or -not $prerequisites.cursor) {
    Write-SystemLog "❌ Critical prerequisites missing" "ERROR"
    exit 1
}

# Установка зависимостей
if (-not (Install-Dependencies)) {
    Write-SystemLog "❌ Failed to install dependencies" "ERROR"
    exit 1
}

# Запуск сервисов
if (-not (Start-AllServices)) {
    Write-SystemLog "❌ Failed to start services" "ERROR"
    exit 1
}

Write-SystemLog "=== SYSTEM STARTED SUCCESSFULLY ===" "SUCCESS"
Write-SystemLog "AI Agent + Cursor Automation is ready!" "SUCCESS"
