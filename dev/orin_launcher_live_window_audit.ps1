param(
    [int]$TimeoutSeconds = 8
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

public static class CodexLiveAuditWin32
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
$OutputDir = Join-Path $RootDir "dev\logs\launcher_live_window_audit\$Stamp"
$ManifestPath = Join-Path $OutputDir "manifest.json"
$SourcePath = Join-Path $env:LOCALAPPDATA "Nexus Desktop AI\saved_actions.json"
$SourceBackupPath = Join-Path $OutputDir "saved_actions.backup.json"
$LauncherPath = Join-Path $RootDir "desktop\orin_desktop_launcher.pyw"
$AuditRuntimeLogPath = Join-Path $OutputDir "audit_runtime.log"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$script:Captures = New-Object System.Collections.Generic.List[object]
$script:AuditStartedAt = Get-Date
$script:AuditRuntimeProcess = $null
$script:BaselinePythonPids = @(
    Get-CimInstance Win32_Process |
        Where-Object { $_.Name -in @("python.exe", "pythonw.exe") } |
        Select-Object -ExpandProperty ProcessId
)

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

function Get-ElementControlTypeNameSafe {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return ""
    }

    try {
        return $Element.Current.ControlType.ProgrammaticName
    } catch {
        return ""
    }
}

function Resolve-LiveDialogRoot {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$ExpectedName = ""
    )

    if ($Dialog) {
        try {
            if (-not $Dialog.Current.IsOffscreen) {
                $rect = $Dialog.Current.BoundingRectangle
                if ($rect.Width -gt 0 -and $rect.Height -gt 0) {
                    return $Dialog
                }
            }
        } catch {
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($ExpectedName)) {
        try {
            $liveDialog = Find-RootWindow -Name $ExpectedName
            if ($liveDialog -and (Test-ElementUsable -Element $liveDialog -RequireEnabled $false)) {
                return $liveDialog
            }
        } catch {
        }
    }

    return $Dialog
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

    $conditions = New-Object System.Collections.Generic.List[System.Windows.Automation.Condition]
    $conditions.Add((New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::NameProperty,
                $Name
            )))

    if ($null -ne $ControlType) {
        $conditions.Add((New-Object System.Windows.Automation.PropertyCondition(
                    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                    $ControlType
                )))
    }

    $condition = if ($conditions.Count -eq 1) {
        $conditions[0]
    } else {
        New-Object System.Windows.Automation.AndCondition($conditions.ToArray())
    }

    return $Root.FindFirst([System.Windows.Automation.TreeScope]::Subtree, $condition)
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
            [CodexLiveAuditWin32]::ShowWindowAsync([IntPtr]$handle, 5) | Out-Null
            [CodexLiveAuditWin32]::SetForegroundWindow([IntPtr]$handle) | Out-Null
        }
    } catch {
    }

    try {
        $Element.SetFocus()
    } catch {
    }
}

