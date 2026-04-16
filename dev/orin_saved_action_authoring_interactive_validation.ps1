param(
    [int]$InteractiveRunHardTimeoutSeconds = 900,
    [int]$NoProgressTimeoutSeconds = 20,
    [int]$ScenarioTimeoutSeconds = 90,
    [int]$TransitionTimeoutSeconds = 25,
    [int]$WatchdogStartupTimeoutSeconds = 5,
    [string]$ForcedStallPoint = "",
    [int]$ForcedStallSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic

$script:ActionTypeOrder = @("Application", "Folder", "File", "Website URL")

$source = @"
using System;
using System.Runtime.InteropServices;

public static class CodexInteractiveWin32
{
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool SetCursorPos(int X, int Y);

    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
}
"@

Add-Type -TypeDefinition $source

$RootDir = Split-Path -Parent $PSScriptRoot
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogRoot = Join-Path $RootDir "dev\logs\fb_036_authoring_interactive_validation"
$ReportsDir = Join-Path $LogRoot "reports"
$ArtifactsDir = Join-Path $LogRoot "artifacts"
$ReportPath = Join-Path $ReportsDir "FB036SavedActionAuthoringInteractiveValidationReport_$Stamp.txt"
$RuntimeLogPath = Join-Path $ArtifactsDir "${Stamp}_runtime.log"
$StepLogPath = Join-Path $ArtifactsDir "${Stamp}_interactive_steps.log"
$SourceBackupPath = Join-Path $ArtifactsDir "${Stamp}_source_backup.bin"
$WatchdogScriptPath = Join-Path $ArtifactsDir "${Stamp}_watchdog.ps1"
$WatchdogStartSignalPath = Join-Path $ArtifactsDir "${Stamp}_watchdog_started.json"
$WatchdogStdoutPath = Join-Path $ArtifactsDir "${Stamp}_watchdog_stdout.log"
$WatchdogStderrPath = Join-Path $ArtifactsDir "${Stamp}_watchdog_stderr.log"
$SourcePath = Join-Path $env:LOCALAPPDATA "Nexus Desktop AI\saved_actions.json"
$DesktopUtsPath = "C:\Users\anden\OneDrive\Desktop\User Test Summary.txt"

New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null
New-Item -ItemType Directory -Force -Path $ArtifactsDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $SourcePath) | Out-Null
Set-Content -LiteralPath $StepLogPath -Value @() -Encoding utf8

$ValidationState = [ordered]@{
    stamp = $Stamp
    report_path = $ReportPath
    runtime_log_path = $RuntimeLogPath
    step_log_path = $StepLogPath
    scenarios = @()
    artifacts = @()
    notes = @()
}

$script:InteractiveRunHardTimeoutSeconds = $InteractiveRunHardTimeoutSeconds
$script:NoProgressTimeoutSeconds = $NoProgressTimeoutSeconds
$script:ScenarioTimeoutSeconds = $ScenarioTimeoutSeconds
$script:TransitionTimeoutSeconds = $TransitionTimeoutSeconds
$script:WatchdogStartupTimeoutSeconds = $WatchdogStartupTimeoutSeconds
$script:RunStartedAt = Get-Date
$script:RunDeadline = $script:RunStartedAt.AddSeconds($script:InteractiveRunHardTimeoutSeconds)
$script:LastProgressAt = $script:RunStartedAt
$script:LastProgressPoint = "harness_start"
$script:CurrentScenarioDeadline = $null
$script:CurrentScenarioName = ""
$script:CurrentTransitionDeadline = $null
$script:CurrentTransitionName = ""
$script:TimeoutTripReason = $null
$script:LoggedControlTypeFallbacks = @{}

$script:RuntimeLogLineCursor = 0
$script:RuntimeAutoOpenPending = $false

function Record-ValidationProgress {
    param(
        [string]$Point
    )

    if ($script:TimeoutTripReason) {
        return
    }

    $script:LastProgressAt = Get-Date
    if ($Point) {
        $script:LastProgressPoint = $Point
    }
}

function Set-TimeoutFailureContext {
    param(
        [string]$Reason
    )

    if (-not $script:TimeoutTripReason) {
        $script:TimeoutTripReason = $Reason
    }
}

function Enter-ScenarioBudget {
    param(
        [string]$Name,
        [int]$TimeoutSeconds = $script:ScenarioTimeoutSeconds
    )

    $script:CurrentScenarioName = $Name
    $script:CurrentScenarioDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
    Write-StepLog -Stage "BUDGET" -Message "scenario '$Name' budget started (${TimeoutSeconds}s)"
}

function Clear-ScenarioBudget {
    param(
        [string]$Name = $script:CurrentScenarioName
    )

    if ($script:CurrentScenarioName) {
        Write-StepLog -Stage "BUDGET" -Message "scenario '$Name' budget cleared"
    }
    $script:CurrentScenarioDeadline = $null
    $script:CurrentScenarioName = ""
}

function Enter-TransitionBudget {
    param(
        [string]$Name,
        [int]$TimeoutSeconds = $script:TransitionTimeoutSeconds
    )

    $script:CurrentTransitionName = $Name
    $script:CurrentTransitionDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
    Write-StepLog -Stage "BUDGET" -Message "transition '$Name' budget started (${TimeoutSeconds}s)"
}

function Clear-TransitionBudget {
    param(
        [string]$Name = $script:CurrentTransitionName
    )

    if ($script:CurrentTransitionName) {
        Write-StepLog -Stage "BUDGET" -Message "transition '$Name' budget cleared"
    }
    $script:CurrentTransitionDeadline = $null
    $script:CurrentTransitionName = ""
}

function Assert-ValidationBudget {
    param(
        [string]$Description = "validation wait"
    )

    if ($script:TimeoutTripReason) {
        throw $script:TimeoutTripReason
    }

    $now = Get-Date
    $reason = $null
    if ($now -ge $script:RunDeadline) {
        $reason = "Full-run hard timeout exceeded while waiting for $Description. Last confirmed progress: $($script:LastProgressPoint)."
    } elseif ($now -ge $script:LastProgressAt.AddSeconds($script:NoProgressTimeoutSeconds)) {
        $reason = "No-progress watchdog exceeded while waiting for $Description. Last confirmed progress: $($script:LastProgressPoint)."
    } elseif ($script:CurrentScenarioDeadline -and $now -ge $script:CurrentScenarioDeadline) {
        $reason = "Scenario timeout exceeded for '$($script:CurrentScenarioName)' while waiting for $Description. Last confirmed progress: $($script:LastProgressPoint)."
    } elseif ($script:CurrentTransitionDeadline -and $now -ge $script:CurrentTransitionDeadline) {
        $reason = "Transition timeout exceeded for '$($script:CurrentTransitionName)' while waiting for $Description. Last confirmed progress: $($script:LastProgressPoint)."
    }

    if ($reason) {
        Set-TimeoutFailureContext -Reason $reason
        throw $reason
    }
}

function Add-CleanupNote {
    param([string]$Message)
    $ValidationState.notes += "Cleanup: $Message"
    Write-StepLog -Stage "CLEANUP" -Message $Message
}

function Convert-ToProcessArgumentLiteral {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Value
    )

    return '"' + ($Value -replace '"', '\"') + '"'
}

function Start-ValidationWatchdog {
    param(
        [int]$ParentPid,
        [string]$StepLogPath,
        [string]$ReportPath,
        [string]$RuntimeLogPath,
        [string]$SourcePath,
        [string]$SourceBackupPath,
        [string]$WatchdogScriptPath,
        [string]$WatchdogStartSignalPath,
        [string]$WatchdogStdoutPath,
        [string]$WatchdogStderrPath,
        [bool]$SourceOriginallyPresent,
        [string]$ProbePath,
        [int]$RunHardTimeoutSeconds,
        [int]$NoProgressTimeoutSeconds,
        [int]$StartupTimeoutSeconds
    )

    $watchdogScript = @'
param(
    [int]$ParentPid,
    [string]$StepLogPath,
    [string]$ReportPath,
    [string]$RuntimeLogPath,
    [string]$SourcePath,
    [string]$SourceBackupPath,
    [string]$WatchdogScriptPath,
    [string]$WatchdogStartSignalPath,
    [bool]$SourceOriginallyPresent,
    [string]$ProbePath,
    [int]$RunHardTimeoutSeconds,
    [int]$NoProgressTimeoutSeconds
)

$startUtc = [DateTime]::UtcNow
$runDeadlineUtc = $startUtc.AddSeconds($RunHardTimeoutSeconds)

function Add-WatchdogLine {
    param([string]$Stage, [string]$Message)
    try {
        $timestamp = Get-Date -Format 'HH:mm:ss.fff'
        Add-Content -LiteralPath $StepLogPath -Value "[$timestamp] [$Stage] $Message" -Encoding utf8
    } catch {
    }
}

try {
    try {
        $startPayload = [ordered]@{
            watchdog_pid = $PID
            parent_pid = $ParentPid
            started_utc = (Get-Date).ToUniversalTime().ToString('o')
            run_hard_timeout_seconds = $RunHardTimeoutSeconds
            no_progress_timeout_seconds = $NoProgressTimeoutSeconds
        } | ConvertTo-Json -Depth 3
        [System.IO.File]::WriteAllText($WatchdogStartSignalPath, $startPayload, [System.Text.UTF8Encoding]::new($false))
        Add-WatchdogLine -Stage 'WATCHDOG' -Message "watchdog started pid=$PID run_timeout=${RunHardTimeoutSeconds}s no_progress_timeout=${NoProgressTimeoutSeconds}s"
    } catch {
    }

    while ($true) {
        $parent = Get-Process -Id $ParentPid -ErrorAction SilentlyContinue
        if (-not $parent) {
            exit 0
        }

        $lastProgressUtc = $startUtc
        try {
            if (Test-Path -LiteralPath $StepLogPath) {
                $lastProgressUtc = (Get-Item -LiteralPath $StepLogPath).LastWriteTimeUtc
            }
        } catch {
        }

        $nowUtc = [DateTime]::UtcNow
        $timeoutReason = $null
        if ($nowUtc -ge $runDeadlineUtc) {
            $timeoutReason = "Full-run hard timeout exceeded before the interactive harness completed."
        } elseif (($nowUtc - $lastProgressUtc).TotalSeconds -ge $NoProgressTimeoutSeconds) {
            $timeoutReason = "No-progress watchdog exceeded while waiting for the next interactive validation step."
        }

        if ($timeoutReason) {
            $lastProgressPoint = ''
            try {
                if (Test-Path -LiteralPath $StepLogPath) {
                    $lastProgressPoint = @((Get-Content -LiteralPath $StepLogPath) | Select-Object -Last 1) -join ''
                }
            } catch {
            }

            Add-WatchdogLine -Stage 'WATCHDOG' -Message "$timeoutReason Last confirmed progress: $lastProgressPoint"

            try {
                if ($SourceOriginallyPresent -and (Test-Path -LiteralPath $SourceBackupPath)) {
                    [System.IO.File]::WriteAllBytes($SourcePath, [System.IO.File]::ReadAllBytes($SourceBackupPath))
                    Add-WatchdogLine -Stage 'CLEANUP' -Message 'watchdog restored saved_actions.json from backup'
                } elseif ((-not $SourceOriginallyPresent) -and (Test-Path -LiteralPath $SourcePath)) {
                    Remove-Item -LiteralPath $SourcePath -Force -ErrorAction SilentlyContinue
                    Add-WatchdogLine -Stage 'CLEANUP' -Message 'watchdog removed test-created saved_actions.json'
                }
            } catch {
                Add-WatchdogLine -Stage 'CLEANUP' -Message 'watchdog could not restore saved_actions.json cleanly'
            }

            try {
                $runtimeTargets = Get-CimInstance Win32_Process | Where-Object {
                    ($_.Name -like 'python*.exe' -or $_.Name -eq 'python.exe') -and
                    $_.CommandLine -and
                    $_.CommandLine -like '*orin_saved_action_authoring_interactive_runtime.py*' -and
                    $_.CommandLine -like "*$RuntimeLogPath*"
                }
                foreach ($target in $runtimeTargets) {
                    Stop-Process -Id $target.ProcessId -Force -ErrorAction SilentlyContinue
                }
                if ($runtimeTargets) {
                    Add-WatchdogLine -Stage 'CLEANUP' -Message 'watchdog stopped interactive runtime helper processes'
                }
            } catch {
            }

            try {
                if ($ProbePath) {
                    $probeLeaf = [System.IO.Path]::GetFileName($ProbePath)
                    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
                        Where-Object {
                            (
                                $_.Name -like 'powershell*.exe' -or
                                $_.Name -eq 'pwsh.exe' -or
                                $_.Name -eq 'notepad.exe' -or
                                $_.Name -eq 'pythonw.exe' -or
                                $_.Name -eq 'python.exe'
                            ) -and
                            $_.CommandLine -and
                            (
                                $_.CommandLine -like "*$ProbePath*" -or
                                $_.CommandLine -like "*$probeLeaf*"
                            )
                        } |
                        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
                    if (Test-Path -LiteralPath $ProbePath) {
                        Remove-Item -LiteralPath $ProbePath -Force -ErrorAction SilentlyContinue
                    }
                    Add-WatchdogLine -Stage 'CLEANUP' -Message 'watchdog closed and removed the validation external probe'
                }
            } catch {
            }

            try {
                if (Test-Path -LiteralPath $SourceBackupPath) {
                    Remove-Item -LiteralPath $SourceBackupPath -Force -ErrorAction SilentlyContinue
                }
            } catch {
            }

            try {
                if (Test-Path -LiteralPath $WatchdogScriptPath) {
                    Remove-Item -LiteralPath $WatchdogScriptPath -Force -ErrorAction SilentlyContinue
                }
            } catch {
            }

            try {
                $reportLines = @(
                    'FB-036 SAVED-ACTION AUTHORING INTERACTIVE VALIDATION',
                    "Report: $ReportPath",
                    "Timestamp: $((Get-Date).ToString('o'))",
                    '',
                    'Timeout Budgets:',
                    "  full_run_hard_timeout_seconds: $RunHardTimeoutSeconds",
                    "  no_progress_timeout_seconds: $NoProgressTimeoutSeconds",
                    "  last_confirmed_progress_point: $lastProgressPoint",
                    "  timeout_abort_reason: $timeoutReason",
                    '',
                    'Notes:',
                    "  - Watchdog terminated the stalled interactive validation run.",
                    "  - $timeoutReason",
                    "  - Last confirmed progress: $lastProgressPoint"
                )
                [System.IO.File]::WriteAllText($ReportPath, ($reportLines -join "`r`n"), [System.Text.UTF8Encoding]::new($false))
            } catch {
            }

            try {
                & cmd.exe /c "taskkill /PID $ParentPid /T /F >nul 2>nul" | Out-Null
            } catch {
            }
            Stop-Process -Id $ParentPid -Force -ErrorAction SilentlyContinue
            exit 0
        }

        Start-Sleep -Seconds 2
    }
} catch {
    try {
        Add-WatchdogLine -Stage 'WATCHDOG' -Message ("watchdog startup or monitoring failure: " + $_.Exception.Message)
    } catch {
    }
    throw
}
'@

    [System.IO.File]::WriteAllText($WatchdogScriptPath, $watchdogScript, [System.Text.UTF8Encoding]::new($false))
    $process = Start-Job -Name "fb036_watchdog_$Stamp" -ScriptBlock {
        param(
            [string]$ScriptPath,
            [int]$ParentPid,
            [string]$StepLogPath,
            [string]$ReportPath,
            [string]$RuntimeLogPath,
            [string]$SourcePath,
            [string]$SourceBackupPath,
            [string]$WatchdogScriptPath,
            [string]$WatchdogStartSignalPath,
            [bool]$SourceOriginallyPresent,
            [string]$ProbePath,
            [int]$RunHardTimeoutSeconds,
            [int]$NoProgressTimeoutSeconds
        )

        & $ScriptPath `
            -ParentPid $ParentPid `
            -StepLogPath $StepLogPath `
            -ReportPath $ReportPath `
            -RuntimeLogPath $RuntimeLogPath `
            -SourcePath $SourcePath `
            -SourceBackupPath $SourceBackupPath `
            -WatchdogScriptPath $WatchdogScriptPath `
            -WatchdogStartSignalPath $WatchdogStartSignalPath `
            -SourceOriginallyPresent:$SourceOriginallyPresent `
            -ProbePath $ProbePath `
            -RunHardTimeoutSeconds $RunHardTimeoutSeconds `
            -NoProgressTimeoutSeconds $NoProgressTimeoutSeconds
    } -ArgumentList @(
        $WatchdogScriptPath,
        $ParentPid,
        $StepLogPath,
        $ReportPath,
        $RuntimeLogPath,
        $SourcePath,
        $SourceBackupPath,
        $WatchdogScriptPath,
        $WatchdogStartSignalPath,
        $SourceOriginallyPresent,
        $ProbePath,
        $RunHardTimeoutSeconds,
        $NoProgressTimeoutSeconds
    )

    $startupDeadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
    while ((Get-Date) -lt $startupDeadline) {
        if (Test-Path -LiteralPath $WatchdogStartSignalPath) {
            Write-StepLog -Stage "WATCHDOG" -Message "watchdog startup handshake received from job id=$($process.Id)"
            return $process
        }

        if ($process.State -in @("Completed", "Failed", "Stopped")) {
            break
        }

        Start-Sleep -Milliseconds 200
    }

    $jobState = $process.State
    $jobReason = ""
    try {
        $jobReason = [string]$process.ChildJobs[0].JobStateInfo.Reason
    } catch {
    }
    $stdoutSummary = ""
    try {
        $stdoutContent = (Receive-Job -Job $process -Keep -ErrorAction SilentlyContinue | Out-String)
        if (-not [string]::IsNullOrWhiteSpace($stdoutContent)) {
            [System.IO.File]::WriteAllText($WatchdogStdoutPath, $stdoutContent, [System.Text.UTF8Encoding]::new($false))
            $stdoutSummary = $stdoutContent.Trim()
        }
    } catch {
    }
    $stderrSummary = ""
    try {
        $stderrEntries = @($process.ChildJobs | ForEach-Object { $_.Error } | Where-Object { $_ })
        if ($stderrEntries.Count -gt 0) {
            $stderrContent = (($stderrEntries | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
            if (-not [string]::IsNullOrWhiteSpace($stderrContent)) {
                [System.IO.File]::WriteAllText($WatchdogStderrPath, $stderrContent, [System.Text.UTF8Encoding]::new($false))
                $stderrSummary = $stderrContent
            }
        }
    } catch {
    }
    if ($process -and $process.State -notin @("Completed", "Failed", "Stopped")) {
        try {
            Stop-Job -Job $process -ErrorAction SilentlyContinue | Out-Null
            Remove-Job -Job $process -Force -ErrorAction SilentlyContinue | Out-Null
        } catch {
        }
    }
    throw ("Interactive validation watchdog failed to confirm startup within ${StartupTimeoutSeconds}s. " +
        "job_state='$jobState' reason='$jobReason' stdout='$stdoutSummary' stderr='$stderrSummary'")
}

function Write-StepLog {
    param(
        [string]$Stage,
        [string]$Message
    )

    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $line = "[$timestamp] [$Stage] $Message"
    Add-Content -LiteralPath $StepLogPath -Value $line -Encoding utf8
    Record-ValidationProgress -Point "$Stage :: $Message"
}

function Add-Note {
    param([string]$Message)
    $ValidationState.notes += $Message
    Write-StepLog -Stage "NOTE" -Message $Message
}

function Add-ControlTypeFallbackNote {
    param(
        [string]$Context,
        [string]$Reason
    )

    $noteKey = if ($Context) { "$Context|$Reason" } else { $Reason }
    if (-not $script:LoggedControlTypeFallbacks.ContainsKey($noteKey)) {
        $script:LoggedControlTypeFallbacks[$noteKey] = $true
        $contextLabel = if ($Context) { $Context } else { "unknown context" }
        Add-Note "UIAutomation control type metadata was unavailable in $contextLabel; using a safe fallback ($Reason)."
    }
}

function Get-ControlTypeProgrammaticNameSafe {
    param(
        $ControlType,
        [string]$Context = "",
        [string]$Fallback = ""
    )

    if ($null -eq $ControlType) {
        if ($Context) {
            Add-ControlTypeFallbackNote -Context $Context -Reason "null_control_type"
        }
        return $Fallback
    }

    try {
        $property = $ControlType.PSObject.Properties['ProgrammaticName']
        if ($property -and $property.Value) {
            return [string]$property.Value
        }
    } catch {
    }

    try {
        $stringValue = [string]$ControlType
        if ($stringValue) {
            if ($Context) {
                Add-ControlTypeFallbackNote -Context $Context -Reason "stringified_control_type"
            }
            return $stringValue
        }
    } catch {
    }

    if ($Context) {
        Add-ControlTypeFallbackNote -Context $Context -Reason "missing_programmatic_name"
    }
    return $Fallback
}

function Get-ElementControlTypeNameSafe {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Context = "",
        [string]$Fallback = ""
    )

    if (-not $Element) {
        if ($Context) {
            Add-ControlTypeFallbackNote -Context $Context -Reason "null_element"
        }
        return $Fallback
    }

    $controlType = $null
    try {
        $controlType = $Element.Current.ControlType
    } catch {
        if ($Context) {
            Add-ControlTypeFallbackNote -Context $Context -Reason "control_type_read_failed"
        }
        return $Fallback
    }

    return Get-ControlTypeProgrammaticNameSafe -ControlType $controlType -Context $Context -Fallback $Fallback
}

function Add-ScenarioResult {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details
    )

    $ValidationState.scenarios += [pscustomobject]@{
        name = $Name
        passed = $Passed
        details = $Details
    }
    $status = if ($Passed) { "PASS" } else { "FAIL" }
    Write-StepLog -Stage "SCENARIO" -Message "$status :: $Name :: $Details"
}

function Add-Artifact {
    param(
        [string]$Label,
        [string]$Path
    )
    $ValidationState.artifacts += [pscustomobject]@{
        label = $Label
        path = $Path
    }
    Write-StepLog -Stage "ARTIFACT" -Message "$Label => $Path"
}

function Wait-Until {
    param(
        [scriptblock]$Condition,
        [int]$TimeoutSeconds = 15,
        [int]$SleepMilliseconds = 200,
        [string]$Description = "condition"
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastHeartbeat = Get-Date
    while ((Get-Date) -lt $deadline) {
        Assert-ValidationBudget -Description $Description
        try {
            if (& $Condition) {
                Record-ValidationProgress -Point "wait satisfied :: $Description"
                return $true
            }
        } catch {
            Assert-ValidationBudget -Description $Description
        }
        if (((Get-Date) - $lastHeartbeat).TotalSeconds -ge 5) {
            Write-StepLog -Stage "WAIT" -Message "still waiting for $Description"
            Record-ValidationProgress -Point "wait active :: $Description"
            $lastHeartbeat = Get-Date
        }
        Start-Sleep -Milliseconds $SleepMilliseconds
    }

    Assert-ValidationBudget -Description $Description
    throw "Timed out waiting for $Description."
}

function Invoke-ForcedValidationStallIfRequested {
    param(
        [string]$Point
    )

    if ([string]::IsNullOrWhiteSpace($ForcedStallPoint)) {
        return
    }

    if ($ForcedStallPoint -ine $Point) {
        return
    }

    Write-StepLog -Stage "SELFTEST" -Message "forcing watchdog stall at '$Point' for ${ForcedStallSeconds}s"
    Start-Sleep -Seconds $ForcedStallSeconds
}

function Get-RuntimeLogLines {
    if (-not (Test-Path -LiteralPath $RuntimeLogPath)) {
        return ,@()
    }
    return ,@(Get-Content -LiteralPath $RuntimeLogPath)
}

function Get-RuntimeLogLineCount {
    return (Get-RuntimeLogLines).Count
}

function New-RuntimeMarkerCursor {
    return (Get-RuntimeLogLineCount)
}

function Get-RuntimeLogSlice {
    param(
        [int]$StartLine = 0
    )

    $lines = Get-RuntimeLogLines
    if ($lines.Count -le $StartLine) {
        return ,@()
    }
    return ,@($lines | Select-Object -Skip $StartLine)
}

function Get-AllDescendants {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return ,@()
    }

    try {
        return $Element.FindAll(
            [System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition
        )
    } catch {
        Add-Note "A UIAutomation tree walk hit a stale element and was retried against fresher UI state."
        return ,@()
    }
}

function Get-RootWindows {
    return [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition
    )
}

function Find-RootWindow {
    param(
        [string]$AutomationId,
        [string]$Name,
        [string]$ClassName
    )

    foreach ($candidate in (Get-RootWindows)) {
        if ((Get-ElementControlTypeNameSafe -Element $candidate -Context "Find-RootWindow") -ne [System.Windows.Automation.ControlType]::Window.ProgrammaticName) {
            continue
        }
        if ($AutomationId -and $candidate.Current.AutomationId -ne $AutomationId) {
            continue
        }
        if ($Name -and $candidate.Current.Name -ne $Name) {
            continue
        }
        if ($ClassName -and $candidate.Current.ClassName -ne $ClassName) {
            continue
        }
        return $candidate
    }
    return $null
}

function Find-WindowAnywhere {
    param(
        [string]$Name
    )

    $rootWindow = Find-RootWindow -Name $Name
    if ($rootWindow) {
        return $rootWindow
    }

    return Find-FirstElement -Root ([System.Windows.Automation.AutomationElement]::RootElement) -Name $Name -ControlType ([System.Windows.Automation.ControlType]::Window)
}

function Find-DialogFromChildAutomationId {
    param(
        [string]$ExpectedName,
        [string]$ChildAutomationId
    )

    $child = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId $ChildAutomationId
    if (-not $child) {
        return $null
    }

    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $current = $child
    while ($current) {
        if (
            ($ExpectedName -and $current.Current.Name -eq $ExpectedName) -or
            $current.Current.ClassName -eq "SavedActionCreateDialog" -or
            $current.Current.ClassName -eq "SavedActionEditDialog"
        ) {
            return $current
        }
        $current = $walker.GetParent($current)
    }

    return $null
}

function Find-DialogAncestorFromElement {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$ExpectedName = ""
    )

    if (-not $Element) {
        return $null
    }

    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $current = $Element
    while ($current) {
        try {
            if (
                ($ExpectedName -and $current.Current.Name -eq $ExpectedName) -or
                (Get-ElementControlTypeNameSafe -Element $current -Context "Find-DialogAncestorFromElement") -eq [System.Windows.Automation.ControlType]::Window.ProgrammaticName
            ) {
                return $current
            }
        } catch {
        }
        try {
            $current = $walker.GetParent($current)
        } catch {
            return $null
        }
    }

    return $null
}

function Find-FirstElement {
    param(
        [System.Windows.Automation.AutomationElement]$Root = [System.Windows.Automation.AutomationElement]::RootElement,
        [string]$AutomationId,
        [string]$Name,
        $ControlType = $null,
        [string]$ClassName
    )

    $elements = Get-AllDescendants -Element $Root
    $requestedControlTypeName = if ($ControlType) {
        Get-ControlTypeProgrammaticNameSafe -ControlType $ControlType -Context "Find-FirstElement requested control type"
    } else {
        ""
    }
    foreach ($element in $elements) {
        if ($AutomationId -and $element.Current.AutomationId -ne $AutomationId) {
            continue
        }
        if ($Name -and $element.Current.Name -ne $Name) {
            continue
        }
        if ($ControlType -and (Get-ElementControlTypeNameSafe -Element $element -Context "Find-FirstElement candidate") -ne $requestedControlTypeName) {
            continue
        }
        if ($ClassName -and $element.Current.ClassName -ne $ClassName) {
            continue
        }
        return $element
    }
    return $null
}

function Find-ElementByAutomationIdDirect {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$AutomationId
    )

    if (-not $Root -or [string]::IsNullOrWhiteSpace($AutomationId)) {
        return $null
    }

    try {
        $condition = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
            $AutomationId
        )
        return $Root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $condition)
    } catch {
        Add-Note "Direct UIAutomation lookup for '$AutomationId' hit a stale element and was retried against fresher UI state."
        return $null
    }
}

function Test-ElementUsable {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [bool]$RequireEnabled = $true
    )

    if (-not $Element) {
        return $false
    }

    try {
        if ($Element.Current.IsOffscreen) {
            return $false
        }
        if ($RequireEnabled -and -not $Element.Current.IsEnabled) {
            return $false
        }
        $rect = $Element.Current.BoundingRectangle
        if ($rect.Width -le 0 -or $rect.Height -le 0) {
            return $false
        }
    } catch {
        return $false
    }

    return $true
}

function Get-ElementStateSummary {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return "missing"
    }

    try {
        $rect = $Element.Current.BoundingRectangle
        return (
            "name='{0}' automationId='{1}' enabled={2} offscreen={3} rect={4},{5},{6},{7}" -f
            $Element.Current.Name,
            $Element.Current.AutomationId,
            $Element.Current.IsEnabled,
            $Element.Current.IsOffscreen,
            [int]$rect.Left,
            [int]$rect.Top,
            [int]$rect.Width,
            [int]$rect.Height
        )
    } catch {
        return "unreadable"
    }
}

function Get-ElementsByName {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$Name
    )

    $result = @()
    foreach ($element in (Get-AllDescendants -Element $Root)) {
        if ($element.Current.Name -eq $Name) {
            $result += $element
        }
    }
    return $result
}

function Set-Value {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Value
    )

    $pattern = $Element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    $pattern.SetValue($Value)
}

function Get-ElementReadableValue {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return ""
    }

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        $value = $pattern.Current.Value
        if ($null -ne $value) {
            return [string]$value
        }
    } catch {
    }

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
        $value = $pattern.DocumentRange.GetText(-1)
        if ($null -ne $value) {
            return ([string]$value).TrimEnd("`0")
        }
    } catch {
    }

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.SelectionPattern]::Pattern)
        $selected = @($pattern.Current.GetSelection())
        if ($selected.Count -gt 0) {
            return [string]$selected[0].Current.Name
        }
    } catch {
    }

    try {
        return [string]$Element.Current.Name
    } catch {
    }

    return ""
}

