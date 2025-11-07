<#
.SYNOPSIS
    Активирует режим "Ленивый Босс" для Cursor AI
    
.DESCRIPTION
    Открывает файл с детальными инструкциями для Cursor AI,
    который должен самостоятельно починить OpenAI интеграцию.
    
.EXAMPLE
    .\START_CURSOR_BOSS_MODE.ps1
#>

$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   🤖 CURSOR BOSS MODE ACTIVATED! 🤖   " -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$taskFile = "CURSOR_TASK_OPENAI_FIX.md"

if (-not (Test-Path $taskFile)) {
    Write-Host "❌ Файл не найден: $taskFile" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Задача для Cursor AI:" -ForegroundColor Yellow
Write-Host "   Починить OpenAI интеграцию" -ForegroundColor White
Write-Host ""
Write-Host "📄 Файл с инструкциями:" -ForegroundColor Yellow
Write-Host "   $taskFile" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Что делать дальше:" -ForegroundColor Yellow
Write-Host "   1. Открой файл $taskFile" -ForegroundColor White
Write-Host "   2. Прочитай ГЛОБАЛЬНУЮ ЗАДАЧУ" -ForegroundColor White
Write-Host "   3. Выдели весь текст (Ctrl+A)" -ForegroundColor White
Write-Host "   4. Отправь в Cursor Chat или создай Task" -ForegroundColor White
Write-Host "   5. Скажи Cursor: 'Выполняй все шаги до победного!'" -ForegroundColor White
Write-Host ""
Write-Host "💡 Или используй Cursor Task:" -ForegroundColor Yellow
Write-Host "   Ctrl+Shift+P → Tasks: Run Task" -ForegroundColor White
Write-Host "   → Выбери: '🤖 AUTO-FIX: OpenAI Integration'" -ForegroundColor White
Write-Host ""

# Открываем файл в Cursor/VS Code
try {
    Write-Host "🚀 Открываю файл в редакторе..." -ForegroundColor Green
    & code $taskFile
    Start-Sleep -Seconds 1
    
    Write-Host ""
    Write-Host "✅ Готово! Теперь делегируй работу Cursor AI! 😎" -ForegroundColor Green
    Write-Host ""
    Write-Host "💬 Пример команды для Cursor Chat:" -ForegroundColor Cyan
    Write-Host "   'Выполни все шаги из CURSOR_TASK_OPENAI_FIX.md'" -ForegroundColor White
    Write-Host "   'Не останавливайся, пока всё не заработает!'" -ForegroundColor White
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "   'Ум того, кто умеет правильно поручать' 😄" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "⚠️ Не удалось открыть редактор автоматически" -ForegroundColor Yellow
    Write-Host "Открой файл вручную: $taskFile" -ForegroundColor White
    Write-Host ""
}

# Опционально: показать краткую справку по API
Write-Host "📊 Быстрая проверка текущего статуса:" -ForegroundColor Yellow
Write-Host ""

try {
    $health = Invoke-RestMethod -Uri "$env:WATSON_API_BASE/health" -TimeoutSec 3 -ErrorAction SilentlyContinue
    Write-Host "   ✅ Watson API: Работает" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Watson API: Не отвечает" -ForegroundColor Yellow
    Write-Host "      Запусти: .\scripts\Start-WatsonApi.ps1 -Port 8090" -ForegroundColor Gray
}

try {
    $openai = Invoke-RestMethod -Uri "$env:WATSON_API_BASE/health/openai" -TimeoutSec 5 -ErrorAction SilentlyContinue
    Write-Host "   ✅ OpenAI: $($openai.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ OpenAI: Не настроен (это и надо починить!)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Давай, делегируй! Cursor сделает всё сам! 🚀" -ForegroundColor Cyan
Write-Host ""

