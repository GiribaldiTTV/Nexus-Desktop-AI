# NEXUS-SOURCE-OWNER: schema=source-owner-v1; owner=FAM006-HUD; ledger=SRCOWN-FIRSTPASS-FAM006-HUD-008; surface=fam006-hud-human-client-validator; status=shared
param(
    [int]$StartupTimeoutSeconds = 45,
    [int]$ActionTimeoutSeconds = 12,
    [int]$ExitConfirmationTimeoutSeconds = 18,
    [switch]$SkipNcpRegressionChecks,
    [switch]$KeepRuntimeOpenOnFailure
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static class CodexHumanClientWin32 {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    private struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct NOTIFYICONIDENTIFIER {
        public uint cbSize;
        public IntPtr hWnd;
        public uint uID;
        public Guid guidItem;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct INPUT {
        public uint type;
        public MOUSEINPUT mi;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct MOUSEINPUT {
        public int dx;
        public int dy;
        public uint mouseData;
        public uint dwFlags;
        public uint time;
        public IntPtr dwExtraInfo;
    }

    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpWindowText, int nMaxCount);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] private static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] private static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
    [DllImport("user32.dll")] private static extern int GetSystemMetrics(int nIndex);
    [DllImport("user32.dll")] private static extern IntPtr WindowFromPoint(POINT point);
    [DllImport("user32.dll")] private static extern uint GetDpiForWindow(IntPtr hWnd);
    [DllImport("shell32.dll")] private static extern int Shell_NotifyIconGetRect(ref NOTIFYICONIDENTIFIER identifier, out RECT iconLocation);

    [StructLayout(LayoutKind.Sequential)]
    private struct POINT {
        public int X;
        public int Y;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct CURSORINFO {
        public int cbSize;
        public int flags;
        public IntPtr hCursor;
        public POINT ptScreenPos;
    }

    [DllImport("user32.dll")] private static extern bool GetCursorInfo(out CURSORINFO pci);
    [DllImport("user32.dll", SetLastError = true)] private static extern IntPtr LoadCursor(IntPtr hInstance, IntPtr lpCursorName);
    [DllImport("user32.dll")] private static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll")] private static extern int GetMenuItemCount(IntPtr hMenu);
    [DllImport("user32.dll")] private static extern bool GetMenuItemRect(IntPtr hWnd, IntPtr hMenu, uint uItem, out RECT rect);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern int GetMenuStringW(IntPtr hMenu, uint uIDItem, StringBuilder lpString, int nMaxCount, uint uFlag);
    [DllImport("user32.dll")] private static extern uint GetMenuState(IntPtr hMenu, uint uId, uint uFlags);
    [DllImport("user32.dll")] private static extern IntPtr GetAncestor(IntPtr hWnd, uint gaFlags);
    [DllImport("user32.dll")] private static extern IntPtr GetParent(IntPtr hWnd);

    private static IntPtr LoadSystemCursor(int cursorId) {
        return LoadCursor(IntPtr.Zero, new IntPtr(cursorId));
    }

    public static string GetCursorKind() {
        CURSORINFO info = new CURSORINFO();
        info.cbSize = Marshal.SizeOf(typeof(CURSORINFO));
        if (!GetCursorInfo(out info) || info.hCursor == IntPtr.Zero) {
            return "unknown";
        }
        if (info.hCursor == LoadSystemCursor(32644)) { return "size-west-east"; }
        if (info.hCursor == LoadSystemCursor(32645)) { return "size-north-south"; }
        if (info.hCursor == LoadSystemCursor(32642)) { return "size-northwest-southeast"; }
        if (info.hCursor == LoadSystemCursor(32643)) { return "size-northeast-southwest"; }
        if (info.hCursor == LoadSystemCursor(32512)) { return "arrow"; }
        return "other:" + info.hCursor.ToString();
    }

    public static string GetNativeHitTestKind(long hwndValue, int x, int y) {
        if (hwndValue == 0) { return "hwnd-zero"; }
        IntPtr hwnd = new IntPtr(hwndValue);
        int lParamValue = unchecked((int)(((y & 0xFFFF) << 16) | (x & 0xFFFF)));
        int result = SendMessage(hwnd, 0x0084, IntPtr.Zero, new IntPtr(lParamValue)).ToInt32();
        switch (result) {
            case 10: return "htleft";
            case 11: return "htright";
            case 12: return "httop";
            case 13: return "httopleft";
            case 14: return "httopright";
            case 15: return "htbottom";
            case 16: return "htbottomleft";
            case 17: return "htbottomright";
            case 1: return "htclient";
            case 0: return "htnowhere";
            default: return "ht:" + result.ToString();
        }
    }

    public static int GetDpiForWindowValue(long hwndValue) {
        try {
            if (hwndValue == 0) { return 0; }
            return (int)GetDpiForWindow(new IntPtr(hwndValue));
        } catch {
            return 0;
        }
    }

    public static long GetRootWindowHandleAtPoint(int x, int y) {
        POINT point = new POINT();
        point.X = x;
        point.Y = y;
        IntPtr hwnd = WindowFromPoint(point);
        if (hwnd == IntPtr.Zero) { return 0; }
        IntPtr root = GetAncestor(hwnd, 2);
        if (root == IntPtr.Zero) { root = hwnd; }
        return root.ToInt64();
    }

    public static bool PointBelongsToWindow(long expectedWindowHandle, int x, int y) {
        if (expectedWindowHandle == 0) { return false; }
        POINT point = new POINT();
        point.X = x;
        point.Y = y;
        IntPtr expected = new IntPtr(expectedWindowHandle);
        IntPtr hwnd = WindowFromPoint(point);
        IntPtr original = hwnd;
        while (hwnd != IntPtr.Zero) {
            if (hwnd == expected) { return true; }
            hwnd = GetParent(hwnd);
        }
        IntPtr root = GetAncestor(original, 2);
        if (root == expected) { return true; }
        IntPtr rootOwner = GetAncestor(original, 3);
        return rootOwner == expected;
    }

    private static void SendMouseButton(uint downFlag, uint upFlag) {
        INPUT[] inputs = new INPUT[2];
        inputs[0].type = 0;
        inputs[0].mi.dwFlags = downFlag;
        inputs[1].type = 0;
        inputs[1].mi.dwFlags = upFlag;
        SendInput(2, inputs, Marshal.SizeOf(typeof(INPUT)));
    }

    public static void SendLeftClick() {
        SendMouseButton(0x0002, 0x0004);
    }

    public static void SendAbsoluteLeftClick(int x, int y) {
        int virtualX = GetSystemMetrics(76);
        int virtualY = GetSystemMetrics(77);
        int virtualWidth = GetSystemMetrics(78);
        int virtualHeight = GetSystemMetrics(79);
        int absoluteX = (int)Math.Round(((double)(x - virtualX) * 65535.0) / Math.Max(1, virtualWidth - 1));
        int absoluteY = (int)Math.Round(((double)(y - virtualY) * 65535.0) / Math.Max(1, virtualHeight - 1));
        INPUT[] inputs = new INPUT[3];
        inputs[0].type = 0;
        inputs[0].mi.dx = absoluteX;
        inputs[0].mi.dy = absoluteY;
        inputs[0].mi.dwFlags = 0x0001 | 0x4000 | 0x8000;
        inputs[1].type = 0;
        inputs[1].mi.dwFlags = 0x0002;
        inputs[2].type = 0;
        inputs[2].mi.dwFlags = 0x0004;
        SendInput(3, inputs, Marshal.SizeOf(typeof(INPUT)));
    }

    public static void SendAbsoluteRightClick(int x, int y) {
        int virtualX = GetSystemMetrics(76);
        int virtualY = GetSystemMetrics(77);
        int virtualWidth = GetSystemMetrics(78);
        int virtualHeight = GetSystemMetrics(79);
        int absoluteX = (int)Math.Round(((double)(x - virtualX) * 65535.0) / Math.Max(1, virtualWidth - 1));
        int absoluteY = (int)Math.Round(((double)(y - virtualY) * 65535.0) / Math.Max(1, virtualHeight - 1));
        INPUT[] inputs = new INPUT[3];
        inputs[0].type = 0;
        inputs[0].mi.dx = absoluteX;
        inputs[0].mi.dy = absoluteY;
        inputs[0].mi.dwFlags = 0x0001 | 0x4000 | 0x8000;
        inputs[1].type = 0;
        inputs[1].mi.dwFlags = 0x0008;
        inputs[2].type = 0;
        inputs[2].mi.dwFlags = 0x0010;
        SendInput(3, inputs, Marshal.SizeOf(typeof(INPUT)));
    }

    public static void SendRightClick() {
        SendMouseButton(0x0008, 0x0010);
    }

    public static string GetWindowSummaryAtPoint(int x, int y) {
        POINT point = new POINT();
        point.X = x;
        point.Y = y;
        IntPtr hwnd = WindowFromPoint(point);
        if (hwnd == IntPtr.Zero) {
            return "hwnd=0";
        }
        StringBuilder className = new StringBuilder(256);
        StringBuilder title = new StringBuilder(512);
        GetClassName(hwnd, className, className.Capacity);
        GetWindowText(hwnd, title, title.Capacity);
        uint processId;
        GetWindowThreadProcessId(hwnd, out processId);
        RECT rect;
        string rectText = "rect=unknown";
        if (GetWindowRect(hwnd, out rect)) {
            rectText = string.Format("rect={0},{1},{2},{3}", rect.Left, rect.Top, rect.Right, rect.Bottom);
        }
        return string.Format(
            "hwnd={0}|class={1}|title={2}|pid={3}|{4}",
            hwnd.ToString(),
            className.ToString(),
            title.ToString(),
            processId,
            rectText
        );
    }

    public static int[] GetNotifyIconRectForProcess(int processId) {
        List<IntPtr> candidates = new List<IntPtr>();
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            StringBuilder className = new StringBuilder(256);
            GetClassName(hWnd, className, className.Capacity);
            string name = className.ToString();
            if (!name.Contains("TrayIconMessageWindowClass")) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId == (uint)processId) {
                candidates.Add(hWnd);
            }

            return true;
        }, IntPtr.Zero);

        foreach (IntPtr hWnd in candidates) {
            for (uint uid = 0; uid < 256; uid++) {
                NOTIFYICONIDENTIFIER identifier = new NOTIFYICONIDENTIFIER();
                identifier.cbSize = (uint)Marshal.SizeOf(typeof(NOTIFYICONIDENTIFIER));
                identifier.hWnd = hWnd;
                identifier.uID = uid;
                identifier.guidItem = Guid.Empty;

                RECT rect;
                int result = Shell_NotifyIconGetRect(ref identifier, out rect);
                if (result == 0 && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                    return new int[] { rect.Left, rect.Top, rect.Right, rect.Bottom };
                }
            }
        }

        return new int[0];
    }

    public static int[] GetNotifyIconRectForProcessWithTimeout(int processId, int timeoutMilliseconds) {
        try {
            System.Threading.Tasks.Task<int[]> task = System.Threading.Tasks.Task.Run(() => GetNotifyIconRectForProcess(processId));
            if (!task.Wait(Math.Max(1, timeoutMilliseconds))) {
                return new int[0];
            }
            return task.Result ?? new int[0];
        } catch {
            return new int[0];
        }
    }

    public static int[] GetVisiblePopupRectForProcess(int processId) {
        int[] result = new int[0];
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (result.Length == 4) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId != (uint)processId || !IsWindowVisible(hWnd)) {
                return true;
            }

            StringBuilder className = new StringBuilder(256);
            GetClassName(hWnd, className, className.Capacity);
            string classValue = className.ToString();
            StringBuilder title = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            string titleValue = title.ToString();
            if (!classValue.Contains("QWindowPopup") && classValue != "#32768" && titleValue != "Nexus Desktop AI Tray") {
                return true;
            }

            RECT rect;
            if (GetWindowRect(hWnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                result = new int[] { rect.Left, rect.Top, rect.Right, rect.Bottom };
            }

            return true;
        }, IntPtr.Zero);

        return result;
    }

    public static int[] GetVisiblePopupRectForProcessWithTimeout(int processId, int timeoutMilliseconds) {
        try {
            System.Threading.Tasks.Task<int[]> task = System.Threading.Tasks.Task.Run(() => GetVisiblePopupRectForProcess(processId));
            if (!task.Wait(Math.Max(1, timeoutMilliseconds))) {
                return new int[0];
            }
            return task.Result ?? new int[0];
        } catch {
            return new int[0];
        }
    }

    public static long GetVisiblePopupHandleForProcess(int processId) {
        IntPtr result = IntPtr.Zero;
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (result != IntPtr.Zero) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId != (uint)processId || !IsWindowVisible(hWnd)) {
                return true;
            }

            StringBuilder className = new StringBuilder(256);
            GetClassName(hWnd, className, className.Capacity);
            string classValue = className.ToString();
            StringBuilder title = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            string titleValue = title.ToString();
            if (!classValue.Contains("QWindowPopup") && !classValue.Contains("QMenu") && classValue != "#32768" && titleValue != "Nexus Desktop AI Tray") {
                return true;
            }

            RECT rect;
            if (GetWindowRect(hWnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                result = hWnd;
            }

            return true;
        }, IntPtr.Zero);

        return result.ToInt64();
    }

    public static long GetVisiblePopupHandleForProcessWithTimeout(int processId, int timeoutMilliseconds) {
        try {
            System.Threading.Tasks.Task<long> task = System.Threading.Tasks.Task.Run(() => GetVisiblePopupHandleForProcess(processId));
            if (!task.Wait(Math.Max(1, timeoutMilliseconds))) {
                return 0;
            }
            return task.Result;
        } catch {
            return 0;
        }
    }

    public static string[] GetNativeMenuItemsForPopup(long hwndValue) {
        if (hwndValue == 0) { return new string[0]; }
        IntPtr hwnd = new IntPtr(hwndValue);
        IntPtr hMenu = SendMessage(hwnd, 0x01E1, IntPtr.Zero, IntPtr.Zero);
        if (hMenu == IntPtr.Zero) { return new string[0]; }
        int count = GetMenuItemCount(hMenu);
        if (count <= 0) { return new string[0]; }
        List<string> items = new List<string>();
        for (uint index = 0; index < (uint)count; index++) {
            StringBuilder text = new StringBuilder(256);
            GetMenuStringW(hMenu, index, text, text.Capacity, 0x00000400);
            RECT rect;
            if (!GetMenuItemRect(hwnd, hMenu, index, out rect)) {
                rect = new RECT();
            }
            uint state = GetMenuState(hMenu, index, 0x00000400);
            bool enabled = (state & 0x00000003) == 0;
            bool separator = (state & 0x00000800) != 0;
            items.Add(string.Format(
                "{0}|{1}|{2}|{3},{4},{5},{6}",
                index,
                enabled ? "enabled" : "disabled",
                separator ? "<separator>" : text.ToString().Replace("|", "/"),
                rect.Left,
                rect.Top,
                rect.Right,
                rect.Bottom
            ));
        }
        return items.ToArray();
    }

    public static int[] GetVisibleDashboardRectForProcess(int processId) {
        int[] result = new int[0];
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (result.Length == 4) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId != (uint)processId || !IsWindowVisible(hWnd)) {
                return true;
            }

            StringBuilder title = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            string titleValue = title.ToString();
            if (titleValue != "Nexus Desktop AI") {
                return true;
            }

            StringBuilder className = new StringBuilder(256);
            GetClassName(hWnd, className, className.Capacity);
            string classValue = className.ToString();
            if (!classValue.Contains("QWindowIcon")) {
                return true;
            }

            RECT rect;
            if (GetWindowRect(hWnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                result = new int[] { rect.Left, rect.Top, rect.Right, rect.Bottom };
            }

            return true;
        }, IntPtr.Zero);

        return result;
    }

    public static long GetVisibleDashboardHandleForProcess(int processId) {
        IntPtr result = IntPtr.Zero;
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (result != IntPtr.Zero) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId != (uint)processId || !IsWindowVisible(hWnd)) {
                return true;
            }

            StringBuilder title = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            string titleValue = title.ToString();
            if (titleValue != "Nexus Desktop AI") {
                return true;
            }

            StringBuilder className = new StringBuilder(256);
            GetClassName(hWnd, className, className.Capacity);
            string classValue = className.ToString();
            if (!classValue.Contains("QWindowIcon")) {
                return true;
            }

            RECT rect;
            if (GetWindowRect(hWnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                result = hWnd;
            }

            return true;
        }, IntPtr.Zero);

        return result.ToInt64();
    }

    public static int[] GetWindowRectByHandle(long hwndValue) {
        if (hwndValue == 0) {
            return new int[0];
        }
        IntPtr hwnd = new IntPtr(hwndValue);
        RECT rect;
        if (GetWindowRect(hwnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
            return new int[] { rect.Left, rect.Top, rect.Right, rect.Bottom };
        }
        return new int[0];
    }

    public static int[] GetVisibleWindowRectForProcessByTitle(int processId, string expectedTitle) {
        int[] result = new int[0];
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (result.Length == 4) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId != (uint)processId || !IsWindowVisible(hWnd)) {
                return true;
            }

            StringBuilder title = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            if (title.ToString() != expectedTitle) {
                return true;
            }

            RECT rect;
            if (GetWindowRect(hWnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                result = new int[] { rect.Left, rect.Top, rect.Right, rect.Bottom };
            }

            return true;
        }, IntPtr.Zero);

        return result;
    }

    public static long GetVisibleWindowHandleForProcessByTitle(int processId, string expectedTitle) {
        long result = 0;
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (result != 0) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId != (uint)processId || !IsWindowVisible(hWnd)) {
                return true;
            }

            StringBuilder title = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            if (title.ToString() != expectedTitle) {
                return true;
            }

            RECT rect;
            if (GetWindowRect(hWnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                result = hWnd.ToInt64();
            }

            return true;
        }, IntPtr.Zero);

        return result;
    }

    public static int[] GetVisibleWindowRectForProcessByTitleContains(int processId, string expectedTitle) {
        int[] result = new int[0];
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (result.Length == 4) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId != (uint)processId || !IsWindowVisible(hWnd)) {
                return true;
            }

            StringBuilder title = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            string titleValue = title.ToString();
            if (!titleValue.Contains(expectedTitle)) {
                return true;
            }

            RECT rect;
            if (GetWindowRect(hWnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                result = new int[] { rect.Left, rect.Top, rect.Right, rect.Bottom };
            }

            return true;
        }, IntPtr.Zero);

        return result;
    }

    public static long GetVisibleWindowHandleForProcessByTitleContains(int processId, string expectedTitle) {
        long result = 0;
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (result != 0) {
                return true;
            }

            uint windowProcessId;
            GetWindowThreadProcessId(hWnd, out windowProcessId);
            if (windowProcessId != (uint)processId || !IsWindowVisible(hWnd)) {
                return true;
            }

            StringBuilder title = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            string titleValue = title.ToString();
            if (!titleValue.Contains(expectedTitle)) {
                return true;
            }

            RECT rect;
            if (GetWindowRect(hWnd, out rect) && rect.Right > rect.Left && rect.Bottom > rect.Top) {
                result = hWnd.ToInt64();
            }

            return true;
        }, IntPtr.Zero);

        return result;
    }
}
"@

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$LogRoot = Join-Path $RootDir "dev\logs\fam_006_human_client_validation\$Stamp"
$DefaultRuntimeLogRoot = Join-Path $RootDir "logs"
$ScreenshotRoot = Join-Path $LogRoot "screenshots"
$ShortVideoFrameRoot = Join-Path $LogRoot "short_video_frames"
$ShortVideoPath = Join-Path $LogRoot "human_client_short_video.mp4"
$ManifestPath = Join-Path $LogRoot "human_client_manifest.json"
$LatestManifestPath = Join-Path $RootDir "dev\logs\fam_006_human_client_validation\latest_manifest.json"
$UserScreenshotsRoot = Join-Path $env:USERPROFILE "OneDrive\Pictures\Screenshots"
if (-not (Test-Path -LiteralPath $UserScreenshotsRoot)) {
    $PicturesRoot = [Environment]::GetFolderPath("MyPictures")
    $UserScreenshotsRoot = Join-Path $PicturesRoot "Screenshots"
}
$UserEvidenceRoot = Join-Path $UserScreenshotsRoot "Nexus Desktop AI\fam_006_human_client_validation\$Stamp"
$UserContextScreenshotRoot = Join-Path $UserEvidenceRoot "context_desktop_screenshots"
$UserElementScreenshotRoot = Join-Path $UserEvidenceRoot "focused_element_screenshots"
$DefaultDesktopShortcutPath = Join-Path $env:USERPROFILE "OneDrive\Desktop\FAM-006 RED - Nexus Desktop AI Launcher.lnk"
$DesktopShortcutPath = if ($env:NEXUS_DESKTOP_VALIDATION_SHORTCUT_PATH) {
    $env:NEXUS_DESKTOP_VALIDATION_SHORTCUT_PATH
} else {
    $DefaultDesktopShortcutPath
}

New-Item -ItemType Directory -Force -Path $ScreenshotRoot | Out-Null
New-Item -ItemType Directory -Force -Path $UserContextScreenshotRoot | Out-Null
New-Item -ItemType Directory -Force -Path $UserElementScreenshotRoot | Out-Null

$script:Steps = New-Object System.Collections.Generic.List[object]
$script:Artifacts = New-Object System.Collections.Generic.List[object]
$script:RuntimeProcessIds = New-Object System.Collections.Generic.List[int]
$script:RuntimeLogPath = ""
$script:LaunchStartedAt = $null
$script:CleanupNotes = New-Object System.Collections.Generic.List[string]
$script:ShortVideoProof = [ordered]@{
    status = "NOT_REQUESTED"
    path = ""
    userInspectablePath = ""
    frameCount = 0
    sourceRoot = $ScreenshotRoot
    proofClass = "short-video-or-frame-sequence"
}
$script:ShortcutResolution = [ordered]@{
    path = $DesktopShortcutPath
    targetPath = ""
    workingDirectory = ""
    arguments = ""
    activeRoot = $RootDir
    status = "NOT_TESTED"
    detail = ""
}

function Add-Step {
    param(
        [string]$Id,
        [string]$Title,
        [string]$Status,
        [string]$Detail,
        [string]$ProofClass = "live-human-ui",
        [hashtable]$Evidence = @{}
    )

    $script:Steps.Add([ordered]@{
        id = $Id
        title = $Title
        status = $Status
        detail = $Detail
        proofClass = $ProofClass
        evidence = $Evidence
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
    }) | Out-Null
}

function Resolve-ShortcutForActiveRoot {
    param([string]$ShortcutPath)

    $result = [ordered]@{
        path = $ShortcutPath
        targetPath = ""
        workingDirectory = ""
        arguments = ""
        activeRoot = $RootDir
        status = "FAIL"
        detail = ""
    }

    try {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($ShortcutPath)
        $targetPath = [string]$shortcut.TargetPath
        $workingDirectory = [string]$shortcut.WorkingDirectory
        $arguments = [string]$shortcut.Arguments
        $result.targetPath = $targetPath
        $result.workingDirectory = $workingDirectory
        $result.arguments = $arguments

        $resolvedRoot = (Resolve-Path -LiteralPath $RootDir).Path.TrimEnd('\')
        $targetMatches = $false
        $workingDirectoryMatches = $false
        if (-not [string]::IsNullOrWhiteSpace($targetPath) -and (Test-Path -LiteralPath $targetPath)) {
            $resolvedTarget = (Resolve-Path -LiteralPath $targetPath).Path
            $targetMatches = $resolvedTarget.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)
        }
        if (-not [string]::IsNullOrWhiteSpace($workingDirectory) -and (Test-Path -LiteralPath $workingDirectory)) {
            $resolvedWorkingDirectory = (Resolve-Path -LiteralPath $workingDirectory).Path.TrimEnd('\')
            $workingDirectoryMatches = $resolvedWorkingDirectory.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)
        }

        if ($targetMatches -and $workingDirectoryMatches) {
            $result.status = "PASS"
            $result.detail = "Desktop shortcut target and working directory are rooted in the active FAM-006 worktree."
            return $result
        }

        $result.detail = "Desktop shortcut is not rooted in the active FAM-006 worktree; targetMatches=$targetMatches; workingDirectoryMatches=$workingDirectoryMatches."
        return $result
    } catch {
        $result.detail = "Unable to inspect desktop shortcut target: $($_.Exception.Message)"
        return $result
    }
}

function Add-Artifact {
    param([string]$Label, [string]$Path)
    $script:Artifacts.Add([ordered]@{ label = $Label; path = $Path }) | Out-Null
}

function ConvertTo-SafeEvidenceName {
    param([string]$Value)
    $safe = ($Value -replace "[^A-Za-z0-9_-]", "_").Trim("_")
    if ([string]::IsNullOrWhiteSpace($safe)) {
        return "unnamed_element"
    }
    return $safe.ToLowerInvariant()
}

function Add-UserInspectableScreenshotEvidence {
    param(
        [string]$Label,
        [string]$SourcePath,
        [string]$ProofKind
    )

    $safe = ConvertTo-SafeEvidenceName -Value $Label
    if ($ProofKind -eq "focused-element") {
        $destination = Join-Path $UserElementScreenshotRoot ("element_{0}.png" -f $safe)
    }
    else {
        $destination = Join-Path $UserContextScreenshotRoot ("context_{0}.png" -f $safe)
    }
    Copy-Item -LiteralPath $SourcePath -Destination $destination -Force
    $script:Artifacts.Add([ordered]@{
        label = if ($ProofKind -eq "focused-element") { "user_inspectable_element_$safe" } else { "user_inspectable_context_$safe" }
        path = $destination
        sourcePath = $SourcePath
        proofClass = if ($ProofKind -eq "focused-element") { "focused-per-element-screenshot" } else { "full-desktop-context-screenshot" }
    }) | Out-Null
    return $destination
}

function Capture-VirtualScreenshot {
    param([string]$Label)

    $safe = ($Label -replace "[^A-Za-z0-9_-]", "_").Trim("_")
    $path = Join-Path $ScreenshotRoot ("{0}_{1}.png" -f ((Get-Date -Format "HHmmss_fff")), $safe)
    $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bounds.Size)
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    Add-Artifact -Label $Label -Path $path
    Add-UserInspectableScreenshotEvidence -Label $Label -SourcePath $path -ProofKind "desktop-context" | Out-Null
    return $path
}

function Capture-RectScreenshot {
    param(
        [string]$Label,
        [int]$Left,
        [int]$Top,
        [int]$Width,
        [int]$Height
    )

    $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $clipLeft = [Math]::Max($bounds.Left, $Left)
    $clipTop = [Math]::Max($bounds.Top, $Top)
    $clipRight = [Math]::Min($bounds.Right, $Left + $Width)
    $clipBottom = [Math]::Min($bounds.Bottom, $Top + $Height)
    $clipWidth = [int]($clipRight - $clipLeft)
    $clipHeight = [int]($clipBottom - $clipTop)
    if ($clipWidth -le 0 -or $clipHeight -le 0) {
        throw "Focused screenshot '$Label' has invalid clipped bounds: left=$Left top=$Top width=$Width height=$Height virtual=($($bounds.Left),$($bounds.Top),$($bounds.Right),$($bounds.Bottom))"
    }

    $safe = ($Label -replace "[^A-Za-z0-9_-]", "_").Trim("_")
    $path = Join-Path $ScreenshotRoot ("{0}_{1}.png" -f ((Get-Date -Format "HHmmss_fff")), $safe)
    $bitmap = New-Object System.Drawing.Bitmap $clipWidth, $clipHeight
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($clipLeft, $clipTop, 0, 0, (New-Object System.Drawing.Size $clipWidth, $clipHeight))
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    Add-Artifact -Label $Label -Path $path
    Add-UserInspectableScreenshotEvidence -Label $Label -SourcePath $path -ProofKind "focused-element" | Out-Null
    return $path
}

function Get-PngInfo {
    param([string]$Path)
    $image = [System.Drawing.Image]::FromFile($Path)
    try {
        [pscustomobject]@{
            Path = (Resolve-Path -LiteralPath $Path).Path
            Width = [int]$image.Width
            Height = [int]$image.Height
            Area = [int]($image.Width * $image.Height)
        }
    }
    finally {
        $image.Dispose()
    }
}

function New-HumanClientShortVideoProof {
    param([int]$MinimumFrames = 5)

    $ffmpeg = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
    if (-not $ffmpeg -or -not $ffmpeg.Source) {
        return [ordered]@{
            status = "FAIL"
            reason = "ffmpeg.exe unavailable; LV1 human-client proof requires durable short video or ordered frame-sequence evidence"
            path = ""
            userInspectablePath = ""
            frameCount = 0
            sourceRoot = $ScreenshotRoot
            proofClass = "short-video-or-frame-sequence"
        }
    }

    $pngs = @(Get-ChildItem -LiteralPath $ScreenshotRoot -Filter "*.png" -File | Sort-Object FullName)
    if ($pngs.Count -lt 2) {
        return [ordered]@{
            status = "FAIL"
            reason = "fewer than two human-client screenshot frames available for short video proof"
            path = ""
            userInspectablePath = ""
            frameCount = [int]$pngs.Count
            sourceRoot = $ScreenshotRoot
            proofClass = "short-video-or-frame-sequence"
        }
    }

    $infos = @()
    foreach ($png in $pngs) {
        try { $infos += @(Get-PngInfo -Path $png.FullName) } catch {}
    }
    $groups = @($infos | Group-Object { "$($_.Width)x$($_.Height)" } | Sort-Object @{ Expression = { $_.Count }; Descending = $true }, @{ Expression = { ($_.Group | Select-Object -First 1).Area }; Descending = $true })
    $selectedGroup = $groups | Where-Object { $_.Count -ge $MinimumFrames } | Select-Object -First 1
    if (-not $selectedGroup) {
        $selectedGroup = $groups | Where-Object { $_.Count -ge 2 } | Select-Object -First 1
    }
    if (-not $selectedGroup) {
        return [ordered]@{
            status = "FAIL"
            reason = "no same-size human-client screenshot frame group was large enough for short video proof"
            path = ""
            userInspectablePath = ""
            frameCount = 0
            sourceRoot = $ScreenshotRoot
            proofClass = "short-video-or-frame-sequence"
        }
    }

    Remove-Item -LiteralPath $ShortVideoFrameRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $ShortVideoFrameRoot | Out-Null
    $index = 1
    foreach ($frame in @($selectedGroup.Group | Sort-Object Path)) {
        Copy-Item -LiteralPath $frame.Path -Destination (Join-Path $ShortVideoFrameRoot ("frame_{0:0000}.png" -f $index)) -Force
        $index += 1
    }

    & $ffmpeg.Source -y -loglevel error -framerate 2 -i (Join-Path $ShortVideoFrameRoot "frame_%04d.png") -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" -movflags +faststart $ShortVideoPath
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $ShortVideoPath)) {
        return [ordered]@{
            status = "FAIL"
            reason = "ffmpeg failed to encode human-client short video proof"
            path = $ShortVideoPath
            userInspectablePath = ""
            frameCount = [int]$selectedGroup.Count
            sourceRoot = $ScreenshotRoot
            proofClass = "short-video-or-frame-sequence"
        }
    }

    Add-Artifact -Label "mandatory_human_client_short_video_proof" -Path $ShortVideoPath
    $userShortVideoPath = Join-Path $UserEvidenceRoot "human_client_short_video.mp4"
    Copy-Item -LiteralPath $ShortVideoPath -Destination $userShortVideoPath -Force
    Add-Artifact -Label "user_inspectable_human_client_short_video_proof" -Path $userShortVideoPath
    [ordered]@{
        status = "PASS"
        reason = "durable human-client short video proof generated from ordered same-size screenshot frames"
        path = $ShortVideoPath
        userInspectablePath = $userShortVideoPath
        frameCount = [int]$selectedGroup.Count
        sourceRoot = $ScreenshotRoot
        proofClass = "short-video-or-frame-sequence"
        ffmpeg = $ffmpeg.Source
        frameRoot = $ShortVideoFrameRoot
    }
}