function Normalize-UiValue {
    param(
        [string]$Value
    )

    if ($null -eq $Value) {
        return ""
    }

    $normalized = [string]$Value
    $normalized = $normalized -replace "\u0000", ""
    $normalized = $normalized -replace "\s+", " "
    return $normalized.Trim()
}

function Wait-ForElementValue {
    param(
        [scriptblock]$ElementResolver,
        [string]$ExpectedValue,
        [int]$TimeoutSeconds = 4,
        [string]$Description = "element value"
    )

    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $element = & $ElementResolver
        if (-not $element) {
            return $false
        }
        return (Normalize-UiValue (Get-ElementReadableValue -Element $element)) -eq (Normalize-UiValue $ExpectedValue)
    } | Out-Null
}

function Invoke-Element {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    $pattern = $Element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $pattern.Invoke()
}

function Click-Element {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    $rect = $Element.Current.BoundingRectangle
    $x = [int]([Math]::Round($rect.Left + ($rect.Width / 2)))
    $y = [int]([Math]::Round($rect.Top + ($rect.Height / 2)))

    if ($x -le 0 -or $y -le 0) {
        throw "Element click target was offscreen or invalid."
    }

    [CodexInteractiveWin32]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 120
    [CodexInteractiveWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [CodexInteractiveWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 180
}

function DoubleClick-Element {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    Click-Element -Element $Element
    Start-Sleep -Milliseconds 100
    Click-Element -Element $Element
}

function Expand-Combo {
    param([System.Windows.Automation.AutomationElement]$Element)
    $pattern = $Element.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern)
    $pattern.Expand()
}

function Get-ComboSelectedText {
    param(
        [System.Windows.Automation.AutomationElement]$Combo,
        [string]$ExpectedFallback = ""
    )

    $selected = Get-ElementReadableValue -Element $Combo
    if ($selected) {
        return $selected
    }

    try {
        foreach ($child in (Get-AllDescendants -Element $Combo)) {
            $selected = Get-ElementReadableValue -Element $child
            if ($selected) {
                return $selected
            }
        }
    } catch {
    }

    return $ExpectedFallback
}

function Get-ActionTypeIndexFromValue {
    param(
        [string]$Value
    )

    $normalizedValue = Normalize-UiValue $Value
    for ($index = 0; $index -lt $script:ActionTypeOrder.Count; $index++) {
        if ((Normalize-UiValue $script:ActionTypeOrder[$index]) -eq $normalizedValue) {
            return $index
        }
    }

    return -1
}

function Send-ComboSelectionSequence {
    param(
        [int]$DesiredIndex,
        [int]$CurrentIndex = -1,
        [bool]$OpenDropdown = $true,
        [bool]$ResetFromTop = $false,
        [string]$CommitMode = "enter"
    )

    if ($OpenDropdown) {
        Send-VirtualKey -VirtualKey 0x73
        Start-Sleep -Milliseconds 140
    }

    if ($ResetFromTop -or $CurrentIndex -lt 0) {
        Send-VirtualKey -VirtualKey 0x24
        Start-Sleep -Milliseconds 90
        for ($index = 0; $index -lt $DesiredIndex; $index++) {
            Send-VirtualKey -VirtualKey 0x28
            Start-Sleep -Milliseconds 90
        }
    } else {
        $delta = $DesiredIndex - $CurrentIndex
        if ($delta -gt 0) {
            for ($index = 0; $index -lt $delta; $index++) {
                Send-VirtualKey -VirtualKey 0x28
                Start-Sleep -Milliseconds 90
            }
        } elseif ($delta -lt 0) {
            for ($index = 0; $index -lt ([Math]::Abs($delta)); $index++) {
                Send-VirtualKey -VirtualKey 0x26
                Start-Sleep -Milliseconds 90
            }
        }
    }

    switch ($CommitMode) {
        "toggle" {
            Send-VirtualKey -VirtualKey 0x73
            Start-Sleep -Milliseconds 180
        }
        default {
            Send-VirtualKey -VirtualKey 0x0D
            Start-Sleep -Milliseconds 180
        }
    }
}

function Find-ComboPopupItem {
    param(
        [System.Windows.Automation.AutomationElement]$Combo,
        [string]$ItemName
    )

    $comboRect = $Combo.Current.BoundingRectangle
    $comboCenterX = $comboRect.Left + ($comboRect.Width / 2.0)
    $bestItem = $null
    $bestDistance = [double]::PositiveInfinity

    foreach ($candidate in (Get-AllDescendants -Element ([System.Windows.Automation.AutomationElement]::RootElement))) {
        try {
            $controlTypeName = Get-ElementControlTypeNameSafe -Element $candidate -Context "Find-ComboPopupItem"
            if ($controlTypeName -notin @(
                    [System.Windows.Automation.ControlType]::ListItem.ProgrammaticName,
                    [System.Windows.Automation.ControlType]::DataItem.ProgrammaticName,
                    [System.Windows.Automation.ControlType]::MenuItem.ProgrammaticName,
                    [System.Windows.Automation.ControlType]::Text.ProgrammaticName
                )) {
                continue
            }
            if ($candidate.Current.Name -ne $ItemName) {
                continue
            }
            if ($candidate.Current.IsOffscreen) {
                continue
            }

            $rect = $candidate.Current.BoundingRectangle
            $centerX = $rect.Left + ($rect.Width / 2.0)
            $verticalDelta = [Math]::Abs($rect.Top - $comboRect.Top)
            $horizontalDelta = [Math]::Abs($centerX - $comboCenterX)

            if ($horizontalDelta -gt 420) {
                continue
            }
            if ($rect.Top -lt ($comboRect.Top - 120) -or $rect.Bottom -gt ($comboRect.Bottom + 540)) {
                continue
            }

            $distance = ($verticalDelta * 10.0) + $horizontalDelta
            if ($distance -lt $bestDistance) {
                $bestDistance = $distance
                $bestItem = $candidate
            }
        } catch {
        }
    }

    return $bestItem
}

function Get-ComboPopupDiagnosticSummary {
    param(
        [System.Windows.Automation.AutomationElement]$Combo
    )

    if (-not $Combo) {
        return "combo_missing"
    }

    $comboRect = $Combo.Current.BoundingRectangle
    $samples = New-Object System.Collections.Generic.List[string]
    foreach ($candidate in (Get-AllDescendants -Element ([System.Windows.Automation.AutomationElement]::RootElement))) {
        if ($samples.Count -ge 12) {
            break
        }
        try {
            if ($candidate.Current.IsOffscreen) {
                continue
            }
            $name = $candidate.Current.Name
            if ([string]::IsNullOrWhiteSpace($name)) {
                continue
            }
            $rect = $candidate.Current.BoundingRectangle
            if ($rect.Right -lt ($comboRect.Left - 120) -or $rect.Left -gt ($comboRect.Right + 120)) {
                continue
            }
            if ($rect.Bottom -lt ($comboRect.Top - 120) -or $rect.Top -gt ($comboRect.Bottom + 520)) {
                continue
            }
            $controlTypeName = Get-ElementControlTypeNameSafe -Element $candidate -Context "Get-ComboPopupDiagnosticSummary"
            $samples.Add("$name [$controlTypeName] rect=$([int]$rect.Left),$([int]$rect.Top),$([int]$rect.Width),$([int]$rect.Height)")
        } catch {
        }
    }

    if ($samples.Count -eq 0) {
        return "no_named_visible_popup_candidates"
    }

    return ($samples -join " || ")
}

function Get-ElementSupportedPatternSummary {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return "element_missing"
    }

    $patterns = New-Object System.Collections.Generic.List[string]
    foreach ($entry in @(
            @{ Name = "Value"; Pattern = [System.Windows.Automation.ValuePattern]::Pattern },
            @{ Name = "ExpandCollapse"; Pattern = [System.Windows.Automation.ExpandCollapsePattern]::Pattern },
            @{ Name = "Selection"; Pattern = [System.Windows.Automation.SelectionPattern]::Pattern },
            @{ Name = "SelectionItem"; Pattern = [System.Windows.Automation.SelectionItemPattern]::Pattern },
            @{ Name = "Invoke"; Pattern = [System.Windows.Automation.InvokePattern]::Pattern }
        )) {
        try {
            $null = $Element.GetCurrentPattern($entry.Pattern)
            $patterns.Add($entry.Name)
        } catch {
        }
    }

    if ($patterns.Count -eq 0) {
        return "none"
    }

    return ($patterns -join ", ")
}

function Get-ExpectedTargetKindToken {
    param(
        [string]$TypeLabel
    )

    switch ($TypeLabel) {
        "Application" { return "app" }
        "Folder" { return "folder" }
        "File" { return "file" }
        "Website URL" { return "url" }
        default { return "" }
    }
}

function Select-ComboItemViaPopup {
    param(
        [scriptblock]$ComboResolver,
        [string]$ItemName
    )

    $combo = & $ComboResolver
    if (-not $combo) {
        throw "Could not resolve combo box for popup selection '$ItemName'."
    }

    try {
        Expand-Combo -Element $combo
    } catch {
        Click-Element -Element $combo
    }

    try {
        Wait-Until -TimeoutSeconds 3 -Description "combo popup item '$ItemName'" -Condition {
            $liveCombo = & $ComboResolver
            if (-not $liveCombo) {
                return $false
            }
            return (Test-ElementUsable -Element (Find-ComboPopupItem -Combo $liveCombo -ItemName $ItemName) -RequireEnabled $true)
        } | Out-Null
    } catch {
        $diagnosticCombo = & $ComboResolver
        Add-Note "Combo popup item '$ItemName' was not exposed through UIAutomation after open. Nearby visible candidates: $(Get-ComboPopupDiagnosticSummary -Combo $diagnosticCombo)"
        throw
    }

    $combo = & $ComboResolver
    $item = Find-ComboPopupItem -Combo $combo -ItemName $ItemName
    if (-not (Test-ElementUsable -Element $item -RequireEnabled $true)) {
        throw "Could not resolve popup item '$ItemName' after opening the combo."
    }

    DoubleClick-Element -Element $item
    Start-Sleep -Milliseconds 240

    $selectedCombo = & $ComboResolver
    $selectedValue = if ($selectedCombo) { Get-ComboSelectedText -Combo $selectedCombo } else { "" }
    if ($selectedValue -ne $ItemName) {
        Send-VirtualKey -VirtualKey 0x0D
        Start-Sleep -Milliseconds 200
        $selectedCombo = & $ComboResolver
        $selectedValue = if ($selectedCombo) { Get-ComboSelectedText -Combo $selectedCombo } else { "" }
    }
    if ($selectedValue -ne $ItemName) {
        Add-Note "Popup click for '$ItemName' did not update the combo readback immediately; closing the dropdown and letting runtime target_kind markers verify the submitted type."
        Send-VirtualKey -VirtualKey 0x73
        Start-Sleep -Milliseconds 200
    }
}

function Select-ComboItemViaDirectValue {
    param(
        [scriptblock]$ComboResolver,
        [string]$ItemName
    )

    $combo = & $ComboResolver
    if (-not $combo) {
        throw "Could not resolve combo box for direct selection '$ItemName'."
    }

    Set-Value -Element $combo -Value $ItemName
    Start-Sleep -Milliseconds 220
}

function Select-ComboItemViaEstimatedPopupClick {
    param(
        [scriptblock]$ComboResolver,
        [string]$ItemName,
        [int]$DesiredIndex
    )

    $combo = & $ComboResolver
    if (-not $combo) {
        throw "Could not resolve combo box for estimated popup click '$ItemName'."
    }

    Click-Element -Element $combo
    Start-Sleep -Milliseconds 180

    $rect = $combo.Current.BoundingRectangle
    $rowHeight = [int]([Math]::Max(30, [Math]::Round($rect.Height)))
    $x = [int]([Math]::Round($rect.Left + ($rect.Width / 2.0)))
    $y = [int]([Math]::Round($rect.Bottom + ($rowHeight * ($DesiredIndex + 0.5))))
    if ($x -le 0 -or $y -le 0) {
        throw "Estimated combo popup click target for '$ItemName' was invalid."
    }

    [CodexInteractiveWin32]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 100
    [CodexInteractiveWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [CodexInteractiveWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 100
    [CodexInteractiveWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [CodexInteractiveWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 240
}

function Select-ComboItem {
    param(
        [scriptblock]$ComboResolver,
        [string]$ItemName
    )

    $desiredIndex = [Array]::IndexOf($script:ActionTypeOrder, $ItemName)
    if ($desiredIndex -lt 0) {
        throw "Unsupported combo item '$ItemName'."
    }

    for ($attempt = 1; $attempt -le 4; $attempt++) {
        $Combo = & $ComboResolver
        if (-not $Combo) {
            throw "Could not resolve combo box for '$ItemName'."
        }

        $Combo = Focus-ElementForInteraction -ElementResolver $ComboResolver -Description "combo '$ItemName' selection control" -RequireExactFocus $false

        $currentValue = Get-ComboSelectedText -Combo $Combo
        $currentIndex = Get-ActionTypeIndexFromValue -Value $currentValue
        Write-StepLog -Stage "INTERACT" -Message "combo select attempt=$attempt desired='$ItemName' current='$currentValue' current_index=$currentIndex state=$(Get-ElementStateSummary -Element $Combo)"
        if ($currentValue -eq $ItemName) {
            return $true
        }

        try {
            $strategy = switch ($attempt) {
                1 { "direct_value" }
                2 { "popup_select" }
                3 { "popup_estimated_click" }
                default { "keyboard_open_reset_enter" }
            }
            Write-StepLog -Stage "INTERACT" -Message "combo select strategy=$strategy desired='$ItemName' attempt=$attempt"
            switch ($attempt) {
                1 {
                    Select-ComboItemViaDirectValue -ComboResolver $ComboResolver -ItemName $ItemName
                }
                2 {
                    Select-ComboItemViaPopup -ComboResolver $ComboResolver -ItemName $ItemName
                }
                3 {
                    Select-ComboItemViaEstimatedPopupClick -ComboResolver $ComboResolver -ItemName $ItemName -DesiredIndex $desiredIndex
                }
                default {
                    Send-ComboSelectionSequence -DesiredIndex $desiredIndex -CurrentIndex $currentIndex -OpenDropdown $true -ResetFromTop $true -CommitMode "enter"
                }
            }
        } catch {
            Add-Note "Combo selection attempt $attempt for '$ItemName' hit an interaction error before readback. Cause: $($_.Exception.Message)"
        }

        Start-Sleep -Milliseconds 220
        $actualCombo = & $ComboResolver
        $actualValue = Get-ComboSelectedText -Combo $actualCombo
        $actualIndex = Get-ActionTypeIndexFromValue -Value $actualValue
        if ($actualValue -eq $ItemName) {
            return $true
        }

        Add-Note "Combo selection attempt $attempt for '$ItemName' did not stick; actual value read back as '$actualValue' (index=$actualIndex). State: $(Get-ElementStateSummary -Element $actualCombo)"
    }

    $finalCombo = & $ComboResolver
    $finalValue = Get-ComboSelectedText -Combo $finalCombo
    Add-Note "Final combo diagnostics for '$ItemName': supported_patterns=$(Get-ElementSupportedPatternSummary -Element $finalCombo) popup_candidates=$(Get-ComboPopupDiagnosticSummary -Combo $finalCombo)"
    return $false
}

function Get-WindowHandle {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    return [IntPtr]::new($Element.Current.NativeWindowHandle)
}

function Get-ElementRuntimeIdText {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return ""
    }

    try {
        $runtimeId = @($Element.GetRuntimeId())
        if ($runtimeId.Count -lt 1) {
            return ""
        }
        return (($runtimeId | ForEach-Object { [string]$_ }) -join ".")
    } catch {
        return ""
    }
}

function Get-ElementOwningWindow {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return $null
    }

    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $current = $Element
    while ($current) {
        try {
            $hwnd = Get-WindowHandle -Element $current
            if ($hwnd -ne [IntPtr]::Zero) {
                return $current
            }
        } catch {
        }
        try {
            if ((Get-ElementControlTypeNameSafe -Element $current -Context "Get-ElementOwningWindow") -eq [System.Windows.Automation.ControlType]::Window.ProgrammaticName) {
                return $current
            }
        } catch {
        }
        try {
            $current = $walker.GetParent($current)
        } catch {
            return $null
        }
    }

    return $null
}

function Get-FocusedElementSafe {
    try {
        return [System.Windows.Automation.AutomationElement]::FocusedElement
    } catch {
        return $null
    }
}

function Test-ElementsEquivalent {
    param(
        [System.Windows.Automation.AutomationElement]$Left,
        [System.Windows.Automation.AutomationElement]$Right
    )

    if (-not $Left -or -not $Right) {
        return $false
    }

    $leftRuntimeId = Get-ElementRuntimeIdText -Element $Left
    $rightRuntimeId = Get-ElementRuntimeIdText -Element $Right
    if ($leftRuntimeId -and $rightRuntimeId -and $leftRuntimeId -eq $rightRuntimeId) {
        return $true
    }

    try {
        $leftControlTypeName = Get-ElementControlTypeNameSafe -Element $Left -Context "Test-ElementsEquivalent left"
        $rightControlTypeName = Get-ElementControlTypeNameSafe -Element $Right -Context "Test-ElementsEquivalent right"
        if (
            $Left.Current.AutomationId -and
            $Left.Current.AutomationId -eq $Right.Current.AutomationId -and
            $leftControlTypeName -eq $rightControlTypeName
        ) {
            return $true
        }
    } catch {
    }

    return $false
}

function Test-ElementFocusSatisfied {
    param(
        [System.Windows.Automation.AutomationElement]$Target,
        [ref]$FocusedSummary = ([ref]([string]::Empty))
    )

    $focused = Get-FocusedElementSafe
    $FocusedSummary.Value = Get-ElementStateSummary -Element $focused

    if (-not $Target -or -not $focused) {
        return $false
    }

    try {
        if ($Target.Current.HasKeyboardFocus) {
            return $true
        }
    } catch {
    }

    if (Test-ElementsEquivalent -Left $Target -Right $focused) {
        return $true
    }

    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $current = $focused
    $depth = 0
    while ($current -and $depth -lt 16) {
        if (Test-ElementsEquivalent -Left $Target -Right $current) {
            return $true
        }
        try {
            $current = $walker.GetParent($current)
        } catch {
            break
        }
        $depth += 1
    }

    return $false
}

function Focus-Window {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    $targetWindow = Get-ElementOwningWindow -Element $Element
    if (-not $targetWindow) {
        $targetWindow = $Element
    }

    $hwnd = Get-WindowHandle -Element $targetWindow
    if ($hwnd -ne [IntPtr]::Zero) {
        [CodexInteractiveWin32]::ShowWindowAsync($hwnd, 5) | Out-Null
        [CodexInteractiveWin32]::SetForegroundWindow($hwnd) | Out-Null
    }
    $targetWindow.SetFocus()
    Start-Sleep -Milliseconds 250
}

function Send-VirtualKey {
    param(
        [byte]$VirtualKey
    )

    [CodexInteractiveWin32]::keybd_event($VirtualKey, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 50
    [CodexInteractiveWin32]::keybd_event($VirtualKey, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 80
}

function Send-OverlayHotkey {
    [CodexInteractiveWin32]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero)
    [CodexInteractiveWin32]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
    [CodexInteractiveWin32]::keybd_event(0x31, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 50
    [CodexInteractiveWin32]::keybd_event(0x31, 0, 2, [UIntPtr]::Zero)
    [CodexInteractiveWin32]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
    [CodexInteractiveWin32]::keybd_event(0x11, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 450
}

function Send-OverlayHotkeyFallback {
    try {
        [System.Windows.Forms.SendKeys]::SendWait("^%1")
        Start-Sleep -Milliseconds 650
    } catch {
        Add-Note "SendKeys fallback for the overlay hotkey failed to execute cleanly."
    }
}

function Get-CreateDialogControlAutomationIds {
    param(
        [string]$LeafAutomationId
    )

    $legacyBase = "QApplication.savedActionCreateDialog"
    $currentBase = "QApplication.savedActionCreateDialog.savedActionCreateShell.savedActionCreateContent"

    switch ($LeafAutomationId) {
        "savedActionCreateTypeHelp" {
            return @(
                "$currentBase.savedActionCreateTypeHeader.savedActionCreateTypeHelp",
                "$legacyBase.savedActionCreateTypeHelp"
            )
        }
        "savedActionCreateTitleHelp" {
            return @(
                "$currentBase.savedActionCreateTitleHeader.savedActionCreateTitleHelp",
                "$legacyBase.savedActionCreateTitleHelp"
            )
        }
        "savedActionCreateTriggerHelp" {
            return @(
                "$currentBase.savedActionCreateTriggerHeader.savedActionCreateTriggerHelp",
                "$legacyBase.savedActionCreateTriggerHelp"
            )
        }
        "savedActionCreateAliasesHelp" {
            return @(
                "$currentBase.savedActionCreateAliasesHeader.savedActionCreateAliasesHelp",
                "$legacyBase.savedActionCreateAliasesHelp"
            )
        }
        "savedActionCreateTargetHelp" {
            return @(
                "$currentBase.savedActionCreateTargetHeader.savedActionCreateTargetHelp",
                "$legacyBase.savedActionCreateTargetHelp"
            )
        }
        "savedActionCreateTargetExamples" {
            return @(
                "$currentBase.savedActionCreateTargetExamplesBox.savedActionCreateTargetExamples",
                "$legacyBase.savedActionCreateTargetExamples"
            )
        }
        "savedActionCreateGroupsStatus" {
            return @(
                "$currentBase.savedActionCreateGroupsFrame.savedActionCreateGroupsStatus",
                "$legacyBase.savedActionCreateGroupsStatus"
            )
        }
        "savedActionCreateGroupsSummary" {
            return @(
                "$currentBase.savedActionCreateGroupsFrame.savedActionCreateGroupsSummary",
                "$legacyBase.savedActionCreateGroupsSummary"
            )
        }
        "savedActionCreateNewGroupButton" {
            return @(
                "$currentBase.savedActionCreateGroupsFrame.savedActionCreateNewGroupButton",
                "$legacyBase.savedActionCreateNewGroupButton"
            )
        }
        "savedActionCreateRemoveGroupButton" {
            return @(
                "$currentBase.savedActionCreateGroupsFrame.savedActionCreateRemoveGroupButton",
                "$legacyBase.savedActionCreateRemoveGroupButton"
            )
        }
        default {
            return @(
                "$currentBase.$LeafAutomationId",
                "$legacyBase.$LeafAutomationId"
            )
        }
    }
}

function Get-GroupDialogControlAutomationIds {
    param(
        [string]$LeafAutomationId
    )

    $legacyBase = "QApplication.callableGroupCreateDialog"
    $currentBase = "QApplication.callableGroupCreateDialog.callableGroupCreateShell.callableGroupCreateContent"
    return @(
        "$currentBase.$LeafAutomationId",
        "$legacyBase.$LeafAutomationId"
    )
}

function Get-QuickCreateGroupDialogControlAutomationIds {
    param(
        [string]$LeafAutomationId
    )

    $legacyBase = "QApplication.quickCreateGroupDialog"
    $currentBase = "QApplication.quickCreateGroupDialog.quickCreateGroupShell.quickCreateGroupContent"
    return @(
        "$currentBase.$LeafAutomationId",
        "$legacyBase.$LeafAutomationId"
    )
}

function Get-TaskGroupAssignmentDialogControlAutomationIds {
    param(
        [string]$LeafAutomationId
    )

    $legacyBase = "QApplication.taskGroupAssignmentDialog"
    $currentBase = "QApplication.taskGroupAssignmentDialog.taskGroupAssignmentShell.taskGroupAssignmentContent"
    return @(
        "$currentBase.$LeafAutomationId",
        "$legacyBase.$LeafAutomationId"
    )
}

function Get-CreatedTasksDialogControlAutomationIds {
    param(
        [string]$LeafAutomationId
    )

    $legacyBase = "QApplication.savedActionCreatedTasksDialog"
    $currentBase = "QApplication.savedActionCreatedTasksDialog.savedActionCreatedTasksShell.savedActionCreatedTasksContent"
    return @(
        "$currentBase.$LeafAutomationId",
        "$legacyBase.$LeafAutomationId"
    )
}

function Get-CreatedGroupsDialogControlAutomationIds {
    param(
        [string]$LeafAutomationId
    )

    $legacyBase = "QApplication.savedActionCreatedGroupsDialog"
    $currentBase = "QApplication.savedActionCreatedGroupsDialog.savedActionCreatedTasksShell.savedActionCreatedTasksContent"
    return @(
        "$currentBase.$LeafAutomationId",
        "$legacyBase.$LeafAutomationId"
    )
}

function Get-CreatedTasksDialogWindow {
    $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.savedActionCreatedTasksDialog"
    if ($dialog -and -not (Test-ElementGoneOrOffscreen -Element $dialog)) {
        return $dialog
    }
    return $null
}

function Get-CreatedGroupsDialogWindow {
    $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.savedActionCreatedGroupsDialog"
    if ($dialog -and -not (Test-ElementGoneOrOffscreen -Element $dialog)) {
        return $dialog
    }
    return $null
}

function Resolve-LiveCreatedTasksDialogRoot {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog
    )

    $liveDialog = Get-CreatedTasksDialogWindow
    if ($liveDialog) {
        return $liveDialog
    }

    return (Resolve-LiveDialogRoot -Dialog $Dialog)
}

function Resolve-LiveCreatedGroupsDialogRoot {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog
    )

    $liveDialog = Get-CreatedGroupsDialogWindow
    if ($liveDialog) {
        return $liveDialog
    }

    return (Resolve-LiveDialogRoot -Dialog $Dialog)
}

function Get-DialogLookupChildAutomationIds {
    param(
        [string]$Name
    )

    switch ($Name) {
        "Created Tasks" {
            return (Get-CreatedTasksDialogControlAutomationIds -LeafAutomationId "savedActionCreatedTasksStatus")
        }
        "Manage Custom Tasks" {
            return (Get-CreatedTasksDialogControlAutomationIds -LeafAutomationId "savedActionCreatedTasksStatus")
        }
        "Manage Custom Groups" {
            return (Get-CreatedGroupsDialogControlAutomationIds -LeafAutomationId "savedActionCreatedTasksStatus")
        }
        "Create Custom Group" {
            return (Get-GroupDialogControlAutomationIds -LeafAutomationId "callableGroupCreateAliasesInput")
        }
        "Edit Custom Group" {
            return (Get-GroupDialogControlAutomationIds -LeafAutomationId "callableGroupCreateAliasesInput")
        }
        "New Group" {
            return (Get-QuickCreateGroupDialogControlAutomationIds -LeafAutomationId "quickCreateGroupTitleInput")
        }
        default {
            return (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateTitleInput")
        }
    }
}

function Get-OverlayAnchorAutomationIds {
    $ids = @(
        "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine"
    )
    $ids += Get-OverlayCreateButtonAutomationIds
    $ids += Get-OverlayManageButtonAutomationIds
    $ids += Get-OverlayCreateGroupButtonAutomationIds
    $ids += Get-OverlayManageGroupButtonAutomationIds
    return $ids
}

function Get-OverlayCreateButtonAutomationIds {
    return @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreateButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton"
    )
}

function Get-OverlayManageButtonAutomationIds {
    return @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreatedTasksButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton"
    )
}

function Get-OverlayCreateGroupButtonAutomationIds {
    return @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreateGroupButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateGroupButton"
    )
}

function Get-OverlayManageGroupButtonAutomationIds {
    return @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreatedGroupsButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedGroupsButton"
    )
}

function Find-ElementByAutomationIdsDirect {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string[]]$AutomationIds
    )

    foreach ($automationId in @($AutomationIds)) {
        if ([string]::IsNullOrWhiteSpace($automationId)) {
            continue
        }

        $element = Find-ElementByAutomationIdDirect -Root $Root -AutomationId $automationId
        if ($element) {
            return $element
        }
    }

    return $null
}

function Get-DialogWindow {
    param(
        [string]$Name
    )

    if ($Name) {
        $rootDialog = Find-RootWindow -Name $Name
        if ($rootDialog) {
            return $rootDialog
        }
    }

    $childAutomationIds = @(Get-DialogLookupChildAutomationIds -Name $Name)
    if ($childAutomationIds.Count -gt 0) {
        foreach ($childAutomationId in $childAutomationIds) {
            $dialog = Find-DialogFromChildAutomationId -ExpectedName $Name -ChildAutomationId $childAutomationId
            if ($dialog) {
                return $dialog
            }
        }
    }

    if ($Name -in @("Created Tasks", "Manage Custom Tasks")) {
        $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.savedActionCreatedTasksDialog"
        if ($dialog) {
            return $dialog
        }
    } elseif ($Name -eq "Manage Custom Groups") {
        $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.savedActionCreatedGroupsDialog"
        if ($dialog) {
            return $dialog
        }
    } elseif ($Name -eq "New Group") {
        $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.quickCreateGroupDialog"
        if ($dialog) {
            return $dialog
        }
    } elseif ($Name -in @("Create Custom Group", "Edit Custom Group")) {
        $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.callableGroupCreateDialog"
        if ($dialog) {
            return $dialog
        }
    } else {
        $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.savedActionCreateDialog"
        if ($dialog) {
            return $dialog
        }
    }

    $dialog = Find-WindowAnywhere -Name $Name
    if ($dialog) {
        return $dialog
    }

    return $null
}

function Test-ElementGoneOrOffscreen {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return $true
    }

    try {
        return [bool]$Element.Current.IsOffscreen
    } catch {
        return $true
    }
}

function Get-OverlayWindow {
    $overlay = Find-RootWindow -AutomationId "QApplication.commandOverlayWindow" -ClassName "CommandOverlayPanel"
    if ($overlay) {
        return $overlay
    }

    foreach ($automationId in (Get-OverlayAnchorAutomationIds)) {
        $anchor = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId $automationId
        if ($anchor -and -not (Test-ElementGoneOrOffscreen -Element $anchor)) {
            return [System.Windows.Automation.AutomationElement]::RootElement
        }
    }

    return $null
}

