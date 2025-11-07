. "$PSScriptRoot\ps_clean.ps1"

if (-not $env:TG_BOT_TOKEN) { throw "TG_BOT_TOKEN не задан" }
Set-Location "D:\AI-Agent"

# запуск в строгом UTF-8
python -X utf8 telegram_bot.py
