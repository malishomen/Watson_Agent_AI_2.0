# Start Telegram Bot - Запуск Telegram бота для AI Agent
# Интеграция с API агентом и автоматизация Cursor

# UTF-8 настройки
[Console]::InputEncoding = [Text.UTF8Encoding]::UTF8
[Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

function Write-BotLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path "telegram_bot.log" -Value $LogEntry -Encoding UTF8
}

function Test-Prerequisites {
    """Проверка предварительных условий"""
    Write-BotLog "Checking prerequisites..." "INFO"
    
    $prerequisites = @{
        python = $false
        api_agent = $false
        bot_token = $false
    }
    
    # Проверка Python
    try {
        $pythonVersion = python --version
        Write-BotLog "✅ Python: $pythonVersion" "SUCCESS"
        $prerequisites.python = $true
    } catch {
        Write-BotLog "❌ Python not found" "ERROR"
    }
    
    # Проверка API агента
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -TimeoutSec 5
        if ($response.status -eq "ok") {
            Write-BotLog "✅ API Agent: Running" "SUCCESS"
            $prerequisites.api_agent = $true
        } else {
            Write-BotLog "❌ API Agent: Not responding" "ERROR"
        }
    } catch {
        Write-BotLog "❌ API Agent: Not running" "ERROR"
    }
    
    # Проверка токена бота
    $botToken = $env:TELEGRAM_BOT_TOKEN
    if ($botToken -and $botToken -ne "YOUR_BOT_TOKEN_HERE") {
        Write-BotLog "✅ Bot Token: Set" "SUCCESS"
        $prerequisites.bot_token = $true
    } else {
        Write-BotLog "❌ Bot Token: Not set" "ERROR"
        Write-BotLog "Set environment variable: `$env:TELEGRAM_BOT_TOKEN = 'your_bot_token'" "WARNING"
    }
    
    return $prerequisites
}

function Start-Bot {
    """Запуск Telegram бота"""
    try {
        Write-BotLog "Starting Telegram bot..." "INFO"
        
        # Запускаем бота
        $botProcess = Start-Process -FilePath "python" -ArgumentList "telegram_bot.py" -PassThru -NoNewWindow
        
        if ($botProcess) {
            Write-BotLog "✅ Telegram bot started (PID: $($botProcess.Id))" "SUCCESS"
            return $true
        } else {
            Write-BotLog "❌ Failed to start Telegram bot" "ERROR"
            return $false
        }
        
    } catch {
        Write-BotLog "❌ Error starting Telegram bot: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Главная логика
Write-BotLog "=== TELEGRAM BOT FOR AI AGENT ===" "INFO"
Write-BotLog "Starting Telegram bot..." "INFO"

# Проверка предварительных условий
$prerequisites = Test-Prerequisites

if (-not $prerequisites.python) {
    Write-BotLog "❌ Python not found" "ERROR"
    exit 1
}

if (-not $prerequisites.api_agent) {
    Write-BotLog "❌ API Agent not running" "ERROR"
    Write-BotLog "Start API Agent first: python -m uvicorn api.agent:app --host 127.0.0.1 --port 8088" "WARNING"
    exit 1
}

if (-not $prerequisites.bot_token) {
    Write-BotLog "❌ Bot token not set" "ERROR"
    Write-BotLog "Create bot via @BotFather and set token:" "WARNING"
    Write-BotLog "`$env:TELEGRAM_BOT_TOKEN = 'your_bot_token'" "WARNING"
    exit 1
}

# Запуск бота
if (-not (Start-Bot)) {
    Write-BotLog "❌ Failed to start Telegram bot" "ERROR"
    exit 1
}

Write-BotLog "=== TELEGRAM BOT STARTED SUCCESSFULLY ===" "SUCCESS"
Write-BotLog "Bot is ready to receive messages!" "SUCCESS"