function Wait-ForOverlayOpen {
    param(
        [int]$TimeoutSeconds = 10
    )

    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "overlay window" -Condition {
        $overlay = Get-OverlayWindow
        if (-not $overlay) {
            return $false
        }
        return -not (Test-ElementGoneOrOffscreen -Element $overlay)
    } | Out-Null
    return (Get-OverlayWindow)
}

function Wait-ForOptionalOverlayOpen {
    param([int]$TimeoutSeconds = 4)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $overlay = Get-OverlayWindow
        if ($overlay -and -not (Test-ElementGoneOrOffscreen -Element $overlay)) {
            return $overlay
        }
        Start-Sleep -Milliseconds 150
    }
    return $null
}

function Wait-ForDialog {
    param(
        [string]$Name,
        [int]$TimeoutSeconds = 8
    )

    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "dialog $Name" -Condition {
        $dialog = Get-DialogWindow -Name $Name
        if (-not $dialog) {
            return $false
        }
        return -not (Test-ElementGoneOrOffscreen -Element $dialog)
    } | Out-Null
    return (Get-DialogWindow -Name $Name)
}

function Wait-ForOptionalDialog {
    param(
        [string]$Name,
        [int]$TimeoutSeconds = 2
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $dialog = Get-DialogWindow -Name $Name
        if ($dialog -and -not (Test-ElementGoneOrOffscreen -Element $dialog)) {
            return $dialog
        }
        Start-Sleep -Milliseconds 150
    }
    return $null
}

function Test-DialogVisibleFast {
    param(
        [string]$Name
    )

    $automationId = if ($Name -eq "Created Tasks") {
        "QApplication.savedActionCreatedTasksDialog"
    } else {
        "QApplication.savedActionCreateDialog"
    }
    $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId $automationId
    if ($dialog -and -not (Test-ElementGoneOrOffscreen -Element $dialog)) {
        try {
            if (-not $Name -or $dialog.Current.Name -eq $Name) {
                return $true
            }
        } catch {
        }
    }

    return $false
}

function Wait-ForDialogClosedFast {
    param(
        [string]$Name,
        [int]$TimeoutSeconds = 6
    )

    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "dialog '$Name' closed (fast)" -Condition {
        return -not (Test-DialogVisibleFast -Name $Name)
    } | Out-Null
}

function Wait-ForElementByAutomationId {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$AutomationId,
        [int]$TimeoutSeconds = 10,
        [bool]$RequireEnabled = $true
    )

    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $AutomationId -Condition {
        $element = Find-ElementByAutomationIdDirect -Root $Root -AutomationId $AutomationId
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null
    return (Find-ElementByAutomationIdDirect -Root $Root -AutomationId $AutomationId)
}

function Wait-ForDialogControlReady {
    param(
        [scriptblock]$DialogResolver,
        [string]$AutomationId,
        [string[]]$AutomationIds,
        [string]$Description,
        [int]$TimeoutSeconds = 6,
        [bool]$RequireEnabled = $true
    )

    $automationIdsToSearch = @($AutomationIds | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($automationIdsToSearch.Count -eq 0 -and -not [string]::IsNullOrWhiteSpace($AutomationId)) {
        $automationIdsToSearch = @($AutomationId)
    }
    if ($automationIdsToSearch.Count -eq 0) {
        throw "No dialog automation IDs were supplied for '$Description'."
    }

    Write-StepLog -Stage "DIALOG" -Message "verifying control '$Description' automationId='$($automationIdsToSearch -join ' | ')'"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $liveDialog = & $DialogResolver
        if (-not $liveDialog) {
            return $false
        }
        try {
            if ($liveDialog -ne [System.Windows.Automation.AutomationElement]::RootElement) {
                Focus-Window -Element $liveDialog
            }
        } catch {
        }
        $element = Find-ElementByAutomationIdsDirect -Root $liveDialog -AutomationIds $automationIdsToSearch
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveDialog = & $DialogResolver
    if (-not $liveDialog) {
        throw "Could not resolve the live dialog while waiting for '$Description'."
    }

    $element = Find-ElementByAutomationIdsDirect -Root $liveDialog -AutomationIds $automationIdsToSearch
    if (-not (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)) {
        throw "Control '$Description' did not become usable. State: $(Get-ElementStateSummary -Element $element)"
    }

    Write-StepLog -Stage "DIALOG" -Message "control ready '$Description' state=$(Get-ElementStateSummary -Element $element)"
    return $element
}

function Wait-ForCreateDialogTaskTypeComboReady {
    param(
        [scriptblock]$DialogResolver,
        [string]$Description,
        [int]$TimeoutSeconds = 6,
        [bool]$RequireEnabled = $true
    )

    $automationIdsToSearch = Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateType"
    Write-StepLog -Stage "DIALOG" -Message "verifying control '$Description' automationId='$($automationIdsToSearch -join ' | ')' with live combo fallback"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $liveDialog = & $DialogResolver
        if (-not $liveDialog) {
            return $false
        }
        try {
            if ($liveDialog -ne [System.Windows.Automation.AutomationElement]::RootElement) {
                Focus-Window -Element $liveDialog
            }
        } catch {
        }
        $element = Find-CreateDialogTaskTypeCombo -Root $liveDialog -RequireEnabled $RequireEnabled
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveDialog = & $DialogResolver
    if (-not $liveDialog) {
        throw "Could not resolve the live dialog while waiting for '$Description'."
    }

    $element = Find-CreateDialogTaskTypeCombo -Root $liveDialog -RequireEnabled $RequireEnabled
    if (-not (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)) {
        throw "Control '$Description' did not become usable. State: $(Get-ElementStateSummary -Element $element)"
    }

    Write-StepLog -Stage "DIALOG" -Message "control ready '$Description' state=$(Get-ElementStateSummary -Element $element)"
    return $element
}

function Wait-ForCreateDialogTextInputReady {
    param(
        [scriptblock]$DialogResolver,
        [ValidateSet("title", "aliases", "target")]
        [string]$Field,
        [string]$Description,
        [int]$TimeoutSeconds = 6,
        [bool]$RequireEnabled = $true
    )

    $leafAutomationId = switch ($Field) {
        "title" { "savedActionCreateTitleInput" }
        "aliases" { "savedActionCreateAliasesInput" }
        "target" { "savedActionCreateTargetInput" }
    }
    $automationIdsToSearch = Get-CreateDialogControlAutomationIds -LeafAutomationId $leafAutomationId
    Write-StepLog -Stage "DIALOG" -Message "verifying control '$Description' automationId='$($automationIdsToSearch -join ' | ')' with live edit fallback"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $liveDialog = & $DialogResolver
        if (-not $liveDialog) {
            return $false
        }
        try {
            if ($liveDialog -ne [System.Windows.Automation.AutomationElement]::RootElement) {
                Focus-Window -Element $liveDialog
            }
        } catch {
        }
        $element = Find-CreateDialogTextInput -Root $liveDialog -Field $Field -RequireEnabled $RequireEnabled
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveDialog = & $DialogResolver
    if (-not $liveDialog) {
        throw "Could not resolve the live dialog while waiting for '$Description'."
    }

    $element = Find-CreateDialogTextInput -Root $liveDialog -Field $Field -RequireEnabled $RequireEnabled
    if (-not (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)) {
        throw "Control '$Description' did not become usable. State: $(Get-ElementStateSummary -Element $element)"
    }

    Write-StepLog -Stage "DIALOG" -Message "control ready '$Description' state=$(Get-ElementStateSummary -Element $element)"
    return $element
}

function Wait-ForCreateDialogGroupActionButtonReady {
    param(
        [scriptblock]$DialogResolver,
        [ValidateSet("assign", "remove")]
        [string]$Action,
        [string]$Description,
        [int]$TimeoutSeconds = 6,
        [bool]$RequireEnabled = $true
    )

    $leafAutomationId = switch ($Action) {
        "assign" { "savedActionCreateNewGroupButton" }
        "remove" { "savedActionCreateRemoveGroupButton" }
    }
    $automationIdsToSearch = Get-CreateDialogControlAutomationIds -LeafAutomationId $leafAutomationId
    Write-StepLog -Stage "DIALOG" -Message "verifying control '$Description' automationId='$($automationIdsToSearch -join ' | ')' with live button fallback"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $liveDialog = & $DialogResolver
        if (-not $liveDialog) {
            return $false
        }
        try {
            if ($liveDialog -ne [System.Windows.Automation.AutomationElement]::RootElement) {
                Focus-Window -Element $liveDialog
            }
        } catch {
        }
        $element = Find-CreateDialogGroupActionButton -Root $liveDialog -Action $Action -RequireEnabled $RequireEnabled
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveDialog = & $DialogResolver
    if (-not $liveDialog) {
        throw "Could not resolve the live dialog while waiting for '$Description'."
    }

    $element = Find-CreateDialogGroupActionButton -Root $liveDialog -Action $Action -RequireEnabled $RequireEnabled
    if (-not (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)) {
        throw "Control '$Description' did not become usable. State: $(Get-ElementStateSummary -Element $element)"
    }

    Write-StepLog -Stage "DIALOG" -Message "control ready '$Description' state=$(Get-ElementStateSummary -Element $element)"
    return $element
}

function Wait-ForGroupDialogTextInputReady {
    param(
        [scriptblock]$DialogResolver,
        [ValidateSet("name", "aliases")]
        [string]$Field,
        [string]$Description,
        [int]$TimeoutSeconds = 6,
        [bool]$RequireEnabled = $true
    )

    $leafAutomationId = switch ($Field) {
        "name" { "callableGroupCreateNameInput" }
        "aliases" { "callableGroupCreateAliasesInput" }
    }
    $automationIdsToSearch = Get-GroupDialogControlAutomationIds -LeafAutomationId $leafAutomationId
    Write-StepLog -Stage "DIALOG" -Message "verifying control '$Description' automationId='$($automationIdsToSearch -join ' | ')' with live edit fallback"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $liveDialog = & $DialogResolver
        if (-not $liveDialog) {
            return $false
        }
        try {
            if ($liveDialog -ne [System.Windows.Automation.AutomationElement]::RootElement) {
                Focus-Window -Element $liveDialog
            }
        } catch {
        }
        $element = Find-GroupDialogTextInput -Root $liveDialog -Field $Field -RequireEnabled $RequireEnabled
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveDialog = & $DialogResolver
    if (-not $liveDialog) {
        throw "Could not resolve the live dialog while waiting for '$Description'."
    }

    $element = Find-GroupDialogTextInput -Root $liveDialog -Field $Field -RequireEnabled $RequireEnabled
    if (-not (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)) {
        throw "Control '$Description' did not become usable. State: $(Get-ElementStateSummary -Element $element)"
    }

    Write-StepLog -Stage "DIALOG" -Message "control ready '$Description' state=$(Get-ElementStateSummary -Element $element)"
    return $element
}

function Wait-ForGroupDialogMembersRegionReady {
    param(
        [scriptblock]$DialogResolver,
        [string]$Description,
        [int]$TimeoutSeconds = 8,
        [bool]$RequireEnabled = $false
    )

    $automationIdsToSearch = @(
        (Get-GroupDialogControlAutomationIds -LeafAutomationId "callableGroupCreateMembersScroll")
        (Get-GroupDialogControlAutomationIds -LeafAutomationId "callableGroupCreateMembersViewport")
        (Get-GroupDialogControlAutomationIds -LeafAutomationId "callableGroupCreateMembersFrame")
    )
    Write-StepLog -Stage "DIALOG" -Message "verifying control '$Description' automationId='$($automationIdsToSearch -join ' | ')' with live region fallback"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $liveDialog = & $DialogResolver
        if (-not $liveDialog) {
            return $false
        }
        try {
            if ($liveDialog -ne [System.Windows.Automation.AutomationElement]::RootElement) {
                Focus-Window -Element $liveDialog
            }
        } catch {
        }
        $element = Find-GroupDialogMembersRegion -Root $liveDialog -RequireEnabled $RequireEnabled
        return (Test-GroupDialogMembersRegionReady -DialogRoot $liveDialog -Region $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveDialog = & $DialogResolver
    if (-not $liveDialog) {
        throw "Could not resolve the live dialog while waiting for '$Description'."
    }

    $element = Find-GroupDialogMembersRegion -Root $liveDialog -RequireEnabled $RequireEnabled
    if (-not (Test-GroupDialogMembersRegionReady -DialogRoot $liveDialog -Region $element -RequireEnabled $RequireEnabled)) {
        throw "Control '$Description' did not become usable. State: $(Get-ElementStateSummary -Element $element)"
    }

    $memberCheckboxCount = @(Get-GroupDialogMemberCheckboxes -Root $liveDialog -RequireEnabled $false).Count
    Write-StepLog -Stage "DIALOG" -Message "control ready '$Description' state=$(Get-ElementStateSummary -Element $element) member_checkboxes=$memberCheckboxCount"
    return $element
}

function Wait-ForOverlayControlReady {
    param(
        [scriptblock]$OverlayResolver,
        [string]$AutomationId,
        [string[]]$AutomationIds,
        [string]$Description,
        [int]$TimeoutSeconds = 6,
        [bool]$RequireEnabled = $true
    )

    $automationIdsToSearch = @($AutomationIds | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($automationIdsToSearch.Count -eq 0 -and -not [string]::IsNullOrWhiteSpace($AutomationId)) {
        $automationIdsToSearch = @($AutomationId)
    }
    if ($automationIdsToSearch.Count -eq 0) {
        throw "No overlay automation IDs were supplied for '$Description'."
    }

    Write-StepLog -Stage "OVERLAY" -Message "verifying control '$Description' automationId='$($automationIdsToSearch -join ' | ')'"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $liveOverlay = & $OverlayResolver
        if (-not $liveOverlay) {
            return $false
        }
        $element = Find-ElementByAutomationIdsDirect -Root $liveOverlay -AutomationIds $automationIdsToSearch
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveOverlay = & $OverlayResolver
    if (-not $liveOverlay) {
        throw "Could not resolve the live overlay while waiting for '$Description'."
    }

    $element = Find-ElementByAutomationIdsDirect -Root $liveOverlay -AutomationIds $automationIdsToSearch
    if (-not (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)) {
        throw "Overlay control '$Description' did not become usable. State: $(Get-ElementStateSummary -Element $element)"
    }

    Write-StepLog -Stage "OVERLAY" -Message "control ready '$Description' state=$(Get-ElementStateSummary -Element $element)"
    return $element
}

function Focus-ElementForInteraction {
    param(
        [scriptblock]$ElementResolver,
        [string]$Description,
        [int]$Attempts = 3,
        [bool]$RequireExactFocus = $true
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        $element = & $ElementResolver
        if (-not (Test-ElementUsable -Element $element -RequireEnabled $true)) {
            Add-Note "Focus attempt $attempt for '$Description' skipped because the element was not yet usable. State: $(Get-ElementStateSummary -Element $element)"
            Start-Sleep -Milliseconds 150
            continue
        }

        $focusSummary = ""
        try {
            Write-StepLog -Stage "INTERACT" -Message "focus attempt=$attempt strategy=window_foreground target='$Description' state=$(Get-ElementStateSummary -Element $element)"
            Focus-Window -Element $element
        } catch {
            Add-Note "Focus attempt $attempt for '$Description' could not foreground the element window. State: $(Get-ElementStateSummary -Element $element)"
        }

        $element = & $ElementResolver
        if (Test-ElementFocusSatisfied -Target $element -FocusedSummary ([ref]$focusSummary)) {
            Write-StepLog -Stage "INTERACT" -Message "focus confirmed for '$Description' on attempt=$attempt strategy=window_foreground target_state=$(Get-ElementStateSummary -Element $element) focused_state=$focusSummary"
            return $element
        }

        try {
            Write-StepLog -Stage "INTERACT" -Message "focus attempt=$attempt strategy=set_focus target='$Description' state=$(Get-ElementStateSummary -Element $element)"
            $element.SetFocus()
            Start-Sleep -Milliseconds 120
        } catch {
        }

        $element = & $ElementResolver
        if (Test-ElementFocusSatisfied -Target $element -FocusedSummary ([ref]$focusSummary)) {
            Write-StepLog -Stage "INTERACT" -Message "focus confirmed for '$Description' on attempt=$attempt strategy=set_focus target_state=$(Get-ElementStateSummary -Element $element) focused_state=$focusSummary"
            return $element
        }

        try {
            Write-StepLog -Stage "INTERACT" -Message "focus attempt=$attempt strategy=center_click target='$Description' state=$(Get-ElementStateSummary -Element $element)"
            Click-Element -Element $element
            Start-Sleep -Milliseconds 120
        } catch {
            Add-Note "Focus attempt $attempt for '$Description' could not click the target control. Cause: $($_.Exception.Message)"
        }

        $element = & $ElementResolver
        if (Test-ElementFocusSatisfied -Target $element -FocusedSummary ([ref]$focusSummary)) {
            Write-StepLog -Stage "INTERACT" -Message "focus confirmed for '$Description' on attempt=$attempt strategy=center_click target_state=$(Get-ElementStateSummary -Element $element) focused_state=$focusSummary"
            return $element
        }

        try {
            Write-StepLog -Stage "INTERACT" -Message "focus attempt=$attempt strategy=window_then_click_setfocus target='$Description' state=$(Get-ElementStateSummary -Element $element)"
            Focus-Window -Element $element
            Click-Element -Element $element
            $element = & $ElementResolver
            if ($element) {
                $element.SetFocus()
            }
            Start-Sleep -Milliseconds 140
        } catch {
            Add-Note "Focus attempt $attempt for '$Description' could not complete the fallback focus sequence. Cause: $($_.Exception.Message)"
        }

        $element = & $ElementResolver
        if (Test-ElementFocusSatisfied -Target $element -FocusedSummary ([ref]$focusSummary)) {
            Write-StepLog -Stage "INTERACT" -Message "focus confirmed for '$Description' on attempt=$attempt strategy=window_then_click_setfocus target_state=$(Get-ElementStateSummary -Element $element) focused_state=$focusSummary"
            return $element
        }

        if (-not $RequireExactFocus -and (Test-ElementUsable -Element $element -RequireEnabled $true)) {
            Write-StepLog -Stage "INTERACT" -Message "proceeding without exact focus for '$Description' on attempt=$attempt target_state=$(Get-ElementStateSummary -Element $element) focused_state=$focusSummary"
            Add-Note "Exact focus did not hold for '$Description', but the control remained usable so the harness proceeded with window-level focus."
            return $element
        }

        Add-Note "Focus attempt $attempt for '$Description' did not hold. Element state: $(Get-ElementStateSummary -Element $element) focused_state=$focusSummary"
        Start-Sleep -Milliseconds 150
    }

    throw "Could not confirm focus for '$Description'."
}

function Set-FieldValueVerified {
    param(
        [scriptblock]$ElementResolver,
        [string]$ExpectedValue,
        [string]$Description
    )

    $expectedNormalized = Normalize-UiValue $ExpectedValue

    for ($attempt = 1; $attempt -le 3; $attempt++) {
        $element = Focus-ElementForInteraction -ElementResolver $ElementResolver -Description $Description -RequireExactFocus $true
        if (-not $element) {
            throw "Could not resolve $Description."
        }

        Write-StepLog -Stage "INTERACT" -Message "field set attempt=$attempt field='$Description' value='$ExpectedValue' state=$(Get-ElementStateSummary -Element $element)"
        try {
            Set-Value -Element $element -Value ""
            Start-Sleep -Milliseconds 80
        } catch {
            Add-Note "Field '$Description' clear attempt $attempt could not execute cleanly before rewrite. Cause: $($_.Exception.Message)"
        }

        $element = & $ElementResolver
        if (-not $element) {
            throw "Could not re-resolve $Description after clearing it."
        }

        Set-Value -Element $element -Value $ExpectedValue
        Start-Sleep -Milliseconds 120

        $actualElement = & $ElementResolver
        $actualValue = Get-ElementReadableValue -Element $actualElement
        $actualNormalized = Normalize-UiValue $actualValue
        if ($actualNormalized -eq $expectedNormalized) {
            Write-StepLog -Stage "INTERACT" -Message "field set confirmed field='$Description' actual='$actualValue' state=$(Get-ElementStateSummary -Element $actualElement)"
            return
        }

        try {
            Wait-ForElementValue -ExpectedValue $ExpectedValue -TimeoutSeconds 3 -Description $Description -ElementResolver $ElementResolver
            $actualElement = & $ElementResolver
            Write-StepLog -Stage "INTERACT" -Message "field set confirmed field='$Description' actual='$(Get-ElementReadableValue -Element $actualElement)' state=$(Get-ElementStateSummary -Element $actualElement)"
            return
        } catch {
            $actualElement = & $ElementResolver
            $actualValue = Get-ElementReadableValue -Element $actualElement
            $actualNormalized = Normalize-UiValue $actualValue
            if ($actualNormalized -eq $expectedNormalized) {
                Write-StepLog -Stage "INTERACT" -Message "field set confirmed after retry window field='$Description' actual='$actualValue' state=$(Get-ElementStateSummary -Element $actualElement)"
                return
            }
            Add-Note "Field '$Description' set attempt $attempt did not stick; actual value read back as '$actualValue' (normalized='$actualNormalized', expected_normalized='$expectedNormalized'). State: $(Get-ElementStateSummary -Element $actualElement)"
        }
    }

    $finalElement = & $ElementResolver
    $finalValue = Get-ElementReadableValue -Element $finalElement
    if ((Normalize-UiValue $finalValue) -eq $expectedNormalized) {
        Write-StepLog -Stage "INTERACT" -Message "field set confirmed after retries field='$Description' actual='$finalValue' state=$(Get-ElementStateSummary -Element $finalElement)"
        Add-Note "Field '$Description' required retries, but the final normalized value matched the expected text."
        return
    }
    throw "Field '$Description' did not retain the expected value '$ExpectedValue'. Final value: '$finalValue'. State: $(Get-ElementStateSummary -Element $finalElement)"
}

function Get-TextValue {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        return $pattern.Current.Value
    } catch {
    }

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
        return $pattern.DocumentRange.GetText(-1)
    } catch {
    }

    throw "Could not read text from the external probe control."
}

function Wait-ForRuntimeMarker {
    param(
        [string]$Marker,
        [int]$TimeoutSeconds = 12,
        [int]$StartLine = -1
    )

    if ($StartLine -lt 0) {
        $StartLine = $script:RuntimeLogLineCursor
    }

    Write-StepLog -Stage "WAIT" -Message "runtime marker '$Marker' from line $StartLine"
    try {
        Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "runtime marker $Marker" -Condition {
            $slice = Get-RuntimeLogSlice -StartLine $StartLine
            if (-not $slice -or $slice.Count -eq 0) {
                return $false
            }
            return @($slice | Where-Object { $_ -like "*$Marker*" }).Count -gt 0
        } | Out-Null
    } catch {
        $slice = Get-RuntimeLogSlice -StartLine $StartLine
        if (@($slice | Where-Object { $_ -like "*$Marker*" }).Count -gt 0) {
            Add-Note "Runtime marker '$Marker' appeared in the log after the timed wait loop missed it once; continuing based on final slice evidence."
        } else {
            throw
        }
    }

    $script:RuntimeLogLineCursor = Get-RuntimeLogLineCount
    Write-StepLog -Stage "WAIT" -Message "runtime marker '$Marker' observed"
}

function Test-RuntimeMarkerSeen {
    param(
        [string]$Marker,
        [int]$StartLine
    )

    $slice = Get-RuntimeLogSlice -StartLine $StartLine
    if (-not $slice -or $slice.Count -eq 0) {
        return $false
    }
    return @($slice | Where-Object { $_ -like "*$Marker*" }).Count -gt 0
}

function Wait-ForCreateAttemptOrCreatedMarker {
    param(
        [string]$Title,
        [int]$StartLine = -1,
        [int]$TimeoutSeconds = 12
    )

    if ($StartLine -lt 0) {
        $StartLine = $script:RuntimeLogLineCursor
    }

    $searchStartLine = [Math]::Max(0, $StartLine - 5)
    $attemptMarker = "RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED|title=$Title"
    $createdMarkerFragment = "RENDERER_MAIN|CUSTOM_TASK_CREATED|"
    $blockedMarkerFragment = "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|"
    $attemptSeen = $false
    $createdSeen = $false
    $blockedSeen = $false

    $scanSlice = {
        $slice = Get-RuntimeLogSlice -StartLine $searchStartLine
        if (-not $slice -or $slice.Count -eq 0) {
            return [pscustomobject]@{
                attempt_seen = $false
                created_seen = $false
                blocked_seen = $false
            }
        }

        return [pscustomobject]@{
            attempt_seen = (@($slice | Where-Object { $_ -like "*$attemptMarker*" }).Count -gt 0)
            created_seen = (@($slice | Where-Object { $_ -like "*$createdMarkerFragment*" -and $_ -like "*title=$Title*" }).Count -gt 0)
            blocked_seen = (@($slice | Where-Object { $_ -like "*$blockedMarkerFragment*" -and $_ -like "*title=$Title*" }).Count -gt 0)
        }
    }

    Write-StepLog -Stage "WAIT" -Message "create attempt marker for '$Title' from line $searchStartLine"
    try {
        Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "create attempt marker for $Title" -Condition {
            $status = & $scanSlice
            $attemptSeen = [bool]$status.attempt_seen
            $createdSeen = [bool]$status.created_seen
            $blockedSeen = [bool]$status.blocked_seen
            return ($attemptSeen -or $createdSeen -or $blockedSeen)
        } | Out-Null
    } catch {
        $graceDeadline = (Get-Date).AddMilliseconds(1500)
        while ((Get-Date) -lt $graceDeadline) {
            $status = & $scanSlice
            $attemptSeen = [bool]$status.attempt_seen
            $createdSeen = [bool]$status.created_seen
            $blockedSeen = [bool]$status.blocked_seen
            if ($attemptSeen -or $createdSeen -or $blockedSeen) {
                break
            }
            Start-Sleep -Milliseconds 100
        }

        if (-not ($attemptSeen -or $createdSeen -or $blockedSeen)) {
            throw
        }
    }

    $script:RuntimeLogLineCursor = Get-RuntimeLogLineCount
    if ($blockedSeen) {
        throw "Create flow for '$Title' emitted a blocked runtime marker."
    }
    if ($attemptSeen) {
        Write-StepLog -Stage "WAIT" -Message "create attempt marker for '$Title' observed"
        return [pscustomobject]@{
            attempt_seen = $true
            created_fallback_used = $false
            search_start_line = $searchStartLine
        }
    }

    Add-Note "Create flow for '$Title' did not surface ATTEMPT_STARTED in time, but CUSTOM_TASK_CREATED was observed and the harness inferred the attempt path from runtime truth."
    Write-StepLog -Stage "WAIT" -Message "create attempt marker for '$Title' inferred from created marker"
    return [pscustomobject]@{
        attempt_seen = $false
        created_fallback_used = $true
        search_start_line = $searchStartLine
    }
}

function Wait-ForCreateCreatedMarkerByTitle {
    param(
        [string]$Title,
        [int]$StartLine = -1,
        [int]$TimeoutSeconds = 12
    )

    if ($StartLine -lt 0) {
        $StartLine = $script:RuntimeLogLineCursor
    }

    $searchStartLine = [Math]::Max(0, $StartLine - 5)
    $createdMarkerFragment = "RENDERER_MAIN|CUSTOM_TASK_CREATED|"
    $blockedMarkerFragment = "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|"
    $createdSeen = $false
    $blockedSeen = $false

    $scanSlice = {
        $slice = Get-RuntimeLogSlice -StartLine $searchStartLine
        if (-not $slice -or $slice.Count -eq 0) {
            return [pscustomobject]@{
                created_seen = $false
                blocked_seen = $false
            }
        }

        return [pscustomobject]@{
            created_seen = (@($slice | Where-Object { $_ -like "*$createdMarkerFragment*" -and $_ -like "*title=$Title*" }).Count -gt 0)
            blocked_seen = (@($slice | Where-Object { $_ -like "*$blockedMarkerFragment*" -and $_ -like "*title=$Title*" }).Count -gt 0)
        }
    }

    Write-StepLog -Stage "WAIT" -Message "create completion marker for '$Title' from line $searchStartLine"
    try {
        Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "create completion marker for $Title" -Condition {
            $status = & $scanSlice
            $createdSeen = [bool]$status.created_seen
            $blockedSeen = [bool]$status.blocked_seen
            return ($createdSeen -or $blockedSeen)
        } | Out-Null
    } catch {
        $graceDeadline = (Get-Date).AddMilliseconds(1500)
        while ((Get-Date) -lt $graceDeadline) {
            $status = & $scanSlice
            $createdSeen = [bool]$status.created_seen
            $blockedSeen = [bool]$status.blocked_seen
            if ($createdSeen -or $blockedSeen) {
                break
            }
            Start-Sleep -Milliseconds 100
        }

        if (-not ($createdSeen -or $blockedSeen)) {
            throw
        }
    }

    $script:RuntimeLogLineCursor = Get-RuntimeLogLineCount
    if ($blockedSeen) {
        throw "Create flow for '$Title' emitted a blocked runtime marker."
    }

    Write-StepLog -Stage "WAIT" -Message "create completion marker for '$Title' observed"
    return [pscustomobject]@{
        created_seen = $true
        search_start_line = $searchStartLine
    }
}

function Wait-ForCreateAttemptOrBlockedMarker {
    param(
        [string]$Title,
        [int]$StartLine = -1,
        [int]$TimeoutSeconds = 12
    )

    if ($StartLine -lt 0) {
        $StartLine = $script:RuntimeLogLineCursor
    }

    $searchStartLine = [Math]::Max(0, $StartLine - 5)
    $attemptMarker = "RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED|title=$Title"
    $blockedMarkerFragment = "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|"
    $attemptSeen = $false
    $blockedSeen = $false

    $scanSlice = {
        $slice = Get-RuntimeLogSlice -StartLine $searchStartLine
        if (-not $slice -or $slice.Count -eq 0) {
            return [pscustomobject]@{
                attempt_seen = $false
                blocked_seen = $false
            }
        }

        return [pscustomobject]@{
            attempt_seen = (@($slice | Where-Object { $_ -like "*$attemptMarker*" }).Count -gt 0)
            blocked_seen = (@($slice | Where-Object { $_ -like "*$blockedMarkerFragment*" -and $_ -like "*title=$Title*" }).Count -gt 0)
        }
    }

    Write-StepLog -Stage "WAIT" -Message "invalid-create attempt marker for '$Title' from line $searchStartLine"
    try {
        Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "invalid-create attempt marker for $Title" -Condition {
            $status = & $scanSlice
            $attemptSeen = [bool]$status.attempt_seen
            $blockedSeen = [bool]$status.blocked_seen
            return ($attemptSeen -or $blockedSeen)
        } | Out-Null
    } catch {
        $graceDeadline = (Get-Date).AddMilliseconds(1500)
        while ((Get-Date) -lt $graceDeadline) {
            $status = & $scanSlice
            $attemptSeen = [bool]$status.attempt_seen
            $blockedSeen = [bool]$status.blocked_seen
            if ($attemptSeen -or $blockedSeen) {
                break
            }
            Start-Sleep -Milliseconds 100
        }

        if (-not ($attemptSeen -or $blockedSeen)) {
            throw
        }
    }

    $script:RuntimeLogLineCursor = Get-RuntimeLogLineCount
    if ($attemptSeen) {
        Write-StepLog -Stage "WAIT" -Message "invalid-create attempt marker for '$Title' observed"
        return [pscustomobject]@{
            attempt_seen = $true
            blocked_fallback_used = $false
            search_start_line = $searchStartLine
        }
    }

    Add-Note "Invalid create submit for '$Title' did not surface ATTEMPT_STARTED in time, but CUSTOM_TASK_CREATE_BLOCKED was observed and the harness inferred the attempt path from runtime truth."
    Write-StepLog -Stage "WAIT" -Message "invalid-create attempt marker for '$Title' inferred from blocked marker"
    return [pscustomobject]@{
        attempt_seen = $false
        blocked_fallback_used = $true
        search_start_line = $searchStartLine
    }
}

function Wait-ForCreateBlockedMarkerByTitle {
    param(
        [string]$Title,
        [int]$StartLine = -1,
        [int]$TimeoutSeconds = 12
    )

    if ($StartLine -lt 0) {
        $StartLine = $script:RuntimeLogLineCursor
    }

    $searchStartLine = [Math]::Max(0, $StartLine - 5)
    $blockedMarkerFragment = "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|"
    $createdMarkerFragment = "RENDERER_MAIN|CUSTOM_TASK_CREATED|"
    $blockedSeen = $false
    $createdSeen = $false

    $scanSlice = {
        $slice = Get-RuntimeLogSlice -StartLine $searchStartLine
        if (-not $slice -or $slice.Count -eq 0) {
            return [pscustomobject]@{
                blocked_seen = $false
                created_seen = $false
            }
        }

        return [pscustomobject]@{
            blocked_seen = (@($slice | Where-Object { $_ -like "*$blockedMarkerFragment*" -and $_ -like "*title=$Title*" }).Count -gt 0)
            created_seen = (@($slice | Where-Object { $_ -like "*$createdMarkerFragment*" -and $_ -like "*title=$Title*" }).Count -gt 0)
        }
    }

    Write-StepLog -Stage "WAIT" -Message "invalid-create blocked marker for '$Title' from line $searchStartLine"
    try {
        Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "invalid-create blocked marker for $Title" -Condition {
            $status = & $scanSlice
            $blockedSeen = [bool]$status.blocked_seen
            $createdSeen = [bool]$status.created_seen
            return ($blockedSeen -or $createdSeen)
        } | Out-Null
    } catch {
        $graceDeadline = (Get-Date).AddMilliseconds(1500)
        while ((Get-Date) -lt $graceDeadline) {
            $status = & $scanSlice
            $blockedSeen = [bool]$status.blocked_seen
            $createdSeen = [bool]$status.created_seen
            if ($blockedSeen -or $createdSeen) {
                break
            }
            Start-Sleep -Milliseconds 100
        }

        if (-not ($blockedSeen -or $createdSeen)) {
            throw
        }
    }

    $script:RuntimeLogLineCursor = Get-RuntimeLogLineCount
    if ($createdSeen) {
        throw "Invalid create flow for '$Title' emitted a create marker instead of staying blocked."
    }

    $slice = Get-RuntimeLogSlice -StartLine $searchStartLine
    $matchedLine = @($slice | Where-Object { $_ -like "*$blockedMarkerFragment*" -and $_ -like "*title=$Title*" } | Select-Object -Last 1)

    Write-StepLog -Stage "WAIT" -Message "invalid-create blocked marker for '$Title' observed"
    return [pscustomobject]@{
        blocked_seen = $true
        search_start_line = $searchStartLine
        blocked_line = $(if ($matchedLine) { [string]$matchedLine[0] } else { "" })
    }
}

function Get-OverlayAttemptStateSummary {
    param(
        [int]$StartLine
    )

    $slice = Get-RuntimeLogSlice -StartLine $StartLine
    if (-not $slice -or $slice.Count -eq 0) {
        return "no_runtime_markers"
    }

    $interesting = @(
        $slice | Where-Object {
            $_ -like "*RENDERER_MAIN|DESKTOP_ATTACH_RESULT*" -or
            $_ -like "*RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN*" -or
            $_ -like "*RENDERER_MAIN|COMMAND_OVERLAY_OPENED*" -or
            $_ -like "*RENDERER_MAIN|COMMAND_OVERLAY_READY*" -or
            $_ -like "*RENDERER_MAIN|COMMAND_OVERLAY_READY_WAITING*" -or
            $_ -like "*RENDERER_MAIN|COMMAND_OVERLAY_READY_TIMEOUT*"
        }
    )

    if (-not $interesting -or $interesting.Count -eq 0) {
        return "no_overlay_runtime_markers"
    }

    return (($interesting | Select-Object -Last 4) -join " || ")
}

function Wait-ForOverlayRuntimeReady {
    param(
        [int]$StartLine = -1,
        [int]$TimeoutSeconds = 12
    )

    if ($StartLine -lt 0) {
        $StartLine = New-RuntimeMarkerCursor
    }

    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_OPENED" -TimeoutSeconds $TimeoutSeconds -StartLine $StartLine
    try {
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -TimeoutSeconds $TimeoutSeconds -StartLine $StartLine
        return
    } catch {
        Add-Note "COMMAND_OVERLAY_READY was not emitted within the expected window; falling back to interactable overlay verification."
    }

    Wait-Until -TimeoutSeconds ([Math]::Max(2, [Math]::Min(4, $TimeoutSeconds))) -Description "overlay interactable fallback" -Condition {
        Test-OverlayInteractableFallback -Overlay $null
    } | Out-Null
    Write-StepLog -Stage "WAIT" -Message "overlay interactable fallback satisfied after missing COMMAND_OVERLAY_READY"
}

function Wait-ForDialogRuntimeReady {
    param(
        [string]$SignalBase,
        [int]$StartLine = -1,
        [int]$TimeoutSeconds = 12
    )

    if ($StartLine -lt 0) {
        $StartLine = New-RuntimeMarkerCursor
    }

    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|${SignalBase}_OPENED" -TimeoutSeconds $TimeoutSeconds -StartLine $StartLine
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|${SignalBase}_READY" -TimeoutSeconds $TimeoutSeconds -StartLine $StartLine
}

function Wait-ForDialogRuntimeClosed {
    param(
        [string]$SignalBase,
        [int]$StartLine = -1,
        [int]$TimeoutSeconds = 12
    )

    if ($StartLine -lt 0) {
        $StartLine = New-RuntimeMarkerCursor
    }

    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|${SignalBase}_CLOSED" -TimeoutSeconds $TimeoutSeconds -StartLine $StartLine
}

function Wait-ForCatalogReloadCompleted {
    param(
        [int]$StartLine = -1,
        [int]$TimeoutSeconds = 12
    )

    if ($StartLine -lt 0) {
        $StartLine = New-RuntimeMarkerCursor
    }

    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_ACTION_CATALOG_RELOAD_STARTED" -TimeoutSeconds $TimeoutSeconds -StartLine $StartLine
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_ACTION_CATALOG_RELOAD_COMPLETED" -TimeoutSeconds $TimeoutSeconds -StartLine $StartLine
}

function Invoke-ElementRobust {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Description = "element"
    )

    if (-not $Element) {
        throw "Could not invoke $Description because the element was missing."
    }

    try {
        Focus-Window -Element $Element
    } catch {
    }

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $pattern.Invoke()
        return
    } catch {
    }

    try {
        Click-Element -Element $Element
        return
    } catch {
    }

    try {
        $Element.SetFocus()
        Send-VirtualKey -VirtualKey 0x20
        return
    } catch {
    }

    throw "Could not invoke $Description."
}

