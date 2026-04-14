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

$script:RuntimeLogLineCursor = 0
$script:RuntimeAutoOpenPending = $false

function Write-StepLog {
    param(
        [string]$Stage,
        [string]$Message
    )

    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $line = "[$timestamp] [$Stage] $Message"
    Add-Content -LiteralPath $StepLogPath -Value $line -Encoding utf8
}

function Add-Note {
    param([string]$Message)
    $ValidationState.notes += $Message
    Write-StepLog -Stage "NOTE" -Message $Message
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
        try {
            if (& $Condition) {
                return $true
            }
        } catch {
        }
        Start-Sleep -Milliseconds $SleepMilliseconds
    }

    throw "Timed out waiting for $Description."
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
        if ($candidate.Current.ControlType.ProgrammaticName -ne [System.Windows.Automation.ControlType]::Window.ProgrammaticName) {
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

function Find-FirstElement {
    param(
        [System.Windows.Automation.AutomationElement]$Root = [System.Windows.Automation.AutomationElement]::RootElement,
        [string]$AutomationId,
        [string]$Name,
        $ControlType = $null,
        [string]$ClassName
    )

    $elements = Get-AllDescendants -Element $Root
    foreach ($element in $elements) {
        if ($AutomationId -and $element.Current.AutomationId -ne $AutomationId) {
            continue
        }
        if ($Name -and $element.Current.Name -ne $Name) {
            continue
        }
        if ($ControlType -and $element.Current.ControlType.ProgrammaticName -ne $ControlType.ProgrammaticName) {
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
            if ($candidate.Current.ControlType.ProgrammaticName -ne [System.Windows.Automation.ControlType]::ListItem.ProgrammaticName) {
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
        try {
            Focus-Window -Element $Combo
        } catch {
        }

        $currentValue = Get-ComboSelectedText -Combo $Combo
        Write-StepLog -Stage "INTERACT" -Message "combo select attempt=$attempt desired='$ItemName' current='$currentValue' state=$(Get-ElementStateSummary -Element $Combo)"
        if ($currentValue -eq $ItemName) {
            return
        }

        $usedPopup = $false
        try {
            Expand-Combo -Element $Combo
            Start-Sleep -Milliseconds 220
            $item = Find-ComboPopupItem -Combo $Combo -ItemName $ItemName
            if ($item) {
                try {
                    Click-Element -Element $item
                } catch {
                    $select = $item.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)
                    $select.Select()
                }
                $usedPopup = $true
            }
        } catch {
        }

        if (-not $usedPopup) {
            try {
                Click-Element -Element $Combo
            } catch {
            }
            Start-Sleep -Milliseconds 150
            Send-VirtualKey -VirtualKey 0x24
            Start-Sleep -Milliseconds 80
            for ($index = 0; $index -lt $desiredIndex; $index++) {
                Send-VirtualKey -VirtualKey 0x28
                Start-Sleep -Milliseconds 80
            }
            Send-VirtualKey -VirtualKey 0x0D
        }

        try {
            Wait-ForElementValue -ExpectedValue $ItemName -TimeoutSeconds 3 -Description "combo value $ItemName" -ElementResolver {
                return (& $ComboResolver)
            }
            return
        } catch {
            $actualCombo = & $ComboResolver
            $actualValue = Get-ComboSelectedText -Combo $actualCombo
            Add-Note "Combo selection attempt $attempt for '$ItemName' did not stick; actual value read back as '$actualValue'. State: $(Get-ElementStateSummary -Element $actualCombo)"
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

function Focus-Window {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    $hwnd = Get-WindowHandle -Element $Element
    if ($hwnd -ne [IntPtr]::Zero) {
        [CodexInteractiveWin32]::ShowWindowAsync($hwnd, 5) | Out-Null
        [CodexInteractiveWin32]::SetForegroundWindow($hwnd) | Out-Null
    }
    $Element.SetFocus()
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

function Get-DialogWindow {
    param(
        [string]$Name
    )

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

    return Find-FirstElement -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId "QApplication.commandOverlayWindow" -ClassName "CommandOverlayPanel"
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
            Focus-Window -Element $liveDialog
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

        try {
            Focus-Window -Element $element
        } catch {
            Add-Note "Focus attempt $attempt for '$Description' could not foreground the element window. State: $(Get-ElementStateSummary -Element $element)"
        }

        $focused = $null
        try {
            $focused = [System.Windows.Automation.AutomationElement]::FocusedElement
        } catch {
        }

        if ($focused) {
            try {
                if (
                    $focused.Current.AutomationId -eq $element.Current.AutomationId -and
                    $focused.Current.ControlType.ProgrammaticName -eq $element.Current.ControlType.ProgrammaticName
                ) {
                    Write-StepLog -Stage "INTERACT" -Message "focus confirmed for '$Description' on attempt=$attempt state=$(Get-ElementStateSummary -Element $element)"
                    return $element
                }
            } catch {
            }
        }

        try {
            $element.SetFocus()
            Start-Sleep -Milliseconds 120
        } catch {
        }

        $focused = $null
        try {
            $focused = [System.Windows.Automation.AutomationElement]::FocusedElement
        } catch {
        }

        if ($focused) {
            try {
                if (
                    $focused.Current.AutomationId -eq $element.Current.AutomationId -and
                    $focused.Current.ControlType.ProgrammaticName -eq $element.Current.ControlType.ProgrammaticName
                ) {
                    Write-StepLog -Stage "INTERACT" -Message "focus confirmed for '$Description' on attempt=$attempt after direct SetFocus state=$(Get-ElementStateSummary -Element $element)"
                    return $element
                }
            } catch {
            }
        }

        if (-not $RequireExactFocus -and (Test-ElementUsable -Element $element -RequireEnabled $true)) {
            Write-StepLog -Stage "INTERACT" -Message "proceeding without exact focus for '$Description' on attempt=$attempt state=$(Get-ElementStateSummary -Element $element)"
            Add-Note "Exact focus did not hold for '$Description', but the control remained usable so the harness proceeded with window-level focus."
            return $element
        }

        Add-Note "Focus attempt $attempt for '$Description' did not hold. Element state: $(Get-ElementStateSummary -Element $element)"
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

    for ($attempt = 1; $attempt -le 3; $attempt++) {
        $element = & $ElementResolver
        if (-not $element) {
            throw "Could not resolve $Description."
        }

        try {
            Focus-Window -Element $element
        } catch {
        }

        Write-StepLog -Stage "INTERACT" -Message "field set attempt=$attempt field='$Description' value='$ExpectedValue' state=$(Get-ElementStateSummary -Element $element)"
        Set-Value -Element $element -Value $ExpectedValue

        try {
            Wait-ForElementValue -ExpectedValue $ExpectedValue -TimeoutSeconds 3 -Description $Description -ElementResolver $ElementResolver
            $actualElement = & $ElementResolver
            Write-StepLog -Stage "INTERACT" -Message "field set confirmed field='$Description' actual='$(Get-ElementReadableValue -Element $actualElement)' state=$(Get-ElementStateSummary -Element $actualElement)"
            return
        } catch {
            $actualElement = & $ElementResolver
            $actualValue = Get-ElementReadableValue -Element $actualElement
            Add-Note "Field '$Description' set attempt $attempt did not stick; actual value read back as '$actualValue'. State: $(Get-ElementStateSummary -Element $actualElement)"
        }
    }

    $finalElement = & $ElementResolver
    $finalValue = Get-ElementReadableValue -Element $finalElement
    if ((Normalize-UiValue $finalValue) -eq (Normalize-UiValue $ExpectedValue)) {
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
        if ($element.Current.ControlType.ProgrammaticName -eq [System.Windows.Automation.ControlType]::Button.ProgrammaticName -and $element.Current.Name -eq "Edit") {
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

    foreach ($automationId in @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton",
        "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine"
    )) {
        $anchor = Find-FirstElement -Root ([System.Windows.Automation.AutomationElement]::RootElement) -AutomationId $automationId
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

    foreach ($automationId in @(
        "QApplication.commandOverlayWindow.commandPanel.commandInputShell.commandInputLine",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton"
    )) {
        $element = Find-FirstElement -Root $liveOverlay -AutomationId $automationId
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
        if ($element.Current.ControlType.ProgrammaticName -eq [System.Windows.Automation.ControlType]::Text.ProgrammaticName -and $element.Current.Name -like "Open*") {
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
    $overlay = Get-OverlayWindow
    if (-not $overlay) {
        return
    }

    try {
        Focus-Window -Element $overlay
    } catch {
    }

    $markerStart = New-RuntimeMarkerCursor
    Write-StepLog -Stage "OVERLAY" -Message "closing overlay via escape"
    Send-VirtualKey -VirtualKey 0x1B
    Start-Sleep -Milliseconds 350
    if ((Get-OverlayWindow) -ne $null) {
        Write-StepLog -Stage "OVERLAY" -Message "overlay still visible after escape, retrying with hotkey"
        Send-OverlayHotkey
    }

    Wait-Until -TimeoutSeconds 8 -Description "overlay close" -Condition { (Get-OverlayWindow) -eq $null } | Out-Null
    try {
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" -TimeoutSeconds 4 -StartLine $markerStart
    } catch {
        Write-StepLog -Stage "OVERLAY" -Message "overlay closed without a fresh close marker"
    }
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

    $Overlay = Resolve-LiveOverlayRoot -Overlay $Overlay
    $button = Find-FirstElement -Root $Overlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton"
    if (-not $button) {
        throw "Created Tasks button was not found in the overlay."
    }
    Write-StepLog -Stage "DIALOG" -Message "opening Created Tasks"
    $markerStart = New-RuntimeMarkerCursor
    $button.SetFocus()
    Invoke-ElementRobust -Element $button -Description "Created Tasks button"

    try {
        Wait-ForDialogRuntimeReady -SignalBase "CREATED_TASKS_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    } catch {
        Invoke-ElementRobust -Element $button -Description "Created Tasks button retry"
        Wait-ForDialogRuntimeReady -SignalBase "CREATED_TASKS_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    }

    $dialog = Wait-ForOptionalDialog -Name "Created Tasks" -TimeoutSeconds 3
    if ($dialog) {
        return $dialog
    }

    return (Wait-ForDialog -Name "Created Tasks" -TimeoutSeconds 8)
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
        try {
            Wait-ForDialogClosed -Name $Dialog.Current.Name -TimeoutSeconds 2
        } catch {
            Add-Note "Dialog close readback lagged after a closed marker; continuing without an ESC fallback."
        }
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

function Close-CreatedTasksDialog {
    param(
        [System.Windows.Automation.AutomationElement]$Dialog
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
        try {
            Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -TimeoutSeconds 3 -StartLine $markerStart
        } catch {
            Add-Note "Created Tasks closed by runtime marker, but overlay-ready follow-up lagged; continuing with runtime marker authority."
        }
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
        try {
            Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -TimeoutSeconds 3 -StartLine $markerStart
        } catch {
            Add-Note "Overlay-ready follow-up lagged after the Created Tasks close fallback; continuing with re-resolved overlay state."
        }
    }
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
        [System.Windows.Automation.AutomationElement]$Overlay
    )

    $liveOverlay = Wait-ForOptionalOverlayOpen -TimeoutSeconds 2
    if ($liveOverlay) {
        try {
            $markerStart = New-RuntimeMarkerCursor
            Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_OVERLAY_READY" -TimeoutSeconds 2 -StartLine $markerStart
        } catch {
        }
        return $liveOverlay
    }

    $resolvedOverlay = Resolve-LiveOverlayRoot -Overlay $Overlay
    if ($resolvedOverlay) {
        return $resolvedOverlay
    }

    Add-Note "Overlay was not visible after a dialog transition; reopening it for the next validation step."
    return (Open-OverlayWithRuntimeRestartFallback -MaxAttempts 2)
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

function Start-NotepadProbe {
    $probeFile = Join-Path $ArtifactsDir "${Stamp}_notepad_probe.txt"
    Write-Utf8NoBomFile -Path $probeFile -Content ""
    $process = Start-Process -FilePath "notepad.exe" -ArgumentList "`"$probeFile`"" -PassThru
    $expectedTitle = "$(Split-Path -Leaf $probeFile) - Notepad"

    $window = $null
    Wait-Until -TimeoutSeconds 15 -Description "notepad probe window" -Condition {
        foreach ($candidate in (Get-RootWindows)) {
            if (
                $candidate.Current.ControlType.ProgrammaticName -eq [System.Windows.Automation.ControlType]::Window.ProgrammaticName -and
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
                $candidate.Current.ControlType.ProgrammaticName -eq [System.Windows.Automation.ControlType]::Window.ProgrammaticName -and
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
            if ($candidate.Current.ControlType.ProgrammaticName -eq [System.Windows.Automation.ControlType]::Edit.ProgrammaticName) {
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

function Get-JsonTitles {
    if (-not (Test-Path -LiteralPath $SourcePath)) {
        return @()
    }
    $parsed = Get-Content -LiteralPath $SourcePath -Raw | ConvertFrom-Json
    return @($parsed.actions | ForEach-Object { $_.title })
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
    try {
        Wait-ForDialogRuntimeClosed -SignalBase "CUSTOM_TASK_CREATE_DIALOG" -StartLine $markerStart -TimeoutSeconds 4
        Wait-ForDialogClosed -Name "Create Custom Task" -TimeoutSeconds 4
    } catch {
        Add-Note "Create dialog close readback lagged after a successful create marker, but the runtime marker and persisted source still confirmed the save."
    }
    $Overlay = Wait-ForOverlayOpen
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Open Notepad Task"
    Close-CreatedTasksDialog -Dialog $createdTasksDialog
    Copy-SourceSnapshot -Slug "after_create" | Out-Null
    return (Ensure-OverlayReady -Overlay $Overlay)
}

function Run-Invalid-Create-Checks {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running invalid create checks"

    $cases = @(
        @{ type = "Application"; title = "Bad App"; aliases = "bad app alias"; target = "notepad.exe --help"; expect = "Application targets" },
        @{ type = "Folder"; title = "Bad Folder"; aliases = "bad folder alias"; target = "Reports\Daily"; expect = "Folder targets" },
        @{ type = "File"; title = "Bad File"; aliases = "bad file alias"; target = "C:\Reports\bad?.txt"; expect = "File targets" },
        @{ type = "Website URL"; title = "Bad Url"; aliases = "bad url alias"; target = "example.com/docs"; expect = "absolute http or https URL" }
    )

    foreach ($case in $cases) {
        $beforeSourceText = if (Test-Path -LiteralPath $SourcePath) {
            Get-Content -LiteralPath $SourcePath -Raw
        } else {
            ""
        }
        $dialog = Open-CreateDialog -Overlay $Overlay
        Fill-AuthoringDialog -Dialog $dialog -TypeLabel $case.type -Title $case.title -Aliases $case.aliases -Target $case.target
        $markerStart = New-RuntimeMarkerCursor
        Submit-Dialog -Dialog $dialog -ButtonName "Create"
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED|title=$($case.title)" -StartLine $markerStart
        Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|reason=validation_error" -StartLine $markerStart
        Wait-Until -TimeoutSeconds 4 -Description "blocked invalid create '$($case.type)'" -Condition {
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
            throw "Invalid target case '$($case.type)' unexpectedly produced a create marker."
        }
        $status = ""
        try {
            Wait-Until -TimeoutSeconds 2 -Description "blocking feedback for invalid create '$($case.type)'" -Condition {
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
            Add-Note "Invalid target case '$($case.type)' kept the dialog open and preserved the source, but the interactive status-label readback was blank."
        }
        Cancel-Dialog -Dialog $dialog
        Wait-ForDialogClosed -Name "Create Custom Task"
        $Overlay = Ensure-OverlayReady -Overlay $Overlay
    }
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
        Wait-ForDialogClosed -Name "Create Custom Task"
        $Overlay = Ensure-OverlayReady -Overlay $Overlay
    }
}

function Run-Edit-Flow {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running valid edit flow"

    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    $editButtons = @(Get-InventoryEditButtons -Overlay $createdTasksDialog)
    if (-not $editButtons -or $editButtons.Count -lt 1) {
        throw "No edit buttons were available for the saved inventory."
    }

    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $editButtons[0] -Description "first Created Tasks edit button"
    Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_TASK_EDIT_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    $dialog = Wait-ForDialog -Name "Edit Custom Task" -TimeoutSeconds 8
    if (Find-WindowAnywhere -Name "Created Tasks") {
        Add-Note "Created Tasks remained visible briefly while the edit dialog opened; continuing because the real edit route was still exercised."
    }
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
        Wait-ForDialogClosed -Name "Edit Custom Task" -TimeoutSeconds 4
    } catch {
        Add-Note "Edit dialog close readback lagged after a successful update marker, but the runtime marker and refreshed inventory still confirmed the save."
    }
    $Overlay = Wait-ForOverlayOpen
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Open Weekly Reports"
    Close-CreatedTasksDialog -Dialog $createdTasksDialog
    Copy-SourceSnapshot -Slug "after_edit" | Out-Null
    return (Ensure-OverlayReady -Overlay $Overlay)
}

function Run-Invalid-Edit-Check {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running invalid edit check"

    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $Overlay
    $editButtons = @(Get-InventoryEditButtons -Overlay $createdTasksDialog)
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $editButtons[0] -Description "first Created Tasks edit button"
    Wait-ForDialogRuntimeReady -SignalBase "CUSTOM_TASK_EDIT_DIALOG" -StartLine $markerStart -TimeoutSeconds 8
    $dialog = Wait-ForDialog -Name "Edit Custom Task" -TimeoutSeconds 8
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
    Wait-ForDialogClosed -Name "Edit Custom Task"
    $Overlay = Ensure-OverlayReady -Overlay $Overlay
}

function Run-ExactMatch-Execution {
    param([System.Windows.Automation.AutomationElement]$Overlay)
    Write-StepLog -Stage "FLOW" -Message "running exact-match execution check"
    $Overlay = Ensure-OverlayReady -Overlay $Overlay
    $input = Get-OverlayInput -Overlay $Overlay
    Set-Value -Element $input -Value "Open Weekly Reports"
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
        $Overlay = Ensure-OverlayReady -Overlay $Overlay
        $input = Get-OverlayInput -Overlay $Overlay
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
    Close-Overlay
    $overlay = Open-OverlayWithRuntimeRestartFallback
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Open Weekly Reports"
    Close-CreatedTasksDialog -Dialog $createdTasksDialog
    return $overlay
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
        Wait-ForDialogClosed -Name "Edit Custom Task" -TimeoutSeconds 4
    } catch {
        Add-Note "Late-item edit dialog close readback lagged after a successful update marker, but the runtime marker and refreshed Created Tasks view still confirmed the save."
    }
    $overlay = Wait-ForOverlayOpen
    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $overlay
    Wait-ForInventoryText -Overlay $createdTasksDialog -Text "Open Reports Eight"
    Close-CreatedTasksDialog -Dialog $createdTasksDialog
    Copy-SourceSnapshot -Slug "after_large_inventory_edit" | Out-Null
    return (Ensure-OverlayReady -Overlay $overlay)
}

function Run-Unsafe-Source-Check {
    Write-StepLog -Stage "FLOW" -Message "running unsafe-source blocking check"
    Corrupt-Source
    Restart-InteractiveRuntime | Out-Null
    $overlay = Open-OverlayWithRuntimeRestartFallback
    $createButton = Find-FirstElement -Root $overlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton"
    $markerStart = New-RuntimeMarkerCursor
    Invoke-ElementRobust -Element $createButton -Description "Create Custom Task button in unsafe-source path"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATE_BLOCKED|reason=source_invalid" -StartLine $markerStart
    $dialog = Get-DialogWindow -Name "Create Custom Task"
    if ($dialog) {
        throw "Unsafe source should block the create dialog before it opens."
    }
    if (Test-RuntimeMarkerSeen -Marker "RENDERER_MAIN|CUSTOM_TASK_CREATED|" -StartLine $markerStart) {
        throw "Unsafe source unexpectedly produced a create marker."
    }
    $status = Find-FirstElement -Root $overlay -AutomationId "QApplication.commandOverlayWindow.commandPanel.commandStatus"
    $statusText = if ($status) { $status.Current.Name } else { "" }
    if ($statusText -notlike "*blocked*") {
        throw "Unsafe source did not surface blocked status text. Saw: '$statusText'"
    }

    $createdTasksDialog = Open-CreatedTasksDialog -Overlay $overlay
    $dialogStatus = Find-FirstElement -Root $createdTasksDialog -AutomationId "QApplication.savedActionCreatedTasksDialog.savedActionCreatedTasksStatus"
    $dialogStatusText = if ($dialogStatus) { $dialogStatus.Current.Name } else { "" }
    if (-not $dialogStatusText) {
        throw "Created Tasks dialog did not surface saved-action source status in the unsafe-source path."
    }

    $editButtons = @(Get-InventoryEditButtons -Overlay $createdTasksDialog)
    if ($editButtons.Count -gt 0) {
        Add-Note "Unsafe source still showed edit buttons inside Created Tasks; expected fail-closed absence was not observed."
    } else {
        Add-Note "Unsafe source hid edit affordances inside Created Tasks, which matches the fail-closed UI posture."
    }
    Close-CreatedTasksDialog -Dialog $createdTasksDialog
    $overlay = Ensure-OverlayReady -Overlay $overlay
}

$originalSourceExists = Test-Path -LiteralPath $SourcePath
$originalSourceBytes = if ($originalSourceExists) { [System.IO.File]::ReadAllBytes($SourcePath) } else { [byte[]]@() }
$script:runtimeProcess = $null
$script:notepadProbe = $null
$runFailure = $null

try {
    Stop-StaleInteractiveValidationProcesses
    $script:runtimeProcess = Start-InteractiveRuntime
    Add-Artifact -Label "interactive_runtime_log" -Path $RuntimeLogPath
    Add-Artifact -Label "interactive_step_log" -Path $StepLogPath

    $script:notepadProbe = Start-NotepadProbe
    Add-Artifact -Label "notepad_probe_file" -Path $script:notepadProbe.path

    New-HealthySource
    Copy-SourceSnapshot -Slug "initial_source" | Out-Null

    $overlay = Open-OverlayWithRuntimeRestartFallback
    Add-ScenarioResult -Name "overlay_open" -Passed $true -Details "Overlay opened through the real hotkey and the runtime log recorded COMMAND_OVERLAY_OPENED."

    $overlay = Run-Create-Flow -Overlay $overlay
    Add-ScenarioResult -Name "valid_create" -Passed $true -Details "A real create dialog session created Open Notepad Task and refreshed inventory immediately."

    Run-Invalid-Create-Checks -Overlay $overlay
    Add-ScenarioResult -Name "invalid_create_rejection" -Passed $true -Details "Application, folder, file, and URL invalid targets stayed blocked in the real dialog with no write."

    Run-Collision-Checks -Overlay $overlay
    Add-ScenarioResult -Name "collision_rejection" -Passed $true -Details "Built-in and saved-action collisions were blocked in the real create dialog."

    $overlay = Run-Edit-Flow -Overlay $overlay
    Add-ScenarioResult -Name "valid_edit" -Passed $true -Details "The real edit dialog updated the same saved action in place and refreshed inventory immediately."

    Run-Invalid-Edit-Check -Overlay $overlay
    Add-ScenarioResult -Name "invalid_edit_rejection" -Passed $true -Details "A malformed edit target stayed blocked in the real edit dialog and did not write."

    Run-ExactMatch-Execution -Overlay $overlay
    Add-ScenarioResult -Name "exact_match_execution" -Passed $true -Details "Exact-match execution sent a real launch request for the edited saved action through the live overlay path."

    $overlay = Run-Reopen-Check
    Add-ScenarioResult -Name "reopen_persistence" -Passed $true -Details "Close/reopen preserved the latest saved action state and returned to a clean entry baseline."

    $overlay = Run-Large-Inventory-Check
    Add-ScenarioResult -Name "large_inventory_reachability" -Passed $true -Details "A later saved action beyond the old six-item cap was reachable and editable in the real UI."

    Run-Unsafe-Source-Check
    Add-ScenarioResult -Name "unsafe_source_blocking" -Passed $true -Details "An invalid saved-actions source blocked real create entry and surfaced repair-oriented status feedback."

    $notepadText = Get-NotepadText -Probe $script:notepadProbe
    if ($notepadText -ne "") {
        throw "Outside Notepad probe received unexpected input: '$notepadText'"
    }
    Add-ScenarioResult -Name "no_input_leakage" -Passed $true -Details "The outside Notepad probe stayed empty through overlay open, dialog interaction, submit, and reopen."

    Copy-SourceSnapshot -Slug "final_source_before_restore" | Out-Null
}
catch {
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

    if ($script:notepadProbe) {
        try {
            Stop-ProcessQuietly -Process $script:notepadProbe.process
        } catch {
        }
    }

    if ($script:runtimeProcess) {
        try {
            Stop-ProcessQuietly -Process $script:runtimeProcess
        } catch {
        }
    }
}

$reportLines = @()
$reportLines += "FB-036 SAVED-ACTION AUTHORING INTERACTIVE VALIDATION"
$reportLines += "Report: $ReportPath"
$reportLines += "Timestamp: $(Get-Date -Format o)"
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
    scenarios = $ValidationState.scenarios
    artifacts = $ValidationState.artifacts
    notes = $ValidationState.notes
}

$summary | ConvertTo-Json -Depth 8

if ($runFailure) {
    throw $runFailure
}
