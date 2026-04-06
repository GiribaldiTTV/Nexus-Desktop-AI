import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

# --- Win32 function bindings ---
SendMessageTimeoutW = user32.SendMessageTimeoutW
EnumWindows = user32.EnumWindows
FindWindowW = user32.FindWindowW
FindWindowExW = user32.FindWindowExW
SetParent = user32.SetParent
ShowWindow = user32.ShowWindow
SetWindowPos = user32.SetWindowPos
GetWindowLongPtrW = user32.GetWindowLongPtrW
SetWindowLongPtrW = user32.SetWindowLongPtrW
GetClassNameW = user32.GetClassNameW
GetParent = user32.GetParent
MapWindowPoints = user32.MapWindowPoints

LONG_PTR = ctypes.c_ssize_t
ULONG_PTR = ctypes.c_size_t
POINT = wintypes.POINT

SendMessageTimeoutW.argtypes = [
    wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
    wintypes.UINT, wintypes.UINT, ctypes.POINTER(wintypes.DWORD)
]
SendMessageTimeoutW.restype = wintypes.LPARAM

EnumWindows.argtypes = [ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM), wintypes.LPARAM]
EnumWindows.restype = wintypes.BOOL

FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
FindWindowW.restype = wintypes.HWND

FindWindowExW.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
FindWindowExW.restype = wintypes.HWND

SetParent.argtypes = [wintypes.HWND, wintypes.HWND]
SetParent.restype = wintypes.HWND

ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
ShowWindow.restype = wintypes.BOOL

SetWindowPos.argtypes = [
    wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, wintypes.UINT
]
SetWindowPos.restype = wintypes.BOOL

GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
GetWindowLongPtrW.restype = LONG_PTR

SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
SetWindowLongPtrW.restype = LONG_PTR

GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
GetClassNameW.restype = ctypes.c_int
GetParent.argtypes = [wintypes.HWND]
GetParent.restype = wintypes.HWND
MapWindowPoints.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.POINTER(POINT), wintypes.UINT]
MapWindowPoints.restype = ctypes.c_int

# --- Constants ---
SMTO_NORMAL = 0x0000
SW_SHOW = 5
SW_HIDE = 0

HWND_BOTTOM = 1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_FRAMECHANGED = 0x0020
SWP_NOOWNERZORDER = 0x0200
SWP_NOSENDCHANGING = 0x0400

GWL_STYLE = -16
GWL_EXSTYLE = -20

WS_CHILD = 0x40000000
WS_VISIBLE = 0x10000000
WS_POPUP = 0x80000000
WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_SYSMENU = 0x00080000

WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TRANSPARENT = 0x00000020
WS_EX_NOACTIVATE = 0x08000000
WS_EX_APPWINDOW = 0x00040000

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
PROBE_SAMPLE_LIMIT = 4
_LAST_WORKERW_PROBE = {}


def _to_signed_long_ptr(value: int) -> int:
    """Convert a Python int into a pointer-sized signed integer for SetWindowLongPtrW."""
    bits = ctypes.sizeof(LONG_PTR) * 8
    mask = (1 << bits) - 1
    value &= mask
    sign_bit = 1 << (bits - 1)
    if value & sign_bit:
        value -= (1 << bits)
    return value


def _set_window_long_ptr(hwnd: int, index: int, value: int) -> int:
    return SetWindowLongPtrW(hwnd, index, _to_signed_long_ptr(value))


def _hwnd_token(hwnd) -> str:
    if isinstance(hwnd, str):
        return hwnd or "none"
    return hex(int(hwnd)) if hwnd else "none"


def _window_class(hwnd) -> str:
    if not hwnd:
        return "none"

    buf = ctypes.create_unicode_buffer(256)
    if GetClassNameW(hwnd, buf, len(buf)) <= 0:
        return "unknown"
    return buf.value or "unknown"