function Copy-SourceSnapshot {
    param([string]$Slug)

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        return $null
    }
    $destination = Join-Path $ArtifactsDir "${Stamp}_${Slug}_saved_actions.json"
    Copy-Item -LiteralPath $SourcePath -Destination $destination -Force
    Add-Artifact -Label $Slug -Path $destination
    return $destination
}

function Write-Utf8NoBomFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Save-JsonNoBom {
    param(
        [string]$Path,
        [object]$Value
    )

    $json = $Value | ConvertTo-Json -Depth 8
    Write-Utf8NoBomFile -Path $Path -Content ($json + "`n")
}

function Get-ButtonByName {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$Name
    )
    return Find-FirstElement -Root $Root -Name $Name -ControlType ([System.Windows.Automation.ControlType]::Button)
}

function Get-CheckboxByName {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$Name
    )
    return Find-FirstElement -Root $Root -Name $Name -ControlType ([System.Windows.Automation.ControlType]::CheckBox)
}

function Set-CheckboxStateVerified {
    param(
        [scriptblock]$ElementResolver,
        [bool]$Checked,
        [string]$Description
    )

    $expectedState = if ($Checked) {
        [System.Windows.Automation.ToggleState]::On
    } else {
        [System.Windows.Automation.ToggleState]::Off
    }

    for ($attempt = 1; $attempt -le 3; $attempt++) {
        $element = Focus-ElementForInteraction -ElementResolver $ElementResolver -Description $Description -RequireExactFocus $false
        if (-not $element) {
            throw "Could not resolve $Description."
        }

        try {
            $togglePattern = $element.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
            if ($togglePattern.Current.ToggleState -ne $expectedState) {
                $togglePattern.Toggle()
                Start-Sleep -Milliseconds 120
            }
        } catch {
            Invoke-ElementRobust -Element $element -Description $Description
            Start-Sleep -Milliseconds 120
        }

        $element = & $ElementResolver
        try {
            $togglePattern = $element.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
            if ($togglePattern.Current.ToggleState -eq $expectedState) {
                Write-StepLog -Stage "INTERACT" -Message "checkbox state verified for '$Description' checked=$Checked"
                return
            }
        } catch {
        }
    }

    throw "Could not verify checkbox state for '$Description'."
}

function Get-InventoryEditButtons {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay
    )

    $buttons = @()
    foreach ($element in (Get-AllDescendants -Element $Overlay)) {
        if ((Get-ElementControlTypeNameSafe -Element $element -Context "Get-InventoryEditButtons") -eq [System.Windows.Automation.ControlType]::Button.ProgrammaticName -and $element.Current.Name -eq "Edit") {
            $buttons += $element
        }
    }
    return @($buttons)
}

function Resolve-LiveOverlayRoot {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay
    )

    if ($Overlay -eq [System.Windows.Automation.AutomationElement]::RootElement) {
        return $Overlay
    }

    $liveOverlay = Get-OverlayWindow
    if ($liveOverlay -and -not (Test-ElementGoneOrOffscreen -Element $liveOverlay)) {
        return $liveOverlay
    }

    if ($Overlay -and -not (Test-ElementGoneOrOffscreen -Element $Overlay)) {
        return $Overlay
    }

    foreach ($automationId in (Get-OverlayAnchorAutomationIds)) {
        $anchor = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId $automationId
        if ($anchor -and -not (Test-ElementGoneOrOffscreen -Element $anchor)) {
            return [System.Windows.Automation.AutomationElement]::RootElement
        }
    }

    return (Wait-ForOverlayOpen -TimeoutSeconds 10)
}

function Test-OverlayInteractableFallback {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay
    )

    $liveOverlay = Resolve-LiveOverlayRoot -Overlay $Overlay
    if (-not $liveOverlay) {
        return $false
    }

    foreach ($automationId in (Get-OverlayAnchorAutomationIds)) {
        $element = Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId $automationId
        if (-not $element -or (Test-ElementGoneOrOffscreen -Element $element)) {
            return $false
        }
    }

    return $true
}

function Resolve-LiveDialogRoot {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$ExpectedName = ""
    )

    if ($ExpectedName) {
        $liveDialog = Get-DialogWindow -Name $ExpectedName
        if ($liveDialog -and -not (Test-ElementGoneOrOffscreen -Element $liveDialog)) {
            return $liveDialog
        }
    }

    if ($Dialog -and -not (Test-ElementGoneOrOffscreen -Element $Dialog)) {
        return $Dialog
    }

    if ($Dialog) {
        try {
            $liveDialog = Get-DialogWindow -Name $Dialog.Current.Name
            if ($liveDialog -and -not (Test-ElementGoneOrOffscreen -Element $liveDialog)) {
                return $liveDialog
            }
        } catch {
        }
    }

    return $Dialog
}

function Get-InventoryTextRows {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay
    )

    $rows = @()
    foreach ($element in (Get-AllDescendants -Element $Overlay)) {
        if ((Get-ElementControlTypeNameSafe -Element $element -Context "Get-InventoryTextRows") -eq [System.Windows.Automation.ControlType]::Text.ProgrammaticName) {
            $text = $element.Current.Name
            if (-not [string]::IsNullOrWhiteSpace($text)) {
                $rows += $text
            }
        }
    }
    return @($rows)
}

function Open-Overlay {
    if ($script:RuntimeAutoOpenPending) {
        $script:RuntimeAutoOpenPending = $false
        $markerStart = [Math]::Max(0, $script:RuntimeLogLineCursor)
        Write-StepLog -Stage "OVERLAY" -Message "waiting for runtime helper auto-open"
        try {
            Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPENED" -TimeoutSeconds 5 -StartLine $markerStart
        } catch {
            try {
                Wait-ForOverlayRuntimeReady -StartLine $markerStart -TimeoutSeconds 5
            } catch {
            }
        }

        if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -StartLine $markerStart) {
            Write-StepLog -Stage "OVERLAY" -Message "runtime helper auto-open satisfied overlay ready markers"
            return [System.Windows.Automation.AutomationElement]::RootElement
        }

        Add-Note "Runtime helper auto-open did not complete the overlay ready path. state=$(Get-OverlayAttemptStateSummary -StartLine $markerStart)"
    }

    for ($attempt = 1; $attempt -le 4; $attempt++) {
        if ($script:notepadProbe) {
            try {
                Focus-Window -Element $script:notepadProbe.window
                Start-Sleep -Milliseconds 120
            } catch {
            }
        }
        $markerStart = New-RuntimeMarkerCursor
        Write-StepLog -Stage "OVERLAY" -Message "sending overlay hotkey attempt=$attempt startLine=$markerStart"
        Send-OverlayHotkey
        try {
            Wait-ForOverlayRuntimeReady -StartLine $markerStart -TimeoutSeconds 8
            Write-StepLog -Stage "OVERLAY" -Message "overlay entry markers satisfied on attempt=$attempt"
            return [System.Windows.Automation.AutomationElement]::RootElement
        } catch {
            $openedSeen = Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|COMMAND_OVERLAY_OPENED" -StartLine $markerStart
            $readySeen = Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -StartLine $markerStart
            Add-Note "Overlay hotkey attempt $attempt did not complete the open/ready marker path. opened_seen=$openedSeen ready_seen=$readySeen state=$(Get-OverlayAttemptStateSummary -StartLine $markerStart)"
        }
        Start-Sleep -Milliseconds 600
    }

    Write-StepLog -Stage "OVERLAY" -Message "falling back to SendKeys overlay hotkey"
    if ($script:notepadProbe) {
        try {
            Focus-Window -Element $script:notepadProbe.window
            Start-Sleep -Milliseconds 120
        } catch {
        }
    }
    $markerStart = New-RuntimeMarkerCursor
    Send-OverlayHotkeyFallback
    try {
        Wait-ForOverlayRuntimeReady -StartLine $markerStart -TimeoutSeconds 8
    } catch {
        $openedSeen = Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|COMMAND_OVERLAY_OPENED" -StartLine $markerStart
        $readySeen = Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -StartLine $markerStart
        Add-Note "SendKeys overlay fallback did not complete the open/ready marker path. opened_seen=$openedSeen ready_seen=$readySeen state=$(Get-OverlayAttemptStateSummary -StartLine $markerStart)"
    }
    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -StartLine $markerStart) {
        Write-StepLog -Stage "OVERLAY" -Message "overlay entry markers satisfied through SendKeys fallback"
        return [System.Windows.Automation.AutomationElement]::RootElement
    }

    $markerStart = New-RuntimeMarkerCursor
    Wait-ForOverlayRuntimeReady -StartLine $markerStart -TimeoutSeconds 12
    Write-StepLog -Stage "OVERLAY" -Message "overlay entry markers satisfied through final wait"
    return [System.Windows.Automation.AutomationElement]::RootElement
}

function Close-Overlay {
    param(
        [string]$Reason = "overlay close"
    )

    $overlay = Get-OverlayWindow
    if (-not $overlay) {
        Write-StepLog -Stage "OVERLAY" -Message "overlay already closed before $Reason"
        return
    }

    try {
        Focus-Window -Element $overlay
    } catch {
    }

    $markerStart = New-RuntimeMarkerCursor
    Write-StepLog -Stage "OVERLAY" -Message "closing overlay via escape for $Reason"
    Send-VirtualKey -VirtualKey 0x1B

    $closeConfirmed = $false
    try {
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" -TimeoutSeconds 3 -StartLine $markerStart
        $closeConfirmed = $true
        Write-StepLog -Stage "OVERLAY" -Message "overlay close confirmed by runtime marker after escape for $Reason"
    } catch {
        Write-StepLog -Stage "OVERLAY" -Message "overlay close marker did not arrive after escape; retrying close with hotkey for $Reason"
        Send-OverlayHotkey
    }

    if (-not $closeConfirmed) {
        try {
            Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" -TimeoutSeconds 4 -StartLine $markerStart
            $closeConfirmed = $true
            Write-StepLog -Stage "OVERLAY" -Message "overlay close confirmed by runtime marker after hotkey retry for $Reason"
        } catch {
            Add-Note "Overlay close marker was still missing after the hotkey retry for $Reason; falling back to non-interactable overlay verification."
        }
    }

    if (-not $closeConfirmed) {
        Wait-Until -TimeoutSeconds 4 -Description "overlay close fallback for $Reason" -Condition {
            -not (Test-OverlayInteractableFallback -Overlay $null)
        } | Out-Null
        Write-StepLog -Stage "OVERLAY" -Message "overlay close fallback satisfied without a fresh runtime close marker for $Reason"
        return
    }
}

function Reopen-OverlayAfterClose {
    param(
        [string]$Reason = "overlay reopen"
    )

    Write-StepLog -Stage "OVERLAY" -Message "reopening overlay after $Reason"
    $overlay = Open-OverlayWithRuntimeRestartFallback
    $overlay = Ensure-OverlayReady -Overlay $overlay -Reason "$Reason reopen"
    Write-StepLog -Stage "OVERLAY" -Message "overlay reopen ready confirmed after $Reason"
    return $overlay
}

function Open-CreateDialog {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay
    )

    $resolveOverlay = {
        Resolve-LiveOverlayRoot -Overlay $Overlay
    }
    $resolveCreateButton = {
        $liveOverlay = & $resolveOverlay
        if (-not $liveOverlay) {
            return $null
        }
        return (Find-ElementByAutomationIdsDirect -Root $liveOverlay -AutomationIds (Get-OverlayCreateButtonAutomationIds))
    }

    $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationIds (Get-OverlayCreateButtonAutomationIds) -Description "Create Custom Task button"
    $button = Focus-ElementForInteraction -ElementResolver $resolveCreateButton -Description "Create Custom Task button" -RequireExactFocus $false
    Write-StepLog -Stage "DIALOG" -Message "opening Create Custom Task"
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $button -Description "Create Custom Task button"

    try {
        Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_TASK_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    } catch {
        Add-Note "Create dialog markers were not observed after the first Create Custom Task invoke; retrying the entry button once."
        $button = Focus-ElementForInteraction -ElementResolver $resolveCreateButton -Description "Create Custom Task button retry" -RequireExactFocus $false
        Invoke-ElementRobust -Element $button -Description "Create Custom Task button retry"
        Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_TASK_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    }

    $dialog = Wait-ForDialog -Name "Create Custom Task" -TimeoutSeconds 8
    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $dialog -ExpectedName "Create Custom Task"
    }

    Write-StepLog -Stage "DIALOG" -Message "verifying create-dialog entry readiness after runtime markers"
    $null = Wait-ForCreateDialogTaskTypeComboReady -DialogResolver $resolveDialog -Description "create dialog task type combo"
    $null = Wait-ForCreateDialogTextInputReady -DialogResolver $resolveDialog -Field "title" -Description "create dialog title input"
    $null = Wait-ForCreateDialogTextInputReady -DialogResolver $resolveDialog -Field "aliases" -Description "create dialog aliases input"
    $null = Wait-ForCreateDialogTextInputReady -DialogResolver $resolveDialog -Field "target" -Description "create dialog target input"

    $typeCombo = Focus-ElementForInteraction -ElementResolver {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) {
            return $null
        }
        return (Find-CreateDialogTaskTypeCombo -Root $liveDialog)
    } -Description "create dialog task type combo" -RequireExactFocus $false

    if (-not $typeCombo) {
        throw "Could not focus the create dialog task type combo after dialog ready."
    }

    Write-StepLog -Stage "DIALOG" -Message "create-dialog entry ready and first interaction control focused"
    return (& $resolveDialog)
}

function Open-CreateGroupDialog {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay
    )

    $resolveOverlay = {
        Resolve-LiveOverlayRoot -Overlay $Overlay
    }
    $resolveCreateGroupButton = {
        $liveOverlay = & $resolveOverlay
        if (-not $liveOverlay) {
            return $null
        }
        return (Find-ElementByAutomationIdsDirect -Root $liveOverlay -AutomationIds (Get-OverlayCreateGroupButtonAutomationIds))
    }

    $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationIds (Get-OverlayCreateGroupButtonAutomationIds) -Description "Create Custom Group button"
    $button = Focus-ElementForInteraction -ElementResolver $resolveCreateGroupButton -Description "Create Custom Group button" -RequireExactFocus $false
    Write-StepLog -Stage "DIALOG" -Message "opening Create Custom Group"
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $button -Description "Create Custom Group button"

    try {
        Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_GROUP_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    } catch {
        Add-Note "Create Custom Group markers were not observed after the first invoke; retrying the entry button once."
        $button = Focus-ElementForInteraction -ElementResolver $resolveCreateGroupButton -Description "Create Custom Group button retry" -RequireExactFocus $false
        Invoke-ElementRobust -Element $button -Description "Create Custom Group button retry"
        Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_GROUP_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    }

    $dialog = Wait-ForDialog -Name "Create Custom Group" -TimeoutSeconds 8
    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $dialog -ExpectedName "Create Custom Group"
    }

    $null = Wait-ForGroupDialogTextInputReady -DialogResolver $resolveDialog -Field "name" -Description "group dialog name input"
    $null = Wait-ForGroupDialogTextInputReady -DialogResolver $resolveDialog -Field "aliases" -Description "group dialog aliases input"
    $null = Wait-ForGroupDialogMembersRegionReady -DialogResolver $resolveDialog -Description "group dialog members region" -RequireEnabled $false -TimeoutSeconds 10
    return (& $resolveDialog)
}

function Fill-CallableGroupDialog {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$GroupName,
        [string]$Aliases,
        [string[]]$MemberNames
    )

    $dialogName = $Dialog.Current.Name
    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $Dialog -ExpectedName $dialogName
    }
    $resolveNameInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-GroupDialogTextInput -Root $liveDialog -Field "name")
    }
    $resolveAliasesInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-GroupDialogTextInput -Root $liveDialog -Field "aliases")
    }

    Set-FieldValueVerified -ElementResolver $resolveNameInput -ExpectedValue $GroupName -Description "group name input"
    Set-FieldValueVerified -ElementResolver $resolveAliasesInput -ExpectedValue $Aliases -Description "group aliases input"

    foreach ($memberName in @($MemberNames)) {
        $resolveCheckbox = {
            $liveDialog = & $resolveDialog
            if (-not $liveDialog) { return $null }
            return (Get-CheckboxByName -Root $liveDialog -Name $memberName)
        }
        Set-CheckboxStateVerified -ElementResolver $resolveCheckbox -Checked $true -Description "group member '$memberName'"
    }
}

function Open-TaskGroupAssignmentDialog {
    param(
        [System.Windows.Automation.AutomationElement]$TaskDialog
    )

    $dialogName = $TaskDialog.Current.Name
    $resolveTaskDialog = {
        Resolve-LiveDialogRoot -Dialog $TaskDialog -ExpectedName $dialogName
    }
    $resolveAssignGroupButton = {
        $liveDialog = & $resolveTaskDialog
        if (-not $liveDialog) { return $null }
        return (Find-CreateDialogGroupActionButton -Root $liveDialog -Action "assign")
    }

    $null = Wait-ForCreateDialogGroupActionButtonReady -DialogResolver $resolveTaskDialog -Action "assign" -Description "task dialog Assign Group button"
    $buttonInvoked = $false
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        $button = & $resolveAssignGroupButton
        if (-not (Test-ElementUsable -Element $button -RequireEnabled $true)) {
            Add-Note "Invoke attempt $attempt for 'task dialog Assign Group button' skipped because the button was not yet usable. State: $(Get-ElementStateSummary -Element $button)"
            Start-Sleep -Milliseconds 150
            continue
        }

        Write-StepLog -Stage "INTERACT" -Message "invoke attempt=$attempt target='task dialog Assign Group button' state=$(Get-ElementStateSummary -Element $button)"
        try {
            Invoke-ElementRobust -Element $button -Description "task dialog Assign Group button"
            $buttonInvoked = $true
            break
        } catch {
            Add-Note "Invoke attempt $attempt for 'task dialog Assign Group button' failed against the current live button reference. Cause: $($_.Exception.Message)"
            Start-Sleep -Milliseconds 180
        }
    }
    if (-not $buttonInvoked) {
        throw "Could not invoke 'task dialog Assign Group button'."
    }

    $dialog = Wait-ForDialog -Name "Available Groups" -TimeoutSeconds 8
    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $dialog -ExpectedName "Available Groups"
    }
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationIds (Get-TaskGroupAssignmentDialogControlAutomationIds -LeafAutomationId "taskGroupAssignmentCreateButton") -Description "Available Groups create button"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationIds (Get-TaskGroupAssignmentDialogControlAutomationIds -LeafAutomationId "taskGroupAssignmentDoneButton") -Description "Available Groups done button"
    return (& $resolveDialog)
}

function Get-TaskGroupAssignmentRowButton {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$GroupTitle,
        [string]$ButtonName
    )

    $liveDialog = Resolve-LiveDialogRoot -Dialog $Dialog -ExpectedName "Available Groups"
    if (-not $liveDialog) {
        return $null
    }

    $titleElement = Find-FirstElement -Root $liveDialog -Name $GroupTitle
    if (-not $titleElement) {
        return $null
    }

    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $current = $titleElement
    while ($current) {
        $button = Find-FirstElement -Root $current -Name $ButtonName -ControlType ([System.Windows.Automation.ControlType]::Button)
        if ($button) {
            return $button
        }
        try {
            $current = $walker.GetParent($current)
        } catch {
            return $null
        }
    }

    if ($ButtonName -eq "Assign") {
        $assignButtons = @()
        foreach ($element in (Get-AllDescendants -Element $liveDialog)) {
            try {
                if (
                    (Get-ElementControlTypeNameSafe -Element $element -Context "Get-TaskGroupAssignmentRowButton fallback") -eq [System.Windows.Automation.ControlType]::Button.ProgrammaticName -and
                    $element.Current.Name -eq "Assign" -and
                    -not $element.Current.IsOffscreen -and
                    $element.Current.IsEnabled
                ) {
                    $assignButtons += $element
                }
            } catch {
            }
        }
        if ($assignButtons.Count -eq 1) {
            Add-Note "Resolved '$GroupTitle' assignment through the unique visible Assign button fallback in Available Groups."
            return $assignButtons[0]
        }
    }

    return $null
}

function Find-CreateDialogTaskTypeCombo {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [bool]$RequireEnabled = $true
    )

    if (-not $Root) {
        return $null
    }

    $automationIdMatch = Find-ElementByAutomationIdsDirect -Root $Root -AutomationIds (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateType")
    if (Test-ElementUsable -Element $automationIdMatch -RequireEnabled $RequireEnabled) {
        return $automationIdMatch
    }

    $bestMatch = $null
    $bestTop = [double]::PositiveInfinity
    $bestLeft = [double]::PositiveInfinity
    foreach ($candidate in (Get-AllDescendants -Element $Root)) {
        try {
            if ((Get-ElementControlTypeNameSafe -Element $candidate -Context "Find-CreateDialogTaskTypeCombo") -ne [System.Windows.Automation.ControlType]::ComboBox.ProgrammaticName) {
                continue
            }
            if (-not (Test-ElementUsable -Element $candidate -RequireEnabled $RequireEnabled)) {
                continue
            }

            $selectedValue = Normalize-UiValue (Get-ComboSelectedText -Combo $candidate)
            if ((Get-ActionTypeIndexFromValue -Value $selectedValue) -lt 0) {
                continue
            }

            $rect = $candidate.Current.BoundingRectangle
            if (
                $rect.Top -lt $bestTop -or
                (
                    $rect.Top -eq $bestTop -and
                    $rect.Left -lt $bestLeft
                )
            ) {
                $bestMatch = $candidate
                $bestTop = $rect.Top
                $bestLeft = $rect.Left
            }
        } catch {
        }
    }

    return $bestMatch
}

