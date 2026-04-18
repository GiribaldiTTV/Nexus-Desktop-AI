param(
    [int]$TimeoutSeconds = 12
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$source = @"
using System;
using System.Runtime.InteropServices;

public static class CodexFb041Win32
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
$OutputDir = Join-Path $RootDir "dev\logs\fb_041_callable_group_interactive_validation\$Stamp"
$ReportPath = Join-Path $OutputDir "FB041CallableGroupInteractiveValidationReport_$Stamp.txt"
$RuntimeLogPath = Join-Path $OutputDir "runtime.log"
$ManifestPath = Join-Path $OutputDir "manifest.json"
$SourcePath = Join-Path $env:LOCALAPPDATA "Nexus Desktop AI\saved_actions.json"
$SourceBackupPath = Join-Path $OutputDir "saved_actions.backup.json"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $SourcePath) | Out-Null

$script:Captures = New-Object System.Collections.Generic.List[object]
$script:ScenarioResults = New-Object System.Collections.Generic.List[object]
$script:Notes = New-Object System.Collections.Generic.List[string]
$script:RuntimeProcess = $null

function Add-Note {
    param([string]$Message)
    $script:Notes.Add($Message)
}

function Add-Capture {
    param(
        [string]$Label,
        [string]$Path
    )

    $script:Captures.Add([pscustomobject]@{
            label = $Label
            path  = $Path
        })
}

function Add-ScenarioResult {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details
    )

    $script:ScenarioResults.Add([pscustomobject]@{
            name    = $Name
            passed  = $Passed
            details = $Details
        })
}

function Wait-Until {
    param(
        [scriptblock]$Condition,
        [string]$Description,
        [int]$TimeoutSeconds = $TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $result = & $Condition
        if ($result) {
            return $result
        }
        Start-Sleep -Milliseconds 120
    }

    throw "Timed out waiting for $Description."
}

function Get-AllDescendants {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return @()
    }

    try {
        return @(
            $Element.FindAll(
                [System.Windows.Automation.TreeScope]::Subtree,
                [System.Windows.Automation.Condition]::TrueCondition
            )
        )
    } catch {
        return @()
    }
}

function Find-RootWindow {
    param(
        [string]$Name = "",
        [string]$AutomationId = "",
        [string]$ClassName = ""
    )

    $children = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition
    )

    for ($i = 0; $i -lt $children.Count; $i++) {
        $window = $children.Item($i)
        try {
            if ($Name -and $window.Current.Name -ne $Name) {
                continue
            }
            if ($AutomationId -and $window.Current.AutomationId -ne $AutomationId) {
                continue
            }
            if ($ClassName -and $window.Current.ClassName -ne $ClassName) {
                continue
            }
            if ($window.Current.IsOffscreen) {
                continue
            }
            return $window
        } catch {
        }
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

    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        $AutomationId
    )
    return $Root.FindFirst([System.Windows.Automation.TreeScope]::Subtree, $condition)
}

function Find-ElementByAutomationIdSuffix {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$Suffix
    )

    if (-not $Root -or [string]::IsNullOrWhiteSpace($Suffix)) {
        return $null
    }

    foreach ($candidate in (Get-AllDescendants -Element $Root)) {
        try {
            $automationId = [string]$candidate.Current.AutomationId
            if ($automationId -and $automationId.EndsWith($Suffix, [System.StringComparison]::OrdinalIgnoreCase)) {
                return $candidate
            }
        } catch {
        }
    }

    return $null
}

function Find-FirstElementByName {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$Name,
        [System.Windows.Automation.ControlType]$ControlType = $null
    )

    if (-not $Root -or [string]::IsNullOrWhiteSpace($Name)) {
        return $null
    }

    foreach ($candidate in (Get-AllDescendants -Element $Root)) {
        try {
            if ($candidate.Current.Name -ne $Name) {
                continue
            }
            if ($null -ne $ControlType -and $candidate.Current.ControlType -ne $ControlType) {
                continue
            }
            return $candidate
        } catch {
        }
    }

    return $null
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
        return ($rect.Width -gt 0 -and $rect.Height -gt 0)
    } catch {
        return $false
    }
}

