# scripts/cyrillic_fixer.ps1
# Cyrillic character fixer for PowerShell commands

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

function Convert-CyrillicToLatin {
    param([string]$text)
    
    # Use Unicode escape sequences to avoid encoding issues
    $cyrillic_c = [char]0x0441  # Cyrillic small letter es
    $latin_c = [char]0x0063     # Latin small letter c
    
    $cyrillic_a = [char]0x0430  # Cyrillic small letter a
    $latin_a = [char]0x0061     # Latin small letter a
    
    $cyrillic_e = [char]0x0435  # Cyrillic small letter e
    $latin_e = [char]0x0065     # Latin small letter e
    
    $cyrillic_o = [char]0x043E  # Cyrillic small letter o
    $latin_o = [char]0x006F     # Latin small letter o
    
    $cyrillic_p = [char]0x0440  # Cyrillic small letter er
    $latin_p = [char]0x0070     # Latin small letter p
    
    $cyrillic_x = [char]0x0445  # Cyrillic small letter ha
    $latin_x = [char]0x0078     # Latin small letter x
    
    $result = $text
    $result = $result -replace $cyrillic_c, $latin_c
    $result = $result -replace $cyrillic_a, $latin_a
    $result = $result -replace $cyrillic_e, $latin_e
    $result = $result -replace $cyrillic_o, $latin_o
    $result = $result -replace $cyrillic_p, $latin_p
    $result = $result -replace $cyrillic_x, $latin_x
    
    return $result
}

function Test-ForCyrillicChars {
    param([string]$text)
    
    for ($i = 0; $i -lt $text.Length; $i++) {
        $char = $text[$i]
        $unicode = [int]$char
        # Cyrillic range: 0x0400-0x04FF
        if ($unicode -ge 0x0400 -and $unicode -le 0x04FF) {
            return $true
        }
    }
    return $false
}

# Main logic
if (Test-ForCyrillicChars -text $Command) {
    Write-Host "WARNING: Cyrillic characters detected!" -ForegroundColor Yellow
    Write-Host "Original: $Command" -ForegroundColor Red
    
    $fixedCommand = Convert-CyrillicToLatin -text $Command
    Write-Host "Fixed: $fixedCommand" -ForegroundColor Green
    
    Write-Host "Executing fixed command..." -ForegroundColor Cyan
    try {
        Invoke-Expression $fixedCommand
        Write-Host "SUCCESS!" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "OK: Only Latin characters found" -ForegroundColor Green
    try {
        Invoke-Expression $Command
        Write-Host "SUCCESS!" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}
