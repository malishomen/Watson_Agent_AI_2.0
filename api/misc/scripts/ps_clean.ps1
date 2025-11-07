# Чистая UTF-8 среда, без профилей
$ErrorActionPreference = 'Stop'

# Глобальная кодировка
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

# Чистый prompt
function prompt { 'PS ' + $(Get-Location) + '> ' }
