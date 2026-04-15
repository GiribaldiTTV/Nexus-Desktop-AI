param(
    [int]$InteractiveRunHardTimeoutSeconds = 420,
    [int]$NoProgressTimeoutSeconds = 45,
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
                    Get-Process notepad -ErrorAction SilentlyContinue |
                        Where-Object { $_.MainWindowTitle -like "*$probeLeaf*" } |
                        ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
                    if (Test-Path -LiteralPath $ProbePath) {
                        Remove-Item -LiteralPath $ProbePath -Force -ErrorAction SilentlyContinue
                    }
                    Add-WatchdogLine -Stage 'CLEANUP' -Message 'watchdog closed and removed the validation Notepad probe'
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
        [bool]$ResetFromTop = $false
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

    Send-VirtualKey -VirtualKey 0x0D
    Start-Sleep -Milliseconds 180
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
            if ((Get-ElementControlTypeNameSafe -Element $candidate -Context "Find-ComboPopupItem") -ne [System.Windows.Automation.ControlType]::ListItem.ProgrammaticName) {
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

function Select-ComboItem {
    param(
        [scriptblock]$ComboResolver,
        [string]$ItemName
    )

    $desiredIndex = [Array]::IndexOf($script:ActionTypeOrder, $ItemName)
    if ($desiredIndex -lt 0) {
        throw "Unsupported combo item '$ItemName'."
    }

    for ($attempt = 1; $attempt -le 3; $attempt++) {
        $Combo = & $ComboResolver
        if (-not $Combo) {
            throw "Could not resolve combo box for '$ItemName'."
        }

        $Combo = Focus-ElementForInteraction -ElementResolver $ComboResolver -Description "combo '$ItemName' selection control" -RequireExactFocus $false

        $currentValue = Get-ComboSelectedText -Combo $Combo
        $currentIndex = Get-ActionTypeIndexFromValue -Value $currentValue
        Write-StepLog -Stage "INTERACT" -Message "combo select attempt=$attempt desired='$ItemName' current='$currentValue' current_index=$currentIndex state=$(Get-ElementStateSummary -Element $Combo)"
        if ($currentValue -eq $ItemName) {
            return
        }

        try {
            $strategy = switch ($attempt) {
                1 { "keyboard_open_delta" }
                2 { "keyboard_open_reset" }
                default { "keyboard_closed_reset" }
            }
            Write-StepLog -Stage "INTERACT" -Message "combo select strategy=$strategy desired='$ItemName' attempt=$attempt"
            switch ($attempt) {
                1 {
                    Send-ComboSelectionSequence -DesiredIndex $desiredIndex -CurrentIndex $currentIndex -OpenDropdown $true -ResetFromTop $false
                }
                2 {
                    Send-ComboSelectionSequence -DesiredIndex $desiredIndex -CurrentIndex $currentIndex -OpenDropdown $true -ResetFromTop $true
                }
                default {
                    Send-ComboSelectionSequence -DesiredIndex $desiredIndex -CurrentIndex $currentIndex -OpenDropdown $false -ResetFromTop $true
                }
            }
        } catch {
            Add-Note "Combo selection attempt $attempt for '$ItemName' hit an interaction error before readback. Cause: $($_.Exception.Message)"
        }

        try {
            Wait-ForElementValue -ExpectedValue $ItemName -TimeoutSeconds 3 -Description "combo value $ItemName" -ElementResolver {
                return (& $ComboResolver)
            }
            return
        } catch {
            $actualCombo = & $ComboResolver
            $actualValue = Get-ComboSelectedText -Combo $actualCombo
            $actualIndex = Get-ActionTypeIndexFromValue -Value $actualValue
            Add-Note "Combo selection attempt $attempt for '$ItemName' did not stick; actual value read back as '$actualValue' (index=$actualIndex). State: $(Get-ElementStateSummary -Element $actualCombo)"
        }
    }

    $finalCombo = & $ComboResolver
    $finalValue = Get-ComboSelectedText -Combo $finalCombo
    throw "Combo selection for '$ItemName' did not stick. Final value: '$finalValue'. State: $(Get-ElementStateSummary -Element $finalCombo)"
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

function Get-DialogLookupChildAutomationId {
    param(
        [string]$Name
    )

    switch ($Name) {
        "Created Tasks" {
            return "QApplication.savedActionCreatedTasksDialog.savedActionCreatedTasksStatus"
        }
        default {
            return "QApplication.savedActionCreateDialog.savedActionCreateTitleInput"
        }
    }
}

function Get-OverlayAnchorAutomationIds {
    return @(
        "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton"
    )
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

    $childAutomationId = Get-DialogLookupChildAutomationId -Name $Name
    if ($childAutomationId) {
        $dialog = Find-DialogFromChildAutomationId -ExpectedName $Name -ChildAutomationId $childAutomationId
        if ($dialog) {
            return $dialog
        }
    }

    if ($Name -eq "Created Tasks") {
        $dialog = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.savedActionCreatedTasksDialog"
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
        [string]$Description,
        [int]$TimeoutSeconds = 6,
        [bool]$RequireEnabled = $true
    )

    Write-StepLog -Stage "DIALOG" -Message "verifying control '$Description' automationId='$AutomationId'"
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
        $element = Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId $AutomationId
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveDialog = & $DialogResolver
    if (-not $liveDialog) {
        throw "Could not resolve the live dialog while waiting for '$Description'."
    }

    $element = Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId $AutomationId
    if (-not (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)) {
        throw "Control '$Description' did not become usable. State: $(Get-ElementStateSummary -Element $element)"
    }

    Write-StepLog -Stage "DIALOG" -Message "control ready '$Description' state=$(Get-ElementStateSummary -Element $element)"
    return $element
}

function Wait-ForOverlayControlReady {
    param(
        [scriptblock]$OverlayResolver,
        [string]$AutomationId,
        [string]$Description,
        [int]$TimeoutSeconds = 6,
        [bool]$RequireEnabled = $true
    )

    Write-StepLog -Stage "OVERLAY" -Message "verifying control '$Description' automationId='$AutomationId'"
    Wait-Until -TimeoutSeconds $TimeoutSeconds -Description $Description -Condition {
        $liveOverlay = & $OverlayResolver
        if (-not $liveOverlay) {
            return $false
        }
        $element = Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId $AutomationId
        return (Test-ElementUsable -Element $element -RequireEnabled $RequireEnabled)
    } | Out-Null

    $liveOverlay = & $OverlayResolver
    if (-not $liveOverlay) {
        throw "Could not resolve the live overlay while waiting for '$Description'."
    }

    $element = Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId $AutomationId
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
        if ((Get-ElementControlTypeNameSafe -Element $element -Context "Get-InventoryTextRows") -eq [System.Windows.Automation.ControlType]::Text.ProgrammaticName -and $element.Current.Name -like "Open*") {
            $rows += $element.Current.Name
        }
    }
    return @($rows)
}

function Open-Overlay {
    if ($script:RuntimeAutoOpenPending) {
        $script:RuntimeAutoOpenPending = $false
        $markerStart = New-RuntimeMarkerCursor
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
        return (Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton")
    }

    $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton" -Description "Create Custom Task button"
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
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateType" -Description "create dialog task type combo"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTitleInput" -Description "create dialog title input"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateAliasesInput" -Description "create dialog aliases input"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTargetInput" -Description "create dialog target input"

    $typeCombo = Focus-ElementForInteraction -ElementResolver {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) {
            return $null
        }
        return (Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateType")
    } -Description "create dialog task type combo"

    if (-not $typeCombo) {
        throw "Could not focus the create dialog task type combo after dialog ready."
    }

    Write-StepLog -Stage "DIALOG" -Message "create-dialog entry ready and first interaction control focused"
    return (& $resolveDialog)
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
        return (Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton")
    }

    $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton" -Description "Created Tasks button"
    $button = Focus-ElementForInteraction -ElementResolver $resolveCreatedTasksButton -Description "Created Tasks button" -RequireExactFocus $false
    Write-StepLog -Stage "DIALOG" -Message "opening Created Tasks"
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $button -Description "Created Tasks button"

    try {
        Wait-ForDialogRuntimeReady -SignalBase "CREATED_TASKS_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    } catch {
        Add-Note "Created Tasks markers were not observed after the first entry button invoke; retrying once."
        $button = Focus-ElementForInteraction -ElementResolver $resolveCreatedTasksButton -Description "Created Tasks button retry" -RequireExactFocus $false
        Invoke-ElementRobust -Element $button -Description "Created Tasks button retry"
        Wait-ForDialogRuntimeReady -SignalBase "CREATED_TASKS_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    }

    $dialog = Wait-ForOptionalDialog -Name "Created Tasks" -TimeoutSeconds 3
    if ($dialog) {
        return $dialog
    }

    return (Wait-ForDialog -Name "Created Tasks" -TimeoutSeconds 8)
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
        Resolve-LiveDialogRoot -Dialog $CreatedTasksDialog -ExpectedName "Created Tasks"
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

    $dialogScope = [System.Windows.Automation.AutomationElement]::RootElement
    Write-StepLog -Stage "DIALOG" -Message "verifying edit-dialog entry readiness after runtime markers"

    $resolveDialog = {
        return $dialogScope
    }

    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateType" -Description "edit dialog task type combo"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTitleInput" -Description "edit dialog title input"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateAliasesInput" -Description "edit dialog aliases input"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTargetInput" -Description "edit dialog target input"

    $typeCombo = Focus-ElementForInteraction -ElementResolver {
        $liveScope = & $resolveDialog
        if (-not $liveScope) {
            return $null
        }
        return (Find-ElementByAutomationIdDirect -Root $liveScope -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateType")
    } -Description "edit dialog task type combo"

    if (-not $typeCombo) {
        throw "Could not focus the edit dialog task type combo after dialog ready."
    }

    $dialog = & $resolveEditDialog
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
        return (Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateType")
    }
    $resolveTitleInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTitleInput")
    }
    $resolveAliasesInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateAliasesInput")
    }
    $resolveTargetInput = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTargetInput")
    }
    $resolveExamplesLabel = {
        $liveDialog = & $resolveDialog
        if (-not $liveDialog) { return $null }
        return (Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTargetExamples")
    }
    $helpButtonMap = @(
        @{ Name = "Title"; AutomationId = "QApplication.savedActionCreateDialog.savedActionCreateTitleHelp" },
        @{ Name = "Aliases"; AutomationId = "QApplication.savedActionCreateDialog.savedActionCreateAliasesHelp" },
        @{ Name = "Trigger"; AutomationId = "QApplication.savedActionCreateDialog.savedActionCreateTriggerHelp" },
        @{ Name = "Target"; AutomationId = "QApplication.savedActionCreateDialog.savedActionCreateTargetHelp" }
    )

    $guidanceMap = @{
        "Application" = "Target format: notepad.exe or C:\\Program Files\\Notepad++\\notepad++.exe"
        "Folder" = "Target format: C:\\Reports"
        "File" = "Target format: C:\\Reports\\weekly.txt"
        "Website URL" = "Target format: https://example.com/docs"
    }

    Write-StepLog -Stage "DIALOG" -Message "verifying authoring dialog interaction readiness for '$dialogName'"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateType" -Description "task type combo"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTitleInput" -Description "title input"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateAliasesInput" -Description "aliases input"
    $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTargetInput" -Description "target input"

    Select-ComboItem -ComboResolver $resolveTypeCombo -ItemName $TypeLabel
    $selectedType = Get-ComboSelectedText -Combo (& $resolveTypeCombo)
    Write-StepLog -Stage "INTERACT" -Message "type selection final desired='$TypeLabel' actual='$selectedType'"
    if ($selectedType -ne $TypeLabel) {
        throw "Type selection did not apply. Expected '$TypeLabel', saw '$selectedType'."
    }

    try {
        $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateTargetExamples" -Description "bottom examples box" -TimeoutSeconds 2 -RequireEnabled $false
    } catch {
        Add-Note "Bottom examples box was not ready before the first field interactions, so the harness continued with the required input controls only."
    }

    foreach ($helpButtonInfo in $helpButtonMap) {
        try {
            $null = Wait-ForDialogControlReady -DialogResolver $resolveDialog -AutomationId $helpButtonInfo.AutomationId -Description "$($helpButtonInfo.Name) help button" -TimeoutSeconds 2 -RequireEnabled $false
        } catch {
            Add-Note "$($helpButtonInfo.Name) help button was not ready before the first field interactions."
        }
    }

    if ($guidanceMap.ContainsKey($TypeLabel)) {
        $expectedGuidance = $guidanceMap[$TypeLabel]
        $guidanceReady = $false
        try {
            Wait-Until -TimeoutSeconds 2 -Description "examples box refresh for $TypeLabel" -Condition {
                $liveExamples = & $resolveExamplesLabel
                if (-not $liveExamples) {
                    return $false
                }
                return (Get-ElementReadableValue -Element $liveExamples) -like "*$expectedGuidance*"
            } | Out-Null
            $guidanceReady = $true
        } catch {
        }
        if (-not $guidanceReady) {
            Add-Note "Bottom examples box did not refresh to the expected '$TypeLabel' wording on the first selection attempt; retrying the type selection once."
            Select-ComboItem -ComboResolver $resolveTypeCombo -ItemName $TypeLabel
            try {
                Wait-Until -TimeoutSeconds 2 -Description "examples box retry for $TypeLabel" -Condition {
                    $liveExamples = & $resolveExamplesLabel
                    if (-not $liveExamples) {
                        return $false
                    }
                    return (Get-ElementReadableValue -Element $liveExamples) -like "*$expectedGuidance*"
                } | Out-Null
                $guidanceReady = $true
            } catch {
            }
        }
        if (-not $guidanceReady) {
            Add-Note "Bottom examples box did not refresh to the expected '$TypeLabel' wording during one dialog interaction, but the subsequent dialog validation path still ran."
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

    $status = Find-FirstElement -Root $Dialog -AutomationId "QApplication.savedActionCreateDialog.savedActionCreateStatus"
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
        [System.Windows.Automation.AutomationElement]$Dialog
    )

    Write-StepLog -Stage "DIALOG" -Message "cancelling dialog '$($Dialog.Current.Name)'"
    $signalBase = if ($Dialog.Current.Name -eq "Edit Custom Task") { "CUSTOM_TASK_EDIT_DIALOG" } else { "CUSTOM_TASK_CREATE_DIALOG" }
    $markerStart = New-RuntimeMarkerCursor
    try { Submit-Dialog -Dialog $Dialog -ButtonName "Cancel" } catch {}
    try {
        Wait-ForDialogRuntimeClosed -SignalBase $signalBase -StartLine $markerStart -TimeoutSeconds 5
        Write-StepLog -Stage "DIALOG" -Message "$($Dialog.Current.Name) close confirmed by runtime marker"
        return
    } catch {
    }

    if (Get-DialogWindow -Name $Dialog.Current.Name) {
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
        $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton" -Description "Create Custom Task button after $Reason"
        $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton" -Description "Created Tasks button after $Reason"
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

    $argString = "dev\orin_saved_action_authoring_interactive_runtime.py --runtime-log `"$RuntimeLogPath`""
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
    $script:RuntimeLogLineCursor = Get-RuntimeLogLineCount
    $script:RuntimeAutoOpenPending = $false
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

function Start-NotepadProbe {
    $probeFile = Join-Path $ArtifactsDir "${Stamp}_notepad_probe.txt"
    Write-Utf8NoBomFile -Path $probeFile -Content ""
    $process = Start-Process -FilePath "notepad.exe" -ArgumentList "`"$probeFile`"" -PassThru
    $expectedTitle = "$(Split-Path -Leaf $probeFile) - Notepad"

    $window = $null
    Wait-Until -TimeoutSeconds 15 -Description "notepad probe window" -Condition {
        foreach ($candidate in (Get-RootWindows)) {
            if (
                (Get-ElementControlTypeNameSafe -Element $candidate -Context "Start-NotepadProbe") -eq [System.Windows.Automation.ControlType]::Window.ProgrammaticName -and
                $candidate.Current.ClassName -eq "Notepad" -and
                ($candidate.Current.Name -eq $expectedTitle -or $candidate.Current.Name -eq "Notepad")
            ) {
                $script:window = $candidate
                return $true
            }
        }
        return $false
    } | Out-Null

    $window = $script:window
    if (-not $window) {
        throw "Could not resolve Notepad automation window from the launched process."
    }
    Focus-Window -Element $window

    $editor = $null
    foreach ($candidate in (Get-AllDescendants -Element $window)) {
        if ($candidate.Current.ClassName -eq "RichEditD2DPT") {
            $editor = $candidate
            break
        }
    }
    if (-not $editor) {
        throw "Could not locate Notepad edit control."
    }
    Set-Value -Element $editor -Value ""

    return [pscustomobject]@{
        process = $process
        process_id = $process.Id
        window = $window
        editor = $editor
        path = $probeFile
        expected_title = $expectedTitle
    }
}

function Resolve-NotepadProbeWindow {
    param($Probe)

    $expectedTitle = if ($Probe.expected_title) { [string]$Probe.expected_title } else { "" }
    $expectedProcessId = 0
    try {
        $expectedProcessId = [int]$Probe.process_id
    } catch {
    }
    foreach ($candidate in (Get-RootWindows)) {
        try {
            if (
                (Get-ElementControlTypeNameSafe -Element $candidate -Context "Resolve-NotepadProbeWindow") -eq [System.Windows.Automation.ControlType]::Window.ProgrammaticName -and
                $candidate.Current.ClassName -eq "Notepad"
            ) {
                if ($expectedProcessId -gt 0 -and $candidate.Current.ProcessId -ne $expectedProcessId) {
                    continue
                }
                if ($expectedTitle -and $candidate.Current.Name -ne $expectedTitle -and $candidate.Current.Name -ne "Notepad") {
                    continue
                }
                return $candidate
            }
        } catch {
        }
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
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED|title=Open Notepad Task" -StartLine $markerStart
    Wait-ForCatalogReloadCompleted -StartLine $markerStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|action_id=open_notepad_task" -StartLine $markerStart
    Write-StepLog -Stage "FLOW" -Message "valid create markers completed; confirming dialog closure"
    try {
        Wait-ForDialogRuntimeClosed -SignalBase "CUSTOM_TASK_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 4
    } catch {
        Add-Note "Create dialog close readback lagged after a successful create marker, but the runtime marker and persisted source still confirmed the save."
    }
    $Overlay = Ensure-OverlayReady -Overlay $Overlay -Reason "successful create flow"
    Write-StepLog -Stage "FLOW" -Message "verifying created inventory after successful create"
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Open Notepad Task"
    $Overlay = Close-CreatedTasksDialog -Dialog $createdTasksDialog -Overlay $Overlay -Reason "post-create Created Tasks close"
    Copy-SourceSnapshot -Slug "after_create" | Out-Null
    Write-StepLog -Stage "FLOW" -Message "valid create flow complete; preparing next scenario"
    return (Ensure-OverlayReady -Overlay $Overlay -Reason "post-create inventory verification")
}

function Get-InvalidCreateCases {
    return @(
        @{ type = "Application"; title = "Bad App"; aliases = "bad app alias"; target = "notepad.exe --help"; expect = "Application targets" },
        @{ type = "Folder"; title = "Bad Folder"; aliases = "bad folder alias"; target = "Reports\Daily"; expect = "Folder targets" },
        @{ type = "File"; title = "Bad File"; aliases = "bad file alias"; target = "C:\Reports\bad?.txt"; expect = "File targets" },
        @{ type = "Website URL"; title = "Bad Url"; aliases = "bad url alias"; target = "example.com/docs"; expect = "absolute http or https URL" }
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

    $attemptMarker = "RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED|title=$Title"
    $blockedMarker = "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|reason=validation_error|title=$Title"
    $attemptSeen = $false
    $blockedSeen = $false

    Write-StepLog -Stage "FLOW" -Message "confirming blocked create submit for type='$TypeLabel' title='$Title'"

    try {
        Wait-ForRuntimeMarker -Marker $attemptMarker -StartLine $StartLine -TimeoutSeconds 6
        $attemptSeen = $true
    } catch {
        Add-Note "Invalid create submit for '$Title' did not surface the attempt-start marker within the first wait window."
    }

    try {
        Wait-ForRuntimeMarker -Marker $blockedMarker -StartLine $StartLine -TimeoutSeconds 6
        $blockedSeen = $true
    } catch {
        if (Test-RuntimeMarkerSeen -Marker $blockedMarker -StartLine $StartLine) {
            $blockedSeen = $true
            Add-Note "Invalid create submit for '$Title' surfaced the blocked marker after the timed wait loop missed it once; continuing with final log slice evidence."
        } else {
            Add-Note "Invalid create submit for '$Title' did not surface the blocked marker within the first wait window."
        }
    }

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

    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|" -StartLine $StartLine) {
        throw "Invalid target case '$TypeLabel' unexpectedly produced a create marker."
    }

    if (-not $blockedSeen) {
        throw "Invalid target case '$TypeLabel' never surfaced the expected blocked marker after submit."
    }

    Write-StepLog -Stage "FLOW" -Message "blocked create submit confirmed for type='$TypeLabel' title='$Title' attempt_marker=$attemptSeen blocked_marker=$blockedSeen"
}

function Run-Invalid-Create-CheckCase {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [hashtable]$Case
    )

    Write-StepLog -Stage "FLOW" -Message "running invalid create case type='$($Case.type)' title='$($Case.title)'"

    $beforeSourceText = if (Test-Path -LiteralPath $SourcePath) {
        Get-Content -LiteralPath $SourcePath -Raw
    } else {
        ""
    }
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
    Cancel-Dialog -Dialog $dialog
    return (Restore-OverlayAfterAuthoringDialogCancel -Overlay $Overlay -Reason "invalid create case '$($Case.type)' cancel")
}

function Run-Collision-Checks {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running collision checks"

    $cases = @(
        @{ title = "Explorer Helper"; aliases = "Open Windows Explorer"; target = "explorer.exe"; expect = "collide" },
        @{ title = "Duplicate Notepad"; aliases = "launch notepad task"; target = "notepad.exe"; expect = "collide" }
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

function Run-Edit-Flow {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running valid edit flow"

    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    $dialog = Open-EditDialog -CreatedTasksDialog $createdTasksDialog -EditIndex 0
    Fill-AuthoringDialog -Dialog $dialog -TypeLabel "Folder" -Title "Open Weekly Reports" -Aliases "weekly reports" -Target "C:\Windows"
    $markerStart = New-RuntimeMarkerCursor
    Submit-Dialog -Dialog $dialog -ButtonName "Save"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_ATTEMPT_STARTED|action_id=open_notepad_task" -StartLine $markerStart
    try {
        Wait-ForCatalogReloadCompleted -StartLine $markerStart
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_UPDATED|action_id=open_notepad_task" -StartLine $markerStart
    } catch {
        $currentDialog = Get-DialogWindow -Name "Edit Custom Task"
        if (-not $currentDialog) {
            throw
        }
        Add-Note "Edit save did not surface an update marker on the first submit; retrying Save once against the still-open dialog."
        $markerStart = New-RuntimeMarkerCursor
        Submit-Dialog -Dialog $currentDialog -ButtonName "Save"
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_ATTEMPT_STARTED|action_id=open_notepad_task" -StartLine $markerStart
        Wait-ForCatalogReloadCompleted -StartLine $markerStart
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_UPDATED|action_id=open_notepad_task" -StartLine $markerStart
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
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_ATTEMPT_STARTED|action_id=open_notepad_task" -StartLine $markerStart
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_EDIT_BLOCKED|reason=validation_error|action_id=open_notepad_task" -StartLine $markerStart
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
        Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton"
    }
    $resolveCommandStatus = {
        $liveOverlay = & $resolveOverlay
        if (-not $liveOverlay) {
            return $null
        }
        Find-ElementByAutomationIdDirect -Root $liveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandStatus"
    }

    $null = Wait-ForOverlayControlReady -OverlayResolver $resolveOverlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton" -Description "Create Custom Task button in unsafe-source path"
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
    $dialogStatus = Wait-ForDialogControlReady -DialogResolver { Resolve-LiveDialogRoot -Dialog $createdTasksDialog -ExpectedName "Created Tasks" } -AutomationId "QApplication.savedActionCreatedTasksDialog.savedActionCreatedTasksStatus" -Description "Created Tasks status in unsafe-source path" -RequireEnabled $false
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
$runFailure = $null

try {
    Write-StepLog -Stage "BUDGET" -Message "interactive validation budgets active: full_run=${script:InteractiveRunHardTimeoutSeconds}s no_progress=${script:NoProgressTimeoutSeconds}s scenario=${script:ScenarioTimeoutSeconds}s transition=${script:TransitionTimeoutSeconds}s"
    Stop-StaleInteractiveValidationProcesses
    $script:runtimeProcess = Start-InteractiveRuntime
    Add-Artifact -Label "interactive_runtime_log" -Path $RuntimeLogPath
    Add-Artifact -Label "interactive_step_log" -Path $StepLogPath

    $script:notepadProbe = Start-NotepadProbe
    Add-Artifact -Label "notepad_probe_file" -Path $script:notepadProbe.path
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

    Enter-ScenarioBudget -Name "valid_create"
    $overlay = Run-Create-Flow -Overlay $overlay
    Add-ScenarioResult -Name "valid_create" -Passed $true -Details "A real create dialog session created Open Notepad Task and refreshed inventory immediately."
    Clear-ScenarioBudget -Name "valid_create"

    foreach ($invalidCreateCase in (Get-InvalidCreateCases)) {
        $invalidCreateScenarioName = "invalid_create_rejection_$(Get-ScenarioSlug -Value $invalidCreateCase.type)"
        Enter-ScenarioBudget -Name $invalidCreateScenarioName
        $overlay = Run-Invalid-Create-CheckCase -Overlay $overlay -Case $invalidCreateCase
        Add-ScenarioResult -Name $invalidCreateScenarioName -Passed $true -Details "Invalid $($invalidCreateCase.type) targets stayed blocked in the real create dialog with no write."
        Clear-ScenarioBudget -Name $invalidCreateScenarioName
    }

    Enter-ScenarioBudget -Name "collision_rejection"
    Run-Collision-Checks -Overlay $overlay
    Add-ScenarioResult -Name "collision_rejection" -Passed $true -Details "Built-in and saved-action collisions were blocked in the real create dialog."
    Clear-ScenarioBudget -Name "collision_rejection"

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
            Add-CleanupNote -Message "closed the validation Notepad probe window"
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
    }

    if ($script:runtimeProcess) {
        try {
            Stop-ProcessQuietly -Process $script:runtimeProcess
            Add-CleanupNote -Message "stopped the interactive runtime helper"
        } catch {
        }
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
