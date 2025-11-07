# safe_python.ps1 - Безопасный запуск Python с проверкой кириллических символов
param(
    [string]$Command = "",
    [string]$Args = ""
)

# Проверяем на кириллические символы в команде
if ($Command -match "[а-яё]") {
    Write-Host "ОШИБКА: Обнаружены кириллические символы в команде!" -ForegroundColor Red
    Write-Host "Команда: $Command" -ForegroundColor Yellow
    Write-Host "Исправьте на латинские символы и попробуйте снова." -ForegroundColor Yellow
    exit 1
}

# Безопасные команды Python
$python_commands = @{
    "python" = "py -3.11"
    "python3" = "py -3.11" 
    "py" = "py -3.11"
}

# Нормализуем команду
$normalized_cmd = $Command.ToLower()
if ($python_commands.ContainsKey($normalized_cmd)) {
    $cmd = $python_commands[$normalized_cmd]
    Write-Host "Выполняю: $cmd $Args" -ForegroundColor Green
    & $cmd $Args
} else {
    Write-Host "Неизвестная команда: $Command" -ForegroundColor Red
    exit 1
}
