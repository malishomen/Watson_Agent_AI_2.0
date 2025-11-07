# ===== apply_patch.ps1 =====
# Run:
#   cd D:\AI-Agent\Memory
#   powershell -ExecutionPolicy Bypass -File .\apply_patch.ps1

$ErrorActionPreference = "Stop"
Write-Host '==> Watson patch: start' -ForegroundColor Cyan
Set-Location "D:\AI-Agent\Memory"

# 0) Prepare .env and .gitignore
if (-not (Test-Path ".gitignore")) { New-Item -ItemType File -Path ".gitignore" -Force | Out-Null }
if (-not (Select-String -Path ".gitignore" -Pattern '^\s*\.env\s*$' -Quiet)) { Add-Content ".gitignore" ".env" }

# If BOT_TOKEN exists in environment, ensure .env
$envToken = [Environment]::GetEnvironmentVariable("BOT_TOKEN","User")
if (-not (Test-Path ".env") -and $envToken) {
  "BOT_TOKEN=$envToken" | Out-File -Encoding UTF8 ".env"
  Write-Host '  OK: .env created from user environment' -ForegroundColor Green
} elseif (-not (Test-Path ".env")) {
  # Placeholder to avoid crash
  "BOT_TOKEN=" | Out-File -Encoding UTF8 ".env"
  Write-Host '  INFO: .env created (BOT_TOKEN is empty)' -ForegroundColor Yellow
}

# 1) BOT_TOKEN check (env or .env)
function Get-EnvOrDotEnvToken {
  $tok = $env:BOT_TOKEN
  if (-not $tok) {
    if (Test-Path ".env") {
      $line = Get-Content ".env" -Raw | Select-String -Pattern "(?m)^\s*BOT_TOKEN=(.*)$"
      if ($line) { $tok = $line.Matches.Groups[1].Value.Trim() }
    }
  }
  return $tok
}

$BOT = Get-EnvOrDotEnvToken
if ($BOT) {
  Write-Host "  INFO: BOT_TOKEN found (len: $($BOT.Length)) - checking via Telegram..." -ForegroundColor DarkCyan
  try {
    $me = Invoke-RestMethod -Uri "https://api.telegram.org/bot$BOT/getMe" -TimeoutSec 10
    if ($me.ok) {
      Write-Host "  OK: Telegram OK: @$($me.result.username) (id: $($me.result.id))" -ForegroundColor Green
    } else {
      Write-Host ("  WARN: Telegram not ok: {0}" -f ($me | ConvertTo-Json -Depth 4)) -ForegroundColor Yellow
    }
  } catch {
    Write-Host ("  WARN: Token check failed: {0}" -f $_.Exception.Message) -ForegroundColor Yellow
  }
} else {
  Write-Host '  WARN: BOT_TOKEN not found in env or .env - Telegram test will be SKIP' -ForegroundColor Yellow
}

# 2) Backup tests if exist
$targets = @("test_bot.py","test_bot_token.py","test_telegram_encoding.py")
foreach ($f in $targets) {
  if (Test-Path $f -PathType Leaf) { Copy-Item $f "$f.bak" -Force }
}

# 3) Replace return ... with assert (...)
function Convert-ReturnsToAsserts {
  param([string]$Path)
  if (-not (Test-Path $Path)) { return }
  $lines = Get-Content $Path
  $out = @()
  foreach ($ln in $lines) {
    if ($ln -match '^[ \t]*return[ \t]+(.+)$') {
      $expr = $Matches[1]
      $out += ("    assert ({0})" -f $expr)
    } else {
      $out += $ln
    }
  }
  $out | Set-Content -Encoding UTF8 $Path
  Write-Host "  OK: ${Path}: return->assert" -ForegroundColor Green
}
foreach ($f in $targets) { Convert-ReturnsToAsserts $f }

# 4) conftest.py: dotenv + stdout/stderr safeguard
$conftest = @"
import sys
import os
import pytest
from dotenv import load_dotenv

# === .env autoload ===
load_dotenv()

# === stdout safeguard (Windows/pytest) ===
def pytest_sessionstart(session):
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

def pytest_configure(config):
    tr = config.pluginmanager.getplugin("terminalreporter")
    if tr and hasattr(tr, "_tw") and hasattr(tr._tw, "_file"):
        tr._tw._file = sys.__stdout__

# === soft warning if no BOT_TOKEN ===
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    if not os.getenv("BOT_TOKEN"):
        item.warn(pytest.PytestWarning("BOT_TOKEN not set. Telegram tests may be skipped."))
"@
Set-Content -Path "conftest.py" -Value $conftest -Encoding UTF8
Write-Host '  OK: conftest.py updated' -ForegroundColor Green

# 5) Telegram smoke test
New-Item -ItemType Directory -Force -Path ".\tests" | Out-Null
$smoke = @"
import os
import pytest
import requests

@pytest.mark.skipif(not os.getenv("BOT_TOKEN"), reason="BOT_TOKEN not set")
def test_telegram_getme_smoke():
    token = os.getenv("BOT_TOKEN")
    r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    assert r.status_code == 200, f"HTTP {r.status_code}"
    data = r.json()
    assert data.get("ok") is True, f"Telegram returned not ok: {data}"
    assert "result" in data and "username" in data["result"], f"No username in {data}"
"@
Set-Content -Path ".\tests\test_telegram_smoke.py" -Value $smoke -Encoding UTF8
Write-Host '  OK: tests\test_telegram_smoke.py created/updated' -ForegroundColor Green

# 6) Cursor PATH hint
$cursorPathGuess = "$env:LOCALAPPDATA\Programs\cursor\bin\cursor.exe"
if (-not (Test-Path $cursorPathGuess)) {
  Write-Host '  INFO: Cursor not found at default path. Add cursor.exe folder to PATH' -ForegroundColor Yellow
  Write-Host '    Example: setx PATH "%PATH%;C:\Users\user\AppData\Local\Programs\cursor\bin"' -ForegroundColor Yellow
} else {
  Write-Host "  OK: Cursor found: $cursorPathGuess (if still SKIP - restart Cursor)" -ForegroundColor Green
}

Write-Host '==> Done. Run:  cd D:\AI-Agent\Memory; py -3.11 -m pytest -q' -ForegroundColor Cyan
# ===== /apply_patch.ps1 =====
