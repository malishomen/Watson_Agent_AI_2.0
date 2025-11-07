# scripts/fix_and_test_cyrillic.ps1
# Автоматическое исправление и тестирование кириллических символов

param(
    [string]$Path = ".",
    [switch]$Test = $false,
    [switch]$Fix = $true
)

Write-Host "=== Автоматическое исправление и тестирование кириллических символов ===" -ForegroundColor Cyan

# 1. Проверка текущего состояния
Write-Host "1. Проверка текущего состояния..." -ForegroundColor Yellow
& "$PSScriptRoot\detect_cyrillic_commands.ps1" -Path $Path

# 2. Автоматическое исправление
if ($Fix) {
    Write-Host "`n2. Автоматическое исправление..." -ForegroundColor Yellow
    & "$PSScriptRoot\detect_cyrillic_commands.ps1" -Path $Path -Fix
}

# 3. Тестирование исправлений
if ($Test) {
    Write-Host "`n3. Тестирование исправлений..." -ForegroundColor Yellow
    
    # Создаем тестовые файлы с проблемными командами
    $testFiles = @(
        @{
            Path = "test_cyrillic_commands.ps1"
            Content = @"
# Тестовый файл с кириллическими символами
Write-Host "Тест кириллических символов"
сpy --version
сpython --version
сpip --version
сpytest --version
"@
        }
    )
    
    foreach ($testFile in $testFiles) {
        Set-Content -Path $testFile.Path -Value $testFile.Content -Encoding UTF8
        Write-Host "   Создан тестовый файл: $($testFile.Path)" -ForegroundColor Green
    }
    
    # Проверяем тестовые файлы
    Write-Host "`n   Проверка тестовых файлов..." -ForegroundColor Yellow
    & "$PSScriptRoot\detect_cyrillic_commands.ps1" -Path "." -Fix
    
    # Удаляем тестовые файлы
    foreach ($testFile in $testFiles) {
        if (Test-Path $testFile.Path) {
            Remove-Item $testFile.Path -Force
            Write-Host "   Удален тестовый файл: $($testFile.Path)" -ForegroundColor Green
        }
    }
}

# 4. Финальная проверка
Write-Host "`n4. Финальная проверка..." -ForegroundColor Yellow
& "$PSScriptRoot\detect_cyrillic_commands.ps1" -Path $Path

# 5. Рекомендации
Write-Host "`n=== Рекомендации для предотвращения проблемы ===" -ForegroundColor Cyan
Write-Host "1. Установите систему предотвращения:" -ForegroundColor White
Write-Host "   .\scripts\prevent_cyrillic_commands.ps1 -Install" -ForegroundColor Yellow
Write-Host "`n2. Настройте IDE для отображения невидимых символов" -ForegroundColor White
Write-Host "3. Используйте UTF-8 кодировку без BOM для всех файлов" -ForegroundColor White
Write-Host "4. Регулярно запускайте проверку:" -ForegroundColor White
Write-Host "   .\scripts\detect_cyrillic_commands.ps1" -ForegroundColor Yellow

Write-Host "`n✅ Процесс завершен!" -ForegroundColor Green
