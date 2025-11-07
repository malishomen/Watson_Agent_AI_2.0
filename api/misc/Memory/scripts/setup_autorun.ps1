# Setup Autorun - Настройка автозапуска системы
# Создание ярлыка в папке автозагрузки Windows

# UTF-8 настройки
[Console]::InputEncoding = [Text.UTF8Encoding]::UTF8
[Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8

function Write-AutorunLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path "autorun.log" -Value $LogEntry -Encoding UTF8
}

function Create-StartupScript {
    """Создание скрипта автозапуска"""
    try {
        Write-AutorunLog "Creating startup script..." "INFO"
        
        $startupScript = @"
@echo off
chcp 65001 >nul

echo === AI Agent + Cursor Automation - Autorun ===
echo Starting system...

REM Ждём 10 секунд для загрузки системы
timeout /t 10 /nobreak >nul

REM Запуск системы
powershell -ExecutionPolicy Bypass -File "D:\AI-Agent\fresh_start\scripts\start_system.ps1" -Task "System startup" -Timeout 300

echo === Autorun Complete ===
"@
        
        $startupScript | Out-File -FilePath "start_windows_autorun.bat" -Encoding UTF8
        Write-AutorunLog "✅ Startup script created" "SUCCESS"
        return $true
        
    } catch {
        Write-AutorunLog "❌ Failed to create startup script: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Create-StartupShortcut {
    """Создание ярлыка автозапуска"""
    try {
        Write-AutorunLog "Creating startup shortcut..." "INFO"
        
        $WshShell = New-Object -ComObject WScript.Shell
        $ShortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\AIAgent.lnk"
        $TargetPath = "D:\AI-Agent\fresh_start\start_windows_autorun.bat"
        
        # Проверяем существование целевого файла
        if (-not (Test-Path $TargetPath)) {
            Write-AutorunLog "❌ Target file not found: $TargetPath" "ERROR"
            return $false
        }
        
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.WorkingDirectory = "D:\AI-Agent\fresh_start"
        $Shortcut.Description = "AI Agent + Cursor Automation Autorun"
        $Shortcut.Save()
        
        Write-AutorunLog "✅ Startup shortcut created: $ShortcutPath" "SUCCESS"
        return $true
        
    } catch {
        Write-AutorunLog "❌ Failed to create startup shortcut: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Главная логика
Write-AutorunLog "=== AI AGENT + CURSOR AUTOMATION - AUTORUN SETUP ===" "INFO"

# Создание скрипта автозапуска
if (-not (Create-StartupScript)) {
    Write-AutorunLog "❌ Failed to create startup script" "ERROR"
    exit 1
}

# Создание ярлыка автозапуска
if (-not (Create-StartupShortcut)) {
    Write-AutorunLog "❌ Failed to create startup shortcut" "ERROR"
    exit 1
}

Write-AutorunLog "=== AUTORUN SETUP COMPLETED ===" "SUCCESS"
Write-AutorunLog "System will auto-start on Windows boot" "SUCCESS"





