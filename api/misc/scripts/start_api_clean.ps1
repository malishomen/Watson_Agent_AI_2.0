param(
  [string]$Secret = $env:AI_AGENT_HTTP_SECRET,
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8088
)

. "$PSScriptRoot\ps_clean.ps1"

if (-not $Secret) { throw "AI_AGENT_HTTP_SECRET не задан" }
$env:AGENT_HTTP_SHARED_SECRET = $Secret

Set-Location "D:\AI-Agent"
python -m uvicorn api.fastapi_agent_fixed:app `
  --host $HostAddress --port $Port --http h11 --loop asyncio --workers 1 `
  --no-access-log --log-level info
