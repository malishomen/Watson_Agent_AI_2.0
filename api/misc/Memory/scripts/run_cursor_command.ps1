param([Parameter(Mandatory=$true)][string]$Text, [string]$Session="Cursor", [string]$Secret="test123")
$b = @{ text = $Text; session = $Session } | ConvertTo-Json -Compress
irm -Method Post $env:AGENT_API_BASE/command `
  -Headers @{ 'x-agent-secret' = $Secret } `
  -ContentType 'application/json; charset=utf-8' `
  -Body $b