function Focus-Element {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return
    }

    try {
        $handle = [int]$Element.Current.NativeWindowHandle
        if ($handle -gt 0) {
            [CodexFb041Win32]::ShowWindowAsync([IntPtr]$handle, 5) | Out-Null
            [CodexFb041Win32]::SetForegroundWindow([IntPtr]$handle) | Out-Null
        }
    } catch {
    }

    try {
        $Element.SetFocus()
    } catch {
    }
}

function Set-ElementValue {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Value,
        [string]$Description
    )

    if (-not $Element) {
        throw "Missing element for $Description."
    }

    Focus-Element -Element $Element

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        $pattern.SetValue($Value)
        return
    } catch {
    }

    throw "Could not set value for $Description."
}

function Send-VirtualKey {
    param([byte]$Key)
    [CodexFb041Win32]::keybd_event($Key, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 35
    [CodexFb041Win32]::keybd_event($Key, 0, 2, [UIntPtr]::Zero)
}

function Get-RectangleBounds {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [int]$Padding = 10
    )

    $rect = $Element.Current.BoundingRectangle
    $left = [math]::Max([int]([math]::Floor($rect.Left)) - $Padding, 0)
    $top = [math]::Max([int]([math]::Floor($rect.Top)) - $Padding, 0)
    $width = [math]::Max([int]([math]::Ceiling($rect.Width)) + ($Padding * 2), 1)
    $height = [math]::Max([int]([math]::Ceiling($rect.Height)) + ($Padding * 2), 1)
    return [pscustomobject]@{
        Left   = $left
        Top    = $top
        Width  = $width
        Height = $height
    }
}

function Capture-ElementScreenshot {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Label,
        [int]$DelayMs = 220
    )

    Focus-Element -Element $Element
    Start-Sleep -Milliseconds $DelayMs

    $bounds = Get-RectangleBounds -Element $Element
    $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bitmap.Size)
    $path = Join-Path $OutputDir ($Label + ".png")
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    Add-Capture -Label $Label -Path $path
    return $path
}

function Get-ElementReadableText {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return ""
    }

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        if ($pattern) {
            return [string]$pattern.Current.Value
        }
    } catch {
    }

    try {
        return [string]$Element.Current.Name
    } catch {
        return ""
    }
}

function Get-RuntimeLogLineCount {
    if (-not (Test-Path -LiteralPath $RuntimeLogPath)) {
        return 0
    }
    return @(Get-Content -LiteralPath $RuntimeLogPath).Count
}

function Get-RuntimeLinesSince {
    param([int]$StartLine = 0)

    if (-not (Test-Path -LiteralPath $RuntimeLogPath)) {
        return @()
    }

    $lines = @(Get-Content -LiteralPath $RuntimeLogPath)
    if ($lines.Count -le $StartLine) {
        return @()
    }
    return @($lines | Select-Object -Skip $StartLine)
}

function Wait-ForRuntimeMarker {
    param(
        [string]$Marker,
        [int]$StartLine = 0,
        [int]$TimeoutSeconds = 12
    )

    return (Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "runtime marker $Marker" -Condition {
            foreach ($line in (Get-RuntimeLinesSince -StartLine $StartLine)) {
                if ($line -like "*$Marker*") {
                    return $line
                }
            }
            return $null
        })
}

function Stop-RuntimeHelper {
    if ($script:RuntimeProcess) {
        try {
            Stop-Process -Id $script:RuntimeProcess.Id -Force -ErrorAction Stop
        } catch {
        }
        $script:RuntimeProcess = $null
        Start-Sleep -Milliseconds 350
    }
}