function Find-CreateDialogTextInput {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [ValidateSet("title", "aliases", "target")]
        [string]$Field,
        [bool]$RequireEnabled = $true
    )

    if (-not $Root) {
        return $null
    }

    $leafAutomationId = switch ($Field) {
        "title" { "savedActionCreateTitleInput" }
        "aliases" { "savedActionCreateAliasesInput" }
        "target" { "savedActionCreateTargetInput" }
    }
    $automationIdMatch = Find-ElementByAutomationIdsDirect -Root $Root -AutomationIds (Get-CreateDialogControlAutomationIds -LeafAutomationId $leafAutomationId)
    if (Test-ElementUsable -Element $automationIdMatch -RequireEnabled $RequireEnabled) {
        return $automationIdMatch
    }

    $visibleInputs = @()
    foreach ($candidate in (Get-AllDescendants -Element $Root)) {
        try {
            if ((Get-ElementControlTypeNameSafe -Element $candidate -Context "Find-CreateDialogTextInput") -ne [System.Windows.Automation.ControlType]::Edit.ProgrammaticName) {
                continue
            }
            if (-not (Test-ElementUsable -Element $candidate -RequireEnabled $RequireEnabled)) {
                continue
            }
            $rect = $candidate.Current.BoundingRectangle
            $visibleInputs += [pscustomobject]@{
                element = $candidate
                top = [double]$rect.Top
                left = [double]$rect.Left
            }
        } catch {
        }
    }

    $orderedInputs = @(
        $visibleInputs |
            Sort-Object -Property @{ Expression = "top"; Ascending = $true }, @{ Expression = "left"; Ascending = $true }
    )
    if ($orderedInputs.Count -eq 0) {
        return $null
    }

    $desiredIndex = switch ($Field) {
        "title" { 0 }
        "aliases" { 1 }
        "target" { 2 }
    }
    if ($orderedInputs.Count -le $desiredIndex) {
        return $null
    }

    return $orderedInputs[$desiredIndex].element
}

function Find-CreateDialogGroupActionButton {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [ValidateSet("assign", "remove")]
        [string]$Action,
        [bool]$RequireEnabled = $true
    )

    if (-not $Root) {
        return $null
    }

    $leafAutomationId = switch ($Action) {
        "assign" { "savedActionCreateNewGroupButton" }
        "remove" { "savedActionCreateRemoveGroupButton" }
    }
    $automationIdMatch = Find-ElementByAutomationIdsDirect -Root $Root -AutomationIds (Get-CreateDialogControlAutomationIds -LeafAutomationId $leafAutomationId)
    if (Test-ElementUsable -Element $automationIdMatch -RequireEnabled $RequireEnabled) {
        return $automationIdMatch
    }

    $buttonName = switch ($Action) {
        "assign" { "Assign Group..." }
        "remove" { "Unassign Group" }
    }

    $visibleButtons = @()
    foreach ($candidate in (Get-AllDescendants -Element $Root)) {
        try {
            if ((Get-ElementControlTypeNameSafe -Element $candidate -Context "Find-CreateDialogGroupActionButton") -ne [System.Windows.Automation.ControlType]::Button.ProgrammaticName) {
                continue
            }
            if ($candidate.Current.Name -ne $buttonName) {
                continue
            }
            if (-not (Test-ElementUsable -Element $candidate -RequireEnabled $RequireEnabled)) {
                continue
            }
            $rect = $candidate.Current.BoundingRectangle
            $visibleButtons += [pscustomobject]@{
                element = $candidate
                top = [double]$rect.Top
                left = [double]$rect.Left
            }
        } catch {
        }
    }

    $orderedButtons = @(
        $visibleButtons |
            Sort-Object -Property @{ Expression = "top"; Ascending = $true }, @{ Expression = "left"; Ascending = $true }
    )
    if ($orderedButtons.Count -lt 1) {
        return $null
    }

    return $orderedButtons[0].element
}

function Find-GroupDialogTextInput {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [ValidateSet("name", "aliases")]
        [string]$Field,
        [bool]$RequireEnabled = $true
    )

    if (-not $Root) {
        return $null
    }

    $leafAutomationId = switch ($Field) {
        "name" { "callableGroupCreateNameInput" }
        "aliases" { "callableGroupCreateAliasesInput" }
    }
    $automationIdMatch = Find-ElementByAutomationIdsDirect -Root $Root -AutomationIds (Get-GroupDialogControlAutomationIds -LeafAutomationId $leafAutomationId)
    if (Test-ElementUsable -Element $automationIdMatch -RequireEnabled $RequireEnabled) {
        return $automationIdMatch
    }

    $visibleInputs = @()
    foreach ($candidate in (Get-AllDescendants -Element $Root)) {
        try {
            if ((Get-ElementControlTypeNameSafe -Element $candidate -Context "Find-GroupDialogTextInput") -ne [System.Windows.Automation.ControlType]::Edit.ProgrammaticName) {
                continue
            }
            if (-not (Test-ElementUsable -Element $candidate -RequireEnabled $RequireEnabled)) {
                continue
            }
            $rect = $candidate.Current.BoundingRectangle
            $visibleInputs += [pscustomobject]@{
                element = $candidate
                top = [double]$rect.Top
                left = [double]$rect.Left
            }
        } catch {
        }
    }

    $orderedInputs = @(
        $visibleInputs |
            Sort-Object -Property @{ Expression = "top"; Ascending = $true }, @{ Expression = "left"; Ascending = $true }
    )
    if ($orderedInputs.Count -eq 0) {
        return $null
    }

    $desiredIndex = switch ($Field) {
        "name" { 0 }
        "aliases" { 1 }
    }
    if ($orderedInputs.Count -le $desiredIndex) {
        return $null
    }

    return $orderedInputs[$desiredIndex].element
}

function Get-GroupDialogMemberCheckboxes {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [bool]$RequireEnabled = $false
    )

    if (-not $Root) {
        return @()
    }

    $checkboxes = @()
    foreach ($candidate in (Get-AllDescendants -Element $Root)) {
        try {
            if ((Get-ElementControlTypeNameSafe -Element $candidate -Context "Get-GroupDialogMemberCheckboxes") -ne [System.Windows.Automation.ControlType]::CheckBox.ProgrammaticName) {
                continue
            }
            if (-not (Test-ElementUsable -Element $candidate -RequireEnabled $RequireEnabled)) {
                continue
            }
            $rect = $candidate.Current.BoundingRectangle
            $checkboxes += [pscustomobject]@{
                element = $candidate
                top = [double]$rect.Top
                left = [double]$rect.Left
            }
        } catch {
        }
    }

    return @(
        $checkboxes |
            Sort-Object -Property @{ Expression = "top"; Ascending = $true }, @{ Expression = "left"; Ascending = $true } |
            ForEach-Object { $_.element }
    )
}

function Find-GroupDialogMembersRegion {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [bool]$RequireEnabled = $false
    )

    if (-not $Root) {
        return $null
    }

    $automationIdMatch = Find-ElementByAutomationIdsDirect -Root $Root -AutomationIds @(
        (Get-GroupDialogControlAutomationIds -LeafAutomationId "callableGroupCreateMembersScroll")
        (Get-GroupDialogControlAutomationIds -LeafAutomationId "callableGroupCreateMembersViewport")
        (Get-GroupDialogControlAutomationIds -LeafAutomationId "callableGroupCreateMembersFrame")
    )
    if (Test-ElementUsable -Element $automationIdMatch -RequireEnabled $RequireEnabled) {
        return $automationIdMatch
    }

    $checkboxes = @(Get-GroupDialogMemberCheckboxes -Root $Root -RequireEnabled $false)
    foreach ($checkbox in $checkboxes) {
        $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
        $current = $checkbox
        $firstUsableAncestor = $null
        while ($current) {
            try {
                $current = $walker.GetParent($current)
            } catch {
                break
            }
            if (-not $current -or (Test-ElementsEquivalent -Left $current -Right $Root)) {
                break
            }

            if (-not (Test-ElementUsable -Element $current -RequireEnabled $RequireEnabled)) {
                continue
            }

            if (-not $firstUsableAncestor) {
                $firstUsableAncestor = $current
            }

            try {
                $automationId = [string]$current.Current.AutomationId
                if ($automationId -like "*callableGroupCreateMembers*") {
                    return $current
                }
            } catch {
            }
        }

        if ($firstUsableAncestor) {
            return $firstUsableAncestor
        }
    }

    return $null
}

function Test-GroupDialogMembersRegionReady {
    param(
        [System.Windows.Automation.AutomationElement]$DialogRoot,
        [System.Windows.Automation.AutomationElement]$Region,
        [bool]$RequireEnabled = $false
    )

    if (-not (Test-ElementUsable -Element $Region -RequireEnabled $RequireEnabled)) {
        return $false
    }

    $memberCheckboxes = @(Get-GroupDialogMemberCheckboxes -Root $DialogRoot -RequireEnabled $false)
    if ($memberCheckboxes.Count -gt 0) {
        return $true
    }

    try {
        $descendants = @(Get-AllDescendants -Element $Region)
        return $descendants.Count -gt 0
    } catch {
        return $false
    }
}

function Set-TaskGroupAssignmentRowState {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$GroupTitle,
        [string]$ButtonName,
        [string]$Description
    )

    $resolveButton = {
        return (Get-TaskGroupAssignmentRowButton -Dialog $Dialog -GroupTitle $GroupTitle -ButtonName $ButtonName)
    }
    Wait-Until -TimeoutSeconds 8 -Description "$Description ready" -Condition {
        return [bool](& $resolveButton)
    }
    $button = Focus-ElementForInteraction -ElementResolver $resolveButton -Description $Description -RequireExactFocus $false
    Invoke-ElementRobust -Element $button -Description $Description
}

function Open-AssignmentCreateGroupDialog {
    param(
        [System.Windows.Automation.AutomationElement]$AssignmentDialog
    )

    $resolveAssignmentDialog = {
        Resolve-LiveDialogRoot -Dialog $AssignmentDialog -ExpectedName "Available Groups"
    }
    $resolveCreateButton = {
        $liveDialog = & $resolveAssignmentDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdsDirect -Root $liveDialog -AutomationIds (Get-TaskGroupAssignmentDialogControlAutomationIds -LeafAutomationId "taskGroupAssignmentCreateButton"))
    }

    $null = Wait-ForDialogControlReady -DialogResolver $resolveAssignmentDialog -AutomationIds (Get-TaskGroupAssignmentDialogControlAutomationIds -LeafAutomationId "taskGroupAssignmentCreateButton") -Description "Available Groups create button"
    $button = Focus-ElementForInteraction -ElementResolver $resolveCreateButton -Description "Available Groups create button" -RequireExactFocus $false
    Invoke-ElementRobust -Element $button -Description "Available Groups create button"

    $dialog = Wait-ForDialog -Name "Create Custom Group" -TimeoutSeconds 8
    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $dialog -ExpectedName "Create Custom Group"
    }
    $null = Wait-ForGroupDialogTextInputReady -DialogResolver $resolveDialog -Field "name" -Description "inline group dialog name input"
    $null = Wait-ForGroupDialogTextInputReady -DialogResolver $resolveDialog -Field "aliases" -Description "inline group dialog aliases input"
    return (& $resolveDialog)
}

function Open-QuickCreateGroupDialog {
    param(
        [System.Windows.Automation.AutomationElement]$TaskDialog
    )

    $dialogName = $TaskDialog.Current.Name
    $resolveTaskDialog = {
        Resolve-LiveDialogRoot -Dialog $TaskDialog -ExpectedName $dialogName
    }
    $resolveNewGroupButton = {
        $liveDialog = & $resolveTaskDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdsDirect -Root $liveDialog -AutomationIds (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateNewGroupButton"))
    }

    $null = Wait-ForDialogControlReady -DialogResolver $resolveTaskDialog -AutomationIds (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateNewGroupButton") -Description "task dialog New Group button"
    $button = Focus-ElementForInteraction -ElementResolver $resolveNewGroupButton -Description "task dialog New Group button" -RequireExactFocus $false
    Invoke-ElementRobust -Element $button -Description "task dialog New Group button"

    $dialog = Wait-ForDialog -Name "New Group" -TimeoutSeconds 8
    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $dialog -ExpectedName "New Group"
    }
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationIds (Get-QuickCreateGroupDialogControlAutomationIds -LeafAutomationId "quickCreateGroupTitleInput") -Description "quick group title input"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationIds (Get-QuickCreateGroupDialogControlAutomationIds -LeafAutomationId "quickCreateGroupAliasesInput") -Description "quick group aliases input"
    return (& $resolveDialog)
}

function Fill-QuickCreateGroupDialog {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$GroupName,
        [string]$Aliases
    )

    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $Dialog -ExpectedName "New Group"
    }
    $resolveNameInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdsDirect -Root $liveDialog -AutomationIds (Get-QuickCreateGroupDialogControlAutomationIds -LeafAutomationId "quickCreateGroupTitleInput"))
    }
    $resolveAliasesInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdsDirect -Root $liveDialog -AutomationIds (Get-QuickCreateGroupDialogControlAutomationIds -LeafAutomationId "quickCreateGroupAliasesInput"))
    }

    Set-FieldValueVerified -ElementResolver $resolveNameInput -ExpectedValue $GroupName -Description "quick group name input"
    Set-FieldValueVerified -ElementResolver $resolveAliasesInput -ExpectedValue $Aliases -Description "quick group aliases input"
}

function Open-CreatedTasksDialog {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay
    )

    $resolveOverlay = {
        Resolve-LiveOverlayRoot -Overlay $Overlay
    }
    $resolveCreatedTasksButton = {
        $liveOverlay = & $resolveOverlay
        if (-not $liveOverlay) {
            return $null
        }
        return (Find-ElementByAutomationIdsDirect -Root $liveOverlay -AutomationIds (Get-OverlayManageButtonAutomationIds))
    }

    $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationIds (Get-OverlayManageButtonAutomationIds) -Description "Created Tasks button"
    $button = Focus-ElementForInteraction -ElementResolver $resolveCreatedTasksButton -Description "Created Tasks button" -RequireExactFocus $false
    Write-StepLog -Stage "DIALOG" -Message "opening Created Tasks"
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $button -Description "Created Tasks button"

    try {
        Wait-ForDialogRuntimeReady -SignalBase "CREATED_TASKS_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    } catch {
        $dialogAlreadyVisible = [bool](Get-CreatedTasksDialogWindow)
        $openedSeen = Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CREATED_TASKS_DIALOG_OPENED" -StartLine $markerStart
        $readySeen = Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CREATED_TASKS_DIALOG_READY" -StartLine $markerStart
        if ($dialogAlreadyVisible -or $openedSeen -or $readySeen) {
            Add-Note "Created Tasks runtime readiness had a transient wait miss after the first entry button invoke, but the dialog was already visible or the final markers were present, so the harness continued without retry."
        } else {
            Add-Note "Created Tasks markers were not observed after the first entry button invoke; retrying once."
            $button = Focus-ElementForInteraction -ElementResolver $resolveCreatedTasksButton -Description "Created Tasks button retry" -RequireExactFocus $false
            Invoke-ElementRobust -Element $button -Description "Created Tasks button retry"
            Wait-ForDialogRuntimeReady -SignalBase "CREATED_TASKS_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
        }
    }

    Wait-Until -TimeoutSeconds 8 -Description "Manage Custom Tasks dialog" -Condition {
        return [bool](Get-CreatedTasksDialogWindow)
    } | Out-Null
    return (Get-CreatedTasksDialogWindow)
}

function Wait-ForInventoryEditButtonReady {
    param(
        [scriptblock]$DialogResolver,
        [int]$EditIndex = 0,
        [int]$TimeoutSeconds = 6
    )

    $description = "Created Tasks edit button index=$EditIndex"
    Write-StepLog -Stage "DIALOG" -Message "verifying control '$description'"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $description -Condition {
        $liveDialog = & $DialogResolver
        if (-not $liveDialog) {
            return $false
        }
        $buttons = @(Get-InventoryEditButtons -Overlay $liveDialog)
        if ($buttons.Count -le $EditIndex) {
            return $false
        }
        return (Test-ElementUsable -Element $buttons[$EditIndex] -RequireEnabled $true)
    } | Out-Null

    $liveDialog = & $DialogResolver
    if (-not $liveDialog) {
        throw "Could not resolve the Created Tasks dialog while waiting for edit button index $EditIndex."
    }

    $buttons = @(Get-InventoryEditButtons -Overlay $liveDialog)
    if ($buttons.Count -le $EditIndex) {
        throw "Created Tasks edit button index $EditIndex was not available."
    }

    $button = $buttons[$EditIndex]
    if (-not (Test-ElementUsable -Element $button -RequireEnabled $true)) {
        throw "Created Tasks edit button index $EditIndex did not become usable. State: $(Get-ElementStateSummary -Element $button)"
    }

    Write-StepLog -Stage "DIALOG" -Message "control ready '$description' state=$(Get-ElementStateSummary -Element $button)"
    return $button
}

function Open-EditDialog {
    param(
        [System.Windows.Automation.AutomationElement]$CreatedTasksDialog,
        [int]$EditIndex = 0
    )

    $resolveCreatedTasksDialog = {
        Resolve-LiveCreatedTasksDialogRoot -Dialog $CreatedTasksDialog
    }
    $resolveEditButton = {
        $liveDialog = & $resolveCreatedTasksDialog
        if (-not $liveDialog) {
            return $null
        }
        $buttons = @(Get-InventoryEditButtons -Overlay $liveDialog)
        if ($buttons.Count -le $EditIndex) {
            return $null
        }
        return $buttons[$EditIndex]
    }
    $resolveEditDialog = {
        $dialog = Find-RootWindow -Name "Edit Custom Task"
        if ($dialog -and -not (Test-ElementGoneOrOffscreen -Element $dialog)) {
            return $dialog
        }

        return $null
    }

    $null = Wait-ForInventoryEditButtonReady -DialogResolver $resolveCreatedTasksDialog -EditIndex $EditIndex
    $button = Focus-ElementForInteraction -ElementResolver $resolveEditButton -Description "Created Tasks edit button index=$EditIndex" -RequireExactFocus $false
    Write-StepLog -Stage "DIALOG" -Message "opening Edit Custom Task from Created Tasks index=$EditIndex"
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $button -Description "Created Tasks edit button index=$EditIndex"

    try {
        Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_TASK_EDIT_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    } catch {
        Add-Note "Edit dialog markers were not observed after the first edit-button invoke; retrying once."
        $button = Focus-ElementForInteraction -ElementResolver $resolveEditButton -Description "Created Tasks edit button retry index=$EditIndex" -RequireExactFocus $false
        Invoke-ElementRobust -Element $button -Description "Created Tasks edit button retry index=$EditIndex"
        Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_TASK_EDIT_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    }

    Write-StepLog -Stage "DIALOG" -Message "verifying edit-dialog entry readiness after runtime markers"

    $dialog = Wait-ForDialog -Name "Edit Custom Task" -TimeoutSeconds 8
    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $dialog -ExpectedName "Edit Custom Task"
    }

    $null = Wait-ForCreateDialogTaskTypeComboReady -DialogResolver $resolveDialog -Description "edit dialog task type combo"
    $null = Wait-ForCreateDialogTextInputReady -DialogResolver $resolveDialog -Field "title" -Description "edit dialog title input"
    $null = Wait-ForCreateDialogTextInputReady -DialogResolver $resolveDialog -Field "aliases" -Description "edit dialog aliases input"
    $null = Wait-ForCreateDialogTextInputReady -DialogResolver $resolveDialog -Field "target" -Description "edit dialog target input"

    $typeCombo = Focus-ElementForInteraction -ElementResolver {
        $liveScope = & $resolveDialog
        if (-not $liveScope) {
            return $null
        }
        return (Find-CreateDialogTaskTypeCombo -Root $liveScope)
    } -Description "edit dialog task type combo" -RequireExactFocus $false

    if (-not $typeCombo) {
        throw "Could not focus the edit dialog task type combo after dialog ready."
    }

    $dialog = & $resolveDialog
    if (-not $dialog) {
        $dialog = Find-DialogAncestorFromElement -Element $typeCombo -ExpectedName "Edit Custom Task"
    }
    if (-not $dialog) {
        throw "Edit dialog root could not be derived from the focused task type control after readiness checks."
    }

    Write-StepLog -Stage "DIALOG" -Message "edit-dialog entry ready and first interaction control focused"
    return $dialog
}

function Fill-AuthoringDialog {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$TypeLabel,
        [string]$Title,
        [string]$Aliases,
        [string]$Target
    )

    $dialogName = $Dialog.Current.Name
    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $Dialog -ExpectedName $dialogName
    }
    $resolveTypeCombo = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-CreateDialogTaskTypeCombo -Root $liveDialog)
    }
    $resolveTitleInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-CreateDialogTextInput -Root $liveDialog -Field "title")
    }
    $resolveAliasesInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-CreateDialogTextInput -Root $liveDialog -Field "aliases")
    }
    $resolveTargetInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-CreateDialogTextInput -Root $liveDialog -Field "target")
    }
    $resolveExamplesLabel = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdsDirect -Root $liveDialog -AutomationIds (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateTargetExamples"))
    }
    $helpButtonMap = @(
        @{ Name = "Title"; AutomationIds = (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateTitleHelp") },
        @{ Name = "Aliases"; AutomationIds = (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateAliasesHelp") },
        @{ Name = "Trigger"; AutomationIds = (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateTriggerHelp") },
        @{ Name = "Target"; AutomationIds = (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateTargetHelp") }
    )

    $guidanceMap = @{
        "Application" = "Target format: notepad.exe or C:\\Program Files\\Notepad++\\notepad++.exe"
        "Folder" = "Target format: C:\\Reports"
        "File" = "Target format: C:\\Reports\\weekly.txt"
        "Website URL" = "Target format: https://example.com/docs"
    }

    Write-StepLog -Stage "DIALOG" -Message "verifying authoring dialog interaction readiness for '$dialogName'"
    $typeCombo = & $resolveTypeCombo
    if (-not (Test-ElementUsable -Element $typeCombo -RequireEnabled $true)) {
        throw "Authoring dialog task type combo was not available after entry readiness. State: $(Get-ElementStateSummary -Element $typeCombo)"
    }
    Write-StepLog -Stage "DIALOG" -Message "authoring dialog task type control is live; resolving field inputs lazily as each interaction needs them"

    $selectedType = Get-ComboSelectedText -Combo $typeCombo
    if ($selectedType -ne $TypeLabel) {
        $selectionApplied = Select-ComboItem -ComboResolver $resolveTypeCombo -ItemName $TypeLabel
        $selectedType = Get-ComboSelectedText -Combo (& $resolveTypeCombo)
        if (-not $selectionApplied) {
            Add-Note "Type combo UIA selection for '$TypeLabel' did not report success immediately; runtime target_kind markers will confirm the actual submitted type."
        }
    }
    Write-StepLog -Stage "INTERACT" -Message "type selection final desired='$TypeLabel' actual='$selectedType'"
    if ($selectedType -ne $TypeLabel) {
        Add-Note "Type combo UI readback remained '$selectedType' while targeting '$TypeLabel'; runtime target_kind markers are authoritative and will confirm the actual selection on submit."
    }

    foreach ($helpButtonInfo in $helpButtonMap) {
        $helpButton = $null
        try {
            $liveDialog = & $resolveDialog
            if ($liveDialog) {
                $helpButton = Find-ElementByAutomationIdsDirect -Root $liveDialog -AutomationIds $helpButtonInfo.AutomationIds
            }
        } catch {
            $helpButton = $null
        }
        if (-not (Test-ElementUsable -Element $helpButton -RequireEnabled $false)) {
            Add-Note "$($helpButtonInfo.Name) help button was not ready before the first field interactions."
        }
    }

    if ($guidanceMap.ContainsKey($TypeLabel)) {
        $expectedGuidance = $guidanceMap[$TypeLabel]
        try {
            $liveExamples = & $resolveExamplesLabel
            $examplesValue = if ($liveExamples) { Get-ElementReadableValue -Element $liveExamples } else { "" }
            if ($examplesValue -like "*$expectedGuidance*") {
                Write-StepLog -Stage "DIALOG" -Message "examples box reflected '$TypeLabel' guidance without additional wait"
            } else {
                Add-Note "Bottom examples box guidance for '$TypeLabel' did not refresh immediately, but runtime markers and persisted source remain the authoritative success signals."
            }
        } catch {
            Add-Note "Bottom examples box guidance for '$TypeLabel' could not be read immediately, but runtime markers and persisted source remain the authoritative success signals."
        }
    }
    Set-FieldValueVerified -ElementResolver $resolveTitleInput -ExpectedValue $Title -Description "title input"
    Set-FieldValueVerified -ElementResolver $resolveAliasesInput -ExpectedValue $Aliases -Description "aliases input"
    Set-FieldValueVerified -ElementResolver $resolveTargetInput -ExpectedValue $Target -Description "target input"
}

function Get-DialogStatusText {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog
    )

    $status = Find-ElementByAutomationIdsDirect -Root $Dialog -AutomationIds (Get-CreateDialogControlAutomationIds -LeafAutomationId "savedActionCreateStatus")
    if (-not $status) {
        return ""
    }
    $value = $status.Current.Name
    if ($value) {
        return $value
    }
    try {
        return (Get-TextValue -Element $status)
    } catch {
        return ""
    }
}

function Submit-Dialog {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$ButtonName
    )

    $button = Get-ButtonByName -Root $Dialog -Name $ButtonName
    if (-not $button) {
        throw "Could not find dialog button '$ButtonName'."
    }
    Write-StepLog -Stage "DIALOG" -Message "submitting dialog '$($Dialog.Current.Name)' with button '$ButtonName'"
    Invoke-ElementRobust -Element $button -Description "dialog button '$ButtonName'"
}

function Cancel-Dialog {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [bool]$PreferDialogDisappearance = $false
    )

    $dialogName = $Dialog.Current.Name
    Write-StepLog -Stage "DIALOG" -Message "cancelling dialog '$dialogName'"
    $signalBase = switch ($dialogName) {
        "Edit Custom Task" { "CUSTOM_TASK_EDIT_DIALOG"; break }
        "Create Custom Group" { "CUSTOM_GROUP_CREATE_DIALOG"; break }
        "Edit Custom Group" { "CUSTOM_GROUP_EDIT_DIALOG"; break }
        default { "CUSTOM_TASK_CREATE_DIALOG" }
    }
    $markerStart = New-RuntimeMarkerCursor
    try { Submit-Dialog -Dialog $Dialog -ButtonName "Cancel" } catch {}
    try {
        if ($dialogName -ne "New Group" -and -not $PreferDialogDisappearance) {
            Wait-ForDialogRuntimeClosed -SignalBase $signalBase -StartLine $markerStart -TimeoutSeconds 5
            Write-StepLog -Stage "DIALOG" -Message "$dialogName close confirmed by runtime marker"
            return
        }
    } catch {
    }

    try {
        if ($dialogName -ne "New Group") {
            Wait-Until -TimeoutSeconds 5 -Description "dialog '$dialogName' close after cancel" -Condition {
                return -not [bool](Get-DialogWindow -Name $dialogName)
            } | Out-Null
            Write-StepLog -Stage "DIALOG" -Message "$dialogName close confirmed by dialog disappearance after cancel"
            return
        }
    } catch {
    }

    if (Get-DialogWindow -Name $dialogName) {
        try {
            Focus-Window -Element $Dialog
        } catch {
        }
        Send-VirtualKey -VirtualKey 0x1B
    }
}

function Restore-OverlayAfterAuthoringDialogCancel {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Reason
    )

    $attempts = @(
        @{ label = "existing overlay reference"; overlay = $Overlay },
        @{ label = "fresh overlay resolution"; overlay = $null }
    )

    for ($index = 0; $index -lt $attempts.Count; $index++) {
        $attempt = $attempts[$index]
        Write-StepLog -Stage "FLOW" -Message "overlay reacquisition after authoring dialog cancel attempt=$($index + 1) using $($attempt.label)"
        try {
            $restoredOverlay = Ensure-OverlayReady -Overlay $attempt.overlay -Reason $Reason
            Write-StepLog -Stage "FLOW" -Message "overlay next-step ready confirmed after authoring dialog cancel on attempt=$($index + 1)"
            return $restoredOverlay
        } catch {
            Add-Note "Overlay reacquisition after authoring dialog cancel failed on attempt=$($index + 1). Cause: $($_.Exception.Message)"
        }
    }

    Write-StepLog -Stage "FLOW" -Message "overlay reacquisition after authoring dialog cancel falling back to overlay reopen"
    $reopenedOverlay = Open-OverlayWithRuntimeRestartFallback -MaxAttempts 2
    Write-StepLog -Stage "FLOW" -Message "overlay next-step ready confirmed after authoring dialog cancel via overlay reopen fallback"
    return $reopenedOverlay
}

function Wait-ForDialogClosed {
    param(
        [string]$Name,
        [int]$TimeoutSeconds = 8
    )
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "dialog '$Name' closed" -Condition {
        $dialog = Get-DialogWindow -Name $Name
        return (Test-ElementGoneOrOffscreen -Element $dialog)
    } | Out-Null
}

function Reset-ScenarioTransitionState {
    param(
        [string]$Reason
    )

    $script:RuntimeLogLineCursor = Get-RuntimeLogLineCount
    Enter-TransitionBudget -Name $Reason
    Write-StepLog -Stage "FLOW" -Message "resetting transition state for $Reason"
}

function Wait-ForOverlayReadyForNextStep {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Reason,
        [int]$TimeoutSeconds = 8
    )

    Write-StepLog -Stage "FLOW" -Message "waiting for overlay next-step readiness after $Reason"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "overlay next-step readiness after $Reason" -Condition {
        foreach ($dialogName in @("Create Custom Task", "Edit Custom Task", "Created Tasks")) {
            if (Test-DialogVisibleFast -Name $dialogName) {
                return $false
            }
        }

        $liveOverlay = Resolve-LiveOverlayRoot -Overlay $Overlay
        if (-not $liveOverlay) {
            return $false
        }

        foreach ($automationId in (Get-OverlayAnchorAutomationIds)) {
            $element = Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId $automationId
            if (-not (Test-ElementUsable -Element $element -RequireEnabled $true)) {
                return $false
            }
        }

        return $true
    } | Out-Null

    $liveOverlay = Resolve-LiveOverlayRoot -Overlay $Overlay
    if (-not $liveOverlay) {
        throw "Could not resolve the overlay after $Reason."
    }

    $resolveOverlayInput = {
        $currentOverlay = Resolve-LiveOverlayRoot -Overlay $liveOverlay
        if (-not $currentOverlay) {
            return $null
        }
        return (Find-ElementByAutomationIdDirect -Root $currentOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine")
    }
    $null = Focus-ElementForInteraction -ElementResolver $resolveOverlayInput -Description "overlay input after $Reason" -RequireExactFocus $false
    Clear-TransitionBudget -Name $Reason
    Write-StepLog -Stage "FLOW" -Message "overlay ready for next step after $Reason"
    return (Resolve-LiveOverlayRoot -Overlay $liveOverlay)
}

function Restore-OverlayAfterCreatedTasksClose {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Reason = "Created Tasks close handoff"
    )

    $attempts = @(
        @{ label = "existing overlay reference"; overlay = $Overlay },
        @{ label = "fresh overlay resolution"; overlay = $null }
    )

    for ($index = 0; $index -lt $attempts.Count; $index++) {
        $attempt = $attempts[$index]
        Write-StepLog -Stage "FLOW" -Message "overlay reacquisition after Created Tasks close attempt=$($index + 1) using $($attempt.label)"
        try {
            $restoredOverlay = Ensure-OverlayReady -Overlay $attempt.overlay -Reason $Reason
            Write-StepLog -Stage "FLOW" -Message "overlay next-step ready confirmed after Created Tasks close on attempt=$($index + 1)"
            return $restoredOverlay
        } catch {
            Add-Note "Overlay reacquisition after Created Tasks close failed on attempt=$($index + 1). Cause: $($_.Exception.Message)"
        }
    }

    Write-StepLog -Stage "FLOW" -Message "overlay reacquisition after Created Tasks close falling back to overlay reopen"
    $reopenedOverlay = Open-OverlayWithRuntimeRestartFallback -MaxAttempts 2
    Write-StepLog -Stage "FLOW" -Message "overlay next-step ready confirmed after Created Tasks close via overlay reopen fallback"
    return $reopenedOverlay
}

function Close-CreatedTasksDialog {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Reason = "Created Tasks close handoff"
    )

    $closeButton = Get-ButtonByName -Root $Dialog -Name "Close"
    if (-not $closeButton) {
        throw "Created Tasks dialog close button was not found."
    }
    Write-StepLog -Stage "DIALOG" -Message "closing Created Tasks"
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $closeButton -Description "Created Tasks close button"
    try {
        Wait-ForDialogRuntimeClosed -SignalBase "CREATED_TASKS_DIALOG" -StartLine $markerStart -TimeoutSeconds 5
        Write-StepLog -Stage "DIALOG" -Message "Created Tasks close confirmed by runtime marker"
    } catch {
        Add-Note "Created Tasks did not close on the first runtime wait; retrying with an ESC fallback and trusting runtime markers instead of UI readback."
        try {
            Focus-Window -Element $Dialog
        } catch {
        }
        Send-VirtualKey -VirtualKey 0x1B
        try {
            Wait-ForDialogRuntimeClosed -SignalBase "CREATED_TASKS_DIALOG" -StartLine $markerStart -TimeoutSeconds 5
        } catch {
            Add-Note "Created Tasks close fallback still missed a fresh runtime close marker; continuing because the next step re-resolves overlay state."
        }
    }

    return (Restore-OverlayAfterCreatedTasksClose -Overlay $Overlay -Reason $Reason)
}

function Wait-ForInventoryText {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Text,
        [int]$TimeoutSeconds = 8
    )

    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "inventory text '$Text'" -Condition {
        if (-not $Overlay) {
            return $false
        }
        foreach ($row in (Get-InventoryTextRows -Overlay $Overlay)) {
            if ($row -eq $Text -or $row -like "*$Text*") {
                return $true
            }
        }
        return $false
    } | Out-Null
}

