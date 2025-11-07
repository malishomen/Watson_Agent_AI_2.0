# cursor\prompt_api_vars.ps1
param(
  [string]$DefaultUrl = "http://127.0.0.1:8088"
)

Write-Host "=== Настройка подключения к Agent API ===" -ForegroundColor Cyan

# URL (видно)
$apiUrl = Read-Host "Введите API URL (Enter для значения по умолчанию: $DefaultUrl)"
if ([string]::IsNullOrWhiteSpace($apiUrl)) { $apiUrl = $DefaultUrl }

# SECRET (скрытый ввод)
$sec = Read-Host -AsSecureString "Введите API SECRET (ввод скрыт)"
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
try {
  $apiSecret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}

# В эту сессию PowerShell (не навсегда)
$env:AGENT_API_URL = $apiUrl
$env:AGENT_API_SECRET = $apiSecret

Write-Host ("AGENT_API_URL = " + $env:AGENT_API_URL) -ForegroundColor Green
if ($env:AGENT_API_SECRET) {
  Write-Host ("AGENT_API_SECRET = " + $env:AGENT_API_SECRET.Substring(0,5) + "...") -ForegroundColor Green
} else {
  Write-Host "AGENT_API_SECRET не задан!" -ForegroundColor Red
  exit 1
}
