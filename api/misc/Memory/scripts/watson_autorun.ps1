param(
  [string]$ProjectPath = (Resolve-Path (Join-Path $PSScriptRoot "..")),
  [int]$HealthTimeoutSec = 5
)

[Console]::InputEncoding=[Text.UTF8Encoding]::UTF8
[Console]::OutputEncoding=[Text.UTF8Encoding]::UTF8
$ErrorActionPreference = "Stop"

function ok($m){Write-Host "✅ $m" -ForegroundColor Green}
function warn($m){Write-Host "⚠️  $m" -ForegroundColor Yellow}
function err($m){Write-Host "❌ $m" -ForegroundColor Red}

try {
  # 1) Kill only our API uvicorn processes (safe, targeted)
  $targets = Get-CimInstance Win32_Process |
    Where-Object { ($_.Name -match '^(python|uvicorn)(\.exe)?$') -and ($_.CommandLine -match 'uvicorn' -and $_.CommandLine -match 'api\.agent:app') }
  foreach ($p in $targets) {
    try { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
  }
  ok "Остановлены старые процессы uvicorn api.agent:app (если были)"

  # 2) Quarantine recent changes (24h)
  $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $quarantineRoot = Join-Path $ProjectPath ("_quarantine_" + $timestamp)
  New-Item -ItemType Directory -Force -Path $quarantineRoot | Out-Null

  $basePath = (Resolve-Path $ProjectPath).Path
  $cutoff = (Get-Date).AddDays(-1)

  Get-ChildItem -Recurse -Force -File $ProjectPath |
    Where-Object { $_.LastWriteTime -gt $cutoff -and $_.FullName -notmatch "\\logs\\" } |
    ForEach-Object {
      $relative = [System.IO.Path]::GetRelativePath($basePath, $_.FullName)
      $dest = Join-Path $quarantineRoot $relative
      New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($dest)) | Out-Null
      Copy-Item -Path $_.FullName -Destination $dest -Force
    }
  ok "Карантин создан: $quarantineRoot"

  # 3) Recreate minimal autorun .bat
  $autorunBatPath = Join-Path $ProjectPath 'start_windows_autorun.bat'
  $bat = @"
@echo off
chcp 65001 >nul
echo === AI-Agent Autorun ===
REM Опционально: запуск Docker Desktop и LM Studio
if exist "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe" start "" "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"
if exist "C:\\Program Files\\LM Studio\\LM Studio.exe" start "" "C:\\Program Files\\LM Studio\\LM Studio.exe"
timeout /t 12 /nobreak >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "${ProjectPath}\scripts\start_agent.ps1"
"@
  Set-Content -Path $autorunBatPath -Value $bat -Encoding UTF8
  ok "start_windows_autorun.bat восстановлён: $autorunBatPath"

  # 4) Scheduler task (ONLOGON)
  $taskName = 'AI_Agent_Autostart'
  $quotedBat = $autorunBatPath.Replace('"','""')
  schtasks /Create /SC ONLOGON /RL HIGHEST /TN $taskName /TR "cmd.exe /c `"$quotedBat`"" /DELAY 0000:30 /F *> $null
  ok "Задача автозапуска обновлена: $taskName"

  # 5) Launch API (foreground smoke)
  Set-Location $ProjectPath
  $apiArgs = @("-3.11","-m","uvicorn","api.agent:app","--host","127.0.0.1","--port","8088","--http","h11","--loop","asyncio","--workers","1","--no-access-log","--log-level","info")
  Start-Process -FilePath "py" -ArgumentList $apiArgs -WindowStyle Hidden
  Start-Sleep -Seconds 5

  try {
    $h = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -TimeoutSec $HealthTimeoutSec
    if ($h.status -eq "ok") {
      ok "API поднят: /health ok"
    } else {
      warn ("API отвечает, но статус: " + ($h | ConvertTo-Json -Compress))
    }
  } catch {
    err ("API не ответил: " + $_)
  }

  ok "Готово. Для проверки автозапуска можно перезагрузить ПК."

} catch {
  err ("Неожиданная ошибка: " + $_)
  exit 1
}