function Invoke-Element {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Description
    )

    if (-not $Element) {
        throw "Missing element for $Description."
    }

    Focus-Element -Element $Element

    try {
        $pattern = $Element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $pattern.Invoke()
        return
    } catch {
    }

    try {
        $point = $Element.GetClickablePoint()
        [CodexLiveAuditWin32]::SetCursorPos([int]$point.X, [int]$point.Y) | Out-Null
        Start-Sleep -Milliseconds 40
        [CodexLiveAuditWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
        [CodexLiveAuditWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
        return
    } catch {
    }

    try {
        $rect = $Element.Current.BoundingRectangle
        $x = [int]($rect.Left + ($rect.Width / 2))
        $y = [int]($rect.Top + ($rect.Height / 2))
        [CodexLiveAuditWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds 40
        [CodexLiveAuditWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
        [CodexLiveAuditWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
        return
    } catch {
    }

    throw "Could not invoke $Description."
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
    [CodexLiveAuditWin32]::keybd_event($Key, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 35
    [CodexLiveAuditWin32]::keybd_event($Key, 0, 2, [UIntPtr]::Zero)
}

function Send-OverlayHotkey {
    try {
        [System.Windows.Forms.SendKeys]::SendWait("^%{HOME}")
    } catch {
        [CodexLiveAuditWin32]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero)
        [CodexLiveAuditWin32]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
        [CodexLiveAuditWin32]::keybd_event(0x24, 0, 0, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 40
        [CodexLiveAuditWin32]::keybd_event(0x24, 0, 2, [UIntPtr]::Zero)
        [CodexLiveAuditWin32]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
        [CodexLiveAuditWin32]::keybd_event(0x11, 0, 2, [UIntPtr]::Zero)
    }
}

function Get-RuntimeLogLineCount {
    if (-not (Test-Path -LiteralPath $AuditRuntimeLogPath)) {
        return 0
    }
    return @(Get-Content -LiteralPath $AuditRuntimeLogPath).Count
}

function Wait-ForRuntimeMarker {
    param(
        [string]$Marker,
        [int]$StartLine = 0,
        [int]$TimeoutSeconds = 12
    )

    return (Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "runtime marker $Marker" -Condition {
            if (-not (Test-Path -LiteralPath $AuditRuntimeLogPath)) {
                return $null
            }

            $lines = @(Get-Content -LiteralPath $AuditRuntimeLogPath)
            if ($lines.Count -le $StartLine) {
                return $null
            }

            $newLines = @($lines | Select-Object -Skip $StartLine)
            foreach ($line in $newLines) {
                if ($line -like "*$Marker*") {
                    return $line
                }
            }

            return $null
        })
}

function Stop-AuditRuntimeHelper {
    if ($script:AuditRuntimeProcess) {
        try {
            Stop-Process -Id $script:AuditRuntimeProcess.Id -Force -ErrorAction Stop
        } catch {
        }
        $script:AuditRuntimeProcess = $null
        Start-Sleep -Milliseconds 350
    }
}

function Start-AuditRuntimeHelper {
    $python = (Get-Command python).Source
    if (-not $python) {
        throw "Could not resolve python executable for the audit runtime helper."
    }

    $baselineLines = Get-RuntimeLogLineCount
    $argString = "dev\\orin_saved_action_authoring_interactive_runtime.py --runtime-log `"$AuditRuntimeLogPath`" --auto-open-overlay"
    $previousOverlayTrace = $env:NEXUS_OVERLAY_TRACE
    $env:NEXUS_OVERLAY_TRACE = "1"
    try {
        $process = Start-Process -FilePath $python -ArgumentList $argString -WorkingDirectory $RootDir -PassThru -WindowStyle Hidden
    } finally {
        $env:NEXUS_OVERLAY_TRACE = $previousOverlayTrace
    }

    $script:AuditRuntimeProcess = $process

    Wait-Until -TimeoutSeconds 20 -Description "audit runtime log creation" -Condition {
        Test-Path -LiteralPath $AuditRuntimeLogPath
    } | Out-Null

    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|STARTUP_READY" -StartLine $baselineLines -TimeoutSeconds 25 | Out-Null
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|DESKTOP_ATTACH_RESULT|success=true" -StartLine $baselineLines -TimeoutSeconds 25 | Out-Null

    return [pscustomobject]@{
        StartLine = [Math]::Max($baselineLines, ((Get-RuntimeLogLineCount) - 50))
        Process   = $process
    }
}

function Get-OverlayWindow {
    $overlay = Find-RootWindow -AutomationId "QApplication.commandOverlayWindow" -ClassName "CommandOverlayPanel"
    if ($overlay) {
        return $overlay
    }

    $input = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine"
    if ($input) {
        return [System.Windows.Automation.AutomationElement]::RootElement
    }

    return $null
}

function Wait-ForOverlay {
    return (Wait-Until -Description "overlay window" -Condition {
            $overlay = Get-OverlayWindow
            if ($overlay -and (Test-ElementUsable -Element $overlay -RequireEnabled $false)) {
                return $overlay
            }
            return $null
        })
}

function Open-Overlay {
    Stop-AuditRuntimeHelper
    $runtime = Start-AuditRuntimeHelper
    $startLine = [int]$runtime.StartLine

    try {
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPENED" -StartLine $startLine -TimeoutSeconds 6 | Out-Null
    } catch {
    }

    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -StartLine $startLine -TimeoutSeconds 8 | Out-Null
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

function Wait-ForDialog {
    param([string]$Name)

    $automationIds = switch ($Name) {
        "Create Custom Task" { @("QApplication.savedActionCreateDialog") }
        "Edit Custom Task" { @("QApplication.savedActionCreateDialog") }
        "Available Groups" { @("QApplication.taskGroupAssignmentDialog") }
        "Create Custom Group" { @("QApplication.callableGroupCreateDialog") }
        "Manage Custom Tasks" { @("QApplication.savedActionCreatedTasksDialog") }
        "Manage Custom Groups" { @("QApplication.savedActionCreatedGroupsDialog") }
        default { @() }
    }

    return (Wait-Until -Description $Name -Condition {
        $dialog = Find-RootWindow -Name $Name
        if ($dialog -and (Test-ElementUsable -Element $dialog -RequireEnabled $false)) {
            return $dialog
        }
        foreach ($automationId in $automationIds) {
            $candidate = Find-ElementByAutomationIdDirect -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId $automationId
            if ($candidate -and (Test-ElementUsable -Element $candidate -RequireEnabled $false)) {
                return $candidate
            }
        }
        return $null
    })
}

function Close-WindowByEsc {
    param([System.Windows.Automation.AutomationElement]$Window)
    Focus-Element -Element $Window
    Send-VirtualKey -Key 0x1B
    Start-Sleep -Milliseconds 200
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

function Launch-Desktop {
    Stop-LaunchedDesktopProcesses

    if (-not (Test-Path -LiteralPath $LauncherPath)) {
        throw "Launcher not found: $LauncherPath"
    }

    $python = (Get-Command python).Source
    if (-not $python) {
        throw "Could not resolve the python executable."
    }

    $argString = '"' + $LauncherPath + '"'
    $launchStartedAt = Get-Date
    $script:LauncherProcess = Start-Process -FilePath $python -ArgumentList $argString -WorkingDirectory $RootDir -WindowStyle Hidden -PassThru

    Wait-Until -Description "fresh launcher runtime log" -TimeoutSeconds 20 -Condition {
        $latest = Get-ChildItem (Join-Path $RootDir "logs") -Filter "Runtime_*.txt" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -ge $launchStartedAt.AddSeconds(-1) } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($latest) {
            return $latest
        }
        return $null
    } | Out-Null

    Wait-Until -Description "launcher runtime startup ready" -TimeoutSeconds 25 -Condition {
        $latest = Get-ChildItem (Join-Path $RootDir "logs") -Filter "Runtime_*.txt" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -ge $launchStartedAt.AddSeconds(-1) } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if (-not $latest) {
            return $null
        }

        $content = Get-Content -LiteralPath $latest.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -like "*RENDERER_MAIN|STARTUP_READY*") {
            return $latest
        }

        return $null
    } | Out-Null

    Start-Sleep -Milliseconds 750
}

function Get-OverlayInput {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    return Find-ElementByAutomationIdDirect -Root $Overlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine"
}

function Resolve-OverlayInput {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay
    )

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

function Get-OverlayButton {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [string[]]$AutomationIds
    )

    foreach ($automationId in $AutomationIds) {
        $element = Find-ElementByAutomationIdDirect -Root $Overlay -AutomationId $automationId
        if ($element) {
            return $element
        }
    }

    return $null
}

function Get-FirstButtonByName {
    param(
        [System.Windows.Automation.AutomationElement]$Root,
        [string]$Name
    )

    return Find-FirstElementByName -Root $Root -Name $Name -ControlType ([System.Windows.Automation.ControlType]::Button)
}

function Get-FirstEditButton {
    param(
        [System.Windows.Automation.AutomationElement]$Root
    )

    $buttons = $Root.FindAll([System.Windows.Automation.TreeScope]::Subtree, (New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                [System.Windows.Automation.ControlType]::Button
            )))

    for ($i = 0; $i -lt $buttons.Count; $i++) {
        $button = $buttons.Item($i)
        try {
            if ($button.Current.Name -eq "Edit" -and -not $button.Current.IsOffscreen) {
                return $button
            }
        } catch {
        }
    }

    return $null
}

function Backup-Source {
    if (Test-Path -LiteralPath $SourcePath) {
        Copy-Item -LiteralPath $SourcePath -Destination $SourceBackupPath -Force
    }
}

function Restore-Source {
    if (Test-Path -LiteralPath $SourceBackupPath) {
        Copy-Item -LiteralPath $SourceBackupPath -Destination $SourcePath -Force
    }
}

function Write-InvalidSource {
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($SourcePath, "{ invalid json", $encoding)
}

function Seed-AuditSource {
    $payload = [ordered]@{
        schema_version = 1
        actions        = @(
            [ordered]@{
                id              = "open_notepad_task"
                title           = "Open Weekly Reports"
                target_kind     = "folder"
                target          = "C:\Windows"
                aliases         = @("weekly reports")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "weekly_reports_explorer"
                title           = "Weekly Reports Explorer"
                target_kind     = "app"
                target          = "explorer.exe"
                aliases         = @("weekly reports")
                invocation_mode = "aliases_only"
                trigger_mode    = "launch"
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
                id              = "workspace_docs_folder"
                title           = "Open Workspace Docs"
                target_kind     = "folder"
                target          = "C:\Nexus Desktop AI\Docs"
                aliases         = @("workspace docs")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_readme_task"
                title           = "Open Root README"
                target_kind     = "file"
                target          = "C:\Nexus Desktop AI\README.md"
                aliases         = @("root readme")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_launcher_source"
                title           = "Open Desktop Launcher"
                target_kind     = "file"
                target          = "C:\Nexus Desktop AI\desktop\orin_desktop_launcher.pyw"
                aliases         = @("desktop launcher")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_issue_board"
                title           = "Open Screenshot Folder"
                target_kind     = "folder"
                target          = "C:\Users\anden\OneDrive\Pictures\Screenshots"
                aliases         = @("screenshot folder")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_saved_source"
                title           = "Open Saved Action Source Module"
                target_kind     = "file"
                target          = "C:\Nexus Desktop AI\desktop\saved_action_source.py"
                aliases         = @("saved action source")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            }
        )
        groups         = @(
            [ordered]@{
                id                = "workspace_tools"
                title             = "Workspace Tools"
                aliases           = @("workspace tools")
                member_action_ids = @("open_saved_actions_folder", "open_notepad_task")
            },
            [ordered]@{
                id                = "notes_suite"
                title             = "Notes Suite"
                aliases           = @("notes suite")
                member_action_ids = @("open_notes_task")
            },
            [ordered]@{
                id                = "docs_hub"
                title             = "Docs Hub"
                aliases           = @("docs hub")
                member_action_ids = @("workspace_docs_folder", "open_readme_task")
            },
            [ordered]@{
                id                = "launcher_tools"
                title             = "Launcher Tools"
                aliases           = @("launcher tools")
                member_action_ids = @("open_launcher_source", "open_saved_source")
            },
            [ordered]@{
                id                = "planning_board"
                title             = "Planning Board"
                aliases           = @("planning board")
                member_action_ids = @("open_issue_board", "weekly_reports_explorer")
            },
            [ordered]@{
                id                = "review_pack"
                title             = "Review Pack"
                aliases           = @("review pack")
                member_action_ids = @("open_readme_task", "open_notes_task", "open_saved_source")
            },
            [ordered]@{
                id                = "workspace_launchers"
                title             = "Workspace Launchers"
                aliases           = @("workspace launchers")
                member_action_ids = @("open_notepad_task", "workspace_docs_folder", "open_issue_board")
            }
        )
    }

    $json = ($payload | ConvertTo-Json -Depth 8) + "`n"
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($SourcePath, $json, $encoding)
}

function Stop-LaunchedDesktopProcesses {
    $newPython = Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @("python.exe", "pythonw.exe") -and
            ($script:BaselinePythonPids -notcontains $_.ProcessId) -and
            (
                $_.CommandLine -like "*orin_desktop_launcher.pyw*" -or
                $_.CommandLine -like "*orin_desktop_main.py*"
            )
        }

    foreach ($process in $newPython) {
        try {
            Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
        } catch {
        }
    }
}

function Get-CreateDialogInput {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$LeafId
    )

    $liveDialog = Resolve-LiveDialogRoot -Dialog $Dialog -ExpectedName "Create Custom Task"
    if (-not $liveDialog) {
        return $null
    }

    $ids = @(
        "QApplication.savedActionCreateDialog.savedActionCreateShell.savedActionCreateContent.$LeafId",
        "QApplication.savedActionCreateDialog.$LeafId"
    )

    foreach ($id in $ids) {
        $element = Find-ElementByAutomationIdDirect -Root $liveDialog -AutomationId $id
        if ($element -and (Test-ElementUsable -Element $element)) {
            return $element
        }
    }

    $visibleInputs = @()
    foreach ($candidate in (Get-AllDescendants -Element $liveDialog)) {
        try {
            if ((Get-ElementControlTypeNameSafe -Element $candidate) -ne [System.Windows.Automation.ControlType]::Edit.ProgrammaticName) {
                continue
            }
            if (-not (Test-ElementUsable -Element $candidate)) {
                continue
            }

            $rect = $candidate.Current.BoundingRectangle
            $visibleInputs += [pscustomobject]@{
                element = $candidate
                top     = [double]$rect.Top
                left    = [double]$rect.Left
            }
        } catch {
        }
    }

    $orderedInputs = @(
        $visibleInputs |
            Sort-Object -Property @{ Expression = "top"; Ascending = $true }, @{ Expression = "left"; Ascending = $true }
    )

    $desiredIndex = switch ($LeafId) {
        "savedActionCreateTitleInput" { 0 }
        "savedActionCreateAliasesInput" { 1 }
        "savedActionCreateTargetInput" { 2 }
        default { -1 }
    }

    if ($desiredIndex -ge 0 -and $orderedInputs.Count -gt $desiredIndex) {
        return $orderedInputs[$desiredIndex].element
    }

    return $null
}

function Get-TaskGroupAssignmentButton {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog,
        [string]$LeafId
    )

    $ids = @(
        "QApplication.taskGroupAssignmentDialog.taskGroupAssignmentShell.taskGroupAssignmentContent.$LeafId",
        "QApplication.taskGroupAssignmentDialog.$LeafId"
    )

    foreach ($id in $ids) {
        $element = Find-ElementByAutomationIdDirect -Root $Dialog -AutomationId $id
        if ($element) {
            return $element
        }
    }

    return $null
}

try {
    Backup-Source
    Seed-AuditSource
    Launch-Desktop

    $overlay = Open-Overlay
    $overlayInput = Resolve-OverlayInput -Overlay $overlay
    Capture-ElementScreenshot -Element $overlay -Label "overlay_entry" | Out-Null

    Set-ElementValue -Element $overlayInput -Value "weekly reports" -Description "overlay ambiguity text"
    Send-VirtualKey -Key 0x0D
    Start-Sleep -Milliseconds 350
    Capture-ElementScreenshot -Element $overlay -Label "overlay_ambiguity" | Out-Null
    Close-WindowByEsc -Window $overlay
    Start-Sleep -Milliseconds 220

    $overlay = Open-Overlay
    $overlayInput = Resolve-OverlayInput -Overlay $overlay
    Set-ElementValue -Element $overlayInput -Value "notes task" -Description "overlay confirm text"
    Send-VirtualKey -Key 0x0D
    Start-Sleep -Milliseconds 350
    Capture-ElementScreenshot -Element $overlay -Label "overlay_confirm" | Out-Null
    Close-WindowByEsc -Window $overlay
    Start-Sleep -Milliseconds 220

    $overlay = Open-Overlay

    $createButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreateButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton"
    )
    Invoke-Element -Element $createButton -Description "Create Custom Task button"
    $createDialog = Wait-ForDialog -Name "Create Custom Task"
    Set-ElementValue -Element (Get-CreateDialogInput -Dialog $createDialog -LeafId "savedActionCreateTitleInput") -Value "Bad App" -Description "create title"
    Set-ElementValue -Element (Get-CreateDialogInput -Dialog $createDialog -LeafId "savedActionCreateAliasesInput") -Value "bad app alias" -Description "create aliases"
    Set-ElementValue -Element (Get-CreateDialogInput -Dialog $createDialog -LeafId "savedActionCreateTargetInput") -Value "notepad.exe --help" -Description "create target"
    $createSubmit = Get-FirstButtonByName -Root $createDialog -Name "Create"
    Invoke-Element -Element $createSubmit -Description "Create submit"
    Start-Sleep -Milliseconds 450
    Capture-ElementScreenshot -Element $createDialog -Label "create_custom_task_error" | Out-Null

    $assignGroup = Get-FirstButtonByName -Root $createDialog -Name "Assign Group..."
    Invoke-Element -Element $assignGroup -Description "Assign Group"
    $assignmentDialog = Wait-ForDialog -Name "Available Groups"
    Capture-ElementScreenshot -Element $assignmentDialog -Label "available_groups" | Out-Null

    $assignmentCreate = Get-TaskGroupAssignmentButton -Dialog $assignmentDialog -LeafId "taskGroupAssignmentCreateButton"
    if (-not $assignmentCreate) {
        $assignmentCreate = Get-FirstButtonByName -Root $assignmentDialog -Name "Create New Group..."
    }
    if (-not $assignmentCreate) {
        $assignmentCreate = Get-FirstButtonByName -Root $assignmentDialog -Name "Create New Group"
    }
    Invoke-Element -Element $assignmentCreate -Description "Available Groups create"
    $inlineCreateGroupDialog = Wait-ForDialog -Name "Create Custom Group"
    Capture-ElementScreenshot -Element $inlineCreateGroupDialog -Label "create_custom_group" | Out-Null
    Close-WindowByEsc -Window $inlineCreateGroupDialog
    Start-Sleep -Milliseconds 220
    Close-WindowByEsc -Window $assignmentDialog
    Start-Sleep -Milliseconds 220
    Close-WindowByEsc -Window $createDialog
    Start-Sleep -Milliseconds 250

    $overlay = Open-Overlay

    $manageTasksButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreatedTasksButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton"
    )
    Invoke-Element -Element $manageTasksButton -Description "Manage Custom Tasks button"
    $manageTasksDialog = Wait-ForDialog -Name "Manage Custom Tasks"
    Capture-ElementScreenshot -Element $manageTasksDialog -Label "manage_custom_tasks" | Out-Null
    $editButton = Wait-Until -Description "first Edit button" -Condition {
        $button = Get-FirstEditButton -Root $manageTasksDialog
        if ($button -and (Test-ElementUsable -Element $button)) { return $button }
        return $null
    }
    Invoke-Element -Element $editButton -Description "first Edit button"
    $editDialog = Wait-ForDialog -Name "Edit Custom Task"
    Capture-ElementScreenshot -Element $editDialog -Label "edit_custom_task" | Out-Null
    Close-WindowByEsc -Window $editDialog
    Start-Sleep -Milliseconds 220
    Close-WindowByEsc -Window $manageTasksDialog
    Start-Sleep -Milliseconds 220

    $overlay = Open-Overlay

    $createGroupButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreateGroupButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateGroupButton"
    )
    Invoke-Element -Element $createGroupButton -Description "Create Custom Group button"
    $directCreateGroupDialog = Wait-ForDialog -Name "Create Custom Group"
    Capture-ElementScreenshot -Element $directCreateGroupDialog -Label "create_custom_group_direct" | Out-Null
    Close-WindowByEsc -Window $directCreateGroupDialog
    Start-Sleep -Milliseconds 220

    $overlay = Open-Overlay
    $manageGroupsButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreatedGroupsButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedGroupsButton"
    )
    Invoke-Element -Element $manageGroupsButton -Description "Manage Custom Groups button"
    $manageGroupsDialog = Wait-ForDialog -Name "Manage Custom Groups"
    Capture-ElementScreenshot -Element $manageGroupsDialog -Label "manage_custom_groups" | Out-Null
    Close-WindowByEsc -Window $manageGroupsDialog
    Start-Sleep -Milliseconds 220

    Write-InvalidSource
    Start-Sleep -Milliseconds 250

    $overlay = Open-Overlay
    $manageTasksButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreatedTasksButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton"
    )
    $manageGroupsButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreatedGroupsButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedGroupsButton"
    )

    Invoke-Element -Element $manageTasksButton -Description "Manage Custom Tasks button invalid source"
    $invalidTasksDialog = Wait-ForDialog -Name "Manage Custom Tasks"
    Capture-ElementScreenshot -Element $invalidTasksDialog -Label "manage_custom_tasks_invalid_source" | Out-Null
    Close-WindowByEsc -Window $invalidTasksDialog
    Start-Sleep -Milliseconds 220

    Invoke-Element -Element $manageGroupsButton -Description "Manage Custom Groups button invalid source"
    $invalidGroupsDialog = Wait-ForDialog -Name "Manage Custom Groups"
    Capture-ElementScreenshot -Element $invalidGroupsDialog -Label "manage_custom_groups_invalid_source" | Out-Null
    Close-WindowByEsc -Window $invalidGroupsDialog

    Restore-Source

    $manifest = [pscustomobject]@{
        capture_dir = $OutputDir
        captures    = $script:Captures
    }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ManifestPath -Encoding utf8

    [pscustomobject]@{
        capture_dir = $OutputDir
        manifest    = $ManifestPath
        captures    = $script:Captures
    } | ConvertTo-Json -Depth 6
}
finally {
    Stop-AuditRuntimeHelper
    Restore-Source
    Stop-LaunchedDesktopProcesses
}