function Start-RuntimeHelper {
    Stop-RuntimeHelper

    $python = (Get-Command python).Source
    if (-not $python) {
        throw "Could not resolve python executable for the interactive runtime helper."
    }

    if (Test-Path -LiteralPath $RuntimeLogPath) {
        Remove-Item -LiteralPath $RuntimeLogPath -Force -ErrorAction SilentlyContinue
    }

    $argString = "dev\\orin_saved_action_authoring_interactive_runtime.py --runtime-log `"$RuntimeLogPath`" --auto-open-overlay"
    $previousOverlayTrace = $env:NEXUS_OVERLAY_TRACE
    $env:NEXUS_OVERLAY_TRACE = "1"
    try {
        $process = Start-Process -FilePath $python -ArgumentList $argString -WorkingDirectory $RootDir -PassThru -WindowStyle Hidden
    } finally {
        $env:NEXUS_OVERLAY_TRACE = $previousOverlayTrace
    }

    $script:RuntimeProcess = $process

    Wait-Until -TimeoutSeconds 20 -Description "runtime log creation" -Condition {
        Test-Path -LiteralPath $RuntimeLogPath
    } | Out-Null

    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|STARTUP_READY" -TimeoutSeconds 25 | Out-Null
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|DESKTOP_ATTACH_RESULT|success=true" -TimeoutSeconds 25 | Out-Null
}

function Get-OverlayWindow {
    $overlay = Find-RootWindow -AutomationId "QApplication.commandOverlayWindow" -ClassName "CommandOverlayPanel"
    if ($overlay) {
        return $overlay
    }
    return $null
}

function Get-OverlayInput {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    return Find-ElementByAutomationIdSuffix -Root $Overlay -Suffix "commandInputLine"
}

function Open-Overlay {
    Start-RuntimeHelper

    try {
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPENED" -TimeoutSeconds 6 | Out-Null
    } catch {
    }

    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -TimeoutSeconds 8 | Out-Null
    return (Wait-Until -TimeoutSeconds ([Math]::Max(4, $TimeoutSeconds)) -Description "overlay window" -Condition {
            $overlay = Get-OverlayWindow
            if (-not $overlay) {
                return $null
            }
            $input = Get-OverlayInput -Overlay $overlay
            if ($input -and (Test-ElementUsable -Element $input)) {
                return $overlay
            }
            return $null
        })
}

function Resolve-OverlayInput {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    return (Wait-Until -Description "overlay input" -Condition {
            $liveOverlay = Get-OverlayWindow
            if (-not $liveOverlay) {
                return $null
            }
            $input = Get-OverlayInput -Overlay $liveOverlay
            if ($input -and (Test-ElementUsable -Element $input)) {
                return $input
            }
            return $null
        })
}

function Close-WindowByEsc {
    param([System.Windows.Automation.AutomationElement]$Window)
    Focus-Element -Element $Window
    Send-VirtualKey -Key 0x1B
    Start-Sleep -Milliseconds 220
}

function Backup-Source {
    if (Test-Path -LiteralPath $SourcePath) {
        Copy-Item -LiteralPath $SourcePath -Destination $SourceBackupPath -Force
    }
}

function Restore-Source {
    if (Test-Path -LiteralPath $SourceBackupPath) {
        Copy-Item -LiteralPath $SourceBackupPath -Destination $SourcePath -Force
    } elseif (Test-Path -LiteralPath $SourcePath) {
        Remove-Item -LiteralPath $SourcePath -Force -ErrorAction SilentlyContinue
    }
}

function Seed-Fb041Source {
    $payload = [ordered]@{
        schema_version = 1
        actions        = @(
            [ordered]@{
                id              = "workspace_docs_folder"
                title           = "Open Workspace Docs"
                target_kind     = "folder"
                target          = "C:\Nexus Desktop AI\Docs"
                aliases         = @("workspace docs")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_notes_task"
                title           = "Open Notes Task"
                target_kind     = "app"
                target          = "notepad.exe"
                aliases         = @("notes task")
                invocation_mode = "aliases_only"
                trigger_mode    = "launch"
            },
            [ordered]@{
                id              = "broken_notes_task"
                title           = "Broken Notes Task"
                target_kind     = "app"
                target          = "C:\definitely_missing\does_not_exist.exe"
                aliases         = @("broken notes")
                invocation_mode = "aliases_only"
                trigger_mode    = "launch"
            }
        )
        groups         = @(
            [ordered]@{
                id                = "workspace_tools"
                title             = "Workspace Tools"
                aliases           = @("workspace tools")
                member_action_ids = @("workspace_docs_folder", "open_notes_task")
            },
            [ordered]@{
                id                = "broken_workspace_tools"
                title             = "Broken Workspace Tools"
                aliases           = @("broken workspace tools")
                member_action_ids = @("broken_notes_task", "open_notes_task")
            }
        )
    }

    $json = ($payload | ConvertTo-Json -Depth 8) + "`n"
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($SourcePath, $json, $encoding)
}

