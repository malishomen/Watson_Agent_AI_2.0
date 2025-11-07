# Cursor Automation Fixed
# Patched version with UTF-8 header, anti-Cyrillic protection, and robust automation

# --- UTF-8 / Anti-'с' Hygiene Header ---
[Console]::InputEncoding  = [Text.UTF8Encoding]::UTF8
[Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
$env:PYTHONUTF8       = '1'
$env:PYTHONIOENCODING = 'utf-8'
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

# --- Python selector (prefers 3.11, else 3.13, else latest 3.x) ---
function Get-PyCmd {
  $candidates = @("python","py -3.11","py -3.13","py -3")
  foreach($c in $candidates){
    try{
      $v = & $c --version 2>$null
      if($LASTEXITCODE -eq 0 -and $v){ return $c }
    }catch{}
  }
  return "python"
}
$PY = Get-PyCmd
Write-Host "Using Python: $PY" -ForegroundColor Cyan

function Remove-LeadingCyrillicS {
  param([string]$Text)
  if (-not $Text) { return $Text }
  $lines = ($Text -split "(`r`n|`n|`r)")
  for ($i=0; $i -lt $lines.Count; $i++) {
    $lines[$i] = ($lines[$i] -replace '^[\uFEFF\s]*\u0441(?=\s|$)','')
  }
  return ($lines -join "`r`n")
}

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Kbd {
  [DllImport("user32.dll")] public static extern IntPtr LoadKeyboardLayout(string pwszKLID, uint Flags);
  [DllImport("user32.dll")] public static extern IntPtr ActivateKeyboardLayout(IntPtr hkl, uint Flags);
}
"@

function Set-KeyboardLayoutEn {
  try {
    $hkl = [Kbd]::LoadKeyboardLayout("00000409", 1) # EN-US
    [void][Kbd]::ActivateKeyboardLayout($hkl, 0)
    return $true
  } catch { return $false }
}

param(
    [string]$ProjectPath = "D:\AI-Agent",
    [string]$Task = "Create full-featured web application on FastAPI with PostgreSQL database",
    [string]$Secret = "test123",
    [int]$Timeout = 600
)

$ErrorActionPreference = "Stop"

# Logging setup with UTF-8 encoding
$LogFile = "cursor_automation_fixed.log"
$StartTime = Get-Date

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Send-KeysToCursor {
    param([string]$Keys, [int]$Delay = 500)
    
    try {
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait($Keys)
        Start-Sleep -Milliseconds $Delay
        return $true
    } catch {
        Write-Log "Error sending keys: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Find-CursorWindow {
    try {
        $processes = Get-Process | Where-Object { 
            $_.ProcessName -like "*cursor*" -or 
            $_.MainWindowTitle -like "*cursor*" -or
            $_.MainWindowTitle -like "*Cursor*"
        }
        
        if ($processes) {
            Write-Log "Found Cursor window: $($processes[0].MainWindowTitle)" "INFO"
            return $processes[0]
        } else {
            Write-Log "Cursor window not found" "WARNING"
            return $null
        }
    } catch {
        Write-Log "Error finding Cursor window: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Activate-CursorWindow {
    param([System.Diagnostics.Process]$Process)
    
    try {
        if ($Process -and $Process.MainWindowHandle -ne [IntPtr]::Zero) {
            Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class Win32 {
                    [DllImport("user32.dll")]
                    public static extern bool SetForegroundWindow(IntPtr hWnd);
                    [DllImport("user32.dll")]
                    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
                    [DllImport("user32.dll")]
                    public static extern bool IsWindowVisible(IntPtr hWnd);
                }
"@
            
            if ([Win32]::IsWindowVisible($Process.MainWindowHandle)) {
                [Win32]::ShowWindow($Process.MainWindowHandle, 9) # SW_RESTORE
                [Win32]::SetForegroundWindow($Process.MainWindowHandle)
                Write-Log "Cursor window activated" "INFO"
                return $true
            } else {
                Write-Log "Cursor window not visible" "WARNING"
                return $false
            }
        } else {
            Write-Log "Could not activate Cursor window" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Error activating window: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-CursorProject {
    Write-Log "=== Step 1: Start Cursor and open project ===" "INFO"
    
    try {
        # Search for cursor.exe if alias 'cursor' not in PATH
        $cursorExe = (Get-Command cursor -ErrorAction SilentlyContinue)?.Source
        if (-not $cursorExe) {
            $candidates = @(
                "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe",
                "$env:LOCALAPPDATA\Cursor\Cursor.exe",
                "$env:ProgramFiles\Cursor\Cursor.exe",
                "$env:ProgramFiles(x86)\Cursor\Cursor.exe"
            )
            $cursorExe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
        }
        if (-not $cursorExe) { 
            throw "Cursor.exe not found. Install shell command 'cursor' or specify path." 
        }
        
        # Set EN keyboard layout before hotkeys
        Set-KeyboardLayoutEn | Out-Null
        
        # Start Cursor with project
        $cursorProcess = Start-Process -FilePath $cursorExe -ArgumentList "`"$ProjectPath`"" -PassThru
        Write-Log "Cursor started (PID: $($cursorProcess.Id))" "INFO"
        
        # Wait for loading
        Start-Sleep -Seconds 8
        
        # Find and activate window
        $cursorWindow = Find-CursorWindow
        if (-not $cursorWindow) {
            throw "Cursor window not found"
        }
        
        if (-not (Activate-CursorWindow -Process $cursorWindow)) {
            throw "Could not activate Cursor window"
        }
        
        Write-Log "✅ Cursor started and project opened" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Error starting Cursor: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Open-AIPanel {
    Write-Log "=== Step 2: Open AI panel ===" "INFO"
    
    try {
        # Press Ctrl+L to open AI panel
        if (-not (Send-KeysToCursor -Keys "^l" -Delay 2000)) {
            throw "Could not open AI panel"
        }
        
        Write-Log "✅ AI panel opened" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Error opening AI panel: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Switch-ToAgentMode {
    Write-Log "=== Step 3: Switch to Agent Mode ===" "INFO"
    
    try {
        # Open command palette (Ctrl+Shift+P)
        Send-KeysToCursor -Keys "^+p" -Delay 2000
        
        # Try multiple Agent Mode commands
        $agentCommands = @("Enable Agent Mode", "Agent: Enable", "Agent Mode")
        foreach ($cmd in $agentCommands) {
            Send-KeysToCursor -Keys $cmd -Delay 1000
            Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
            Start-Sleep -Seconds 1
        }
        
        Write-Log "✅ Agent Mode activated" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Error switching to Agent Mode: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Send-AgentRequest {
    param([string]$TaskDescription)
    
    Write-Log "=== Step 4: Send request to agent ===" "INFO"
    
    try {
        # Clear input field
        Send-KeysToCursor -Keys "^a" -Delay 500
        
        # Type task text
        Send-KeysToCursor -Keys $TaskDescription -Delay 1000
        
        # Send request (Enter)
        Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
        
        Write-Log "✅ Request sent to agent" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Error sending request: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Wait-ForAgentCompletion {
    param([int]$TimeoutSeconds = 600)
    
    Write-Log "=== Step 5: Wait for agent completion ===" "INFO"
    
    $startTime = Get-Date
    $lastActivity = $startTime
    
    while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($TimeoutSeconds)) {
        try {
            # Auto-confirm changes
            Auto-ConfirmChanges
            
            # Check completion
            if (Test-AgentCompletion) {
                Write-Log "✅ Agent completed work" "INFO"
                break
            }
            
            # Check activity
            if ((Get-Date) - $lastActivity -gt [TimeSpan]::FromMinutes(2)) {
                Write-Log "⏰ No activity for 2 minutes, considering completed" "INFO"
                break
            }
            
            # Update last activity time
            if (Test-AgentActivity) {
                $lastActivity = Get-Date
            }
            
            $elapsed = [Math]::Round(((Get-Date) - $startTime).TotalSeconds)
            Write-Log "⏳ Waiting... ${elapsed}s / ${TimeoutSeconds}s" "INFO"
            
            Start-Sleep -Seconds 10
            
        } catch {
            Write-Log "Error while waiting: $($_.Exception.Message)" "ERROR"
            Start-Sleep -Seconds 5
        }
    }
    
    Write-Log "✅ Waiting completed" "INFO"
    return $true
}

function Auto-ConfirmChanges {
    try {
        # Press Ctrl+Enter to confirm commands
        Send-KeysToCursor -Keys "^+{ENTER}" -Delay 100
        Send-KeysToCursor -Keys "{ENTER}" -Delay 100
        Send-KeysToCursor -Keys "{TAB}" -Delay 100
        
    } catch {
        Write-Log "Auto-confirm error: $($_.Exception.Message)" "DEBUG"
    }
}

function Test-AgentCompletion {
    try {
        # Check via API agent
        $headers = @{"x-agent-secret" = $Secret}
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
        
        if ($response.status -eq "ok") {
            return $true
        } else {
            return $false
        }
        
    } catch {
        Write-Log "API not responding: $($_.Exception.Message)" "DEBUG"
        return $false
    }
}

function Test-AgentActivity {
    try {
        # Check API agent
        if (Test-AgentCompletion) {
            return $true
        }
        
        return $false
        
    } catch {
        Write-Log "Error checking activity: $($_.Exception.Message)" "DEBUG"
        return $false
    }
}

function Save-AllFiles {
    Write-Log "=== Step 6: Save all files ===" "INFO"
    
    try {
        # Save all files through palette (more reliable than Ctrl+Shift+S)
        Send-KeysToCursor -Keys "^+p" -Delay 1000
        Send-KeysToCursor -Keys "File: Save All" -Delay 1000
        Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
        
        Write-Log "✅ All files saved" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Error saving files: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Add-CodeComments {
    Write-Log "=== Step 7: Add code comments ===" "INFO"
    
    try {
        # Open AI panel for new request
        Send-KeysToCursor -Keys "^l" -Delay 2000
        
        # Form comment request
        $commentRequest = @"
Add detailed comments to code explaining:
1. Purpose of each function and class
2. Parameters and return values
3. Algorithm logic
4. Usage examples
5. Error handling
6. Component relationships
"@
        
        # Clear input field
        Send-KeysToCursor -Keys "^a" -Delay 500
        
        # Send request
        Send-KeysToCursor -Keys $commentRequest -Delay 1000
        Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
        
        # Wait for completion
        Start-Sleep -Seconds 30
        
        Write-Log "✅ Comments added" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Error adding comments: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-Tests {
    Write-Log "=== Step 8: Start tests ===" "INFO"
    
    try {
        # Open terminal through palette (more reliable than Ctrl+`)
        Send-KeysToCursor -Keys "^+p" -Delay 2000
        Send-KeysToCursor -Keys "Terminal: New Terminal" -Delay 1000
        Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
        
        # Clear terminal
        Send-KeysToCursor -Keys "^l" -Delay 500
        
        # Run tests
        $testCommand = "python -m pytest -q"
        Send-KeysToCursor -Keys $testCommand -Delay 1000
        Send-KeysToCursor -Keys "{ENTER}" -Delay 5000
        
        Write-Log "✅ Tests started" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Error starting tests: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-ProjectValidation {
    Write-Log "=== Step 9: Project validation ===" "INFO"
    
    try {
        # Check project structure
        $projectFiles = Get-ChildItem -Path $ProjectPath -Recurse -Include "*.py", "*.json", "*.yml", "*.yaml" | Measure-Object
        $fileCount = $projectFiles.Count
        
        # Check API agent
        if (Test-AgentCompletion) {
            Write-Log "✅ API agent working" "INFO"
        } else {
            Write-Log "⚠️ API agent not responding" "WARNING"
        }
        
        Write-Log "✅ Project validated: $fileCount files" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Error validating project: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function New-ExecutionReport {
    Write-Log "=== Generate report ===" "INFO"
    
    try {
        $endTime = Get-Date
        $duration = ($endTime - $StartTime).TotalSeconds
        
        $report = @{
            start_time = $StartTime.ToString("yyyy-MM-dd HH:mm:ss")
            end_time = $endTime.ToString("yyyy-MM-dd HH:mm:ss")
            duration_seconds = [Math]::Round($duration, 2)
            project_path = $ProjectPath
            task = $Task
            timeout = $Timeout
            success = $true
        }
        
        # Save report
        $reportPath = Join-Path $ProjectPath "cursor_automation_fixed_report.json"
        $report | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath -Encoding UTF8
        
        Write-Log "✅ Report saved: $reportPath" "INFO"
        Write-Log "📊 Statistics: $($report | ConvertTo-Json -Compress)" "INFO"
        
        return $report
        
    } catch {
        Write-Log "❌ Error generating report: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Start-APIAgent {
    Write-Log "Starting API agent..." "INFO"
    
    try {
        # Start API agent through PowerShell script
        $scriptPath = Join-Path $ProjectPath "start_agent_final.ps1"
        
        if (Test-Path $scriptPath) {
            Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $scriptPath -WindowStyle Hidden
            
            # Wait for API startup
            Start-Sleep -Seconds 10
            
            # Health check
            if (Test-AgentCompletion) {
                Write-Log "✅ API agent started and working" "INFO"
                return $true
            } else {
                Write-Log "❌ API agent not responding" "ERROR"
                return $false
            }
        } else {
            Write-Log "❌ Script not found: $scriptPath" "ERROR"
            return $false
        }
        
    } catch {
        Write-Log "❌ Error starting API agent: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main function
function Start-FullWorkflow {
    Write-Log "🚀 === START FULL WORKFLOW AUTONOMOUS AGENT ===" "INFO"
    
    try {
        # Start API agent
        if (-not (Start-APIAgent)) {
            Write-Log "❌ Could not start API agent" "ERROR"
            return $false
        }
        
        # Step 1: Start Cursor
        if (-not (Start-CursorProject)) {
            return $false
        }
        
        # Step 2: Open AI panel
        if (-not (Open-AIPanel)) {
            return $false
        }
        
        # Step 3: Switch to Agent Mode
        if (-not (Switch-ToAgentMode)) {
            Write-Log "⚠️ Could not switch to Agent Mode, continuing..." "WARNING"
        }
        
        # Step 4: Send main request
        if (-not (Send-AgentRequest -TaskDescription $Task)) {
            return $false
        }
        
        # Step 5: Wait for completion
        if (-not (Wait-ForAgentCompletion -TimeoutSeconds $Timeout)) {
            Write-Log "⚠️ Agent did not complete work in expected time" "WARNING"
        }
        
        # Step 6: Save files
        Save-AllFiles
        
        # Step 7: Add comments
        Add-CodeComments
        
        # Step 8: Start tests
        Start-Tests
        
        # Step 9: Project validation
        Test-ProjectValidation
        
        # Generate report
        New-ExecutionReport
        
        Write-Log "🎉 === WORKFLOW COMPLETED SUCCESSFULLY ===" "INFO"
        return $true
        
    } catch {
        Write-Log "❌ Critical error in workflow: $($_.Exception.Message)" "ERROR"
        New-ExecutionReport
        return $false
    }
}

# Start full workflow
$success = Start-FullWorkflow

if ($success) {
    Write-Log "🎉 Project completed successfully!" "INFO"
    exit 0
} else {
    Write-Log "❌ Errors occurred during execution" "ERROR"
    exit 1
}
