#Requires -Version 5.1
param(
  [Parameter(Mandatory=$true)][string]$Host,
  [int]$TimeoutSec = 60
)
$ErrorActionPreference = 'Stop'
function Get-Json([string]$Url, [int]$Timeout) {
  Invoke-RestMethod -Uri $Url -TimeoutSec $Timeout
}
$base = "http://$Host:8080"
$sw = [System.Diagnostics.Stopwatch]::StartNew()
try {
  $h = Get-Json "$base/health" $TimeoutSec
  if (-not $h.ok) { throw "/health != ok:true" }
  $m = Get-Json "$base/metrics" $TimeoutSec
  $git = $m.version.git_sha
  $tag = $m.version.image_tag
  $prof = $m.profile.active
  if (-not $git -or -not $tag -or $prof -ne 'staging') { throw "metrics fields missing or profile!=staging" }
  $sw.Stop()
  Write-Output ("OK {0} {1} {2:N2}s" -f $tag, $git, $sw.Elapsed.TotalSeconds)
  exit 0
} catch {
  $sw.Stop()
  Write-Output ("FAIL {0} {1:N2}s" -f $_.Exception.Message, $sw.Elapsed.TotalSeconds)
  exit 2
}