function Get-NotepadProcessIds {
    return @(
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq "notepad.exe" } |
            Select-Object -ExpandProperty ProcessId
    )
}

function Wait-ForNewNotepadProcess {
    param(
        [int[]]$BaselineIds,
        [int]$TimeoutSeconds = 8
    )

    return (Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "new Notepad process" -Condition {
            $newIds = @((Get-NotepadProcessIds) | Where-Object { $BaselineIds -notcontains $_ })
            if ($newIds.Count -gt 0) {
                return $newIds
            }
            return $null
        })
}

function Stop-NewNotepadProcesses {
    param([int[]]$BaselineIds)

    $newIds = @((Get-NotepadProcessIds) | Where-Object { $BaselineIds -notcontains $_ })
    foreach ($id in $newIds) {
        try {
            Stop-Process -Id $id -Force -ErrorAction Stop
        } catch {
        }
    }
}

function Get-OverlayTextByAutomationIdSuffix {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Suffix
    )

    $element = Find-ElementByAutomationIdSuffix -Root $Overlay -Suffix $Suffix
    return (Get-ElementReadableText -Element $element).Trim()
}

function Wait-ForOverlayStatusTextExact {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Expected
    )

    return (Wait-Until -Description "status text '$Expected'" -Condition {
            $liveOverlay = Get-OverlayWindow
            if (-not $liveOverlay) {
                return $null
            }
            $text = Get-OverlayTextByAutomationIdSuffix -Overlay $liveOverlay -Suffix "commandStatus"
            if ($text -eq $Expected) {
                return $text
            }
            return $null
        })
}

function Wait-ForOverlayStatusTextPrefix {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Prefix
    )

    return (Wait-Until -Description "status text prefix '$Prefix'" -Condition {
            $liveOverlay = Get-OverlayWindow
            if (-not $liveOverlay) {
                return $null
            }
            $text = Get-OverlayTextByAutomationIdSuffix -Overlay $liveOverlay -Suffix "commandStatus"
            if ($text.StartsWith($Prefix, [System.StringComparison]::Ordinal)) {
                return $text
            }
            return $null
        })
}

function Wait-ForOverlayHintText {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string]$Expected
    )

    return (Wait-Until -Description "hint text '$Expected'" -Condition {
            $liveOverlay = Get-OverlayWindow
            if (-not $liveOverlay) {
                return $null
            }
            $text = Get-OverlayTextByAutomationIdSuffix -Overlay $liveOverlay -Suffix "commandHint"
            if ($text -eq $Expected) {
                return $text
            }
            return $null
        })
}

function Wait-ForTextPresence {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$Text,
        [int]$TimeoutSeconds = 6
    )

    return (Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "text '$Text'" -Condition {
            $liveRoot = Get-OverlayWindow
            if (-not $liveRoot) {
                return $null
            }
            $element = Find-FirstElementByName -Root $liveRoot -Name $Text
            if ($element) {
                return $element
            }
            return $null
        })
}

