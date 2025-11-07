# === RADICAL POWERSHELL FIX ===
# This script completely eliminates Cyrillic issues

Write-Host "=== RADICAL POWERSHELL FIX ===" -ForegroundColor Red
Write-Host "Starting radical cleanup..." -ForegroundColor Yellow

# 1. Kill all PowerShell processes
Write-Host "Stopping all PowerShell processes..." -ForegroundColor Yellow
Get-Process powershell -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Remove ALL profile files
$profilePaths = @(
    "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1",
    "$env:USERPROFILE\Documents\PowerShell\Microsoft.PowerShell_profile.ps1",
    "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.VSCode_profile.ps1",
    "$env:USERPROFILE\Documents\PowerShell\Microsoft.VSCode_profile.ps1"
)

foreach ($path in $profilePaths) {
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "Removed: $path" -ForegroundColor Green
    }
}

# 3. Create completely clean profile
$cleanProfile = @'
# === CLEAN POWERSHELL PROFILE ===
# No Cyrillic, no problems

# Set UTF-8
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# Environment
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

# Simple prompt
function prompt { "PS $($PWD.Path)> " }
'@

# 4. Write clean profile
$profileDir = "$env:USERPROFILE\Documents\WindowsPowerShell"
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText("$profileDir\Microsoft.PowerShell_profile.ps1", $cleanProfile, $Utf8NoBom)

Write-Host "Clean profile created!" -ForegroundColor Green

# 5. Reset console
Write-Host "Resetting console..." -ForegroundColor Yellow
[Console]::Clear()
[Console]::ResetColor()

Write-Host "=== RADICAL FIX COMPLETE ===" -ForegroundColor Green
Write-Host "Please restart PowerShell completely!" -ForegroundColor Red

