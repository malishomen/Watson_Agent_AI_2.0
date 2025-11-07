param(
  [string]$Secret = $env:AGENT_HTTP_SHARED_SECRET,
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8088
)
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"
if (-not $Secret) { Write-Error "AGENT_HTTP_SHARED_SECRET is empty"; exit 1 }
cd D:\AI-Agent
$env:AGENT_HTTP_SHARED_SECRET = $Secret
D:\AI-Agent\venv\Scripts\Activate.ps1
uvicorn api.agent:app --host $HostAddress --port $Port --http h11 --loop asyncio --workers 1 --no-access-log --log-level info
