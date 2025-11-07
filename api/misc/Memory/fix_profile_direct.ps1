# Direct profile fix without PowerShell commands
# This script creates the profile file directly

$profilePath = "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
$profileContent = @'
# === AI-Agent UTF-8 & Prompt ===

# Включаем кодировку UTF-8
chcp 65001 | Out-Null
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'

# Чистый prompt без кириллицы
function prompt { 'PS ' + $(Get-Location) + '> ' }
'@

# Create directory if it doesn't exist
$profileDir = Split-Path $profilePath -Parent
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force
}

# Write file with UTF-8 without BOM
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($profilePath, $profileContent, $Utf8NoBom)

Write-Host "Profile fixed at: $profilePath" -ForegroundColor Green
Write-Host "Please restart PowerShell to apply changes." -ForegroundColor Yellow

