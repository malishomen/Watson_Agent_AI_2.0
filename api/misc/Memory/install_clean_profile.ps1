# Установка чистого профиля PowerShell
$profilePath = "$env:USERPROFILE\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"

# Создаем директорию если не существует
$profileDir = Split-Path $profilePath -Parent
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

# Создаем резервную копию существующего профиля
if (Test-Path $profilePath) {
    Copy-Item $profilePath "$profilePath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Force
    Write-Host "Создана резервная копия: $profilePath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')" -ForegroundColor Yellow
}

# Устанавливаем чистый профиль
$cleanProfile = @'
# === AI-Agent Clean UTF-8 Profile ===

# Включаем UTF-8 для консоли и Python
chcp 65001 | Out-Null
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8       = '1'

# Чистая функция prompt (без кириллицы, без скрытых символов)
function prompt { "PS " + (Get-Location) + "> " }
'@

Set-Content -Path $profilePath -Value $cleanProfile -Encoding UTF8 -Force

Write-Host "✅ Чистый профиль PowerShell установлен: $profilePath" -ForegroundColor Green
Write-Host "ℹ️ Откройте НОВУЮ вкладку терминала PowerShell для применения изменений" -ForegroundColor Yellow

