# === AI-Agent Clean UTF-8 Profile ===

# Включаем UTF-8 для консоли и Python
chcp 65001 | Out-Null
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8       = '1'

# Чистая функция prompt (без кириллицы, без скрытых символов)
function prompt { "PS " + (Get-Location) + "> " }