function Assert-RuntimeMarkerOrder {
    param(
        [string[]]$Lines,
        [string[]]$Markers
    )

    $lastIndex = -1
    foreach ($marker in $Markers) {
        $index = -1
        for ($i = 0; $i -lt $Lines.Count; $i++) {
            if ($Lines[$i] -like "*$marker*") {
                $index = $i
                break
            }
        }
        if ($index -lt 0) {
            throw "Missing runtime marker '$marker'."
        }
        if ($index -le $lastIndex) {
            throw "Runtime marker '$marker' did not appear after the prior marker."
        }
        $lastIndex = $index
    }
}

function Run-GroupSuccessScenario {
    Seed-Fb041Source
    $baselineNotepadIds = @(Get-NotepadProcessIds)
    $overlay = Open-Overlay
    $overlayInput = Resolve-OverlayInput -Overlay $overlay

    $markerStart = Get-RuntimeLogLineCount
    Set-ElementValue -Element $overlayInput -Value "workspace tools" -Description "group success invocation"
    Send-VirtualKey -Key 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_AMBIGUOUS|count=2" -StartLine $markerStart -TimeoutSeconds 6 | Out-Null

    Focus-Element -Element $overlay
    Start-Sleep -Milliseconds 180
    $markerStart = Get-RuntimeLogLineCount
    Send-VirtualKey -Key 0x32
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=open_notes_task" -StartLine $markerStart -TimeoutSeconds 6 | Out-Null

    $expectedGroupHint = 'Review the selected member details below. Press Enter to run "Workspace Tools" group in stored order.'
    $expectedGroupHelp = 'Press Enter to run "Workspace Tools" group in stored order, or Esc to return.'
    Wait-ForOverlayHintText -Overlay $overlay -Expected $expectedGroupHint | Out-Null
    Wait-ForTextPresence -Root $overlay -Text "Selected member" | Out-Null
    Wait-ForTextPresence -Root $overlay -Text $expectedGroupHelp | Out-Null
    Wait-ForTextPresence -Root $overlay -Text "Open Notes Task" | Out-Null
    Capture-ElementScreenshot -Element $overlay -Label "group_success_confirm" | Out-Null

    $markerStart = Get-RuntimeLogLineCount
    Focus-Element -Element $overlay
    Send-VirtualKey -Key 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|GROUP_EXECUTION_COMPLETED|group_id=workspace_tools" -StartLine $markerStart -TimeoutSeconds 10 | Out-Null
    $resultText = Wait-ForOverlayStatusTextExact -Overlay $overlay -Expected 'Group "Workspace Tools" executed in stored order.'
    $hintText = Wait-ForOverlayHintText -Overlay $overlay -Expected "Returning to passive desktop mode."
    Capture-ElementScreenshot -Element $overlay -Label "group_success_result" | Out-Null

    $newNotepad = @(Wait-ForNewNotepadProcess -BaselineIds $baselineNotepadIds -TimeoutSeconds 8)
    $runtimeLines = @(Get-RuntimeLinesSince -StartLine $markerStart)
    Assert-RuntimeMarkerOrder -Lines $runtimeLines -Markers @(
        "RENDERER_MAIN|GROUP_EXECUTION_STARTED|group_id=workspace_tools",
        "RENDERER_MAIN|GROUP_EXECUTION_STEP_STARTED|group_id=workspace_tools|step_index=1|action_id=workspace_docs_folder",
        "RENDERER_MAIN|GROUP_EXECUTION_STEP_SUCCEEDED|group_id=workspace_tools|step_index=1|action_id=workspace_docs_folder",
        "RENDERER_MAIN|GROUP_EXECUTION_STEP_STARTED|group_id=workspace_tools|step_index=2|action_id=open_notes_task",
        "RENDERER_MAIN|GROUP_EXECUTION_STEP_SUCCEEDED|group_id=workspace_tools|step_index=2|action_id=open_notes_task",
        "RENDERER_MAIN|GROUP_EXECUTION_COMPLETED|group_id=workspace_tools"
    )
    Stop-NewNotepadProcesses -BaselineIds $baselineNotepadIds
    Stop-RuntimeHelper

    Add-ScenarioResult -Name "group_success" -Passed $true -Details (
        "Real launched-process group execution ran Workspace Tools in stored order after the confirm surface kept Open Notes Task as inspection context. " +
        "Result text was '$resultText', hint remained '$hintText', and a real Notepad process launched."
    )
}