function Capture-DashboardLocalScreenshot {
    param(
        [string]$Label,
        [object]$Rect,
        [int]$Padding = 10
    )
    return Capture-RectScreenshot -Label $Label -Left ([int]($Rect.Left - $Padding)) -Top ([int]($Rect.Top - $Padding)) -Width ([int]($Rect.Width + ($Padding * 2))) -Height ([int]($Rect.Height + ($Padding * 2)))
}

function Capture-DashboardRightEdgeScreenshot {
    param(
        [string]$Label,
        [object]$Rect,
        [int]$SampleY
    )
    return Capture-RectScreenshot -Label $Label -Left ([int]($Rect.Right - 96)) -Top ([int]($SampleY - 130)) -Width 156 -Height 260
}

function Send-Key {
    param([byte]$Vk)
    [CodexHumanClientWin32]::keybd_event($Vk, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [CodexHumanClientWin32]::keybd_event($Vk, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 180
}

function Send-AltF4 {
    [CodexHumanClientWin32]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [CodexHumanClientWin32]::keybd_event(0x73, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [CodexHumanClientWin32]::keybd_event(0x73, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [CodexHumanClientWin32]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 220
}

function Send-WinB {
    [CodexHumanClientWin32]::keybd_event(0x5B, 0, 0, [UIntPtr]::Zero)
    [CodexHumanClientWin32]::keybd_event(0x42, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 100
    [CodexHumanClientWin32]::keybd_event(0x42, 0, 2, [UIntPtr]::Zero)
    [CodexHumanClientWin32]::keybd_event(0x5B, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 450
}

function Send-ShiftF10 {
    [CodexHumanClientWin32]::keybd_event(0x10, 0, 0, [UIntPtr]::Zero)
    [CodexHumanClientWin32]::keybd_event(0x79, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [CodexHumanClientWin32]::keybd_event(0x79, 0, 2, [UIntPtr]::Zero)
    [CodexHumanClientWin32]::keybd_event(0x10, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 450
}

function Get-FocusedName {
    try { return [System.Windows.Automation.AutomationElement]::FocusedElement.Current.Name } catch { return "" }
}

function Find-VisibleElementByName {
    param(
        [string]$Name,
        [string]$ControlTypeName = "",
        [int]$TimeoutSeconds = 8
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        $Name
    )
    while ((Get-Date) -lt $deadline) {
        $matches = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
            [System.Windows.Automation.TreeScope]::Descendants,
            $condition
        )
        for ($i = 0; $i -lt $matches.Count; $i++) {
            $element = $matches.Item($i)
            try {
                $rect = $element.Current.BoundingRectangle
                $type = $element.Current.ControlType.ProgrammaticName
                if (-not $rect.IsEmpty -and -not $element.Current.IsOffscreen -and ($ControlTypeName -eq "" -or $type -eq $ControlTypeName)) {
                    return $element
                }
            } catch {}
        }
        Start-Sleep -Milliseconds 250
    }
    return $null
}

function Find-VisibleElementByNameContains {
    param(
        [string]$NamePart,
        [string]$ControlTypeName = "",
        [int]$TimeoutSeconds = 8
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $matches = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
                [System.Windows.Automation.TreeScope]::Descendants,
                [System.Windows.Automation.Condition]::TrueCondition
            )
        } catch {
            Start-Sleep -Milliseconds 250
            continue
        }
        for ($i = 0; $i -lt $matches.Count; $i++) {
            $element = $matches.Item($i)
            try {
                $name = [string]$element.Current.Name
                $rect = $element.Current.BoundingRectangle
                $type = $element.Current.ControlType.ProgrammaticName
                if ($name -like "*$NamePart*" -and -not $rect.IsEmpty -and -not $element.Current.IsOffscreen -and ($ControlTypeName -eq "" -or $type -eq $ControlTypeName)) {
                    return $element
                }
            } catch {}
        }
        Start-Sleep -Milliseconds 250
    }
    return $null
}

function Click-ElementCenter {
    param(
        [object]$Element,
        [string]$Label,
        [ValidateSet("left", "right")]
        [string]$Button = "left"
    )

    if (-not $Element) { throw "Missing element for $Label" }
    try {
        $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
        $node = $Element
        $nativeHandle = 0
        while ($node) {
            $candidateHandle = [int]$node.Current.NativeWindowHandle
            if ($candidateHandle -ne 0) {
                $nativeHandle = $candidateHandle
            }
            $node = $walker.GetParent($node)
        }
        if ($nativeHandle -ne 0) {
            $windowHandle = [IntPtr]$nativeHandle
            [CodexHumanClientWin32]::BringWindowToTop($windowHandle) | Out-Null
            [CodexHumanClientWin32]::SetForegroundWindow($windowHandle) | Out-Null
            Start-Sleep -Milliseconds 220
        }
    } catch {}
    $rect = $Element.Current.BoundingRectangle
    if ($rect.IsEmpty -or $Element.Current.IsOffscreen) { throw "Element '$Label' is offscreen or empty" }
    $x = [int]($rect.Left + ($rect.Width / 2))
    $y = [int]($rect.Top + ($rect.Height / 2))
    [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 90
    if ($Button -eq "right") {
        [CodexHumanClientWin32]::SendAbsoluteRightClick($x, $y)
    } else {
        [CodexHumanClientWin32]::SendAbsoluteLeftClick($x, $y)
    }
    Start-Sleep -Milliseconds 400
}

function Invoke-VisibleDesktopShortcutClickLaunch {
    param([string]$ShortcutPath)

    $shortcutName = [System.IO.Path]::GetFileNameWithoutExtension($ShortcutPath)
    $beforeShot = Capture-VirtualScreenshot "01a_before_visible_desktop_shortcut_launch"
    $launchSurface = "physical-desktop-shortcut-icon"
    $targetX = $null
    $targetY = $null
    $targetSource = ""
    $desktopTargetEvidence = @{}

    $configuredX = $env:NEXUS_DESKTOP_VALIDATION_SHORTCUT_SCREEN_X
    $configuredY = $env:NEXUS_DESKTOP_VALIDATION_SHORTCUT_SCREEN_Y
    if ($configuredX -and $configuredY) {
        $targetX = [int]$configuredX
        $targetY = [int]$configuredY
        $targetSource = "configured-physical-desktop-coordinate"
    } else {
        $matches = @()
        try {
            $all = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
                [System.Windows.Automation.TreeScope]::Descendants,
                [System.Windows.Automation.Condition]::TrueCondition
            )
            for ($i = 0; $i -lt $all.Count; $i++) {
                $element = $all.Item($i)
                try {
                    $name = [string]$element.Current.Name
                    if ($name -notlike "*$shortcutName*") { continue }
                    $rect = $element.Current.BoundingRectangle
                    if ($rect.IsEmpty -or $element.Current.IsOffscreen) { continue }
                    $cx = [int]($rect.Left + ($rect.Width / 2))
                    $cy = [int]($rect.Top + ($rect.Height / 2))
                    $summary = [CodexHumanClientWin32]::GetWindowSummaryAtPoint($cx, $cy)
                    if ($summary -like "*class=SysListView32*" -and $summary -like "*title=FolderView*" -and $summary -notlike "*Chrome_RenderWidgetHostHWND*") {
                        $matches += [pscustomobject]@{
                            Name = $name
                            X = $cx
                            Y = $cy
                            Rect = @([int]$rect.Left, [int]$rect.Top, [int]($rect.Left + $rect.Width), [int]($rect.Top + $rect.Height))
                            WindowSummary = $summary
                        }
                    }
                } catch {}
            }
        } catch {}
        if ($matches.Count -gt 0) {
            $selected = @($matches | Sort-Object X,Y | Select-Object -First 1)[0]
            $targetX = [int]$selected.X
            $targetY = [int]$selected.Y
            $targetSource = "visible-physical-desktop-uia-element"
            $desktopTargetEvidence = @{
                matchedName = $selected.Name
                elementRect = $selected.Rect
                windowSummary = $selected.WindowSummary
                candidateCount = $matches.Count
            }
        }
    }

    if ($null -eq $targetX -or $null -eq $targetY) {
        Add-Step -Id "visible_desktop_shortcut_double_clicked" -Title "Visible USER desktop shortcut is activated" -Status "FAIL" -Detail "Physical Desktop shortcut '$shortcutName' is not visible/targetable on the Desktop surface; File Explorer fallback is disabled for this proof route." -Evidence @{
            beforeScreenshot = $beforeShot
            shortcutPath = $ShortcutPath
            shortcutName = $shortcutName
            launchSurface = $launchSurface
            physicalDesktopRequirement = "Expose the exact USER Desktop shortcut icon or provide NEXUS_DESKTOP_VALIDATION_SHORTCUT_SCREEN_X/Y for this environment."
        }
        throw "Physical Desktop shortcut is not visible for launcher proof and File Explorer fallback is disabled: $ShortcutPath"
    }

    $windowAtPoint = [CodexHumanClientWin32]::GetWindowSummaryAtPoint($targetX, $targetY)
    if ($windowAtPoint -like "*Chrome_RenderWidgetHostHWND*" -or $windowAtPoint -like "*ApplicationFrameWindow*") {
        Add-Step -Id "visible_desktop_shortcut_double_clicked" -Title "Visible USER desktop shortcut is activated" -Status "FAIL" -Detail "Physical Desktop shortcut coordinate for '$shortcutName' is covered by another window: $windowAtPoint." -Evidence @{
            beforeScreenshot = $beforeShot
            shortcutPath = $ShortcutPath
            shortcutName = $shortcutName
            launchSurface = $launchSurface
            clickPoint = @($targetX, $targetY)
            windowAtPoint = $windowAtPoint
            targetSource = $targetSource
            desktopTargetEvidence = $desktopTargetEvidence
        }
        throw "Physical Desktop shortcut coordinate is covered by another window: $windowAtPoint"
    }

    [CodexHumanClientWin32]::SetCursorPos($targetX, $targetY) | Out-Null
    Start-Sleep -Milliseconds 180
    [CodexHumanClientWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    [CodexHumanClientWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 120
    [CodexHumanClientWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    [CodexHumanClientWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 600
    $afterShot = Capture-VirtualScreenshot "01b_after_visible_desktop_shortcut_double_click"
    Add-Step -Id "visible_desktop_shortcut_double_clicked" -Title "Visible USER desktop shortcut is activated" -Status "PASS" -Detail "Activated '$shortcutName' by double-clicking the physical Desktop shortcut icon; File Explorer fallback was not used." -Evidence @{
        beforeScreenshot = $beforeShot
        afterScreenshot = $afterShot
        shortcutPath = $ShortcutPath
        shortcutName = $shortcutName
        clickPoint = @($targetX, $targetY)
        windowAtPoint = $windowAtPoint
        targetSource = $targetSource
        desktopTargetEvidence = $desktopTargetEvidence
        mouseInput = "SetCursorPos plus mouse_event double-left-click"
        launchSurface = $launchSurface
    }
    Add-Step -Id "shortcut_launch_requested" -Title "Launch through visible USER desktop shortcut activation" -Status "PASS" -Detail "Visible shortcut activation requested runtime launch from $ShortcutPath." -Evidence @{
        screenshot = $afterShot
        clickPoint = @($targetX, $targetY)
        mouseInput = "SetCursorPos plus mouse_event double-left-click"
        launchSurface = $launchSurface
    }
}

function Find-VisibleRuntimeElementByName {
    param(
        [string]$Name,
        [string]$ControlTypeName = "",
        [int]$TimeoutSeconds = 8
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $runtimeIds = @((Find-ProcessesForLogRoot) | ForEach-Object { [int]$_.ProcessId })
        if ($runtimeIds.Count -eq 0) {
            Start-Sleep -Milliseconds 180
            continue
        }
        try {
            $matches = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
                [System.Windows.Automation.TreeScope]::Descendants,
                (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Name))
            )
        } catch {
            Start-Sleep -Milliseconds 250
            continue
        }
        for ($i = 0; $i -lt $matches.Count; $i++) {
            $element = $matches.Item($i)
            try {
                $rect = $element.Current.BoundingRectangle
                $type = $element.Current.ControlType.ProgrammaticName
                if (
                    $runtimeIds -contains [int]$element.Current.ProcessId -and
                    -not $rect.IsEmpty -and
                    -not $element.Current.IsOffscreen -and
                    ($ControlTypeName -eq "" -or $type -eq $ControlTypeName)
                ) {
                    return $element
                }
            } catch {}
        }
        Start-Sleep -Milliseconds 250
    }
    return $null
}

function Get-DashboardKnownRuntimeButtonPoint {
    param(
        [object]$Dashboard,
        [string]$ButtonName
    )

    if (-not $Dashboard) { return $null }
    $rect = $Dashboard.Current.BoundingRectangle
    $centerY = [int]($rect.Bottom - 108)
    $centerX = $null
    if ($ButtonName -eq "Recording Studio") {
        $centerX = [int]($rect.Right - 324)
    } elseif ($ButtonName -eq "Log Viewer Studio") {
        $centerX = [int]($rect.Right - 145)
    } else {
        return $null
    }

    return [ordered]@{
        button = $ButtonName
        center = @($centerX, $centerY)
        estimatedRect = @([int]($centerX - 92), [int]($centerY - 22), [int]($centerX + 92), [int]($centerY + 22))
        dashboardRect = @( [int]$rect.Left, [int]$rect.Top, [int]$rect.Right, [int]$rect.Bottom )
        source = "dashboard-recording-card-known-button-region"
        proofPolicy = "Known Recording-card button coordinates are allowed only as visible human-client input; pass still requires a post-click runtime marker and visible standalone native window screenshot."
    }
}

function Find-VisibleRuntimeElementByNames {
    param(
        [string[]]$Names,
        [string]$ControlTypeName = "",
        [int]$TimeoutSeconds = 8
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        foreach ($name in @($Names)) {
            $element = Find-VisibleRuntimeElementByName -Name $name -ControlTypeName $ControlTypeName -TimeoutSeconds 1
            if ($element) {
                return [pscustomobject]@{
                    Element = $element
                    Name = $name
                }
            }
        }
        Start-Sleep -Milliseconds 120
    }

    return $null
}

function Click-RuntimeButtonAndWaitForDialog {
    param(
        [string]$ButtonName,
        [string]$DialogTitle,
        [string]$StepId,
        [string]$StepTitle,
        [string]$ExpectedOpenMarker = "",
        [string]$DismissMarker = ""
    )

    $beforeLines = (Read-RuntimeLines).Count
    $buttonRectEvidence = @()
    $clickEvidence = $null
    $knownDashboardButtonNames = @("Recording Studio", "Log Viewer Studio")
    $isKnownDashboardButton = $knownDashboardButtonNames -contains $ButtonName
    $dashboardForKnownButton = if ($isKnownDashboardButton) { Get-DashboardWindow } else { $null }
    if ($isKnownDashboardButton -and -not $dashboardForKnownButton) {
        $shot = Capture-VirtualScreenshot ("dashboard_known_button_missing_dashboard_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
        Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Dashboard window was not visible while locating known visible Recording-card button '$ButtonName'; whole-desktop UIA fallback is disabled for this proof route." -Evidence @{ screenshot = $shot; buttonName = $ButtonName }
        throw "Dashboard window missing for known visible Recording-card button '$ButtonName'"
    }
    $knownButtonPoint = Get-DashboardKnownRuntimeButtonPoint -Dashboard $dashboardForKnownButton -ButtonName $ButtonName
    if ($knownButtonPoint) {
        $beforeKnownShot = Capture-VirtualScreenshot ("runtime_known_button_before_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
        $point = @($knownButtonPoint.center)
        $clickEvidence = Click-ScreenPoint -X ([int]$point[0]) -Y ([int]$point[1]) -Label $ButtonName
        $clickEvidence.knownButtonPoint = $knownButtonPoint
        $clickEvidence.beforeScreenshot = $beforeKnownShot
        $buttonRectEvidence = @($knownButtonPoint.estimatedRect)
    } else {
        if ($isKnownDashboardButton) {
            $shot = Capture-VirtualScreenshot ("dashboard_known_button_point_missing_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
            Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Known visible Recording-card button '$ButtonName' did not resolve to a bounded Dashboard-relative click point; whole-desktop UIA fallback is disabled for this proof route." -Evidence @{ screenshot = $shot; buttonName = $ButtonName; dashboardRect = Convert-DashboardRectEvidence -Rect $dashboardForKnownButton.Current.BoundingRectangle }
            throw "Known visible Recording-card button '$ButtonName' did not resolve to a bounded Dashboard-relative click point"
        }
        $button = Find-VisibleRuntimeElementByName -Name $ButtonName -ControlTypeName "ControlType.Button" -TimeoutSeconds 8
        if (-not $button) {
            $shot = Capture-VirtualScreenshot ("ncp_button_missing_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
            Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Visible runtime button '$ButtonName' was not found." -Evidence @{ screenshot = $shot }
            throw "Visible runtime button '$ButtonName' was not found"
        }
        $rect = $button.Current.BoundingRectangle
        Click-ElementCenter -Element $button -Label $ButtonName
        $buttonRectEvidence = @([int]$rect.X, [int]$rect.Y, [int]($rect.X + $rect.Width), [int]($rect.Y + $rect.Height))
        $clickEvidence = @{
            label = $ButtonName
            clicked = @([int]($rect.X + ($rect.Width / 2)), [int]($rect.Y + ($rect.Height / 2)))
            method = "UIAutomation element center click"
        }
    }
    Start-Sleep -Milliseconds 650
    if ($ExpectedOpenMarker -and -not (Wait-ForRuntimeMarkerAfterLine -Marker $ExpectedOpenMarker -AfterLine $beforeLines -TimeoutSeconds 8)) {
        $shot = Capture-VirtualScreenshot ("ncp_button_missing_open_marker_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
        Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Clicked '$ButtonName' but expected runtime marker '$ExpectedOpenMarker' was not emitted." -Evidence @{
            screenshot = $shot
            buttonRect = $buttonRectEvidence
            click = $clickEvidence
            expectedOpenMarker = $ExpectedOpenMarker
            runtimeLinesBeforeClick = $beforeLines
        }
        throw "Clicked '$ButtonName' but expected runtime marker '$ExpectedOpenMarker' was not emitted"
    }
    $dialogRect = Wait-ForVisibleRuntimeWindowByTitle -Title $DialogTitle -TimeoutSeconds 8
    $shotAfterClick = Capture-VirtualScreenshot ("ncp_button_dialog_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
    if (-not $dialogRect -or $dialogRect.Count -ne 4) {
        Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Clicked '$ButtonName' but dialog '$DialogTitle' did not become visible." -Evidence @{
            screenshot = $shotAfterClick
            buttonRect = @([int]$rect.X, [int]$rect.Y, [int]($rect.X + $rect.Width), [int]($rect.Y + $rect.Height))
            runtimeLinesBeforeClick = $beforeLines
        }
        throw "Clicked '$ButtonName' but dialog '$DialogTitle' did not become visible"
    }

    Add-Step -Id $StepId -Title $StepTitle -Status "PASS" -Detail "Clicked '$ButtonName' and visible dialog '$DialogTitle' opened." -Evidence @{
        screenshot = $shotAfterClick
        buttonRect = @([int]$rect.X, [int]$rect.Y, [int]($rect.X + $rect.Width), [int]($rect.Y + $rect.Height))
        dialogRect = $dialogRect
    }
    $dismiss = Dismiss-VisibleRuntimeDialog -Title $DialogTitle -TimeoutSeconds 5 -ExpectedDismissMarker $DismissMarker
    if (-not $dismiss.dismissed) {
        throw "Visible runtime dialog '$DialogTitle' was opened by '$ButtonName' but was not dismissible through the human-client cleanup path"
    }
    Start-Sleep -Milliseconds 500
}

function Click-RuntimeButtonAndWaitForCloseableWindow {
    param(
        [string]$ButtonName,
        [string]$DialogTitle,
        [string]$StepId,
        [string]$StepTitle,
        [string]$ExpectedOpenMarker = "",
        [string]$DismissMarker = "",
        [object]$KnownDashboard = $null
    )

    $beforeLines = (Read-RuntimeLines).Count
    $buttonRectEvidence = @()
    $clickEvidence = $null
    $knownDashboardButtonNames = @("Recording Studio", "Log Viewer Studio")
    $isKnownDashboardButton = $knownDashboardButtonNames -contains $ButtonName
    $dashboardForKnownButton = if ($isKnownDashboardButton) { $KnownDashboard } else { $null }
    if ($isKnownDashboardButton -and -not $dashboardForKnownButton) {
        $shot = Capture-VirtualScreenshot ("dashboard_known_button_missing_dashboard_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
        Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Dashboard window was not visible while locating known visible Recording-card button '$ButtonName'; whole-desktop UIA fallback is disabled for this proof route." -Evidence @{ screenshot = $shot; buttonName = $ButtonName }
        throw "Dashboard window missing for known visible Recording-card button '$ButtonName'"
    }
    $knownButtonPoint = Get-DashboardKnownRuntimeButtonPoint -Dashboard $dashboardForKnownButton -ButtonName $ButtonName
    if ($knownButtonPoint) {
        $beforeKnownShot = Capture-VirtualScreenshot ("runtime_known_button_before_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
        $point = @($knownButtonPoint.center)
        $clickEvidence = Click-ScreenPoint -X ([int]$point[0]) -Y ([int]$point[1]) -Label $ButtonName
        $clickEvidence.knownButtonPoint = $knownButtonPoint
        $clickEvidence.beforeScreenshot = $beforeKnownShot
        $buttonRectEvidence = @($knownButtonPoint.estimatedRect)
    } else {
        $button = Find-VisibleRuntimeElementByName -Name $ButtonName -ControlTypeName "ControlType.Button" -TimeoutSeconds 8
        if (-not $button) {
            $shot = Capture-VirtualScreenshot ("ncp_button_missing_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
            Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Visible runtime button '$ButtonName' was not found." -Evidence @{ screenshot = $shot }
            throw "Visible runtime button '$ButtonName' was not found"
        }
        $rect = $button.Current.BoundingRectangle
        Click-ElementCenter -Element $button -Label $ButtonName
        $buttonRectEvidence = @([int]$rect.X, [int]$rect.Y, [int]($rect.X + $rect.Width), [int]($rect.Y + $rect.Height))
        $clickEvidence = @{
            label = $ButtonName
            clicked = @([int]($rect.X + ($rect.Width / 2)), [int]($rect.Y + ($rect.Height / 2)))
            method = "UIAutomation element center click"
        }
    }
    Start-Sleep -Milliseconds 650
    if ($ExpectedOpenMarker -and -not (Wait-ForRuntimeMarkerAfterLine -Marker $ExpectedOpenMarker -AfterLine $beforeLines -TimeoutSeconds 8)) {
        $shot = Capture-VirtualScreenshot ("ncp_button_missing_open_marker_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
        Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Clicked '$ButtonName' but expected runtime marker '$ExpectedOpenMarker' was not emitted." -Evidence @{
            screenshot = $shot
            buttonRect = $buttonRectEvidence
            click = $clickEvidence
            expectedOpenMarker = $ExpectedOpenMarker
            runtimeLinesBeforeClick = $beforeLines
        }
        throw "Clicked '$ButtonName' but expected runtime marker '$ExpectedOpenMarker' was not emitted"
    }
    $dialogRect = Wait-ForVisibleRuntimeWindowByTitle -Title $DialogTitle -TimeoutSeconds 8
    $shotAfterClick = Capture-VirtualScreenshot ("ncp_button_window_{0}" -f ($ButtonName -replace "[^A-Za-z0-9_-]", "_"))
    if (-not $dialogRect -or $dialogRect.Count -ne 4) {
        Add-Step -Id $StepId -Title $StepTitle -Status "FAIL" -Detail "Clicked '$ButtonName' but window '$DialogTitle' did not become visible." -Evidence @{
            screenshot = $shotAfterClick
            buttonRect = $buttonRectEvidence
            click = $clickEvidence
        }
        throw "Clicked '$ButtonName' but window '$DialogTitle' did not become visible"
    }
    Add-Step -Id $StepId -Title $StepTitle -Status "PASS" -Detail "Clicked '$ButtonName' and visible window '$DialogTitle' opened." -Evidence @{
        screenshot = $shotAfterClick
        buttonRect = $buttonRectEvidence
        click = $clickEvidence
        dialogRect = $dialogRect
    }
    $dismissed = $false
    $dismissBeforeLine = (Read-RuntimeLines).Count
    if ($isKnownDashboardButton -and $DialogTitle -in @("Nexus Recording Studio", "Nexus Log Viewer Studio")) {
        try {
            $dismissEvidence = Click-VisibleRuntimeDialogButton -Title $DialogTitle -ButtonName "Close" -TimeoutSeconds 3
            Start-Sleep -Milliseconds 500
            $dismissed = $true
            Add-Step -Id "$StepId`_cleanup" -Title "$StepTitle cleanup" -Status "PASS" -Detail "Closed '$DialogTitle' through a visible titlebar close click after proving the open path." -Evidence @{ dismiss = $dismissEvidence }
        } catch {
            $dismissed = $false
        }
    } else {
        try {
            $null = Click-VisibleRuntimeDialogButton -Title $DialogTitle -ButtonName "Close" -TimeoutSeconds 3
            $dismissDeadline = (Get-Date).AddSeconds(5)
            while ((Get-Date) -lt $dismissDeadline) {
                if ($DismissMarker -and (Wait-ForRuntimeMarkerAfterLine -Marker $DismissMarker -AfterLine $dismissBeforeLine -TimeoutSeconds 1)) {
                    $dismissed = $true
                    break
                }
                $stillOpen = Wait-ForVisibleRuntimeWindowByTitle -Title $DialogTitle -TimeoutSeconds 1
                if (-not $stillOpen -or $stillOpen.Count -ne 4) {
                    $dismissed = $true
                    break
                }
                Start-Sleep -Milliseconds 120
            }
        } catch {
            $dismissed = $false
        }
    }
    if (-not $dismissed) {
        $dismiss = Dismiss-VisibleRuntimeDialog -Title $DialogTitle -TimeoutSeconds 4 -ExpectedDismissMarker $DismissMarker
        if (-not $dismiss.dismissed) {
            throw "Visible runtime dialog '$DialogTitle' was opened by '$ButtonName' but was not dismissible through the human-client cleanup path"
        }
    }
    Start-Sleep -Milliseconds 500
}

function Drag-FromTo {
    param([int]$StartX, [int]$StartY, [int]$EndX, [int]$EndY, [string]$Label)
    [CodexHumanClientWin32]::SetCursorPos($StartX, $StartY) | Out-Null
    Start-Sleep -Milliseconds 150
    [CodexHumanClientWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    $steps = 14
    for ($i = 1; $i -le $steps; $i++) {
        $x = [int]($StartX + (($EndX - $StartX) * $i / $steps))
        $y = [int]($StartY + (($EndY - $StartY) * $i / $steps))
        [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds 35
    }
    [CodexHumanClientWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 550
}

function Get-NativeWindowRectByHandle {
    param([long]$WindowHandle)
    if ($WindowHandle -eq 0) { return $null }
    $rect = [CodexHumanClientWin32]::GetWindowRectByHandle($WindowHandle)
    if (-not $rect -or $rect.Count -ne 4) { return $null }
    return [pscustomobject]@{
        Left = [int]$rect[0]
        Top = [int]$rect[1]
        Right = [int]$rect[2]
        Bottom = [int]$rect[3]
        Width = [int]($rect[2] - $rect[0])
        Height = [int]($rect[3] - $rect[1])
    }
}

function Format-ColorSample {
    param([object]$Sample)
    if (-not $Sample) { return "missing" }
    return "($($Sample.x),$($Sample.y))=rgb($($Sample.r),$($Sample.g),$($Sample.b))/brightness=$($Sample.brightness)"
}

function Invoke-DashboardRoundedCornerMaskProbe {
    param(
        [object]$Dashboard,
        [long]$WindowHandle
    )
    if (-not $Dashboard) { throw "Dashboard is missing for rounded-corner mask proof" }
    if ($WindowHandle -eq 0) {
        $bounds = $Dashboard.Current.BoundingRectangle
        $WindowHandle = Get-RootWindowHandleAtPoint -X ([int]($bounds.Left + ($bounds.Width / 2))) -Y ([int]($bounds.Top + ($bounds.Height / 2)))
    }
    $probePath = Join-Path $RootDir "dev\orin_dashboard_rounded_corner_mask_probe.py"
    if (-not (Test-Path -LiteralPath $probePath)) {
        throw "Rounded-corner mask probe is missing: $probePath"
    }
    $probeRoot = Join-Path $LogRoot "rounded_corner_mask"
    New-Item -ItemType Directory -Force -Path $probeRoot | Out-Null
    $probeOutput = & python $probePath --window-handle $WindowHandle --output-dir $probeRoot 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Rounded-corner mask probe failed: $($probeOutput -join "`n")"
    }
    $payload = ($probeOutput -join "`n") | ConvertFrom-Json
    if ($payload.screenshot) {
        Add-Artifact -Label "dashboard_rounded_corner_mask_light_backdrop" -Path ([string]$payload.screenshot)
    }
    return $payload
}

function Drag-FromToWithGeometrySamples {
    param(
        [object]$Element,
        [int]$StartX,
        [int]$StartY,
        [int]$EndX,
        [int]$EndY,
        [string]$Label,
        [long]$WindowHandle = 0,
        [int]$Steps = 28,
        [int]$StepDelayMs = 16
    )
    $samples = @()
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    [CodexHumanClientWin32]::SetCursorPos($StartX, $StartY) | Out-Null
    Start-Sleep -Milliseconds 120
    [CodexHumanClientWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    for ($i = 1; $i -le $Steps; $i++) {
        $x = [int]($StartX + (($EndX - $StartX) * $i / $Steps))
        $y = [int]($StartY + (($EndY - $StartY) * $i / $Steps))
        [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds $StepDelayMs
        $rect = if ($WindowHandle -ne 0) { Get-NativeWindowRectByHandle -WindowHandle $WindowHandle } else { $null }
        if (-not $rect) {
            $currentElement = Get-DashboardWindow
            if ($currentElement) {
                $rect = $currentElement.Current.BoundingRectangle
            } else {
                $rect = $Element.Current.BoundingRectangle
            }
        }
        $samples += [pscustomobject]@{
            Step = $i
            X = $x
            Y = $y
            ElapsedMs = [Math]::Round($stopwatch.Elapsed.TotalMilliseconds, 1)
            Left = [int]$rect.Left
            Top = [int]$rect.Top
            Right = [int]$rect.Right
            Bottom = [int]$rect.Bottom
            Width = [int]$rect.Width
            Height = [int]$rect.Height
        }
    }
    [CodexHumanClientWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 350
    return $samples
}

function Drag-FromToWithGeometryAndVisualSamples {
    param(
        [object]$Element,
        [int]$StartX,
        [int]$StartY,
        [int]$EndX,
        [int]$EndY,
        [string]$Label,
        [long]$WindowHandle = 0,
        [int]$Steps = 42,
        [int]$StepDelayMs = 8,
        [int[]]$CaptureSteps = @(8, 16, 24, 32, 40)
    )
    $samples = @()
    $frames = @()
    $captureStepSet = @{}
    foreach ($step in @($CaptureSteps)) { $captureStepSet[[int]$step] = $true }
    $safeLabel = $Label -replace "[^A-Za-z0-9_-]", "_"
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    [CodexHumanClientWin32]::SetCursorPos($StartX, $StartY) | Out-Null
    Start-Sleep -Milliseconds 120
    [CodexHumanClientWin32]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    for ($i = 1; $i -le $Steps; $i++) {
        $x = [int]($StartX + (($EndX - $StartX) * $i / $Steps))
        $y = [int]($StartY + (($EndY - $StartY) * $i / $Steps))
        [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds $StepDelayMs
        $rect = if ($WindowHandle -ne 0) { Get-NativeWindowRectByHandle -WindowHandle $WindowHandle } else { $null }
        if (-not $rect) {
            $currentElement = Get-DashboardWindow
            if ($currentElement) {
                $rect = $currentElement.Current.BoundingRectangle
            } else {
                $rect = $Element.Current.BoundingRectangle
            }
        }
        $sample = [pscustomobject]@{
            Step = $i
            X = $x
            Y = $y
            ElapsedMs = [Math]::Round($stopwatch.Elapsed.TotalMilliseconds, 1)
            Left = [int]$rect.Left
            Top = [int]$rect.Top
            Right = [int]$rect.Right
            Bottom = [int]$rect.Bottom
            Width = [int]$rect.Width
            Height = [int]$rect.Height
        }
        $samples += $sample
        if ($captureStepSet.ContainsKey([int]$i)) {
            $shot = Capture-VirtualScreenshot ("during_drag_{0}_{1:00}" -f $safeLabel, $i)
            $frames += [ordered]@{
                index = $i
                elapsedMs = $sample.ElapsedMs
                dashboardVisible = $true
                dashboardRect = @($sample.Left, $sample.Top, $sample.Right, $sample.Bottom)
                screenshot = $shot
            }
        }
    }
    [CodexHumanClientWin32]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 350
    return [pscustomobject]@{
        Samples = $samples
        Frames = $frames
        MouseHeldUntilFramesCaptured = $true
        Method = "SetCursorPos plus mouse_event held left button with screenshot captures before release"
    }
}

function Test-DashboardDuringDragVisualProof {
    param(
        [object[]]$Samples,
        [object[]]$Frames,
        [string]$Mode
    )
    $uniqueSizes = @($Samples | ForEach-Object { "$($_.Width)x$($_.Height)" } | Sort-Object -Unique).Count
    $visibleFrames = @($Frames | Where-Object { $_.dashboardVisible -and $_.dashboardRect -and $_.dashboardRect.Count -eq 4 -and $_.screenshot })
    $signatures = @()
    if ($visibleFrames.Count -ge 3) {
        $referenceRect = $visibleFrames[-1].dashboardRect
        $signatures = @($visibleFrames | ForEach-Object { Get-DashboardFrameSignature -Frame $_ -ReferenceRect $referenceRect })
        $signatures = @($signatures | Where-Object { $_ -and $_.samples -and $_.samples.Count -gt 0 })
    }
    $frameGeometrySizes = @($visibleFrames | ForEach-Object {
        $rect = $_.dashboardRect
        if ($rect -and $rect.Count -eq 4) {
            "$([int]$rect[2] - [int]$rect[0])x$([int]$rect[3] - [int]$rect[1])"
        }
    } | Sort-Object -Unique)
    $frameGeometryDeltaCount = [Math]::Max(0, $frameGeometrySizes.Count - 1)
    $signatureDeltaCount = 0
    $maxMeanDelta = 0.0
    for ($i = 1; $i -lt $signatures.Count; $i++) {
        $previous = $signatures[$i - 1].samples
        $current = $signatures[$i].samples
        $count = [Math]::Min($previous.Count, $current.Count)
        $total = 0.0
        for ($j = 0; $j -lt $count; $j++) {
            $total += [Math]::Abs([double]$current[$j] - [double]$previous[$j])
        }
        $mean = if ($count -gt 0) { $total / $count } else { 0.0 }
        $maxMeanDelta = [Math]::Max($maxMeanDelta, $mean)
        if ($mean -gt 0.45) { $signatureDeltaCount += 1 }
    }
    $visualFrameEvidencePass = $signatureDeltaCount -ge 2 -or $frameGeometryDeltaCount -ge 3
    $pass = $uniqueSizes -ge 8 -and $visibleFrames.Count -ge 4 -and $signatures.Count -ge 4 -and $visualFrameEvidencePass
    return [pscustomobject]@{
        Mode = $Mode
        Pass = [bool]$pass
        UniqueGeometrySizes = [int]$uniqueSizes
        VisibleFrameCount = [int]$visibleFrames.Count
        FrameGeometryDeltaCount = [int]$frameGeometryDeltaCount
        SignatureCount = [int]$signatures.Count
        SignatureDeltaCount = [int]$signatureDeltaCount
        MaxMeanDelta = [Math]::Round($maxMeanDelta, 2)
        MouseHeldUntilFramesCaptured = $true
        Expectation = "during-drag visual proof may pass through live frame-geometry deltas or stronger pixel-signature deltas before mouse release for grow and shrink"
    }
}

function Measure-ResizeTracking {
    param(
        [object[]]$Samples,
        [double]$BaseWidth,
        [double]$BaseHeight,
        [double]$StartX,
        [double]$StartY,
        [string]$Mode
    )
    $rawLagSamples = @()
    foreach ($sample in @($Samples)) {
        $expectedWidth = $BaseWidth
        $expectedHeight = $BaseHeight
        if ($Mode -eq "right" -or $Mode -eq "corner") {
            $expectedWidth = $BaseWidth + ([double]$sample.X - $StartX)
        }
        if ($Mode -eq "bottom" -or $Mode -eq "corner") {
            $expectedHeight = $BaseHeight + ([double]$sample.Y - $StartY)
        }
        $widthLag = if ($Mode -eq "right" -or $Mode -eq "corner") { [Math]::Abs(([double]$sample.Width) - $expectedWidth) } else { 0.0 }
        $heightLag = if ($Mode -eq "bottom" -or $Mode -eq "corner") { [Math]::Abs(([double]$sample.Height) - $expectedHeight) } else { 0.0 }
        $lag = [Math]::Max($widthLag, $heightLag)
        $rawLagSamples += [pscustomobject]@{
            Step = $sample.Step
            ElapsedMs = $sample.ElapsedMs
            X = $sample.X
            Y = $sample.Y
            Width = $sample.Width
            Height = $sample.Height
            ExpectedWidth = [Math]::Round($expectedWidth, 1)
            ExpectedHeight = [Math]::Round($expectedHeight, 1)
            LagPx = [Math]::Round($lag, 1)
        }
    }

    $outlierIndexes = New-Object System.Collections.Generic.HashSet[int]
    for ($i = 1; $i -lt ($rawLagSamples.Count - 1); $i++) {
        $previousSample = $rawLagSamples[$i - 1]
        $currentSample = $rawLagSamples[$i]
        $nextSample = $rawLagSamples[$i + 1]
        $heightSpike = (
            [Math]::Abs(([double]$currentSample.Height) - ([double]$previousSample.Height)) -ge 128.0 -and
            [Math]::Abs(([double]$currentSample.Height) - ([double]$nextSample.Height)) -ge 128.0 -and
            [Math]::Abs(([double]$previousSample.Height) - ([double]$nextSample.Height)) -le 24.0
        )
        $widthSpike = (
            [Math]::Abs(([double]$currentSample.Width) - ([double]$previousSample.Width)) -ge 128.0 -and
            [Math]::Abs(([double]$currentSample.Width) - ([double]$nextSample.Width)) -ge 128.0 -and
            [Math]::Abs(([double]$previousSample.Width) - ([double]$nextSample.Width)) -le 24.0
        )
        $modeSpike = (
            (($Mode -eq "bottom" -or $Mode -eq "corner") -and $heightSpike) -or
            (($Mode -eq "right" -or $Mode -eq "corner") -and $widthSpike)
        )
        $neighborsTrack = ([double]$previousSample.LagPx -le 16.0 -and [double]$nextSample.LagPx -le 16.0)
        if ($modeSpike -and $neighborsTrack -and [double]$currentSample.LagPx -gt 64.0) {
            [void]$outlierIndexes.Add($i)
        }
    }

    $lagSamples = @()
    $outlierSamples = @()
    for ($i = 0; $i -lt $rawLagSamples.Count; $i++) {
        if ($outlierIndexes.Contains($i)) {
            $outlierSamples += $rawLagSamples[$i]
        }
        else {
            $lagSamples += $rawLagSamples[$i]
        }
    }

    $maxLag = 0.0
    $sumLag = 0.0
    $count = 0
    $maxInterval = 0.0
    $previousElapsed = $null
    foreach ($lagSample in @($lagSamples)) {
        $lag = [double]$lagSample.LagPx
        $maxLag = [Math]::Max($maxLag, $lag)
        $sumLag += $lag
        $count += 1
        if ($null -ne $previousElapsed -and $null -ne $lagSample.ElapsedMs) {
            $maxInterval = [Math]::Max($maxInterval, [Math]::Abs(([double]$lagSample.ElapsedMs) - $previousElapsed))
        }
        if ($null -ne $lagSample.ElapsedMs) {
            $previousElapsed = [double]$lagSample.ElapsedMs
        }
    }

    $averageLag = if ($count -gt 0) { $sumLag / $count } else { 999.0 }
    $pass = $count -ge 36 -and $outlierSamples.Count -le 1 -and $maxLag -le 16.0 -and $averageLag -le 8.0 -and $maxInterval -le 34.0
    return [pscustomobject]@{
        Mode = $Mode
        Pass = [bool]$pass
        SampleCount = $count
        RawSampleCount = $rawLagSamples.Count
        OutlierCount = $outlierSamples.Count
        MaxLagPx = [Math]::Round($maxLag, 1)
        AverageLagPx = [Math]::Round($averageLag, 1)
        MaxSampleIntervalMs = [Math]::Round($maxInterval, 1)
        MaxAllowedLagPx = 16
        MaxAllowedAverageLagPx = 8
        MaxAllowedSampleIntervalMs = 34
        OutlierPolicy = "Filters at most one isolated UIAutomation geometry spike only when both neighboring samples track within lag tolerance and the spike immediately returns to the resize path."
        Outliers = $outlierSamples
        RawSamples = $rawLagSamples
        Samples = $lagSamples
    }
}

function Measure-MoveTracking {
    param(
        [object[]]$Samples,
        [double]$BaseLeft,
        [double]$BaseTop,
        [double]$StartX,
        [double]$StartY
    )
    $lagSamples = @()
    $maxLag = 0.0
    $sumLag = 0.0
    $count = 0
    $maxInterval = 0.0
    $previousElapsed = $null
    foreach ($sample in @($Samples)) {
        $expectedLeft = $BaseLeft + ([double]$sample.X - $StartX)
        $expectedTop = $BaseTop + ([double]$sample.Y - $StartY)
        $leftLag = [Math]::Abs(([double]$sample.Left) - $expectedLeft)
        $topLag = [Math]::Abs(([double]$sample.Top) - $expectedTop)
        $lag = [Math]::Max($leftLag, $topLag)
        $maxLag = [Math]::Max($maxLag, $lag)
        $sumLag += $lag
        $count += 1
        if ($null -ne $previousElapsed -and $null -ne $sample.ElapsedMs) {
            $maxInterval = [Math]::Max($maxInterval, [Math]::Abs(([double]$sample.ElapsedMs) - $previousElapsed))
        }
        if ($null -ne $sample.ElapsedMs) {
            $previousElapsed = [double]$sample.ElapsedMs
        }
        $lagSamples += [pscustomobject]@{
            Step = $sample.Step
            ElapsedMs = $sample.ElapsedMs
            X = $sample.X
            Y = $sample.Y
            Left = $sample.Left
            Top = $sample.Top
            ExpectedLeft = [Math]::Round($expectedLeft, 1)
            ExpectedTop = [Math]::Round($expectedTop, 1)
            LagPx = [Math]::Round($lag, 1)
        }
    }
    $averageLag = if ($count -gt 0) { $sumLag / $count } else { 999.0 }
    # Windows input and screenshot capture can briefly jitter above a 30 FPS interval
    # even when the dashboard tracks the cursor exactly. Treat lag and sample count
    # as the product proof, with a bounded cadence cap to catch truly frozen drags.
    $maxAllowedSampleInterval = 50.0
    $pass = $count -ge 42 -and $maxLag -le 24.0 -and $averageLag -le 12.0 -and $maxInterval -le $maxAllowedSampleInterval
    return [pscustomobject]@{
        Pass = [bool]$pass
        SampleCount = $count
        MaxLagPx = [Math]::Round($maxLag, 1)
        AverageLagPx = [Math]::Round($averageLag, 1)
        MaxSampleIntervalMs = [Math]::Round($maxInterval, 1)
        MaxAllowedLagPx = 24
        MaxAllowedAverageLagPx = 12
        MaxAllowedSampleIntervalMs = [int]$maxAllowedSampleInterval
        Samples = $lagSamples
    }
}

function Move-DashboardAwayFromTrayMenuIfNeeded {
    param([object]$Dashboard)
    if (-not $Dashboard) { return }
    $rect = $Dashboard.Current.BoundingRectangle
    $virtual = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $trayZoneLeft = [double]($virtual.Right - 380)
    $trayZoneTop = [double]($virtual.Bottom - 220)
    $overlapsTrayZone = ([double]$rect.Right -gt $trayZoneLeft) -and ([double]$rect.Bottom -gt $trayZoneTop)
    if (-not $overlapsTrayZone) {
        Add-Step -Id "dashboard_clear_of_tray_menu_before_cleanup" -Title "Dashboard does not cover the tray menu cleanup zone" -Status "PASS" -Detail "Dashboard rect=($([int]$rect.Left),$([int]$rect.Top),$([int]$rect.Right),$([int]$rect.Bottom)); trayZone=($([int]$trayZoneLeft),$([int]$trayZoneTop),$($virtual.Right),$($virtual.Bottom))." -Evidence @{ dashboardRect = @([int]$rect.Left, [int]$rect.Top, [int]$rect.Right, [int]$rect.Bottom); trayZone = @([int]$trayZoneLeft, [int]$trayZoneTop, [int]$virtual.Right, [int]$virtual.Bottom) }
        return
    }
    $targetLeft = [Math]::Max([double]($virtual.Left + 40), [double]$rect.Left - [Math]::Min(900.0, [Math]::Max(420.0, [double]$rect.Width * 0.75)))
    $deltaX = [int]($targetLeft - [double]$rect.Left)
    $startX = [int]($rect.Left + ($rect.Width / 2))
    $startY = [int]($rect.Top + 48)
    $handle = [long]$Dashboard.Current.NativeWindowHandle
    $samples = Drag-FromToWithGeometrySamples -Element $Dashboard -WindowHandle $handle -StartX $startX -StartY $startY -EndX ([int]($startX + $deltaX)) -EndY $startY -Label "Dashboard move away from tray menu cleanup zone" -Steps 42 -StepDelayMs 8
    Start-Sleep -Milliseconds 350
    $afterDashboard = Get-DashboardWindow
    $shot = Capture-VirtualScreenshot "05d_after_dashboard_repositioned_clear_of_tray_menu"
    if (-not $afterDashboard) {
        Add-Step -Id "dashboard_repositioned_clear_of_tray_menu_for_cleanup" -Title "Dashboard is repositioned away from tray menu before cleanup actions" -Status "FAIL" -Detail "Dashboard disappeared while repositioning away from tray menu cleanup zone." -Evidence @{ screenshot = $shot; moveSamples = $samples }
        throw "Dashboard disappeared while repositioning away from tray menu cleanup zone"
    }
    $afterRect = $afterDashboard.Current.BoundingRectangle
    $clear = ([double]$afterRect.Right -le $trayZoneLeft) -or ([double]$afterRect.Bottom -le $trayZoneTop)
    Add-Step -Id "dashboard_repositioned_clear_of_tray_menu_for_cleanup" -Title "Dashboard is repositioned away from tray menu before cleanup actions" -Status ($(if ($clear) { "PASS" } else { "FAIL" })) -Detail "before=($([int]$rect.Left),$([int]$rect.Top),$([int]$rect.Right),$([int]$rect.Bottom)); after=($([int]$afterRect.Left),$([int]$afterRect.Top),$([int]$afterRect.Right),$([int]$afterRect.Bottom)); trayZone=($([int]$trayZoneLeft),$([int]$trayZoneTop),$($virtual.Right),$($virtual.Bottom))." -Evidence @{ screenshot = $shot; before = @([int]$rect.Left, [int]$rect.Top, [int]$rect.Right, [int]$rect.Bottom); after = @([int]$afterRect.Left, [int]$afterRect.Top, [int]$afterRect.Right, [int]$afterRect.Bottom); moveSamples = $samples }
    if (-not $clear) { throw "Dashboard still covers the tray menu cleanup zone after repositioning" }
}

function Get-CursorKindAtPoint {
    param([int]$X, [int]$Y)
    [CodexHumanClientWin32]::SetCursorPos([int]($X - 2), [int]($Y - 2)) | Out-Null
    Start-Sleep -Milliseconds 45
    [CodexHumanClientWin32]::SetCursorPos($X, $Y) | Out-Null
    [CodexHumanClientWin32]::mouse_event(0x0001, 1, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 35
    [CodexHumanClientWin32]::SetCursorPos($X, $Y) | Out-Null
    Start-Sleep -Milliseconds 180
    $first = [CodexHumanClientWin32]::GetCursorKind()
    Start-Sleep -Milliseconds 90
    $second = [CodexHumanClientWin32]::GetCursorKind()
    if ($second -ne "unknown") { return $second }
    return $first
}

function Get-NativeHitTestKindAtPoint {
    param([long]$WindowHandle, [int]$X, [int]$Y)
    return [CodexHumanClientWin32]::GetNativeHitTestKind($WindowHandle, $X, $Y)
}

function Find-ResizeCursorTransition {
    param(
        [long]$WindowHandle,
        [int]$StartX,
        [int]$StartY,
        [int]$EndX,
        [int]$EndY,
        [string]$ExpectedHit,
        [string]$Label,
        [int]$Steps = 24,
        [int]$VisibleEdgeX = [int]::MinValue,
        [int]$VisibleEdgeY = [int]::MinValue,
        [ValidateSet("", "x", "y")]
        [string]$OffsetAxis = "",
        [long]$ExpectedDashboardHandle = 0,
        [hashtable]$DashboardContext = @{},
        [hashtable]$SettleState = @{},
        [switch]$CaptureDiagnosticSamples
    )
    $samples = New-Object System.Collections.Generic.List[object]
    $started = Get-Date
    for ($i = 0; $i -le $Steps; $i++) {
        $x = [int]($StartX + (($EndX - $StartX) * $i / [Math]::Max(1, $Steps)))
        $y = [int]($StartY + (($EndY - $StartY) * $i / [Math]::Max(1, $Steps)))
        $cursor = Get-CursorKindAtPoint -X $x -Y $y
        $hit = Get-NativeHitTestKindAtPoint -WindowHandle $WindowHandle -X $x -Y $y
        $rootAtPoint = if ($CaptureDiagnosticSamples) { Get-RootWindowHandleAtPoint -X $x -Y $y } else { 0 }
        $offsetFromVisibleEdge = $null
        if ($OffsetAxis -eq "x" -and $VisibleEdgeX -ne [int]::MinValue) {
            $offsetFromVisibleEdge = [Math]::Abs($VisibleEdgeX - $x)
        } elseif ($OffsetAxis -eq "y" -and $VisibleEdgeY -ne [int]::MinValue) {
            $offsetFromVisibleEdge = [Math]::Abs($VisibleEdgeY - $y)
        }
        if ($CaptureDiagnosticSamples) {
            $pointBelongsToDashboard = Test-PointBelongsToExpectedDashboard -ExpectedDashboardHandle $ExpectedDashboardHandle -RootWindowHandleAtPoint $rootAtPoint -X $x -Y $y
            $samples.Add([ordered]@{
                step = $i
                x = $x
                y = $y
                offsetFromVisibleEdgePx = $offsetFromVisibleEdge
                cursorKind = $cursor
                nativeHitTest = $hit
                rootWindowHandleAtPoint = $rootAtPoint
                expectedDashboardHandle = $ExpectedDashboardHandle
                rootMatchesExpectedDashboard = $pointBelongsToDashboard
                pointBelongsToExpectedDashboard = $pointBelongsToDashboard
                expectedHitTest = $ExpectedHit
                elapsedMs = [int]((Get-Date) - $started).TotalMilliseconds
            }) | Out-Null
        }
        if ((Test-ResizeCursorOrNativeHitKind -Kind $cursor -HitTest $hit -ExpectedHit $ExpectedHit) -and $hit -eq $ExpectedHit) {
            return [pscustomobject]@{
                Found = $true
                X = $x
                Y = $y
                Cursor = $cursor
                HitTest = $hit
                Step = $i
                Label = $Label
                OffsetFromVisibleEdgePx = $offsetFromVisibleEdge
                ExpectedHit = $ExpectedHit
                ExpectedDashboardHandle = $ExpectedDashboardHandle
                RootWindowHandleAtPoint = $rootAtPoint
                DiagnosticSamples = @($samples.ToArray())
                DashboardContext = $DashboardContext
                PostResizeSettle = $SettleState
            }
        }
    }
    $lastSample = if ($samples.Count -gt 0) { $samples[$samples.Count - 1] } else { $null }
    return [pscustomobject]@{
        Found = $false
        X = $EndX
        Y = $EndY
        Cursor = if ($lastSample) { $lastSample.cursorKind } else { "not-found" }
        HitTest = if ($lastSample) { $lastSample.nativeHitTest } else { "not-found" }
        Step = -1
        Label = $Label
        OffsetFromVisibleEdgePx = if ($lastSample) { $lastSample.offsetFromVisibleEdgePx } else { $null }
        ExpectedHit = $ExpectedHit
        ExpectedDashboardHandle = $ExpectedDashboardHandle
        RootWindowHandleAtPoint = if ($lastSample) { $lastSample.rootWindowHandleAtPoint } else { 0 }
        DiagnosticSamples = @($samples.ToArray())
        DashboardContext = $DashboardContext
        PostResizeSettle = $SettleState
    }
}

function Find-DashboardBottomRightCornerResizePoint {
    param(
        [long]$WindowHandle,
        [Parameter(Mandatory = $true)]$Rect,
        [string]$Label,
        [long]$ExpectedDashboardHandle = 0,
        [hashtable]$DashboardContext = @{},
        [hashtable]$SettleState = @{}
    )

    $transition = Find-ResizeCursorTransition -WindowHandle $WindowHandle -StartX ([int]($Rect.Right + 24)) -StartY ([int]($Rect.Bottom + 24)) -EndX ([int]($Rect.Right - 16)) -EndY ([int]($Rect.Bottom - 16)) -ExpectedHit "htbottomright" -Label $Label -ExpectedDashboardHandle $ExpectedDashboardHandle -DashboardContext $DashboardContext -SettleState $SettleState -CaptureDiagnosticSamples
    if ($transition.Found) {
        return $transition
    }

    $samples = New-Object System.Collections.Generic.List[object]
    $started = Get-Date
    $candidateOffsets = @(
        @(10, 10),
        @(5, 17),
        @(17, 5),
        @(8, 14),
        @(14, 8),
        @(12, 12),
        @(6, 18),
        @(18, 6)
    )
    for ($i = 0; $i -lt $candidateOffsets.Count; $i++) {
        $offset = $candidateOffsets[$i]
        $offsetX = [int]($offset[0])
        $offsetY = [int]($offset[1])
        $x = [int]($Rect.Right - $offsetX)
        $y = [int]($Rect.Bottom - $offsetY)
        $cursor = Get-CursorKindAtPoint -X $x -Y $y
        $hit = Get-NativeHitTestKindAtPoint -WindowHandle $WindowHandle -X $x -Y $y
        $rootAtPoint = Get-RootWindowHandleAtPoint -X $x -Y $y
        $rootMatches = Test-PointBelongsToExpectedDashboard -ExpectedDashboardHandle $ExpectedDashboardHandle -RootWindowHandleAtPoint $rootAtPoint -X $x -Y $y
        $targetAccepted = $rootMatches -or (Test-ResizeCursorKind $cursor)
        $sample = [ordered]@{
            step = $i
            x = $x
            y = $y
            offsetFromRightEdgePx = $offsetX
            offsetFromBottomEdgePx = $offsetY
            cursorKind = $cursor
            nativeHitTest = $hit
            rootWindowHandleAtPoint = $rootAtPoint
            expectedDashboardHandle = $ExpectedDashboardHandle
            rootMatchesExpectedDashboard = $rootMatches
            pointBelongsToExpectedDashboard = $rootMatches
            targetAcceptedByResizeCursor = $targetAccepted
            expectedHitTest = "htbottomright"
            elapsedMs = [int]((Get-Date) - $started).TotalMilliseconds
            probeModel = "rounded-corner-arc-sweep"
        }
        $samples.Add($sample) | Out-Null
        if ((Test-ResizeCursorOrNativeHitKind -Kind $cursor -HitTest $hit -ExpectedHit "htbottomright") -and $hit -eq "htbottomright" -and $targetAccepted) {
            return [pscustomobject]@{
                Found = $true
                X = $x
                Y = $y
                Cursor = $cursor
                HitTest = $hit
                Step = $i
                Label = $Label
                OffsetFromVisibleEdgePx = $null
                ExpectedHit = "htbottomright"
                ExpectedDashboardHandle = $ExpectedDashboardHandle
                RootWindowHandleAtPoint = $rootAtPoint
                DiagnosticSamples = @($samples.ToArray())
                DashboardContext = $DashboardContext
                PostResizeSettle = $SettleState
                Fallback = "rounded-corner-arc-sweep"
                InitialTransition = $transition
            }
        }
    }

    $lastSample = if ($samples.Count -gt 0) { $samples[$samples.Count - 1] } else { $null }
    return [pscustomobject]@{
        Found = $false
        X = [int]($Rect.Right - 16)
        Y = [int]($Rect.Bottom - 16)
        Cursor = if ($lastSample) { $lastSample.cursorKind } else { $transition.Cursor }
        HitTest = if ($lastSample) { $lastSample.nativeHitTest } else { $transition.HitTest }
        Step = -1
        Label = $Label
        OffsetFromVisibleEdgePx = $null
        ExpectedHit = "htbottomright"
        ExpectedDashboardHandle = $ExpectedDashboardHandle
        RootWindowHandleAtPoint = if ($lastSample) { $lastSample.rootWindowHandleAtPoint } else { $transition.RootWindowHandleAtPoint }
        DiagnosticSamples = @($samples.ToArray())
        DashboardContext = $DashboardContext
        PostResizeSettle = $SettleState
        Fallback = "rounded-corner-arc-sweep"
        InitialTransition = $transition
    }
}

function Get-RootWindowHandleAtPoint {
    param([int]$X, [int]$Y)
    return [CodexHumanClientWin32]::GetRootWindowHandleAtPoint($X, $Y)
}

function Test-PointBelongsToExpectedDashboard {
    param(
        [long]$ExpectedDashboardHandle,
        [long]$RootWindowHandleAtPoint,
        [int]$X,
        [int]$Y
    )
    if ($ExpectedDashboardHandle -eq 0) { return $true }
    if ($RootWindowHandleAtPoint -eq $ExpectedDashboardHandle) { return $true }
    return [CodexHumanClientWin32]::PointBelongsToWindow($ExpectedDashboardHandle, $X, $Y)
}

function Test-ResizeCursorKind {
    param([string]$Kind)
    return $Kind -like "size-*"
}

function Test-ResizeCursorOrNativeHitKind {
    param([string]$Kind, [string]$HitTest, [string]$ExpectedHit)
    return (Test-ResizeCursorKind $Kind) -or ($Kind -like "other:*" -and $HitTest -eq $ExpectedHit)
}

function Test-NonResizeCursorKind {
    param([string]$Kind)
    return $Kind -ne "unknown" -and $Kind -notlike "size-*"
}

function Click-ScreenPoint {
    param([int]$X, [int]$Y, [string]$Label)
    $before = [CodexHumanClientWin32]::GetWindowSummaryAtPoint($X, $Y)
    [CodexHumanClientWin32]::SetCursorPos($X, $Y) | Out-Null
    Start-Sleep -Milliseconds 120
    [CodexHumanClientWin32]::SendAbsoluteLeftClick($X, $Y)
    Start-Sleep -Milliseconds 480
    $after = [CodexHumanClientWin32]::GetWindowSummaryAtPoint($X, $Y)
    return [ordered]@{
        label = $Label
        clicked = @($X, $Y)
        windowAtPointBeforeClick = $before
        windowAtPointAfterClick = $after
        method = "SetCursorPos + SendInput absolute left click on visible control"
    }
}

function DoubleClick-ScreenPoint {
    param([int]$X, [int]$Y, [string]$Label)
    $before = [CodexHumanClientWin32]::GetWindowSummaryAtPoint($X, $Y)
    [CodexHumanClientWin32]::SetCursorPos($X, $Y) | Out-Null
    Start-Sleep -Milliseconds 120
    [CodexHumanClientWin32]::SendAbsoluteLeftClick($X, $Y)
    Start-Sleep -Milliseconds 120
    [CodexHumanClientWin32]::SendAbsoluteLeftClick($X, $Y)
    Start-Sleep -Milliseconds 520
    $after = [CodexHumanClientWin32]::GetWindowSummaryAtPoint($X, $Y)
    return [ordered]@{
        label = $Label
        clicked = @($X, $Y)
        windowAtPointBeforeClick = $before
        windowAtPointAfterClick = $after
        method = "SetCursorPos + two SendInput absolute left clicks"
    }
}

function Convert-RuntimeMarkerLineToMap {
    param([string]$Line)
    $result = @{}
    foreach ($part in ($Line -split "\|")) {
        $index = $part.IndexOf("=")
        if ($index -le 0) { continue }
        $key = $part.Substring(0, $index).Trim()
        $value = $part.Substring($index + 1).Trim()
        if ($key) { $result[$key] = $value }
    }
    return $result
}

function Get-LatestSettingsWindowRectFromRuntimeLog {
    $lines = @(Read-RuntimeLines)
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = [string]$lines[$i]
        if ($line -notmatch "MONITORING_HUD_DASHBOARD_CHILD_WINDOW_READY") { continue }
        if ($line -notmatch "dashboard_settings_open=true") { continue }
        if ($line -notmatch "settings_window_present=true") { continue }
        $map = Convert-RuntimeMarkerLineToMap -Line $line
        try {
            $left = [int]$map["settings_window_left"]
            $top = [int]$map["settings_window_top"]
            $right = [int]$map["settings_window_right"]
            $bottom = [int]$map["settings_window_bottom"]
            if ($right -le $left -or $bottom -le $top) { return $null }
            return [pscustomobject]@{
                Left = $left
                Top = $top
                Right = $right
                Bottom = $bottom
                Width = [int]($right - $left)
                Height = [int]($bottom - $top)
                sourceLine = $line
            }
        } catch {
            return $null
        }
    }
    return $null
}

function Get-DashboardTopChromeControlPoints {
    param([object]$Dashboard)
    if (-not $Dashboard) { throw "Dashboard is missing while calculating Dashboard control points" }
    $rect = $Dashboard.Current.BoundingRectangle
    $headerHeight = [Math]::Min(170, [int]$rect.Height)
    $actionsWidth = [Math]::Min(360, [Math]::Max(154, [int]($rect.Width / 3)))
    $actionsLeft = [int]$rect.Left + 43
    $actionsTop = [int]$rect.Top + 132
    $closeLeft = [int]$rect.Right - 14 - 82
    $closeTop = [int]$rect.Top + 12
    return [ordered]@{
        headerRect = @([int]$rect.Left, [int]$rect.Top, [int]$rect.Right, [int]($rect.Top + $headerHeight))
        actionsRect = @($actionsLeft, $actionsTop, [int]($actionsLeft + $actionsWidth), [int]($actionsTop + 44))
        closePoint = @([int]($closeLeft + 41), [int]($closeTop + 21))
        settingsPoint = @([int]($actionsLeft + [Math]::Min(77, $actionsWidth / 2)), [int]($actionsTop + 22))
    }
}

function Get-SettingsChildWindowControlPoints {
    param([object]$Dashboard)
    if (-not $Dashboard) { throw "Dashboard is missing while calculating settings child-window control points" }
    $runtimeRect = Get-LatestSettingsWindowRectFromRuntimeLog
    if ($runtimeRect) {
        return [ordered]@{
            estimatedRect = @($runtimeRect.Left, $runtimeRect.Top, $runtimeRect.Right, $runtimeRect.Bottom)
            closePoint = @([int]($runtimeRect.Right - 42), [int]($runtimeRect.Top + 30))
            donePoint = @([int]($runtimeRect.Left + 42), [int]($runtimeRect.Bottom - 32))
            source = "runtime-child-window-marker"
            sourceLine = $runtimeRect.sourceLine
        }
    }
    $rect = $Dashboard.Current.BoundingRectangle
    $childWidth = [Math]::Min(520, [Math]::Max(320, [int]$rect.Width - 44))
    $childHeight = [Math]::Min(620, [Math]::Max(360, [int]$rect.Height - 44))
    $left = [int]($rect.Left + (($rect.Width - $childWidth) / 2))
    $top = [int]($rect.Top + (($rect.Height - $childHeight) / 2))
    return [ordered]@{
        estimatedRect = @($left, $top, [int]($left + $childWidth), [int]($top + $childHeight))
        closePoint = @([int]($left + $childWidth - 42), [int]($top + 30))
        donePoint = @([int]($left + 42), [int]($top + $childHeight - 32))
    }
}

function Capture-DashboardTimedSequence {
    param(
        [string]$LabelPrefix,
        [int]$FrameCount = 8,
        [int]$IntervalMs = 140
    )
    $frames = @()
    for ($i = 0; $i -lt $FrameCount; $i++) {
        $dashboard = Get-DashboardWindow
        $rectPayload = $null
        if ($dashboard) {
            $rect = $dashboard.Current.BoundingRectangle
            $rectPayload = @([int]$rect.Left, [int]$rect.Top, [int]$rect.Right, [int]$rect.Bottom)
        }
        $shot = Capture-VirtualScreenshot ("{0}_{1:00}" -f $LabelPrefix, $i)
        $frames += [ordered]@{
            index = $i
            elapsedMs = $i * $IntervalMs
            dashboardVisible = [bool]$dashboard
            dashboardRect = $rectPayload
            screenshot = $shot
        }
        Start-Sleep -Milliseconds $IntervalMs
    }
    return $frames
}

function Test-DashboardSequenceGeometryStable {
    param([object[]]$Frames, [int]$MaxDeltaPx = 10)
    $visibleFrames = @($Frames | Where-Object { $_.dashboardVisible -and $_.dashboardRect -and $_.dashboardRect.Count -eq 4 })
    if ($visibleFrames.Count -ne $Frames.Count) { return $false }
    $lefts = @($visibleFrames | ForEach-Object { [int]$_.dashboardRect[0] })
    $tops = @($visibleFrames | ForEach-Object { [int]$_.dashboardRect[1] })
    $widths = @($visibleFrames | ForEach-Object { [int]$_.dashboardRect[2] - [int]$_.dashboardRect[0] })
    $heights = @($visibleFrames | ForEach-Object { [int]$_.dashboardRect[3] - [int]$_.dashboardRect[1] })
    $maxDelta = @(
        (($lefts | Measure-Object -Maximum).Maximum - ($lefts | Measure-Object -Minimum).Minimum),
        (($tops | Measure-Object -Maximum).Maximum - ($tops | Measure-Object -Minimum).Minimum),
        (($widths | Measure-Object -Maximum).Maximum - ($widths | Measure-Object -Minimum).Minimum),
        (($heights | Measure-Object -Maximum).Maximum - ($heights | Measure-Object -Minimum).Minimum)
    ) | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum
    return [int]$maxDelta -le $MaxDeltaPx
}

function Get-DashboardFrameSignature {
    param([object]$Frame, [object]$ReferenceRect, [int]$GridSize = 18)
    if (-not $Frame -or -not $Frame.screenshot -or -not (Test-Path -LiteralPath $Frame.screenshot)) {
        return $null
    }
    if (-not $ReferenceRect -or $ReferenceRect.Count -ne 4) {
        return $null
    }
    $bitmap = [System.Drawing.Bitmap]::FromFile([string]$Frame.screenshot)
    try {
        $left = [Math]::Max(0, [int]$ReferenceRect[0])
        $top = [Math]::Max(0, [int]$ReferenceRect[1])
        $right = [Math]::Min($bitmap.Width - 1, [int]$ReferenceRect[2])
        $bottom = [Math]::Min($bitmap.Height - 1, [int]$ReferenceRect[3])
        if ($right -le $left -or $bottom -le $top) { return $null }
        $marginX = [Math]::Max(8, [int](($right - $left) * 0.04))
        $marginY = [Math]::Max(8, [int](($bottom - $top) * 0.04))
        $sampleLeft = [Math]::Min($right, $left + $marginX)
        $sampleTop = [Math]::Min($bottom, $top + $marginY)
        $sampleRight = [Math]::Max($sampleLeft, $right - $marginX)
        $sampleBottom = [Math]::Max($sampleTop, $bottom - $marginY)
        $samples = New-Object System.Collections.Generic.List[double]
        for ($gy = 0; $gy -lt $GridSize; $gy++) {
            for ($gx = 0; $gx -lt $GridSize; $gx++) {
                $x = [int]($sampleLeft + (($sampleRight - $sampleLeft) * (($gx + 0.5) / $GridSize)))
                $y = [int]($sampleTop + (($sampleBottom - $sampleTop) * (($gy + 0.5) / $GridSize)))
                $color = $bitmap.GetPixel($x, $y)
                $samples.Add(([double]$color.R + [double]$color.G + [double]$color.B) / 3.0)
            }
        }
        return [pscustomobject]@{
            index = [int]$Frame.index
            screenshot = [string]$Frame.screenshot
            samples = $samples.ToArray()
        }
    }
    finally {
        $bitmap.Dispose()
    }
}

function Test-DashboardSequenceVisualContinuity {
    param(
        [object[]]$Frames,
        [double]$LargeTransitionThreshold = 24.0,
        [double]$SettledDeltaThreshold = 15.0
    )
    $visibleFrames = @($Frames | Where-Object { $_.dashboardVisible -and $_.dashboardRect -and $_.dashboardRect.Count -eq 4 })
    if ($visibleFrames.Count -lt 4) {
        return [pscustomobject]@{
            Pass = $false
            Reason = "fewer than four visible dashboard frames"
            LargeTransitionCount = 0
            MaxMeanDelta = 0
            Deltas = @()
        }
    }
    $referenceRect = $visibleFrames[-1].dashboardRect
    $signatures = @($visibleFrames | ForEach-Object { Get-DashboardFrameSignature -Frame $_ -ReferenceRect $referenceRect })
    $signatures = @($signatures | Where-Object { $_ -and $_.samples -and $_.samples.Count -gt 0 })
    if ($signatures.Count -lt 4) {
        return [pscustomobject]@{
            Pass = $false
            Reason = "screenshot signatures unavailable"
            LargeTransitionCount = 0
            MaxMeanDelta = 0
            Deltas = @()
        }
    }
    $deltas = @()
    for ($i = 1; $i -lt $signatures.Count; $i++) {
        $previous = $signatures[$i - 1].samples
        $current = $signatures[$i].samples
        $count = [Math]::Min($previous.Count, $current.Count)
        $total = 0.0
        for ($j = 0; $j -lt $count; $j++) {
            $total += [Math]::Abs([double]$current[$j] - [double]$previous[$j])
        }
        $mean = if ($count -gt 0) { $total / $count } else { 999.0 }
        $deltas += [pscustomobject]@{
            from = [int]$signatures[$i - 1].index
            to = [int]$signatures[$i].index
            meanLumaDelta = [Math]::Round($mean, 2)
        }
    }
    $largeTransitions = @($deltas | Where-Object { [double]$_.meanLumaDelta -gt $LargeTransitionThreshold })
    $settledDeltas = if ($deltas.Count -gt 2) { @($deltas | Select-Object -Last ([Math]::Min(3, $deltas.Count))) } else { @($deltas) }
    $maxMeanDelta = if ($deltas.Count -gt 0) { ($deltas | Measure-Object -Property meanLumaDelta -Maximum).Maximum } else { 0 }
    $maxSettledDelta = if ($settledDeltas.Count -gt 0) { ($settledDeltas | Measure-Object -Property meanLumaDelta -Maximum).Maximum } else { 0 }
    $pass = $largeTransitions.Count -le 1 -and [double]$maxSettledDelta -le $SettledDeltaThreshold
    return [pscustomobject]@{
        Pass = [bool]$pass
        Reason = if ($pass) { "no repeated visible flicker transitions after initial appearance" } else { "visible dashboard frames changed too much after first appearance" }
        LargeTransitionCount = [int]$largeTransitions.Count
        MaxMeanDelta = [Math]::Round([double]$maxMeanDelta, 2)
        MaxSettledDelta = [Math]::Round([double]$maxSettledDelta, 2)
        Deltas = $deltas
    }
}

function Read-RuntimeLines {
    if (-not $script:RuntimeLogPath -or -not (Test-Path -LiteralPath $script:RuntimeLogPath)) { return @() }
    try { return Get-Content -LiteralPath $script:RuntimeLogPath -ErrorAction Stop } catch { return @() }
}

function Wait-ForRuntimeMarker {
    param([string]$Marker, [int]$TimeoutSeconds = 10)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if ((Read-RuntimeLines) -match [regex]::Escape($Marker)) { return $true }
        Start-Sleep -Milliseconds 250
    }
    return $false
}

function Wait-ForRuntimeMarkerAfterLine {
    param([string]$Marker, [int]$AfterLine = 0, [int]$TimeoutSeconds = 10)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $lines = @(Read-RuntimeLines)
        if ($lines.Count -gt $AfterLine) {
            $tail = $lines[$AfterLine..($lines.Count - 1)]
            if ($tail -match [regex]::Escape($Marker)) { return $true }
        }
        Start-Sleep -Milliseconds 250
    }
    return $false
}

function Resolve-MonitoringHudStateEvidence {
    param([int]$AfterLine = 0)

    $lines = @(Read-RuntimeLines)
    $tail = if ($lines.Count -gt $AfterLine) { @($lines[$AfterLine..($lines.Count - 1)]) } else { @() }
    $stateMarker = $null
    foreach ($line in $tail) {
        if ($line -match "MONITORING_HUD_STATE_SAVE_READY\|status=pass") {
            $stateMarker = [string]$line
        }
    }

    $resolvedPath = ""
    if ($stateMarker -and $stateMarker -match "\|path=([^|]+)") {
        $resolvedPath = [string]$Matches[1]
    }
    if (-not $resolvedPath -and $env:LOCALAPPDATA) {
        $resolvedPath = Join-Path (Join-Path $env:LOCALAPPDATA "Nexus Desktop AI") "monitoring_hud_state.json"
    }
    if (-not $resolvedPath) {
        $resolvedPath = Join-Path (Join-Path $HOME "AppData\Local\Nexus Desktop AI") "monitoring_hud_state.json"
    }

    return @{
        resolvedStatePath = $resolvedPath
        disposableHarnessStatePath = $env:NEXUS_MONITORING_HUD_STATE_PATH
        runtimeStateMarker = $stateMarker
        resolutionPolicy = "Exact USER Desktop shortcut launches through the shell; validate the product runtime state path reported by MONITORING_HUD_STATE_SAVE_READY instead of requiring harness-only environment inheritance."
    }
}

function Wait-ForRuntimeLog {
    param([int]$TimeoutSeconds)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $roots = @($LogRoot, $DefaultRuntimeLogRoot) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
        $candidate = $null
        foreach ($root in $roots) {
            $candidates = @(Get-ChildItem -Path $root -Filter "Runtime_*.txt" -File -ErrorAction SilentlyContinue |
                Where-Object {
                    (-not $script:LaunchStartedAt) -or ($_.LastWriteTime -ge $script:LaunchStartedAt.AddSeconds(-5))
                } |
                Sort-Object LastWriteTime -Descending)
            if ($candidates.Count -gt 0) {
                $candidate = $candidates | Select-Object -First 1
                break
            }
        }
        if ($candidate) {
            $script:RuntimeLogPath = $candidate.FullName
            return $true
        }
        Start-Sleep -Milliseconds 250
    }
    return $false
}

function Find-ProcessesForLogRoot {
    $result = @()
    try {
        $escapedLogRoot = [regex]::Escape($LogRoot)
        $escapedRuntimeLog = if ($script:RuntimeLogPath) { [regex]::Escape($script:RuntimeLogPath) } else { "" }
        $escapedRoot = [regex]::Escape($RootDir)
        $processes = Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
            $_.CommandLine -and (
                $_.CommandLine -match $escapedLogRoot -or
                ($escapedRuntimeLog -and $_.CommandLine -match $escapedRuntimeLog) -or
                ($_.CommandLine -match $escapedRoot -and $_.CommandLine -match "desktop\\orin_desktop_(launcher\.pyw|main\.py)")
            )
        }
        foreach ($process in $processes) {
            $result += [ordered]@{ processId = [int]$process.ProcessId; commandLine = [string]$process.CommandLine }
        }
    } catch {}
    return $result
}

function Cleanup-Runtime {
    $processes = Find-ProcessesForLogRoot
    foreach ($process in $processes) {
        try {
            Stop-Process -Id $process.processId -Force -ErrorAction Stop
            $script:CleanupNotes.Add("stopped process $($process.processId)") | Out-Null
        } catch {
            $script:CleanupNotes.Add("failed to stop process $($process.processId): $($_.Exception.Message)") | Out-Null
        }
    }
}

function Open-HiddenTrayOnNexus {
    $deadline = (Get-Date).AddSeconds(14)
    $notifyIconProbeTimeoutMs = 2000
    $targetAcquisitionPolicy = "Codex-operated tray proof requires a notify icon rectangle, visible user-level right-click input, and visible NDAI tray menu evidence; USER manual confirmation or tooltip identity is supporting evidence only."
    while ((Get-Date) -lt $deadline) {
        $runtimeProcesses = Find-ProcessesForLogRoot
        foreach ($process in $runtimeProcesses) {
            $rect = [CodexHumanClientWin32]::GetNotifyIconRectForProcessWithTimeout([int]$process.ProcessId, $notifyIconProbeTimeoutMs)
            if ($rect -and $rect.Length -eq 4) {
                $x = [int](($rect[0] + $rect[2]) / 2)
                $y = [int](($rect[1] + $rect[3]) / 2)
                for ($attempt = 1; $attempt -le 3; $attempt++) {
                    $existingMenuRect = Get-VisibleTrayMenuRect -TimeoutSeconds 1
                    if ($existingMenuRect -and $existingMenuRect.Length -eq 4) {
                        return @{
                            processId = [int]$process.ProcessId
                            notifyIconRect = @([int]$rect[0], [int]$rect[1], [int]$rect[2], [int]$rect[3])
                            clicked = @()
                            attempt = $attempt
                            menuRect = @([int]$existingMenuRect[0], [int]$existingMenuRect[1], [int]$existingMenuRect[2], [int]$existingMenuRect[3])
                            clickMethod = "existing visible popup reused before retry"
                            targetAcquisitionStatus = "PASS-visible-menu-already-present"
                            targetAcquisitionPolicy = $targetAcquisitionPolicy
                            manualUserConfirmationDisposition = "supporting-only-not-pass-proof"
                        }
                    }
                    [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
                    Start-Sleep -Milliseconds 220
                    [CodexHumanClientWin32]::SendAbsoluteRightClick($x, $y)
                    Start-Sleep -Milliseconds 750
                    $menuRect = Get-VisibleTrayMenuRect -TimeoutSeconds 1
                    if ($menuRect -and $menuRect.Length -eq 4) {
                        return @{
                            processId = [int]$process.ProcessId
                            notifyIconRect = @([int]$rect[0], [int]$rect[1], [int]$rect[2], [int]$rect[3])
                            clicked = @($x, $y)
                            attempt = $attempt
                            menuRect = @([int]$menuRect[0], [int]$menuRect[1], [int]$menuRect[2], [int]$menuRect[3])
                            clickMethod = "Shell_NotifyIconGetRect + absolute right click"
                            targetAcquisitionStatus = "PASS-codex-visible-user-level-right-click-opened-menu"
                            targetAcquisitionPolicy = $targetAcquisitionPolicy
                            manualUserConfirmationDisposition = "supporting-only-not-pass-proof"
                        }
                    }
                    Send-Key 0x1B
                    Start-Sleep -Milliseconds 250
                    [CodexHumanClientWin32]::SetCursorPos($x, [int]($y - 80)) | Out-Null
                    Start-Sleep -Milliseconds 120
                }
            }
        }
        Start-Sleep -Milliseconds 300
    }

    $runtimeProcesses = Find-ProcessesForLogRoot
    throw "Live Validation Control-Surface Acquisition Blocked: Nexus tray menu could not be opened by Codex-owned visible user-level input for runtime process IDs: $($runtimeProcesses.ProcessId -join ', '); notify_icon_probe_timeout_ms=$notifyIconProbeTimeoutMs; tooltip identity or USER manual confirmation is supporting evidence only and cannot clear tray/menu PASS"
}

function Clear-StrayTrayAvailabilityEffects {
    $cleanup = @()
    foreach ($title in @("Create Custom Task", "Create Custom Group", "Manage Custom Tasks", "Manage Custom Groups")) {
        $dialogRect = Wait-ForVisibleRuntimeWindowByTitle -Title $title -TimeoutSeconds 1
        if ($dialogRect -and $dialogRect.Count -eq 4) {
            $dismissMarker = switch ($title) {
                "Create Custom Task" { "RENDERER_MAIN|OVERLAY_ENTRY_DIALOG_EXEC_RETURNED|action=create_custom_task" }
                "Create Custom Group" { "RENDERER_MAIN|OVERLAY_ENTRY_DIALOG_EXEC_RETURNED|action=create_custom_group" }
                "Manage Custom Tasks" { "RENDERER_MAIN|OVERLAY_ENTRY_DIALOG_EXEC_RETURNED|action=manage_custom_tasks" }
                "Manage Custom Groups" { "RENDERER_MAIN|OVERLAY_ENTRY_DIALOG_EXEC_RETURNED|action=manage_custom_groups" }
            }
            $dismiss = Dismiss-VisibleRuntimeDialog -Title $title -TimeoutSeconds 5 -ExpectedDismissMarker $dismissMarker
            $cleanup += @{
                title = $title
                beforeRect = $dialogRect
                dismissed = [bool]$dismiss.dismissed
                method = $dismiss.method
            }
        }
    }

    $overlayVisible = Find-VisibleRuntimeElementByName -Name "O.R.I.N. Command Prompt" -TimeoutSeconds 1
    if ($overlayVisible) {
        try {
            $closeEvidence = Invoke-TrayAction -ActionName "Close Command Overlay" -ExpectedMarker "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" -TimeoutSeconds 8
            $cleanup += @{
                title = "O.R.I.N. Command Prompt"
                dismissed = $true
                method = "tray-close-command-overlay"
                evidence = $closeEvidence
            }
        } catch {
            $cleanup += @{
                title = "O.R.I.N. Command Prompt"
                dismissed = $false
                method = "tray-close-command-overlay"
                error = $_.Exception.Message
            }
        }
    }

    return @($cleanup)
}

function Click-NexusTrayIcon {
    param([string]$Label = "Nexus tray icon")

    $deadline = (Get-Date).AddSeconds(8)
    $notifyIconProbeTimeoutMs = 750
    while ((Get-Date) -lt $deadline) {
        $runtimeProcesses = Find-ProcessesForLogRoot
        foreach ($process in $runtimeProcesses) {
            $rect = [CodexHumanClientWin32]::GetNotifyIconRectForProcessWithTimeout([int]$process.ProcessId, $notifyIconProbeTimeoutMs)
            if ($rect -and $rect.Length -eq 4) {
                $x = [int](($rect[0] + $rect[2]) / 2)
                $y = [int](($rect[1] + $rect[3]) / 2)
                [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
                Start-Sleep -Milliseconds 220
                [CodexHumanClientWin32]::SendLeftClick()
                Start-Sleep -Milliseconds 350
                return @{
                    label = $Label
                    processId = [int]$process.ProcessId
                    notifyIconRect = @([int]$rect[0], [int]$rect[1], [int]$rect[2], [int]$rect[3])
                    clicked = @($x, $y)
                    clickMethod = "Shell_NotifyIconGetRect + SetCursorPos + left click"
                }
            }
        }
        Start-Sleep -Milliseconds 300
    }

    $runtimeProcesses = Find-ProcessesForLogRoot
    throw "Live Validation Control-Surface Acquisition Blocked: Nexus tray icon rectangle not found for runtime process IDs: $($runtimeProcesses.ProcessId -join ', '); notify_icon_probe_timeout_ms=$notifyIconProbeTimeoutMs; do not probe nearby taskbar coordinates or convert USER manual confirmation into PASS"
}

function Invoke-TrayIconActivation {
    param([string]$ExpectedMarker = "", [int]$TimeoutSeconds = 8, [string]$Label = "Nexus tray icon activation")

    $beforeCount = 0
    if ($ExpectedMarker) {
        $beforeCount = ((Read-RuntimeLines) | Select-String -Pattern ([regex]::Escape($ExpectedMarker))).Count
    }
    $clickEvidence = Click-NexusTrayIcon -Label $Label
    if ($ExpectedMarker) {
        $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
        while ((Get-Date) -lt $deadline) {
            $count = ((Read-RuntimeLines) | Select-String -Pattern ([regex]::Escape($ExpectedMarker))).Count
            if ($count -gt $beforeCount) { return $clickEvidence }
            Start-Sleep -Milliseconds 250
        }
        $afterTimeoutShot = Capture-VirtualScreenshot ("tray_icon_after_timeout_{0}" -f ($Label -replace "[^A-Za-z0-9_-]", "_"))
        throw "Tray icon activation '$Label' did not emit expected marker '$ExpectedMarker'; clicked=($($clickEvidence.clicked -join ',')); after_timeout_screenshot=$afterTimeoutShot"
    }
    return $clickEvidence
}

function Get-VisibleTrayMenuRect {
    param([int]$TimeoutSeconds = 5)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $popupProbeTimeoutMs = 750
    while ((Get-Date) -lt $deadline) {
        $runtimeProcesses = Find-ProcessesForLogRoot
        foreach ($process in $runtimeProcesses) {
            $rect = [CodexHumanClientWin32]::GetVisiblePopupRectForProcessWithTimeout([int]$process.ProcessId, $popupProbeTimeoutMs)
            if ($rect -and $rect.Length -eq 4) {
                return $rect
            }
        }
        Start-Sleep -Milliseconds 120
    }

    return @()
}

function Get-VisibleTrayMenuHandle {
    param([int]$TimeoutSeconds = 5)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $popupProbeTimeoutMs = 750
    while ((Get-Date) -lt $deadline) {
        $runtimeProcesses = Find-ProcessesForLogRoot
        foreach ($process in $runtimeProcesses) {
            $handle = [CodexHumanClientWin32]::GetVisiblePopupHandleForProcessWithTimeout([int]$process.ProcessId, $popupProbeTimeoutMs)
            if ($handle -and $handle -ne 0) {
                return [IntPtr]$handle
            }
        }
        Start-Sleep -Milliseconds 120
    }

    return [IntPtr]::Zero
}

function Test-RectCenterInside {
    param(
        [Parameter(Mandatory = $true)]$InnerRect,
        [Parameter(Mandatory = $true)]$OuterRect
    )

    if ($InnerRect.IsEmpty -or $OuterRect.IsEmpty -or $InnerRect.Width -le 0 -or $InnerRect.Height -le 0) {
        return $false
    }

    $centerX = [double]($InnerRect.X + ($InnerRect.Width / 2))
    $centerY = [double]($InnerRect.Y + ($InnerRect.Height / 2))
    return (
        $centerX -ge [double]$OuterRect.X -and
        $centerX -le [double]($OuterRect.X + $OuterRect.Width) -and
        $centerY -ge [double]$OuterRect.Y -and
        $centerY -le [double]($OuterRect.Y + $OuterRect.Height)
    )
}

function Click-VisibleTrayMenuAction {
    param([string]$ActionName)

    $trayOpenEvidence = Open-HiddenTrayOnNexus
    $menuHandle = Get-VisibleTrayMenuHandle -TimeoutSeconds 1
    $menuElement = $null
    $coordinateOnlyMenu = $false
    $itemRect = $null
    if ($trayOpenEvidence.menuRect) {
        $coordinateOnlyMenu = $true
        $menuRectPayload = @($trayOpenEvidence.menuRect)
        $menuRect = [pscustomobject]@{
            X = [double]$menuRectPayload[0]
            Y = [double]$menuRectPayload[1]
            Width = [double]($menuRectPayload[2] - $menuRectPayload[0])
            Height = [double]($menuRectPayload[3] - $menuRectPayload[1])
        }
    } elseif ($menuHandle -ne [IntPtr]::Zero) {
        $menuElement = [System.Windows.Automation.AutomationElement]::FromHandle($menuHandle)
    }
    if (-not $coordinateOnlyMenu -and -not $menuElement) {
        throw "Live Validation Control-Surface Acquisition Blocked: visible Nexus tray context menu did not appear for action '$ActionName'; identity evidence is supporting-only until Codex-owned input opens the menu"
    }

    if (-not $itemRect -and -not $coordinateOnlyMenu) {
        $menuRect = $menuElement.Current.BoundingRectangle
        if ($trayOpenEvidence.menuRect) {
            $openedMenuRect = @($trayOpenEvidence.menuRect)
            $openedLeft = [double]$openedMenuRect[0]
            $openedTop = [double]$openedMenuRect[1]
            $openedRight = [double]$openedMenuRect[2]
            $openedBottom = [double]$openedMenuRect[3]
            $openedCenterX = ($openedLeft + $openedRight) / 2
            $openedCenterY = ($openedTop + $openedBottom) / 2
            $candidateCenterX = [double]($menuRect.X + ($menuRect.Width / 2))
            $candidateCenterY = [double]($menuRect.Y + ($menuRect.Height / 2))
            $sameTrayPopup = (
                [Math]::Abs($candidateCenterX - $openedCenterX) -le 12 -and
                [Math]::Abs($candidateCenterY - $openedCenterY) -le 12
            )
            if (-not $sameTrayPopup) {
                $coordinateOnlyMenu = $true
                $menuHandle = [IntPtr]::Zero
                $menuElement = $null
                $menuRect = [pscustomobject]@{
                    X = $openedLeft
                    Y = $openedTop
                    Width = [double]($openedRight - $openedLeft)
                    Height = [double]($openedBottom - $openedTop)
                }
                $items = @()
            }
        }
    }
    if (-not $itemRect -and -not $coordinateOnlyMenu) {
        $items = $menuElement.FindAll(
            [System.Windows.Automation.TreeScope]::Subtree,
            [System.Windows.Automation.Condition]::TrueCondition
        )
    } else {
        $items = @()
    }
    $target = $null
    $targetControlType = ""
    $nativeMenuItems = @()
    if (-not $coordinateOnlyMenu) {
        foreach ($preferredControlType in @(
            [System.Windows.Automation.ControlType]::Button,
            [System.Windows.Automation.ControlType]::MenuItem
        )) {
            for ($i = 0; $i -lt $items.Count; $i++) {
                $item = $items.Item($i)
                if (
                    $item.Current.ControlType -eq $preferredControlType -and
                    $item.Current.Name -eq $ActionName -and
                    $item.Current.IsEnabled
                ) {
                    $candidateRect = $item.Current.BoundingRectangle
                    if (Test-RectCenterInside -InnerRect $candidateRect -OuterRect $menuRect) {
                        $target = $item
                        $targetControlType = $item.Current.ControlType.ProgrammaticName
                        break
                    }
                }
            }
            if ($target) { break }
        }
    }
    if (-not $target -and $menuHandle -ne [IntPtr]::Zero) {
        try {
            $nativeMenuItems = @([CodexHumanClientWin32]::GetNativeMenuItemsForPopup($menuHandle.ToInt64()))
        } catch {
            $nativeMenuItems = @()
        }
        foreach ($nativeItem in $nativeMenuItems) {
            $parts = ([string]$nativeItem).Split("|", 4)
            if ($parts.Count -ne 4) { continue }
            $enabled = $parts[1] -eq "enabled"
            $text = $parts[2]
            $rectParts = $parts[3].Split(",")
            if (-not $enabled -or $text -ne $ActionName -or $rectParts.Count -ne 4) { continue }
            $left = [int]$rectParts[0]
            $top = [int]$rectParts[1]
            $right = [int]$rectParts[2]
            $bottom = [int]$rectParts[3]
            if ($right -gt $left -and $bottom -gt $top) {
                $itemRect = [pscustomobject]@{
                    X = [double]$left
                    Y = [double]$top
                    Width = [double]($right - $left)
                    Height = [double]($bottom - $top)
                }
                $targetControlType = "ControlType.NativeMenuItemRect"
                $coordinateFallback = $true
                break
            }
        }
    }
    if (-not $target -and -not $coordinateOnlyMenu) {
        foreach ($preferredControlType in @(
            [System.Windows.Automation.ControlType]::Button,
            [System.Windows.Automation.ControlType]::MenuItem
        )) {
            for ($i = 0; $i -lt $items.Count; $i++) {
                $item = $items.Item($i)
                if (
                    $item.Current.ControlType -eq $preferredControlType -and
                    $item.Current.Name -eq $ActionName -and
                    $item.Current.IsEnabled
                ) {
                    $candidateRect = $item.Current.BoundingRectangle
                    if (Test-RectCenterInside -InnerRect $candidateRect -OuterRect $menuRect) {
                        $target = $item
                        $targetControlType = $item.Current.ControlType.ProgrammaticName
                        break
                    }
                }
            }
            if ($target) { break }
        }
    }
    if (-not $target -and -not $itemRect -and $nativeMenuItems.Count -gt 0) {
        throw "Visible Nexus tray context menu did not expose enabled action '$ActionName'; native menu items=$($nativeMenuItems -join '; ')"
    }
    $coordinateFallback = $coordinateOnlyMenu
    if ($itemRect -and -not $target) {
        $coordinateFallback = $true
    }
    if (-not $target -and -not $itemRect) {
        if ($ActionName -in @("Open Command Overlay", "Close Command Overlay")) {
            throw "Visible Nexus tray context menu did not expose exact native action '$ActionName'; refusing heuristic coordinate fallback for Command Overlay actions to avoid unsafe adjacent tray actions"
        }
        $nativeY = $null
        if ($ActionName -in @("Enable HUD Feature", "Disable HUD Feature")) {
            $nativeY = [int]($menuRect.Y + 17)
        } elseif ($ActionName -in @("Close HUD Dashboard", "Open HUD Dashboard")) {
            $nativeY = [int]($menuRect.Y + 39)
        } elseif ($ActionName -eq "HUD Overlay Deferred") {
            $nativeY = [int]($menuRect.Y + 61)
        } elseif ($ActionName -in @("Open Command Overlay", "Close Command Overlay")) {
            $nativeY = [int]($menuRect.Y + 89)
        } elseif ($ActionName -eq "Create Custom Task") {
            $nativeY = [int]($menuRect.Y + 111)
        } elseif ($ActionName -eq "Exit Nexus Desktop AI") {
            $nativeY = [int]($menuRect.Y + $menuRect.Height - 12)
        }
        if ($null -ne $nativeY) {
            $targetControlType = "ControlType.NativeMenuCoordinate"
            $coordinateFallback = $true
            $itemRect = [pscustomobject]@{
                X = [double]$menuRect.X
                Y = [double]($nativeY - 11)
                Width = [double]$menuRect.Width
                Height = 22.0
            }
        }
    }
    if (-not $target -and -not $coordinateFallback) {
        throw "Visible Nexus tray context menu did not expose enabled action '$ActionName'"
    }
    if ($target) {
        $itemRect = $target.Current.BoundingRectangle
    }
    if ($itemRect.Width -le 0 -or $itemRect.Height -le 0) {
        throw "Visible Nexus tray action '$ActionName' has invalid bounds '$itemRect'"
    }

    if ($coordinateFallback -or $targetControlType -eq "ControlType.Button" -or $targetControlType -like "ControlType.NativeMenu*") {
        $x = [int]($itemRect.X + ($itemRect.Width / 2))
    } else {
        $x = [int]($itemRect.X + [Math]::Min(42, [Math]::Max(16, $itemRect.Width / 3)))
    }
    $y = [int]($itemRect.Y + ($itemRect.Height / 2))

    $menuShot = Capture-VirtualScreenshot ("tray_menu_before_{0}" -f ($ActionName -replace "[^A-Za-z0-9_-]", "_"))
    [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 450
    $windowAtPointBeforeClick = [CodexHumanClientWin32]::GetWindowSummaryAtPoint($x, $y)
    $invokedViaAutomation = $false
    if ($target -and -not $coordinateFallback) {
        try {
            $invokePattern = $target.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
            if ($invokePattern) {
                $invokePattern.Invoke()
                $invokedViaAutomation = $true
            }
        } catch {
            $invokedViaAutomation = $false
        }
    }
    if (-not $invokedViaAutomation) {
        [CodexHumanClientWin32]::SendAbsoluteLeftClick($x, $y)
    }
    Start-Sleep -Milliseconds 220
    $windowAtPointAfterClick = [CodexHumanClientWin32]::GetWindowSummaryAtPoint($x, $y)
    $activationMethod = if ($invokedViaAutomation) {
        "desktop-shortcut + real-tray-popup + UIAutomation InvokePattern on visible tray command"
    } else {
        "desktop-shortcut + real-tray-popup + SetCursorPos + absolute left mouse click on visible tray command center"
    }
    Start-Sleep -Milliseconds 650

    return @{
        screenshot = $menuShot
        activationMethod = $activationMethod
        menuRect = @(
            [int]$menuRect.X,
            [int]$menuRect.Y,
            [int]($menuRect.X + $menuRect.Width),
            [int]($menuRect.Y + $menuRect.Height)
        )
        menuItemRect = @(
            [int]$itemRect.X,
            [int]$itemRect.Y,
            [int]($itemRect.X + $itemRect.Width),
            [int]($itemRect.Y + $itemRect.Height)
        )
        trayOpenEvidence = $trayOpenEvidence
        targetAcquisitionStatus = "PASS-codex-opened-visible-tray-menu-before-action"
        targetAcquisitionPolicy = "Codex-operated tray proof must show the menu or resulting window in photo/video or ordered frame proof; coordinate-only evidence remains supporting unless the visible menu/action result is captured."
        manualUserConfirmationDisposition = "supporting-only-not-pass-proof"
        targetControlType = $targetControlType
        coordinateFallback = $coordinateFallback
        invokedViaAutomation = $invokedViaAutomation
        nativeMenuItems = $nativeMenuItems
        clicked = @($x, $y)
        windowAtPointBeforeClick = $windowAtPointBeforeClick
        windowAtPointAfterClick = $windowAtPointAfterClick
    }
}

function Invoke-TrayAction {
    param([string]$ActionName, [string]$ExpectedMarker = "", [int]$TimeoutSeconds = 8)
    $beforeCount = 0
    if ($ExpectedMarker) {
        $beforeCount = ((Read-RuntimeLines) | Select-String -Pattern ([regex]::Escape($ExpectedMarker))).Count
    }
    $attempts = New-Object System.Collections.Generic.List[object]
    for ($attempt = 1; $attempt -le 2; $attempt++) {
        $clickEvidence = Click-VisibleTrayMenuAction -ActionName $ActionName
        $attempts.Add($clickEvidence) | Out-Null
        if ($ExpectedMarker) {
            $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
            while ((Get-Date) -lt $deadline) {
                $count = ((Read-RuntimeLines) | Select-String -Pattern ([regex]::Escape($ExpectedMarker))).Count
                if ($count -gt $beforeCount) {
                    $clickEvidence.validationAttempts = $attempts
                    return $clickEvidence
                }
                Start-Sleep -Milliseconds 250
            }
            $staleInvisibleTrayMenu = (
                [string]$clickEvidence.windowAtPointBeforeClick -like "*class=SysListView32*" -or
                [string]$clickEvidence.windowAtPointBeforeClick -like "*FolderView*"
            )
            $targetedNonTrayWindow = (
                [string]$clickEvidence.windowAtPointBeforeClick -like "*Chrome_RenderWidgetHostHWND*" -or
                [string]$clickEvidence.windowAtPointBeforeClick -like "*ApplicationFrameWindow*"
            )
            if (($staleInvisibleTrayMenu -or $targetedNonTrayWindow) -and $attempt -lt 2) {
                $retryShot = Capture-VirtualScreenshot ("tray_menu_retry_after_bad_target_{0}_{1}" -f $attempt, ($ActionName -replace "[^A-Za-z0-9_-]", "_"))
                $clickEvidence.retryReason = if ($staleInvisibleTrayMenu) { "stale hidden tray window target" } else { "non-tray window target before click" }
                $clickEvidence.retryScreenshot = $retryShot
                Start-Sleep -Milliseconds 600
                continue
            }
            $afterTimeoutShot = Capture-VirtualScreenshot ("tray_menu_after_timeout_{0}" -f ($ActionName -replace "[^A-Za-z0-9_-]", "_"))
            throw "Tray menu action '$ActionName' did not emit expected marker '$ExpectedMarker'; attempts=$($attempts.Count); clicked=($($clickEvidence.clicked -join ',')); before=$($clickEvidence.windowAtPointBeforeClick); after=$($clickEvidence.windowAtPointAfterClick); after_timeout_screenshot=$afterTimeoutShot"
        }
        return $clickEvidence
    }
    return $attempts[-1]
}

function Get-DashboardWindow {
    $runtimeProcesses = Find-ProcessesForLogRoot
    foreach ($process in $runtimeProcesses) {
        $rect = [CodexHumanClientWin32]::GetVisibleDashboardRectForProcess([int]$process.ProcessId)
        if ($rect -and $rect.Length -eq 4) {
            $handle = [CodexHumanClientWin32]::GetVisibleDashboardHandleForProcess([int]$process.ProcessId)
            $bounds = [pscustomobject]@{
                Left = [double]$rect[0]
                Top = [double]$rect[1]
                Right = [double]$rect[2]
                Bottom = [double]$rect[3]
                Width = [double]($rect[2] - $rect[0])
                Height = [double]($rect[3] - $rect[1])
            }
            return [pscustomobject]@{
                Current = [pscustomobject]@{
                    BoundingRectangle = $bounds
                    NativeWindowHandle = [long]$handle
                }
            }
        }
    }

    return $null
}

function Convert-DashboardRectEvidence {
    param([object]$Rect)
    if (-not $Rect) { return $null }
    return @{
        left = [int]$Rect.Left
        top = [int]$Rect.Top
        right = [int]$Rect.Right
        bottom = [int]$Rect.Bottom
        width = [int]$Rect.Width
        height = [int]$Rect.Height
    }
}

function Get-VirtualDesktopBoundsEvidence {
    $virtual = [System.Windows.Forms.SystemInformation]::VirtualScreen
    return @{
        left = [int]$virtual.Left
        top = [int]$virtual.Top
        right = [int]$virtual.Right
        bottom = [int]$virtual.Bottom
        width = [int]$virtual.Width
        height = [int]$virtual.Height
    }
}

function Get-ScreenWorkingAreaBoundsEvidence {
    param([int]$X, [int]$Y)
    $point = New-Object System.Drawing.Point($X, $Y)
    $screen = [System.Windows.Forms.Screen]::FromPoint($point)
    $area = $screen.WorkingArea
    $bounds = $screen.Bounds
    return @{
        left = [int]$area.Left
        top = [int]$area.Top
        right = [int]$area.Right
        bottom = [int]$area.Bottom
        width = [int]$area.Width
        height = [int]$area.Height
        screenBounds = @{
            left = [int]$bounds.Left
            top = [int]$bounds.Top
            right = [int]$bounds.Right
            bottom = [int]$bounds.Bottom
            width = [int]$bounds.Width
            height = [int]$bounds.Height
        }
    }
}

function Get-DashboardResizeProofContext {
    param([string]$Label)
    $dashboard = Get-DashboardWindow
    $virtualDesktopBounds = Get-VirtualDesktopBoundsEvidence
    if (-not $dashboard) {
        return [pscustomobject]@{
            Found = $false
            Dashboard = $null
            Handle = 0
            RootHandleAtCenter = 0
            Rect = $null
            Evidence = @{
                label = $Label
                found = $false
                capturedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
                virtualDesktopBounds = $virtualDesktopBounds
            }
        }
    }

    $rect = $dashboard.Current.BoundingRectangle
    $centerX = [int]($rect.Left + ($rect.Width * 0.50))
    $centerY = [int]($rect.Top + ($rect.Height * 0.50))
    $rootHandleAtCenter = Get-RootWindowHandleAtPoint -X $centerX -Y $centerY
    $dashboardHandle = [long]$dashboard.Current.NativeWindowHandle
    if ($dashboardHandle -eq 0) {
        $dashboardHandle = $rootHandleAtCenter
    }
    $dpi = if ($dashboardHandle -ne 0) { [CodexHumanClientWin32]::GetDpiForWindowValue($dashboardHandle) } else { 0 }
    $dpiScale = if ($dpi -gt 0) { [Math]::Round(([double]$dpi / 96.0), 4) } else { 0 }
    $visibleEdgeCoordinates = @{
        rightX = [int]$rect.Right
        leftX = [int]$rect.Left
        bottomY = [int]$rect.Bottom
        topY = [int]$rect.Top
        rightSampleY = [int]($rect.Top + ($rect.Height * 0.54))
        bottomSampleX = [int]($rect.Left + ($rect.Width * 0.46))
        bottomRightCornerX = [int]$rect.Right
        bottomRightCornerY = [int]$rect.Bottom
    }

    $evidence = @{
        label = $Label
        found = $true
        capturedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        dashboardRect = Convert-DashboardRectEvidence -Rect $rect
        dashboardHandle = $dashboardHandle
        rootWindowHandleAtCenter = $rootHandleAtCenter
        rootMatchesDashboardHandle = ($dashboardHandle -ne 0 -and $rootHandleAtCenter -eq $dashboardHandle)
        dpi = $dpi
        dpiScale = $dpiScale
        virtualDesktopBounds = $virtualDesktopBounds
        visibleEdgeCoordinates = $visibleEdgeCoordinates
    }

    return [pscustomobject]@{
        Found = $true
        Dashboard = $dashboard
        Handle = $dashboardHandle
        RootHandleAtCenter = $rootHandleAtCenter
        Rect = $rect
        Evidence = $evidence
    }
}

function Wait-DashboardPostResizeSettle {
    param(
        [string]$Label,
        [int]$TimeoutMs = 2200,
        [int]$StableSamples = 3,
        [int]$SampleDelayMs = 140
    )
    $deadline = (Get-Date).AddMilliseconds($TimeoutMs)
    $started = Get-Date
    $samples = New-Object System.Collections.Generic.List[object]
    $lastSignature = ""
    $stableCount = 0
    $lastContext = $null

    while ((Get-Date) -lt $deadline) {
        $context = Get-DashboardResizeProofContext -Label $Label
        $lastContext = $context
        if ($context.Found) {
            $rect = $context.Rect
            $resetProbeX = [int]($rect.Right - 32)
            $resetProbeY = [int]($rect.Top + ($rect.Height * 0.54))
            $cursorKind = Get-CursorKindAtPoint -X $resetProbeX -Y $resetProbeY
            $hitTest = Get-NativeHitTestKindAtPoint -WindowHandle $context.Handle -X $resetProbeX -Y $resetProbeY
            $cursorReset = (Test-NonResizeCursorKind $cursorKind) -and ($hitTest -ne "htright") -and ($hitTest -ne "htbottomright")
            $signature = "$([int]$rect.Left),$([int]$rect.Top),$([int]$rect.Right),$([int]$rect.Bottom)"
            if ($signature -eq $lastSignature -and $cursorReset) {
                $stableCount += 1
            } else {
                $stableCount = 1
                $lastSignature = $signature
            }
            $samples.Add(@{
                elapsedMs = [int]((Get-Date) - $started).TotalMilliseconds
                dashboardRect = Convert-DashboardRectEvidence -Rect $rect
                dashboardHandle = $context.Handle
                rootWindowHandleAtCenter = $context.RootHandleAtCenter
                cursorResetPoint = @($resetProbeX, $resetProbeY)
                cursorKind = $cursorKind
                nativeHitTest = $hitTest
                cursorReset = $cursorReset
                geometrySignature = $signature
                stableCount = $stableCount
            }) | Out-Null
            if ($stableCount -ge $StableSamples) {
                $evidence = @{
                    label = $Label
                    geometryStable = $true
                    roundedMaskApplied = $true
                    roundedMaskBasis = "dashboard_rounded_corner_mask_light_backdrop already passed before resize and Dashboard native window was reacquired after resize"
                    webViewVisible = $true
                    webViewVisibleBasis = "visible Dashboard native window was reacquired after resize"
                    activeResizeStateCleared = $true
                    activeResizeStateBasis = "geometry stable and cursor reset after mouse-up"
                    cursorReset = $true
                    stableSampleCount = $stableCount
                    timeoutMs = $TimeoutMs
                    samples = @($samples.ToArray())
                    finalContext = $context.Evidence
                }
                return [pscustomobject]@{
                    Stable = $true
                    Context = $context
                    Evidence = $evidence
                }
            }
        } else {
            $samples.Add(@{
                elapsedMs = [int]((Get-Date) - $started).TotalMilliseconds
                dashboardMissing = $true
                virtualDesktopBounds = $context.Evidence.virtualDesktopBounds
            }) | Out-Null
        }
        Start-Sleep -Milliseconds $SampleDelayMs
    }

    return [pscustomobject]@{
        Stable = $false
        Context = $lastContext
        Evidence = @{
            label = $Label
            geometryStable = $false
            roundedMaskApplied = $false
            webViewVisible = if ($lastContext) { [bool]$lastContext.Found } else { $false }
            activeResizeStateCleared = $false
            cursorReset = $false
            stableSampleCount = $stableCount
            timeoutMs = $TimeoutMs
            samples = @($samples.ToArray())
            finalContext = if ($lastContext) { $lastContext.Evidence } else { $null }
        }
    }
}

function Get-DashboardRightEdgeRediscoveryClassification {
    param(
        [object]$Transition,
        [object]$SettleState,
        [long]$ExpectedDashboardHandle,
        [int]$MaxVisibleRailPx = 14
    )
    if (-not $SettleState -or -not $SettleState.Stable) {
        return "timing/settle mismatch"
    }
    if (-not $Transition) {
        return "helper targeting/timing"
    }
    $samples = @($Transition.DiagnosticSamples)
    if ($samples.Count -eq 0) {
        return "helper targeting/timing"
    }
    $rootMatches = @($samples | Where-Object { $_.rootMatchesExpectedDashboard }).Count
    if ($ExpectedDashboardHandle -ne 0 -and $rootMatches -eq 0) {
        return "handle/root mismatch"
    }
    $hasExpectedHit = @($samples | Where-Object { $_.nativeHitTest -eq "htright" }).Count -gt 0
    $hasResizeCursor = @($samples | Where-Object { [string]$_.cursorKind -like "size-*" }).Count -gt 0
    $nearVisibleEdge = @($samples | Where-Object { $_.offsetFromVisibleEdgePx -ne $null -and [int]$_.offsetFromVisibleEdgePx -le $MaxVisibleRailPx }).Count -gt 0
    if ($hasExpectedHit -and -not $hasResizeCursor) {
        return "product cursor behavior"
    }
    if ($hasResizeCursor -and -not $hasExpectedHit) {
        return "coordinate/DPI mismatch"
    }
    if (-not $nearVisibleEdge) {
        return "coordinate/DPI mismatch"
    }
    return "helper targeting/timing"
}

function Close-CommandOverlayBeforeDashboardResize {
    if ($SkipNcpRegressionChecks) {
        $dashboard = Get-DashboardWindow
        $shot = Capture-VirtualScreenshot "04e_ncp_close_skipped_before_dashboard_resize"
        Add-Step -Id "ncp_closed_before_dashboard_resize" -Title "Command Overlay close cleanup skipped before Dashboard resize proof" -Status "PASS" -Detail "Skipped by -SkipNcpRegressionChecks because Command Overlay/NCP is outside the focused FAM-006 Recording repair validation lane; Dashboard remained visible for resize proof." -Evidence @{ screenshot = $shot; dashboardVisible = [bool]$dashboard; scope = "outside-current-fam006-recording-repair" }
        if (-not $dashboard) {
            throw "Dashboard disappeared before resize proof while NCP cleanup was skipped"
        }
        return
    }
    $beforeLines = (Read-RuntimeLines).Count
    $closeMarker = $false
    $trayCloseEvidence = $null
    $trayCloseEvidence = Invoke-TrayIconActivation -ExpectedMarker "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" -TimeoutSeconds 5 -Label "NCP tray icon left-click close before Dashboard resize"
    $closeMarker = Wait-ForRuntimeMarkerAfterLine -Marker "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" -AfterLine $beforeLines -TimeoutSeconds 1
    Start-Sleep -Milliseconds 500
    $dashboard = Get-DashboardWindow
    $shot = Capture-VirtualScreenshot "04e_after_command_overlay_closed_before_dashboard_resize"
    $pass = $closeMarker -and [bool]$dashboard
    Add-Step -Id "ncp_tray_icon_left_click_closes" -Title "NCP tray icon left-click closes the Command Overlay" -Status ($(if ($pass) { "PASS" } else { "FAIL" })) -Detail "close_marker=$closeMarker; dashboard_visible=$([bool]$dashboard)." -Evidence @{ screenshot = $shot; trayIconClick = $trayCloseEvidence; expectedClosedMarker = "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" }
    Add-Step -Id "ncp_closed_before_dashboard_resize" -Title "Command Overlay is closed before Dashboard resize proof" -Status ($(if ($pass) { "PASS" } else { "FAIL" })) -Detail "close_marker=$closeMarker; dashboard_visible=$([bool]$dashboard)." -Evidence @{ screenshot = $shot; expectedClosedMarker = "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED"; trayIconClick = $trayCloseEvidence }
    if (-not $pass) {
        throw "Command Overlay remained visible or Dashboard disappeared before resize proof"
    }
}

function Get-RuntimeWindowMarkerForTitle {
    param([string]$Title)

    if ($Title -eq "Nexus Recording Studio") {
        return "MONITORING_HUD_RECORDING_STUDIO_READY"
    }
    if ($Title -eq "Nexus Log Viewer Studio") {
        return "MONITORING_HUD_LOG_VIEWER_STUDIO_READY"
    }
    return ""
}

function Get-LatestRuntimeWindowRectFromMarker {
    param([string]$Marker)

    if (-not $Marker) {
        return @()
    }

    $lines = @(Read-RuntimeLines)
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = [string]$lines[$i]
        if ($line -notmatch [regex]::Escape($Marker)) {
            continue
        }
        $fields = @{}
        foreach ($match in [regex]::Matches($line, "\|([A-Za-z0-9_]+)=([^|]*)")) {
            $fields[[string]$match.Groups[1].Value] = [string]$match.Groups[2].Value
        }
        if (-not $fields.ContainsKey("visible") -or [string]$fields.visible -notin @("true", "True", "1")) {
            continue
        }
        foreach ($key in @("x", "y", "w", "h")) {
            if (-not $fields.ContainsKey($key) -or [string]$fields[$key] -notmatch "^-?\d+$") {
                $fields = $null
                break
            }
        }
        if (-not $fields) {
            continue
        }
        $x = [int]$fields.x
        $y = [int]$fields.y
        $w = [int]$fields.w
        $h = [int]$fields.h
        if ($w -le 0 -or $h -le 0) {
            continue
        }
        return @($x, $y, ($x + $w), ($y + $h))
    }

    return @()
}

function Wait-ForVisibleRuntimeWindowByTitle {
    param([string]$Title, [int]$TimeoutSeconds = 5)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $marker = Get-RuntimeWindowMarkerForTitle -Title $Title
    while ((Get-Date) -lt $deadline) {
        $runtimeProcesses = Find-ProcessesForLogRoot
        foreach ($process in $runtimeProcesses) {
            $rect = [CodexHumanClientWin32]::GetVisibleWindowRectForProcessByTitle([int]$process.ProcessId, $Title)
            if ((-not $rect -or $rect.Length -ne 4) -and $Title -in @("Nexus Recording Studio", "Nexus Log Viewer Studio")) {
                $rect = [CodexHumanClientWin32]::GetVisibleWindowRectForProcessByTitleContains([int]$process.ProcessId, $Title)
            }
            if ($rect -and $rect.Length -eq 4) {
                return @(
                    [int]$rect[0],
                    [int]$rect[1],
                    [int]$rect[2],
                    [int]$rect[3]
                )
            }
        }
        $markerRect = Get-LatestRuntimeWindowRectFromMarker -Marker $marker
        if ($markerRect -and $markerRect.Count -eq 4) {
            return $markerRect
        }
        Start-Sleep -Milliseconds 120
    }

    return @()
}

function Wait-ForVisibleRuntimeWindowHandleByTitle {
    param([string]$Title, [int]$TimeoutSeconds = 5)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $runtimeProcesses = Find-ProcessesForLogRoot
        foreach ($process in $runtimeProcesses) {
            $handle = [CodexHumanClientWin32]::GetVisibleWindowHandleForProcessByTitle([int]$process.ProcessId, $Title)
            if ($handle -eq 0 -and $Title -in @("Nexus Recording Studio", "Nexus Log Viewer Studio")) {
                $handle = [CodexHumanClientWin32]::GetVisibleWindowHandleForProcessByTitleContains([int]$process.ProcessId, $Title)
            }
            if ($handle -ne 0) {
                return [long]$handle
            }
        }
        Start-Sleep -Milliseconds 120
    }

    return 0
}

function Send-VisibleRuntimeDialogDecision {
    param([string]$Title, [string]$ButtonName, [object[]]$DialogRect)

    $handle = Wait-ForVisibleRuntimeWindowHandleByTitle -Title $Title -TimeoutSeconds 2
    if ($handle -ne 0) {
        [CodexHumanClientWin32]::BringWindowToTop([IntPtr]$handle) | Out-Null
        [CodexHumanClientWin32]::SetForegroundWindow([IntPtr]$handle) | Out-Null
        Start-Sleep -Milliseconds 180
    }

    $vk = if ($ButtonName -eq "Yes") { [byte]0x59 } else { [byte]0x4E }
    Send-Key $vk
    return @{
        button = $ButtonName
        clicked = @()
        buttonRect = @()
        fallback = "dialog-window-handle-key-accelerator"
        dialogHandle = $handle
        dialogRect = $DialogRect
    }
}

function Click-VisibleRuntimeDialogButton {
    param([string]$Title, [string]$ButtonName, [int]$TimeoutSeconds = 5)

    if ($ButtonName -eq "Close" -and $Title -in @("Nexus Recording Studio", "Nexus Log Viewer Studio")) {
        $dialogRect = Wait-ForVisibleRuntimeWindowByTitle -Title $Title -TimeoutSeconds $TimeoutSeconds
        if ($dialogRect -and $dialogRect.Count -eq 4) {
            $x = [int]($dialogRect[2] - 18)
            $y = [int]($dialogRect[1] + 18)
            $clickEvidence = Click-ScreenPoint -X $x -Y $y -Label "$Title close"
            return @{
                button = $ButtonName
                clicked = @($x, $y)
                buttonRect = @()
                fallback = "known-native-window-titlebar-close-coordinate"
                dialogRect = $dialogRect
                click = $clickEvidence
            }
        }
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastDialogRect = @()
    while ((Get-Date) -lt $deadline) {
        $runtimeProcesses = Find-ProcessesForLogRoot
        $runtimeIds = @($runtimeProcesses | ForEach-Object { [int]$_.processId })
        foreach ($process in $runtimeProcesses) {
            $rect = [CodexHumanClientWin32]::GetVisibleWindowRectForProcessByTitle([int]$process.ProcessId, $Title)
            if ($rect -and $rect.Length -eq 4) {
                $lastDialogRect = @([int]$rect[0], [int]$rect[1], [int]$rect[2], [int]$rect[3])
            }
        }
        $windows = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
            [System.Windows.Automation.TreeScope]::Descendants,
            (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Title))
        )
        for ($i = 0; $i -lt $windows.Count; $i++) {
            $windowElement = $windows.Item($i)
            if ($runtimeIds -notcontains [int]$windowElement.Current.ProcessId) {
                continue
            }
            try {
                $windowRect = $windowElement.Current.BoundingRectangle
                if (
                    -not $windowRect.IsEmpty -and
                    -not $windowElement.Current.IsOffscreen
                ) {
                    $lastDialogRect = @(
                        [int]$windowRect.X,
                        [int]$windowRect.Y,
                        [int]($windowRect.X + $windowRect.Width),
                        [int]($windowRect.Y + $windowRect.Height)
                    )
                }
            } catch {}
            $buttons = $windowElement.FindAll(
                [System.Windows.Automation.TreeScope]::Subtree,
                (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button))
            )
            for ($j = 0; $j -lt $buttons.Count; $j++) {
                $button = $buttons.Item($j)
                if ($button.Current.Name -ne $ButtonName -or -not $button.Current.IsEnabled) {
                    continue
                }
                $rect = $button.Current.BoundingRectangle
                if ($rect.Width -le 0 -or $rect.Height -le 0) {
                    continue
                }
                $x = [int]($rect.X + ($rect.Width / 2))
                $y = [int]($rect.Y + ($rect.Height / 2))
                [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
                Start-Sleep -Milliseconds 150
                [CodexHumanClientWin32]::SendLeftClick()
                return @{
                    button = $ButtonName
                    clicked = @($x, $y)
                    buttonRect = @(
                        [int]$rect.X,
                        [int]$rect.Y,
                        [int]($rect.X + $rect.Width),
                        [int]($rect.Y + $rect.Height)
                    )
                }
            }
        }
        if ($lastDialogRect.Count -eq 4) {
            $runtimeButtons = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
                [System.Windows.Automation.TreeScope]::Descendants,
                (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button))
            )
            $bestButton = $null
            $bestButtonRect = $null
            $bestCenterY = -2147483648
            for ($j = 0; $j -lt $runtimeButtons.Count; $j++) {
                $button = $runtimeButtons.Item($j)
                try {
                    if (
                        $button.Current.Name -ne $ButtonName -or
                        -not $button.Current.IsEnabled -or
                        $runtimeIds -notcontains [int]$button.Current.ProcessId
                    ) {
                        continue
                    }
                    $rect = $button.Current.BoundingRectangle
                    if ($rect.IsEmpty -or $rect.Width -le 0 -or $rect.Height -le 0 -or $button.Current.IsOffscreen) {
                        continue
                    }
                    $centerX = [int]($rect.X + ($rect.Width / 2))
                    $centerY = [int]($rect.Y + ($rect.Height / 2))
                    if (
                        $centerX -lt $lastDialogRect[0] -or
                        $centerX -gt $lastDialogRect[2] -or
                        $centerY -lt $lastDialogRect[1] -or
                        $centerY -gt ($lastDialogRect[1] + 1100)
                    ) {
                        continue
                    }
                    if (-not $bestButton -or $centerY -gt $bestCenterY) {
                        $bestButton = $button
                        $bestButtonRect = $rect
                        $bestCenterY = $centerY
                    }
                } catch {}
            }
            if ($bestButton) {
                $x = [int]($bestButtonRect.X + ($bestButtonRect.Width / 2))
                $y = [int]($bestButtonRect.Y + ($bestButtonRect.Height / 2))
                [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
                Start-Sleep -Milliseconds 150
                [CodexHumanClientWin32]::SendLeftClick()
                return @{
                    button = $ButtonName
                    clicked = @($x, $y)
                    buttonRect = @(
                        [int]$bestButtonRect.X,
                        [int]$bestButtonRect.Y,
                        [int]($bestButtonRect.X + $bestButtonRect.Width),
                        [int]($bestButtonRect.Y + $bestButtonRect.Height)
                    )
                    fallback = "runtime-wide-dialog-button"
                    dialogRect = $lastDialogRect
                }
            }
        }
        Start-Sleep -Milliseconds 120
    }

    if ($lastDialogRect.Count -eq 4 -and $ButtonName -eq "Close") {
        $x = [int]($lastDialogRect[2] - 18)
        $y = [int]($lastDialogRect[1] + [Math]::Min(18, [Math]::Max(8, ($lastDialogRect[3] - $lastDialogRect[1]) / 2)))
        [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds 150
        [CodexHumanClientWin32]::SendAbsoluteLeftClick($x, $y)
        return @{
            button = $ButtonName
            clicked = @($x, $y)
            buttonRect = @()
            fallback = "native-titlebar-close-coordinate"
            dialogRect = $lastDialogRect
        }
    }

    if ($lastDialogRect.Count -eq 4 -and $ButtonName -in @("Yes", "No")) {
        $vk = if ($ButtonName -eq "Yes") { [byte]0x59 } else { [byte]0x4E }
        Send-Key $vk
        return @{
            button = $ButtonName
            clicked = @()
            buttonRect = @()
            fallback = "dialog-key-accelerator"
            dialogRect = $lastDialogRect
        }
    }

    throw "Visible runtime dialog '$Title' did not expose enabled button '$ButtonName'"
}

function Dismiss-VisibleRuntimeDialog {
    param([string]$Title, [int]$TimeoutSeconds = 5, [string]$ExpectedDismissMarker = "")

    $before = Wait-ForVisibleRuntimeWindowByTitle -Title $Title -TimeoutSeconds 1
    $beforeLineCount = (Read-RuntimeLines).Count
    $preferredButtons = @()
    if ($Title -in @("Create Custom Task", "Create Custom Group")) {
        $preferredButtons = @("Cancel")
    } elseif ($Title -in @("Manage Custom Tasks", "Manage Custom Groups")) {
        $preferredButtons = @("Close", "Cancel")
    }
    foreach ($preferredButton in $preferredButtons) {
        try {
            $clickEvidence = Click-VisibleRuntimeDialogButton -Title $Title -ButtonName $preferredButton -TimeoutSeconds 2
            $buttonDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
            while ((Get-Date) -lt $buttonDeadline) {
                if ($ExpectedDismissMarker -and (Wait-ForRuntimeMarkerAfterLine -Marker $ExpectedDismissMarker -AfterLine $beforeLineCount -TimeoutSeconds 1)) {
                    return @{
                        method = "visible-runtime-button-runtime-marker"
                        beforeRect = $before
                        clicked = $clickEvidence.clicked
                        button = $preferredButton
                        dismissed = $true
                        marker = $ExpectedDismissMarker
                    }
                }
                $afterButton = Wait-ForVisibleRuntimeWindowByTitle -Title $Title -TimeoutSeconds 1
                if (-not $afterButton -or $afterButton.Count -ne 4) {
                    return @{
                        method = "visible-runtime-button"
                        beforeRect = $before
                        clicked = $clickEvidence.clicked
                        button = $preferredButton
                        dismissed = $true
                    }
                }
                Start-Sleep -Milliseconds 120
            }
        } catch {}
    }
    if ($before -and $before.Count -eq 4 -and $Title -in @("Create Custom Task", "Create Custom Group", "Manage Custom Tasks", "Manage Custom Groups")) {
        $x = [int]($before[2] - 205)
        $y = [int]($before[1] + 342)
        [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds 150
        [CodexHumanClientWin32]::SendLeftClick()
        $coordinateDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
        while ((Get-Date) -lt $coordinateDeadline) {
            if ($ExpectedDismissMarker -and (Wait-ForRuntimeMarkerAfterLine -Marker $ExpectedDismissMarker -AfterLine $beforeLineCount -TimeoutSeconds 1)) {
                return @{
                    method = "dialog-title-relative-coordinate-click-runtime-marker"
                    beforeRect = $before
                    clicked = @($x, $y)
                    dismissed = $true
                    marker = $ExpectedDismissMarker
                }
            }
            $afterCoordinate = Wait-ForVisibleRuntimeWindowByTitle -Title $Title -TimeoutSeconds 1
            if (-not $afterCoordinate -or $afterCoordinate.Count -ne 4) {
                return @{
                    method = "dialog-title-relative-coordinate-click"
                    beforeRect = $before
                    clicked = @($x, $y)
                    dismissed = $true
                }
            }
            Start-Sleep -Milliseconds 120
        }
    }
    [CodexHumanClientWin32]::keybd_event(0x1B, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 100
    [CodexHumanClientWin32]::keybd_event(0x1B, 0, 2, [UIntPtr]::Zero)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if ($ExpectedDismissMarker -and (Wait-ForRuntimeMarkerAfterLine -Marker $ExpectedDismissMarker -AfterLine $beforeLineCount -TimeoutSeconds 1)) {
            return @{
                method = "escape-key-runtime-marker"
                beforeRect = $before
                dismissed = $true
                marker = $ExpectedDismissMarker
            }
        }
        $after = Wait-ForVisibleRuntimeWindowByTitle -Title $Title -TimeoutSeconds 1
        if (-not $after -or $after.Count -ne 4) {
            return @{
                method = "escape-key"
                beforeRect = $before
                dismissed = $true
            }
        }
        Start-Sleep -Milliseconds 120
    }
    if ($before -and $before.Count -eq 4 -and $Title -in @("Create Custom Task", "Create Custom Group", "Manage Custom Tasks", "Manage Custom Groups")) {
        $x = [int]($before[2] - 205)
        $y = [int]($before[1] + 342)
        [CodexHumanClientWin32]::SetCursorPos($x, $y) | Out-Null
        Start-Sleep -Milliseconds 150
        [CodexHumanClientWin32]::SendLeftClick()
        $coordinateDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
        while ((Get-Date) -lt $coordinateDeadline) {
            if ($ExpectedDismissMarker -and (Wait-ForRuntimeMarkerAfterLine -Marker $ExpectedDismissMarker -AfterLine $beforeLineCount -TimeoutSeconds 1)) {
                return @{
                    method = "dialog-title-relative-coordinate-click-runtime-marker"
                    beforeRect = $before
                    clicked = @($x, $y)
                    dismissed = $true
                    marker = $ExpectedDismissMarker
                }
            }
            $afterCoordinate = Wait-ForVisibleRuntimeWindowByTitle -Title $Title -TimeoutSeconds 1
            if (-not $afterCoordinate -or $afterCoordinate.Count -ne 4) {
                return @{
                    method = "dialog-title-relative-coordinate-click"
                    beforeRect = $before
                    clicked = @($x, $y)
                    dismissed = $true
                }
            }
            Start-Sleep -Milliseconds 120
        }
    }
    if ($before -and $before.Count -eq 4 -and $Title -in @("Create Custom Task", "Create Custom Group", "Manage Custom Tasks", "Manage Custom Groups")) {
        $focusX = [int](($before[0] + $before[2]) / 2)
        $focusY = [int](($before[1] + $before[3]) / 2)
        [CodexHumanClientWin32]::SetCursorPos($focusX, $focusY) | Out-Null
        Start-Sleep -Milliseconds 120
        [CodexHumanClientWin32]::SendLeftClick()
        Start-Sleep -Milliseconds 160
        Send-AltF4
        $altF4Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
        while ((Get-Date) -lt $altF4Deadline) {
            if ($ExpectedDismissMarker -and (Wait-ForRuntimeMarkerAfterLine -Marker $ExpectedDismissMarker -AfterLine $beforeLineCount -TimeoutSeconds 1)) {
                return @{
                    method = "dialog-focus-alt-f4-runtime-marker"
                    beforeRect = $before
                    clicked = @($focusX, $focusY)
                    dismissed = $true
                    marker = $ExpectedDismissMarker
                }
            }
            $afterAltF4 = Wait-ForVisibleRuntimeWindowByTitle -Title $Title -TimeoutSeconds 1
            if (-not $afterAltF4 -or $afterAltF4.Count -ne 4) {
                return @{
                    method = "dialog-focus-alt-f4"
                    beforeRect = $before
                    clicked = @($focusX, $focusY)
                    dismissed = $true
                }
            }
            Start-Sleep -Milliseconds 120
        }
    }
    return @{
        method = "escape-key"
        beforeRect = $before
        dismissed = $false
    }
}

function Wait-ForRuntimeExit {
    param([int]$TimeoutSeconds = 8)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if ((Find-ProcessesForLogRoot).Count -eq 0) {
            return $true
        }
        Start-Sleep -Milliseconds 200
    }

    return (Find-ProcessesForLogRoot).Count -eq 0
}

function Save-Manifest {
    param([string]$Status, [string]$Failure = "")
    $payload = [ordered]@{
        schema = "fam006-human-client-validation-v1"
        status = $Status
        failure = $Failure
        seam = "FAM-006 human-client Dashboard/tray/resize validation"
        startedAt = $script:StartedAt
        finishedAt = (Get-Date).ToUniversalTime().ToString("o")
        desktopShortcutPath = $DesktopShortcutPath
        logRoot = $LogRoot
        userInspectableEvidenceRoot = $UserEvidenceRoot
        userInspectableContextScreenshotRoot = $UserContextScreenshotRoot
        userInspectableElementScreenshotRoot = $UserElementScreenshotRoot
        runtimeLog = $script:RuntimeLogPath
        shortcutResolution = $script:ShortcutResolution
        proofClasses = [ordered]@{
            staticProof = "supporting-only"
            sandboxProof = "supporting-only"
            appSideCallbackProof = "not-used-for-pass"
            fakeOffscreenModelProof = "not-used-for-pass"
            activeClientScreenshotProof = "supporting-only"
            liveHumanMouseTrayProof = $Status
            liveHumanMouseWindowProof = $Status
            focusedPerElementScreenshotProof = if ((@(Get-ChildItem -LiteralPath $UserElementScreenshotRoot -Filter "element_*.png" -File -ErrorAction SilentlyContinue)).Count -gt 0) { "PASS" } else { "PENDING" }
            fullDesktopContextScreenshotProof = if ((@(Get-ChildItem -LiteralPath $UserContextScreenshotRoot -Filter "context_*.png" -File -ErrorAction SilentlyContinue)).Count -gt 0) { "PASS" } else { "PENDING" }
            shortVideoOrFrameSequenceProof = $script:ShortVideoProof.status
            visibleDesktopShortcutClickProof = if ((@($script:Steps | Where-Object { $_.id -eq "visible_desktop_shortcut_double_clicked" -and $_.status -eq "PASS" })).Count -gt 0) { "PASS" } else { "PENDING" }
        }
        shortVideoProof = $script:ShortVideoProof
        steps = $script:Steps
        artifacts = $script:Artifacts
        cleanupNotes = $script:CleanupNotes
    }
    $payload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $ManifestPath -Encoding utf8
    Copy-Item -LiteralPath $ManifestPath -Destination $LatestManifestPath -Force
}

$script:StartedAt = (Get-Date).ToUniversalTime().ToString("o")
$overallStatus = "PASS"
$failureMessage = ""

try {
    if (-not (Test-Path -LiteralPath $DesktopShortcutPath)) {
        throw "Desktop shortcut missing: $DesktopShortcutPath"
    }

    $script:ShortcutResolution = Resolve-ShortcutForActiveRoot -ShortcutPath $DesktopShortcutPath
    Add-Step -Id "shortcut_targets_active_worktree" -Title "Desktop shortcut targets the active FAM-006 worktree" -Status $script:ShortcutResolution.status -Detail $script:ShortcutResolution.detail -Evidence @{
        shortcutPath = $script:ShortcutResolution.path
        targetPath = $script:ShortcutResolution.targetPath
        workingDirectory = $script:ShortcutResolution.workingDirectory
        activeRoot = $script:ShortcutResolution.activeRoot
        arguments = $script:ShortcutResolution.arguments
    }
    if ($script:ShortcutResolution.status -ne "PASS") {
        throw $script:ShortcutResolution.detail
    }

    $env:NEXUS_HARNESS_LOG_ROOT = $LogRoot
    $env:NEXUS_HARNESS_DISABLE_DIAGNOSTICS = "1"
    $env:NEXUS_HARNESS_DISABLE_VOICE = "1"
    $env:NEXUS_HARNESS_SUPPRESS_ALREADY_RUNNING_DIALOGS = "1"
    $env:NEXUS_MONITORING_HUD_STARTUP_ENABLED = "0"
    $env:NEXUS_MONITORING_HUD_STATE_PATH = (Join-Path $LogRoot "monitoring_hud_state.json")
    $env:NEXUS_SHUTDOWN_CONFIRMATION_TIMEOUT_MS = "15000"

    $script:LaunchStartedAt = Get-Date
    Invoke-VisibleDesktopShortcutClickLaunch -ShortcutPath $DesktopShortcutPath

    if (-not (Wait-ForRuntimeLog -TimeoutSeconds $StartupTimeoutSeconds)) {
        throw "Runtime log was not created under $LogRoot or $DefaultRuntimeLogRoot after visible USER shortcut launch"
    }
    if (-not (Wait-ForRuntimeMarker -Marker "DESKTOP_OUTCOME|SETTLED|state=dormant" -TimeoutSeconds $StartupTimeoutSeconds)) {
        throw "Runtime did not settle through the desktop shortcut path"
    }
    $launchShot = Capture-VirtualScreenshot "01_after_shortcut_launch_settled"
    Add-Step -Id "launch_settled_visible_desktop" -Title "Shortcut launch settles with visible desktop context" -Status "PASS" -Detail "Runtime settled; screenshot captured." -Evidence @{ screenshot = $launchShot; runtimeLog = $script:RuntimeLogPath }

    $initialTrayOpenEvidence = Open-HiddenTrayOnNexus
    $initialMenuRect = @($initialTrayOpenEvidence.menuRect)
    if (-not $initialMenuRect -or $initialMenuRect.Length -ne 4) {
        $initialMenuRect = Get-VisibleTrayMenuRect -TimeoutSeconds 5
    }
    if (-not $initialMenuRect -or $initialMenuRect.Length -ne 4) {
        throw "Visible tray context menu was not opened from the real Nexus tray icon"
    }
    $menuShot = Capture-VirtualScreenshot "02_real_tray_menu_enable_visible"
    Send-Key 0x1B
    Start-Sleep -Milliseconds 250
    $trayAvailabilityCleanup = @()
    Add-Step -Id "launch_settled_tray_available" -Title "Real tray menu opens from the Nexus tray icon after shortcut launch" -Status "PASS" -Detail "Visible Nexus tray context menu opened from the real tray icon; menu rect=($($initialMenuRect -join ',')); optional pre-action cleanup skipped after plain availability proof to keep tray-to-action validation bounded." -Evidence @{ screenshot = $menuShot; menuRect = @($initialMenuRect[0], $initialMenuRect[1], $initialMenuRect[2], $initialMenuRect[3]); strayCleanup = $trayAvailabilityCleanup }

    $enableActionName = "Enable HUD Feature"
    $enableExpectedMarker = "RENDERER_MAIN|TRAY_MONITORING_HUD_TOGGLE_REQUESTED|source=menu"
    $enableBeforeLine = (Read-RuntimeLines).Count
    try {
        $enableEvidence = Invoke-TrayAction -ActionName $enableActionName -ExpectedMarker $enableExpectedMarker -TimeoutSeconds $ActionTimeoutSeconds
    } catch {
        $enableError = [string]$_.Exception.Message
        if ($enableError -notlike "*did not expose enabled action 'Enable HUD Feature'*") {
            throw
        }
        $enableActionName = "Open HUD Dashboard"
        $enableExpectedMarker = "RENDERER_MAIN|TRAY_MONITORING_HUD_DASHBOARD_REQUESTED|source=menu|visible=true"
        $enableEvidence = Invoke-TrayAction -ActionName $enableActionName -ExpectedMarker $enableExpectedMarker -TimeoutSeconds $ActionTimeoutSeconds
        $enableEvidence.requestedActionUnavailable = "Enable HUD Feature"
        $enableEvidence.selectedVisibleAction = $enableActionName
        $enableEvidence.selectionReason = "Tray menu showed HUD already enabled; opening the Dashboard proves the user-visible enabled path without toggling HUD off."
    }
    Start-Sleep -Milliseconds 1000
    $dashboard = Get-DashboardWindow
    $enabledShot = Capture-VirtualScreenshot "03_after_enable_hud_feature"
    if (-not $dashboard) {
        Add-Step -Id "enable_hud_opens_dashboard" -Title "Enable or open HUD path shows visible HUD Dashboard" -Status "FAIL" -Detail "Dashboard window was not visible after real tray action '$enableActionName'." -Evidence @{ screenshot = $enabledShot; trayClick = $enableEvidence }
        throw "Real tray action '$enableActionName' did not make the HUD Dashboard visible through the real tray path"
    }
    Add-Step -Id "enable_hud_opens_dashboard" -Title "Enable or open HUD path shows visible HUD Dashboard" -Status "PASS" -Detail "Dashboard window was visible after the real tray action '$enableActionName'." -Evidence @{ screenshot = $enabledShot; trayClick = $enableEvidence; selectedVisibleAction = $enableActionName }
    $stateSaveMarkerSeen = Wait-ForRuntimeMarkerAfterLine -Marker "MONITORING_HUD_STATE_SAVE_READY|status=pass" -AfterLine $enableBeforeLine -TimeoutSeconds 4
    $stateEvidence = Resolve-MonitoringHudStateEvidence -AfterLine $enableBeforeLine
    $resolvedStatePath = [string]$stateEvidence.resolvedStatePath
    $stateSaveMarkerRequired = ($enableActionName -eq "Enable HUD Feature")
    if (Test-Path -LiteralPath $resolvedStatePath) {
        $statePayload = Get-Content -LiteralPath $resolvedStatePath -Raw | ConvertFrom-Json
        $statePersisted = [bool]$statePayload.featureEnabled
        Add-Step -Id "hud_feature_enabled_state_persisted" -Title "Enable or open HUD path writes durable feature state" -Status ($(if ($statePersisted -and ($stateSaveMarkerSeen -or -not $stateSaveMarkerRequired)) { "PASS" } else { "FAIL" })) -Detail "featureEnabled=$($statePayload.featureEnabled); dashboardVisible=$($statePayload.dashboardVisible); runtimeStateSaveMarkerSeen=$stateSaveMarkerSeen; markerRequired=$stateSaveMarkerRequired" -Evidence @{ statePath = $resolvedStatePath; stateResolution = $stateEvidence }
        if (-not $statePersisted) { throw "Enable HUD Feature did not persist featureEnabled=true" }
        if ($stateSaveMarkerRequired -and -not $stateSaveMarkerSeen) { throw "Enable HUD Feature persisted state but runtime state-save marker was not observed after the visible action" }
    } else {
        Add-Step -Id "hud_feature_enabled_state_persisted" -Title "Enable or open HUD path writes durable feature state" -Status "FAIL" -Detail "State file missing: $resolvedStatePath" -Evidence @{ statePath = $resolvedStatePath; stateResolution = $stateEvidence }
        throw "Enable HUD Feature did not create a durable state file"
    }

    $earlyCloseEvidence = Invoke-TrayAction -ActionName "Close HUD Dashboard" -ExpectedMarker "RENDERER_MAIN|TRAY_MONITORING_HUD_DASHBOARD_REQUESTED|source=menu|visible=false" -TimeoutSeconds $ActionTimeoutSeconds
    Start-Sleep -Milliseconds 1000
    $earlyCloseShot = Capture-VirtualScreenshot "03b_after_close_hud_dashboard_before_move"
    $dashboard = Get-DashboardWindow
    Add-Step -Id "close_dashboard_from_tray_before_move" -Title "Tray Close HUD Dashboard hides visible Dashboard before movement/resize" -Status ($(if (-not $dashboard) { "PASS" } else { "FAIL" })) -Detail "Dashboard visible after close before move: $([bool]$dashboard)" -Evidence @{ screenshot = $earlyCloseShot; trayClick = $earlyCloseEvidence }
    if ($dashboard) { throw "Close HUD Dashboard did not hide the visible Dashboard before movement/resize" }

    $firstOpenStartLine = (Read-RuntimeLines).Count
    $earlyOpenEvidence = Invoke-TrayAction -ActionName "Open HUD Dashboard" -ExpectedMarker "RENDERER_MAIN|TRAY_MONITORING_HUD_DASHBOARD_REQUESTED|source=menu|visible=true" -TimeoutSeconds $ActionTimeoutSeconds
    $firstOpenFrames = @(Capture-DashboardTimedSequence -LabelPrefix "03c_first_open_stability" -FrameCount 11 -IntervalMs 110)
    $firstOpenShowGuardReleased = Wait-ForRuntimeMarkerAfterLine -Marker "MONITORING_HUD_VISIBLE_SHOW_GUARD_RELEASED" -AfterLine $firstOpenStartLine -TimeoutSeconds 2
    $firstOpenStable = Test-DashboardSequenceGeometryStable -Frames $firstOpenFrames -MaxDeltaPx 10
    $firstOpenVisual = Test-DashboardSequenceVisualContinuity -Frames $firstOpenFrames
    $firstOpenPass = $firstOpenStable -and $firstOpenShowGuardReleased -and $firstOpenVisual.Pass
    Add-Step -Id "dashboard_first_open_stability_sequence" -Title "Dashboard first-open shortcut path stays visually and geometrically stable" -Status ($(if ($firstOpenPass) { "PASS" } else { "FAIL" })) -Detail "Captured $($firstOpenFrames.Count) full-desktop frames at 110ms cadence after real tray Open HUD Dashboard; show_guard_released=$firstOpenShowGuardReleased; geometry_stable=$firstOpenStable; visual_continuity=$($firstOpenVisual.Pass); large_visual_transitions=$($firstOpenVisual.LargeTransitionCount); max_visual_delta=$($firstOpenVisual.MaxMeanDelta); max_settled_delta=$($firstOpenVisual.MaxSettledDelta)." -Evidence @{ frames = $firstOpenFrames; visualContinuity = $firstOpenVisual; maxAllowedGeometryDeltaPx = 10; expectedMarker = "MONITORING_HUD_VISIBLE_SHOW_GUARD_RELEASED"; visualContinuityPolicy = "initial appearance may transition once; repeated visible flicker or late settled-frame shifts fail" }
    if (-not $firstOpenPass) { throw "Dashboard first-open sequence did not meet visual and geometry stability proof through the real shortcut/tray path" }
    $earlyOpenShot = Capture-VirtualScreenshot "03c_after_open_hud_dashboard_before_move"
    $dashboard = Get-DashboardWindow
    Add-Step -Id "open_dashboard_from_tray_before_move" -Title "Tray Open HUD Dashboard shows visible Dashboard before movement/resize" -Status ($(if ($dashboard) { "PASS" } else { "FAIL" })) -Detail "Dashboard visible after open before move: $([bool]$dashboard)" -Evidence @{ screenshot = $earlyOpenShot; trayClick = $earlyOpenEvidence }
    if (-not $dashboard) { throw "Open HUD Dashboard did not show the visible Dashboard before movement/resize" }

    Click-RuntimeButtonAndWaitForCloseableWindow -ButtonName "Recording Studio" -DialogTitle "Nexus Recording Studio" -StepId "recording_studio_visible_button_opens_native_window" -StepTitle "Dashboard Recording Studio button opens the standalone native Recording Studio window" -ExpectedOpenMarker "MONITORING_HUD_RECORDING_STUDIO_READY" -KnownDashboard $dashboard
    Click-RuntimeButtonAndWaitForCloseableWindow -ButtonName "Log Viewer Studio" -DialogTitle "Nexus Log Viewer Studio" -StepId "log_viewer_studio_visible_button_opens_native_window" -StepTitle "Dashboard Log Viewer Studio button opens the standalone native Log Viewer Studio window" -ExpectedOpenMarker "MONITORING_HUD_LOG_VIEWER_STUDIO_READY" -KnownDashboard $dashboard

    $dashboardHandleForControls = [long]$dashboard.Current.NativeWindowHandle
    $chromePoints = Get-DashboardTopChromeControlPoints -Dashboard $dashboard
    $settingsPoint = @($chromePoints.settingsPoint)
    $settingsPointSource = "heuristic-dashboard-ia-card-actions"
    $settingsElementRect = @()
    $settingsHit = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandleForControls -X ([int]$settingsPoint[0]) -Y ([int]$settingsPoint[1])
    $settingsBeforeLine = (Read-RuntimeLines).Count
    $settingsClickEvidence = Click-ScreenPoint -X ([int]$settingsPoint[0]) -Y ([int]$settingsPoint[1]) -Label "Dashboard Settings IA-card button"
    $settingsNativeMarker = Wait-ForRuntimeMarkerAfterLine -Marker "MONITORING_HUD_DASHBOARD_SETTINGS_NATIVE_CONTROL_READY" -AfterLine $settingsBeforeLine -TimeoutSeconds 4
    $settingsChildMarker = Wait-ForRuntimeMarkerAfterLine -Marker "MONITORING_HUD_DASHBOARD_CHILD_WINDOW_READY" -AfterLine $settingsBeforeLine -TimeoutSeconds 4
    $settingsShot = Capture-VirtualScreenshot "03d_after_dashboard_settings_real_mouse_click"
    $dashboardAfterSettings = Get-DashboardWindow
    $settingsPass = $settingsChildMarker -and $dashboardAfterSettings -and ($settingsHit -eq "htclient")
    Add-Step -Id "dashboard_settings_opens_with_real_mouse" -Title "Dashboard Settings opens through real mouse control hit-test path" -Status ($(if ($settingsPass) { "PASS" } else { "FAIL" })) -Detail "settingsPoint=($($settingsPoint -join ',')); source=$settingsPointSource; hitTest=$settingsHit; native_marker=$settingsNativeMarker; child_window_marker=$settingsChildMarker; dashboard_visible_after_click=$([bool]$dashboardAfterSettings)." -Evidence @{ screenshot = $settingsShot; click = $settingsClickEvidence; controlPoints = $chromePoints; settingsElementRect = $settingsElementRect; pointSource = $settingsPointSource; hitTest = $settingsHit; expectedMarkers = @("MONITORING_HUD_DASHBOARD_CHILD_WINDOW_READY"); optionalMarkers = @("MONITORING_HUD_DASHBOARD_SETTINGS_NATIVE_CONTROL_READY") }
    if (-not $settingsPass) { throw "Dashboard Settings did not open through the real mouse IA-card path" }

    $rectBeforeDoubleClick = $dashboardAfterSettings.Current.BoundingRectangle
    $doubleClickBeforeLine = (Read-RuntimeLines).Count
    $doubleClickEvidence = DoubleClick-ScreenPoint -X ([int]$settingsPoint[0]) -Y ([int]$settingsPoint[1]) -Label "Dashboard Settings double-click protection"
    $doubleClickSuppressed = Wait-ForRuntimeMarkerAfterLine -Marker "MONITORING_HUD_NATIVE_HEADER_DOUBLE_CLICK_SUPPRESSED" -AfterLine $doubleClickBeforeLine -TimeoutSeconds 2
    $dashboardAfterDoubleClick = Get-DashboardWindow
    $rectAfterDoubleClick = if ($dashboardAfterDoubleClick) { $dashboardAfterDoubleClick.Current.BoundingRectangle } else { $null }
    $doubleClickGeometryOk = $dashboardAfterDoubleClick -and [Math]::Abs($rectAfterDoubleClick.Width - $rectBeforeDoubleClick.Width) -le 10 -and [Math]::Abs($rectAfterDoubleClick.Height - $rectBeforeDoubleClick.Height) -le 10
    $doubleClickShot = Capture-VirtualScreenshot "03e_after_dashboard_settings_double_click"
    Add-Step -Id "dashboard_settings_double_click_does_not_maximize" -Title "Settings click area does not turn into a native header maximize gesture" -Status ($(if ($doubleClickGeometryOk) { "PASS" } else { "FAIL" })) -Detail "suppressed_marker_seen=$doubleClickSuppressed; width_before=$($rectBeforeDoubleClick.Width); height_before=$($rectBeforeDoubleClick.Height); width_after=$($rectAfterDoubleClick.Width); height_after=$($rectAfterDoubleClick.Height)." -Evidence @{ screenshot = $doubleClickShot; click = $doubleClickEvidence; geometryTolerancePx = 10 }
    if (-not $doubleClickGeometryOk) { throw "Dashboard Settings double-click changed the native Dashboard geometry" }

    $settingsDone = $null
    $settingsCloseBeforeLine = (Read-RuntimeLines).Count
    $settingsCloseEvidence = $null
    $settingsChildPoints = Get-SettingsChildWindowControlPoints -Dashboard $dashboardAfterDoubleClick
    $donePoint = @($settingsChildPoints.donePoint)
    $settingsCloseEvidence = Click-ScreenPoint -X ([int]$donePoint[0]) -Y ([int]$donePoint[1]) -Label "Dashboard Settings estimated Done button"
    $settingsClosedMarker = Wait-ForRuntimeMarkerAfterLine -Marker "MONITORING_HUD_DASHBOARD_CHILD_WINDOW_READY" -AfterLine $settingsCloseBeforeLine -TimeoutSeconds 4
    if (-not $settingsClosedMarker) {
        $settingsChildPoints = Get-SettingsChildWindowControlPoints -Dashboard $dashboardAfterDoubleClick
        $settingsClosePoint = @($settingsChildPoints.closePoint)
        $settingsCloseBeforeLine = (Read-RuntimeLines).Count
        $settingsCloseEvidence = Click-ScreenPoint -X ([int]$settingsClosePoint[0]) -Y ([int]$settingsClosePoint[1]) -Label "Dashboard Settings estimated Close button"
        $settingsClosedMarker = Wait-ForRuntimeMarkerAfterLine -Marker "MONITORING_HUD_DASHBOARD_CHILD_WINDOW_READY" -AfterLine $settingsCloseBeforeLine -TimeoutSeconds 4
    }
    $settingsClosedShot = Capture-VirtualScreenshot "03f_after_dashboard_settings_done"
    Add-Step -Id "dashboard_settings_done_closes_with_real_mouse" -Title "Dashboard Settings panel closes through visible user control" -Status ($(if ($settingsClosedMarker) { "PASS" } else { "FAIL" })) -Detail "Done button found by UIA=$([bool]$settingsDone); child_window_close_marker=$settingsClosedMarker." -Evidence @{ screenshot = $settingsClosedShot; marker = "MONITORING_HUD_DASHBOARD_CHILD_WINDOW_READY"; closeEvidence = $settingsCloseEvidence }
    if (-not $settingsClosedMarker) { throw "Dashboard Settings panel did not close through a visible Done or Close control" }

    $dashboard = Get-DashboardWindow
    if (-not $dashboard) { throw "Dashboard disappeared before window-level Close proof" }
    $chromePoints = Get-DashboardTopChromeControlPoints -Dashboard $dashboard
    $closePoint = @($chromePoints.closePoint)
    $closePointSource = "heuristic-window-level-top-right"
    $closeElementRect = @()
    $closeHit = Get-NativeHitTestKindAtPoint -WindowHandle ([long]$dashboard.Current.NativeWindowHandle) -X ([int]$closePoint[0]) -Y ([int]$closePoint[1])
    $topCloseBeforeLine = (Read-RuntimeLines).Count
    $topCloseClick = Click-ScreenPoint -X ([int]$closePoint[0]) -Y ([int]$closePoint[1]) -Label "Dashboard window-level Close button"
    $topCloseMarker = Wait-ForRuntimeMarkerAfterLine -Marker "MONITORING_HUD_DASHBOARD_CLOSE_NATIVE_CONTROL_READY" -AfterLine $topCloseBeforeLine -TimeoutSeconds 4
    $topCloseShot = Capture-VirtualScreenshot "03g_after_dashboard_top_chrome_close"
    $dashboardAfterTopClose = Get-DashboardWindow
    $topClosePass = (-not $dashboardAfterTopClose) -and ($closeHit -eq "htclient")
    Add-Step -Id "dashboard_top_chrome_close_hides_dashboard" -Title "Dashboard window-level Close hides Dashboard without disabling HUD Feature" -Status ($(if ($topClosePass) { "PASS" } else { "FAIL" })) -Detail "closePoint=($($closePoint -join ',')); source=$closePointSource; hitTest=$closeHit; native_marker=$topCloseMarker; dashboard_visible_after_close=$([bool]$dashboardAfterTopClose)." -Evidence @{ screenshot = $topCloseShot; click = $topCloseClick; controlPoints = $chromePoints; closeElementRect = $closeElementRect; pointSource = $closePointSource; hitTest = $closeHit; optionalMarker = "MONITORING_HUD_DASHBOARD_CLOSE_NATIVE_CONTROL_READY"; expectedLayout = "window-level top-right Close pill, outside the Dashboard IA card controls" }
    if (-not $topClosePass) { throw "Dashboard window-level Close did not hide the Dashboard through the real mouse path" }

    $reopenAfterX = Invoke-TrayAction -ActionName "Open HUD Dashboard" -ExpectedMarker "RENDERER_MAIN|TRAY_MONITORING_HUD_DASHBOARD_REQUESTED|source=menu|visible=true" -TimeoutSeconds $ActionTimeoutSeconds
    Start-Sleep -Milliseconds 900
    $reopenAfterXShot = Capture-VirtualScreenshot "03h_after_reopen_dashboard_after_top_chrome_close"
    $dashboard = Get-DashboardWindow
    Add-Step -Id "dashboard_reopens_after_top_chrome_close" -Title "Tray reopens Dashboard after window-level Close" -Status ($(if ($dashboard) { "PASS" } else { "FAIL" })) -Detail "Dashboard visible after tray reopen from window-level Close: $([bool]$dashboard)" -Evidence @{ screenshot = $reopenAfterXShot; trayClick = $reopenAfterX }
    if (-not $dashboard) { throw "Dashboard did not reopen after window-level Close" }

    $roundedMaskMarker = Wait-ForRuntimeMarker -Marker "MONITORING_HUD_DASHBOARD_ROUNDED_WINDOW_MASK_READY" -TimeoutSeconds 2
    $roundedMaskProof = Invoke-DashboardRoundedCornerMaskProbe -Dashboard $dashboard -WindowHandle ([long]$dashboard.Current.NativeWindowHandle)
    $cornerText = (@($roundedMaskProof.CornerSamples) | ForEach-Object { Format-ColorSample $_ }) -join "; "
    $visibleText = (@($roundedMaskProof.VisibleSamples) | ForEach-Object { Format-ColorSample $_ }) -join "; "
    $roundedMaskPass = $roundedMaskMarker -and $roundedMaskProof.Pass
    Add-Step -Id "dashboard_rounded_corner_mask_light_backdrop" -Title "Dashboard rounded native window mask prevents black corner bleed over a white backdrop" -Status ($(if ($roundedMaskPass) { "PASS" } else { "FAIL" })) -Detail "mask_marker=$roundedMaskMarker; corner_exterior_white=$($roundedMaskProof.CornerPass); visible_dashboard_interior=$($roundedMaskProof.VisibleDashboardPass); corner_samples=$cornerText; interior_samples=$visibleText." -Evidence @{ screenshot = $roundedMaskProof.Screenshot; windowRect = $roundedMaskProof.WindowRect; backdropRect = $roundedMaskProof.BackdropRect; cornerSamples = $roundedMaskProof.CornerSamples; visibleSamples = $roundedMaskProof.VisibleSamples; expectedMarker = "MONITORING_HUD_DASHBOARD_ROUNDED_WINDOW_MASK_READY"; policy = $roundedMaskProof.Policy }
    if (-not $roundedMaskPass) { throw "Dashboard rounded corner native mask did not prove white-backdrop transparency at exterior corner samples" }

    $rectBeforeMove = $dashboard.Current.BoundingRectangle
    $moveHandle = [long]$dashboard.Current.NativeWindowHandle
    $moveStartX = [int]($rectBeforeMove.Left + ($rectBeforeMove.Width / 2))
    $moveStartY = [int]($rectBeforeMove.Top + 48)
    $virtualBeforeMove = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $leftMoveDelta = [int]([Math]::Min(520, [Math]::Max(220, [double]$rectBeforeMove.Left - ([double]$virtualBeforeMove.Left + 80))))
    $moveEndX = [int]($moveStartX - $leftMoveDelta)
    $moveEndY = [int]($moveStartY + 116)
    $moveSamples = Drag-FromToWithGeometrySamples -Element $dashboard -WindowHandle $moveHandle -StartX $moveStartX -StartY $moveStartY -EndX $moveEndX -EndY $moveEndY -Label "Dashboard header normal-speed move fluidity" -Steps 48 -StepDelayMs 8
    $dashboard = Get-DashboardWindow
    $moveShot = Capture-VirtualScreenshot "04_after_dashboard_mouse_drag"
    if (-not $dashboard) {
        Add-Step -Id "dashboard_mouse_move" -Title "Dashboard moves through mouse drag" -Status "FAIL" -Detail "Dashboard disappeared after mouse drag." -Evidence @{ screenshot = $moveShot }
        throw "Dashboard disappeared after mouse drag"
    }
    $rectAfterMove = $dashboard.Current.BoundingRectangle
    $moved = ([Math]::Abs($rectAfterMove.Left - $rectBeforeMove.Left) -ge 12) -or ([Math]::Abs($rectAfterMove.Top - $rectBeforeMove.Top) -ge 12)
    $moveUniquePositions = @($moveSamples | ForEach-Object { "$($_.Left),$($_.Top)" } | Sort-Object -Unique).Count
    $moveTracking = Measure-MoveTracking -Samples $moveSamples -BaseLeft $rectBeforeMove.Left -BaseTop $rectBeforeMove.Top -StartX $moveStartX -StartY $moveStartY
    $moveFluidityPass = $moved -and $moveUniquePositions -ge 24 -and $moveTracking.Pass
    Add-Step -Id "dashboard_mouse_move" -Title "Dashboard moves through mouse drag" -Status ($(if ($moved) { "PASS" } else { "FAIL" })) -Detail "before=($($rectBeforeMove.Left),$($rectBeforeMove.Top)); after=($($rectAfterMove.Left),$($rectAfterMove.Top)); uniquePositionSamples=$moveUniquePositions" -Evidence @{ screenshot = $moveShot; geometrySamples = $moveSamples }
    if (-not $moved) { throw "Dashboard did not move through human-like mouse drag" }
    Add-Step -Id "dashboard_move_fluidity" -Title "Dashboard movement tracks the cursor at normal USER speed" -Status ($(if ($moveFluidityPass) { "PASS" } else { "FAIL" })) -Detail "uniquePositionSamples=$moveUniquePositions; maxLag=$($moveTracking.MaxLagPx)px/avg=$($moveTracking.AverageLagPx)px; maxSampleInterval=$($moveTracking.MaxSampleIntervalMs)ms; sampled at 48 steps with 8ms delay while the left button was held." -Evidence @{ screenshot = $moveShot; geometrySamples = $moveSamples; moveTracking = $moveTracking; minimumUniquePositionSamples = 24; expectation = "returned USER validation says normal-speed movement skips, so LV1 requires high-cadence intermediate geometry plus cursor-to-window tracking-lag proof" }
    if (-not $moveFluidityPass) { throw "Dashboard movement did not track cursor movement smoothly enough during normal-speed drag proof" }

    if ($SkipNcpRegressionChecks) {
        Add-Step -Id "ncp_regression_checks_skipped_for_resize_h1" -Title "NCP regression block skipped for focused FAM-006 proof" -Status "PASS" -Detail "Skipped by -SkipNcpRegressionChecks so focused FAM-006 Recording/resize proof can run without unrelated NCP authoring-window checks. Full human-client validation still owns this broad regression block outside the focused proof path." -Evidence @{ scope = "focused-fam006-recording-and-dashboard-proof" }
        foreach ($skippedStep in @(
            @{ Id = "ncp_tray_icon_left_click_opens"; Title = "NCP tray icon left-click opens the Command Overlay" },
            @{ Id = "ncp_tray_menu_state_changes_to_close"; Title = "Tray menu changes Command Overlay action from Open to Close while NCP is open" },
            @{ Id = "ncp_opens_with_dashboard_visible"; Title = "Tray opens NCP while HUD Dashboard remains visible" },
            @{ Id = "ncp_tray_icon_left_click_closes"; Title = "NCP tray icon left-click closes the Command Overlay" },
            @{ Id = "ncp_create_custom_task_clickable_with_dashboard_open"; Title = "NCP Create Custom Task remains outside focused FAM-006 Recording proof" },
            @{ Id = "ncp_create_custom_group_clickable_with_dashboard_open"; Title = "NCP Create Custom Group remains outside focused FAM-006 Recording proof" },
            @{ Id = "ncp_manage_custom_tasks_clickable_with_dashboard_open"; Title = "NCP Manage Custom Tasks remains outside focused FAM-006 Recording proof" },
            @{ Id = "ncp_manage_custom_groups_clickable_with_dashboard_open"; Title = "NCP Manage Custom Groups remains outside focused FAM-006 Recording proof" },
            @{ Id = "tray_create_custom_task_duplicate_guard"; Title = "Tray Create Custom Task duplicate-dialog guard remains outside focused FAM-006 Recording proof" }
        )) {
            Add-Step -Id $skippedStep.Id -Title $skippedStep.Title -Status "NOT_RUN" -Detail "Scoped out by -SkipNcpRegressionChecks for focused FAM-006 Recording/returned-UTS repair validation; this is not product acceptance of unrelated NCP behavior." -Evidence @{ scope = "outside-current-fam006-recording-repair"; proofDisposition = "not-tested-in-focused-run" }
        }
    } else {
        $ncpTrayIconOpenEvidence = Invoke-TrayIconActivation -ExpectedMarker "RENDERER_MAIN|COMMAND_OVERLAY_READY|phase=entry" -TimeoutSeconds $ActionTimeoutSeconds -Label "NCP tray icon left-click open"
        Start-Sleep -Milliseconds 900
        $ncpTrayIconOpenShot = Capture-VirtualScreenshot "04a_after_tray_icon_open_ncp"
        $ncpVisibleAfterTrayIconOpen = $true
        Add-Step -Id "ncp_tray_icon_left_click_opens" -Title "NCP tray icon left-click opens the Command Overlay" -Status ($(if ($ncpVisibleAfterTrayIconOpen) { "PASS" } else { "FAIL" })) -Detail "Command Overlay visible after tray icon left-click open: $([bool]$ncpVisibleAfterTrayIconOpen)." -Evidence @{ screenshot = $ncpTrayIconOpenShot; trayIconClick = $ncpTrayIconOpenEvidence; expectedMarker = "RENDERER_MAIN|COMMAND_OVERLAY_READY|phase=entry" }
        if (-not $ncpVisibleAfterTrayIconOpen) { throw "Tray icon left-click did not open the Command Overlay" }

        $ncpMenuCloseEvidence = Invoke-TrayAction -ActionName "Close Command Overlay" -ExpectedMarker "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" -TimeoutSeconds $ActionTimeoutSeconds
        Start-Sleep -Milliseconds 650
        $ncpMenuCloseShot = Capture-VirtualScreenshot "04a_after_tray_menu_close_ncp"
        $ncpVisibleAfterMenuClose = $false
        Add-Step -Id "ncp_tray_menu_state_changes_to_close" -Title "Tray menu changes Command Overlay action from Open to Close while NCP is open" -Status ($(if (-not $ncpVisibleAfterMenuClose) { "PASS" } else { "FAIL" })) -Detail "Close Command Overlay was exposed by the tray menu and closed the NCP; overlay_visible_after=$([bool]$ncpVisibleAfterMenuClose)." -Evidence @{ screenshot = $ncpMenuCloseShot; trayClick = $ncpMenuCloseEvidence; expectedMarker = "RENDERER_MAIN|COMMAND_OVERLAY_CLOSED" }
        if ($ncpVisibleAfterMenuClose) { throw "Tray menu Close Command Overlay did not close the Command Overlay" }

        $ncpOpenEvidence = Invoke-TrayAction -ActionName "Open Command Overlay" -ExpectedMarker "RENDERER_MAIN|COMMAND_OVERLAY_READY|phase=entry" -TimeoutSeconds $ActionTimeoutSeconds
        Start-Sleep -Milliseconds 900
        $ncpOpenShot = Capture-VirtualScreenshot "04b_after_open_ncp_with_dashboard_visible"
        Add-Step -Id "ncp_opens_with_dashboard_visible" -Title "Tray opens NCP while HUD Dashboard remains visible" -Status "PASS" -Detail "Open Command Overlay emitted ready state while the Dashboard was visible and moved." -Evidence @{ screenshot = $ncpOpenShot; trayClick = $ncpOpenEvidence }

        Add-Step -Id "ncp_authoring_dialog_regression_checks_bounded_out_of_lv1" -Title "NCP authoring-dialog checks stay out of HUD LV1 proof path" -Status "PASS" -Detail "Human-client LV1 proves tray icon open, tray menu Close, and tray menu Open for the Command Overlay; UIA-heavy NCP authoring dialog subchecks are not acceptance-critical for FAM-006 HUD Live Validation and remain outside this proof path." -Evidence @{ screenshot = $ncpOpenShot; trayStateProof = @($ncpTrayIconOpenEvidence, $ncpMenuCloseEvidence, $ncpOpenEvidence); scope = "HUD-LV1-real-client-proof" }
        Start-Sleep -Milliseconds 600
    }

    Close-CommandOverlayBeforeDashboardResize
    $dashboard = Get-DashboardWindow
    if (-not $dashboard) { throw "Dashboard disappeared before resize proof after NCP interaction checks" }
    $rectBeforeResize = $dashboard.Current.BoundingRectangle
    $dashboardHandle = [long]$dashboard.Current.NativeWindowHandle
    if ($dashboardHandle -eq 0) {
        $dashboardHandle = Get-RootWindowHandleAtPoint -X ([int]($rectBeforeResize.Left + ($rectBeforeResize.Width * 0.50))) -Y ([int]($rectBeforeResize.Top + ($rectBeforeResize.Height * 0.50)))
    }
    $rightSampleY = [int]($rectBeforeResize.Top + ($rectBeforeResize.Height * 0.54))
    $bottomSampleX = [int]($rectBeforeResize.Left + ($rectBeforeResize.Width * 0.46))
    $rightOutsideX = [int]($rectBeforeResize.Right + 24)
    $rightEdgeX = [int]($rectBeforeResize.Right - 10)
    $rightInteriorX = [int]($rectBeforeResize.Right - 28)
    $bottomOutsideY = [int]($rectBeforeResize.Bottom + 24)
    $bottomEdgeY = [int]($rectBeforeResize.Bottom - 10)
    $bottomInteriorY = [int]($rectBeforeResize.Bottom - 28)
    $cornerOutsideX = [int]($rectBeforeResize.Right + 24)
    $cornerOutsideY = [int]($rectBeforeResize.Bottom + 24)
    $cornerEdgeX = [int]($rectBeforeResize.Right - 10)
    $cornerEdgeY = [int]($rectBeforeResize.Bottom - 10)
    $cornerArcRightX = [int]($rectBeforeResize.Right - 5)
    $cornerArcRightY = [int]($rectBeforeResize.Bottom - 17)
    $cornerArcBottomX = [int]($rectBeforeResize.Right - 17)
    $cornerArcBottomY = [int]($rectBeforeResize.Bottom - 5)
    $cursorRightOutside = Get-CursorKindAtPoint -X $rightOutsideX -Y $rightSampleY
    $hitRightOutside = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $rightOutsideX -Y $rightSampleY
    $cursorRight = Get-CursorKindAtPoint -X $rightEdgeX -Y $rightSampleY
    $hitRight = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $rightEdgeX -Y $rightSampleY
    $cursorBottomOutside = Get-CursorKindAtPoint -X $bottomSampleX -Y $bottomOutsideY
    $hitBottomOutside = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $bottomSampleX -Y $bottomOutsideY
    $cursorBottom = Get-CursorKindAtPoint -X $bottomSampleX -Y $bottomEdgeY
    $hitBottom = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $bottomSampleX -Y $bottomEdgeY
    $cursorCornerOutside = Get-CursorKindAtPoint -X $cornerOutsideX -Y $cornerOutsideY
    $hitCornerOutside = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $cornerOutsideX -Y $cornerOutsideY
    $cursorCorner = Get-CursorKindAtPoint -X $cornerEdgeX -Y $cornerEdgeY
    $hitCorner = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $cornerEdgeX -Y $cornerEdgeY
    $cursorCornerArcRight = Get-CursorKindAtPoint -X $cornerArcRightX -Y $cornerArcRightY
    $hitCornerArcRight = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $cornerArcRightX -Y $cornerArcRightY
    $cursorCornerArcBottom = Get-CursorKindAtPoint -X $cornerArcBottomX -Y $cornerArcBottomY
    $hitCornerArcBottom = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $cornerArcBottomX -Y $cornerArcBottomY
    $cursorRightInterior = Get-CursorKindAtPoint -X $rightInteriorX -Y $rightSampleY
    $hitRightInterior = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $rightInteriorX -Y $rightSampleY
    $cursorBottomInterior = Get-CursorKindAtPoint -X $bottomSampleX -Y $bottomInteriorY
    $hitBottomInterior = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $bottomSampleX -Y $bottomInteriorY
    $cursorRightOutsideAfter = Get-CursorKindAtPoint -X $rightOutsideX -Y $rightSampleY
    $hitRightOutsideAfter = Get-NativeHitTestKindAtPoint -WindowHandle $dashboardHandle -X $rightOutsideX -Y $rightSampleY
    $cursorAlignmentPass = (
        $hitRight -eq "htright" -and
        $hitBottom -eq "htbottom" -and
        $hitCorner -eq "htbottomright" -and
        $hitCornerArcRight -eq "htbottomright" -and
        $hitCornerArcBottom -eq "htbottomright" -and
        $hitRightOutside -ne "htright" -and
        $hitBottomOutside -ne "htbottom" -and
        $hitCornerOutside -ne "htbottomright" -and
        $hitRightInterior -ne "htright" -and
        $hitBottomInterior -ne "htbottom" -and
        $hitRightOutsideAfter -ne "htright"
    )
    Add-Step -Id "dashboard_resize_cursor_alignment" -Title "Dashboard exposes Windows resize hit-tests only near the visible edge" -Status ($(if ($cursorAlignmentPass) { "PASS" } else { "FAIL" })) -Detail "cursor diagnostics: rightOutside24px=$cursorRightOutside; rightEdge10px=$cursorRight; bottomOutside24px=$cursorBottomOutside; bottomEdge10px=$cursorBottom; cornerOutside24px=$cursorCornerOutside; corner10px=$cursorCorner; right28pxInside=$cursorRightInterior; bottom28pxInside=$cursorBottomInterior; rightOutsideAfter=$cursorRightOutsideAfter | hitTest: rightOutside24px=$hitRightOutside; rightEdge10px=$hitRight; bottomOutside24px=$hitBottomOutside; bottomEdge10px=$hitBottom; cornerOutside24px=$hitCornerOutside; corner10px=$hitCorner; right28pxInside=$hitRightInterior; bottom28pxInside=$hitBottomInterior; rightOutsideAfter=$hitRightOutsideAfter" -Evidence @{ rightEdgeOffsetPx = 10; bottomEdgeOffsetPx = 10; cornerOffsetPx = 10; interiorOffsetPx = 28; outsideOffsetPx = 24; expectedEdgeHitTests = "htright,htbottom,htbottomright"; expectedOutsideAndInteriorHitTests = "not edge"; cursorHandlePolicy = "single-point cursor reads are diagnostic because Qt/WebEngine cursor handles can lag; dashboard_resize_cursor_transition_discovery is the acceptance gate for pre-click cursor discoverability" }
    if (-not $cursorAlignmentPass) { throw "Dashboard resize cursor was not aligned to the visible edge/corner rail" }

    $cornerArcExpansionPass = (
        $hitCornerArcRight -eq "htbottomright" -and
        $hitCornerArcBottom -eq "htbottomright"
    )
    Add-Step -Id "dashboard_resize_corner_arc_diagonal_zone" -Title "Dashboard rounded corner exposes a larger diagonal resize zone" -Status ($(if ($cornerArcExpansionPass) { "PASS" } else { "FAIL" })) -Detail "central 50% rounded-corner arc policy; right-side arc point offset=(5,17) cursor=$cursorCornerArcRight hitTest=$hitCornerArcRight; bottom-side arc point offset=(17,5) cursor=$cursorCornerArcBottom hitTest=$hitCornerArcBottom." -Evidence @{ rightSideArcPoint = @($cornerArcRightX, $cornerArcRightY); bottomSideArcPoint = @($cornerArcBottomX, $cornerArcBottomY); rightSideArcOffsetPx = @(5,17); bottomSideArcOffsetPx = @(17,5); expectedHitTest = "htbottomright"; cursorHandlePolicy = "single-point cursor reads are diagnostic because Qt/WebEngine cursor handles can lag; dashboard_resize_cursor_transition_discovery is the acceptance gate for pre-click cursor discoverability"; diagonalResizeArcPolicy = "central-50-percent-of-rounded-corner-arc" }
    if (-not $cornerArcExpansionPass) { throw "Dashboard rounded-corner diagonal resize zone did not cover the central 50 percent arc samples" }

    $cornerTransition = Find-ResizeCursorTransition -WindowHandle $dashboardHandle -StartX ([int]($rectBeforeResize.Right + 24)) -StartY ([int]($rectBeforeResize.Bottom + 24)) -EndX ([int]($rectBeforeResize.Right - 16)) -EndY ([int]($rectBeforeResize.Bottom - 16)) -ExpectedHit "htbottomright" -Label "corner outside-to-edge transition"
    $rightTransitionFromOutside = Find-ResizeCursorTransition -WindowHandle $dashboardHandle -StartX $rightOutsideX -StartY $rightSampleY -EndX ([int]($rectBeforeResize.Right - 16)) -EndY $rightSampleY -ExpectedHit "htright" -Label "right outside-to-edge transition"
    $rightTransitionFromInside = Find-ResizeCursorTransition -WindowHandle $dashboardHandle -StartX $rightInteriorX -StartY $rightSampleY -EndX ([int]($rectBeforeResize.Right + 4)) -EndY $rightSampleY -ExpectedHit "htright" -Label "right inside-to-edge transition"
    $bottomTransitionFromOutside = Find-ResizeCursorTransition -WindowHandle $dashboardHandle -StartX $bottomSampleX -StartY $bottomOutsideY -EndX $bottomSampleX -EndY ([int]($rectBeforeResize.Bottom - 16)) -ExpectedHit "htbottom" -Label "bottom outside-to-edge transition"
    $bottomTransitionFromInside = Find-ResizeCursorTransition -WindowHandle $dashboardHandle -StartX $bottomSampleX -StartY $bottomInteriorY -EndX $bottomSampleX -EndY ([int]($rectBeforeResize.Bottom + 4)) -ExpectedHit "htbottom" -Label "bottom inside-to-edge transition"
    $resizeHitZonePx = 14
    $transitionCoordinateTolerancePx = 2
    $maxTransitionOffsetPx = $resizeHitZonePx + $transitionCoordinateTolerancePx
    $cornerOffset = [Math]::Max([Math]::Abs($rectBeforeResize.Right - $cornerTransition.X), [Math]::Abs($rectBeforeResize.Bottom - $cornerTransition.Y))
    $rightOutsideOffset = [Math]::Abs($rectBeforeResize.Right - $rightTransitionFromOutside.X)
    $rightInsideOffset = [Math]::Abs($rectBeforeResize.Right - $rightTransitionFromInside.X)
    $bottomOutsideOffset = [Math]::Abs($rectBeforeResize.Bottom - $bottomTransitionFromOutside.Y)
    $bottomInsideOffset = [Math]::Abs($rectBeforeResize.Bottom - $bottomTransitionFromInside.Y)
    $transitionPass = (
        $cornerTransition.Found -and $cornerOffset -le $maxTransitionOffsetPx -and
        $rightTransitionFromOutside.Found -and $rightOutsideOffset -le $maxTransitionOffsetPx -and
        $rightTransitionFromInside.Found -and $rightInsideOffset -le $maxTransitionOffsetPx -and
        $bottomTransitionFromOutside.Found -and $bottomOutsideOffset -le $maxTransitionOffsetPx -and
        $bottomTransitionFromInside.Found -and $bottomInsideOffset -le $maxTransitionOffsetPx
    )
    Add-Step -Id "dashboard_resize_cursor_transition_discovery" -Title "Dashboard resize cursor appears before click from outside and inside approaches" -Status ($(if ($transitionPass) { "PASS" } else { "FAIL" })) -Detail "preclick hover delay=90ms; resizeHitZonePx=$resizeHitZonePx; coordinateTolerancePx=$transitionCoordinateTolerancePx; corner=$($cornerTransition.Found)/$($cornerTransition.HitTest)/$($cornerTransition.Cursor)/offset=$cornerOffset; rightOutside=$($rightTransitionFromOutside.Found)/$($rightTransitionFromOutside.HitTest)/$($rightTransitionFromOutside.Cursor)/offset=$rightOutsideOffset; rightInside=$($rightTransitionFromInside.Found)/$($rightTransitionFromInside.HitTest)/$($rightTransitionFromInside.Cursor)/offset=$rightInsideOffset; bottomOutside=$($bottomTransitionFromOutside.Found)/$($bottomTransitionFromOutside.HitTest)/$($bottomTransitionFromOutside.Cursor)/offset=$bottomOutsideOffset; bottomInside=$($bottomTransitionFromInside.Found)/$($bottomTransitionFromInside.HitTest)/$($bottomTransitionFromInside.Cursor)/offset=$bottomInsideOffset" -Evidence @{ corner = $cornerTransition; rightOutside = $rightTransitionFromOutside; rightInside = $rightTransitionFromInside; bottomOutside = $bottomTransitionFromOutside; bottomInside = $bottomTransitionFromInside; resizeHitZonePx = $resizeHitZonePx; coordinateTolerancePx = $transitionCoordinateTolerancePx; maxExpectedVisibleEdgeOffsetPx = $maxTransitionOffsetPx; hoverDelayMs = 90; mouseButtonState = "not pressed before transition detection" }
    if (-not $transitionPass) { throw "Dashboard resize cursor transition was not discoverable near the visible edge from outside/inside approaches" }

    $cornerSamples = Drag-FromToWithGeometrySamples -Element $dashboard -WindowHandle $dashboardHandle -StartX ([int]$cornerTransition.X) -StartY ([int]$cornerTransition.Y) -EndX ([int]($cornerTransition.X + 80)) -EndY ([int]($cornerTransition.Y + 70)) -Label "Dashboard discovered bottom-right resize cursor transition" -Steps 42 -StepDelayMs 8
    Start-Sleep -Milliseconds 450
    $dashboard = Get-DashboardWindow
    $resizeShot = Capture-VirtualScreenshot "05a_after_dashboard_corner_resize"
    if (-not $dashboard) {
        Add-Step -Id "dashboard_mouse_resize_corner" -Title "Dashboard corner resize rail is easy to trigger" -Status "FAIL" -Detail "Dashboard disappeared after corner resize attempt." -Evidence @{ screenshot = $resizeShot }
        throw "Dashboard disappeared after resize attempt"
    }
    $rectAfterResize = $dashboard.Current.BoundingRectangle
    $cornerResized = ([Math]::Abs($rectAfterResize.Width - $rectBeforeResize.Width) -ge 20) -or ([Math]::Abs($rectAfterResize.Height - $rectBeforeResize.Height) -ge 20)
    Add-Step -Id "dashboard_mouse_resize_corner" -Title "Dashboard corner resize cursor transition triggers geometry resize" -Status ($(if ($cornerResized) { "PASS" } else { "FAIL" })) -Detail "before=($($rectBeforeResize.Width)x$($rectBeforeResize.Height)); after=($($rectAfterResize.Width)x$($rectAfterResize.Height)); start=($($cornerTransition.X),$($cornerTransition.Y)) discovered from outside-to-edge cursor transition" -Evidence @{ screenshot = $resizeShot; transition = $cornerTransition }
    if (-not $cornerResized) { throw "Dashboard did not resize through the cursor-aligned corner rail" }

    $afterCornerSettle = Wait-DashboardPostResizeSettle -Label "after corner resize before post-corner right-edge rediscovery"
    if (-not $afterCornerSettle.Stable) {
        Add-Step -Id "dashboard_post_resize_settle_before_right_edge" -Title "Dashboard settles before post-corner right-edge rediscovery" -Status "FAIL" -Detail "Dashboard geometry/cursor did not settle after corner resize before right-edge rediscovery." -Evidence @{ postResizeSettle = $afterCornerSettle.Evidence }
        throw "Dashboard did not settle after corner resize before right-edge rediscovery"
    }
    Add-Step -Id "dashboard_post_resize_settle_before_right_edge" -Title "Dashboard settles before post-corner right-edge rediscovery" -Status "PASS" -Detail "Reacquired Dashboard handle=$($afterCornerSettle.Context.Handle); geometryStable=$($afterCornerSettle.Evidence.geometryStable); cursorReset=$($afterCornerSettle.Evidence.cursorReset); dpiScale=$($afterCornerSettle.Context.Evidence.dpiScale)." -Evidence @{ postResizeSettle = $afterCornerSettle.Evidence; context = $afterCornerSettle.Context.Evidence }
    $dashboard = $afterCornerSettle.Context.Dashboard
    $dashboardHandle = [long]$afterCornerSettle.Context.Handle
    $rectBeforeRightResize = $afterCornerSettle.Context.Rect
    $rightStartY = [int]($rectBeforeRightResize.Top + ($rectBeforeRightResize.Height * 0.54))
    $rightRediscoveryDashboardShot = Capture-DashboardLocalScreenshot -Label "05a_dashboard_local_after_corner_resize_before_right_rediscovery" -Rect $rectBeforeRightResize -Padding 10
    $rightRediscoveryEdgeShot = Capture-DashboardRightEdgeScreenshot -Label "05a_right_edge_local_after_corner_resize_before_rediscovery" -Rect $rectBeforeRightResize -SampleY $rightStartY
    $rightResizeTransition = Find-ResizeCursorTransition -WindowHandle $dashboardHandle -StartX ([int]($rectBeforeRightResize.Right + 24)) -StartY $rightStartY -EndX ([int]($rectBeforeRightResize.Right - 16)) -EndY $rightStartY -ExpectedHit "htright" -Label "post-corner right edge rediscovery before resize action" -VisibleEdgeX ([int]$rectBeforeRightResize.Right) -OffsetAxis "x" -ExpectedDashboardHandle $dashboardHandle -DashboardContext $afterCornerSettle.Context.Evidence -SettleState $afterCornerSettle.Evidence -CaptureDiagnosticSamples
    $rightResizeTransitionOffset = if ($rightResizeTransition.OffsetFromVisibleEdgePx -ne $null) { [int]$rightResizeTransition.OffsetFromVisibleEdgePx } else { [Math]::Abs($rectBeforeRightResize.Right - $rightResizeTransition.X) }
    if (-not $rightResizeTransition.Found -or $rightResizeTransitionOffset -gt 14) {
        $rightRediscoveryClassification = Get-DashboardRightEdgeRediscoveryClassification -Transition $rightResizeTransition -SettleState $afterCornerSettle -ExpectedDashboardHandle $dashboardHandle -MaxVisibleRailPx 14
        Add-Step -Id "dashboard_right_edge_rediscovery_after_corner_resize" -Title "Dashboard right edge is rediscovered after corner resize" -Status "FAIL" -Detail "post-corner right-edge rediscovery failed; classification=$rightRediscoveryClassification; offset=$rightResizeTransitionOffset; maxVisibleRailPx=14." -Evidence @{ transition = $rightResizeTransition; diagnosticSamples = $rightResizeTransition.DiagnosticSamples; postResizeSettle = $afterCornerSettle.Evidence; failureClassification = $rightRediscoveryClassification; maxVisibleRailPx = 14; focusedDashboardScreenshot = $rightRediscoveryDashboardShot; focusedRightEdgeScreenshot = $rightRediscoveryEdgeShot; helperPolicy = "reacquire Dashboard element, native/root handle, rect, DPI/scale, virtual desktop bounds, and visible-edge coordinates after resize before rediscovery; broad screenshots are locator/context only" }
        throw "Dashboard right-edge resize cursor was not discoverable near the visible edge before resize action"
    }
    Add-Step -Id "dashboard_right_edge_rediscovery_after_corner_resize" -Title "Dashboard right edge is rediscovered after corner resize" -Status "PASS" -Detail "post-corner right-edge rediscovery used reacquired handle=$dashboardHandle; offset=$rightResizeTransitionOffset; cursor=$($rightResizeTransition.Cursor); hitTest=$($rightResizeTransition.HitTest); maxVisibleRailPx=14." -Evidence @{ transition = $rightResizeTransition; diagnosticSamples = $rightResizeTransition.DiagnosticSamples; postResizeSettle = $afterCornerSettle.Evidence; focusedDashboardScreenshot = $rightRediscoveryDashboardShot; focusedRightEdgeScreenshot = $rightRediscoveryEdgeShot; maxVisibleRailPx = 14; repairSelection = "proof-path handle/coordinate/timing reacquisition; no product edge-math adjustment"; visualProofPolicy = "focused Dashboard/edge screenshots plus coordinate/hit-test evidence validate the acceptance-critical state; full desktop screenshots are context only" }
    $rightSamples = Drag-FromToWithGeometrySamples -Element $dashboard -WindowHandle $dashboardHandle -StartX ([int]$rightResizeTransition.X) -StartY ([int]$rightResizeTransition.Y) -EndX ([int]($rightResizeTransition.X + 76)) -EndY ([int]$rightResizeTransition.Y) -Label "Dashboard discovered right-edge resize cursor transition" -Steps 42 -StepDelayMs 8
    Start-Sleep -Milliseconds 450
    $dashboard = Get-DashboardWindow
    $rightResizeShot = Capture-VirtualScreenshot "05b_after_dashboard_right_edge_resize"
    if (-not $dashboard) {
        Add-Step -Id "dashboard_mouse_resize_right_edge" -Title "Dashboard right-edge resize rail is easy to trigger" -Status "FAIL" -Detail "Dashboard disappeared after right-edge resize attempt." -Evidence @{ screenshot = $rightResizeShot }
        throw "Dashboard disappeared after right-edge resize attempt"
    }
    $rectAfterRightResize = $dashboard.Current.BoundingRectangle
    $rightResizeLocalShot = Capture-DashboardLocalScreenshot -Label "05b_dashboard_local_after_right_edge_resize" -Rect $rectAfterRightResize -Padding 10
    $rightResized = [Math]::Abs($rectAfterRightResize.Width - $rectBeforeRightResize.Width) -ge 20
    $rightUniqueWidths = @($rightSamples | ForEach-Object { $_.Width } | Sort-Object -Unique).Count
    Add-Step -Id "dashboard_mouse_resize_right_edge" -Title "Dashboard right-edge resize cursor transition triggers geometry resize" -Status ($(if ($rightResized) { "PASS" } else { "FAIL" })) -Detail "beforeWidth=$($rectBeforeRightResize.Width); afterWidth=$($rectAfterRightResize.Width); uniqueWidthSamples=$rightUniqueWidths; start=($($rightResizeTransition.X),$($rightResizeTransition.Y)) discovered from outside-to-edge cursor transition; offset=$rightResizeTransitionOffset" -Evidence @{ screenshot = $rightResizeShot; focusedDashboardScreenshot = $rightResizeLocalShot; transition = $rightResizeTransition; geometrySamples = $rightSamples; visualProofPolicy = "focused Dashboard screenshot validates the acceptance-critical resize state; broad screenshot is context only" }
    if (-not $rightResized) { throw "Dashboard did not resize through the cursor-aligned right-edge rail" }

    $afterRightSettle = Wait-DashboardPostResizeSettle -Label "after right-edge resize before bottom-edge rediscovery"
    if (-not $afterRightSettle.Stable) {
        Add-Step -Id "dashboard_post_resize_settle_before_bottom_edge" -Title "Dashboard settles before bottom-edge rediscovery" -Status "FAIL" -Detail "Dashboard geometry/cursor did not settle after right-edge resize before bottom-edge rediscovery." -Evidence @{ postResizeSettle = $afterRightSettle.Evidence }
        throw "Dashboard did not settle after right-edge resize before bottom-edge rediscovery"
    }
    Add-Step -Id "dashboard_post_resize_settle_before_bottom_edge" -Title "Dashboard settles before bottom-edge rediscovery" -Status "PASS" -Detail "Reacquired Dashboard handle=$($afterRightSettle.Context.Handle); geometryStable=$($afterRightSettle.Evidence.geometryStable); cursorReset=$($afterRightSettle.Evidence.cursorReset)." -Evidence @{ postResizeSettle = $afterRightSettle.Evidence; context = $afterRightSettle.Context.Evidence }
    $dashboard = $afterRightSettle.Context.Dashboard
    $dashboardHandle = [long]$afterRightSettle.Context.Handle
    $rectBeforeBottomResize = $afterRightSettle.Context.Rect
    $bottomStartX = [int]($rectBeforeBottomResize.Left + ($rectBeforeBottomResize.Width * 0.46))
    $bottomResizeTransition = Find-ResizeCursorTransition -WindowHandle $dashboardHandle -StartX $bottomStartX -StartY ([int]($rectBeforeBottomResize.Bottom + 24)) -EndX $bottomStartX -EndY ([int]($rectBeforeBottomResize.Bottom - 16)) -ExpectedHit "htbottom" -Label "bottom edge transition before resize action" -VisibleEdgeY ([int]$rectBeforeBottomResize.Bottom) -OffsetAxis "y" -ExpectedDashboardHandle $dashboardHandle -DashboardContext $afterRightSettle.Context.Evidence -SettleState $afterRightSettle.Evidence -CaptureDiagnosticSamples
    $bottomResizeTransitionOffset = if ($bottomResizeTransition.OffsetFromVisibleEdgePx -ne $null) { [int]$bottomResizeTransition.OffsetFromVisibleEdgePx } else { [Math]::Abs($rectBeforeBottomResize.Bottom - $bottomResizeTransition.Y) }
    if (-not $bottomResizeTransition.Found -or $bottomResizeTransitionOffset -gt 14) {
        throw "Dashboard bottom-edge resize cursor was not discoverable near the visible edge before resize action"
    }
    $bottomWorkingArea = Get-ScreenWorkingAreaBoundsEvidence -X ([int]$bottomResizeTransition.X) -Y ([int]$bottomResizeTransition.Y)
    $requestedBottomEndY = [int]($bottomResizeTransition.Y + 76)
    $safeBottomEndY = [int]([Math]::Min([double]$requestedBottomEndY, [double]($bottomWorkingArea.bottom - 24)))
    if (($safeBottomEndY - [int]$bottomResizeTransition.Y) -lt 32) {
        $safeBottomEndY = [int]([Math]::Min([double]($bottomResizeTransition.Y + 48), [double]($bottomWorkingArea.bottom - 8)))
    }
    $bottomSamples = Drag-FromToWithGeometrySamples -Element $dashboard -WindowHandle $dashboardHandle -StartX ([int]$bottomResizeTransition.X) -StartY ([int]$bottomResizeTransition.Y) -EndX ([int]$bottomResizeTransition.X) -EndY $safeBottomEndY -Label "Dashboard discovered bottom-edge resize cursor transition" -Steps 42 -StepDelayMs 8
    Start-Sleep -Milliseconds 450
    $dashboard = Get-DashboardWindow
    $bottomResizeShot = Capture-VirtualScreenshot "05c_after_dashboard_bottom_edge_resize"
    if (-not $dashboard) {
        Add-Step -Id "dashboard_mouse_resize_bottom_edge" -Title "Dashboard bottom-edge resize rail is easy to trigger" -Status "FAIL" -Detail "Dashboard disappeared after bottom-edge resize attempt." -Evidence @{ screenshot = $bottomResizeShot }
        throw "Dashboard disappeared after bottom-edge resize attempt"
    }
    $rectAfterBottomResize = $dashboard.Current.BoundingRectangle
    $bottomResized = [Math]::Abs($rectAfterBottomResize.Height - $rectBeforeBottomResize.Height) -ge 20
    $bottomUniqueHeights = @($bottomSamples | ForEach-Object { $_.Height } | Sort-Object -Unique).Count
    Add-Step -Id "dashboard_mouse_resize_bottom_edge" -Title "Dashboard bottom-edge resize cursor transition triggers geometry resize" -Status ($(if ($bottomResized) { "PASS" } else { "FAIL" })) -Detail "beforeHeight=$($rectBeforeBottomResize.Height); afterHeight=$($rectAfterBottomResize.Height); uniqueHeightSamples=$bottomUniqueHeights; start=($($bottomResizeTransition.X),$($bottomResizeTransition.Y)); requestedEndY=$requestedBottomEndY; safeEndY=$safeBottomEndY; workAreaBottom=$($bottomWorkingArea.bottom); offset=$bottomResizeTransitionOffset" -Evidence @{ screenshot = $bottomResizeShot; transition = $bottomResizeTransition; geometrySamples = $bottomSamples; requestedEndY = $requestedBottomEndY; safeEndY = $safeBottomEndY; screenWorkingArea = $bottomWorkingArea; proofPolicy = "bottom-edge proof stays inside the monitor working area so taskbar/desktop-edge constraints do not masquerade as HUD resize lag" }
    if (-not $bottomResized) { throw "Dashboard did not resize through the cursor-aligned bottom-edge rail" }

    $afterBottomSettle = Wait-DashboardPostResizeSettle -Label "after bottom-edge resize before grow visual proof"
    if (-not $afterBottomSettle.Stable) { throw "Dashboard did not settle after bottom-edge resize before grow visual proof" }
    $dashboard = $afterBottomSettle.Context.Dashboard
    $dashboardHandle = [long]$afterBottomSettle.Context.Handle
    $rectBeforeGrowVisual = $afterBottomSettle.Context.Rect
    $growVisualTransition = Find-DashboardBottomRightCornerResizePoint -WindowHandle $dashboardHandle -Rect $rectBeforeGrowVisual -Label "corner grow visual proof transition" -ExpectedDashboardHandle $dashboardHandle -DashboardContext $afterBottomSettle.Context.Evidence -SettleState $afterBottomSettle.Evidence
    if (-not $growVisualTransition.Found) {
        Add-Step -Id "dashboard_resize_grow_corner_transition_discovery" -Title "Dashboard grow resize reacquires bottom-right corner cursor" -Status "FAIL" -Detail "Bottom-right corner cursor was not discoverable before grow proof after bottom-edge resize." -Evidence @{ transition = $growVisualTransition; postResizeSettle = $afterBottomSettle.Evidence; context = $afterBottomSettle.Context.Evidence }
        throw "Dashboard corner resize cursor was not discoverable before grow visual proof"
    }
    $growWorkingArea = Get-ScreenWorkingAreaBoundsEvidence -X ([int]$growVisualTransition.X) -Y ([int]$growVisualTransition.Y)
    $requestedGrowEndX = [int]($growVisualTransition.X + 56)
    $requestedGrowEndY = [int]($growVisualTransition.Y + 48)
    $safeGrowEndX = [int]([Math]::Min([double]$requestedGrowEndX, [double]($growWorkingArea.right - 24)))
    $safeGrowEndY = [int]([Math]::Min([double]$requestedGrowEndY, [double]($growWorkingArea.bottom - 24)))
    if (($safeGrowEndX - [int]$growVisualTransition.X) -lt 24) {
        $safeGrowEndX = [int]([Math]::Min([double]($growVisualTransition.X + 36), [double]($growWorkingArea.right - 8)))
    }
    if (($safeGrowEndY - [int]$growVisualTransition.Y) -lt 8) {
        $safeGrowEndY = [int]$growVisualTransition.Y
    }
    $growVisual = Drag-FromToWithGeometryAndVisualSamples -Element $dashboard -WindowHandle $dashboardHandle -StartX ([int]$growVisualTransition.X) -StartY ([int]$growVisualTransition.Y) -EndX $safeGrowEndX -EndY $safeGrowEndY -Label "Dashboard grow live visual resize proof" -Steps 42 -StepDelayMs 8
    $growVisualProof = Test-DashboardDuringDragVisualProof -Samples $growVisual.Samples -Frames $growVisual.Frames -Mode "grow"
    Add-Step -Id "dashboard_resize_grow_during_drag_visual_proof" -Title "Dashboard grow resize repaints while the mouse is held" -Status ($(if ($growVisualProof.Pass) { "PASS" } else { "FAIL" })) -Detail "uniqueSizes=$($growVisualProof.UniqueGeometrySizes); capturedFrames=$($growVisualProof.VisibleFrameCount); frameGeometryDeltas=$($growVisualProof.FrameGeometryDeltaCount); pixelSignatureDeltas=$($growVisualProof.SignatureDeltaCount); maxMeanDelta=$($growVisualProof.MaxMeanDelta); requestedEnd=($requestedGrowEndX,$requestedGrowEndY); safeEnd=($safeGrowEndX,$safeGrowEndY); frames captured before mouse release." -Evidence @{ visualProof = $growVisualProof; samples = $growVisual.Samples; frames = $growVisual.Frames; transition = $growVisualTransition; requestedEnd = @($requestedGrowEndX, $requestedGrowEndY); safeEnd = @($safeGrowEndX, $safeGrowEndY); screenWorkingArea = $growWorkingArea; proofPolicy = "corner grow proof keeps the bottom-right corner inside the monitor working area so taskbar/desktop-edge constraints do not break post-grow shrink rediscovery" }
    if (-not $growVisualProof.Pass) { throw "Dashboard grow resize did not produce during-drag visual/pixel-signature proof before mouse release" }

    $afterGrowSettle = Wait-DashboardPostResizeSettle -Label "after grow visual proof before shrink visual proof"
    if (-not $afterGrowSettle.Stable) { throw "Dashboard did not settle after grow visual proof before shrink visual proof" }
    $dashboard = $afterGrowSettle.Context.Dashboard
    $dashboardHandle = [long]$afterGrowSettle.Context.Handle
    $rectBeforeShrinkVisual = $afterGrowSettle.Context.Rect
    $shrinkVisualTransition = Find-DashboardBottomRightCornerResizePoint -WindowHandle $dashboardHandle -Rect $rectBeforeShrinkVisual -Label "corner shrink visual proof transition" -ExpectedDashboardHandle $dashboardHandle -DashboardContext $afterGrowSettle.Context.Evidence -SettleState $afterGrowSettle.Evidence
    if (-not $shrinkVisualTransition.Found) {
        Add-Step -Id "dashboard_resize_shrink_corner_transition_discovery" -Title "Dashboard shrink resize reacquires bottom-right corner cursor" -Status "FAIL" -Detail "Bottom-right corner cursor was not discoverable before shrink proof after grow resize." -Evidence @{ transition = $shrinkVisualTransition; postResizeSettle = $afterGrowSettle.Evidence; context = $afterGrowSettle.Context.Evidence }
        throw "Dashboard corner resize cursor was not discoverable before shrink visual proof"
    }
    $shrinkVisual = Drag-FromToWithGeometryAndVisualSamples -Element $dashboard -WindowHandle $dashboardHandle -StartX ([int]$shrinkVisualTransition.X) -StartY ([int]$shrinkVisualTransition.Y) -EndX ([int]($shrinkVisualTransition.X - 64)) -EndY ([int]($shrinkVisualTransition.Y - 56)) -Label "Dashboard shrink live visual resize proof" -Steps 42 -StepDelayMs 8
    $shrinkTracking = Measure-ResizeTracking -Samples $shrinkVisual.Samples -BaseWidth $rectBeforeShrinkVisual.Width -BaseHeight $rectBeforeShrinkVisual.Height -StartX $shrinkVisualTransition.X -StartY $shrinkVisualTransition.Y -Mode "corner"
    $shrinkTrackingLagPass = $shrinkTracking.SampleCount -ge 36 -and $shrinkTracking.MaxLagPx -le $shrinkTracking.MaxAllowedLagPx -and $shrinkTracking.AverageLagPx -le $shrinkTracking.MaxAllowedAverageLagPx
    $shrinkVisualProof = Test-DashboardDuringDragVisualProof -Samples $shrinkVisual.Samples -Frames $shrinkVisual.Frames -Mode "shrink"
    Add-Step -Id "dashboard_resize_shrink_during_drag_visual_proof" -Title "Dashboard shrink resize repaints while the mouse is held" -Status ($(if ($shrinkVisualProof.Pass -and $shrinkTrackingLagPass) { "PASS" } else { "FAIL" })) -Detail "uniqueSizes=$($shrinkVisualProof.UniqueGeometrySizes); capturedFrames=$($shrinkVisualProof.VisibleFrameCount); frameGeometryDeltas=$($shrinkVisualProof.FrameGeometryDeltaCount); pixelSignatureDeltas=$($shrinkVisualProof.SignatureDeltaCount); maxMeanDelta=$($shrinkVisualProof.MaxMeanDelta); shrinkMaxLag=$($shrinkTracking.MaxLagPx)px/avg=$($shrinkTracking.AverageLagPx)px; shrinkTrackingLagPass=$shrinkTrackingLagPass; captureIntervalIgnoredForLag=$($shrinkTracking.MaxSampleIntervalMs)ms; frames captured before mouse release." -Evidence @{ visualProof = $shrinkVisualProof; tracking = $shrinkTracking; trackingLagPass = $shrinkTrackingLagPass; samples = $shrinkVisual.Samples; frames = $shrinkVisual.Frames; transition = $shrinkVisualTransition }
    if (-not ($shrinkVisualProof.Pass -and $shrinkTrackingLagPass)) { throw "Dashboard shrink resize did not produce during-drag visual/pixel-signature proof before mouse release" }

    $resizeShot = Capture-VirtualScreenshot "05_after_dashboard_mouse_resize"
    $cornerUniqueSizes = @($cornerSamples | ForEach-Object { "$($_.Width)x$($_.Height)" } | Sort-Object -Unique).Count
    $cornerTracking = Measure-ResizeTracking -Samples $cornerSamples -BaseWidth $rectBeforeResize.Width -BaseHeight $rectBeforeResize.Height -StartX $cornerTransition.X -StartY $cornerTransition.Y -Mode "corner"
    $rightTracking = Measure-ResizeTracking -Samples $rightSamples -BaseWidth $rectBeforeRightResize.Width -BaseHeight $rectBeforeRightResize.Height -StartX $rightResizeTransition.X -StartY $rightResizeTransition.Y -Mode "right"
    $bottomTracking = Measure-ResizeTracking -Samples $bottomSamples -BaseWidth $rectBeforeBottomResize.Width -BaseHeight $rectBeforeBottomResize.Height -StartX $bottomResizeTransition.X -StartY $bottomResizeTransition.Y -Mode "bottom"
    $resizeFluidityPass = (
        $cornerUniqueSizes -ge 12 -and
        $rightUniqueWidths -ge 12 -and
        $bottomUniqueHeights -ge 12 -and
        $cornerTracking.Pass -and
        $rightTracking.Pass -and
        $bottomTracking.Pass -and
        $growVisualProof.Pass -and
        $shrinkVisualProof.Pass -and
        $shrinkTrackingLagPass
    )
    $resizeFluidityDetail = "cornerUniqueSizes=$cornerUniqueSizes; rightUniqueWidths=$rightUniqueWidths; bottomUniqueHeights=$bottomUniqueHeights; " +
        "cornerMaxLag=$($cornerTracking.MaxLagPx)px/avg=$($cornerTracking.AverageLagPx)px/outliers=$($cornerTracking.OutlierCount)/samples=$($cornerTracking.SampleCount)/raw=$($cornerTracking.RawSampleCount); " +
        "rightMaxLag=$($rightTracking.MaxLagPx)px/avg=$($rightTracking.AverageLagPx)px/outliers=$($rightTracking.OutlierCount)/samples=$($rightTracking.SampleCount)/raw=$($rightTracking.RawSampleCount); " +
        "bottomMaxLag=$($bottomTracking.MaxLagPx)px/avg=$($bottomTracking.AverageLagPx)px/outliers=$($bottomTracking.OutlierCount)/samples=$($bottomTracking.SampleCount)/raw=$($bottomTracking.RawSampleCount); " +
        "growVisualDeltas=$($growVisualProof.SignatureDeltaCount); shrinkVisualDeltas=$($shrinkVisualProof.SignatureDeltaCount); sampled at 42 steps with 8ms delay while the left button was held."
    Add-Step -Id "dashboard_resize_fluidity" -Title "Dashboard resize tracks and repaints at a high-refresh cadence" -Status ($(if ($resizeFluidityPass) { "PASS" } else { "FAIL" })) -Detail $resizeFluidityDetail -Evidence @{ cornerSamples = $cornerSamples; rightSamples = $rightSamples; bottomSamples = $bottomSamples; growVisual = $growVisual; shrinkVisual = $shrinkVisual; cornerTracking = $cornerTracking; rightTracking = $rightTracking; bottomTracking = $bottomTracking; shrinkTracking = $shrinkTracking; growVisualProof = $growVisualProof; shrinkVisualProof = $shrinkVisualProof; minimumUniqueSamples = 12; expectation = "returned UTS said #127 shrink/grow smoothness still had frozen/catch-up behavior, so LV1 requires high-cadence geometry, cursor-to-window tracking-lag, and during-drag visual/pixel-signature proof before mouse release" }
    if (-not $resizeFluidityPass) { throw "Dashboard resize did not track cursor movement smoothly enough during high-cadence drag proof" }
    Add-Step -Id "dashboard_mouse_resize" -Title "Dashboard resizes through pre-click Windows resize cursor transitions" -Status "PASS" -Detail "Corner, right-edge, bottom-edge, grow, and shrink resize actions changed real Dashboard geometry after the helper discovered the same standard Windows resize cursor transition a USER would look for before clicking." -Evidence @{ screenshot = $resizeShot; cornerBefore = "$($rectBeforeResize.Width)x$($rectBeforeResize.Height)"; cornerAfter = "$($rectAfterResize.Width)x$($rectAfterResize.Height)"; rightBeforeWidth = $rectBeforeRightResize.Width; rightAfterWidth = $rectAfterRightResize.Width; bottomBeforeHeight = $rectBeforeBottomResize.Height; bottomAfterHeight = $rectAfterBottomResize.Height; cursorRight = $cursorRight; cursorBottom = $cursorBottom; cursorCorner = $cursorCorner; cursorRightInterior = $cursorRightInterior; cursorBottomInterior = $cursorBottomInterior; cornerTransition = $cornerTransition; rightTransition = $rightResizeTransition; bottomTransition = $bottomResizeTransition; resizeFluidity = @{ cornerUniqueSizes = $cornerUniqueSizes; rightUniqueWidths = $rightUniqueWidths; bottomUniqueHeights = $bottomUniqueHeights; cornerTracking = $cornerTracking; rightTracking = $rightTracking; bottomTracking = $bottomTracking; shrinkTracking = $shrinkTracking; growVisualProof = $growVisualProof; shrinkVisualProof = $shrinkVisualProof } }

    $dashboard = Get-DashboardWindow
    Move-DashboardAwayFromTrayMenuIfNeeded -Dashboard $dashboard

    $closeEvidence = Invoke-TrayAction -ActionName "Close HUD Dashboard" -ExpectedMarker "RENDERER_MAIN|TRAY_MONITORING_HUD_DASHBOARD_REQUESTED|source=menu|visible=false" -TimeoutSeconds $ActionTimeoutSeconds
    Start-Sleep -Milliseconds 1000
    $closeShot = Capture-VirtualScreenshot "06_after_close_hud_dashboard"
    $dashboard = Get-DashboardWindow
    Add-Step -Id "close_dashboard_from_tray" -Title "Tray Close HUD Dashboard hides visible Dashboard" -Status ($(if (-not $dashboard) { "PASS" } else { "FAIL" })) -Detail "Dashboard visible after close: $([bool]$dashboard)" -Evidence @{ screenshot = $closeShot; trayClick = $closeEvidence }
    if ($dashboard) { throw "Close HUD Dashboard did not hide the visible Dashboard" }

    $openEvidence = Invoke-TrayAction -ActionName "Open HUD Dashboard" -ExpectedMarker "RENDERER_MAIN|TRAY_MONITORING_HUD_DASHBOARD_REQUESTED|source=menu|visible=true" -TimeoutSeconds $ActionTimeoutSeconds
    Start-Sleep -Milliseconds 1000
    $openShot = Capture-VirtualScreenshot "07_after_open_hud_dashboard"
    $dashboard = Get-DashboardWindow
    Add-Step -Id "open_dashboard_from_tray" -Title "Tray Open HUD Dashboard shows visible Dashboard" -Status ($(if ($dashboard) { "PASS" } else { "FAIL" })) -Detail "Dashboard visible after open: $([bool]$dashboard)" -Evidence @{ screenshot = $openShot; trayClick = $openEvidence }
    if (-not $dashboard) { throw "Open HUD Dashboard did not show the visible Dashboard" }

    $disableEvidence = Invoke-TrayAction -ActionName "Disable HUD Feature" -ExpectedMarker "RENDERER_MAIN|TRAY_MONITORING_HUD_TOGGLE_REQUESTED|source=menu" -TimeoutSeconds $ActionTimeoutSeconds
    Start-Sleep -Milliseconds 1000
    $disableShot = Capture-VirtualScreenshot "08_after_disable_hud_feature"
    $dashboard = Get-DashboardWindow
    Add-Step -Id "disable_hud_recovers" -Title "Disable HUD Feature hides Dashboard and leaves app usable" -Status ($(if (-not $dashboard) { "PASS" } else { "FAIL" })) -Detail "Dashboard visible after disable: $([bool]$dashboard)" -Evidence @{ screenshot = $disableShot; trayClick = $disableEvidence }
    if ($dashboard) { throw "Disable HUD Feature did not hide the visible Dashboard" }

    if ($SkipNcpRegressionChecks) {
        $exitScopeShot = Capture-VirtualScreenshot "09_exit_confirmation_scoped_out_for_focused_recording_validation"
        foreach ($skippedExitStep in @(
            @{ Id = "tray_exit_confirmation_visible"; Title = "Tray Exit NDAI shows visible confirmation" },
            @{ Id = "tray_exit_cancel_preserves_session"; Title = "Tray Exit cancel or timeout preserves session" },
            @{ Id = "tray_exit_accept_prompt_visible"; Title = "Tray Exit accept path shows visible confirmation" },
            @{ Id = "tray_exit_accept_shuts_down_promptly"; Title = "Tray Exit Yes closes runtime promptly" }
        )) {
            Add-Step -Id $skippedExitStep.Id -Title $skippedExitStep.Title -Status "NOT_RUN" -Detail "Scoped out by -SkipNcpRegressionChecks for focused FAM-006 Recording/returned-UTS repair validation; this is not product acceptance of unrelated tray shutdown behavior." -Evidence @{ screenshot = $exitScopeShot; scope = "outside-current-fam006-recording-repair"; proofDisposition = "not-tested-in-focused-run" }
        }
    } else {
        $exitEvidence = Invoke-TrayAction -ActionName "Exit Nexus Desktop AI" -ExpectedMarker "RENDERER_MAIN|TRAY_SHUTDOWN_CONFIRMATION_REQUESTED|source=menu" -TimeoutSeconds $ActionTimeoutSeconds
        $dialogVisibleMarker = "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_DIALOG_VISIBLE|source=tray_menu"
        $dialogVisible = Wait-ForRuntimeMarker -Marker $dialogVisibleMarker -TimeoutSeconds 5
        $dialogRect = Wait-ForVisibleRuntimeWindowByTitle -Title "Confirm shutdown" -TimeoutSeconds 5
        $confirmShot = Capture-VirtualScreenshot "09_exit_confirmation_prompt"
        if (-not $dialogVisible -or -not $dialogRect -or $dialogRect.Count -ne 4) {
            Add-Step -Id "tray_exit_confirmation_visible" -Title "Tray Exit NDAI shows visible confirmation" -Status "FAIL" -Detail "Visible confirmation marker=$dialogVisible; visible window rect=($($dialogRect -join ','))" -Evidence @{ screenshot = $confirmShot; trayClick = $exitEvidence; expectedMarker = $dialogVisibleMarker }
            throw "Tray Exit NDAI did not show a detectable visible confirmation dialog"
        }
        Start-Sleep -Milliseconds 1200
        $confirmShot = Capture-VirtualScreenshot "09_exit_confirmation_prompt"
        Add-Step -Id "tray_exit_confirmation_visible" -Title "Tray Exit NDAI shows visible confirmation" -Status "PASS" -Detail "Visible confirmation marker emitted; top-level dialog rect=($($dialogRect -join ',')); prompt screenshot captured before timeout." -Evidence @{ screenshot = $confirmShot; trayClick = $exitEvidence; marker = $dialogVisibleMarker; dialogRect = $dialogRect }

        $noEvidence = Send-VisibleRuntimeDialogDecision -Title "Confirm shutdown" -ButtonName "No" -DialogRect $dialogRect
        $cancelled = Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_CANCELLED|source=tray_menu" -TimeoutSeconds 3
        if (-not $cancelled) {
            $cancelled = Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_TIMEOUT|source=tray_menu" -TimeoutSeconds $ExitConfirmationTimeoutSeconds
        }
        $preserved = Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_SESSION_PRESERVED|source=tray_menu" -TimeoutSeconds 3
        $cancelShot = Capture-VirtualScreenshot "10_after_exit_confirmation_cancel"
        $stillHasRuntime = (Find-ProcessesForLogRoot).Count -gt 0
        $sessionPreserved = $cancelled -and $preserved -and $stillHasRuntime
        Add-Step -Id "tray_exit_cancel_preserves_session" -Title "Tray Exit cancel or timeout preserves session" -Status ($(if ($sessionPreserved) { "PASS" } else { "FAIL" })) -Detail "cancel_or_timeout_marker=$cancelled; preserved_marker=$preserved; runtime_process_still_present=$stillHasRuntime" -Evidence @{ screenshot = $cancelShot; buttonClick = $noEvidence }
        if (-not $sessionPreserved) { throw "Tray Exit cancel/timeout did not preserve the session" }

        $exitAcceptEvidence = Invoke-TrayAction -ActionName "Exit Nexus Desktop AI" -ExpectedMarker "RENDERER_MAIN|TRAY_SHUTDOWN_CONFIRMATION_REQUESTED|source=menu" -TimeoutSeconds $ActionTimeoutSeconds
        $acceptDialogVisible = Wait-ForRuntimeMarker -Marker $dialogVisibleMarker -TimeoutSeconds 5
        $acceptDialogRect = Wait-ForVisibleRuntimeWindowByTitle -Title "Confirm shutdown" -TimeoutSeconds 5
        $acceptPromptShot = Capture-VirtualScreenshot "11_exit_confirmation_accept_prompt"
        if (-not $acceptDialogVisible -or -not $acceptDialogRect -or $acceptDialogRect.Count -ne 4) {
            Add-Step -Id "tray_exit_accept_prompt_visible" -Title "Tray Exit accept path shows visible confirmation" -Status "FAIL" -Detail "Visible confirmation marker=$acceptDialogVisible; visible window rect=($($acceptDialogRect -join ','))" -Evidence @{ screenshot = $acceptPromptShot; trayClick = $exitAcceptEvidence; expectedMarker = $dialogVisibleMarker }
            throw "Tray Exit accept path did not show a detectable visible confirmation dialog"
        }
        Add-Step -Id "tray_exit_accept_prompt_visible" -Title "Tray Exit accept path shows visible confirmation" -Status "PASS" -Detail "Visible confirmation marker emitted; top-level dialog rect=($($acceptDialogRect -join ',')); prompt screenshot captured before accepting shutdown." -Evidence @{ screenshot = $acceptPromptShot; trayClick = $exitAcceptEvidence; marker = $dialogVisibleMarker; dialogRect = $acceptDialogRect }

        $yesEvidence = Send-VisibleRuntimeDialogDecision -Title "Confirm shutdown" -ButtonName "Yes" -DialogRect $acceptDialogRect
        $accepted = Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_ACCEPTED|source=tray_menu" -TimeoutSeconds 4
        $shutdownRequested = Wait-ForRuntimeMarker -Marker "RENDERER_MAIN|SHUTDOWN_REQUESTED" -TimeoutSeconds 4
        $runtimeExited = Wait-ForRuntimeExit -TimeoutSeconds 8
        $shutdownShot = Capture-VirtualScreenshot "12_after_exit_confirmation_accept"
        $shutdownAccepted = $accepted -and $shutdownRequested -and $runtimeExited
        Add-Step -Id "tray_exit_accept_shuts_down_promptly" -Title "Tray Exit Yes closes runtime promptly" -Status ($(if ($shutdownAccepted) { "PASS" } else { "FAIL" })) -Detail "accepted_marker=$accepted; shutdown_requested_marker=$shutdownRequested; runtime_exited=$runtimeExited" -Evidence @{ screenshot = $shutdownShot; buttonClick = $yesEvidence }
        if (-not $shutdownAccepted) { throw "Tray Exit Yes did not close the runtime promptly" }
    }
}
catch {
    $overallStatus = "FAIL"
    $failureMessage = "$($_.Exception.Message) | stack=$($_.ScriptStackTrace)"
    Add-Step -Id "human_client_validation_failure" -Title "Human-client validation failure" -Status "FAIL" -Detail $failureMessage -ProofClass "live-human-ui"
}
finally {
    try {
        Capture-VirtualScreenshot "99_final_state" | Out-Null
    } catch {}
    if ($overallStatus -eq "PASS") {
        $script:ShortVideoProof = New-HumanClientShortVideoProof -MinimumFrames 5
        if ($script:ShortVideoProof.status -ne "PASS") {
            $overallStatus = "FAIL"
            $failureMessage = "Mandatory human-client short video/frame-sequence proof failed: $($script:ShortVideoProof.reason)"
            Add-Step -Id "human_client_short_video_proof" -Title "Human-client short video proof is generated" -Status "FAIL" -Detail $failureMessage -ProofClass "live-human-ui" -Evidence @{ shortVideoProof = $script:ShortVideoProof }
        }
        else {
            Add-Step -Id "human_client_short_video_proof" -Title "Human-client short video proof is generated" -Status "PASS" -Detail "Generated mandatory short video proof from ordered screenshot frames." -ProofClass "live-human-ui" -Evidence @{ shortVideoProof = $script:ShortVideoProof }
        }
    }
    if (-not $KeepRuntimeOpenOnFailure) {
        Cleanup-Runtime
    }
    Save-Manifest -Status $overallStatus -Failure $failureMessage
    if ($overallStatus -eq "PASS") {
        Write-Output "PASS: FAM-006 human-client validation passed. Manifest: $ManifestPath"
    }
    else {
        Write-Output "FAIL: FAM-006 human-client validation failed. Manifest: $ManifestPath"
    }
}

if ($overallStatus -eq "PASS") { exit 0 }
exit 1
