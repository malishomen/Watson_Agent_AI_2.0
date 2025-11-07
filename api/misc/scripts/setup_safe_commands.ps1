# scripts/setup_safe_commands.ps1
# Setup safe command aliases to prevent Cyrillic character issues

Write-Host "Setting up safe command aliases..." -ForegroundColor Cyan

# Create a safe execution function
function Safe-Execute {
    param([string]$Command)
    
    # Check for Cyrillic characters
    $hasCyrillic = $false
    for ($i = 0; $i -lt $Command.Length; $i++) {
        $char = $Command[$i]
        $unicode = [int]$char
        if ($unicode -ge 0x0400 -and $unicode -le 0x04FF) {
            $hasCyrillic = $true
            break
        }
    }
    
    if ($hasCyrillic) {
        Write-Host "WARNING: Cyrillic characters detected in command!" -ForegroundColor Yellow
        Write-Host "Original: $Command" -ForegroundColor Red
        
        # Fix most common Cyrillic characters
        $fixed = $Command
        $fixed = $fixed -replace [char]0x0441, [char]0x0063  # с -> c
        $fixed = $fixed -replace [char]0x0430, [char]0x0061  # а -> a
        $fixed = $fixed -replace [char]0x0435, [char]0x0065  # е -> e
        $fixed = $fixed -replace [char]0x043E, [char]0x006F  # о -> o
        $fixed = $fixed -replace [char]0x0440, [char]0x0070  # р -> p
        $fixed = $fixed -replace [char]0x0445, [char]0x0078  # х -> x
        
        Write-Host "Fixed: $fixed" -ForegroundColor Green
        Write-Host "Executing fixed command..." -ForegroundColor Cyan
        
        try {
            Invoke-Expression $fixed
            Write-Host "SUCCESS: Command executed!" -ForegroundColor Green
        } catch {
            Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        # Execute normally
        try {
            Invoke-Expression $Command
        } catch {
            Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Create aliases for common commands
Set-Alias -Name "scd" -Value "Set-Location"
Set-Alias -Name "sdir" -Value "Get-ChildItem"

Write-Host "Safe aliases created:" -ForegroundColor Green
Write-Host "  scd    - Safe cd command" -ForegroundColor White
Write-Host "  sdir   - Safe dir command" -ForegroundColor White
Write-Host ""
Write-Host "Usage examples:" -ForegroundColor Cyan
Write-Host "  Safe-Execute 'cd ..'" -ForegroundColor White
Write-Host "  Safe-Execute '.\scripts\start_fastapi.ps1'" -ForegroundColor White
Write-Host ""
Write-Host "Setup completed!" -ForegroundColor Green