function Run-GroupFailureScenario {
    Seed-Fb041Source
    $baselineNotepadIds = @(Get-NotepadProcessIds)
    $overlay = Open-Overlay
    $overlayInput = Resolve-OverlayInput -Overlay $overlay

    $markerStart = Get-RuntimeLogLineCount
    Set-ElementValue -Element $overlayInput -Value "broken workspace tools" -Description "group failure invocation"
    Send-VirtualKey -Key 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_AMBIGUOUS|count=2" -StartLine $markerStart -TimeoutSeconds 6 | Out-Null

    Focus-Element -Element $overlay
    Start-Sleep -Milliseconds 180
    $markerStart = Get-RuntimeLogLineCount
    Send-VirtualKey -Key 0x32
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=open_notes_task" -StartLine $markerStart -TimeoutSeconds 6 | Out-Null

    $markerStart = Get-RuntimeLogLineCount
    Focus-Element -Element $overlay
    Send-VirtualKey -Key 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|GROUP_EXECUTION_FAILED|group_id=broken_workspace_tools" -StartLine $markerStart -TimeoutSeconds 10 | Out-Null
    $resultText = Wait-ForOverlayStatusTextPrefix -Overlay $overlay -Prefix 'Group "Broken Workspace Tools" failed at step 1:'
    $hintText = Wait-ForOverlayHintText -Overlay $overlay -Expected "Returning to passive desktop mode."
    Capture-ElementScreenshot -Element $overlay -Label "group_failure_result" | Out-Null

    $runtimeLines = @(Get-RuntimeLinesSince -StartLine $markerStart)
    Assert-RuntimeMarkerOrder -Lines $runtimeLines -Markers @(
        "RENDERER_MAIN|GROUP_EXECUTION_STARTED|group_id=broken_workspace_tools",
        "RENDERER_MAIN|GROUP_EXECUTION_STEP_STARTED|group_id=broken_workspace_tools|step_index=1|action_id=broken_notes_task",
        "RENDERER_MAIN|GROUP_EXECUTION_STEP_FAILED|group_id=broken_workspace_tools|step_index=1|action_id=broken_notes_task",
        "RENDERER_MAIN|GROUP_EXECUTION_FAILED|group_id=broken_workspace_tools"
    )
    foreach ($line in $runtimeLines) {
        if ($line -like "*GROUP_EXECUTION_STEP_STARTED*group_id=broken_workspace_tools*action_id=open_notes_task*") {
            throw "Failure scenario unexpectedly started a later member after the first failure."
        }
    }

    $newNotepad = @((Get-NotepadProcessIds) | Where-Object { $baselineNotepadIds -notcontains $_ })
    if ($newNotepad.Count -gt 0) {
        throw "Failure scenario unexpectedly launched Notepad."
    }

    Stop-RuntimeHelper
    Add-ScenarioResult -Name "group_failure" -Passed $true -Details (
        "Real launched-process group execution failed on Broken Workspace Tools step 1 without starting later members. " +
        "Result text began with '$resultText' and the result hint remained '$hintText'."
    )
}