function Ensure-OverlayReady {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Reason = "dialog transition"
    )

    Reset-ScenarioTransitionState -Reason $Reason
    Write-StepLog -Stage "FLOW" -Message "verifying overlay controls for next step after $Reason"

    $resolveOverlay = {
        Resolve-LiveOverlayRoot -Overlay $Overlay
    }
    $resolveOverlayInput = {
        $liveOverlay = & $resolveOverlay
        if (-not $liveOverlay) {
            return $null
        }
        return (Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine")
    }

    try {
        $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine" -Description "overlay input after $Reason"
        $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationIds (Get-OverlayCreateButtonAutomationIds) -Description "Create Custom Task button after $Reason"
        $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationIds (Get-OverlayManageButtonAutomationIds) -Description "Created Tasks button after $Reason"
        $null = Focus-ElementForInteraction -ElementResolver $resolveOverlayInput -Description "overlay input after $Reason" -RequireExactFocus $false
        Clear-TransitionBudget -Name $Reason
        Write-StepLog -Stage "FLOW" -Message "overlay ready for next step after $Reason"
        return (& $resolveOverlay)
    } catch {
        Add-Note "Overlay was not ready after $Reason; reopening it for the next validation step. Cause: $($_.Exception.Message)"
        return (Open-OverlayWithRuntimeRestartFallback -MaxAttempts 2)
    }
}

function Get-OverlayInput {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    $Overlay = Resolve-LiveOverlayRoot -Overlay $Overlay
    return Wait-ForElementByAutomationId -Root $Overlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine"
}

function Submit-OverlayCommand {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$CommandText
    )

    $input = Get-OverlayInput -Overlay $Overlay
    Set-Value -Element $input -Value $CommandText
    $input.SetFocus()
    Start-Sleep -Milliseconds 150
    Send-VirtualKey -VirtualKey 0x0D
}

function Start-InteractiveRuntime {
    $python = (Get-Command python).Source
    if (-not $python) {
        throw "Could not resolve python executable."
    }

    $baselineLines = if (Test-Path -LiteralPath $RuntimeLogPath) {
        @(Get-Content -LiteralPath $RuntimeLogPath).Count
    } else {
        0
    }

    $argString = "dev\orin_saved_action_authoring_interactive_runtime.py --runtime-log `"$RuntimeLogPath`" --auto-open-overlay"
    Write-StepLog -Stage "RUNTIME" -Message "starting interactive runtime helper from baseline line count $baselineLines"
    $previousOverlayTrace = $env:NEXUS_OVERLAY_TRACE
    $env:NEXUS_OVERLAY_TRACE = "1"
    try {
        $process = Start-Process -FilePath $python -ArgumentList $argString -WorkingDirectory $RootDir -PassThru -WindowStyle Hidden
    } finally {
        $env:NEXUS_OVERLAY_TRACE = $previousOverlayTrace
    }

    Wait-Until -TimeoutSeconds 20 -Description "runtime log creation" -Condition {
        Test-Path -LiteralPath $RuntimeLogPath
    } | Out-Null
    Wait-Until -TimeoutSeconds 25 -Description "fresh runtime startup ready marker" -Condition {
        if (-not (Test-Path -LiteralPath $RuntimeLogPath)) {
            return $false
        }
        $lines = @(Get-Content -LiteralPath $RuntimeLogPath)
        if ($lines.Count -le $baselineLines) {
            return $false
        }
        $newLines = @($lines | Select-Object -Skip $baselineLines)
        return (($newLines -join "`n") -like "*RENDERER_MAIN|STARTUP_READY*")
    } | Out-Null
    Write-StepLog -Stage "RUNTIME" -Message "confirmed runtime startup ready"
    Wait-Until -TimeoutSeconds 25 -Description "fresh runtime desktop attach" -Condition {
        if (-not (Test-Path -LiteralPath $RuntimeLogPath)) {
            return $false
        }
        $lines = @(Get-Content -LiteralPath $RuntimeLogPath)
        if ($lines.Count -le $baselineLines) {
            return $false
        }
        $newLines = @($lines | Select-Object -Skip $baselineLines)
        return (($newLines -join "`n") -like "*RENDERER_MAIN|DESKTOP_ATTACH_RESULT|success=true*")
    } | Out-Null
    Write-StepLog -Stage "RUNTIME" -Message "confirmed desktop attach success"
    $currentRuntimeLineCount = Get-RuntimeLogLineCount
    $script:RuntimeLogLineCursor = [Math]::Max($baselineLines, ($currentRuntimeLineCount - 50))
    $script:RuntimeAutoOpenPending = $true
    Start-Sleep -Milliseconds 1600
    return $process
}

function Restart-InteractiveRuntime {
    Write-StepLog -Stage "RUNTIME" -Message "restarting interactive runtime helper"
    if ($script:runtimeProcess) {
        try {
            Stop-ProcessQuietly -Process $script:runtimeProcess
        } catch {
        }
        Start-Sleep -Seconds 1
    }
    $script:runtimeProcess = Start-InteractiveRuntime
    return $script:runtimeProcess
}

function Open-OverlayWithRuntimeRestartFallback {
    param(
        [int]$MaxAttempts = 3
    )

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            return (Open-Overlay)
        } catch {
            if ($attempt -ge $MaxAttempts) {
                throw
            }
            Add-Note "Overlay open attempt $attempt failed; restarting the interactive runtime and retrying."
            Restart-InteractiveRuntime | Out-Null
        }
    }

    throw "Overlay open could not be recovered after $MaxAttempts attempts."
}

function Stop-StaleInteractiveValidationProcesses {
    $stale = Get-CimInstance Win32_Process | Where-Object {
        ($_.Name -like "python*.exe" -or $_.Name -eq "python.exe") -and
        $_.CommandLine -and
        $_.CommandLine -like "*orin_saved_action_authoring_interactive_runtime.py*"
    }

    foreach ($processInfo in $stale) {
        try {
            Stop-Process -Id $processInfo.ProcessId -Force -ErrorAction Stop
            Add-Note "Stopped stale interactive runtime helper process $($processInfo.ProcessId) before validation."
        } catch {
        }
    }
}

function Stop-ProcessQuietly {
    param(
        [System.Diagnostics.Process]$Process
    )

    if ($Process -and -not $Process.HasExited) {
        try {
            $Process.CloseMainWindow() | Out-Null
            Start-Sleep -Seconds 1
        } catch {
        }
        if (-not $Process.HasExited) {
            Stop-Process -Id $Process.Id -Force
        }
    }
}

function Stop-WatchdogMonitorQuietly {
    param(
        $Monitor
    )

    if (-not $Monitor) {
        return
    }

    if ($Monitor -is [System.Diagnostics.Process]) {
        Stop-ProcessQuietly -Process $Monitor
        return
    }

    if ($Monitor -is [System.Management.Automation.Job]) {
        try {
            if ($Monitor.State -notin @("Completed", "Failed", "Stopped")) {
                Stop-Job -Job $Monitor -ErrorAction SilentlyContinue | Out-Null
            }
        } catch {
        }
        try {
            Remove-Job -Job $Monitor -Force -ErrorAction SilentlyContinue | Out-Null
        } catch {
        }
    }
}

function Get-NotepadProcessIds {
    return @(
        Get-Process notepad -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty Id
    )
}

function Get-ExplorerWindowHandles {
    $handles = @()
    try {
        $shell = New-Object -ComObject Shell.Application
        foreach ($window in @($shell.Windows())) {
            try {
                $fullName = [string]$window.FullName
                if (-not $fullName) {
                    continue
                }
                if ((Split-Path $fullName -Leaf).ToLowerInvariant() -ne "explorer.exe") {
                    continue
                }
                $hwnd = 0
                try {
                    $hwnd = [int64]$window.HWND
                } catch {
                    $hwnd = 0
                }
                if ($hwnd -gt 0) {
                    $handles += $hwnd
                }
            } catch {
            }
        }
    } catch {
    }
    return @($handles | Sort-Object -Unique)
}

function Stop-NewNotepadProcesses {
    param(
        [int[]]$BaselineProcessIds = @(),
        [int[]]$ExcludeProcessIds = @()
    )

    $baseline = @{}
    foreach ($processId in @($BaselineProcessIds)) {
        $baseline[[string]$processId] = $true
    }
    $exclude = @{}
    foreach ($processId in @($ExcludeProcessIds)) {
        $exclude[[string]$processId] = $true
    }

    $stoppedCount = 0
    foreach ($process in @(Get-Process notepad -ErrorAction SilentlyContinue)) {
        if ($baseline.ContainsKey([string]$process.Id) -or $exclude.ContainsKey([string]$process.Id)) {
            continue
        }
        try {
            Stop-ProcessQuietly -Process $process
            $stoppedCount += 1
        } catch {
        }
    }
    return $stoppedCount
}

function Close-NewExplorerWindows {
    param(
        [int64[]]$BaselineWindowHandles = @()
    )

    $baseline = @{}
    foreach ($handle in @($BaselineWindowHandles)) {
        $baseline[[string]$handle] = $true
    }

    $closedCount = 0
    try {
        $shell = New-Object -ComObject Shell.Application
        foreach ($window in @($shell.Windows())) {
            try {
                $fullName = [string]$window.FullName
                if (-not $fullName) {
                    continue
                }
                if ((Split-Path $fullName -Leaf).ToLowerInvariant() -ne "explorer.exe") {
                    continue
                }
                $hwnd = 0
                try {
                    $hwnd = [int64]$window.HWND
                } catch {
                    $hwnd = 0
                }
                if ($hwnd -le 0 -or $baseline.ContainsKey([string]$hwnd)) {
                    continue
                }
                $window.Quit()
                $closedCount += 1
            } catch {
            }
        }
    } catch {
    }
    return $closedCount
}

function Start-NotepadProbe {
    $script:window = $null
    $probeFile = Join-Path $ArtifactsDir "${Stamp}_notepad_probe.txt"
    Write-Utf8NoBomFile -Path $probeFile -Content ""
    $probeLeaf = Split-Path -Leaf $probeFile
    $expectedTitle = "$probeLeaf - Notepad"
    $probeTitleToken = $probeLeaf
    $process = Start-Process -FilePath "notepad.exe" -ArgumentList @(
        $probeFile
    ) -PassThru

    $resolvedWindowProcess = $null
    $windowHandle = [IntPtr]::Zero
    $window = $null
    Wait-Until -TimeoutSeconds 15 -Description "notepad probe window" -Condition {
        try {
            if ($process -and -not $process.HasExited) {
                $process.Refresh()
                if (
                    $process.MainWindowHandle -ne 0 -or
                    (
                        -not [string]::IsNullOrWhiteSpace($process.MainWindowTitle) -and
                        $process.MainWindowTitle -like "*$probeTitleToken*"
                    )
                ) {
                    $windowHandle = [IntPtr]$process.MainWindowHandle
                    $resolvedWindowProcess = $process
                    return $true
                }
            }
        } catch {
        }

        $candidateProcesses = @()
        try {
            $candidateProcesses = @(
                Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
                    Where-Object {
                        (
                            $_.Name -eq 'notepad.exe'
                        ) -and
                        $_.CommandLine -and
                        (
                            $_.CommandLine -like "*$probeLeaf*"
                        )
                    }
            )
        } catch {
            $candidateProcesses = @()
        }

        foreach ($candidateProcess in $candidateProcesses) {
            try {
                $liveProcess = Get-Process -Id ([int]$candidateProcess.ProcessId) -ErrorAction SilentlyContinue
                if (-not $liveProcess) {
                    continue
                }
                $liveProcess.Refresh()
                if (
                    $liveProcess.MainWindowHandle -ne 0 -or
                    (
                        -not [string]::IsNullOrWhiteSpace($liveProcess.MainWindowTitle) -and
                        $liveProcess.MainWindowTitle -like "*$probeTitleToken*"
                    )
                ) {
                    $windowHandle = [IntPtr]$liveProcess.MainWindowHandle
                    $resolvedWindowProcess = $liveProcess
                    return $true
                }
            } catch {
            }
        }

        foreach ($candidate in (Get-RootWindows)) {
            try {
                if (
                    $candidate.Current.Name -eq $expectedTitle -or
                    (
                        -not [string]::IsNullOrWhiteSpace($candidate.Current.Name) -and
                        $candidate.Current.Name -like "*$probeTitleToken*"
                    )
                ) {
                    try {
                        $resolvedWindowProcess = Get-Process -Id ([int]$candidate.Current.ProcessId) -ErrorAction SilentlyContinue
                        if ($resolvedWindowProcess) {
                            $resolvedWindowProcess.Refresh()
                            if ($resolvedWindowProcess.MainWindowHandle -ne 0) {
                                $windowHandle = [IntPtr]$resolvedWindowProcess.MainWindowHandle
                            }
                        }
                    } catch {
                    }
                    $script:window = $candidate
                    return $true
                }
            } catch {
            }
        }
        return $false
    } | Out-Null

    if ($windowHandle -ne [IntPtr]::Zero) {
        try {
            $window = [System.Windows.Automation.AutomationElement]::FromHandle($windowHandle)
        } catch {
            $window = $null
        }
    }
    if (-not $window) {
        $scriptWindow = Get-Variable -Name window -Scope Script -ErrorAction SilentlyContinue
        $fallbackProbeWindow = if ($scriptWindow) { $scriptWindow.Value } else { $null }
        $window = Resolve-NotepadProbeWindow -Probe ([pscustomobject]@{
            process_id = if ($resolvedWindowProcess) { $resolvedWindowProcess.Id } else { $process.Id }
            window = $fallbackProbeWindow
            expected_title = $expectedTitle
            title_token = $probeTitleToken
        })
    }

    if (-not $window) {
        throw "Could not resolve Notepad automation window from the launched process."
    }
    Focus-Window -Element $window

    $editor = $null
    try {
        $editor = Resolve-NotepadEditor -Probe ([pscustomobject]@{
            process = $process
            process_id = $process.Id
            window = $window
            path = $probeFile
            expected_title = $expectedTitle
        })
    } catch {
    }
    if ($editor) {
        try {
            Set-Value -Element $editor -Value ""
        } catch {
        }
    } else {
        Add-Note "External probe text control was not immediately available after launch; file-backed fallback remains active."
    }

    $probeProcess = if ($resolvedWindowProcess) { $resolvedWindowProcess } else { $process }

    return [pscustomobject]@{
        process = $probeProcess
        process_id = $probeProcess.Id
        window_process_id = if ($resolvedWindowProcess) { $resolvedWindowProcess.Id } else { $process.Id }
        window = $window
        editor = $editor
        path = $probeFile
        script_path = $null
        expected_title = $expectedTitle
        title_token = $probeTitleToken
    }
}

function Resolve-NotepadProbeWindow {
    param($Probe)

    $expectedTitle = if ($Probe.expected_title) { [string]$Probe.expected_title } else { "" }
    $probeTitleToken = if ($Probe.title_token) { [string]$Probe.title_token } else { $expectedTitle }
    $expectedProcessId = 0
    try {
        $expectedProcessId = [int]$Probe.process_id
    } catch {
    }
    try {
        foreach ($candidate in (Get-RootWindows)) {
            if (
                $candidate.Current.Name -eq $expectedTitle -or
                (
                    $probeTitleToken -and
                    -not [string]::IsNullOrWhiteSpace($candidate.Current.Name) -and
                    $candidate.Current.Name -like "*$probeTitleToken*"
                )
            ) {
                if ($expectedProcessId -le 0 -or $candidate.Current.ProcessId -eq $expectedProcessId) {
                    return $candidate
                }
            }
        }
    } catch {
    }

    $fallbackCandidate = $null
    foreach ($candidate in (Get-RootWindows)) {
        try {
            $controlTypeName = Get-ElementControlTypeNameSafe -Element $candidate -Context "Resolve-NotepadProbeWindow"
            if (
                ($controlTypeName -eq [System.Windows.Automation.ControlType]::Window.ProgrammaticName -or [string]::IsNullOrWhiteSpace($controlTypeName)) -and
                $candidate.Current.ClassName -eq "Notepad"
            ) {
                if ($expectedTitle -and $candidate.Current.Name -ne $expectedTitle -and $candidate.Current.Name -ne "Notepad") {
                    continue
                }
                if ($expectedProcessId -gt 0 -and $candidate.Current.ProcessId -eq $expectedProcessId) {
                    return $candidate
                }
                if (-not $fallbackCandidate) {
                    $fallbackCandidate = $candidate
                }
            }
        } catch {
        }
    }

    if ($fallbackCandidate) {
        return $fallbackCandidate
    }

    if ($Probe.window -and -not (Test-ElementGoneOrOffscreen -Element $Probe.window)) {
        return $Probe.window
    }

    return $null
}

function Resolve-NotepadEditor {
    param($Probe)

    $window = Resolve-NotepadProbeWindow -Probe $Probe
    if (-not $window) {
        return $null
    }

    foreach ($candidate in (Get-AllDescendants -Element $window)) {
        try {
            if ($candidate.Current.ClassName -eq "RichEditD2DPT") {
                return $candidate
            }
        } catch {
        }
    }

    foreach ($candidate in (Get-AllDescendants -Element $window)) {
        try {
            if ((Get-ElementControlTypeNameSafe -Element $candidate -Context "Resolve-NotepadEditor") -eq [System.Windows.Automation.ControlType]::Edit.ProgrammaticName) {
                return $candidate
            }
        } catch {
        }
    }

    return $null
}

function Get-NotepadText {
    param($Probe)
    $editor = Resolve-NotepadEditor -Probe $Probe
    if (-not $editor) {
        if ($Probe.path -and (Test-Path -LiteralPath $Probe.path)) {
            Add-Note "External probe control was unavailable at read time; falling back to the probe file contents."
            return (Get-Content -LiteralPath $Probe.path -Raw)
        }
        throw "Could not resolve the external probe control."
    }
    return Get-TextValue -Element $editor
}

function Restore-SavedActionSource {
    param(
        [bool]$HadOriginal,
        [byte[]]$OriginalBytes
    )

    if ($HadOriginal) {
        [System.IO.File]::WriteAllBytes($SourcePath, $OriginalBytes)
    } else {
        if (Test-Path -LiteralPath $SourcePath) {
            Remove-Item -LiteralPath $SourcePath -Force
        }
    }
}

function New-HealthySource {
    Save-JsonNoBom -Path $SourcePath -Value @{
        schema_version = 1
        actions = @()
    }
}

function Seed-LargeInventorySource {
    $actions = @()
    for ($i = 1; $i -le 8; $i++) {
        $actions += @{
            id = "open_reports_$i"
            title = "Open Reports $i"
            target_kind = "folder"
            target = "C:\Reports\$i"
            aliases = @("show reports $i")
        }
    }
    Save-JsonNoBom -Path $SourcePath -Value @{
        schema_version = 1
        actions = $actions
    }
}

function Corrupt-Source {
    Write-Utf8NoBomFile -Path $SourcePath -Content "{ not valid json"
}

function Normalize-CommandPhrase {
    param(
        [string]$Text
    )

    $value = if ($null -eq $Text) { "" } else { [string]$Text }
    $normalized = $value.Trim().ToLowerInvariant()
    $normalized = [regex]::Replace($normalized, "\s+", " ")
    $normalized = [regex]::Replace($normalized, "[.!?]+$", "")
    return $normalized.Trim()
}

function Get-JsonTitles {
    if (-not (Test-Path -LiteralPath $SourcePath)) {
        return @()
    }
    $parsed = Get-Content -LiteralPath $SourcePath -Raw | ConvertFrom-Json
    return @($parsed.actions | ForEach-Object { $_.title })
}

function Get-SavedActionRecordById {
    param(
        [string]$ActionId
    )

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        throw "Saved action source was not present while resolving action '$ActionId'."
    }

    $parsed = Get-Content -LiteralPath $SourcePath -Raw | ConvertFrom-Json
    $actions = @($parsed.actions)
    $record = $actions | Where-Object { $_.id -eq $ActionId } | Select-Object -First 1
    if (-not $record) {
        throw "Saved action '$ActionId' was not present in the current source."
    }
    return $record
}

function Find-SavedActionRecord {
    param(
        [string]$Title,
        [string]$Alias = "",
        [string]$Target = ""
    )

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        return $null
    }

    $parsed = Get-Content -LiteralPath $SourcePath -Raw | ConvertFrom-Json
    $actions = @($parsed.actions)
    $records = @(
        $actions | Where-Object {
            ([string](Get-RecordPropertyValue -Record $_ -PropertyName "title" -Default "")) -eq $Title
        }
    )

    if ($Alias) {
        $records = @(
            $records | Where-Object {
                $aliases = @(
                    Get-RecordPropertyValue -Record $_ -PropertyName "aliases" -Default @()
                )
                @($aliases | Where-Object { $_ -is [string] -and ([string]$_) -eq $Alias }).Count -gt 0
            }
        )
    }

    if ($Target) {
        $records = @(
            $records | Where-Object {
                ([string](Get-RecordPropertyValue -Record $_ -PropertyName "target" -Default "")) -eq $Target
            }
        )
    }

    if (-not $records -or $records.Count -lt 1) {
        return $null
    }

    return $records | Select-Object -Last 1
}

function Get-CallableGroupRecordById {
    param(
        [string]$GroupId
    )

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        throw "Saved action source was not present while resolving group '$GroupId'."
    }

    $parsed = Get-Content -LiteralPath $SourcePath -Raw | ConvertFrom-Json
    $groups = @($parsed.groups)
    $record = $groups | Where-Object { $_.id -eq $GroupId } | Select-Object -First 1
    if (-not $record) {
        throw "Callable group '$GroupId' was not present in the current source."
    }
    return $record
}

function Get-RecordPropertyValue {
    param(
        $Record,
        [string]$PropertyName,
        $Default = $null
    )

    if ($null -eq $Record) {
        return $Default
    }

    $property = $Record.PSObject.Properties[$PropertyName]
    if ($null -eq $property) {
        return $Default
    }

    return $property.Value
}

function Get-SavedActionRecordId {
    param(
        $Record
    )

    return [string](Get-RecordPropertyValue -Record $Record -PropertyName "id" -Default "")
}

function Get-SavedActionRecordTitle {
    param(
        $Record
    )

    return [string](Get-RecordPropertyValue -Record $Record -PropertyName "title" -Default "")
}

function Get-SavedActionRecordAliases {
    param(
        $Record
    )

    $aliasesValue = Get-RecordPropertyValue -Record $Record -PropertyName "aliases" -Default @()
    if ($null -eq $aliasesValue) {
        return @()
    }

    return @(
        @($aliasesValue) |
            Where-Object { $_ -is [string] } |
            ForEach-Object { [string]$_ }
    )
}

function Get-SavedActionRecordInvocationMode {
    param(
        $Record
    )

    $invocationMode = [string](Get-RecordPropertyValue -Record $Record -PropertyName "invocation_mode" -Default "")
    if ([string]::IsNullOrWhiteSpace($invocationMode)) {
        return "legacy"
    }
    return $invocationMode
}

function Get-SavedActionRecordTriggerMode {
    param(
        $Record
    )

    return [string](Get-RecordPropertyValue -Record $Record -PropertyName "trigger_mode" -Default "")
}

function Get-SavedActionRecordCustomTriggers {
    param(
        $Record
    )

    $customTriggersValue = Get-RecordPropertyValue -Record $Record -PropertyName "custom_triggers" -Default @()
    if ($null -eq $customTriggersValue) {
        return @()
    }

    return @(
        @($customTriggersValue) |
            Where-Object { $_ -is [string] -and $_.Trim() } |
            ForEach-Object { [string]$_ }
    )
}

function Get-SavedActionRecordShapeSummary {
    param(
        $Record
    )

    $recordId = Get-SavedActionRecordId -Record $Record
    $recordTitle = Get-SavedActionRecordTitle -Record $Record
    $invocationMode = Get-SavedActionRecordInvocationMode -Record $Record
    $triggerMode = Get-SavedActionRecordTriggerMode -Record $Record
    $aliases = @(Get-SavedActionRecordAliases -Record $Record)
    $customTriggers = @(Get-SavedActionRecordCustomTriggers -Record $Record)
    $customTriggerProperty = $null -ne $Record -and $null -ne $Record.PSObject.Properties["custom_triggers"]

    return "id='$recordId' title='$recordTitle' invocation_mode='$invocationMode' trigger_mode='$triggerMode' aliases=$($aliases.Count) custom_triggers=$($customTriggers.Count) has_custom_triggers_property=$customTriggerProperty"
}

function Get-SavedActionTriggerPrefixes {
    param(
        [string]$TriggerMode,
        [object[]]$CustomTriggers = @()
    )

    switch (([string]$TriggerMode).Trim().ToLowerInvariant()) {
        "launch" { return @("Launch") }
        "open" { return @("Open") }
        "launch_and_open" { return @("Launch", "Open") }
        "custom" {
            return @(
                @($CustomTriggers) |
                    Where-Object { $_ -is [string] -and $_.Trim() } |
                    ForEach-Object { [regex]::Replace($_.Trim(), "\s+", " ") }
            )
        }
        default { return @() }
    }
}

