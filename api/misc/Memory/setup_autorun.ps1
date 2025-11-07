# Setup Windows Autorun for Watson Agent + Cursor Automation
# Создание автозапуска при старте Windows

Write-Host "=== Watson Agent + Cursor Automation - Autorun Setup ===" -ForegroundColor Cyan

try {
    # Проверка наличия PowerShell 7
    $pwshPath = Get-Command pwsh -ErrorAction SilentlyContinue
    if (-not $pwshPath) {
        Write-Host "⚠️ PowerShell 7 not found. Using Windows PowerShell 5.x" -ForegroundColor Yellow
    }

    $WshShell = New-Object -ComObject WScript.Shell
    $ShortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\WatsonAgent.lnk"
    $TargetPath = "D:\AI-Agent\start_windows_autorun.bat"

    Write-Host "Creating shortcut for autorun..." -ForegroundColor Yellow
    Write-Host "Shortcut Path: $ShortcutPath" -ForegroundColor Cyan
    Write-Host "Target Path: $TargetPath" -ForegroundColor Cyan

    # Проверка существования целевого файла
    if (-not (Test-Path $TargetPath)) {
        Write-Host "❌ Target file not found: $TargetPath" -ForegroundColor Red
        throw "Target file not found"
    }

    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.WorkingDirectory = "D:\AI-Agent"
    $Shortcut.Description = "Watson Agent + Cursor Automation Autorun"
    $Shortcut.Save()

    Write-Host "✅ Autorun shortcut created successfully!" -ForegroundColor Green
    Write-Host "✅ System will auto-start on Windows boot" -ForegroundColor Green

    # Дополнительная проверка
    if (Test-Path $ShortcutPath) {
        Write-Host "✅ Shortcut verified: $ShortcutPath" -ForegroundColor Green
    } else {
        Write-Host "❌ Shortcut creation failed" -ForegroundColor Red
    }

} catch {
    Write-Host "❌ Error setting up autorun: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Manual setup required:" -ForegroundColor Yellow
    Write-Host "1. Copy start_windows_autorun.bat to Startup folder" -ForegroundColor Yellow
    Write-Host "2. Or create scheduled task for autorun" -ForegroundColor Yellow
}

Write-Host "`n=== Autorun Setup Complete ===" -ForegroundColor Green