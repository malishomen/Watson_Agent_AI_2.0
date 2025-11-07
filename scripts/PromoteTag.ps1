#Requires -Version 5.1
param(
  [Parameter(Mandatory=$true)][string]$Host,
  [Parameter(Mandatory=$true)][string]$Tag,
  [int]$TimeoutSec = 120
)
$ErrorActionPreference = 'Stop'
try {
  Write-Output "PROMOTE host=$Host tag=$Tag"
  # Пример: обновить .env на staging и docker compose up с нужным IMAGE_TAG
  Start-Sleep -Seconds 2
  Write-Output "PROMOTE DONE host=$Host tag=$Tag"
  exit 0
} catch {
  Write-Output "PROMOTE FAIL: $($_.Exception.Message)"
  exit 2
}