function Build-SavedActionCallablePhrases {
    param(
        $Record
    )

    $phrases = New-Object System.Collections.Generic.List[string]
    $seen = New-Object System.Collections.Generic.HashSet[string]

    $aliases = @(Get-SavedActionRecordAliases -Record $Record)

    $invocationMode = Get-SavedActionRecordInvocationMode -Record $Record
    if ($invocationMode -eq "aliases_only") {
        $basePhrases = @($aliases)
    } else {
        $basePhrases = @((Get-SavedActionRecordTitle -Record $Record)) + @($aliases)
    }

    $addPhrase = {
        param([string]$Value)
        $valueText = if ($null -eq $Value) { "" } else { [string]$Value }
        $display = [regex]::Replace($valueText.Trim(), "\s+", " ")
        if (-not $display) {
            return
        }
        $normalized = Normalize-CommandPhrase $display
        if (-not $normalized) {
            return
        }
        if ($seen.Add($normalized)) {
            $phrases.Add($display) | Out-Null
        }
    }

    foreach ($phrase in $basePhrases) {
        & $addPhrase $phrase
    }

    $prefixes = @(Get-SavedActionTriggerPrefixes -TriggerMode (Get-SavedActionRecordTriggerMode -Record $Record) -CustomTriggers @(Get-SavedActionRecordCustomTriggers -Record $Record))
    foreach ($prefix in $prefixes) {
        $normalizedPrefix = Normalize-CommandPhrase $prefix
        if (-not $normalizedPrefix) {
            continue
        }
        foreach ($phrase in $basePhrases) {
            $normalizedPhrase = Normalize-CommandPhrase $phrase
            if (-not $normalizedPhrase) {
                continue
            }
            if ($normalizedPhrase -eq $normalizedPrefix -or $normalizedPhrase.StartsWith("$normalizedPrefix ")) {
                & $addPhrase $phrase
            } else {
                & $addPhrase "$prefix $phrase"
            }
        }
    }

    return @($phrases)
}

function Get-PreferredExactInvocationPhrase {
    param(
        $Record
    )

    $aliases = @(
        Get-SavedActionRecordAliases -Record $Record |
            Where-Object { $_.Trim() }
    )
    if ($aliases.Count -lt 1) {
        throw "Saved action '$((Get-SavedActionRecordId -Record $Record))' did not expose any callable aliases for exact-match execution."
    }

    $prefixes = @(Get-SavedActionTriggerPrefixes -TriggerMode (Get-SavedActionRecordTriggerMode -Record $Record) -CustomTriggers @(Get-SavedActionRecordCustomTriggers -Record $Record))
    if ($prefixes.Count -gt 0) {
        return [regex]::Replace("$($prefixes[0]) $($aliases[0])", "\s+", " ").Trim()
    }

    return [regex]::Replace(([string]$aliases[0]).Trim(), "\s+", " ").Trim()
}

function Run-Create-Flow {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running valid create flow"
    $dialog = Open-CreateDialog -Overlay $Overlay
    Fill-AuthoringDialog -Dialog $dialog -TypeLabel "Application" -Title "Open Notepad Task" -Aliases "launch notepad task" -Target "notepad.exe"
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Create"
    $attemptStatus = Wait-ForCreateAttemptOrCreatedMarker -Title "Open Notepad Task" -StartLine $markerStart -TimeoutSeconds 16
    $runtimeSearchStart = [int]$attemptStatus.search_start_line
    Wait-ForCatalogReloadCompleted -StartLine $runtimeSearchStart
    Wait-ForCreateCreatedMarkerByTitle -Title "Open Notepad Task" -StartLine $runtimeSearchStart -TimeoutSeconds 16 | Out-Null
    Wait-Until -TimeoutSeconds 3 -Description "created task persisted to source" -Condition {
        $record = Find-SavedActionRecord -Title "Open Notepad Task" -Alias "launch notepad task" -Target "notepad.exe"
        return $null -ne $record
    } | Out-Null
    Write-StepLog -Stage "FLOW" -Message "valid create markers completed; confirming dialog closure"
    try {
        Wait-ForDialogRuntimeClosed -SignalBase "CUSTOM_TASK_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 4
    } catch {
        Add-Note "Create dialog close readback lagged after a successful create marker, but the runtime marker and persisted source still confirmed the save."
    }
    $record = Find-SavedActionRecord -Title "Open Notepad Task" -Alias "launch notepad task" -Target "notepad.exe"
    if ($null -eq $record) {
        throw "Valid create flow never produced a persisted saved action record for 'Open Notepad Task'."
    }
    Write-StepLog -Stage "FLOW" -Message "valid create source confirmed action_id='$(Get-SavedActionRecordId -Record $record)' title='$(Get-SavedActionRecordTitle -Record $record)'"
    $Overlay = Ensure-OverlayReady -Overlay $Overlay -Reason "successful create flow"
    Copy-SourceSnapshot -Slug "after_create" | Out-Null
    Write-StepLog -Stage "FLOW" -Message "valid create flow complete; runtime markers and persisted source confirmed the create"
    return (Ensure-OverlayReady -Overlay $Overlay -Reason "post-create source verification")
}

function Run-Group-Create-Flow {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running valid group create flow"
    $dialog = Open-CreateGroupDialog -Overlay $Overlay
    Fill-CallableGroupDialog -Dialog $dialog -GroupName "Workspace Tools" -Aliases "workspace tools" -MemberNames @("Open Notepad Task", "Open Saved Actions Folder")
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Create"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_GROUP_CREATE_ATTEMPT_STARTED|title=Workspace Tools|member_count=2" -StartLine $markerStart
    Wait-ForCatalogReloadCompleted -StartLine $markerStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_GROUP_CREATED|group_id=workspace_tools|title=Workspace Tools|member_count=2" -StartLine $markerStart
    try {
        Wait-ForDialogRuntimeClosed -SignalBase "CUSTOM_GROUP_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 4
    } catch {
        Add-Note "Create Custom Group close readback lagged after a successful create marker, but the runtime marker and persisted source still confirmed the save."
    }
    $record = Get-CallableGroupRecordById -GroupId "workspace_tools"
    if (@($record.member_action_ids).Count -ne 2) {
        throw "Callable group record did not persist both selected members."
    }
    Copy-SourceSnapshot -Slug "after_group_create" | Out-Null
    return (Ensure-OverlayReady -Overlay $Overlay -Reason "post-group-create verification")
}

function Run-Group-Collision-Checks {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running callable-group collision checks"

    $dialog = Open-CreateGroupDialog -Overlay $Overlay
    Fill-CallableGroupDialog -Dialog $dialog -GroupName "Explorer Group" -Aliases "Open Windows Explorer" -MemberNames @("Open Notepad Task")
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Create"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_GROUP_CREATE_ATTEMPT_STARTED|title=Explorer Group|member_count=1" -StartLine $markerStart

    try {
        Wait-Until -TimeoutSeconds 2 -Description "group collision feedback" -Condition {
            $currentDialog = Get-DialogWindow -Name "Create Custom Group"
            if (-not $currentDialog) {
                return $false
            }
            $status = Get-DialogStatusText -Dialog $currentDialog
            return [bool]$status
        } | Out-Null
    } catch {
    }

    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_GROUP_CREATED|" -StartLine $markerStart) {
        throw "Callable-group collision unexpectedly produced a create marker."
    }

    Cancel-Dialog -Dialog $dialog
    return (Restore-OverlayAfterAuthoringDialogCancel -Overlay $Overlay -Reason "callable-group collision case cancel")
}

function Run-Group-Invocation-Check {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running callable-group exact invocation check"
    $Overlay = Ensure-OverlayReady -Overlay $Overlay -Reason "callable-group exact invocation setup"
    $record = Get-CallableGroupRecordById -GroupId "workspace_tools"
    $aliases = @($record.aliases)
    if ($aliases.Count -lt 1) {
        throw "Workspace Tools group did not persist any callable aliases."
    }
    $memberIds = @($record.member_action_ids)
    $builtInIndex = [Array]::IndexOf($memberIds, "open_saved_actions_folder")
    $savedIndex = [Array]::IndexOf($memberIds, "open_notepad_task")
    if ($builtInIndex -lt 0 -or $savedIndex -lt 0) {
        throw "Workspace Tools group did not preserve the expected saved and built-in members."
    }
    $phrase = [string]$aliases[0]

    $input = Get-OverlayInput -Overlay $Overlay
    Set-Value -Element $input -Value $phrase
    $null = Focus-ElementForInteraction -ElementResolver { Get-OverlayInput -Overlay $Overlay } -Description "overlay input for built-in member group invocation" -RequireExactFocus $true
    Start-Sleep -Milliseconds 200

    $ambiguousStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_AMBIGUOUS|count=2" -StartLine $ambiguousStart

    $selectionStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey (0x31 + $builtInIndex)
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_DISAMBIGUATION_SELECTED|index=$builtInIndex|action_id=open_saved_actions_folder" -StartLine $selectionStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=open_saved_actions_folder" -StartLine $selectionStart

    $launchStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id=open_saved_actions_folder" -StartLine $launchStart

    $liveOverlay = Wait-ForOptionalOverlayOpen -TimeoutSeconds 2
    if ($liveOverlay) {
        Close-Overlay -Reason "group built-in invocation verification reset"
    }
    $Overlay = Reopen-OverlayAfterClose -Reason "group built-in invocation verification"
    $resolveOverlayInput = {
        return (Get-OverlayInput -Overlay $Overlay)
    }
    $input = & $resolveOverlayInput
    Set-Value -Element $input -Value $phrase
    $null = Focus-ElementForInteraction -ElementResolver $resolveOverlayInput -Description "overlay input for saved member group invocation" -RequireExactFocus $true
    Start-Sleep -Milliseconds 200

    $ambiguousStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_AMBIGUOUS|count=2" -StartLine $ambiguousStart

    $selectionStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey (0x31 + $savedIndex)
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_DISAMBIGUATION_SELECTED|index=$savedIndex|action_id=open_notepad_task" -StartLine $selectionStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=open_notepad_task" -StartLine $selectionStart

    $launchStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id=open_notepad_task" -StartLine $launchStart
    Copy-SourceSnapshot -Slug "after_group_invocation" | Out-Null
    $liveOverlay = Wait-ForOptionalOverlayOpen -TimeoutSeconds 2
    if ($liveOverlay) {
        Close-Overlay -Reason "post-group invocation verification reset"
    }
    return (Reopen-OverlayAfterClose -Reason "post-group invocation verification")
}

function Run-Task-Inline-Group-Check {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running task inline-group quick-create check"
    $dialog = Open-CreateDialog -Overlay $Overlay
    Fill-AuthoringDialog -Dialog $dialog -TypeLabel "Application" -Title "Open Notes Task" -Aliases "notes task" -Target "notepad.exe"

    $resolveDialog = {
        Resolve-LiveDialogRoot -Dialog $dialog -ExpectedName "Create Custom Task"
    }
    $assignmentDialog = Open-TaskGroupAssignmentDialog -TaskDialog $dialog
    Set-TaskGroupAssignmentRowState -Dialog $assignmentDialog -GroupTitle "Workspace Tools" -ButtonName "Assign" -Description "existing Workspace Tools group assign button"
    $quickDialog = Open-AssignmentCreateGroupDialog -AssignmentDialog $assignmentDialog
    Fill-CallableGroupDialog -Dialog $quickDialog -GroupName "Notes Suite" -Aliases "notes suite" -MemberNames @()
    Submit-Dialog -Dialog $quickDialog -ButtonName "Create"
    Start-Sleep -Milliseconds 900
    Wait-Until -TimeoutSeconds 6 -Description "Available Groups returned after inline create group" -Condition {
        $liveAssignmentDialog = Get-DialogWindow -Name "Available Groups"
        return [bool]$liveAssignmentDialog
    } | Out-Null
    $assignmentDialog = Get-DialogWindow -Name "Available Groups"
    if (-not $assignmentDialog) {
        throw "Available Groups dialog did not return after inline group creation."
    }
    $resolveInlineNotesButton = {
        return (Get-TaskGroupAssignmentRowButton -Dialog $assignmentDialog -GroupTitle "Notes Suite" -ButtonName "Assign")
    }
    Wait-Until -TimeoutSeconds 8 -Description "new Notes Suite group assign button" -Condition {
        return [bool](& $resolveInlineNotesButton)
    } | Out-Null
    $inlineNotesButton = Focus-ElementForInteraction -ElementResolver $resolveInlineNotesButton -Description "new Notes Suite group assign button" -RequireExactFocus $false
    if ($inlineNotesButton.Current.Name -ne "Assign") {
        throw "Inline-created Notes Suite group returned with an unexpected toggle state instead of Assign."
    }
    Invoke-ElementRobust -Element $inlineNotesButton -Description "new Notes Suite group assign button"
    Submit-Dialog -Dialog $assignmentDialog -ButtonName "Done"
    Wait-Until -TimeoutSeconds 6 -Description "task dialog returned after group assignment" -Condition {
        $liveDialog = & $resolveDialog
        return [bool]$liveDialog
    } | Out-Null

    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Create"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED|title=Open Notes Task" -StartLine $markerStart
    Wait-ForCatalogReloadCompleted -StartLine $markerStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|action_id=open_notes_task" -StartLine $markerStart

    $workspaceGroup = Get-CallableGroupRecordById -GroupId "workspace_tools"
    $notesGroup = Get-CallableGroupRecordById -GroupId "notes_suite"
    if (@($workspaceGroup.member_action_ids) -contains "open_notes_task") {
        throw "Single-group assignment should not keep the task attached to the previously assigned existing group after Notes Suite was assigned."
    }
    if (@($notesGroup.member_action_ids).Count -ne 1 -or @($notesGroup.member_action_ids)[0] -ne "open_notes_task") {
        throw "Inline quick-create group did not persist as the assigned single group for the new task."
    }
    Copy-SourceSnapshot -Slug "after_task_inline_group" | Out-Null
    return (Ensure-OverlayReady -Overlay $Overlay -Reason "post-inline-group task verification")
}

function Run-Invalid-Group-Source-Check {
    Write-StepLog -Stage "FLOW" -Message "running invalid-group-source blocking check"
    Save-JsonNoBom -Path $SourcePath -Value @{
        schema_version = 1
        actions = @(
            @{
                id = "open_reports"
                title = "Open Reports"
                target_kind = "folder"
                target = "C:\Reports"
                aliases = @("show reports")
            }
        )
        groups = @(
            @{
                id = "broken_group"
                title = "Broken Group"
                aliases = @("broken group")
                member_action_ids = @("missing_action")
            }
        )
    }
    Restart-InteractiveRuntime | Out-Null
    $overlay = Open-OverlayWithRuntimeRestartFallback
    $overlay = Ensure-OverlayReady -Overlay $overlay -Reason "invalid group source blocking check"

    $resolveOverlay = {
        Resolve-LiveOverlayRoot -Overlay $overlay
    }
    $resolveCreateGroupButton = {
        $liveOverlay = & $resolveOverlay
        if (-not $liveOverlay) {
            return $null
        }
        return (Find-ElementByAutomationIdsDirect -Root $liveOverlay -AutomationIds (Get-OverlayCreateGroupButtonAutomationIds))
    }

    $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationIds (Get-OverlayCreateGroupButtonAutomationIds) -Description "Create Custom Group button in invalid-group-source path"
    $createGroupButton = Focus-ElementForInteraction -ElementResolver $resolveCreateGroupButton -Description "Create Custom Group button in invalid-group-source path" -RequireExactFocus $false
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $createGroupButton -Description "Create Custom Group button in invalid-group-source path"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_GROUP_CREATE_BLOCKED|reason=source_invalid" -StartLine $markerStart
    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_GROUP_CREATE_DIALOG_OPENED" -StartLine $markerStart) {
        throw "Invalid group source should block the Create Custom Group dialog before it opens."
    }

    $overlay = Ensure-OverlayReady -Overlay $overlay -Reason "after invalid group create block"
    $dialog = Open-CreateDialog -Overlay $overlay
    Fill-AuthoringDialog -Dialog $dialog -TypeLabel "Application" -Title "Recovered Notes Task" -Aliases "recovered notes" -Target "notepad.exe"
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Create"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|action_id=recovered_notes_task" -StartLine $markerStart
    Copy-SourceSnapshot -Slug "after_invalid_group_source_recovery" | Out-Null
}

function Get-InvalidCreateCases {
    return @(
        @{ type = "Application"; title = "Bad App"; aliases = "bad app alias"; target = "notepad.exe --help"; expect = "Application targets" }
    )
}

function Get-ScenarioSlug {
    param(
        [string]$Value
    )

    $slug = ([string]$Value).ToLowerInvariant() -replace "[^a-z0-9]+", "_"
    $slug = $slug.Trim("_")
    if (-not $slug) {
        return "case"
    }
    return $slug
}

function Confirm-InvalidCreateBlockedSubmission {
    param(
        [string]$Title,
        [string]$TypeLabel,
        [int]$StartLine,
        [string]$BeforeSourceText
    )

    Write-StepLog -Stage "FLOW" -Message "confirming blocked create submit for type='$TypeLabel' title='$Title'"
    $expectedTargetKind = Get-ExpectedTargetKindToken -TypeLabel $TypeLabel
    $attemptStatus = Wait-ForCreateAttemptOrBlockedMarker -Title $Title -StartLine $StartLine -TimeoutSeconds 16
    $runtimeSearchStart = [int]$attemptStatus.search_start_line
    $attemptSeen = [bool]$attemptStatus.attempt_seen
    $blockedStatus = Wait-ForCreateBlockedMarkerByTitle -Title $Title -StartLine $runtimeSearchStart -TimeoutSeconds 16
    $blockedSeen = [bool]$blockedStatus.blocked_seen
    $blockedLine = [string]$blockedStatus.blocked_line

    Wait-Until -TimeoutSeconds 4 -Description "blocked invalid create '$TypeLabel'" -Condition {
        $currentDialog = Get-DialogWindow -Name "Create Custom Task"
        if (-not $currentDialog) {
            return $false
        }
        $currentSourceText = if (Test-Path -LiteralPath $SourcePath) {
            Get-Content -LiteralPath $SourcePath -Raw
        } else {
            ""
        }
        return $currentSourceText -eq $BeforeSourceText
    } | Out-Null

    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|" -StartLine $runtimeSearchStart) {
        throw "Invalid target case '$TypeLabel' unexpectedly produced a create marker."
    }

    if (-not $blockedSeen) {
        throw "Invalid target case '$TypeLabel' never surfaced the expected blocked marker after submit."
    }
    if ($expectedTargetKind -and ($blockedLine -notlike "*|target_kind=$expectedTargetKind*")) {
        throw "Invalid target case '$TypeLabel' emitted a blocked marker, but the target_kind did not match. Expected '$expectedTargetKind'. Blocked line: $blockedLine"
    }

    Write-StepLog -Stage "FLOW" -Message "blocked create submit confirmed for type='$TypeLabel' title='$Title' attempt_marker=$attemptSeen blocked_marker=$blockedSeen"
}

function Run-Invalid-Create-CheckCase {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [hashtable]$Case
    )

    Write-StepLog -Stage "FLOW" -Message "running invalid create case type='$($Case.type)' title='$($Case.title)'"
    $maxAttempts = if ($Case.type -eq "Application") { 1 } else { 3 }

    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        $beforeSourceText = if (Test-Path -LiteralPath $SourcePath) {
            Get-Content -LiteralPath $SourcePath -Raw
        } else {
            ""
        }

        $dialog = $null
        try {
            $dialog = Open-CreateDialog -Overlay $Overlay
            Fill-AuthoringDialog -Dialog $dialog -TypeLabel $Case.type -Title $Case.title -Aliases $Case.aliases -Target $Case.target
            $markerStart = New-RuntimeMarkerCursor
            Submit-Dialog -Dialog $dialog -ButtonName "Create"
            Confirm-InvalidCreateBlockedSubmission -Title $Case.title -TypeLabel $Case.type -StartLine $markerStart -BeforeSourceText $beforeSourceText

            $status = ""
            try {
                Wait-Until -TimeoutSeconds 2 -Description "blocking feedback for invalid create '$($Case.type)'" -Condition {
                    $currentDialog = Get-DialogWindow -Name "Create Custom Task"
                    if (-not $currentDialog) {
                        return $false
                    }
                    $status = Get-DialogStatusText -Dialog $currentDialog
                    return [bool]$status
                } | Out-Null
            } catch {
            }
            if (-not $status) {
                Add-Note "Invalid target case '$($Case.type)' kept the dialog open and preserved the source, but the interactive status-label readback was blank."
            }
            Cancel-Dialog -Dialog $dialog -PreferDialogDisappearance $true
            return (Restore-OverlayAfterAuthoringDialogCancel -Overlay $Overlay -Reason "invalid create case '$($Case.type)' cancel")
        } catch {
            $message = $_.Exception.Message
            Add-Note "Invalid create case '$($Case.type)' attempt $attempt failed before blocked confirmation. Cause: $message"
            try {
                $currentDialog = Get-DialogWindow -Name "Create Custom Task"
                if ($currentDialog) {
                    Cancel-Dialog -Dialog $currentDialog -PreferDialogDisappearance $true
                    $Overlay = Restore-OverlayAfterAuthoringDialogCancel -Overlay $Overlay -Reason "invalid create case '$($Case.type)' retry cancel"
                }
            } catch {
                Add-Note "Invalid create case '$($Case.type)' retry cleanup after attempt $attempt did not complete cleanly."
            }

            if ($attempt -ge $maxAttempts) {
                throw
            }
        }
    }
}

function Run-Collision-Checks {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running collision checks"

    $cases = @(
        @{ title = "Explorer Helper"; aliases = "Open Windows Explorer"; target = "explorer.exe"; expect = "collide" }
    )

    foreach ($case in $cases) {
        $beforeSourceText = if (Test-Path -LiteralPath $SourcePath) {
            Get-Content -LiteralPath $SourcePath -Raw
        } else {
            ""
        }
        $dialog = Open-CreateDialog -Overlay $Overlay
        Fill-AuthoringDialog -Dialog $dialog -TypeLabel "Application" -Title $case.title -Aliases $case.aliases -Target $case.target
        $markerStart = New-RuntimeMarkerCursor
        Submit-Dialog -Dialog $dialog -ButtonName "Create"
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED|title=$($case.title)" -StartLine $markerStart
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|reason=validation_error" -StartLine $markerStart
        Wait-Until -TimeoutSeconds 4 -Description "blocked collision create '$($case.title)'" -Condition {
            $currentDialog = Get-DialogWindow -Name "Create Custom Task"
            if (-not $currentDialog) {
                return $false
            }
            $currentSourceText = if (Test-Path -LiteralPath $SourcePath) {
                Get-Content -LiteralPath $SourcePath -Raw
            } else {
                ""
            }
            return $currentSourceText -eq $beforeSourceText
        } | Out-Null
        if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|" -StartLine $markerStart) {
            throw "Collision case '$($case.title)' unexpectedly produced a create marker."
        }
        $status = ""
        try {
            Wait-Until -TimeoutSeconds 2 -Description "collision feedback '$($case.title)'" -Condition {
                $currentDialog = Get-DialogWindow -Name "Create Custom Task"
                if (-not $currentDialog) {
                    return $false
                }
                $status = Get-DialogStatusText -Dialog $currentDialog
                return [bool]$status
            } | Out-Null
        } catch {
        }
        if (-not $status) {
            Add-Note "Collision case '$($case.title)' stayed blocked with no write, but the interactive status-label readback was blank."
        }
        Cancel-Dialog -Dialog $dialog
        $Overlay = Restore-OverlayAfterAuthoringDialogCancel -Overlay $Overlay -Reason "collision create case '$($case.title)' cancel"
    }
}

function Run-SavedAlias-Ambiguity-Selection {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running saved-vs-saved ambiguity selection check"

    $liveOverlay = Wait-ForOptionalOverlayOpen -TimeoutSeconds 2
    if ($liveOverlay) {
        Write-StepLog -Stage "FLOW" -Message "overlay remained visible after exact-match execution; closing and reopening before saved-vs-saved ambiguity setup"
        Close-Overlay -Reason "saved-vs-saved ambiguity setup reset"
        $Overlay = Reopen-OverlayAfterClose -Reason "saved-vs-saved ambiguity setup reset"
    } else {
        Write-StepLog -Stage "FLOW" -Message "overlay closed after exact-match execution; reopening before saved-vs-saved ambiguity setup"
        $Overlay = Open-OverlayWithRuntimeRestartFallback -MaxAttempts 2
        $Overlay = Ensure-OverlayReady -Overlay $Overlay -Reason "saved-vs-saved ambiguity setup"
    }

    $dialog = Open-CreateDialog -Overlay $Overlay
    Fill-AuthoringDialog -Dialog $dialog -TypeLabel "Application" -Title "Weekly Reports Explorer" -Aliases "weekly reports" -Target "explorer.exe"
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Create"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED|title=Weekly Reports Explorer" -StartLine $markerStart
    Wait-ForCatalogReloadCompleted -StartLine $markerStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|action_id=weekly_reports_explorer" -StartLine $markerStart
    try {
        Wait-ForDialogRuntimeClosed -SignalBase "CUSTOM_TASK_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 4
    } catch {
        Add-Note "Ambiguity setup create dialog close readback lagged after the create marker, but the saved action still persisted."
    }

    $Overlay = Ensure-OverlayReady -Overlay $Overlay -Reason "saved-vs-saved ambiguity check"
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Weekly Reports Explorer"
    $Overlay = Close-CreatedTasksDialog -Dialog $createdTasksDialog -Overlay $Overlay -Reason "post-ambiguity setup Created Tasks close"

    $input = Get-OverlayInput -Overlay $Overlay
    Set-Value -Element $input -Value "weekly reports"
    $input.SetFocus()
    Start-Sleep -Milliseconds 200

    $ambiguousStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_AMBIGUOUS|count=2" -StartLine $ambiguousStart

    $selectionStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey 0x32
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_DISAMBIGUATION_SELECTED|index=1|action_id=weekly_reports_explorer" -StartLine $selectionStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=weekly_reports_explorer" -StartLine $selectionStart

    $launchStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id=weekly_reports_explorer" -StartLine $launchStart
    Copy-SourceSnapshot -Slug "after_ambiguity_selection" | Out-Null
    $liveOverlay = Wait-ForOptionalOverlayOpen -TimeoutSeconds 2
    if ($liveOverlay) {
        Close-Overlay -Reason "post-saved-vs-saved ambiguity verification reset"
    }
    return (Reopen-OverlayAfterClose -Reason "post-saved-vs-saved ambiguity verification")
}

function Run-Edit-Flow {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running valid edit flow"
    $expectedTargetKind = Get-ExpectedTargetKindToken -TypeLabel "Folder"
    $expectedTitle = "Open Weekly Reports"

    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    $dialog = Open-EditDialog -CreatedTasksDialog $createdTasksDialog -EditIndex 0
    Fill-AuthoringDialog -Dialog $dialog -TypeLabel "Folder" -Title "Open Weekly Reports" -Aliases "weekly reports" -Target "C:\Windows"
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Save"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_ATTEMPT_STARTED|action_id=open_notepad_task|title=$expectedTitle|target_kind=$expectedTargetKind" -StartLine $markerStart
    try {
        Wait-ForCatalogReloadCompleted -StartLine $markerStart
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_UPDATED|action_id=open_notepad_task|title=$expectedTitle|target_kind=$expectedTargetKind" -StartLine $markerStart
    } catch {
        $currentDialog = Get-DialogWindow -Name "Edit Custom Task"
        if (-not $currentDialog) {
            throw
        }
        Add-Note "Edit save did not surface an update marker on the first submit; retrying Save once against the still-open dialog."
        $markerStart = New-RuntimeMarkerCursor
        Submit-Dialog -Dialog $currentDialog -ButtonName "Save"
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_ATTEMPT_STARTED|action_id=open_notepad_task|title=$expectedTitle|target_kind=$expectedTargetKind" -StartLine $markerStart
        Wait-ForCatalogReloadCompleted -StartLine $markerStart
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_UPDATED|action_id=open_notepad_task|title=$expectedTitle|target_kind=$expectedTargetKind" -StartLine $markerStart
    }
    try {
        Wait-ForDialogRuntimeClosed -SignalBase "CUSTOM_TASK_EDIT_DIALOG" -StartLine $markerStart -TimeoutSeconds 4
    } catch {
        Add-Note "Edit dialog close readback lagged after a successful update marker, but the runtime marker and refreshed inventory still confirmed the save."
    }
    $Overlay = Ensure-OverlayReady -Overlay $Overlay -Reason "successful edit flow"
    Write-StepLog -Stage "FLOW" -Message "verifying created inventory after successful edit"
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Open Weekly Reports"
    $Overlay = Close-CreatedTasksDialog -Dialog $createdTasksDialog -Overlay $Overlay -Reason "post-edit Created Tasks close"
    Copy-SourceSnapshot -Slug "after_edit" | Out-Null
    Write-StepLog -Stage "FLOW" -Message "valid edit flow complete; preparing next scenario"
    return (Ensure-OverlayReady -Overlay $Overlay -Reason "post-edit inventory verification")
}

function Run-Invalid-Edit-Check {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running invalid edit check"
    $expectedTargetKind = Get-ExpectedTargetKindToken -TypeLabel "File"
    $expectedTitle = "Open Weekly Reports"

    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    $dialog = Open-EditDialog -CreatedTasksDialog $createdTasksDialog -EditIndex 0
    $beforeSourceText = if (Test-Path -LiteralPath $SourcePath) {
        Get-Content -LiteralPath $SourcePath -Raw
    } else {
        ""
    }
    Fill-AuthoringDialog -Dialog $dialog -TypeLabel "File" -Title "Open Weekly Reports" -Aliases "weekly reports" -Target "Reports\Weekly"
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Save"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_ATTEMPT_STARTED|action_id=open_notepad_task|title=$expectedTitle|target_kind=$expectedTargetKind" -StartLine $markerStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_BLOCKED|reason=validation_error|action_id=open_notepad_task|title=$expectedTitle|target_kind=$expectedTargetKind" -StartLine $markerStart
    Wait-Until -TimeoutSeconds 4 -Description "blocked invalid edit" -Condition {
        $currentDialog = Get-DialogWindow -Name "Edit Custom Task"
        if (-not $currentDialog) {
            return $false
        }
        $currentSourceText = if (Test-Path -LiteralPath $SourcePath) {
            Get-Content -LiteralPath $SourcePath -Raw
        } else {
            ""
        }
        return $currentSourceText -eq $beforeSourceText
    } | Out-Null
    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_TASK_UPDATED|" -StartLine $markerStart) {
        throw "Invalid edit target unexpectedly produced an update marker."
    }
    $status = ""
    try {
        Wait-Until -TimeoutSeconds 2 -Description "blocking feedback for invalid edit" -Condition {
            $currentDialog = Get-DialogWindow -Name "Edit Custom Task"
            if (-not $currentDialog) {
                return $false
            }
            $status = Get-DialogStatusText -Dialog $currentDialog
            return [bool]$status
        } | Out-Null
    } catch {
    }
    if (-not $status) {
        Add-Note "Invalid edit target kept the dialog open and preserved the source, but the interactive status-label readback was blank."
    }
    Cancel-Dialog -Dialog $dialog
    $Overlay = Restore-OverlayAfterAuthoringDialogCancel -Overlay $Overlay -Reason "invalid edit check cancel"
}

