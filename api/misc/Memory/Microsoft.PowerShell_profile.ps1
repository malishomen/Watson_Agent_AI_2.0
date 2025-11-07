# === AI-Agent UTF-8 & Prompt ===

# Включаем кодировку UTF-8
chcp 65001 | Out-Null
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'

# Чистый prompt без кириллицы
function prompt { 'PS ' + $(Get-Location) + '> ' }

