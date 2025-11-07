$token   = "7073794782:AAF3M5W0mGhh3cFkWPUo0PGObVmQAka1ofk"
$chat_id = "73332538"


[Environment]::SetEnvironmentVariable("TELEGRAM_TOKEN", $token, "User")
[Environment]::SetEnvironmentVariable("TELEGRAM_CHAT_ID", $chat_id, "User")

Write-Host "✅ Telegram token и chat_id сохранены как постоянные переменные окружения."
