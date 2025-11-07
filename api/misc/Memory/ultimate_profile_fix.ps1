# === Ultimate PowerShell Profile Fix ===
# This script completely fixes PowerShell profile issues

Write-Host "=== Ultimate PowerShell Profile Fix ===" -ForegroundColor Cyan
Write-Host "Starting comprehensive profile cleanup..." -ForegroundColor Yellow

# Get profile path
$profilePath = "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
Write-Host "Profile path: $profilePath" -ForegroundColor Gray

# Create directory if it doesn't exist
$profileDir = Split-Path $profilePath -Parent
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    Write-Host "Created profile directory: $profileDir" -ForegroundColor Green
}

# Backup existing profile
if (Test-Path $profilePath) {
    $backupPath = "$profilePath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item $profilePath $backupPath -Force
    Write-Host "Backed up existing profile to: $backupPath" -ForegroundColor Green
}

# Create clean profile content
$cleanProfile = @'
# === AI-Agent UTF-8 & Prompt ===
# This profile is protected against Cyrillic issues

# Set UTF-8 encoding
chcp 65001 | Out-Null
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)

# Python UTF-8 environment
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

# Clean prompt function without Cyrillic
function prompt { 
    'PS ' + $(Get-Location) + '> ' 
}

# Remove any existing problematic functions
Remove-Item Function:\prompt -ErrorAction SilentlyContinue
function prompt { 'PS ' + $(Get-Location) + '> ' }
'@

# Write clean profile with UTF-8 without BOM
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($profilePath, $cleanProfile, $Utf8NoBom)

Write-Host "Clean profile written to: $profilePath" -ForegroundColor Green

# Test the profile
Write-Host "Testing profile..." -ForegroundColor Yellow
try {
    # Source the profile
    . $profilePath
    Write-Host "Profile loaded successfully!" -ForegroundColor Green
    
    # Test prompt function
    $promptDef = (Get-Command prompt -CommandType Function).Definition
    Write-Host "Current prompt definition:" -ForegroundColor Cyan
    Write-Host $promptDef -ForegroundColor White
    
    # Test basic commands
    Write-Host "Testing basic commands..." -ForegroundColor Yellow
    Get-Location | Out-Null
    Write-Host "Get-Location: OK" -ForegroundColor Green
    
} catch {
    Write-Host "Error testing profile: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "=== Profile Fix Complete ===" -ForegroundColor Cyan
Write-Host "Please restart PowerShell to ensure all changes take effect." -ForegroundColor Yellow
Write-Host "All Cursor tasks use -NoProfile flag for protection." -ForegroundColor Green