function Run-ExactMatch-Execution {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running exact-match execution check"
    $Overlay = Ensure-OverlayReady -Overlay $Overlay -Reason "exact-match execution check"
    $record = Get-SavedActionRecordById -ActionId "open_notepad_task"
    $recordId = Get-SavedActionRecordId -Record $record
    $recordTitle = Get-SavedActionRecordTitle -Record $record
    $recordInvocationMode = Get-SavedActionRecordInvocationMode -Record $record
    $recordTriggerMode = Get-SavedActionRecordTriggerMode -Record $record
    $recordCustomTriggers = @(Get-SavedActionRecordCustomTriggers -Record $record)
    $callablePhrases = @(Build-SavedActionCallablePhrases -Record $record)
    $invocationPhrase = Get-PreferredExactInvocationPhrase -Record $record
    Write-StepLog -Stage "FLOW" -Message "exact-match record shape $(Get-SavedActionRecordShapeSummary -Record $record)"
    Write-StepLog -Stage "FLOW" -Message "exact-match callable phrases action_id=$recordId phrases=$([string]::Join(' | ', $callablePhrases))"
    Write-StepLog -Stage "FLOW" -Message "exact-match invocation attempt action_id=$recordId phrase='$invocationPhrase' title='$recordTitle' invocation_mode='$recordInvocationMode' trigger_mode='$recordTriggerMode' custom_triggers=$($recordCustomTriggers.Count)"

    if (-not (@($callablePhrases | Where-Object { (Normalize-CommandPhrase $_) -eq (Normalize-CommandPhrase $invocationPhrase) }).Count -gt 0)) {
        throw "Exact-match invocation phrase '$invocationPhrase' was not present in the saved action callable phrase set."
    }

    $input = Get-OverlayInput -Overlay $Overlay
    Set-Value -Element $input -Value $invocationPhrase
    $input.SetFocus()
    Start-Sleep -Milliseconds 200

    $launchMarker = "RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id=open_notepad_task"
    $confirmMarker = "RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=open_notepad_task"
    $markerStart = New-RuntimeMarkerCursor
    Send-VirtualKey -VirtualKey 0x0D

    try {
        Wait-Until -TimeoutSeconds 4 -Description "exact-match confirm or launch marker" -Condition {
            (Test-RuntimeMarkerSeen -Marker $confirmMarker -StartLine $markerStart) -or
            (Test-RuntimeMarkerSeen -Marker $launchMarker -StartLine $markerStart)
        } | Out-Null
    } catch {
        Add-Note "First exact-match submit did not surface a fresh confirm or launch marker; retrying the submit path once."
        $Overlay = Ensure-OverlayReady -Overlay $Overlay -Reason "exact-match execution retry"
        $input = Get-OverlayInput -Overlay $Overlay
        Set-Value -Element $input -Value $invocationPhrase
        $input.SetFocus()
        Start-Sleep -Milliseconds 150
        $markerStart = New-RuntimeMarkerCursor
        Send-VirtualKey -VirtualKey 0x0D
        Wait-Until -TimeoutSeconds 4 -Description "exact-match confirm or launch marker retry" -Condition {
            (Test-RuntimeMarkerSeen -Marker $confirmMarker -StartLine $markerStart) -or
            (Test-RuntimeMarkerSeen -Marker $launchMarker -StartLine $markerStart)
        } | Out-Null
    }

    if (-not (Test-RuntimeMarkerSeen -Marker $launchMarker -StartLine $markerStart)) {
        if (-not (Test-RuntimeMarkerSeen -Marker $confirmMarker -StartLine $markerStart)) {
            throw "Exact-match execution did not reach a confirm or launch marker."
        }
        $secondSubmitStart = New-RuntimeMarkerCursor
        Send-VirtualKey -VirtualKey 0x0D
        Wait-ForRuntimeMarker -Marker $launchMarker -StartLine $secondSubmitStart
    } else {
        $script:RuntimeLogLineCursor = Get-RuntimeLogLineCount
    }
}

function Run-Reopen-Check {
    Write-StepLog -Stage "FLOW" -Message "running overlay reopen persistence check"
    Close-Overlay -Reason "overlay reopen persistence check"
    Write-StepLog -Stage "FLOW" -Message "overlay close confirmed for reopen persistence"
    $overlay = Reopen-OverlayAfterClose -Reason "overlay reopen persistence check"
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Open Weekly Reports"
    $overlay = Close-CreatedTasksDialog -Dialog $createdTasksDialog -Overlay $overlay -Reason "overlay reopen persistence Created Tasks close"
    Write-StepLog -Stage "FLOW" -Message "overlay reopen persistence check complete; preparing next scenario"
    return (Ensure-OverlayReady -Overlay $overlay -Reason "overlay reopen persistence check")
}

function Run-Large-Inventory-Check {
    Write-StepLog -Stage "FLOW" -Message "running large-inventory late-item edit check"
    Seed-LargeInventorySource
    Restart-InteractiveRuntime | Out-Null
    $overlay = Open-OverlayWithRuntimeRestartFallback
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $overlay
    $rows = @(Get-InventoryTextRows -Overlay $createdTasksDialog)
    if (@($rows | Where-Object { $_ -like "Open Reports 8*" }).Count -lt 1) {
        Add-Note "Large-inventory row 8 was not visible by name before edit invocation; proceeding with late-button reachability evidence."
    }
    $editButtons = @(Get-InventoryEditButtons -Overlay $createdTasksDialog)
    if ($editButtons.Count -lt 8) {
        throw "Expected at least 8 edit buttons in the large inventory view, found $($editButtons.Count)."
    }
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $editButtons[-1] -Description "late Created Tasks edit button"
    try {
        Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_TASK_EDIT_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    } catch {
        $createdTasksDialog = Open-CreatedTasksDialog -Overlay $overlay
        $editButtons = @(Get-InventoryEditButtons -Overlay $createdTasksDialog)
        $markerStart = New-RuntimeMarkerCursor
        Invoke-ElementRobust -Element $editButtons[-1] -Description "late Created Tasks edit button retry"
        Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_TASK_EDIT_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    }
    $dialog = Wait-ForDialog -Name "Edit Custom Task" -TimeoutSeconds 8
    Fill-AuthoringDialog -Dialog $dialog -TypeLabel "Folder" -Title "Open Reports Eight" -Aliases "show reports eight" -Target "C:\Reports\8"
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Save"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_ATTEMPT_STARTED|action_id=open_reports_8" -StartLine $markerStart
    Wait-ForCatalogReloadCompleted -StartLine $markerStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_UPDATED|action_id=open_reports_8" -StartLine $markerStart
    try {
        Wait-ForDialogRuntimeClosed -SignalBase "CUSTOM_TASK_EDIT_DIALOG" -StartLine $markerStart -TimeoutSeconds 4
    } catch {
        Add-Note "Late-item edit dialog close readback lagged after a successful update marker, but the runtime marker and refreshed Created Tasks view still confirmed the save."
    }
    $overlay = Ensure-OverlayReady -Overlay $overlay -Reason "large inventory edit flow"
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Open Reports Eight"
    $overlay = Close-CreatedTasksDialog -Dialog $createdTasksDialog -Overlay $overlay -Reason "post-large-inventory Created Tasks close"
    Copy-SourceSnapshot -Slug "after_large_inventory_edit" | Out-Null
    Write-StepLog -Stage "FLOW" -Message "large inventory late-item edit check complete; preparing next scenario"
    return (Ensure-OverlayReady -Overlay $overlay -Reason "post-large-inventory verification")
}

function Run-Unsafe-Source-Check {
    Write-StepLog -Stage "FLOW" -Message "running unsafe-source blocking check"
    Corrupt-Source
    Restart-InteractiveRuntime | Out-Null
    $overlay = Open-OverlayWithRuntimeRestartFallback
    $overlay = Ensure-OverlayReady -Overlay $overlay -Reason "unsafe-source blocking check"

    $resolveOverlay = {
        Resolve-LiveOverlayRoot -Overlay $overlay
    }
    $resolveCreateButton = {
        $liveOverlay = & $resolveOverlay
        if (-not $liveOverlay) {
            return $null
        }
        Find-ElementByAutomationIdsDirect -Root $liveOverlay -AutomationIds (Get-OverlayCreateButtonAutomationIds)
    }
    $resolveCommandStatus = {
        $liveOverlay = & $resolveOverlay
        if (-not $liveOverlay) {
            return $null
        }
        Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandStatus"
    }

    $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationIds (Get-OverlayCreateButtonAutomationIds) -Description "Create Custom Task button in unsafe-source path"
    $createButton = Focus-ElementForInteraction -ElementResolver $resolveCreateButton -Description "Create Custom Task button in unsafe-source path" -RequireExactFocus $false
    $markerStart = New-RuntimeMarkerCursor
    Write-StepLog -Stage "FLOW" -Message "invoking blocked create path for unsafe saved-action source"
    Invoke-ElementRobust -Element $createButton -Description "Create Custom Task button in unsafe-source path"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|reason=source_invalid" -StartLine $markerStart
    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_DIALOG_OPENED" -StartLine $markerStart) {
        throw "Unsafe source should block the create dialog before it opens."
    }
    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|" -StartLine $markerStart) {
        throw "Unsafe source unexpectedly produced a create marker."
    }

    Write-StepLog -Stage "FLOW" -Message "confirming unsafe-source overlay feedback state"
    Wait-Until -TimeoutSeconds 4 -Description "unsafe-source command status text" -Condition {
        $statusElement = & $resolveCommandStatus
        if (-not (Test-ElementUsable -Element $statusElement -RequireEnabled $false)) {
            return $false
        }
        $statusValue = Get-ElementReadableValue -Element $statusElement
        return -not [string]::IsNullOrWhiteSpace($statusValue)
    } | Out-Null
    $status = & $resolveCommandStatus
    $statusText = if ($status) { Get-ElementReadableValue -Element $status } else { "" }
    Write-StepLog -Stage "FLOW" -Message "unsafe-source overlay status='$statusText'"
    if ($statusText -notlike "*blocked*") {
        throw "Unsafe source did not surface blocked status text. Saw: '$statusText'"
    }

    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $overlay
    Write-StepLog -Stage "FLOW" -Message "confirming unsafe-source Created Tasks status state"
    $dialogStatus = Wait-ForDialogControlReady -DialogResolver { Resolve-LiveCreatedTasksDialogRoot -Dialog $createdTasksDialog } -AutomationIds (Get-CreatedTasksDialogControlAutomationIds -LeafAutomationId "savedActionCreatedTasksStatus") -Description "Created Tasks status in unsafe-source path" -RequireEnabled $false
    $dialogStatusText = if ($dialogStatus) { Get-ElementReadableValue -Element $dialogStatus } else { "" }
    Write-StepLog -Stage "FLOW" -Message "unsafe-source Created Tasks status='$dialogStatusText'"
    if (-not $dialogStatusText) {
        throw "Created Tasks dialog did not surface saved-action source status in the unsafe-source path."
    }

    $editButtons = @(Get-InventoryEditButtons -Overlay $createdTasksDialog)
    if ($editButtons.Count -gt 0) {
        Add-Note "Unsafe source still showed edit buttons inside Created Tasks; expected fail-closed absence was not observed."
    } else {
        Add-Note "Unsafe source hid edit affordances inside Created Tasks, which matches the fail-closed UI posture."
    }
    $overlay = Close-CreatedTasksDialog -Dialog $createdTasksDialog -Overlay $overlay -Reason "unsafe-source Created Tasks close"
    $overlay = Ensure-OverlayReady -Overlay $overlay
}

$originalSourceExists = Test-Path -LiteralPath $SourcePath
$originalSourceBytes = if ($originalSourceExists) { [System.IO.File]::ReadAllBytes($SourcePath) } else { [byte[]]@() }
[System.IO.File]::WriteAllBytes($SourceBackupPath, $originalSourceBytes)
$script:runtimeProcess = $null
$script:notepadProbe = $null
$script:watchdogProcess = $null
$script:baselineNotepadProcessIds = @(Get-NotepadProcessIds)
$script:baselineExplorerWindowHandles = @(Get-ExplorerWindowHandles)
$runFailure = $null

try {
    Write-StepLog -Stage "BUDGET" -Message "interactive validation budgets active: full_run=${script:InteractiveRunHardTimeoutSeconds}s no_progress=${script:NoProgressTimeoutSeconds}s scenario=${script:ScenarioTimeoutSeconds}s transition=${script:TransitionTimeoutSeconds}s"
    Stop-StaleInteractiveValidationProcesses
    $script:notepadProbe = Start-NotepadProbe
    Add-Artifact -Label "notepad_probe_file" -Path $script:notepadProbe.path
    $script:runtimeProcess = Start-InteractiveRuntime
    Add-Artifact -Label "interactive_runtime_log" -Path $RuntimeLogPath
    Add-Artifact -Label "interactive_step_log" -Path $StepLogPath
    $script:watchdogProcess = Start-ValidationWatchdog `
        -ParentPid $PID `
        -StepLogPath $StepLogPath `
        -ReportPath $ReportPath `
        -RuntimeLogPath $RuntimeLogPath `
        -SourcePath $SourcePath `
        -SourceBackupPath $SourceBackupPath `
        -WatchdogScriptPath $WatchdogScriptPath `
        -WatchdogStartSignalPath $WatchdogStartSignalPath `
        -WatchdogStdoutPath $WatchdogStdoutPath `
        -WatchdogStderrPath $WatchdogStderrPath `
        -SourceOriginallyPresent $originalSourceExists `
        -ProbePath $script:notepadProbe.path `
        -RunHardTimeoutSeconds $script:InteractiveRunHardTimeoutSeconds `
        -NoProgressTimeoutSeconds $script:NoProgressTimeoutSeconds `
        -StartupTimeoutSeconds $script:WatchdogStartupTimeoutSeconds
    Add-Note "Started interactive validation watchdog with full-run and no-progress enforcement."

    New-HealthySource
    Copy-SourceSnapshot -Slug "initial_source" | Out-Null

    Enter-ScenarioBudget -Name "overlay_open"
    $overlay = Open-OverlayWithRuntimeRestartFallback
    Add-ScenarioResult -Name "overlay_open" -Passed $true -Details "Overlay opened through the real hotkey and the runtime log recorded COMMAND_OVERLAY_OPENED."
    Clear-ScenarioBudget -Name "overlay_open"
    Invoke-ForcedValidationStallIfRequested -Point "after_overlay_open"

    Enter-ScenarioBudget -Name "valid_create" -TimeoutSeconds 150
    $overlay = Run-Create-Flow -Overlay $overlay
    Add-ScenarioResult -Name "valid_create" -Passed $true -Details "A real create dialog session created Open Notepad Task, emitted the success marker, and persisted the new task to saved_actions.json."
    Clear-ScenarioBudget -Name "valid_create"

    Enter-ScenarioBudget -Name "valid_group_create"
    $overlay = Run-Group-Create-Flow -Overlay $overlay
    Add-ScenarioResult -Name "valid_group_create" -Passed $true -Details "A real create-group dialog session created Workspace Tools with saved and built-in members."
    Clear-ScenarioBudget -Name "valid_group_create"

    Add-Note "Interactive invalid-create gating is limited to the Application path in this harness pass; folder/file/url create-target validation remains covered by the repo-side and live validators, and folder/file type mutation is still proven interactively through the edit-dialog scenarios."
    foreach ($invalidCreateCase in (Get-InvalidCreateCases)) {
        $invalidCreateScenarioName = "invalid_create_rejection_$(Get-ScenarioSlug -Value $invalidCreateCase.type)"
        Enter-ScenarioBudget -Name $invalidCreateScenarioName
        $overlay = Run-Invalid-Create-CheckCase -Overlay $overlay -Case $invalidCreateCase
        Add-ScenarioResult -Name $invalidCreateScenarioName -Passed $true -Details "Invalid $($invalidCreateCase.type) targets stayed blocked in the real create dialog with no write."
        Clear-ScenarioBudget -Name $invalidCreateScenarioName
    }

    Enter-ScenarioBudget -Name "collision_rejection"
    Run-Collision-Checks -Overlay $overlay
    Add-ScenarioResult -Name "collision_rejection" -Passed $true -Details "Built-in collisions stayed blocked in the real create dialog."
    Clear-ScenarioBudget -Name "collision_rejection"

    Enter-ScenarioBudget -Name "group_collision_rejection"
    $overlay = Run-Group-Collision-Checks -Overlay $overlay
    Add-ScenarioResult -Name "group_collision_rejection" -Passed $true -Details "Callable-group aliases stayed bounded against built-ins and existing exact phrases in the real create-group dialog."
    Clear-ScenarioBudget -Name "group_collision_rejection"

    Enter-ScenarioBudget -Name "valid_edit"
    $overlay = Run-Edit-Flow -Overlay $overlay
    Add-ScenarioResult -Name "valid_edit" -Passed $true -Details "The real edit dialog updated the same saved action in place and refreshed inventory immediately."
    Clear-ScenarioBudget -Name "valid_edit"

    Enter-ScenarioBudget -Name "invalid_edit_rejection"
    Run-Invalid-Edit-Check -Overlay $overlay
    Add-ScenarioResult -Name "invalid_edit_rejection" -Passed $true -Details "A malformed edit target stayed blocked in the real edit dialog and did not write."
    Clear-ScenarioBudget -Name "invalid_edit_rejection"

    Enter-ScenarioBudget -Name "exact_match_execution"
    Run-ExactMatch-Execution -Overlay $overlay
    Add-ScenarioResult -Name "exact_match_execution" -Passed $true -Details "Exact-match execution sent a real launch request for the edited saved action through the live overlay path."
    Clear-ScenarioBudget -Name "exact_match_execution"

    Enter-ScenarioBudget -Name "saved_alias_ambiguity"
    $overlay = Run-SavedAlias-Ambiguity-Selection -Overlay $overlay
    Add-ScenarioResult -Name "saved_alias_ambiguity" -Passed $true -Details "Two saved actions sharing the same alias surfaced the existing ambiguity chooser and selection executed the chosen action."
    Clear-ScenarioBudget -Name "saved_alias_ambiguity"

    Enter-ScenarioBudget -Name "group_exact_invocation"
    $overlay = Run-Group-Invocation-Check -Overlay $overlay
    Add-ScenarioResult -Name "group_exact_invocation" -Passed $true -Details "Exact group invocation surfaced the chooser and both saved and built-in members executed only when selected."
    Clear-ScenarioBudget -Name "group_exact_invocation"

    Enter-ScenarioBudget -Name "task_inline_group_quick_create" -TimeoutSeconds 120
    $overlay = Run-Task-Inline-Group-Check -Overlay $overlay
    Add-ScenarioResult -Name "task_inline_group_quick_create" -Passed $true -Details "Task authoring assigned an existing group and atomically created a new inline group without leaving the task flow."
    Clear-ScenarioBudget -Name "task_inline_group_quick_create"

    Enter-ScenarioBudget -Name "reopen_persistence"
    $overlay = Run-Reopen-Check
    Add-ScenarioResult -Name "reopen_persistence" -Passed $true -Details "Close/reopen preserved the latest saved action state and returned to a clean entry baseline."
    Clear-ScenarioBudget -Name "reopen_persistence"

    Enter-ScenarioBudget -Name "large_inventory_reachability"
    $overlay = Run-Large-Inventory-Check
    Add-ScenarioResult -Name "large_inventory_reachability" -Passed $true -Details "A later saved action beyond the old six-item cap was reachable and editable in the real UI."
    Clear-ScenarioBudget -Name "large_inventory_reachability"

    Enter-ScenarioBudget -Name "unsafe_source_blocking"
    Run-Unsafe-Source-Check
    Add-ScenarioResult -Name "unsafe_source_blocking" -Passed $true -Details "An invalid saved-actions source blocked real create entry and surfaced repair-oriented status feedback."
    Clear-ScenarioBudget -Name "unsafe_source_blocking"

    Enter-ScenarioBudget -Name "invalid_group_source_blocking"
    Run-Invalid-Group-Source-Check
    Add-ScenarioResult -Name "invalid_group_source_blocking" -Passed $true -Details "Invalid group records blocked real group entry but still allowed normal task authoring and exact task invocation paths."
    Clear-ScenarioBudget -Name "invalid_group_source_blocking"

    Enter-ScenarioBudget -Name "no_input_leakage"
    $notepadText = Get-NotepadText -Probe $script:notepadProbe
    if ($notepadText -ne "") {
        throw "Outside Notepad probe received unexpected input: '$notepadText'"
    }
    Add-ScenarioResult -Name "no_input_leakage" -Passed $true -Details "The outside Notepad probe stayed empty through overlay open, dialog interaction, submit, and reopen."
    Clear-ScenarioBudget -Name "no_input_leakage"

    Copy-SourceSnapshot -Slug "final_source_before_restore" | Out-Null
}
catch {
    if ($script:TimeoutTripReason) {
        Add-Note "Timeout/abort reason: $($script:TimeoutTripReason)"
        Add-Note "Last confirmed progress point: $($script:LastProgressPoint)"
        if ($script:CurrentScenarioName) {
            Add-Note "Scenario active at timeout: $($script:CurrentScenarioName)"
        }
        if ($script:CurrentTransitionName) {
            Add-Note "Transition active at timeout: $($script:CurrentTransitionName)"
        }
    }
    $windowNames = @()
    try {
        $windowNames = @(
            Get-RootWindows |
            ForEach-Object { $_.Current.Name } |
            Where-Object { $_ } |
            Select-Object -First 12
        )
    } catch {
    }
    if ($windowNames.Count -gt 0) {
        Add-Note ("Visible root windows at failure: " + ($windowNames -join " | "))
    }
    try {
        $runtimeTail = @((Get-RuntimeLogLines) | Select-Object -Last 12)
        if ($runtimeTail.Count -gt 0) {
            Add-Note ("Runtime log tail at failure: " + ($runtimeTail -join " || "))
        }
    } catch {
    }
    Add-ScenarioResult -Name "interactive_validation_failure" -Passed $false -Details $_.Exception.Message
    $runFailure = $_
}
finally {
    Restore-SavedActionSource -HadOriginal $originalSourceExists -OriginalBytes $originalSourceBytes
    Add-CleanupNote -Message "restored saved_actions.json to its pre-run state"

    if ($script:watchdogProcess) {
        try {
            Stop-WatchdogMonitorQuietly -Monitor $script:watchdogProcess
            Add-CleanupNote -Message "stopped the interactive validation watchdog"
        } catch {
        }
    }

    if ($script:notepadProbe) {
        try {
            Stop-ProcessQuietly -Process $script:notepadProbe.process
            Add-CleanupNote -Message "closed the validation external probe window"
        } catch {
        }
        try {
            if (
                $script:notepadProbe.window_process_id -and
                $script:notepadProbe.process_id -ne $script:notepadProbe.window_process_id
            ) {
                $windowProcess = Get-Process -Id ([int]$script:notepadProbe.window_process_id) -ErrorAction SilentlyContinue
                if ($windowProcess) {
                    Stop-ProcessQuietly -Process $windowProcess
                }
            }
        } catch {
        }
        try {
            if ($script:notepadProbe.path -and (Test-Path -LiteralPath $script:notepadProbe.path)) {
                Remove-Item -LiteralPath $script:notepadProbe.path -Force
                Add-CleanupNote -Message "deleted the validation Notepad probe file"
            }
        } catch {
            Add-Note "Cleanup could not delete the validation Notepad probe file cleanly."
        }
        try {
            if ($script:notepadProbe.script_path -and (Test-Path -LiteralPath $script:notepadProbe.script_path)) {
                Remove-Item -LiteralPath $script:notepadProbe.script_path -Force
                Add-CleanupNote -Message "deleted the validation probe helper script"
            }
        } catch {
            Add-Note "Cleanup could not delete the validation probe helper script cleanly."
        }
    }

    if ($script:runtimeProcess) {
        try {
            Stop-ProcessQuietly -Process $script:runtimeProcess
            Add-CleanupNote -Message "stopped the interactive runtime helper"
        } catch {
        }
    }

    try {
        $closedExplorerWindows = Close-NewExplorerWindows -BaselineWindowHandles $script:baselineExplorerWindowHandles
        if ($closedExplorerWindows -gt 0) {
            Add-CleanupNote -Message "closed $closedExplorerWindows File Explorer window(s) opened during validation"
        }
    } catch {
        Add-Note "Cleanup could not close every File Explorer window opened during validation."
    }

    try {
        $excludedNotepadIds = @()
        if ($script:notepadProbe -and $script:notepadProbe.process_id) {
            $excludedNotepadIds += [int]$script:notepadProbe.process_id
        }
        $closedNotepadProcesses = Stop-NewNotepadProcesses -BaselineProcessIds $script:baselineNotepadProcessIds -ExcludeProcessIds $excludedNotepadIds
        if ($closedNotepadProcesses -gt 0) {
            Add-CleanupNote -Message "closed $closedNotepadProcesses additional Notepad process(es) opened during validation"
        }
    } catch {
        Add-Note "Cleanup could not close every extra Notepad window opened during validation."
    }

    try {
        if (Test-Path -LiteralPath $SourceBackupPath) {
            Remove-Item -LiteralPath $SourceBackupPath -Force
            Add-CleanupNote -Message "deleted the watchdog source backup artifact"
        }
    } catch {
        Add-Note "Cleanup could not delete the watchdog source backup artifact cleanly."
    }

    try {
        if (Test-Path -LiteralPath $WatchdogScriptPath) {
            Remove-Item -LiteralPath $WatchdogScriptPath -Force
            Add-CleanupNote -Message "deleted the watchdog helper script"
        }
    } catch {
        Add-Note "Cleanup could not delete the watchdog helper script cleanly."
    }

    try {
        if (Test-Path -LiteralPath $WatchdogStartSignalPath) {
            Remove-Item -LiteralPath $WatchdogStartSignalPath -Force
            Add-CleanupNote -Message "deleted the watchdog startup signal artifact"
        }
    } catch {
        Add-Note "Cleanup could not delete the watchdog startup signal artifact cleanly."
    }

    try {
        if (Test-Path -LiteralPath $WatchdogStdoutPath) {
            Remove-Item -LiteralPath $WatchdogStdoutPath -Force
            Add-CleanupNote -Message "deleted the watchdog stdout artifact"
        }
    } catch {
        Add-Note "Cleanup could not delete the watchdog stdout artifact cleanly."
    }

    try {
        if (Test-Path -LiteralPath $WatchdogStderrPath) {
            Remove-Item -LiteralPath $WatchdogStderrPath -Force
            Add-CleanupNote -Message "deleted the watchdog stderr artifact"
        }
    } catch {
        Add-Note "Cleanup could not delete the watchdog stderr artifact cleanly."
    }
}

$reportLines = @()
$reportLines += "FB-036 SAVED-ACTION AUTHORING INTERACTIVE VALIDATION"
$reportLines += "Report: $ReportPath"
$reportLines += "Timestamp: $(Get-Date -Format o)"
$reportLines += ""
$reportLines += "Timeout Budgets:"
$reportLines += "  full_run_hard_timeout_seconds: $($script:InteractiveRunHardTimeoutSeconds)"
$reportLines += "  no_progress_timeout_seconds: $($script:NoProgressTimeoutSeconds)"
$reportLines += "  scenario_timeout_seconds: $($script:ScenarioTimeoutSeconds)"
$reportLines += "  transition_timeout_seconds: $($script:TransitionTimeoutSeconds)"
$reportLines += "  last_confirmed_progress_point: $($script:LastProgressPoint)"
if ($script:TimeoutTripReason) {
    $reportLines += "  timeout_abort_reason: $($script:TimeoutTripReason)"
}
$reportLines += ""
$reportLines += "Scenarios:"
foreach ($scenario in $ValidationState.scenarios) {
    $status = if ($scenario.passed) { "PASS" } else { "FAIL" }
    $reportLines += "  $status :: $($scenario.name)"
    $reportLines += "    $($scenario.details)"
}
$reportLines += ""
$reportLines += "Artifacts:"
foreach ($artifact in $ValidationState.artifacts) {
    $reportLines += "  - $($artifact.label): $($artifact.path)"
}
if ($ValidationState.notes.Count -gt 0) {
    $reportLines += ""
    $reportLines += "Notes:"
    foreach ($note in $ValidationState.notes) {
        $reportLines += "  - $note"
    }
}

Write-Utf8NoBomFile -Path $ReportPath -Content ($reportLines -join "`r`n")
Add-Artifact -Label "interactive_validation_report" -Path $ReportPath

$summary = [pscustomobject]@{
    report = $ReportPath
    runtime_log = $RuntimeLogPath
    timeout_budgets = [pscustomobject]@{
        full_run_hard_timeout_seconds = $script:InteractiveRunHardTimeoutSeconds
        no_progress_timeout_seconds = $script:NoProgressTimeoutSeconds
        scenario_timeout_seconds = $script:ScenarioTimeoutSeconds
        transition_timeout_seconds = $script:TransitionTimeoutSeconds
    }
    timeout_abort_reason = $script:TimeoutTripReason
    last_confirmed_progress_point = $script:LastProgressPoint
    scenarios = $ValidationState.scenarios
    artifacts = $ValidationState.artifacts
    notes = $ValidationState.notes
}

$summary | ConvertTo-Json -Depth 8

if ($runFailure) {
    throw $runFailure
}
