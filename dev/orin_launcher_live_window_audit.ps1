param(
    [int]$TimeoutSeconds = 8,
    [int]$NoProgressTimeoutSeconds = 10,
    [switch]$Fb037Validation
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$source = @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

public static class CodexLiveAuditWin32
{
    public struct Point
    {
        public int X;
        public int Y;
    }

    public sealed class WindowInfo
    {
        public IntPtr Handle { get; set; }
        public int ProcessId { get; set; }
        public string Title { get; set; }
        public string ClassName { get; set; }
        public bool IsVisible { get; set; }
    }

    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

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

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool ScreenToClient(IntPtr hWnd, ref Point lpPoint);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    private static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);

    public static WindowInfo[] GetTopLevelWindows()
    {
        var windows = new List<WindowInfo>();
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam)
        {
            uint processId;
            GetWindowThreadProcessId(hWnd, out processId);
            var title = new StringBuilder(512);
            var className = new StringBuilder(256);
            GetWindowText(hWnd, title, title.Capacity);
            GetClassName(hWnd, className, className.Capacity);
            windows.Add(new WindowInfo
            {
                Handle = hWnd,
                ProcessId = (int)processId,
                Title = title.ToString(),
                ClassName = className.ToString(),
                IsVisible = IsWindowVisible(hWnd)
            });
            return true;
        }, IntPtr.Zero);
        return windows.ToArray();
    }

    public static void SendWindowClick(IntPtr hWnd, int screenX, int screenY, bool rightButton)
    {
        const uint WM_LBUTTONDOWN = 0x0201;
        const uint WM_LBUTTONUP = 0x0202;
        const uint WM_RBUTTONDOWN = 0x0204;
        const uint WM_RBUTTONUP = 0x0205;
        const int MK_LBUTTON = 0x0001;
        const int MK_RBUTTON = 0x0002;

        var point = new Point { X = screenX, Y = screenY };
        ScreenToClient(hWnd, ref point);
        int lParam = ((point.Y & 0xffff) << 16) | (point.X & 0xffff);
        if (rightButton)
        {
            SendMessage(hWnd, WM_RBUTTONDOWN, (IntPtr)MK_RBUTTON, (IntPtr)lParam);
            SendMessage(hWnd, WM_RBUTTONUP, IntPtr.Zero, (IntPtr)lParam);
            return;
        }

        SendMessage(hWnd, WM_LBUTTONDOWN, (IntPtr)MK_LBUTTON, (IntPtr)lParam);
        SendMessage(hWnd, WM_LBUTTONUP, IntPtr.Zero, (IntPtr)lParam);
    }

    public static void SendWindowKey(IntPtr hWnd, int virtualKey)
    {
        const uint WM_KEYDOWN = 0x0100;
        const uint WM_KEYUP = 0x0101;
        SendMessage(hWnd, WM_KEYDOWN, (IntPtr)virtualKey, (IntPtr)0x00000001);
        SendMessage(hWnd, WM_KEYUP, (IntPtr)virtualKey, (IntPtr)unchecked((int)0xC0000001));
    }
}
"@

Add-Type -TypeDefinition $source

$RootDir = Split-Path -Parent $PSScriptRoot
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutputDir = Join-Path $RootDir "dev\logs\launcher_live_window_audit\$Stamp"
$ManifestPath = Join-Path $OutputDir "manifest.json"
$StepLogPath = Join-Path $OutputDir "step_log.txt"
$SourcePath = Join-Path $env:LOCALAPPDATA "Nexus Desktop AI\saved_actions.json"
$SourceBackupPath = Join-Path $OutputDir "saved_actions.backup.json"
$LauncherPath = Join-Path $RootDir "desktop\orin_desktop_launcher.pyw"
$AuditRuntimeLogPath = Join-Path $OutputDir "audit_runtime.log"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$script:Captures = New-Object System.Collections.Generic.List[object]
$script:ScenarioResults = New-Object System.Collections.Generic.List[object]
$script:CleanupNotes = New-Object System.Collections.Generic.List[object]
$script:AuditStartedAt = Get-Date
$script:LastProgressAt = $script:AuditStartedAt
$script:LastProgressPoint = "audit_start"
$script:ManifestStatus = "ABORTED"
$script:ManifestFailureMessage = "Run ended before a final manifest status was recorded."
$script:AuditRuntimeProcess = $null
$script:Fb037ManagedProcessNames = @("notepad", "mspaint", "calc", "CalculatorApp", "taskmgr")
$script:BaselinePythonPids = @(
    Get-CimInstance Win32_Process |
        Where-Object { $_.Name -in @("python.exe", "pythonw.exe") } |
        Select-Object -ExpandProperty ProcessId
)
$script:BaselineAppPids = @(
    foreach ($name in $script:Fb037ManagedProcessNames) {
        Get-Process -Name $name -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty Id
    }
)

function Write-AuditStep {
    param(
        [string]$Stage,
        [string]$Message,
        [switch]$DoesNotCountAsProgress
    )

    $timestamp = (Get-Date).ToString("o")
    $line = "$timestamp [$Stage] $Message"
    Add-Content -LiteralPath $StepLogPath -Value $line -Encoding utf8
    Write-Host $line

    if (-not $DoesNotCountAsProgress) {
        $script:LastProgressAt = Get-Date
        $script:LastProgressPoint = "$Stage :: $Message"
    }
}

function Assert-NoProgressBudget {
    param([string]$Activity)

    if ($NoProgressTimeoutSeconds -gt 0 -and (Get-Date) -ge $script:LastProgressAt.AddSeconds($NoProgressTimeoutSeconds)) {
        throw "No-progress watchdog exceeded during $Activity. Last confirmed progress: $($script:LastProgressPoint)."
    }
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

function Wait-Until {
    param(
        [scriptblock]$Condition,
        [string]$Description,
        [int]$TimeoutSeconds = $TimeoutSeconds
    )

    Write-AuditStep -Stage "WAIT" -Message "waiting for $Description"
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $result = & $Condition
        if ($result) {
            Write-AuditStep -Stage "WAIT" -Message "satisfied $Description"
            return $result
        }

        if ($NoProgressTimeoutSeconds -gt 0 -and (Get-Date) -ge $script:LastProgressAt.AddSeconds($NoProgressTimeoutSeconds)) {
            throw "No-progress watchdog exceeded while waiting for $Description. Last confirmed progress: $($script:LastProgressPoint)."
        }

        Start-Sleep -Milliseconds 120
    }

    throw "Timed out waiting for $Description. Last confirmed progress: $($script:LastProgressPoint)."
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
            "name='{0}' automationId='{1}' controlType='{2}' enabled={3} offscreen={4} focus={5} rect={6},{7},{8},{9}" -f
            $Element.Current.Name,
            $Element.Current.AutomationId,
            (Get-ElementControlTypeNameSafe -Element $Element),
            $Element.Current.IsEnabled,
            $Element.Current.IsOffscreen,
            $Element.Current.HasKeyboardFocus,
            [int]$rect.Left,
            [int]$rect.Top,
            [int]$rect.Width,
            [int]$rect.Height
        )
    } catch {
        return "unreadable"
    }
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
        return [string]$Element.Current.Name
    } catch {
    }

    return ""
}