def _sample_tokens(values, limit=PROBE_SAMPLE_LIMIT):
    if not values:
        return "none"

    tokens = [_hwnd_token(value) for value in values[:limit]]
    remaining = len(values) - len(tokens)
    if remaining > 0:
        tokens.append(f"+{remaining}_more")
    return ",".join(tokens)


def get_last_workerw_probe_events():
    probe = _LAST_WORKERW_PROBE
    if not probe:
        return []

    shell_hosts = probe.get("shell_hosts", [])
    host_tokens = []
    for host in shell_hosts[:2]:
        host_tokens.append(
            f"{host['class']}@{host['hwnd']}(defview={host['defview']},next={host['next_workerw']})"
        )
    remaining_hosts = len(shell_hosts) - len(host_tokens)
    if remaining_hosts > 0:
        host_tokens.append(f"+{remaining_hosts}_more")

    return [
        (
            "WORKERW_PROBE|"
            f"progman={probe.get('progman', 'none')}|"
            f"progman_class={probe.get('progman_class', 'none')}|"
            f"progman_message_sent={probe.get('progman_message_sent', 'false')}|"
            f"progman_message_result={probe.get('progman_message_result', 'none')}|"
            f"progman_child_workerw={probe.get('progman_child_workerw', 'none')}|"
            f"top_level_window_count={probe.get('top_level_window_count', 0)}"
        ),
        (
            "WORKERW_HOSTS|"
            f"shell_host_count={len(shell_hosts)}|"
            f"shell_hosts={','.join(host_tokens) if host_tokens else 'none'}|"
            f"selected_workerw={probe.get('selected_workerw', 'none')}|"
            f"selection_reason={probe.get('selection_reason', 'none')}"
        ),
        (
            "WORKERW_CANDIDATES|"
            f"workerw_count={len(probe.get('workerw_candidates', []))}|"
            f"workerw_sample={_sample_tokens(probe.get('workerw_candidates', []))}"
        ),
    ]


def get_workerw():
    progman = FindWindowW("Progman", None)
    progman_message_sent = False
    progman_message_result = "none"
    selection_reason = "none"
    progman_child_workerw = None
    if progman:
        result = wintypes.DWORD()
        send_result = SendMessageTimeoutW(
            progman,
            0x052C,
            0,
            0,
            SMTO_NORMAL,
            1000,
            ctypes.byref(result),
        )
        progman_message_sent = bool(send_result)
        progman_message_result = str(int(result.value))
        progman_child_workerw = FindWindowExW(progman, None, "WorkerW", None)

    workerw = None
    windows = []

    @WNDENUMPROC
    def enum_windows_proc(hwnd, lparam):
        windows.append(hwnd)
        return True

    EnumWindows(enum_windows_proc, 0)

    workerw_candidates = []
    shell_hosts = []

    for hwnd in windows:
        window_class = _window_class(hwnd)

        if window_class == "WorkerW":
            workerw_candidates.append(hwnd)

        shell_def_view = FindWindowExW(hwnd, None, "SHELLDLL_DefView", None)
        if shell_def_view:
            possible = FindWindowExW(None, hwnd, "WorkerW", None)
            shell_hosts.append(
                {
                    "hwnd": _hwnd_token(hwnd),
                    "class": window_class,
                    "defview": _hwnd_token(shell_def_view),
                    "next_workerw": _hwnd_token(possible),
                }
            )
            if workerw is None and possible:
                workerw = possible
                selection_reason = "next_workerw"

    if workerw is None and progman_child_workerw:
        workerw = progman_child_workerw
        selection_reason = "progman_child_workerw"

    if workerw is None and progman:
        workerw = progman
        selection_reason = "progman_fallback"

    global _LAST_WORKERW_PROBE
    _LAST_WORKERW_PROBE = {
        "progman": _hwnd_token(progman),
        "progman_class": _window_class(progman),
        "progman_message_sent": "true" if progman_message_sent else "false",
        "progman_message_result": progman_message_result,
        "progman_child_workerw": _hwnd_token(progman_child_workerw),
        "top_level_window_count": len(windows),
        "shell_hosts": shell_hosts,
        "workerw_candidates": [_hwnd_token(hwnd) for hwnd in workerw_candidates],
        "selected_workerw": _hwnd_token(workerw),
        "selection_reason": selection_reason,
    }
    return workerw


