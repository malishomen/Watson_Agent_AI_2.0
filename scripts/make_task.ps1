param(
  [Parameter(Mandatory=$true)]
  [string]$Text,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$inboxDir = Join-Path $PSScriptRoot ".." "inbox"
if (-not (Test-Path $inboxDir)) {
    New-Item -ItemType Directory -Path $inboxDir | Out-Null
}

$taskId = Get-Random -Minimum 1000 -Maximum 9999
$taskFile = Join-Path $inboxDir "task_$taskId.task.json"

$taskData = @{
    text = $Text
    dry_run = $DryRun.IsPresent
    chat_id = "manual"
    created_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
} | ConvertTo-Json -Depth 5

Set-Content -Path $taskFile -Value $taskData -Encoding UTF8

Write-Host "✅ Задача создана: task_$taskId.task.json" -ForegroundColor Green
Write-Host "📋 Текст: $Text" -ForegroundColor Cyan
Write-Host "🧪 Dry-run: $($DryRun.IsPresent)" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏳ Task Watcher обработает задачу автоматически..." -ForegroundColor Gray