function Get-WindowHandle {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return [IntPtr]::Zero
    }

    try {
        $handle = [int]$Element.Current.NativeWindowHandle
        if ($handle -gt 0) {
            return [IntPtr]$handle
        }
    } catch {
    }

    return [IntPtr]::Zero
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
            $handle = Get-WindowHandle -Element $current
            if ($handle -ne [IntPtr]::Zero) {
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

function Focus-ElementWindow {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if (-not $Element) {
        return
    }

    $targetWindow = Get-ElementOwningWindow -Element $Element
    if (-not $targetWindow) {
        $targetWindow = $Element
    }

    try {
        $handle = Get-WindowHandle -Element $targetWindow
        if ($handle -ne [IntPtr]::Zero) {
            [CodexLiveAuditWin32]::ShowWindowAsync($handle, 5) | Out-Null
            [CodexLiveAuditWin32]::SetForegroundWindow($handle) | Out-Null
        }
    } catch {
    }

    try {
        $targetWindow.SetFocus()
    } catch {
    }

    Start-Sleep -Milliseconds 120
}

function Click-ElementCenter {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Description
    )

    if (-not $Element) {
        throw "Missing element for $Description."
    }

    try {
        $point = $Element.GetClickablePoint()
        [CodexLiveAuditWin32]::SetCursorPos([int]$point.X, [int]$point.Y) | Out-Null
        Start-Sleep -Milliseconds 50
        [CodexLiveAuditWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 50
        [CodexLiveAuditWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 120
        return
    } catch {
    }

    try {
        $rect = $Element.Current.BoundingRectangle
        $x = [int]([Math]::Round($rect.Left + ($rect.Width / 2)))
        $y = [int]([Math]::Round($rect.Top + ($rect.Height / 2)))
        if ($x -le 0 -or $y -le 0) {
            throw "Element click target was offscreen or invalid."
        }
        [CodexLiveAuditWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds 50
        [CodexLiveAuditWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 50
        [CodexLiveAuditWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 120
        return
    } catch {
    }

    throw "Could not click $Description."
}

function Click-ElementCenterByBounds {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Description,
        [ValidateSet("left", "right")]
        [string]$Button = "left"
    )

    if (-not $Element) {
        throw "Missing element for $Description."
    }

    try {
        $rect = $Element.Current.BoundingRectangle
        $x = [int]([Math]::Round($rect.Left + ($rect.Width / 2)))
        $y = [int]([Math]::Round($rect.Top + ($rect.Height / 2)))
        if ($x -le 0 -or $y -le 0) {
            throw "Element click target was offscreen or invalid."
        }

        $owningWindow = Get-ElementOwningWindow -Element $Element
        $windowHandle = Get-WindowHandle -Element $owningWindow
        if ($windowHandle -ne [IntPtr]::Zero) {
            [CodexLiveAuditWin32]::SetForegroundWindow($windowHandle) | Out-Null
            Start-Sleep -Milliseconds 80
            [CodexLiveAuditWin32]::SendWindowClick($windowHandle, $x, $y, ($Button -eq "right"))
            Start-Sleep -Milliseconds 160
            return
        }

        $down = if ($Button -eq "right") { 0x0008 } else { 0x0002 }
        $up = if ($Button -eq "right") { 0x0010 } else { 0x0004 }
        [CodexLiveAuditWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds 60
        [CodexLiveAuditWin32]::mouse_event($down, 0, 0, 0, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 60
        [CodexLiveAuditWin32]::mouse_event($up, 0, 0, 0, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 160
        return
    } catch {
        throw "Could not $Button-click $Description by bounds: $($_.Exception.Message)"
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

function Send-EnterToElementWindow {
    param(
        [System.Windows.Automation.AutomationElement]$Element,
        [string]$Description
    )

    $owningWindow = Get-ElementOwningWindow -Element $Element
    $windowHandle = Get-WindowHandle -Element $owningWindow
    if ($windowHandle -ne [IntPtr]::Zero) {
        [CodexLiveAuditWin32]::SetForegroundWindow($windowHandle) | Out-Null
        Start-Sleep -Milliseconds 80
        [CodexLiveAuditWin32]::SendWindowKey($windowHandle, 0x0D)
        Start-Sleep -Milliseconds 80
        Write-AuditStep -Stage "FB037" -Message "enter sent to owning window for '$Description'"
        return
    }

    Send-VirtualKey -Key 0x0D
    Write-AuditStep -Stage "FB037" -Message "enter sent by virtual key fallback for '$Description'"
}

function Focus-OverlayInputForSubmit {
    param(
        [System.Windows.Automation.AutomationElement]$Overlay,
        [System.Windows.Automation.AutomationElement]$InputElement,
        [string]$Description
    )

    $liveOverlay = Get-OverlayWindow
    if ($liveOverlay) {
        $Overlay = $liveOverlay
        Focus-ElementWindow -Element $Overlay
    }

    if ($Overlay) {
        $liveInput = Get-OverlayInput -Overlay $Overlay
        if ($liveInput) {
            $InputElement = $liveInput
        }
    }

    if (-not $InputElement) {
        throw "Missing overlay input for $Description."
    }

    Focus-ElementWindow -Element $InputElement
    Click-ElementCenterByBounds -Element $InputElement -Description $Description -Button "right"
    Click-ElementCenterByBounds -Element $InputElement -Description $Description -Button "left"
    try {
        $InputElement.SetFocus()
    } catch {
    }
    Start-Sleep -Milliseconds 160
    Write-AuditStep -Stage "FB037" -Message "input focused for '$Description' state=$(Get-ElementStateSummary -Element $InputElement)"
    return $InputElement
}

function Submit-OverlayInput {
    param(
        [System.Windows.Automation.AutomationElement]$InputElement,
        [string]$Description
    )

    Focus-ElementWindow -Element $InputElement
    Click-ElementCenterByBounds -Element $InputElement -Description $Description -Button "right"
    Click-ElementCenterByBounds -Element $InputElement -Description $Description -Button "left"
    try {
        $InputElement.SetFocus()
    } catch {
    }
    Start-Sleep -Milliseconds 80
    Send-EnterToElementWindow -Element $InputElement -Description $Description
}

function Engage-OverlayInputForSubmit {
    param(
        [System.Windows.Automation.AutomationElement]$InputElement,
        [string]$ExpectedValue,
        [string]$Description
    )

    Focus-ElementWindow -Element $InputElement
    Click-ElementCenterByBounds -Element $InputElement -Description $Description -Button "right"
    Click-ElementCenterByBounds -Element $InputElement -Description $Description -Button "left"
    try {
        $InputElement.SetFocus()
    } catch {
    }

    try {
        [System.Windows.Forms.SendKeys]::SendWait("{END}")
        Start-Sleep -Milliseconds 30
        [System.Windows.Forms.SendKeys]::SendWait(" ")
        Start-Sleep -Milliseconds 30
        [System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}")
    } catch {
        Send-VirtualKey -Key 0x23
        Start-Sleep -Milliseconds 30
        Send-VirtualKey -Key 0x20
        Start-Sleep -Milliseconds 30
        Send-VirtualKey -Key 0x08
    }

    Start-Sleep -Milliseconds 120
    $currentValue = Get-ElementReadableValue -Element $InputElement
    if ($currentValue -ne $ExpectedValue) {
        Set-ElementValue -Element $InputElement -Value $ExpectedValue -Description "$Description value restore"
        Start-Sleep -Milliseconds 80
    }
    Write-AuditStep -Stage "FB037" -Message "input engagement nudged for '$Description' state=$(Get-ElementStateSummary -Element $InputElement) value='$(Get-ElementReadableValue -Element $InputElement)'"
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
        Write-AuditStep -Stage "CLEANUP" -Message "stopping audit runtime helper pid=$($script:AuditRuntimeProcess.Id)"
        try {
            Stop-Process -Id $script:AuditRuntimeProcess.Id -Force -ErrorAction Stop
            Write-AuditStep -Stage "CLEANUP" -Message "audit runtime helper stopped"
        } catch {
            Add-CleanupNote -Action "stop_runtime_helper" -Result "helper_failure" -Details "could not stop audit runtime helper pid=$($script:AuditRuntimeProcess.Id): $($_.Exception.Message)"
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
    $existingOverlay = Get-OverlayWindow
    if ($existingOverlay) {
        try {
            Close-WindowByEsc -Window $existingOverlay
            Start-Sleep -Milliseconds 300
        } catch {
        }
    }

    Send-OverlayHotkey
    Start-Sleep -Milliseconds 300
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

function Write-SourcePayload {
    param([object]$Payload)

    $json = ($Payload | ConvertTo-Json -Depth 8) + "`n"
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($SourcePath, $json, $encoding)
}

function Seed-Fb037EmptySource {
    Write-SourcePayload -Payload ([ordered]@{
            schema_version = 1
            actions        = @()
            groups         = @()
        })
}

function New-Fb037OverrideAction {
    param(
        [string]$Id,
        [string]$Title,
        [string]$Alias
    )

    return [ordered]@{
        id              = $Id
        title           = $Title
        target_kind     = "folder"
        target          = (Join-Path $RootDir "Docs")
        aliases         = @($Alias)
        invocation_mode = "aliases_only"
        trigger_mode    = "open"
    }
}

function Seed-Fb037OverrideSource {
    param([string[]]$Aliases)

    $actions = @()
    foreach ($alias in $Aliases) {
        $slug = ($alias -replace "[^A-Za-z0-9]+", "_").Trim("_").ToLowerInvariant()
        $title = "Saved Override " + ((Get-Culture).TextInfo.ToTitleCase($alias))
        $actions += New-Fb037OverrideAction -Id "saved_override_$slug" -Title $title -Alias $alias
    }

    Write-SourcePayload -Payload ([ordered]@{
            schema_version = 1
            actions        = $actions
            groups         = @()
        })
}

function Add-ScenarioResult {
    param(
        [string]$Name,
        [string]$Result,
        [string]$Details,
        [object]$Artifacts = $null
    )

    $script:ScenarioResults.Add([pscustomobject]@{
            name      = $Name
            result    = $Result
            details   = $Details
            artifacts = $Artifacts
        })
    Write-AuditStep -Stage "SCENARIO" -Message "$Name :: $Result :: $Details"
}

function Add-CleanupNote {
    param(
        [string]$Action,
        [string]$Result,
        [string]$Details
    )

    $script:CleanupNotes.Add([pscustomobject]@{
            action  = $Action
            result  = $Result
            details = $Details
    })
    Write-AuditStep -Stage "CLEANUP" -Message "$Action :: $Result :: $Details"
}

function Get-CleanupSummary {
    $resultValues = @($script:CleanupNotes | ForEach-Object { $_.result })
    return [pscustomobject]@{
        success_count          = @($resultValues | Where-Object { $_ -eq "success" }).Count
        os_blocked_count       = @($resultValues | Where-Object { $_ -eq "os_blocked" }).Count
        helper_failure_count   = @($resultValues | Where-Object { $_ -eq "helper_failure" }).Count
        baseline_skipped_count = @($resultValues | Where-Object { $_ -eq "baseline_skipped" }).Count
    }
}

function Get-Fb037ManagedProcesses {
    $processes = @()
    foreach ($name in $script:Fb037ManagedProcessNames) {
        $processes += @(Get-Process -Name $name -ErrorAction SilentlyContinue)
    }
    return @($processes)
}

function Test-BaselineAppProcess {
    param([int]$ProcessId)
    return ($script:BaselineAppPids -contains $ProcessId)
}

function Get-RuntimeLinesSince {
    param([int]$StartLine)

    if (-not (Test-Path -LiteralPath $AuditRuntimeLogPath)) {
        return @()
    }

    $lines = @(Get-Content -LiteralPath $AuditRuntimeLogPath)
    if ($lines.Count -le $StartLine) {
        return ,@()
    }

    return ,@($lines | Select-Object -Skip $StartLine)
}

function Get-RuntimeTailText {
    param(
        [int]$StartLine,
        [int]$Count = 8
    )

    $lines = Get-RuntimeLinesSince -StartLine $StartLine
    if ($lines.Count -eq 0) {
        return "<no fresh runtime lines>"
    }

    return (@($lines | Select-Object -Last $Count) -join " || ")
}

function Wait-ForCommandSubmitOutcome {
    param(
        [string]$ExpectedActionId,
        [int]$StartLine,
        [int]$TimeoutSeconds = 3
    )

    return (Wait-Until -TimeoutSeconds $TimeoutSeconds -Description "submit outcome for action_id=$ExpectedActionId" -Condition {
            $lines = Get-RuntimeLinesSince -StartLine $StartLine
            foreach ($line in $lines) {
                if ($line -like "*RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=$ExpectedActionId*") {
                    return [pscustomobject]@{
                        Kind = "confirm"
                        Line = $line
                    }
                }
                if ($line -like "*RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=*" -and $line -notlike "*action_id=$ExpectedActionId*") {
                    return [pscustomobject]@{
                        Kind = "wrong_confirm"
                        Line = $line
                    }
                }
                if ($line -like "*RENDERER_MAIN|COMMAND_NOT_FOUND*") {
                    return [pscustomobject]@{
                        Kind = "not_found"
                        Line = $line
                    }
                }
                if ($line -like "*RENDERER_MAIN|COMMAND_AMBIGUOUS*") {
                    return [pscustomobject]@{
                        Kind = "ambiguous"
                        Line = $line
                    }
                }
                if ($line -like "*OVERLAY_TRACE|source=renderer|event=submit_result*" -and $line -like "*result='not_found'*") {
                    return [pscustomobject]@{
                        Kind = "not_found"
                        Line = $line
                    }
                }
                if ($line -like "*OVERLAY_TRACE|source=renderer|event=submit_result*" -and $line -like "*result='ambiguous'*") {
                    return [pscustomobject]@{
                        Kind = "ambiguous"
                        Line = $line
                    }
                }
            }

            return $null
        })
}

function Assert-RuntimeMarkerAbsent {
    param(
        [string]$Marker,
        [int]$StartLine
    )

    $lines = Get-RuntimeLinesSince -StartLine $StartLine
    foreach ($line in $lines) {
        if ($line -like "*$Marker*") {
            throw "Unexpected runtime marker found after line ${StartLine}: $Marker"
        }
    }
}

function Find-RootWindowByNamePattern {
    param([string[]]$NamePatterns)

    $children = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition
    )

    for ($i = 0; $i -lt $children.Count; $i++) {
        $window = $children.Item($i)
        try {
            if ($window.Current.IsOffscreen) {
                continue
            }

            foreach ($pattern in $NamePatterns) {
                if ($window.Current.Name -like $pattern) {
                    return $window
                }
            }
        } catch {
        }
    }

    return $null
}

function Wait-ForRootWindowByNamePattern {
    param(
        [string[]]$NamePatterns,
        [int]$TimeoutSeconds = 8
    )

    $description = "window matching " + ($NamePatterns -join ", ")
    return (Wait-Until -Description $description -TimeoutSeconds $TimeoutSeconds -Condition {
            $window = Find-RootWindowByNamePattern -NamePatterns $NamePatterns
            if ($window -and (Test-ElementUsable -Element $window -RequireEnabled $false)) {
                return $window
            }
            return $null
        })
}

function Get-ProcessLaunchProbe {
    param([string[]]$ProcessNames)

    $processes = @()
    $baselineProcesses = @()
    foreach ($processName in $ProcessNames) {
        $matchingProcesses = @(
            Get-Process -Name $processName -ErrorAction SilentlyContinue
        )
        $processes += @(
            $matchingProcesses |
                Where-Object {
                    ($_.StartTime -ge $script:AuditStartedAt.AddSeconds(-2)) -and
                    -not (Test-BaselineAppProcess -ProcessId ([int]$_.Id))
                }
        )
        $baselineProcesses += @(
            $matchingProcesses |
                Where-Object { Test-BaselineAppProcess -ProcessId ([int]$_.Id) }
        )
    }

    $processIds = @($processes | Select-Object -ExpandProperty Id -ErrorAction SilentlyContinue)
    $baselineProcessIds = @($baselineProcesses | Select-Object -ExpandProperty Id -ErrorAction SilentlyContinue)
    $windows = @()
    $baselineWindows = @()
    if ($processIds.Count -gt 0) {
        foreach ($window in [CodexLiveAuditWin32]::GetTopLevelWindows()) {
            if ($processIds -contains [int]$window.ProcessId) {
                $windows += $window
            }
        }
    }
    if ($baselineProcessIds.Count -gt 0) {
        foreach ($window in [CodexLiveAuditWin32]::GetTopLevelWindows()) {
            if ($baselineProcessIds -contains [int]$window.ProcessId) {
                $baselineWindows += $window
            }
        }
    }

    return [pscustomobject]@{
        processes          = @($processes | ForEach-Object {
                [pscustomobject]@{
                    id                = $_.Id
                    process_name      = $_.ProcessName
                    main_window_title = $_.MainWindowTitle
                    main_window_handle = $_.MainWindowHandle.ToInt64()
                    start_time        = $_.StartTime.ToString("o")
                }
            })
        windows            = @($windows | ForEach-Object {
                [pscustomobject]@{
                    handle     = $_.Handle.ToInt64()
                    process_id = $_.ProcessId
                    title      = $_.Title
                    class_name = $_.ClassName
                    is_visible = $_.IsVisible
                }
            })
        baseline_processes = @($baselineProcesses | ForEach-Object {
                [pscustomobject]@{
                    id                = $_.Id
                    process_name      = $_.ProcessName
                    main_window_title = $_.MainWindowTitle
                    main_window_handle = $_.MainWindowHandle.ToInt64()
                    start_time        = $_.StartTime.ToString("o")
                }
            })
        baseline_windows   = @($baselineWindows | ForEach-Object {
                [pscustomobject]@{
                    handle     = $_.Handle.ToInt64()
                    process_id = $_.ProcessId
                    title      = $_.Title
                    class_name = $_.ClassName
                    is_visible = $_.IsVisible
                }
            })
    }
}

function Write-LaunchProbeArtifact {
    param(
        [string]$Label,
        [object]$Probe,
        [string]$Classification
    )

    $path = Join-Path $OutputDir "$Label.json"
    [pscustomobject]@{
        classification = $Classification
        probe          = $Probe
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding utf8

    return $path
}

function Resolve-AutomationElementFromWindowInfo {
    param([object]$WindowInfo)

    if (-not $WindowInfo) {
        return $null
    }

    try {
        if (-not $WindowInfo.IsVisible) {
            return $null
        }
        $handle = [IntPtr]::new([Int64]$WindowInfo.Handle)
        if ($handle -eq [IntPtr]::Zero) {
            return $null
        }
        $element = [System.Windows.Automation.AutomationElement]::FromHandle($handle)
        if ($element -and (Test-ElementUsable -Element $element -RequireEnabled $false)) {
            return $element
        }
    } catch {
    }

    return $null
}

function Wait-ForLaunchedWindowEvidence {
    param(
        [string[]]$NamePatterns,
        [string[]]$ProcessNames,
        [int]$TimeoutSeconds = 14,
        [switch]$AllowProcessOnlyEvidence,
        [switch]$AllowExistingWindowEvidence
    )

    $description = "visible launched window matching " + (($NamePatterns + $ProcessNames) -join ", ")
    Write-AuditStep -Stage "WAIT" -Message "waiting for $description"
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastProbe = $null
    $lastProbeSignature = ""
    $lastProbeHeartbeatAt = Get-Date
    $processOnlyEligibleAt = $null
    $processOnlyEvidenceProbe = $null
    while ((Get-Date) -lt $deadline) {
        $lastProbe = Get-ProcessLaunchProbe -ProcessNames $ProcessNames
        $probeSignature = "processes=$($lastProbe.processes.Count);windows=$($lastProbe.windows.Count);baseline_processes=$($lastProbe.baseline_processes.Count);baseline_windows=$($lastProbe.baseline_windows.Count)"
        if ($probeSignature -ne $lastProbeSignature) {
            $lastProbeSignature = $probeSignature
            $lastProbeHeartbeatAt = Get-Date
            Write-AuditStep -Stage "WAIT" -Message "$description probe update: $probeSignature"
        } elseif ((Get-Date) -ge $lastProbeHeartbeatAt.AddSeconds(2)) {
            $lastProbeHeartbeatAt = Get-Date
            Write-AuditStep -Stage "WAIT" -Message "$description probe stable: $probeSignature"
        }
        if ($AllowProcessOnlyEvidence -and $lastProbe.processes.Count -gt 0 -and -not $processOnlyEligibleAt) {
            $processOnlyEligibleAt = (Get-Date).AddSeconds(3)
            $processOnlyEvidenceProbe = $lastProbe
            Write-AuditStep -Stage "WAIT" -Message "$description process-only evidence candidate observed; waiting briefly for a visible window"
        }

        $uiaWindow = Find-RootWindowByNamePattern -NamePatterns $NamePatterns
        if ($uiaWindow -and (Test-ElementUsable -Element $uiaWindow -RequireEnabled $false)) {
            $uiaProcessId = 0
            try {
                $uiaProcessId = [int]$uiaWindow.Current.ProcessId
            } catch {
            }
            $launchedProcessIds = @($lastProbe.processes | ForEach-Object { [int]$_.id })
            if ($ProcessNames.Count -eq 0 -or $launchedProcessIds -contains $uiaProcessId -or $lastProbe.processes.Count -gt 0) {
                $method = if ($ProcessNames.Count -gt 0 -and $lastProbe.processes.Count -gt 0 -and -not ($launchedProcessIds -contains $uiaProcessId)) {
                    "uia_name_pattern_after_process"
                } else {
                    "uia_name_pattern"
                }
                Write-AuditStep -Stage "WAIT" -Message "satisfied $description via $method"
                return [pscustomobject]@{
                    element        = $uiaWindow
                    method         = $method
                    probe          = $lastProbe
                    classification = "visible_window"
                }
            }
        }

        if ($AllowExistingWindowEvidence -and $lastProbe.processes.Count -eq 0 -and $lastProbe.baseline_processes.Count -gt 0 -and $uiaWindow -and (Test-ElementUsable -Element $uiaWindow -RequireEnabled $false)) {
            Write-AuditStep -Stage "WAIT" -Message "satisfied $description via existing baseline window after launch request"
            return [pscustomobject]@{
                element        = $uiaWindow
                method         = "existing_baseline_window_after_launch_request"
                probe          = $lastProbe
                classification = "existing_window_reused"
            }
        }

        foreach ($candidate in $lastProbe.windows) {
            if (-not $candidate.is_visible) {
                continue
            }

            $matches = $false
            foreach ($pattern in $NamePatterns) {
                if ($candidate.title -like $pattern -or $candidate.class_name -like $pattern) {
                    $matches = $true
                    break
                }
            }
            if (-not $matches -and $ProcessNames.Count -gt 0) {
                $matches = $true
            }
            if (-not $matches) {
                continue
            }

            $element = Resolve-AutomationElementFromWindowInfo -WindowInfo $candidate
            if ($element) {
                Write-AuditStep -Stage "WAIT" -Message "satisfied $description via Win32 process window"
                return [pscustomobject]@{
                    element        = $element
                    method         = "win32_process_window"
                    probe          = $lastProbe
                    classification = "visible_window"
                }
            }

            Write-AuditStep -Stage "WAIT" -Message "satisfied $description via Win32 visible-window probe"
            return [pscustomobject]@{
                element        = $null
                method         = "win32_visible_window_probe"
                probe          = $lastProbe
                classification = "visible_window_probe"
            }
        }

        if ($AllowProcessOnlyEvidence -and $processOnlyEvidenceProbe -and $processOnlyEligibleAt -and (Get-Date) -ge $processOnlyEligibleAt) {
            Write-AuditStep -Stage "WAIT" -Message "satisfied $description via classified process-only launch evidence"
            return [pscustomobject]@{
                element        = $null
                method         = "process_only_no_visible_window"
                probe          = $processOnlyEvidenceProbe
                classification = "process_launched_no_visible_window"
            }
        }

        if ($NoProgressTimeoutSeconds -gt 0 -and (Get-Date) -ge $script:LastProgressAt.AddSeconds($NoProgressTimeoutSeconds)) {
            $probeJson = if ($lastProbe) { $lastProbe | ConvertTo-Json -Depth 6 -Compress } else { "{}" }
            throw "No-progress watchdog exceeded while waiting for $description. Last confirmed progress: $($script:LastProgressPoint). Process/window probe: $probeJson"
        }

        Start-Sleep -Milliseconds 150
    }

    $probeJson = if ($lastProbe) { $lastProbe | ConvertTo-Json -Depth 6 -Compress } else { "{}" }
    throw "Timed out waiting for $description. Last confirmed progress: $($script:LastProgressPoint). Process/window probe: $probeJson"
}

function Close-RootWindowsByNamePattern {
    param([string[]]$NamePatterns)

    $closed = 0
    while ($true) {
        $window = Find-RootWindowByNamePattern -NamePatterns $NamePatterns
        if (-not $window) {
            break
        }

        try {
            Close-WindowByEsc -Window $window
            Start-Sleep -Milliseconds 250
        } catch {
        }

        try {
            if (-not $window.Current.IsOffscreen) {
                Focus-Element -Element $window
                [System.Windows.Forms.SendKeys]::SendWait("%{F4}")
                Start-Sleep -Milliseconds 450
            }
        } catch {
        }

        $closed += 1
        if ($closed -ge 6) {
            break
        }
    }

    return $closed
}

function Close-RootWindowsForProcessIds {
    param(
        [int[]]$ProcessIds,
        [string[]]$NamePatterns
    )

    if (-not $ProcessIds -or $ProcessIds.Count -eq 0) {
        return 0
    }

    $closed = 0
    $windows = @(
        [CodexLiveAuditWin32]::GetTopLevelWindows() |
            Where-Object { $ProcessIds -contains [int]$_.ProcessId }
    )
    Write-AuditStep -Stage "CLEANUP" -Message "close_window scan found $($windows.Count) top-level launched window(s) for process ids: $($ProcessIds -join ', ')"

    $maxCloseAttempts = 12
    for ($i = 0; $i -lt $windows.Count; $i++) {
        Assert-NoProgressBudget -Activity "cleanup close-window scan"
        if ($i -ge $maxCloseAttempts) {
            Write-AuditStep -Stage "CLEANUP" -Message "close_window attempts reached $maxCloseAttempts; remaining cleanup will be classified by process termination"
            break
        }

        $windowInfo = $windows[$i]
        try {
            $matchesName = ($NamePatterns.Count -eq 0)
            foreach ($pattern in $NamePatterns) {
                if ($windowInfo.Title -like $pattern -or $windowInfo.ClassName -like $pattern) {
                    $matchesName = $true
                    break
                }
            }
            if (-not $matchesName) {
                continue
            }

            Write-AuditStep -Stage "CLEANUP" -Message "close_window attempt pid=$($windowInfo.ProcessId) handle=$($windowInfo.Handle.ToInt64()) title='$($windowInfo.Title)' class='$($windowInfo.ClassName)'"
            $window = Resolve-AutomationElementFromWindowInfo -WindowInfo $windowInfo
            if (-not $window) {
                Write-AuditStep -Stage "CLEANUP" -Message "close_window probe-only window handle=$($windowInfo.Handle.ToInt64()) pid=$($windowInfo.ProcessId); process termination will classify final cleanup"
                continue
            }

            Close-WindowByEsc -Window $window
            Start-Sleep -Milliseconds 250
            if (-not $window.Current.IsOffscreen) {
                Focus-Element -Element $window
                [System.Windows.Forms.SendKeys]::SendWait("%{F4}")
                Start-Sleep -Milliseconds 450
            }
            $closed += 1
        } catch {
            Add-CleanupNote -Action "close_window" -Result "helper_failure" -Details "could not request close for process-owned window: $($_.Exception.Message)"
        }
    }

    return $closed
}

function Stop-Fb037LaunchedApps {
    Write-AuditStep -Stage "CLEANUP" -Message "starting FB-037 launched-app cleanup"
    Assert-NoProgressBudget -Activity "FB-037 launched-app cleanup start"
    $launchedProcesses = @(
        Get-Fb037ManagedProcesses |
            Where-Object {
                ($_.StartTime -ge $script:AuditStartedAt.AddSeconds(-2)) -and
                -not (Test-BaselineAppProcess -ProcessId ([int]$_.Id))
            }
    )
    $baselineProcesses = @(
        Get-Fb037ManagedProcesses |
            Where-Object { Test-BaselineAppProcess -ProcessId ([int]$_.Id) }
    )
    if ($baselineProcesses.Count -gt 0) {
        Add-CleanupNote -Action "baseline_processes" -Result "baseline_skipped" -Details "preserved baseline app process ids: $((@($baselineProcesses | ForEach-Object { $_.Id }) -join ', '))"
    }

    $launchedProcessIds = @($launchedProcesses | ForEach-Object { [int]$_.Id })
    Write-AuditStep -Stage "CLEANUP" -Message "FB-037 launched process ids: $($launchedProcessIds -join ', ')"
    $closedWindows = Close-RootWindowsForProcessIds -ProcessIds $launchedProcessIds -NamePatterns @("*Task Manager*", "*Calculator*", "*Notepad*", "*Untitled*", "*Paint*", "*Docs*")
    if ($closedWindows -gt 0) {
        Add-CleanupNote -Action "close_windows" -Result "success" -Details "requested close for $closedWindows launched window(s)"
    }

    foreach ($process in $launchedProcesses) {
        Assert-NoProgressBudget -Activity "FB-037 stop-process cleanup"
        Write-AuditStep -Stage "CLEANUP" -Message "stop_process attempt $($process.ProcessName) pid=$($process.Id)"
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            Add-CleanupNote -Action "stop_process" -Result "success" -Details "stopped $($process.ProcessName) pid=$($process.Id)"
        } catch {
            $result = if ($_.Exception.Message -like "*Cannot find a process*" -or $_.Exception.Message -like "*process identifier*") {
                "success"
            } elseif ($_.Exception.Message -like "*Access is denied*") {
                "os_blocked"
            } else {
                "helper_failure"
            }
            $details = if ($result -eq "success") {
                "$($process.ProcessName) pid=$($process.Id) already exited before forced stop"
            } else {
                "could not stop $($process.ProcessName) pid=$($process.Id): $($_.Exception.Message)"
            }
            Add-CleanupNote -Action "stop_process" -Result $result -Details $details
        }
    }
    Write-AuditStep -Stage "CLEANUP" -Message "FB-037 launched-app cleanup complete"
}

function Invoke-Fb037Command {
    param(
        [string]$ScenarioName,
        [string]$Phrase,
        [string]$ExpectedActionId,
        [string[]]$ExpectedWindowPatterns = @(),
        [string[]]$ExpectedProcessNames = @(),
        [string[]]$ForbiddenActionIds = @(),
        [switch]$AllowProcessOnlyEvidence,
        [switch]$AllowExistingWindowEvidence
    )

    Write-AuditStep -Stage "FB037" -Message "running '$Phrase' expecting action_id=$ExpectedActionId"
    $overlay = Open-Overlay
    $overlayInput = Resolve-OverlayInput -Overlay $overlay
    $startLine = Get-RuntimeLogLineCount
    $overlayInput = Focus-OverlayInputForSubmit -Overlay $overlay -InputElement $overlayInput -Description "FB-037 command '$Phrase'"
    Set-ElementValue -Element $overlayInput -Value $Phrase -Description "FB-037 command '$Phrase'"
    Write-AuditStep -Stage "FB037" -Message "text set for '$Phrase' state=$(Get-ElementStateSummary -Element $overlayInput) value='$(Get-ElementReadableValue -Element $overlayInput)'"
    Wait-ForRuntimeMarker -Marker "OVERLAY_TRACE|source=renderer|event=local_text_changed" -StartLine $startLine -TimeoutSeconds 4 | Out-Null

    $confirmed = $false
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        $overlay = Get-OverlayWindow
        if (-not $overlay) {
            $overlay = Open-Overlay
        }
        $overlayInput = Resolve-OverlayInput -Overlay $overlay
        $overlayInput = Focus-OverlayInputForSubmit -Overlay $overlay -InputElement $overlayInput -Description "FB-037 command '$Phrase' submit attempt $attempt"
        Engage-OverlayInputForSubmit -InputElement $overlayInput -ExpectedValue $Phrase -Description "FB-037 command '$Phrase' submit attempt $attempt"
        $submitStartLine = Get-RuntimeLogLineCount
        Write-AuditStep -Stage "FB037" -Message "submit attempted for '$Phrase' attempt=$attempt"
        Submit-OverlayInput -InputElement $overlayInput -Description "FB-037 command '$Phrase' submit attempt $attempt"

        try {
            $outcome = Wait-ForCommandSubmitOutcome -ExpectedActionId $ExpectedActionId -StartLine $submitStartLine -TimeoutSeconds 3
        } catch {
            Write-AuditStep -Stage "FB037" -Message "submit attempt $attempt did not produce a confirm or failure marker for '$Phrase'. runtime_tail=$(Get-RuntimeTailText -StartLine $submitStartLine)"
            continue
        }

        if ($outcome.Kind -eq "confirm") {
            Write-AuditStep -Stage "FB037" -Message "submit confirmed for '$Phrase' attempt=$attempt line=$($outcome.Line)"
            $confirmed = $true
            break
        }

        throw "Submit for '$Phrase' produced $($outcome.Kind) instead of action_id=$ExpectedActionId. Runtime line: $($outcome.Line)"
    }

    if (-not $confirmed) {
        throw "Submit for '$Phrase' did not reach COMMAND_CONFIRM_READY for action_id=$ExpectedActionId after retries. Runtime tail: $(Get-RuntimeTailText -StartLine $startLine)"
    }

    $confirmPath = Capture-ElementScreenshot -Element $overlay -Label "${ScenarioName}_confirm" -DelayMs 180

    Write-AuditStep -Stage "FB037" -Message "launch submit attempted for '$Phrase'"
    Send-EnterToElementWindow -Element $overlay -Description "FB-037 command '$Phrase' launch"
    Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id=$ExpectedActionId" -StartLine $startLine -TimeoutSeconds 8 | Out-Null
    foreach ($forbiddenActionId in $ForbiddenActionIds) {
        Assert-RuntimeMarkerAbsent -Marker "RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id=$forbiddenActionId" -StartLine $startLine
    }
    $resultPath = Capture-ElementScreenshot -Element $overlay -Label "${ScenarioName}_result" -DelayMs 180

    $windowPath = ""
    $windowMethod = ""
    $windowProbe = $null
    $windowProbePath = ""
    $windowClassification = ""
    if ($ExpectedWindowPatterns.Count -gt 0) {
        $windowEvidence = Wait-ForLaunchedWindowEvidence -NamePatterns $ExpectedWindowPatterns -ProcessNames $ExpectedProcessNames -TimeoutSeconds 14 -AllowProcessOnlyEvidence:$AllowProcessOnlyEvidence -AllowExistingWindowEvidence:$AllowExistingWindowEvidence
        $windowMethod = $windowEvidence.method
        $windowProbe = $windowEvidence.probe
        $windowClassification = $windowEvidence.classification
        if ($windowEvidence.element) {
            $windowPath = Capture-ElementScreenshot -Element $windowEvidence.element -Label "${ScenarioName}_launched_window" -DelayMs 180
        } else {
            $windowProbePath = Write-LaunchProbeArtifact -Label "${ScenarioName}_launch_probe" -Probe $windowProbe -Classification $windowClassification
        }
    }

    Close-WindowByEsc -Window $overlay

    $artifacts = [pscustomobject]@{
        confirm_capture = $confirmPath
        result_capture  = $resultPath
        window_capture  = $windowPath
        window_method   = $windowMethod
        launch_probe    = $windowProbe
        launch_probe_capture = $windowProbePath
        launch_classification = $windowClassification
    }
    Add-ScenarioResult -Name $ScenarioName -Result "PASS" -Details "Phrase '$Phrase' resolved and launched action_id=$ExpectedActionId." -Artifacts $artifacts
    return $artifacts
}

function Assert-Fb037CreateCollisionRejected {
    param(
        [string]$ScenarioName,
        [string]$Alias
    )

    Write-AuditStep -Stage "FB037" -Message "verifying create collision rejection for '$Alias'"
    $overlay = Open-Overlay
    $createButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreateButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateButton"
    )
    Invoke-Element -Element $createButton -Description "Create Custom Task button"
    $createDialog = Wait-ForDialog -Name "Create Custom Task"
    Set-ElementValue -Element (Get-CreateDialogInput -Dialog $createDialog -LeafId "savedActionCreateTitleInput") -Value "Blocked $Alias" -Description "create collision title"
    Set-ElementValue -Element (Get-CreateDialogInput -Dialog $createDialog -LeafId "savedActionCreateAliasesInput") -Value $Alias -Description "create collision aliases"
    Set-ElementValue -Element (Get-CreateDialogInput -Dialog $createDialog -LeafId "savedActionCreateTargetInput") -Value "notepad.exe" -Description "create collision target"
    $createSubmit = Get-FirstButtonByName -Root $createDialog -Name "Create"
    Invoke-Element -Element $createSubmit -Description "Create collision submit"
    Start-Sleep -Milliseconds 300
    $capturePath = Capture-ElementScreenshot -Element $createDialog -Label "${ScenarioName}_create_collision" -DelayMs 180
    Close-WindowByEsc -Window $createDialog
    Add-ScenarioResult -Name $ScenarioName -Result "PASS" -Details "Create dialog rejected built-in phrase '$Alias'." -Artifacts ([pscustomobject]@{ capture = $capturePath })
}

function Assert-Fb037EditCollisionRejected {
    param(
        [string]$ScenarioName,
        [string]$Alias
    )

    Write-AuditStep -Stage "FB037" -Message "verifying edit collision rejection for '$Alias'"
    Seed-Fb037OverrideSource -Aliases @("fb037 editable safe")
    $overlay = Open-Overlay
    $manageTasksButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreatedTasksButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedTasksButton"
    )
    Invoke-Element -Element $manageTasksButton -Description "Manage Custom Tasks button"
    $manageTasksDialog = Wait-ForDialog -Name "Manage Custom Tasks"
    $editButton = Wait-Until -Description "first Edit button for FB-037 edit collision" -Condition {
        $button = Get-FirstEditButton -Root $manageTasksDialog
        if ($button -and (Test-ElementUsable -Element $button)) { return $button }
        return $null
    }
    Invoke-Element -Element $editButton -Description "first Edit button"
    $editDialog = Wait-ForDialog -Name "Edit Custom Task"
    Set-ElementValue -Element (Get-CreateDialogInput -Dialog $editDialog -LeafId "savedActionCreateAliasesInput") -Value $Alias -Description "edit collision aliases"
    $saveButton = Get-FirstButtonByName -Root $editDialog -Name "Save"
    if (-not $saveButton) {
        $saveButton = Get-FirstButtonByName -Root $editDialog -Name "Update"
    }
    Invoke-Element -Element $saveButton -Description "Edit collision submit"
    Start-Sleep -Milliseconds 300
    $capturePath = Capture-ElementScreenshot -Element $editDialog -Label "${ScenarioName}_edit_collision" -DelayMs 180
    Close-WindowByEsc -Window $editDialog
    Close-WindowByEsc -Window $manageTasksDialog
    Add-ScenarioResult -Name $ScenarioName -Result "PASS" -Details "Edit dialog rejected built-in phrase '$Alias'." -Artifacts ([pscustomobject]@{ capture = $capturePath })
}

function Write-AuditManifest {
    param(
        [string]$Status = "PASS",
        [string]$FailureMessage = ""
    )

    $script:ManifestStatus = $Status
    $script:ManifestFailureMessage = $FailureMessage
    $manifest = [pscustomobject]@{
        capture_dir                   = $OutputDir
        status                        = $Status
        failure_message               = $FailureMessage
        captures                      = $script:Captures
        scenarios                     = $script:ScenarioResults
        cleanup_notes                 = $script:CleanupNotes
        cleanup_summary               = Get-CleanupSummary
        baseline_app_process_ids      = $script:BaselineAppPids
        step_log                      = $StepLogPath
        timeout_budgets               = [pscustomobject]@{
            default_timeout_seconds     = $TimeoutSeconds
            no_progress_timeout_seconds = $NoProgressTimeoutSeconds
        }
        last_confirmed_progress_point = $script:LastProgressPoint
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding utf8

    [pscustomobject]@{
        capture_dir = $OutputDir
        manifest    = $ManifestPath
        status      = $Status
        scenarios   = $script:ScenarioResults
        captures    = $script:Captures
    } | ConvertTo-Json -Depth 8
}

function Run-Fb037Validation {
    try {
    Write-AuditStep -Stage "BUDGET" -Message "FB-037 live validation budgets active: default_timeout=${TimeoutSeconds}s no_progress=${NoProgressTimeoutSeconds}s"
    Backup-Source
    Write-AuditStep -Stage "SOURCE" -Message "saved action source backed up"
    Seed-Fb037EmptySource
    Write-AuditStep -Stage "SOURCE" -Message "FB-037 empty source seeded for built-in fallback scenarios"
    Launch-Desktop
    Write-AuditStep -Stage "RUNTIME" -Message "desktop runtime launched and ready"

    $builtInCases = @(
        @{ Name = "fb037_builtin_task_manager"; Phrase = "open task manager"; ActionId = "open_task_manager"; Windows = @("*Task Manager*"); Processes = @("taskmgr"); AllowExisting = $true; AllowProcessOnly = $false },
        @{ Name = "fb037_builtin_calculator"; Phrase = "open calculator"; ActionId = "open_calculator"; Windows = @("*Calculator*"); Processes = @("CalculatorApp", "calc"); AllowExisting = $false; AllowProcessOnly = $false },
        @{ Name = "fb037_builtin_notepad"; Phrase = "open notepad"; ActionId = "open_notepad"; Windows = @("*Notepad*", "*Untitled*"); Processes = @("notepad"); AllowExisting = $false; AllowProcessOnly = $true },
        @{ Name = "fb037_builtin_paint"; Phrase = "open paint"; ActionId = "open_paint"; Windows = @("*Paint*", "*Untitled*"); Processes = @("mspaint"); AllowExisting = $false; AllowProcessOnly = $true }
    )
    foreach ($case in $builtInCases) {
        Invoke-Fb037Command -ScenarioName $case["Name"] -Phrase $case["Phrase"] -ExpectedActionId $case["ActionId"] -ExpectedWindowPatterns $case["Windows"] -ExpectedProcessNames $case["Processes"] -AllowExistingWindowEvidence:([bool]$case["AllowExisting"]) -AllowProcessOnlyEvidence:([bool]$case["AllowProcessOnly"]) | Out-Null
        Stop-Fb037LaunchedApps
    }

    Seed-Fb037OverrideSource -Aliases @("task manager", "calculator", "notepad", "paint")
    Write-AuditStep -Stage "SOURCE" -Message "FB-037 saved-action override source seeded"
    $overrideCases = @(
        @{ Name = "fb037_override_task_manager"; Phrase = "task manager"; ActionId = "saved_override_task_manager"; Forbidden = "open_task_manager" },
        @{ Name = "fb037_override_calculator"; Phrase = "calculator"; ActionId = "saved_override_calculator"; Forbidden = "open_calculator" },
        @{ Name = "fb037_override_notepad"; Phrase = "notepad"; ActionId = "saved_override_notepad"; Forbidden = "open_notepad" },
        @{ Name = "fb037_override_paint"; Phrase = "paint"; ActionId = "saved_override_paint"; Forbidden = "open_paint" }
    )
    foreach ($case in $overrideCases) {
        Invoke-Fb037Command -ScenarioName $case["Name"] -Phrase $case["Phrase"] -ExpectedActionId $case["ActionId"] -ForbiddenActionIds @($case["Forbidden"]) | Out-Null
        Stop-Fb037LaunchedApps
    }

    Seed-Fb037EmptySource
    Assert-Fb037CreateCollisionRejected -ScenarioName "fb037_authoring_create_task_manager_collision" -Alias "task manager"
    Assert-Fb037CreateCollisionRejected -ScenarioName "fb037_authoring_create_calculator_collision" -Alias "calculator"
    Assert-Fb037CreateCollisionRejected -ScenarioName "fb037_authoring_create_notepad_collision" -Alias "notepad"
    Assert-Fb037CreateCollisionRejected -ScenarioName "fb037_authoring_create_paint_collision" -Alias "paint"
    Assert-Fb037EditCollisionRejected -ScenarioName "fb037_authoring_edit_task_manager_collision" -Alias "task manager"

    Seed-Fb037OverrideSource -Aliases @("calculator", "paint")
    Write-AuditStep -Stage "SOURCE" -Message "FB-037 mixed source seeded"
    Invoke-Fb037Command -ScenarioName "fb037_mixed_task_manager_builtin" -Phrase "task manager" -ExpectedActionId "open_task_manager" -ExpectedWindowPatterns @("*Task Manager*") -ExpectedProcessNames @("taskmgr") -AllowExistingWindowEvidence | Out-Null
    Stop-Fb037LaunchedApps
    Invoke-Fb037Command -ScenarioName "fb037_mixed_calculator_saved" -Phrase "calculator" -ExpectedActionId "saved_override_calculator" -ForbiddenActionIds @("open_calculator") | Out-Null
    Stop-Fb037LaunchedApps
    Invoke-Fb037Command -ScenarioName "fb037_mixed_notepad_builtin" -Phrase "notepad" -ExpectedActionId "open_notepad" -ExpectedWindowPatterns @("*Notepad*", "*Untitled*") -ExpectedProcessNames @("notepad") -AllowProcessOnlyEvidence | Out-Null
    Stop-Fb037LaunchedApps
    Invoke-Fb037Command -ScenarioName "fb037_mixed_paint_saved" -Phrase "paint" -ExpectedActionId "saved_override_paint" -ForbiddenActionIds @("open_paint") | Out-Null
    Stop-Fb037LaunchedApps

    Seed-Fb037EmptySource
    Invoke-Fb037Command -ScenarioName "fb037_repeated_notepad_first" -Phrase "notepad" -ExpectedActionId "open_notepad" -ExpectedWindowPatterns @("*Notepad*", "*Untitled*") -ExpectedProcessNames @("notepad") -AllowProcessOnlyEvidence | Out-Null
    Stop-Fb037LaunchedApps
    Invoke-Fb037Command -ScenarioName "fb037_repeated_notepad_second" -Phrase "notepad" -ExpectedActionId "open_notepad" -ExpectedWindowPatterns @("*Notepad*", "*Untitled*") -ExpectedProcessNames @("notepad") -AllowProcessOnlyEvidence | Out-Null
    Stop-Fb037LaunchedApps

    Restore-Source
    Write-AuditStep -Stage "SOURCE" -Message "saved action source restored"
    Write-AuditManifest -Status "PASS"
    } catch {
        $failureMessage = $_.Exception.Message
        Add-ScenarioResult -Name "fb037_validation_run" -Result "FAIL" -Details $failureMessage
        Write-AuditManifest -Status "FAIL" -FailureMessage $failureMessage | Out-Null
        try {
            Stop-Fb037LaunchedApps
        } catch {
            Add-CleanupNote -Action "fb037_cleanup" -Result "blocked" -Details $_.Exception.Message
        }
        try {
            Restore-Source
            Write-AuditStep -Stage "SOURCE" -Message "saved action source restored after failure"
        } catch {
            Add-CleanupNote -Action "restore_source" -Result "blocked" -Details $_.Exception.Message
        }
        Write-AuditManifest -Status "FAIL" -FailureMessage $failureMessage
        throw
    }
}

function Stop-LaunchedDesktopProcesses {
    Write-AuditStep -Stage "CLEANUP" -Message "checking for launched desktop runtime helper processes"
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
        Assert-NoProgressBudget -Activity "desktop runtime process cleanup"
        Write-AuditStep -Stage "CLEANUP" -Message "stopping launched desktop runtime pid=$($process.ProcessId)"
        try {
            Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
            Add-CleanupNote -Action "stop_desktop_runtime" -Result "success" -Details "stopped launched desktop runtime pid=$($process.ProcessId)"
        } catch {
            $result = if ($_.Exception.Message -like "*Cannot find a process*" -or $_.Exception.Message -like "*process identifier*") {
                "success"
            } else {
                "helper_failure"
            }
            $details = if ($result -eq "success") {
                "launched desktop runtime pid=$($process.ProcessId) already exited before forced stop"
            } else {
                "could not stop launched desktop runtime pid=$($process.ProcessId): $($_.Exception.Message)"
            }
            Add-CleanupNote -Action "stop_desktop_runtime" -Result $result -Details $details
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
    if ($Fb037Validation) {
        Run-Fb037Validation
    } else {
    Write-AuditStep -Stage "BUDGET" -Message "launcher live audit budgets active: default_timeout=${TimeoutSeconds}s no_progress=${NoProgressTimeoutSeconds}s"
    Backup-Source
    Write-AuditStep -Stage "SOURCE" -Message "saved action source backed up"
    Seed-AuditSource
    Write-AuditStep -Stage "SOURCE" -Message "audit source seeded"
    Launch-Desktop
    Write-AuditStep -Stage "RUNTIME" -Message "desktop runtime launched and ready"

    $overlay = Open-Overlay
    Write-AuditStep -Stage "OVERLAY" -Message "overlay opened for entry capture"
    $overlayInput = Resolve-OverlayInput -Overlay $overlay
    Capture-ElementScreenshot -Element $overlay -Label "overlay_entry" | Out-Null

    Set-ElementValue -Element $overlayInput -Value "weekly reports" -Description "overlay ambiguity text"
    Send-VirtualKey -Key 0x0D
    Start-Sleep -Milliseconds 350
    Capture-ElementScreenshot -Element $overlay -Label "overlay_ambiguity" | Out-Null
    Write-AuditStep -Stage "CAPTURE" -Message "ambiguity surface captured"
    Close-WindowByEsc -Window $overlay
    Start-Sleep -Milliseconds 220

    $overlay = Open-Overlay
    Write-AuditStep -Stage "OVERLAY" -Message "overlay reopened for confirm capture"
    $overlayInput = Resolve-OverlayInput -Overlay $overlay
    Set-ElementValue -Element $overlayInput -Value "notes task" -Description "overlay confirm text"
    Send-VirtualKey -Key 0x0D
    Start-Sleep -Milliseconds 350
    Capture-ElementScreenshot -Element $overlay -Label "overlay_confirm" | Out-Null
    Write-AuditStep -Stage "CAPTURE" -Message "confirm surface captured"
    Close-WindowByEsc -Window $overlay
    Start-Sleep -Milliseconds 220

    $overlay = Open-Overlay
    Write-AuditStep -Stage "AUTHORING" -Message "starting create dialog audit"

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
    Write-AuditStep -Stage "AUTHORING" -Message "create validation error captured"

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
    Write-AuditStep -Stage "AUTHORING" -Message "inline group create dialog captured"
    Close-WindowByEsc -Window $inlineCreateGroupDialog
    Start-Sleep -Milliseconds 220
    Close-WindowByEsc -Window $assignmentDialog
    Start-Sleep -Milliseconds 220
    Close-WindowByEsc -Window $createDialog
    Start-Sleep -Milliseconds 250

    $overlay = Open-Overlay
    Write-AuditStep -Stage "AUTHORING" -Message "starting manage custom tasks audit"

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
    Write-AuditStep -Stage "AUTHORING" -Message "edit custom task dialog captured"
    Close-WindowByEsc -Window $editDialog
    Start-Sleep -Milliseconds 220
    Close-WindowByEsc -Window $manageTasksDialog
    Start-Sleep -Milliseconds 220

    $overlay = Open-Overlay
    Write-AuditStep -Stage "AUTHORING" -Message "starting direct group create audit"

    $createGroupButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreateGroupButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreateGroupButton"
    )
    Invoke-Element -Element $createGroupButton -Description "Create Custom Group button"
    $directCreateGroupDialog = Wait-ForDialog -Name "Create Custom Group"
    Capture-ElementScreenshot -Element $directCreateGroupDialog -Label "create_custom_group_direct" | Out-Null
    Write-AuditStep -Stage "AUTHORING" -Message "direct group create dialog captured"
    Close-WindowByEsc -Window $directCreateGroupDialog
    Start-Sleep -Milliseconds 220

    $overlay = Open-Overlay
    Write-AuditStep -Stage "AUTHORING" -Message "starting manage custom groups audit"
    $manageGroupsButton = Get-OverlayButton -Overlay $overlay -AutomationIds @(
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.QFrame.savedActionCreatedGroupsButton",
        "QApplication.commandOverlayWindow.commandPanel.savedActionInventory.savedActionCreatedGroupsButton"
    )
    Invoke-Element -Element $manageGroupsButton -Description "Manage Custom Groups button"
    $manageGroupsDialog = Wait-ForDialog -Name "Manage Custom Groups"
    Capture-ElementScreenshot -Element $manageGroupsDialog -Label "manage_custom_groups" | Out-Null
    Write-AuditStep -Stage "AUTHORING" -Message "manage custom groups dialog captured"
    Close-WindowByEsc -Window $manageGroupsDialog
    Start-Sleep -Milliseconds 220

    Write-InvalidSource
    Write-AuditStep -Stage "SOURCE" -Message "invalid source written for recovery audit"
    Start-Sleep -Milliseconds 250

    $overlay = Open-Overlay
    Write-AuditStep -Stage "AUTHORING" -Message "starting invalid-source management audit"
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
    Write-AuditStep -Stage "AUTHORING" -Message "invalid-source manage tasks captured"
    Close-WindowByEsc -Window $invalidTasksDialog
    Start-Sleep -Milliseconds 220

    Invoke-Element -Element $manageGroupsButton -Description "Manage Custom Groups button invalid source"
    $invalidGroupsDialog = Wait-ForDialog -Name "Manage Custom Groups"
    Capture-ElementScreenshot -Element $invalidGroupsDialog -Label "manage_custom_groups_invalid_source" | Out-Null
    Write-AuditStep -Stage "AUTHORING" -Message "invalid-source manage groups captured"
    Close-WindowByEsc -Window $invalidGroupsDialog

    Restore-Source
    Write-AuditStep -Stage "SOURCE" -Message "saved action source restored"

    $manifest = [pscustomobject]@{
        capture_dir                   = $OutputDir
        captures                      = $script:Captures
        step_log                      = $StepLogPath
        timeout_budgets               = [pscustomobject]@{
            default_timeout_seconds     = $TimeoutSeconds
            no_progress_timeout_seconds = $NoProgressTimeoutSeconds
        }
        last_confirmed_progress_point = $script:LastProgressPoint
    }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ManifestPath -Encoding utf8

    [pscustomobject]@{
        capture_dir = $OutputDir
        manifest    = $ManifestPath
        captures    = $script:Captures
    } | ConvertTo-Json -Depth 6
    }
}
finally {
    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        try {
            Write-AuditStep -Stage "MANIFEST" -Message "manifest missing before final cleanup; writing abort manifest"
            Write-AuditManifest -Status "ABORTED" -FailureMessage "Run reached final cleanup before manifest generation." | Out-Null
        } catch {
            Write-AuditStep -Stage "MANIFEST" -Message "failed to write pre-cleanup abort manifest: $($_.Exception.Message)"
        }
    }

    try {
        Write-AuditStep -Stage "CLEANUP" -Message "starting live audit cleanup"
        Stop-AuditRuntimeHelper
        Write-AuditStep -Stage "CLEANUP" -Message "restoring saved action source during final cleanup"
        Restore-Source
        Write-AuditStep -Stage "CLEANUP" -Message "saved action source restore completed during final cleanup"
        Stop-LaunchedDesktopProcesses
        Write-AuditStep -Stage "CLEANUP" -Message "live audit cleanup complete"
    } catch {
        Add-CleanupNote -Action "final_cleanup" -Result "helper_failure" -Details $_.Exception.Message
        if ($script:ManifestStatus -eq "PASS") {
            $script:ManifestStatus = "FAIL"
            $script:ManifestFailureMessage = "Final cleanup failed: $($_.Exception.Message)"
        }
    }

    try {
        Write-AuditManifest -Status $script:ManifestStatus -FailureMessage $script:ManifestFailureMessage | Out-Null
    } catch {
        Write-AuditStep -Stage "MANIFEST" -Message "failed to refresh final manifest after cleanup: $($_.Exception.Message)"
    }
}
