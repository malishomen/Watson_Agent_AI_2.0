param(
  [int]$Port = 8090,
  [string]$ListenHost = "127.0.0.1"
)

$ErrorActionPreference = 'Stop'

function Stop-PortUsers([int]$p) {
  try {
    $conns = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
      if ($c.OwningProcess) {
        try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
      }
    }
  } catch {}
}

function Start-Uvicorn([string]$repo, [string]$bindHost, [int]$port) {
  $env:PYTHONPATH = $repo
  $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = 1
  $env:TELEGRAM_TOKEN = [Environment]::GetEnvironmentVariable('TELEGRAM_TOKEN','User')
  $env:TELEGRAM_CHAT_ID = [Environment]::GetEnvironmentVariable('TELEGRAM_CHAT_ID','User')
  
  # Cursor API integration
  $env:CURSOR_API_URL = [Environment]::GetEnvironmentVariable('CURSOR_API_URL','User')
  $env:CURSOR_API_KEY = [Environment]::GetEnvironmentVariable('CURSOR_API_KEY','User')
  $env:AGENT_HTTP_SHARED_SECRET = [Environment]::GetEnvironmentVariable('AGENT_HTTP_SHARED_SECRET','User')

  Push-Location $repo
  try {
    $outLog = Join-Path $repo ("uvicorn_${port}.out.log")
    $errLog = Join-Path $repo ("uvicorn_${port}.err.log")
    # Жёстко гасим старые процессы на порту
    Stop-PortUsers -p $port
    # Запускаем uvicorn в фоне
    Start-Process -WindowStyle Hidden -WorkingDirectory $repo -FilePath py -ArgumentList "-3.11","-m","uvicorn","--app-dir",".","api.fastapi_agent:app","--host",$bindHost,"--port",$port,"--log-level","info" -RedirectStandardOutput $outLog -RedirectStandardError $errLog
    return $outLog
  } finally {
    Pop-Location
  }
}

function Wait-Health([string]$url, [int]$retries = 30) {
  for ($i=0; $i -lt $retries; $i++) {
    try {
      $resp = Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 2
      if ($resp.StatusCode -eq 200) { return $true }
    } catch {}
    Start-Sleep -Milliseconds 300
  }
  return $false
}

$repo = (Resolve-Path (Join-Path $PSScriptRoot ".."))
$logPath = Start-Uvicorn -repo $repo -bindHost $ListenHost -port $Port

$ok = Wait-Health -url ("http://{0}:{1}/health" -f $ListenHost,$Port)
if (-not $ok) {
  Write-Output ("API did not respond on /health at http://{0}:{1}. See log: {2}" -f $ListenHost,$Port,$logPath)
  exit 2
}
Write-Output ("API is ready on http://{0}:{1} (log: {2})" -f $ListenHost,$Port,$logPath)

