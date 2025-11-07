# scripts/safe_command_executor_simple.ps1
# Safe command executor with automatic Cyrillic to Latin conversion

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

function Convert-CyrillicToLatin {
    param([string]$text)
    
    # Basic Cyrillic to Latin replacements (most common)
    $replacements = @{
        'а' = 'a'
        'с' = 'c' 
        'е' = 'e'
        'о' = 'o'
        'р' = 'p'
        'х' = 'x'
        'у' = 'u'
        'к' = 'k'
        'н' = 'n'
        'м' = 'm'
        'т' = 't'
        'и' = 'i'
        'в' = 'v'
        'д' = 'd'
        'л' = 'l'
        'б' = 'b'
        'з' = 'z'
        'г' = 'g'
        'п' = 'p'
        'ф' = 'f'
        'ц' = 'ts'
        'ч' = 'ch'
        'ш' = 'sh'
        'щ' = 'sch'
        'ж' = 'zh'
        'э' = 'e'
        'ю' = 'yu'
        'я' = 'ya'
        'й' = 'y'
        'ы' = 'y'
        'ъ' = ''
        'ь' = ''
    }
    
    $result = $text
    foreach ($cyrillic in $replacements.Keys) {
        $result = $result -replace $cyrillic, $replacements[$cyrillic]
    }
    
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

# Check for Cyrillic characters
if (Test-ForCyrillicChars -text $Command) {
    Write-Host "WARNING: Cyrillic characters detected!" -ForegroundColor Yellow
    Write-Host "Original command: $Command" -ForegroundColor Red
    
    $fixedCommand = Convert-CyrillicToLatin -text $Command
    Write-Host "Fixed command: $fixedCommand" -ForegroundColor Green
    Write-Host "Executing fixed command..." -ForegroundColor Cyan
    
    try {
        Invoke-Expression $fixedCommand
        Write-Host "SUCCESS: Command executed!" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "OK: Command contains only Latin characters" -ForegroundColor Green
    try {
        Invoke-Expression $Command
        Write-Host "SUCCESS: Command executed!" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}
