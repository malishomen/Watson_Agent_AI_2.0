# scripts/fix_cyrillic_commands.ps1
# Скрипт для проверки и исправления кириллических символов в командах

param(
    [string]$Command = ""
)

function Test-CommandForCyrillic {
    param([string]$cmd)
    
    # Проверяем наличие кириллических символов по Unicode кодам
    $cyrillicChars = @()
    for ($i = 0; $i -lt $cmd.Length; $i++) {
        $char = $cmd[$i]
        $unicode = [int]$char
        # Кириллические символы находятся в диапазоне 0x0400-0x04FF
        if ($unicode -ge 0x0400 -and $unicode -le 0x04FF) {
            $cyrillicChars += $char
        }
    }
    
    if ($cyrillicChars.Count -gt 0) {
        Write-Host "❌ ОБНАРУЖЕНЫ КИРИЛЛИЧЕСКИЕ СИМВОЛЫ в команде!" -ForegroundColor Red
        Write-Host "Найденные символы: $($cyrillicChars -join ', ')" -ForegroundColor Yellow
        Write-Host "Исходная команда: $cmd" -ForegroundColor Yellow
        
        # Заменяем кириллические символы на латинские
        $fixed_cmd = $cmd
        $replacements = @{
            'с' = 'c'  # Кириллический с -> латинский c
            'а' = 'a'  # Кириллический а -> латинский a
            'е' = 'e'  # Кириллический е -> латинский e
            'о' = 'o'  # Кириллический о -> латинский o
            'р' = 'p'  # Кириллический р -> латинский p
            'х' = 'x'  # Кириллический х -> латинский x
        }
        
        foreach ($cyrillic in $replacements.Keys) {
            $fixed_cmd = $fixed_cmd -replace $cyrillic, $replacements[$cyrillic]
        }
        
        Write-Host "Исправленная команда: $fixed_cmd" -ForegroundColor Green
        return $fixed_cmd
    } else {
        Write-Host "✅ Команда содержит только латинские символы" -ForegroundColor Green
        return $cmd
    }
}

function Show-CyrillicWarning {
    Write-Host "=== ПРЕДУПРЕЖДЕНИЕ О КИРИЛЛИЧЕСКИХ СИМВОЛАХ ===" -ForegroundColor Red
    Write-Host "Кириллический символ 'с' (U+0441) ЗАПРЕЩЕН в командах PowerShell!" -ForegroundColor Yellow
    Write-Host "Используйте только латинский символ 'c' (U+0063)" -ForegroundColor Yellow
    Write-Host "===============================================" -ForegroundColor Red
}

# Показать предупреждение
Show-CyrillicWarning

# Если передана команда для проверки
if ($Command) {
    Write-Host "Проверяем команду: $Command" -ForegroundColor Cyan
    $fixed = Test-CommandForCyrillic -cmd $Command
    
    if ($fixed -ne $Command) {
        Write-Host "Хотите выполнить исправленную команду? (y/n)" -ForegroundColor Yellow
        $response = Read-Host
        if ($response -eq "y" -or $response -eq "Y") {
            Write-Host "Выполняем исправленную команду..." -ForegroundColor Green
            Invoke-Expression $fixed
        }
    }
} else {
    Write-Host "Примеры правильного использования:" -ForegroundColor Cyan
    Write-Host "✅ .\scripts\start_fastapi.ps1" -ForegroundColor Green
    Write-Host "✅ cd .." -ForegroundColor Green
    Write-Host "✅ Invoke-RestMethod" -ForegroundColor Green
    Write-Host ""
    Write-Host "❌ с.\scripts\start_fastapi.ps1" -ForegroundColor Red
    Write-Host "❌ сd .." -ForegroundColor Red
    Write-Host "❌ Invoke-RestMethod (с кириллическим с)" -ForegroundColor Red
}
