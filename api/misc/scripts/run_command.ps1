# run_command.ps1 - Удобный скрипт для отправки команд агенту
param(
    [string]$Text = "",
    [string]$Session = "Telegram"
)

# Настройка UTF-8
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

# Проверка секрета
if (-not $env:AGENT_HTTP_SHARED_SECRET) {
    Write-Host "Ошибка: AGENT_HTTP_SHARED_SECRET не установлен" -ForegroundColor Red
    exit 1
}

# Отправка команды
$h = @{ "x-agent-secret" = $env:AGENT_HTTP_SHARED_SECRET }
$body = @{ text = $Text; session = $Session } | ConvertTo-Json -Depth 4 -Compress

try {
    $result = Invoke-RestMethod -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'
    
    if ($result.ok) {
        Write-Host "✅ Команда выполнена:" -ForegroundColor Green
        Write-Host "Нормализовано: $($result.normalized)" -ForegroundColor Cyan
        Write-Host "Результат: $($result.result)" -ForegroundColor White
    } else {
        Write-Host "❌ Ошибка: $($result.result)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Ошибка соединения: $($_.Exception.Message)" -ForegroundColor Red
}
