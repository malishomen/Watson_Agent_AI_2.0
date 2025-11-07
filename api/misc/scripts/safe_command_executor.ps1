# scripts/safe_command_executor.ps1
# Безопасный исполнитель команд с автоматическим исправлением кириллических символов

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

function Convert-CyrillicToLatin {
    param([string]$text)
    
    # Словарь замен кириллических символов на латинские
    $replacements = @{
        'а' = 'a'  # U+0430 -> U+0061
        'б' = 'b'  # U+0431 -> U+0062  
        'в' = 'v'  # U+0432 -> U+0076
        'г' = 'g'  # U+0433 -> U+0067
        'д' = 'd'  # U+0434 -> U+0064
        'е' = 'e'  # U+0435 -> U+0065
        'ж' = 'zh' # U+0436 -> zh
        'з' = 'z'  # U+0437 -> U+007A
        'и' = 'i'  # U+0438 -> U+0069
        'й' = 'y'  # U+0439 -> U+0079
        'к' = 'k'  # U+043A -> U+006B
        'л' = 'l'  # U+043B -> U+006C
        'м' = 'm'  # U+043C -> U+006D
        'н' = 'n'  # U+043D -> U+006E
        'о' = 'o'  # U+043E -> U+006F
        'п' = 'p'  # U+043F -> U+0070
        'р' = 'r'  # U+0440 -> U+0072
        'с' = 'c'  # U+0441 -> U+0063
        'т' = 't'  # U+0442 -> U+0074
        'у' = 'u'  # U+0443 -> U+0075
        'ф' = 'f'  # U+0444 -> U+0066
        'х' = 'x'  # U+0445 -> U+0078
        'ц' = 'ts' # U+0446 -> ts
        'ч' = 'ch' # U+0447 -> ch
        'ш' = 'sh' # U+0448 -> sh
        'щ' = 'sch'# U+0449 -> sch
        'ъ' = ''   # U+044A -> (удаляем)
        'ы' = 'y'  # U+044B -> U+0079
        'ь' = ''   # U+044C -> (удаляем)
        'э' = 'e'  # U+044D -> U+0065
        'ю' = 'yu' # U+044E -> yu
        'я' = 'ya' # U+044F -> ya
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
        # Кириллические символы находятся в диапазоне 0x0400-0x04FF
        if ($unicode -ge 0x0400 -and $unicode -le 0x04FF) {
            return $true
        }
    }
    return $false
}

# Проверяем команду на кириллические символы
if (Test-ForCyrillicChars -text $Command) {
    Write-Host "⚠️  ОБНАРУЖЕНЫ КИРИЛЛИЧЕСКИЕ СИМВОЛЫ!" -ForegroundColor Yellow
    Write-Host "Исходная команда: $Command" -ForegroundColor Red
    
    $fixedCommand = Convert-CyrillicToLatin -text $Command
    Write-Host "Исправленная команда: $fixedCommand" -ForegroundColor Green
    Write-Host "Выполняем исправленную команду..." -ForegroundColor Cyan
    
    try {
        Invoke-Expression $fixedCommand
        Write-Host "✅ Команда выполнена успешно!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ошибка выполнения команды: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Команда содержит только латинские символы" -ForegroundColor Green
    try {
        Invoke-Expression $Command
        Write-Host "✅ Команда выполнена успешно!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ошибка выполнения команды: $($_.Exception.Message)" -ForegroundColor Red
    }
}
