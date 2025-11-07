param(
  [string]$Source = "D:\AI-Agent\Memory",
  [string]$Dest   = "D:\projects\Ai-Agent_Watson\Watson_Agent_2.0",
  [switch]$IncludeSecrets,
  [switch]$DryRun,
  [switch]$Validate,
  [switch]$Zip,
  [switch]$DisableCursorStartup = $true,
  [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

function Info($m){ Write-Host $m -ForegroundColor Cyan }
function Ok($m){ Write-Host "  ✔ $m" -ForegroundColor Green }
function Warn($m){ Write-Host "  ⚠ $m" -ForegroundColor Yellow }
function Err($m){ Write-Host "  ✖ $m" -ForegroundColor Red }

function Test-ExcludedPath {
  param([string]$Path, [string[]]$ExcludeDirs)
  $p = $Path.ToLower()
  foreach ($ex in $ExcludeDirs) {
    if ($p -like ("*\" + $ex.ToLower() + "\*")) { return $true }
  }
  return $false
}

function Get-RelativePath {
  param([string]$FullPath, [string]$Root)
  $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\') + '\\'
  $full = [System.IO.Path]::GetFullPath($FullPath)
  if ($full.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    return $full.Substring($rootFull.Length)
  }
  return [System.IO.Path]::GetFileName($full)
}

function Copy-Preserve {
  param([System.IO.FileInfo]$File, [string]$SrcRoot, [string]$DstRoot, [switch]$IsDryRun)
  $rel = Get-RelativePath -FullPath $File.FullName -Root $SrcRoot
  $dst = Join-Path $DstRoot $rel
  $dstDir = Split-Path $dst -Parent
  if (-not $IsDryRun) { New-Item -ItemType Directory -Force -Path $dstDir | Out-Null }
  if (-not $IsDryRun) { Copy-Item -Path $File.FullName -Destination $dst -Force }
  return ,@($rel,$dst)
}

$metrics = [ordered]@{
  totalFound = 0
  copied = 0
  skippedExcluded = 0
  dynamicFound = 0
  errors = 0
  elapsedMs = 0
}

$sw = [System.Diagnostics.Stopwatch]::StartNew()

# --- 0) Проверки путей ---
if (-not (Test-Path $Source)) { Err "Source не найден: $Source"; exit 1 }
if (Test-Path $Dest) {
  if ($Overwrite) {
    if (-not $DryRun) { Remove-Item -Recurse -Force $Dest }
    Warn "Очистил существующий $Dest (Overwrite)"
  } else {
    Warn "Папка назначения уже существует. Использую её (без очистки). Добавлю/перезапишу нужные файлы."
  }
}
if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $Dest | Out-Null }

# --- 1) Отключаем автозапуск Cursor ---
if ($DisableCursorStartup) {
  Info "Отключаю автозапуск Cursor..."
  try {
    $startup = [Environment]::GetFolderPath("Startup")
    Get-ChildItem $startup -Filter "*cursor*.lnk" -ErrorAction SilentlyContinue | ForEach-Object {
      if (-not $DryRun) { Remove-Item $_.FullName -Force }
      Ok "Удалён ярлык: $($_.Name)"
    }

    $runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    if (Test-Path $runKey) {
      (Get-ItemProperty $runKey).PSObject.Properties |
        Where-Object { $_.Value -and ($_.Value -as [string]) -match "cursor" } |
        ForEach-Object {
          if (-not $DryRun) { Remove-ItemProperty -Path $runKey -Name $_.Name -Force }
          Ok "Удалена запись автозапуска (Run): $($_.Name)"
        }
    }

    $tasks = schtasks /Query /FO LIST /V 2>$null | Select-String -Pattern "TaskName:|Actions:"
    $current = $null
    foreach ($line in $tasks) {
      if ($line -match "^TaskName:\s+(.*)$") { $current = $Matches[1] }
      if ($line -match "^Actions:\s+(.*)$") {
        $act = $Matches[1]
        if ($act -match "cursor\.exe") {
          if (-not $DryRun) { schtasks /Change /TN $current /Disable | Out-Null }
          Ok "Отключена задача автозапуска: $current"
        }
      }
    }
  } catch {
    Warn "Не удалось полностью отключить автозапуск: $($_.Exception.Message)"
  }
}

# --- 2) Правила копирования ---
$excludeDirs = @(
  ".git",".cursor",".idea",".vscode","node_modules",
  ".pytest_cache","__pycache__","dist","build","logs","tmp","output","data","datasets",
  "venv",".venv","env",".mypy_cache",".ruff_cache"
)

$includeGlobs = @(
  "api\**\*.py",
  "api\**\*.json","api\**\*.yml","api\**\*.yaml","api\**\*.toml",
  "tests\**\*",
  "conftest.py",
  "requirements.txt","pyproject.toml","poetry.lock",
  "README.md","README*.md","LICENSE*",
  "apply_patch.ps1","test_and_report.ps1","run_agent.ps1","api_tests.http"
)

# --- 3) Сбор списка файлов к копированию ---
$selectedPaths = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)

foreach ($pattern in $includeGlobs) {
  $items = Get-ChildItem -Path $Source -Recurse -File -Include $pattern -ErrorAction SilentlyContinue
  foreach ($it in $items) {
    if (-not (Test-ExcludedPath -Path $it.FullName -ExcludeDirs $excludeDirs)) {
      [void]$selectedPaths.Add($it.FullName)
    } else {
      $metrics.skippedExcluded++
    }
  }
}

$dynamicBot = Get-ChildItem -Path $Source -Recurse -File -Include *bot*.py,*telegram*.py -ErrorAction SilentlyContinue
foreach ($it in $dynamicBot) {
  if (-not (Test-ExcludedPath -Path $it.FullName -ExcludeDirs $excludeDirs)) {
    if ($selectedPaths.Add($it.FullName)) { $metrics.dynamicFound++ }
  } else {
    $metrics.skippedExcluded++
  }
}

$toCopy = $selectedPaths | ForEach-Object { Get-Item $_ } | Sort-Object FullName -Unique
$metrics.totalFound = @($toCopy).Count

# --- 4) Копирование с сохранением структуры ---
Info "Файлы к переносу:"
$manifest = @()
foreach ($f in $toCopy) {
  try {
    $rel,$dst = Copy-Preserve -File $f -SrcRoot $Source -DstRoot $Dest -IsDryRun:$DryRun
    Write-Host "  → $rel"
    $manifest += $rel
    if (-not $DryRun) { $metrics.copied++ }
  } catch {
    $metrics.errors++
    Err "Не удалось обработать: $($f.FullName) — $($_.Exception.Message)"
  }
}

# --- 5) Секреты: .env / .env.example ---
$envSrc = Join-Path $Source ".env"
$envDst = Join-Path $Dest ".env"
$envEx  = Join-Path $Dest ".env.example"

if (Test-Path $envSrc) {
  if ($IncludeSecrets) {
    if (-not $DryRun) { Copy-Item $envSrc $envDst -Force }
    Ok ".env перенесён (по флагу -IncludeSecrets)"
  } else {
    $lines = Get-Content $envSrc -ErrorAction SilentlyContinue
    $masked = $lines | ForEach-Object {
      if ($_ -match '^\s*BOT_TOKEN\s*=\s*(.+)$') { "BOT_TOKEN=" } else { $_ }
    }
    if (-not $DryRun) { $masked | Set-Content -Encoding UTF8 $envEx }
    Ok ".env.example создан (секреты не перенесены)"
  }
} else {
  Warn ".env не найден в исходнике — пропускаю"
}

# --- 6) Манифест ---
$manifestPath = Join-Path $Dest "MANIFEST_copied_files.txt"
if (-not $DryRun) { $manifest | Set-Content -Encoding UTF8 $manifestPath }
Ok "Манифест: $manifestPath"

# --- 7) Валидация ---
if ($Validate) {
  if ($DryRun) {
    Info "Валидация (DryRun): проверяю обязательные пути в Source"
    $basePath = $Source
  } else {
    Info "Валидация структуры..."
    $basePath = $Dest
  }
  $must = @("conftest.py","tests","api")
  $miss = @()
  foreach ($m in $must) {
    if (-not (Test-Path (Join-Path $basePath $m))) { $miss += $m }
  }
  if ($miss.Count -gt 0) { Err "Не хватает обязательных путей: $($miss -join ', ')"; if (-not $DryRun) { exit 2 } else { Warn "(DryRun) Валидация по Source выявила недостающие элементы" } }
  else { Ok "Базовая структура на месте" }
}

# --- 8) Упаковка в zip ---
if ($Zip) {
  $zipPath = Join-Path (Split-Path $Dest -Parent) ("{0}.zip" -f (Split-Path $Dest -Leaf))
  if (-not $DryRun) {
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Compress-Archive -Path (Join-Path $Dest "*") -DestinationPath $zipPath
  }
  Ok "Упаковано: $zipPath"
}

$sw.Stop()
$metrics.elapsedMs = [int]$sw.Elapsed.TotalMilliseconds

Info "Итоговые метрики:"
Write-Host ("  Найдено файлов: {0}" -f $metrics.totalFound)
Write-Host ("  Скопировано: {0}" -f $metrics.copied)
Write-Host ("  Пропущено (исключения): {0}" -f $metrics.skippedExcluded)
Write-Host ("  Найдено динамически (бот/telegram): {0}" -f $metrics.dynamicFound)
Write-Host ("  Ошибок: {0}" -f $metrics.errors)
Write-Host ("  Время, мс: {0}" -f $metrics.elapsedMs)

Info "Готово."