def attach_window_to_desktop(hwnd: int) -> bool:
    workerw = get_workerw()
    selection_reason = _LAST_WORKERW_PROBE.get("selection_reason", "none")
    if not workerw or selection_reason not in {"next_workerw", "progman_child_workerw", "progman_fallback"}:
        return False

    # Parent first so the shell owns the window relationship.
    SetParent(hwnd, workerw)

    # Force child-style hosting to try to avoid normal app-window treatment.
    style = int(GetWindowLongPtrW(hwnd, GWL_STYLE))
    style &= ~(
        WS_POPUP
        | WS_OVERLAPPEDWINDOW
        | WS_CAPTION
        | WS_THICKFRAME
        | WS_MINIMIZEBOX
        | WS_MAXIMIZEBOX
        | WS_SYSMENU
        | WS_VISIBLE
    )
    style |= WS_CHILD
    _set_window_long_ptr(hwnd, GWL_STYLE, style)

    exstyle = int(GetWindowLongPtrW(hwnd, GWL_EXSTYLE))
    exstyle &= ~WS_EX_APPWINDOW
    exstyle |= WS_EX_TRANSPARENT | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
    _set_window_long_ptr(hwnd, GWL_EXSTYLE, exstyle)

    SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        0,
        0,
        0,
        0,
        SWP_NOMOVE
        | SWP_NOSIZE
        | SWP_NOACTIVATE
        | SWP_FRAMECHANGED
        | SWP_NOOWNERZORDER
        | SWP_NOSENDCHANGING,
    )
    return True


def make_window_noninteractive(hwnd: int) -> None:
    # Reapply the desktop-child styles after the widget has finished showing.
    style = int(GetWindowLongPtrW(hwnd, GWL_STYLE))
    style &= ~(
        WS_POPUP
        | WS_OVERLAPPEDWINDOW
        | WS_CAPTION
        | WS_THICKFRAME
        | WS_MINIMIZEBOX
        | WS_MAXIMIZEBOX
        | WS_SYSMENU
        | WS_VISIBLE
    )
    style |= WS_CHILD
    _set_window_long_ptr(hwnd, GWL_STYLE, style)

    exstyle = int(GetWindowLongPtrW(hwnd, GWL_EXSTYLE))
    exstyle &= ~WS_EX_APPWINDOW
    exstyle |= WS_EX_TRANSPARENT | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
    _set_window_long_ptr(hwnd, GWL_EXSTYLE, exstyle)

    SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        0,
        0,
        0,
        0,
        SWP_NOMOVE
        | SWP_NOSIZE
        | SWP_NOACTIVATE
        | SWP_FRAMECHANGED
        | SWP_NOOWNERZORDER
        | SWP_NOSENDCHANGING,
    )


def position_desktop_child(hwnd: int, x: int, y: int, width: int, height: int) -> None:
    parent = GetParent(hwnd)
    left = int(x)
    top = int(y)
    right = int(x + width)
    bottom = int(y + height)

    if parent:
        points = (POINT * 2)()
        points[0].x = left
        points[0].y = top
        points[1].x = right
        points[1].y = bottom
        MapWindowPoints(0, parent, points, 2)
        left = points[0].x
        top = points[0].y
        right = points[1].x
        bottom = points[1].y

    SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        left,
        top,
        max(1, right - left),
        max(1, bottom - top),
        SWP_NOACTIVATE
        | SWP_SHOWWINDOW
        | SWP_FRAMECHANGED
        | SWP_NOOWNERZORDER
        | SWP_NOSENDCHANGING,
    )