function Run-SingleActionAuditScenario {
    Seed-Fb041Source
    $baselineNotepadIds = @(Get-NotepadProcessIds)
    $overlay = Open-Overlay
    $overlayInput = Resolve-OverlayInput -Overlay $overlay

    $markerStart = Get-RuntimeLogLineCount
    Set-ElementValue -Element $overlayInput -Value "notes task" -Description "single action invocation"
    Send-VirtualKey -Key 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=open_notes_task" -StartLine $markerStart -TimeoutSeconds 6 | Out-Null

    $expectedSingleHint = "Review the resolved action origin and destination before execution."
    $expectedSingleHelp = "Press Enter to confirm or Esc to return."
    Wait-ForOverlayHintText -Overlay $overlay -Expected $expectedSingleHint | Out-Null
    Wait-ForTextPresence -Root $overlay -Text "Resolved action" | Out-Null
    Wait-ForTextPresence -Root $overlay -Text $expectedSingleHelp | Out-Null
    Capture-ElementScreenshot -Element $overlay -Label "single_action_confirm" | Out-Null

    $markerStart = Get-RuntimeLogLineCount
    Focus-Element -Element $overlay
    Send-VirtualKey -Key 0x0D
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id=open_notes_task" -StartLine $markerStart -TimeoutSeconds 8 | Out-Null
    $resultText = Wait-ForOverlayStatusTextExact -Overlay $overlay -Expected "Launch request sent."
    $hintText = Wait-ForOverlayHintText -Overlay $overlay -Expected "Returning to passive desktop mode."
    Capture-ElementScreenshot -Element $overlay -Label "single_action_result" | Out-Null

    $newNotepad = @(Wait-ForNewNotepadProcess -BaselineIds $baselineNotepadIds -TimeoutSeconds 8)
    Stop-NewNotepadProcesses -BaselineIds $baselineNotepadIds
    Stop-RuntimeHelper

    Add-ScenarioResult -Name "single_action_audit" -Passed $true -Details (
        "Single-action confirm and result surfaces stayed unchanged: confirm hint '$expectedSingleHint', result text '$resultText', hint '$hintText'."
    )
}

try {
    Backup-Source
    Seed-Fb041Source

    Run-GroupSuccessScenario
    Run-GroupFailureScenario
    Run-SingleActionAuditScenario
} catch {
    Add-ScenarioResult -Name "interactive_validation_failure" -Passed $false -Details $_.Exception.Message
    throw
} finally {
    Stop-NewNotepadProcesses -BaselineIds @()
    Stop-RuntimeHelper
    Restore-Source
}

$reportLines = @()
$reportLines += "FB-041 Callable Group Interactive Validation Report"
$reportLines += "stamp: $Stamp"
$reportLines += "output_dir: $OutputDir"
$reportLines += "runtime_log: $RuntimeLogPath"
$reportLines += ""
$reportLines += "Scenarios:"
foreach ($scenario in $script:ScenarioResults) {
    $status = if ($scenario.passed) { "PASS" } else { "FAIL" }
    $reportLines += "  $status :: $($scenario.name)"
    $reportLines += "    $($scenario.details)"
}
$reportLines += ""
$reportLines += "Captures:"
foreach ($capture in $script:Captures) {
    $reportLines += "  - $($capture.label): $($capture.path)"
}
if ($script:Notes.Count -gt 0) {
    $reportLines += ""
    $reportLines += "Notes:"
    foreach ($note in $script:Notes) {
        $reportLines += "  - $note"
    }
}

Set-Content -LiteralPath $ReportPath -Value $reportLines -Encoding utf8

$manifest = [pscustomobject]@{
    report_path       = $ReportPath
    runtime_log_path  = $RuntimeLogPath
    captures          = $script:Captures
    scenarios         = $script:ScenarioResults
    notes             = $script:Notes
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding utf8

$hasFailures = @($script:ScenarioResults | Where-Object { -not $_.passed }).Count -gt 0
if ($hasFailures) {
    throw "FB-041 interactive validation recorded one or more failed scenarios. See $ReportPath"
}

Write-Output $ReportPath
