# scripts/prevent_cyrillic_commands.ps1
# Script for preventing Cyrillic characters in commands

param(
    [string]$Path = ".",
    [switch]$Install = $false,
    [switch]$Uninstall = $false
)

Write-Host "=== Cyrillic Characters Prevention System ===" -ForegroundColor Cyan

# Function to create git pre-commit hook
function Install-GitHook {
    $hookPath = ".git\hooks\pre-commit"
    
    if (-not (Test-Path ".git")) {
        Write-Host "❌ .git directory not found. Initialize git repository." -ForegroundColor Red
        return $false
    }
    
    $hookContent = @"
#!/bin/sh
# Git hook to prevent Cyrillic characters in commands

echo "Checking for Cyrillic characters in commands..."

# Check only modified files
git diff --cached --name-only | while read file; do
    if [[ "$file" =~ \.(ps1|py|md|txt)$ ]]; then
        # Check for Cyrillic characters in commands
        if git show ":$file" | grep -E "(сpy |сpython |сpip |сuv |сuvicorn |сpytest |сmypy )" > /dev/null; then
            echo "❌ Error: Found Cyrillic characters in commands in file: $file"
            echo "Use Latin 'c' instead of Cyrillic 's'"
            echo "Run: powershell -ExecutionPolicy Bypass -File scripts\detect_cyrillic_commands.ps1 -Fix"
            exit 1
        fi
    fi
done

echo "✅ Cyrillic characters check passed"
"@

    Set-Content -Path $hookPath -Value $hookContent -Encoding UTF8
    Write-Host "✅ Git pre-commit hook installed: $hookPath" -ForegroundColor Green
    return $true
}

# Function to create PowerShell profile
function Install-PowerShellProfile {
    $profilePath = $PROFILE
    $profileDir = Split-Path $profilePath -Parent
    
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }
    
    $profileContent = @"
# PowerShell profile to prevent Cyrillic characters
function Test-CyrillicCommands {
    param([string]`$Command)
    
    if (`$Command -match "сpy\s|сpython\s|сpip\s|сuv\s|сuvicorn\s|сpytest\s|сmypy\s") {
        Write-Host "⚠️  WARNING: Found Cyrillic character 's' in command!" -ForegroundColor Red
        Write-Host "Command: `$Command" -ForegroundColor Yellow
        Write-Host "Use Latin 'c' instead of Cyrillic 's'" -ForegroundColor White
        
        `$fixed = `$Command -replace "сpy\s", "cpy " -replace "сpython\s", "cpython " -replace "сpip\s", "cpip " -replace "сuv\s", "cuv " -replace "сuvicorn\s", "cuvicorn " -replace "сpytest\s", "cpytest " -replace "сmypy\s", "cmypy "
        
        if (`$fixed -ne `$Command) {
            Write-Host "Fixed command: `$fixed" -ForegroundColor Green
            return `$fixed
        }
    }
    return `$Command
}

# Intercept PowerShell commands
function Invoke-Expression {
    param([string]`$Command)
    
    `$fixedCommand = Test-CyrillicCommands -Command `$Command
    Microsoft.PowerShell.Utility\Invoke-Expression `$fixedCommand
}

Write-Host "✅ PowerShell profile loaded - Cyrillic characters protection active" -ForegroundColor Green
"@

    Add-Content -Path $profilePath -Value $profileContent -Encoding UTF8
    Write-Host "✅ PowerShell profile updated: $profilePath" -ForegroundColor Green
    return $true
}

# Function to create VS Code settings
function Install-VSCodeSettings {
    $vscodeDir = ".vscode"
    $settingsPath = "$vscodeDir\settings.json"
    
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
    }
    
    $settings = @{
        "files.encoding" = "utf8"
        "powershell.integratedConsole.forceClearScrollbackBuffer" = $true
        "powershell.scriptAnalysis.enable" = $true
        "powershell.scriptAnalysis.settingsPath" = "scripts\PSScriptAnalyzerSettings.psd1"
        "editor.rulers" = @(80, 120)
        "editor.unicodeHighlight.nonBasicASCII" = $true
        "editor.unicodeHighlight.ambiguousCharacters" = $true
    }
    
    $settings | ConvertTo-Json -Depth 3 | Set-Content -Path $settingsPath -Encoding UTF8
    Write-Host "✅ VS Code settings updated: $settingsPath" -ForegroundColor Green
    return $true
}

# Function to create PSScriptAnalyzer settings
function Install-PSScriptAnalyzerSettings {
    $settingsPath = "scripts\PSScriptAnalyzerSettings.psd1"
    
    $settings = @"
@{
    Rules = @{
        PSReviewUnusedParameter = @{
            Enable = `$true
        }
        PSUseApprovedVerbs = @{
            Enable = `$true
        }
        PSUseConsistentIndentation = @{
            Enable = `$true
            IndentationSize = 4
        }
        PSUseConsistentWhitespace = @{
            Enable = `$true
        }
        PSAlignAssignmentStatement = @{
            Enable = `$true
        }
    }
    CustomRulePath = @(
        "scripts\CustomRules\"
    )
}
"@

    Set-Content -Path $settingsPath -Value $settings -Encoding UTF8
    Write-Host "✅ PSScriptAnalyzer settings created: $settingsPath" -ForegroundColor Green
    return $true
}

# Main logic
if ($Install) {
    Write-Host "Installing prevention system..." -ForegroundColor Yellow
    
    $success = $true
    $success = $success -and (Install-GitHook)
    $success = $success -and (Install-PowerShellProfile)
    $success = $success -and (Install-VSCodeSettings)
    $success = $success -and (Install-PSScriptAnalyzerSettings)
    
    if ($success) {
        Write-Host "`n✅ Prevention system installed successfully!" -ForegroundColor Green
        Write-Host "Restart PowerShell to activate profile." -ForegroundColor Yellow
    } else {
        Write-Host "`n❌ Installation completed with errors." -ForegroundColor Red
    }
}
elseif ($Uninstall) {
    Write-Host "Uninstalling prevention system..." -ForegroundColor Yellow
    
    # Remove git hook
    $hookPath = ".git\hooks\pre-commit"
    if (Test-Path $hookPath) {
        Remove-Item $hookPath -Force
        Write-Host "✅ Git hook removed" -ForegroundColor Green
    }
    
    # Remove from PowerShell profile (requires manual intervention)
    Write-Host "⚠️  Manually remove content from PowerShell profile: $PROFILE" -ForegroundColor Yellow
    
    Write-Host "`n✅ Prevention system removed!" -ForegroundColor Green
}
else {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\scripts\prevent_cyrillic_commands.ps1 -Install    # Install protection" -ForegroundColor White
    Write-Host "  .\scripts\prevent_cyrillic_commands.ps1 -Uninstall  # Remove protection" -ForegroundColor White
    Write-Host "  .\scripts\prevent_cyrillic_commands.ps1             # Show help" -ForegroundColor White
}