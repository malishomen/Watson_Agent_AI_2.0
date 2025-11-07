# scripts/detect_cyrillic_commands.ps1
# Script for detecting Cyrillic characters in Python commands

param(
    [string]$Path = ".",
    [switch]$Fix = $false
)

Write-Host "=== Detecting Cyrillic Characters in Commands ===" -ForegroundColor Cyan

# Patterns for searching Cyrillic characters in Python commands
$patterns = @(
    "сpy\s",           # Cyrillic 's' before 'py'
    "сpython\s",       # Cyrillic 's' before 'python'
    "сpython3\s",      # Cyrillic 's' before 'python3'
    "сpip\s",          # Cyrillic 's' before 'pip'
    "сuv\s",           # Cyrillic 's' before 'uv'
    "сuvicorn\s",      # Cyrillic 's' before 'uvicorn'
    "сpytest\s",       # Cyrillic 's' before 'pytest'
    "сmypy\s"          # Cyrillic 's' before 'mypy'
)

$foundIssues = @()

# Search in all files
Get-ChildItem -Path $Path -Recurse -Include "*.ps1", "*.py", "*.md", "*.txt" | ForEach-Object {
    $file = $_
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    
    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            $matches = [regex]::Matches($content, $pattern)
            foreach ($match in $matches) {
                $lineNumber = ($content.Substring(0, $match.Index) -split "`n").Count
                $foundIssues += @{
                    File = $file.FullName
                    Line = $lineNumber
                    Pattern = $pattern
                    Match = $match.Value
                    Context = ($content -split "`n")[$lineNumber - 1]
                }
            }
        }
    }
}

if ($foundIssues.Count -eq 0) {
    Write-Host "✅ No Cyrillic characters found in commands!" -ForegroundColor Green
    exit 0
}

Write-Host "❌ Found $($foundIssues.Count) issues with Cyrillic characters:" -ForegroundColor Red

foreach ($issue in $foundIssues) {
    Write-Host "`nFile: $($issue.File)" -ForegroundColor Yellow
    Write-Host "Line $($issue.Line): $($issue.Context)" -ForegroundColor White
    Write-Host "Issue: '$($issue.Match)' (pattern: $($issue.Pattern))" -ForegroundColor Red
}

if ($Fix) {
    Write-Host "`n=== Auto-fixing ===" -ForegroundColor Cyan
    
    foreach ($issue in $foundIssues) {
        $content = Get-Content -Path $issue.File -Raw -Encoding UTF8
        $fixedContent = $content
        
        # Replace Cyrillic 's' with Latin 'c'
        $fixedContent = $fixedContent -replace "сpy\s", "cpy "
        $fixedContent = $fixedContent -replace "сpython\s", "cpython "
        $fixedContent = $fixedContent -replace "сpython3\s", "cpython3 "
        $fixedContent = $fixedContent -replace "сpip\s", "cpip "
        $fixedContent = $fixedContent -replace "сuv\s", "cuv "
        $fixedContent = $fixedContent -replace "сuvicorn\s", "cuvicorn "
        $fixedContent = $fixedContent -replace "сpytest\s", "cpytest "
        $fixedContent = $fixedContent -replace "сmypy\s", "cmypy "
        
        if ($fixedContent -ne $content) {
            Set-Content -Path $issue.File -Value $fixedContent -Encoding UTF8
            Write-Host "✅ Fixed file: $($issue.File)" -ForegroundColor Green
        }
    }
    
    Write-Host "`n=== Re-checking ===" -ForegroundColor Cyan
    & $MyInvocation.MyCommand.Path -Path $Path
}

Write-Host "`n=== Recommendations ===" -ForegroundColor Yellow
Write-Host "1. Always use Latin 'c' in commands: py, python, pip, pytest" -ForegroundColor White
Write-Host "2. Configure IDE to show invisible characters" -ForegroundColor White
Write-Host "3. Use command: .\scripts\detect_cyrillic_commands.ps1 -Fix" -ForegroundColor White
Write-Host "4. Check file encoding: UTF-8 without BOM" -ForegroundColor White