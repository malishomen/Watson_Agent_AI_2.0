# scripts\fix_ps_profile.ps1
# Цель: полностью вычистить проблемные профили, поставить минимальный и безопасный UTF-8 prompt.

$ErrorActionPreference = 'Stop'

# 1. Определяем все профили PS (текущий/все хосты/все пользователи)
$profiles = @()
$profiles += $PROFILE
$profiles += $PROFILE.CurrentUserAllHosts
$profiles += $PROFILE.AllUsersCurrentHost
$profiles += $PROFILE.AllUsersAllHosts
$profiles = $profiles | Sort-Object -Unique

# 2. Бэкап существующих профилей (если есть)
foreach ($p in $profiles) {
  if ([string]::IsNullOrWhiteSpace($p)) { continue }
  $dir = Split-Path $p -Parent
  if (-not (Test-Path $dir)) { New-Item -Force -ItemType Directory -Path $dir | Out-Null }
  if (Test-Path $p) {
    Copy-Item $p "$p.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Force
  }
}

# 3. Минимальный безопасный профиль для всех хостов текущего пользователя
$cleanProfile = @'
# === CLEAN UTF-8 PROFILE (AI-Agent) ===
# Никаких сторонних модулей/украшателей/alias. Только безопасная кодировка и простой prompt.

[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)

$env:PYTHONUTF8       = '1'
$env:PYTHONIOENCODING = 'utf-8'

function prompt { "PS $((Get-Location).Path)> " }
'@

# 4. Записываем чистый профиль
Set-Content -Path $PROFILE.CurrentUserAllHosts -Encoding UTF8 -Force -Value $cleanProfile

# 5. Удаляем шумные/конфликтные настройки в других профилях (делаем их пустыми)
$empty = "# (empty by AI-Agent)"
foreach ($p in @($PROFILE, $PROFILE.AllUsersCurrentHost, $PROFILE.AllUsersAllHosts)) {
  if (-not [string]::IsNullOrWhiteSpace($p)) {
    Set-Content -Path $p -Encoding UTF8 -Force -Value $empty
  }
}

# 6. Чистим сторонние украшатели, если они были автоподключены (oh-my-posh / starship / posh-git)
# (НЕ критично, просто на всякий случай)
$commonPlaces = @(
  "$env:USERPROFILE\Documents\PowerShell\Microsoft.PowerShell_profile.ps1",
  "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
)
foreach ($cp in $commonPlaces) {
  if (Test-Path $cp) {
    (Get-Content $cp -Encoding UTF8) |
      Where-Object {$_ -notmatch 'oh-my-posh|starship|posh-git|Write-Host|chcp|Set-PSReadLine'} |
      Set-Content -Path $cp -Encoding UTF8 -Force
  }
}

Write-Host "✅ Профиль PowerShell очищен и установлен минимальный безопасный вариант." -ForegroundColor Green
Write-Host "ℹ️ Откройте НОВУЮ вкладку терминала PowerShell и проверьте, что 'с' больше не добавляется." -ForegroundColor Yellow

