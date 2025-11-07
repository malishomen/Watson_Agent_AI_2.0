#Requires -Version 5.1
param(
  [Parameter(Mandatory=$true)][string]$Host,
  [string]$To = "prev",
  [int]$TimeoutSec = 120
)
$ErrorActionPreference = 'Stop'
try {
  Write-Output "ROLLBACK host=$Host to=$To"
  # Пример: выбрать предыдущий tag (или заданный) и перезапустить compose
  Start-Sleep -Seconds 2
  Write-Output "ROLLBACK DONE host=$Host to=$To"
  exit 0
} catch {
  Write-Output "ROLLBACK FAIL: $($_.Exception.Message)"
  exit 2
}


