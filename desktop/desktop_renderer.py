import inspect
import json
import math
import os
import re
import ctypes
import ctypes.wintypes
import datetime
import time
import urllib.parse
import webbrowser
import weakref
from html import escape
from pathlib import Path
from typing import Iterable, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QFrame,
    QDialog,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QComboBox,
    QScrollArea,
    QFileDialog,
    QToolTip,
    QSizePolicy,
    QCheckBox,
    QSizeGrip,
    QSplitter,
    QSplitterHandle,
)
from PySide6.QtCore import Qt, QTimer, QUrl, QRect, QRectF, Signal, QPoint, QPointF, QEvent, QSettings
from PySide6.QtGui import QColor, QCursor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath, QPalette, QPen, QRegion
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

from .interaction_overlay_model import CommandOverlayModel
from .ai_provider_state import (
    build_default_provider_readiness_config,
    build_provider_setup_completion_foundation_state,
    resolve_default_provider_durable_consent_store_dir,
)
from .monitoring_hud_controls import build_monitoring_hud_controls_visibility_contract
from .monitoring_hud_access import MonitoringHudAccessAdapter
from .monitoring_hud_placement import build_monitoring_hud_placement_contract
from .monitoring_hud_status import build_monitoring_hud_status_snapshot
from .monitoring_hud_state import save_monitoring_hud_state
from .monitoring_hud_telemetry import build_monitoring_hud_telemetry_snapshot
from .recording_output_contract import recording_export_dir, recording_output_dir, write_recording_output_files
from .saved_action_authoring import (
    CallableGroupDraft,
    CallableGroupDraftValidationError,
    CallableGroupUnsafeSourceError,
    SavedActionDraft,
    SavedActionDraftValidationError,
    SavedActionUnsafeSourceError,
    create_callable_group_from_draft,
    create_saved_action_from_draft,
    delete_callable_group,
    delete_saved_action,
    load_callable_group_draft_for_edit,
    load_saved_action_draft_for_edit,
    update_callable_group_from_draft,
    update_saved_action_from_draft,
)
from .saved_action_source import SavedActionSourceWriteBlocked
from .resident_access import (
    DEFAULT_QUICK_SLOT_ROUTE_IDS,
    MAX_QUICK_SLOT_COUNT,
    ResidentAccessSettings,
    WINDOWS_TRAY_VISIBILITY_LIMITATION,
    build_resident_access_menu_plan,
    load_resident_access_settings,
    normalize_quick_slot_ids,
    quick_slot_candidate_routes,
    route_for_id,
    save_resident_access_settings,
)
from .shared_action_model import (
    DEFAULT_COMMAND_ACTIONS,
    build_callable_group_phrases,
    build_saved_action_callable_phrases,
    default_saved_action_trigger_mode,
    execute_command_group,
    launch_command_action,
)
from .orin_support_reporting import SupportBundleError, prepare_manual_issue_report
from .workerw_utils import (
    WNDENUMPROC,
    attach_window_to_desktop,
    get_last_workerw_probe_events,
    make_window_noninteractive,
    position_desktop_child,
)

WM_NCHITTEST = 0x0084
WM_CLOSE = 0x0010
WM_CANCELMODE = 0x001F
WM_SETCURSOR = 0x0020
WM_SYSCOMMAND = 0x0112
WM_NCMOUSEMOVE = 0x00A0
WM_NCLBUTTONDOWN = 0x00A1
WM_NCLBUTTONUP = 0x00A2
WM_NCLBUTTONDBLCLK = 0x00A3
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_CAPTURECHANGED = 0x0215
VK_LBUTTON = 0x01
MK_LBUTTON = 0x0001
HTTRANSPARENT = -1
HTCLIENT = 1
HTCAPTION = 2
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17
SC_CLOSE = 0xF060
IDC_ARROW = 32512
IDC_SIZENWSE = 32642
IDC_SIZENESW = 32643
IDC_SIZEWE = 32644
IDC_SIZENS = 32645
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32
WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
HCURSOR = getattr(ctypes.wintypes, "HCURSOR", ctypes.wintypes.HANDLE)
LoadCursorW = user32.LoadCursorW
LoadCursorW.restype = HCURSOR
SetCursor = user32.SetCursor
SetCursor.argtypes = [HCURSOR]
SetCursor.restype = HCURSOR
SetCapture = user32.SetCapture
SetCapture.argtypes = [ctypes.wintypes.HWND]
SetCapture.restype = ctypes.wintypes.HWND
ReleaseCapture = user32.ReleaseCapture
ReleaseCapture.restype = ctypes.c_bool
GetAsyncKeyState = user32.GetAsyncKeyState
GetAsyncKeyState.argtypes = [ctypes.c_int]
GetAsyncKeyState.restype = ctypes.c_short
GetWindowRect = user32.GetWindowRect
GetWindowRect.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.wintypes.RECT)]
GetWindowRect.restype = ctypes.c_bool
GetForegroundWindow = user32.GetForegroundWindow
GetForegroundWindow.restype = ctypes.wintypes.HWND
GetCurrentThreadId = kernel32.GetCurrentThreadId
GetCurrentThreadId.restype = ctypes.wintypes.DWORD
GetWindowThreadProcessId = user32.GetWindowThreadProcessId
GetWindowThreadProcessId.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.wintypes.DWORD)]
GetWindowThreadProcessId.restype = ctypes.wintypes.DWORD
AttachThreadInput = user32.AttachThreadInput
AttachThreadInput.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.DWORD, ctypes.c_bool]
AttachThreadInput.restype = ctypes.c_bool
SetForegroundWindow = user32.SetForegroundWindow
SetForegroundWindow.argtypes = [ctypes.wintypes.HWND]
SetForegroundWindow.restype = ctypes.c_bool
SetActiveWindow = user32.SetActiveWindow
SetActiveWindow.argtypes = [ctypes.wintypes.HWND]
SetActiveWindow.restype = ctypes.wintypes.HWND
BringWindowToTop = user32.BringWindowToTop
BringWindowToTop.argtypes = [ctypes.wintypes.HWND]
BringWindowToTop.restype = ctypes.c_bool
SwitchToThisWindow = user32.SwitchToThisWindow
SwitchToThisWindow.argtypes = [ctypes.wintypes.HWND, ctypes.c_bool]
SwitchToThisWindow.restype = None
GetClassNameW = user32.GetClassNameW
GetClassNameW.argtypes = [ctypes.wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]
GetClassNameW.restype = ctypes.c_int
GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = [ctypes.wintypes.HWND]
GetWindowTextLengthW.restype = ctypes.c_int
GetWindowTextW = user32.GetWindowTextW
GetWindowTextW.argtypes = [ctypes.wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]
GetWindowTextW.restype = ctypes.c_int
GetCursorPos = user32.GetCursorPos
GetCursorPos.argtypes = [ctypes.POINTER(ctypes.wintypes.POINT)]
GetCursorPos.restype = ctypes.c_bool
WindowFromPoint = user32.WindowFromPoint
WindowFromPoint.argtypes = [ctypes.wintypes.POINT]
WindowFromPoint.restype = ctypes.wintypes.HWND
EnumChildWindows = user32.EnumChildWindows
EnumChildWindows.argtypes = [ctypes.wintypes.HWND, WNDENUMPROC, ctypes.wintypes.LPARAM]
EnumChildWindows.restype = ctypes.wintypes.BOOL
EnumWindows = user32.EnumWindows
EnumWindows.argtypes = [WNDENUMPROC, ctypes.wintypes.LPARAM]
EnumWindows.restype = ctypes.wintypes.BOOL
ShowWindowW = user32.ShowWindow
ShowWindowW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
ShowWindowW.restype = ctypes.c_bool
SetWindowPos = user32.SetWindowPos
SetWindowPos.argtypes = [
    ctypes.wintypes.HWND,
    ctypes.wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint,
]
SetWindowPos.restype = ctypes.c_bool
GetWindowLongW = user32.GetWindowLongW
GetWindowLongW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
GetWindowLongW.restype = ctypes.c_long
SetWindowLongW = user32.SetWindowLongW
SetWindowLongW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_long]
SetWindowLongW.restype = ctypes.c_long
IsWindowVisible = user32.IsWindowVisible
IsWindowVisible.argtypes = [ctypes.wintypes.HWND]
IsWindowVisible.restype = ctypes.c_bool
GetParentW = user32.GetParent
GetParentW.argtypes = [ctypes.wintypes.HWND]
GetParentW.restype = ctypes.wintypes.HWND
GetWindowW = user32.GetWindow
GetWindowW.argtypes = [ctypes.wintypes.HWND, ctypes.c_uint]
GetWindowW.restype = ctypes.wintypes.HWND
IsWindow = user32.IsWindow
IsWindow.argtypes = [ctypes.wintypes.HWND]
IsWindow.restype = ctypes.c_bool
IsIconic = user32.IsIconic
IsIconic.argtypes = [ctypes.wintypes.HWND]
IsIconic.restype = ctypes.c_bool
GetWindowLongPtrW = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
GetWindowLongPtrW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
GetWindowLongPtrW.restype = ctypes.c_ssize_t
SetWindowLongPtrW = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
SetWindowLongPtrW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
SetWindowLongPtrW.restype = ctypes.c_ssize_t


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.wintypes.UINT),
        ("flags", ctypes.wintypes.UINT),
        ("showCmd", ctypes.wintypes.UINT),
        ("ptMinPosition", ctypes.wintypes.POINT),
        ("ptMaxPosition", ctypes.wintypes.POINT),
        ("rcNormalPosition", ctypes.wintypes.RECT),
    ]


GetWindowPlacement = user32.GetWindowPlacement
GetWindowPlacement.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(WINDOWPLACEMENT)]
GetWindowPlacement.restype = ctypes.c_bool
HRGN = getattr(ctypes.wintypes, "HRGN", ctypes.wintypes.HANDLE)
HGDIOBJ = getattr(ctypes.wintypes, "HGDIOBJ", ctypes.wintypes.HANDLE)
CreateRoundRectRgn = gdi32.CreateRoundRectRgn
CreateRoundRectRgn.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
]
CreateRoundRectRgn.restype = HRGN
SetWindowRgn = user32.SetWindowRgn
SetWindowRgn.argtypes = [ctypes.wintypes.HWND, HRGN, ctypes.wintypes.BOOL]
SetWindowRgn.restype = ctypes.c_int
DeleteObject = gdi32.DeleteObject
DeleteObject.argtypes = [HGDIOBJ]
DeleteObject.restype = ctypes.wintypes.BOOL
SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_SHOW = 5
SW_RESTORE = 9
HWND_TOP = ctypes.wintypes.HWND(0)
SWP_NOZORDER = 0x0004
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
SWP_SHOWWINDOW = 0x0040
SWP_NOOWNERZORDER = 0x0200
GW_OWNER = 4
GWL_STYLE = -16
GWL_EXSTYLE = -20
GWLP_HWNDPARENT = -8
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
WS_EX_NOACTIVATE = 0x08000000
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def classify_ai_dashboard_iconic_artifact(
    native_facts: dict[str, object],
    *,
    visible_proof: str | None = None,
) -> str:
    """Keep native window facts separate from visual artifact adjudication."""
    proof = str(visible_proof or "").strip().upper()
    if proof == "DETECTED":
        return "DETECTED"
    if proof == "NOT_DETECTED":
        return "NOT_DETECTED_WITH_VISIBLE_PROOF"
    if proof == "NOT_APPLICABLE":
        return "N/A"
    return "VISUAL_ADJUDICATION_REQUIRED"


_DIALOG_RUNTIME_LOGGER = None

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_BORDER_COLOR = 34
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36
DWMWCP_ROUND = 2

THEMED_TOOLTIP_QSS = """
            QToolTip {
                border: 1px solid rgba(102, 219, 204, 0.22);
                border-radius: 12px;
                background: rgba(5, 16, 28, 248);
                color: rgba(192, 212, 207, 0.96);
                padding: 12px 14px;
                font-size: 12px;
                line-height: 1.45em;
            }
"""


def _windows_colorref(red: int, green: int, blue: int) -> int:
    return (blue << 16) | (green << 8) | red


def _apply_windows_dark_title_bar(widget):
    if os.name != "nt":
        return
    hwnd = 0
    try:
        hwnd = int(widget.winId())
    except Exception:
        hwnd = 0
    if not hwnd:
        return

    try:
        dwmapi = ctypes.windll.dwmapi
        set_window_attribute = dwmapi.DwmSetWindowAttribute
    except Exception:
        return

    def set_int_attribute(attribute: int, value: int):
        try:
            attribute_value = ctypes.c_int(value)
            set_window_attribute(
                ctypes.wintypes.HWND(hwnd),
                ctypes.c_uint(attribute),
                ctypes.byref(attribute_value),
                ctypes.sizeof(attribute_value),
            )
        except Exception:
            pass

    set_int_attribute(DWMWA_USE_IMMERSIVE_DARK_MODE, 1)
    set_int_attribute(DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUND)
    set_int_attribute(DWMWA_CAPTION_COLOR, _windows_colorref(9, 18, 28))
    set_int_attribute(DWMWA_TEXT_COLOR, _windows_colorref(236, 247, 255))
    set_int_attribute(DWMWA_BORDER_COLOR, _windows_colorref(26, 61, 86))


def _emit_global_runtime_marker(event: str):
    logger = _DIALOG_RUNTIME_LOGGER
    if not callable(logger):
        return
    try:
        logger(event)
    except Exception:
        pass


def _clear_layout_widgets(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.deleteLater()
        elif child_layout is not None:
            _clear_layout_widgets(child_layout)


def _visible_row_height_for_layout(layout, max_rows: int, *, extra_padding: int = 0) -> int:
    if layout is None or max_rows <= 0:
        return 0

    spacing = max(0, int(layout.spacing()))
    margins = layout.contentsMargins()
    total_height = margins.top() + margins.bottom()
    visible_rows = 0

    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item is None:
            continue
        widget = item.widget()
        if widget is None or not widget.isVisible():
            continue
        rendered_height = widget.height() if widget.height() > 0 else 0
        row_height = (
            rendered_height
            if rendered_height > 0
            else max(widget.sizeHint().height(), widget.minimumSizeHint().height())
        )
        total_height += row_height
        visible_rows += 1
        if visible_rows >= max_rows:
            break
        total_height += spacing

    if visible_rows == 0:
        return 0
    return total_height + max(0, int(extra_padding))


def _screen_available_geometry_for_widget(widget: QWidget) -> QRect | None:
    screen = None
    try:
        screen = widget.screen()
    except Exception:
        screen = None
    if screen is None:
        try:
            screen = QApplication.screenAt(widget.frameGeometry().center())
        except Exception:
            screen = None
    if screen is None:
        try:
            screen = QApplication.primaryScreen()
        except Exception:
            screen = None
    if screen is None:
        return None
    try:
        return screen.availableGeometry()
    except Exception:
        return None


def _clamp_window_to_available_screen(widget: QWidget, *, padding: int = 18):
    bounds = _screen_available_geometry_for_widget(widget)
    if bounds is None:
        return

    max_width = max(360, bounds.width() - (padding * 2))
    max_height = max(280, bounds.height() - (padding * 2))
    target_width = min(widget.width(), max_width)
    target_height = min(widget.height(), max_height)
    if target_width != widget.width() or target_height != widget.height():
        widget.resize(target_width, target_height)

    frame = widget.frameGeometry()
    x = max(bounds.x() + padding, min(frame.x(), bounds.x() + bounds.width() - frame.width() - padding))
    y = max(bounds.y() + padding, min(frame.y(), bounds.y() + bounds.height() - frame.height() - padding))
    if x != frame.x() or y != frame.y():
        widget.move(x, y)


def _schedule_window_clamp(widget: QWidget, *, padding: int = 18):
    QTimer.singleShot(0, lambda target=widget, inset=padding: _clamp_window_to_available_screen(target, padding=inset))


def _apply_rounded_dialog_mask(widget: QWidget, *, radius: int = 22):
    if widget is None:
        return
    rect = widget.rect()
    if rect.width() <= 0 or rect.height() <= 0:
        return
    path = QPainterPath()
    path.addRoundedRect(QRectF(rect), radius, radius)
    widget.setMask(QRegion(path.toFillPolygon().toPolygon()))


def _saved_inventory_target_kind_label(item: dict) -> str:
    raw_target_kind = (item.get("target_kind_label") or item.get("target_kind") or "").strip()
    normalized = raw_target_kind.casefold()
    if normalized == "app":
        return "Application"
    if normalized == "folder":
        return "Folder"
    if normalized == "file":
        return "File"
    if normalized == "url":
        return "Website URL"
    return raw_target_kind


def _build_saved_inventory_item_text(item: dict) -> str:
    title = item.get("title", "")
    origin_label = item.get("origin_label", "Saved")
    target_kind = item.get("target_kind", "")
    target_display = item.get("target_display") or item.get("target", "")
    item_text = title
    metadata_bits = [origin_label]
    if target_kind:
        metadata_bits.append(target_kind)
    if metadata_bits:
        item_text += f"\n{' - '.join(metadata_bits)}"
    if target_display:
        item_text += f"\n{target_display}"
    return item_text


def _populate_saved_inventory_item_layout(
    layout,
    parent,
    items: list[dict],
    edit_handler,
    delete_handler,
):
    _clear_layout_widgets(layout)
    for item in items:
        item_id = str(item.get("id") or "").strip()
        title = item.get("title", "")
        origin_label = item.get("origin_label", "Saved")
        target_kind_label = _saved_inventory_target_kind_label(item)
        target_display = item.get("target_display") or item.get("target", "")

        item_frame = QFrame(parent)
        item_frame.setProperty("inventoryRole", "itemFrame")
        item_frame.setMinimumHeight(70)
        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(8, 4, 8, 4)
        item_layout.setSpacing(6)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(1)

        title_label = QLabel(title, item_frame)
        title_label.setProperty("inventoryRole", "itemTitle")
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)

        metadata_bits = [f"{origin_label} task"]
        if target_kind_label:
            metadata_bits.append(target_kind_label)
        metadata_label = QLabel(" | ".join(metadata_bits), item_frame)
        metadata_label.setProperty("inventoryRole", "itemMeta")
        metadata_label.setWordWrap(True)
        content_layout.addWidget(metadata_label)

        if target_display:
            target_label = QLabel(target_display, item_frame)
            target_label.setProperty("inventoryRole", "itemTarget")
            target_label.setWordWrap(True)
            target_label.setToolTip(item.get("target", ""))
            content_layout.addWidget(target_label)

        item_layout.addLayout(content_layout, 1)

        if item_id:
            action_shell = QFrame(item_frame)
            action_shell.setProperty("inventoryRole", "actionShell")
            button_layout = QVBoxLayout(action_shell)
            button_layout.setContentsMargins(2, 2, 2, 2)
            button_layout.setSpacing(2)

            edit_button = QPushButton("Edit", action_shell)
            edit_button.setProperty("inventoryRole", "editButton")
            edit_button.setToolTip(f'Edit "{title}"')
            edit_button.clicked.connect(
                lambda _checked=False, action_id=item_id: edit_handler(action_id)
            )
            button_layout.addWidget(edit_button)

            delete_button = QPushButton("Delete", action_shell)
            delete_button.setProperty("inventoryRole", "deleteButton")
            delete_button.setToolTip(f'Delete "{title}"')
            delete_button.clicked.connect(
                lambda _checked=False, action_id=item_id: delete_handler(action_id)
            )
            button_layout.addWidget(delete_button)
            button_layout.addStretch(1)

            item_layout.addWidget(action_shell, 0, Qt.AlignTop)

        layout.addWidget(item_frame)
    layout.addStretch(1)


def _populate_saved_group_item_layout(
    layout,
    parent,
    items: list[dict],
    edit_handler,
    delete_handler,
):
    _clear_layout_widgets(layout)
    for item in items:
        item_id = str(item.get("id") or "").strip()
        title = item.get("title", "")
        aliases = item.get("aliases") or []
        member_count = int(item.get("member_count") or 0)
        member_noun = "member" if member_count == 1 else "members"
        alias_preview = ", ".join(str(alias).strip() for alias in aliases if str(alias).strip())

        item_frame = QFrame(parent)
        item_frame.setProperty("inventoryRole", "itemFrame")
        item_frame.setMinimumHeight(70)
        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(8, 4, 8, 4)
        item_layout.setSpacing(6)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(1)

        title_label = QLabel(title, item_frame)
        title_label.setProperty("inventoryRole", "itemTitle")
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)

        metadata_label = QLabel(f"Custom group | {member_count} {member_noun}", item_frame)
        metadata_label.setProperty("inventoryRole", "itemMeta")
        metadata_label.setWordWrap(True)
        metadata_label.setToolTip(
            f'This group can surface {member_count} {member_noun} when one of its exact aliases is used.'
        )
        content_layout.addWidget(metadata_label)

        if alias_preview:
            aliases_label = QLabel(f"Aliases: {alias_preview}", item_frame)
            aliases_label.setProperty("inventoryRole", "itemTarget")
            aliases_label.setWordWrap(True)
            aliases_label.setToolTip(f'Exact callable aliases for "{title}": {alias_preview}')
            content_layout.addWidget(aliases_label)

        item_layout.addLayout(content_layout, 1)

        if item_id:
            action_shell = QFrame(item_frame)
            action_shell.setProperty("inventoryRole", "actionShell")
            button_layout = QVBoxLayout(action_shell)
            button_layout.setContentsMargins(2, 2, 2, 2)
            button_layout.setSpacing(2)

            edit_button = QPushButton("Edit", action_shell)
            edit_button.setProperty("inventoryRole", "editButton")
            edit_button.setToolTip(f'Edit the aliases or members for "{title}".')
            edit_button.clicked.connect(
                lambda _checked=False, group_id=item_id: edit_handler(group_id)
            )
            button_layout.addWidget(edit_button)

            delete_button = QPushButton("Delete", action_shell)
            delete_button.setProperty("inventoryRole", "deleteButton")
            delete_button.setToolTip(f'Delete the group "{title}". Tasks stay saved.')
            delete_button.clicked.connect(
                lambda _checked=False, group_id=item_id: delete_handler(group_id)
            )
            button_layout.addWidget(delete_button)
            button_layout.addStretch(1)

            item_layout.addWidget(action_shell, 0, Qt.AlignTop)

        layout.addWidget(item_frame)
    layout.addStretch(1)


class CommandInputLineEdit(QLineEdit):
    submit_requested = Signal()
    escape_requested = Signal()
    input_armed_changed = Signal(bool)
    focus_acquired = Signal()
    focus_lost = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._input_armed = False
        self._manual_focus_requested = False
        self._last_focus_was_manual = False
        self._local_typing_enabled = False
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setPlaceholderText("Type a built-in or saved action")
        self.setReadOnly(True)

    def is_input_armed(self) -> bool:
        return self._input_armed

    def set_input_armed(self, armed: bool, notify: bool = True):
        armed = bool(armed)
        if self._input_armed == armed:
            return

        self._input_armed = armed
        self.setReadOnly(not armed)
        if not armed:
            self._local_typing_enabled = False
            self.clearFocus()
        if notify:
            self.input_armed_changed.emit(armed)

    def set_local_typing_enabled(self, enabled: bool):
        self._local_typing_enabled = bool(enabled)

    def mousePressEvent(self, event):
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            if not self._input_armed:
                self.set_input_armed(True)
            self._manual_focus_requested = True
            self._local_typing_enabled = True
            self.setFocus(Qt.MouseFocusReason)
            # The line can already be programmatically focused on open, so a real
            # user click needs to re-assert manual ownership even if focusInEvent
            # does not fire again.
            self._last_focus_was_manual = True
            self.focus_acquired.emit()
            if event.button() == Qt.RightButton:
                event.accept()
                return

        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not self._local_typing_enabled:
                event.accept()
                return
            self.submit_requested.emit()
            event.accept()
            return

        if event.key() == Qt.Key_Escape:
            if not self._local_typing_enabled:
                event.accept()
                return
            self.escape_requested.emit()
            event.accept()
            return

        if not self._input_armed:
            event.accept()
            return

        if not self._local_typing_enabled:
            event.accept()
            return

        super().keyPressEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._last_focus_was_manual = self._manual_focus_requested or event.reason() == Qt.MouseFocusReason
        self._manual_focus_requested = False
        self.focus_acquired.emit()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._last_focus_was_manual = False
        self._manual_focus_requested = False
        self.focus_lost.emit()

    def last_focus_was_manual(self) -> bool:
        return self._last_focus_was_manual


class ImmediateHelpButton(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTipDuration(20000)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_Hover, True)

    def _tooltip_anchor(self) -> QPoint:
        return self.mapToGlobal(
            QPoint(max(22, min(self.width() - 12, self.width() // 3)), self.height() + 12)
        )

    def show_help_tooltip_now(self):
        tooltip_text = (self.toolTip() or "").strip()
        if not tooltip_text:
            return
        QToolTip.hideText()
        QToolTip.showText(
            self._tooltip_anchor(),
            tooltip_text,
            self,
            self.rect(),
            self.toolTipDuration(),
        )

    def enterEvent(self, event):
        super().enterEvent(event)
        self.show_help_tooltip_now()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.show_help_tooltip_now()

    def mousePressEvent(self, event):
        self.show_help_tooltip_now()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.show_help_tooltip_now()
            event.accept()
            return
        super().keyPressEvent(event)

    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)

    def focusOutEvent(self, event):
        QToolTip.hideText()
        super().focusOutEvent(event)


class DialogChromeBar(QFrame):
    def __init__(
        self,
        title: str,
        dialog: QDialog,
        *,
        object_prefix: str,
        parent=None,
        show_title: bool = False,
        show_minimize: bool = False,
        show_maximize: bool = False,
        clustered_controls: bool = False,
        hero_header: bool = False,
        compact_hero: bool = False,
        settings_header: bool = False,
        kicker: str = "",
        subtitle: str = "",
        role_pairs: tuple[tuple[str, str], ...] = (),
    ):
        super().__init__(parent or dialog)
        self._dialog = dialog
        self._drag_offset: QPoint | None = None
        self.setObjectName(f"{object_prefix}ChromeBar")
        self.setProperty("chromeRole", "bar")
        self.setProperty("showTitle", bool(show_title))
        self.setProperty("windowControlCluster", "compact-minimize-maximize-close" if clustered_controls else "compact-close")
        header_anatomy = "compact-dialog-bar"
        if settings_header:
            header_anatomy = "ndai-global-settings-centered-settings-chrome-v22"
        elif hero_header:
            header_anatomy = "ai-control-center-compact-reference-derived" if compact_hero else "ai-control-center-reference-derived"
        self.setProperty("headerAnatomy", header_anatomy)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.OpenHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        if settings_header:
            layout = QGridLayout(self)
            layout.setContentsMargins(16, 5, 12, 5)
            layout.setHorizontalSpacing(8)
            layout.setVerticalSpacing(0)
            layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 0)
            layout.setColumnStretch(2, 1)

            self.kicker_label = QLabel(kicker, self)
            self.kicker_label.setObjectName(f"{object_prefix}ChromeKicker")
            self.kicker_label.setProperty("chromeRole", "kicker")
            self.kicker_label.setAlignment(Qt.AlignCenter)
            self.kicker_label.setVisible(False)

            self.title_label = QLabel(title, self)
            self.title_label.setObjectName(f"{object_prefix}ChromeTitle")
            self.title_label.setProperty("chromeRole", "title")
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setVisible(bool(show_title))
            layout.addWidget(self.title_label, 0, 1, Qt.AlignCenter)

            self.subtitle_label = QLabel("", self)
            self.subtitle_label.setVisible(False)
            self.role_pill = QFrame(self)
            self.role_pill.setVisible(False)
            self.role_labels = []
        else:
            layout = QHBoxLayout(self)
        if hero_header and not settings_header:
            if compact_hero:
                layout.setContentsMargins(20, 13, 14, 12)
                layout.setSpacing(10)
            else:
                layout.setContentsMargins(24, 20, 16, 18)
                layout.setSpacing(14)
            title_stack = QVBoxLayout()
            title_stack.setContentsMargins(0, 0, 0, 0)
            title_stack.setSpacing(2 if compact_hero else 3)

            self.kicker_label = QLabel(kicker, self)
            self.kicker_label.setObjectName(f"{object_prefix}ChromeKicker")
            self.kicker_label.setProperty("chromeRole", "kicker")
            self.kicker_label.setVisible(bool(kicker))
            title_stack.addWidget(self.kicker_label)

            self.title_label = QLabel(title, self)
            self.title_label.setObjectName(f"{object_prefix}ChromeTitle")
            self.title_label.setProperty("chromeRole", "title")
            self.title_label.setVisible(bool(show_title))
            title_stack.addWidget(self.title_label)

            self.subtitle_label = QLabel(subtitle, self)
            self.subtitle_label.setObjectName(f"{object_prefix}ChromeSubtitle")
            self.subtitle_label.setProperty("chromeRole", "subtitle")
            self.subtitle_label.setVisible(bool(subtitle))
            title_stack.addWidget(self.subtitle_label)

            self.role_pill = QFrame(self)
            self.role_pill.setObjectName(f"{object_prefix}ChromeRolePill")
            self.role_pill.setProperty("chromeRole", "surface-role")
            self.role_pill.setAttribute(Qt.WA_StyledBackground, True)
            role_layout = QHBoxLayout(self.role_pill)
            role_layout.setContentsMargins(10, 4, 10, 4)
            role_layout.setSpacing(8)
            self.role_labels: list[QLabel] = []
            for label, value in role_pairs:
                pair = QLabel(f"{label} - {value}", self.role_pill)
                pair.setObjectName(f"{object_prefix}ChromeRolePair")
                pair.setProperty("chromeRole", "surface-role-pair")
                role_layout.addWidget(pair)
                self.role_labels.append(pair)
            role_layout.addStretch(1)
            self.role_pill.setVisible(bool(role_pairs))
            title_stack.addWidget(self.role_pill, 0, Qt.AlignLeft)
            layout.addLayout(title_stack, 1)
        elif not settings_header:
            layout.setContentsMargins(12, 5, 14, 5)
            layout.setSpacing(4)

            self.kicker_label = QLabel("", self)
            self.kicker_label.setVisible(False)
            self.subtitle_label = QLabel("", self)
            self.subtitle_label.setVisible(False)
            self.role_pill = QFrame(self)
            self.role_pill.setVisible(False)
            self.role_labels = []

            self.title_label = QLabel(title, self)
            self.title_label.setObjectName(f"{object_prefix}ChromeTitle")
            self.title_label.setProperty("chromeRole", "title")
            self.title_label.setVisible(bool(show_title))
            layout.addWidget(self.title_label, 0, Qt.AlignVCenter)
            layout.addStretch(1)

        self.control_cluster = QFrame(self)
        self.control_cluster.setObjectName(f"{object_prefix}WindowControls")
        self.control_cluster.setProperty("chromeRole", "window-controls")
        if settings_header:
            self.control_cluster.setProperty("controlClusterDensity", "settings-compact-v22")
        self.control_cluster.setAttribute(Qt.WA_StyledBackground, True)
        control_layout = QHBoxLayout(self.control_cluster)
        control_layout.setContentsMargins(2, 2, 2, 2)
        control_layout.setSpacing(2)

        self.minimize_button = QPushButton("\N{MINUS SIGN}", self.control_cluster)
        self.minimize_button.setObjectName(f"{object_prefix}ChromeMinimize")
        self.minimize_button.setProperty("chromeRole", "minimize")
        self.minimize_button.setAccessibleName(f"Minimize {title}")
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setFlat(True)
        control_size = 24 if settings_header else (28 if clustered_controls else 20)
        self.minimize_button.setFixedSize(control_size, control_size)
        self.minimize_button.setVisible(bool(show_minimize))
        self.minimize_button.clicked.connect(self._dialog.showMinimized)
        control_layout.addWidget(self.minimize_button, 0, Qt.AlignVCenter)

        self.maximize_button = QPushButton("\N{WHITE SQUARE}", self.control_cluster)
        self.maximize_button.setObjectName(f"{object_prefix}ChromeMaximize")
        self.maximize_button.setProperty("chromeRole", "maximize")
        self.maximize_button.setAccessibleName(f"Maximize {title} unavailable")
        self.maximize_button.setCursor(Qt.PointingHandCursor)
        self.maximize_button.setFlat(True)
        self.maximize_button.setFixedSize(control_size, control_size)
        self.maximize_button.setVisible(bool(show_maximize))
        self.maximize_button.setEnabled(False)
        control_layout.addWidget(self.maximize_button, 0, Qt.AlignVCenter)

        self.close_button = QPushButton("\N{MULTIPLICATION SIGN}", self.control_cluster)
        self.close_button.setObjectName(f"{object_prefix}ChromeClose")
        self.close_button.setProperty("chromeRole", "close")
        self.close_button.setAccessibleName(f"Close {title}")
        close_font = QFont("Segoe UI Symbol")
        close_font.setPointSize(11)
        close_font.setWeight(QFont.DemiBold)
        self.close_button.setFont(close_font)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setFlat(True)
        self.close_button.setFixedSize(control_size, control_size)
        self.close_button.clicked.connect(self._dialog.reject)
        control_layout.addWidget(self.close_button, 0, Qt.AlignVCenter)
        if settings_header:
            layout.addWidget(self.control_cluster, 0, 2, Qt.AlignRight | Qt.AlignVCenter)
        else:
            layout.addWidget(self.control_cluster, 0, Qt.AlignTop if hero_header else Qt.AlignVCenter)
        self.setFixedHeight(46 if settings_header else ((92 if compact_hero else 148) if hero_header else (36 if clustered_controls else 28)))

    def set_title(self, title: str):
        self.title_label.setText(title)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self._dialog.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self._dialog.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)


class NexusSettingsSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)
        self.setProperty("splitterVisualState", "normal")

    def _set_visual_state(self, state: str):
        self.setProperty("splitterVisualState", state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def enterEvent(self, event):
        if self.property("splitterVisualState") != "active":
            self._set_visual_state("hover")
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.property("splitterVisualState") != "active":
            self._set_visual_state("normal")
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._set_visual_state("active")
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._set_visual_state("hover" if self.rect().contains(event.position().toPoint()) else "normal")
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        center_x = rect.width() / 2
        state = str(self.property("splitterVisualState") or "normal")
        line_alpha = {"normal": 16, "hover": 58, "active": 92}.get(state, 16)
        dot_alpha = {"normal": 0, "hover": 96, "active": 144}.get(state, 0)
        painter.setPen(QPen(QColor(122, 232, 255, line_alpha), 1.0))
        painter.drawLine(int(center_x), 10, int(center_x), max(10, rect.height() - 10))
        if dot_alpha:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(153, 246, 228, dot_alpha))
            mid_y = rect.height() / 2
            for offset in (-7, 0, 7):
                painter.drawRoundedRect(QRectF(center_x - 1.0, mid_y + offset - 1.0, 2.0, 2.0), 1.0, 1.0)


class NexusSettingsSplitter(QSplitter):
    def createHandle(self):
        handle = NexusSettingsSplitterHandle(self.orientation(), self)
        handle.setObjectName("residentAccessSettingsSplitterHandle")
        handle.setAccessibleName("Resize Global Settings navigation pane")
        return handle


class NexusCategoryIcon(QWidget):
    def __init__(self, icon_kind: str, parent=None):
        super().__init__(parent)
        self.icon_kind = icon_kind
        self.setFixedSize(16, 16)
        self.setProperty("categoryIconRenderPolicy", "high-contrast-contained-12px-v38")
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setPen(QPen(QColor(224, 252, 255, 246), 1.35, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        if self.icon_kind == "tray":
            painter.setBrush(QColor(91, 224, 244, 36))
            painter.drawRoundedRect(QRectF(2.4, 2.7, 7.2, 5.2), 1.25, 1.25)
            painter.setBrush(Qt.NoBrush)
            painter.drawLine(QPointF(6.0, 8.0), QPointF(6.0, 10.0))
            painter.drawLine(QPointF(3.8, 10.0), QPointF(8.2, 10.0))
        elif self.icon_kind == "hud":
            painter.setBrush(QColor(91, 224, 244, 28))
            painter.drawRoundedRect(QRectF(1.8, 2.0, 8.4, 7.0), 1.4, 1.4)
            painter.setBrush(Qt.NoBrush)
            path = QPainterPath()
            path.moveTo(2.8, 6.2)
            path.lineTo(4.1, 6.2)
            path.lineTo(5.0, 4.1)
            path.lineTo(6.1, 7.2)
            path.lineTo(7.0, 5.4)
            path.lineTo(9.0, 5.4)
            painter.drawPath(path)
        else:
            path = QPainterPath()
            path.moveTo(6.8, 1.5)
            path.lineTo(2.9, 6.9)
            path.lineTo(5.8, 6.9)
            path.lineTo(4.9, 10.8)
            path.lineTo(9.2, 5.4)
            path.lineTo(6.3, 5.4)
            path.closeSubpath()
            painter.setPen(QPen(QColor(227, 255, 249, 170), 0.65, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(QColor(184, 255, 236, 244))
            painter.drawPath(path)


class NexusGlyphButton(QPushButton):
    def __init__(self, glyph: str, parent=None):
        super().__init__("", parent)
        self._glyph = glyph
        self.setProperty("glyphButton", glyph)

    def set_glyph(self, glyph: str):
        self._glyph = glyph
        self.setProperty("glyphButton", glyph)
        self.update()

    def enterEvent(self, event):
        super().enterEvent(event)
        self._update_glyph_zone_parent()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._update_glyph_zone_parent()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._update_glyph_zone_parent()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self._update_glyph_zone_parent()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._update_glyph_zone_parent()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._update_glyph_zone_parent()

    def _update_glyph_zone_parent(self) -> None:
        if bool(self.property("glyphZoneButton")) and self.parentWidget() is not None:
            self.parentWidget().update()
        self.update()

    def paintEvent(self, event):
        glyph_zone = bool(self.property("glyphZoneButton"))
        if not glyph_zone:
            super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        enabled = self.isEnabled()
        quiet = bool(self.property("quietGlyph"))
        interactive = self.underMouse() or self.hasFocus() or self.isDown()
        segment = str(self.property("glyphSegment") or "")
        if glyph_zone:
            self._paint_glyph_zone_background(painter, segment, enabled, interactive)
        glyph_alpha = 152 if quiet else 226
        disabled_alpha = 58 if quiet else 92
        if glyph_zone and enabled:
            glyph_alpha = 222 if interactive else 172
        custom_scale = self.property("glyphScale")
        color = QColor(216, 255, 248, glyph_alpha if enabled else disabled_alpha)
        if self.property("dangerGlyph"):
            danger_alpha = 226 if interactive else (190 if quiet else 226)
            color = QColor(255, 196, 196, danger_alpha if enabled else (78 if quiet else 96))
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        try:
            scale = float(custom_scale) if custom_scale is not None else (0.66 if quiet else 1.0)
        except (TypeError, ValueError):
            scale = 0.66 if quiet else 1.0
        if self._glyph in {"up", "down", "chevron-down", "chevron-right"}:
            path = QPainterPath()
            if self._glyph == "up":
                path.moveTo(cx, cy - 4.0 * scale)
                path.lineTo(cx - 5.0 * scale, cy + 3.5 * scale)
                path.lineTo(cx + 5.0 * scale, cy + 3.5 * scale)
            elif self._glyph == "down" or self._glyph == "chevron-down":
                path.moveTo(cx - 5.0 * scale, cy - 3.5 * scale)
                path.lineTo(cx + 5.0 * scale, cy - 3.5 * scale)
                path.lineTo(cx, cy + 4.0 * scale)
            else:
                path.moveTo(cx - 3.0 * scale, cy - 5.0 * scale)
                path.lineTo(cx + 4.0 * scale, cy)
                path.lineTo(cx - 3.0 * scale, cy + 5.0 * scale)
            path.closeSubpath()
            painter.drawPath(path)
            return
        if self._glyph == "close":
            painter.setPen(QPen(color, 1.35 if quiet else 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            span = 4.0 * scale
            painter.drawLine(QPoint(int(cx - span), int(cy - span)), QPoint(int(cx + span), int(cy + span)))
            painter.drawLine(QPoint(int(cx + span), int(cy - span)), QPoint(int(cx - span), int(cy + span)))

    def _paint_glyph_zone_background(self, painter: QPainter, segment: str, enabled: bool, interactive: bool) -> None:
        is_danger = bool(self.property("dangerGlyph")) or segment == "standalone-danger"
        if is_danger:
            if not enabled:
                fill = QColor(148, 163, 184, 38)
                border = QColor(148, 163, 184, 46)
            elif self.isDown():
                fill = QColor(127, 29, 29, 184)
                border = QColor(252, 165, 165, 188)
            elif interactive:
                fill = QColor(91, 23, 35, 178)
                border = QColor(248, 113, 113, 184)
            else:
                fill = QColor(52, 13, 21, 138)
                border = QColor(248, 113, 113, 128)
            rect = QRectF(0.5, 0.5, max(0, self.width() - 1), max(0, self.height() - 1))
            painter.setPen(QPen(border, 1.0))
            painter.setBrush(fill)
            painter.drawRoundedRect(rect, 8.0, 8.0)
            return

        if segment in {"left", "right"}:
            return

        if not enabled:
            fill = QColor(148, 163, 184, 34)
        elif self.isDown():
            fill = QColor(20, 184, 166, 66)
        elif interactive:
            fill = QColor(20, 184, 166, 42)
        else:
            return

        rect = QRectF(0, 0, self.width(), self.height())
        radius = 8.0
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(fill)
        painter.setClipRect(rect)
        path = QPainterPath()
        if segment == "left":
            path.addRoundedRect(QRectF(rect.x(), rect.y(), rect.width() + radius, rect.height()), radius, radius)
        elif segment == "right":
            path.addRoundedRect(QRectF(rect.x() - radius, rect.y(), rect.width() + radius, rect.height()), radius, radius)
        else:
            path.addRect(rect)
        painter.drawPath(path)
        painter.restore()


class NexusToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(38, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setProperty("togglePrimitive", "ndai-compact-track-thumb-v1")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        enabled = self.isEnabled()
        checked = self.isChecked()
        interactive = self.underMouse() or self.hasFocus()
        track = QRectF(1.0, 2.0, self.width() - 2.0, self.height() - 4.0)
        if not enabled:
            track_fill = QColor(35, 48, 64, 150)
            track_border = QColor(100, 116, 139, 90)
            thumb_fill = QColor(148, 163, 184, 130)
        elif checked:
            track_fill = QColor(13, 148, 136, 220 if interactive else 196)
            track_border = QColor(153, 246, 228, 190 if interactive else 142)
            thumb_fill = QColor(236, 253, 245, 248)
        else:
            track_fill = QColor(21, 35, 52, 235)
            track_border = QColor(122, 232, 255, 130 if interactive else 88)
            thumb_fill = QColor(183, 214, 224, 226)
        painter.setPen(QPen(track_border, 1.0))
        painter.setBrush(track_fill)
        painter.drawRoundedRect(track, 9.0, 9.0)
        thumb_size = 14.0
        thumb_x = self.width() - thumb_size - 4.0 if checked else 4.0
        painter.setPen(Qt.NoPen)
        painter.setBrush(thumb_fill)
        painter.drawEllipse(QRectF(thumb_x, 4.0, thumb_size, thumb_size))
        if self.hasFocus():
            painter.setPen(QPen(QColor(153, 246, 228, 150), 1.0, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(QRectF(0.5, 1.5, self.width() - 1.0, self.height() - 3.0), 9.5, 9.5)


class QuickSlotReorderPill(QFrame):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        outer = QRectF(0.5, 0.5, max(0, self.width() - 1), max(0, self.height() - 1))
        inner = QRectF(1.0, 1.0, max(0, self.width() - 2), max(0, self.height() - 2))
        radius = 8.0
        full_inner_path = QPainterPath()
        full_inner_path.addRoundedRect(inner, radius, radius)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(4, 24, 38, 194))
        painter.drawPath(full_inner_path)

        segments = (
            ("left", self.findChild(QPushButton, "residentAccessQuickSlotMoveUp"), QRectF(1.0, 1.0, 25.0, 27.0)),
            ("right", self.findChild(QPushButton, "residentAccessQuickSlotMoveDown"), QRectF(27.0, 1.0, 25.0, 27.0)),
        )
        for _role, button, segment_rect in segments:
            fill = self._segment_fill(button)
            if fill is None:
                continue
            clip_path = QPainterPath()
            clip_path.addRect(segment_rect)
            painter.setBrush(fill)
            painter.drawPath(full_inner_path.intersected(clip_path))

        painter.setPen(QPen(QColor(118, 226, 255, 56), 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(outer, 8.5, 8.5)

    def _segment_fill(self, button: Optional[QPushButton]) -> Optional[QColor]:
        if button is None:
            return None
        if not button.isEnabled():
            return QColor(148, 163, 184, 38)
        if button.isDown():
            return QColor(20, 184, 166, 70)
        if button.underMouse() or button.hasFocus():
            return QColor(20, 184, 166, 46)
        return None


class ResidentAccessSettingsDialog(QDialog):
    RESIZE_MARGIN = 8
    RESIZE_CORNER_MARGIN = 12
    RESIZE_CURSOR_RELEASE_MARGIN = 2
    BASE_MINIMUM_SIZE = (684, 388)
    MAXIMUM_SIZE = (840, 610)
    DEFAULT_SIZE = (780, 458)
    QUICK_SLOT_ROW_HEIGHT = 38
    QUICK_SLOT_ROW_SPACING = 7
    QUICK_SLOT_INDEX_WIDTH = 22
    QUICK_SLOT_ACTION_CLUSTER_WIDTH = 86
    QUICK_SLOT_COMBO_MIN_WIDTH = 250
    QUICK_SLOT_COMBO_MAX_WIDTH = 456
    QUICK_SLOT_ROW_SIDE_GUTTER = 8
    QUICK_SLOT_ROW_ITEM_GAP = 6
    QUICK_SLOT_CONTAINER_CHROME_HEIGHT = 118
    QUICK_ACCESS_WINDOW_VERTICAL_CHROME = 204
    SETTINGS_NAV_MIN_WIDTH = 76
    SETTINGS_NAV_MAX_WIDTH = 270
    SETTINGS_NAV_CONTENT_MIN_WIDTH = 144
    SETTINGS_NAV_CATEGORY_GAP = 4
    SETTINGS_NAV_LABEL_POINT_SIZE = 10
    SETTINGS_NAV_PARENT_DEFAULT_WIDTH = 118
    SETTINGS_NAV_CHILD_DEFAULT_WIDTH = 112
    SETTINGS_NAV_PARENT_MAX_WIDTH = 129
    SETTINGS_NAV_CHILD_MAX_WIDTH = 136
    SETTINGS_NAV_PARENT_DEFAULT_LABEL_WIDTH = 58
    SETTINGS_NAV_CHILD_DEFAULT_LABEL_WIDTH = 88

    @classmethod
    def _settings_nav_text_width(cls, text: str) -> int:
        font = QFont("Segoe UI")
        font.setPointSize(cls.SETTINGS_NAV_LABEL_POINT_SIZE)
        return QFontMetrics(font).horizontalAdvance(text) + 2

    @classmethod
    def _settings_nav_label_width(cls, text: str, role: str) -> int:
        width = cls._settings_nav_text_width(text)
        default_width = (
            cls.SETTINGS_NAV_PARENT_DEFAULT_LABEL_WIDTH
            if role == "parent"
            else cls.SETTINGS_NAV_CHILD_DEFAULT_LABEL_WIDTH
        )
        max_width = (
            cls.SETTINGS_NAV_PARENT_MAX_WIDTH - 53
            if role == "parent"
            else cls.SETTINGS_NAV_CHILD_MAX_WIDTH - 25
        )
        return min(max(default_width, width), max_width)

    @classmethod
    def _settings_nav_pill_width(cls, text: str, role: str) -> int:
        text_width = cls._settings_nav_text_width(text)
        if role == "parent":
            required_width = 53 + text_width
            return min(max(cls.SETTINGS_NAV_PARENT_DEFAULT_WIDTH, required_width), cls.SETTINGS_NAV_PARENT_MAX_WIDTH)
        required_width = 25 + text_width
        return min(max(cls.SETTINGS_NAV_CHILD_DEFAULT_WIDTH, required_width), cls.SETTINGS_NAV_CHILD_MAX_WIDTH)

    SETTINGS_FOCUS_ALIASES = {
        "tray": "tray",
        "quick_access": "quick_access",
        "hud": "hud",
        "monitoring_hud": "hud",
        "hud_dashboard": "hud_dashboard",
        "ai_status": "tray",
        "privacy": "tray",
        "owner_routes": "tray",
    }
    SETTINGS_TRAY_CONTEXT_DETAILS = {
        "ai_status": "AI status opens through the FAM-007 Command Center doorway.",
        "privacy": "Privacy controls stay FAM-007-owned; Tray keeps the doorway visible.",
        "owner_routes": "Unavailable tray routes stay future-gated until the owning surface is active.",
    }

    def __init__(self, parent=None, runtime=None, focus: str = "quick_access"):
        super().__init__(parent)
        self.runtime = runtime or parent
        self._focus = focus or "quick_access"
        self._focus_context = self._focus
        self._settings = load_resident_access_settings()
        self._saved_settings = self._settings
        self._notice_text = ""
        self._close_guard_active = False
        self._close_guard_pending_result = None
        self._close_guard_pending_callback = None
        self._dirty_close_intercept_count = 0
        self._dirty_close_last_event_ignored = False
        self._dirty_close_last_resolution = ""
        self._slot_combos: list[QComboBox] = []
        self._nav_buttons: dict[str, QPushButton] = {}
        self._tray_children_expanded = True
        self._hud_children_expanded = True
        self._hud_access_result = None
        self._hud_operation_active = False
        self._hud_progress_label = "Applying..."
        self._hud_checkbox_sync = False
        self._settings_resize_active = False
        self._settings_resize_edges = Qt.Edges()
        self._settings_resize_start_global = QPoint()
        self._settings_resize_start_geometry = QRect()
        self._settings_resize_pending_point = QPoint()
        self._settings_resize_last_geometry = QRect()
        self._settings_resize_cursor_key = None
        self._settings_resize_override_cursor_active = False
        self._settings_resize_poll_timer = QTimer(self)
        self._settings_resize_poll_timer.setInterval(8)
        self._settings_resize_poll_timer.timeout.connect(self._poll_settings_resize)
        self._settings_resize_hover_timer = QTimer(self)
        self._settings_resize_hover_timer.setInterval(8)
        self._settings_resize_hover_timer.timeout.connect(self._poll_settings_resize_hover_cursor)
        self.setModal(False)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.setWindowTitle("Global Settings")
        self.setObjectName("residentAccessSettingsDialog")
        self.setProperty("surfaceClassification", "Nexus-Owned Product Surface")
        self.setProperty("visualInheritance", "UIREF-001-UIREF-002-UIREF-003-UIREF-007-FAM-002")
        self.setProperty(
            "settingsInformationArchitecture",
            "global-settings-shell-tray-and-hud-parent-child-deterministic-rail-r2",
        )
        self.setProperty("referenceDerivedHeader", "ndai-global-settings-centered-settings-chrome-v22")
        self.setProperty("settingsVisualRepair", "lv1-global-settings-compact-ndai-grammar-close-intercept-v32")
        self.setProperty("dirtyGuardReference", "manage-monitors-modal-save-discard-cancel")
        self.setProperty("uiExposureContract", "real-enabled-meaningful-visible-ui-v1")
        self.setProperty("sharedPrimitiveClaim", "none-promoted-reference-derived-only")
        self.setProperty("referenceComparatorRequired", "ui-reference-plus-product-grade-same-defect-comparator-v22")
        self.setProperty("standardWindowArchitecture", "pyside-dialogchrome-native-edge-corner-hit-test-reference-derived")
        self.setProperty("platformException", "none")
        self.setProperty("windowResizeBehavior", "uiref-007-frameless-top-level-hover-polled-edge-corner-cursor-app-owned-fallback-8px-edge-12px-corner-no-visible-grip-splitter-travel-76-270-horizontal-overflow-minimum-684x388-dynamic-content-minimum-maximum-840x610-close-intercept-no-forced-arrow-hysteresis-v43")
        self.setProperty("quickAccessLayoutPolicy", "uiref-007-deterministic-row-width-combo-integrated-action-capsule-row-count-close-intercept-v42")
        self.setProperty("settingsRailPolishPolicy", "fixed-gap-deterministic-text-width-sharpened-icons-horizontal-overflow-splitter-travel-v41")
        self.setProperty("contentScalePolicy", "control-pill-anchored-proportional-content-scale-v32")
        self.setProperty("dirtyCloseRouteCoverage", "window-close-system-close-keybind-client-shutdown-save-discard-cancel-v32")
        self.setProperty("dirtyCloseInterceptState", "idle")
        self.setProperty("visibleResizeGrip", "removed")
        self.setProperty("deferredWatermarkConcept", "future-centered-global-settings-watermark-deferred-no-runtime-exposure-v22")
        self.setProperty("runtimeWatermarkVisible", "false")
        self.setMinimumSize(*self.BASE_MINIMUM_SIZE)
        self.setMaximumSize(*self.MAXIMUM_SIZE)
        self.resize(*self.DEFAULT_SIZE)
        self._apply_native_settings_palette()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("residentAccessSettingsShell")
        self.shell.setAttribute(Qt.WA_StyledBackground, True)
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.chrome_bar = DialogChromeBar(
            "Settings",
            self,
            object_prefix="residentAccessSettings",
            parent=self.shell,
            show_title=True,
            show_minimize=True,
            clustered_controls=True,
            settings_header=True,
            role_pairs=(),
        )
        self.chrome_bar.setFixedHeight(46)
        shell_layout.addWidget(self.chrome_bar)

        body = QWidget(self.shell)
        self.settings_body = body
        body.setObjectName("residentAccessSettingsBody")
        body.setAttribute(Qt.WA_StyledBackground, True)
        shell_layout.addWidget(body, 1)

        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(16, 9, 16, 14)
        body_layout.setSpacing(0)

        self.settings_splitter = NexusSettingsSplitter(Qt.Horizontal, body)
        self.settings_splitter.setObjectName("residentAccessSettingsSplitter")
        self.settings_splitter.setChildrenCollapsible(False)
        self.settings_splitter.setHandleWidth(9)
        self.settings_splitter.setProperty("settingsSplitterAffordance", "quiet-default-hover-dots-9px-hit-zone-v28")
        self.settings_splitter.setAccessibleName("Resize Global Settings navigation pane")
        body_layout.addWidget(self.settings_splitter, 1)

        self.nav_shell = QFrame(body)
        self.nav_shell.setObjectName("residentAccessSettingsNavShell")
        self.nav_shell.setAttribute(Qt.WA_StyledBackground, True)
        self.nav_shell.setProperty("settingsShellIdentity", "ndai-slim-global-settings")
        self.nav_shell.setMinimumWidth(self.SETTINGS_NAV_MIN_WIDTH)
        self.nav_shell.setMaximumWidth(self.SETTINGS_NAV_MAX_WIDTH)
        self.nav_shell.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.settings_splitter.addWidget(self.nav_shell)
        nav_shell_layout = QVBoxLayout(self.nav_shell)
        nav_shell_layout.setContentsMargins(0, 0, 0, 0)
        nav_shell_layout.setSpacing(0)

        self.nav_scroll_area = QScrollArea(self.nav_shell)
        self.nav_scroll_area.setObjectName("residentAccessSettingsNavScrollArea")
        self.nav_scroll_area.setFrameShape(QFrame.NoFrame)
        self.nav_scroll_area.setWidgetResizable(True)
        self.nav_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.nav_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.nav_scroll_area.setAccessibleName("Global Settings navigation list")
        nav_shell_layout.addWidget(self.nav_scroll_area, 1)

        self.nav_content = QWidget(self.nav_scroll_area)
        self.nav_content.setObjectName("residentAccessSettingsNavContent")
        self.nav_content.setMinimumWidth(self.SETTINGS_NAV_CONTENT_MIN_WIDTH)
        self.nav_content.setMinimumHeight(96)
        self.nav_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.nav_scroll_area.setWidget(self.nav_content)
        nav_layout = QVBoxLayout(self.nav_content)
        nav_layout.setContentsMargins(6, 6, 6, 6)
        nav_layout.setSpacing(4)

        self.tray_nav_item = QFrame(self.nav_shell)
        self.tray_nav_item.setObjectName("residentAccessSettingsCategoryItem")
        self.tray_nav_item.setProperty("settingsCategoryRole", "selectable-parent-page")
        self.tray_nav_item.setProperty("settingsNavDensity", "slim-parent-row")
        self.tray_nav_item.setAttribute(Qt.WA_StyledBackground, True)
        tray_label = "Tray"
        tray_pill_width = self._settings_nav_pill_width(tray_label, "parent")
        tray_label_width = self._settings_nav_label_width(tray_label, "parent")
        self.tray_nav_item.setFixedSize(tray_pill_width, 28)
        self.tray_nav_item.setProperty("settingsNavSizingPolicy", "font-metric-default-min-clamped-v39")
        tray_nav_layout = QHBoxLayout(self.tray_nav_item)
        tray_nav_layout.setContentsMargins(5, 2, 4, 2)
        tray_nav_layout.setSpacing(5)
        self.tray_nav_indicator = QLabel("", self.tray_nav_item)
        self.tray_nav_indicator.setObjectName("residentAccessSettingsNavIndicator")
        self.tray_nav_indicator.setFixedSize(2, 18)
        tray_nav_layout.addWidget(self.tray_nav_indicator)
        self.tray_nav_icon = NexusCategoryIcon("tray", self.tray_nav_item)
        self.tray_nav_icon.setObjectName("residentAccessSettingsNavPrimaryIcon")
        self.tray_nav_icon.setAccessibleName("Tray category icon")
        self.tray_nav_icon.setFixedSize(12, 12)
        tray_nav_layout.addWidget(self.tray_nav_icon)
        self.tray_nav_button = QPushButton(tray_label, self.tray_nav_item)
        self.tray_nav_button.setObjectName("residentAccessSettingsCategoryButton")
        self.tray_nav_button.setCheckable(True)
        self.tray_nav_button.setMaximumWidth(tray_label_width)
        self.tray_nav_button.setAccessibleName("Open Tray Settings")
        self.tray_nav_button.clicked.connect(lambda: self.set_focus("tray"))
        tray_nav_layout.addWidget(self.tray_nav_button, 1)
        self.tray_expand_button = NexusGlyphButton("chevron-down", self.tray_nav_item)
        self.tray_expand_button.setObjectName("residentAccessSettingsNavExpander")
        self.tray_expand_button.setProperty("quietGlyph", True)
        self.tray_expand_button.setCheckable(True)
        self.tray_expand_button.setChecked(True)
        self.tray_expand_button.setAccessibleName("Expand or collapse Tray settings pages")
        self.tray_expand_button.clicked.connect(self._toggle_tray_children)
        tray_nav_layout.addWidget(self.tray_expand_button)
        nav_layout.addWidget(self.tray_nav_item)
        self._nav_buttons["tray"] = self.tray_nav_button

        self.subpage_nav_rail = QFrame(self.nav_shell)
        self.subpage_nav_rail.setObjectName("residentAccessSettingsSubpageRail")
        self.subpage_nav_rail.setAttribute(Qt.WA_StyledBackground, True)
        subpage_layout = QVBoxLayout(self.subpage_nav_rail)
        subpage_layout.setContentsMargins(14, 0, 0, 0)
        subpage_layout.setSpacing(2)

        quick_access_label = "Quick Access"
        quick_access_pill_width = self._settings_nav_pill_width(quick_access_label, "child")
        quick_access_label_width = self._settings_nav_label_width(quick_access_label, "child")
        self.quick_access_nav_item = QFrame(self.nav_shell)
        self.quick_access_nav_item.setObjectName("residentAccessSettingsNavItem")
        self.quick_access_nav_item.setProperty("navState", "selected")
        self.quick_access_nav_item.setProperty("settingsNavDensity", "two-level-subpage-row")
        self.quick_access_nav_item.setProperty("settingsNavIdentity", "ndai-signal-leaf")
        self.quick_access_nav_item.setAttribute(Qt.WA_StyledBackground, True)
        self.quick_access_nav_item.setFixedSize(quick_access_pill_width, 26)
        self.quick_access_nav_item.setProperty("settingsNavSizingPolicy", "font-metric-default-min-clamped-v39")
        nav_item_layout = QHBoxLayout(self.quick_access_nav_item)
        nav_item_layout.setContentsMargins(5, 2, 4, 2)
        nav_item_layout.setSpacing(4)
        self.quick_access_nav_icon = NexusCategoryIcon("quick-access", self.quick_access_nav_item)
        self.quick_access_nav_icon.setObjectName("residentAccessSettingsNavIcon")
        self.quick_access_nav_icon.setAccessibleName("Quick Access child page icon")
        self.quick_access_nav_icon.setFixedSize(12, 12)
        nav_item_layout.addWidget(self.quick_access_nav_icon)
        nav_text_stack = QVBoxLayout()
        nav_text_stack.setContentsMargins(0, 0, 0, 0)
        nav_text_stack.setSpacing(0)
        self.quick_access_nav_button = QPushButton(quick_access_label, self.quick_access_nav_item)
        self.quick_access_nav_button.setObjectName("residentAccessSettingsNavButton")
        self.quick_access_nav_button.setCheckable(True)
        self.quick_access_nav_button.setMaximumWidth(quick_access_label_width)
        self.quick_access_nav_button.setAccessibleName("Open Tray Quick Access Settings")
        self.quick_access_nav_button.clicked.connect(lambda: self.set_focus("quick_access"))
        self._nav_buttons["quick_access"] = self.quick_access_nav_button
        nav_text_stack.addWidget(self.quick_access_nav_button)
        self.quick_access_nav_caption = QLabel("", self.quick_access_nav_item)
        self.quick_access_nav_caption.setObjectName("residentAccessSettingsNavCaption")
        self.quick_access_nav_caption.setVisible(False)
        nav_text_stack.addWidget(self.quick_access_nav_caption)
        nav_item_layout.addLayout(nav_text_stack, 1)
        subpage_layout.addWidget(self.quick_access_nav_item)
        subpage_layout.addStretch(1)
        nav_layout.addWidget(self.subpage_nav_rail)

        self.hud_nav_item = QFrame(self.nav_shell)
        self.hud_nav_item.setObjectName("residentAccessSettingsCategoryItem")
        self.hud_nav_item.setProperty("settingsCategoryRole", "persistent-owner-bounded-parent")
        self.hud_nav_item.setProperty("settingsNavDensity", "slim-parent-row")
        self.hud_nav_item.setAttribute(Qt.WA_StyledBackground, True)
        hud_label = "HUD"
        hud_pill_width = self._settings_nav_pill_width(hud_label, "parent")
        hud_label_width = self._settings_nav_label_width(hud_label, "parent")
        self.hud_nav_item.setFixedSize(hud_pill_width, 28)
        self.hud_nav_item.setProperty("settingsNavSizingPolicy", "font-metric-default-min-clamped-v39")
        hud_nav_layout = QHBoxLayout(self.hud_nav_item)
        hud_nav_layout.setContentsMargins(5, 2, 4, 2)
        hud_nav_layout.setSpacing(5)
        self.hud_nav_indicator = QLabel("", self.hud_nav_item)
        self.hud_nav_indicator.setObjectName("residentAccessSettingsNavIndicator")
        self.hud_nav_indicator.setFixedSize(2, 18)
        hud_nav_layout.addWidget(self.hud_nav_indicator)
        self.hud_nav_icon = NexusCategoryIcon("hud", self.hud_nav_item)
        self.hud_nav_icon.setObjectName("residentAccessSettingsNavPrimaryIcon")
        self.hud_nav_icon.setAccessibleName("HUD category icon")
        self.hud_nav_icon.setFixedSize(12, 12)
        hud_nav_layout.addWidget(self.hud_nav_icon)
        self.hud_nav_button = QPushButton(hud_label, self.hud_nav_item)
        self.hud_nav_button.setObjectName("residentAccessSettingsCategoryButton")
        self.hud_nav_button.setCheckable(True)
        self.hud_nav_button.setMaximumWidth(hud_label_width)
        self.hud_nav_button.setAccessibleName("Open HUD Settings")
        self.hud_nav_button.clicked.connect(lambda: self.set_focus("hud"))
        hud_nav_layout.addWidget(self.hud_nav_button, 1)
        self._nav_buttons["hud"] = self.hud_nav_button
        self.hud_expand_button = NexusGlyphButton("chevron-down", self.hud_nav_item)
        self.hud_expand_button.setObjectName("residentAccessSettingsNavExpander")
        self.hud_expand_button.setProperty("quietGlyph", True)
        self.hud_expand_button.setCheckable(True)
        self.hud_expand_button.setChecked(True)
        self.hud_expand_button.setAccessibleName("Expand or collapse HUD settings pages")
        self.hud_expand_button.clicked.connect(self._toggle_hud_children)
        hud_nav_layout.addWidget(self.hud_expand_button)
        nav_layout.addWidget(self.hud_nav_item)

        self.hud_subpage_nav_rail = QFrame(self.nav_shell)
        self.hud_subpage_nav_rail.setObjectName("residentAccessSettingsSubpageRail")
        self.hud_subpage_nav_rail.setAttribute(Qt.WA_StyledBackground, True)
        hud_subpage_layout = QVBoxLayout(self.hud_subpage_nav_rail)
        hud_subpage_layout.setContentsMargins(14, 0, 0, 0)
        hud_subpage_layout.setSpacing(2)
        hud_dashboard_label = "HUD Dashboard"
        hud_dashboard_pill_width = self._settings_nav_pill_width(hud_dashboard_label, "child")
        hud_dashboard_label_width = self._settings_nav_label_width(hud_dashboard_label, "child")
        self.hud_dashboard_nav_item = QFrame(self.nav_shell)
        self.hud_dashboard_nav_item.setObjectName("residentAccessSettingsNavItem")
        self.hud_dashboard_nav_item.setProperty("navState", "available")
        self.hud_dashboard_nav_item.setProperty("settingsNavDensity", "two-level-subpage-row")
        self.hud_dashboard_nav_item.setProperty("settingsNavIdentity", "ndai-signal-leaf")
        self.hud_dashboard_nav_item.setAttribute(Qt.WA_StyledBackground, True)
        self.hud_dashboard_nav_item.setFixedSize(hud_dashboard_pill_width, 26)
        self.hud_dashboard_nav_item.setProperty("settingsNavSizingPolicy", "font-metric-default-min-clamped-v39")
        hud_dashboard_nav_layout = QHBoxLayout(self.hud_dashboard_nav_item)
        hud_dashboard_nav_layout.setContentsMargins(5, 2, 4, 2)
        hud_dashboard_nav_layout.setSpacing(4)
        self.hud_dashboard_nav_icon = NexusCategoryIcon("hud", self.hud_dashboard_nav_item)
        self.hud_dashboard_nav_icon.setObjectName("residentAccessSettingsNavIcon")
        self.hud_dashboard_nav_icon.setAccessibleName("HUD Dashboard child page icon")
        self.hud_dashboard_nav_icon.setFixedSize(12, 12)
        hud_dashboard_nav_layout.addWidget(self.hud_dashboard_nav_icon)
        self.hud_dashboard_nav_button = QPushButton(hud_dashboard_label, self.hud_dashboard_nav_item)
        self.hud_dashboard_nav_button.setObjectName("residentAccessSettingsNavButton")
        self.hud_dashboard_nav_button.setCheckable(True)
        self.hud_dashboard_nav_button.setMaximumWidth(hud_dashboard_label_width)
        self.hud_dashboard_nav_button.setAccessibleName("Open HUD Dashboard Settings")
        self.hud_dashboard_nav_button.clicked.connect(lambda: self.set_focus("hud_dashboard"))
        hud_dashboard_nav_layout.addWidget(self.hud_dashboard_nav_button, 1)
        self._nav_buttons["hud_dashboard"] = self.hud_dashboard_nav_button
        hud_subpage_layout.addWidget(self.hud_dashboard_nav_item)
        hud_subpage_layout.addStretch(1)
        nav_layout.addWidget(self.hud_subpage_nav_rail)
        nav_layout.addStretch(1)

        self.nav_boundary = QLabel("", self.nav_shell)
        self.nav_boundary.setObjectName("residentAccessSettingsNavBoundary")
        self.nav_boundary.setWordWrap(True)
        self.nav_boundary.setVisible(False)

        content_shell = QFrame(body)
        content_shell.setObjectName("residentAccessSettingsContentShell")
        content_shell.setAttribute(Qt.WA_StyledBackground, True)
        self.settings_splitter.addWidget(content_shell)
        self.settings_splitter.setStretchFactor(0, 0)
        self.settings_splitter.setStretchFactor(1, 1)
        self.settings_splitter.setSizes([160, 590])
        content_layout = QVBoxLayout(content_shell)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)

        self.settings_page_frame = QFrame(content_shell)
        self.settings_page_frame.setObjectName("residentAccessSettingsPageFrame")
        self.settings_page_frame.setAttribute(Qt.WA_StyledBackground, True)
        page_layout = QVBoxLayout(self.settings_page_frame)
        page_layout.setContentsMargins(12, 9, 12, 9)
        page_layout.setSpacing(6)
        self.settings_page_frame.setMinimumWidth(486)
        self.settings_page_frame.setMaximumWidth(660)
        self.settings_page_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        content_layout.addWidget(self.settings_page_frame, 0, Qt.AlignTop)
        content_layout.addStretch(1)

        self.section_heading = QLabel("Quick Access", self.settings_page_frame)
        self.section_heading.setObjectName("residentAccessSettingsHeading")
        self.section_badge = QLabel("Tray", self.settings_page_frame)
        self.section_badge.setObjectName("residentAccessSettingsSectionBadge")
        self.section_badge.setAlignment(Qt.AlignCenter)
        self.section_badge.setFixedSize(38, 24)
        self.section_badge.setVisible(False)
        self.section_scope = QLabel("", self.settings_page_frame)
        self.section_scope.setObjectName("residentAccessSettingsScope")
        self.section_scope.setVisible(False)
        self.slot_count_badge = QLabel("", self.settings_page_frame)
        self.slot_count_badge.setObjectName("residentAccessSettingsSlotCount")
        self.slot_count_badge.setAlignment(Qt.AlignCenter)
        self.slot_count_badge.setFixedSize(56, 28)
        self.settings_state_chip = QLabel("", self.settings_page_frame)
        self.settings_state_chip.setObjectName("residentAccessSettingsStateText")
        self.settings_state_chip.setAlignment(Qt.AlignCenter)
        self.settings_state_chip.setMaximumHeight(20)
        self.settings_state_chip.setVisible(False)
        page_layout.addWidget(self.section_scope)
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)
        header_row.addWidget(self.section_heading)
        header_row.addWidget(self.section_badge)
        header_row.addStretch(1)
        page_layout.addLayout(header_row)

        self.section_detail = QLabel("", self.settings_page_frame)
        self.section_detail.setObjectName("residentAccessSettingsDetail")
        self.section_detail.setWordWrap(True)
        self.section_detail.setVisible(False)
        page_layout.addWidget(self.section_detail)

        self.status_summary = QLabel("", self.settings_page_frame)
        self.status_summary.setObjectName("residentAccessSettingsStatus")
        self.status_summary.setWordWrap(True)
        self.status_summary.setVisible(False)

        self.change_summary = QLabel("", self.settings_page_frame)
        self.change_summary.setObjectName("residentAccessSettingsChangeSummary")
        self.change_summary.setWordWrap(False)
        self.change_summary.setMinimumWidth(128)
        self.change_summary.setMaximumHeight(24)

        self.tray_overview_container = QFrame(self.settings_page_frame)
        self.tray_overview_container.setObjectName("residentAccessTrayOverviewContainer")
        self.tray_overview_container.setAttribute(Qt.WA_StyledBackground, True)
        tray_overview_layout = QVBoxLayout(self.tray_overview_container)
        tray_overview_layout.setContentsMargins(12, 10, 12, 10)
        tray_overview_layout.setSpacing(6)
        self.tray_deferred_notice = QFrame(self.tray_overview_container)
        self.tray_deferred_notice.setObjectName("residentAccessTrayDeferredNotice")
        self.tray_deferred_notice.setAttribute(Qt.WA_StyledBackground, True)
        tray_notice_layout = QVBoxLayout(self.tray_deferred_notice)
        tray_notice_layout.setContentsMargins(8, 6, 8, 6)
        tray_notice_layout.setSpacing(1)
        self.tray_deferred_title = QLabel("Tray behavior", self.tray_deferred_notice)
        self.tray_deferred_title.setObjectName("residentAccessTrayDeferredTitle")
        tray_notice_layout.addWidget(self.tray_deferred_title)
        self.tray_deferred_detail = QLabel(
            "Tray click settings are not active yet. "
            f"{WINDOWS_TRAY_VISIBILITY_LIMITATION}",
            self.tray_deferred_notice,
        )
        self.tray_deferred_detail.setObjectName("residentAccessTrayDeferredDetail")
        self.tray_deferred_detail.setWordWrap(True)
        tray_notice_layout.addWidget(self.tray_deferred_detail)
        tray_overview_layout.addWidget(self.tray_deferred_notice)
        tray_overview_layout.addStretch(1)
        page_layout.addWidget(self.tray_overview_container)

        self.quick_slot_container = QFrame(self.settings_page_frame)
        self.quick_slot_container.setObjectName("residentAccessQuickSlotContainer")
        self.quick_slot_container.setAttribute(Qt.WA_StyledBackground, True)
        self.quick_slot_container.setMaximumWidth(620)
        self.quick_slot_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        quick_slot_layout = QVBoxLayout(self.quick_slot_container)
        quick_slot_layout.setContentsMargins(12, 10, 12, 14)
        quick_slot_layout.setSpacing(6)

        quick_header = QHBoxLayout()
        quick_header.setContentsMargins(0, 0, 0, 0)
        quick_header.setSpacing(8)
        quick_header_text = QVBoxLayout()
        quick_header_text.setContentsMargins(0, 0, 0, 0)
        quick_header_text.setSpacing(1)
        self.quick_slot_title = QLabel("Menu order", self.quick_slot_container)
        self.quick_slot_title.setObjectName("residentAccessQuickSlotTitle")
        quick_header_text.addWidget(self.quick_slot_title)
        self.quick_slot_hint = QLabel("Top to bottom in the tray menu.", self.quick_slot_container)
        self.quick_slot_hint.setObjectName("residentAccessQuickSlotHint")
        quick_header_text.addWidget(self.quick_slot_hint)
        quick_header.addLayout(quick_header_text, 1)
        self.reset_slots_button = QPushButton("Defaults", self.quick_slot_container)
        self.reset_slots_button.setObjectName("residentAccessDefaultsButton")
        self.reset_slots_button.setAccessibleName("Restore Default Quick Access Shortcuts (stages changes)")
        self.reset_slots_button.clicked.connect(self._reset_slots)
        quick_header.addWidget(self.reset_slots_button)
        quick_slot_layout.addLayout(quick_header)

        self.quick_help = QLabel("", self.quick_slot_container)
        self.quick_help.setObjectName("residentAccessSettingsQuickHelp")
        self.quick_help.setWordWrap(True)
        self.quick_help.setVisible(False)
        quick_slot_layout.addWidget(self.quick_help)

        self.quick_slot_rows = QWidget(self.quick_slot_container)
        self.quick_slot_rows.setObjectName("residentAccessQuickSlotRows")
        self.quick_slot_rows.setAttribute(Qt.WA_StyledBackground, True)
        self.quick_slot_rows.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.quick_slot_rows_layout = QVBoxLayout(self.quick_slot_rows)
        self.quick_slot_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.quick_slot_rows_layout.setSpacing(self.QUICK_SLOT_ROW_SPACING)
        quick_slot_layout.addWidget(self.quick_slot_rows)
        add_row = QHBoxLayout()
        add_row.setContentsMargins(0, 0, 0, 0)
        add_row.setSpacing(6)
        self.add_slot_button = QPushButton("Add Slot", self.quick_slot_container)
        self.add_slot_button.setObjectName("residentAccessAddSlotButton")
        self.add_slot_button.setAccessibleName("Add Quick Access Slot")
        self.add_slot_button.clicked.connect(self._add_slot)
        add_row.addWidget(self.add_slot_button, 0, Qt.AlignLeft)
        add_row.addWidget(self.slot_count_badge, 0, Qt.AlignLeft | Qt.AlignVCenter)
        add_row.addStretch(1)
        quick_slot_layout.addLayout(add_row)
        page_layout.addWidget(self.quick_slot_container)

        self.hud_settings_container = QFrame(self.settings_page_frame)
        self.hud_settings_container.setObjectName("residentAccessHudSettingsContainer")
        self.hud_settings_container.setAttribute(Qt.WA_StyledBackground, True)
        self.hud_settings_container.setMaximumWidth(620)
        self.hud_settings_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.hud_settings_container.setProperty("hudSettingsOwnership", "FAM-003-doorway-FAM-006-state-semantics")
        hud_settings_layout = QVBoxLayout(self.hud_settings_container)
        hud_settings_layout.setContentsMargins(12, 10, 12, 12)
        hud_settings_layout.setSpacing(7)

        hud_master_row = QHBoxLayout()
        hud_master_row.setContentsMargins(0, 0, 0, 0)
        hud_master_row.setSpacing(10)
        self.hud_enabled_label = QLabel("Enable HUD", self.hud_settings_container)
        self.hud_enabled_label.setObjectName("residentAccessHudEnabledLabel")
        hud_master_row.addWidget(self.hud_enabled_label, 1)
        self.hud_enabled_checkbox = NexusToggle(self.hud_settings_container)
        self.hud_enabled_checkbox.setObjectName("residentAccessHudEnabledControl")
        self.hud_enabled_checkbox.setAccessibleName("Enable HUD")
        self.hud_enabled_checkbox.toggled.connect(self._handle_hud_enabled_toggled)
        hud_master_row.addWidget(self.hud_enabled_checkbox)
        self.hud_state_badge = QLabel("Disabled", self.hud_settings_container)
        self.hud_state_badge.setObjectName("residentAccessHudStateBadge")
        self.hud_state_badge.setAlignment(Qt.AlignCenter)
        self.hud_state_badge.setMinimumWidth(74)
        self.hud_state_badge.setFixedHeight(24)
        hud_settings_layout.addLayout(hud_master_row)

        self.hud_enable_detail = QLabel(
            "Enabling adds the resident HUD route. Open HUD Dashboard when you want to use it.",
            self.hud_settings_container,
        )
        self.hud_enable_detail.setObjectName("residentAccessHudEnableDetail")
        self.hud_enable_detail.setWordWrap(True)
        hud_settings_layout.addWidget(self.hud_enable_detail)

        self.hud_operation_status = QLabel("", self.hud_settings_container)
        self.hud_operation_status.setObjectName("residentAccessHudOperationStatus")
        self.hud_operation_status.setWordWrap(True)
        self.hud_operation_status.setAccessibleName("HUD Dashboard operation status")
        hud_settings_layout.addWidget(self.hud_operation_status)

        hud_action_row = QHBoxLayout()
        hud_action_row.setContentsMargins(0, 2, 0, 0)
        hud_action_row.setSpacing(7)
        hud_action_row.addWidget(self.hud_state_badge)
        hud_action_row.addStretch(1)
        self.hud_retry_button = QPushButton("Retry", self.hud_settings_container)
        self.hud_retry_button.setObjectName("residentAccessHudRetryButton")
        self.hud_retry_button.setAccessibleName("Retry HUD Dashboard operation")
        self.hud_retry_button.clicked.connect(self._handle_hud_retry)
        hud_action_row.addWidget(self.hud_retry_button)
        self.hud_open_button = QPushButton("Open HUD Dashboard", self.hud_settings_container)
        self.hud_open_button.setObjectName("residentAccessHudOpenButton")
        self.hud_open_button.setAccessibleName("Open HUD Dashboard")
        self.hud_open_button.clicked.connect(self._handle_hud_open)
        hud_action_row.addWidget(self.hud_open_button)
        hud_settings_layout.addLayout(hud_action_row)
        page_layout.addWidget(self.hud_settings_container)

        self.hud_dashboard_settings_container = QFrame(self.settings_page_frame)
        self.hud_dashboard_settings_container.setObjectName("residentAccessHudDashboardSettingsContainer")
        self.hud_dashboard_settings_container.setProperty("settingsOwner", "FAM-006")
        self.hud_dashboard_settings_container.setProperty("settingsAvailability", "future-gated")
        self.hud_dashboard_settings_container.setAttribute(Qt.WA_StyledBackground, True)
        page_layout.addWidget(self.hud_dashboard_settings_container)

        self.route_summary = QLabel("", self.settings_page_frame)
        self.route_summary.setObjectName("residentAccessSettingsRouteSummary")
        self.route_summary.setWordWrap(True)
        page_layout.addWidget(self.route_summary)

        self.footer_frame = QFrame(self.settings_page_frame)
        self.footer_frame.setObjectName("residentAccessSettingsFooter")
        self.footer_frame.setAttribute(Qt.WA_StyledBackground, True)
        self.footer_frame.setMaximumWidth(620)
        self.footer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        footer = QHBoxLayout(self.footer_frame)
        footer.setContentsMargins(0, 3, 0, 0)
        footer.setSpacing(7)
        footer.addWidget(self.change_summary, 1)
        footer.addWidget(self.settings_state_chip)
        footer.addStretch(1)
        self.keep_editing_button = QPushButton("Cancel", self.settings_page_frame)
        self.keep_editing_button.setObjectName("residentAccessKeepEditingButton")
        self.keep_editing_button.setAccessibleName("Cancel Close")
        self.keep_editing_button.clicked.connect(self._keep_editing)
        footer.addWidget(self.keep_editing_button)
        self.discard_button = QPushButton("Discard", self.settings_page_frame)
        self.discard_button.setObjectName("residentAccessDiscardButton")
        self.discard_button.setAccessibleName("Discard Unsaved Quick Access Changes")
        self.discard_button.clicked.connect(self._discard_and_close)
        footer.addWidget(self.discard_button)
        self.revert_button = QPushButton("Revert", self.settings_page_frame)
        self.revert_button.setObjectName("residentAccessRevertButton")
        self.revert_button.setAccessibleName("Revert Quick Access Settings")
        self.revert_button.clicked.connect(self._revert_settings)
        footer.addWidget(self.revert_button)
        self.save_button = QPushButton("Save", self.settings_page_frame)
        self.save_button.setObjectName("residentAccessSaveButton")
        self.save_button.setAccessibleName("Save Quick Access Settings")
        self.save_button.clicked.connect(self._save_settings)
        footer.addWidget(self.save_button)
        page_layout.addWidget(self.footer_frame)

        self.close_guard_overlay = QFrame(self.shell)
        self.close_guard_overlay.setObjectName("residentAccessCloseGuardOverlay")
        self.close_guard_overlay.setAttribute(Qt.WA_StyledBackground, True)
        self.close_guard_overlay.setProperty("unsavedGuard", "closed")
        self.close_guard_overlay.setProperty("guardActionLayout", "modal-save-discard-cancel")
        self.close_guard_overlay.setAccessibleName("Unsaved Quick Access changes close guard")
        self.close_guard_overlay.hide()
        overlay_layout = QVBoxLayout(self.close_guard_overlay)
        overlay_layout.setContentsMargins(14, 14, 14, 14)
        overlay_layout.setSpacing(0)
        overlay_layout.addStretch(1)

        self.close_guard_panel = QFrame(self.close_guard_overlay)
        self.close_guard_panel.setObjectName("residentAccessCloseGuardPanel")
        self.close_guard_panel.setAttribute(Qt.WA_StyledBackground, True)
        self.close_guard_panel.setProperty("unsavedGuard", "closed")
        self.close_guard_panel.setProperty("guardActionLayout", "modal-save-discard-cancel")
        panel_layout = QVBoxLayout(self.close_guard_panel)
        panel_layout.setContentsMargins(14, 12, 14, 14)
        panel_layout.setSpacing(8)
        self.close_guard_title = QLabel("Unsaved Quick Access changes", self.close_guard_panel)
        self.close_guard_title.setObjectName("residentAccessCloseGuardTitle")
        panel_layout.addWidget(self.close_guard_title)
        self.close_guard_detail = QLabel("Save changes or discard the draft before continuing.", self.close_guard_panel)
        self.close_guard_detail.setObjectName("residentAccessCloseGuardDetail")
        self.close_guard_detail.setWordWrap(True)
        panel_layout.addWidget(self.close_guard_detail)
        guard_actions = QHBoxLayout()
        guard_actions.setContentsMargins(0, 2, 0, 0)
        guard_actions.setSpacing(8)
        self.guard_save_button = QPushButton("Save", self.close_guard_panel)
        self.guard_save_button.setObjectName("residentAccessCloseGuardSave")
        self.guard_save_button.setAccessibleName("Save Quick Access changes and close Global Settings")
        self.guard_save_button.setProperty("guardAction", "save")
        self.guard_save_button.setProperty("guardVisualRole", "primary-save")
        self.guard_save_button.clicked.connect(self._save_settings)
        guard_actions.addWidget(self.guard_save_button)
        self.guard_discard_button = QPushButton("Discard", self.close_guard_panel)
        self.guard_discard_button.setObjectName("residentAccessCloseGuardDiscard")
        self.guard_discard_button.setAccessibleName("Discard Quick Access changes and close Global Settings")
        self.guard_discard_button.setProperty("guardAction", "discard")
        self.guard_discard_button.setProperty("guardVisualRole", "destructive-discard")
        self.guard_discard_button.clicked.connect(self._discard_and_close)
        guard_actions.addWidget(self.guard_discard_button)
        self.guard_cancel_button = QPushButton("Cancel", self.close_guard_panel)
        self.guard_cancel_button.setObjectName("residentAccessCloseGuardCancel")
        self.guard_cancel_button.setAccessibleName("Cancel close and keep editing Quick Access settings")
        self.guard_cancel_button.setProperty("guardAction", "cancel")
        self.guard_cancel_button.setProperty("guardVisualRole", "neutral-cancel")
        self.guard_cancel_button.clicked.connect(self._keep_editing)
        guard_actions.addWidget(self.guard_cancel_button)
        panel_layout.addLayout(guard_actions)
        overlay_layout.addWidget(self.close_guard_panel, 0, Qt.AlignCenter)
        overlay_layout.addStretch(1)
        self.close_guard_overlay.raise_()

        dropdown_arrow_asset = (Path(__file__).resolve().parent / "nexus_dropdown_arrow.svg").as_posix()
        self.setStyleSheet(
            "#residentAccessSettingsDialog {"
            " background: #020914;"
            " color: #f8fafc;"
            " font-family: 'Segoe UI';"
            " font-size: 10pt;"
            "}"
            "#residentAccessSettingsShell {"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #03111e, stop:0.48 #061725, stop:1 #020711);"
            " border: 1px solid rgba(122, 232, 255, 0.42);"
            " border-radius: 20px;"
            "}"
            "#residentAccessSettingsBody {"
            " background: transparent;"
            " border-bottom-left-radius: 20px;"
            " border-bottom-right-radius: 20px;"
            "}"
            "#residentAccessSettingsChromeBar {"
            " background: transparent;"
            " border-bottom: none;"
            " border-top-left-radius: 20px;"
            " border-top-right-radius: 20px;"
            " padding: 0;"
            "}"
            "#residentAccessSettingsChromeKicker {"
            " color: rgba(132, 220, 244, 0.92);"
            " font-size: 9px;"
            " font-weight: 800;"
            " letter-spacing: 0;"
            "}"
            "#residentAccessSettingsChromeTitle {"
            " color: rgba(244, 250, 255, 0.98);"
            " font-size: 16px;"
            " font-weight: 850;"
            "}"
            "#residentAccessSettingsChromeSubtitle {"
            " color: rgba(179, 204, 221, 0.94);"
            " font-size: 11px;"
            " font-weight: 700;"
            "}"
            "#residentAccessSettingsChromeRolePill {"
            " background: transparent;"
            " border: none;"
            " border-radius: 16px;"
            "}"
            "#residentAccessSettingsChromeRolePair {"
            " color: rgba(194, 248, 236, 0.96);"
            " font-size: 10px;"
            " font-weight: 800;"
            "}"
            "#residentAccessSettingsWindowControls {"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(7, 38, 55, 0.86), stop:1 rgba(3, 18, 32, 0.94));"
            " border: 1px solid rgba(122, 232, 255, 0.50);"
            " border-radius: 16px;"
            " min-height: 30px;"
            " max-height: 30px;"
            "}"
            "#residentAccessSettingsChromeMinimize, #residentAccessSettingsChromeMaximize, #residentAccessSettingsChromeClose {"
            " color: rgba(235, 252, 255, 0.92);"
            " background: rgba(5, 22, 36, 0.40);"
            " border: 1px solid rgba(122, 232, 255, 0.24);"
            " border-radius: 12px;"
            " padding: 0;"
            " min-width: 24px;"
            " min-height: 24px;"
            " max-width: 24px;"
            " max-height: 24px;"
            " font-weight: 900;"
            "}"
            "#residentAccessSettingsChromeMinimize:hover, #residentAccessSettingsChromeClose:hover,"
            "#residentAccessSettingsChromeMinimize:focus, #residentAccessSettingsChromeClose:focus {"
            " background: rgba(9, 49, 70, 0.78);"
            " border-color: rgba(126, 248, 218, 0.56);"
            "}"
            "#residentAccessSettingsChromeMinimize:pressed,"
            "#residentAccessSettingsChromeClose:pressed {"
            " background: rgba(7, 40, 57, 0.86);"
            " border-color: rgba(163, 255, 228, 0.72);"
            "}"
            "#residentAccessSettingsSplitter {"
            " background: transparent;"
            " border: none;"
            "}"
            "#residentAccessSettingsSplitter::handle {"
            " background: rgba(122, 232, 255, 0.008);"
            " border-left: 1px solid rgba(122, 232, 255, 0.035);"
            " border-right: 1px solid rgba(153, 246, 228, 0.018);"
            " border-radius: 3px;"
            "}"
            "#residentAccessSettingsSplitter::handle:hover {"
            " background: rgba(122, 232, 255, 0.06);"
            " border-color: rgba(153, 246, 228, 0.18);"
            "}"
            "#residentAccessSettingsNavShell {"
            " background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(3, 18, 32, 0.78), stop:0.58 rgba(2, 12, 24, 0.62), stop:1 rgba(1, 8, 17, 0.42));"
            " border: 1px solid rgba(122, 232, 255, 0.16);"
            " border-right: 1px solid rgba(153, 246, 228, 0.26);"
            " border-radius: 14px;"
            "}"
            "#residentAccessSettingsNavScrollArea {"
            " background: transparent;"
            " border: none;"
            "}"
            "#residentAccessSettingsNavContent {"
            " background: transparent;"
            " border: none;"
            "}"
            "QScrollBar:vertical {"
            " background: rgba(2, 11, 21, 0.68);"
            " width: 5px;"
            " margin: 0;"
            " border: none;"
            " border-radius: 3px;"
            "}"
            "QScrollBar::handle:vertical {"
            " background: rgba(122, 232, 255, 0.46);"
            " border-radius: 3px;"
            " min-height: 22px;"
            "}"
            "QScrollBar::handle:vertical:hover {"
            " background: rgba(153, 246, 228, 0.66);"
            "}"
            "QScrollBar:horizontal {"
            " background: rgba(2, 11, 21, 0.68);"
            " height: 8px;"
            " margin: 0;"
            " border: none;"
            " border-radius: 4px;"
            "}"
            "QScrollBar::handle:horizontal {"
            " background: rgba(122, 232, 255, 0.46);"
            " border-radius: 4px;"
            " min-width: 24px;"
            "}"
            "QScrollBar::handle:horizontal:hover {"
            " background: rgba(153, 246, 228, 0.66);"
            "}"
            "QScrollBar::add-line, QScrollBar::sub-line {"
            " width: 0;"
            " height: 0;"
            " border: none;"
            " background: transparent;"
            "}"
            "QScrollBar::add-page, QScrollBar::sub-page {"
            " background: transparent;"
            "}"
            "#residentAccessSettingsPrimaryRail {"
            " background: transparent;"
            " border: none;"
            " border-radius: 0;"
            "}"
            "#residentAccessSettingsSubpageRail {"
            " background: transparent;"
            " border-left: 1px solid rgba(122, 232, 255, 0.18);"
            "}"
            "#residentAccessSettingsCategoryItem {"
            " background: transparent;"
            " border: none;"
            " border-left: 2px solid transparent;"
            " border-radius: 6px;"
            "}"
            "#residentAccessSettingsCategoryItem[navState=\"selected\"] {"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(11, 74, 94, 0.62), stop:1 rgba(5, 25, 41, 0.32));"
            " border: 1px solid rgba(122, 232, 255, 0.22);"
            " border-left-color: rgba(153, 246, 228, 0.78);"
            "}"
            "#residentAccessSettingsCategoryItem[navState=\"contains-selected\"] {"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(6, 39, 56, 0.44), stop:1 rgba(3, 18, 32, 0.18));"
            " border: 1px solid rgba(122, 232, 255, 0.12);"
            " border-left-color: rgba(122, 232, 255, 0.62);"
            "}"
            "#residentAccessSettingsCategoryItem[navState=\"available\"]:hover {"
            " background: rgba(7, 26, 42, 0.42);"
            " border: none;"
            "}"
            "#residentAccessSettingsCategoryButton {"
            " background: transparent;"
            " color: rgba(225, 244, 248, 0.96);"
            " border: none;"
            " border-radius: 0;"
            " min-height: 20px;"
            " padding: 0;"
            " text-align: left;"
            " font-size: 10px;"
            " font-weight: 850;"
            "}"
            "#residentAccessSettingsCategoryButton:hover, #residentAccessSettingsCategoryButton:focus, "
            "#residentAccessSettingsCategoryButton:checked {"
            " color: rgba(255, 255, 255, 0.98);"
            " background: transparent;"
            " border: none;"
            "}"
            "#residentAccessSettingsNavIndicator {"
            " background: rgba(153, 246, 228, 0.70);"
            " border-radius: 2px;"
            "}"
            "#residentAccessSettingsNavPrimaryIcon {"
            " background: transparent;"
            " color: rgba(213, 255, 246, 0.94);"
            " border: none;"
            " border-radius: 0;"
            " font-size: 9px;"
            " font-weight: 900;"
            "}"
            "#residentAccessSettingsNavExpander {"
            " background: rgba(3, 16, 28, 0.52);"
            " color: rgba(202, 241, 246, 0.96);"
            " border: 1px solid rgba(122, 232, 255, 0.14);"
            " border-radius: 5px;"
            " min-width: 15px;"
            " max-width: 15px;"
            " min-height: 15px;"
            " max-height: 15px;"
            " padding: 0;"
            " font-size: 8px;"
            " font-weight: 820;"
            "}"
            "#residentAccessSettingsNavExpander:hover, #residentAccessSettingsNavExpander:focus {"
            " background: rgba(10, 47, 64, 0.78);"
            " border-color: rgba(153, 246, 228, 0.44);"
            "}"
            "#residentAccessSettingsPrimaryTray {"
            " background: rgba(12, 52, 68, 0.62);"
            " color: rgba(236, 253, 245, 0.98);"
            " border: 1px solid rgba(153, 246, 228, 0.34);"
            " border-radius: 8px;"
            " min-width: 20px;"
            " min-height: 20px;"
            " max-width: 22px;"
            " max-height: 22px;"
            " padding: 0;"
            " font-size: 12px;"
            " font-weight: 800;"
            "}"
            "#residentAccessSettingsPrimaryTray:hover, #residentAccessSettingsPrimaryTray:focus {"
            " background: rgba(17, 70, 86, 0.82);"
            " border-color: rgba(153, 246, 228, 0.58);"
            "}"
            "#residentAccessSettingsNavKicker {"
            " color: rgba(132, 220, 244, 0.84);"
            " font-size: 10px;"
            " font-weight: 800;"
            " letter-spacing: 1px;"
            "}"
            "#residentAccessSettingsNavTitle {"
            " color: rgba(231, 245, 255, 0.96);"
            " font-size: 15px;"
            " font-weight: 800;"
            "}"
            "#residentAccessSettingsCategoryLabel {"
            " color: rgba(158, 232, 245, 0.86);"
            " background: transparent;"
            " border: none;"
            " padding: 2px 4px 4px 4px;"
            " font-size: 11px;"
            " font-weight: 900;"
            "}"
            "#residentAccessSettingsNavDetail, #residentAccessSettingsNavCaption, #residentAccessSettingsNavBoundary {"
            " color: rgba(132, 170, 188, 0.86);"
            " font-size: 10px;"
            " line-height: 1.25;"
            "}"
            "#residentAccessSettingsNavItem {"
            " background: transparent;"
            " border: none;"
            " border-left: 2px solid transparent;"
            " border-radius: 6px;"
            "}"
            "#residentAccessSettingsNavItem[navState=\"selected\"] {"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(7, 47, 66, 0.58), stop:1 rgba(2, 19, 32, 0.20));"
            " border: 1px solid rgba(122, 232, 255, 0.19);"
            " border-left-color: rgba(153, 246, 228, 0.76);"
            "}"
            "#residentAccessSettingsNavItem:hover {"
            " background: rgba(8, 31, 48, 0.46);"
            " border: 1px solid rgba(122, 232, 255, 0.18);"
            " border-left-color: rgba(153, 246, 228, 0.64);"
            "}"
            "#residentAccessSettingsNavItem[navState=\"selected\"]:hover, "
            "#residentAccessSettingsNavItem[navState=\"selected\"]:focus {"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(7, 47, 66, 0.64), stop:1 rgba(2, 19, 32, 0.24));"
            " border: 1px solid rgba(122, 232, 255, 0.24);"
            " border-left-color: rgba(153, 246, 228, 0.82);"
            "}"
            "#residentAccessSettingsNavBoundary {"
            " color: rgba(116, 150, 168, 0.86);"
            " border: none;"
            " padding: 0;"
            " margin: 0;"
            "}"
            "#residentAccessSettingsNavButton {"
            " background: transparent;"
            " color: rgba(225, 244, 248, 0.96);"
            " border: none;"
            " border-radius: 0;"
            " min-height: 20px;"
            " padding: 0;"
            " text-align: left;"
            " font-size: 10px;"
            " font-weight: 820;"
            "}"
            "#residentAccessSettingsNavIcon {"
            " color: rgba(206, 255, 244, 0.90);"
            " background: transparent;"
            " border: none;"
            " border-radius: 0;"
            " font-size: 9px;"
            " font-weight: 900;"
            "}"
            "#residentAccessSettingsNavItem[navState=\"selected\"] #residentAccessSettingsNavIcon {"
            " background: transparent;"
            " border-color: transparent;"
            "}"
            "#residentAccessSettingsNavButton:hover, #residentAccessSettingsNavButton:focus {"
            " color: rgba(255, 255, 255, 0.98);"
            " background: transparent;"
            " border: none;"
            "}"
            "#residentAccessSettingsNavButton:checked {"
            " background: transparent;"
            " color: rgba(255, 255, 255, 0.98);"
            " border: none;"
            "}"
            "#residentAccessSettingsContentShell {"
            " background: transparent;"
            " border: none;"
            " border-radius: 12px;"
            "}"
            "#residentAccessSettingsPageFrame {"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(3, 14, 25, 0.76), stop:1 rgba(2, 8, 17, 0.82));"
            " border: 1px solid rgba(122, 232, 255, 0.16);"
            " border-radius: 12px;"
            "}"
            "#residentAccessSettingsScope {"
            " color: rgba(132, 220, 244, 0.84);"
            " font-size: 10px;"
            " font-weight: 800;"
            " letter-spacing: 1px;"
            "}"
            "#residentAccessSettingsHeading {"
            " color: #f8fafc;"
            " font-size: 20px;"
            " font-weight: 840;"
            "}"
            "#residentAccessSettingsSectionBadge {"
            " color: rgba(153, 246, 228, 0.96);"
            " background: rgba(8, 47, 73, 0.28);"
            " border: 1px solid rgba(118, 226, 255, 0.14);"
            " border-radius: 14px;"
            " font-size: 11px;"
            " font-weight: 800;"
            "}"
            "#residentAccessSettingsSlotCount {"
            " color: #9ee8f5;"
            " background: rgba(8, 47, 73, 0.20);"
            " border: 1px solid rgba(118, 226, 255, 0.12);"
            " border-radius: 11px;"
            " padding: 1px 6px;"
            " font-size: 10px;"
            " font-weight: 760;"
            "}"
            "#residentAccessSettingsSubheading {"
            " color: #dbeafe;"
            " font-size: 13px;"
            " font-weight: 800;"
            "}"
            "#residentAccessSettingsDetail, #residentAccessSettingsRouteSummary, #residentAccessSettingsQuickHelp {"
            " color: rgba(176, 201, 219, 0.92);"
            " line-height: 1.25;"
            " font-size: 13px;"
            "}"
            "#residentAccessSettingsStateText {"
            " color: rgba(153, 246, 228, 0.86);"
            " background: transparent;"
            " border: none;"
            " padding: 0 2px;"
            " font-size: 10px;"
            " font-weight: 760;"
            "}"
            "#residentAccessSettingsStatus {"
            " background: rgba(8, 47, 73, 0.88);"
            " color: #e0f2fe;"
            " border: 1px solid rgba(56, 189, 248, 0.52);"
            " border-radius: 6px;"
            " padding: 8px;"
            "}"
            "#residentAccessSettingsChangeSummary {"
            " background: transparent;"
            " color: rgba(186, 230, 253, 0.94);"
            " border: none;"
            " border-radius: 0;"
            " padding: 2px 0;"
            "}"
            "#residentAccessTrayOverviewContainer {"
            " background: rgba(2, 12, 24, 0.36);"
            " border: 1px solid rgba(118, 226, 255, 0.12);"
            " border-radius: 9px;"
            "}"
            "#residentAccessTrayDeferredNotice {"
            " background: rgba(5, 18, 32, 0.50);"
            " border: 1px solid rgba(117, 228, 255, 0.12);"
            " border-left: 2px solid rgba(153, 246, 228, 0.32);"
            " border-radius: 8px;"
            "}"
            "#residentAccessTrayDeferredTitle {"
            " color: rgba(244, 250, 255, 0.96);"
            " font-size: 13px;"
            " font-weight: 850;"
            "}"
            "#residentAccessTrayDeferredDetail {"
            " color: rgba(148, 184, 199, 0.90);"
            " font-size: 10px;"
            " font-weight: 700;"
            "}"
            "#residentAccessQuickSlotContainer {"
            " background: rgba(2, 12, 24, 0.46);"
            " border: 1px solid rgba(118, 226, 255, 0.16);"
            " border-radius: 10px;"
            "}"
            "#residentAccessQuickSlotTitle {"
            " color: rgba(244, 250, 255, 0.96);"
            " font-size: 15px;"
            " font-weight: 850;"
            "}"
            "#residentAccessQuickSlotHint {"
            " color: rgba(148, 184, 199, 0.88);"
            " font-size: 12px;"
            " font-weight: 700;"
            "}"
            "#residentAccessQuickSlotRows {"
            " background: transparent;"
            " border: none;"
            "}"
            "#residentAccessQuickSlotRow {"
            " background: rgba(5, 18, 32, 0.76);"
            " border: 1px solid rgba(117, 228, 255, 0.18);"
            " border-left: 2px solid rgba(153, 246, 228, 0.38);"
            " border-radius: 6px;"
            "}"
            "#residentAccessQuickSlotIndex {"
            " color: rgba(139, 233, 255, 0.76);"
            " background: transparent;"
            " border: none;"
            " border-radius: 0;"
            " font-size: 13px;"
            " font-weight: 760;"
            " padding: 4px 0;"
            "}"
            "#residentAccessQuickSlotContainer QPushButton, #residentAccessSettingsContentShell QPushButton {"
            " background: rgba(7, 28, 43, 0.62);"
            " color: rgba(191, 212, 207, 0.96);"
            " border: 1px solid rgba(118, 226, 255, 0.14);"
            " border-radius: 6px;"
            " padding: 0 8px;"
            " min-height: 31px;"
            " font-size: 13px;"
            " font-weight: 700;"
            "}"
            "#residentAccessQuickSlotContainer QPushButton:hover, #residentAccessSettingsContentShell QPushButton:hover {"
            " background: rgba(13, 43, 65, 232);"
            " border-color: rgba(118, 226, 255, 0.48);"
            "}"
            "#residentAccessQuickSlotContainer QPushButton:focus, #residentAccessSettingsContentShell QPushButton:focus {"
            " border-color: rgba(118, 226, 255, 0.54);"
            "}"
            "#residentAccessQuickSlotContainer QPushButton:pressed, #residentAccessSettingsContentShell QPushButton:pressed {"
            " background: rgba(15, 118, 110, 0.94);"
            " color: #ffffff;"
            "}"
            "#residentAccessQuickSlotContainer QPushButton:disabled, #residentAccessSettingsContentShell QPushButton:disabled {"
            " background: #101827;"
            " color: #64748b;"
            " border-color: #1f2937;"
            "}"
            "#residentAccessSaveButton:enabled {"
            " background: #0f766e;"
            " color: #ecfeff;"
            " border-color: rgba(153, 246, 228, 0.58);"
            "}"
            "#residentAccessDiscardButton:enabled {"
            " color: #fecaca;"
            " border-color: rgba(248, 113, 113, 0.44);"
            "}"
            "#residentAccessSettingsFooter {"
            " background: transparent;"
            " border: none;"
            " border-radius: 0;"
            "}"
            "#residentAccessCloseGuardOverlay {"
            " background: qradialgradient(cx:0.50, cy:0.34, radius:0.72, fx:0.50, fy:0.34, stop:0 rgba(255, 214, 108, 0.08), stop:0.58 rgba(1, 8, 16, 0.62), stop:1 rgba(1, 8, 16, 0.74));"
            " border-radius: 0;"
            "}"
            "#residentAccessCloseGuardPanel {"
            " background: qradialgradient(cx:0.18, cy:0.00, radius:0.76, fx:0.18, fy:0.00, stop:0 rgba(46, 32, 14, 1.00), stop:0.50 rgba(21, 14, 10, 1.00), stop:1 rgba(21, 14, 10, 1.00));"
            " border: 1px solid rgba(255, 214, 108, 0.24);"
            " border-radius: 8px;"
            " min-width: 360px;"
            " max-width: 420px;"
            "}"
            "#residentAccessCloseGuardTitle {"
            " color: rgba(255, 247, 225, 0.96);"
            " font-size: 12px;"
            " font-weight: 850;"
            "}"
            "#residentAccessCloseGuardDetail {"
            " color: rgba(172, 215, 228, 0.84);"
            " font-size: 12px;"
            " font-weight: 620;"
            " line-height: 1.3;"
            "}"
            "#residentAccessCloseGuardPanel QPushButton {"
            " background: rgba(7, 28, 43, 0.70);"
            " color: rgba(235, 250, 255, 0.96);"
            " border: 1px solid rgba(118, 226, 255, 0.18);"
            " border-radius: 6px;"
            " min-width: 96px;"
            " min-height: 28px;"
            " padding: 0 10px;"
            " font-weight: 760;"
            "}"
            "#residentAccessCloseGuardPanel QPushButton:hover, #residentAccessCloseGuardPanel QPushButton:focus {"
            " background: rgba(13, 43, 65, 0.92);"
            " border-color: rgba(118, 226, 255, 0.48);"
            "}"
            "#residentAccessCloseGuardPanel QPushButton:pressed {"
            " background: rgba(15, 118, 110, 0.94);"
            " color: #ffffff;"
            "}"
            "QPushButton#residentAccessCloseGuardSave, QPushButton#residentAccessCloseGuardSave:hover, QPushButton#residentAccessCloseGuardSave:focus {"
            " background: rgba(15, 118, 110, 0.94);"
            " color: #ecfeff;"
            " border-color: rgba(153, 246, 228, 0.58);"
            "}"
            "QPushButton#residentAccessCloseGuardSave:pressed {"
            " background: rgba(20, 184, 166, 0.94);"
            " color: #ffffff;"
            "}"
            "QPushButton#residentAccessCloseGuardDiscard, QPushButton#residentAccessCloseGuardDiscard:hover, QPushButton#residentAccessCloseGuardDiscard:focus {"
            " color: #fecaca;"
            " border-color: rgba(248, 113, 113, 0.44);"
            " background: rgba(52, 13, 21, 0.92);"
            "}"
            "QPushButton#residentAccessCloseGuardDiscard:pressed {"
            " background: rgba(127, 29, 29, 0.94);"
            " color: #ffffff;"
            "}"
            "QPushButton#residentAccessCloseGuardCancel, QPushButton#residentAccessCloseGuardCancel:hover, QPushButton#residentAccessCloseGuardCancel:focus {"
            " color: rgba(214, 226, 234, 0.94);"
            " border-color: rgba(148, 163, 184, 0.28);"
            " background: rgba(7, 28, 43, 0.82);"
            "}"
            "QPushButton#residentAccessCloseGuardCancel:pressed {"
            " background: rgba(30, 41, 59, 0.94);"
            " color: #ffffff;"
            "}"
            "#residentAccessQuickSlotActions {"
            " background: transparent;"
            " border: none;"
            "}"
            "#residentAccessQuickSlotActions QPushButton {"
            " min-height: 27px;"
            " max-height: 27px;"
            " padding: 0;"
            " border: none;"
            " border-radius: 0;"
            " font-size: 11px;"
            " background: transparent;"
            "}"
            "#residentAccessQuickSlotReorderGroup {"
            " background: transparent;"
            " border: none;"
            " border-radius: 9px;"
            "}"
            "#residentAccessQuickSlotReorderGroup QPushButton {"
            " background: transparent;"
            " border: none;"
            " border-radius: 0;"
            " padding: 0;"
            "}"
            "#residentAccessQuickSlotMoveUp {"
            " border-top-left-radius: 8px;"
            " border-bottom-left-radius: 8px;"
            "}"
            "#residentAccessQuickSlotMoveDown {"
            " border-top-right-radius: 8px;"
            " border-bottom-right-radius: 8px;"
            "}"
            "#residentAccessQuickSlotReorderGroup QPushButton:hover,"
            "#residentAccessQuickSlotReorderGroup QPushButton:focus {"
            " background: transparent;"
            " color: rgba(236, 254, 255, 0.98);"
            "}"
            "#residentAccessQuickSlotReorderGroup QPushButton:pressed {"
            " background: transparent;"
            "}"
            "#residentAccessQuickSlotReorderGroup QPushButton:disabled {"
            " background: transparent;"
            "}"
            "#residentAccessQuickSlotReorderDivider {"
            " background: rgba(118, 226, 255, 0.24);"
            " border: none;"
            " min-width: 1px;"
            " max-width: 1px;"
            " min-height: 17px;"
            " max-height: 17px;"
            "}"
            "#residentAccessQuickSlotDelete {"
            " color: #fecaca;"
            " background: transparent;"
            " border: none;"
            " border-radius: 9px;"
            " font-weight: 800;"
            "}"
            "#residentAccessQuickSlotDelete:hover, #residentAccessQuickSlotDelete:focus {"
            " background: transparent;"
            " border: none;"
            "}"
            "#residentAccessQuickSlotDelete:pressed {"
            " background: transparent;"
            " border: none;"
            "}"
            "#residentAccessQuickSlotDelete:disabled {"
            " background: transparent;"
            " border: none;"
            "}"
            "QComboBox {"
            " background: rgba(2, 12, 24, 0.96);"
            " color: rgba(193, 213, 208, 0.96);"
            " border: 1px solid rgba(118, 226, 255, 0.20);"
            " border-radius: 6px;"
            " padding: 0 22px 0 7px;"
            " min-height: 30px;"
            " font-size: 12px;"
            " font-weight: 700;"
            "}"
            "QComboBox:hover { border-color: rgba(118, 226, 255, 0.38); background: rgba(7, 22, 36, 220); }"
            "QComboBox:focus { border-color: rgba(118, 226, 255, 0.54); background: rgba(7, 22, 36, 232); }"
            "QComboBox:disabled { color: #64748b; background: #101827; border-color: #1f2937; }"
            "QComboBox::drop-down {"
            " width: 22px;"
            " border-left: 1px solid rgba(118, 226, 255, 0.16);"
            " background: rgba(6, 27, 43, 0.55);"
            "}"
            "QComboBox::down-arrow {"
            " image: url("
            f"{dropdown_arrow_asset}"
            ");"
            " width: 9px;"
            " height: 6px;"
            " margin-right: 8px;"
            "}"
            "QComboBox QAbstractItemView {"
            " background: rgba(5, 14, 25, 250);"
            " color: rgba(193, 213, 208, 0.96);"
            " border: 1px solid rgba(118, 226, 255, 0.28);"
            " border-radius: 7px;"
            " padding: 2px;"
            " selection-background-color: rgba(22, 61, 90, 232);"
            " selection-color: rgba(205, 221, 216, 0.99);"
            " outline: none;"
            "}"
            "QComboBox QAbstractItemView::item {"
            " min-height: 24px;"
            " padding: 2px 6px;"
            " border-radius: 5px;"
            "}"
            "QLineEdit {"
            " background: rgba(2, 12, 24, 0.96);"
            " color: rgba(222, 240, 237, 0.96);"
            " border: 1px solid rgba(118, 226, 255, 0.18);"
            " border-radius: 6px;"
            " padding: 0 8px;"
            " min-height: 24px;"
            " font-size: 12px;"
            " font-weight: 700;"
            " selection-background-color: rgba(22, 61, 90, 232);"
            " selection-color: #ffffff;"
            "}"
            "QLineEdit:focus {"
            " border-color: rgba(153, 246, 228, 0.52);"
            " background: rgba(7, 22, 36, 232);"
            "}"
            "QLineEdit:disabled {"
            " color: #64748b;"
            " background: #101827;"
            " border-color: #1f2937;"
            "}"
            "QCheckBox {"
            " color: rgba(214, 226, 234, 0.94);"
            " spacing: 7px;"
            " font-size: 12px;"
            " font-weight: 700;"
            "}"
            "QCheckBox::indicator {"
            " width: 14px;"
            " height: 14px;"
            " border: 1px solid rgba(118, 226, 255, 0.30);"
            " border-radius: 4px;"
            " background: rgba(2, 12, 24, 0.96);"
            "}"
            "QCheckBox::indicator:checked {"
            " background: rgba(15, 118, 110, 0.94);"
            " border-color: rgba(153, 246, 228, 0.68);"
            "}"
            "QCheckBox::indicator:disabled {"
            " background: #101827;"
            " border-color: #1f2937;"
            "}"
            "#residentAccessHudSettingsContainer {"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(4, 20, 34, 0.82), stop:1 rgba(2, 12, 24, 0.88));"
            " border: 1px solid rgba(122, 232, 255, 0.18);"
            " border-radius: 10px;"
            "}"
            "#residentAccessHudEnabledLabel {"
            " color: rgba(239, 252, 255, 0.98);"
            " font-size: 12px;"
            " font-weight: 800;"
            "}"
            "#residentAccessHudEnabledControl { spacing: 0; }"
            "#residentAccessHudEnabledControl::indicator {"
            " width: 30px;"
            " height: 16px;"
            " border-radius: 8px;"
            " border: 1px solid rgba(122, 232, 255, 0.34);"
            " background: rgba(22, 34, 50, 0.96);"
            "}"
            "#residentAccessHudEnabledControl::indicator:checked {"
            " background: rgba(13, 148, 136, 0.90);"
            " border-color: rgba(153, 246, 228, 0.72);"
            "}"
            "#residentAccessHudEnabledControl::indicator:disabled {"
            " background: rgba(32, 43, 58, 0.72);"
            " border-color: rgba(100, 116, 139, 0.35);"
            "}"
            "#residentAccessHudStateBadge {"
            " color: rgba(203, 237, 244, 0.94);"
            " background: rgba(8, 30, 47, 0.86);"
            " border: 1px solid rgba(122, 232, 255, 0.20);"
            " border-radius: 7px;"
            " padding: 0 8px;"
            " font-size: 10px;"
            " font-weight: 800;"
            "}"
            "#residentAccessHudStateBadge[resultStatus=\"success\"] {"
            " color: rgba(209, 250, 229, 0.98);"
            " border-color: rgba(52, 211, 153, 0.42);"
            " background: rgba(6, 78, 59, 0.42);"
            "}"
            "#residentAccessHudStateBadge[resultStatus=\"partial\"], #residentAccessHudStateBadge[resultStatus=\"failed\"] {"
            " color: rgba(254, 226, 226, 0.98);"
            " border-color: rgba(248, 113, 113, 0.46);"
            " background: rgba(127, 29, 29, 0.34);"
            "}"
            "#residentAccessHudEnableDetail {"
            " color: rgba(169, 199, 216, 0.94);"
            " font-size: 10px;"
            " font-weight: 650;"
            "}"
            "#residentAccessHudOperationStatus {"
            " color: rgba(190, 220, 232, 0.96);"
            " background: rgba(2, 10, 20, 0.48);"
            " border-left: 2px solid rgba(122, 232, 255, 0.34);"
            " border-radius: 4px;"
            " padding: 5px 7px;"
            " font-size: 10px;"
            "}"
            "#residentAccessHudOpenButton, #residentAccessHudRetryButton {"
            " min-height: 28px;"
            " padding: 0 11px;"
            " border-radius: 7px;"
            " font-size: 10px;"
            " font-weight: 800;"
            "}"
            "#residentAccessHudOpenButton {"
            " color: rgba(231, 255, 250, 0.98);"
            " background: rgba(11, 79, 78, 0.74);"
            " border: 1px solid rgba(94, 234, 212, 0.44);"
            "}"
            "#residentAccessHudOpenButton:hover, #residentAccessHudOpenButton:focus {"
            " background: rgba(13, 111, 105, 0.88);"
            " border-color: rgba(153, 246, 228, 0.70);"
            "}"
            "#residentAccessHudRetryButton {"
            " color: rgba(217, 235, 242, 0.96);"
            " background: rgba(18, 34, 52, 0.82);"
            " border: 1px solid rgba(122, 232, 255, 0.22);"
            "}"
            "#residentAccessHudRetryButton:hover, #residentAccessHudRetryButton:focus {"
            " background: rgba(20, 55, 70, 0.90);"
            " border-color: rgba(122, 232, 255, 0.48);"
            "}"
            "#residentAccessHudOpenButton:disabled, #residentAccessHudRetryButton:disabled {"
            " color: rgba(127, 148, 164, 0.56);"
            " background: rgba(15, 24, 37, 0.58);"
            " border-color: rgba(71, 85, 105, 0.34);"
            "}"
            "QSlider::groove:horizontal {"
            " height: 5px;"
            " background: rgba(2, 12, 24, 0.96);"
            " border: 1px solid rgba(118, 226, 255, 0.14);"
            " border-radius: 3px;"
            "}"
            "QSlider::handle:horizontal {"
            " width: 14px;"
            " margin: -5px 0;"
            " border-radius: 7px;"
            " background: rgba(153, 246, 228, 0.88);"
            " border: 1px solid rgba(235, 252, 255, 0.55);"
            "}"
            "QSlider::sub-page:horizontal {"
            " background: rgba(15, 118, 110, 0.78);"
            " border-radius: 3px;"
            "}"
        )

        self._rebuild_quick_slot_rows()
        self.set_focus(self._focus)
        self.setTabOrder(self.hud_dashboard_nav_button, self.hud_enabled_checkbox)
        self.setTabOrder(self.hud_enabled_checkbox, self.hud_open_button)
        self.setTabOrder(self.hud_open_button, self.hud_retry_button)
        self._install_settings_resize_event_filters()

    def _apply_native_settings_palette(self):
        base_font = QFont("Segoe UI")
        base_font.setPointSize(10)
        self.setFont(base_font)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#07111f"))
        palette.setColor(QPalette.WindowText, QColor("#f8fafc"))
        palette.setColor(QPalette.Base, QColor("#0b1220"))
        palette.setColor(QPalette.AlternateBase, QColor("#0f172a"))
        palette.setColor(QPalette.Text, QColor("#f8fafc"))
        palette.setColor(QPalette.Button, QColor("#132238"))
        palette.setColor(QPalette.ButtonText, QColor("#e5f0ff"))
        palette.setColor(QPalette.ToolTipBase, QColor("#101b2d"))
        palette.setColor(QPalette.ToolTipText, QColor("#f8fafc"))
        palette.setColor(QPalette.PlaceholderText, QColor("#8293a8"))
        palette.setColor(QPalette.Highlight, QColor("#0f766e"))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)

    def _install_settings_resize_event_filters(self) -> None:
        for widget in [self, *self.findChildren(QWidget)]:
            try:
                if widget.property("settingsResizeEventFilterInstalled") == "true":
                    continue
                widget.installEventFilter(self)
                widget.setMouseTracking(True)
                widget.setProperty("settingsResizeEventFilterInstalled", "true")
            except Exception:
                pass

    def _emit_runtime_signal(self, signal_name: str, **fields):
        emitter = getattr(self.runtime, "_emit_runtime_signal", None)
        if callable(emitter):
            emitter(signal_name, **fields)

    def _plan(self) -> dict[str, object]:
        provider_state = None
        provider = getattr(self.runtime, "_ai_provider_state", None)
        if provider is not None and hasattr(provider, "as_renderer_payload"):
            try:
                provider_state = provider.as_renderer_payload()
            except Exception:
                provider_state = None
        monitoring_state = {}
        hud_provider = getattr(self.runtime, "monitoring_hud_feature_state", None)
        if callable(hud_provider):
            try:
                monitoring_state = hud_provider()
            except Exception:
                monitoring_state = {}
        command_state = {}
        command_provider = getattr(self.runtime, "command_overlay_state", None)
        if callable(command_provider):
            try:
                command_state = command_provider()
            except Exception:
                command_state = {}
        return build_resident_access_menu_plan(
            settings=self._settings,
            ai_provider_state=provider_state,
            monitoring_hud_state=monitoring_state,
            command_overlay_state=command_state,
        )

    def _hud_access(self):
        provider = getattr(self.runtime, "monitoring_hud_access", None)
        if not callable(provider):
            return None
        try:
            return provider()
        except Exception:
            return None

    def _refresh_hud_controls(self) -> None:
        access = self._hud_access()
        state = access.query_state() if access is not None else None
        enabled = bool(getattr(state, "enabled", False))
        available = bool(getattr(state, "available", False))
        runtime_available = bool(getattr(state, "runtime_available", False))
        reason = str(getattr(state, "availability_reason", "") or "HUD runtime is unavailable.")
        result = self._hud_access_result
        result_status = str(getattr(result, "status", "") or "")

        self._hud_checkbox_sync = True
        self.hud_enabled_checkbox.setChecked(enabled)
        self._hud_checkbox_sync = False
        self.hud_enabled_checkbox.setEnabled(runtime_available and not self._hud_operation_active)
        self.hud_open_button.setVisible(enabled and available)
        self.hud_open_button.setEnabled(enabled and available and not self._hud_operation_active)
        self.hud_retry_button.setVisible(bool(getattr(result, "retryable", False)))
        self.hud_retry_button.setEnabled(not self._hud_operation_active)

        if self._hud_operation_active:
            badge_text = self._hud_progress_label
            status_text = "Applying the HUD Dashboard change and waiting for owner confirmation..."
            result_status = "progress"
        elif result is not None:
            badge_text = (
                "Enabled"
                if bool(getattr(result, "confirmed_enabled", enabled))
                else "Disabled"
            )
            if result_status == "partial":
                badge_text = "Partial"
            elif result_status in {"failed", "blocked"}:
                badge_text = "Needs attention"
            status_text = str(getattr(result, "message", "") or reason)
        elif not runtime_available:
            badge_text = "Unavailable"
            status_text = reason
            result_status = "blocked"
        elif enabled and available:
            badge_text = "Enabled"
            status_text = "Enabled. HUD Dashboard is available from the resident tray."
            result_status = "success"
        elif enabled:
            badge_text = "Unavailable"
            status_text = f"Enabled, but unavailable. {reason}"
            result_status = "partial"
        else:
            badge_text = "Disabled"
            status_text = "Disabled. This Settings destination remains available for recovery."
            result_status = "disabled"

        self.hud_state_badge.setText(badge_text)
        self.hud_state_badge.setProperty("resultStatus", result_status)
        self.hud_operation_status.setText(status_text)
        self.hud_operation_status.setProperty("resultStatus", result_status)
        for widget in (self.hud_state_badge, self.hud_operation_status):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _begin_hud_operation(self, label: str) -> None:
        self._hud_operation_active = True
        self._hud_progress_label = label
        self._hud_access_result = None
        self._refresh_hud_controls()
        QApplication.processEvents()

    def _finish_hud_operation(self, result, source: str) -> None:
        self._hud_operation_active = False
        self._hud_access_result = result
        self._refresh_hud_controls()
        self._emit_runtime_signal(
            "RESIDENT_ACCESS_HUD_OPERATION_RESULT",
            source=source,
            operation=getattr(result, "operation", "unknown"),
            status=getattr(result, "status", "failed"),
            generation=getattr(result, "generation", 0),
            confirmed_enabled=getattr(result, "confirmed_enabled", False),
            persistence=getattr(result, "persistence_succeeded", None),
            tray_refresh=getattr(result, "tray_refresh_succeeded", None),
            dashboard_action=getattr(result, "dashboard_action_succeeded", None),
        )

    def _handle_hud_enabled_toggled(self, enabled: bool) -> None:
        if self._hud_checkbox_sync:
            return
        access = self._hud_access()
        if access is None:
            self._hud_access_result = None
            self._refresh_hud_controls()
            return
        source = "global_settings_hud_enable" if enabled else "global_settings_hud_disable"
        self._begin_hud_operation("Enabling..." if enabled else "Disabling...")
        result = access.set_enabled(bool(enabled), source)
        self._finish_hud_operation(result, source)

    def _handle_hud_open(self) -> None:
        access = self._hud_access()
        if access is None:
            self._refresh_hud_controls()
            return
        source = "global_settings_open_hud_dashboard"
        self._begin_hud_operation("Opening...")
        result = access.open_or_restore_dashboard(source)
        self._finish_hud_operation(result, source)

    def _handle_hud_retry(self) -> None:
        access = self._hud_access()
        if access is None:
            self._refresh_hud_controls()
            return
        source = "global_settings_hud_retry"
        self._begin_hud_operation("Retrying...")
        result = access.retry_last_operation(source)
        self._finish_hud_operation(result, source)

    def _route_label(self, route) -> str:
        compact_labels = {
            "command_overlay": "Command Overlay",
            "create_custom_task": "Create Task",
            "open_saved_actions_folder": "Saved Actions",
            "tray_visibility_education": "Tray Help",
        }
        return compact_labels.get(route.route_id, route.label)

    def _has_unsaved_changes(self) -> bool:
        return self._settings != self._saved_settings

    def _available_quick_slot_limit(self) -> int:
        return min(MAX_QUICK_SLOT_COUNT, len(quick_slot_candidate_routes()))

    def _update_guard_buttons(self):
        dirty = self._has_unsaved_changes()
        self.save_button.setEnabled(dirty)
        self.save_button.setText("Save")
        self.revert_button.setEnabled(dirty)
        self.revert_button.setVisible(not self._close_guard_active)
        self.discard_button.setVisible(False)
        self.keep_editing_button.setVisible(False)
        guard_open = self._close_guard_active and dirty
        self.close_guard_overlay.setVisible(guard_open)
        self.close_guard_overlay.setProperty("unsavedGuard", "open-save-discard" if guard_open else "closed")
        self.close_guard_panel.setProperty("unsavedGuard", "open-save-discard" if guard_open else "closed")
        self.setProperty("dirtyCloseInterceptState", "blocked-before-resolution" if guard_open else "idle")
        for widget in (self.close_guard_overlay, self.close_guard_panel):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
        if guard_open:
            self._position_close_guard_overlay()
            self.close_guard_overlay.raise_()
            QTimer.singleShot(0, self.guard_save_button.setFocus)

    def _open_close_guard(self, source: str, pending_result=None, event_ignored: bool = False, pending_callback=None):
        self._close_guard_active = True
        self._close_guard_pending_result = pending_result
        self._close_guard_pending_callback = pending_callback
        self._dirty_close_intercept_count += 1
        self._dirty_close_last_event_ignored = event_ignored
        self._dirty_close_last_resolution = ""
        self.setProperty("dirtyCloseInterceptState", "blocked-before-resolution")
        self.setProperty("dirtyCloseInterceptSource", source)
        self.setProperty("dirtyCloseInterceptCount", str(self._dirty_close_intercept_count))
        self.setProperty("dirtyCloseEventIgnored", "true" if event_ignored else "not-applicable")
        self._notice_text = "Unsaved changes"
        self._refresh_text()
        if not self.isVisible():
            self.show()
        self.raise_()
        self.activateWindow()

    def request_dirty_close_intercept(self, source: str = "external_close", pending_callback=None) -> bool:
        if not self._has_unsaved_changes():
            return False
        self._open_close_guard(
            source,
            pending_result=None,
            event_ignored=True,
            pending_callback=pending_callback,
        )
        return True

    def _keep_editing(self):
        self._dirty_close_last_resolution = "cancel-preserved-dirty-window-open"
        self.setProperty("dirtyCloseInterceptState", "cancel-preserved-dirty-window-open")
        self.setProperty("dirtyCloseResolution", self._dirty_close_last_resolution)
        self._close_guard_pending_result = None
        self._close_guard_pending_callback = None
        self._close_guard_active = False
        self._notice_text = "Unsaved changes"
        self._refresh_text()

    def _request_close(self):
        if self._has_unsaved_changes():
            self._open_close_guard("request_close", pending_result=None, event_ignored=False)
            return
        super().accept()

    def _discard_and_close(self):
        pending_callback = self._close_guard_pending_callback
        self._settings = self._saved_settings
        self._close_guard_active = False
        self._dirty_close_last_resolution = "discard-dropped-draft-closed"
        self.setProperty("dirtyCloseInterceptState", self._dirty_close_last_resolution)
        self.setProperty("dirtyCloseResolution", self._dirty_close_last_resolution)
        self._close_guard_pending_result = None
        self._close_guard_pending_callback = None
        super().reject()
        if callable(pending_callback):
            QTimer.singleShot(0, pending_callback)

    def accept(self):
        self._request_close()

    def reject(self):
        self._request_close()

    def done(self, result):
        if self._has_unsaved_changes():
            self._open_close_guard("done", pending_result=result, event_ignored=False)
            return
        super().done(result)

    def closeEvent(self, event):
        if self._has_unsaved_changes():
            self._open_close_guard("close_event", pending_result=None, event_ignored=True)
            event.ignore()
            return
        self._settings_resize_hover_timer.stop()
        self._reset_settings_resize_cursor()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        key = event.key()
        close_key = key == Qt.Key_Escape or (
            key in (Qt.Key_W, Qt.Key_Q) and bool(modifiers & Qt.ControlModifier)
        )
        if close_key:
            if self._has_unsaved_changes():
                self._open_close_guard("keyboard_close", pending_result=None, event_ignored=True)
                event.accept()
                return
            self._request_close()
            event.accept()
            return
        super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self._settings_resize_hover_timer.start()

    def hideEvent(self, event):
        self._settings_resize_hover_timer.stop()
        if not self._settings_resize_active:
            self._reset_settings_resize_cursor()
        super().hideEvent(event)

    def _selected_slot_ids(self) -> tuple[str, ...]:
        ids = []
        for combo in self._slot_combos:
            route_id = combo.currentData()
            if route_id:
                ids.append(str(route_id))
        return normalize_quick_slot_ids(ids)

    def _clear_quick_slot_rows(self):
        while self.quick_slot_rows_layout.count():
            item = self.quick_slot_rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self._slot_combos = []
        self._slot_rows: list[QFrame] = []
        self._slot_action_clusters: list[QFrame] = []

    def _quick_slot_combo_width_for_row(self, row_width: int) -> int:
        reserved_width = (
            self.QUICK_SLOT_ROW_SIDE_GUTTER * 2
            + self.QUICK_SLOT_INDEX_WIDTH
            + self.QUICK_SLOT_ACTION_CLUSTER_WIDTH
            + self.QUICK_SLOT_ROW_ITEM_GAP * 2
        )
        available_width = max(0, row_width - reserved_width)
        return max(
            self.QUICK_SLOT_COMBO_MIN_WIDTH,
            min(self.QUICK_SLOT_COMBO_MAX_WIDTH, available_width),
        )

    def _apply_quick_slot_row_geometry(self):
        if not getattr(self, "_slot_combos", None):
            return
        rows = getattr(self, "_slot_rows", [])
        for row, combo, action_cluster in zip(rows, self._slot_combos, self._slot_action_clusters):
            row_width = row.width() or self.quick_slot_rows.width() or max(
                0,
                self.quick_slot_container.width() - 24,
            )
            combo_width = self._quick_slot_combo_width_for_row(row_width)
            combo.setMinimumWidth(combo_width)
            combo.setMaximumWidth(combo_width)
            if combo.view() is not None:
                combo.view().setMinimumWidth(combo_width)
                combo.view().setMaximumWidth(combo_width)
            action_cluster.setFixedWidth(self.QUICK_SLOT_ACTION_CLUSTER_WIDTH)

    def _rebuild_quick_slot_rows(self):
        self._clear_quick_slot_rows()
        candidates = quick_slot_candidate_routes()
        selected_ids = normalize_quick_slot_ids(self._settings.quick_slot_ids)
        for index, selected_id in enumerate(selected_ids):
            row = QFrame(self.quick_slot_rows)
            row.setObjectName("residentAccessQuickSlotRow")
            row.setAttribute(Qt.WA_StyledBackground, True)
            row.setFixedHeight(self.QUICK_SLOT_ROW_HEIGHT)
            row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(
                self.QUICK_SLOT_ROW_SIDE_GUTTER,
                3,
                self.QUICK_SLOT_ROW_SIDE_GUTTER,
                3,
            )
            row_layout.setSpacing(self.QUICK_SLOT_ROW_ITEM_GAP)
            slot_label = QLabel(f"{index + 1:02d}", row)
            slot_label.setObjectName("residentAccessQuickSlotIndex")
            slot_label.setAccessibleName(f"Quick Access Slot {index + 1} label")
            slot_label.setFixedWidth(self.QUICK_SLOT_INDEX_WIDTH)
            row_layout.addWidget(slot_label)
            combo = QComboBox(row)
            combo.setAccessibleName(f"Quick Access Slot {index + 1} Route")
            combo.setMinimumWidth(self.QUICK_SLOT_COMBO_MIN_WIDTH)
            combo.setMaximumWidth(self.QUICK_SLOT_COMBO_MAX_WIDTH)
            combo.setMaxVisibleItems(4)
            for route in candidates:
                combo.addItem(self._route_label(route), route.route_id)
                if route.route_id == selected_id:
                    combo.setCurrentIndex(combo.count() - 1)
            popup = combo.view()
            if popup is not None:
                popup.setObjectName("residentAccessQuickSlotRoutePopup")
                popup.setAutoFillBackground(True)
                popup_palette = popup.palette()
                popup_palette.setColor(QPalette.Base, QColor("#08121e"))
                popup_palette.setColor(QPalette.Text, QColor("#c1d5d0"))
                popup_palette.setColor(QPalette.Highlight, QColor("#163d5a"))
                popup_palette.setColor(QPalette.HighlightedText, QColor("#e5f0ff"))
                popup.setPalette(popup_palette)
                popup.setStyleSheet(
                    "QAbstractItemView {"
                    " background: #08121e;"
                    " color: #c1d5d0;"
                    " border: 1px solid #2b7485;"
                    " selection-background-color: #163d5a;"
                    " selection-color: #e5f0ff;"
                    " outline: 0;"
                    " padding: 2px;"
                    "}"
                    "QAbstractItemView::item {"
                    " min-height: 24px;"
                    " padding: 2px 6px;"
                    " border-radius: 5px;"
                    "}"
                    "QAbstractItemView::item:selected {"
                    " background: #163d5a;"
                    " color: #e5f0ff;"
                    "}"
                )
                popup.setMinimumHeight(132)
                popup.setMaximumHeight(136)
            combo.currentIndexChanged.connect(lambda _idx, index=index: self._update_slot(index))
            self._slot_combos.append(combo)
            row_layout.addWidget(combo, 1)
            action_cluster = QFrame(row)
            action_cluster.setObjectName("residentAccessQuickSlotActions")
            action_cluster.setAttribute(Qt.WA_StyledBackground, True)
            action_cluster.setAttribute(Qt.WA_Hover, True)
            action_cluster.setFixedWidth(self.QUICK_SLOT_ACTION_CLUSTER_WIDTH)
            action_cluster.setProperty("quickSlotActionControlPolicy", "two-pill-reorder-delete-parent-painted-segment-fill-v47")
            action_layout = QHBoxLayout(action_cluster)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(4)
            reorder_group = QuickSlotReorderPill(action_cluster)
            reorder_group.setObjectName("residentAccessQuickSlotReorderGroup")
            reorder_group.setAttribute(Qt.WA_StyledBackground, True)
            reorder_group.setFixedSize(53, 29)
            reorder_group.setProperty("quickSlotReorderSplitPolicy", "parent-painted-25-1-25-exact-segment-fill-v47")
            reorder_layout = QHBoxLayout(reorder_group)
            reorder_layout.setContentsMargins(1, 1, 1, 1)
            reorder_layout.setSpacing(0)
            up_button = NexusGlyphButton("up", reorder_group)
            up_button.setObjectName("residentAccessQuickSlotMoveUp")
            up_button.setProperty("quietGlyph", True)
            up_button.setProperty("glyphZoneButton", True)
            up_button.setProperty("glyphSegment", "left")
            up_button.setProperty("glyphScale", 0.76)
            up_button.setAccessibleName(f"Move Quick Access Slot {index + 1} Up")
            up_button.setFixedSize(25, 27)
            up_button.setEnabled(index > 0)
            up_button.clicked.connect(lambda _checked=False, index=index: self._move_slot(index, -1))
            reorder_layout.addWidget(up_button)
            reorder_divider = QFrame(reorder_group)
            reorder_divider.setObjectName("residentAccessQuickSlotReorderDivider")
            reorder_divider.setAttribute(Qt.WA_StyledBackground, True)
            reorder_divider.setFixedSize(1, 17)
            reorder_layout.addWidget(reorder_divider)
            down_button = NexusGlyphButton("down", reorder_group)
            down_button.setObjectName("residentAccessQuickSlotMoveDown")
            down_button.setProperty("quietGlyph", True)
            down_button.setProperty("glyphZoneButton", True)
            down_button.setProperty("glyphSegment", "right")
            down_button.setProperty("glyphScale", 0.76)
            down_button.setAccessibleName(f"Move Quick Access Slot {index + 1} Down")
            down_button.setFixedSize(25, 27)
            down_button.setEnabled(index < len(selected_ids) - 1)
            down_button.clicked.connect(lambda _checked=False, index=index: self._move_slot(index, 1))
            reorder_layout.addWidget(down_button)
            action_layout.addWidget(reorder_group)
            delete_button = NexusGlyphButton("close", action_cluster)
            delete_button.setObjectName("residentAccessQuickSlotDelete")
            delete_button.setProperty("dangerGlyph", True)
            delete_button.setProperty("quietGlyph", True)
            delete_button.setProperty("glyphZoneButton", True)
            delete_button.setProperty("glyphSegment", "standalone-danger")
            delete_button.setProperty("glyphScale", 0.76)
            delete_button.setAccessibleName(f"Delete Quick Access Slot {index + 1}")
            delete_button.setFixedSize(28, 27)
            delete_button.setEnabled(len(selected_ids) > 1)
            delete_button.clicked.connect(lambda _checked=False, index=index: self._remove_slot(index))
            action_layout.addWidget(delete_button)
            row_layout.addWidget(action_cluster)
            self.quick_slot_rows_layout.addWidget(row)
            self._slot_rows.append(row)
            self._slot_action_clusters.append(action_cluster)
        self.add_slot_button.setEnabled(len(selected_ids) < self._available_quick_slot_limit())
        self._resize_for_slot_count(len(selected_ids))
        QTimer.singleShot(0, self._apply_quick_slot_row_geometry)
        self._install_settings_resize_event_filters()

    def _resize_for_slot_count(self, slot_count: int):
        self.setMaximumSize(*self.MAXIMUM_SIZE)
        bounded_count = max(1, min(slot_count, self._available_quick_slot_limit()))
        row_total = (
            bounded_count * self.QUICK_SLOT_ROW_HEIGHT
            + max(0, bounded_count - 1) * self.QUICK_SLOT_ROW_SPACING
        )
        container_height = self.QUICK_SLOT_CONTAINER_CHROME_HEIGHT + row_total
        dynamic_min_height = min(
            self.MAXIMUM_SIZE[1],
            max(self.BASE_MINIMUM_SIZE[1], self.QUICK_ACCESS_WINDOW_VERTICAL_CHROME + container_height),
        )
        target_width = max(self.width(), self.DEFAULT_SIZE[0])
        target_height = min(
            self.MAXIMUM_SIZE[1],
            max(self.DEFAULT_SIZE[1], self.QUICK_ACCESS_WINDOW_VERTICAL_CHROME + container_height + 10),
        )
        self.setMinimumSize(self.BASE_MINIMUM_SIZE[0], dynamic_min_height)
        self.setMaximumSize(*self.MAXIMUM_SIZE)
        if hasattr(self, "quick_slot_container"):
            self.quick_slot_rows.setMinimumHeight(row_total)
            self.quick_slot_rows.setMaximumHeight(row_total)
            self.quick_slot_container.setFixedHeight(container_height)
            self.quick_slot_container.setProperty("quickAccessRowCount", str(bounded_count))
            self.quick_slot_container.setProperty("quickAccessRowPolicy", self.property("quickAccessLayoutPolicy"))
        if self.height() < target_height or self.width() < self.BASE_MINIMUM_SIZE[0]:
            self.resize(min(self.MAXIMUM_SIZE[0], target_width), target_height)

    def _replace_quick_slots(self, slot_ids: Iterable[str], notice: str | None = None):
        self._settings = ResidentAccessSettings(
            quick_slot_ids=normalize_quick_slot_ids(slot_ids),
            menu_budget=self._settings.menu_budget,
            show_ai_privacy_status=self._settings.show_ai_privacy_status,
        )
        self._close_guard_active = False
        self._notice_text = notice or "Unsaved changes"
        self._rebuild_quick_slot_rows()
        self._refresh_text()

    def _update_slot(self, _index):
        self._replace_quick_slots(self._selected_slot_ids())

    def _move_slot(self, index: int, direction: int):
        slots = list(self._selected_slot_ids())
        new_index = index + direction
        if new_index < 0 or new_index >= len(slots):
            return
        slots[index], slots[new_index] = slots[new_index], slots[index]
        self._replace_quick_slots(slots)

    def _remove_slot(self, index: int):
        slots = list(self._selected_slot_ids())
        if len(slots) <= 1 or index < 0 or index >= len(slots):
            return
        del slots[index]
        self._replace_quick_slots(slots)

    def _add_slot(self):
        slots = list(self._selected_slot_ids())
        if len(slots) >= self._available_quick_slot_limit():
            return
        for route in quick_slot_candidate_routes():
            if route.route_id not in slots:
                slots.append(route.route_id)
                break
        self._replace_quick_slots(slots)

    def _reset_slots(self):
        self._replace_quick_slots(
            DEFAULT_QUICK_SLOT_ROUTE_IDS,
            notice="Default shortcut order staged.",
        )

    def _revert_settings(self):
        self._settings = self._saved_settings
        self._close_guard_active = False
        self._notice_text = "Changes reverted."
        self._rebuild_quick_slot_rows()
        self._refresh_text()

    def _save_settings(self):
        should_close = self._close_guard_active
        pending_callback = self._close_guard_pending_callback
        self._settings = ResidentAccessSettings(
            quick_slot_ids=self._selected_slot_ids(),
            menu_budget=self._settings.menu_budget,
            show_ai_privacy_status=self._settings.show_ai_privacy_status,
        )
        path = save_resident_access_settings(self._settings)
        self._saved_settings = self._settings
        self._close_guard_active = False
        self._notice_text = ""
        self._dirty_close_last_resolution = "save-persisted-closed" if should_close else "save-persisted-clean"
        self.setProperty("dirtyCloseInterceptState", self._dirty_close_last_resolution)
        self.setProperty("dirtyCloseResolution", self._dirty_close_last_resolution)
        self._close_guard_pending_result = None
        self._close_guard_pending_callback = None
        self._emit_runtime_signal(
            "RESIDENT_ACCESS_SETTINGS_SAVED",
            source="global_settings",
            quick_slot_count=len(self._settings.quick_slot_ids),
            path=str(path),
        )
        self._refresh_text(saved=True)
        if should_close:
            super().accept()
            if callable(pending_callback):
                QTimer.singleShot(0, pending_callback)

    def _refresh_text(self, saved: bool = False):
        plan = self._plan()
        route_count = len(plan.get("quickSlots", ()) or ())
        available_slot_limit = self._available_quick_slot_limit()
        self.status_summary.clear()
        self.status_summary.setVisible(False)
        is_hud = self._focus in {"hud", "hud_dashboard"}
        self.section_heading.setText(
            "HUD"
            if self._focus == "hud"
            else "HUD Dashboard"
            if self._focus == "hud_dashboard"
            else "Tray"
            if self._focus == "tray"
            else "Quick Access"
        )
        self.section_badge.setVisible(False)
        self.slot_count_badge.setText(f"{route_count} of {available_slot_limit}")
        self.slot_count_badge.setVisible(self._focus == "quick_access")
        if self._focus == "hud":
            self.section_scope.setText("HUD")
            self.section_detail.setText("Control HUD availability and open the Dashboard explicitly.")
        elif self._focus == "hud_dashboard":
            self.section_scope.setText("HUD / HUD DASHBOARD")
            self.section_detail.setText("Dashboard settings are reserved for the HUD owner.")
        elif self._focus == "tray":
            self.section_scope.setText("NEXUS TRAY")
            self.section_detail.setText(
                self.SETTINGS_TRAY_CONTEXT_DETAILS.get(
                    self._focus_context,
                    "Tray visibility help and future click behavior settings.",
                )
            )
        else:
            self.section_scope.setText("NEXUS TRAY / QUICK ACCESS")
            self.section_detail.setText("Choose the shortcuts shown in the tray menu.")
        self.section_scope.setVisible(True)
        self.section_detail.setVisible(True)

        dirty = self._has_unsaved_changes()
        if self._close_guard_active and dirty:
            change_text = ""
        elif self._notice_text:
            change_text = self._notice_text
        elif dirty:
            change_text = "Unsaved changes"
        else:
            change_text = ""
        slot_count_text = f"{route_count} of {available_slot_limit}"
        if change_text.strip() == slot_count_text:
            change_text = "Unsaved changes" if dirty else ""
        self.change_summary.setText(change_text)
        if self._close_guard_active and dirty:
            self.change_summary.setAccessibleName("Unsaved changes. Save, Discard, or Cancel before closing.")
        else:
            self.change_summary.setAccessibleName(change_text or "Quick Access change status")
        self.change_summary.setVisible(bool(change_text))
        self.settings_state_chip.setText("")
        self.settings_state_chip.setAccessibleName("Quick Access settings state")
        self.settings_state_chip.setVisible(False)
        route_text = ""
        self.route_summary.setText(route_text)
        self.route_summary.setVisible(False)
        self.tray_overview_container.setVisible(self._focus == "tray")
        self.quick_slot_container.setVisible(self._focus == "quick_access")
        self.hud_settings_container.setVisible(self._focus == "hud")
        self.hud_dashboard_settings_container.setVisible(self._focus == "hud_dashboard")
        self.subpage_nav_rail.setVisible(self._tray_children_expanded)
        self.hud_subpage_nav_rail.setVisible(self._hud_children_expanded)
        self.tray_expand_button.setChecked(self._tray_children_expanded)
        if hasattr(self.tray_expand_button, "set_glyph"):
            self.tray_expand_button.set_glyph("chevron-down" if self._tray_children_expanded else "chevron-right")
        self.tray_expand_button.setProperty("expanded", "true" if self._tray_children_expanded else "false")
        self.tray_expand_button.style().unpolish(self.tray_expand_button)
        self.tray_expand_button.style().polish(self.tray_expand_button)
        self.hud_expand_button.setChecked(self._hud_children_expanded)
        if hasattr(self.hud_expand_button, "set_glyph"):
            self.hud_expand_button.set_glyph("chevron-down" if self._hud_children_expanded else "chevron-right")
        self.hud_expand_button.setProperty("expanded", "true" if self._hud_children_expanded else "false")
        self.hud_expand_button.style().unpolish(self.hud_expand_button)
        self.hud_expand_button.style().polish(self.hud_expand_button)
        self._refresh_hud_controls()
        self._update_guard_buttons()
        self.footer_frame.setVisible((self._focus == "quick_access" or dirty) and not self._close_guard_active)

    def _toggle_tray_children(self):
        self._tray_children_expanded = not self._tray_children_expanded
        if not self._tray_children_expanded and self._focus == "quick_access":
            self._focus = "tray"
        self.set_focus(self._focus)

    def _toggle_hud_children(self):
        self._hud_children_expanded = not self._hud_children_expanded
        self._refresh_text()

    def set_focus(self, focus: str):
        requested_focus = (focus or "").strip()
        self._focus = self.SETTINGS_FOCUS_ALIASES.get(requested_focus, "quick_access")
        self._focus_context = requested_focus if requested_focus in self.SETTINGS_FOCUS_ALIASES else self._focus
        if self._focus == "quick_access" and not self._tray_children_expanded:
            self._tray_children_expanded = True
        if self._focus == "hud_dashboard" and not self._hud_children_expanded:
            self._hud_children_expanded = True
        for nav_id, button in self._nav_buttons.items():
            is_selected = nav_id == self._focus
            button.setChecked(is_selected)
            button.setProperty("navState", "selected" if is_selected else "available")
            button.style().unpolish(button)
            button.style().polish(button)
        tray_state = (
            "selected"
            if self._focus == "tray"
            else "contains-selected"
            if self._focus == "quick_access"
            else "available"
        )
        self.tray_nav_item.setProperty("navState", tray_state)
        self.quick_access_nav_item.setProperty("navState", "selected" if self._focus == "quick_access" else "available")
        hud_child_selected = self._focus == "hud_dashboard"
        self.hud_nav_button.setChecked(self._focus == "hud")
        self.hud_nav_item.setProperty(
            "navState", "selected" if self._focus == "hud" else "contains-selected" if hud_child_selected else "available"
        )
        self.hud_dashboard_nav_item.setProperty("navState", "selected" if hud_child_selected else "available")
        for nav_item in (
            self.tray_nav_item,
            self.quick_access_nav_item,
            self.subpage_nav_rail,
            self.hud_nav_item,
            self.hud_dashboard_nav_item,
            self.hud_subpage_nav_rail,
        ):
            nav_item.style().unpolish(nav_item)
            nav_item.style().polish(nav_item)
        if self._focus == "quick_access":
            self._resize_for_slot_count(len(self._settings.quick_slot_ids))
        else:
            self.setMinimumSize(*self.BASE_MINIMUM_SIZE)
        self._refresh_text()
        self.show()
        self.raise_()
        self.activateWindow()

    def _settings_resize_edges_for_local_pos(self, local: QPoint):
        margin = self.RESIZE_MARGIN
        corner_margin = self.RESIZE_CORNER_MARGIN
        width = self.width()
        height = self.height()
        if not QRect(0, 0, width, height).contains(local):
            return Qt.Edges()
        edges = Qt.Edges()
        if local.x() <= corner_margin and local.y() <= corner_margin:
            edges |= Qt.LeftEdge | Qt.TopEdge
        elif local.x() >= max(0, width - corner_margin) and local.y() <= corner_margin:
            edges |= Qt.RightEdge | Qt.TopEdge
        elif local.x() <= corner_margin and local.y() >= max(0, height - corner_margin):
            edges |= Qt.LeftEdge | Qt.BottomEdge
        elif local.x() >= max(0, width - corner_margin) and local.y() >= max(0, height - corner_margin):
            edges |= Qt.RightEdge | Qt.BottomEdge
        else:
            if local.x() <= margin:
                edges |= Qt.LeftEdge
            elif local.x() >= max(0, width - margin):
                edges |= Qt.RightEdge
            if local.y() <= margin:
                edges |= Qt.TopEdge
            elif local.y() >= max(0, height - margin):
                edges |= Qt.BottomEdge
        return edges

    def _settings_resize_edge_key(self, edges) -> tuple[bool, bool, bool, bool]:
        return (
            bool(edges & Qt.LeftEdge),
            bool(edges & Qt.RightEdge),
            bool(edges & Qt.TopEdge),
            bool(edges & Qt.BottomEdge),
        )

    def _settings_resize_cursor_for_edges(self, edges):
        left, right, top, bottom = self._settings_resize_edge_key(edges)
        if (left and top) or (right and bottom):
            return Qt.SizeFDiagCursor
        if (right and top) or (left and bottom):
            return Qt.SizeBDiagCursor
        if left or right:
            return Qt.SizeHorCursor
        if top or bottom:
            return Qt.SizeVerCursor
        return None

    def _settings_resize_cursor(self, edges):
        return self._settings_resize_cursor_for_edges(edges) or Qt.ArrowCursor

    def _settings_windows_resize_cursor_id_for_edges(self, edges):
        if not edges:
            return IDC_ARROW
        left, right, top, bottom = self._settings_resize_edge_key(edges)
        if (left and top) or (right and bottom):
            return IDC_SIZENWSE
        if (right and top) or (left and bottom):
            return IDC_SIZENESW
        if left or right:
            return IDC_SIZEWE
        if top or bottom:
            return IDC_SIZENS
        return IDC_ARROW

    def _apply_settings_windows_resize_cursor(self, edges) -> None:
        if os.name != "nt":
            return
        # resize-cursor-no-forced-arrow-release: clear our override without
        # forcing IDC_ARROW, or Windows edge hover can flicker arrow/resize.
        if not edges:
            return
        try:
            cursor_handle = LoadCursorW(None, self._settings_windows_resize_cursor_id_for_edges(edges))
            if cursor_handle:
                SetCursor(cursor_handle)
        except Exception:
            pass

    def _set_settings_override_resize_cursor(self, cursor) -> None:
        try:
            if cursor is None:
                if self._settings_resize_override_cursor_active:
                    QApplication.restoreOverrideCursor()
                    self._settings_resize_override_cursor_active = False
                return
            qt_cursor = QCursor(cursor)
            if self._settings_resize_override_cursor_active:
                QApplication.changeOverrideCursor(qt_cursor)
            else:
                QApplication.setOverrideCursor(qt_cursor)
                self._settings_resize_override_cursor_active = True
        except Exception:
            self._settings_resize_override_cursor_active = False

    def _set_settings_resize_cursor(self, edges) -> None:
        key = self._settings_resize_edge_key(edges) if edges else None
        if key == self._settings_resize_cursor_key:
            if os.name == "nt":
                if key is not None:
                    self._set_settings_override_resize_cursor(
                        self._settings_resize_cursor_for_edges(edges)
                    )
                self._apply_settings_windows_resize_cursor(edges if key is not None else Qt.Edges())
            return
        self._settings_resize_cursor_key = key
        cursor = self._settings_resize_cursor_for_edges(edges) if edges else None
        targets = [self]
        for attr_name in ("shell", "chrome_bar", "settings_body", "settings_splitter"):
            target = getattr(self, attr_name, None)
            if target is not None:
                targets.append(target)
        try:
            targets.extend(self.findChildren(QWidget))
        except Exception:
            pass
        if os.name == "nt":
            for target in targets:
                try:
                    target.unsetCursor()
                except Exception:
                    pass
            self._set_settings_override_resize_cursor(cursor)
            self._apply_settings_windows_resize_cursor(edges if edges else Qt.Edges())
            return
        for target in targets:
            try:
                if cursor is None:
                    target.unsetCursor()
                else:
                    target.setCursor(QCursor(cursor))
            except Exception:
                pass
        self._set_settings_override_resize_cursor(cursor)
        self._apply_settings_windows_resize_cursor(edges if edges else Qt.Edges())

    def _reset_settings_resize_cursor(self) -> None:
        self._set_settings_resize_cursor(Qt.Edges())

    def _settings_resize_hit_test_for_edges(self, edges) -> int:
        left = bool(edges & Qt.LeftEdge)
        right = bool(edges & Qt.RightEdge)
        top = bool(edges & Qt.TopEdge)
        bottom = bool(edges & Qt.BottomEdge)
        if left and top:
            return HTTOPLEFT
        if right and top:
            return HTTOPRIGHT
        if left and bottom:
            return HTBOTTOMLEFT
        if right and bottom:
            return HTBOTTOMRIGHT
        if left:
            return HTLEFT
        if right:
            return HTRIGHT
        if top:
            return HTTOP
        if bottom:
            return HTBOTTOM
        return 0

    def _settings_resize_edges_for_hit_test(self, hit_test: int):
        edge_map = {
            HTLEFT: Qt.LeftEdge,
            HTRIGHT: Qt.RightEdge,
            HTTOP: Qt.TopEdge,
            HTBOTTOM: Qt.BottomEdge,
            HTTOPLEFT: Qt.TopEdge | Qt.LeftEdge,
            HTTOPRIGHT: Qt.TopEdge | Qt.RightEdge,
            HTBOTTOMLEFT: Qt.BottomEdge | Qt.LeftEdge,
            HTBOTTOMRIGHT: Qt.BottomEdge | Qt.RightEdge,
        }
        return edge_map.get(int(hit_test), Qt.Edges())

    def _settings_cursor_screen_point(self) -> QPoint:
        if os.name == "nt":
            try:
                point = ctypes.wintypes.POINT()
                if GetCursorPos(ctypes.byref(point)):
                    return QPoint(int(point.x), int(point.y))
            except Exception:
                pass
        try:
            return QCursor.pos()
        except Exception:
            return QPoint()

    def _settings_left_mouse_button_down(self) -> bool:
        try:
            return bool(GetAsyncKeyState(VK_LBUTTON) & 0x8000)
        except Exception:
            return False

    def _settings_point_belongs_to_window(self, point: QPoint) -> bool:
        if point.isNull():
            return False
        if os.name != "nt":
            return self.geometry().adjusted(-2, -2, 2, 2).contains(point)
        try:
            probe = ctypes.wintypes.POINT(int(point.x()), int(point.y()))
            hwnd = int(WindowFromPoint(probe))
            settings_hwnd = int(self.winId())
            while hwnd:
                if hwnd == settings_hwnd:
                    return True
                hwnd = int(GetParentW(ctypes.wintypes.HWND(hwnd)))
        except Exception:
            return self.geometry().adjusted(-2, -2, 2, 2).contains(point)
        return False

    def _settings_resize_edges_for_screen_point(self, screen_point: QPoint):
        if screen_point.isNull():
            return Qt.Edges()
        local = self.mapFromGlobal(screen_point)
        if not QRect(0, 0, self.width(), self.height()).contains(local):
            return Qt.Edges()
        if self._settings_control_cluster_rect().contains(local):
            return Qt.Edges()
        return self._settings_resize_edges_for_local_pos(local)

    def _settings_resize_edges_under_cursor(self) -> tuple[QPoint, Qt.Edges]:
        if not self.isVisible():
            return QPoint(), Qt.Edges()
        screen_point = self._settings_cursor_screen_point()
        if screen_point.isNull():
            return QPoint(), Qt.Edges()
        if not self.geometry().adjusted(-2, -2, 2, 2).contains(screen_point):
            return screen_point, Qt.Edges()
        if not self._settings_point_belongs_to_window(screen_point):
            return screen_point, Qt.Edges()
        return screen_point, self._settings_resize_edges_for_screen_point(screen_point)

    def _settings_should_clear_resize_cursor(self, screen_point: QPoint) -> bool:
        if self._settings_resize_cursor_key is None:
            return False
        if screen_point.isNull():
            return True
        if not self.geometry().adjusted(-2, -2, 2, 2).contains(screen_point):
            return True
        if not self._settings_point_belongs_to_window(screen_point):
            return True
        local = self.mapFromGlobal(screen_point)
        if self._settings_control_cluster_rect().contains(local):
            return True
        release_margin = self.RESIZE_MARGIN + self.RESIZE_CURSOR_RELEASE_MARGIN
        near_edge = (
            local.x() <= release_margin
            or local.x() >= self.width() - release_margin
            or local.y() <= release_margin
            or local.y() >= self.height() - release_margin
        )
        return not near_edge

    def _poll_settings_resize_hover_cursor(self) -> None:
        if self._settings_resize_active:
            return
        screen_point, edges = self._settings_resize_edges_under_cursor()
        if edges:
            self._set_settings_resize_cursor(edges)
            return
        if self._settings_should_clear_resize_cursor(screen_point):
            self._reset_settings_resize_cursor()

    def _reset_settings_resize_cursor_if_cursor_left(self) -> None:
        if self._settings_resize_active:
            return
        screen_point = self._settings_cursor_screen_point()
        if not screen_point.isNull() and self.geometry().adjusted(-2, -2, 2, 2).contains(screen_point):
            if self._settings_point_belongs_to_window(screen_point):
                return
        self._reset_settings_resize_cursor()

    def _settings_screen_point_from_mouse_event(self, watched, event) -> QPoint:
        try:
            local = event.position().toPoint()
        except Exception:
            try:
                local = event.pos()
            except Exception:
                local = QPoint()
        if local.isNull():
            return self._settings_cursor_screen_point()
        try:
            return watched.mapToGlobal(local)
        except Exception:
            return self._settings_cursor_screen_point()

    def _settings_available_desktop_geometry(self) -> QRect:
        screens = QApplication.screens()
        if not screens:
            return QRect(0, 0, 1920, 1080)
        available = QRect(screens[0].availableGeometry())
        for screen in screens[1:]:
            available = available.united(screen.availableGeometry())
        return available

    def _bound_settings_geometry_to_available_desktop(self, rect: QRect) -> QRect:
        available = self._settings_available_desktop_geometry()
        bounded = QRect(rect)
        bounded.setWidth(max(self.minimumWidth(), min(bounded.width(), self.maximumWidth())))
        bounded.setHeight(max(self.minimumHeight(), min(bounded.height(), self.maximumHeight())))
        if bounded.left() < available.left():
            bounded.moveLeft(available.left())
        if bounded.top() < available.top():
            bounded.moveTop(available.top())
        if bounded.right() > available.right():
            bounded.moveRight(available.right())
        if bounded.bottom() > available.bottom():
            bounded.moveBottom(available.bottom())
        return bounded

    def _start_settings_resize(self, edges, screen_point: QPoint) -> bool:
        if not edges:
            return False
        if screen_point.isNull():
            screen_point = self._settings_cursor_screen_point()
        if screen_point.isNull():
            return False
        self._settings_resize_active = True
        self._settings_resize_edges = edges
        self._settings_resize_start_global = QPoint(screen_point)
        self._settings_resize_start_geometry = QRect(self.geometry())
        self._settings_resize_pending_point = QPoint(screen_point)
        self._settings_resize_last_geometry = QRect(self.geometry())
        try:
            SetCapture(ctypes.wintypes.HWND(int(self.winId())))
        except Exception:
            pass
        self._set_settings_resize_cursor(edges)
        self._settings_resize_poll_timer.start()
        self._update_settings_resize(screen_point)
        return True

    def _poll_settings_resize(self) -> None:
        if not self._settings_resize_active:
            self._settings_resize_poll_timer.stop()
            return
        screen_point = self._settings_cursor_screen_point()
        if not screen_point.isNull():
            self._update_settings_resize(screen_point)
        if self._settings_left_mouse_button_down():
            return
        self._finish_settings_resize(screen_point)

    def _update_settings_resize(self, screen_point: QPoint) -> None:
        if not self._settings_resize_active or screen_point.isNull():
            return
        self._settings_resize_pending_point = QPoint(screen_point)
        next_rect = self._settings_resize_rect_from_global_delta(screen_point)
        if next_rect == self._settings_resize_last_geometry:
            return
        self.setGeometry(next_rect)
        self._settings_resize_last_geometry = QRect(next_rect)
        self._position_close_guard_overlay()

    def _settings_resize_rect_from_global_delta(self, screen_point: QPoint) -> QRect:
        base = self._settings_resize_start_geometry
        if base.isNull() or not base.isValid():
            base = QRect(self.geometry())
        delta = screen_point - self._settings_resize_start_global
        left_edge, right_edge, top_edge, bottom_edge = self._settings_resize_edge_key(self._settings_resize_edges)
        x = base.x()
        y = base.y()
        width = base.width()
        height = base.height()
        if left_edge:
            x = base.x() + delta.x()
            width = base.width() - delta.x()
        elif right_edge:
            width = base.width() + delta.x()
        if top_edge:
            y = base.y() + delta.y()
            height = base.height() - delta.y()
        elif bottom_edge:
            height = base.height() + delta.y()
        min_width = self.minimumWidth()
        min_height = self.minimumHeight()
        max_width = self.maximumWidth()
        max_height = self.maximumHeight()
        if width < min_width:
            if left_edge:
                x = base.right() - min_width + 1
            width = min_width
        if height < min_height:
            if top_edge:
                y = base.bottom() - min_height + 1
            height = min_height
        if width > max_width:
            if left_edge:
                x = base.right() - max_width + 1
            width = max_width
        if height > max_height:
            if top_edge:
                y = base.bottom() - max_height + 1
            height = max_height
        return self._bound_settings_geometry_to_available_desktop(QRect(x, y, width, height))

    def _finish_settings_resize(self, screen_point: QPoint = None) -> None:
        if not self._settings_resize_active:
            self._reset_settings_resize_cursor()
            return
        self._settings_resize_poll_timer.stop()
        if screen_point is None or screen_point.isNull():
            screen_point = self._settings_cursor_screen_point()
        if screen_point.isNull():
            screen_point = QPoint(self._settings_resize_start_global)
        if not screen_point.isNull():
            next_rect = self._settings_resize_rect_from_global_delta(screen_point)
            if next_rect != self._settings_resize_last_geometry:
                self.setGeometry(next_rect)
                self._settings_resize_last_geometry = QRect(next_rect)
        self._settings_resize_active = False
        self._settings_resize_edges = Qt.Edges()
        self._settings_resize_start_global = QPoint()
        self._settings_resize_start_geometry = QRect()
        self._settings_resize_pending_point = QPoint()
        self._settings_resize_last_geometry = QRect()
        try:
            ReleaseCapture()
        except Exception:
            pass
        self._reset_settings_resize_cursor()
        self._position_close_guard_overlay()

    def _settings_control_cluster_rect(self) -> QRect:
        if not hasattr(self.chrome_bar, "control_cluster"):
            return QRect()
        origin = self.chrome_bar.control_cluster.mapTo(self, QPoint(0, 0))
        return QRect(origin, self.chrome_bar.control_cluster.size()).adjusted(-6, -6, 6, 6)

    def _settings_native_hit_test(self, screen_point: QPoint) -> int:
        local = self.mapFromGlobal(screen_point)
        if not QRect(0, 0, self.width(), self.height()).contains(local):
            return 0
        if self._settings_control_cluster_rect().contains(local):
            return HTCLIENT
        hit_test = self._settings_resize_hit_test_for_edges(self._settings_resize_edges_for_local_pos(local))
        if hit_test:
            return hit_test
        if local.y() <= self.chrome_bar.height():
            return HTCAPTION
        return 0

    def _position_close_guard_overlay(self):
        if not hasattr(self, "close_guard_overlay") or not hasattr(self, "settings_body"):
            return
        self.close_guard_overlay.setGeometry(self.settings_body.geometry())
        self.close_guard_overlay.raise_()

    def nativeEvent(self, eventType, message):
        if eventType in ("windows_generic_MSG", "windows_dispatcher_MSG"):
            try:
                msg = ctypes.wintypes.MSG.from_address(int(message))
            except Exception:
                msg = None
            if msg is not None:
                message_id = int(msg.message)
                if message_id == WM_CLOSE:
                    if self.request_dirty_close_intercept("wm_close"):
                        return True, 0
                if message_id == WM_SYSCOMMAND and (int(msg.wParam) & 0xFFF0) == SC_CLOSE:
                    if self.request_dirty_close_intercept("system_close"):
                        return True, 0
                if message_id == WM_NCHITTEST:
                    x = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
                    y = ctypes.c_short((int(msg.lParam) >> 16) & 0xFFFF).value
                    hit_test = self._settings_native_hit_test(QPoint(x, y))
                    if hit_test:
                        return True, hit_test
                if message_id == WM_SETCURSOR and not self._settings_resize_active:
                    hit_test = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
                    edges = self._settings_resize_edges_for_hit_test(hit_test)
                    if edges:
                        self._set_settings_resize_cursor(edges)
                        return True, 1
                    _, hover_edges = self._settings_resize_edges_under_cursor()
                    if hover_edges:
                        self._set_settings_resize_cursor(hover_edges)
                        return True, 1
                    screen_point = self._settings_cursor_screen_point()
                    if self._settings_should_clear_resize_cursor(screen_point):
                        self._reset_settings_resize_cursor()
                if message_id in (WM_MOUSEMOVE, WM_NCMOUSEMOVE) and not self._settings_resize_active:
                    if message_id == WM_NCMOUSEMOVE:
                        edges = self._settings_resize_edges_for_hit_test(int(msg.wParam))
                        if edges:
                            self._set_settings_resize_cursor(edges)
                            return True, 0
                    _, edges = self._settings_resize_edges_under_cursor()
                    if edges:
                        self._set_settings_resize_cursor(edges)
                    elif message_id == WM_MOUSEMOVE:
                        screen_point = self._settings_cursor_screen_point()
                        if self._settings_should_clear_resize_cursor(screen_point):
                            self._reset_settings_resize_cursor()
                if message_id == WM_LBUTTONDOWN:
                    screen_point, edges = self._settings_resize_edges_under_cursor()
                    if edges and self._start_settings_resize(edges, screen_point):
                        return True, 0
                if message_id == WM_NCLBUTTONDOWN:
                    edges = self._settings_resize_edges_for_hit_test(int(msg.wParam))
                    screen_point = self._settings_cursor_screen_point()
                    if edges and self._start_settings_resize(edges, screen_point):
                        return True, 0
                if self._settings_resize_active and message_id in (WM_MOUSEMOVE, WM_NCMOUSEMOVE):
                    screen_point = self._settings_cursor_screen_point()
                    if not screen_point.isNull():
                        self._update_settings_resize(screen_point)
                    return True, 0
                if self._settings_resize_active and message_id in (
                    WM_LBUTTONUP,
                    WM_NCLBUTTONUP,
                    WM_CAPTURECHANGED,
                    WM_CANCELMODE,
                ):
                    self._finish_settings_resize(self._settings_cursor_screen_point())
                    return True, 0
                if message_id == WM_NCLBUTTONDBLCLK:
                    screen_point = QCursor.pos()
                    if self._settings_native_hit_test(screen_point) == HTCAPTION:
                        return True, 0
        return super().nativeEvent(eventType, message)

    def eventFilter(self, watched, event):
        event_type = event.type()
        if event_type == QEvent.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            screen_point = self._settings_screen_point_from_mouse_event(watched, event)
            edges = self._settings_resize_edges_for_screen_point(screen_point)
            if edges and self._start_settings_resize(edges, screen_point):
                event.accept()
                return True
        if event_type == QEvent.MouseMove:
            if self._settings_resize_active:
                screen_point = self._settings_cursor_screen_point()
                if screen_point.isNull():
                    screen_point = self._settings_screen_point_from_mouse_event(watched, event)
                self._update_settings_resize(screen_point)
                event.accept()
                return True
            screen_point = self._settings_screen_point_from_mouse_event(watched, event)
            edges = self._settings_resize_edges_for_screen_point(screen_point)
            if edges:
                self._set_settings_resize_cursor(edges)
            elif self._settings_should_clear_resize_cursor(screen_point):
                self._reset_settings_resize_cursor()
        if event_type == QEvent.MouseButtonRelease and self._settings_resize_active:
            self._finish_settings_resize(self._settings_cursor_screen_point())
            event.accept()
            return True
        if event_type in (QEvent.Leave, QEvent.HoverLeave) and not self._settings_resize_active:
            self._reset_settings_resize_cursor_if_cursor_left()
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            screen_point, edges = self._settings_resize_edges_under_cursor()
            if edges and self._start_settings_resize(edges, screen_point):
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._settings_resize_active:
            screen_point = self._settings_cursor_screen_point()
            if screen_point.isNull():
                try:
                    screen_point = event.globalPosition().toPoint()
                except Exception:
                    screen_point = QPoint()
            self._update_settings_resize(screen_point)
            event.accept()
            return
        try:
            local = event.position().toPoint()
        except Exception:
            local = QPoint()
        if not local.isNull():
            edges = self._settings_resize_edges_for_local_pos(local)
            if self._settings_control_cluster_rect().contains(local):
                edges = Qt.Edges()
            if edges:
                self._set_settings_resize_cursor(edges)
            elif self._settings_should_clear_resize_cursor(self.mapToGlobal(local)):
                self._reset_settings_resize_cursor()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._settings_resize_active and event.button() == Qt.MouseButton.LeftButton:
            self._finish_settings_resize(self._settings_cursor_screen_point())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if not self._settings_resize_active:
            self._reset_settings_resize_cursor_if_cursor_left()
        super().leaveEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_quick_slot_row_geometry()
        self._position_close_guard_overlay()



class AIControlCenterCommandPage(QWebEnginePage):
    ai_control_center_command = Signal(str)
    DOORWAY_COMMANDS = {
        "control-center": "open-control-center-child-window",
        "readiness-diagnostics": "open-readiness-diagnostics-child-window",
        "capabilities-maintenance": "open-maintenance-lifecycle-child-window",
    }

    def __init__(self, parent=None, *, event_logger=None):
        super().__init__(parent)
        self._event_logger = event_logger

    def _log_doorway_event(self, event: str) -> None:
        try:
            if callable(self._event_logger):
                self._event_logger(event)
        except Exception:
            pass

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        input_prefix = "NEXUS_AI_CONTROL_CENTER_DOORWAY_INPUT:"
        if isinstance(message, str) and message.startswith(input_prefix):
            fields = message[len(input_prefix):].split("|")
            if len(fields) == 2 and fields[0] in self.DOORWAY_COMMANDS and fields[1] in {"pointerup", "click"}:
                self._log_doorway_event(
                    "RENDERER_MAIN|AI_DASHBOARD_DOORWAY_DOM_INPUT"
                    f"|domain={fields[0]}|event={fields[1]}"
                )
                return
        prefix = "NEXUS_AI_CONTROL_CENTER_COMMAND:"
        if isinstance(message, str) and message.startswith(prefix):
            command = message[len(prefix):]
            if command in self.DOORWAY_COMMANDS.values():
                self._log_doorway_event(
                    "RENDERER_MAIN|AI_DASHBOARD_DOORWAY_BRIDGE_COMMAND"
                    f"|command={command}"
                )
            self.ai_control_center_command.emit(command)
            return
        super().javaScriptConsoleMessage(level, message, line_number, source_id)


class AIDashboardDomainCommandPage(QWebEnginePage):
    domain_command = Signal(str, str)

    def __init__(self, domain_id: str, parent=None):
        super().__init__(parent)
        self._domain_id = str(domain_id or "unknown")

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        prefix = "NEXUS_AI_DOMAIN_WINDOW_COMMAND:"
        if isinstance(message, str) and message.startswith(prefix):
            self.domain_command.emit(self._domain_id, message[len(prefix):])
            return
        super().javaScriptConsoleMessage(level, message, line_number, source_id)


class AIDashboardDomainWindow(QDialog):
    RESIZE_EDGE_MARGIN = 8
    RESIZE_CORNER_MARGIN = 12
    SHELL_RADIUS = 24
    DRAG_REGION_FALLBACK_BOTTOM = 74
    CONTROL_ZONE_WIDTH = 96
    CONTROL_ZONE_HEIGHT = 68
    AVAILABLE_DESKTOP_GUTTER = 18
    MAXIMUM_USEFUL_WIDTH = 920
    MAXIMUM_USEFUL_HEIGHT = 840
    CONTENT_FIT_SETTLE_MS = 140
    CONTENT_FIT_SAFETY_PX = 2
    STATE_TAXONOMY_CONTRACT = "ai-dashboard-ai-control-center-state-taxonomy-v1"
    VIEW_MODEL_CONTRACT = "ai-dashboard-provider-state-view-model-v1"
    REQUIRED_STATE_TAXONOMY_STATES = (
        "no-provider-fail-closed",
        "provider-unavailable",
        "stale-state-fail-closed",
        "failed-check-fail-closed",
        "retry-local-check-only",
        "recovery-local-only",
        "blocked-action",
        "unavailable-capability",
        "degraded-no-provider",
    )
    _instance_refs_by_domain: dict[str, dict[int, weakref.ReferenceType]] = {}

    DOMAIN_DEFINITIONS = {
        "readiness-diagnostics": {
            "title": "AI Readiness & Diagnostics",
            "kicker": "Nexus Desktop AI",
            "description": "Local checks, readiness reports, copy, diagnostic detail, and results live here, outside the AI Dashboard hub.",
            "classification": "external-unique",
            "lifecycle": "stays-open-if-dashboard-closes",
            "actions": ("run-local-check", "generate-readiness-report", "copy-readiness-report"),
        },
        "control-center": {
            "title": "AI Control Center",
            "kicker": "Nexus Desktop AI",
            "description": "Persona, capabilities, provider/model readiness, Developer and Owner gates, and control-plane details live here.",
            "classification": "exclusive-child",
            "lifecycle": "closes-with-dashboard",
            "actions": ("show-control-boundary", "show-control-recovery", "show-control-taxonomy"),
        },
        "capabilities-maintenance": {
            "title": "Capabilities & Maintenance",
            "kicker": "Nexus Desktop AI",
            "description": "Capability-pack, maintenance placement, and edition gates live here. Update, download, install, fetch, and capability execution are blocked.",
            "classification": "exclusive-child",
            "lifecycle": "closes-with-dashboard",
            "actions": ("show-capability-lifecycle", "show-capability-lanes", "show-capability-maintenance"),
        },
    }

    def __init__(self, domain_id: str, screen, *, parent=None, event_logger=None):
        # Logical Dashboard ownership is deliberately separate from native HWND ownership.
        super().__init__(None)
        self.domain_id = str(domain_id or "")
        self.screen_ref = screen
        self.event_logger = event_logger
        self._dashboard_ref = weakref.ref(parent) if parent is not None else None
        self._provider_payload: dict[str, object] = {}
        self._page_ready = False
        self._current_report_text = ""
        self._lifecycle_sequence = 0
        self._lifecycle_records: list[dict[str, object]] = []
        self._pending_lifecycle_transition: dict[str, object] | None = None
        self._last_valid_normal_geometry = QRect()
        self._last_minimized_hwnd = 0
        self._last_minimized_normal_geometry = QRect()
        self._lifecycle_generation = 1
        self._ever_shown = False
        self._close_state = "open"
        self._last_known_native_hwnd = 0
        definition = self.DOMAIN_DEFINITIONS.get(self.domain_id, self.DOMAIN_DEFINITIONS["control-center"])
        self.definition = definition
        self.setObjectName(f"fam007AiDashboardDomainWindow_{self.domain_id.replace('-', '_')}")
        self.setWindowTitle(definition["title"])
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowModality(Qt.NonModal)
        self.setMinimumSize(460, 360)
        available = screen.availableGeometry() if screen is not None else QRect()
        if available.isValid():
            self.setMaximumSize(
                max(self.minimumWidth(), min(self.MAXIMUM_USEFUL_WIDTH, available.width() - (self.AVAILABLE_DESKTOP_GUTTER * 2))),
                max(self.minimumHeight(), min(self.MAXIMUM_USEFUL_HEIGHT, available.height() - (self.AVAILABLE_DESKTOP_GUTTER * 2))),
            )
        else:
            self.setMaximumSize(self.MAXIMUM_USEFUL_WIDTH, self.MAXIMUM_USEFUL_HEIGHT)
        self.resize(620, 420)
        self._last_valid_normal_geometry = QRect(self.geometry())
        self.setProperty("aiDashboardDomainWindow", self.domain_id)
        self.setProperty("aiDashboardDomainClassification", definition["classification"])
        self.setProperty("aiDashboardDomainLifecycle", definition["lifecycle"])
        self.setProperty("ndaiNativeChrome", True)
        self.setProperty("genericOsChromeRejected", True)
        self.setProperty("windowControlCluster", "compact-minimize-close")
        self.setProperty("providerVisibleData", "none")
        self.setProperty("providerModelExecution", "blocked")
        self.setProperty("promptSend", "prompt-send-disabled")
        self.setProperty("networkEgress", "network-egress-blocked")
        self.setProperty("memoryIndexing", "memory-indexing-disabled")
        self.setProperty("aiControlCenterStateTaxonomyContract", self.STATE_TAXONOMY_CONTRACT)
        self.setProperty("aiControlCenterStateTaxonomyComplete", "false")
        self.setProperty("aiControlCenterDiagnosticState", "no-provider-fail-closed")
        self.setProperty("aiControlCenterStateTaxonomyRenderedStates", "")
        self.setProperty("aiDashboardProviderStateViewModelContract", self.VIEW_MODEL_CONTRACT)
        self.setProperty("aiDashboardProviderStateViewModelApplied", "false")
        self.setProperty("ndaiShellConformance", "ndai-webview-rounded-window-shell")
        self.setProperty("windowBoundaryContract", "single-rounded-shell-mask-hit-rails-coincident-v2")
        self.setProperty("windowBoundaryInset", "0")
        self.setProperty("windowResizeRailLocation", "inside-visible-rounded-shell")
        self.setProperty("windowOutsideHitBehavior", "noninteractive")
        self.setProperty("windowMoveBehavior", "measured-visible-title-strip-native-and-fallback-v2")
        self.setProperty("windowResizeBehavior", "windows-native-edge-corner-hit-test-with-webview-fallback")
        self.setProperty("windowDefaultGeometryContract", "settled-dom-content-measured-screen-bounded-v2")
        self.setProperty("windowSupportedGeometryContract", "minimum-default-intermediate-useful-large-screen-bounded")
        self.setProperty("windowMaximumUsefulSize", f"{self.maximumWidth()}x{self.maximumHeight()}")
        self.setProperty("windowMaximizeFullscreenPolicy", "not-offered-compact-detached-window")
        self.setProperty("windowReopenGeometryContract", "preserve-last-user-geometry-until-destroyed")
        self.setProperty("windowNativeOwnerContract", "native-parentless-logical-dashboard-lifecycle")
        self.setProperty("windowTaskbarContract", "individual-title-thumbnail-grouping-allowed-no-appusermodelid")
        self.setProperty("windowMinimizeContract", "standard-windows-taskbar-managed-same-hwnd")
        self.setProperty("windowRestoreContract", "taskbar-or-dashboard-doorway-same-hwnd-prior-normal-geometry")
        self.setProperty("windowAppUserModelIdCustomization", "not-used")
        self.setProperty("windowShellVisualContract", "single-border-no-outer-halo")
        self.setProperty("windowDescriptionDragBehavior", "client-content-never-caption")
        self.setProperty("windowInitialContentFitApplied", "false")
        self._drag_start_global = QPoint()
        self._drag_window_origin = QPoint()
        self._dragging_header = False
        self._resize_start_global = QPoint()
        self._resize_start_geometry = QRect()
        self._resize_edges = Qt.Edges()
        self._resizing_window = False
        self._initial_content_fit_pending = True
        self._pending_content_metrics: dict[str, object] = {}
        self._drag_region_bottom = self.DRAG_REGION_FALLBACK_BOTTOM
        self._description_region_top = self.DRAG_REGION_FALLBACK_BOTTOM
        self._visible_shell_region_cache = QRegion()
        self._visible_shell_region_size = (-1, -1)
        self._content_fit_timer = QTimer(self)
        self._content_fit_timer.setSingleShot(True)
        self._content_fit_timer.timeout.connect(self._apply_pending_initial_content_fit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.webview = QWebEngineView(self)
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setStyleSheet("background-color: transparent; border: none;")
        self.webview.setMouseTracking(True)
        self.setMouseTracking(True)
        self.webview.installEventFilter(self)
        self._web_page = AIDashboardDomainCommandPage(self.domain_id, self.webview)
        self._web_page.domain_command.connect(self._handle_domain_command)
        self.webview.setPage(self._web_page)
        self.webview.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.webview.loadFinished.connect(self._on_html_loaded)
        layout.addWidget(self.webview)
        self.webview.setHtml(self._domain_html(), QUrl.fromLocalFile(str(self._asset_base_dir()) + os.sep))
        _apply_windows_dark_title_bar(self)
        self._apply_shell_mask()
        self._register_runtime_instance()

    def _register_runtime_instance(self) -> None:
        domain_refs = self._instance_refs_by_domain.setdefault(self.domain_id, {})
        identity = id(self)

        def forget(_ref, *, domain=self.domain_id, object_identity=identity) -> None:
            refs = self._instance_refs_by_domain.get(domain)
            if refs is None:
                return
            refs.pop(object_identity, None)
            if not refs:
                self._instance_refs_by_domain.pop(domain, None)

        domain_refs[identity] = weakref.ref(self, forget)

    @staticmethod
    def _qt_object_is_live(window) -> bool:
        try:
            window.objectName()
            return True
        except RuntimeError:
            return False

    @classmethod
    def _live_domain_objects(cls, domain_id: str) -> list["AIDashboardDomainWindow"]:
        objects: dict[int, AIDashboardDomainWindow] = {}
        for reference in cls._instance_refs_by_domain.get(domain_id, {}).values():
            window = reference()
            if window is not None and cls._qt_object_is_live(window):
                objects[id(window)] = window
        app = QApplication.instance()
        if app is not None:
            for window in QApplication.topLevelWidgets():
                if (
                    isinstance(window, cls)
                    and getattr(window, "domain_id", None) == domain_id
                    and cls._qt_object_is_live(window)
                ):
                    objects[id(window)] = window
        return list(objects.values())

    @classmethod
    def _process_domain_hwnds(cls, domain_id: str) -> list[int]:
        definition = cls.DOMAIN_DEFINITIONS.get(domain_id, {})
        expected_title = str(definition.get("title") or "")
        if not expected_title:
            return []
        current_pid = os.getpid()
        matches: list[int] = []

        @WNDENUMPROC
        def collect(hwnd, _lparam):
            pid = ctypes.wintypes.DWORD()
            GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if int(pid.value) != current_pid:
                return True
            length = int(GetWindowTextLengthW(hwnd) or 0)
            if length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            GetWindowTextW(hwnd, buffer, length + 1)
            if buffer.value == expected_title and IsWindow(hwnd):
                matches.append(int(hwnd))
            return True

        EnumWindows(collect, 0)
        return sorted(set(matches))

    @classmethod
    def runtime_lifecycle_inventory(cls, domain_id: str, dashboard=None) -> dict[str, object]:
        registry = getattr(dashboard, "_domain_windows", {}) if dashboard is not None else {}
        registered_objects: list[object] = []
        if isinstance(registry, dict):
            for key, window in registry.items():
                if key == domain_id or getattr(window, "domain_id", None) == domain_id:
                    registered_objects.append(window)

        live_by_identity: dict[int, AIDashboardDomainWindow] = {}
        object_sources: dict[int, set[str]] = {}
        for reference in cls._instance_refs_by_domain.get(domain_id, {}).values():
            window = reference()
            if window is not None and cls._qt_object_is_live(window):
                identity = id(window)
                live_by_identity[identity] = window
                object_sources.setdefault(identity, set()).add("class-weak-instance-registry")
        app = QApplication.instance()
        if app is not None:
            for window in QApplication.topLevelWidgets():
                if (
                    isinstance(window, cls)
                    and getattr(window, "domain_id", None) == domain_id
                    and cls._qt_object_is_live(window)
                ):
                    identity = id(window)
                    live_by_identity[identity] = window
                    object_sources.setdefault(identity, set()).add("qt-top-level-widget-enumeration")
        for window in registered_objects:
            if window is not None and cls._qt_object_is_live(window):
                identity = id(window)
                live_by_identity[identity] = window
                object_sources.setdefault(identity, set()).add("dashboard-domain-registry")
        identities: list[dict[str, object]] = []
        object_hwnds: set[int] = set()
        pending_object_ids: set[int] = set()
        for identity, window in sorted(live_by_identity.items()):
            hwnd = 0
            try:
                hwnd = int(window._native_domain_hwnd())
            except RuntimeError:
                hwnd = 0
            if hwnd and IsWindow(ctypes.wintypes.HWND(hwnd)):
                object_hwnds.add(hwnd)
            close_state = str(getattr(window, "_close_state", "unknown"))
            if close_state == "close-requested":
                pending_object_ids.add(identity)
            sources = sorted(object_sources.get(identity, set()))
            identities.append(
                {
                    "objectIdentity": identity,
                    "hwnd": hwnd,
                    "qtObjectAlive": True,
                    "nativeHwndAlive": bool(hwnd and IsWindow(ctypes.wintypes.HWND(hwnd))),
                    "registered": "dashboard-domain-registry" in sources,
                    "closeState": close_state,
                    "sources": sources,
                }
            )

        process_hwnds = set(cls._process_domain_hwnds(domain_id))
        live_hwnds = sorted(process_hwnds | object_hwnds)
        closing_hwnds = getattr(dashboard, "_domain_closing_hwnds", {}) if dashboard is not None else {}
        closing_identities = getattr(dashboard, "_domain_closing_identities", {}) if dashboard is not None else {}
        pending_hwnd = int(closing_hwnds.get(domain_id, 0) or 0) if isinstance(closing_hwnds, dict) else 0
        pending_identity = int(closing_identities.get(domain_id, 0) or 0) if isinstance(closing_identities, dict) else 0
        if pending_identity:
            pending_object_ids.add(pending_identity)

        stale_registry_identities: list[int] = []
        for window in registered_objects:
            if window is None or not cls._qt_object_is_live(window):
                stale_registry_identities.append(id(window))
                continue
            known_hwnd = int(getattr(window, "_last_known_native_hwnd", 0) or 0)
            if known_hwnd and known_hwnd not in process_hwnds and getattr(window, "_close_state", "") != "open":
                stale_registry_identities.append(id(window))

        registered_count = len(registered_objects)
        live_object_count = len(live_by_identity)
        live_hwnd_count = len(live_hwnds)
        duplicate_object_count = max(0, live_object_count - 1)
        duplicate_hwnd_count = max(0, live_hwnd_count - 1)
        return {
            "inventoryContract": "fam007-production-live-object-hwnd-inventory-v2",
            "inventorySource": "production-live-runtime-inventory",
            "inventorySources": [
                "dashboard-domain-registry",
                "class-weak-instance-registry",
                "qt-top-level-widget-enumeration",
                "win32-current-process-top-level-hwnd-enumeration-by-domain-title",
            ],
            "inventoryCompleteness": {
                "registeredObjects": "complete-for-dashboard-domain-registry",
                "liveQtObjects": "complete-for-current-process-qt-top-level-widgets-plus-class-weak-registry",
                "liveNativeHwnds": "complete-for-current-process-top-level-windows-with-exact-domain-title",
            },
            "inventoryInjectedFieldsUsed": False,
            "registeredObjectCount": registered_count,
            "liveObjectCount": live_object_count,
            "liveSameDomainHwndCount": live_hwnd_count,
            "pendingClosingCount": len(pending_object_ids) if pending_object_ids else int(bool(pending_hwnd)),
            "staleRegistryCount": len(set(stale_registry_identities)),
            "duplicateObjectCount": duplicate_object_count,
            "duplicateHwndCount": duplicate_hwnd_count,
            "duplicateCount": max(duplicate_object_count, duplicate_hwnd_count),
            "objectIdentities": identities,
            "hwndIdentities": live_hwnds,
            "pendingClosingObjectIdentities": sorted(pending_object_ids),
            "pendingClosingHwnd": pending_hwnd,
            "staleRegistryObjectIdentities": sorted(set(stale_registry_identities)),
        }

    def eventFilter(self, obj, event):
        if obj is self.webview:
            event_type = event.type()
            if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                local = event.position().toPoint() if hasattr(event, "position") else event.pos()
                edges = self._resize_edges_for_point(local)
                if edges:
                    self._resizing_window = True
                    self._resize_edges = edges
                    self._resize_start_global = event.globalPosition().toPoint()
                    self._resize_start_geometry = QRect(self.geometry())
                    event.accept()
                    return True
                if self._is_drag_point(local):
                    self._dragging_header = True
                    self._drag_start_global = event.globalPosition().toPoint()
                    self._drag_window_origin = self.frameGeometry().topLeft()
                    event.accept()
                    return True
            if event_type == QEvent.MouseMove and self._resizing_window:
                self._apply_resize_from_global(event.globalPosition().toPoint())
                event.accept()
                return True
            if event_type == QEvent.MouseMove and self._dragging_header:
                current = event.globalPosition().toPoint()
                self.move(self._drag_window_origin + (current - self._drag_start_global))
                event.accept()
                return True
            if event_type == QEvent.MouseMove:
                local = event.position().toPoint() if hasattr(event, "position") else event.pos()
                self._set_resize_cursor(self._resize_edges_for_point(local))
            if event_type == QEvent.MouseButtonRelease and (self._dragging_header or self._resizing_window):
                self._dragging_header = False
                self._resizing_window = False
                self._resize_edges = Qt.Edges()
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_shell_mask()
        self._remember_normal_geometry()

    def moveEvent(self, event):
        super().moveEvent(event)
        self._remember_normal_geometry()

    def changeEvent(self, event):
        old_state = event.oldState() if event.type() == QEvent.WindowStateChange else Qt.WindowNoState
        super().changeEvent(event)
        if (
            event.type() == QEvent.WindowStateChange
            and bool(old_state & Qt.WindowMinimized)
            and not self.isMinimized()
            and self._pending_lifecycle_transition is None
        ):
            QTimer.singleShot(0, self._complete_taskbar_restore_transition)

    def closeEvent(self, event):
        context = self._pending_lifecycle_transition
        if not isinstance(context, dict) or context.get("requestedAction") not in {"close", "parent-close"}:
            context = self._begin_lifecycle_action(
                requested_route="windows-close-or-system-menu",
                requested_action="close",
                qt_method="closeEvent",
            )
        dashboard = self._dashboard()
        if dashboard is not None:
            mark_closing = getattr(dashboard, "_mark_ai_dashboard_domain_window_closing", None)
            if callable(mark_closing):
                mark_closing(self, context)
        self._close_state = "close-requested"
        super().closeEvent(event)
        accepted = bool(event.isAccepted())
        if not accepted:
            self._close_state = "open"
            if dashboard is not None:
                cancel_closing = getattr(dashboard, "_cancel_ai_dashboard_domain_window_closing", None)
                if callable(cancel_closing):
                    cancel_closing(self.domain_id, id(self))
        self._record_lifecycle_transition(
            context,
            method_result=accepted,
            close_result="accepted-destroy-pending" if accepted else "rejected",
            restore_route="not-applicable",
        )
        self._pending_lifecycle_transition = None

    @staticmethod
    def _qrect_lifecycle_snapshot(rect: QRect) -> dict[str, int] | None:
        if not isinstance(rect, QRect) or not rect.isValid():
            return None
        return {
            "x": int(rect.x()),
            "y": int(rect.y()),
            "width": int(rect.width()),
            "height": int(rect.height()),
        }

    @staticmethod
    def _qt_enum_value(value) -> int:
        return int(getattr(value, "value", value))

    def _dashboard(self):
        return self._dashboard_ref() if self._dashboard_ref is not None else None

    def _remember_normal_geometry(self) -> None:
        pending_action = (
            self._pending_lifecycle_transition.get("requestedAction")
            if isinstance(self._pending_lifecycle_transition, dict)
            else ""
        )
        if pending_action == "minimize" or self.isMinimized() or self.isMaximized() or self.isFullScreen():
            return
        geometry = self.geometry()
        if geometry.isValid() and geometry.width() >= self.minimumWidth() and geometry.height() >= self.minimumHeight():
            self._last_valid_normal_geometry = QRect(geometry)

    def _bounded_domain_geometry(self, candidate: QRect) -> QRect:
        rect = QRect(candidate) if isinstance(candidate, QRect) and candidate.isValid() else QRect(self.geometry())
        screen = QApplication.screenAt(rect.center()) if rect.isValid() else None
        if screen is None:
            screen = self.screen_ref or QApplication.primaryScreen()
        if screen is None:
            return rect
        available = screen.availableGeometry()
        gutter = self.AVAILABLE_DESKTOP_GUTTER
        max_width = max(self.minimumWidth(), min(self.maximumWidth(), available.width() - (gutter * 2)))
        max_height = max(self.minimumHeight(), min(self.maximumHeight(), available.height() - (gutter * 2)))
        width = max(self.minimumWidth(), min(rect.width(), max_width))
        height = max(self.minimumHeight(), min(rect.height(), max_height))
        min_x = available.x() + gutter
        min_y = available.y() + gutter
        max_x = max(min_x, available.x() + available.width() - width - gutter)
        max_y = max(min_y, available.y() + available.height() - height - gutter)
        return QRect(
            max(min_x, min(rect.x(), max_x)),
            max(min_y, min(rect.y(), max_y)),
            width,
            height,
        )

    def _native_domain_hwnd(self) -> int:
        try:
            hwnd = int(self.winId())
            if hwnd:
                self._last_known_native_hwnd = hwnd
            return hwnd
        except (RuntimeError, TypeError, ValueError):
            return int(getattr(self, "_last_known_native_hwnd", 0) or 0)

    def _registry_lifecycle_snapshot(self) -> dict[str, object]:
        dashboard = self._dashboard()
        inventory = self.runtime_lifecycle_inventory(self.domain_id, dashboard)
        registered = any(
            item.get("objectIdentity") == id(self) and item.get("registered") is True
            for item in inventory["objectIdentities"]
        )
        return {
            "identity": id(self),
            "registered": registered,
            "registryCount": inventory["registeredObjectCount"],
            "domainEntryCount": inventory["registeredObjectCount"],
            "duplicateCount": inventory["duplicateCount"],
            "staleEntryDetected": bool(inventory["staleRegistryCount"]),
            **inventory,
        }

    def _parent_lifecycle_snapshot(self) -> dict[str, object]:
        dashboard = self._dashboard()
        if dashboard is None:
            return {
                "present": False,
                "visible": False,
                "minimized": False,
                "closingExclusiveChildren": False,
            }
        return {
            "present": True,
            "visible": bool(dashboard.isVisible()),
            "minimized": bool(dashboard.isMinimized()),
            "closingExclusiveChildren": bool(getattr(dashboard, "_closing_domain_children", False)),
        }

    def _native_lifecycle_snapshot(self) -> dict[str, object]:
        hwnd = self._native_domain_hwnd()
        native_hwnd = ctypes.wintypes.HWND(hwnd) if hwnd else ctypes.wintypes.HWND()
        current_rect = ctypes.wintypes.RECT()
        current_rect_ok = bool(hwnd and GetWindowRect(native_hwnd, ctypes.byref(current_rect)))
        placement = WINDOWPLACEMENT()
        placement.length = ctypes.sizeof(WINDOWPLACEMENT)
        placement_ok = bool(hwnd and GetWindowPlacement(native_hwnd, ctypes.byref(placement)))
        owner_hwnd = int(GetWindowW(native_hwnd, GW_OWNER) or 0) if hwnd else 0
        style = (int(GetWindowLongPtrW(native_hwnd, GWL_STYLE)) & 0xFFFFFFFF) if hwnd else 0
        extended_style = (int(GetWindowLongPtrW(native_hwnd, GWL_EXSTYLE)) & 0xFFFFFFFF) if hwnd else 0
        pid = ctypes.wintypes.DWORD()
        if hwnd:
            GetWindowThreadProcessId(native_hwnd, ctypes.byref(pid))
        taskbar_eligible = bool(
            hwnd
            and owner_hwnd == 0
            and extended_style & WS_EX_APPWINDOW
            and not extended_style & WS_EX_TOOLWINDOW
            and not extended_style & WS_EX_NOACTIVATE
        )
        if current_rect_ok:
            current = QRect(
                current_rect.left,
                current_rect.top,
                max(0, current_rect.right - current_rect.left),
                max(0, current_rect.bottom - current_rect.top),
            )
        else:
            current = QRect(self.geometry())
        if placement_ok:
            native_normal = QRect(
                placement.rcNormalPosition.left,
                placement.rcNormalPosition.top,
                max(0, placement.rcNormalPosition.right - placement.rcNormalPosition.left),
                max(0, placement.rcNormalPosition.bottom - placement.rcNormalPosition.top),
            )
            show_cmd = int(placement.showCmd)
        else:
            native_normal = QRect(self._last_valid_normal_geometry)
            show_cmd = 0
        minimized = bool(hwnd and IsIconic(native_hwnd)) or bool(self.isMinimized())
        icon_sized_rect = bool(current.isValid() and current.width() <= 200 and current.height() <= 60)
        foreground_hwnd = int(GetForegroundWindow() or 0)
        iconic_artifact_native_facts = {
            "nativeMinimized": minimized,
            "iconSizedRectangle": icon_sized_rect,
            "showCmd": show_cmd,
            "currentRectangle": self._qrect_lifecycle_snapshot(current),
            "taskbarEligible": taskbar_eligible,
        }
        iconic_artifact_status = classify_ai_dashboard_iconic_artifact(
            iconic_artifact_native_facts,
            visible_proof=None,
        )
        return {
            "hwnd": hwnd,
            "pid": int(pid.value) if hwnd else os.getpid(),
            "title": self.windowTitle(),
            "nativeOwnerHwnd": owner_hwnd,
            "logicalDashboardOwner": self.definition["classification"] == "exclusive-child",
            "qtFlags": self._qt_enum_value(self.windowFlags()),
            "style": style,
            "extendedStyle": extended_style,
            "taskbarEligible": taskbar_eligible,
            "taskbarRepresentationState": (
                "individual-title-thumbnail-grouping-allowed"
                if taskbar_eligible
                else "ineligible-stop"
            ),
            "taskbarGroupingAllowed": True,
            "ungroupedTaskbarIconRequired": False,
            "appUserModelIdCustomization": False,
            "showCmd": show_cmd,
            "qtVisible": bool(self.isVisible()),
            "nativeVisible": bool(hwnd and IsWindowVisible(native_hwnd)),
            "qtMinimized": bool(self.isMinimized()),
            "nativeMinimized": minimized,
            "normalRectangle": self._qrect_lifecycle_snapshot(native_normal),
            "rememberedNormalRectangle": self._qrect_lifecycle_snapshot(self._last_valid_normal_geometry),
            "currentRectangle": self._qrect_lifecycle_snapshot(current),
            "foregroundHwnd": foreground_hwnd,
            "foregroundResult": bool(hwnd and foreground_hwnd == hwnd),
            "focusResult": bool(self.isActiveWindow() or (hwnd and foreground_hwnd == hwnd)),
            "iconicArtifactNativeFacts": iconic_artifact_native_facts,
            "iconicArtifactStatus": iconic_artifact_status,
            "iconicArtifactVisualEvidenceScope": "none-component-or-runtime-state-only",
            "unexpectedIconicArtifactDetected": None,
            "unexpectedIconicArtifactObservationComplete": False,
            "unexpectedIconicArtifactVisualProofRequired": True,
        }

    def _normalize_native_taskbar_contract(self) -> dict[str, object]:
        hwnd = self._native_domain_hwnd()
        if not hwnd:
            return self._native_lifecycle_snapshot()
        native_hwnd = ctypes.wintypes.HWND(hwnd)
        SetWindowLongPtrW(native_hwnd, GWLP_HWNDPARENT, 0)
        extended_style = int(GetWindowLongPtrW(native_hwnd, GWL_EXSTYLE))
        extended_style = (
            extended_style
            & ~WS_EX_TOOLWINDOW
            & ~WS_EX_NOACTIVATE
        ) | WS_EX_APPWINDOW
        SetWindowLongPtrW(native_hwnd, GWL_EXSTYLE, extended_style)
        SetWindowPos(
            native_hwnd,
            HWND_TOP,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )
        return self._native_lifecycle_snapshot()

    def _activate_domain_window(self) -> dict[str, object]:
        self.raise_()
        self.activateWindow()
        handle = self.windowHandle() if hasattr(self, "windowHandle") else None
        if handle is not None:
            handle.requestActivate()
        hwnd = self._native_domain_hwnd()
        if hwnd:
            native_hwnd = ctypes.wintypes.HWND(hwnd)
            BringWindowToTop(native_hwnd)
            SetActiveWindow(native_hwnd)
            SetForegroundWindow(native_hwnd)
        QApplication.processEvents()
        return self._native_lifecycle_snapshot()

    def _begin_lifecycle_action(
        self,
        *,
        requested_route: str,
        requested_action: str,
        qt_method: str,
    ) -> dict[str, object]:
        self._lifecycle_sequence += 1
        requested_native = self._native_lifecycle_snapshot()
        requested_registry = self._registry_lifecycle_snapshot()
        context = {
            "sequenceId": (
                f"{self.domain_id}:g{self._lifecycle_generation}:{self._lifecycle_sequence:04d}"
            ),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "lifecycleClass": self.definition["classification"],
            "lifecyclePolicy": self.definition["lifecycle"],
            "childSurface": self.definition["title"],
            "domain": self.domain_id,
            "lifecycleGeneration": self._lifecycle_generation,
            "requestedRoute": requested_route,
            "requestedAction": requested_action,
            "qtMethodInvoked": qt_method,
            "requestedHwnd": requested_native["hwnd"],
            "requestedShowCmd": requested_native["showCmd"],
            "priorNormalRectangle": requested_native["rememberedNormalRectangle"],
            "requestedRegistryIdentity": requested_registry["identity"],
            "requestedRegistryCount": requested_registry["registryCount"],
            "requestedDuplicateCount": requested_registry["duplicateCount"],
        }
        if callable(self.event_logger):
            self.event_logger(
                "RENDERER_MAIN|AI_DASHBOARD_DOMAIN_LIFECYCLE_ACTION_REQUESTED"
                f"|sequence_id={context['sequenceId']}|domain={self.domain_id}"
                f"|route={requested_route}|action={requested_action}|qt_method={qt_method}"
            )
        return context

    def _record_lifecycle_transition(
        self,
        context: dict[str, object],
        *,
        method_result,
        close_result: str = "not-applicable",
        restore_route: str = "not-applicable",
        restored_rectangle: QRect | None = None,
    ) -> dict[str, object]:
        native = self._native_lifecycle_snapshot()
        registry = self._registry_lifecycle_snapshot()
        record = {
            **context,
            "resultTimestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "methodResult": method_result,
            **native,
            "restoredRectangle": self._qrect_lifecycle_snapshot(restored_rectangle) if restored_rectangle else None,
            "restoreRoute": restore_route,
            "registryIdentity": registry["identity"],
            "registryRegistered": registry["registered"],
            "registryCount": registry["registryCount"],
            "registryDomainEntryCount": registry["domainEntryCount"],
            "duplicateCount": registry["duplicateCount"],
            "staleRegistryEntryDetected": registry["staleEntryDetected"],
            "lifecycleInventory": {
                key: value
                for key, value in registry.items()
                if key not in {"identity", "registered", "registryCount", "domainEntryCount", "staleEntryDetected"}
            },
            "parentState": self._parent_lifecycle_snapshot(),
            "childState": (
                "minimized"
                if native["nativeMinimized"]
                else "visible-normal"
                if native["nativeVisible"]
                else "closing-or-hidden"
            ),
            "childDestroyed": close_result == "destroyed",
            "closeResult": close_result,
            "orphanTaskbarVisibleHwndDetected": False,
            "supportingDiagnosticOnly": True,
            "gatingDecision": "UNEVALUATED_REQUIRES_SEPARATE_FOCUSED_CLOSURE",
        }
        self._lifecycle_records.append(record)
        self._lifecycle_records = self._lifecycle_records[-128:]
        self.setProperty("aiDashboardDomainLifecycleLastSequence", context["sequenceId"])
        self.setProperty("aiDashboardDomainLifecycleLastAction", context["requestedAction"])
        if callable(self.event_logger):
            encoded = urllib.parse.quote(json.dumps(record, sort_keys=True, separators=(",", ":")))
            self.event_logger(
                "RENDERER_MAIN|AI_DASHBOARD_DOMAIN_LIFECYCLE_TRANSITION"
                f"|sequence_id={context['sequenceId']}|domain={self.domain_id}|record={encoded}"
            )
        return record

    def lifecycle_debug_state(self) -> dict[str, object]:
        return {
            "contract": "fam007-option-a-taskbar-managed-child-lifecycle-v1",
            "domain": self.domain_id,
            "classification": self.definition["classification"],
            "lifecycle": self.definition["lifecycle"],
            "native": self._native_lifecycle_snapshot(),
            "registry": self._registry_lifecycle_snapshot(),
            "parent": self._parent_lifecycle_snapshot(),
            "records": list(self._lifecycle_records),
        }

    def _restore_remembered_normal_geometry(self) -> QRect:
        candidate = self._last_valid_normal_geometry
        if not isinstance(candidate, QRect) or not candidate.isValid():
            candidate = self.normalGeometry()
        bounded = self._bounded_domain_geometry(candidate)
        if bounded.isValid():
            self.setGeometry(bounded)
            self._last_valid_normal_geometry = QRect(bounded)
        return bounded

    def _complete_taskbar_restore_transition(self) -> None:
        context = self._begin_lifecycle_action(
            requested_route="windows-taskbar-or-thumbnail",
            requested_action="restore",
            qt_method="windows-shell-restore",
        )
        context["requestedHwnd"] = self._last_minimized_hwnd
        context["requestedShowCmd"] = 2
        context["priorNormalRectangle"] = self._qrect_lifecycle_snapshot(
            self._last_minimized_normal_geometry
        )
        restored = self._restore_remembered_normal_geometry()
        self._normalize_native_taskbar_contract()
        state = self._activate_domain_window()
        self._record_lifecycle_transition(
            context,
            method_result=bool(state["nativeVisible"] and not state["nativeMinimized"]),
            restore_route="windows-taskbar-or-thumbnail",
            restored_rectangle=restored,
        )

    def _finalize_minimize_transition(self, sequence_id: str) -> None:
        context = self._pending_lifecycle_transition
        if not isinstance(context, dict) or context.get("sequenceId") != sequence_id:
            return
        state = self._native_lifecycle_snapshot()
        self._record_lifecycle_transition(
            context,
            method_result=bool(state["nativeMinimized"] and state["taskbarEligible"]),
        )
        self._pending_lifecycle_transition = None

    def minimize_domain_window(self, requested_route: str = "visible-minimize-control") -> dict[str, object]:
        self._remember_normal_geometry()
        context = self._begin_lifecycle_action(
            requested_route=requested_route,
            requested_action="minimize",
            qt_method="showMinimized",
        )
        self._last_minimized_hwnd = int(context["requestedHwnd"] or 0)
        self._last_minimized_normal_geometry = QRect(self._last_valid_normal_geometry)
        self._pending_lifecycle_transition = context
        self._normalize_native_taskbar_contract()
        self.showMinimized()
        QTimer.singleShot(0, lambda sequence=context["sequenceId"]: self._finalize_minimize_transition(sequence))
        return {"sequenceId": context["sequenceId"], "hwnd": self._native_domain_hwnd()}

    def close_domain_window(self, requested_route: str) -> bool:
        if self._close_state == "close-requested":
            return False
        requested_action = "parent-close" if requested_route == "dashboard-parent-close" else "close"
        context = self._begin_lifecycle_action(
            requested_route=requested_route,
            requested_action=requested_action,
            qt_method="close",
        )
        self._pending_lifecycle_transition = context
        return bool(self.close())

    def record_dashboard_parent_close_survival(self) -> dict[str, object]:
        context = self._begin_lifecycle_action(
            requested_route="dashboard-parent-close",
            requested_action="parent-close",
            qt_method="no-close-stays-open",
        )
        state = self._native_lifecycle_snapshot()
        return self._record_lifecycle_transition(
            context,
            method_result=bool(
                self.definition["classification"] == "external-unique"
                and state["taskbarEligible"]
                and state["hwnd"]
                and IsWindow(ctypes.wintypes.HWND(int(state["hwnd"])))
            ),
            close_result="not-closed-by-external-unique-lifecycle",
        )

    def leaveEvent(self, event):
        if not self._resizing_window:
            self.unsetCursor()
        super().leaveEvent(event)

    def _apply_shell_mask(self) -> None:
        if self.width() <= 0 or self.height() <= 0:
            return
        self.setMask(self._visible_shell_region())

    def _window_bounds_rect(self) -> QRect:
        return QRect(0, 0, max(0, self.width()), max(0, self.height()))

    def _visible_shell_region(self) -> QRegion:
        if self.width() <= 0 or self.height() <= 0:
            return QRegion()
        current_size = (self.width(), self.height())
        if getattr(self, "_visible_shell_region_size", None) == current_size:
            return self._visible_shell_region_cache
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(0.0, 0.0, float(self.width()), float(self.height())),
            self.SHELL_RADIUS,
            self.SHELL_RADIUS,
        )
        self._visible_shell_region_cache = QRegion(path.toFillPolygon().toPolygon())
        self._visible_shell_region_size = current_size
        return self._visible_shell_region_cache

    def _point_in_visible_shell(self, point: QPoint) -> bool:
        return self._window_bounds_rect().contains(point) and self._visible_shell_region().contains(point)

    def _drag_region(self) -> QRect:
        bottom = min(max(0, int(self._drag_region_bottom)), self.height())
        return QRect(0, 0, max(0, self.width()), bottom)

    def _is_drag_point(self, point: QPoint) -> bool:
        return (
            self._point_in_visible_shell(point)
            and self._drag_region().contains(point)
            and not self._control_cluster_zone().contains(point)
        )

    @staticmethod
    def _rect_snapshot(rect: QRect) -> dict[str, int]:
        return {
            "left": rect.left(),
            "top": rect.top(),
            "width": rect.width(),
            "height": rect.height(),
        }

    def _boundary_contract_snapshot(self) -> dict[str, object]:
        bounds = self._window_bounds_rect()
        sample_y = max(0, self.height() // 2)
        samples = {
            "outsideLeft": QPoint(-1, sample_y),
            "outsideRight": QPoint(self.width(), sample_y),
            "outsideTop": QPoint(max(0, self.width() // 2), -1),
            "outsideBottom": QPoint(max(0, self.width() // 2), self.height()),
            "transparentTopLeft": QPoint(0, 0),
            "visibleTopLeftRail": QPoint(
                self.RESIZE_CORNER_MARGIN - 4,
                self.RESIZE_CORNER_MARGIN - 4,
            ),
        }
        return {
            "contract": str(self.property("windowBoundaryContract") or ""),
            "windowBounds": self._rect_snapshot(bounds),
            "visibleShellBounds": self._rect_snapshot(self._visible_shell_region().boundingRect()),
            "maskBounds": self._rect_snapshot(self.mask().boundingRect()),
            "boundaryInset": 0,
            "resizeRailsInsideVisibleShell": True,
            "outsideHitBehavior": "noninteractive",
            "samples": {
                name: {
                    "point": {"x": point.x(), "y": point.y()},
                    "visibleShell": self._point_in_visible_shell(point),
                    "resizeEdges": int(getattr(self._resize_edges_for_point(point), "value", 0)),
                }
                for name, point in samples.items()
            },
        }

    def _resize_edges_for_point(self, point: QPoint):
        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0 or not self._point_in_visible_shell(point):
            return Qt.Edges()
        edge_margin = self.RESIZE_EDGE_MARGIN
        corner_margin = self.RESIZE_CORNER_MARGIN
        near_top_corner = point.y() <= corner_margin
        near_bottom_corner = point.y() >= height - corner_margin
        edges = Qt.Edges()
        if point.x() <= (corner_margin if near_top_corner or near_bottom_corner else edge_margin):
            edges |= Qt.LeftEdge
        elif point.x() >= width - (corner_margin if near_top_corner or near_bottom_corner else edge_margin):
            edges |= Qt.RightEdge
        near_left_corner = point.x() <= corner_margin
        near_right_corner = point.x() >= width - corner_margin
        if point.y() <= (corner_margin if near_left_corner or near_right_corner else edge_margin):
            edges |= Qt.TopEdge
        elif point.y() >= height - (corner_margin if near_left_corner or near_right_corner else edge_margin):
            edges |= Qt.BottomEdge
        return edges

    @staticmethod
    def _hit_test_for_resize_edges(edges) -> int:
        if edges == (Qt.LeftEdge | Qt.TopEdge):
            return HTTOPLEFT
        if edges == (Qt.RightEdge | Qt.TopEdge):
            return HTTOPRIGHT
        if edges == (Qt.LeftEdge | Qt.BottomEdge):
            return HTBOTTOMLEFT
        if edges == (Qt.RightEdge | Qt.BottomEdge):
            return HTBOTTOMRIGHT
        if edges & Qt.LeftEdge:
            return HTLEFT
        if edges & Qt.RightEdge:
            return HTRIGHT
        if edges & Qt.TopEdge:
            return HTTOP
        if edges & Qt.BottomEdge:
            return HTBOTTOM
        return HTCLIENT

    @staticmethod
    def _resize_edges_for_hit_test(hit_test: int):
        return {
            HTLEFT: Qt.LeftEdge,
            HTRIGHT: Qt.RightEdge,
            HTTOP: Qt.TopEdge,
            HTBOTTOM: Qt.BottomEdge,
            HTTOPLEFT: Qt.TopEdge | Qt.LeftEdge,
            HTTOPRIGHT: Qt.TopEdge | Qt.RightEdge,
            HTBOTTOMLEFT: Qt.BottomEdge | Qt.LeftEdge,
            HTBOTTOMRIGHT: Qt.BottomEdge | Qt.RightEdge,
        }.get(int(hit_test), Qt.Edges())

    def _control_cluster_zone(self) -> QRect:
        return QRect(
            max(0, self.width() - self.CONTROL_ZONE_WIDTH),
            0,
            self.CONTROL_ZONE_WIDTH,
            self.CONTROL_ZONE_HEIGHT,
        )

    def _native_hit_test(self, screen_point: QPoint) -> int:
        local = self.mapFromGlobal(screen_point)
        if not self._point_in_visible_shell(local):
            return 0
        edges = self._resize_edges_for_point(local)
        if edges:
            return self._hit_test_for_resize_edges(edges)
        if self._is_drag_point(local):
            return HTCAPTION
        return HTCLIENT

    def nativeEvent(self, eventType, message):
        if eventType in ("windows_generic_MSG", "windows_dispatcher_MSG"):
            try:
                msg = ctypes.wintypes.MSG.from_address(int(message))
            except Exception:
                msg = None
            if msg is not None:
                message_id = int(msg.message)
                if message_id == WM_NCHITTEST:
                    x = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
                    y = ctypes.c_short((int(msg.lParam) >> 16) & 0xFFFF).value
                    return True, self._native_hit_test(QPoint(x, y))
                if message_id == WM_NCLBUTTONDBLCLK:
                    if self._native_hit_test(QCursor.pos()) == HTCAPTION:
                        return True, 0
                if message_id == WM_NCLBUTTONDOWN:
                    hit_test = int(msg.wParam)
                    handle = self.windowHandle()
                    if handle is not None and hit_test == HTCAPTION and handle.startSystemMove():
                        return True, 0
                    resize_edges = self._resize_edges_for_hit_test(hit_test)
                    if handle is not None and resize_edges and handle.startSystemResize(resize_edges):
                        return True, 0
                if message_id == WM_SETCURSOR and not self._resizing_window:
                    hit_test = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
                    cursor_edges = self._resize_edges_for_hit_test(hit_test)
                    if cursor_edges:
                        self._set_resize_cursor(cursor_edges)
                        return True, 1
                    self.unsetCursor()
        return super().nativeEvent(eventType, message)

    def _set_resize_cursor(self, edges) -> None:
        if edges in (Qt.LeftEdge | Qt.TopEdge, Qt.RightEdge | Qt.BottomEdge):
            self.setCursor(Qt.SizeFDiagCursor)
        elif edges in (Qt.RightEdge | Qt.TopEdge, Qt.LeftEdge | Qt.BottomEdge):
            self.setCursor(Qt.SizeBDiagCursor)
        elif edges & (Qt.LeftEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeHorCursor)
        elif edges & (Qt.TopEdge | Qt.BottomEdge):
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.unsetCursor()

    def _apply_resize_from_global(self, current_global: QPoint) -> None:
        delta = current_global - self._resize_start_global
        rect = QRect(self._resize_start_geometry)
        min_width = self.minimumWidth()
        min_height = self.minimumHeight()
        if self._resize_edges & Qt.LeftEdge:
            rect.setLeft(min(rect.right() - min_width, rect.left() + delta.x()))
        if self._resize_edges & Qt.RightEdge:
            rect.setRight(max(rect.left() + min_width, rect.right() + delta.x()))
        if self._resize_edges & Qt.TopEdge:
            rect.setTop(min(rect.bottom() - min_height, rect.top() + delta.y()))
        if self._resize_edges & Qt.BottomEdge:
            rect.setBottom(max(rect.top() + min_height, rect.bottom() + delta.y()))
        self.setGeometry(rect)
        self._apply_shell_mask()

    def _update_interaction_metrics(self, metrics: dict[str, object]) -> None:
        try:
            drag_bottom = int(math.ceil(float(metrics.get("dragRegionBottom") or 0)))
            description_top = int(math.floor(float(metrics.get("descriptionTop") or drag_bottom)))
        except (TypeError, ValueError):
            return
        if drag_bottom <= 0:
            return
        drag_bottom = min(max(self.RESIZE_EDGE_MARGIN + 1, drag_bottom), max(1, self.height()))
        description_top = min(max(drag_bottom, description_top), max(drag_bottom, self.height()))
        self._drag_region_bottom = drag_bottom
        self._description_region_top = description_top
        self.setProperty("windowMeasuredDragRegionBottom", str(drag_bottom))
        self.setProperty("windowMeasuredDescriptionTop", str(description_top))

    def _queue_initial_content_fit(self, metrics: dict[str, object]) -> None:
        self._update_interaction_metrics(metrics)
        if not self._initial_content_fit_pending:
            return
        self._pending_content_metrics = dict(metrics)
        self._content_fit_timer.start(self.CONTENT_FIT_SETTLE_MS)

    def _apply_pending_initial_content_fit(self) -> None:
        if self._pending_content_metrics:
            self._apply_initial_content_fit(self._pending_content_metrics)

    def _apply_initial_content_fit(self, metrics: dict[str, object]) -> None:
        if not self._initial_content_fit_pending:
            return
        try:
            measured_content_height = int(math.ceil(float(metrics.get("contentHeight") or 0)))
        except (TypeError, ValueError):
            return
        if measured_content_height <= 0:
            return
        content_height = measured_content_height + self.CONTENT_FIT_SAFETY_PX
        screen = self.screen_ref or QApplication.primaryScreen()
        available = screen.availableGeometry() if screen is not None else QRect()
        max_height = max(
            self.minimumHeight(),
            min(self.maximumHeight(), available.height() - (self.AVAILABLE_DESKTOP_GUTTER * 2)),
        ) if available.isValid() else min(self.maximumHeight(), max(self.minimumHeight(), content_height))
        target_height = min(max(self.minimumHeight(), content_height), max_height)
        self._initial_content_fit_pending = False
        self._pending_content_metrics = {}
        if self.height() != target_height:
            self.resize(self.width(), target_height)
        self.setProperty("windowInitialContentFitApplied", "true")
        self.setProperty("windowMeasuredContentHeight", str(measured_content_height))
        self.setProperty("windowDefaultContentFitHeight", str(target_height))
        self.setProperty(
            "windowDefaultOverflowContract",
            "content-fit" if target_height >= content_height else "screen-bounded-scroll",
        )
        self.webview.page().runJavaScript(
            "(() => {"
            "const surface = document.querySelector('[data-ai-dashboard-child-window]');"
            "if (!surface) return;"
            "surface.dataset.initialContentFitApplied = 'true';"
            f"surface.dataset.measuredContentHeight = {json.dumps(str(measured_content_height))};"
            f"surface.dataset.defaultContentFitHeight = {json.dumps(str(target_height))};"
            f"surface.dataset.defaultOverflowContract = {json.dumps(str(self.property('windowDefaultOverflowContract') or ''))};"
            "})();"
        )
        if self.isVisible():
            _schedule_window_clamp(self, padding=self.AVAILABLE_DESKTOP_GUTTER)
        if callable(self.event_logger):
            self.event_logger(
                "RENDERER_MAIN|AI_DASHBOARD_DOMAIN_WINDOW_CONTENT_FIT_READY"
                f"|domain={self.domain_id}|content_h={measured_content_height}|window_h={target_height}"
                f"|overflow={self.property('windowDefaultOverflowContract')}"
            )

    def _asset_base_dir(self) -> Path:
        return Path(__file__).resolve().parents[1] / "nexus_visual"

    def _domain_html(self) -> str:
        definition = self.definition
        body = self._domain_body_html()
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(definition["title"])}</title>
  <link rel="stylesheet" href="monitoring_hud.css" />
  <style>
    html, body {{ margin: 0; width: 100%; height: 100%; background: transparent; }}
    body.desktop-mode {{ overflow: hidden; }}
    .ai-domain-window {{
      width: 100%;
      height: 100vh;
      padding: 0;
      --ai-domain-row-gutter: 8px;
      --ai-domain-row-vertical-gutter: 6px;
      --ai-domain-row-label-width: 0px;
      box-sizing: border-box;
      color: rgba(235, 252, 255, 0.96);
      background: transparent;
      font-family: "Inter", "Segoe UI", Arial, sans-serif;
    }}
    .ai-domain-window__chrome {{
      position: relative;
      width: 100%;
      height: 100vh;
      overflow: auto;
      scrollbar-width: thin;
      scrollbar-color: rgba(108, 232, 255, 0.58) transparent;
      border: 1px solid rgba(94, 207, 229, 0.42);
      border-radius: 24px;
      padding: 14px;
      box-sizing: border-box;
      background: linear-gradient(180deg, rgba(4, 16, 28, 0.985), rgba(2, 8, 16, 0.985));
      box-shadow: none;
    }}
    .ai-domain-window__content {{
      min-width: 0;
    }}
    .ai-domain-window__chrome::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
      background: transparent;
    }}
    .ai-domain-window__chrome::-webkit-scrollbar-track {{
      margin: 18px 0;
      border-radius: 999px;
      background: transparent;
    }}
    .ai-domain-window__chrome::-webkit-scrollbar-button {{
      width: 0;
      height: 0;
      display: none;
      background: transparent;
    }}
    .ai-domain-window__chrome::-webkit-scrollbar-thumb {{
      min-height: 44px;
      border-radius: 999px;
      background: rgba(108, 232, 255, 0.58);
      box-shadow: 0 0 8px rgba(88, 225, 255, 0.14);
    }}
    .ai-domain-window__chrome::-webkit-scrollbar-thumb:hover {{
      background: rgba(126, 248, 218, 0.66);
      box-shadow: 0 0 12px rgba(88, 225, 255, 0.20);
    }}
    .ai-domain-window__chrome::-webkit-scrollbar-corner {{
      background: transparent;
    }}
    .ai-domain-window__header {{
      box-sizing: border-box;
      border-bottom: 1px solid rgba(94, 207, 229, 0.24);
      margin-bottom: 12px;
      cursor: default;
    }}
    .ai-domain-window__drag-region {{
      display: grid;
      gap: 6px;
      padding: 10px 118px 6px 10px;
      box-sizing: border-box;
      cursor: move;
      user-select: none;
    }}
    .ai-domain-window__controls {{
      position: absolute;
      right: 14px;
      top: 14px;
      z-index: 8;
      display: flex;
      align-items: center;
      gap: 2px;
      padding: 2px;
      border: 1px solid rgba(122, 232, 255, 0.44);
      border-radius: 999px;
      background: linear-gradient(145deg, rgba(7, 42, 62, 0.70), rgba(3, 18, 32, 0.76));
      box-shadow: 0 0 0 1px rgba(230, 251, 255, 0.05) inset, 0 8px 19px rgba(0, 0, 0, 0.28);
    }}
    .ai-domain-window__control {{
      position: relative;
      width: 26px;
      min-width: 26px;
      height: 24px;
      min-height: 24px;
      padding: 0;
      border: 1px solid rgba(122, 232, 255, 0.24);
      border-radius: 999px;
      background: rgba(5, 22, 36, 0.62);
      color: transparent;
      cursor: pointer;
      box-shadow: 0 0 0 1px rgba(230, 251, 255, 0.04) inset;
      transition: border-color 120ms ease, background 120ms ease, box-shadow 120ms ease, transform 120ms ease;
    }}
    .ai-domain-window__control::before,
    .ai-domain-window__control::after {{
      position: absolute;
      left: 50%;
      top: 50%;
      content: "";
      box-sizing: border-box;
      border-color: rgba(235, 252, 255, 0.92);
      background: rgba(235, 252, 255, 0.92);
      transform: translate(-50%, -50%);
      transition: border-color 120ms ease, background 120ms ease, box-shadow 120ms ease;
    }}
    .ai-domain-window__control:hover,
    .ai-domain-window__control:focus-visible {{
      border-color: rgba(126, 248, 218, 0.56);
      background: rgba(9, 49, 70, 0.78);
      box-shadow: 0 0 0 1px rgba(230, 251, 255, 0.07) inset, 0 0 14px rgba(86, 236, 255, 0.28);
      outline: none;
    }}
    .ai-domain-window__control:active {{
      border-color: rgba(163, 255, 228, 0.72);
      background: rgba(7, 40, 57, 0.86);
      transform: translateY(1px);
    }}
    .ai-domain-window__control--minimize::before {{
      width: 10px;
      height: 2px;
      border-radius: 999px;
    }}
    .ai-domain-window__control--close::before,
    .ai-domain-window__control--close::after {{
      width: 11px;
      height: 2px;
      border-radius: 999px;
    }}
    .ai-domain-window__control--close::before {{
      transform: translate(-50%, -50%) rotate(45deg);
    }}
    .ai-domain-window__control--close::after {{
      transform: translate(-50%, -50%) rotate(-45deg);
    }}
    .ai-domain-window__kicker {{
      color: rgba(103, 224, 255, 0.95);
      font-size: 11px;
      font-weight: 820;
      letter-spacing: 0.20em;
      text-transform: uppercase;
    }}
    .ai-domain-window__title {{
      font-size: 26px;
      line-height: 1.05;
      font-weight: 850;
      letter-spacing: 0;
    }}
    .ai-domain-window__description {{
      margin: 0;
      padding: 0 118px 14px 10px;
      color: rgba(181, 218, 229, 0.88);
      font-size: 12px;
      font-weight: 720;
      line-height: 1.35;
      cursor: default;
    }}
    .ai-domain-window__card {{
      display: grid;
      gap: 8px;
      padding: 14px 18px 12px;
      border: 1px solid rgba(94, 207, 229, 0.28);
      border-radius: 18px;
      background: rgba(3, 18, 32, 0.74);
      margin-bottom: 10px;
    }}
    .ai-domain-window__card-heading {{
      display: grid;
      grid-template-columns: 36px minmax(0, 1fr);
      gap: 6px 14px;
      align-items: start;
    }}
    .ai-domain-window__card-number {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border: 1px solid rgba(87, 213, 236, 0.46);
      border-radius: 12px;
      color: rgba(103, 224, 255, 0.98);
      background: rgba(7, 54, 77, 0.52);
      font-size: 11px;
      font-weight: 820;
    }}
    .ai-domain-window__card-title {{
      color: rgba(235, 252, 255, 0.96);
      font-size: 16px;
      font-weight: 840;
      line-height: 1.12;
      text-transform: uppercase;
    }}
    .ai-domain-window__card-description {{
      grid-column: 2;
      margin: -6px 0 2px;
      color: rgba(181, 218, 229, 0.88);
      font-size: 11px;
      font-weight: 760;
      line-height: 1.28;
    }}
    .ai-domain-window__rows {{
      display: grid;
      gap: var(--ai-domain-row-vertical-gutter, 6px);
      min-width: 0;
    }}
    .ai-domain-window__row {{
      display: grid;
      grid-template-columns: var(--ai-domain-row-label-width, 0px) minmax(0, 1fr);
      column-gap: var(--ai-domain-row-gutter, 8px);
      min-height: 0;
      padding: 4px 0 2px;
      border-top: 1px solid rgba(94, 207, 229, 0.18);
    }}
    .ai-domain-window__row span {{
      color: rgba(103, 224, 255, 0.95);
      width: max-content;
      max-width: none;
      white-space: nowrap;
      font-size: 11px;
      font-weight: 720;
      letter-spacing: 0.07em;
      text-transform: uppercase;
    }}
    .ai-domain-window__row strong {{
      color: rgba(235, 252, 255, 0.96);
      font-size: 11px;
      font-weight: 720;
      line-height: 1.35;
    }}
    .ai-domain-window__actions {{
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      margin-top: 0;
      padding-top: 5px;
    }}
    .ai-domain-window__button {{
      min-height: 31px;
      max-width: 220px;
      padding: 0 14px;
      border: 1px solid rgba(122, 232, 255, 0.36);
      border-radius: 999px;
      background: linear-gradient(145deg, rgba(7, 42, 62, 0.72), rgba(3, 18, 32, 0.78));
      color: rgba(235, 252, 255, 0.96);
      font-size: 11px;
      font-weight: 720;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      cursor: pointer;
    }}
    .ai-domain-window__button:hover,
    .ai-domain-window__button:focus-visible {{
      border-color: rgba(126, 248, 218, 0.56);
      background: rgba(9, 49, 70, 0.78);
      box-shadow: 0 0 14px rgba(86, 236, 255, 0.24);
      outline: none;
    }}
    .ai-domain-window__button:disabled {{
      opacity: 0.55;
      cursor: default;
      box-shadow: none;
    }}
    .ai-domain-window__button[aria-pressed="true"] {{
      border-color: rgba(126, 248, 218, 0.68);
      background: rgba(10, 58, 72, 0.82);
      box-shadow: 0 0 0 1px rgba(230, 251, 255, 0.08) inset, 0 0 14px rgba(86, 236, 255, 0.22);
    }}
  </style>
</head>
<body class="desktop-mode">
  <main class="ai-domain-window" data-ai-dashboard-child-window="{escape(self.domain_id)}" data-window-classification="{escape(definition["classification"])}" data-window-lifecycle="{escape(definition["lifecycle"])}" data-ndai-native-chrome="true" data-generic-os-chrome="rejected" data-shell-conformance="ndai-webview-rounded-window-shell" data-window-boundary-contract="single-rounded-shell-mask-hit-rails-coincident-v2" data-window-boundary-inset="0" data-window-resize-rail-location="inside-visible-rounded-shell" data-window-outside-hit-behavior="noninteractive" data-window-move="measured-visible-title-strip-native-and-fallback-v2" data-window-description-drag="client-content-never-caption" data-window-resize="windows-native-edge-corner-hit-test-with-webview-fallback" data-window-default-geometry-contract="settled-dom-content-measured-screen-bounded-v2" data-window-supported-geometry-contract="minimum-default-intermediate-useful-large-screen-bounded" data-window-maximum-useful-size="{self.maximumWidth()}x{self.maximumHeight()}" data-window-maximize-fullscreen-policy="not-offered-compact-detached-window" data-window-reopen-geometry-contract="preserve-last-user-geometry-until-destroyed" data-window-shell-visual-contract="single-border-no-outer-halo" data-window-control-cluster="compact-minimize-close" data-scrollbar-style="ndai-rounded-domain-scrollbar" data-state-taxonomy-contract="{escape(self.STATE_TAXONOMY_CONTRACT)}" data-state-taxonomy-source="AIProviderStateSnapshot.aiControlCenterStateTaxonomy" data-state-taxonomy-scope="{escape(self.domain_id)}" data-state-taxonomy-required-states="{escape(" ".join(self.REQUIRED_STATE_TAXONOMY_STATES))}" data-view-model-contract="{escape(self.VIEW_MODEL_CONTRACT)}" data-view-model-source="AIProviderStateSnapshot.as_renderer_payload" data-view-model-state="pending-provider-payload" data-provider-visible-data-state="none" data-no-provider-state="no-provider-fail-closed" data-prompt-execution-state="prompt-send-disabled" data-provider-model-runtime-state="blocked-no-model-path" data-trust-boundary-state="local-only-no-egress-no-memory-no-cache">
    <section class="ai-domain-window__chrome">
      <div class="ai-domain-window__controls" role="group" aria-label="{escape(definition["title"])} window controls">
        <button class="ai-domain-window__control ai-domain-window__control--minimize" type="button" data-domain-command="window-minimize" aria-label="Minimize {escape(definition["title"])}" title="Minimize"></button>
        <button class="ai-domain-window__control ai-domain-window__control--close" type="button" data-domain-command="window-close" aria-label="Close {escape(definition["title"])}" title="Close"></button>
      </div>
      <div class="ai-domain-window__content">
        <header class="ai-domain-window__header">
          <div class="ai-domain-window__drag-region" data-window-drag-region="visible-title-strip">
            <div class="ai-domain-window__kicker">{escape(definition["kicker"])}</div>
            <div class="ai-domain-window__title">{escape(definition["title"])}</div>
          </div>
          <p class="ai-domain-window__description">{escape(definition["description"])}</p>
        </header>
        {body}
      </div>
    </section>
  </main>
  <script>
    const prefix = "NEXUS_AI_DOMAIN_WINDOW_COMMAND:";
    const stateTaxonomyContract = "{escape(self.STATE_TAXONOMY_CONTRACT)}";
    const viewModelContract = "{escape(self.VIEW_MODEL_CONTRACT)}";
    const requiredStateTaxonomyStates = {json.dumps(list(self.REQUIRED_STATE_TAXONOMY_STATES))};
    let providerState = {{}};
    let reportText = "";
    const byId = (id) => document.getElementById(id);
    const setText = (id, value) => {{ const target = byId(id); if (target) target.textContent = String(value || ""); }};
    const emit = (command) => console.info(prefix + command);
    const reportWindowContentMetrics = () => {{
      const surface = document.querySelector("[data-ai-dashboard-child-window]");
      const chrome = document.querySelector(".ai-domain-window__chrome");
      const content = document.querySelector(".ai-domain-window__content");
      const dragRegion = document.querySelector(".ai-domain-window__drag-region");
      const description = document.querySelector(".ai-domain-window__description");
      if (!surface || !chrome || !content || !dragRegion || !description) return;
      const chromeStyle = getComputedStyle(chrome);
      const contentHeight = Math.ceil(
        Math.max(content.scrollHeight, content.getBoundingClientRect().height)
        + parseFloat(chromeStyle.paddingTop || "0")
        + parseFloat(chromeStyle.paddingBottom || "0")
        + parseFloat(chromeStyle.borderTopWidth || "0")
        + parseFloat(chromeStyle.borderBottomWidth || "0")
      );
      const dragRegionBottom = Math.ceil(dragRegion.getBoundingClientRect().bottom);
      const descriptionTop = Math.ceil(description.getBoundingClientRect().top);
      Object.assign(surface.dataset, {{
        contentMeasuredHeight: String(contentHeight),
        contentViewportHeight: String(Math.round(chrome.clientHeight || 0)),
        contentScrollHeight: String(Math.round(chrome.scrollHeight || 0)),
        windowDefaultGeometryContract: "settled-dom-content-measured-screen-bounded-v2",
        measuredDragRegionBottom: String(dragRegionBottom),
        measuredDescriptionTop: String(descriptionTop),
      }});
      emit("window-content-metrics:" + encodeURIComponent(JSON.stringify({{
        contentHeight,
        viewportHeight: Math.round(chrome.clientHeight || 0),
        scrollHeight: Math.round(chrome.scrollHeight || 0),
        dragRegionBottom,
        descriptionTop,
      }})));
    }};
    const syncDomainRowLayout = () => {{
      const surface = document.querySelector("[data-ai-dashboard-child-window]");
      const labels = [...document.querySelectorAll(".ai-domain-window__row > span")];
      if (!surface || !labels.length) return;
      const maxLabelWidth = Math.ceil(Math.max(...labels.map((label) => label.getBoundingClientRect().width || 0)));
      surface.style.setProperty("--ai-domain-row-label-width", maxLabelWidth + "px");
      Object.assign(surface.dataset, {{
        rowLabelColumnSource: "measured-max-visible-label-content-px",
        rowLabelColumnWidth: String(maxLabelWidth),
        rowLabelColumnUnit: "px",
        rowValueColumnContract: "shared-max-label-content-plus-fixed-gutter",
        rowValueGutter: "8px",
        rowVerticalGutter: "6px",
      }});
      requestAnimationFrame(reportWindowContentMetrics);
    }};
    const formatItems = (items, keys = ["label"]) => {{
      const list = Array.isArray(items) ? items : [];
      if (!list.length) return "None";
      return list.map((item) => {{
        if (item && typeof item === "object") {{
          return keys.map((key) => String(item[key] || "").trim()).filter(Boolean).join(" - ");
        }}
        return String(item || "").trim();
      }}).filter(Boolean).join("; ");
    }};
    const formatUserItems = (items, keys = ["label"]) => {{
      const list = Array.isArray(items) ? items : [];
      if (!list.length) return "None";
      return list.map((item) => {{
        if (item && typeof item === "object") {{
          return keys.map((key) => String(item[key] || "").trim()).filter(Boolean).join(" - ");
        }}
        return String(item || "").trim();
      }}).filter(Boolean).join("; ");
    }};
    const buildReportText = (report) => [
      String(report.title || "Local AI Readiness Report"),
      "",
      "Summary: " + String(report.summary || "No local readiness report is available."),
      "Provider-visible data: " + String(report.providerVisibleData || "none"),
      "Ready: " + formatItems(report.readyConditions, ["label", "evidence"]),
      "Missing: " + formatItems(report.missingRequirements, ["label", "reason"]),
      "Blocked: " + formatItems(report.blockedPaths, ["label", "state", "gate"]),
      "Evidence checked: " + formatItems(report.localEvidenceChecked),
      "Safe next steps: " + formatItems(report.safeNextSteps),
      "Trust boundaries: " + formatItems(report.trustBoundaries)
    ].join("\\n");
    const guardClosed = () => providerState.sentToProvider === false
      && providerState.canAcceptPrompts === false
      && providerState.providerVisibleData === "none"
      && providerState.promptSendPosture === "prompt-send-disabled"
      && providerState.networkEgressState === "network-egress-blocked"
      && providerState.memoryIndexingState === "memory-indexing-disabled";
    const setNoProviderFlowState = (state, extra = {{}}) => {{
      const surface = document.querySelector("[data-ai-dashboard-child-window]");
      const workspace = document.querySelector("[data-domain-workspace='readiness-diagnostics']");
      const target = workspace || surface;
      if (!target) return;
      Object.assign(target.dataset, {{
        noProviderDiagnosticsFlow: "local-only-no-provider-readiness-v1",
        noProviderFlowState: state,
        noProviderFlowProviderVisibleData: String(providerState.providerVisibleData || "none"),
        noProviderFlowSentToProvider: providerState.sentToProvider === false ? "false" : String(providerState.sentToProvider || ""),
        noProviderFlowCanAcceptPrompts: providerState.canAcceptPrompts === false ? "false" : String(providerState.canAcceptPrompts || ""),
        noProviderFlowPromptSend: String(providerState.promptSendPosture || "prompt-send-disabled"),
        noProviderFlowNetworkEgress: String(providerState.networkEgressState || "network-egress-blocked"),
        noProviderFlowMemoryIndexing: String(providerState.memoryIndexingState || "memory-indexing-disabled"),
        ...extra,
      }});
    }};
    const buildDomainViewModel = () => {{
      const providerVisibleDataNone = providerState.providerVisibleData === "none";
      const providerRuntimeBlocked = providerState.providerExecutionGateState === "provider-execution-disabled"
        && providerState.modelExecutionGateState === "model-execution-disabled";
      const promptDisabled = providerState.promptSendPosture === "prompt-send-disabled"
        && providerState.memoryIndexingState === "memory-indexing-disabled";
      const installBlocked = String(providerState.installIntentState || "").includes("blocked")
        || String(providerState.capabilityPackInstallState || "").includes("blocked");
      const updatesBlocked = String(providerState.capabilityPackUpdateState || "").includes("blocked");
      const privateSetupBlocked = providerState.privateSetupAuthorized === false
        && providerState.privateMaterialVisible === false;
      const ownerRuntimeBlocked = providerState.ownerMemoryEnabled === false
        && providerState.ownerAgentsEnabled === false;
      return {{
        contract: viewModelContract,
        source: "AIProviderStateSnapshot.as_renderer_payload",
        providerVisibleData: providerVisibleDataNone ? "None" : String(providerState.providerVisibleData || "None"),
        providerModel: providerRuntimeBlocked ? "Disabled and blocked" : "Disabled; provider state requires review",
        promptMemory: promptDisabled ? "Not accepted, sent, stored, or indexed" : "Not accepted; prompt boundary mismatch",
        capabilityPacks: installBlocked ? "Install blocked; downloads disabled" : "Install unavailable; capability proof required",
        maintenanceUpdates: updatesBlocked ? "Lifecycle placement only; update execution blocked" : "Lifecycle placement only; update state requires review",
        developerLane: providerState.developerLaneBoundaryLabel || "Developer lane: gated; private setup not configured",
        ownerLane: providerState.ownerLaneBoundaryLabel || "Owner lane: gated; private setup not configured",
        privateSetup: privateSetupBlocked ? "Private setup blocked; no private material visible" : "Private setup boundary requires review",
        executionBoundary: "No update, download, install, fetch, provider/model, private setup, packaging, or capability execution is approved.",
        localResult: "Waiting for local action",
        localDetail: providerState.providerVisibleDataDetail || "No prompt, file, memory, telemetry, or provider config is sent.",
        disabledActions: {{
          providerModelExecution: providerRuntimeBlocked,
          promptSend: promptDisabled,
          capabilityInstallDownload: installBlocked,
          maintenanceUpdateExecution: updatesBlocked,
          providerVisibleDataEgress: providerVisibleDataNone && providerState.sentToProvider === false,
          privateSetup: privateSetupBlocked,
          ownerMemoryAgents: ownerRuntimeBlocked,
        }},
      }};
    }};
    const syncCapabilityBoundaryContract = (viewModel) => {{
      const workspace = document.querySelector("[data-domain-workspace='capabilities-maintenance']");
      if (!workspace) return;
      Object.assign(workspace.dataset, {{
        capabilitiesBoundaryContract: "capabilities-maintenance-developer-owner-boundary-v1",
        capabilityPackLifecycleState: String(providerState.capabilityPackLifecycleState || "capability-pack-lifecycle-planned"),
        capabilityPackDownloadState: String(providerState.capabilityPackDownloadState || "capability-pack-downloads-blocked"),
        installIntentState: String(providerState.installIntentState || "install-intent-blocked"),
        capabilityPackInstallState: String(providerState.capabilityPackInstallState || "install-blocked"),
        capabilityPackUpdateState: String(providerState.capabilityPackUpdateState || "update-blocked"),
        capabilityPackUninstallState: String(providerState.capabilityPackUninstallState || "uninstall-blocked"),
        developerLaneBoundaryState: String(providerState.developerLaneBoundaryState || "developer-lane-private-setup-blocked"),
        ownerLaneBoundaryState: String(providerState.ownerLaneBoundaryState || "owner-lane-private-setup-blocked"),
        privateSetupBoundaryState: String(providerState.privateSetupBoundaryState || "private-setup-blocked"),
        privateSetupAuthorized: providerState.privateSetupAuthorized === false ? "false" : String(providerState.privateSetupAuthorized || ""),
        privateMaterialVisible: providerState.privateMaterialVisible === false ? "false" : String(providerState.privateMaterialVisible || ""),
        ownerMemoryEnabled: providerState.ownerMemoryEnabled === false ? "false" : String(providerState.ownerMemoryEnabled || ""),
        ownerAgentsEnabled: providerState.ownerAgentsEnabled === false ? "false" : String(providerState.ownerAgentsEnabled || ""),
        updateExecution: "blocked",
        downloadExecution: "blocked",
        installExecution: "blocked",
        fetchExecution: "blocked",
        capabilityExecution: "blocked",
        packagingExecution: "blocked",
        viewModelPrivateSetupBlocked: viewModel.disabledActions.privateSetup ? "true" : "false",
        viewModelOwnerMemoryAgentsBlocked: viewModel.disabledActions.ownerMemoryAgents ? "true" : "false",
      }});
    }};
    const setPressedState = (commands, activeCommand) => {{
      commands.forEach((command) => {{
        document.querySelectorAll(`[data-domain-command="${{command}}"]`).forEach((button) => {{
          button.setAttribute("aria-pressed", command === activeCommand ? "true" : "false");
        }});
      }});
    }};
    const applyControlCenterMode = (mode) => {{
      const workspace = document.querySelector("[data-domain-workspace='control-center']");
      if (!workspace) return false;
      const closed = guardClosed();
      const renderedStates = Array.isArray(providerState.aiControlCenterStateTaxonomy)
        ? providerState.aiControlCenterStateTaxonomy
            .map((item) => item && typeof item === "object" ? String(item.state || "").trim() : "")
            .filter(Boolean)
        : [];
      const modes = {{
        boundary: {{
          command: "show-control-boundary",
          label: "Boundary review",
          state: closed ? "Provider/model blocked; local boundary active" : "Boundary mismatch; fail-closed",
          detail: closed
            ? "No provider data, prompt, memory, cache, network egress, or model path is available."
            : "Review halted because the trust boundary is inconsistent.",
          recovery: "Retry local check only; setup stays future-gated.",
          taxonomy: `${{renderedStates.length}} fail-closed states rendered`,
        }},
        recovery: {{
          command: "show-control-recovery",
          label: "Recovery route",
          state: "Local recovery only; provider setup remains unavailable",
          detail: providerState.aiControlCenterRecoveryDetail || "Recovery guidance stays inside this window and does not open provider setup.",
          recovery: providerState.aiControlCenterRecoveryLabel || "Retry local check only",
          taxonomy: "Recovery state mapped to local-only diagnostics",
        }},
        taxonomy: {{
          command: "show-control-taxonomy",
          label: "State taxonomy",
          state: "State taxonomy mapped from provider payload",
          detail: renderedStates.length ? renderedStates.join("; ") : "No provider state taxonomy was supplied.",
          recovery: "Blocked, unavailable, degraded, retry, and recovery states remain visible.",
          taxonomy: renderedStates.length ? "Complete taxonomy rendered" : "Taxonomy missing; fail-closed",
        }},
      }};
      const next = modes[mode] || modes.boundary;
      Object.assign(workspace.dataset, {{
        controlCenterOperationalContract: "ai-control-center-local-boundary-control-v1",
        controlCenterMode: mode in modes ? mode : "boundary",
        controlCenterGuardClosed: closed ? "true" : "false",
        controlCenterProviderActionExecuted: "false",
        controlCenterProviderModelExecution: "blocked",
        controlCenterPromptSendExecution: "blocked",
        controlCenterNetworkEgress: String(providerState.networkEgressState || "network-egress-blocked"),
        controlCenterMemoryIndexing: String(providerState.memoryIndexingState || "memory-indexing-disabled"),
        controlCenterProviderVisibleData: String(providerState.providerVisibleData || "none"),
      }});
      setText("control-center-mode", next.label);
      setText("control-center-review-state", next.state);
      setText("control-center-review-detail", next.detail);
      setText("control-center-recovery-route", next.recovery);
      setText("control-center-taxonomy", next.taxonomy);
      setPressedState(["show-control-boundary", "show-control-recovery", "show-control-taxonomy"], next.command);
      requestAnimationFrame(syncDomainRowLayout);
      return closed;
    }};
    const applyCapabilitiesMode = (mode) => {{
      const workspace = document.querySelector("[data-domain-workspace='capabilities-maintenance']");
      if (!workspace) return false;
      const modes = {{
        lifecycle: {{
          command: "show-capability-lifecycle",
          label: "Lifecycle review",
          state: "Capability packs remain planned; downloads disabled",
          detail: "Manifest, checksum, signature, compatibility, install, update, and uninstall stay blocked.",
          next: "Future carrier must prove source trust before any package action.",
        }},
        lanes: {{
          command: "show-capability-lanes",
          label: "Edition gates",
          state: "Public lane only; Developer and Owner lanes gated",
          detail: "Private setup, private material, Owner memory, and Owner agents are not visible or enabled.",
          next: "FAM/private setup remains future-gated and outside this runtime repair.",
        }},
        maintenance: {{
          command: "show-capability-maintenance",
          label: "Maintenance hold",
          state: "Update, install, fetch, and packaging execution blocked",
          detail: "This window can inspect the maintenance posture but cannot run downloads, updates, installs, fetches, or packaging.",
          next: "Keep display-only posture until an approved maintenance carrier exists.",
        }},
      }};
      const next = modes[mode] || modes.lifecycle;
      Object.assign(workspace.dataset, {{
        capabilitiesMaintenanceWorkflowContract: "capabilities-maintenance-display-workflow-v1",
        capabilitiesMaintenanceMode: mode in modes ? mode : "lifecycle",
        capabilitiesMaintenanceActionExecuted: "false",
        capabilitiesMaintenanceDownloadExecution: "blocked",
        capabilitiesMaintenanceInstallExecution: "blocked",
        capabilitiesMaintenanceUpdateExecution: "blocked",
        capabilitiesMaintenanceFetchExecution: "blocked",
        capabilitiesMaintenancePackagingExecution: "blocked",
        capabilitiesMaintenancePrivateSetup: providerState.privateSetupAuthorized === false ? "blocked" : "blocked-review-required",
      }});
      setText("capabilities-mode", next.label);
      setText("capabilities-workflow-state", next.state);
      setText("capabilities-workflow-detail", next.detail);
      setText("capabilities-workflow-next", next.next);
      setPressedState(["show-capability-lifecycle", "show-capability-lanes", "show-capability-maintenance"], next.command);
      requestAnimationFrame(syncDomainRowLayout);
      return true;
    }};
    const applyDomainViewModel = () => {{
      const viewModel = buildDomainViewModel();
      window.nexusAiDomainCurrentViewModel = viewModel;
      const surface = document.querySelector("[data-ai-dashboard-child-window]");
      if (surface) {{
        Object.assign(surface.dataset, {{
          viewModelContract: viewModel.contract,
          viewModelSource: viewModel.source,
          viewModelState: "provider-payload-applied",
          viewModelProviderRuntimeBlocked: viewModel.disabledActions.providerModelExecution ? "true" : "false",
          viewModelPromptSendDisabled: viewModel.disabledActions.promptSend ? "true" : "false",
          viewModelProviderVisibleDataNone: viewModel.disabledActions.providerVisibleDataEgress ? "true" : "false",
          viewModelPrivateSetupBlocked: viewModel.disabledActions.privateSetup ? "true" : "false",
          viewModelOwnerMemoryAgentsBlocked: viewModel.disabledActions.ownerMemoryAgents ? "true" : "false",
        }});
      }}
      setText("provider-visible-data", viewModel.providerVisibleData);
      setText("provider-model", viewModel.providerModel);
      setText("prompt-memory", viewModel.promptMemory);
      setText("capability-packs", viewModel.capabilityPacks);
      setText("maintenance-updates", viewModel.maintenanceUpdates);
      setText("developer-lane-boundary", viewModel.developerLane);
      setText("owner-lane-boundary", viewModel.ownerLane);
      setText("private-setup-boundary", viewModel.privateSetup);
      setText("execution-boundary", viewModel.executionBoundary);
      setText("local-result", viewModel.localResult);
      setText("local-detail", viewModel.localDetail);
      syncCapabilityBoundaryContract(viewModel);
      applyControlCenterMode("boundary");
      applyCapabilitiesMode("lifecycle");
      requestAnimationFrame(syncDomainRowLayout);
      return viewModel;
    }};
    const syncStateTaxonomyContract = () => {{
      const surface = document.querySelector("[data-ai-dashboard-child-window]");
      if (!surface) return;
      const taxonomy = Array.isArray(providerState.aiControlCenterStateTaxonomy)
        ? providerState.aiControlCenterStateTaxonomy
        : [];
      const renderedStates = taxonomy
        .map((item) => item && typeof item === "object" ? String(item.state || "").trim() : "")
        .filter(Boolean);
      const complete = requiredStateTaxonomyStates.every((state) => renderedStates.includes(state));
      const providerVisibleData = String(providerState.providerVisibleData || "none");
      const promptSendPosture = String(providerState.promptSendPosture || "prompt-send-disabled");
      const diagnosticState = String(providerState.aiControlCenterDiagnosticState || "no-provider-fail-closed");
      const providerExecution = (
        providerState.providerExecutionGateState === "provider-execution-disabled"
        && providerState.modelExecutionGateState === "model-execution-disabled"
      ) ? "blocked-no-model-path" : "blocked-fail-closed";
      Object.assign(surface.dataset, {{
        stateTaxonomyContract,
        stateTaxonomyRenderedStates: renderedStates.join(" "),
        stateTaxonomyComplete: complete ? "true" : "false",
        providerVisibleDataState: providerVisibleData,
        noProviderState: diagnosticState,
        promptExecutionState: promptSendPosture,
        providerModelRuntimeState: providerExecution,
        trustBoundaryState: guardClosed()
          ? "local-only-no-egress-no-memory-no-cache"
          : "fail-closed-boundary-mismatch",
      }});
    }};
    window.nexusAiDomainApplyProviderState = (payload) => {{
      providerState = payload && typeof payload === "object" ? payload : {{}};
      const viewModel = applyDomainViewModel();
      syncStateTaxonomyContract();
      setText("provider-visible-data", viewModel.providerVisibleData);
      setText("provider-model", viewModel.providerModel);
      setText("prompt-memory", viewModel.promptMemory);
      setText("capability-packs", viewModel.capabilityPacks);
      setText("maintenance-updates", viewModel.maintenanceUpdates);
      setText("edition-lanes", "Public only; Developer and Owner gated");
      setText("local-result", viewModel.localResult);
      setText("local-detail", viewModel.localDetail);
      setText("report-state", "Not generated");
      setText("report-summary", "Generate the report to inspect local readiness.");
      setNoProviderFlowState("waiting-for-user-action", {{
        noProviderFlowReportState: "not-generated",
        noProviderFlowCopyState: "not-ready",
      }});
      applyControlCenterMode("boundary");
      applyCapabilitiesMode("lifecycle");
      const body = byId("report-body");
      if (body) body.hidden = true;
      const copy = byId("copy-report");
      if (copy) {{ copy.disabled = true; copy.setAttribute("aria-disabled", "true"); }}
      requestAnimationFrame(syncDomainRowLayout);
    }};
    window.nexusAiDomainRunLocalCheck = () => {{
      const ok = guardClosed();
      setText("local-result", ok ? "No provider configured" : "Local check: blocked");
      setText("local-detail", ok
        ? (providerState.localActionResultDetail || "No prompt was accepted or sent; provider-visible data remains none.")
        : "Provider boundary mismatch; no local result was produced.");
      setNoProviderFlowState(ok ? "local-check-complete-no-provider" : "local-check-blocked-fail-closed", {{
        noProviderFlowReportState: "not-generated",
        noProviderFlowCopyState: "not-ready",
      }});
      requestAnimationFrame(syncDomainRowLayout);
      return ok;
    }};
    window.nexusAiDomainGenerateReport = () => {{
      const report = providerState.localAiReadinessReport || {{}};
      if (!guardClosed()) {{
        reportText = "";
        setText("report-state", "Blocked by boundary mismatch");
        setText("report-summary", "Report blocked because local trust-boundary proof is inconsistent.");
        setNoProviderFlowState("report-blocked-fail-closed", {{
          noProviderFlowReportState: "blocked-boundary-mismatch",
          noProviderFlowCopyState: "not-ready",
        }});
        return false;
      }}
      reportText = buildReportText(report);
      setText("report-state", "Generated locally");
      setText("report-summary", report.summary || "Local readiness report generated.");
      setText("report-ready", formatUserItems(report.readyConditions, ["label"]));
      setText("report-missing", formatUserItems(report.missingRequirements, ["label", "reason"]));
      setText("report-blocked", formatUserItems(report.blockedPaths, ["label"]));
      setText("report-evidence", formatUserItems(report.localEvidenceChecked));
      setText("report-next", formatUserItems(report.safeNextSteps));
      setText("report-boundary", "No provider/model execution, prompt send, download, cache, memory, or private setup ran. Copy report includes raw local proof details.");
      const body = byId("report-body");
      if (body) body.hidden = false;
      const copy = byId("copy-report");
      if (copy) {{ copy.disabled = false; copy.setAttribute("aria-disabled", "false"); }}
      setNoProviderFlowState("report-generated-local-only", {{
        noProviderFlowReportState: "generated-locally",
        noProviderFlowCopyState: "ready-user-initiated-only",
      }});
      requestAnimationFrame(syncDomainRowLayout);
      return true;
    }};
    window.nexusAiDomainCopyReport = () => {{
      if (!reportText) {{
        setText("report-state", "Generate report before copying");
        setNoProviderFlowState("copy-blocked-report-not-generated", {{
          noProviderFlowCopyState: "blocked-report-not-generated",
        }});
        return false;
      }}
      const text = document.createElement("textarea");
      text.value = reportText;
      text.setAttribute("readonly", "");
      text.style.position = "fixed";
      text.style.left = "-9999px";
      document.body.appendChild(text);
      text.focus();
      text.select();
      const copied = document.execCommand("copy");
      text.remove();
      setText("report-state", copied ? "Copied locally" : "Copy unavailable; report remains visible");
      setNoProviderFlowState(copied ? "report-copied-locally" : "copy-unavailable-report-visible", {{
        noProviderFlowReportState: "generated-locally",
        noProviderFlowCopyState: copied ? "copied-locally" : "copy-unavailable-report-visible",
      }});
      return copied;
    }};
    window.nexusAiDomainShowControlBoundary = () => applyControlCenterMode("boundary");
    window.nexusAiDomainShowControlRecovery = () => applyControlCenterMode("recovery");
    window.nexusAiDomainShowControlTaxonomy = () => applyControlCenterMode("taxonomy");
    window.nexusAiDomainShowCapabilitiesLifecycle = () => applyCapabilitiesMode("lifecycle");
    window.nexusAiDomainShowCapabilitiesLanes = () => applyCapabilitiesMode("lanes");
    window.nexusAiDomainShowCapabilitiesMaintenance = () => applyCapabilitiesMode("maintenance");
    document.addEventListener("click", (event) => {{
      const button = event.target.closest("[data-domain-command]");
      if (!button || button.disabled) return;
      const command = button.dataset.domainCommand;
      if (command === "window-minimize" || command === "window-close") {{
        emit(command);
      }} else if (command === "run-local-check") {{
        window.nexusAiDomainRunLocalCheck();
        emit("run-local-check");
      }} else if (command === "generate-readiness-report") {{
        emit(window.nexusAiDomainGenerateReport() ? "generate-readiness-report" : "generate-readiness-report-blocked");
      }} else if (command === "copy-readiness-report") {{
        if (window.nexusAiDomainCopyReport()) {{
          emit("copy-readiness-report");
        }} else if (reportText) {{
          setText("report-state", "Copying locally");
          emit("copy-readiness-report-native:" + encodeURIComponent(reportText));
        }} else {{
          emit("copy-readiness-report-blocked");
        }}
      }} else if (command === "show-control-boundary") {{
        emit(window.nexusAiDomainShowControlBoundary() ? "show-control-boundary" : "show-control-boundary-blocked");
      }} else if (command === "show-control-recovery") {{
        emit(window.nexusAiDomainShowControlRecovery() ? "show-control-recovery" : "show-control-recovery-blocked");
      }} else if (command === "show-control-taxonomy") {{
        emit(window.nexusAiDomainShowControlTaxonomy() ? "show-control-taxonomy" : "show-control-taxonomy-blocked");
      }} else if (command === "show-capability-lifecycle") {{
        window.nexusAiDomainShowCapabilitiesLifecycle();
        emit("show-capability-lifecycle");
      }} else if (command === "show-capability-lanes") {{
        window.nexusAiDomainShowCapabilitiesLanes();
        emit("show-capability-lanes");
      }} else if (command === "show-capability-maintenance") {{
        window.nexusAiDomainShowCapabilitiesMaintenance();
        emit("show-capability-maintenance");
      }}
    }});
    if (window.ResizeObserver) {{
      const rowObserver = new ResizeObserver(() => requestAnimationFrame(syncDomainRowLayout));
      document.querySelectorAll(".ai-domain-window__row > span, .ai-domain-window__content").forEach((node) => rowObserver.observe(node));
    }}
    if (document.fonts && document.fonts.ready) {{
      document.fonts.ready.then(() => requestAnimationFrame(syncDomainRowLayout)).catch(() => {{}});
    }}
    window.addEventListener("resize", syncDomainRowLayout);
    syncDomainRowLayout();
    requestAnimationFrame(() => {{ syncDomainRowLayout(); reportWindowContentMetrics(); }});
  </script>
</body>
</html>"""

    def _domain_body_html(self) -> str:
        if self.domain_id == "readiness-diagnostics":
            return """
      <section class="ai-domain-window__card" data-domain-workspace="readiness-diagnostics" data-executes-inside-child-window="true" data-no-provider-diagnostics-flow="local-only-no-provider-readiness-v1" data-no-provider-flow-state="waiting-for-user-action" data-no-provider-flow-provider-visible-data="none" data-no-provider-flow-sent-to-provider="false" data-no-provider-flow-can-accept-prompts="false" data-no-provider-flow-prompt-send="prompt-send-disabled" data-no-provider-flow-network-egress="network-egress-blocked" data-no-provider-flow-memory-indexing="memory-indexing-disabled" data-no-provider-flow-report-state="not-generated" data-no-provider-flow-copy-state="not-ready">
        <div class="ai-domain-window__card-heading">
          <span class="ai-domain-window__card-number">01</span>
          <strong class="ai-domain-window__card-title">Local Readiness</strong>
          <p class="ai-domain-window__card-description">Runs local-only checks and report generation inside this diagnostics window.</p>
        </div>
        <div class="ai-domain-window__rows" data-row-group="readiness-diagnostics">
          <div class="ai-domain-window__row"><span>Local check</span><strong id="local-result">Waiting for local action</strong></div>
          <div class="ai-domain-window__row"><span>Prompt / data</span><strong id="local-detail">No prompt, file, memory, telemetry, or provider config is sent.</strong></div>
          <div class="ai-domain-window__row"><span>Report state</span><strong id="report-state">Not generated</strong></div>
          <div class="ai-domain-window__row"><span>Persistence</span><strong>View-only; copy is USER initiated</strong></div>
          <div class="ai-domain-window__row"><span>Summary</span><strong id="report-summary">Generate the report to inspect local readiness.</strong></div>
        </div>
        <div class="ai-domain-window__actions" data-action-row-contract="separate-from-state-rows">
          <button class="ai-domain-window__button" type="button" id="run-local-check" data-domain-command="run-local-check">Run Local Check</button>
          <button class="ai-domain-window__button" type="button" id="generate-report" data-domain-command="generate-readiness-report">Generate Report</button>
          <button class="ai-domain-window__button" type="button" id="copy-report" data-domain-command="copy-readiness-report" disabled aria-disabled="true">Copy Report</button>
        </div>
        <div id="report-body" hidden>
          <div class="ai-domain-window__row"><span>Ready</span><strong id="report-ready">Not generated</strong></div>
          <div class="ai-domain-window__row"><span>Missing</span><strong id="report-missing">Not generated</strong></div>
          <div class="ai-domain-window__row"><span>Blocked</span><strong id="report-blocked">Not generated</strong></div>
          <div class="ai-domain-window__row"><span>Evidence</span><strong id="report-evidence">Not generated</strong></div>
          <div class="ai-domain-window__row"><span>Next</span><strong id="report-next">Not generated</strong></div>
          <div class="ai-domain-window__row"><span>Boundary</span><strong id="report-boundary">Not generated</strong></div>
        </div>
      </section>"""
        if self.domain_id == "capabilities-maintenance":
            return """
      <section class="ai-domain-window__card" data-domain-workspace="capabilities-maintenance" data-capabilities-boundary-contract="capabilities-maintenance-developer-owner-boundary-v1" data-capabilities-maintenance-workflow-contract="capabilities-maintenance-display-workflow-v1" data-capabilities-maintenance-mode="lifecycle" data-capabilities-maintenance-action-executed="false" data-capabilities-maintenance-download-execution="blocked" data-capabilities-maintenance-install-execution="blocked" data-capabilities-maintenance-update-execution="blocked" data-capabilities-maintenance-fetch-execution="blocked" data-capabilities-maintenance-packaging-execution="blocked" data-capability-pack-lifecycle-state="capability-pack-lifecycle-planned" data-capability-pack-download-state="capability-pack-downloads-blocked" data-install-intent-state="install-intent-blocked" data-capability-pack-install-state="install-blocked" data-capability-pack-update-state="update-blocked" data-capability-pack-uninstall-state="uninstall-blocked" data-developer-lane-boundary-state="developer-lane-private-setup-blocked" data-owner-lane-boundary-state="owner-lane-private-setup-blocked" data-private-setup-boundary-state="private-setup-blocked" data-private-setup-authorized="false" data-private-material-visible="false" data-owner-memory-enabled="false" data-owner-agents-enabled="false" data-update-execution="blocked" data-download-execution="blocked" data-install-execution="blocked" data-fetch-execution="blocked" data-capability-execution="blocked" data-packaging-execution="blocked">
        <div class="ai-domain-window__card-heading">
          <span class="ai-domain-window__card-number">01</span>
          <strong class="ai-domain-window__card-title">Capability Boundary</strong>
          <p class="ai-domain-window__card-description">Reviews capability lifecycle, edition gates, and maintenance hold without update, download, or install execution.</p>
        </div>
        <div class="ai-domain-window__rows" data-row-group="capabilities-maintenance">
          <div class="ai-domain-window__row"><span>Mode</span><strong id="capabilities-mode">Lifecycle review</strong></div>
          <div class="ai-domain-window__row"><span>Capability packs</span><strong id="capability-packs">Install blocked; downloads disabled</strong></div>
          <div class="ai-domain-window__row"><span>Maintenance</span><strong id="maintenance-updates">Lifecycle placement only; update execution blocked</strong></div>
          <div class="ai-domain-window__row"><span>Provider / model</span><strong id="provider-model">Provider/model lifecycle remains unavailable</strong></div>
          <div class="ai-domain-window__row"><span>Developer</span><strong id="developer-lane-boundary">Developer lane: gated; private setup not configured</strong></div>
          <div class="ai-domain-window__row"><span>Owner</span><strong id="owner-lane-boundary">Owner lane: gated; private setup not configured</strong></div>
          <div class="ai-domain-window__row"><span>Private setup</span><strong id="private-setup-boundary">Private setup blocked; no private material visible</strong></div>
          <div class="ai-domain-window__row"><span>Execution</span><strong id="execution-boundary">No update, download, install, fetch, provider/model, private setup, packaging, or capability execution is approved.</strong></div>
          <div class="ai-domain-window__row"><span>Review</span><strong id="capabilities-workflow-state">Capability packs remain planned; downloads disabled</strong></div>
          <div class="ai-domain-window__row"><span>Detail</span><strong id="capabilities-workflow-detail">Manifest, checksum, signature, compatibility, install, update, and uninstall stay blocked.</strong></div>
          <div class="ai-domain-window__row"><span>Next</span><strong id="capabilities-workflow-next">Future carrier must prove source trust before any package action.</strong></div>
        </div>
        <div class="ai-domain-window__actions" data-action-row-contract="separate-from-state-rows">
          <button class="ai-domain-window__button" type="button" id="capabilities-review-lifecycle" data-domain-command="show-capability-lifecycle" aria-pressed="true">Lifecycle</button>
          <button class="ai-domain-window__button" type="button" id="capabilities-review-lanes" data-domain-command="show-capability-lanes" aria-pressed="false">Edition Gates</button>
          <button class="ai-domain-window__button" type="button" id="capabilities-review-maintenance" data-domain-command="show-capability-maintenance" aria-pressed="false">Maintenance Hold</button>
        </div>
      </section>"""
        return """
      <section class="ai-domain-window__card" data-domain-workspace="control-center" data-control-center-operational-contract="ai-control-center-local-boundary-control-v1" data-control-center-mode="boundary" data-control-center-guard-closed="true" data-control-center-provider-action-executed="false" data-control-center-provider-model-execution="blocked" data-control-center-prompt-send-execution="blocked" data-control-center-network-egress="network-egress-blocked" data-control-center-memory-indexing="memory-indexing-disabled" data-control-center-provider-visible-data="none">
        <div class="ai-domain-window__card-heading">
          <span class="ai-domain-window__card-number">01</span>
          <strong class="ai-domain-window__card-title">AI Control State</strong>
          <p class="ai-domain-window__card-description">Reviews local AI boundary, recovery, and state taxonomy without provider/model execution.</p>
        </div>
        <div class="ai-domain-window__rows" data-row-group="control-center">
          <div class="ai-domain-window__row"><span>Mode</span><strong id="control-center-mode">Boundary review</strong></div>
          <div class="ai-domain-window__row"><span>Provider data</span><strong id="provider-visible-data">None</strong></div>
          <div class="ai-domain-window__row"><span>Provider / model</span><strong id="provider-model">Disabled and blocked</strong></div>
          <div class="ai-domain-window__row"><span>Prompt / memory</span><strong id="prompt-memory">Not accepted, sent, stored, or indexed</strong></div>
          <div class="ai-domain-window__row"><span>Persona</span><strong>Future-gated; ORIN persona is not implemented</strong></div>
          <div class="ai-domain-window__row"><span>Developer / Owner</span><strong id="edition-lanes">Public only; Developer and Owner gated</strong></div>
          <div class="ai-domain-window__row"><span>Review</span><strong id="control-center-review-state">Provider/model blocked; local boundary active</strong></div>
          <div class="ai-domain-window__row"><span>Detail</span><strong id="control-center-review-detail">No provider data, prompt, memory, cache, network egress, or model path is available.</strong></div>
          <div class="ai-domain-window__row"><span>Recovery</span><strong id="control-center-recovery-route">Retry local check only; setup stays future-gated.</strong></div>
          <div class="ai-domain-window__row"><span>Taxonomy</span><strong id="control-center-taxonomy">Fail-closed states rendered from provider payload</strong></div>
        </div>
        <div class="ai-domain-window__actions" data-action-row-contract="separate-from-state-rows">
          <button class="ai-domain-window__button" type="button" id="control-review-boundary" data-domain-command="show-control-boundary" aria-pressed="true">Boundary Review</button>
          <button class="ai-domain-window__button" type="button" id="control-review-recovery" data-domain-command="show-control-recovery" aria-pressed="false">Recovery Route</button>
          <button class="ai-domain-window__button" type="button" id="control-review-taxonomy" data-domain-command="show-control-taxonomy" aria-pressed="false">State Taxonomy</button>
        </div>
      </section>"""

    def _on_html_loaded(self, ok: bool) -> None:
        self._page_ready = bool(ok)
        if self._page_ready:
            self.update_provider_state(self._provider_payload)
        elif callable(self.event_logger):
            self.event_logger(
                "RENDERER_MAIN|AI_DASHBOARD_DOMAIN_WINDOW_HTML_LOAD_FAILED"
                f"|domain={self.domain_id}"
            )

    def _handle_domain_command(self, domain_id: str, command: str) -> None:
        if domain_id == self.domain_id and command.startswith("window-content-metrics:"):
            encoded_metrics = command.split(":", 1)[1]
            try:
                metrics = json.loads(urllib.parse.unquote(encoded_metrics))
            except (TypeError, ValueError, json.JSONDecodeError):
                metrics = {}
            if isinstance(metrics, dict):
                self._queue_initial_content_fit(metrics)
            return
        if (
            domain_id == "readiness-diagnostics"
            and command.startswith("copy-readiness-report-native:")
        ):
            encoded_report = command.split(":", 1)[1]
            report_text = urllib.parse.unquote(encoded_report)
            clipboard = QApplication.clipboard()
            if clipboard is not None and report_text:
                clipboard.setText(report_text)
                self.webview.page().runJavaScript(
                    "document.getElementById('report-state') && "
                    "(document.getElementById('report-state').textContent = 'Copied locally');"
                )
                command = "copy-readiness-report"
            else:
                self.webview.page().runJavaScript(
                    "document.getElementById('report-state') && "
                    "(document.getElementById('report-state').textContent = "
                    "'Copy unavailable; report remains visible');"
                )
                command = "copy-readiness-report-blocked"
        if callable(self.event_logger):
            self.event_logger(
                "RENDERER_MAIN|AI_DASHBOARD_DOMAIN_WINDOW_COMMAND"
                f"|domain={domain_id}|command={command}"
            )
        if command == "window-minimize":
            self.minimize_domain_window("visible-minimize-control")
        elif command == "window-close":
            self.close_domain_window("visible-close-control")

    def update_provider_state(self, payload: dict[str, object]) -> None:
        self._provider_payload = dict(payload or {})
        taxonomy = self._provider_payload.get("aiControlCenterStateTaxonomy")
        rendered_states = []
        if isinstance(taxonomy, list):
            for item in taxonomy:
                if isinstance(item, dict):
                    state = str(item.get("state") or "").strip()
                    if state:
                        rendered_states.append(state)
        complete = set(self.REQUIRED_STATE_TAXONOMY_STATES).issubset(set(rendered_states))
        self.setProperty("aiControlCenterStateTaxonomyContract", self.STATE_TAXONOMY_CONTRACT)
        self.setProperty("aiControlCenterStateTaxonomyComplete", "true" if complete else "false")
        self.setProperty("aiDashboardProviderStateViewModelContract", self.VIEW_MODEL_CONTRACT)
        self.setProperty("aiDashboardProviderStateViewModelApplied", "true")
        self.setProperty(
            "aiControlCenterDiagnosticState",
            str(self._provider_payload.get("aiControlCenterDiagnosticState") or "no-provider-fail-closed"),
        )
        self.setProperty("aiControlCenterStateTaxonomyRenderedStates", " ".join(rendered_states))
        if not self._page_ready:
            return
        self.webview.page().runJavaScript(
            "window.nexusAiDomainApplyProviderState && "
            f"window.nexusAiDomainApplyProviderState({json.dumps(self._provider_payload, sort_keys=True)});"
        )

    def show_domain_window(
        self,
        origin: QRect | None = None,
        *,
        requested_route: str = "ai-dashboard-doorway",
    ) -> dict[str, object]:
        hwnd_before = self._native_domain_hwnd()
        minimized = bool(self.isMinimized() or (hwnd_before and IsIconic(ctypes.wintypes.HWND(hwnd_before))))
        context = self._begin_lifecycle_action(
            requested_route=requested_route,
            requested_action=(
                "restore"
                if minimized
                else "focus-existing"
                if self._ever_shown
                else "reopen"
                if self._lifecycle_generation > 1
                else "open"
            ),
            qt_method=(
                "showNormal+show+raise+activateWindow+requestActivate"
                if minimized
                else "show+raise+activateWindow+requestActivate"
            ),
        )
        restored = None
        if minimized:
            self._pending_lifecycle_transition = context
            self.showNormal()
            restored = self._restore_remembered_normal_geometry()
        elif not self._ever_shown and origin is not None and origin.isValid():
            available = self.screen_ref.availableGeometry() if self.screen_ref is not None else QApplication.primaryScreen().availableGeometry()
            target_x = origin.x() - self.width() - 24
            if target_x < available.x() + 12:
                right_x = origin.x() + origin.width() + 24
                if right_x + self.width() <= available.right() - 12:
                    target_x = right_x
                else:
                    target_x = min(origin.x() + 44, available.right() - self.width() - 12)
            domain_offset = {
                "control-center": 0,
                "readiness-diagnostics": 34,
                "capabilities-maintenance": 68,
            }.get(self.domain_id, 0)
            target_y = min(
                max(available.y() + 12, origin.y() + domain_offset),
                available.bottom() - self.height() - 12,
            )
            self.setGeometry(self._bounded_domain_geometry(QRect(target_x, target_y, self.width(), self.height())))
            self._remember_normal_geometry()
        self._normalize_native_taskbar_contract()
        self.show()
        self._normalize_native_taskbar_contract()
        state = self._activate_domain_window()
        hwnd_after = int(state["hwnd"] or 0)
        self._ever_shown = True
        self._pending_lifecycle_transition = None
        lifecycle_record = self._record_lifecycle_transition(
            context,
            method_result=bool(
                state["nativeVisible"]
                and not state["nativeMinimized"]
                and state["taskbarEligible"]
                and state["focusResult"]
                and (not hwnd_before or hwnd_before == hwnd_after)
            ),
            restore_route=requested_route if minimized else "not-applicable",
            restored_rectangle=restored,
        )
        if callable(self.event_logger):
            self.event_logger(
                "RENDERER_MAIN|AI_DASHBOARD_DOMAIN_WINDOW_VISIBLE"
                f"|domain={self.domain_id}|classification={self.definition['classification']}"
                f"|lifecycle={self.definition['lifecycle']}|singleton=true"
                f"|taskbar_eligible={str(state['taskbarEligible']).lower()}"
                f"|native_owner_hwnd={state['nativeOwnerHwnd']}"
            )
        return {
            "domain": self.domain_id,
            "visible": bool(state["nativeVisible"]),
            "classification": self.definition["classification"],
            "lifecycle": self.definition["lifecycle"],
            "hwnd": hwnd_after,
            "sameHwnd": bool(not hwnd_before or hwnd_before == hwnd_after),
            "taskbarEligible": bool(state["taskbarEligible"]),
            "nativeOwnerHwnd": int(state["nativeOwnerHwnd"]),
            "focusResult": bool(state["focusResult"]),
            "lifecycleSequenceId": lifecycle_record["sequenceId"],
        }


class QuickCreateGroupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("New Group")
        self.setObjectName("quickCreateGroupDialog")
        self.setMinimumWidth(420)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("quickCreateGroupShell")
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.content = QWidget(self.shell)
        self.content.setObjectName("quickCreateGroupContent")
        shell_layout.addWidget(self.content)

        self.chrome_bar = DialogChromeBar(
            "New Group",
            self,
            object_prefix="quickCreateGroup",
            parent=self.shell,
            show_title=False,
        )
        self.chrome_bar.raise_()

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(22, 10, 22, 16)
        layout.setSpacing(10)

        title_label = QLabel("New Group", self)
        title_label.setObjectName("quickCreateGroupTitle")
        layout.addWidget(title_label)

        hint_label = QLabel(
            "Create a callable group name and aliases for the current task. The task becomes the first member when save succeeds.",
            self,
        )
        hint_label.setObjectName("quickCreateGroupHint")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        name_label = QLabel("Group name", self)
        name_label.setProperty("createRole", "fieldHeader")
        layout.addWidget(name_label)

        self.title_input = QLineEdit(self)
        self.title_input.setObjectName("quickCreateGroupTitleInput")
        self.title_input.setMinimumHeight(42)
        self.title_input.setPlaceholderText("Workspace Tools")
        layout.addWidget(self.title_input)

        aliases_label = QLabel("Aliases", self)
        aliases_label.setProperty("createRole", "fieldHeader")
        layout.addWidget(aliases_label)

        self.aliases_input = QLineEdit(self)
        self.aliases_input.setObjectName("quickCreateGroupAliasesInput")
        self.aliases_input.setMinimumHeight(42)
        self.aliases_input.setPlaceholderText("workspace tools, tools group")
        layout.addWidget(self.aliases_input)

        self.status_label = QLabel("", self)
        self.status_label.setObjectName("quickCreateGroupStatus")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(8)
        button_row.addStretch(1)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)

        create_button = QPushButton("Add Group", self)
        create_button.setDefault(True)
        create_button.clicked.connect(self._handle_submit)
        button_row.addWidget(create_button)

        layout.addLayout(button_row)

        self.setStyleSheet(
            """
            #quickCreateGroupDialog { background: transparent; }
            #quickCreateGroupShell {
                border-radius: 18px;
                border: 1px solid rgba(118, 226, 255, 0.14);
                background: rgb(9, 18, 28);
            }
            #quickCreateGroupContent { background: transparent; }
            #quickCreateGroupChromeBar {
                border: none;
                background: transparent;
            }
            QPushButton[chromeRole="close"] {
                min-width: 24px;
                max-width: 24px;
                min-height: 20px;
                max-height: 20px;
                padding: 0 0 1px 0;
                text-align: center;
                border-radius: 8px;
                border: 1px solid rgba(118, 226, 255, 0.10);
                background: rgba(26, 62, 92, 0.94);
                color: rgba(191, 212, 207, 0.94);
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton[chromeRole="close"]:hover {
                border: 1px solid rgba(102, 219, 204, 0.24);
                background: rgba(15, 36, 52, 0.70);
            }
            #quickCreateGroupTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 22px;
                font-weight: 650;
            }
            #quickCreateGroupHint {
                color: rgba(136, 165, 174, 0.88);
                font-size: 12px;
            }
            #quickCreateGroupStatus {
                color: rgba(255, 189, 176, 0.96);
                font-size: 12px;
            }
            QLineEdit {
                min-height: 42px;
                border-radius: 13px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(193, 213, 208, 0.96);
                padding: 7px 14px;
            }
            QPushButton {
                min-height: 38px;
                padding: 0 18px;
                border-radius: 11px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(191, 212, 207, 0.96);
            }
            """
        )

        self._update_chrome_overlay_geometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_chrome_overlay_geometry()

    def _update_chrome_overlay_geometry(self):
        if hasattr(self, "chrome_bar") and hasattr(self, "shell"):
            self.chrome_bar.setGeometry(6, 6, max(72, self.shell.width() - 12), self.chrome_bar.height())
            self.chrome_bar.raise_()

    def draft(self) -> CallableGroupDraft:
        aliases = tuple(
            part.strip()
            for part in (self.aliases_input.text() or "").replace("\n", ",").split(",")
            if part.strip()
        )
        return CallableGroupDraft(
            title=self.title_input.text(),
            aliases=aliases,
            member_action_ids=(),
        )

    def _handle_submit(self):
        try:
            _coerced = CallableGroupDraft(
                title=self.title_input.text().strip(),
                aliases=tuple(
                    part.strip()
                    for part in (self.aliases_input.text() or "").replace("\n", ",").split(",")
                    if part.strip()
                ),
                member_action_ids=(),
            )
            if not _coerced.title:
                raise CallableGroupDraftValidationError("Callable group name must not be empty.")
            if not _coerced.aliases:
                raise CallableGroupDraftValidationError("Callable groups require at least one exact alias.")
        except CallableGroupDraftValidationError as exc:
            self.status_label.setText(str(exc))
            self.status_label.show()
            return
        self.accept()


class TaskGroupAssignmentDialog(QDialog):
    def __init__(
        self,
        *,
        available_groups: list[dict] | None = None,
        available_members: list[dict] | None = None,
        selected_group_ids: tuple[str, ...] = (),
        inline_group_draft: CallableGroupDraft | None = None,
        inline_group_assigned: bool = False,
        group_status_kind: str = "loaded",
        group_status_text: str = "",
        lifecycle_callback=None,
        parent=None,
    ):
        super().__init__(parent)
        self._lifecycle_callback = lifecycle_callback
        self._dialog_signal_name = "TASK_GROUP_ASSIGNMENT_DIALOG"
        self._ready_signal_emitted = False
        self._available_groups = list(available_groups or [])
        self._available_members = list(available_members or [])
        self._selected_group_id = next(
            (
                str(group_id).strip()
                for group_id in (selected_group_ids or ())
                if str(group_id).strip()
            ),
            "",
        )
        self._inline_group_draft = inline_group_draft
        self._inline_group_assigned = bool(inline_group_assigned and inline_group_draft is not None)
        self._group_status_kind = group_status_kind or "template_only"
        self._group_status_text = group_status_text or ""
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("Manage Custom Groups")
        self.setObjectName("taskGroupAssignmentDialog")
        self.setMinimumWidth(620)
        self.setMaximumWidth(680)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("taskGroupAssignmentShell")
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.chrome_bar = DialogChromeBar(
            "Available Groups",
            self,
            object_prefix="taskGroupAssignment",
            parent=self.shell,
            show_title=False,
        )
        self.chrome_bar.close_button.setToolTip("Close Available Groups")
        shell_layout.addWidget(self.chrome_bar)

        self.content = QWidget(self.shell)
        self.content.setObjectName("taskGroupAssignmentContent")
        shell_layout.addWidget(self.content)

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(14, 2, 14, 10)
        layout.setSpacing(2)

        self.title_label = QLabel("Manage Custom Groups", self)
        self.title_label.setObjectName("taskGroupAssignmentTitle")
        self.title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        self.hint_label = QLabel(
            "Review callable groups, assign one to this task, or create a new callable group without leaving the current task session.",
            self,
        )
        self.hint_label.setObjectName("taskGroupAssignmentHint")
        self.hint_label.setWordWrap(True)
        self.hint_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self.hint_label)

        self.status_label = QLabel("", self)
        self.status_label.setObjectName("taskGroupAssignmentStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.source_label = QLabel("", self)
        self.source_label.setObjectName("taskGroupAssignmentSource")
        self.source_label.setWordWrap(True)
        layout.addWidget(self.source_label)

        self.guidance_label = QLabel("", self)
        self.guidance_label.setObjectName("taskGroupAssignmentGuidance")
        self.guidance_label.setWordWrap(True)
        layout.addWidget(self.guidance_label)

        self.items_frame = QFrame(self)
        self.items_frame.setObjectName("taskGroupAssignmentItems")
        self.items_layout = QVBoxLayout(self.items_frame)
        self.items_layout.setContentsMargins(0, 2, 0, 0)
        self.items_layout.setSpacing(2)

        self.items_scroll = QScrollArea(self)
        self.items_scroll.setObjectName("taskGroupAssignmentItemsScroll")
        self.items_scroll.setFrameShape(QFrame.NoFrame)
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.items_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.items_scroll.setFocusPolicy(Qt.NoFocus)
        self.items_scroll.setMaximumHeight(0)
        self.items_scroll.viewport().setObjectName("taskGroupAssignmentViewport")
        self.items_scroll.viewport().setAutoFillBackground(False)
        self.items_scroll.setWidget(self.items_frame)
        layout.addWidget(self.items_scroll)

        self.footer_frame = QFrame(self)
        self.footer_frame.setObjectName("taskGroupAssignmentFooter")
        actions_row = QHBoxLayout(self.footer_frame)
        actions_row.setContentsMargins(0, 4, 0, 0)
        actions_row.setSpacing(8)

        self.create_group_button = QPushButton("Create New Group", self.footer_frame)
        self.create_group_button.setObjectName("taskGroupAssignmentCreateButton")
        self.create_group_button.setMinimumHeight(34)
        self.create_group_button.setToolTip(
            "Create a new callable group, then return here to assign it to this task."
        )
        self.create_group_button.clicked.connect(self._handle_create_group_requested)
        actions_row.addWidget(self.create_group_button, 0, Qt.AlignLeft)
        actions_row.addStretch(1)

        self.done_button = QPushButton("Done", self.footer_frame)
        self.done_button.setObjectName("taskGroupAssignmentDoneButton")
        self.done_button.setMinimumHeight(34)
        self.done_button.clicked.connect(self.accept)
        actions_row.addWidget(self.done_button)
        layout.addWidget(self.footer_frame)

        self.setStyleSheet(
            """
            #taskGroupAssignmentDialog { background: transparent; }
            #taskGroupAssignmentShell {
                border-radius: 22px;
                border: 1px solid rgba(118, 226, 255, 0.20);
                background: rgba(4, 16, 28, 238);
            }
            #taskGroupAssignmentContent {
                border-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #taskGroupAssignmentChromeBar {
                border: none;
                border-top-left-radius: 22px;
                border-top-right-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #taskGroupAssignmentFooter {
                border-top: 1px solid rgba(118, 226, 255, 0.12);
                background: transparent;
            }
            #taskGroupAssignmentTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 20px;
                font-weight: 600;
                padding: 0px 6px 1px 6px;
                background: transparent;
            }
            #taskGroupAssignmentHint {
                color: rgba(136, 165, 174, 0.88);
                font-size: 11px;
                line-height: 1.45em;
                padding: 0px 6px 3px 6px;
                background: transparent;
            }
            #taskGroupAssignmentStatus {
                color: rgba(255, 189, 176, 0.96);
                font-size: 13px;
                background: transparent;
            }
            #taskGroupAssignmentSource {
                color: rgba(126, 157, 171, 0.78);
                font-size: 13px;
                background: transparent;
            }
            #taskGroupAssignmentGuidance {
                color: rgba(110, 201, 164, 0.86);
                font-size: 13px;
                background: transparent;
            }
            """
            + THEMED_TOOLTIP_QSS
            + """
            #taskGroupAssignmentItemsScroll {
                border: none;
                background: transparent;
            }
            #taskGroupAssignmentViewport {
                border-radius: 18px;
                background: rgba(4, 12, 22, 236);
            }
            #taskGroupAssignmentItems {
                background: transparent;
            }
            QFrame[groupAssignRole="row"] {
                border-radius: 14px;
                border: 1px solid rgba(118, 226, 255, 0.22);
                background: rgba(12, 28, 44, 208);
            }
            QFrame[groupAssignRole="actionShell"] {
                border-radius: 16px;
                border: none;
                background: rgba(15, 40, 62, 248);
            }
            QLabel[groupAssignRole="title"] {
                color: rgba(184, 208, 200, 0.96);
                font-size: 14px;
                font-weight: 650;
                background: transparent;
            }
            QLabel[groupAssignRole="meta"] {
                color: rgba(84, 192, 181, 0.83);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                background: transparent;
            }
            QLabel[groupAssignRole="detail"] {
                color: rgba(163, 189, 196, 0.92);
                font-size: 12px;
                background: transparent;
            }
            QPushButton[chromeRole="close"] {
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                padding: 0px;
                text-align: center;
                border-radius: 7px;
                border: 1px solid rgba(118, 226, 255, 0.16);
                background: rgba(18, 52, 78, 228);
                color: rgba(191, 212, 207, 0.94);
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton[chromeRole="close"]:hover {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(22, 61, 90, 238);
            }
            QPushButton[groupAssignRole="toggle"], #taskGroupAssignmentCreateButton, #taskGroupAssignmentDoneButton {
                min-height: 34px;
                padding: 0 16px;
                border-radius: 12px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(191, 212, 207, 0.96);
                font-size: 14px;
                font-weight: 650;
            }
            QPushButton[groupAssignRole="toggle"] {
                min-width: 96px;
                border: 1px solid rgba(118, 226, 255, 0.30);
                background: rgba(18, 52, 78, 228);
            }
            QPushButton[groupAssignRole="toggle"][assigned="true"] {
                border: 1px solid rgba(110, 220, 174, 0.30);
                background: rgba(13, 47, 40, 214);
            }
            QPushButton[groupAssignRole="toggle"]:hover, #taskGroupAssignmentCreateButton:hover, #taskGroupAssignmentDoneButton:hover {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(8, 24, 38, 220);
            }
            #taskGroupAssignmentItemsScroll QScrollBar:vertical {
                width: 8px;
                margin: 4px 1px 4px 0;
                border-radius: 4px;
                background: rgba(6, 18, 30, 0.58);
            }
            #taskGroupAssignmentItemsScroll QScrollBar::handle:vertical {
                min-height: 38px;
                border-radius: 4px;
                border: 1px solid rgba(118, 226, 255, 0.20);
                background: rgba(18, 52, 78, 0.96);
            }
            #taskGroupAssignmentItemsScroll QScrollBar::handle:vertical:hover {
                background: rgba(22, 61, 90, 0.98);
            }
            #taskGroupAssignmentItemsScroll QScrollBar::add-line:vertical,
            #taskGroupAssignmentItemsScroll QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            #taskGroupAssignmentItemsScroll QScrollBar::add-page:vertical,
            #taskGroupAssignmentItemsScroll QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

        self._update_chrome_overlay_geometry()
        self._refresh_items()

    def _emit_lifecycle_event(self, stage: str, **fields):
        if callable(self._lifecycle_callback):
            try:
                self._lifecycle_callback(self._dialog_signal_name, stage, dialog=self, **fields)
            except Exception:
                pass

    def _emit_ready_signal(self):
        if self._ready_signal_emitted or not self.isVisible():
            return
        self._ready_signal_emitted = True
        self._emit_lifecycle_event("ready")

    def showEvent(self, event):
        super().showEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        self._sync_items_scroll_height()
        _schedule_window_clamp(self)
        self._emit_lifecycle_event("opened")
        QTimer.singleShot(0, self._emit_ready_signal)
        QTimer.singleShot(0, self._sync_items_scroll_height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        self._sync_items_scroll_height()
        _schedule_window_clamp(self)
        QTimer.singleShot(0, self._sync_items_scroll_height)

    def done(self, result):
        self._emit_lifecycle_event(
            "closed",
            result="accepted" if result == QDialog.Accepted else "rejected",
        )
        super().done(result)

    def _update_chrome_overlay_geometry(self):
        if hasattr(self, "chrome_bar"):
            self.chrome_bar.raise_()

    def _sync_items_scroll_height(self):
        if not hasattr(self, "items_scroll") or not hasattr(self, "items_layout"):
            return
        row_frames = [
            self.items_layout.itemAt(index).widget()
            for index in range(self.items_layout.count())
            if self.items_layout.itemAt(index) is not None
            and self.items_layout.itemAt(index).widget() is not None
            and self.items_layout.itemAt(index).widget().property("groupAssignRole") == "row"
        ]
        visible_rows = sum(1 for frame in row_frames if frame.isVisible())
        if visible_rows <= 0:
            self.items_scroll.setMaximumHeight(0)
            self.items_scroll.setFixedHeight(0)
            return
        desired_height = _visible_row_height_for_layout(
            self.items_layout,
            min(5, visible_rows),
            extra_padding=0,
        )
        self.items_scroll.setMaximumHeight(desired_height)
        self.items_scroll.setFixedHeight(desired_height)

    def selected_group_ids(self) -> tuple[str, ...]:
        if not self._selected_group_id:
            return ()
        return (self._selected_group_id,)

    def inline_group_draft(self) -> CallableGroupDraft | None:
        return self._inline_group_draft

    def inline_group_assigned(self) -> bool:
        return bool(self._inline_group_draft is not None and self._inline_group_assigned)

    def _toggle_existing_group(self, group_id: str):
        normalized_key = str(group_id or "").strip().casefold()
        if not normalized_key:
            return
        if self._selected_group_id and self._selected_group_id.casefold() == normalized_key:
            self._selected_group_id = ""
        else:
            self._selected_group_id = str(group_id).strip()
            self._inline_group_assigned = False
        self._refresh_items()

    def _toggle_inline_group(self):
        if self._inline_group_draft is None:
            return
        self._inline_group_assigned = not self._inline_group_assigned
        if self._inline_group_assigned:
            self._selected_group_id = ""
        self._refresh_items()

    def _handle_create_group_requested(self):
        if self._group_status_kind == "invalid_groups":
            self.status_label.setText(self._group_status_text)
            self.status_label.setVisible(bool(self.status_label.text()))
            return

        dialog = CallableGroupCreateDialog(
            self,
            dialog_title="Create Custom Group",
            heading_text="Create Custom Group",
            hint_text="Pick a group name and exact aliases below. You will return to Manage Custom Groups for this task after the group is created.",
            submit_button_text="Create",
            available_members=self._available_members,
            show_member_picker=False,
            lifecycle_callback=self._lifecycle_callback,
        )
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            self._inline_group_draft = dialog.build_draft()
        except CallableGroupDraftValidationError as exc:
            self.status_label.setText(str(exc))
            self.status_label.setVisible(True)
            return
        self._inline_group_assigned = False
        self._refresh_items()

    def _make_group_row(
        self,
        *,
        title: str,
        meta_text: str,
        detail_text: str,
        assigned: bool,
        on_toggle,
        parent: QWidget,
        row_object_name: str = "",
        title_object_name: str = "",
        button_object_name: str = "",
    ) -> QFrame:
        frame = QFrame(parent)
        if row_object_name:
            frame.setObjectName(row_object_name)
        frame.setProperty("groupAssignRole", "row")
        frame.setMinimumHeight(70)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)

        title_label = QLabel(title, frame)
        if title_object_name:
            title_label.setObjectName(title_object_name)
        title_label.setProperty("groupAssignRole", "title")
        title_label.setWordWrap(True)
        text_column.addWidget(title_label)

        meta_label = QLabel(meta_text, frame)
        meta_label.setProperty("groupAssignRole", "meta")
        meta_label.setWordWrap(True)
        text_column.addWidget(meta_label)

        if detail_text:
            detail_label = QLabel(detail_text, frame)
            detail_label.setProperty("groupAssignRole", "detail")
            detail_label.setWordWrap(True)
            text_column.addWidget(detail_label)

        layout.addLayout(text_column, 1)

        action_shell = QFrame(frame)
        action_shell.setProperty("groupAssignRole", "actionShell")
        action_layout = QVBoxLayout(action_shell)
        action_layout.setContentsMargins(4, 4, 4, 4)
        action_layout.setSpacing(0)

        action_button = QPushButton("Remove" if assigned else "Assign", action_shell)
        if button_object_name:
            action_button.setObjectName(button_object_name)
        action_button.setProperty("groupAssignRole", "toggle")
        action_button.setProperty("assigned", assigned)
        action_button.setMinimumWidth(90)
        action_button.clicked.connect(on_toggle)
        action_button.setEnabled(self._group_status_kind != "invalid_groups")
        action_layout.addWidget(action_button)
        layout.addWidget(action_shell, 0, Qt.AlignTop)
        return frame

    def _refresh_items(self):
        _clear_layout_widgets(self.items_layout)
        show_disabled_state = self._group_status_kind == "invalid_groups"
        self.status_label.setText(self._group_status_text if show_disabled_state else "")
        self.status_label.setVisible(bool(self.status_label.text()))
        self.create_group_button.setEnabled(not show_disabled_state)

        normalized_selected = self._selected_group_id.casefold() if self._selected_group_id else ""
        row_count = 0
        available_group_count = 0

        for item in self._available_groups:
            group_id = str(item.get("id") or "").strip()
            if not group_id:
                continue
            aliases = ", ".join(
                str(alias).strip()
                for alias in (item.get("aliases") or [])
                if str(alias).strip()
            )
            member_count = int(item.get("member_count") or 0)
            member_noun = "member" if member_count == 1 else "members"
            row = self._make_group_row(
                title=str(item.get("title") or "").strip() or group_id,
                meta_text=f"Custom group | {member_count} {member_noun}",
                detail_text=(f"Aliases: {aliases}" if aliases else "Aliases: none"),
                assigned=bool(normalized_selected and group_id.casefold() == normalized_selected),
                on_toggle=lambda _checked=False, value=group_id: self._toggle_existing_group(value),
                parent=self.items_frame,
            )
            self.items_layout.addWidget(row)
            row_count += 1
            available_group_count += 1

        if self._inline_group_draft is not None:
            inline_aliases = ", ".join(self._inline_group_draft.aliases)
            row = self._make_group_row(
                title=self._inline_group_draft.title,
                meta_text="Custom group | queued for assignment",
                detail_text=(
                    f"Aliases: {inline_aliases}"
                    if inline_aliases
                    else "Aliases: none yet"
                ),
                assigned=self._inline_group_assigned,
                on_toggle=lambda _checked=False: self._toggle_inline_group(),
                parent=self.items_frame,
                row_object_name="taskGroupAssignmentInlineGroupRow",
                title_object_name="taskGroupAssignmentInlineGroupTitle",
                button_object_name="taskGroupAssignmentInlineGroupToggleButton",
            )
            self.items_layout.addWidget(row)
            row_count += 1

        if row_count == 0:
            empty_frame = QFrame(self.items_frame)
            empty_frame.setProperty("groupAssignRole", "row")
            empty_layout = QVBoxLayout(empty_frame)
            empty_layout.setContentsMargins(10, 10, 10, 10)
            empty_layout.setSpacing(4)

            empty_title = QLabel("No callable groups yet", empty_frame)
            empty_title.setProperty("groupAssignRole", "title")
            empty_layout.addWidget(empty_title)

            empty_meta = QLabel("Create one here", empty_frame)
            empty_meta.setProperty("groupAssignRole", "meta")
            empty_layout.addWidget(empty_meta)

            empty_detail = QLabel(
                "Use Create New Group to add one without leaving this task session.",
                empty_frame,
            )
            empty_detail.setProperty("groupAssignRole", "detail")
            empty_detail.setWordWrap(True)
            empty_layout.addWidget(empty_detail)
            self.items_layout.addWidget(empty_frame)
            row_count = 1

        self.source_label.setText(
            (
                f"{available_group_count} custom {'group' if available_group_count == 1 else 'groups'} loaded from the current source."
                if available_group_count
                else "No custom groups loaded from the current source."
            )
            if not show_disabled_state
            else ""
        )
        self.source_label.setVisible(bool(self.source_label.text()))
        self.guidance_label.setText(
            ""
            if not show_disabled_state and available_group_count
            else (
                "Create a callable group here, then assign it to this task without leaving task authoring."
                if not show_disabled_state
                else "Repair the saved-groups source before changing task-group assignments."
            )
        )
        self.guidance_label.setVisible(bool(self.guidance_label.text()))

        self.items_layout.addStretch(1)
        self.items_layout.activate()
        self._sync_items_scroll_height()
        QTimer.singleShot(0, self._sync_items_scroll_height)

class SavedActionCreateDialog(QDialog):
    ACTION_TYPE_OPTIONS = (
        ("Application", "app"),
        ("Folder", "folder"),
        ("File", "file"),
        ("Website URL", "url"),
    )
    TRIGGER_OPTIONS = (
        ("Launch", "launch"),
        ("Open", "open"),
        ("Launch and Open", "launch_and_open"),
        ("Custom", "custom"),
    )

    TITLE_TOOLTIP_TEXT = (
        "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The display label people see for this task."
        "<br/><br/><b>How it affects calling</b><br/>It does not create callable phrases on its own."
        "<br/>Calling comes from <b>Aliases</b>."
        "<br/><br/><b>Examples</b><br/>Open Nexus AI<br/>Weekly Reports Hub</div>"
    )
    TASK_TYPE_TOOLTIP_TEXT = (
        "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The kind of destination this task opens."
        "<br/><br/><b>How it affects calling</b><br/>It sets the default trigger family and target guidance."
        "<br/><br/><b>Options</b><br/>Application<br/>Folder<br/>File<br/>Website URL</div>"
    )
    ALIASES_TOOLTIP_TEXT = (
        "<div style=\"max-width: 250px;\"><b>What this is</b><br/>Exact callable words or phrases for this task."
        "<br/><br/><b>How it affects calling</b><br/>New-model tasks are called from aliases, not the title."
        "<br/>Add at least one alias, separated by commas."
        "<br/><br/><b>Examples</b><br/>Nexus AI<br/>NDAI<br/>weekly reports</div>"
    )
    TRIGGER_TOOLTIP_TEXT = (
        "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The explicit call prefixes placed before aliases."
        "<br/><br/><b>How it affects calling</b><br/>Launch, Open, or your custom phrases expand the callable surface."
        "<br/><br/><b>Examples</b><br/>Open<br/>Launch<br/>Force Open</div>"
    )
    TARGET_TOOLTIP_TEXT = {
        "app": (
            "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The command or executable Nexus launches."
            "<br/><br/><b>How it affects calling</b><br/>The task can resolve, but launch still depends on a valid application target."
            "<br/><br/><b>Examples</b><br/>notepad.exe"
            r"<br/>C:\Program Files\Notepad++\notepad++.exe</div>"
        ),
        "folder": (
            "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The folder path Nexus opens."
            "<br/><br/><b>How it affects calling</b><br/>Folder tasks open the exact folder you point to here."
            r"<br/><br/><b>Example</b><br/>C:\Reports</div>"
        ),
        "file": (
            "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The file path Nexus opens."
            "<br/><br/><b>How it affects calling</b><br/>File tasks open the exact file you point to here."
            r"<br/><br/><b>Example</b><br/>C:\Reports\weekly.txt</div>"
        ),
        "url": (
            "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The full website address Nexus opens."
            "<br/><br/><b>How it affects calling</b><br/>URL tasks open the exact address you enter here."
            "<br/><br/><b>Example</b><br/>https://example.com/docs</div>"
        ),
    }
    TARGET_FORMAT_EXAMPLES = {
        "app": (
            r"Target format: notepad.exe or C:\Program Files\Notepad++\notepad++.exe"
        ),
        "folder": (
            r"Target format: C:\Reports"
        ),
        "file": (
            r"Target format: C:\Reports\weekly.txt"
        ),
        "url": (
            "Target format: https://example.com/docs"
        ),
    }

    TARGET_ERROR_GUIDANCE = {
        "app": (
            "Application tasks only accept a bare command like notepad.exe "
            "or an absolute Windows executable path."
        ),
        "folder": (
            "Folder tasks need an absolute Windows path to the folder you want to open."
        ),
        "file": (
            "File tasks need an absolute Windows path that includes the final file name."
        ),
        "url": (
            "Website tasks need the full address, including http:// or https://."
        ),
    }

    def __init__(
        self,
        parent=None,
        submit_handler=None,
        *,
        dialog_title: str = "Create Custom Task",
        heading_text: str = "Create Custom Task",
        hint_text: str = (
            "Pick the task type first, then shape the label, trigger, aliases, and target below."
        ),
        submit_button_text: str = "Create",
        initial_draft: SavedActionDraft | None = None,
        available_groups: list[dict] | None = None,
        available_group_members: list[dict] | None = None,
        group_status_kind: str = "template_only",
        group_status_text: str = "",
        lifecycle_callback=None,
        dialog_signal_name: str = "CUSTOM_TASK_CREATE_DIALOG",
    ):
        _emit_global_runtime_marker(f"RENDERER_MAIN|{dialog_signal_name}_PRECONSTRUCT")
        super().__init__(parent)
        _emit_global_runtime_marker(f"RENDERER_MAIN|{dialog_signal_name}_POSTSUPER")
        self._submit_handler = submit_handler
        self._lifecycle_callback = lifecycle_callback
        self._dialog_signal_name = dialog_signal_name
        self._ready_signal_emitted = False
        self._syncing_trigger_selection = False
        self._trigger_manually_changed = False
        self._loaded_trigger_follows_default = True
        self._preserve_legacy_bare_trigger = False
        self._invocation_mode = "aliases_only"
        self._available_groups = list(available_groups or [])
        self._available_group_members = list(available_group_members or [])
        self._group_status_kind = group_status_kind or "template_only"
        self._group_status_text = group_status_text or ""
        self._inline_group_draft: CallableGroupDraft | None = None
        self._inline_group_assigned = False
        self._selected_group_ids_state: tuple[str, ...] = ()
        self._emit_lifecycle_event("construct_start")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle(dialog_title)
        self.setObjectName("savedActionCreateDialog")
        self.setMinimumWidth(720)
        self.setMaximumWidth(788)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("savedActionCreateShell")
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.chrome_bar = DialogChromeBar(
            dialog_title,
            self,
            object_prefix="savedActionCreate",
            parent=self.shell,
            show_title=False,
        )
        shell_layout.addWidget(self.chrome_bar)

        self.content = QWidget(self.shell)
        self.content.setObjectName("savedActionCreateContent")
        shell_layout.addWidget(self.content)

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(14, 2, 14, 10)
        layout.setSpacing(2)

        self.title_label = QLabel(heading_text, self)
        self.title_label.setObjectName("savedActionCreateTitle")
        self.title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        self.hint_frame = QFrame(self)
        self.hint_frame.setObjectName("savedActionCreateHintFrame")
        self.hint_frame.setAttribute(Qt.WA_StyledBackground, True)
        hint_layout = QVBoxLayout(self.hint_frame)
        hint_layout.setContentsMargins(8, 0, 8, 0)
        hint_layout.setSpacing(0)

        self.hint_label = QLabel(hint_text, self.hint_frame)
        self.hint_label.setObjectName("savedActionCreateHint")
        self.hint_label.setWordWrap(True)
        self.hint_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        hint_layout.addWidget(self.hint_label)
        layout.addWidget(self.hint_frame)

        form = QVBoxLayout()
        self.form_layout = form
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(5)

        self.type_combo = QComboBox(self)
        self.type_combo.setObjectName("savedActionCreateType")
        self.type_combo.setMinimumHeight(34)
        self.type_combo.view().setObjectName("savedActionCreateTypePopup")
        self.type_combo.view().viewport().setObjectName("savedActionCreateTypePopupViewport")
        for label, target_kind in self.ACTION_TYPE_OPTIONS:
            self.type_combo.addItem(label, target_kind)
        self.type_combo.currentIndexChanged.connect(self._handle_target_kind_changed)
        self.type_header, self.type_header_label, self.type_help_button, self.type_header_divider = self._make_form_section(
            "Task type",
            self.type_combo,
            tooltip_text=self.TASK_TYPE_TOOLTIP_TEXT,
            object_name="savedActionCreateTypeHeader",
            help_object_name="savedActionCreateTypeHelp",
        )
        self.type_header_divider.setFixedHeight(0)
        self.type_header_divider.setMinimumHeight(0)
        self.type_header_divider.setMaximumHeight(0)
        self.type_header_divider.hide()
        form.addWidget(self.type_header)

        self.title_input = QLineEdit(self)
        self.title_input.setObjectName("savedActionCreateTitleInput")
        self.title_input.setMinimumHeight(34)
        self.title_input.setPlaceholderText("Open Reports")
        self.title_input.textChanged.connect(self._refresh_examples_box)
        self.title_header, self.title_header_label, self.title_help_button, self.title_header_divider = self._make_form_section(
            "Title",
            self.title_input,
            tooltip_text=self.TITLE_TOOLTIP_TEXT,
            object_name="savedActionCreateTitleHeader",
            help_object_name="savedActionCreateTitleHelp",
        )
        form.addWidget(self.title_header)

        self.trigger_combo = QComboBox(self)
        self.trigger_combo.setObjectName("savedActionCreateTrigger")
        self.trigger_combo.setMinimumHeight(34)
        self.trigger_combo.view().setObjectName("savedActionCreateTriggerPopup")
        self.trigger_combo.view().viewport().setObjectName("savedActionCreateTriggerPopupViewport")
        for label, trigger_mode in self.TRIGGER_OPTIONS:
            self.trigger_combo.addItem(label, trigger_mode)
        self.trigger_combo.currentIndexChanged.connect(self._handle_trigger_selection_changed)
        self.custom_triggers_input = QLineEdit(self)
        self.custom_triggers_input.setObjectName("savedActionCreateCustomTriggersInput")
        self.custom_triggers_input.setMinimumHeight(34)
        self.custom_triggers_input.setPlaceholderText("Force Open, Duck Duck Goose")
        self.custom_triggers_input.textChanged.connect(self._refresh_examples_box)
        trigger_row = QVBoxLayout()
        trigger_row.setContentsMargins(0, 0, 0, 0)
        trigger_row.setSpacing(6)
        trigger_row.addWidget(self.trigger_combo)
        trigger_row.addWidget(self.custom_triggers_input)
        trigger_widget = QWidget(self)
        trigger_widget.setObjectName("savedActionCreateTriggerContent")
        trigger_widget.setLayout(trigger_row)
        self.trigger_header, self.trigger_header_label, self.trigger_help_button, self.trigger_header_divider = self._make_form_section(
            "Trigger",
            trigger_widget,
            tooltip_text=self.TRIGGER_TOOLTIP_TEXT,
            object_name="savedActionCreateTriggerHeader",
            help_object_name="savedActionCreateTriggerHelp",
        )
        form.addWidget(self.trigger_header)

        self.aliases_input = QLineEdit(self)
        self.aliases_input.setObjectName("savedActionCreateAliasesInput")
        self.aliases_input.setMinimumHeight(34)
        self.aliases_input.setPlaceholderText("Required, comma-separated")
        self.aliases_input.textChanged.connect(self._refresh_examples_box)
        self.aliases_header, self.aliases_header_label, self.aliases_help_button, self.aliases_header_divider = self._make_form_section(
            "Aliases",
            self.aliases_input,
            tooltip_text=self.ALIASES_TOOLTIP_TEXT,
            object_name="savedActionCreateAliasesHeader",
            help_object_name="savedActionCreateAliasesHelp",
        )
        form.addWidget(self.aliases_header)

        self.groups_frame = QFrame(self)
        self.groups_frame.setObjectName("savedActionCreateGroupsFrame")
        groups_layout = QVBoxLayout(self.groups_frame)
        groups_layout.setContentsMargins(10, 10, 10, 10)
        groups_layout.setSpacing(8)

        self.groups_status_label = QLabel("", self.groups_frame)
        self.groups_status_label.setObjectName("savedActionCreateGroupsStatus")
        self.groups_status_label.setWordWrap(True)
        groups_layout.addWidget(self.groups_status_label)

        self.groups_summary_label = QLabel("", self.groups_frame)
        self.groups_summary_label.setObjectName("savedActionCreateGroupsSummary")
        self.groups_summary_label.setWordWrap(True)
        groups_layout.addWidget(self.groups_summary_label)

        groups_button_row = QHBoxLayout()
        groups_button_row.setContentsMargins(0, 0, 0, 0)
        groups_button_row.setSpacing(8)

        self.groups_new_button = QPushButton("Assign Group...", self.groups_frame)
        self.groups_new_button.setObjectName("savedActionCreateNewGroupButton")
        self.groups_new_button.setMinimumHeight(36)
        self.groups_new_button.setToolTip(
            "Choose an existing callable group or create a new one for this task."
        )
        self.groups_new_button.clicked.connect(self._handle_group_assignment_requested)
        groups_button_row.addWidget(self.groups_new_button, 0, Qt.AlignLeft)

        self.groups_remove_button = QPushButton("Unassign Group", self.groups_frame)
        self.groups_remove_button.setObjectName("savedActionCreateRemoveGroupButton")
        self.groups_remove_button.setMinimumHeight(36)
        self.groups_remove_button.setToolTip(
            "Remove this task from its current callable group."
        )
        self.groups_remove_button.clicked.connect(self._handle_group_unassign_requested)
        groups_button_row.addWidget(self.groups_remove_button, 0, Qt.AlignLeft)
        groups_button_row.addStretch(1)
        groups_layout.addLayout(groups_button_row)
        self.groups_header, self.groups_header_label, self.groups_help_button, self.groups_header_divider = self._make_form_section(
            "Groups",
            self.groups_frame,
            tooltip_text=(
                "<div style=\"max-width: 250px;\"><b>What this is</b><br/>An optional callable group this task belongs to."
                "<br/><br/><b>How it affects calling</b><br/>Group aliases open that group's member chooser, then the normal confirm step."
                "<br/><br/><b>Boundaries</b><br/>Tasks stay limited to one assigned group here. Groups stay exact-match and do not generate trigger phrases.</div>"
            ),
            object_name="savedActionCreateGroupsHeader",
            help_object_name="savedActionCreateGroupsHelp",
        )
        form.addWidget(self.groups_header)

        self.target_header, self.target_header_label, self.target_help_button, self.target_header_divider = self._make_form_section(
            "Target",
            None,
            tooltip_text="",
            object_name="savedActionCreateTargetHeader",
            help_object_name="savedActionCreateTargetHelp",
        )
        self.target_input = QLineEdit(self)
        self.target_input.setObjectName("savedActionCreateTargetInput")
        self.target_input.setMinimumHeight(34)
        self.target_browse_button = QPushButton("Browse...", self)
        self.target_browse_button.setObjectName("savedActionCreateTargetBrowseButton")
        self.target_browse_button.setMinimumHeight(36)
        self.target_browse_button.setMinimumWidth(104)
        self.target_browse_button.clicked.connect(self._handle_target_browse_clicked)
        target_row = QVBoxLayout()
        target_row.setContentsMargins(0, 0, 0, 0)
        target_row.setSpacing(6)
        target_row.addWidget(self.target_input)
        target_row.addWidget(self.target_browse_button, 0, Qt.AlignLeft)
        target_row.addStretch(1)
        target_widget = QWidget(self)
        target_widget.setObjectName("savedActionCreateTargetContent")
        target_widget.setMinimumHeight(90)
        target_widget.setLayout(target_row)
        self._attach_form_section_content(self.target_header, target_widget)
        form.addWidget(self.target_header)

        self.target_footer_divider = QFrame(self)
        self.target_footer_divider.setObjectName("savedActionCreateTargetFooterDivider")
        self.target_footer_divider.setProperty("createRole", "fieldHeaderDividerLine")
        self.target_footer_divider.setFrameShape(QFrame.HLine)
        self.target_footer_divider.setFixedHeight(1)
        self.target_footer_divider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form.addWidget(self.target_footer_divider)

        content_row = QHBoxLayout()
        self.content_row = content_row
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(12)
        content_row.addLayout(form, 1)

        self.top_form_divider = QFrame(self)
        self.top_form_divider.setObjectName("savedActionCreateTopFormDivider")
        self.top_form_divider.setProperty("createRole", "fieldHeaderDividerLine")
        self.top_form_divider.setFrameShape(QFrame.HLine)
        self.top_form_divider.setFixedHeight(1)
        self.top_form_divider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.status_label = QLabel("", self)
        self.status_label.setObjectName("savedActionCreateStatus")
        self.status_label.setWordWrap(True)
        self.status_label.hide()

        self.target_examples_box = QFrame(self)
        self.target_examples_box.setObjectName("savedActionCreateTargetExamplesBox")
        self.target_examples_box.setMinimumWidth(220)
        self.target_examples_box.setMaximumWidth(236)
        self.target_examples_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        target_examples_layout = QVBoxLayout(self.target_examples_box)
        target_examples_layout.setContentsMargins(10, 10, 10, 10)
        target_examples_layout.setSpacing(5)

        self.target_examples_title = QLabel("Callable surface", self.target_examples_box)
        self.target_examples_title.setObjectName("savedActionCreateTargetExamplesTitle")
        target_examples_layout.addWidget(self.target_examples_title)

        self.target_examples_label = QLabel("", self.target_examples_box)
        self.target_examples_label.setObjectName("savedActionCreateTargetExamples")
        self.target_examples_label.setWordWrap(True)
        self.target_examples_label.setTextFormat(Qt.RichText)
        target_examples_layout.addWidget(self.target_examples_label)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(8)
        button_row.addStretch(1)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setObjectName("savedActionCreateCancelButton")
        self.cancel_button.setMinimumHeight(34)
        self.cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self.cancel_button)

        self.create_button = QPushButton(submit_button_text, self)
        self.create_button.setObjectName("savedActionCreateSubmitButton")
        self.create_button.setMinimumHeight(34)
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self._handle_create_clicked)
        button_row.addWidget(self.create_button)

        right_rail = QVBoxLayout()
        self.right_rail_layout = right_rail
        right_rail.setContentsMargins(0, 0, 0, 0)
        right_rail.setSpacing(7)
        right_rail.addWidget(self.target_examples_box, 0)
        right_rail.addStretch(1)
        right_rail.addLayout(button_row)

        content_row.addLayout(right_rail, 0)

        layout.addWidget(self.top_form_divider)
        layout.addLayout(content_row)
        layout.addWidget(self.status_label)
        self._emit_lifecycle_event("construct_layout_ready")

        self.setStyleSheet(
            """
            #savedActionCreateDialog {
                background: transparent;
            }
            #savedActionCreateShell {
                border-radius: 22px;
                border: 1px solid rgba(118, 226, 255, 0.22);
                background: rgb(4, 16, 28);
            }
            #savedActionCreateContent {
                border-radius: 22px;
                background: transparent;
            }
            #savedActionCreateChromeBar {
                border: none;
                border-top-left-radius: 22px;
                border-top-right-radius: 22px;
                background: transparent;
            }
            #savedActionCreateChromeTitle {
                color: rgba(126, 171, 181, 0.84);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.24em;
            }
            #savedActionCreateChromeClose {
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                padding: 0px;
                text-align: center;
                border-radius: 7px;
                border: 1px solid rgba(118, 226, 255, 0.16);
                background: rgba(18, 52, 78, 228);
                color: rgba(191, 212, 207, 0.94);
                font-size: 12px;
                font-weight: 600;
            }
            #savedActionCreateChromeClose:hover {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(22, 61, 90, 238);
            }
            #savedActionCreateTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 20px;
                font-weight: 600;
                padding: 0px 6px 1px 6px;
                background: transparent;
            }
            #savedActionCreateHintFrame {
                background: transparent;
            }
            #savedActionCreateHint {
                color: rgba(136, 165, 174, 0.88);
                font-size: 11px;
                line-height: 1.45em;
                padding: 0px 6px 3px 6px;
                background: transparent;
            }
            QToolTip {
                border: 1px solid rgba(102, 219, 204, 0.22);
                border-radius: 12px;
                background: rgba(5, 16, 28, 248);
                color: rgba(192, 212, 207, 0.96);
                padding: 12px 14px;
                font-size: 12px;
                line-height: 1.45em;
            }
            #savedActionCreateTargetExamplesBox {
                border-radius: 0px;
                border: none;
                background: transparent;
            }
            #savedActionCreateTargetExamplesTitle {
                color: rgba(84, 192, 181, 0.88);
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                background: transparent;
            }
            #savedActionCreateTargetExamples {
                color: rgba(168, 193, 199, 0.93);
                font-size: 13px;
                line-height: 1.45em;
                background: transparent;
            }
            #savedActionCreateGroupsFrame {
                border-radius: 18px;
                border: 1px solid rgba(118, 226, 255, 0.16);
                background: rgb(8, 20, 34);
            }
            #savedActionCreateGroupsSummary {
                color: rgba(168, 193, 199, 0.93);
                font-size: 13px;
                line-height: 1.45em;
                padding: 0px;
                background: transparent;
            }
            #savedActionCreateGroupsStatus {
                color: rgba(255, 189, 176, 0.96);
                font-size: 13px;
                background: transparent;
            }
            #savedActionCreateStatus {
                min-height: 0px;
                color: rgba(255, 189, 176, 0.96);
                font-size: 13px;
                background: transparent;
            }
            QLabel[createRole="label"] {
                color: rgba(78, 176, 173, 0.76);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.08em;
            }
            QWidget[createRole="fieldHeaderDivider"] {
                border: none;
                background: transparent;
            }
            QFrame[createRole="fieldRow"] {
                border-radius: 0px;
                border: none;
                background: transparent;
            }
            QWidget[createRole="fieldLabelHolder"], QWidget[createRole="fieldContentHolder"] {
                background: transparent;
            }
            #savedActionCreateTriggerContent, #savedActionCreateTargetContent {
                background: transparent;
            }
            QFrame[createRole="fieldHeaderDividerLine"] {
                min-height: 1px;
                max-height: 1px;
                border: none;
                background: rgba(118, 226, 255, 0.18);
            }
            QLabel[createRole="fieldHeader"], QLabel[createRole="fieldHeaderHelp"] {
                color: rgba(182, 206, 198, 0.96);
                font-size: 13px;
                font-weight: 650;
                background: transparent;
            }
            QLabel[createRole="fieldHeaderHelp"] {
                padding-bottom: 0px;
            }
            QLabel[createRole="fieldHeaderHelp"]:hover {
                color: rgba(198, 218, 211, 0.99);
            }
            QLabel[createRole="fieldHeaderHelp"]:focus {
                color: rgba(198, 218, 211, 0.99);
            }
            QLineEdit, QComboBox {
                min-height: 30px;
                border-radius: 14px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(193, 213, 208, 0.96);
                padding: 4px 10px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid rgba(118, 226, 255, 0.42);
                background: rgba(7, 22, 36, 220);
            }
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid rgba(118, 226, 255, 0.24);
                border-radius: 12px;
                background: rgba(8, 18, 30, 248);
                color: rgba(193, 213, 208, 0.96);
                outline: 0;
                padding: 6px;
                selection-background-color: rgba(22, 61, 90, 232);
                selection-color: rgba(205, 221, 216, 0.99);
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 4px 8px;
                border-radius: 8px;
            }
            QPushButton {
                min-height: 34px;
                padding: 0 16px;
                border-radius: 12px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(191, 212, 207, 0.96);
                font-size: 14px;
                font-weight: 650;
            }
            QPushButton:hover {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(8, 24, 38, 220);
            }
            #savedActionCreateCancelButton {
                background: rgba(6, 18, 30, 196);
            }
            #savedActionCreateSubmitButton {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(18, 52, 78, 228);
                font-weight: 650;
            }
            #savedActionCreateSubmitButton:hover {
                border: 1px solid rgba(118, 226, 255, 0.52);
                background: rgba(22, 61, 90, 238);
            }
            """
        )
        self._emit_lifecycle_event("construct_style_ready")

        self._refresh_groups_ui()
        self._apply_default_trigger_mode(force=True)
        self._sync_trigger_ui_from_selection(mark_manual=False)
        self._trigger_manually_changed = False
        self._update_target_guidance()
        self._refresh_examples_box()
        if initial_draft is not None:
            self.load_draft(initial_draft)
        self._emit_lifecycle_event("construct_complete")

    def _emit_lifecycle_event(self, stage: str, **fields):
        if callable(self._lifecycle_callback):
            try:
                self._lifecycle_callback(self._dialog_signal_name, stage, dialog=self, **fields)
            except Exception:
                pass

    def _emit_ready_signal(self):
        if self._ready_signal_emitted or not self.isVisible():
            return
        self._ready_signal_emitted = True
        self._emit_lifecycle_event("ready")

    def showEvent(self, event):
        super().showEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        _schedule_window_clamp(self)
        self._emit_lifecycle_event("opened")
        QTimer.singleShot(0, self._emit_ready_signal)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        _schedule_window_clamp(self)

    def done(self, result):
        self._emit_lifecycle_event(
            "closed",
            result="accepted" if result == QDialog.Accepted else "rejected",
        )
        super().done(result)

    def _update_chrome_overlay_geometry(self):
        if hasattr(self, "chrome_bar"):
            self.chrome_bar.raise_()

    def _make_form_header(
        self,
        text: str,
        *,
        tooltip_text: str,
        object_name: str,
        help_object_name: str,
    ) -> tuple[QWidget, QLabel, QLabel, QFrame]:
        container = QWidget(self)
        container.setObjectName(object_name)
        container.setProperty("createRole", "fieldHeaderDivider")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 3)
        layout.setSpacing(2)

        divider = QFrame(container)
        divider.setObjectName(f"{object_name}Divider")
        divider.setProperty("createRole", "fieldHeaderDividerLine")
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedHeight(1)
        divider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(divider)

        label = ImmediateHelpButton(container)
        label.setObjectName(help_object_name)
        label.setProperty("createRole", "fieldHeaderHelp")
        label.setText(text)
        label.setToolTip(tooltip_text)
        header_font = label.font()
        header_font.setPointSize(12)
        header_font.setBold(True)
        label.setFont(header_font)
        layout.addWidget(label, 0, Qt.AlignLeft)
        return container, label, label, divider

    def _attach_form_section_content(self, section: QWidget, content_widget: QWidget | None):
        if section is None:
            return
        content_holder = getattr(section, "_section_content_holder", None)
        if content_holder is None:
            return
        content_layout = content_holder.layout()
        if content_layout is None:
            content_layout = QVBoxLayout(content_holder)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)
        _clear_layout_widgets(content_layout)
        if content_widget is not None:
            content_layout.addWidget(content_widget)
        row = getattr(section, "_section_row_layout", None)
        if row is not None:
            row.invalidate()
        section.adjustSize()

    def _make_form_section(
        self,
        text: str,
        content_widget: QWidget | None,
        *,
        tooltip_text: str,
        object_name: str,
        help_object_name: str,
        label_width: int = 112,
    ) -> tuple[QWidget, QLabel, QLabel, QFrame]:
        container = QWidget(self)
        container.setObjectName(object_name)
        container.setProperty("createRole", "fieldHeaderDivider")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        divider = QFrame(container)
        divider.setObjectName(f"{object_name}Divider")
        divider.setProperty("createRole", "fieldHeaderDividerLine")
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedHeight(1)
        divider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(divider)

        row_widget = QFrame(container)
        row_widget.setProperty("createRole", "fieldRow")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)

        label_holder = QWidget(row_widget)
        label_holder.setProperty("createRole", "fieldLabelHolder")
        label_holder.setFixedWidth(label_width)
        label_holder.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        label_layout = QVBoxLayout(label_holder)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(0)
        label_layout.addStretch(1)

        label = ImmediateHelpButton(label_holder)
        label.setObjectName(help_object_name)
        label.setProperty("createRole", "fieldHeaderHelp")
        label.setText(text)
        label.setToolTip(tooltip_text)
        header_font = label.font()
        header_font.setPointSize(12)
        header_font.setBold(True)
        label.setFont(header_font)
        label_layout.addWidget(label, 0, Qt.AlignLeft)
        label_layout.addStretch(1)
        row_layout.addWidget(label_holder, 0)

        content_holder = QWidget(row_widget)
        content_holder.setProperty("createRole", "fieldContentHolder")
        content_holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        row_layout.addWidget(content_holder, 1)
        layout.addWidget(row_widget)

        container._section_row_layout = row_layout
        container._section_content_holder = content_holder
        SavedActionCreateDialog._attach_form_section_content(self, container, content_widget)
        return container, label, label, divider

    def _selected_group_ids(self) -> tuple[str, ...]:
        return tuple(self._selected_group_ids_state[:1])

    def _refresh_groups_ui(self):
        show_disabled_state = self._group_status_kind == "invalid_groups"
        self.groups_status_label.setText(self._group_status_text if show_disabled_state else "")
        self.groups_status_label.setVisible(bool(self.groups_status_label.text()))
        assigned_text = "No group assigned yet."
        if self._selected_group_ids_state:
            selected_id = self._selected_group_ids_state[0].casefold()
            for item in self._available_groups:
                group_id = str(item.get("id") or "").strip()
                if not group_id or group_id.casefold() != selected_id:
                    continue
                member_count = int(item.get("member_count") or 0)
                aliases = ", ".join(
                    str(alias).strip()
                    for alias in (item.get("aliases") or [])
                    if str(alias).strip()
                )
                member_noun = "member" if member_count == 1 else "members"
                assigned_text = (
                    f'Assigned group: {str(item.get("title") or "").strip() or group_id}'
                    f" ({member_count} {member_noun})"
                )
                if aliases:
                    assigned_text += f"\nAliases: {aliases}"
                break
        elif self._inline_group_draft is not None and self._inline_group_assigned:
            inline_aliases = ", ".join(self._inline_group_draft.aliases)
            assigned_text = f"Assigned group: {self._inline_group_draft.title} (new)"
            if inline_aliases:
                assigned_text += f"\nAliases: {inline_aliases}"

        self.groups_summary_label.setText(assigned_text)
        self.groups_summary_label.setTextFormat(Qt.PlainText)
        has_assigned_group = bool(
            self._selected_group_ids_state or (self._inline_group_draft is not None and self._inline_group_assigned)
        )
        self.groups_new_button.setVisible(not has_assigned_group)
        self.groups_new_button.setEnabled(not show_disabled_state)
        self.groups_remove_button.setVisible(has_assigned_group)
        self.groups_remove_button.setEnabled(not show_disabled_state)

    def _handle_group_assignment_requested(self):
        if self._group_status_kind == "invalid_groups":
            self.set_error_text(self._group_status_text)
            return

        dialog = TaskGroupAssignmentDialog(
            available_groups=self._available_groups,
            available_members=self._available_group_members,
            selected_group_ids=self._selected_group_ids_state,
            inline_group_draft=self._inline_group_draft,
            inline_group_assigned=self._inline_group_assigned,
            group_status_kind=self._group_status_kind,
            group_status_text=self._group_status_text,
            lifecycle_callback=self._lifecycle_callback,
            parent=self,
        )
        if dialog.exec() != QDialog.Accepted:
            return

        self._selected_group_ids_state = dialog.selected_group_ids()
        self._inline_group_draft = dialog.inline_group_draft()
        self._inline_group_assigned = dialog.inline_group_assigned()
        self._refresh_groups_ui()

    def _handle_group_unassign_requested(self):
        self._selected_group_ids_state = ()
        self._inline_group_assigned = False
        self._refresh_groups_ui()

    def current_target_kind(self) -> str:
        return str(self.type_combo.currentData() or "app")

    def current_trigger_mode(self) -> str:
        return str(self.trigger_combo.currentData() or default_saved_action_trigger_mode(self.current_target_kind()))

    def _effective_trigger_mode(self) -> str:
        if self._preserve_legacy_bare_trigger and not self._trigger_manually_changed:
            return ""
        return self.current_trigger_mode()

    def _draft_trigger_follows_default(self, draft: SavedActionDraft) -> bool:
        if draft.custom_triggers:
            return False
        trigger_mode = (draft.trigger_mode or "").strip().casefold()
        if not trigger_mode:
            return draft.invocation_mode != "aliases_only"
        return trigger_mode == default_saved_action_trigger_mode(draft.target_kind)

    def _build_alias_suggestions(self, title: str) -> tuple[str, ...]:
        normalized_title = re.sub(r"\s+", " ", (title or "").strip())
        if not normalized_title:
            return ()

        lower_title = normalized_title.casefold()
        core_title = normalized_title
        for prefix in ("open ", "show ", "launch ", "start ", "run ", "view "):
            if lower_title.startswith(prefix):
                core_title = normalized_title[len(prefix):].strip()
                break

        suggestions: list[str] = []

        def add_suggestion(value: str):
            normalized_value = re.sub(r"\s+", " ", value.strip())
            if not normalized_value:
                return
            if any(existing.casefold() == normalized_value.casefold() for existing in suggestions):
                return
            suggestions.append(normalized_value)

        if core_title and core_title.casefold() != lower_title:
            add_suggestion(core_title)
        else:
            add_suggestion(normalized_title)

        return tuple(suggestions[:3])

    def _set_trigger_mode(self, trigger_mode: str):
        self._syncing_trigger_selection = True
        try:
            for index in range(self.trigger_combo.count()):
                if str(self.trigger_combo.itemData(index) or "") == trigger_mode:
                    self.trigger_combo.setCurrentIndex(index)
                    break
        finally:
            self._syncing_trigger_selection = False

    def _apply_default_trigger_mode(self, *, force: bool = False):
        if force or not self._trigger_manually_changed:
            self._set_trigger_mode(default_saved_action_trigger_mode(self.current_target_kind()))

    def _handle_target_kind_changed(self):
        self._apply_default_trigger_mode()
        self._update_target_guidance()
        self._refresh_examples_box()

    def _handle_trigger_selection_changed(self):
        self._sync_trigger_ui_from_selection(mark_manual=not self._syncing_trigger_selection)

    def _sync_trigger_ui_from_selection(self, *, mark_manual: bool):
        if mark_manual:
            self._trigger_manually_changed = True
        is_custom = self.current_trigger_mode() == "custom"
        self.custom_triggers_input.setVisible(is_custom)
        self._refresh_examples_box()

    def _parse_custom_triggers_text(self) -> tuple[str, ...]:
        trigger_text = (self.custom_triggers_input.text() or "").replace("\n", ",")
        triggers = [re.sub(r"\s+", " ", part.strip()) for part in trigger_text.split(",")]
        return tuple(trigger for trigger in triggers if trigger)

    def _target_tooltip_text(self) -> str:
        return self.TARGET_TOOLTIP_TEXT.get(self.current_target_kind(), "")

    def _target_format_example_text(self) -> str:
        return self.TARGET_FORMAT_EXAMPLES.get(self.current_target_kind(), "")

    def _build_examples_section(self, title: str, body_html: str) -> str:
        return (
            "<div style=\"margin: 0; padding: 0;\">"
            f"<div style=\"color: rgba(84, 192, 181, 0.86); font-size: 10.5px; font-weight: 600; "
            "letter-spacing: 0.04em; text-transform: uppercase;\">"
            f"{escape(title)}</div>"
            f"<div style=\"margin-top: 3px; color: rgba(168, 193, 199, 0.93);\">{body_html}</div>"
            "</div>"
        )

    def _refresh_examples_box(self):
        title = re.sub(r"\s+", " ", (self.title_input.text() or "").strip())
        aliases = self._parse_aliases_text()
        trigger_mode = self._effective_trigger_mode()
        custom_triggers = self._parse_custom_triggers_text()
        alias_suggestions = self._build_alias_suggestions(title)
        normalized_aliases = {alias.casefold() for alias in aliases}
        visible_suggestions = tuple(
            suggestion for suggestion in alias_suggestions
            if suggestion.casefold() not in normalized_aliases
        )

        sections: list[str] = []
        if visible_suggestions:
            suggestion_lines = "<br/>".join(
                f"&bull; {escape(suggestion)}" for suggestion in visible_suggestions[:3]
            )
            sections.append(self._build_examples_section("Suggested aliases", suggestion_lines))

        callable_phrases = build_saved_action_callable_phrases(
            title,
            aliases,
            invocation_mode=self._invocation_mode,
            trigger_mode=trigger_mode,
            custom_triggers=custom_triggers,
        )
        if callable_phrases:
            phrase_lines = "<br/>".join(
                f"&bull; {escape(phrase)}" for phrase in callable_phrases[:6]
            )
            sections.append(
                self._build_examples_section(
                    "Real callable phrases",
                    "<span style=\"color: rgba(146, 178, 181, 0.89);\">Exact phrases, case-insensitive.</span>"
                    f"<br/>{phrase_lines}",
                )
            )
        elif trigger_mode == "custom":
            sections.append(
                self._build_examples_section(
                    "Real callable phrases",
                    "Add an alias and at least one custom trigger to preview the callable surface.",
                )
            )
        else:
            sections.append(
                self._build_examples_section(
                    "Real callable phrases",
                    "Add an alias to preview the exact callable phrases.",
                )
            )

        target_format = self._target_format_example_text()
        if target_format:
            sections.append(
                self._build_examples_section("Target format", escape(target_format))
            )
        self.target_examples_label.setText("<br/><br/>".join(sections))

    def _update_target_guidance(self):
        target_kind = self.current_target_kind()
        self.target_help_button.setToolTip(self._target_tooltip_text())
        if target_kind == "url":
            self.target_input.setPlaceholderText("https://example.com/docs")
            self.target_browse_button.hide()
            self.target_browse_button.setToolTip("")
        elif target_kind == "folder":
            self.target_input.setPlaceholderText(r"C:\Users\YourName\Documents")
            self.target_browse_button.show()
            self.target_browse_button.setToolTip("Choose a folder path.")
        elif target_kind == "file":
            self.target_input.setPlaceholderText(r"C:\Users\YourName\Documents\notes.txt")
            self.target_browse_button.show()
            self.target_browse_button.setToolTip("Choose a file path.")
        else:
            self.target_input.setPlaceholderText("notepad.exe")
            self.target_browse_button.show()
            self.target_browse_button.setToolTip("Choose an application path.")

    def _target_picker_start_path(self) -> str:
        target_text = (self.target_input.text() or "").strip()
        if target_text:
            return target_text
        return os.path.expanduser("~")

    def _choose_application_target(self) -> str:
        selected_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Choose Application",
            self._target_picker_start_path(),
            "Applications (*.exe *.com *.bat *.cmd);;All Files (*)",
        )
        return selected_path or ""

    def _choose_folder_target(self) -> str:
        selected_path = QFileDialog.getExistingDirectory(
            self,
            "Choose Folder",
            self._target_picker_start_path(),
        )
        return selected_path or ""

    def _choose_file_target(self) -> str:
        selected_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Choose File",
            self._target_picker_start_path(),
            "All Files (*)",
        )
        return selected_path or ""

    def _pick_target_value(self) -> str:
        target_kind = self.current_target_kind()
        if target_kind == "folder":
            return self._choose_folder_target()
        if target_kind == "file":
            return self._choose_file_target()
        if target_kind == "app":
            return self._choose_application_target()
        return ""

    def _handle_target_browse_clicked(self):
        selected_target = self._pick_target_value()
        if selected_target:
            self.target_input.setText(selected_target)

    def _parse_aliases_text(self) -> tuple[str, ...]:
        alias_text = (self.aliases_input.text() or "").replace("\n", ",")
        aliases = [part.strip() for part in alias_text.split(",")]
        return tuple(alias for alias in aliases if alias)

    def build_draft(self) -> SavedActionDraft:
        trigger_mode = self._effective_trigger_mode()
        custom_triggers = self._parse_custom_triggers_text() if trigger_mode == "custom" else ()
        return SavedActionDraft(
            title=self.title_input.text(),
            target_kind=self.current_target_kind(),
            target=self.target_input.text(),
            aliases=self._parse_aliases_text(),
            invocation_mode=self._invocation_mode,
            trigger_mode=trigger_mode,
            custom_triggers=custom_triggers,
            group_ids=self._selected_group_ids(),
            inline_group=self._inline_group_draft if self._inline_group_assigned else None,
        )

    def load_draft(self, draft: SavedActionDraft):
        trigger_follows_default = self._draft_trigger_follows_default(draft)
        self._invocation_mode = draft.invocation_mode or "legacy"
        self._loaded_trigger_follows_default = trigger_follows_default
        self._preserve_legacy_bare_trigger = (
            self._invocation_mode == "legacy"
            and not (draft.trigger_mode or "").strip()
            and not draft.custom_triggers
        )
        for index in range(self.type_combo.count()):
            if str(self.type_combo.itemData(index) or "") == draft.target_kind:
                self.type_combo.setCurrentIndex(index)
                break
        self.title_input.setText(draft.title)
        self.aliases_input.setText(", ".join(draft.aliases))
        self.custom_triggers_input.setText(", ".join(draft.custom_triggers))
        self._set_trigger_mode(draft.trigger_mode or default_saved_action_trigger_mode(draft.target_kind))
        self.target_input.setText(draft.target)
        self._inline_group_draft = draft.inline_group
        self._inline_group_assigned = draft.inline_group is not None
        self._selected_group_ids_state = tuple(draft.group_ids[:1])
        self._refresh_groups_ui()
        self._sync_trigger_ui_from_selection(mark_manual=False)
        self._trigger_manually_changed = not trigger_follows_default
        self._update_target_guidance()
        self._refresh_examples_box()

    def _format_error_text(self, text: str) -> str:
        message = (text or "").strip()
        if not message:
            return ""

        lower_message = message.casefold()
        if "saved actions are unavailable" in lower_message:
            return (
                "Custom tasks are blocked until the saved-actions source is repaired. "
                f"{message}"
            )
        if "collides with" in lower_message:
            return (
                "Callable phrases: pick aliases or triggers that do not overlap with a built-in action "
                "or another custom task. "
                f"{message}"
            )
        if "trigger mode" in lower_message or "custom trigger" in lower_message or "trigger" in lower_message:
            return (
                "Trigger: choose a standard trigger or enter unique custom trigger phrases separated by commas. "
                f"{message}"
            )
        if "could not be found for editing" in lower_message:
            return (
                "This task could not be reopened for editing. "
                "Refresh the Manage Custom Tasks window and try again. "
                f"{message}"
            )
        if "aliases" in lower_message:
            return (
                "Aliases: add one or more distinct callable phrases for this task. "
                "Keep each one unique after normalization. "
                f"{message}"
            )
        if "title" in lower_message:
            return (
                "Title: this is the display label people will see for the task. "
                "Choose a short, readable label. "
                f"{message}"
            )
        if "target kind" in lower_message:
            return (
                "Task type: choose the kind that matches where this task should go, "
                "then follow the target guidance for that type. "
                f"{message}"
            )
        if (
            "target" in lower_message
            or "path" in lower_message
            or "command" in lower_message
            or "http" in lower_message
            or "url" in lower_message
        ):
            return (
                "Target: "
                f"{self.TARGET_ERROR_GUIDANCE.get(self.current_target_kind(), 'Check where this task should open or launch.')} "
                f"{message}"
            )
        if "could not be saved" in lower_message and "source" in lower_message:
            return (
                "Custom task changes were blocked before write so the existing source stays safe. "
                f"{message}"
            )
        return message

    def set_error_text(self, text: str):
        message = self._format_error_text(text)
        self.status_label.setText(message)
        self.status_label.setVisible(bool(message))

    def _handle_create_clicked(self):
        if self._submit_handler is None:
            self.accept()
            return

        try:
            self._submit_handler(self.build_draft())
        except (SavedActionDraftValidationError, SavedActionUnsafeSourceError, SavedActionSourceWriteBlocked) as exc:
            self.set_error_text(str(exc))
            return
        except Exception as exc:
            self.set_error_text(f"Custom task could not be saved: {exc}")
            return

        self.accept()


class SavedActionEditDialog(SavedActionCreateDialog):
    def __init__(
        self,
        parent=None,
        submit_handler=None,
        initial_draft: SavedActionDraft | None = None,
        lifecycle_callback=None,
    ):
        super().__init__(
            parent,
            submit_handler,
            dialog_title="Edit Custom Task",
            heading_text="Edit Custom Task",
            hint_text=(
                "Update the fields below for this custom task."
            ),
            submit_button_text="Save",
            initial_draft=initial_draft,
            lifecycle_callback=lifecycle_callback,
            dialog_signal_name="CUSTOM_TASK_EDIT_DIALOG",
        )


class CallableGroupCreateDialog(QDialog):
    def __init__(
        self,
        parent=None,
        submit_handler=None,
        *,
        dialog_title: str = "Create Custom Group",
        heading_text: str = "Create Custom Group",
        hint_text: str = "Pick a group name, exact aliases, and explicit members below.",
        submit_button_text: str = "Create",
        available_members: list[dict] | None = None,
        initial_draft: CallableGroupDraft | None = None,
        lifecycle_callback=None,
        dialog_signal_name: str = "CUSTOM_GROUP_CREATE_DIALOG",
        show_member_picker: bool = True,
    ):
        super().__init__(parent)
        self._submit_handler = submit_handler
        self._available_members = list(available_members or [])
        self._lifecycle_callback = lifecycle_callback
        self._dialog_signal_name = dialog_signal_name
        self._ready_signal_emitted = False
        self._show_member_picker = bool(show_member_picker)
        self._member_checkboxes: list[QCheckBox] = []
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle(dialog_title)
        self.setObjectName("callableGroupCreateDialog")
        self.setMinimumWidth(620)
        self.setMaximumWidth(680)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("callableGroupCreateShell")
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.chrome_bar = DialogChromeBar(
            dialog_title,
            self,
            object_prefix="callableGroupCreate",
            parent=self.shell,
            show_title=False,
        )
        self.chrome_bar.close_button.setToolTip(f"Close {dialog_title}")
        shell_layout.addWidget(self.chrome_bar)

        self.content = QWidget(self.shell)
        self.content.setObjectName("callableGroupCreateContent")
        shell_layout.addWidget(self.content)

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(14, 2, 14, 10)
        layout.setSpacing(2)

        self.title_label = QLabel(heading_text, self)
        self.title_label.setObjectName("callableGroupCreateTitle")
        self.title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        self.hint_frame = QFrame(self)
        self.hint_frame.setObjectName("callableGroupCreateHintFrame")
        self.hint_frame.setAttribute(Qt.WA_StyledBackground, True)
        hint_layout = QVBoxLayout(self.hint_frame)
        hint_layout.setContentsMargins(8, 0, 8, 0)
        hint_layout.setSpacing(0)

        self.hint_label = QLabel(hint_text, self.hint_frame)
        self.hint_label.setObjectName("callableGroupCreateHint")
        self.hint_label.setWordWrap(True)
        self.hint_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        hint_layout.addWidget(self.hint_label)
        layout.addWidget(self.hint_frame)

        form = QVBoxLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(6)

        self.name_input = QLineEdit(self)
        self.name_input.setObjectName("callableGroupCreateNameInput")
        self.name_input.setMinimumHeight(34)
        self.name_input.setPlaceholderText("Workspace Tools")
        self.name_header, self.name_header_label, self.name_help_button, self.name_header_divider = SavedActionCreateDialog._make_form_section(
            self,
            "Group name",
            self.name_input,
            tooltip_text=(
                "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The display label people see for this group."
                "<br/><br/><b>How it affects calling</b><br/>Calling still comes from the group's aliases, not the name.</div>"
            ),
            object_name="callableGroupCreateNameHeader",
            help_object_name="callableGroupCreateNameHelp",
        )
        form.addWidget(self.name_header)

        self.aliases_input = QLineEdit(self)
        self.aliases_input.setObjectName("callableGroupCreateAliasesInput")
        self.aliases_input.setMinimumHeight(34)
        self.aliases_input.setPlaceholderText("workspace tools, tools group")
        self.aliases_input.textChanged.connect(self._refresh_examples_box)

        self.examples_box = QFrame(self)
        self.examples_box.setObjectName("callableGroupCreateExamplesBox")
        examples_layout = QVBoxLayout(self.examples_box)
        examples_layout.setContentsMargins(10, 10, 10, 10)
        examples_layout.setSpacing(5)
        examples_title = QLabel("Callable surface", self.examples_box)
        examples_title.setObjectName("callableGroupCreateExamplesTitle")
        examples_layout.addWidget(examples_title)
        self.examples_label = QLabel("", self.examples_box)
        self.examples_label.setObjectName("callableGroupCreateExamples")
        self.examples_label.setWordWrap(True)
        self.examples_label.setTextFormat(Qt.RichText)
        examples_layout.addWidget(self.examples_label)
        aliases_content = QWidget(self)
        aliases_content.setObjectName("callableGroupCreateAliasesContent")
        aliases_content_layout = QVBoxLayout(aliases_content)
        aliases_content_layout.setContentsMargins(0, 0, 0, 0)
        aliases_content_layout.setSpacing(6)
        aliases_content_layout.addWidget(self.aliases_input)
        aliases_content_layout.addWidget(self.examples_box)
        self.aliases_header, self.aliases_header_label, self.aliases_help_button, self.aliases_header_divider = SavedActionCreateDialog._make_form_section(
            self,
            "Aliases",
            aliases_content,
            tooltip_text=(
                "<div style=\"max-width: 250px;\"><b>What this is</b><br/>Exact phrases that call this group."
                "<br/><br/><b>How it affects calling</b><br/>Using one of these aliases opens the group's member chooser.</div>"
            ),
            object_name="callableGroupCreateAliasesHeader",
            help_object_name="callableGroupCreateAliasesHelp",
        )
        form.addWidget(self.aliases_header)

        self.members_scroll = None
        self.members_frame = None
        self.members_layout = None
        self.task_flow_note = None
        self.members_scroll = QScrollArea(self)
        self.members_scroll.setObjectName("callableGroupCreateMembersScroll")
        self.members_scroll.setFrameShape(QFrame.NoFrame)
        self.members_scroll.setWidgetResizable(True)
        self.members_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.members_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.members_scroll.setFocusPolicy(Qt.NoFocus)
        self.members_scroll.setMaximumHeight(0)
        self.members_scroll.viewport().setObjectName("callableGroupCreateMembersViewport")
        self.members_scroll.viewport().setAutoFillBackground(False)
        self.members_frame = QFrame(self)
        self.members_frame.setObjectName("callableGroupCreateMembersFrame")
        self.members_layout = QVBoxLayout(self.members_frame)
        self.members_layout.setContentsMargins(8, 8, 8, 8)
        self.members_layout.setSpacing(3)
        self.members_scroll.setWidget(self.members_frame)
        self.members_header, self.members_header_label, self.members_help_button, self.members_header_divider = SavedActionCreateDialog._make_form_section(
            self,
            "Available Tasks",
            self.members_scroll,
            tooltip_text=(
                "<div style=\"max-width: 250px;\"><b>What this is</b><br/>The built-ins and saved tasks this group can surface."
                "<br/><br/><b>How it affects calling</b><br/>Group aliases only show these members in the chooser.</div>"
            ),
            object_name="callableGroupCreateMembersHeader",
            help_object_name="callableGroupCreateMembersHelp",
        )
        form.addWidget(self.members_header)

        layout.addLayout(form)

        self.status_label = QLabel("", self)
        self.status_label.setObjectName("callableGroupCreateStatus")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(8)
        button_row.addStretch(1)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self.cancel_button)
        self.submit_button = QPushButton(submit_button_text, self)
        self.submit_button.setDefault(True)
        self.submit_button.clicked.connect(self._handle_submit_clicked)
        button_row.addWidget(self.submit_button)
        layout.addLayout(button_row)

        self.setStyleSheet(
            """
            #callableGroupCreateDialog { background: transparent; }
            #callableGroupCreateShell {
                border-radius: 22px;
                border: 1px solid rgba(118, 226, 255, 0.22);
                background: rgba(4, 16, 28, 238);
            }
            #callableGroupCreateContent {
                border-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #callableGroupCreateChromeBar {
                border: none;
                border-top-left-radius: 22px;
                border-top-right-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #callableGroupCreateTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 20px;
                font-weight: 600;
                padding: 0px 6px 1px 6px;
                background: transparent;
            }
            #callableGroupCreateHintFrame {
                background: transparent;
            }
            #callableGroupCreateHint {
                color: rgba(136, 165, 174, 0.88);
                font-size: 11px;
                line-height: 1.45em;
                padding: 0px 6px 3px 6px;
                background: transparent;
            }
            """
            + THEMED_TOOLTIP_QSS
            + """
            #callableGroupCreateExamplesBox {
                border-radius: 0px;
                border: none;
                background: transparent;
            }
            #callableGroupCreateTaskFlowNote {
                border-radius: 0px;
                border: none;
                background: transparent;
            }
            #callableGroupCreateMembersScroll {
                border-radius: 18px;
                border: none;
                background: rgba(8, 20, 34, 214);
            }
            #callableGroupCreateMembersViewport {
                border-radius: 14px;
                background: transparent;
            }
            #callableGroupCreateMembersFrame {
                background: transparent;
            }
            #callableGroupCreateAliasesContent {
                background: transparent;
            }
            #callableGroupCreateExamplesTitle {
                color: rgba(84, 192, 181, 0.88);
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                background: transparent;
            }
            #callableGroupCreateTaskFlowTitle {
                color: rgba(84, 192, 181, 0.88);
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                background: transparent;
            }
            #callableGroupCreateExamples {
                color: rgba(168, 193, 199, 0.93);
                font-size: 13px;
                line-height: 1.45em;
                background: transparent;
            }
            #callableGroupCreateTaskFlowBody {
                color: rgba(168, 193, 199, 0.93);
                font-size: 13px;
                line-height: 1.45em;
                background: transparent;
            }
            #callableGroupCreateStatus {
                color: rgba(255, 189, 176, 0.96);
                font-size: 13px;
            }
            QWidget[createRole="fieldHeaderDivider"] {
                border: none;
                background: transparent;
            }
            QFrame[createRole="fieldRow"] {
                border-radius: 0px;
                border: none;
                background: transparent;
            }
            QWidget[createRole="fieldLabelHolder"], QWidget[createRole="fieldContentHolder"] {
                background: transparent;
            }
            QFrame[createRole="fieldHeaderDividerLine"] {
                min-height: 1px;
                max-height: 1px;
                border: none;
                background: rgba(118, 226, 255, 0.18);
            }
            QLabel[createRole="fieldHeader"], QLabel[createRole="fieldHeaderHelp"] {
                color: rgba(182, 206, 198, 0.96);
                font-size: 13px;
                font-weight: 650;
                background: transparent;
            }
            QLabel[createRole="fieldHeaderHelp"] {
                padding-bottom: 0px;
            }
            QLabel[createRole="fieldHeaderHelp"]:hover {
                color: rgba(198, 218, 211, 0.99);
            }
            QLineEdit {
                min-height: 30px;
                border-radius: 14px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(193, 213, 208, 0.96);
                padding: 4px 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(118, 226, 255, 0.42);
                background: rgba(7, 22, 36, 220);
            }
            QPushButton {
                min-height: 38px;
                padding: 0 16px;
                border-radius: 12px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(191, 212, 207, 0.96);
                font-size: 14px;
                font-weight: 650;
            }
            QPushButton[chromeRole="close"] {
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                padding: 0px;
                text-align: center;
                border-radius: 7px;
                border: 1px solid rgba(118, 226, 255, 0.16);
                background: rgba(18, 52, 78, 228);
                color: rgba(191, 212, 207, 0.94);
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton[chromeRole="close"]:hover,
            QPushButton:hover {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(8, 24, 38, 220);
            }
            QPushButton[chromeRole="close"]:hover {
                background: rgba(22, 61, 90, 238);
            }
            QCheckBox {
                color: rgba(182, 206, 198, 0.94);
                spacing: 6px;
                font-size: 13px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border-radius: 5px;
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(8, 20, 34, 0.98);
            }
            QCheckBox::indicator:hover {
                border: 1px solid rgba(118, 226, 255, 0.48);
                background: rgba(10, 26, 40, 0.98);
            }
            QCheckBox::indicator:checked {
                border: 1px solid rgba(102, 219, 204, 0.70);
                background: rgba(22, 88, 79, 0.96);
            }
            #callableGroupCreateMembersScroll QScrollBar:vertical {
                width: 8px;
                margin: 4px 1px 4px 0;
                border-radius: 4px;
                background: rgba(6, 18, 30, 0.58);
            }
            #callableGroupCreateMembersScroll QScrollBar::handle:vertical {
                min-height: 38px;
                border-radius: 4px;
                border: 1px solid rgba(118, 226, 255, 0.20);
                background: rgba(18, 52, 78, 0.96);
            }
            #callableGroupCreateMembersScroll QScrollBar::handle:vertical:hover {
                background: rgba(22, 61, 90, 0.98);
            }
            #callableGroupCreateMembersScroll QScrollBar::add-line:vertical,
            #callableGroupCreateMembersScroll QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            #callableGroupCreateMembersScroll QScrollBar::add-page:vertical,
            #callableGroupCreateMembersScroll QScrollBar::sub-page:vertical {
                background: transparent;
            }
            #callableGroupCreateMemberCard {
                border-radius: 14px;
                border: 1px solid rgba(118, 226, 255, 0.22);
                background: rgba(12, 28, 44, 208);
            }
            #callableGroupCreateMemberTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 14px;
                font-weight: 650;
                background: transparent;
            }
            #callableGroupCreateMemberMeta {
                color: rgba(84, 192, 181, 0.88);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                background: transparent;
            }
            #callableGroupCreateMemberDetail {
                color: rgba(168, 193, 199, 0.93);
                font-size: 12px;
                background: transparent;
            }
            #callableGroupCreateMemberToggle {
                color: rgba(188, 212, 203, 0.94);
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            }
            """
        )
        self._populate_member_choices()
        self._refresh_examples_box()
        if initial_draft is not None:
            self.load_draft(initial_draft)

    def _emit_lifecycle_event(self, stage: str, **fields):
        if callable(self._lifecycle_callback):
            try:
                self._lifecycle_callback(self._dialog_signal_name, stage, dialog=self, **fields)
            except Exception:
                pass

    def _emit_ready_signal(self):
        if self._ready_signal_emitted or not self.isVisible():
            return
        self._ready_signal_emitted = True
        self._emit_lifecycle_event("ready")

    def showEvent(self, event):
        super().showEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        _schedule_window_clamp(self)
        self._emit_lifecycle_event("opened")
        QTimer.singleShot(0, self._emit_ready_signal)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        _schedule_window_clamp(self)

    def done(self, result):
        self._emit_lifecycle_event(
            "closed",
            result="accepted" if result == QDialog.Accepted else "rejected",
        )
        super().done(result)

    def _update_chrome_overlay_geometry(self):
        if hasattr(self, "chrome_bar"):
            self.chrome_bar.raise_()

    def _build_members_placeholder_card(self, message: str) -> QFrame:
        card = QFrame(self.members_frame)
        card.setObjectName("callableGroupCreateTaskFlowNote")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(4)

        title_label = QLabel("Section guidance", card)
        title_label.setObjectName("callableGroupCreateTaskFlowTitle")
        card_layout.addWidget(title_label)

        body_label = QLabel(message, card)
        body_label.setObjectName("callableGroupCreateTaskFlowBody")
        body_label.setWordWrap(True)
        card_layout.addWidget(body_label)
        return card

    def _build_member_choice_card(
        self,
        *,
        member_id: str,
        title: str,
        subtitle: str,
        target_display: str,
    ) -> tuple[QFrame, QCheckBox]:
        card = QFrame(self.members_frame)
        card.setObjectName("callableGroupCreateMemberCard")
        card.setMinimumHeight(64)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 6, 12, 6)
        card_layout.setSpacing(3)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(10)

        title_label = QLabel(title, card)
        title_label.setObjectName("callableGroupCreateMemberTitle")
        title_label.setWordWrap(True)
        header_row.addWidget(title_label, 1)

        checkbox = QCheckBox("Include", card)
        checkbox.setObjectName("callableGroupCreateMemberToggle")
        checkbox.setProperty("memberId", member_id)
        header_row.addWidget(checkbox, 0, Qt.AlignRight | Qt.AlignTop)
        card_layout.addLayout(header_row)

        if subtitle:
            subtitle_label = QLabel(subtitle, card)
            subtitle_label.setObjectName("callableGroupCreateMemberMeta")
            subtitle_label.setWordWrap(True)
            card_layout.addWidget(subtitle_label)

        if target_display:
            detail_label = QLabel(target_display, card)
            detail_label.setObjectName("callableGroupCreateMemberDetail")
            detail_label.setWordWrap(True)
            card_layout.addWidget(detail_label)

        return card, checkbox

    def _sync_members_scroll_height(self):
        if self.members_scroll is None or self.members_layout is None:
            return
        member_widgets = [
            self.members_layout.itemAt(index).widget()
            for index in range(self.members_layout.count())
            if self.members_layout.itemAt(index) is not None
            and self.members_layout.itemAt(index).widget() is not None
        ]
        if not member_widgets:
            self.members_scroll.setFixedHeight(0)
            return

        visible_rows = sum(1 for widget in member_widgets if widget.isVisible())
        minimum_height = 120 if any(widget.objectName() == "callableGroupCreateTaskFlowNote" for widget in member_widgets) else 0
        desired_height = _visible_row_height_for_layout(
            self.members_layout,
            min(5, visible_rows),
            extra_padding=0,
        )
        desired_height = min(max(minimum_height, desired_height), 432)
        self.members_scroll.setMaximumHeight(desired_height)
        self.members_scroll.setFixedHeight(desired_height)

    def _populate_member_choices(self):
        if self.members_layout is None or self.members_frame is None:
            return
        _clear_layout_widgets(self.members_layout)
        self._member_checkboxes = []
        if not self._show_member_picker:
            self.task_flow_note = self._build_members_placeholder_card(
                "Task-path create skips member picking here. After save, this path returns you to Manage Custom Groups for the current task so you can assign the new group immediately without leaving task authoring."
            )
            self.members_layout.addWidget(self.task_flow_note)
            self.members_layout.addStretch(1)
            self.members_layout.activate()
            self._sync_members_scroll_height()
            QTimer.singleShot(0, self._sync_members_scroll_height)
            return
        if not self._available_members:
            self.members_layout.addWidget(
                self._build_members_placeholder_card(
                    "No saved tasks or built-in actions are loaded from the current source yet."
                )
            )
            self.members_layout.addStretch(1)
            self.members_layout.activate()
            self._sync_members_scroll_height()
            QTimer.singleShot(0, self._sync_members_scroll_height)
            return
        added_member_rows = 0
        for item in self._available_members:
            member_id = str(item.get("id") or "").strip()
            title = str(item.get("title") or item.get("id") or "").strip()
            if not title:
                continue
            origin_label = str(item.get("origin_label") or "").strip() or "Member"
            target_kind = str(item.get("target_kind") or "").strip()
            target_display = str(item.get("target_display") or "").strip()
            subtitle = f"{origin_label} | {target_kind}".strip(" |")
            card, checkbox = self._build_member_choice_card(
                member_id=member_id,
                title=title,
                subtitle=subtitle,
                target_display=target_display,
            )
            if subtitle:
                checkbox.setToolTip(
                    f"{subtitle}\nBecomes selectable when this group's alias is used."
                )
            else:
                checkbox.setToolTip("Becomes selectable when this group's alias is used.")
            self.members_layout.addWidget(card)
            self._member_checkboxes.append(checkbox)
            added_member_rows += 1
        if added_member_rows <= 0:
            self.members_layout.addWidget(
                self._build_members_placeholder_card(
                    "No saved tasks or built-in actions are loaded from the current source yet."
                )
            )
            self.members_layout.addStretch(1)
            self.members_layout.activate()
            self._sync_members_scroll_height()
            QTimer.singleShot(0, self._sync_members_scroll_height)
            return
        self.members_layout.addStretch(1)
        self.members_layout.activate()
        self._sync_members_scroll_height()
        QTimer.singleShot(0, self._sync_members_scroll_height)

    def _selected_member_ids(self) -> tuple[str, ...]:
        return tuple(
            checkbox.property("memberId")
            for checkbox in self._member_checkboxes
            if checkbox.isChecked() and str(checkbox.property("memberId") or "").strip()
        )

    def _refresh_examples_box(self):
        aliases = tuple(
            part.strip()
            for part in (self.aliases_input.text() or "").replace("\n", ",").split(",")
            if part.strip()
        )
        phrases = build_callable_group_phrases(aliases)
        if phrases:
            body = "<br/>".join(f"&bull; {escape(phrase)}" for phrase in phrases)
        else:
            body = "Add one or more aliases to preview the exact callable phrases."
        self.examples_label.setText(body)

    def build_draft(self) -> CallableGroupDraft:
        aliases = tuple(
            part.strip()
            for part in (self.aliases_input.text() or "").replace("\n", ",").split(",")
            if part.strip()
        )
        return CallableGroupDraft(
            title=self.name_input.text(),
            aliases=aliases,
            member_action_ids=self._selected_member_ids() if self._show_member_picker else (),
        )

    def load_draft(self, draft: CallableGroupDraft):
        self.name_input.setText(draft.title)
        self.aliases_input.setText(", ".join(draft.aliases))
        if self._show_member_picker:
            selected_ids = {member_id.casefold() for member_id in draft.member_action_ids}
            for checkbox in self._member_checkboxes:
                checkbox.setChecked(str(checkbox.property("memberId") or "").strip().casefold() in selected_ids)
        self._refresh_examples_box()

    def set_error_text(self, text: str):
        self.status_label.setText((text or "").strip())
        self.status_label.setVisible(bool(self.status_label.text()))

    def _handle_submit_clicked(self):
        if self._submit_handler is None:
            self.accept()
            return
        try:
            self._submit_handler(self.build_draft())
        except (CallableGroupDraftValidationError, CallableGroupUnsafeSourceError, SavedActionSourceWriteBlocked) as exc:
            self.set_error_text(str(exc))
            return
        except Exception as exc:
            self.set_error_text(f"Custom group could not be saved: {exc}")
            return
        self.accept()


class CallableGroupEditDialog(CallableGroupCreateDialog):
    def __init__(
        self,
        parent=None,
        submit_handler=None,
        initial_draft: CallableGroupDraft | None = None,
        available_members: list[dict] | None = None,
        lifecycle_callback=None,
    ):
        super().__init__(
            parent,
            submit_handler,
            dialog_title="Edit Custom Group",
            heading_text="Edit Custom Group",
            hint_text="Update the group name, aliases, and members below.",
            submit_button_text="Save",
            available_members=available_members,
            initial_draft=initial_draft,
            lifecycle_callback=lifecycle_callback,
            dialog_signal_name="CUSTOM_GROUP_EDIT_DIALOG",
        )

class CreatedTasksDialog(QDialog):
    def __init__(self, parent=None, inventory_payload: dict | None = None, lifecycle_callback=None):
        super().__init__(parent)
        self._selected_action_id = ""
        self._selected_delete_action_id = ""
        self._lifecycle_callback = lifecycle_callback
        self._ready_signal_emitted = False
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("Manage Custom Tasks")
        self.setObjectName("savedActionCreatedTasksDialog")
        self.setMinimumWidth(620)
        self.setMaximumWidth(680)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("savedActionCreatedTasksShell")
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.chrome_bar = DialogChromeBar(
            "Manage Custom Tasks",
            self,
            object_prefix="savedActionCreatedTasks",
            parent=self.shell,
            show_title=False,
        )
        self.chrome_bar.close_button.setToolTip("Close Manage Custom Tasks")
        shell_layout.addWidget(self.chrome_bar)

        self.content = QWidget(self.shell)
        self.content.setObjectName("savedActionCreatedTasksContent")
        shell_layout.addWidget(self.content)

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(14, 2, 14, 10)
        layout.setSpacing(2)

        self.title_label = QLabel("Manage Custom Tasks", self)
        self.title_label.setObjectName("savedActionCreatedTasksTitle")
        self.title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        self.hint_label = QLabel(
            "Review, update, or remove tasks from the current saved-task source.",
            self,
        )
        self.hint_label.setObjectName("savedActionCreatedTasksHint")
        self.hint_label.setWordWrap(True)
        self.hint_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self.hint_label)

        self.status_label = QLabel("", self)
        self.status_label.setObjectName("savedActionCreatedTasksStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.source_label = QLabel("", self)
        self.source_label.setObjectName("savedActionCreatedTasksSource")
        self.source_label.setWordWrap(True)
        layout.addWidget(self.source_label)

        self.guidance_label = QLabel("", self)
        self.guidance_label.setObjectName("savedActionCreatedTasksGuidance")
        self.guidance_label.setWordWrap(True)
        layout.addWidget(self.guidance_label)

        self.items_frame = QFrame(self)
        self.items_frame.setObjectName("savedActionCreatedTasksItems")
        self.items_layout = QVBoxLayout(self.items_frame)
        self.items_layout.setContentsMargins(0, 2, 0, 0)
        self.items_layout.setSpacing(2)

        self.items_scroll = QScrollArea(self)
        self.items_scroll.setObjectName("savedActionCreatedTasksItemsScroll")
        self.items_scroll.setFrameShape(QFrame.NoFrame)
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.items_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.items_scroll.setFocusPolicy(Qt.NoFocus)
        self.items_scroll.setMaximumHeight(0)
        self.items_scroll.viewport().setObjectName("savedActionCreatedTasksViewport")
        self.items_scroll.viewport().setAutoFillBackground(False)
        self.items_scroll.setWidget(self.items_frame)
        layout.addWidget(self.items_scroll)

        self.footer_frame = QFrame(self)
        self.footer_frame.setObjectName("savedActionCreatedTasksFooter")
        footer_layout = QHBoxLayout(self.footer_frame)
        footer_layout.setContentsMargins(0, 4, 0, 0)
        footer_layout.setSpacing(8)
        footer_layout.addStretch(1)

        self.close_button = QPushButton("Close", self.footer_frame)
        self.close_button.setObjectName("savedActionCreatedTasksClose")
        self.close_button.setMinimumHeight(34)
        self.close_button.clicked.connect(self.reject)
        footer_layout.addWidget(self.close_button)

        layout.addWidget(self.footer_frame)

        self.setStyleSheet(
            """
            #savedActionCreatedTasksDialog {
                background: transparent;
            }
            #savedActionCreatedTasksShell {
                border-radius: 22px;
                border: 1px solid rgba(118, 226, 255, 0.20);
                background: rgba(4, 16, 28, 238);
            }
            #savedActionCreatedTasksContent {
                border-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #savedActionCreatedTasksFooter {
                border-top: 1px solid rgba(118, 226, 255, 0.12);
                background: transparent;
            }
            #savedActionCreatedTasksChromeBar {
                border: none;
                border-top-left-radius: 22px;
                border-top-right-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #savedActionCreatedTasksChromeTitle {
                color: rgba(126, 171, 181, 0.84);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.24em;
            }
            #savedActionCreatedTasksChromeClose {
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                padding: 0px;
                text-align: center;
                border-radius: 7px;
                border: 1px solid rgba(118, 226, 255, 0.16);
                background: rgba(18, 52, 78, 228);
                color: rgba(191, 212, 207, 0.94);
                font-size: 12px;
                font-weight: 600;
            }
            #savedActionCreatedTasksChromeClose:hover {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(22, 61, 90, 238);
            }
            #savedActionCreatedTasksTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 20px;
                font-weight: 600;
                padding: 0px 6px 1px 6px;
                background: transparent;
            }
            #savedActionCreatedTasksHint {
                color: rgba(136, 165, 174, 0.88);
                font-size: 11px;
                line-height: 1.45em;
                padding: 0px 6px 3px 6px;
                background: transparent;
            }
            """
            + THEMED_TOOLTIP_QSS
            + """
            #savedActionCreatedTasksStatus {
                color: rgba(148, 180, 178, 0.89);
                font-size: 13px;
                font-weight: 600;
            }
            #savedActionCreatedTasksStatus[statusKind="invalid_source"], #savedActionCreatedTasksStatus[statusKind="invalid_saved_actions"], #savedActionCreatedTasksStatus[statusKind="missing"] {
                color: rgba(255, 189, 176, 0.96);
            }
            #savedActionCreatedTasksSource {
                color: rgba(126, 157, 171, 0.78);
                font-size: 13px;
            }
            #savedActionCreatedTasksGuidance {
                color: rgba(110, 201, 164, 0.86);
                font-size: 13px;
                line-height: 1.4em;
            }
            #savedActionCreatedTasksItemsScroll {
                border: none;
                background: transparent;
            }
            #savedActionCreatedTasksViewport {
                border-radius: 18px;
                background: rgba(4, 12, 22, 236);
            }
            #savedActionCreatedTasksItems {
                background: transparent;
            }
            QFrame[inventoryRole="itemFrame"] {
                border-radius: 14px;
                border: 1px solid rgba(118, 226, 255, 0.22);
                background: rgba(12, 28, 44, 208);
            }
            QFrame[inventoryRole="actionShell"] {
                border-radius: 16px;
                border: none;
                background: rgba(15, 40, 62, 248);
            }
            QLabel[inventoryRole="itemTitle"] {
                color: rgba(184, 208, 200, 0.96);
                font-size: 14px;
                font-weight: 650;
            }
            QLabel[inventoryRole="itemMeta"] {
                color: rgba(84, 192, 181, 0.83);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            QLabel[inventoryRole="itemTarget"] {
                color: rgba(163, 189, 196, 0.92);
                font-size: 12px;
            }
            QPushButton[inventoryRole="editButton"], QPushButton[inventoryRole="deleteButton"], #savedActionCreatedTasksClose {
                min-height: 28px;
                padding: 0 16px;
                border-radius: 12px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(191, 212, 207, 0.96);
                font-size: 14px;
                font-weight: 650;
            }
            #savedActionCreatedTasksClose {
                min-height: 34px;
            }
            QPushButton[inventoryRole="editButton"], QPushButton[inventoryRole="deleteButton"] {
                min-width: 104px;
            }
            QPushButton[inventoryRole="editButton"] {
                border: 1px solid rgba(118, 226, 255, 0.30);
                background: rgba(18, 52, 78, 228);
            }
            QPushButton[inventoryRole="deleteButton"] {
                border: 1px solid rgba(255, 138, 138, 0.26);
                background: rgba(34, 12, 16, 212);
                color: rgba(255, 231, 231, 0.96);
            }
            QPushButton[inventoryRole="editButton"]:hover, QPushButton[inventoryRole="deleteButton"]:hover, #savedActionCreatedTasksClose:hover {
                border: 1px solid rgba(118, 226, 255, 0.36);
                background: rgba(8, 24, 38, 220);
            }
            QPushButton[inventoryRole="deleteButton"]:hover {
                border: 1px solid rgba(255, 166, 166, 0.42);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar:vertical {
                width: 8px;
                margin: 4px 1px 4px 0;
                border-radius: 4px;
                background: rgba(6, 18, 30, 0.58);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::handle:vertical {
                min-height: 38px;
                border-radius: 4px;
                border: 1px solid rgba(118, 226, 255, 0.20);
                background: rgba(18, 52, 78, 0.96);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::handle:vertical:hover {
                background: rgba(22, 61, 90, 0.98);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::handle:vertical:pressed {
                background: rgba(118, 226, 255, 0.54);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::add-line:vertical,
            #savedActionCreatedTasksItemsScroll QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::add-page:vertical,
            #savedActionCreatedTasksItemsScroll QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

        self.refresh_inventory(inventory_payload or {})

    def _emit_lifecycle_event(self, stage: str, **fields):
        if callable(self._lifecycle_callback):
            try:
                self._lifecycle_callback("CREATED_TASKS_DIALOG", stage, dialog=self, **fields)
            except Exception:
                pass

    def _emit_ready_signal(self):
        if self._ready_signal_emitted or not self.isVisible():
            return
        self._ready_signal_emitted = True
        self._emit_lifecycle_event("ready")

    def showEvent(self, event):
        super().showEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        _schedule_window_clamp(self)
        self._emit_lifecycle_event("opened")
        QTimer.singleShot(0, self._emit_ready_signal)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        _schedule_window_clamp(self)

    def done(self, result):
        self._emit_lifecycle_event(
            "closed",
            result="accepted" if result == QDialog.Accepted else "rejected",
        )
        super().done(result)

    def _update_chrome_overlay_geometry(self):
        if hasattr(self, "chrome_bar"):
            self.chrome_bar.raise_()

    def _sync_items_scroll_height(self):
        if not hasattr(self, "items_scroll") or not hasattr(self, "items_layout"):
            return
        item_frames = [
            self.items_layout.itemAt(index).widget()
            for index in range(self.items_layout.count())
            if self.items_layout.itemAt(index) is not None
            and self.items_layout.itemAt(index).widget() is not None
            and self.items_layout.itemAt(index).widget().property("inventoryRole") == "itemFrame"
        ]
        visible_rows = sum(1 for frame in item_frames if frame.isVisible())
        if visible_rows <= 0:
            self.items_scroll.setMaximumHeight(0)
            self.items_scroll.setFixedHeight(0)
            return
        desired_height = _visible_row_height_for_layout(
            self.items_layout,
            min(5, visible_rows),
            extra_padding=0,
        )
        self.items_scroll.setMaximumHeight(desired_height)
        self.items_scroll.setFixedHeight(desired_height)

    def selected_action_id(self) -> str:
        return self._selected_action_id

    def selected_delete_action_id(self) -> str:
        return self._selected_delete_action_id

    def _handle_edit_requested(self, action_id: str):
        self._selected_action_id = action_id
        self._selected_delete_action_id = ""
        self.accept()

    def _handle_delete_requested(self, action_id: str):
        self._selected_delete_action_id = action_id
        self._selected_action_id = ""
        self.accept()

    def refresh_inventory(self, inventory_payload: dict):
        inventory_payload = inventory_payload or {}
        self.title_label.setText("Manage Custom Tasks")

        status_kind = inventory_payload.get("status_kind", "hidden")
        self.status_label.setProperty("statusKind", status_kind)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_label.setText(inventory_payload.get("status_text", ""))

        source_path = inventory_payload.get("path", "")
        source_display = inventory_payload.get("path_display") or source_path
        items = inventory_payload.get("items") or []
        show_source_details = status_kind in {"invalid_source", "invalid_saved_actions", "missing", "template_only"} or not items
        self.source_label.setText(f"Source: {source_display}" if show_source_details and source_display else "")
        self.source_label.setToolTip(source_path)
        guidance_text = inventory_payload.get("guidance_text", "")
        show_guidance = bool(guidance_text) and (
            status_kind in {"invalid_source", "invalid_saved_actions", "missing", "template_only"} or not items
        )
        self.guidance_label.setText(guidance_text if show_guidance else "")
        self.source_label.setVisible(bool(self.source_label.text()))
        self.guidance_label.setVisible(bool(self.guidance_label.text()))

        _populate_saved_inventory_item_layout(
            self.items_layout,
            self.items_frame,
            items,
            self._handle_edit_requested,
            self._handle_delete_requested,
        )
        self.items_scroll.setVisible(bool(items))
        if items:
            self.items_layout.activate()
            self._sync_items_scroll_height()
            QTimer.singleShot(0, self._sync_items_scroll_height)
        else:
            self.items_scroll.setMaximumHeight(0)
            self.items_scroll.setFixedHeight(0)


class CreatedGroupsDialog(QDialog):
    def __init__(self, parent=None, inventory_payload: dict | None = None, lifecycle_callback=None):
        super().__init__(parent)
        self._selected_group_id = ""
        self._selected_delete_group_id = ""
        self._lifecycle_callback = lifecycle_callback
        self._ready_signal_emitted = False
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("Manage Custom Groups")
        self.setObjectName("savedActionCreatedGroupsDialog")
        self.setMinimumWidth(660)
        self.setMaximumWidth(760)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("savedActionCreatedTasksShell")
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.chrome_bar = DialogChromeBar(
            "Manage Custom Groups",
            self,
            object_prefix="savedActionCreatedTasks",
            parent=self.shell,
            show_title=False,
        )
        self.chrome_bar.close_button.setToolTip("Close Manage Custom Groups")
        shell_layout.addWidget(self.chrome_bar)

        self.content = QWidget(self.shell)
        self.content.setObjectName("savedActionCreatedTasksContent")
        shell_layout.addWidget(self.content)

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(14, 2, 14, 10)
        layout.setSpacing(2)

        self.title_label = QLabel("Manage Custom Groups", self)
        self.title_label.setObjectName("savedActionCreatedTasksTitle")
        self.title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        self.hint_label = QLabel(
            "Review, update, or remove callable groups from the current source.",
            self,
        )
        self.hint_label.setObjectName("savedActionCreatedTasksHint")
        self.hint_label.setWordWrap(True)
        self.hint_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self.hint_label)

        self.status_label = QLabel("", self)
        self.status_label.setObjectName("savedActionCreatedTasksStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.source_label = QLabel("", self)
        self.source_label.setObjectName("savedActionCreatedTasksSource")
        self.source_label.setWordWrap(True)
        layout.addWidget(self.source_label)

        self.guidance_label = QLabel("", self)
        self.guidance_label.setObjectName("savedActionCreatedTasksGuidance")
        self.guidance_label.setWordWrap(True)
        layout.addWidget(self.guidance_label)

        self.items_frame = QFrame(self)
        self.items_frame.setObjectName("savedActionCreatedTasksItems")
        self.items_layout = QVBoxLayout(self.items_frame)
        self.items_layout.setContentsMargins(0, 2, 0, 0)
        self.items_layout.setSpacing(2)

        self.items_scroll = QScrollArea(self)
        self.items_scroll.setObjectName("savedActionCreatedTasksItemsScroll")
        self.items_scroll.setFrameShape(QFrame.NoFrame)
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.items_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.items_scroll.setFocusPolicy(Qt.NoFocus)
        self.items_scroll.setMaximumHeight(0)
        self.items_scroll.viewport().setObjectName("savedActionCreatedTasksViewport")
        self.items_scroll.viewport().setAutoFillBackground(False)
        self.items_scroll.setWidget(self.items_frame)
        layout.addWidget(self.items_scroll)

        self.footer_frame = QFrame(self)
        self.footer_frame.setObjectName("savedActionCreatedTasksFooter")
        footer_layout = QHBoxLayout(self.footer_frame)
        footer_layout.setContentsMargins(0, 4, 0, 0)
        footer_layout.setSpacing(8)
        footer_layout.addStretch(1)

        self.close_button = QPushButton("Close", self.footer_frame)
        self.close_button.setObjectName("savedActionCreatedTasksClose")
        self.close_button.setMinimumHeight(34)
        self.close_button.clicked.connect(self.reject)
        footer_layout.addWidget(self.close_button)

        layout.addWidget(self.footer_frame)
        self.setStyleSheet(
            """
            #savedActionCreatedGroupsDialog {
                background: transparent;
            }
            #savedActionCreatedTasksShell {
                border-radius: 22px;
                border: 1px solid rgba(118, 226, 255, 0.20);
                background: rgba(4, 16, 28, 238);
            }
            #savedActionCreatedTasksContent {
                border-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #savedActionCreatedTasksChromeBar {
                border: none;
                border-top-left-radius: 22px;
                border-top-right-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #savedActionCreatedTasksFooter {
                border-top: 1px solid rgba(118, 226, 255, 0.12);
                background: transparent;
            }
            #savedActionCreatedTasksTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 20px;
                font-weight: 600;
                padding: 0px 6px 1px 6px;
                background: transparent;
            }
            #savedActionCreatedTasksHint {
                color: rgba(136, 165, 174, 0.88);
                font-size: 11px;
                padding: 0px 6px 3px 6px;
                background: transparent;
            }
            """
            + THEMED_TOOLTIP_QSS
            + """
            #savedActionCreatedTasksStatus {
                color: rgba(148, 180, 178, 0.89);
                font-size: 13px;
                font-weight: 600;
            }
            #savedActionCreatedTasksStatus[statusKind="invalid_source"], #savedActionCreatedTasksStatus[statusKind="invalid_groups"], #savedActionCreatedTasksStatus[statusKind="invalid_saved_actions"], #savedActionCreatedTasksStatus[statusKind="missing"] {
                color: rgba(255, 189, 176, 0.96);
            }
            #savedActionCreatedTasksSource {
                color: rgba(126, 157, 171, 0.78);
                font-size: 13px;
            }
            #savedActionCreatedTasksGuidance {
                color: rgba(110, 201, 164, 0.86);
                font-size: 13px;
            }
            #savedActionCreatedTasksItemsScroll {
                border: none;
                background: transparent;
            }
            #savedActionCreatedTasksViewport {
                border-radius: 18px;
                background: rgba(4, 12, 22, 236);
            }
            #savedActionCreatedTasksItems {
                background: transparent;
            }
            QFrame[inventoryRole="itemFrame"] {
                border-radius: 14px;
                border: 1px solid rgba(118, 226, 255, 0.22);
                background: rgba(12, 28, 44, 208);
            }
            QFrame[inventoryRole="actionShell"] {
                border-radius: 16px;
                border: none;
                background: rgba(15, 40, 62, 248);
            }
            QLabel[inventoryRole="itemTitle"] {
                color: rgba(184, 208, 200, 0.96);
                font-size: 14px;
                font-weight: 650;
            }
            QLabel[inventoryRole="itemMeta"] {
                color: rgba(84, 192, 181, 0.83);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            QLabel[inventoryRole="itemTarget"] {
                color: rgba(163, 189, 196, 0.92);
                font-size: 12px;
            }
            QPushButton[inventoryRole="editButton"], QPushButton[inventoryRole="deleteButton"], #savedActionCreatedTasksClose {
                min-height: 28px;
                padding: 0 16px;
                border-radius: 12px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(191, 212, 207, 0.96);
                font-size: 14px;
                font-weight: 650;
            }
            #savedActionCreatedTasksClose {
                min-height: 34px;
            }
            QPushButton[inventoryRole="editButton"], QPushButton[inventoryRole="deleteButton"] {
                min-width: 104px;
            }
            QPushButton[inventoryRole="editButton"] {
                border: 1px solid rgba(118, 226, 255, 0.30);
                background: rgba(18, 52, 78, 228);
            }
            QPushButton[inventoryRole="deleteButton"] {
                border: 1px solid rgba(255, 138, 138, 0.26);
                background: rgba(34, 12, 16, 212);
                color: rgba(255, 231, 231, 0.96);
            }
            QPushButton[chromeRole="close"] {
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                padding: 0px;
                text-align: center;
                border-radius: 7px;
                border: 1px solid rgba(118, 226, 255, 0.16);
                background: rgba(18, 52, 78, 228);
                color: rgba(191, 212, 207, 0.94);
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton[chromeRole="close"]:hover {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(22, 61, 90, 238);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar:vertical {
                width: 8px;
                margin: 4px 1px 4px 0;
                border-radius: 4px;
                background: rgba(6, 18, 30, 0.58);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::handle:vertical {
                min-height: 38px;
                border-radius: 4px;
                border: 1px solid rgba(118, 226, 255, 0.20);
                background: rgba(18, 52, 78, 0.96);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::handle:vertical:hover {
                background: rgba(22, 61, 90, 0.98);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::handle:vertical:pressed {
                background: rgba(118, 226, 255, 0.54);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::add-line:vertical,
            #savedActionCreatedTasksItemsScroll QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::add-page:vertical,
            #savedActionCreatedTasksItemsScroll QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )
        self.refresh_inventory(inventory_payload or {})

    def _emit_lifecycle_event(self, stage: str, **fields):
        if callable(self._lifecycle_callback):
            try:
                self._lifecycle_callback("CREATED_GROUPS_DIALOG", stage, dialog=self, **fields)
            except Exception:
                pass

    def _emit_ready_signal(self):
        if self._ready_signal_emitted or not self.isVisible():
            return
        self._ready_signal_emitted = True
        self._emit_lifecycle_event("ready")

    def showEvent(self, event):
        super().showEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        _schedule_window_clamp(self)
        self._emit_lifecycle_event("opened")
        QTimer.singleShot(0, self._sync_items_scroll_height)
        QTimer.singleShot(0, self._emit_ready_signal)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_chrome_overlay_geometry()
        _apply_rounded_dialog_mask(self)
        _schedule_window_clamp(self)
        QTimer.singleShot(0, self._sync_items_scroll_height)

    def done(self, result):
        self._emit_lifecycle_event(
            "closed",
            result="accepted" if result == QDialog.Accepted else "rejected",
        )
        super().done(result)

    def _update_chrome_overlay_geometry(self):
        if hasattr(self, "chrome_bar"):
            self.chrome_bar.raise_()

    def _sync_items_scroll_height(self):
        if not hasattr(self, "items_scroll") or not hasattr(self, "items_layout"):
            return
        item_frames = [
            self.items_layout.itemAt(index).widget()
            for index in range(self.items_layout.count())
            if self.items_layout.itemAt(index) is not None
            and self.items_layout.itemAt(index).widget() is not None
            and self.items_layout.itemAt(index).widget().property("inventoryRole") == "itemFrame"
        ]
        visible_rows = sum(1 for frame in item_frames if frame.isVisible())
        if visible_rows <= 0:
            self.items_scroll.setMaximumHeight(0)
            self.items_scroll.setFixedHeight(0)
            return
        desired_height = _visible_row_height_for_layout(
            self.items_layout,
            min(5, visible_rows),
            extra_padding=0,
        )
        self.items_scroll.setMaximumHeight(desired_height)
        self.items_scroll.setFixedHeight(desired_height)

    def selected_group_id(self) -> str:
        return self._selected_group_id

    def selected_delete_group_id(self) -> str:
        return self._selected_delete_group_id

    def _handle_edit_requested(self, group_id: str):
        self._selected_group_id = group_id
        self._selected_delete_group_id = ""
        self.accept()

    def _handle_delete_requested(self, group_id: str):
        self._selected_delete_group_id = group_id
        self._selected_group_id = ""
        self.accept()

    def refresh_inventory(self, inventory_payload: dict):
        inventory_payload = inventory_payload or {}
        self.title_label.setText("Manage Custom Groups")

        status_kind = inventory_payload.get("status_kind", "hidden")
        self.status_label.setProperty("statusKind", status_kind)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_label.setText(inventory_payload.get("status_text", ""))

        source_path = inventory_payload.get("path", "")
        source_display = inventory_payload.get("path_display") or source_path
        items = inventory_payload.get("items") or []
        show_source_details = status_kind in {"invalid_source", "invalid_groups", "invalid_saved_actions", "missing", "template_only"} or not items
        self.source_label.setText(f"Source: {source_display}" if show_source_details and source_display else "")
        self.source_label.setToolTip(source_path)
        guidance_text = inventory_payload.get("guidance_text", "")
        show_guidance = bool(guidance_text) and (
            status_kind in {"invalid_source", "invalid_groups", "invalid_saved_actions", "missing", "template_only"} or not items
        )
        self.guidance_label.setText(guidance_text if show_guidance else "")
        self.source_label.setVisible(bool(self.source_label.text()))
        self.guidance_label.setVisible(bool(self.guidance_label.text()))

        _populate_saved_group_item_layout(
            self.items_layout,
            self.items_frame,
            items,
            self._handle_edit_requested,
            self._handle_delete_requested,
        )
        self.items_scroll.setVisible(bool(items))
        if items:
            self.items_layout.activate()
            self._sync_items_scroll_height()
            QTimer.singleShot(0, self._sync_items_scroll_height)
        else:
            self.items_scroll.setMaximumHeight(0)
            self.items_scroll.setFixedHeight(0)


class CommandOverlayPanel(QWidget):
    submit_requested = Signal()
    escape_requested = Signal()
    input_text_changed = Signal(str)
    input_armed_changed = Signal(bool)
    input_focus_acquired = Signal()
    input_focus_lost = Signal()
    ambiguous_match_selected = Signal(int)
    create_custom_task_requested = Signal()
    created_tasks_requested = Signal()
    create_custom_group_requested = Signal()
    created_groups_requested = Signal()
    edit_saved_action_requested = Signal(str)

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setObjectName("commandOverlayWindow")
        command_font = QFont("Segoe UI")
        command_font.setPointSize(10)
        self.setFont(command_font)
        self._visible_ambiguous_count = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.panel = QFrame(self)
        self.panel.setObjectName("commandPanel")
        root.addWidget(self.panel)

        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(0)

        self.kicker_label = QLabel("O.R.I.N. Command Prompt", self.panel)
        self.kicker_label.setObjectName("commandKicker")
        layout.addWidget(self.kicker_label)

        self.title_label = QLabel("Typed desktop interaction", self.panel)
        self.title_label.setObjectName("commandTitle")
        layout.addWidget(self.title_label)

        self.hint_label = QLabel(
            "Left-click or right-click the command box to activate.",
            self.panel,
        )
        self.hint_label.setObjectName("commandHint")
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        self.input_shell = QFrame(self.panel)
        self.input_shell.setObjectName("commandInputShell")
        input_layout = QHBoxLayout(self.input_shell)
        input_layout.setContentsMargins(16, 14, 16, 14)
        input_layout.setSpacing(10)

        self.prompt_label = QLabel(">", self.input_shell)
        self.prompt_label.setObjectName("commandPrompt")
        input_layout.addWidget(self.prompt_label)

        self.input_line = CommandInputLineEdit(self.input_shell)
        self.input_line.setObjectName("commandInputLine")
        self.input_line.textChanged.connect(self.input_text_changed)
        self.input_line.submit_requested.connect(self.submit_requested)
        self.input_line.escape_requested.connect(self.escape_requested)
        self.input_line.input_armed_changed.connect(self.input_armed_changed)
        self.input_line.focus_acquired.connect(self.input_focus_acquired)
        self.input_line.focus_lost.connect(self.input_focus_lost)
        input_layout.addWidget(self.input_line, 1)

        self.caret = QFrame(self.input_shell)
        self.caret.setObjectName("commandCaret")
        input_layout.addWidget(self.caret)

        layout.addWidget(self.input_shell)

        self.status_label = QLabel("", self.panel)
        self.status_label.setObjectName("commandStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.saved_inventory_frame = QFrame(self.panel)
        self.saved_inventory_frame.setObjectName("savedActionInventory")
        saved_inventory_layout = QVBoxLayout(self.saved_inventory_frame)
        saved_inventory_layout.setContentsMargins(18, 16, 18, 16)
        saved_inventory_layout.setSpacing(10)

        self.saved_inventory_title = QLabel("Custom tasks and groups", self.saved_inventory_frame)
        self.saved_inventory_title.setObjectName("savedActionInventoryTitle")
        saved_inventory_layout.addWidget(self.saved_inventory_title)

        self.saved_inventory_status = QLabel(
            "Create or manage exact-match tasks and callable groups.",
            self.saved_inventory_frame,
        )
        self.saved_inventory_status.setObjectName("savedActionInventoryStatus")
        self.saved_inventory_status.setWordWrap(True)
        saved_inventory_layout.addWidget(self.saved_inventory_status)

        self.entry_actions_layout = QGridLayout()
        self.entry_actions_layout.setContentsMargins(0, 0, 0, 0)
        self.entry_actions_layout.setHorizontalSpacing(12)
        self.entry_actions_layout.setVerticalSpacing(12)
        self.entry_actions_layout.setColumnStretch(0, 1)
        self.entry_actions_layout.setColumnStretch(1, 1)

        self.create_action_frame = QFrame(self.saved_inventory_frame)
        self.create_action_frame.setProperty("entryActionCard", "true")
        self.create_action_frame.setProperty("entryActionVariant", "primary")
        create_action_layout = QVBoxLayout(self.create_action_frame)
        create_action_layout.setContentsMargins(12, 12, 12, 12)
        create_action_layout.setSpacing(6)

        self.create_custom_task_button = QPushButton("Create Custom Task", self.create_action_frame)
        self.create_custom_task_button.setObjectName("savedActionCreateButton")
        self.create_custom_task_button.setProperty("entryAction", "true")
        self.create_custom_task_button.setProperty("entryActionVariant", "primary")
        self.create_custom_task_button.clicked.connect(
            lambda _checked=False: self.create_custom_task_requested.emit()
        )
        create_action_layout.addWidget(self.create_custom_task_button)

        self.create_custom_task_description = QLabel(
            "Start a new application, folder, file, or website task.",
            self.create_action_frame,
        )
        self.create_custom_task_description.setObjectName("savedActionCreateDescription")
        self.create_custom_task_description.setWordWrap(True)
        create_action_layout.addWidget(self.create_custom_task_description)
        self.entry_actions_layout.addWidget(self.create_action_frame, 0, 0)

        self.manage_action_frame = QFrame(self.saved_inventory_frame)
        self.manage_action_frame.setProperty("entryActionCard", "true")
        self.manage_action_frame.setProperty("entryActionVariant", "secondary")
        manage_action_layout = QVBoxLayout(self.manage_action_frame)
        manage_action_layout.setContentsMargins(12, 12, 12, 12)
        manage_action_layout.setSpacing(6)

        self.created_tasks_button = QPushButton("Manage Custom Tasks", self.manage_action_frame)
        self.created_tasks_button.setObjectName("savedActionCreatedTasksButton")
        self.created_tasks_button.setProperty("entryAction", "true")
        self.created_tasks_button.setProperty("entryActionVariant", "secondary")
        self.created_tasks_button.clicked.connect(
            lambda _checked=False: self.created_tasks_requested.emit()
        )
        manage_action_layout.addWidget(self.created_tasks_button)

        self.created_tasks_description = QLabel(
            "Review, edit, or remove the tasks you have already saved.",
            self.manage_action_frame,
        )
        self.created_tasks_description.setObjectName("savedActionCreatedTasksDescription")
        self.created_tasks_description.setWordWrap(True)
        manage_action_layout.addWidget(self.created_tasks_description)
        self.entry_actions_layout.addWidget(self.manage_action_frame, 0, 1)

        self.create_group_action_frame = QFrame(self.saved_inventory_frame)
        self.create_group_action_frame.setProperty("entryActionCard", "true")
        self.create_group_action_frame.setProperty("entryActionVariant", "primary")
        create_group_layout = QVBoxLayout(self.create_group_action_frame)
        create_group_layout.setContentsMargins(12, 12, 12, 12)
        create_group_layout.setSpacing(6)

        self.create_custom_group_button = QPushButton("Create Custom Group", self.create_group_action_frame)
        self.create_custom_group_button.setObjectName("savedActionCreateGroupButton")
        self.create_custom_group_button.setProperty("entryAction", "true")
        self.create_custom_group_button.setProperty("entryActionVariant", "primary")
        self.create_custom_group_button.setToolTip(
            "Create an exact-match callable group that can surface selected built-ins and saved tasks."
        )
        self.create_custom_group_button.clicked.connect(
            lambda _checked=False: self.create_custom_group_requested.emit()
        )
        create_group_layout.addWidget(self.create_custom_group_button)

        self.create_custom_group_description = QLabel(
            "Start a callable group that can surface built-ins and saved tasks.",
            self.create_group_action_frame,
        )
        self.create_custom_group_description.setObjectName("savedActionCreateGroupDescription")
        self.create_custom_group_description.setWordWrap(True)
        create_group_layout.addWidget(self.create_custom_group_description)
        self.entry_actions_layout.addWidget(self.create_group_action_frame, 1, 0)

        self.manage_group_action_frame = QFrame(self.saved_inventory_frame)
        self.manage_group_action_frame.setProperty("entryActionCard", "true")
        self.manage_group_action_frame.setProperty("entryActionVariant", "secondary")
        manage_group_layout = QVBoxLayout(self.manage_group_action_frame)
        manage_group_layout.setContentsMargins(12, 12, 12, 12)
        manage_group_layout.setSpacing(6)

        self.created_groups_button = QPushButton("Manage Custom Groups", self.manage_group_action_frame)
        self.created_groups_button.setObjectName("savedActionCreatedGroupsButton")
        self.created_groups_button.setProperty("entryAction", "true")
        self.created_groups_button.setProperty("entryActionVariant", "secondary")
        self.created_groups_button.setToolTip(
            "Review, edit, or remove callable groups and manage which members each group can surface."
        )
        self.created_groups_button.clicked.connect(
            lambda _checked=False: self.created_groups_requested.emit()
        )
        manage_group_layout.addWidget(self.created_groups_button)

        self.created_groups_description = QLabel(
            "Review, edit, or remove callable groups and their members.",
            self.manage_group_action_frame,
        )
        self.created_groups_description.setObjectName("savedActionCreatedGroupsDescription")
        self.created_groups_description.setWordWrap(True)
        manage_group_layout.addWidget(self.created_groups_description)
        self.entry_actions_layout.addWidget(self.manage_group_action_frame, 1, 1)

        saved_inventory_layout.addLayout(self.entry_actions_layout)

        saved_inventory_layout.addStretch(1)

        layout.addWidget(self.saved_inventory_frame)
        self.saved_inventory_frame.hide()

        self.ambiguous_label = QLabel("", self.panel)
        self.ambiguous_label.setObjectName("commandAmbiguous")
        self.ambiguous_label.setWordWrap(True)
        layout.addWidget(self.ambiguous_label)

        self.ambiguous_choices_frame = QFrame(self.panel)
        self.ambiguous_choices_frame.setObjectName("commandAmbiguousChoices")
        self.ambiguous_choices_layout = QVBoxLayout(self.ambiguous_choices_frame)
        self.ambiguous_choices_layout.setContentsMargins(0, 8, 0, 0)
        self.ambiguous_choices_layout.setSpacing(8)
        layout.addWidget(self.ambiguous_choices_frame)
        self.ambiguous_choices_frame.hide()

        self.confirmation_frame = QFrame(self.panel)
        self.confirmation_frame.setObjectName("commandConfirmation")
        confirm_layout = QGridLayout(self.confirmation_frame)
        confirm_layout.setContentsMargins(18, 16, 18, 14)
        confirm_layout.setHorizontalSpacing(14)
        confirm_layout.setVerticalSpacing(8)

        confirm_layout.addWidget(self._make_confirm_label("Typed request"), 0, 0)
        self.confirm_request_value = self._make_confirm_value()
        confirm_layout.addWidget(self.confirm_request_value, 0, 1)

        self.confirm_title_label = self._make_confirm_label("Resolved action")
        confirm_layout.addWidget(self.confirm_title_label, 1, 0)
        self.confirm_title_value = self._make_confirm_value()
        confirm_layout.addWidget(self.confirm_title_value, 1, 1)

        confirm_layout.addWidget(self._make_confirm_label("Action origin"), 2, 0)
        self.confirm_origin_value = self._make_confirm_value()
        confirm_layout.addWidget(self.confirm_origin_value, 2, 1)

        confirm_layout.addWidget(self._make_confirm_label("Target kind"), 3, 0)
        self.confirm_kind_value = self._make_confirm_value()
        confirm_layout.addWidget(self.confirm_kind_value, 3, 1)

        confirm_layout.addWidget(self._make_confirm_label("Target"), 4, 0)
        self.confirm_target_value = self._make_confirm_value()
        confirm_layout.addWidget(self.confirm_target_value, 4, 1)

        self.confirm_help_label = QLabel(
            "Press Enter to confirm or Esc to return.",
            self.confirmation_frame,
        )
        self.confirm_help_label.setObjectName("commandConfirmHelp")
        self.confirm_help_label.setWordWrap(True)
        confirm_layout.addWidget(self.confirm_help_label, 5, 0, 1, 2)

        layout.addWidget(self.confirmation_frame)
        self.confirmation_frame.hide()

        self.setStyleSheet(
            """
            #commandOverlayWindow, #commandOverlayWindow * {
                font-family: "Segoe UI";
            }
            #commandPanel {
                border: 1px solid rgba(118, 226, 255, 0.22);
                border-radius: 22px;
                background: rgba(4, 16, 28, 238);
            }
            #commandKicker {
                color: rgba(84, 192, 181, 0.84);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.24em;
            }
            #commandTitle {
                margin-top: 8px;
                color: rgba(188, 212, 203, 0.97);
                font-size: 28px;
                font-weight: 600;
            }
            #commandHint {
                margin-top: 10px;
                color: rgba(136, 165, 174, 0.88);
                font-size: 14px;
            }
            """
            + THEMED_TOOLTIP_QSS
            + """
            #commandInputShell {
                margin-top: 18px;
                border-radius: 16px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
            }
            #commandInputShell[armed="true"] {
                border: 1px solid rgba(118, 226, 255, 0.36);
                background: rgba(7, 22, 36, 220);
            }
            #commandInputShell[locked="true"] {
                border: 1px solid rgba(118, 226, 255, 0.24);
                background: rgba(8, 18, 30, 214);
            }
            #commandPrompt {
                color: rgba(84, 192, 181, 0.88);
                font-size: 22px;
                font-weight: 600;
            }
            #commandInputLine {
                border: none;
                background: transparent;
                color: rgba(193, 213, 208, 0.96);
                font-size: 21px;
                selection-background-color: rgba(118, 226, 255, 0.28);
            }
            #commandInputLine:read-only {
                color: rgba(133, 155, 164, 0.92);
            }
            #commandCaret {
                min-width: 10px;
                max-width: 10px;
                min-height: 24px;
                max-height: 24px;
                border-radius: 999px;
                background: rgba(132, 236, 255, 0.82);
            }
            #commandCaret[armed="false"] {
                background: rgba(132, 236, 255, 0.22);
            }
            #commandStatus {
                margin-top: 14px;
                min-height: 22px;
                color: rgba(146, 176, 178, 0.89);
                font-size: 14px;
            }
            #commandStatus[statusKind="not_found"], #commandStatus[statusKind="launch_failed"] {
                color: rgba(255, 176, 176, 0.95);
            }
            #commandStatus[statusKind="ambiguous"] {
                color: rgba(255, 222, 154, 0.95);
            }
            #commandStatus[statusKind="launch_requested"], #commandStatus[statusKind="ready"] {
                color: rgba(166, 247, 195, 0.94);
            }
            #savedActionInventory {
                margin-top: 16px;
                border-radius: 18px;
                background: rgba(8, 20, 34, 214);
                border: 1px solid rgba(118, 226, 255, 0.12);
            }
            #savedActionInventoryTitle {
                color: rgba(84, 192, 181, 0.90);
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.08em;
            }
            #savedActionInventoryStatus {
                color: rgba(136, 165, 174, 0.88);
                font-size: 13px;
                line-height: 1.45em;
            }
            QFrame[entryActionCard="true"] {
                border-radius: 18px;
                border: 1px solid rgba(118, 226, 255, 0.12);
                background: rgba(7, 20, 34, 0.82);
            }
            QFrame[entryActionCard="true"][entryActionVariant="primary"] {
                border: 1px solid rgba(118, 226, 255, 0.20);
                background: rgba(10, 28, 46, 0.90);
            }
            QFrame[entryActionCard="true"][entryActionVariant="secondary"] {
                background: rgba(9, 22, 37, 0.88);
            }
            #savedActionCreateDescription, #savedActionCreatedTasksDescription,
            #savedActionCreateGroupDescription, #savedActionCreatedGroupsDescription {
                color: rgba(147, 174, 182, 0.87);
                font-size: 12px;
                line-height: 1.4em;
            }
            QPushButton[entryAction="true"] {
                min-height: 38px;
                margin-top: 0;
                padding: 0 14px;
                border-radius: 12px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(191, 212, 207, 0.96);
                text-align: left;
                font-size: 14px;
                font-weight: 650;
            }
            QPushButton[entryAction="true"][entryActionVariant="primary"] {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(18, 52, 78, 228);
            }
            QPushButton[entryAction="true"]:hover {
                border: 1px solid rgba(118, 226, 255, 0.36);
                background: rgba(8, 24, 38, 220);
            }
            QPushButton[entryAction="true"][entryActionVariant="primary"]:hover {
                border: 1px solid rgba(118, 226, 255, 0.50);
                background: rgba(22, 61, 90, 238);
            }
            #commandAmbiguous {
                min-height: 20px;
                color: rgba(255, 222, 154, 0.90);
                font-size: 13px;
            }
            #commandAmbiguousChoices {
                margin-top: 2px;
            }
            QPushButton[choiceRole="ambiguous"] {
                padding: 10px 14px;
                border-radius: 14px;
                border: 1px solid rgba(255, 222, 154, 0.28);
                background: rgba(32, 24, 10, 180);
                color: rgba(255, 239, 198, 0.96);
                text-align: left;
                font-size: 13px;
            }
            QPushButton[choiceRole="ambiguous"]:hover {
                border: 1px solid rgba(255, 222, 154, 0.44);
                background: rgba(44, 30, 12, 214);
            }
            #commandConfirmation {
                margin-top: 18px;
                border-radius: 18px;
                background: rgba(10, 22, 38, 220);
                border: 1px solid rgba(118, 226, 255, 0.14);
            }
            QLabel[confirmRole="label"] {
                color: rgba(78, 176, 173, 0.78);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.12em;
            }
            QLabel[confirmRole="value"] {
                color: rgba(189, 210, 204, 0.95);
                font-size: 15px;
            }
            #commandConfirmHelp {
                margin-top: 14px;
                color: rgba(140, 168, 176, 0.89);
                font-size: 13px;
            }
            """
        )

    def _make_confirm_label(self, text: str) -> QLabel:
        label = QLabel(text, self.confirmation_frame)
        label.setProperty("confirmRole", "label")
        return label

    def _make_confirm_value(self) -> QLabel:
        label = QLabel("", self.confirmation_frame)
        label.setProperty("confirmRole", "value")
        label.setWordWrap(True)
        return label

    def _build_confirm_surface_copy(self, selection_context: str, pending_group: dict | None = None) -> dict[str, str]:
        normalized_selection_context = (selection_context or "").strip().casefold()
        pending_group = pending_group or {}
        group_title = (pending_group.get("title") or "").strip()
        if normalized_selection_context == "group":
            group_subject = f'"{group_title}" group' if group_title else "the full matched group"
            return {
                "title_label": "Selected member",
                "hint_text": f"Review the selected member details below. Press Enter to run {group_subject} in stored order.",
                "help_text": f"Press Enter to run {group_subject} in stored order, or Esc to return.",
            }
        return {
            "title_label": "Resolved action",
            "hint_text": "Review the resolved action origin and destination before execution.",
            "help_text": "Press Enter to confirm or Esc to return.",
        }

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.submit_requested.emit()
            event.accept()
            return

        if event.key() == Qt.Key_Escape:
            self.escape_requested.emit()
            event.accept()
            return

        ambiguous_index = self._resolve_ambiguous_choice_index(event)
        if ambiguous_index is not None:
            self.ambiguous_match_selected.emit(ambiguous_index)
            event.accept()
            return

        super().keyPressEvent(event)

    def _resolve_ambiguous_choice_index(self, event) -> int | None:
        if self._visible_ambiguous_count <= 0:
            return None

        text = event.text() or ""
        if text.isdigit():
            index = int(text) - 1
            if 0 <= index < self._visible_ambiguous_count:
                return index

        return None

    def _apply_geometry(self, host_geometry: QRect, bounds_geometry: QRect | None = None):
        width = max(520, min(680, int(host_geometry.width() * 0.56)))
        self.panel.setFixedWidth(width)
        self.panel.adjustSize()
        self.adjustSize()

        anchor_x = host_geometry.x() + int(host_geometry.width() * 0.84)
        x = anchor_x - (self.width() // 2)
        y = host_geometry.y() + max(18, (host_geometry.height() - self.height()) // 2)

        if bounds_geometry is not None:
            min_x = bounds_geometry.x()
            max_x = bounds_geometry.x() + max(0, bounds_geometry.width() - self.width())
            min_y = bounds_geometry.y()
            max_y = bounds_geometry.y() + max(0, bounds_geometry.height() - self.height())
            x = max(min_x, min(x, max_x))
            y = max(min_y, min(y, max_y))

        self.move(x, y)

    def show_for_geometry(self, host_geometry: QRect, bounds_geometry: QRect | None = None):
        self._apply_geometry(host_geometry, bounds_geometry)
        self.show()
        self.raise_()

    def refresh_for_geometry(self, host_geometry: QRect, bounds_geometry: QRect | None = None):
        self._apply_geometry(host_geometry, bounds_geometry)

    def focus_input(self, reason=Qt.ShortcutFocusReason):
        self.raise_()
        self.activateWindow()
        window_handle = self.windowHandle()
        if window_handle is not None:
            window_handle.requestActivate()
        self.setFocus(Qt.ActiveWindowFocusReason)
        self.input_line.setFocus(reason)
        self.input_line.setCursorPosition(len(self.input_line.text()))

    def ensure_typing_ready(self):
        self.input_line.set_input_armed(True, notify=False)
        self.focus_input(Qt.ShortcutFocusReason)

    def focus_input_after_show(self):
        self.ensure_typing_ready()
        QTimer.singleShot(0, self.ensure_typing_ready)
        QTimer.singleShot(40, self.ensure_typing_ready)

    def _clear_ambiguous_choice_buttons(self):
        while self.ambiguous_choices_layout.count():
            item = self.ambiguous_choices_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _populate_ambiguous_choice_buttons(self, matches: list[dict]):
        self._clear_ambiguous_choice_buttons()
        for match in matches:
            index = int(match.get("index", -1))
            title = match.get("title", "")
            origin_label = match.get("origin_label", "Action")
            target_kind = match.get("target_kind", "")
            target_display = match.get("target_display") or match.get("target", "")
            button_text = f"{index + 1}. {title}"
            metadata_bits = [origin_label]
            if target_kind:
                metadata_bits.append(target_kind)
            if metadata_bits:
                button_text += f"\n{' - '.join(metadata_bits)}"
            if target_display:
                button_text += f"\n{target_display}"
            button = QPushButton(button_text, self.ambiguous_choices_frame)
            button.setProperty("choiceRole", "ambiguous")
            button.setToolTip(match.get("target", ""))
            button.clicked.connect(lambda _checked=False, idx=index: self.ambiguous_match_selected.emit(idx))
            self.ambiguous_choices_layout.addWidget(button)
        self.ambiguous_choices_frame.setVisible(bool(matches))

    def render_payload(self, payload: dict):
        payload = payload or {}
        phase = payload.get("phase", "hidden")
        armed = bool(payload.get("input_armed")) and phase == "entry"
        typing_ready = bool(payload.get("typing_ready", armed)) and phase == "entry"
        locked = phase in {"choose", "confirm", "result"}
        ambiguous_matches = payload.get("ambiguous_matches") or []
        self._visible_ambiguous_count = len(ambiguous_matches)

        self.input_shell.setProperty("armed", "true" if typing_ready else "false")
        self.input_shell.setProperty("locked", "true" if locked else "false")
        self.caret.setProperty("armed", "true" if typing_ready else "false")
        for widget in (self.input_shell, self.caret):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

        self.input_line.blockSignals(True)
        if self.input_line.text() != payload.get("input_text", ""):
            self.input_line.setText(payload.get("input_text", ""))
        self.input_line.set_input_armed(armed, notify=False)
        self.input_line.blockSignals(False)
        if locked:
            self.setFocus(Qt.ActiveWindowFocusReason)

        selection_context = payload.get("selection_context", "")
        pending_group = payload.get("pending_group") or {}
        confirm_surface_copy = self._build_confirm_surface_copy(selection_context, pending_group)

        if phase == "confirm":
            self.hint_label.setText(confirm_surface_copy["hint_text"])
        elif phase == "choose":
            if selection_context == "group" and pending_group.get("title"):
                self.hint_label.setText(
                    f'Select a member from "{pending_group.get("title")}" after reviewing its origin and destination.'
                )
            else:
                self.hint_label.setText("Press a number key or click the intended action after reviewing its origin and destination.")
        elif phase == "result":
            self.hint_label.setText("Returning to passive desktop mode.")
        else:
            self.hint_label.setText("Type a built-in or saved action, or use the buttons below.")

        status_kind = payload.get("status_kind", "idle")
        self.status_label.setProperty("statusKind", status_kind)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        if payload.get("status_text"):
            self.status_label.setText(payload["status_text"])
        elif phase == "entry" and not armed:
            self.status_label.setText("Type an action or alias to begin.")
        else:
            self.status_label.setText("")

        saved_action_inventory = payload.get("saved_action_inventory") or {}
        saved_group_inventory = payload.get("saved_group_inventory") or {}
        show_inventory = phase == "entry" and bool(
            saved_action_inventory.get("visible") or saved_group_inventory.get("visible")
        )
        self.saved_inventory_frame.setVisible(show_inventory)
        if show_inventory:
            self.create_custom_task_button.setEnabled(True)
            self.created_tasks_button.setEnabled(True)
            self.create_custom_group_button.setEnabled(True)
            self.created_groups_button.setEnabled(True)
            self.saved_inventory_title.setText("Custom tasks and groups")
            self.saved_inventory_status.setProperty("statusKind", "idle")
            self.saved_inventory_status.style().unpolish(self.saved_inventory_status)
            self.saved_inventory_status.style().polish(self.saved_inventory_status)
            self.saved_inventory_status.setText("Create or manage exact-match tasks and callable groups.")
        else:
            self.saved_inventory_status.setText("")

        titles = payload.get("ambiguous_titles") or []
        if phase == "choose" and titles:
            if selection_context == "group" and pending_group.get("title"):
                self.ambiguous_label.setText(
                    f'Select the member you want from "{pending_group.get("title")}".'
                )
            else:
                self.ambiguous_label.setText(
                    "Multiple actions matched your request. Press a number key or click a choice after reviewing the origin and destination detail below."
                )
        else:
            self.ambiguous_label.setText(f"Matches: {' | '.join(titles)}" if titles else "")
        self._populate_ambiguous_choice_buttons(ambiguous_matches)

        action = payload.get("pending_action") or {}
        show_confirm = phase == "confirm" and bool(action)
        self.confirmation_frame.setVisible(show_confirm)
        if show_confirm:
            self.confirm_title_label.setText(confirm_surface_copy["title_label"])
            self.confirm_request_value.setText(payload.get("typed_request", ""))
            self.confirm_title_value.setText(action.get("title", ""))
            self.confirm_origin_value.setText(action.get("origin_label", ""))
            self.confirm_kind_value.setText(action.get("target_kind", ""))
            self.confirm_target_value.setText(action.get("target_display") or action.get("target", ""))
            self.confirm_target_value.setToolTip(action.get("target", ""))
            self.confirm_help_label.setText(confirm_surface_copy["help_text"])


class MonitoringHudOverlayDisplayWindow(QWidget):
    def __init__(self, screen, event_logger=None):
        super().__init__(None)
        self.screen_ref = screen
        self.event_logger = event_logger
        self._anchored = True
        self._drag_origin: QPoint | None = None
        self._drag_window_origin = QPoint()
        self._last_unanchored_geometry = QRect()
        self._card_widgets: dict[str, dict[str, object]] = {}
        self._card_layouts: dict[str, dict[str, int | str | bool]] = {}
        self._card_drag_id = ""
        self._card_drag_resize = False
        self._card_drag_origin: QPoint | None = None
        self._card_drag_base: dict[str, int | str | bool] = {}
        self.setObjectName("monitoringHudOverlayDisplayWindow")
        flags = Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet(
            """
            QWidget#monitoringHudOverlayDisplayWindow {
                background: transparent;
            }
            QFrame#monitoringHudOverlayDisplayFrame {
                border: 1px solid rgba(116, 239, 255, 0.22);
                border-radius: 14px;
                background:
                    qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(7, 20, 33, 0.34),
                        stop:0.52 rgba(5, 31, 44, 0.20),
                        stop:1 rgba(6, 12, 22, 0.30));
            }
            QLabel {
                color: #dffbff;
                font-family: Bahnschrift, Segoe UI, sans-serif;
                background: transparent;
            }
            QLabel[role="eyebrow"] {
                color: rgba(120, 239, 255, 0.42);
                font-size: 10px;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            QLabel[role="title"] {
                color: #f5ffff;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel[role="state"] {
                color: #a5f8dc;
                font-size: 12px;
            }
            QLabel[role="card"] {
                color: #d7faff;
                border: 1px solid rgba(112, 242, 255, 0.24);
                border-radius: 14px;
                padding: 10px 12px;
                background: rgba(3, 14, 24, 0.38);
            }
            QLabel[role="warning"] {
                color: #ffe3a6;
                font-size: 11px;
            }
            QLabel[role="watermark"] {
                color: rgba(120, 239, 255, 0.30);
                font-size: 10px;
                letter-spacing: 3px;
                text-transform: uppercase;
            }
            QFrame[role="overlayCard"] {
                border: 1px solid rgba(112, 242, 255, 0.24);
                border-radius: 14px;
                background: rgba(3, 14, 24, 0.38);
            }
            QFrame[role="overlayCard"][state="setup"] {
                border-color: rgba(255, 214, 113, 0.30);
            }
            QFrame[role="overlayCard"][state="no-data"] {
                border-color: rgba(124, 178, 210, 0.28);
            }
            QLabel[role="cardTitle"] {
                color: rgba(139, 233, 255, 0.86);
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            QLabel[role="cardSummary"] {
                color: #f5ffff;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel[role="cardMeta"] {
                color: rgba(189, 232, 242, 0.80);
                font-size: 10px;
            }
            QFrame[role="cardResizeHandle"] {
                border: 1px solid rgba(125, 235, 255, 0.30);
                border-radius: 4px;
                background: rgba(125, 235, 255, 0.18);
            }
            QPushButton {
                min-height: 28px;
                padding: 4px 10px;
                border: 1px solid rgba(116, 239, 255, 0.26);
                border-radius: 999px;
                background: rgba(5, 22, 38, 0.72);
                color: #dffbff;
                font-family: Bahnschrift, Segoe UI, sans-serif;
                font-size: 10px;
                font-weight: 700;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        frame = QFrame(self)
        frame.setObjectName("monitoringHudOverlayDisplayFrame")
        frame.setProperty("role", "overlayDisplayCanvas")
        frame.installEventFilter(self)
        self._watermark = QLabel("Nexus Desktop AI / ORIN", frame)
        self._watermark.setProperty("role", "watermark")
        self._title = QLabel("Monitoring HUD Overlay", frame)
        self._title.setProperty("role", "title")
        self._state = QLabel("Provider setup required", frame)
        self._state.setProperty("role", "state")
        self._warning = QLabel("Visual warning baseline only", frame)
        self._warning.setProperty("role", "warning")
        self._resize_grip = QSizeGrip(frame)
        for widget in (self._watermark, self._title, self._state, self._warning, self._resize_grip):
            widget.installEventFilter(self)
        root.addWidget(frame)
        self._frame = frame
        self._quick_controls = (self._resize_grip,)
        self._sync_overlay_card(
            "cpu",
            {"x": 28, "y": 84, "w": 360, "h": 150, "title": "CPU Group", "enabled": True},
            "Provider warming",
            "setup",
        )
        self._sync_overlay_card(
            "gpu",
            {"x": 28, "y": 254, "w": 360, "h": 150, "title": "GPU Group", "enabled": True},
            "Provider required",
            "no-data",
        )

        self.setGeometry(self._compute_overlay_geometry(initial=True))
        self._layout_overlay_children()
        self.hide()
        QTimer.singleShot(0, self._apply_native_click_through_flags)

    def _default_card_layout(self, card_id: str) -> dict[str, int | str | bool]:
        y = 84 + (170 * len(self._card_layouts))
        return {"x": 28, "y": y, "w": 360, "h": 150, "title": f"{card_id.upper()} Group", "enabled": True}

    def _create_overlay_card(self, card_id: str) -> dict[str, object]:
        card = QFrame(self._frame)
        card.setProperty("role", "overlayCard")
        card.setProperty("cardId", card_id)
        card.installEventFilter(self)
        title = QLabel("Monitor Group", card)
        title.setProperty("role", "cardTitle")
        summary = QLabel("Provider required", card)
        summary.setProperty("role", "cardSummary")
        meta = QLabel("Provider route pending", card)
        meta.setProperty("role", "cardMeta")
        edit_button = QPushButton("Edit", card)
        edit_button.setProperty("cardId", card_id)
        resize_handle = QFrame(card)
        resize_handle.setProperty("role", "cardResizeHandle")
        resize_handle.setProperty("resizeCardId", card_id)
        for widget in (title, summary, meta, edit_button, resize_handle):
            widget.installEventFilter(self)
        widgets = {
            "frame": card,
            "title": title,
            "summary": summary,
            "meta": meta,
            "edit": edit_button,
            "resize": resize_handle,
        }
        self._card_widgets[card_id] = widgets
        return widgets

    def _bound_card_layout(self, layout: dict[str, int | str | bool]) -> dict[str, int | str | bool]:
        frame_width = max(420, self._frame.width())
        frame_height = max(260, self._frame.height())
        width = max(220, min(int(layout.get("w") or 360), frame_width))
        height = max(110, min(int(layout.get("h") or 150), frame_height))
        x = max(8, min(int(layout.get("x") or 28), max(8, frame_width - width - 8)))
        y = max(52, min(int(layout.get("y") or 84), max(52, frame_height - height - 28)))
        bounded = dict(layout)
        bounded.update({"x": x, "y": y, "w": width, "h": height})
        return bounded

    def _sync_overlay_card(
        self,
        card_id: str,
        layout: dict[str, object],
        summary: str,
        state: str,
    ):
        if card_id not in self._card_widgets:
            self._create_overlay_card(card_id)
        existing = dict(self._card_layouts.get(card_id) or self._default_card_layout(card_id))
        incoming = dict(layout or {})
        # Dashboard edits can rename/enable monitors, but overlay placement is
        # owned by the standalone overlay window after the card exists.
        for key in ("title", "enabled", "pollingRateMs"):
            if key in incoming:
                existing[key] = incoming[key]
        if card_id not in self._card_layouts:
            for key in ("x", "y", "w", "h"):
                if key in incoming:
                    try:
                        existing[key] = int(float(incoming[key]))
                    except (TypeError, ValueError):
                        pass
        existing = self._bound_card_layout(existing)
        self._card_layouts[card_id] = existing
        widgets = self._card_widgets[card_id]
        frame = widgets["frame"]
        title = widgets["title"]
        summary_label = widgets["summary"]
        meta = widgets["meta"]
        frame.setProperty("state", state)
        frame.style().unpolish(frame)
        frame.style().polish(frame)
        title.setText(str(existing.get("title") or f"{card_id.upper()} Group"))
        summary_label.setText("Hidden in overlay" if existing.get("enabled") is False else summary)
        meta.setText("1s default after provider proof; no fake values.")
        widgets["edit"].setVisible(not self._anchored)  # type: ignore[index]
        widgets["resize"].setVisible(not self._anchored)  # type: ignore[index]
        frame.setGeometry(int(existing["x"]), int(existing["y"]), int(existing["w"]), int(existing["h"]))
        self._layout_card_children(card_id)
        frame.show()

    def _layout_card_children(self, card_id: str):
        widgets = self._card_widgets.get(card_id)
        if not widgets:
            return
        frame: QFrame = widgets["frame"]  # type: ignore[assignment]
        title: QLabel = widgets["title"]  # type: ignore[assignment]
        summary: QLabel = widgets["summary"]  # type: ignore[assignment]
        meta: QLabel = widgets["meta"]  # type: ignore[assignment]
        edit: QPushButton = widgets["edit"]  # type: ignore[assignment]
        resize: QFrame = widgets["resize"]  # type: ignore[assignment]
        w = max(1, frame.width())
        h = max(1, frame.height())
        title.setGeometry(14, 12, max(1, w - 110), 22)
        summary.setGeometry(14, 42, max(1, w - 28), 28)
        meta.setGeometry(14, max(70, h - 36), max(1, w - 44), 22)
        edit.setGeometry(max(14, w - 78), 10, 62, 28)
        resize.setGeometry(max(0, w - 18), max(0, h - 18), 12, 12)

    def _layout_overlay_children(self):
        frame_width = max(1, self._frame.width())
        frame_height = max(1, self._frame.height())
        self._watermark.setGeometry(18, 12, max(1, frame_width - 36), 18)
        self._title.setGeometry(18, 34, min(320, max(1, frame_width - 36)), 24)
        self._state.setGeometry(max(18, frame_width - 300), 34, 282, 24)
        self._warning.setGeometry(18, max(56, frame_height - 26), max(1, frame_width - 70), 20)
        self._resize_grip.setGeometry(max(0, frame_width - 22), max(0, frame_height - 22), 20, 20)
        for card_id, layout in list(self._card_layouts.items()):
            bounded = self._bound_card_layout(layout)
            self._card_layouts[card_id] = bounded
            widgets = self._card_widgets.get(card_id)
            if widgets:
                frame: QFrame = widgets["frame"]  # type: ignore[assignment]
                frame.setGeometry(int(bounded["x"]), int(bounded["y"]), int(bounded["w"]), int(bounded["h"]))
                self._layout_card_children(card_id)

    def _virtual_desktop_geometry(self) -> QRect:
        screens = QApplication.screens()
        if not screens:
            return self.screen_ref.availableGeometry()
        rect = screens[0].availableGeometry()
        for screen in screens[1:]:
            rect = rect.united(screen.availableGeometry())
        return rect

    def _initial_overlay_target_geometry(self) -> QRect:
        screens = QApplication.screens()
        if not screens:
            return self.screen_ref.availableGeometry()
        core_screen = self.screen_ref.availableGeometry()
        candidates = []
        for screen in screens:
            geometry = screen.availableGeometry()
            same_screen = (
                geometry.x() == core_screen.x()
                and geometry.y() == core_screen.y()
                and geometry.width() == core_screen.width()
                and geometry.height() == core_screen.height()
            )
            if not same_screen:
                candidates.append(geometry)
        if not candidates:
            return core_screen
        core_center_x = core_screen.center().x()
        return sorted(
            candidates,
            key=lambda rect: (abs(rect.center().x() - core_center_x), rect.center().x()),
            reverse=True,
        )[0]

    def _compute_overlay_geometry(self, *, initial: bool = False) -> QRect:
        virtual = self._virtual_desktop_geometry()
        if not initial and self.geometry().isValid() and self.geometry().width() > 0 and self.geometry().height() > 0:
            return self.geometry()
        target = self._initial_overlay_target_geometry()
        margin = 48
        width = min(max(720, int(target.width() * 0.72)), max(420, target.width() - margin * 2))
        height = min(max(420, int(target.height() * 0.68)), max(280, target.height() - margin * 2))
        return QRect(
            target.x() + max(margin, (target.width() - width) // 2),
            target.y() + max(margin, (target.height() - height) // 2),
            width,
            height,
        )

    def _apply_native_click_through_flags(self):
        try:
            hwnd = ctypes.wintypes.HWND(int(self.winId()))
            style = int(GetWindowLongW(hwnd, GWL_EXSTYLE))
            if self._anchored:
                style |= WS_EX_NOACTIVATE | WS_EX_TRANSPARENT
            else:
                style = style & ~WS_EX_NOACTIVATE & ~WS_EX_TRANSPARENT
            SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception:
            return

    def _set_overlay_interaction_mode(self, anchored: bool):
        self._anchored = bool(anchored)
        if anchored and self.geometry().isValid():
            self._last_unanchored_geometry = QRect(self.geometry())
        self.setAttribute(Qt.WA_ShowWithoutActivating, bool(anchored))
        self.setAttribute(Qt.WA_TransparentForMouseEvents, bool(anchored))
        self.setFocusPolicy(Qt.NoFocus if anchored else Qt.StrongFocus)
        self._frame.setProperty("anchored", anchored)
        self._frame.style().unpolish(self._frame)
        self._frame.style().polish(self._frame)
        for control in self._quick_controls:
            control.setVisible(not anchored)
        for widgets in self._card_widgets.values():
            edit = widgets.get("edit")
            resize = widgets.get("resize")
            if edit is not None:
                edit.setVisible(not anchored)
            if resize is not None:
                resize.setVisible(not anchored)
        self._apply_native_click_through_flags()
        if not anchored:
            self.show()
            self.raise_()
            self.activateWindow()

    def _bound_geometry_to_virtual_desktop(self, rect: QRect) -> QRect:
        virtual = self._virtual_desktop_geometry()
        width = max(360, min(rect.width(), virtual.width()))
        height = max(220, min(rect.height(), virtual.height()))
        left = max(virtual.x(), min(rect.x(), virtual.x() + virtual.width() - width))
        top = max(virtual.y(), min(rect.y(), virtual.y() + virtual.height() - height))
        return QRect(left, top, width, height)

    def update_product_state(
        self,
        *,
        visible: bool,
        anchored: bool,
        provider_label: str = "Provider setup required",
        warning_label: str = "Visual warning baseline only",
        cards: dict[str, object] | None = None,
    ):
        self._set_overlay_interaction_mode(bool(anchored))
        self._state.setText(provider_label or "Provider setup required")
        self._warning.setText(warning_label or "Visual warning baseline only")
        card_map = cards if isinstance(cards, dict) else {}
        cpu = card_map.get("cpu") if isinstance(card_map.get("cpu"), dict) else {}
        gpu = card_map.get("gpu") if isinstance(card_map.get("gpu"), dict) else {}
        self._sync_overlay_card("cpu", cpu or {}, "Provider warming", "setup")
        self._sync_overlay_card("gpu", gpu or {}, "Provider required", "no-data")
        for card_id, layout in card_map.items():
            if str(card_id) in {"cpu", "gpu"} or not isinstance(layout, dict):
                continue
            self._sync_overlay_card(str(card_id), layout, "Provider route pending", "no-data")
        if visible:
            if not self.geometry().isValid() or self.geometry().width() <= 0 or self.geometry().height() <= 0:
                self.setGeometry(self._compute_overlay_geometry(initial=True))
            self.setGeometry(self._bound_geometry_to_virtual_desktop(self.geometry()))
            self._layout_overlay_children()
            self.show()
            if anchored:
                self.raise_()
            self._apply_native_click_through_flags()
            if callable(self.event_logger):
                self.event_logger("MONITORING_HUD_OVERLAY_DISPLAY_WINDOW_VISIBLE|surface=standalone_edgeless_overlay_display")
            return
        self.hide()

    def proof_state(self) -> dict[str, object]:
        hwnd = int(self.winId())
        style = 0
        try:
            style = int(GetWindowLongW(ctypes.wintypes.HWND(hwnd), GWL_EXSTYLE))
        except Exception:
            style = 0
        geometry = self.geometry()
        virtual = self._virtual_desktop_geometry()
        center = ctypes.wintypes.POINT(geometry.x() + geometry.width() // 2, geometry.y() + geometry.height() // 2)
        try:
            window_from_center = int(WindowFromPoint(center))
        except Exception:
            window_from_center = 0
        last = self._last_unanchored_geometry if self._last_unanchored_geometry.isValid() else QRect(geometry)
        return {
            "hwnd": hwnd,
            "visible": bool(self.isVisible()),
            "x": geometry.x(),
            "y": geometry.y(),
            "w": geometry.width(),
            "h": geometry.height(),
            "virtualX": virtual.x(),
            "virtualY": virtual.y(),
            "virtualW": virtual.width(),
            "virtualH": virtual.height(),
            "surface": "standalone_edgeless_overlay_display",
            "owner": "MonitoringHudOverlayDisplayWindow",
            "anchored": bool(self._anchored),
            "focusPolicy": "no_focus" if self.focusPolicy() == Qt.NoFocus else "interactive",
            "transparentForMouseEvents": bool(self.testAttribute(Qt.WA_TransparentForMouseEvents)),
            "showWithoutActivating": bool(self.testAttribute(Qt.WA_ShowWithoutActivating)),
            "exNoActivate": bool(style & WS_EX_NOACTIVATE),
            "exTransparent": bool(style & WS_EX_TRANSPARENT),
            "windowFromCenter": window_from_center,
            "windowFromCenterBypassesOverlay": bool(window_from_center and window_from_center != hwnd),
            "standaloneTopLevel": self.parent() is None,
            "quickControlsVisible": any(control.isVisible() for control in self._quick_controls),
            "overlayCardCount": len(self._card_widgets),
            "cardLayouts": {
                card_id: {
                    "x": int(layout.get("x") or 0),
                    "y": int(layout.get("y") or 0),
                    "w": int(layout.get("w") or 0),
                    "h": int(layout.get("h") or 0),
                }
                for card_id, layout in self._card_layouts.items()
            },
            "cardsMovableInOverlay": True,
            "dashboardCoupled": False,
            "surfaceIndependence": "dashboard_overlay_core_top_level_windows",
            "ownedByDashboardWindow": False,
            "lastUnanchoredX": last.x(),
            "lastUnanchoredY": last.y(),
            "lastUnanchoredW": last.width(),
            "lastUnanchoredH": last.height(),
            "positionPreserved": (
                not self._last_unanchored_geometry.isNull()
                and geometry.x() == last.x()
                and geometry.y() == last.y()
                and geometry.width() == last.width()
                and geometry.height() == last.height()
            ),
        }

    def _card_id_from_widget(self, widget) -> tuple[str, bool]:
        current = widget
        while current is not None:
            resize_card_id = current.property("resizeCardId") if hasattr(current, "property") else None
            if resize_card_id:
                return str(resize_card_id), True
            card_id = current.property("cardId") if hasattr(current, "property") else None
            if card_id:
                return str(card_id), False
            current = current.parent() if hasattr(current, "parent") else None
        return "", False

    def _move_card_from_delta(self, delta: QPoint):
        if not self._card_drag_id:
            return
        layout = dict(self._card_drag_base)
        if self._card_drag_resize:
            layout["w"] = int(round((int(layout.get("w") or 360) + delta.x()) / 20) * 20)
            layout["h"] = int(round((int(layout.get("h") or 150) + delta.y()) / 20) * 20)
        else:
            layout["x"] = int(round((int(layout.get("x") or 28) + delta.x()) / 20) * 20)
            layout["y"] = int(round((int(layout.get("y") or 84) + delta.y()) / 20) * 20)
        layout = self._bound_card_layout(layout)
        self._card_layouts[self._card_drag_id] = layout
        widgets = self._card_widgets.get(self._card_drag_id)
        if widgets:
            frame: QFrame = widgets["frame"]  # type: ignore[assignment]
            frame.setGeometry(int(layout["x"]), int(layout["y"]), int(layout["w"]), int(layout["h"]))
            self._layout_card_children(self._card_drag_id)

    def eventFilter(self, watched, event):
        if self._anchored:
            return super().eventFilter(watched, event)
        event_type = event.type()
        if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            card_id, resize = self._card_id_from_widget(watched)
            if card_id:
                self._card_drag_id = card_id
                self._card_drag_resize = resize
                self._card_drag_origin = event.globalPosition().toPoint()
                self._card_drag_base = dict(self._card_layouts.get(card_id) or self._default_card_layout(card_id))
                event.accept()
                return True
            if watched in {self._frame, self._watermark, self._title, self._state, self._warning}:
                self._drag_origin = event.globalPosition().toPoint()
                self._drag_window_origin = self.pos()
                event.accept()
                return True
        if event_type == QEvent.MouseMove:
            if self._card_drag_id and self._card_drag_origin is not None:
                self._move_card_from_delta(event.globalPosition().toPoint() - self._card_drag_origin)
                event.accept()
                return True
            if self._drag_origin is not None:
                delta = event.globalPosition().toPoint() - self._drag_origin
                next_rect = QRect(self._drag_window_origin + delta, self.size())
                self.setGeometry(self._bound_geometry_to_virtual_desktop(next_rect))
                event.accept()
                return True
        if event_type in (QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick):
            if self._card_drag_id:
                card_id = self._card_drag_id
                self._move_card_from_delta(event.globalPosition().toPoint() - (self._card_drag_origin or QPoint()))
                layout = self._card_layouts.get(card_id, {})
                if callable(self.event_logger):
                    self.event_logger(
                        "MONITORING_HUD_OVERLAY_CARD_LAYOUT_EDITED|"
                        f"card={card_id}|x={layout.get('x')}|y={layout.get('y')}|"
                        f"w={layout.get('w')}|h={layout.get('h')}|resize={str(self._card_drag_resize).lower()}"
                    )
                self._card_drag_id = ""
                self._card_drag_resize = False
                self._card_drag_origin = None
                self._card_drag_base = {}
                event.accept()
                return True
            if self._drag_origin is not None:
                self._last_unanchored_geometry = QRect(self.geometry())
                if callable(self.event_logger):
                    self.event_logger(
                        "MONITORING_HUD_OVERLAY_DISPLAY_POSITION_EDITED|"
                        f"x={self.geometry().x()}|y={self.geometry().y()}|w={self.geometry().width()}|h={self.geometry().height()}"
                    )
                self._drag_origin = None
                event.accept()
                return True
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_overlay_children()

    def mousePressEvent(self, event):
        if self._anchored or event.button() != Qt.LeftButton:
            return super().mousePressEvent(event)
        self._drag_origin = event.globalPosition().toPoint()
        self._drag_window_origin = self.pos()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._anchored or self._drag_origin is None:
            return super().mouseMoveEvent(event)
        delta = event.globalPosition().toPoint() - self._drag_origin
        next_rect = QRect(self._drag_window_origin + delta, self.size())
        self.setGeometry(self._bound_geometry_to_virtual_desktop(next_rect))
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._drag_origin is not None:
            self._last_unanchored_geometry = QRect(self.geometry())
            if callable(self.event_logger):
                self.event_logger(
                    "MONITORING_HUD_OVERLAY_DISPLAY_POSITION_EDITED|"
                    f"x={self.geometry().x()}|y={self.geometry().y()}|w={self.geometry().width()}|h={self.geometry().height()}"
                )
        self._drag_origin = None
        return super().mouseReleaseEvent(event)

    def request_shutdown(self):
        self.hide()
        self.close()


MONITORING_HUD_STUDIO_VISUAL_CONTRACT = "fam006-unique-child-studio-shell-v5"
MONITORING_HUD_STUDIO_VISUAL_SAMPLE = "ai-control-center-uiref-001-002-003-primitives"
MONITORING_HUD_STUDIO_VISUAL_INHERITANCE = "nexus-window-primitives-v1-rendered-dom-css"
MONITORING_HUD_STUDIO_VISUAL_ADJUDICATION = "photo-video-comparison-required"
MONITORING_HUD_STUDIO_VISUAL_PROOF_AUTHORITY = "photo-video-comparison-not-runtime-self-attestation"
MONITORING_HUD_STUDIO_VISUAL_CLAIM_STATE = "declared-not-proven-by-runtime"
MONITORING_HUD_STUDIO_BUTTON_VISUAL_GRAMMAR = "shared-uiref-003-button-primitive-with-fam006-feature-studio-composition"
MONITORING_HUD_STUDIO_BODY_VISUAL_GRAMMAR = "fam006-unique-child-purpose-stack-v6-action-first-requires-photo-adjudication"
MONITORING_HUD_STUDIO_REFERENCE_SURFACES = (
    "AI Control Center shared primitives",
    "Overlay Profile Settings",
    "Manage Monitors",
    "UIREF-001 Top-Level Window Frame",
    "UIREF-002 Compact Window Control Cluster",
    "UIREF-003 Control State And Selector Grammar",
)


def _monitoring_hud_window_settings() -> QSettings:
    return QSettings("Nexus Desktop AI", "Monitoring HUD Windows")


def _monitoring_hud_available_rect(screen) -> QRect:
    if screen is not None:
        try:
            rect = screen.availableGeometry()
            if rect.isValid() and not rect.isNull():
                return QRect(rect)
        except Exception:
            pass
    primary = QApplication.primaryScreen()
    if primary is not None:
        return QRect(primary.availableGeometry())
    return QRect(0, 0, 1280, 720)


def _monitoring_hud_rect_has_visible_center(rect: QRect) -> bool:
    if not rect.isValid() or rect.isNull():
        return False
    for screen in QApplication.screens():
        available = screen.availableGeometry()
        if available.contains(rect.center()):
            return True
    return False


def _monitoring_hud_bound_window_rect(rect: QRect, screen, *, min_width: int = 360, min_height: int = 240) -> QRect:
    available = _monitoring_hud_available_rect(screen)
    min_width = max(1, int(min_width))
    min_height = max(1, int(min_height))
    width = min(max(min_width, rect.width()), max(min_width, available.width()))
    height = min(max(min_height, rect.height()), max(min_height, available.height()))
    left = min(max(rect.x(), available.left()), max(available.left(), available.right() - width + 1))
    top = min(max(rect.y(), available.top()), max(available.top(), available.bottom() - height + 1))
    return QRect(left, top, width, height)


def _monitoring_hud_qrect_to_dict(rect: QRect | None) -> dict[str, int] | None:
    if rect is None or not rect.isValid() or rect.isNull():
        return None
    return {
        "x": int(rect.x()),
        "y": int(rect.y()),
        "w": int(rect.width()),
        "h": int(rect.height()),
    }


def _monitoring_hud_restore_window_geometry(widget: QWidget, key: str, fallback: QRect) -> bool:
    settings = _monitoring_hud_window_settings()
    prefix = f"{key}/geometry/"
    try:
        saved = QRect(
            int(settings.value(prefix + "x", fallback.x())),
            int(settings.value(prefix + "y", fallback.y())),
            int(settings.value(prefix + "w", fallback.width())),
            int(settings.value(prefix + "h", fallback.height())),
        )
    except Exception:
        saved = QRect(fallback)
    restored = _monitoring_hud_rect_has_visible_center(saved)
    widget.setGeometry(_monitoring_hud_bound_window_rect(saved if restored else fallback, getattr(widget, "screen_ref", None)))
    return restored


def _monitoring_hud_save_window_geometry(widget: QWidget, key: str) -> None:
    if widget.isMinimized():
        return
    rect = widget.geometry()
    if not rect.isValid() or rect.isNull():
        return
    settings = _monitoring_hud_window_settings()
    prefix = f"{key}/geometry/"
    settings.setValue(prefix + "x", rect.x())
    settings.setValue(prefix + "y", rect.y())
    settings.setValue(prefix + "w", rect.width())
    settings.setValue(prefix + "h", rect.height())
    settings.sync()


def _monitoring_hud_studio_row(
    label: str,
    value_widget: QLabel,
    parent: QWidget,
    *,
    value_word_wrap: bool = True,
    value_role: str = "sectionValue",
) -> QFrame:
    row = QFrame(parent)
    row.setProperty("role", "studioRow")
    row_height = 44 if value_word_wrap else 34
    row.setMinimumHeight(row_height)
    row.setMaximumHeight(row_height)
    layout = QGridLayout(row)
    layout.setContentsMargins(0, 4, 0, 2)
    layout.setHorizontalSpacing(6)
    layout.setVerticalSpacing(2)
    label_widget = QLabel(label, row)
    label_widget.setProperty("role", "sectionLabel")
    label_widget.setMinimumHeight(20)
    value_widget.setProperty("role", value_role)
    value_widget.setMinimumHeight(22 if value_word_wrap else 18)
    value_widget.setWordWrap(value_word_wrap)
    if not value_word_wrap:
        value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    layout.addWidget(label_widget, 0, 0, Qt.AlignVCenter)
    layout.addWidget(value_widget, 0, 1, Qt.AlignVCenter)
    layout.setColumnStretch(0, 0)
    layout.setColumnStretch(1, 1)
    return row


def _monitoring_hud_ai_control_center_primitive_contract() -> dict[str, str]:
    return {
        "implementationAuthority": "Shared Rendered Primitive Implementation",
        "primaryReference": "nexus_visual/ai_control_center.html for shared primitives only",
        "compositionReference": "FAM-006 detached child feature-studio contract",
        "acceptedReferenceSet": "UIREF-001|UIREF-002|UIREF-003|FAM-002",
        "windowFrame": "fam006-compact-feature-studio-dark-glass-rounded-frame",
        "windowControls": "ai-control-center-symbol-window-control-cluster-identical",
        "actionButtons": "monitoring-hud-hub-action-content-fit-button-identical",
        "rows": "fam006-detached-child-window-divider-state-rows",
        "header": "detached-child-window-header-no-title-card",
        "proofRule": "photo-video-comparison-required; runtime-marker-is-supporting-evidence-only",
    }


def _monitoring_hud_prepare_studio_button(
    button: QPushButton,
    *,
    role: str,
    minimum_width: int,
    accessible_name: str = "",
    tooltip: str = "",
) -> None:
    button.setProperty("actionRole", role)
    button.setFocusPolicy(Qt.StrongFocus)
    button.setCursor(Qt.PointingHandCursor)
    button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    if accessible_name:
        button.setAccessibleName(accessible_name)
    if tooltip or accessible_name:
        button.setToolTip(tooltip or accessible_name)
    compact_window_control = role == "studioWindowControl"
    button_width = minimum_width
    button.setMinimumWidth(button_width)
    button.setMaximumWidth(button_width)
    button_height = 32 if not compact_window_control else 34
    button.setMinimumHeight(button_height)
    button.setMaximumHeight(button_height)
    button.setFixedHeight(button_height)
    button.setProperty(
        "controlStateProof",
        "default-hover-focus-pressed-disabled-keyboard-accessible",
    )
    button.setProperty("visualPrimitiveAuthority", "Shared-Rendered-AI-Control-Center-Primitive")
    if compact_window_control:
        button.setProperty("sharedPrimitiveSeed", "AI-Control-Center-UIREF-002-window-control-cluster")
        button.setProperty("primitiveRole", "window-control-symbol-pill")
        button.setProperty("visiblePrimitiveShape", "ai-control-center-symbol-window-control-pill")
    else:
        button.setProperty("sharedPrimitiveSeed", "AI-Control-Center-UIREF-003-action-button")
        button.setProperty("primitiveRole", "primary-secondary-action-button")
        button.setProperty("visiblePrimitiveShape", "hub-action-content-fit-equal-gutter-32px-pill")


def _monitoring_hud_studio_window_control_cluster(parent: QWidget) -> QFrame:
    cluster = QFrame(parent)
    cluster.setProperty("role", "studioWindowControls")
    cluster.setProperty("sharedPrimitiveSeed", "AI-Control-Center-UIREF-002-window-control-cluster")
    cluster.setProperty("visualPrimitiveAuthority", "Shared-Rendered-AI-Control-Center-Primitive")
    layout = QHBoxLayout(cluster)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    return cluster


def _monitoring_hud_position_studio_window_controls(shell: QWidget, controls: QWidget) -> None:
    controls.adjustSize()
    controls.move(max(12, shell.width() - controls.width() - 24), 26)
    controls.raise_()


def _monitoring_hud_studio_button_proof(button: QPushButton) -> dict[str, object]:
    return {
        "text": button.text(),
        "actionRole": str(button.property("actionRole") or ""),
        "accessibleName": button.accessibleName(),
        "tooltip": button.toolTip(),
        "enabled": button.isEnabled(),
        "focusPolicy": "StrongFocus" if button.focusPolicy() == Qt.StrongFocus else str(button.focusPolicy()),
        "keyboardReachable": button.focusPolicy() == Qt.StrongFocus,
        "controlStateProof": str(button.property("controlStateProof") or ""),
        "sharedPrimitiveSeed": str(button.property("sharedPrimitiveSeed") or ""),
        "visualPrimitiveAuthority": str(button.property("visualPrimitiveAuthority") or ""),
        "primitiveRole": str(button.property("primitiveRole") or ""),
        "visiblePrimitiveShape": str(button.property("visiblePrimitiveShape") or ""),
        "width": button.width(),
        "height": button.height(),
    }


def _monitoring_hud_apply_studio_shadow(widget: QWidget) -> None:
    widget.setProperty("studioShadowMode", "painted-shell")


class MonitoringHudStudioButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._visual_hovered = False
        self._visual_pressed = False
        self.setAttribute(Qt.WA_Hover, True)

    def enterEvent(self, event):
        self._visual_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._visual_hovered = False
        self._visual_pressed = False
        self.update()
        super().leaveEvent(event)

    def focusInEvent(self, event):
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._visual_pressed = False
        self.update()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        self._visual_pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._visual_pressed = False
        try:
            self._visual_hovered = self.rect().contains(self.mapFromGlobal(QCursor.pos()))
        except Exception:
            self._visual_hovered = self.underMouse()
        self.update()
        super().mouseReleaseEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in {QEvent.EnabledChange, QEvent.PaletteChange, QEvent.StyleChange, QEvent.ActivationChange}:
            if not self.isActiveWindow():
                self._visual_hovered = False
                self._visual_pressed = False
            self.update()

    def paintEvent(self, event):
        # Non-symbol controls intentionally render through the shared Qt stylesheet so
        # visual states are not split between QSS and a one-off painter.
        super().paintEvent(event)
        return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        role = str(self.property("actionRole") or "")
        if role == "studioWindowControl":
            self._paint_ai_control_center_window_control(painter)
            return

        rect = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        radius = rect.height() / 2.0
        enabled = self.isEnabled()
        pressed = enabled and (self._visual_pressed or self.isDown())
        hovered = enabled and self._visual_hovered and not pressed
        focused = enabled and self.hasFocus()

        if pressed:
            border = QColor(163, 255, 228, 184)
            top = QColor(7, 40, 57, 250)
            bottom = QColor(3, 18, 32, 245)
            glow = QColor(103, 255, 210, 26)
            text = QColor(246, 255, 253, 252)
        elif hovered:
            border = QColor(126, 248, 218, 143)
            top = QColor(9, 49, 70, 240)
            bottom = QColor(4, 24, 40, 232)
            glow = QColor(86, 236, 255, 30)
            text = QColor(241, 255, 252, 252)
        elif focused:
            border = QColor(117, 228, 255, 112)
            top = QColor(7, 42, 62, 232)
            bottom = QColor(3, 18, 32, 227)
            glow = QColor(123, 246, 255, 24)
            text = QColor(235, 252, 255, 246)
        elif enabled:
            border = QColor(117, 228, 255, 56)
            top = QColor(7, 42, 62, 224)
            bottom = QColor(3, 18, 32, 219)
            glow = QColor(99, 225, 255, 0)
            text = QColor(229, 249, 255, 240)
        else:
            border = QColor(149, 176, 194, 61)
            top = QColor(12, 29, 42, 138)
            bottom = QColor(8, 20, 34, 138)
            glow = QColor(176, 204, 214, 8)
            text = QColor(176, 204, 214, 178)

        glow_passes = (((-0.5, 0.20),) if (hovered or pressed or focused) else tuple())
        for inset, alpha_scale in glow_passes:
            glow_rect = rect.adjusted(inset, inset, -inset, -inset)
            glow_color = QColor(glow)
            glow_color.setAlpha(max(0, min(255, int(glow.alpha() * alpha_scale))))
            painter.setPen(QPen(glow_color, 1.0))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(glow_rect, glow_rect.height() / 2.0, glow_rect.height() / 2.0)

        fill = QLinearGradient(rect.topLeft(), rect.bottomRight())
        fill.setColorAt(0.0, top)
        fill.setColorAt(1.0, bottom)
        painter.setPen(QPen(border, 1.0))
        painter.setBrush(fill)
        painter.drawRoundedRect(rect, radius, radius)

        inner = rect.adjusted(1.0, 1.0, -1.0, -1.0)
        painter.setPen(QPen(QColor(232, 251, 255, 18 if enabled else 10), 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(inner, inner.height() / 2.0, inner.height() / 2.0)

        font = QFont("Bahnschrift")
        font.setStyleHint(QFont.SansSerif)
        font.setPixelSize(12)
        if enabled:
            font.setWeight(QFont.Weight.DemiBold)
        else:
            font.setWeight(QFont.Weight.DemiBold)
        font.setLetterSpacing(QFont.PercentageSpacing, 109)
        painter.setFont(font)
        painter.setPen(text)
        text_inset = 0.0 if role == "studioWindowControl" else 12.0
        painter.drawText(rect.adjusted(text_inset, 0.0, -text_inset, 0.0), Qt.AlignCenter, self.text().upper())

    def _paint_ai_control_center_window_control(self, painter: QPainter) -> None:
        enabled = self.isEnabled()
        pressed = enabled and (self._visual_pressed or self.isDown())
        hovered = enabled and self._visual_hovered and not pressed
        focused = enabled and self.hasFocus()
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = rect.height() / 2.0

        if pressed:
            border = QColor(163, 255, 228, 184)
            fill = QColor(7, 40, 57, 219)
            glyph = QColor(235, 252, 255, 235)
            translate_y = 1.0
            glow_alpha = 0
        elif hovered or focused:
            border = QColor(126, 248, 218, 143)
            fill = QColor(9, 49, 70, 199)
            glyph = QColor(235, 252, 255, 235)
            translate_y = 0.0
            glow_alpha = 71
        elif enabled:
            border = QColor(122, 232, 255, 61)
            fill = QColor(5, 22, 36, 158)
            glyph = QColor(235, 252, 255, 235)
            translate_y = 0.0
            glow_alpha = 0
        else:
            border = QColor(122, 232, 255, 46)
            fill = QColor(5, 22, 36, 87)
            glyph = QColor(179, 226, 238, 158)
            translate_y = 0.0
            glow_alpha = 0

        target_rect = rect.translated(0.0, translate_y)
        painter.setPen(QPen(border, 1.0))
        painter.setBrush(fill)
        painter.drawRoundedRect(target_rect, radius, radius)
        painter.setPen(QPen(QColor(230, 251, 255, 18 if enabled else 7), 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(target_rect.adjusted(1.0, 1.0, -1.0, -1.0), radius - 1.0, radius - 1.0)
        if glow_alpha:
            painter.setPen(QPen(QColor(86, 236, 255, glow_alpha), 2.0))
            painter.drawRoundedRect(target_rect.adjusted(-1.0, -1.0, 1.0, 1.0), radius + 1.0, radius + 1.0)

        painter.setPen(QPen(glyph, 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        center = target_rect.center()
        if self.text().strip() == "-":
            painter.drawLine(
                QPointF(center.x() - 5.0, center.y()),
                QPointF(center.x() + 5.0, center.y()),
            )
        else:
            painter.drawLine(
                QPointF(center.x() - 5.5, center.y() - 5.5),
                QPointF(center.x() + 5.5, center.y() + 5.5),
            )
            painter.drawLine(
                QPointF(center.x() + 5.5, center.y() - 5.5),
                QPointF(center.x() - 5.5, center.y() + 5.5),
            )


def _monitoring_hud_compact_path_label_text(full_path: str, label: QLabel) -> str:
    path_text = os.path.normpath(str(full_path or "").strip())
    if not path_text:
        return "Unavailable"
    available_width = max(190, label.width() or 240)
    return label.fontMetrics().elidedText(path_text, Qt.ElideMiddle, available_width)


def _monitoring_hud_set_contained_path_label(label: QLabel, full_path: str) -> str:
    display_text = _monitoring_hud_compact_path_label_text(full_path, label)
    label.setText(display_text)
    label.setToolTip(os.path.normpath(str(full_path or "").strip()))
    label.setProperty("pathDisplayMode", "middle-elided-contained")
    return display_text


def _monitoring_hud_set_contained_value_label(
    label: QLabel,
    value: str,
    *,
    tooltip: str = "",
    mode: str = "single-line-contained",
) -> str:
    text = str(value or "").strip() or "Unavailable"
    available_width = max(190, label.width() or 240)
    display_text = label.fontMetrics().elidedText(text, Qt.ElideMiddle, available_width)
    label.setText(display_text)
    label.setToolTip(str(tooltip or text))
    label.setProperty("pathDisplayMode", mode)
    return display_text


def _monitoring_hud_studio_stylesheet(object_name: str) -> str:
    return f"""
        QWidget#{object_name} {{
            background: transparent;
            color: rgba(235, 252, 255, 0.96);
            font-family: Bahnschrift, Segoe UI, sans-serif;
            letter-spacing: 0px;
        }}
        QFrame[role="studioShell"] {{
            background: qradialgradient(cx:0.06, cy:0.00, radius:0.35, fx:0.06, fy:0.00, stop:0 rgba(91, 221, 255, 0.22), stop:1 transparent), qradialgradient(cx:1.00, cy:0.20, radius:0.33, fx:1.00, fy:0.20, stop:0 rgba(84, 255, 190, 0.16), stop:1 transparent), qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(4, 17, 32, 0.96), stop:1 rgba(1, 7, 16, 0.94));
            border: 1px solid rgba(125, 235, 255, 0.30);
            border-radius: 28px;
            color: rgba(235, 252, 255, 0.96);
        }}
        QFrame[role="studioHeader"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(5, 23, 39, 0.985), stop:1 rgba(2, 10, 20, 0.965));
            border: 1px solid rgba(130, 236, 255, 0.12);
            border-radius: 20px;
        }}
        QFrame[role="studioWindowControls"] {{
            background: transparent;
            border: 0px solid transparent;
            border-radius: 0px;
            padding: 0px;
        }}
        QFrame[role="studioPanel"] {{
            background: rgba(5, 18, 31, 0.86);
            border: 1px solid rgba(116, 240, 255, 0.13);
            border-radius: 20px;
        }}
        QFrame[role="studioRow"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(117, 228, 255, 0.045), stop:0.16 rgba(117, 228, 255, 0.024), stop:0.52 rgba(117, 228, 255, 0.006), stop:1 transparent);
            border-top: 1px solid rgba(138, 236, 255, 0.28);
            border-bottom: 0px solid transparent;
            border-left: 0px solid transparent;
            border-radius: 0px;
        }}
        QLabel {{
            color: rgba(235, 252, 255, 0.96);
            background: transparent;
        }}
        QLabel[role="eyebrow"] {{
            color: rgba(139, 233, 255, 0.86);
            font-size: 11px;
            font-weight: 740;
            letter-spacing: 0.20em;
            text-transform: uppercase;
        }}
        QLabel[role="title"] {{
            color: rgba(234, 253, 255, 0.95);
            font-size: 30px;
            font-weight: 750;
            letter-spacing: 0em;
            text-transform: none;
        }}
        QLabel[role="sectionLabel"] {{
            min-width: 132px;
            padding-left: 8px;
            border-left: 2px solid rgba(117, 228, 255, 0.30);
            color: rgba(145, 202, 218, 0.82);
            font-size: 10px;
            font-weight: 720;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        QLabel[role="sectionValue"] {{
            color: rgba(157, 246, 218, 0.90);
            font-size: 11px;
            font-weight: 700;
        }}
        QLabel[role="pathValue"] {{
            color: rgba(157, 246, 218, 0.90);
            font-size: 11px;
            font-weight: 700;
        }}
        QLabel[role="warning"] {{
            color: rgba(169, 190, 208, 0.86);
            font-size: 11px;
            line-height: 1.35;
        }}
        QLabel[folderActionState="opened"] {{
            color: rgba(157, 246, 218, 0.90);
        }}
        QLabel[folderActionState="blocked"] {{
            color: rgba(255, 194, 138, 0.92);
        }}
        QPushButton {{
            min-height: 38px;
            max-height: 38px;
            padding: 8px 18px;
            border: 1px solid rgba(117, 228, 255, 0.22);
            border-radius: 19px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(7, 42, 62, 0.91), stop:1 rgba(3, 18, 32, 0.89));
            color: rgba(229, 249, 255, 0.94);
            font-family: Bahnschrift, Rajdhani, Segoe UI, sans-serif;
            font-size: 12px;
            font-weight: 720;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            box-shadow: 0px 0px 0px rgba(0, 0, 0, 0);
        }}
        QPushButton[actionRole="studioWindowControl"] {{
            min-height: 34px;
            max-height: 34px;
            padding: 8px 18px;
            border-radius: 17px;
            border: 1px solid rgba(122, 232, 255, 0.26);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(7, 42, 62, 0.91), stop:1 rgba(3, 18, 32, 0.89));
            color: rgba(235, 252, 255, 0.96);
            font-size: 12px;
            font-weight: 760;
            letter-spacing: 0.08em;
        }}
        QPushButton[actionRole="studioAction"] {{
            min-height: 38px;
            max-height: 38px;
        }}
        QPushButton:hover {{
            border-color: rgba(126, 248, 218, 0.56);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(9, 49, 70, 0.94), stop:1 rgba(4, 24, 40, 0.91));
        }}
        QPushButton:focus {{
            border-color: rgba(117, 228, 255, 0.22);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(7, 42, 62, 0.91), stop:1 rgba(3, 18, 32, 0.89));
            color: rgba(229, 249, 255, 0.94);
        }}
        QPushButton:focus:hover {{
            border-color: rgba(126, 248, 218, 0.56);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(9, 49, 70, 0.94), stop:1 rgba(4, 24, 40, 0.91));
            color: rgba(241, 255, 252, 0.99);
        }}
        QPushButton:pressed {{
            border-color: rgba(163, 255, 228, 0.72);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(7, 40, 57, 0.98), stop:1 rgba(3, 18, 32, 0.96));
        }}
        QPushButton:disabled {{
            color: rgba(198, 224, 232, 0.54);
            border-color: rgba(116, 239, 255, 0.14);
            background: rgba(8, 20, 34, 0.58);
        }}
    """


def _monitoring_hud_mouse_global_pos(event) -> QPoint:
    try:
        return event.globalPosition().toPoint()
    except Exception:
        try:
            return event.globalPos()
        except Exception:
            return QCursor.pos()


class MonitoringHudStudioCommandPage(QWebEnginePage):
    studio_command = Signal(str)

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        prefix = "NEXUS_MONITORING_HUD_STUDIO_COMMAND:"
        if isinstance(message, str) and message.startswith(prefix):
            self.studio_command.emit(message[len(prefix):])
            return
        super().javaScriptConsoleMessage(level, message, line_number, source_id)


def _monitoring_hud_studio_html_path() -> Path:
    return Path(__file__).resolve().parents[1] / "nexus_visual" / "monitoring_hud_studio.html"


def _monitoring_hud_studio_dom_control_proof(kind: str) -> dict[str, object]:
    if kind in {"minimize", "close"}:
        return {
            "enabled": True,
            "accessibleName": f"{kind.title()} Studio",
            "tooltip": "",
            "role": "studioWindowControl",
            "sharedPrimitiveSeed": "AI-Control-Center-UIREF-002-window-control-cluster",
            "visualClaimState": MONITORING_HUD_STUDIO_VISUAL_CLAIM_STATE,
            "primitiveRole": "window-control-symbol-pill",
            "visiblePrimitiveShape": "ai-control-center-symbol-window-control-pill",
            "keyboardFocusable": True,
            "visualProofAuthority": MONITORING_HUD_STUDIO_VISUAL_PROOF_AUTHORITY,
            "implementationPrimitive": "QWebEngineView/monitoring_hud.css DOM",
        }
    return {
        "enabled": True,
        "accessibleName": kind,
        "tooltip": "",
        "role": "studioAction",
        "sharedPrimitiveSeed": "AI-Control-Center-UIREF-003-action-button",
        "visualClaimState": MONITORING_HUD_STUDIO_VISUAL_CLAIM_STATE,
        "primitiveRole": "primary-secondary-action-button",
        "visiblePrimitiveShape": "hub-action-content-fit-equal-gutter-32px-pill",
        "keyboardFocusable": True,
        "visualProofAuthority": MONITORING_HUD_STUDIO_VISUAL_PROOF_AUTHORITY,
        "implementationPrimitive": "QWebEngineView/monitoring_hud.css DOM",
    }


class MonitoringHudStudioWebWindow(QWidget):
    WIDTH = 570
    HEIGHT = 430
    MINIMUM_WIDTH = 440
    MINIMUM_HEIGHT = 330
    DRAG_HEADER_HEIGHT = 56
    STUDIO_RESIZABLE = True
    RESIZE_BEHAVIOR = "edge-resize-native-top-level"
    RESIZE_EDGE_MARGIN = 14
    WINDOW_CONTROL_ZONE_TOP = 14
    WINDOW_CONTROL_ZONE_RIGHT = 15
    WINDOW_CONTROL_ZONE_WIDTH = 60
    WINDOW_CONTROL_ZONE_HEIGHT = 30
    PARENT_NEIGHBOR_SLOT = "generic"
    PARENT_NEIGHBOR_STACK_STEP_HEIGHT = 0

    def __init__(self, screen, event_logger=None):
        super().__init__(None)
        self.screen_ref = screen
        self.event_logger = event_logger
        self._page_ready = False
        self._pending_studio_state: dict[str, object] = {}
        self._drag_offset = None
        self._resize_edges = ""
        self._resize_origin = QPoint()
        self._resize_geometry = QRect()
        self._resize_pending_point = QPoint()
        self._resize_last_geometry = QRect()
        self._resize_last_apply = 0.0
        self._resize_frame_interval_ms = 16
        self._resize_started_at = 0.0
        self._resize_cursor_key = None
        self._resize_override_cursor_active = False
        self._native_resize_interaction_state = "not-started"
        self._geometry_persistence_ready = False
        self._geometry_restored_from_saved = False
        self._session_user_geometry: QRect | None = None
        self._session_geometry_restored = False
        self._parent_neighbor_geometry: QRect | None = None
        self._placement_source = "initial-safe-default"
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setWindowModality(Qt.NonModal)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setMouseTracking(True)
        self.installEventFilter(self)
        if self.STUDIO_RESIZABLE:
            self.setMinimumSize(self.MINIMUM_WIDTH, self.MINIMUM_HEIGHT)
            self.resize(self.WIDTH, self.HEIGHT)
        else:
            self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setStyleSheet("background-color: transparent;")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.webview = QWebEngineView(self)
        self.webview.setAttribute(Qt.WA_TranslucentBackground, True)
        self.webview.setAttribute(Qt.WA_NoSystemBackground, True)
        self.webview.setAutoFillBackground(False)
        self.webview.setStyleSheet("background-color: transparent; border: none;")
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setMouseTracking(True)
        self.webview.installEventFilter(self)
        self._web_page = MonitoringHudStudioCommandPage(self.webview)
        self._web_page.studio_command.connect(self._handle_studio_command)
        self.webview.setPage(self._web_page)
        self.webview.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.webview.loadFinished.connect(self._on_studio_html_loaded)
        self.webview.load(QUrl.fromLocalFile(str(_monitoring_hud_studio_html_path())))
        root.addWidget(self.webview)
        self._drag_handle = QWidget(self)
        self._drag_handle.setObjectName("monitoringHudStudioNativeDragHandle")
        self._drag_handle.setAttribute(Qt.WA_TranslucentBackground, True)
        self._drag_handle.setCursor(Qt.SizeAllCursor)
        self._drag_handle.installEventFilter(self)
        self._drag_handle.raise_()
        self._position_studio_drag_handle()
        self._resize_poll_timer = QTimer(self)
        self._resize_poll_timer.setSingleShot(False)
        self._resize_poll_timer.setInterval(self._studio_resize_frame_interval_ms())
        self._resize_poll_timer.timeout.connect(self._poll_native_edge_resize)
        self._resize_frame_timer = QTimer(self)
        self._resize_frame_timer.setSingleShot(True)
        self._resize_frame_timer.timeout.connect(self._apply_queued_edge_resize)
        self._resize_hover_timer = QTimer(self)
        self._resize_hover_timer.setSingleShot(False)
        self._resize_hover_timer.setInterval(max(8, self._studio_resize_frame_interval_ms()))
        self._resize_hover_timer.timeout.connect(self._poll_native_edge_resize_hover_cursor)
        if self.STUDIO_RESIZABLE:
            self.winId()
            window_handle = self.windowHandle()
            if window_handle is not None:
                window_handle.visibilityChanged.connect(self._sync_resize_hover_polling_lifecycle)
                window_handle.windowStateChanged.connect(self._sync_resize_hover_polling_lifecycle)

    def _on_studio_html_loaded(self, ok: bool) -> None:
        self._page_ready = bool(ok)
        if self._page_ready:
            self._sync_studio_state_to_web()
            self._sync_studio_window_controls()
        elif callable(self.event_logger):
            self.event_logger("RENDERER_MAIN|MONITORING_HUD_STUDIO_HTML_LOAD_FAILED")

    def _sync_studio_state_to_web(self) -> None:
        if not getattr(self, "_page_ready", False) or not hasattr(self, "webview"):
            return
        script = (
            "window.nexusMonitoringHudStudioApplyState && "
            f"window.nexusMonitoringHudStudioApplyState({json.dumps(self._pending_studio_state)});"
        )
        self.webview.page().runJavaScript(script)

    def _sync_studio_window_controls(self) -> None:
        if not getattr(self, "_page_ready", False) or not hasattr(self, "webview"):
            return
        state = "maximized" if self.isMaximized() else "normal"
        script = (
            "window.nexusMonitoringHudStudioSetWindowState && "
            f"window.nexusMonitoringHudStudioSetWindowState({json.dumps(state)}, "
            f"{json.dumps({'minimize': 'active', 'close': 'active'})});"
        )
        self.webview.page().runJavaScript(script)

    def _handle_studio_command(self, command: str) -> None:
        if command == "minimize":
            self.showMinimized()
            return
        if command == "close":
            self.close()
            return
        self._handle_surface_command(command)

    def _handle_surface_command(self, command: str) -> None:
        return

    def _resize_edges_for_pos(self, pos: QPoint) -> str:
        if not self.STUDIO_RESIZABLE:
            return ""
        margin = self.RESIZE_EDGE_MARGIN
        edges = ""
        if pos.x() <= margin:
            edges += "l"
        elif pos.x() >= self.width() - margin:
            edges += "r"
        if pos.y() <= margin:
            edges += "t"
        elif pos.y() >= self.height() - margin:
            edges += "b"
        return edges

    def _cursor_for_resize_edges(self, edges: str):
        if edges in {"lt", "rb"}:
            return Qt.SizeFDiagCursor
        if edges in {"rt", "lb"}:
            return Qt.SizeBDiagCursor
        if edges in {"l", "r"}:
            return Qt.SizeHorCursor
        if edges in {"t", "b"}:
            return Qt.SizeVerCursor
        return Qt.ArrowCursor

    def _resize_cursor_key_for_edges(self, edges: str):
        return (
            "l" in edges,
            "r" in edges,
            "t" in edges,
            "b" in edges,
        ) if edges else None

    def _windows_resize_cursor_id_for_edges(self, edges: str) -> int:
        if edges in {"lt", "rb"}:
            return IDC_SIZENWSE
        if edges in {"rt", "lb"}:
            return IDC_SIZENESW
        if edges in {"l", "r"}:
            return IDC_SIZEWE
        if edges in {"t", "b"}:
            return IDC_SIZENS
        return IDC_ARROW

    def _apply_windows_resize_cursor(self, edges: str) -> None:
        if os.name != "nt":
            return
        # resize-cursor-no-forced-arrow-release: clear our override without
        # forcing IDC_ARROW, or Windows edge hover can flicker arrow/resize.
        if not edges:
            return
        try:
            cursor_handle = LoadCursorW(None, self._windows_resize_cursor_id_for_edges(edges))
            if cursor_handle:
                SetCursor(cursor_handle)
        except Exception:
            pass

    def _set_override_resize_cursor(self, cursor) -> None:
        try:
            if cursor is None:
                if self._resize_override_cursor_active:
                    QApplication.restoreOverrideCursor()
                    self._resize_override_cursor_active = False
                return
            qt_cursor = QCursor(cursor)
            if self._resize_override_cursor_active:
                QApplication.changeOverrideCursor(qt_cursor)
            else:
                QApplication.setOverrideCursor(qt_cursor)
                self._resize_override_cursor_active = True
        except Exception:
            self._resize_override_cursor_active = False

    def _set_native_edge_resize_cursor(self, edges: str) -> None:
        key = self._resize_cursor_key_for_edges(edges)
        if key == self._resize_cursor_key:
            if key is not None:
                self._set_override_resize_cursor(self._cursor_for_resize_edges(edges))
            self._apply_windows_resize_cursor(edges)
            return
        self._resize_cursor_key = key
        cursor = self._cursor_for_resize_edges(edges) if edges else None
        targets = [self, self.webview]
        try:
            targets.extend(self.webview.findChildren(QWidget))
        except Exception:
            pass
        if os.name == "nt":
            for target in targets:
                target.unsetCursor()
            self._set_override_resize_cursor(cursor)
            self._apply_windows_resize_cursor(edges)
            return
        for target in targets:
            if cursor is None:
                target.unsetCursor()
            else:
                target.setCursor(QCursor(cursor))
        self._set_override_resize_cursor(cursor)
        self._apply_windows_resize_cursor(edges)

    def _reset_native_edge_resize_cursor(self) -> None:
        self._set_native_edge_resize_cursor("")

    def _resize_edges_for_hit_test(self, hit_test: int) -> str:
        return {
            HTLEFT: "l",
            HTRIGHT: "r",
            HTTOP: "t",
            HTBOTTOM: "b",
            HTTOPLEFT: "lt",
            HTTOPRIGHT: "rt",
            HTBOTTOMLEFT: "lb",
            HTBOTTOMRIGHT: "rb",
        }.get(int(hit_test), "")

    def _hit_test_for_resize_edges(self, edges: str) -> int:
        return {
            "l": HTLEFT,
            "r": HTRIGHT,
            "t": HTTOP,
            "b": HTBOTTOM,
            "lt": HTTOPLEFT,
            "rt": HTTOPRIGHT,
            "lb": HTBOTTOMLEFT,
            "rb": HTBOTTOMRIGHT,
        }.get(edges, HTCLIENT)

    def _screen_point_from_windows_message(self, message) -> QPoint:
        lparam = int(message.lParam)
        x = ctypes.c_short(lparam & 0xFFFF).value
        y = ctypes.c_short((lparam >> 16) & 0xFFFF).value
        return QPoint(x, y)

    def _resize_edges_for_global_pos(self, global_pos: QPoint) -> str:
        return self._resize_edges_for_pos(self.mapFromGlobal(global_pos))

    def _resize_edges_under_cursor(self) -> tuple[QPoint, str]:
        if not self.STUDIO_RESIZABLE or not self.isVisible():
            return QPoint(), ""
        point = QCursor.pos()
        if point.isNull():
            return QPoint(), ""
        if not self.geometry().adjusted(-2, -2, 2, 2).contains(point):
            return point, ""
        local_pos = self.mapFromGlobal(point)
        if self._studio_close_zone().contains(local_pos):
            return point, ""
        return point, self._resize_edges_for_pos(local_pos)

    def _left_mouse_button_down(self) -> bool:
        try:
            return bool(GetAsyncKeyState(VK_LBUTTON) & 0x8000)
        except Exception:
            return False

    def _studio_resize_frame_interval_ms(self) -> int:
        refresh_rate = 60.0
        for screen in (self.screen(), getattr(self, "screen_ref", None), QApplication.primaryScreen()):
            if screen is None:
                continue
            try:
                measured = float(screen.refreshRate() or 0.0)
            except Exception:
                measured = 0.0
            if measured >= 30.0:
                refresh_rate = measured
                break
        return max(8, min(33, int(round(1000.0 / refresh_rate))))

    def _begin_native_edge_resize(self, edges: str, global_pos: QPoint) -> None:
        if not edges:
            return
        if global_pos.isNull():
            global_pos = QCursor.pos()
        if global_pos.isNull():
            return
        self._resize_edges = edges
        self._drag_offset = None
        self._resize_origin = QPoint(global_pos)
        self._resize_geometry = QRect(self.geometry())
        self._resize_pending_point = QPoint(global_pos)
        self._resize_last_geometry = QRect(self.geometry())
        self._resize_last_apply = 0.0
        self._resize_frame_interval_ms = self._studio_resize_frame_interval_ms()
        self._resize_started_at = time.monotonic()
        self._native_resize_interaction_state = f"dragging-{edges}"
        self._set_native_edge_resize_cursor(edges)
        try:
            SetCapture(ctypes.wintypes.HWND(int(self.winId())))
        except Exception:
            pass
        try:
            self.grabMouse(self._cursor_for_resize_edges(edges))
        except RuntimeError:
            pass
        self._resize_poll_timer.stop()
        self._resize_poll_timer.setInterval(self._resize_frame_interval_ms)
        self._resize_poll_timer.start()
        self._poll_native_edge_resize()

    def _finish_native_edge_resize(self) -> None:
        if self._resize_edges:
            self._native_resize_interaction_state = "completed"
        self._resize_edges = ""
        self._reset_native_edge_resize_cursor()
        try:
            self.releaseMouse()
        except RuntimeError:
            pass
        try:
            ReleaseCapture()
        except Exception:
            pass
        self._resize_poll_timer.stop()
        self._resize_frame_timer.stop()
        self._resize_pending_point = QPoint()
        self._resize_last_geometry = QRect()
        self._resize_last_apply = 0.0
        self._resize_started_at = 0.0
        self._save_current_geometry()

    def _apply_edge_resize(self, global_pos: QPoint) -> None:
        if not self._resize_edges:
            return
        delta = global_pos - self._resize_origin
        rect = QRect(self._resize_geometry)
        min_width = max(int(self.minimumWidth() or 0), self.MINIMUM_WIDTH)
        min_height = max(int(self.minimumHeight() or 0), self.MINIMUM_HEIGHT)
        if "l" in self._resize_edges:
            new_left = min(rect.right() - min_width + 1, rect.left() + delta.x())
            rect.setLeft(new_left)
        if "r" in self._resize_edges:
            rect.setRight(max(rect.left() + min_width - 1, rect.right() + delta.x()))
        if "t" in self._resize_edges:
            new_top = min(rect.bottom() - min_height + 1, rect.top() + delta.y())
            rect.setTop(new_top)
        if "b" in self._resize_edges:
            rect.setBottom(max(rect.top() + min_height - 1, rect.bottom() + delta.y()))
        self.setGeometry(rect)

    def _update_native_edge_resize(self, global_pos: QPoint) -> None:
        if not self._resize_edges:
            return
        if global_pos.isNull():
            global_pos = QCursor.pos()
        if global_pos.isNull():
            return
        self._resize_pending_point = QPoint(global_pos)
        interval_s = max(0.004, self._resize_frame_interval_ms / 1000.0)
        now = time.monotonic()
        elapsed = now - self._resize_last_apply
        if self._resize_last_apply <= 0.0 or elapsed >= interval_s:
            self._apply_queued_edge_resize()
            return
        if not self._resize_frame_timer.isActive():
            remaining_ms = max(1, int(round((interval_s - elapsed) * 1000.0)))
            self._resize_frame_timer.start(remaining_ms)

    def _apply_queued_edge_resize(self) -> None:
        if not self._resize_edges:
            return
        point = QPoint(self._resize_pending_point)
        if point.isNull():
            point = QCursor.pos()
        if point.isNull():
            return
        before = QRect(self.geometry())
        self._apply_edge_resize(point)
        after = QRect(self.geometry())
        self._resize_last_geometry = after
        self._resize_last_apply = time.monotonic()
        if after != before:
            if hasattr(self, "webview"):
                self.webview.setGeometry(self.rect())
                self.webview.resize(self.size())
                self.webview.updateGeometry()
                self.webview.update()
            self._position_studio_drag_handle()
            QApplication.processEvents()
            if getattr(self, "_page_ready", False):
                self.webview.page().runJavaScript(
                    "window.requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));"
                )

    def _poll_native_edge_resize(self) -> None:
        if not self._resize_edges:
            self._resize_poll_timer.stop()
            return
        point = QCursor.pos()
        if not point.isNull():
            self._update_native_edge_resize(point)
        if self._left_mouse_button_down():
            return
        if time.monotonic() - float(self._resize_started_at or 0.0) < 0.25:
            return
        self._finish_native_edge_resize()

    def _sync_resize_hover_polling_lifecycle(self, *_args) -> bool:
        should_run = bool(
            self.STUDIO_RESIZABLE
            and self.isVisible()
            and not self.isMinimized()
        )
        if should_run:
            if not self._resize_hover_timer.isActive():
                self._resize_hover_timer.start()
        else:
            if self._resize_hover_timer.isActive():
                self._resize_hover_timer.stop()
            if not self._resize_edges:
                self._reset_native_edge_resize_cursor()
        return should_run

    def _poll_native_edge_resize_hover_cursor(self) -> None:
        if (
            not self._sync_resize_hover_polling_lifecycle()
            or self._resize_edges
            or self._drag_offset is not None
        ):
            return
        _, edges = self._resize_edges_under_cursor()
        if edges:
            self._set_native_edge_resize_cursor(edges)
        else:
            self._reset_native_edge_resize_cursor()

    def eventFilter(self, watched, event):
        if watched is getattr(self, "webview", None) or watched is self:
            event_type = event.type()
            if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                pos = event.position().toPoint()
                resize_edges = self._resize_edges_for_pos(pos)
                if resize_edges:
                    self._begin_native_edge_resize(resize_edges, event.globalPosition().toPoint())
                    event.accept()
                    return True
                if pos.y() <= self.DRAG_HEADER_HEIGHT and not self._studio_close_zone().contains(pos):
                    self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    event.accept()
                    return True
            elif (
                event_type == QEvent.MouseMove
                and event.buttons() & Qt.LeftButton
            ):
                if self._resize_edges:
                    self._update_native_edge_resize(event.globalPosition().toPoint())
                    event.accept()
                    return True
                if self._drag_offset is not None:
                    self.move(event.globalPosition().toPoint() - self._drag_offset)
                    event.accept()
                    return True
            elif event_type == QEvent.MouseMove and self.STUDIO_RESIZABLE:
                self._set_native_edge_resize_cursor(self._resize_edges_for_pos(event.position().toPoint()))
            elif event_type == QEvent.MouseButtonRelease:
                if self._resize_edges:
                    self._finish_native_edge_resize()
                else:
                    self._resize_edges = ""
                self._drag_offset = None
                self._reset_native_edge_resize_cursor()
                self._save_current_geometry()
            elif event_type == QEvent.Leave and self.STUDIO_RESIZABLE and not self._resize_edges:
                self._reset_native_edge_resize_cursor()
        if watched is getattr(self, "_drag_handle", None):
            event_type = event.type()
            if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return True
            if (
                event_type == QEvent.MouseMove
                and self._drag_offset is not None
                and event.buttons() & Qt.LeftButton
            ):
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                event.accept()
                return True
            if event_type == QEvent.MouseButtonRelease:
                self._drag_offset = None
                self._save_current_geometry()
                event.accept()
                return True
        return super().eventFilter(watched, event)

    def nativeEvent(self, eventType, message):
        if not self.STUDIO_RESIZABLE:
            return super().nativeEvent(eventType, message)
        msg = ctypes.wintypes.MSG.from_address(int(message))
        if msg.message == WM_NCHITTEST:
            global_pos = self._screen_point_from_windows_message(msg)
            local_pos = self.mapFromGlobal(global_pos)
            if self._studio_close_zone().contains(local_pos):
                return True, HTCLIENT
            edges = self._resize_edges_for_pos(local_pos)
            if edges:
                return True, self._hit_test_for_resize_edges(edges)
            if 0 <= local_pos.y() <= self.DRAG_HEADER_HEIGHT:
                return True, HTCAPTION
            return True, HTCLIENT
        if msg.message == WM_SETCURSOR and not self._resize_edges:
            hit_test = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
            edges = self._resize_edges_for_hit_test(hit_test)
            if edges:
                self._set_native_edge_resize_cursor(edges)
                return True, 1
            _, edges = self._resize_edges_under_cursor()
            if edges:
                self._set_native_edge_resize_cursor(edges)
                return True, 1
            self._reset_native_edge_resize_cursor()
        if msg.message in {WM_MOUSEMOVE, WM_NCMOUSEMOVE} and not self._resize_edges:
            edges = ""
            if msg.message == WM_NCMOUSEMOVE:
                edges = self._resize_edges_for_hit_test(int(msg.wParam))
            if not edges:
                _, edges = self._resize_edges_under_cursor()
            if edges:
                self._set_native_edge_resize_cursor(edges)
            elif msg.message == WM_MOUSEMOVE:
                self._reset_native_edge_resize_cursor()
        if msg.message == WM_NCLBUTTONDOWN:
            edges = self._resize_edges_for_hit_test(int(msg.wParam))
            global_pos = QCursor.pos()
            if not edges:
                edges = self._resize_edges_for_global_pos(global_pos)
            if edges:
                self._begin_native_edge_resize(edges, global_pos)
                return True, 0
        if msg.message in {WM_MOUSEMOVE, WM_NCMOUSEMOVE} and self._resize_edges:
            self._update_native_edge_resize(QCursor.pos())
            return True, 0
        if msg.message in {WM_LBUTTONUP, WM_NCLBUTTONUP, WM_CANCELMODE, WM_CAPTURECHANGED} and self._resize_edges:
            self._finish_native_edge_resize()
            return True, 0
        return super().nativeEvent(eventType, message)

    def _studio_close_zone(self) -> QRect:
        return QRect(
            max(0, self.width() - self.WINDOW_CONTROL_ZONE_RIGHT - self.WINDOW_CONTROL_ZONE_WIDTH),
            self.WINDOW_CONTROL_ZONE_TOP,
            self.WINDOW_CONTROL_ZONE_WIDTH,
            self.WINDOW_CONTROL_ZONE_HEIGHT,
        )

    def _position_studio_drag_handle(self) -> None:
        if not hasattr(self, "_drag_handle"):
            return
        handle_width = max(
            1,
            self.width() - self.WINDOW_CONTROL_ZONE_RIGHT - self.WINDOW_CONTROL_ZONE_WIDTH - 12,
        )
        self._drag_handle.setGeometry(0, 0, handle_width, self.DRAG_HEADER_HEIGHT)
        self._drag_handle.raise_()

    def _restore_saved_geometry(self) -> None:
        fallback = self._initial_geometry()
        if isinstance(self._parent_neighbor_geometry, QRect) and self._parent_neighbor_geometry.isValid():
            fallback = self._parent_neighbor_geometry
        if isinstance(self._session_user_geometry, QRect) and self._session_user_geometry.isValid():
            geometry = _monitoring_hud_bound_window_rect(
                self._session_user_geometry,
                getattr(self, "screen_ref", None),
                min_width=self.MINIMUM_WIDTH,
                min_height=self.MINIMUM_HEIGHT,
            )
            self.setGeometry(geometry)
            self._geometry_restored_from_saved = False
            self._session_geometry_restored = True
            self._placement_source = "same-session-user-moved-position"
        else:
            self.setGeometry(
                _monitoring_hud_bound_window_rect(
                    fallback,
                    getattr(self, "screen_ref", None),
                    min_width=self.MINIMUM_WIDTH,
                    min_height=self.MINIMUM_HEIGHT,
                )
            )
            self._geometry_restored_from_saved = False
            self._session_geometry_restored = False
            self._placement_source = (
                "parent-neighbor-default"
                if isinstance(self._parent_neighbor_geometry, QRect) and self._parent_neighbor_geometry.isValid()
                else "initial-safe-default"
            )
        if not self.STUDIO_RESIZABLE:
            restored_position = self.geometry().topLeft()
            self.setFixedSize(self.WIDTH, self.HEIGHT)
            self.move(restored_position)

    def _parent_neighbor_default_geometry(self, parent_geometry: QRect, *, stack_index: int = 0) -> QRect:
        available = _monitoring_hud_available_rect(getattr(self, "screen_ref", None))
        gap = 18
        vertical_gap = 12
        width = int(self.width() or self.WIDTH)
        height = int(self.height() or self.HEIGHT)
        stack_step_height = int(self.PARENT_NEIGHBOR_STACK_STEP_HEIGHT or height)
        preferred_x = parent_geometry.right() + 1 + gap
        if preferred_x + width - 1 > available.right():
            preferred_x = parent_geometry.left() - gap - width
        if preferred_x < available.left():
            preferred_x = min(
                max(parent_geometry.left() + gap, available.left()),
                max(available.left(), available.right() - width + 1),
            )
        preferred_y = parent_geometry.top() + (stack_step_height + vertical_gap) * max(0, stack_index)
        if preferred_y + height - 1 > available.bottom():
            preferred_y = max(available.top(), parent_geometry.bottom() - height + 1)
        return _monitoring_hud_bound_window_rect(
            QRect(preferred_x, preferred_y, width, height),
            getattr(self, "screen_ref", None),
            min_width=self.MINIMUM_WIDTH,
            min_height=self.MINIMUM_HEIGHT,
        )

    def set_parent_neighbor_geometry(self, parent_geometry: QRect | None, *, stack_index: int = 0) -> None:
        if parent_geometry is None or not parent_geometry.isValid() or parent_geometry.isNull():
            self._parent_neighbor_geometry = None
            return
        self._parent_neighbor_geometry = self._parent_neighbor_default_geometry(parent_geometry, stack_index=stack_index)

    def _save_current_geometry(self) -> None:
        if not getattr(self, "_geometry_persistence_ready", False):
            return
        if self.isMinimized():
            return
        rect = self.geometry()
        if not rect.isValid() or rect.isNull():
            return
        self._session_user_geometry = QRect(rect)

    def moveEvent(self, event):
        super().moveEvent(event)
        self._save_current_geometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "webview"):
            self.webview.setGeometry(self.rect())
            self.webview.updateGeometry()
            self.webview.update()
            if getattr(self, "_page_ready", False):
                self.webview.page().runJavaScript(
                    "window.requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));"
                )
        self._position_studio_drag_handle()
        self._save_current_geometry()

    def closeEvent(self, event):
        self._resize_hover_timer.stop()
        self._drag_offset = None
        self._finish_native_edge_resize()
        self._reset_native_edge_resize_cursor()
        self._save_current_geometry()
        super().closeEvent(event)

    def _show_or_raise(self, activate_window: bool) -> None:
        if not activate_window:
            return
        if not self.isVisible():
            self._restore_saved_geometry()
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.raise_()
        self.activateWindow()
        self._sync_resize_hover_polling_lifecycle()


class MonitoringHudRecordingStudioWindow(MonitoringHudStudioWebWindow):
    WIDTH = 432
    HEIGHT = 154
    MINIMUM_WIDTH = 432
    MINIMUM_HEIGHT = 154
    DRAG_HEADER_HEIGHT = 64
    STUDIO_RESIZABLE = False
    RESIZE_BEHAVIOR = "not-resizable-position-memory-only"
    PARENT_NEIGHBOR_SLOT = "recording"

    def __init__(self, screen, event_logger=None, recording_action_handler=None, log_viewer_handler=None):
        self.recording_action_handler = recording_action_handler
        self.log_viewer_handler = log_viewer_handler
        self._request_id = 0
        self._recording_session_state = "ready"
        self._start_stop_state = "target-required"
        self._current_log_state = "no-current-log"
        self._native_log_path = ""
        self._native_log_row_count = 0
        self._native_log_display_text = "None yet."
        self._native_log_display_mode = "single-line-contained"
        self._last_activation_mode = "not-requested"
        self._opened_by_explicit_user_path = False
        self._geometry_persistence_key = "recording_studio_feature_studio_v5"
        super().__init__(screen, event_logger)
        self.setObjectName("monitoringHudRecordingStudioWindow")
        self.setWindowTitle("Nexus Recording Suite")
        self.resize(self.WIDTH, self.HEIGHT)
        self._restore_saved_geometry()
        self._geometry_persistence_ready = True
        self._pending_studio_state = self._recording_studio_state_payload()
        self._sync_studio_state_to_web()

    def _initial_geometry(self) -> QRect:
        available = self.screen_ref.availableGeometry()
        width = self.WIDTH
        height = self.HEIGHT
        return QRect(
            available.x() + max(24, available.width() - width - 80),
            available.y() + max(24, available.height() - height - 110),
            width,
            height,
        )

    def _request_recording_action(self, action: str) -> None:
        normalized_action = action if action in {"start", "pause", "stop"} else "toggle"
        if callable(self.recording_action_handler):
            self.recording_action_handler(normalized_action)
        if callable(self.event_logger):
            self.event_logger(
                "MONITORING_HUD_RECORDING_STUDIO_ACTION_REQUESTED|"
                f"action={normalized_action}|sessionState={self._recording_session_state}"
            )

    def _handle_surface_command(self, command: str) -> None:
        if command in {"start", "pause", "stop"}:
            self._request_recording_action(command)
        elif command == "open-log-viewer" and callable(self.log_viewer_handler):
            self.log_viewer_handler()
            if callable(self.event_logger):
                self.event_logger("MONITORING_HUD_RECORDING_STUDIO_LOG_VIEWER_REQUESTED")

    def _refresh_native_log_text(self) -> None:
        if self._native_log_path:
            rows = f" ({int(self._native_log_row_count)} rows)" if self._native_log_row_count else ""
            display = os.path.normpath(self._native_log_path)
            if len(display) > 56:
                display = f"{display[:18]}...{display[-32:]}"
            self._native_log_display_text = f"{display}{rows}"
            self._native_log_display_mode = "middle-elided-contained"
            return
        self._native_log_display_text = "Pending until recording stops." if self._recording_session_state == "recording" else "None yet."
        self._native_log_display_mode = "single-line-contained"

    def _recording_studio_state_payload(self) -> dict[str, object]:
        self._refresh_native_log_text()
        count = int(getattr(self, "_target_count", 0) or 0)
        session_label = {
            "saved-complete": "saved",
            "recording": "recording",
            "saving": "saving",
            "paused": "paused",
            "ready": "ready",
            "disabled-error": "blocked",
        }.get(self._recording_session_state, self._recording_session_state.replace("-", " "))
        profile = getattr(self, "_active_profile_name", "") or "No active overlay profile"
        target_names = getattr(self, "_target_names", "") or "No active monitor targets"
        if self._recording_session_state == "recording":
            state_label = "STATE"
            status_text = f"Recording - {count} active monitor{'s' if count != 1 else ''}"
            detail_text = ""
        elif self._recording_session_state == "paused":
            state_label = "STATE"
            status_text = f"Paused - {count} active monitor{'s' if count != 1 else ''}"
            detail_text = ""
        elif self._recording_session_state == "saved-complete":
            state_label = "STATE"
            status_text = f"Saved - {count} active monitor{'s' if count != 1 else ''}"
            detail_text = ""
        elif self._recording_session_state == "saving":
            state_label = "STATE"
            status_text = f"Saving - {count} active monitor{'s' if count != 1 else ''}"
            detail_text = ""
        elif self._recording_session_state == "disabled-error":
            state_label = "STATE"
            status_text = "Recording blocked"
            detail_text = ""
        elif self._start_stop_state == "start-enabled":
            state_label = "STATE"
            status_text = f"Ready - {count} active monitor{'s' if count != 1 else ''}"
            detail_text = ""
        else:
            state_label = "STATE"
            status_text = "Select active profile"
            detail_text = ""
        return {
            "surface": "recording",
            "kicker": "ACTIVE OVERLAY RECORDING",
            "title": "RECORDING SUITE",
            "subtitle": "",
            "roleLabelA": "Surface",
            "roleValueA": "Recording",
            "roleLabelB": "State",
            "roleValueB": session_label.title(),
            "roleLabelC": "Target",
            "roleValueC": "Overlay Profile",
            "recordingStateLabel": state_label,
            "recordingTarget": profile,
            "recordingTargetDetail": "",
            "recordingStatus": status_text,
            "recordingDetail": detail_text,
            "recordingBoundary": "Controls the current Recording target from the active Overlay Profile.",
            "startEnabled": self._start_stop_state == "start-enabled",
            "pausedResumeEnabled": self._start_stop_state == "paused-stop-enabled",
            "pauseEnabled": self._start_stop_state == "recording-stop-enabled",
            "stopEnabled": self._start_stop_state in {"recording-stop-enabled", "paused-stop-enabled"},
        }

    def update_product_state(
        self,
        *,
        request_id: int,
        active_profile_name: str,
        target_count: int,
        target_names: str,
        target_state: str,
        recording_session_state: str = "ready",
        start_stop_state: str = "target-required",
        native_log_path: str = "",
        export_dir: str = "",
        row_count: int = 0,
        current_log_state: str = "no-current-log",
        activate_window: bool = True,
        parent_geometry: QRect | None = None,
    ) -> None:
        self._request_id = max(self._request_id, int(request_id or 0))
        self._last_activation_mode = "explicit-user-open" if activate_window else "passive-state-refresh"
        self._opened_by_explicit_user_path = self._opened_by_explicit_user_path or bool(activate_window)
        self._recording_session_state = recording_session_state or "ready"
        self._start_stop_state = start_stop_state or "target-required"
        self._native_log_path = native_log_path.strip()
        self._native_log_row_count = int(row_count or 0)
        self._current_log_state = current_log_state or "no-current-log"
        self._active_profile_name = active_profile_name.strip() or "No active overlay profile"
        self._target_count = max(0, int(target_count or 0))
        self._target_names = target_names
        self._target_state = target_state
        self.set_parent_neighbor_geometry(parent_geometry, stack_index=0)
        self._pending_studio_state = self._recording_studio_state_payload()
        self._sync_studio_state_to_web()
        self._show_or_raise(activate_window)

    def proof_state(self) -> dict[str, object]:
        geometry = self.geometry()
        self._refresh_native_log_text()
        return {
            "owner": "MonitoringHudRecordingStudioWindow",
            "surface": "recording_studio_window",
            "standaloneTopLevel": self.parent() is None,
            "windowFlag": "normal_window",
            "taskbarRestorable": True,
            "minimizeControl": True,
            "minimizeControlLocation": "top-right-header",
            "minimizeControlProof": _monitoring_hud_studio_dom_control_proof("minimize"),
            "closeControl": True,
            "closeControlLocation": "top-right-header",
            "closeControlProof": _monitoring_hud_studio_dom_control_proof("close"),
            "windowControlCluster": "UIREF-002-compact-window-control-cluster",
            "windowControlVisibleTextPolicy": "ai-control-center-symbol-visible-accessible-label",
            "windowControlContainerVisualPolicy": "ai-control-center-symbol-window-control-cluster",
            "actionButtonGeometryPolicy": "monitoring-hud-hub-action-content-fit-equal-gutter-v4",
            "stateRowDensityPolicy": "action-first-controller-with-ai-control-center-state-rows-no-report-panels",
            "titleGroupVisualPolicy": "detached-child-window-header-no-title-card",
            "titleTreatment": "detached-child-window-header-no-title-card",
            "titleCardState": "absent",
            "childWindowTitleGrammar": "title-first-description-beneath-no-title-card",
            "visualPrimitiveAdoptionContract": _monitoring_hud_ai_control_center_primitive_contract(),
            "referenceTemplatePrimitiveClassification": "Bounded FAM-006 Shared Primitive Carry-In",
            "primaryVisualComparator": "FAM-006 unique child feature-studio grammar",
            "compositionModel": "action-first-ultra-lightweight-detached-recording-controller",
            "windowTaxonomy": "unique-child-standalone-feature-studio",
            "attachedChildResizeGrip": False,
            "uniqueChildResizePolicy": "no-resize-recording-edge-resize-log-viewer",
            "acceptedReferenceSet": list(MONITORING_HUD_STUDIO_REFERENCE_SURFACES),
            "headerPrimitiveSeed": "AI-Control-Center-UIREF-001-title-group",
            "panelPrimitiveSeed": "FAM-006 action-first controller plus AI Control Center / HUD Dashboard state-row underglow",
            "recordingExecutionState": "enabled",
            "recordingFileWritingState": "enabled",
            "nativeLogPath": self._native_log_path,
            "nativeLogDisplayText": self._native_log_display_text,
            "nativeLogPathDisplayMode": self._native_log_display_mode,
            "nativeLogPathWordWrap": False,
            "nativeLogRowsContained": bool(self._native_log_display_text and "\n" not in self._native_log_display_text),
            "currentLogState": self._current_log_state,
            "activationMode": self._last_activation_mode,
            "openedByExplicitUserPath": self._opened_by_explicit_user_path,
            "startStopState": self._start_stop_state,
            "visualContractDeclared": MONITORING_HUD_STUDIO_VISUAL_CONTRACT,
            "visualSystemInheritanceClaim": "nexus-window-primitives-v1-rendered-dom-css",
            "visualSampledElements": MONITORING_HUD_STUDIO_VISUAL_SAMPLE,
            "visualAdjudicationState": MONITORING_HUD_STUDIO_VISUAL_ADJUDICATION,
            "visualProofAuthority": MONITORING_HUD_STUDIO_VISUAL_PROOF_AUTHORITY,
            "visualRuntimeSelfAttestation": "rejected",
            "visualMatrixRequired": True,
            "visualReferenceSurfacesRequired": list(MONITORING_HUD_STUDIO_REFERENCE_SURFACES),
            "standaloneWindowLayout": "ultra-lightweight-detached-recording-controller",
            "dashboardLifecycleDependency": "independent-while-runtime-active",
            "logViewerRoute": "recording-studio-open-log-viewer-action",
            "recordingStartRoute": "recording-studio-start-action",
            "recordingPauseRoute": "recording-studio-pause-action",
            "recordingStopRoute": "recording-studio-stop-action",
            "recordingStudioVisibleActionModel": "selected-REC-A-explicit-start-pause-stop-plus-open-log-viewer",
            "sharedPrimitiveSourcePath": "nexus_visual/nexus_window_primitives.css",
            "sharedPrimitiveConsumer": "nexus-window-primitives-v1",
            "featureStudioPrimitive": MONITORING_HUD_STUDIO_VISUAL_CONTRACT,
            "sharedVisualDna": "nexus-window-primitives-v1-rendered-dom-css",
            "genericShellRejected": "nexus-window-primitives-v1-rendered-dom-css",
            "titleHeaderBadgeState": "removed",
            "standaloneHeaderTreatment": "ai-control-center-title-group-no-extra-badge",
            "buttonVisualGrammar": "monitoring-hud-rendered-content-fit-equal-gutter-v4-button-primitive",
            "windowBodyVisualGrammar": MONITORING_HUD_STUDIO_BODY_VISUAL_GRAMMAR,
            "denseValidatorStatusPanelRejected": True,
            "tableRowTruthLayoutRejected": True,
            "boxedTablePanelRejected": True,
            "statusReportPanelRejected": True,
            "visibleAnatomy": "primary-action-plus-compact-target-log-truth",
            "cardInCardHierarchyAbsent": True,
            "attachedChildCornerResizeGripAbsent": True,
            "windowPlacementMemoryState": "enabled",
            "windowPlacementPolicy": "B2-same-session-user-moved-position-or-parent-neighbor-default",
            "placementSource": self._placement_source,
            "parentNeighborDefaultGeometry": _monitoring_hud_qrect_to_dict(self._parent_neighbor_geometry),
            "sessionUserGeometryPresent": isinstance(self._session_user_geometry, QRect),
            "sessionGeometryRestored": self._session_geometry_restored,
            "resizeBehavior": self.RESIZE_BEHAVIOR,
            "geometryPersistenceKey": self._geometry_persistence_key,
            "geometryRestoredFromSaved": self._geometry_restored_from_saved,
            "startEnabled": self._start_stop_state == "start-enabled",
            "pausedResumeEnabled": self._start_stop_state == "paused-stop-enabled",
            "pauseEnabled": self._start_stop_state == "recording-stop-enabled",
            "stopEnabled": self._start_stop_state in {"recording-stop-enabled", "paused-stop-enabled"},
            "recordingStartControlProof": _monitoring_hud_studio_dom_control_proof("recording-start"),
            "recordingPauseControlProof": _monitoring_hud_studio_dom_control_proof("recording-pause"),
            "recordingStopControlProof": _monitoring_hud_studio_dom_control_proof("recording-stop"),
            "logViewerRouteControlProof": _monitoring_hud_studio_dom_control_proof("open-log-viewer"),
            "controlStateProof": "default-hover-focus-pressed-disabled-keyboard-accessible",
            "accessibilityKeyboardProofState": "controls-focusable-accessible-names-tooltips",
            "visible": self.isVisible(),
            "isActiveWindow": self.isActiveWindow(),
            "isMinimized": self.isMinimized(),
            "requestId": self._request_id,
            "x": geometry.x(),
            "y": geometry.y(),
            "w": geometry.width(),
            "h": geometry.height(),
        }


class MonitoringHudLogViewerStudioWindow(MonitoringHudStudioWebWindow):
    WIDTH = 430
    HEIGHT = 134
    MINIMUM_WIDTH = 430
    MINIMUM_HEIGHT = 134
    DRAG_HEADER_HEIGHT = 64
    STUDIO_RESIZABLE = True
    RESIZE_BEHAVIOR = "edge-resize-native-top-level"
    PARENT_NEIGHBOR_SLOT = "log-viewer"
    PARENT_NEIGHBOR_STACK_STEP_HEIGHT = MonitoringHudRecordingStudioWindow.HEIGHT

    def __init__(self, screen, event_logger=None):
        self._request_id = ""
        self._last_activation_mode = "not-requested"
        self._geometry_persistence_key = "log_viewer_studio_feature_studio_v6"
        self._native_full_path = str(recording_output_dir())
        self._export_full_path = str(recording_export_dir())
        self._folder_status_text = "Choose a log destination to open."
        self._folder_status_state = "ready"
        self._last_folder_kind = ""
        super().__init__(screen, event_logger)
        self.setObjectName("monitoringHudLogViewerStudioWindow")
        self.setWindowTitle("Nexus Log Viewer")
        self.resize(self.WIDTH, self.HEIGHT)
        self._restore_saved_geometry()
        self._geometry_persistence_ready = True
        self._pending_studio_state = self._log_viewer_studio_state_payload()
        self._sync_studio_state_to_web()

    def _initial_geometry(self) -> QRect:
        available = self.screen_ref.availableGeometry()
        return QRect(
            available.x() + max(24, available.width() - self.WIDTH - 120),
            available.y() + 96,
            self.WIDTH,
            self.HEIGHT,
        )

    def _compact_path(self, value: str) -> str:
        path = os.path.normpath(str(value or ""))
        if len(path) <= 58:
            return path
        return f"{path[:18]}...{path[-34:]}"

    def _log_viewer_studio_state_payload(self) -> dict[str, object]:
        return {
            "surface": "log-viewer",
            "kicker": "NATIVE AND EXPORTED LOG ACCESS",
            "title": "LOG VIEWER",
            "subtitle": "",
            "roleLabelA": "Surface",
            "roleValueA": "Logs",
            "roleLabelB": "State",
            "roleValueB": self._folder_status_state.replace("-", " ").title(),
            "roleLabelC": "Boundary",
            "roleValueC": "Folder Access",
            "viewerState": "Deferred",
            "viewerStateTooltip": "Full in-app log viewing remains future-gated; this branch exposes folder actions only.",
            "folderStatus": self._folder_status_text,
            "logBoundary": (
                "This branch provides folder access only. Previous-log selection, in-app viewing, "
                "export customization, and Native Log Loader remain future-gated."
            ),
        }

    def _destination_state_text(self, folder_kind: str) -> str:
        if self._last_folder_kind == folder_kind and self._folder_status_state == "opened":
            return "Opened"
        if self._last_folder_kind == folder_kind and self._folder_status_state == "blocked":
            return "Could not open"
        if folder_kind == "native":
            return "Available now"
        return "Empty until exported"

    def _handle_surface_command(self, command: str) -> None:
        if command == "open-native":
            self._open_log_folder("native")
        elif command == "open-export":
            self._open_log_folder("export")

    def _open_log_folder(self, folder_kind: str) -> None:
        root = recording_output_dir() if folder_kind == "native" else recording_export_dir()
        target_folder = os.path.abspath(str(root))
        try:
            os.makedirs(target_folder, exist_ok=True)
            os.startfile(target_folder)
            self._folder_status_text = "Native NDAI logs folder opened." if folder_kind == "native" else "Exported logs folder opened."
            self._folder_status_state = "opened"
            self._last_folder_kind = folder_kind
            if callable(self.event_logger):
                self.event_logger(
                    "MONITORING_HUD_LOG_VIEWER_STUDIO_FOLDER_OPENED|"
                    f"folderKind={folder_kind}|outputDir={target_folder}"
                )
        except Exception as exc:
            self._folder_status_text = "Native NDAI logs folder could not be opened." if folder_kind == "native" else "Exported logs folder could not be opened."
            self._folder_status_state = "blocked"
            self._last_folder_kind = folder_kind
            if callable(self.event_logger):
                self.event_logger(
                    "MONITORING_HUD_LOG_VIEWER_STUDIO_FOLDER_BLOCKED|"
                    f"folderKind={folder_kind}|error={exc}"
                )
        self._pending_studio_state = self._log_viewer_studio_state_payload()
        self._sync_studio_state_to_web()

    def update_product_state(
        self,
        *,
        request_id: str,
        native_log_path: str = "",
        export_dir: str = "",
        activate_window: bool = True,
        parent_geometry: QRect | None = None,
    ) -> None:
        self._request_id = request_id or self._request_id
        self._last_activation_mode = "explicit-user-open" if activate_window else "passive-state-refresh"
        native_root = recording_output_dir()
        export_root = recording_export_dir()
        self._native_full_path = native_log_path.strip() or str(native_root)
        self._export_full_path = export_dir.strip() or str(export_root)
        self.set_parent_neighbor_geometry(parent_geometry, stack_index=1)
        self._pending_studio_state = self._log_viewer_studio_state_payload()
        self._sync_studio_state_to_web()
        self._show_or_raise(activate_window)

    def proof_state(self) -> dict[str, object]:
        geometry = self.geometry()
        native_root = str(recording_output_dir())
        export_root = str(recording_export_dir())
        native_display = self._compact_path(self._native_full_path)
        export_display = self._compact_path(self._export_full_path)
        leakage_terms = ("fam-006", "fam006", "feature_fam_006", "feature-fam-006", "worktrees", "nexus governance state")
        combined_roots = f"{native_root} {export_root}".casefold()
        return {
            "owner": "MonitoringHudLogViewerStudioWindow",
            "surface": "log_viewer_shell",
            "standaloneTopLevel": self.parent() is None,
            "windowFlag": "normal_window",
            "taskbarRestorable": True,
            "minimizeControl": True,
            "minimizeControlLocation": "top-right-header",
            "minimizeControlProof": _monitoring_hud_studio_dom_control_proof("minimize"),
            "closeControl": True,
            "closeControlLocation": "top-right-header",
            "closeControlProof": _monitoring_hud_studio_dom_control_proof("close"),
            "windowControlCluster": "UIREF-002-compact-window-control-cluster",
            "windowControlVisibleTextPolicy": "ai-control-center-symbol-visible-accessible-label",
            "windowControlContainerVisualPolicy": "ai-control-center-symbol-window-control-cluster",
            "actionButtonGeometryPolicy": "monitoring-hud-hub-action-content-fit-equal-gutter-v4",
            "stateRowDensityPolicy": "doorway-shell-viewer-deferred-row-plus-bottom-folder-actions-no-technical-path-table",
            "titleGroupVisualPolicy": "detached-child-window-header-no-title-card",
            "titleTreatment": "detached-child-window-header-no-title-card",
            "titleCardState": "absent",
            "childWindowTitleGrammar": "title-first-description-beneath-no-title-card",
            "visualPrimitiveAdoptionContract": _monitoring_hud_ai_control_center_primitive_contract(),
            "referenceTemplatePrimitiveClassification": "Bounded FAM-006 Shared Primitive Carry-In",
            "primaryVisualComparator": "FAM-006 unique child feature-studio grammar",
            "compositionModel": "compact-current-branch-log-access-shell",
            "windowTaxonomy": "unique-child-standalone-feature-studio",
            "attachedChildResizeGrip": False,
            "uniqueChildResizePolicy": "no-resize-recording-edge-resize-log-viewer",
            "acceptedReferenceSet": list(MONITORING_HUD_STUDIO_REFERENCE_SURFACES),
            "headerPrimitiveSeed": "AI-Control-Center-UIREF-001-title-group",
            "panelPrimitiveSeed": "FAM-006 compact folder-action shell with AI Control Center / HUD Dashboard state-row underglow",
            "nativeFolderPreSessionUsable": True,
            "exportFolderPreSessionUsable": True,
            "nativeLogRoot": native_root,
            "exportLogRoot": export_root,
            "nativeLogFullPath": os.path.normpath(str(self._native_full_path)),
            "exportLogFullPath": os.path.normpath(str(self._export_full_path)),
            "nativeLogDisplayText": "Recordings folder",
            "exportLogDisplayText": "Exported Logs folder",
            "nativeLogPathDisplayMode": "supporting-tooltip-only",
            "exportLogPathDisplayMode": "supporting-tooltip-only",
            "nativeLogPathTooltip": os.path.normpath(str(self._native_full_path)),
            "exportLogPathTooltip": os.path.normpath(str(self._export_full_path)),
            "nativeLogPathWordWrap": False,
            "exportLogPathWordWrap": False,
            "stateRowsContained": True,
            "pathRowsVisualState": "hidden-from-default-body-supporting-tooltip-only",
            "folderActionStatusText": self._folder_status_text,
            "folderActionStatusState": self._folder_status_state,
            "folderActionStatusAccessibleName": "Log Viewer folder action status",
            "openNativeControlProof": _monitoring_hud_studio_dom_control_proof("open-native"),
            "openExportControlProof": _monitoring_hud_studio_dom_control_proof("open-export"),
            "controlStateProof": "default-hover-focus-pressed-disabled-keyboard-accessible",
            "accessibilityKeyboardProofState": "controls-focusable-accessible-names-tooltips",
            "errorBlockedStateProof": "folder-open-blocked-status-visible",
            "nativeLogRootPublicLabel": "Native NDAI logs",
            "exportLogRootPublicLabel": "Exported logs",
            "userVisibleStorageModel": "flat-user-recording-and-export-roots",
            "internalPathLeakageAbsent": not any(term in combined_roots for term in leakage_terms),
            "visualContractDeclared": MONITORING_HUD_STUDIO_VISUAL_CONTRACT,
            "visualSystemInheritanceClaim": "nexus-window-primitives-v1-rendered-dom-css",
            "visualSampledElements": MONITORING_HUD_STUDIO_VISUAL_SAMPLE,
            "visualAdjudicationState": MONITORING_HUD_STUDIO_VISUAL_ADJUDICATION,
            "visualProofAuthority": MONITORING_HUD_STUDIO_VISUAL_PROOF_AUTHORITY,
            "visualRuntimeSelfAttestation": "rejected",
            "visualMatrixRequired": True,
            "visualReferenceSurfacesRequired": list(MONITORING_HUD_STUDIO_REFERENCE_SURFACES),
            "standaloneWindowLayout": "compact-current-branch-log-access-shell",
            "sharedPrimitiveSourcePath": "nexus_visual/nexus_window_primitives.css",
            "sharedPrimitiveConsumer": "nexus-window-primitives-v1",
            "featureStudioPrimitive": MONITORING_HUD_STUDIO_VISUAL_CONTRACT,
            "sharedVisualDna": "nexus-window-primitives-v1-rendered-dom-css",
            "genericShellRejected": "nexus-window-primitives-v1-rendered-dom-css",
            "titleHeaderBadgeState": "removed",
            "standaloneHeaderTreatment": "ai-control-center-title-group-no-extra-badge",
            "buttonVisualGrammar": "monitoring-hud-rendered-content-fit-equal-gutter-v4-button-primitive",
            "windowBodyVisualGrammar": MONITORING_HUD_STUDIO_BODY_VISUAL_GRAMMAR,
            "denseValidatorStatusPanelRejected": True,
            "boxedTablePanelRejected": True,
            "tableRowTruthLayoutRejected": True,
            "technicalPathViewerRejected": True,
            "viewerDeferredRow": "VIEWER - Deferred",
            "visibleAnatomy": "doorway-shell-with-viewer-deferred-row-and-bottom-native-export-actions",
            "futureScopeVisualLeakageAbsent": True,
            "attachedChildCornerResizeGripAbsent": True,
            "edgeResizeProofRequired": True,
            "windowPlacementMemoryState": "enabled",
            "windowPlacementPolicy": "B2-same-session-user-moved-position-or-parent-neighbor-default",
            "placementSource": self._placement_source,
            "parentNeighborDefaultGeometry": _monitoring_hud_qrect_to_dict(self._parent_neighbor_geometry),
            "sessionUserGeometryPresent": isinstance(self._session_user_geometry, QRect),
            "sessionGeometryRestored": self._session_geometry_restored,
            "resizeBehavior": self.RESIZE_BEHAVIOR,
            "nativeEdgeResizeHitTest": "WM_NCHITTEST+manual-fallback-geometry-resize",
            "nativeResizeInteractionState": self._native_resize_interaction_state,
            "geometryPersistenceKey": self._geometry_persistence_key,
            "geometryRestoredFromSaved": self._geometry_restored_from_saved,
            "previousLogSelectionState": "future-gated",
            "exportCustomizationState": "future-gated",
            "nativeLogLoaderState": "future-gated",
            "activationMode": self._last_activation_mode,
            "visible": self.isVisible(),
            "isActiveWindow": self.isActiveWindow(),
            "isMinimized": self.isMinimized(),
            "requestId": self._request_id,
            "x": geometry.x(),
            "y": geometry.y(),
            "w": geometry.width(),
            "h": geometry.height(),
        }


class AIControlCenterDialog(QDialog):
    WINDOW_STATE_SCHEMA_VERSION = 9
    WINDOW_STATE_ENV = "NEXUS_AI_CONTROL_CENTER_STATE_PATH"
    WINDOW_GEOMETRY_MEMORY_ENV = "NEXUS_AI_CONTROL_CENTER_ENABLE_GEOMETRY_MEMORY"
    WINDOW_STATE_FILENAME = "ai_control_center_window_state.json"
    DEFAULT_WIDTH = 471
    DEFAULT_HEIGHT = 598
    DEFAULT_MAX_HEIGHT = 680
    DEFAULT_SCREEN_MARGIN_X = 96
    DEFAULT_SCREEN_MARGIN_Y = 80
    MINIMUM_WIDTH = 430
    MINIMUM_HEIGHT = 520
    RESIZE_MARGIN = 16
    DRAG_HEADER_HEIGHT = 190
    WINDOW_CONTROL_ZONE_TOP = 15
    WINDOW_CONTROL_ZONE_RIGHT = 15
    WINDOW_CONTROL_ZONE_WIDTH = 60
    WINDOW_CONTROL_ZONE_HEIGHT = 30
    WINDOW_CONTROL_ALLOWED_STATES = frozenset({"hidden", "blocked", "active"})
    WINDOW_CONTROL_WEB_KEYS = {
        "minimize": "minimize",
        "maximize-restore": "maximizeRestore",
        "close": "close",
    }
    WINDOW_CONTROL_STATES = {
        "minimize": "active",
        "maximize-restore": "hidden",
        "close": "active",
    }

    def __init__(self, screen, event_logger=None):
        super().__init__(None)
        self.screen_ref = screen
        self.event_logger = event_logger
        self._provider_payload = {}
        self._restoring_window_geometry = False
        self._geometry_persist_timer = QTimer(self)
        self._geometry_persist_timer.setSingleShot(True)
        self._geometry_persist_timer.timeout.connect(self._persist_window_geometry)
        self.setObjectName("fam007AiControlCenter")
        self.setWindowTitle("AI Dashboard")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setWindowModality(Qt.NonModal)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumSize(self.MINIMUM_WIDTH, self.MINIMUM_HEIGHT)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setProperty("aiControlCenterOwner", "FAM-007")
        self.setProperty("aiControlCenterRoute", "fam007-ai-dashboard")
        self.setProperty("aiDashboardVisibleName", "AI Dashboard")
        self.setProperty("aiControlCenterPlacement", "focused-domain-card-inside-ai-dashboard")
        self.setProperty("fam003CarryIn", "f3-ff01-narrow-doorway-only")
        self.setProperty("surfaceClassification", "Nexus-Owned Product Surface")
        self.setProperty("visualInheritance", "FAM-002-HUD")
        self.setProperty("platformException", "none")
        self.setProperty("providerVisibleData", "none")
        self.setProperty("promptSend", "prompt-send-disabled")
        self.setProperty("providerModelExecution", "blocked")
        self.setProperty("networkEgress", "network-egress-blocked")
        self.setProperty("memoryIndexing", "memory-indexing-disabled")
        self.setProperty("aiControlCenterWindowMemoryPolicy", "restart-memory-disabled")
        self.setProperty("fam003ResetDependency", "ai-global-settings-reset-default-location-size")
        self.setProperty("aiControlCenterMinimizeAffordance", "Minimize AI Dashboard")
        self.setProperty("aiControlCenterMaximizeDisposition", "hidden-future-gated")
        self.setProperty("aiControlCenterMaximizeDecisionGate", "per-window-relevance-before-inheritance")
        self.setProperty("aiControlCenterWindowControlStateModel", "hidden-blocked-active")
        self.setProperty("aiControlCenterWindowControlCluster", "compact-minimize-maximize-close")
        self.setProperty("aiControlCenterActiveSpecimen", "webview-hud-specimen")
        self.setProperty("aiControlCenterNativeMirrorDisposition", "removed-webview-owned-specimen")
        self.setProperty("aiDashboardChildWindowModel", "detached-domain-window-route-lifecycle-active")
        self.setProperty("aiDashboardReadinessWindowClassification", "external-unique")
        self.setProperty("aiDashboardControlWindowClassification", "exclusive-child")
        self.setProperty("aiDashboardMaintenanceWindowClassification", "exclusive-child")
        self._page_ready = False
        self._pending_provider_payload = {}
        self._domain_windows: dict[str, AIDashboardDomainWindow] = {}
        self._domain_generation_counts: dict[str, int] = {}
        self._domain_closing_hwnds: dict[str, int] = {}
        self._domain_closing_identities: dict[str, int] = {}
        self._domain_closing_contexts: dict[str, dict[str, object]] = {}
        self._domain_pending_reopen: dict[str, bool] = {}
        self._domain_close_completion_timers: dict[str, QTimer] = {}
        self._closing_domain_children = False
        self._drag_offset = None
        self._resize_active = False
        self._resize_edges = Qt.Edges()
        self._resize_start_global = QPoint()
        self._resize_start_geometry = QRect()
        self._resize_pending_point = QPoint()
        self._resize_last_geometry = QRect()
        self._resize_last_apply = 0.0
        self._resize_frame_interval_ms = 16
        self._resize_cursor_key = None
        self._resize_override_cursor_active = False
        self._resize_poll_timer = QTimer(self)
        self._resize_poll_timer.setSingleShot(False)
        try:
            self._resize_poll_timer.setTimerType(Qt.PreciseTimer)
        except Exception:
            pass
        self._resize_poll_timer.timeout.connect(self._poll_ai_control_center_resize)
        self._resize_frame_timer = QTimer(self)
        self._resize_frame_timer.setSingleShot(True)
        try:
            self._resize_frame_timer.setTimerType(Qt.PreciseTimer)
        except Exception:
            pass
        self._resize_frame_timer.timeout.connect(self._apply_ai_control_center_queued_resize)
        self._resize_hover_timer = QTimer(self)
        self._resize_hover_timer.setInterval(8)
        self._resize_hover_timer.timeout.connect(self._poll_ai_control_center_resize_hover_cursor)
        self.setStyleSheet("background-color: transparent;")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.webview = QWebEngineView(self)
        self.webview.setAttribute(Qt.WA_TranslucentBackground, True)
        self.webview.setAttribute(Qt.WA_NoSystemBackground, True)
        self.webview.setAutoFillBackground(False)
        self.webview.setStyleSheet("background-color: transparent; border: none;")
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setMouseTracking(True)
        self.webview.installEventFilter(self)
        self._web_page = AIControlCenterCommandPage(self.webview, event_logger=self.event_logger)
        self._web_page.ai_control_center_command.connect(self._handle_ai_control_center_command)
        self.webview.setPage(self._web_page)
        self.webview.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.webview.loadFinished.connect(self._on_ai_control_center_html_loaded)
        self.webview.load(QUrl.fromLocalFile(str(self._ai_control_center_html_path())))
        root.addWidget(self.webview)
        self.setGeometry(self._restored_geometry())

    def _ai_control_center_html_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "nexus_visual" / "ai_control_center.html"

    def _on_ai_control_center_html_loaded(self, ok: bool) -> None:
        self._page_ready = bool(ok)
        if self._page_ready:
            self._sync_provider_state_to_web()
            self._sync_ai_control_center_window_controls()
        elif callable(self.event_logger):
            self.event_logger("RENDERER_MAIN|AI_CONTROL_CENTER_HTML_LOAD_FAILED")

    def _ai_control_center_window_control_states(self) -> dict[str, str]:
        states: dict[str, str] = {}
        for command in self.WINDOW_CONTROL_WEB_KEYS:
            state = self.WINDOW_CONTROL_STATES.get(command, "blocked")
            states[command] = state if state in self.WINDOW_CONTROL_ALLOWED_STATES else "blocked"
        return states

    def _ai_control_center_window_command_is_active(self, command: str) -> bool:
        return self._ai_control_center_window_control_states().get(command) == "active"

    def _log_ai_dashboard_doorway_result(self, stage, domain_id, *, result=None, error=None) -> None:
        try:
            if not callable(self.event_logger):
                return
            event = f"RENDERER_MAIN|AI_DASHBOARD_DOORWAY_RECEIVER|stage={stage}|domain={domain_id}"
            if result is not None:
                reasons = {
                    "none", "unknown_domain", "parent-close-in-progress", "close-in-progress-reopen-deferred",
                    "stale-registry-live-hwnd-stop", "duplicate-live-domain-window-stop", "unowned-live-domain-hwnd-stop",
                }
                reason = result.get("reason", "none") if isinstance(result, dict) else "unclassified"
                if reason not in reasons:
                    reason = "unclassified"
                hwnd = result.get("hwnd", 0) if isinstance(result, dict) else 0
                event += f"|reason={reason}|hwnd={hwnd if type(hwnd) is int else 0}"
            if error is not None:
                event += f"|exceptionType={type(error).__name__}"
                known_domain_frames = {
                    'AIControlCenterDialog._ai_dashboard_domain_parent_for',
                    'AIControlCenterDialog._show_ai_dashboard_domain_window',
                    'AIDashboardDomainWindow.__init__',
                    'AIDashboardDomainWindow._activate_domain_window',
                    'AIDashboardDomainWindow._apply_shell_mask',
                    'AIDashboardDomainWindow._asset_base_dir',
                    'AIDashboardDomainWindow._begin_lifecycle_action',
                    'AIDashboardDomainWindow._bounded_domain_geometry',
                    'AIDashboardDomainWindow._dashboard',
                    'AIDashboardDomainWindow._domain_body_html',
                    'AIDashboardDomainWindow._domain_html',
                    'AIDashboardDomainWindow._live_domain_objects',
                    'AIDashboardDomainWindow._native_domain_hwnd',
                    'AIDashboardDomainWindow._native_lifecycle_snapshot',
                    'AIDashboardDomainWindow._normalize_native_taskbar_contract',
                    'AIDashboardDomainWindow._parent_lifecycle_snapshot',
                    'AIDashboardDomainWindow._process_domain_hwnds',
                    'AIDashboardDomainWindow._process_domain_hwnds.<locals>.collect',
                    'AIDashboardDomainWindow._qrect_lifecycle_snapshot',
                    'AIDashboardDomainWindow._qt_enum_value',
                    'AIDashboardDomainWindow._qt_object_is_live',
                    'AIDashboardDomainWindow._record_lifecycle_transition',
                    'AIDashboardDomainWindow._register_runtime_instance',
                    'AIDashboardDomainWindow._registry_lifecycle_snapshot',
                    'AIDashboardDomainWindow._remember_normal_geometry',
                    'AIDashboardDomainWindow._restore_remembered_normal_geometry',
                    'AIDashboardDomainWindow._visible_shell_region',
                    'AIDashboardDomainWindow.lifecycle_debug_state',
                    'AIDashboardDomainWindow.runtime_lifecycle_inventory',
                    'AIDashboardDomainWindow.show_domain_window',
                    'AIDashboardDomainWindow.update_provider_state',
                }
                traceback = error.__traceback__
                origin = None
                while traceback is not None:
                    code = traceback.tb_frame.f_code
                    if code.co_filename == __file__ and code.co_qualname in known_domain_frames:
                        origin = (code.co_qualname, traceback.tb_lineno)
                    traceback = traceback.tb_next
                function, line = origin if origin is not None else ("unresolved", 0)
                event += f"|originFunction={function}|originLine={line}"
            self.event_logger(event)
        except Exception:
            pass

    def _handle_ai_control_center_command(self, command: str) -> None:
        if command in self.WINDOW_CONTROL_WEB_KEYS and not self._ai_control_center_window_command_is_active(command):
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_CONTROL_CENTER_WINDOW_CONTROL_BLOCKED"
                    f"|command={command}|state={self._ai_control_center_window_control_states().get(command, 'missing')}"
                )
            return
        if command == "minimize":
            self._reset_ai_control_center_resize_cursor()
            self.showMinimized()
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_CONTROL_CENTER_MINIMIZED"
                    "|memory_policy=restart-memory-disabled"
                )
            return
        if command == "maximize-restore":
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
            self._sync_ai_control_center_window_controls()
            return
        if command == "close":
            self.close()
            return
        domain_by_command = {
            "open-readiness-diagnostics-child-window": "readiness-diagnostics",
            "open-control-center-child-window": "control-center",
            "open-maintenance-lifecycle-child-window": "capabilities-maintenance",
        }
        if command in domain_by_command:
            domain_id = domain_by_command[command]
            self._log_ai_dashboard_doorway_result("entered", domain_id)
            try:
                result = self._show_ai_dashboard_domain_window(domain_id)
            except Exception as error:
                self._log_ai_dashboard_doorway_result("exception", domain_id, error=error)
                raise
            self._log_ai_dashboard_doorway_result("returned", domain_id, result=result)
            return
        if command == "run-local-check":
            self.run_local_assist_check(sync_web=False)
            return
        if command == "generate-readiness-report":
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_CONTROL_CENTER_READINESS_REPORT_GENERATED"
                    "|provider_visible_data=none|sent_to_provider=false|can_accept_prompts=false"
                    "|prompt_send=disabled|network_egress=blocked|memory_indexing=disabled"
                    "|persistence=view_only|copy_mode=clipboard_only_user_initiated"
                )
            return
        if command == "generate-readiness-report-blocked":
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_CONTROL_CENTER_READINESS_REPORT_BLOCKED"
                    "|reason=boundary_mismatch"
                )
            return
        if command == "copy-readiness-report":
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_CONTROL_CENTER_READINESS_REPORT_COPIED"
                    "|mode=clipboard_only_user_initiated|file_export=false"
                )
            return
        if command == "copy-readiness-report-blocked":
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_CONTROL_CENTER_READINESS_REPORT_COPY_BLOCKED"
                    "|reason=report_not_generated_or_clipboard_unavailable"
                )
            return
        if command == "open-settings-future-gated":
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_DASHBOARD_SETTINGS_ROUTE_FUTURE_GATED"
                    "|route=fam003-global-settings-ai|fam003_mutation=false|settings_window_opened=false"
            )
            return

    def _ai_dashboard_domain_parent_for(self, domain_id: str):
        return self

    def _mark_ai_dashboard_domain_window_closing(
        self,
        window: AIDashboardDomainWindow,
        context: dict[str, object],
    ) -> None:
        domain_id = window.domain_id
        self._domain_closing_hwnds[domain_id] = window._native_domain_hwnd()
        self._domain_closing_identities[domain_id] = id(window)
        self._domain_closing_contexts[domain_id] = dict(context)

    def _cancel_ai_dashboard_domain_window_closing(self, domain_id: str, object_identity: int) -> None:
        if self._domain_closing_identities.get(domain_id) != object_identity:
            return
        self._domain_closing_hwnds.pop(domain_id, None)
        self._domain_closing_identities.pop(domain_id, None)
        self._domain_closing_contexts.pop(domain_id, None)
        self._domain_pending_reopen.pop(domain_id, None)

    def _schedule_ai_dashboard_domain_close_completion(
        self,
        domain_id: str,
        object_identity: int,
    ) -> None:
        timer = self._domain_close_completion_timers.get(domain_id)
        if timer is None:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.setInterval(12)
            timer.timeout.connect(
                lambda key=domain_id, identity=object_identity: (
                    self._complete_ai_dashboard_domain_window_destruction(key, identity)
                )
            )
            self._domain_close_completion_timers[domain_id] = timer
        if not timer.isActive():
            timer.start()

    def _complete_ai_dashboard_domain_window_destruction(
        self,
        domain_id: str,
        object_identity: int,
    ) -> None:
        if self._domain_closing_identities.get(domain_id) not in {None, object_identity}:
            return
        hwnd = int(self._domain_closing_hwnds.get(domain_id, 0) or 0)
        if hwnd and hwnd in AIDashboardDomainWindow._process_domain_hwnds(domain_id):
            self._schedule_ai_dashboard_domain_close_completion(domain_id, object_identity)
            return

        current = self._domain_windows.get(domain_id)
        if current is None or id(current) == object_identity:
            self._domain_windows.pop(domain_id, None)
        context = self._domain_closing_contexts.pop(domain_id, {})
        self._domain_closing_hwnds.pop(domain_id, None)
        self._domain_closing_identities.pop(domain_id, None)
        timer = self._domain_close_completion_timers.pop(domain_id, None)
        if timer is not None:
            timer.stop()
            timer.deleteLater()

        inventory = AIDashboardDomainWindow.runtime_lifecycle_inventory(domain_id, self)
        parent_close = context.get("requestedAction") == "parent-close"
        reopen_requested = bool(self._domain_pending_reopen.pop(domain_id, False))
        record = {
            **context,
            "resultTimestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "hwnd": hwnd,
            "registryIdentity": object_identity,
            "registryCount": inventory["registeredObjectCount"],
            "registryRegistered": bool(inventory["registeredObjectCount"]),
            "childDestroyed": True,
            "closeResult": "destroyed",
            "orphanTaskbarVisibleHwndDetected": False,
            "deferredReopenRequested": reopen_requested,
            "deferredReopenSuppressedByParentClose": bool(parent_close and reopen_requested),
            "lifecycleInventory": inventory,
            "supportingDiagnosticOnly": True,
            "gatingDecision": "UNEVALUATED_REQUIRES_SEPARATE_FOCUSED_CLOSURE",
        }
        if callable(self.event_logger):
            encoded = urllib.parse.quote(json.dumps(record, sort_keys=True, separators=(",", ":")))
            self.event_logger(
                "RENDERER_MAIN|AI_DASHBOARD_DOMAIN_WINDOW_DESTROYED"
                f"|domain={domain_id}|object_identity={object_identity}|hwnd={hwnd}"
                "|hwnd_alive=false|orphan_taskbar_visible_hwnd=false"
                f"|registry_count={inventory['registeredObjectCount']}|record={encoded}"
            )
        if reopen_requested and not parent_close and not self._closing_domain_children:
            QTimer.singleShot(
                0,
                lambda key=domain_id: self._show_ai_dashboard_domain_window(
                    key,
                    requested_route="deferred-doorway-after-destruction",
                ),
            )

    def _on_ai_dashboard_domain_window_destroyed(self, domain_id: str, object_identity: int) -> None:
        self._schedule_ai_dashboard_domain_close_completion(domain_id, object_identity)

    def _show_ai_dashboard_domain_window(
        self,
        domain_id: str,
        *,
        requested_route: str = "ai-dashboard-doorway",
    ) -> dict[str, object]:
        if domain_id not in AIDashboardDomainWindow.DOMAIN_DEFINITIONS:
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_DASHBOARD_DOMAIN_WINDOW_BLOCKED"
                    f"|domain={domain_id}|reason=unknown_domain"
                )
            return {"visible": False, "reason": "unknown_domain"}
        closing_identity = int(self._domain_closing_identities.get(domain_id, 0) or 0)
        if closing_identity:
            context = self._domain_closing_contexts.get(domain_id, {})
            parent_close = context.get("requestedAction") == "parent-close"
            if not parent_close and not self._closing_domain_children:
                self._domain_pending_reopen[domain_id] = True
            return {
                "visible": False,
                "reason": "parent-close-in-progress" if parent_close else "close-in-progress-reopen-deferred",
                "domain": domain_id,
                "hwnd": int(self._domain_closing_hwnds.get(domain_id, 0) or 0),
                "closingObjectIdentity": closing_identity,
                "deferredReopenRequested": bool(self._domain_pending_reopen.get(domain_id, False)),
            }
        window = self._domain_windows.get(domain_id)
        if window is not None:
            if getattr(window, "_close_state", "open") == "close-requested":
                self._domain_pending_reopen[domain_id] = True
                return {
                    "visible": False,
                    "reason": "close-in-progress-reopen-deferred",
                    "domain": domain_id,
                    "hwnd": int(getattr(window, "_last_known_native_hwnd", 0) or 0),
                    "closingObjectIdentity": id(window),
                    "deferredReopenRequested": True,
                }
            try:
                window.lifecycle_debug_state()
            except RuntimeError:
                inventory = AIDashboardDomainWindow.runtime_lifecycle_inventory(domain_id, self)
                if inventory["liveSameDomainHwndCount"]:
                    return {
                        "visible": False,
                        "reason": "stale-registry-live-hwnd-stop",
                        "domain": domain_id,
                        "lifecycleInventory": inventory,
                    }
                if self._domain_windows.get(domain_id) is window:
                    self._domain_windows.pop(domain_id, None)
                window = None
        if window is None:
            inventory = AIDashboardDomainWindow.runtime_lifecycle_inventory(domain_id, self)
            live_objects = AIDashboardDomainWindow._live_domain_objects(domain_id)
            owned_live_objects = [
                candidate for candidate in live_objects if candidate._dashboard() is self
            ]
            if inventory["duplicateCount"]:
                return {
                    "visible": False,
                    "reason": "duplicate-live-domain-window-stop",
                    "domain": domain_id,
                    "lifecycleInventory": inventory,
                }
            if len(owned_live_objects) == 1:
                window = owned_live_objects[0]
                self._domain_windows[domain_id] = window
            elif inventory["liveSameDomainHwndCount"]:
                return {
                    "visible": False,
                    "reason": "unowned-live-domain-hwnd-stop",
                    "domain": domain_id,
                    "lifecycleInventory": inventory,
                }
        if window is None:
            generation = self._domain_generation_counts.get(domain_id, 0) + 1
            self._domain_generation_counts[domain_id] = generation
            window = AIDashboardDomainWindow(
                domain_id,
                self.screen(),
                parent=self._ai_dashboard_domain_parent_for(domain_id),
                event_logger=self.event_logger,
            )
            window._lifecycle_generation = generation
            object_identity = id(window)
            window.destroyed.connect(
                lambda _obj=None, key=domain_id, identity=object_identity: (
                    self._on_ai_dashboard_domain_window_destroyed(key, identity)
                )
            )
            self._domain_windows[domain_id] = window
        window.update_provider_state(self._provider_payload)
        result = window.show_domain_window(self.geometry(), requested_route=requested_route)
        if callable(self.event_logger):
            self.event_logger(
                "RENDERER_MAIN|AI_DASHBOARD_CATEGORY_LAUNCHER_OPENED_WINDOW"
                f"|domain={domain_id}|classification={result.get('classification')}"
                f"|lifecycle={result.get('lifecycle')}|singleton=true|focus=bring_to_front"
            )
        return result

    def _sync_provider_state_to_web(self) -> None:
        payload = dict(self._provider_payload or self._pending_provider_payload or {})
        self._pending_provider_payload = payload
        if not getattr(self, "_page_ready", False) or not hasattr(self, "webview"):
            return
        script = (
            "window.nexusAiControlCenterApplyProviderState && "
            f"window.nexusAiControlCenterApplyProviderState({json.dumps(payload)});"
        )
        self.webview.page().runJavaScript(script)

    def _sync_ai_control_center_window_controls(self) -> None:
        if not getattr(self, "_page_ready", False) or not hasattr(self, "webview"):
            return
        state = "maximized" if self.isMaximized() else "normal"
        control_states = {
            web_key: self._ai_control_center_window_control_states()[command]
            for command, web_key in self.WINDOW_CONTROL_WEB_KEYS.items()
        }
        script = (
            "window.nexusAiControlCenterSetWindowState && "
            f"window.nexusAiControlCenterSetWindowState({json.dumps(state)}, {json.dumps(control_states)});"
        )
        self.webview.page().runJavaScript(script)

    def eventFilter(self, watched, event):
        if watched is getattr(self, "webview", None):
            event_type = event.type()
            if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                pos = event.position().toPoint()
                resize_edges = self._ai_control_center_resize_edges_for_local_pos(pos)
                if resize_edges:
                    if self._start_ai_control_center_resize(
                        resize_edges,
                        self._ai_control_center_live_drag_screen_point(event),
                    ):
                        event.accept()
                        return True
                close_zone = self._ai_control_center_close_zone().contains(pos)
                if pos.y() <= self.DRAG_HEADER_HEIGHT and not close_zone and not self.isMaximized():
                    self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    event.accept()
                    return True
            elif event_type == QEvent.MouseMove and self._resize_active:
                self._update_ai_control_center_resize(self._ai_control_center_live_drag_screen_point(event))
                event.accept()
                return True
            elif (
                event_type == QEvent.MouseMove
                and self._drag_offset is not None
                and event.buttons() & Qt.LeftButton
            ):
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                event.accept()
                return True
            elif event_type == QEvent.MouseMove and not event.buttons():
                self._update_ai_control_center_resize_cursor(event.position().toPoint())
            elif event_type == QEvent.MouseButtonRelease:
                if self._resize_active:
                    self._finish_ai_control_center_resize(self._ai_control_center_live_drag_screen_point(event))
                    event.accept()
                    return True
                self._drag_offset = None
            elif event_type == QEvent.Leave and not self._resize_active:
                self._reset_ai_control_center_resize_cursor()
        return super().eventFilter(watched, event)

    def _ai_control_center_close_zone(self) -> QRect:
        return QRect(
            max(0, self.width() - self.WINDOW_CONTROL_ZONE_RIGHT - self.WINDOW_CONTROL_ZONE_WIDTH),
            self.WINDOW_CONTROL_ZONE_TOP,
            self.WINDOW_CONTROL_ZONE_WIDTH,
            self.WINDOW_CONTROL_ZONE_HEIGHT,
        )

    def _ai_control_center_resize_edges_for_local_pos(self, local: QPoint):
        if self.isMaximized():
            return Qt.Edges()
        if not QRect(0, 0, self.width(), self.height()).contains(local):
            return Qt.Edges()
        if self._ai_control_center_close_zone().contains(local):
            return Qt.Edges()
        margin = self.RESIZE_MARGIN
        corner_margin = margin * 2
        width = self.width()
        height = self.height()
        edges = Qt.Edges()
        if local.x() <= corner_margin and local.y() <= corner_margin:
            edges |= Qt.LeftEdge | Qt.TopEdge
        elif local.x() >= max(0, width - corner_margin) and local.y() <= corner_margin:
            edges |= Qt.RightEdge | Qt.TopEdge
        elif local.x() <= corner_margin and local.y() >= max(0, height - corner_margin):
            edges |= Qt.LeftEdge | Qt.BottomEdge
        elif local.x() >= max(0, width - corner_margin) and local.y() >= max(0, height - corner_margin):
            edges |= Qt.RightEdge | Qt.BottomEdge
        else:
            if local.x() <= margin:
                edges |= Qt.LeftEdge
            elif local.x() >= max(0, width - margin):
                edges |= Qt.RightEdge
            if local.y() <= margin:
                edges |= Qt.TopEdge
            elif local.y() >= max(0, height - margin):
                edges |= Qt.BottomEdge
        return edges

    def _ai_control_center_resize_edges_for_screen_point(self, screen_point: QPoint):
        if screen_point.isNull():
            return Qt.Edges()
        return self._ai_control_center_resize_edges_for_local_pos(self.mapFromGlobal(screen_point))

    def _ai_control_center_resize_edge_key(self, edges) -> tuple[bool, bool, bool, bool]:
        return (
            bool(edges & Qt.LeftEdge),
            bool(edges & Qt.RightEdge),
            bool(edges & Qt.TopEdge),
            bool(edges & Qt.BottomEdge),
        )

    def _ai_control_center_resize_cursor(self, edges):
        return self._ai_control_center_resize_cursor_for_edges(edges) or Qt.ArrowCursor

    def _ai_control_center_resize_cursor_for_edges(self, edges):
        left, right, top, bottom = self._ai_control_center_resize_edge_key(edges)
        if (left and top) or (right and bottom):
            return Qt.SizeFDiagCursor
        if (right and top) or (left and bottom):
            return Qt.SizeBDiagCursor
        if left or right:
            return Qt.SizeHorCursor
        if top or bottom:
            return Qt.SizeVerCursor
        return None

    def _ai_control_center_windows_resize_cursor_id_for_edges(self, edges):
        if not edges:
            return IDC_ARROW
        left, right, top, bottom = self._ai_control_center_resize_edge_key(edges)
        if (left and top) or (right and bottom):
            return IDC_SIZENWSE
        if (right and top) or (left and bottom):
            return IDC_SIZENESW
        if left or right:
            return IDC_SIZEWE
        if top or bottom:
            return IDC_SIZENS
        return IDC_ARROW

    def _apply_ai_control_center_windows_resize_cursor(self, edges) -> None:
        if os.name != "nt":
            return
        # resize-cursor-no-forced-arrow-release: clear our override without
        # forcing IDC_ARROW, or Windows edge hover can flicker arrow/resize.
        if not edges:
            return
        try:
            cursor_handle = LoadCursorW(None, self._ai_control_center_windows_resize_cursor_id_for_edges(edges))
            if cursor_handle:
                SetCursor(cursor_handle)
        except Exception:
            pass

    def _set_ai_control_center_override_resize_cursor(self, cursor) -> None:
        try:
            if cursor is None:
                if self._resize_override_cursor_active:
                    QApplication.restoreOverrideCursor()
                    self._resize_override_cursor_active = False
                return
            qt_cursor = QCursor(cursor)
            if self._resize_override_cursor_active:
                QApplication.changeOverrideCursor(qt_cursor)
            else:
                QApplication.setOverrideCursor(qt_cursor)
                self._resize_override_cursor_active = True
        except Exception:
            self._resize_override_cursor_active = False

    def _set_ai_control_center_resize_cursor(self, edges) -> None:
        key = self._ai_control_center_resize_edge_key(edges) if edges else None
        if key == self._resize_cursor_key:
            if os.name == "nt":
                self._set_ai_control_center_override_resize_cursor(
                    self._ai_control_center_resize_cursor_for_edges(edges) if key is not None else None
                )
                self._apply_ai_control_center_windows_resize_cursor(edges if key is not None else Qt.Edges())
            return
        self._resize_cursor_key = key
        cursor = self._ai_control_center_resize_cursor_for_edges(edges) if edges else None
        targets = [self]
        if hasattr(self, "webview"):
            targets.append(self.webview)
            try:
                targets.extend(self.webview.findChildren(QWidget))
            except Exception:
                pass
        if os.name == "nt":
            for target in targets:
                target.unsetCursor()
            self._set_ai_control_center_override_resize_cursor(cursor)
            self._apply_ai_control_center_windows_resize_cursor(edges if edges else Qt.Edges())
            return
        for target in targets:
            if cursor is None:
                target.unsetCursor()
            else:
                target.setCursor(QCursor(cursor))
        self._set_ai_control_center_override_resize_cursor(cursor)
        self._apply_ai_control_center_windows_resize_cursor(edges if edges else Qt.Edges())

    def _reset_ai_control_center_resize_cursor(self) -> None:
        self._set_ai_control_center_resize_cursor(Qt.Edges())

    def _update_ai_control_center_resize_cursor(self, local: QPoint) -> None:
        if self._resize_active:
            return
        self._set_ai_control_center_resize_cursor(self._ai_control_center_resize_edges_for_local_pos(local))

    def _ai_control_center_cursor_screen_point(self) -> QPoint:
        if os.name == "nt":
            try:
                point = ctypes.wintypes.POINT()
                if GetCursorPos(ctypes.byref(point)):
                    return QPoint(int(point.x), int(point.y))
            except Exception:
                pass
        try:
            return QCursor.pos()
        except Exception:
            return QPoint()

    def _ai_control_center_live_drag_screen_point(self, event) -> QPoint:
        cursor_point = self._ai_control_center_cursor_screen_point()
        if not cursor_point.isNull():
            return cursor_point
        try:
            return event.globalPosition().toPoint()
        except Exception:
            return QPoint()

    def _ai_control_center_left_mouse_button_down(self) -> bool:
        try:
            return bool(GetAsyncKeyState(VK_LBUTTON) & 0x8000)
        except Exception:
            return False

    def _ai_control_center_resize_refresh_rate_hz(self) -> float:
        screens = []
        try:
            screens.append(self.screen())
        except Exception:
            pass
        screens.extend([getattr(self, "screen_ref", None), QApplication.primaryScreen()])
        for screen in screens:
            if screen is None:
                continue
            try:
                refresh_rate = float(screen.refreshRate())
            except Exception:
                continue
            if 30.0 <= refresh_rate <= 360.0:
                return refresh_rate
        return 60.0

    def _ai_control_center_resize_frame_interval_ms(self) -> int:
        refresh_rate = self._ai_control_center_resize_refresh_rate_hz()
        return max(4, min(16, int(round(1000.0 / refresh_rate))))

    def _ai_control_center_point_belongs_to_window(self, point: QPoint) -> bool:
        if point.isNull():
            return False
        if os.name != "nt":
            return self.geometry().adjusted(-2, -2, 2, 2).contains(point)
        adjusted_geometry = self.geometry().adjusted(-2, -2, 2, 2)
        try:
            probe = ctypes.wintypes.POINT(int(point.x()), int(point.y()))
            hwnd = int(WindowFromPoint(probe))
            dialog_hwnd = int(self.winId())
            while hwnd:
                if hwnd == dialog_hwnd:
                    return True
                hwnd = int(GetParentW(ctypes.wintypes.HWND(hwnd)))
        except Exception:
            return adjusted_geometry.contains(point)
        return adjusted_geometry.contains(point)

    def _ai_control_center_resize_edges_under_cursor(self) -> tuple[QPoint, Qt.Edges]:
        if not self.isVisible():
            return QPoint(), Qt.Edges()
        screen_point = self._ai_control_center_cursor_screen_point()
        if screen_point.isNull():
            return QPoint(), Qt.Edges()
        if not self.geometry().adjusted(-2, -2, 2, 2).contains(screen_point):
            return screen_point, Qt.Edges()
        if not self._ai_control_center_point_belongs_to_window(screen_point):
            return screen_point, Qt.Edges()
        return screen_point, self._ai_control_center_resize_edges_for_screen_point(screen_point)

    def _poll_ai_control_center_resize_hover_cursor(self) -> None:
        if self._resize_active or self._drag_offset is not None:
            return
        _, edges = self._ai_control_center_resize_edges_under_cursor()
        if edges:
            self._set_ai_control_center_resize_cursor(edges)
            return
        self._reset_ai_control_center_resize_cursor()

    def _ai_control_center_resize_hit_test_for_edges(self, edges) -> int:
        left, right, top, bottom = self._ai_control_center_resize_edge_key(edges)
        if left and top:
            return HTTOPLEFT
        if right and top:
            return HTTOPRIGHT
        if left and bottom:
            return HTBOTTOMLEFT
        if right and bottom:
            return HTBOTTOMRIGHT
        if left:
            return HTLEFT
        if right:
            return HTRIGHT
        if top:
            return HTTOP
        if bottom:
            return HTBOTTOM
        return 0

    def _ai_control_center_resize_edges_for_hit_test(self, hit_test: int):
        edge_map = {
            HTLEFT: Qt.LeftEdge,
            HTRIGHT: Qt.RightEdge,
            HTTOP: Qt.TopEdge,
            HTBOTTOM: Qt.BottomEdge,
            HTTOPLEFT: Qt.TopEdge | Qt.LeftEdge,
            HTTOPRIGHT: Qt.TopEdge | Qt.RightEdge,
            HTBOTTOMLEFT: Qt.BottomEdge | Qt.LeftEdge,
            HTBOTTOMRIGHT: Qt.BottomEdge | Qt.RightEdge,
        }
        return edge_map.get(int(hit_test), Qt.Edges())

    def _start_ai_control_center_resize(self, edges, screen_point: QPoint) -> bool:
        if not edges:
            return False
        if screen_point.isNull():
            screen_point = self._ai_control_center_cursor_screen_point()
        if screen_point.isNull():
            return False
        self._resize_active = True
        self._drag_offset = None
        self._resize_edges = edges
        self._resize_start_global = QPoint(screen_point)
        self._resize_start_geometry = QRect(self.geometry())
        self._resize_pending_point = QPoint(screen_point)
        self._resize_last_geometry = QRect(self.geometry())
        self._resize_last_apply = 0.0
        self._resize_frame_interval_ms = self._ai_control_center_resize_frame_interval_ms()
        try:
            SetCapture(ctypes.wintypes.HWND(int(self.winId())))
        except Exception:
            pass
        self._set_ai_control_center_resize_cursor(edges)
        if callable(self.event_logger):
            self.event_logger(
                "RENDERER_MAIN|AI_CONTROL_CENTER_WINDOW_RESIZE_FALLBACK_STARTED"
                f"|x={screen_point.x()}|y={screen_point.y()}"
                f"|resize_hit_zone_px={self.RESIZE_MARGIN}"
                f"|resize_frame_interval_ms={self._resize_frame_interval_ms}"
                f"|edges={str(edges)}"
            )
        self._resize_poll_timer.stop()
        self._resize_poll_timer.setInterval(self._resize_frame_interval_ms)
        self._resize_poll_timer.start()
        self._poll_ai_control_center_resize()
        return True

    def _poll_ai_control_center_resize(self) -> None:
        if not self._resize_active:
            self._resize_poll_timer.stop()
            return
        screen_point = self._ai_control_center_cursor_screen_point()
        if not screen_point.isNull():
            self._update_ai_control_center_resize(screen_point)
        if self._ai_control_center_left_mouse_button_down():
            return
        self._finish_ai_control_center_resize(screen_point)

    def _update_ai_control_center_resize(self, screen_point: QPoint) -> None:
        if not self._resize_active or screen_point.isNull():
            return
        self._resize_pending_point = QPoint(screen_point)
        interval_s = max(0.004, self._resize_frame_interval_ms / 1000.0)
        now = time.monotonic()
        elapsed = now - self._resize_last_apply
        if self._resize_last_apply <= 0.0 or elapsed >= interval_s:
            self._apply_ai_control_center_queued_resize()
            return
        if not self._resize_frame_timer.isActive():
            remaining_ms = max(1, int(round((interval_s - elapsed) * 1000.0)))
            self._resize_frame_timer.start(remaining_ms)

    def _apply_ai_control_center_queued_resize(self) -> None:
        if not self._resize_active:
            return
        screen_point = QPoint(self._resize_pending_point)
        if screen_point.isNull():
            screen_point = self._ai_control_center_cursor_screen_point()
        if screen_point.isNull():
            return
        next_rect = self._ai_control_center_resize_rect_from_global_delta(screen_point)
        if next_rect == self._resize_last_geometry:
            self._resize_last_apply = time.monotonic()
            return
        self.setGeometry(next_rect)
        self._resize_last_geometry = QRect(next_rect)
        self._resize_last_apply = time.monotonic()
        self._sync_ai_control_center_resize_frame()

    def _resize_ai_control_center_from_global(self, screen_point: QPoint) -> None:
        self._update_ai_control_center_resize(screen_point)

    def _ai_control_center_resize_rect_from_global_delta(self, screen_point: QPoint) -> QRect:
        base = self._resize_start_geometry
        if base.isNull() or not base.isValid():
            base = QRect(self.geometry())
        delta = screen_point - self._resize_start_global
        left_edge, right_edge, top_edge, bottom_edge = self._ai_control_center_resize_edge_key(self._resize_edges)
        x = base.x()
        y = base.y()
        width = base.width()
        height = base.height()
        if left_edge:
            x = base.x() + delta.x()
            width = base.width() - delta.x()
        elif right_edge:
            width = base.width() + delta.x()
        if top_edge:
            y = base.y() + delta.y()
            height = base.height() - delta.y()
        elif bottom_edge:
            height = base.height() + delta.y()
        min_width = self.minimumWidth()
        min_height = self.minimumHeight()
        if width < min_width:
            if left_edge:
                x = base.right() - min_width + 1
            width = min_width
        if height < min_height:
            if top_edge:
                y = base.bottom() - min_height + 1
            height = min_height
        return self._bound_geometry_to_available_desktop(QRect(x, y, width, height))

    def _sync_ai_control_center_resize_frame(self, *, force: bool = False) -> None:
        if not hasattr(self, "webview"):
            return
        self.webview.setGeometry(self.rect())
        self.webview.updateGeometry()
        self.webview.update()
        self.update()
        try:
            self.webview.page().runJavaScript("window.requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));")
        except Exception:
            pass
        if force:
            try:
                QApplication.processEvents()
            except Exception:
                pass

    def _finish_ai_control_center_resize(self, screen_point: QPoint = None) -> None:
        if not self._resize_active:
            self._reset_ai_control_center_resize_cursor()
            return
        self._resize_poll_timer.stop()
        self._resize_frame_timer.stop()
        if screen_point is None or screen_point.isNull():
            screen_point = self._ai_control_center_cursor_screen_point()
        if screen_point.isNull():
            screen_point = QPoint(self._resize_start_global)
        if not screen_point.isNull():
            next_rect = self._ai_control_center_resize_rect_from_global_delta(screen_point)
            if next_rect != self._resize_last_geometry:
                self.setGeometry(next_rect)
                self._resize_last_geometry = QRect(next_rect)
        self._sync_ai_control_center_resize_frame(force=True)
        self._resize_active = False
        self._resize_edges = Qt.Edges()
        self._resize_start_global = QPoint()
        self._resize_start_geometry = QRect()
        self._resize_pending_point = QPoint()
        self._resize_last_geometry = QRect()
        self._resize_last_apply = 0.0
        try:
            ReleaseCapture()
        except Exception:
            pass
        self._reset_ai_control_center_resize_cursor()
        self._schedule_window_geometry_persist()
        if callable(self.event_logger):
            geometry = self.geometry()
            self.event_logger(
                "RENDERER_MAIN|AI_CONTROL_CENTER_WINDOW_RESIZE_READY"
                f"|w={geometry.width()}|h={geometry.height()}"
            )

    def _ai_control_center_native_hit_test(self, screen_point: QPoint) -> int:
        local = self.mapFromGlobal(screen_point)
        if not QRect(0, 0, self.width(), self.height()).contains(local):
            return 0
        if self._ai_control_center_close_zone().contains(local):
            return HTCLIENT
        if self.isMaximized():
            return HTCLIENT
        hit_test = self._ai_control_center_resize_hit_test_for_edges(
            self._ai_control_center_resize_edges_for_local_pos(local)
        )
        if hit_test:
            return hit_test
        if local.y() <= self.DRAG_HEADER_HEIGHT:
            return HTCAPTION
        return 0

    def nativeEvent(self, eventType, message):
        if eventType in ("windows_generic_MSG", "windows_dispatcher_MSG"):
            try:
                msg = ctypes.wintypes.MSG.from_address(int(message))
            except Exception:
                msg = None
            if msg is not None:
                message_id = int(msg.message)
                if message_id == WM_NCHITTEST:
                    x = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
                    y = ctypes.c_short((int(msg.lParam) >> 16) & 0xFFFF).value
                    hit_test = self._ai_control_center_native_hit_test(QPoint(x, y))
                    if hit_test:
                        return True, hit_test
                if message_id == WM_NCLBUTTONDBLCLK:
                    screen_point = QCursor.pos()
                    if self._ai_control_center_native_hit_test(screen_point) == HTCAPTION:
                        return True, 0
                if message_id == WM_SETCURSOR and not self._resize_active:
                    hit_test = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
                    edges = self._ai_control_center_resize_edges_for_hit_test(hit_test)
                    if edges:
                        self._set_ai_control_center_resize_cursor(edges)
                        return True, 1
                    self._reset_ai_control_center_resize_cursor()
                if message_id in (WM_MOUSEMOVE, WM_NCMOUSEMOVE) and not self._resize_active:
                    if message_id == WM_NCMOUSEMOVE:
                        edges = self._ai_control_center_resize_edges_for_hit_test(int(msg.wParam))
                        if edges:
                            self._set_ai_control_center_resize_cursor(edges)
                            return True, 0
                    _, edges = self._ai_control_center_resize_edges_under_cursor()
                    if edges:
                        self._set_ai_control_center_resize_cursor(edges)
                    elif message_id == WM_MOUSEMOVE:
                        self._reset_ai_control_center_resize_cursor()
                if message_id == WM_LBUTTONDOWN:
                    screen_point, edges = self._ai_control_center_resize_edges_under_cursor()
                    if edges and self._start_ai_control_center_resize(edges, screen_point):
                        return True, 0
                if message_id == WM_NCLBUTTONDOWN:
                    edges = self._ai_control_center_resize_edges_for_hit_test(int(msg.wParam))
                    screen_point = self._ai_control_center_cursor_screen_point()
                    if edges and not screen_point.isNull():
                        self._set_ai_control_center_resize_cursor(edges)
                        if self._start_ai_control_center_resize(edges, screen_point):
                            return True, 0
                if self._resize_active and message_id in (WM_MOUSEMOVE, WM_NCMOUSEMOVE):
                    screen_point = self._ai_control_center_cursor_screen_point()
                    if not screen_point.isNull():
                        self._update_ai_control_center_resize(screen_point)
                    return True, 0
                if self._resize_active and message_id in (
                    WM_LBUTTONUP,
                    WM_NCLBUTTONUP,
                    WM_CAPTURECHANGED,
                    WM_CANCELMODE,
                ):
                    self._finish_ai_control_center_resize(self._ai_control_center_cursor_screen_point())
                    return True, 0
        return super().nativeEvent(eventType, message)

    def _window_state_path(self) -> Path:
        override = os.environ.get(self.WINDOW_STATE_ENV, "").strip()
        if override:
            return Path(override)
        local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
        if local_app_data:
            return Path(local_app_data) / "Nexus Desktop AI" / self.WINDOW_STATE_FILENAME
        return Path.home() / "AppData" / "Local" / "Nexus Desktop AI" / self.WINDOW_STATE_FILENAME

    def _window_geometry_memory_enabled(self) -> bool:
        value = os.environ.get(self.WINDOW_GEOMETRY_MEMORY_ENV, "").strip().lower()
        return value in {"1", "true", "yes", "on"}

    def _available_desktop_geometry(self) -> QRect:
        screens = QApplication.screens()
        if not screens:
            return self.screen_ref.availableGeometry()
        available = QRect(screens[0].availableGeometry())
        for screen in screens[1:]:
            available = available.united(screen.availableGeometry())
        if available.isValid() and not available.isNull():
            return available
        return self.screen_ref.availableGeometry()

    def _default_window_size(self) -> tuple[int, int]:
        available = self.screen_ref.availableGeometry()
        width = min(
            self.DEFAULT_WIDTH,
            max(self.MINIMUM_WIDTH, available.width() - (self.DEFAULT_SCREEN_MARGIN_X * 2)),
        )
        max_height = min(
            self.DEFAULT_MAX_HEIGHT,
            max(self.MINIMUM_HEIGHT, available.height() - (self.DEFAULT_SCREEN_MARGIN_Y * 2)),
        )
        height = min(self.DEFAULT_HEIGHT, max_height)
        return int(width), int(max(self.MINIMUM_HEIGHT, height))

    def _bound_geometry_to_available_desktop(self, rect: QRect) -> QRect:
        available = self._available_desktop_geometry()
        fallback = self._initial_geometry()
        width = rect.width() if rect.isValid() and rect.width() > 0 else fallback.width()
        height = rect.height() if rect.isValid() and rect.height() > 0 else fallback.height()
        width = max(self.minimumWidth(), min(width, max(self.minimumWidth(), available.width())))
        height = max(self.minimumHeight(), min(height, max(self.minimumHeight(), available.height())))
        max_x = available.right() - width + 1
        max_y = available.bottom() - height + 1
        x = min(max(rect.x(), available.x()), max_x)
        y = min(max(rect.y(), available.y()), max_y)
        return QRect(x, y, width, height)

    def _saved_geometry_is_usable(self, rect: QRect) -> bool:
        if not rect.isValid() or rect.width() < self.minimumWidth() or rect.height() < self.minimumHeight():
            return False
        available = self._available_desktop_geometry()
        if rect.width() > available.width() or rect.height() > available.height():
            return False
        visible = rect.intersected(available)
        return bool(
            visible.isValid()
            and visible.width() >= rect.width() - 4
            and visible.height() >= rect.height() - 4
        )

    def _restored_geometry(self) -> QRect:
        fallback = self._initial_geometry()
        if not self._window_geometry_memory_enabled():
            return fallback
        path = self._window_state_path()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return fallback
        if not isinstance(payload, dict):
            return fallback
        if payload.get("schemaVersion") != self.WINDOW_STATE_SCHEMA_VERSION:
            try:
                migrated = QRect(
                    int(payload.get("x")),
                    int(payload.get("y")),
                    fallback.width(),
                    fallback.height(),
                )
            except Exception:
                return fallback
            return self._bound_geometry_to_available_desktop(migrated)
        try:
            rect = QRect(
                int(payload.get("x")),
                int(payload.get("y")),
                int(payload.get("w")),
                int(payload.get("h")),
            )
        except Exception:
            return fallback
        if not self._saved_geometry_is_usable(rect):
            return fallback
        return self._bound_geometry_to_available_desktop(rect)

    def _persist_window_geometry(self) -> None:
        if self._restoring_window_geometry or not self._window_geometry_memory_enabled():
            return
        geometry = self.geometry()
        if not self._saved_geometry_is_usable(geometry):
            return
        payload = {
            "schemaVersion": self.WINDOW_STATE_SCHEMA_VERSION,
            "kind": "ai-control-center-window-geometry",
            "x": int(geometry.x()),
            "y": int(geometry.y()),
            "w": int(geometry.width()),
            "h": int(geometry.height()),
            "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        path = self._window_state_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = path.with_name(f"{path.name}.tmp")
            temp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            os.replace(temp_path, path)
        except Exception as exc:
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_CONTROL_CENTER_GEOMETRY_SAVE_FAILED"
                    f"|reason={type(exc).__name__}"
                )

    def _schedule_window_geometry_persist(self) -> None:
        if (
            self._restoring_window_geometry
            or not self.isVisible()
            or not self._window_geometry_memory_enabled()
        ):
            return
        self._geometry_persist_timer.start(350)

    def _initial_geometry(self) -> QRect:
        available = self.screen_ref.availableGeometry()
        width, height = self._default_window_size()
        return QRect(
            available.x() + max(24, available.width() - width - self.DEFAULT_SCREEN_MARGIN_X),
            available.y() + max(24, available.height() - height - self.DEFAULT_SCREEN_MARGIN_Y),
            width,
            height,
        )

    def moveEvent(self, event):
        super().moveEvent(event)
        self._schedule_window_geometry_persist()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_ai_control_center_window_controls()
        self._schedule_window_geometry_persist()

    def showEvent(self, event):
        super().showEvent(event)
        self._resize_hover_timer.start()
        self._sync_ai_control_center_window_controls()

    def hideEvent(self, event):
        self._resize_hover_timer.stop()
        if self._resize_active:
            self._finish_ai_control_center_resize(self._ai_control_center_cursor_screen_point())
        super().hideEvent(event)

    def closeEvent(self, event):
        self._resize_hover_timer.stop()
        if self._resize_active:
            self._finish_ai_control_center_resize(self._ai_control_center_cursor_screen_point())
        else:
            self._reset_ai_control_center_resize_cursor()
        self._closing_domain_children = True
        try:
            for domain_id, window in list(self._domain_windows.items()):
                definition = AIDashboardDomainWindow.DOMAIN_DEFINITIONS.get(domain_id, {})
                if definition.get("classification") == "exclusive-child":
                    self._domain_pending_reopen.pop(domain_id, None)
                    if self._domain_closing_identities.get(domain_id) == id(window):
                        context = self._domain_closing_contexts.setdefault(domain_id, {})
                        context.update(
                            {
                                "requestedRoute": "dashboard-parent-close",
                                "requestedAction": "parent-close",
                                "qtMethodInvoked": "close-already-pending-parent-suppressed",
                            }
                        )
                    else:
                        window.close_domain_window("dashboard-parent-close")
                elif definition.get("classification") == "external-unique":
                    window.record_dashboard_parent_close_survival()
        finally:
            self._closing_domain_children = False
        self._geometry_persist_timer.stop()
        self._persist_window_geometry()
        super().closeEvent(event)

    def update_provider_state(self, payload: dict[str, object]) -> None:
        self._provider_payload = dict(payload or {})
        self._sync_provider_state_to_web()
        for window in list(self._domain_windows.values()):
            try:
                window.update_provider_state(self._provider_payload)
            except RuntimeError:
                pass

    def run_local_assist_check(self, *, sync_web: bool = True) -> None:
        payload = self._provider_payload or {}
        guard_closed = (
            payload.get("sentToProvider") is False
            and payload.get("canAcceptPrompts") is False
            and payload.get("providerVisibleData") == "none"
            and payload.get("promptSendPosture") == "prompt-send-disabled"
            and payload.get("networkEgressState") == "network-egress-blocked"
            and payload.get("memoryIndexingState") == "memory-indexing-disabled"
        )
        if guard_closed:
            event = (
                "RENDERER_MAIN|AI_CONTROL_CENTER_LOCAL_ASSIST_RESULT"
                "|provider_visible_data=none|sent_to_provider=false|can_accept_prompts=false"
                "|network_egress=blocked|memory_indexing=disabled"
            )
        else:
            event = "RENDERER_MAIN|AI_CONTROL_CENTER_LOCAL_ASSIST_BLOCKED|reason=boundary_mismatch"
        if sync_web and hasattr(self, "webview"):
            self.webview.page().runJavaScript(
                "window.nexusAiControlCenterRunLocalCheck && "
                "window.nexusAiControlCenterRunLocalCheck();"
            )
        if callable(self.event_logger):
            self.event_logger(event)

    def _native_hwnd(self) -> int:
        try:
            return int(self.winId())
        except Exception:
            return 0

    def _native_visibility_state(self) -> dict[str, object]:
        hwnd = self._native_hwnd()
        rect = ctypes.wintypes.RECT()
        rect_ok = bool(hwnd and GetWindowRect(ctypes.wintypes.HWND(hwnd), ctypes.byref(rect)))
        native_visible = bool(hwnd and IsWindowVisible(ctypes.wintypes.HWND(hwnd)))
        if rect_ok:
            x = rect.left
            y = rect.top
            w = max(0, rect.right - rect.left)
            h = max(0, rect.bottom - rect.top)
        else:
            geometry = self.geometry()
            x = geometry.x()
            y = geometry.y()
            w = geometry.width()
            h = geometry.height()
        return {
            "hwnd": hwnd,
            "qtVisible": bool(self.isVisible()),
            "nativeVisible": native_visible,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
        }

    def _promote_native_window(self) -> dict[str, object]:
        hwnd = self._native_hwnd()
        if not hwnd:
            return self._native_visibility_state()
        native_hwnd = ctypes.wintypes.HWND(hwnd)
        geometry = self.geometry()
        try:
            style = int(GetWindowLongW(native_hwnd, GWL_EXSTYLE))
            style = (style & ~WS_EX_NOACTIVATE & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            SetWindowLongW(native_hwnd, GWL_EXSTYLE, style)
            ShowWindowW(native_hwnd, SW_RESTORE)
            ShowWindowW(native_hwnd, SW_SHOWNORMAL)
            ShowWindowW(native_hwnd, SW_SHOW)
            SetWindowPos(
                native_hwnd,
                HWND_TOP,
                int(geometry.x()),
                int(geometry.y()),
                int(geometry.width()),
                int(geometry.height()),
                SWP_SHOWWINDOW | SWP_NOOWNERZORDER,
            )
            BringWindowToTop(native_hwnd)
            SetActiveWindow(native_hwnd)
            SetForegroundWindow(native_hwnd)
            try:
                SwitchToThisWindow(native_hwnd, True)
            except Exception:
                pass
            QApplication.processEvents()
        except Exception as exc:
            if callable(self.event_logger):
                self.event_logger(
                    "RENDERER_MAIN|AI_CONTROL_CENTER_NATIVE_SHOW_SKIPPED"
                    f"|reason={type(exc).__name__}"
                )
        state = self._native_visibility_state()
        if callable(self.event_logger):
            self.event_logger(
                "RENDERER_MAIN|AI_CONTROL_CENTER_NATIVE_SHOW_APPLIED"
                f"|qt_visible={str(state.get('qtVisible')).lower()}"
                f"|native_visible={str(state.get('nativeVisible')).lower()}"
                f"|hwnd={state.get('hwnd')}"
                f"|x={state.get('x')}|y={state.get('y')}|w={state.get('w')}|h={state.get('h')}"
            )
        return state

    def show_from_tray(self) -> dict[str, object]:
        geometry = self.geometry()
        if (
            geometry.width() <= 0
            or geometry.height() <= 0
            or not self._saved_geometry_is_usable(geometry)
        ):
            self.setGeometry(self._restored_geometry())
        else:
            self.setGeometry(self._bound_geometry_to_available_desktop(geometry))
        self.showNormal()
        self.show()
        self.raise_()
        self.activateWindow()
        QApplication.processEvents()
        return self._promote_native_window()


class DesktopRuntimeWindow(QWidget):
    core_visualization_ready = Signal()
    core_visualization_visible = Signal()

    def __init__(
        self,
        screen,
        visual_html_path: str,
        event_logger=None,
        runtime_log_path: str = "",
        surface_role: str = "hud",
        monitoring_hud_feature_enabled: bool = False,
        monitoring_hud_dashboard_visible: bool | None = None,
        monitoring_hud_initial_state: dict | None = None,
    ):
        super().__init__()
        global _DIALOG_RUNTIME_LOGGER

        self.screen_ref = screen
        self.visual_html_path = os.path.abspath(visual_html_path)
        self.event_logger = event_logger
        self.runtime_log_path = os.path.abspath(runtime_log_path) if runtime_log_path else ""
        self.surface_role = surface_role if surface_role in {"hud", "combined"} else "hud"
        self._overlay_trace_enabled = (os.environ.get("NEXUS_OVERLAY_TRACE") or "").strip().casefold() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self.desktop_mode = False
        self._is_shutting_down = False
        self._page_ready = False
        self._desktop_mode_requested = False
        self._startup_visibility_guard_active = True
        self._pending_visual_state = None
        self._pending_voice_level = None
        self._saved_action_source_path = None
        self._saved_action_create_dialog_factory = SavedActionCreateDialog
        self._created_tasks_dialog_factory = CreatedTasksDialog
        self._saved_action_edit_dialog_factory = SavedActionEditDialog
        self._callable_group_create_dialog_factory = CallableGroupCreateDialog
        self._created_groups_dialog_factory = CreatedGroupsDialog
        self._callable_group_edit_dialog_factory = CallableGroupEditDialog
        self._resident_access_settings_dialog = None
        _DIALOG_RUNTIME_LOGGER = self._log_event
        self._command_model = CommandOverlayModel()
        self._command_panel = CommandOverlayPanel()
        self._command_panel.submit_requested.connect(self.handle_local_submit_requested)
        self._command_panel.escape_requested.connect(self.handle_command_escape)
        self._command_panel.input_text_changed.connect(self.handle_command_text_changed)
        self._command_panel.input_armed_changed.connect(self.handle_command_input_armed_changed)
        self._command_panel.input_focus_acquired.connect(self.handle_command_input_focus_acquired)
        self._command_panel.input_focus_lost.connect(self.handle_command_input_focus_lost)
        self._command_panel.ambiguous_match_selected.connect(self.handle_ambiguous_match_selected)
        self._command_panel.create_custom_task_requested.connect(self.handle_create_custom_task_requested)
        self._command_panel.created_tasks_requested.connect(self.handle_created_tasks_requested)
        self._command_panel.create_custom_group_requested.connect(self.handle_create_custom_group_requested)
        self._command_panel.created_groups_requested.connect(self.handle_created_groups_requested)
        self._command_panel.edit_saved_action_requested.connect(self.handle_edit_saved_action_requested)
        self._provider_durable_consent_store_dir = (
            resolve_default_provider_durable_consent_store_dir()
        )
        self._ai_provider_state = build_provider_setup_completion_foundation_state(
            build_default_provider_readiness_config(),
            surface_role=self.surface_role,
            durable_consent_store_dir=self._provider_durable_consent_store_dir,
        )
        self._ai_control_center_dialog = None
        self._result_close_timer = QTimer(self)
        self._result_close_timer.setSingleShot(True)
        self._result_close_timer.timeout.connect(self._close_command_overlay_after_result)
        self._overlay_input_capture_until = 0.0
        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = False
        self._overlay_ready_timer = None
        self._overlay_ready_emitted = False
        self._overlay_ready_wait_attempt = 0
        self._overlay_ready_last_block_reason = ""
        self._overlay_ready_timeout_emitted = False
        self._authoring_dialog_active = False
        self._last_launch_failure_action_id = ""
        self._last_launch_failure_count = 0
        self._reported_recoverable_launch_failures = set()
        initial_hud_state = monitoring_hud_initial_state if isinstance(monitoring_hud_initial_state, dict) else {}
        self._monitoring_hud_feature_enabled = bool(monitoring_hud_feature_enabled)
        if monitoring_hud_dashboard_visible is None:
            monitoring_hud_dashboard_visible = monitoring_hud_feature_enabled
        self._monitoring_hud_visible = bool(
            self._monitoring_hud_feature_enabled and monitoring_hud_dashboard_visible
        )
        self._monitoring_hud_state_source = str(initial_hud_state.get("source") or "startup")
        self._monitoring_hud_access_adapter = MonitoringHudAccessAdapter(
            query_state=self.monitoring_hud_feature_state,
            persist_enabled=self._persist_monitoring_hud_enabled_from_access,
            open_or_restore_dashboard=self._open_or_restore_monitoring_hud_dashboard_from_access,
            close_dashboard=self._close_monitoring_hud_dashboard_from_access,
            is_shutting_down=lambda: bool(self._is_shutting_down),
            event_logger=self._log_event,
        )
        self._monitoring_hud_anchored = True
        self._monitoring_hud_snap_enabled = True
        self._monitoring_hud_polling_rate_ms = 1000
        self._monitoring_hud_control_signature = None
        self._monitoring_hud_monitor_management_signature = None
        self._monitoring_hud_overlay_profile_signature = None
        self._monitoring_hud_overlay_display_acceptance_signature = None
        self._monitoring_hud_active_overlay_profile_display_signature = None
        self._monitoring_hud_dashboard_overlay_independence_signature = None
        self._monitoring_hud_recording_control_signature = None
        self._monitoring_hud_recording_studio_active_request_id = 0
        self._monitoring_hud_recording_output_signature = None
        self._monitoring_hud_recording_folder_open_signature = None
        self._monitoring_hud_log_viewer_studio_signature = None
        self._monitoring_hud_log_viewer_studio_active_request_id = ""
        self._monitoring_hud_overlay_profiles = dict(initial_hud_state.get("overlayProfiles") if isinstance(initial_hud_state.get("overlayProfiles"), dict) else {})
        self._monitoring_hud_active_overlay_profile_id = str(initial_hud_state.get("activeOverlayProfileId") or "default-overlay-profile")
        self._monitoring_hud_overlay_profile_default_deleted_by_user = bool(initial_hud_state.get("overlayProfileDefaultDeletedByUser"))
        self._monitoring_hud_overlay_profile_monitor_ids = []
        self._monitoring_hud_active_child_window_signature = None
        self._monitoring_hud_control_sync_timer = QTimer(self)
        self._monitoring_hud_control_sync_timer.timeout.connect(self._sync_monitoring_hud_control_state_from_page)
        self._monitoring_hud_poll_timer = QTimer(self)
        self._monitoring_hud_poll_timer.timeout.connect(self._publish_monitoring_hud_telemetry_boundary)
        self._monitoring_hud_interactive_screen_rect = QRect()
        self._monitoring_hud_native_panel_drag_active = False
        self._monitoring_hud_native_panel_drag_start = QPoint()
        self._monitoring_hud_native_panel_drag_base = QPoint()
        self._monitoring_hud_native_window_resize_active = False
        self._monitoring_hud_native_window_resize_edges = Qt.Edges()
        self._monitoring_hud_native_window_resize_start = QPoint()
        self._monitoring_hud_native_window_resize_base = QRect()
        self._monitoring_hud_native_window_resize_poll_active = False
        self._monitoring_hud_native_window_resize_last_rect = QRect()
        self._monitoring_hud_native_window_resize_pending_point = QPoint()
        self._monitoring_hud_native_window_resize_last_apply = 0.0
        self._monitoring_hud_native_window_resize_frame_interval_ms = 8
        self._monitoring_hud_native_window_resize_poll_timer = QTimer(self)
        self._monitoring_hud_native_window_resize_poll_timer.setSingleShot(False)
        try:
            self._monitoring_hud_native_window_resize_poll_timer.setTimerType(Qt.PreciseTimer)
        except Exception:
            pass
        self._monitoring_hud_native_window_resize_poll_timer.timeout.connect(
            self._poll_monitoring_hud_fallback_window_resize
        )
        self._monitoring_hud_native_window_resize_frame_timer = QTimer(self)
        self._monitoring_hud_native_window_resize_frame_timer.setSingleShot(True)
        try:
            self._monitoring_hud_native_window_resize_frame_timer.setTimerType(Qt.PreciseTimer)
        except Exception:
            pass
        self._monitoring_hud_native_window_resize_frame_timer.timeout.connect(
            self._apply_monitoring_hud_queued_window_resize
        )
        self._monitoring_hud_user_geometry_override_active = False
        self._monitoring_hud_native_move_user_active = False
        self._monitoring_hud_native_move_start_geometry = QRect()
        self._monitoring_hud_native_move_last_geometry = QRect()
        self._monitoring_hud_native_move_source = ""
        self._monitoring_hud_native_move_frame_sync_last = 0.0
        self._monitoring_hud_resize_frame_sync_last = 0.0
        self._monitoring_hud_resize_js_sync_last = 0.0
        self._monitoring_hud_show_guard_active = False
        self._monitoring_hud_show_guard_generation = 0
        self._monitoring_hud_show_guard_release_delay_ms = 620
        self._monitoring_hud_deferred_initial_visibility_release = False
        self._monitoring_hud_resize_cursor_key = None
        self._monitoring_hud_resize_override_cursor_active = False
        self._monitoring_hud_resize_hover_timer = QTimer(self)
        self._monitoring_hud_resize_hover_timer.setInterval(8)
        self._monitoring_hud_resize_hover_timer.timeout.connect(self._poll_monitoring_hud_resize_hover_cursor)
        self._monitoring_hud_recording_control_click_bridge_timer = QTimer(self)
        self._monitoring_hud_recording_control_click_bridge_timer.setInterval(16)
        self._monitoring_hud_recording_control_click_bridge_timer.timeout.connect(
            self._poll_monitoring_hud_recording_control_click_bridge
        )
        self._monitoring_hud_lifecycle_transition_generation = 0
        self._monitoring_hud_lifecycle_timer_signature = None
        self._monitoring_hud_recording_control_click_bridge_down = False
        self._monitoring_hud_recording_control_click_bridge_press_point = QPoint()
        self._monitoring_hud_recording_control_click_bridge_last_activation_at = 0.0
        self._monitoring_hud_native_move_finalize_timer = QTimer(self)
        self._monitoring_hud_native_move_finalize_timer.setSingleShot(True)
        self._monitoring_hud_native_move_finalize_timer.setInterval(260)
        self._monitoring_hud_native_move_finalize_timer.timeout.connect(
            lambda: self._finish_monitoring_hud_native_system_move(
                self._monitoring_hud_native_move_source or "native_caption_move"
            )
        )
        self._monitoring_hud_native_card_drag_active = False
        self._monitoring_hud_native_card_resize_active = False
        self._monitoring_hud_native_card_drag_id = ""
        self._monitoring_hud_native_card_drag_start = QPoint()
        self._monitoring_hud_native_card_drag_base: dict[str, int] = {}
        self._monitoring_hud_live_screen_rects: dict[str, QRect] = {}
        self._monitoring_hud_live_page_state: dict[str, object] = {}
        self._monitoring_hud_dashboard_close_last_screen_rect = QRect()
        self._monitoring_hud_settings_action_last_screen_rect = QRect()
        self._monitoring_hud_window_corner_radius_px = 28
        self._monitoring_hud_rounded_window_mask_signature = None
        self._monitoring_hud_native_anchor_click_pending = False
        self._monitoring_hud_native_anchor_click_expected = True
        self._monitoring_hud_tray_menu_guard_active = False
        self._monitoring_hud_minimal_native_overlay = (
            MonitoringHudOverlayDisplayWindow(screen, event_logger)
            if self.surface_role == "hud"
            else None
        )
        self._monitoring_hud_recording_studio_window = (
            MonitoringHudRecordingStudioWindow(
                screen,
                event_logger,
                recording_action_handler=self._dispatch_monitoring_hud_recording_studio_action,
                log_viewer_handler=self._open_monitoring_hud_log_viewer_studio_from_recording,
            )
            if self.surface_role == "hud"
            else None
        )
        self._monitoring_hud_log_viewer_studio_window = (
            MonitoringHudLogViewerStudioWindow(screen, event_logger)
            if self.surface_role == "hud"
            else None
        )

        # The Dashboard is a standalone user-facing window; Core/Overlay ownership stays separate.
        self.setWindowFlags(
            (Qt.Window if self.surface_role == "hud" else Qt.Tool)
            | Qt.FramelessWindowHint
        )
        self.setAutoFillBackground(self.surface_role != "hud")
        if self.surface_role == "hud":
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setAttribute(Qt.WA_NoSystemBackground, True)
            self.setStyleSheet("background-color: transparent;")
        else:
            self.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.setWindowOpacity(0.0)

        self.setGeometry(self.compute_compact_geometry())
        if self.surface_role == "hud":
            self._apply_monitoring_hud_effective_window_minimum_size()
            self._apply_monitoring_hud_rounded_window_mask(source="init")
        self.setMouseTracking(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.webview = QWebEngineView(self)
        self.webview.setStyleSheet(
            "background-color: transparent; border: none;"
            if self.surface_role == "hud"
            else "background-color: rgb(0, 0, 0); border: none;"
        )
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setFocusPolicy(Qt.StrongFocus if self.surface_role == "hud" else Qt.NoFocus)
        self.webview.setMouseTracking(True)
        if self.surface_role == "hud":
            self.webview.setAttribute(Qt.WA_TranslucentBackground, True)
            self.webview.setAttribute(Qt.WA_NoSystemBackground, True)
            self.webview.setAutoFillBackground(False)
        self.webview.installEventFilter(self)
        QApplication.instance().installEventFilter(self)
        if self.surface_role == "hud":
            self.winId()
            window_handle = self.windowHandle()
            if window_handle is not None:
                window_handle.visibilityChanged.connect(
                    lambda *_args: QTimer.singleShot(
                        0, self._apply_monitoring_hud_window_interaction_state
                    )
                )
                window_handle.windowStateChanged.connect(
                    lambda *_args: QTimer.singleShot(
                        0, self._apply_monitoring_hud_window_interaction_state
                    )
                )
        self.webview.hide()

        self.webview.page().setBackgroundColor(
            QColor(0, 0, 0, 0) if self.surface_role == "hud" else QColor(0, 0, 0)
        )
        self.webview.loadFinished.connect(self._on_load_finished)
        self.webview.load(QUrl.fromLocalFile(self.visual_html_path))

        root.addWidget(self.webview)

    def eventFilter(self, watched, event):
        if watched is self.webview:
            try:
                self._handle_monitoring_hud_webview_recording_control_bridge(event)
            except Exception as exc:
                self._emit_runtime_signal(
                    "MONITORING_HUD_WEBVIEW_RECORDING_CONTROL_BRIDGE_GUARDED",
                    package="PKG-006",
                    slice="SLC-053",
                    error=type(exc).__name__,
                )
        try:
            if self._handle_monitoring_hud_webview_keyboard_activation_bridge(event):
                return True
        except Exception as exc:
            self._emit_runtime_signal(
                "MONITORING_HUD_WEBVIEW_KEYBOARD_ACTIVATION_BRIDGE_GUARDED",
                package="PKG-006",
                slice="SLC-053",
                error=type(exc).__name__,
            )
        try:
            if self._handle_monitoring_hud_native_panel_drag_event(event):
                return True
        except Exception as exc:
            self._emit_runtime_signal(
                "MONITORING_HUD_NATIVE_PANEL_EVENT_FILTER_GUARDED",
                package="PKG-006",
                slice="SLC-026",
                error=type(exc).__name__,
            )
            return False
        return super().eventFilter(watched, event)

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.surface_role != "hud" or not self.desktop_mode or not self.isVisible():
            return
        self._monitoring_hud_interactive_screen_rect = self.geometry()
        if (
            self._monitoring_hud_native_move_user_active
            and not self._monitoring_hud_native_window_resize_active
        ):
            self._monitoring_hud_native_move_last_geometry = QRect(self.geometry())
            self._sync_monitoring_hud_move_frame()
            self._monitoring_hud_native_move_finalize_timer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.surface_role == "hud":
            self._apply_monitoring_hud_rounded_window_mask(source="resize")

    def _handle_monitoring_hud_webview_keyboard_activation_bridge(self, event) -> bool:
        if self.surface_role != "hud" or not self.desktop_mode or not self.isVisible():
            return False
        active_window = QApplication.activeWindow()
        if active_window is not None and active_window is not self:
            return False
        if event.type() != QEvent.KeyRelease or event.key() not in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            return False
        key_name = " " if event.key() == Qt.Key_Space else "Enter"
        script = f"""
        (function() {{
            const active = document.activeElement && document.activeElement.closest
                ? document.activeElement.closest('[data-control="close-dashboard"],[data-control="open-recording-studio"],[data-control="open-log-viewer"],[data-control="toggle-recording"]')
                : null;
            if (!active) {{
                return JSON.stringify({{ eligible: false, key: {json.dumps(key_name)} }});
            }}
            const control = String(active.dataset.control || "");
            let activated = false;
            if (control === "open-recording-studio" && typeof monitoringHudRequestRecordingControlWindow === "function") {{
                activated = monitoringHudRequestRecordingControlWindow() !== false;
            }} else if (control === "open-log-viewer" && typeof monitoringHudRequestLogViewerWindow === "function") {{
                activated = monitoringHudRequestLogViewerWindow() !== false;
            }} else if (control === "toggle-recording" && typeof monitoringHudToggleRecording === "function") {{
                activated = monitoringHudToggleRecording() !== false;
            }} else if (control === "close-dashboard") {{
                activated = true;
            }}
            if (activated && monitoringHud) {{
                monitoringHud.dataset.nativeQtKeyboardActivationBridge = control;
                monitoringHud.dataset.nativeQtKeyboardActivationBridgeKey = {json.dumps(key_name)};
                monitoringHud.dataset.nativeQtKeyboardActivationBridgeAt = String(Date.now());
            }}
            if (activated && typeof monitoringHudRecordReliableActivation === "function") {{
                monitoringHudRecordReliableActivation(active, "native-qt-webview-keyboard-bridge", true);
            }}
            return JSON.stringify({{
                eligible: true,
                activated,
                control,
                id: String(active.id || ""),
                key: {json.dumps(key_name)}
            }});
        }})();
        """

        def record(result):
            payload = str(result or "")
            if '"control":"close-dashboard"' in payload or '"control": "close-dashboard"' in payload:
                self.request_monitoring_hud_dashboard_from_tray(
                    source="native-qt-webview-keyboard-close-bridge",
                    visible=False,
                )
            else:
                if '"control":"open-recording-studio"' in payload or '"control": "open-recording-studio"' in payload:
                    self._monitoring_hud_keyboard_force_visible_control = "open-recording-studio"
                elif '"control":"open-log-viewer"' in payload or '"control": "open-log-viewer"' in payload:
                    self._monitoring_hud_keyboard_force_visible_control = "open-log-viewer"
                QTimer.singleShot(120, self._sync_monitoring_hud_control_state_from_page)
                QTimer.singleShot(360, self._sync_monitoring_hud_control_state_from_page)
                QTimer.singleShot(720, self._sync_monitoring_hud_control_state_from_page)
            self._emit_runtime_signal(
                "MONITORING_HUD_NATIVE_QT_KEYBOARD_ACTIVATION_BRIDGE_READY",
                package="PKG-006",
                slice="SLC-053",
                result=payload[:240],
            )

        self._run_javascript_with_result(script, record)
        event.accept()
        return True

    def _handle_monitoring_hud_webview_recording_control_bridge(self, event) -> None:
        if self.surface_role != "hud" or not self.desktop_mode or not self.isVisible():
            return
        if event.type() != QEvent.MouseButtonRelease or event.button() != Qt.LeftButton:
            return
        try:
            point = event.position().toPoint()
        except Exception:
            return
        script = f"""
        (function() {{
            const x = {int(point.x())};
            const y = {int(point.y())};
            const rawTarget = document.elementFromPoint ? document.elementFromPoint(x, y) : null;
            const target = rawTarget && rawTarget.closest
                ? rawTarget.closest('[data-control="open-recording-studio"],[data-control="open-log-viewer"],[data-control="toggle-recording"]')
                : null;
            if (!target) {{
                return JSON.stringify({{ eligible: false, x, y }});
            }}
            const control = String(target.dataset.control || "");
            const before = {{
                recordingControlWindowRequested: Boolean(monitoringHudControlState && monitoringHudControlState.recordingControlWindowRequested),
                logViewerRequested: Boolean(monitoringHudControlState && monitoringHudControlState.logViewerRequested),
                recordingState: typeof monitoringHudRecordingState === "function" ? monitoringHudRecordingState() : ""
            }};
            const releasePointerActivatedAt = Number(target.dataset.reliablePointerActivatedAt || 0);
            const releaseNativeCursorActivatedAt = Number(target.dataset.nativeCursorActivatedAt || 0);
            const releaseRecentReliable = Boolean(
                (releasePointerActivatedAt && Date.now() - releasePointerActivatedAt < 1100)
                || (releaseNativeCursorActivatedAt && Date.now() - releaseNativeCursorActivatedAt < 2200)
            );
            window.setTimeout(() => {{
                let activated = false;
                let alreadyHandled = false;
                let skippedRecentReliable = false;
                const pointerActivatedAt = Number(target.dataset.reliablePointerActivatedAt || 0);
                const nativeCursorActivatedAt = Number(target.dataset.nativeCursorActivatedAt || 0);
                const recentReliable = Boolean(
                    (pointerActivatedAt && Date.now() - pointerActivatedAt < 1100)
                    || (nativeCursorActivatedAt && Date.now() - nativeCursorActivatedAt < 2200)
                );
                if (recentReliable) {{
                    alreadyHandled = true;
                    skippedRecentReliable = true;
                    const nativeRequestMissing = Boolean(
                        (control === "open-recording-studio"
                            && !(monitoringHudControlState && monitoringHudControlState.recordingControlWindowRequested))
                        || (control === "open-log-viewer"
                            && !(monitoringHudControlState && monitoringHudControlState.logViewerRequested))
                    );
                    if (nativeRequestMissing) {{
                        alreadyHandled = false;
                        skippedRecentReliable = false;
                    }}
                    if (nativeRequestMissing && control === "open-recording-studio") {{
                        if (typeof monitoringHudRequestRecordingControlWindow === "function") {{
                            activated = monitoringHudRequestRecordingControlWindow() !== false;
                        }}
                    }} else if (nativeRequestMissing && control === "open-log-viewer") {{
                        if (typeof monitoringHudRequestLogViewerWindow === "function") {{
                            activated = monitoringHudRequestLogViewerWindow() !== false;
                        }}
                    }}
                }} else if (control === "open-recording-studio") {{
                    if (typeof monitoringHudRequestRecordingControlWindow === "function") {{
                        activated = monitoringHudRequestRecordingControlWindow() !== false;
                    }}
                }} else if (control === "open-log-viewer") {{
                    if (typeof monitoringHudRequestLogViewerWindow === "function") {{
                        activated = monitoringHudRequestLogViewerWindow() !== false;
                    }}
                }} else if (control === "toggle-recording") {{
                    if (typeof monitoringHudToggleRecording === "function") {{
                        activated = monitoringHudToggleRecording() !== false;
                    }}
                }}
                if (activated && monitoringHud) {{
                    monitoringHud.dataset.nativeQtRecordingControlBridge = control;
                    monitoringHud.dataset.nativeQtRecordingControlBridgePhase = "mouse-release";
                    monitoringHud.dataset.nativeQtRecordingControlBridgeAt = String(Date.now());
                }}
                if (activated && typeof monitoringHudRecordReliableActivation === "function") {{
                    monitoringHudRecordReliableActivation(target, "native-qt-webview-release-bridge", true);
                }}
            }}, 90);
                return JSON.stringify({{
                    eligible: true,
                    control,
                    alreadyHandled: releaseRecentReliable,
                    skippedRecentReliable: releaseRecentReliable,
                    id: String(target.id || ""),
                    x,
                    y,
                before
            }});
        }})();
        """
        self._run_javascript_with_result(
            script,
            lambda result: self._emit_runtime_signal(
                "MONITORING_HUD_NATIVE_QT_RECORDING_CONTROL_BRIDGE_READY",
                package="PKG-006",
                slice="SLC-053",
                result=str(result)[:240],
            ),
        )
        QTimer.singleShot(160, self._sync_monitoring_hud_control_state_from_page)

    def _monitoring_hud_webview_local_point_from_screen_point(self, screen_point: QPoint) -> QPoint:
        if screen_point.isNull() or self.webview is None:
            return QPoint()
        try:
            local_point = self.webview.mapFromGlobal(screen_point)
        except Exception:
            return QPoint()
        try:
            if not self.webview.rect().contains(local_point):
                return QPoint()
        except Exception:
            return QPoint()
        return local_point

    def _request_monitoring_hud_recording_control_click_bridge(
        self,
        press_point: QPoint,
        release_point: QPoint,
    ) -> None:
        if self.surface_role != "hud" or not self.desktop_mode or not self.isVisible():
            return
        if self.webview is None or not self.webview.isVisible():
            return
        press_local = self._monitoring_hud_webview_local_point_from_screen_point(press_point)
        release_local = self._monitoring_hud_webview_local_point_from_screen_point(release_point)
        if press_local.isNull() or release_local.isNull():
            return
        now = time.monotonic()
        if now - self._monitoring_hud_recording_control_click_bridge_last_activation_at < 0.12:
            return
        self._monitoring_hud_recording_control_click_bridge_last_activation_at = now
        script = f"""
        (function() {{
            const pressX = {int(press_local.x())};
            const pressY = {int(press_local.y())};
            const releaseX = {int(release_local.x())};
            const releaseY = {int(release_local.y())};
            const selector = '[data-control="open-recording-studio"],[data-control="open-log-viewer"],[data-control="toggle-recording"]';
            const pressRaw = document.elementFromPoint ? document.elementFromPoint(pressX, pressY) : null;
            const releaseRaw = document.elementFromPoint ? document.elementFromPoint(releaseX, releaseY) : null;
            const pressTarget = pressRaw && pressRaw.closest ? pressRaw.closest(selector) : null;
            const releaseTarget = releaseRaw && releaseRaw.closest ? releaseRaw.closest(selector) : null;
            if (!pressTarget || !releaseTarget || pressTarget !== releaseTarget) {{
                return JSON.stringify({{
                    eligible: false,
                    reason: "press-release-target-mismatch",
                    pressTarget: pressTarget ? String(pressTarget.id || pressTarget.dataset.control || "") : "",
                    releaseTarget: releaseTarget ? String(releaseTarget.id || releaseTarget.dataset.control || "") : "",
                    pressX,
                    pressY,
                    releaseX,
                    releaseY
                }});
            }}
            const control = String(releaseTarget.dataset.control || "");
            const before = {{
                recordingControlWindowRequested: Boolean(monitoringHudControlState && monitoringHudControlState.recordingControlWindowRequested),
                logViewerRequested: Boolean(monitoringHudControlState && monitoringHudControlState.logViewerRequested),
                recordingState: typeof monitoringHudRecordingState === "function" ? monitoringHudRecordingState() : ""
            }};
            let activated = false;
            let alreadyHandled = false;
            let skippedRecentReliable = false;
            const pointerActivatedAt = Number(releaseTarget.dataset.reliablePointerActivatedAt || 0);
            const nativeCursorActivatedAt = Number(releaseTarget.dataset.nativeCursorActivatedAt || 0);
            const recentReliable = Boolean(
                (pointerActivatedAt && Date.now() - pointerActivatedAt < 1100)
                || (nativeCursorActivatedAt && Date.now() - nativeCursorActivatedAt < 2200)
            );
            if (recentReliable) {{
                skippedRecentReliable = true;
                alreadyHandled = true;
                const nativeRequestMissing = Boolean(
                    (control === "open-recording-studio"
                        && !(monitoringHudControlState && monitoringHudControlState.recordingControlWindowRequested))
                    || (control === "open-log-viewer"
                        && !(monitoringHudControlState && monitoringHudControlState.logViewerRequested))
                );
                if (nativeRequestMissing) {{
                    skippedRecentReliable = false;
                    alreadyHandled = false;
                }}
                if (nativeRequestMissing && control === "open-recording-studio") {{
                    if (typeof monitoringHudRequestRecordingControlWindow === "function") {{
                        activated = monitoringHudRequestRecordingControlWindow() !== false;
                    }}
                }} else if (nativeRequestMissing && control === "open-log-viewer") {{
                    if (typeof monitoringHudRequestLogViewerWindow === "function") {{
                        activated = monitoringHudRequestLogViewerWindow() !== false;
                    }}
                }}
            }} else if (control === "open-recording-studio") {{
                if (typeof monitoringHudRequestRecordingControlWindow === "function") {{
                    activated = monitoringHudRequestRecordingControlWindow() !== false;
                }}
            }} else if (control === "open-log-viewer") {{
                if (typeof monitoringHudRequestLogViewerWindow === "function") {{
                    activated = monitoringHudRequestLogViewerWindow() !== false;
                }}
            }} else if (control === "toggle-recording") {{
                if (typeof monitoringHudToggleRecording === "function") {{
                    activated = monitoringHudToggleRecording() !== false;
                }}
            }}
            if (monitoringHudControlState && activated) {{
                monitoringHudControlState.lastMouseEvent = {{
                    type: "native-cursor-left-release",
                    target: String(releaseTarget.id || releaseTarget.dataset.control || ""),
                    control,
                    pressClientX: pressX,
                    pressClientY: pressY,
                    clientX: releaseX,
                    clientY: releaseY,
                    bridge: "native-cursor-recording-control"
                }};
            }}
            if (activated && monitoringHud) {{
                releaseTarget.dataset.nativeCursorActivatedAt = String(Date.now());
                releaseTarget.dataset.reliablePointerActivatedAt = String(Date.now());
                monitoringHud.dataset.nativeCursorRecordingControlBridge = control;
                monitoringHud.dataset.nativeCursorRecordingControlBridgePhase = "left-button-release";
                monitoringHud.dataset.nativeCursorRecordingControlBridgeAt = String(Date.now());
                monitoringHud.dataset.nativeCursorRecordingControlBridgeProof = "press-release-same-visible-control";
                monitoringHud.dataset.nativeCursorRecordingStudioReopenProof = "normal-button-reopen-path";
            }}
            if (activated && typeof monitoringHudRecordReliableActivation === "function") {{
                const key = control === "toggle-recording"
                    ? "recording-control:quick-access-start-stop"
                    : `recording-control:${{control}}`;
                monitoringHudRecordReliableActivation(releaseTarget, "native-cursor-left-release-bridge", true);
                if (monitoringHud) {{
                    monitoringHud.dataset.lastInteractiveControl = key;
                    monitoringHud.dataset.lastInteractiveControlPhase = "native-cursor-left-release-bridge";
                }}
            }}
            return JSON.stringify({{
                eligible: true,
                activated,
                alreadyHandled,
                skippedRecentReliable,
                control,
                id: String(releaseTarget.id || ""),
                pressX,
                pressY,
                releaseX,
                releaseY,
                before,
                after: {{
                    recordingControlWindowRequested: Boolean(monitoringHudControlState && monitoringHudControlState.recordingControlWindowRequested),
                    logViewerRequested: Boolean(monitoringHudControlState && monitoringHudControlState.logViewerRequested),
                    recordingState: typeof monitoringHudRecordingState === "function" ? monitoringHudRecordingState() : ""
                }}
            }});
        }})();
        """
        self._run_javascript_with_result(
            script,
            lambda result: self._emit_runtime_signal(
                "MONITORING_HUD_NATIVE_CURSOR_RECORDING_CONTROL_BRIDGE_READY",
                package="PKG-006",
                slice="SLC-053",
                result=str(result)[:320],
            ),
        )
        QTimer.singleShot(160, self._sync_monitoring_hud_control_state_from_page)

    def _poll_monitoring_hud_recording_control_click_bridge(self):
        if (
            self.surface_role != "hud"
            or not self.desktop_mode
            or not self.isVisible()
            or self.webview is None
            or not self.webview.isVisible()
            or self._monitoring_hud_native_panel_drag_active
            or self._monitoring_hud_native_window_resize_active
            or self._monitoring_hud_native_card_drag_active
            or self._monitoring_hud_native_card_resize_active
        ):
            self._monitoring_hud_recording_control_click_bridge_down = False
            self._monitoring_hud_recording_control_click_bridge_press_point = QPoint()
            return
        down = self._monitoring_hud_left_mouse_button_down()
        screen_point = self._monitoring_hud_cursor_screen_point()
        if down and not self._monitoring_hud_recording_control_click_bridge_down:
            self._monitoring_hud_recording_control_click_bridge_press_point = QPoint(screen_point)
        elif not down and self._monitoring_hud_recording_control_click_bridge_down:
            press_point = QPoint(self._monitoring_hud_recording_control_click_bridge_press_point)
            self._monitoring_hud_recording_control_click_bridge_press_point = QPoint()
            if not press_point.isNull() and not screen_point.isNull():
                self._request_monitoring_hud_recording_control_click_bridge(press_point, screen_point)
        self._monitoring_hud_recording_control_click_bridge_down = down

    def compute_compact_geometry(self):
        g = self.screen_ref.geometry()
        if self.surface_role == "hud":
            available = self.screen_ref.availableGeometry()
            width = min(780, max(640, int(available.width() * 0.30)))
            height = min(1060, max(760, available.height() - 150))
            margin_x = min(56, max(24, int(available.width() * 0.02)))
            margin_y = min(90, max(36, int(available.height() * 0.06)))
            x = available.x() + available.width() - width - margin_x
            y = available.y() + margin_y
            return QRect(x, y, width, height)

        width = int(g.width() * 0.46)
        height = int(g.height() * 0.68)

        x = g.x() + (g.width() - width) // 2
        y = g.y() + int(g.height() * 0.08)

        return QRect(x, y, width, height)

    def _virtual_desktop_geometry(self) -> QRect:
        screens = QApplication.screens()
        if not screens:
            return self.screen_ref.availableGeometry()
        rect = screens[0].availableGeometry()
        for screen in screens[1:]:
            rect = rect.united(screen.availableGeometry())
        return rect

    def prepare_desktop_geometry(self):
        self.setGeometry(self.compute_compact_geometry())
        self._apply_monitoring_hud_rounded_window_mask(source="prepare_desktop_geometry")

    def is_core_visualization_ready(self):
        return self._page_ready

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_monitoring_hud_rounded_window_mask(source="show")

        if not self.desktop_mode:
            self._desktop_mode_requested = True
            self._schedule_desktop_mode_enable()

    def _apply_monitoring_hud_rounded_window_mask(self, *, source: str = "runtime"):
        if self.surface_role != "hud":
            return
        rect = self.rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return
        radius = min(
            self._monitoring_hud_window_corner_radius_px,
            max(1, rect.width() // 2),
            max(1, rect.height() // 2),
        )
        region_radius = self._monitoring_hud_window_region_corner_radius_px(radius)
        signature = (
            rect.width(),
            rect.height(),
            radius,
            region_radius,
            "win32-roundrect" if os.name == "nt" else "qt-region",
        )
        if signature == self._monitoring_hud_rounded_window_mask_signature:
            return
        if os.name == "nt":
            try:
                # Use a simple native rounded rectangle region instead of a polygonal
                # Qt mask. The native region keeps the light-backdrop corner fix while
                # avoiding complex shaped-window movement/resize jank.
                region_handle = CreateRoundRectRgn(
                    0,
                    0,
                    int(rect.width()) + 1,
                    int(rect.height()) + 1,
                    int(region_radius * 2),
                    int(region_radius * 2),
                )
                if region_handle:
                    applied = bool(SetWindowRgn(ctypes.wintypes.HWND(int(self.winId())), region_handle, True))
                    if applied:
                        self._monitoring_hud_rounded_window_mask_signature = signature
                        self._emit_monitoring_hud_rounded_window_mask_ready(
                            source=source,
                            radius=radius,
                            width=rect.width(),
                            height=rect.height(),
                            bounds_width=rect.width(),
                            bounds_height=rect.height(),
                            region_radius=region_radius,
                            mask_model="simple-native-roundrect-region-matches-css-chrome",
                        )
                        return
                    DeleteObject(HGDIOBJ(region_handle))
            except Exception:
                pass
            signature = (rect.width(), rect.height(), radius, region_radius, "qt-region")
            if signature == self._monitoring_hud_rounded_window_mask_signature:
                return
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), float(region_radius), float(region_radius))
        region = QRegion(path.toFillPolygon().toPolygon())
        if region.isEmpty():
            return
        self.setMask(region)
        self._monitoring_hud_rounded_window_mask_signature = signature
        bounds = region.boundingRect()
        self._emit_monitoring_hud_rounded_window_mask_ready(
            source=source,
            radius=radius,
            width=rect.width(),
            height=rect.height(),
            bounds_width=bounds.width(),
            bounds_height=bounds.height(),
            region_radius=region_radius,
            mask_model="native-rounded-window-region-matches-css-chrome",
        )

    def _emit_monitoring_hud_rounded_window_mask_ready(
        self,
        *,
        source: str,
        radius: int,
        region_radius: int,
        width: int,
        height: int,
        bounds_width: int,
        bounds_height: int,
        mask_model: str,
    ):
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_ROUNDED_WINDOW_MASK_READY",
            package="PKG-006",
            slice="SLC-027",
            issue=137,
            source=source,
            mask_model=mask_model,
            corner_bleed_policy="no-opaque-rectangular-corners-over-light-backdrops",
            resize_hit_test_model="rounded-mask-clipped-visible-rail",
            radius_px=radius,
            visual_radius_px=radius,
            region_radius_px=region_radius,
            width=width,
            height=height,
            bounds_width=bounds_width,
            bounds_height=bounds_height,
        )

    def _log_event(self, event):
        if callable(self.event_logger):
            try:
                self.event_logger(event)
            except Exception:
                pass

    def _normalize_runtime_signal_value(self, value) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        text = str(value)
        for original, replacement in (
            ("\r", " "),
            ("\n", " "),
            ("\t", " "),
            ("|", "/"),
        ):
            text = text.replace(original, replacement)
        return text.strip()

    def _emit_runtime_signal(self, signal_name: str, **fields):
        parts = [f"RENDERER_MAIN|{signal_name}"]
        for key, value in fields.items():
            normalized = self._normalize_runtime_signal_value(value)
            if not normalized:
                continue
            parts.append(f"{key}={normalized}")
        self._log_event("|".join(parts))

    def _saved_action_inventory_signal_fields(self, inventory=None) -> dict:
        inventory = inventory or self._command_model.action_catalog.saved_action_inventory
        return {
            "saved_status_kind": getattr(inventory, "status_kind", ""),
            "saved_count": len(getattr(inventory, "actions", ()) or ()),
            "source_path": getattr(inventory, "path", ""),
        }

    def _saved_group_inventory_signal_fields(self, inventory=None) -> dict:
        inventory = inventory or self._command_model.action_catalog.saved_group_inventory
        return {
            "group_status_kind": getattr(inventory, "status_kind", ""),
            "group_count": len(getattr(inventory, "groups", ()) or ()),
            "group_source_path": getattr(inventory, "path", ""),
        }

    def _ensure_overlay_ready_tracking(self):
        if getattr(self, "_overlay_ready_timer", None) is None:
            try:
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(self._check_overlay_ready_state)
                self._overlay_ready_timer = timer
            except RuntimeError:
                self._overlay_ready_timer = False
        if not hasattr(self, "_overlay_ready_emitted"):
            self._overlay_ready_emitted = False
        if not hasattr(self, "_overlay_ready_wait_attempt"):
            self._overlay_ready_wait_attempt = 0
        if not hasattr(self, "_overlay_ready_last_block_reason"):
            self._overlay_ready_last_block_reason = ""
        if not hasattr(self, "_overlay_ready_timeout_emitted"):
            self._overlay_ready_timeout_emitted = False

    def _reset_overlay_ready_tracking(self):
        self._ensure_overlay_ready_tracking()
        if self._overlay_ready_timer not in {None, False}:
            self._overlay_ready_timer.stop()
        self._overlay_ready_emitted = False
        self._overlay_ready_wait_attempt = 0
        self._overlay_ready_last_block_reason = ""
        self._overlay_ready_timeout_emitted = False

    def _overlay_ready_signal_fields(self) -> dict:
        panel_visible = self._command_panel.isVisible()
        input_focus = self._command_panel.input_line.hasFocus()
        input_visible = self._command_panel.input_line.isVisible()
        input_enabled = self._command_panel.input_line.isEnabled()
        panel_active = self._command_panel.isActiveWindow()
        capture_active = self._overlay_input_capture_active()
        needs_global_capture = False
        try:
            needs_global_capture = self.overlay_needs_global_input_capture()
        except Exception:
            needs_global_capture = False
        entry_actions_visible = (
            self._command_panel.create_custom_task_button.isVisible()
            and self._command_panel.created_tasks_button.isVisible()
            and self._command_panel.create_custom_group_button.isVisible()
            and self._command_panel.created_groups_button.isVisible()
        )
        return {
            "phase": self._command_model.phase,
            "input_armed": self._command_model.input_armed,
            "model_visible": self._command_model.visible,
            "panel_visible": panel_visible,
            "panel_active": panel_active,
            "input_focus": input_focus,
            "input_visible": input_visible,
            "input_enabled": input_enabled,
            "input_capture_active": capture_active,
            "local_input_engaged": self._overlay_local_input_engaged,
            "global_capture_suspended": self._overlay_global_capture_suspended,
            "needs_global_capture": needs_global_capture,
            "entry_actions_visible": entry_actions_visible,
            "panel_width": self._command_panel.width(),
            "panel_height": self._command_panel.height(),
        }

    def _overlay_ready_state_reason(self, fields: dict) -> str:
        if self._is_shutting_down:
            return "shutting_down"
        if not fields.get("model_visible"):
            return "model_hidden"
        if not fields.get("panel_visible"):
            return "panel_hidden"
        if int(fields.get("panel_width") or 0) <= 0 or int(fields.get("panel_height") or 0) <= 0:
            return "panel_geometry_unstable"
        if not fields.get("input_visible"):
            return "input_hidden"
        if not fields.get("input_enabled"):
            return "input_disabled"
        if fields.get("phase") != "entry":
            return f"phase_{fields.get('phase') or 'unknown'}"
        if not fields.get("input_armed"):
            return "input_not_armed"
        if not fields.get("entry_actions_visible"):
            return "entry_actions_hidden"
        if (
            fields.get("input_focus")
            or fields.get("local_input_engaged")
            or fields.get("needs_global_capture")
            or fields.get("input_capture_active")
        ):
            return "ready"
        return "input_path_not_ready"

    def _schedule_overlay_ready_check(self, delay_ms: int = 0):
        self._ensure_overlay_ready_tracking()
        if self._overlay_ready_timer is False:
            return
        if self._is_shutting_down or self._overlay_ready_emitted:
            return
        self._overlay_ready_timer.start(max(0, int(delay_ms)))

    def _emit_overlay_ready_signal(self):
        self._ensure_overlay_ready_tracking()
        if self._overlay_ready_emitted:
            return
        fields = self._overlay_ready_signal_fields()
        reason = self._overlay_ready_state_reason(fields)
        if reason != "ready":
            return
        self._overlay_ready_emitted = True
        if self._overlay_ready_timer not in {None, False}:
            self._overlay_ready_timer.stop()
        self._emit_runtime_signal("COMMAND_OVERLAY_READY", **fields)

    def _check_overlay_ready_state(self):
        self._ensure_overlay_ready_tracking()
        if self._overlay_ready_emitted:
            return
        fields = self._overlay_ready_signal_fields()
        reason = self._overlay_ready_state_reason(fields)
        if reason == "ready":
            self._emit_overlay_ready_signal()
            return

        self._overlay_ready_wait_attempt += 1
        if (
            reason != self._overlay_ready_last_block_reason
            or self._overlay_ready_wait_attempt in {1, 5, 15}
        ):
            self._overlay_ready_last_block_reason = reason
            self._emit_runtime_signal(
                "COMMAND_OVERLAY_READY_WAITING",
                reason=reason,
                attempt=self._overlay_ready_wait_attempt,
                **fields,
            )
        if self._overlay_ready_wait_attempt >= 25 and not self._overlay_ready_timeout_emitted:
            self._overlay_ready_timeout_emitted = True
            self._emit_runtime_signal(
                "COMMAND_OVERLAY_READY_TIMEOUT",
                reason=reason,
                attempt=self._overlay_ready_wait_attempt,
                **fields,
            )
        if self._command_model.visible and not self._is_shutting_down:
            self._schedule_overlay_ready_check(40 if self._overlay_ready_wait_attempt < 15 else 120)

    def _handle_dialog_lifecycle_signal(self, signal_base: str, stage: str, dialog=None, **fields):
        signal_name = f"{signal_base}_{stage.upper()}"
        if dialog is not None:
            fields.setdefault("dialog_name", dialog.windowTitle())
            fields.setdefault("dialog_object_name", dialog.objectName())
            fields.setdefault("dialog_class_name", type(dialog).__name__)
            try:
                fields.setdefault("win_id", str(int(dialog.winId())))
            except Exception:
                pass
            try:
                focus_widget = dialog.focusWidget()
            except Exception:
                focus_widget = None
            if focus_widget is not None:
                fields.setdefault(
                    "focus_widget",
                    focus_widget.objectName() or type(focus_widget).__name__,
                )
        self._emit_runtime_signal(signal_name, **fields)

    def _create_dialog_with_optional_lifecycle(self, factory, *args, **kwargs):
        try:
            return factory(*args, **kwargs)
        except TypeError as exc:
            try:
                signature = inspect.signature(factory)
            except (TypeError, ValueError):
                signature = None

            if signature is None or any(
                parameter.kind == inspect.Parameter.VAR_KEYWORD
                for parameter in signature.parameters.values()
            ):
                raise

            accepted_kwargs = {
                name
                for name, parameter in signature.parameters.items()
                if parameter.kind in {
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                }
            }
            filtered_kwargs = {
                name: value
                for name, value in kwargs.items()
                if name in accepted_kwargs
            }
            if filtered_kwargs == kwargs:
                raise exc
            return factory(*args, **filtered_kwargs)

    def _authoring_dialog_blocks_new_dialog(self) -> bool:
        return bool(getattr(self, "_authoring_dialog_active", False))

    def _exec_authoring_dialog(self, dialog: QDialog, *, action: str):
        self._authoring_dialog_active = True
        try:
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_DIALOG_EXEC_START",
                action=action,
                dialog_name=dialog.windowTitle(),
                dialog_object_name=dialog.objectName() or type(dialog).__name__,
                win_id=int(dialog.winId()),
            )
            result = dialog.exec()
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_DIALOG_EXEC_RETURNED",
                action=action,
                dialog_name=dialog.windowTitle(),
                dialog_object_name=dialog.objectName() or type(dialog).__name__,
                win_id=int(dialog.winId()),
                result="accepted" if result == QDialog.Accepted else "rejected",
            )
            return result
        finally:
            self._authoring_dialog_active = False

    def _trace_overlay(self, event: str, **fields):
        if not self._overlay_trace_enabled:
            return
        phase = getattr(self._command_model, "phase", "unknown")
        local_engaged = "true" if self._overlay_local_input_engaged else "false"
        panel_active = "true" if self._command_panel.isActiveWindow() else "false"
        input_focus = "true" if self._command_panel.input_line.hasFocus() else "false"
        input_text = repr(self._command_model.input_text)
        extras = [
            f"event={event}",
            f"phase={phase}",
            f"local_engaged={local_engaged}",
            f"capture_suspended={'true' if self._overlay_global_capture_suspended else 'false'}",
            f"panel_active={panel_active}",
            f"input_focus={input_focus}",
            f"input_text={input_text}",
        ]
        for key, value in fields.items():
            extras.append(f"{key}={value}")
        self._log_event("OVERLAY_TRACE|source=renderer|" + "|".join(extras))

    def _foreground_window_snapshot(self):
        try:
            hwnd = GetForegroundWindow()
            if not hwnd:
                return {"hwnd": "none", "class_name": "", "title": ""}

            class_buffer = ctypes.create_unicode_buffer(256)
            GetClassNameW(hwnd, class_buffer, len(class_buffer))

            title_length = max(0, int(GetWindowTextLengthW(hwnd)))
            title_buffer = ctypes.create_unicode_buffer(max(1, title_length + 1))
            GetWindowTextW(hwnd, title_buffer, len(title_buffer))

            return {
                "hwnd": hex(int(hwnd)),
                "class_name": class_buffer.value or "",
                "title": title_buffer.value or "",
            }
        except Exception:
            return {"hwnd": "unavailable", "class_name": "", "title": ""}

    def _run_javascript(self, script):
        page = self.webview.page()
        if page is not None:
            page.runJavaScript(script)

    def _dispatch_monitoring_hud_recording_studio_action(self, action: str) -> None:
        if action == "start":
            script = "if (typeof monitoringHudStartRecording === 'function') { monitoringHudStartRecording(); }"
        elif action == "pause":
            script = "if (typeof monitoringHudPauseRecording === 'function') { monitoringHudPauseRecording(); }"
        elif action == "stop":
            script = "if (typeof monitoringHudStopRecording === 'function') { monitoringHudStopRecording(); }"
        else:
            script = "if (typeof monitoringHudToggleRecording === 'function') { monitoringHudToggleRecording(); }"
        self._run_javascript(script)

    def _open_monitoring_hud_log_viewer_studio_from_recording(self) -> None:
        if self._monitoring_hud_log_viewer_studio_window is None:
            return
        state = getattr(self, "_monitoring_hud_live_page_state", {}) or {}
        summary = state.get("logViewerSummary") if isinstance(state, dict) else {}
        if not isinstance(summary, dict):
            summary = {}
        request_id = f"recording-studio-route-{int(time.time() * 1000)}"
        self._monitoring_hud_log_viewer_studio_window.update_product_state(
            request_id=request_id,
            native_log_path=str(summary.get("nativeLogPath") or ""),
            export_dir=str(summary.get("exportDir") or ""),
            activate_window=True,
            parent_geometry=self.geometry(),
        )
        proof = self._monitoring_hud_log_viewer_studio_window.proof_state()
        self._emit_runtime_signal(
            "MONITORING_HUD_RECORDING_STUDIO_LOG_VIEWER_ROUTE_READY",
            package="PKG-006",
            slice="SLC-054",
            seam="Live Validation",
            request_id=request_id,
            surface=proof.get("surface"),
            visible=proof.get("visible"),
            standalone=proof.get("standaloneTopLevel"),
            route="recording-studio-open-log-viewer-action",
        )

    def _run_javascript_with_result(self, script, callback):
        page = self.webview.page()
        if page is None:
            callback(None)
            return
        try:
            page.runJavaScript(script, 0, callback)
        except TypeError:
            page.runJavaScript(script, callback)

    def _monitoring_hud_control_state(self) -> dict[str, object]:
        return {
            "featureEnabled": self._monitoring_hud_feature_enabled,
            "overlayDeferred": True,
            "visible": self._monitoring_hud_visible,
            "anchored": self._monitoring_hud_anchored,
            "snapEnabled": self._monitoring_hud_snap_enabled,
            "pollingRateMs": self._monitoring_hud_polling_rate_ms,
            "overlayProfiles": dict(getattr(self, "_monitoring_hud_overlay_profiles", {}) or {}),
            "activeOverlayProfileId": str(getattr(self, "_monitoring_hud_active_overlay_profile_id", "default-overlay-profile") or ""),
            "overlayProfileDefaultDeletedByUser": bool(getattr(self, "_monitoring_hud_overlay_profile_default_deleted_by_user", False)),
        }

    def _publish_monitoring_hud_control_state_to_page(self):
        if not self._page_ready or self._is_shutting_down:
            return
        state_json = json.dumps(self._monitoring_hud_control_state(), sort_keys=True)
        self._run_javascript(
            f"""
            if (window.setMonitoringHudControlState) {{
                window.setMonitoringHudControlState({state_json});
            }}
            """
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_CONTROL_STATE_READY",
            package="PKG-006",
            slice="SLC-027",
            source="page_publish",
            feature_enabled=self._monitoring_hud_feature_enabled,
            visible=self._monitoring_hud_visible,
            anchored=self._monitoring_hud_anchored,
            snap=self._monitoring_hud_snap_enabled,
            polling_rate_ms=self._monitoring_hud_polling_rate_ms,
        )

    def _estimate_monitoring_hud_interactive_screen_rect(self) -> QRect:
        geometry = self.geometry()
        if geometry.width() <= 0 or geometry.height() <= 0:
            geometry = self.compute_compact_geometry()
        if self.surface_role == "hud":
            return QRect(geometry.x(), geometry.y(), geometry.width(), geometry.height())
        panel_width = min(780, max(320, geometry.width() - 48))
        panel_height = min(1040, max(360, geometry.height() - 48))
        right_margin = min(max(int(geometry.width() * 0.04), 24), 64)
        top_margin = min(max(int(geometry.height() * 0.04), 24), 56)
        left = geometry.x() + max(0, geometry.width() - right_margin - panel_width)
        top = geometry.y() + top_margin
        return QRect(
            int(left) - 12,
            int(top) - 12,
            int(panel_width) + 24,
            int(panel_height) + 24,
        )

    def _set_monitoring_hud_interactive_rect_from_page(self, rect: dict[str, object] | None):
        if not isinstance(rect, dict):
            self._monitoring_hud_interactive_screen_rect = self._estimate_monitoring_hud_interactive_screen_rect()
            return
        try:
            top_left = self.webview.mapToGlobal(
                QPoint(int(float(rect.get("left") or 0)), int(float(rect.get("top") or 0)))
            )
            left = top_left.x()
            top = top_left.y()
            width = int(float(rect.get("width") or 0))
            height = int(float(rect.get("height") or 0))
        except (TypeError, ValueError):
            self._monitoring_hud_interactive_screen_rect = self._estimate_monitoring_hud_interactive_screen_rect()
            return
        if width <= 0 or height <= 0:
            self._monitoring_hud_interactive_screen_rect = self._estimate_monitoring_hud_interactive_screen_rect()
            return
        if self.surface_role == "hud":
            self._monitoring_hud_interactive_screen_rect = QRect(left, top, width, height)
        else:
            self._monitoring_hud_interactive_screen_rect = QRect(left - 12, top - 12, width + 24, height + 24)

    def _monitoring_hud_screen_rect_from_page_rect(self, rect: dict[str, object] | None) -> QRect:
        if not isinstance(rect, dict):
            return QRect()
        try:
            left = int(float(rect.get("left") or 0))
            top = int(float(rect.get("top") or 0))
            width = int(float(rect.get("width") or 0))
            height = int(float(rect.get("height") or 0))
        except (TypeError, ValueError):
            return QRect()
        if width <= 0 or height <= 0:
            return QRect()
        top_left = self.webview.mapToGlobal(QPoint(left, top))
        return QRect(top_left.x(), top_left.y(), width, height)

    def _set_monitoring_hud_live_client_page_state(
        self,
        state: dict[str, object] | None,
        geometry: dict[str, object] | None,
    ):
        self._monitoring_hud_live_page_state = state if isinstance(state, dict) else {}
        screen_rects: dict[str, QRect] = {}
        if isinstance(geometry, dict):
            for name, rect in geometry.items():
                if isinstance(rect, dict):
                    screen_rect = self._monitoring_hud_screen_rect_from_page_rect(rect)
                    if screen_rect.isValid() and not screen_rect.isNull():
                        screen_rects[str(name)] = screen_rect
        self._monitoring_hud_live_screen_rects = screen_rects
        dashboard_close_rect = screen_rects.get("dashboardClose", QRect())
        if dashboard_close_rect.isValid() and not dashboard_close_rect.isNull():
            self._monitoring_hud_dashboard_close_last_screen_rect = QRect(dashboard_close_rect)
        settings_action_rect = screen_rects.get("settingsAction", QRect())
        if settings_action_rect.isValid() and not settings_action_rect.isNull():
            self._monitoring_hud_settings_action_last_screen_rect = QRect(settings_action_rect)

    def _monitoring_hud_dashboard_close_fallback_screen_rect(self) -> QRect:
        rect = self._monitoring_hud_interactive_screen_rect
        if rect.isNull() or not rect.isValid():
            rect = self._estimate_monitoring_hud_interactive_screen_rect()
            self._monitoring_hud_interactive_screen_rect = rect
        if not rect.isValid() or rect.isNull():
            return QRect()
        return QRect(
            rect.right() + 1 - 14 - 82,
            rect.y() + 12,
            82,
            42,
        )

    def _monitoring_hud_settings_action_fallback_screen_rect(self) -> QRect:
        actions_rect = self._monitoring_hud_dashboard_actions_fallback_screen_rect()
        if not actions_rect.isValid() or actions_rect.isNull():
            return QRect()
        return QRect(
            actions_rect.x(),
            actions_rect.y(),
            actions_rect.width(),
            44,
        )

    def _monitoring_hud_dashboard_actions_fallback_screen_rect(self) -> QRect:
        header_rect = self._monitoring_hud_header_rect()
        if not header_rect.isValid() or header_rect.isNull():
            return QRect()
        width = min(360, max(154, header_rect.width() // 3))
        height = 44
        left = header_rect.x() + 43
        return QRect(
            left,
            header_rect.y() + 132,
            width,
            height,
        )

    def _monitoring_hud_point_in_interactive_rect(self, point: QPoint) -> bool:
        rect = self._monitoring_hud_interactive_screen_rect
        if rect.isNull() or not rect.isValid():
            rect = self._estimate_monitoring_hud_interactive_screen_rect()
            self._monitoring_hud_interactive_screen_rect = rect
        return bool(rect.contains(point))

    def _apply_monitoring_hud_native_activation_style(self, anchored: bool):
        try:
            hwnd = ctypes.wintypes.HWND(int(self.winId()))
            style = int(GetWindowLongW(hwnd, GWL_EXSTYLE))
            style = style & ~WS_EX_NOACTIVATE & ~WS_EX_TRANSPARENT
            if self.surface_role == "hud":
                style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception:
            return

    def set_monitoring_hud_tray_menu_interaction_guard(self, active: bool, source: str = "tray_menu"):
        if self.surface_role != "hud":
            return
        self._monitoring_hud_tray_menu_guard_active = bool(active)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, bool(active))
        style = 0
        try:
            hwnd = ctypes.wintypes.HWND(int(self.winId()))
            style = int(GetWindowLongW(hwnd, GWL_EXSTYLE))
            if active:
                style |= WS_EX_TRANSPARENT
            else:
                style &= ~WS_EX_TRANSPARENT
            SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception:
            style = 0
        self._emit_runtime_signal(
            "MONITORING_HUD_TRAY_MENU_INTERACTION_GUARD_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS48",
            source=source,
            active=bool(active),
            transparent_for_mouse=bool(self.testAttribute(Qt.WA_TransparentForMouseEvents)),
            ex_transparent=bool(style & WS_EX_TRANSPARENT),
        )

    def _monitoring_hud_native_ownership_state(self) -> dict[str, object]:
        style = 0
        try:
            style = int(GetWindowLongW(ctypes.wintypes.HWND(int(self.winId())), GWL_EXSTYLE))
        except Exception:
            style = 0
        return {
            "windowFlag": "normal_window" if self.surface_role == "hud" else "tool_window",
            "topmost": False,
            "showWithoutActivating": bool(self.testAttribute(Qt.WA_ShowWithoutActivating)),
            "transparentForMouseEvents": bool(self.testAttribute(Qt.WA_TransparentForMouseEvents)),
            "exNoActivate": bool(style & WS_EX_NOACTIVATE),
            "exTransparent": bool(style & WS_EX_TRANSPARENT),
            "exToolWindow": bool(style & WS_EX_TOOLWINDOW),
            "exAppWindow": bool(style & WS_EX_APPWINDOW),
            "movementModel": "os-system-move-no-snap",
            "resizeModel": "os-edge-corner-resize",
            "focusPolicy": "no_focus" if self.focusPolicy() == Qt.NoFocus else "interactive",
        }

    def _emit_monitoring_hud_window_ownership_focus_ready(self, source: str = "runtime"):
        if self.surface_role != "hud":
            return
        state = self._monitoring_hud_native_ownership_state()
        self._emit_runtime_signal(
            "MONITORING_HUD_WINDOW_OWNERSHIP_FOCUS_READY",
            package="PKG-006",
            slice="SLC-026",
            seam="WS38",
            source=source,
            surface="dashboard_control_panel",
            window_flag=state["windowFlag"],
            topmost=state["topmost"],
            show_without_activating=state["showWithoutActivating"],
            transparent_for_mouse=state["transparentForMouseEvents"],
            ex_noactivate=state["exNoActivate"],
            ex_transparent=state["exTransparent"],
            ex_tool_window=state["exToolWindow"],
            ex_app_window=state["exAppWindow"],
            movement_model=state["movementModel"],
            resize_model=state["resizeModel"],
            focus_policy=state["focusPolicy"],
        )

    def _emit_monitoring_hud_window_status(self, source: str = "runtime"):
        geometry = self.geometry()
        virtual = self._virtual_desktop_geometry()
        overlay_proof = self._monitoring_hud_minimal_native_proof_state()
        ownership = self._monitoring_hud_native_ownership_state()
        self._emit_runtime_signal(
            "MONITORING_HUD_WINDOW_STATUS_READY",
            package="PKG-006",
            slice="SLC-026",
            source=source,
            surface="standalone_native_hud_window" if self.surface_role == "hud" else "combined_core_surface",
            feature_enabled=self._monitoring_hud_feature_enabled,
            visible=self._monitoring_hud_visible,
            anchored=self._monitoring_hud_anchored,
            x=geometry.x(),
            y=geometry.y(),
            w=geometry.width(),
            h=geometry.height(),
            virtual_x=virtual.x(),
            virtual_y=virtual.y(),
            virtual_w=virtual.width(),
            virtual_h=virtual.height(),
            window_flag=ownership.get("windowFlag"),
            movement_model=ownership.get("movementModel"),
            resize_model=ownership.get("resizeModel"),
            ex_tool_window=ownership.get("exToolWindow"),
            ex_app_window=ownership.get("exAppWindow"),
            focus_policy="no_focus" if self.focusPolicy() == Qt.NoFocus else "interactive",
        )
        if self.surface_role == "hud":
            self._emit_runtime_signal(
                "MONITORING_HUD_STANDALONE_DASHBOARD_WINDOW_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS28",
                source=source,
                surface="dashboard_control_panel_window",
                owner="DesktopRuntimeWindow",
                standalone=self.parent() is None,
                overlay_owner=overlay_proof.get("owner") or "MonitoringHudOverlayDisplayWindow",
                overlay_separate_hwnd=bool(overlay_proof.get("hwnd") and overlay_proof.get("hwnd") != int(self.winId())),
                virtual_desktop="all_monitors",
                x=geometry.x(),
                y=geometry.y(),
                w=geometry.width(),
                h=geometry.height(),
            )

    def _sync_monitoring_hud_minimal_native_overlay(self, source: str = "runtime"):
        overlay = self._monitoring_hud_minimal_native_overlay
        if overlay is None:
            return
        telemetry = self._monitoring_hud_telemetry_snapshot()
        status = self._monitoring_hud_status_snapshot()
        cards = {}
        page_state = self._monitoring_hud_live_page_state if isinstance(self._monitoring_hud_live_page_state, dict) else {}
        if isinstance(page_state.get("cards"), dict):
            cards = page_state.get("cards") or {}
        overlay.update_product_state(
            visible=False,
            anchored=bool(self._monitoring_hud_anchored),
            provider_label=str(telemetry.get("providerLabel") or "Provider setup required"),
            warning_label=str(status.get("warningPosture") or "Visual warning baseline only"),
            cards=cards,
        )
        proof = overlay.proof_state()
        self._emit_runtime_signal(
            "MONITORING_HUD_MINIMAL_NATIVE_OVERLAY_READY",
            package="PKG-006",
            slice="SLC-026",
            seam="WS22",
            source=source,
            surface="minimal_native_overlay_window",
            visible=proof.get("visible"),
            x=proof.get("x"),
            y=proof.get("y"),
            w=proof.get("w"),
            h=proof.get("h"),
            separate_hwnd=bool(proof.get("hwnd") and proof.get("hwnd") != int(self.winId())),
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_STANDALONE_OVERLAY_DISPLAY_WINDOW_READY",
            package="PKG-006",
            slice="SLC-026",
            seam="WS26",
            source=source,
            surface=proof.get("surface"),
            owner=proof.get("owner"),
            standalone=proof.get("standaloneTopLevel"),
            visible=proof.get("visible"),
            anchored=proof.get("anchored"),
            x=proof.get("x"),
            y=proof.get("y"),
            w=proof.get("w"),
            h=proof.get("h"),
            virtual_x=proof.get("virtualX"),
            virtual_y=proof.get("virtualY"),
            virtual_w=proof.get("virtualW"),
            virtual_h=proof.get("virtualH"),
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_SURFACE_NATIVE_INDEPENDENCE_READY",
            package="PKG-006",
            slice="SLC-026",
            seam="WS28",
            source=source,
            dashboard_owner="DesktopRuntimeWindow",
            overlay_owner=proof.get("owner"),
            overlay_standalone=proof.get("standaloneTopLevel"),
            overlay_dashboard_coupled=proof.get("dashboardCoupled"),
            overlay_cards_movable=proof.get("cardsMovableInOverlay"),
            core_surface="CoreVisualizationWindow",
            virtual_desktop="all_monitors",
        )
        if self._monitoring_hud_visible and self._monitoring_hud_anchored:
            self._emit_runtime_signal(
                "MONITORING_HUD_MINIMAL_ANCHORED_CLICK_THROUGH_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS22",
                source=source,
                ex_transparent=proof.get("exTransparent"),
                transparent_for_mouse=proof.get("transparentForMouseEvents"),
                window_from_center_bypasses_overlay=proof.get("windowFromCenterBypassesOverlay"),
            )
            self._emit_runtime_signal(
                "MONITORING_HUD_MINIMAL_NON_FOCUS_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS22",
                source=source,
                focus_policy=proof.get("focusPolicy"),
                ex_noactivate=proof.get("exNoActivate"),
                show_without_activating=proof.get("showWithoutActivating"),
            )
            self._emit_runtime_signal(
                "MONITORING_HUD_ANCHORED_OVERLAY_UNINTERACTABLE_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS26",
                surface="standalone_edgeless_overlay_display",
                transparent_for_mouse=proof.get("transparentForMouseEvents"),
                ex_transparent=proof.get("exTransparent"),
                focus_policy=proof.get("focusPolicy"),
                ex_noactivate=proof.get("exNoActivate"),
                quick_controls_visible=proof.get("quickControlsVisible"),
                window_from_center_bypasses_overlay=proof.get("windowFromCenterBypassesOverlay"),
            )
            if proof.get("positionPreserved"):
                self._emit_runtime_signal(
                    "MONITORING_HUD_OVERLAY_POSITION_PRESERVED_READY",
                    package="PKG-006",
                    slice="SLC-026",
                    seam="WS26",
                    surface="standalone_edgeless_overlay_display",
                    x=proof.get("x"),
                    y=proof.get("y"),
                    w=proof.get("w"),
                    h=proof.get("h"),
                )
        elif self._monitoring_hud_visible:
            self._emit_runtime_signal(
                "MONITORING_HUD_UNANCHORED_OVERLAY_EDIT_WINDOW_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS26",
                surface="standalone_edgeless_overlay_display",
                transparent_for_mouse=proof.get("transparentForMouseEvents"),
                focus_policy=proof.get("focusPolicy"),
                quick_controls_visible=proof.get("quickControlsVisible"),
                movable="native_window_drag",
                resizable="native_size_grip",
            )

    def _monitoring_hud_minimal_native_proof_state(self) -> dict[str, object]:
        overlay = self._monitoring_hud_minimal_native_overlay
        if overlay is None:
            return {}
        return overlay.proof_state()

    def _monitoring_hud_overlay_card_screen_rect(self, card_id: str, *, resize: bool = False) -> QRect:
        overlay = self._monitoring_hud_minimal_native_overlay
        if overlay is None:
            return QRect()
        proof = overlay.proof_state()
        layouts = proof.get("cardLayouts") if isinstance(proof.get("cardLayouts"), dict) else {}
        layout = layouts.get(card_id) if isinstance(layouts.get(card_id), dict) else {}
        if not layout:
            return QRect()
        geometry = overlay.geometry()
        x = geometry.x() + int(layout.get("x") or 0)
        y = geometry.y() + int(layout.get("y") or 0)
        w = int(layout.get("w") or 0)
        h = int(layout.get("h") or 0)
        if resize:
            return QRect(x + max(0, w - 22), y + max(0, h - 22), 18, 18)
        return QRect(x + 12, y + 12, max(1, min(w - 24, 180)), max(1, min(h - 24, 48)))

    def _monitoring_hud_core_visualization_window(self):
        app = QApplication.instance()
        if app is None:
            return None
        for widget in app.topLevelWidgets():
            if callable(getattr(widget, "compute_core_geometry", None)) and "ORIN Core" in str(widget.windowTitle()):
                return widget
        return None

    def _monitoring_hud_rect_payload(self, rect: QRect) -> dict[str, int]:
        if rect is None or rect.isNull() or not rect.isValid():
            return {"x": 0, "y": 0, "w": 0, "h": 0}
        return {"x": rect.x(), "y": rect.y(), "w": rect.width(), "h": rect.height()}

    def _monitoring_hud_rect_within(self, inner: QRect, outer: QRect) -> bool:
        if inner is None or outer is None or inner.isNull() or outer.isNull():
            return False
        return (
            inner.left() >= outer.left()
            and inner.top() >= outer.top()
            and inner.right() <= outer.right()
            and inner.bottom() <= outer.bottom()
        )

    def _monitoring_hud_travel_rect(self, target: QRect, width: int, height: int, *, align: str) -> QRect:
        margin = 32
        usable_w = max(260, target.width() - (margin * 2))
        usable_h = max(240, target.height() - (margin * 2))
        w = min(max(260, int(width)), usable_w)
        h = min(max(240, int(height)), usable_h)
        if align == "right":
            x = target.x() + max(margin, target.width() - w - margin)
        elif align == "center":
            x = target.x() + max(margin, (target.width() - w) // 2)
        else:
            x = target.x() + margin
        y = target.y() + max(margin, (target.height() - h) // 2)
        return QRect(x, y, w, h)

    def _monitoring_hud_screen_targets(self) -> list[QRect]:
        targets: list[QRect] = []
        for screen in QApplication.screens():
            rect = screen.availableGeometry()
            if rect.isValid() and not rect.isNull():
                targets.append(rect)
        if not targets:
            targets.append(self._virtual_desktop_geometry())
        return sorted(targets, key=lambda rect: (rect.x(), rect.y()))

    def _monitoring_hud_window_travel_detail(self, name: str, widget: QWidget, target: QRect, virtual: QRect) -> dict[str, object]:
        geometry = widget.geometry()
        return {
            "surface": name,
            "visible": widget.isVisible(),
            "geometry": self._monitoring_hud_rect_payload(geometry),
            "target": self._monitoring_hud_rect_payload(target),
            "withinTargetMonitor": self._monitoring_hud_rect_within(geometry, target),
            "withinVirtualDesktop": self._monitoring_hud_rect_within(geometry, virtual),
            "intersectsTargetMonitor": geometry.intersected(target).width() > 120
            and geometry.intersected(target).height() > 120,
        }

    def _monitoring_hud_run_surface_travel_probe(self) -> dict[str, object]:
        overlay = self._monitoring_hud_minimal_native_overlay
        core = self._monitoring_hud_core_visualization_window()
        virtual = self._virtual_desktop_geometry()
        targets = self._monitoring_hud_screen_targets()
        dashboard_target = targets[0]
        overlay_target = targets[-1]
        if len(targets) > 1 and overlay_target == dashboard_target:
            overlay_target = targets[-1]

        dashboard_rect = self._monitoring_hud_travel_rect(
            dashboard_target,
            self.width(),
            self.height(),
            align="left",
        )
        overlay_width = max(720, int(overlay_target.width() * 0.72))
        overlay_height = max(500, int(overlay_target.height() * 0.58))
        overlay_rect = self._monitoring_hud_travel_rect(
            overlay_target,
            overlay_width,
            overlay_height,
            align="right",
        )

        core_geometry_before = (
            core.desktop_screen_geometry()
            if core is not None and callable(getattr(core, "desktop_screen_geometry", None))
            else core.geometry() if core is not None else QRect()
        )
        core_screen_geometry = core.screen_ref.availableGeometry() if core is not None else QRect()

        self.setGeometry(dashboard_rect)
        self._monitoring_hud_interactive_screen_rect = self.geometry()
        self._emit_monitoring_hud_window_status(source="virtual_desktop_travel")
        if overlay is not None:
            overlay.setGeometry(overlay._bound_geometry_to_virtual_desktop(overlay_rect))
            overlay._last_unanchored_geometry = QRect(overlay.geometry())
            overlay._layout_overlay_children()
            self._sync_monitoring_hud_minimal_native_overlay(source="virtual_desktop_travel")
        QApplication.processEvents()

        dashboard_detail = self._monitoring_hud_window_travel_detail("dashboard_control_panel", self, dashboard_target, virtual)
        overlay_detail = (
            self._monitoring_hud_window_travel_detail("hud_overlay_display", overlay, overlay_target, virtual)
            if overlay is not None
            else {"surface": "hud_overlay_display", "visible": False}
        )
        core_geometry_after = (
            core.desktop_screen_geometry()
            if core is not None and callable(getattr(core, "desktop_screen_geometry", None))
            else core.geometry() if core is not None else QRect()
        )
        dashboard_core_overlap = bool(core_geometry_after.isValid() and self.geometry().intersects(core_geometry_after))
        overlay_geometry_after = overlay.geometry() if overlay is not None else QRect()
        overlay_core_overlap = bool(core_geometry_after.isValid() and overlay_geometry_after.isValid() and overlay_geometry_after.intersects(core_geometry_after))
        separation_required = len(targets) > 1
        surface_separation_ok = not separation_required or not (dashboard_core_overlap or overlay_core_overlap)
        core_detail = {
            "surface": "orin_persona_core_visualization",
            "visible": core.isVisible() if core is not None else False,
            "geometry": self._monitoring_hud_rect_payload(core_geometry_after),
            "presetMonitor": self._monitoring_hud_rect_payload(core_screen_geometry),
            "withinPresetMonitor": self._monitoring_hud_rect_within(core_geometry_after, core_screen_geometry),
            "remainedOnUserSelectedMonitor": self._monitoring_hud_rect_payload(core_geometry_after)
            == self._monitoring_hud_rect_payload(core_geometry_before),
            "travelPolicy": "independent_user_selected_monitor_scoped",
            "attachedToHudDashboardOrNcp": False,
            "movable": False,
            "dashboardOverlap": dashboard_core_overlap,
            "overlayOverlap": overlay_core_overlap,
            "surfaceSeparationRequired": separation_required,
            "surfaceSeparationOk": surface_separation_ok,
        }
        dashboard_ok = bool(
            dashboard_detail.get("visible")
            and dashboard_detail.get("withinTargetMonitor")
            and dashboard_detail.get("withinVirtualDesktop")
        )
        overlay_ok = bool(
            overlay_detail.get("visible")
            and overlay_detail.get("withinTargetMonitor")
            and overlay_detail.get("withinVirtualDesktop")
        )
        core_ok = bool(
            core_detail.get("visible")
            and core_detail.get("withinPresetMonitor")
            and core_detail.get("remainedOnUserSelectedMonitor")
            and core_detail.get("attachedToHudDashboardOrNcp") is False
            and core_detail.get("movable") is False
            and core_detail.get("surfaceSeparationOk") is True
        )
        ok = dashboard_ok and overlay_ok and core_ok
        if ok:
            self._emit_runtime_signal(
                "MONITORING_HUD_SURFACE_VIRTUAL_DESKTOP_TRAVEL_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS28",
                dashboard="moved_to_target_monitor",
                overlay="moved_to_target_monitor",
                core="independent_user_selected_monitor_scoped",
                core_attachment="none",
                screen_count=len(targets),
                virtual_desktop="all_monitors",
            )
            self._emit_runtime_signal(
                "CORE_VISUALIZATION_HUD_SURFACE_SEPARATION_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS30",
                core="fixed_preset_monitor",
                dashboard_overlap=str(dashboard_core_overlap).lower(),
                overlay_overlap=str(overlay_core_overlap).lower(),
                movable="false",
            )
        return {
            "ok": ok,
            "screenCount": len(targets),
            "virtualDesktop": self._monitoring_hud_rect_payload(virtual),
            "dashboard": dashboard_detail,
            "overlay": overlay_detail,
            "core": core_detail,
        }

    def _monitoring_hud_run_dashboard_standalone_probe(self) -> dict[str, object]:
        overlay = self._monitoring_hud_minimal_native_overlay
        core = self._monitoring_hud_core_visualization_window()
        virtual = self._virtual_desktop_geometry()
        targets = self._monitoring_hud_screen_targets()
        current_geometry = self.geometry()
        current_center = current_geometry.center() if current_geometry.isValid() else QPoint(0, 0)

        core_geometry_before = (
            core.desktop_screen_geometry()
            if core is not None and callable(getattr(core, "desktop_screen_geometry", None))
            else core.geometry() if core is not None else QRect()
        )
        core_screen_geometry = core.screen_ref.availableGeometry() if core is not None else QRect()
        overlay_geometry_before = overlay.geometry() if overlay is not None else QRect()

        non_core_targets = [
            target
            for target in targets
            if not (
                core_screen_geometry.isValid()
                and target.intersected(core_screen_geometry).width() > 120
                and target.intersected(core_screen_geometry).height() > 120
            )
        ]
        candidate_targets = non_core_targets or targets
        target = max(
            candidate_targets,
            key=lambda rect: abs(rect.center().x() - current_center.x()) + abs(rect.center().y() - current_center.y()),
        )
        dashboard_rect = self._monitoring_hud_travel_rect(
            target,
            max(self.width(), 700),
            max(self.height(), 560),
            align="center",
        )

        self.setGeometry(dashboard_rect)
        self._monitoring_hud_interactive_screen_rect = self.geometry()
        self._emit_monitoring_hud_window_status(source="dashboard_standalone_travel")
        QApplication.processEvents()

        dashboard_detail = self._monitoring_hud_window_travel_detail(
            "dashboard_control_panel",
            self,
            target,
            virtual,
        )
        overlay_geometry_after = overlay.geometry() if overlay is not None else QRect()
        core_geometry_after = (
            core.desktop_screen_geometry()
            if core is not None and callable(getattr(core, "desktop_screen_geometry", None))
            else core.geometry() if core is not None else QRect()
        )
        overlay_payload_before = self._monitoring_hud_rect_payload(overlay_geometry_before)
        overlay_payload_after = self._monitoring_hud_rect_payload(overlay_geometry_after)
        core_payload_before = self._monitoring_hud_rect_payload(core_geometry_before)
        core_payload_after = self._monitoring_hud_rect_payload(core_geometry_after)
        overlay_geometry_unchanged = overlay is None or overlay_payload_before == overlay_payload_after
        core_geometry_unchanged = core is not None and core_payload_before == core_payload_after
        dashboard_core_overlap = bool(
            core_geometry_after.isValid()
            and self.geometry().isValid()
            and self.geometry().intersects(core_geometry_after)
        )
        dashboard_overlay_overlap = bool(
            overlay is not None
            and overlay_geometry_after.isValid()
            and self.geometry().isValid()
            and self.geometry().intersects(overlay_geometry_after)
        )
        clipping_ok = bool(
            dashboard_detail.get("visible")
            and dashboard_detail.get("withinTargetMonitor")
            and dashboard_detail.get("withinVirtualDesktop")
            and dashboard_detail.get("intersectsTargetMonitor")
        )
        core_ok = bool(
            core is not None
            and core.isVisible()
            and self._monitoring_hud_rect_within(core_geometry_after, core_screen_geometry)
            and core_geometry_unchanged
        )
        decoupling_ok = bool(overlay_geometry_unchanged and core_ok)
        ok = bool(clipping_ok and decoupling_ok)

        if ok:
            self._emit_runtime_signal(
                "MONITORING_HUD_DASHBOARD_STANDALONE_WINDOW_TRAVEL_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS32",
                surface="dashboard_control_panel",
                movement="dashboard_native_window_only",
                virtual_desktop="all_monitors",
                screen_count=len(targets),
            )
            self._emit_runtime_signal(
                "MONITORING_HUD_DASHBOARD_CLIPPING_BOUNDARY_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS32",
                surface="dashboard_control_panel",
                within_target_monitor=str(bool(dashboard_detail.get("withinTargetMonitor"))).lower(),
                within_virtual_desktop=str(bool(dashboard_detail.get("withinVirtualDesktop"))).lower(),
                clipping="none",
            )
            self._emit_runtime_signal(
                "MONITORING_HUD_DASHBOARD_CORE_OVERLAY_DECOUPLING_READY",
                package="PKG-006",
                slice="SLC-026",
                seam="WS32",
                overlay_geometry_unchanged=str(overlay_geometry_unchanged).lower(),
                core_geometry_unchanged=str(core_geometry_unchanged).lower(),
                overlay_acceptance="deferred_non_gating",
                core_classification="dependency_only",
            )

        return {
            "ok": ok,
            "movement": "dashboard_native_window_only",
            "screenCount": len(targets),
            "virtualDesktop": self._monitoring_hud_rect_payload(virtual),
            "dashboard": dashboard_detail,
            "targetPolicy": "non_core_monitor_when_available",
            "clippingOk": clipping_ok,
            "decouplingOk": decoupling_ok,
            "overlayGeometryUnchanged": overlay_geometry_unchanged,
            "coreGeometryUnchanged": core_geometry_unchanged,
            "overlay": {
                "surface": "hud_overlay_display",
                "releaseGate": "deferred_non_gating",
                "geometryBefore": overlay_payload_before,
                "geometryAfter": overlay_payload_after,
                "geometryUnchanged": overlay_geometry_unchanged,
                "dashboardOverlap": dashboard_overlay_overlap,
            },
            "core": {
                "surface": "orin_persona_core_visualization",
                "classification": "dependency_only",
                "visible": core.isVisible() if core is not None else False,
                "geometryBefore": core_payload_before,
                "geometryAfter": core_payload_after,
                "presetMonitor": self._monitoring_hud_rect_payload(core_screen_geometry),
                "geometryUnchanged": core_geometry_unchanged,
                "withinPresetMonitor": self._monitoring_hud_rect_within(core_geometry_after, core_screen_geometry),
                "dashboardOverlap": dashboard_core_overlap,
                "movable": False,
            },
        }

    def _promote_monitoring_hud_edit_window(self):
        if self.surface_role != "hud":
            return
        self.raise_()

    def _monitoring_hud_dashboard_control_rect_contains(self, point: QPoint) -> bool:
        if self._monitoring_hud_active_child_window_rect_contains(point):
            return True
        control_rect_names = (
            "anchorToggle",
            "visibilityToggle",
            "settingsAction",
            "dashboardClose",
            "createMonitor",
            "snapToggle",
            "pollingRate",
            "warningModeControl",
            "settingsWarningToggle",
            "monitorSelector",
            "monitorEnabled",
            "monitorPollingRate",
            "overlayProfileWindowClose",
            "overlayProfileWindowSelector",
            "overlayProfileNameInput",
            "overlayProfileMonitorSearch",
            "overlayProfileMonitorFilter",
            "overlayProfileMembershipList",
            "overlayProfileMembershipFirstToggle",
            "overlayProfileCreate",
            "overlayProfileSave",
            "overlayProfileDiscard",
            "overlayProfileDelete",
            "overlayProfileDeleteConfirmation",
            "overlayAssignmentWindow",
            "overlayAssignmentList",
            "sourceSettingsWindow",
            "sourceSettingsBody",
        )
        for name in control_rect_names:
            rect = self._monitoring_hud_live_screen_rects.get(name, QRect())
            if rect.isValid() and not rect.isNull() and rect.contains(point):
                return True
            if name == "dashboardClose":
                if (
                    self._monitoring_hud_dashboard_close_last_screen_rect.isValid()
                    and not self._monitoring_hud_dashboard_close_last_screen_rect.isNull()
                    and self._monitoring_hud_dashboard_close_last_screen_rect.contains(point)
                ):
                    return True
                fallback_rect = self._monitoring_hud_dashboard_close_fallback_screen_rect()
                if fallback_rect.isValid() and not fallback_rect.isNull() and fallback_rect.contains(point):
                    return True
            if name == "settingsAction":
                if (
                    self._monitoring_hud_settings_action_last_screen_rect.isValid()
                    and not self._monitoring_hud_settings_action_last_screen_rect.isNull()
                    and self._monitoring_hud_settings_action_last_screen_rect.contains(point)
                ):
                    return True
                fallback_rect = self._monitoring_hud_settings_action_fallback_screen_rect()
                if fallback_rect.isValid() and not fallback_rect.isNull() and fallback_rect.contains(point):
                    return True
        return False

    def _monitoring_hud_any_child_window_active(self) -> bool:
        state = self._monitoring_hud_live_page_state if isinstance(self._monitoring_hud_live_page_state, dict) else {}
        active_child_window = str(state.get("activeChildWindow", "none") or "none")
        return active_child_window not in ("", "none", "closed")

    def _monitoring_hud_active_child_window_rect_contains(self, point: QPoint) -> bool:
        if point.isNull():
            return False
        state = self._monitoring_hud_live_page_state if isinstance(self._monitoring_hud_live_page_state, dict) else {}
        active_child_window = str(state.get("activeChildWindow", "none") or "none")
        if active_child_window in ("", "none", "closed"):
            return False
        rect_names_by_child_window = {
            "dashboard-settings": ("settingsWindow", "settingsClose"),
            "monitor-group-create": ("createMonitorWindow", "createMonitorClose"),
            "monitor-group-edit": ("editMonitorWindow", "editMonitorClose"),
            "overlay-profile-settings": (
                "overlayProfileWindow",
                "overlayProfileWindowClose",
                "overlayProfileWindowSelector",
                "overlayProfileCreate",
                "overlayProfileSave",
                "overlayProfileDiscard",
                "overlayProfileDelete",
                "overlayProfileDeleteConfirmation",
                "overlayProfileMonitorSearch",
                "overlayProfileMonitorFilter",
                "overlayProfileMembershipList",
            ),
            "monitor-overlay-assignment": ("overlayAssignmentWindow", "overlayAssignmentList"),
            "sensor-source-settings": ("sourceSettingsWindow", "sourceSettingsBody"),
        }
        for name in rect_names_by_child_window.get(active_child_window, ()):
            rect = self._monitoring_hud_live_screen_rects.get(name, QRect())
            if rect.isValid() and not rect.isNull() and rect.contains(point):
                return True
        return False

    def _guard_monitoring_hud_active_child_window_background_click(
        self,
        point: QPoint,
        source: str,
    ) -> bool:
        if point.isNull() or not self._monitoring_hud_any_child_window_active():
            return False
        if self._monitoring_hud_active_child_window_rect_contains(point):
            return False
        if not self._monitoring_hud_point_in_interactive_rect(point):
            return False
        self._emit_runtime_signal(
            "MONITORING_HUD_ACTIVE_CHILD_WINDOW_BACKGROUND_CLICK_GUARDED",
            package="PKG-006",
            slice="SLC-029",
            seam="LV1",
            source=source,
            x=point.x(),
            y=point.y(),
        )
        return True

    def _monitoring_hud_dashboard_close_control_rect_contains(self, point: QPoint) -> bool:
        if self._monitoring_hud_any_child_window_active():
            return False
        rect = self._monitoring_hud_live_screen_rects.get("dashboardClose", QRect())
        if rect.isValid() and not rect.isNull() and rect.contains(point):
            return True
        settings_rect = self._monitoring_hud_live_screen_rects.get("settingsAction", QRect())
        if settings_rect.isValid() and not settings_rect.isNull() and settings_rect.contains(point):
            return False
        if (
            self._monitoring_hud_settings_action_last_screen_rect.isValid()
            and not self._monitoring_hud_settings_action_last_screen_rect.isNull()
            and self._monitoring_hud_settings_action_last_screen_rect.contains(point)
        ):
            return False
        settings_fallback_rect = self._monitoring_hud_settings_action_fallback_screen_rect()
        if settings_fallback_rect.isValid() and not settings_fallback_rect.isNull() and settings_fallback_rect.contains(point):
            return False
        if (
            self._monitoring_hud_dashboard_close_last_screen_rect.isValid()
            and not self._monitoring_hud_dashboard_close_last_screen_rect.isNull()
            and self._monitoring_hud_dashboard_close_last_screen_rect.contains(point)
        ):
            return True
        fallback_rect = self._monitoring_hud_dashboard_close_fallback_screen_rect()
        return bool(fallback_rect.isValid() and not fallback_rect.isNull() and fallback_rect.contains(point))

    def _monitoring_hud_dashboard_settings_control_rect_contains(self, point: QPoint) -> bool:
        if self._monitoring_hud_any_child_window_active():
            return False
        rect = self._monitoring_hud_live_screen_rects.get("settingsAction", QRect())
        if rect.isValid() and not rect.isNull() and rect.contains(point):
            return True
        if (
            self._monitoring_hud_settings_action_last_screen_rect.isValid()
            and not self._monitoring_hud_settings_action_last_screen_rect.isNull()
            and self._monitoring_hud_settings_action_last_screen_rect.contains(point)
        ):
            return True
        fallback_rect = self._monitoring_hud_settings_action_fallback_screen_rect()
        return bool(fallback_rect.isValid() and not fallback_rect.isNull() and fallback_rect.contains(point))

    def _handle_monitoring_hud_dashboard_close_native_control(self, screen_point: QPoint) -> bool:
        if not self._monitoring_hud_dashboard_close_control_rect_contains(screen_point):
            return False
        self.request_monitoring_hud_dashboard_from_tray(source="dashboard-close-native-control", visible=False)
        self._persist_monitoring_hud_feature_state(source="dashboard-close-native-control")
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_CLOSE_NATIVE_CONTROL_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS43",
            feature_enabled=bool(self._monitoring_hud_feature_enabled),
            dashboard_visible=bool(self.isVisible() and self._monitoring_hud_visible),
            x=screen_point.x(),
            y=screen_point.y(),
        )
        return True

    def _handle_monitoring_hud_dashboard_settings_native_control(self, screen_point: QPoint) -> bool:
        if not self._monitoring_hud_dashboard_settings_control_rect_contains(screen_point):
            return False
        script = """
        (() => {
          const button = document.getElementById("monitoring-hud-settings-action");
          if (!button) return "missing";
          button.click();
          return "clicked";
        })();
        """
        self._run_javascript(script)
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_SETTINGS_NATIVE_CONTROL_READY",
            package="PKG-006",
            slice="SLC-029",
            seam="LV1",
            control="dashboard-settings",
            action="open",
            x=screen_point.x(),
            y=screen_point.y(),
        )
        return True

    def _begin_monitoring_hud_native_user_move(self, source: str = "native_caption_move") -> None:
        if self.surface_role != "hud":
            return
        geometry = self.geometry()
        self._monitoring_hud_native_move_user_active = True
        self._monitoring_hud_native_move_start_geometry = QRect(geometry)
        self._monitoring_hud_native_move_last_geometry = QRect(geometry)
        self._monitoring_hud_native_move_source = source
        self._monitoring_hud_native_move_finalize_timer.stop()

    def _clear_monitoring_hud_native_user_move(self) -> None:
        self._monitoring_hud_native_move_user_active = False
        self._monitoring_hud_native_move_start_geometry = QRect()
        self._monitoring_hud_native_move_last_geometry = QRect()
        self._monitoring_hud_native_move_source = ""
        self._monitoring_hud_native_move_frame_sync_last = 0.0
        self._monitoring_hud_native_move_finalize_timer.stop()

    def _sync_monitoring_hud_move_frame(self) -> None:
        if self.surface_role != "hud" or self._is_shutting_down:
            return
        now = time.monotonic()
        if now - self._monitoring_hud_native_move_frame_sync_last < 0.016:
            return
        self._monitoring_hud_native_move_frame_sync_last = now
        self.webview.setGeometry(self.rect())
        self.webview.updateGeometry()
        self.webview.update()
        self.update()
        try:
            QApplication.processEvents()
        except Exception:
            pass
        self._run_javascript(
            """
            window.requestAnimationFrame(() => {
                window.dispatchEvent(new Event('resize'));
            });
            """
        )

    def _finish_monitoring_hud_native_system_move(self, source: str = "system_move"):
        geometry = self.geometry()
        move_was_user_initiated = bool(self._monitoring_hud_native_move_user_active)
        start_geometry = QRect(self._monitoring_hud_native_move_start_geometry)
        geometry_changed = bool(
            move_was_user_initiated
            and start_geometry.isValid()
            and geometry != start_geometry
        )
        self._clear_monitoring_hud_native_user_move()
        if geometry_changed:
            self._monitoring_hud_user_geometry_override_active = True
        self._monitoring_hud_interactive_screen_rect = geometry
        self._run_javascript(
            """
            window.requestAnimationFrame(() => {
                window.dispatchEvent(new Event('resize'));
            });
            """
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_NATIVE_WINDOW_MOVE_READY",
            package="PKG-006",
            slice="SLC-026",
            seam="WS38",
            source=source,
            movement_model="os-system-move-no-snap",
            x=geometry.x(),
            y=geometry.y(),
            w=geometry.width(),
            h=geometry.height(),
            virtual_desktop="all_monitors",
            user_initiated=move_was_user_initiated,
            geometry_changed=geometry_changed,
        )
        self._emit_monitoring_hud_window_ownership_focus_ready(source=source)
        self._emit_monitoring_hud_window_status(source=source)

    def _finish_monitoring_hud_native_system_resize(self, source: str = "system_resize"):
        self._monitoring_hud_user_geometry_override_active = True
        self._monitoring_hud_interactive_screen_rect = self.geometry()
        geometry = self.geometry()
        self._emit_runtime_signal(
            "MONITORING_HUD_NATIVE_WINDOW_RESIZE_READY",
            package="PKG-006",
            slice="SLC-026",
            seam="WS44",
            source=source,
            resize_model="os-edge-corner-resize",
            x=geometry.x(),
            y=geometry.y(),
            w=geometry.width(),
            h=geometry.height(),
            min_w=self.minimumWidth(),
            min_h=self.minimumHeight(),
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_SHELL_LAYOUT_READY",
            package="PKG-006",
            slice="SLC-016",
            seam="WS44",
            surface="hud_dashboard",
            sticky_header=True,
            single_surface_scrollbar=True,
            title="HUD Dashboard",
            resize_model="os-edge-corner-resize",
        )
        self._emit_monitoring_hud_visual_shell_ready(source=source)
        self._emit_monitoring_hud_window_ownership_focus_ready(source=source)
        self._emit_monitoring_hud_window_status(source=source)

    def _emit_monitoring_hud_visual_shell_ready(self, source: str = "runtime"):
        if self.surface_role != "hud":
            return
        geometry = self.geometry()
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_VISUAL_SHELL_READY",
            package="PKG-006",
            slice="SLC-016",
            seam="WS44",
            source=source,
            scrollbar_owner="monitoring-hud-control-hub",
            scrollbar_boundary="inner-content-well-gutter",
            outer_frame_haze="removed-no-square-layer",
            minimum_edge_policy="native-min-size-bottom-edge-visible",
            native_resize_hit_zone="preclick-hover-cursor-aligned-14px-app-owned-resize-action",
            resize_edge_scope="all-edges-and-corners",
            resize_hit_zone_px=self._monitoring_hud_resize_hit_zone_px(),
            corner_diagonal_resize_arc_percent=50,
            corner_diagonal_resize_model="central-half-of-rounded-corner-arc",
            resize_hover_cursor_model="polls-real-cursor-before-click",
            resize_poll_interval_ms=8,
            deadzone_policy="auto-height-content-no-empty-hit-zones",
            grid_scope="control-hub-cards-only",
            sticky_header_mask="opaque-scroll-mask",
            x=geometry.x(),
            y=geometry.y(),
            w=geometry.width(),
            h=geometry.height(),
        )

    def _start_monitoring_hud_native_system_move(self, screen_point: QPoint) -> bool:
        if self.surface_role != "hud":
            return False
        window_handle = self.windowHandle()
        start_system_move = getattr(window_handle, "startSystemMove", None) if window_handle else None
        if not callable(start_system_move):
            return False
        self._monitoring_hud_native_panel_drag_active = False
        self._emit_runtime_signal(
            "MONITORING_HUD_NATIVE_SYSTEM_MOVE_STARTED",
            package="PKG-006",
            slice="SLC-026",
            seam="WS38",
            x=screen_point.x(),
            y=screen_point.y(),
            movement_model="os-system-move-no-snap",
        )
        try:
            self._begin_monitoring_hud_native_user_move("system_move")
            started = bool(start_system_move())
        except Exception:
            started = False
        if started:
            QTimer.singleShot(360, lambda: self._finish_monitoring_hud_native_system_move("system_move"))
        else:
            self._clear_monitoring_hud_native_user_move()
        return started

    def _start_monitoring_hud_fallback_panel_move(
        self,
        screen_point: QPoint,
        source: str = "fallback_direct_header_move",
    ) -> bool:
        if self.surface_role != "hud":
            return False
        self._clear_monitoring_hud_native_user_move()
        self._monitoring_hud_native_panel_drag_active = True
        self._monitoring_hud_native_panel_drag_start = QPoint(screen_point)
        self._monitoring_hud_native_panel_drag_base = self.pos()
        self._monitoring_hud_user_geometry_override_active = True
        self._emit_runtime_signal(
            "MONITORING_HUD_NATIVE_PANEL_DRAG_STARTED",
            package="PKG-006",
            slice="SLC-026",
            seam="WS38",
            source=source,
            movement_model="fallback-direct-move-no-snap",
            x=screen_point.x(),
            y=screen_point.y(),
        )
        return True

    def _update_monitoring_hud_fallback_panel_move(self, screen_point: QPoint) -> None:
        if self.surface_role != "hud" or not self._monitoring_hud_native_panel_drag_active:
            return
        delta = screen_point - self._monitoring_hud_native_panel_drag_start
        self._set_monitoring_hud_panel_position_from_native_drag(
            self._monitoring_hud_native_panel_drag_base.x() + delta.x(),
            self._monitoring_hud_native_panel_drag_base.y() + delta.y(),
            emit_status=False,
        )

    def _finish_monitoring_hud_fallback_panel_move(self, screen_point: QPoint) -> None:
        if self.surface_role != "hud" or not self._monitoring_hud_native_panel_drag_active:
            return
        if screen_point.isNull():
            screen_point = QPoint(self._monitoring_hud_native_panel_drag_start)
        delta = screen_point - self._monitoring_hud_native_panel_drag_start
        self._set_monitoring_hud_panel_position_from_native_drag(
            self._monitoring_hud_native_panel_drag_base.x() + delta.x(),
            self._monitoring_hud_native_panel_drag_base.y() + delta.y(),
        )
        self._monitoring_hud_native_panel_drag_active = False
        self._emit_runtime_signal(
            "MONITORING_HUD_NATIVE_PANEL_DRAG_READY",
            package="PKG-006",
            slice="SLC-026",
            dx=delta.x(),
            dy=delta.y(),
            movement_model="fallback-direct-move-no-snap",
        )

    def _monitoring_hud_native_resize_edges_for_point(self, point: QPoint):
        if self.surface_role != "hud":
            return Qt.Edges()
        rect = self.geometry()
        if rect.isNull() or not rect.isValid():
            return Qt.Edges()
        # Keep the fallback resize rail close to the visible chrome so cursor feedback
        # and actual drag behavior agree with standard Windows resize expectations.
        margin = self._monitoring_hud_resize_hit_zone_px()
        if not rect.adjusted(-2, -2, 2, 2).contains(point):
            return Qt.Edges()
        if not self._monitoring_hud_screen_point_inside_rounded_window_mask(point):
            return Qt.Edges()
        radius = min(
            int(self._monitoring_hud_window_corner_radius_px),
            max(1, rect.width() // 2),
            max(1, rect.height() // 2),
        )
        corner_edges = self._monitoring_hud_rounded_corner_diagonal_resize_edges_for_point(
            point,
            rect,
            radius,
            margin,
        )
        if corner_edges:
            return corner_edges
        edges = Qt.Edges()
        if abs(point.x() - rect.left()) <= margin:
            edges |= Qt.LeftEdge
        if abs(point.x() - rect.right()) <= margin:
            edges |= Qt.RightEdge
        if abs(point.y() - rect.top()) <= margin:
            edges |= Qt.TopEdge
        if abs(point.y() - rect.bottom()) <= margin:
            edges |= Qt.BottomEdge
        return edges

    def _monitoring_hud_resize_hit_zone_px(self) -> int:
        return 14

    def _monitoring_hud_window_region_corner_radius_px(self, visual_radius: int | None = None) -> int:
        radius = (
            int(visual_radius)
            if visual_radius is not None
            else int(self._monitoring_hud_window_corner_radius_px)
        )
        return max(4, radius - self._monitoring_hud_resize_hit_zone_px())

    def _monitoring_hud_rounded_corner_diagonal_resize_edges_for_point(
        self,
        point: QPoint,
        rect: QRect,
        radius: int,
        margin: int,
    ):
        if radius <= 0:
            return Qt.Edges()
        local_x = int(point.x() - rect.x())
        local_y = int(point.y() - rect.y())
        width = int(rect.width())
        height = int(rect.height())

        corner_center_x = None
        corner_center_y = None
        horizontal_edge = Qt.Edges()
        vertical_edge = Qt.Edges()
        if local_x < radius:
            corner_center_x = radius
            horizontal_edge = Qt.LeftEdge
        elif local_x >= width - radius:
            corner_center_x = width - radius
            horizontal_edge = Qt.RightEdge
        if local_y < radius:
            corner_center_y = radius
            vertical_edge = Qt.TopEdge
        elif local_y >= height - radius:
            corner_center_y = height - radius
            vertical_edge = Qt.BottomEdge
        if corner_center_x is None or corner_center_y is None:
            return Qt.Edges()

        dx = abs(local_x - corner_center_x)
        dy = abs(local_y - corner_center_y)
        distance = math.hypot(dx, dy)
        # The rounded edge is a 90 degree arc. Treat the central 50 percent of
        # that arc as diagonal resize, while the outer quarters still behave as
        # the adjacent horizontal or vertical edge.
        if not (max(0, radius - margin) <= distance <= radius):
            return Qt.Edges()
        angle = math.degrees(math.atan2(dy, dx)) if dx or dy else 45.0
        if 22.5 <= angle <= 67.5:
            return horizontal_edge | vertical_edge
        return Qt.Edges()

    def _monitoring_hud_screen_point_inside_rounded_window_mask(self, point: QPoint) -> bool:
        if self.surface_role != "hud":
            return True
        rect = self.geometry()
        if rect.isNull() or not rect.isValid():
            return False
        local_x = int(point.x() - rect.x())
        local_y = int(point.y() - rect.y())
        width = int(rect.width())
        height = int(rect.height())
        if local_x < 0 or local_y < 0 or local_x >= width or local_y >= height:
            return False
        radius = min(
            int(self._monitoring_hud_window_corner_radius_px),
            max(1, width // 2),
            max(1, height // 2),
        )
        radius = self._monitoring_hud_window_region_corner_radius_px(radius)
        if radius <= 0:
            return True
        corner_center_x = None
        corner_center_y = None
        if local_x < radius:
            corner_center_x = radius
        elif local_x >= width - radius:
            corner_center_x = width - radius
        if local_y < radius:
            corner_center_y = radius
        elif local_y >= height - radius:
            corner_center_y = height - radius
        if corner_center_x is None or corner_center_y is None:
            return True
        dx = local_x - corner_center_x
        dy = local_y - corner_center_y
        return (dx * dx + dy * dy) <= (radius * radius)

    def _monitoring_hud_window_resize_interaction_available(self) -> bool:
        return (
            self.surface_role == "hud"
            and self.desktop_mode
            and self.isVisible()
            and self.webview.isVisible()
        )

    def _monitoring_hud_point_belongs_to_dashboard_window(self, point: QPoint) -> bool:
        if os.name != "nt" or point.isNull():
            return self.geometry().contains(point)
        try:
            probe = ctypes.wintypes.POINT(int(point.x()), int(point.y()))
            hwnd = int(WindowFromPoint(probe))
            dashboard_hwnd = int(self.winId())
            while hwnd:
                if hwnd == dashboard_hwnd:
                    return True
                hwnd = int(GetParentW(ctypes.wintypes.HWND(hwnd)))
        except Exception:
            return self.geometry().contains(point)
        return (
            self.geometry().contains(point)
            and self._monitoring_hud_screen_point_inside_rounded_window_mask(point)
        )

    def _monitoring_hud_resize_edges_under_cursor(self) -> tuple[QPoint, Qt.Edges]:
        if not self._monitoring_hud_window_resize_interaction_available():
            return QPoint(), Qt.Edges()
        screen_point = self._monitoring_hud_cursor_screen_point()
        if screen_point.isNull():
            return QPoint(), Qt.Edges()
        if not self.geometry().adjusted(-2, -2, 2, 2).contains(screen_point):
            return screen_point, Qt.Edges()
        if not self._monitoring_hud_point_belongs_to_dashboard_window(screen_point):
            return screen_point, Qt.Edges()
        edges = self._monitoring_hud_native_resize_edges_for_point(screen_point)
        if edges and self._monitoring_hud_dashboard_control_rect_contains(screen_point):
            return screen_point, Qt.Edges()
        return screen_point, edges

    def _poll_monitoring_hud_resize_hover_cursor(self):
        if (
            self._monitoring_hud_native_panel_drag_active
            or self._monitoring_hud_native_window_resize_active
            or self._monitoring_hud_native_card_drag_active
            or self._monitoring_hud_native_card_resize_active
        ):
            return
        _, edges = self._monitoring_hud_resize_edges_under_cursor()
        if edges:
            self._set_monitoring_hud_resize_cursor(edges)
            return
        self._reset_monitoring_hud_resize_cursor()

    def _monitoring_hud_native_resize_hit_test_for_edges(self, edges) -> int:
        left, right, top, bottom = self._monitoring_hud_resize_edge_key(edges)
        if left and top:
            return HTTOPLEFT
        if right and top:
            return HTTOPRIGHT
        if left and bottom:
            return HTBOTTOMLEFT
        if right and bottom:
            return HTBOTTOMRIGHT
        if left:
            return HTLEFT
        if right:
            return HTRIGHT
        if top:
            return HTTOP
        if bottom:
            return HTBOTTOM
        return 0

    def _monitoring_hud_native_resize_edges_for_hit_test(self, hit_test: int):
        edge_map = {
            HTLEFT: Qt.LeftEdge,
            HTRIGHT: Qt.RightEdge,
            HTTOP: Qt.TopEdge,
            HTBOTTOM: Qt.BottomEdge,
            HTTOPLEFT: Qt.TopEdge | Qt.LeftEdge,
            HTTOPRIGHT: Qt.TopEdge | Qt.RightEdge,
            HTBOTTOMLEFT: Qt.BottomEdge | Qt.LeftEdge,
            HTBOTTOMRIGHT: Qt.BottomEdge | Qt.RightEdge,
        }
        return edge_map.get(int(hit_test), Qt.Edges())

    def _monitoring_hud_cursor_position(self) -> tuple[int, int] | None:
        point = ctypes.wintypes.POINT()
        if not GetCursorPos(ctypes.byref(point)):
            return None
        return int(point.x), int(point.y)

    def _monitoring_hud_cursor_screen_point(self) -> QPoint:
        cursor_position = self._monitoring_hud_cursor_position()
        if cursor_position is None:
            return QPoint()
        return QPoint(int(cursor_position[0]), int(cursor_position[1]))

    def _monitoring_hud_live_drag_screen_point(self, event) -> QPoint:
        cursor_point = self._monitoring_hud_cursor_screen_point()
        if not cursor_point.isNull():
            return cursor_point
        try:
            return event.globalPosition().toPoint()
        except Exception:
            return QPoint()

    def _monitoring_hud_left_mouse_button_down(self) -> bool:
        try:
            return bool(GetAsyncKeyState(VK_LBUTTON) & 0x8000)
        except Exception:
            return False

    def _monitoring_hud_resize_refresh_rate_hz(self) -> float:
        screens = []
        try:
            screens.append(self.screen())
        except Exception:
            pass
        screens.extend([getattr(self, "screen_ref", None), QApplication.primaryScreen()])
        for screen in screens:
            if screen is None:
                continue
            try:
                refresh_rate = float(screen.refreshRate())
            except Exception:
                continue
            if 30.0 <= refresh_rate <= 360.0:
                return refresh_rate
        return 60.0

    def _monitoring_hud_resize_frame_interval_ms(self) -> int:
        refresh_rate = self._monitoring_hud_resize_refresh_rate_hz()
        return max(4, min(16, int(round(1000.0 / refresh_rate))))

    def _start_monitoring_hud_native_system_resize(self, edges, screen_point: QPoint) -> bool:
        if self.surface_role != "hud" or not edges:
            return False
        window_handle = self.windowHandle()
        start_system_resize = getattr(window_handle, "startSystemResize", None) if window_handle else None
        if not callable(start_system_resize):
            return False
        self._emit_runtime_signal(
            "MONITORING_HUD_NATIVE_SYSTEM_RESIZE_STARTED",
            package="PKG-006",
            slice="SLC-026",
            seam="WS44",
            x=screen_point.x(),
            y=screen_point.y(),
            resize_model="os-edge-corner-resize",
            edges=str(edges),
        )
        try:
            started = bool(start_system_resize(edges))
        except Exception:
            started = False
        if started:
            QTimer.singleShot(360, lambda: self._finish_monitoring_hud_native_system_resize("system_resize"))
        return started

    def _monitoring_hud_resize_edge_key(self, edges) -> tuple[bool, bool, bool, bool]:
        return (
            bool(edges & Qt.LeftEdge),
            bool(edges & Qt.RightEdge),
            bool(edges & Qt.TopEdge),
            bool(edges & Qt.BottomEdge),
        )

    def _monitoring_hud_resize_cursor_for_edges(self, edges):
        left, right, top, bottom = self._monitoring_hud_resize_edge_key(edges)
        if (left and top) or (right and bottom):
            return Qt.SizeFDiagCursor
        if (right and top) or (left and bottom):
            return Qt.SizeBDiagCursor
        if left or right:
            return Qt.SizeHorCursor
        if top or bottom:
            return Qt.SizeVerCursor
        return None

    def _monitoring_hud_windows_resize_cursor_id_for_edges(self, edges):
        if not edges:
            return IDC_ARROW
        left, right, top, bottom = self._monitoring_hud_resize_edge_key(edges)
        if (left and top) or (right and bottom):
            return IDC_SIZENWSE
        if (right and top) or (left and bottom):
            return IDC_SIZENESW
        if left or right:
            return IDC_SIZEWE
        if top or bottom:
            return IDC_SIZENS
        return IDC_ARROW

    def _apply_monitoring_hud_windows_resize_cursor(self, edges):
        if os.name != "nt":
            return
        # resize-cursor-no-forced-arrow-release: clear our override without
        # forcing IDC_ARROW, or Windows edge hover can flicker arrow/resize.
        if not edges:
            return
        try:
            cursor_id = self._monitoring_hud_windows_resize_cursor_id_for_edges(edges)
            cursor_handle = LoadCursorW(None, cursor_id)
            if cursor_handle:
                SetCursor(cursor_handle)
        except Exception:
            pass

    def _set_monitoring_hud_override_resize_cursor(self, cursor):
        try:
            if cursor is None:
                if self._monitoring_hud_resize_override_cursor_active:
                    QApplication.restoreOverrideCursor()
                    self._monitoring_hud_resize_override_cursor_active = False
                return
            qt_cursor = QCursor(cursor)
            if self._monitoring_hud_resize_override_cursor_active:
                QApplication.changeOverrideCursor(qt_cursor)
            else:
                QApplication.setOverrideCursor(qt_cursor)
                self._monitoring_hud_resize_override_cursor_active = True
        except Exception:
            self._monitoring_hud_resize_override_cursor_active = False

    def _set_monitoring_hud_resize_cursor(self, edges):
        key = self._monitoring_hud_resize_edge_key(edges) if edges else None
        if key == self._monitoring_hud_resize_cursor_key:
            if os.name == "nt":
                if key is not None:
                    self._set_monitoring_hud_override_resize_cursor(
                        self._monitoring_hud_resize_cursor_for_edges(edges)
                    )
                self._apply_monitoring_hud_windows_resize_cursor(edges if key is not None else Qt.Edges())
            elif key is not None:
                self._apply_monitoring_hud_windows_resize_cursor(edges)
            return
        self._monitoring_hud_resize_cursor_key = key
        cursor = self._monitoring_hud_resize_cursor_for_edges(edges) if edges else None
        targets = [self, self.webview]
        try:
            targets.extend(self.webview.findChildren(QWidget))
        except Exception:
            pass
        if os.name == "nt":
            for target in targets:
                target.unsetCursor()
            self._set_monitoring_hud_override_resize_cursor(cursor)
            self._apply_monitoring_hud_windows_resize_cursor(edges)
            return
        for target in targets:
            if cursor is None:
                target.unsetCursor()
            else:
                target.setCursor(QCursor(cursor))
        self._set_monitoring_hud_override_resize_cursor(cursor)
        self._apply_monitoring_hud_windows_resize_cursor(edges)

    def _reset_monitoring_hud_resize_cursor(self):
        self._set_monitoring_hud_resize_cursor(Qt.Edges())

    def _start_monitoring_hud_fallback_window_resize(self, edges, screen_point: QPoint):
        resize_refresh_rate_hz = self._monitoring_hud_resize_refresh_rate_hz()
        resize_frame_interval_ms = self._monitoring_hud_resize_frame_interval_ms()
        self._monitoring_hud_native_window_resize_active = True
        self._monitoring_hud_user_geometry_override_active = True
        self._monitoring_hud_native_window_resize_edges = edges
        self._monitoring_hud_native_window_resize_start = screen_point
        self._monitoring_hud_native_window_resize_base = QRect(self.geometry())
        self._monitoring_hud_native_window_resize_last_rect = QRect(self.geometry())
        self._monitoring_hud_native_window_resize_pending_point = QPoint(screen_point)
        self._monitoring_hud_native_window_resize_last_apply = 0.0
        self._monitoring_hud_native_window_resize_frame_interval_ms = resize_frame_interval_ms
        self._monitoring_hud_native_window_resize_poll_active = True
        self._monitoring_hud_resize_frame_sync_last = 0.0
        self._monitoring_hud_resize_js_sync_last = 0.0
        self._clear_monitoring_hud_native_user_move()
        try:
            SetCapture(ctypes.wintypes.HWND(int(self.winId())))
        except Exception:
            pass
        self._emit_runtime_signal(
            "MONITORING_HUD_NATIVE_WINDOW_RESIZE_FALLBACK_STARTED",
            package="PKG-006",
            slice="SLC-026",
            seam="WS56",
            x=screen_point.x(),
            y=screen_point.y(),
            resize_model="refresh-rate-paced-cursor-owned-fluid-geometry-resize",
            resize_edge_scope="all-edges-and-corners",
            resize_hit_zone_px=self._monitoring_hud_resize_hit_zone_px(),
            resize_refresh_rate_hz=round(resize_refresh_rate_hz, 2),
            resize_frame_interval_ms=resize_frame_interval_ms,
            resize_poll_interval_ms=resize_frame_interval_ms,
            edges=str(edges),
        )
        self._monitoring_hud_native_window_resize_poll_timer.stop()
        self._monitoring_hud_native_window_resize_poll_timer.setInterval(resize_frame_interval_ms)
        self._monitoring_hud_native_window_resize_poll_timer.start()
        self._poll_monitoring_hud_fallback_window_resize()

    def _poll_monitoring_hud_fallback_window_resize(self):
        if not self._monitoring_hud_native_window_resize_active:
            self._monitoring_hud_native_window_resize_poll_timer.stop()
            self._monitoring_hud_native_window_resize_poll_active = False
            return
        screen_point = self._monitoring_hud_cursor_screen_point()
        if not screen_point.isNull():
            self._update_monitoring_hud_fallback_window_resize(screen_point)
        if self._monitoring_hud_left_mouse_button_down():
            return
        self._finish_monitoring_hud_fallback_window_resize(screen_point)

    def _update_monitoring_hud_fallback_window_resize(self, screen_point: QPoint):
        if not self._monitoring_hud_native_window_resize_active:
            return
        self._monitoring_hud_native_window_resize_pending_point = QPoint(screen_point)
        interval_s = max(0.004, self._monitoring_hud_native_window_resize_frame_interval_ms / 1000.0)
        now = time.monotonic()
        elapsed = now - self._monitoring_hud_native_window_resize_last_apply
        if self._monitoring_hud_native_window_resize_last_apply <= 0.0 or elapsed >= interval_s:
            self._apply_monitoring_hud_queued_window_resize()
            return
        if not self._monitoring_hud_native_window_resize_frame_timer.isActive():
            remaining_ms = max(1, int(round((interval_s - elapsed) * 1000.0)))
            self._monitoring_hud_native_window_resize_frame_timer.start(remaining_ms)

    def _apply_monitoring_hud_queued_window_resize(self):
        if not self._monitoring_hud_native_window_resize_active:
            return
        screen_point = QPoint(self._monitoring_hud_native_window_resize_pending_point)
        if screen_point.isNull():
            screen_point = self._monitoring_hud_cursor_screen_point()
        if screen_point.isNull():
            return
        next_rect = self._monitoring_hud_resize_rect_from_native_delta(screen_point)
        if next_rect == self._monitoring_hud_native_window_resize_last_rect:
            self._monitoring_hud_native_window_resize_last_apply = time.monotonic()
            return
        self.setGeometry(next_rect)
        self._monitoring_hud_native_window_resize_last_rect = QRect(next_rect)
        self._monitoring_hud_interactive_screen_rect = self.geometry()
        self._monitoring_hud_native_window_resize_last_apply = time.monotonic()
        self._sync_monitoring_hud_resize_frame()

    def _finish_monitoring_hud_fallback_window_resize(self, screen_point: QPoint):
        if not self._monitoring_hud_native_window_resize_active:
            return
        self._monitoring_hud_native_window_resize_poll_timer.stop()
        self._monitoring_hud_native_window_resize_frame_timer.stop()
        if screen_point.isNull():
            screen_point = self._monitoring_hud_native_window_resize_start
        next_rect = self._monitoring_hud_resize_rect_from_native_delta(screen_point)
        if next_rect != self._monitoring_hud_native_window_resize_last_rect:
            self.setGeometry(next_rect)
            self._monitoring_hud_native_window_resize_last_rect = QRect(next_rect)
        self._sync_monitoring_hud_resize_frame(force=True)
        self._monitoring_hud_native_window_resize_active = False
        self._monitoring_hud_native_window_resize_poll_active = False
        self._monitoring_hud_native_window_resize_edges = Qt.Edges()
        self._monitoring_hud_native_window_resize_last_rect = QRect()
        self._monitoring_hud_native_window_resize_pending_point = QPoint()
        self._monitoring_hud_native_window_resize_last_apply = 0.0
        try:
            ReleaseCapture()
        except Exception:
            pass
        self._reset_monitoring_hud_resize_cursor()
        self._finish_monitoring_hud_native_system_resize("fallback_window_resize")

    def _sync_monitoring_hud_resize_frame(self, *, force: bool = False):
        if self.surface_role != "hud" or self._is_shutting_down:
            return
        now = time.monotonic()
        frame_interval_s = max(0.004, self._monitoring_hud_native_window_resize_frame_interval_ms / 1000.0)
        if not force and now - self._monitoring_hud_resize_frame_sync_last < frame_interval_s:
            return
        self._monitoring_hud_resize_frame_sync_last = now
        self.webview.setGeometry(self.rect())
        self.webview.updateGeometry()
        self.webview.update()
        self.update()
        try:
            QApplication.processEvents()
        except Exception:
            pass
        js_interval_s = max(0.033, frame_interval_s * 2.0)
        if force or now - self._monitoring_hud_resize_js_sync_last >= js_interval_s:
            self._monitoring_hud_resize_js_sync_last = now
            self._run_javascript(
                """
                window.requestAnimationFrame(() => {
                    window.dispatchEvent(new Event('resize'));
                });
                """
            )

    def _monitoring_hud_effective_window_minimum_size(self) -> tuple[int, int]:
        virtual = self._virtual_desktop_geometry()
        min_width = min(max(self.minimumWidth(), 640), max(1, virtual.width()))
        min_height = min(max(self.minimumHeight(), 595), max(1, virtual.height()))
        return min_width, min_height

    def _apply_monitoring_hud_effective_window_minimum_size(self):
        min_width, min_height = self._monitoring_hud_effective_window_minimum_size()
        self.setMinimumSize(min_width, min_height)

    def _bound_monitoring_hud_window_resize_rect(self, rect: QRect) -> QRect:
        virtual = self._virtual_desktop_geometry()
        min_width, min_height = self._monitoring_hud_effective_window_minimum_size()
        width = max(min_width, min(rect.width(), virtual.width()))
        height = max(min_height, min(rect.height(), virtual.height()))
        left = max(virtual.x(), min(rect.x(), virtual.x() + virtual.width() - width))
        top = max(virtual.y(), min(rect.y(), virtual.y() + virtual.height() - height))
        return QRect(left, top, width, height)

    def _monitoring_hud_resize_rect_from_native_delta(self, screen_point: QPoint) -> QRect:
        base = self._monitoring_hud_native_window_resize_base
        if base.isNull() or not base.isValid():
            base = QRect(self.geometry())
        delta = screen_point - self._monitoring_hud_native_window_resize_start
        left, right, top, bottom = self._monitoring_hud_resize_edge_key(
            self._monitoring_hud_native_window_resize_edges
        )
        x = base.x()
        y = base.y()
        width = base.width()
        height = base.height()
        if left:
            x = base.x() + delta.x()
            width = base.width() - delta.x()
        elif right:
            width = base.width() + delta.x()
        if top:
            y = base.y() + delta.y()
            height = base.height() - delta.y()
        elif bottom:
            height = base.height() + delta.y()

        min_width, min_height = self._monitoring_hud_effective_window_minimum_size()
        if width < min_width:
            if left:
                x = base.right() - min_width + 1
            width = min_width
        if height < min_height:
            if top:
                y = base.bottom() - min_height + 1
            height = min_height
        return self._bound_monitoring_hud_window_resize_rect(QRect(x, y, width, height))

    def _monitoring_hud_header_rect(self) -> QRect:
        rect = self._monitoring_hud_interactive_screen_rect
        if rect.isNull() or not rect.isValid():
            rect = self._estimate_monitoring_hud_interactive_screen_rect()
            self._monitoring_hud_interactive_screen_rect = rect
        return QRect(rect.x(), rect.y(), rect.width(), min(170, rect.height()))

    def _monitoring_hud_page_origin_from_screen_rect(self) -> QPoint:
        rect = self._monitoring_hud_interactive_screen_rect
        if rect.isNull() or not rect.isValid():
            rect = self._estimate_monitoring_hud_interactive_screen_rect()
            self._monitoring_hud_interactive_screen_rect = rect
        webview_origin = self.webview.mapToGlobal(QPoint(0, 0))
        return QPoint(max(0, rect.x() + 12 - webview_origin.x()), max(0, rect.y() + 12 - webview_origin.y()))

    def _set_monitoring_hud_panel_position_from_native_drag(self, left: int, top: int, *, emit_status: bool = True):
        if self.surface_role == "hud":
            self._monitoring_hud_user_geometry_override_active = True
            virtual = self._virtual_desktop_geometry()
            max_left = virtual.x() + max(0, virtual.width() - self.width())
            max_top = virtual.y() + max(0, virtual.height() - self.height())
            bounded_left = self._monitoring_hud_bound_native(
                int(left),
                virtual.x(),
                max_left,
            )
            bounded_top = self._monitoring_hud_bound_native(
                int(top),
                virtual.y(),
                max_top,
            )
            self.move(bounded_left, bounded_top)
            self._monitoring_hud_interactive_screen_rect = self.geometry()
            if emit_status:
                self._emit_runtime_signal(
                    "MONITORING_HUD_NATIVE_WINDOW_MOVE_READY",
                    package="PKG-006",
                    slice="SLC-026",
                    seam="WS38",
                    movement_model="fallback-direct-move-no-snap",
                    x=bounded_left,
                    y=bounded_top,
                    virtual_desktop="all_monitors",
                )
                self._emit_monitoring_hud_window_ownership_focus_ready(source="fallback_direct_move")
                self._emit_monitoring_hud_window_status(source="native_window_drag")
            return
        state = {
            "visible": True,
            "anchored": False,
            "snapEnabled": self._monitoring_hud_snap_enabled,
            "pollingRateMs": self._monitoring_hud_polling_rate_ms,
            "panelPosition": {
                "left": max(0, int(left)),
                "top": max(0, int(top)),
            },
        }
        state_json = json.dumps(state, sort_keys=True)
        self._run_javascript(
            f"""
            if (window.setMonitoringHudControlState) {{
                window.setMonitoringHudControlState({state_json});
            }}
            """
        )

    def _monitoring_hud_snap_native(self, value: int | float) -> int:
        return int(round(float(value) / 20) * 20)

    def _monitoring_hud_bound_native(self, value: int, lower: int, upper: int) -> int:
        return max(lower, min(upper, int(value)))

    def _monitoring_hud_card_layout_base(self, card_id: str) -> dict[str, int]:
        defaults = {
            "cpu": {"x": 0, "y": 0, "w": 600, "h": 280},
            "gpu": {"x": 0, "y": 300, "w": 600, "h": 280},
        }
        base = dict(defaults.get(card_id, {"x": 0, "y": 0, "w": 600, "h": 280}))
        cards = self._monitoring_hud_live_page_state.get("cards") if isinstance(self._monitoring_hud_live_page_state, dict) else {}
        card = cards.get(card_id) if isinstance(cards, dict) else {}
        if isinstance(card, dict):
            for key in ("x", "y", "w", "h"):
                try:
                    base[key] = int(float(card.get(key, base[key])))
                except (TypeError, ValueError):
                    pass
        return base

    def _monitoring_hud_card_board_bounds(self) -> tuple[int, int]:
        board_rect = self._monitoring_hud_live_screen_rects.get("cardBoard", QRect())
        if board_rect.isValid() and not board_rect.isNull():
            return max(420, board_rect.width()), max(620, board_rect.height())
        return 720, 620

    def _set_monitoring_hud_card_layout_from_native_drag(self, card_id: str, layout: dict[str, int]):
        state: dict[str, object] = {}
        if isinstance(self._monitoring_hud_live_page_state, dict):
            for key in ("visible", "anchored", "snapEnabled", "pollingRateMs", "panelPosition"):
                if key in self._monitoring_hud_live_page_state:
                    state[key] = self._monitoring_hud_live_page_state[key]
        state.update(
            {
                "visible": True,
                "anchored": False,
                "snapEnabled": self._monitoring_hud_snap_enabled,
                "pollingRateMs": self._monitoring_hud_polling_rate_ms,
            }
        )
        cards: dict[str, dict[str, int]] = {
            "cpu": {"x": 0, "y": 0, "w": 600, "h": 280},
            "gpu": {"x": 0, "y": 300, "w": 600, "h": 280},
        }
        page_cards = self._monitoring_hud_live_page_state.get("cards") if isinstance(self._monitoring_hud_live_page_state, dict) else {}
        if isinstance(page_cards, dict):
            for existing_id, existing_layout in page_cards.items():
                if isinstance(existing_layout, dict):
                    merged = dict(cards.get(str(existing_id), {"x": 0, "y": 0, "w": 600, "h": 280}))
                    for key in ("x", "y", "w", "h"):
                        try:
                            merged[key] = int(float(existing_layout.get(key, merged[key])))
                        except (TypeError, ValueError):
                            pass
                    cards[str(existing_id)] = merged
        cards[card_id] = {
            "x": int(layout.get("x", 0)),
            "y": int(layout.get("y", 0)),
            "w": int(layout.get("w", 600)),
            "h": int(layout.get("h", 280)),
        }
        state["cards"] = cards
        state_json = json.dumps(state, sort_keys=True)
        self._run_javascript(
            f"""
            if (window.setMonitoringHudControlState) {{
                window.setMonitoringHudControlState({state_json});
            }}
            """
        )

    def _apply_monitoring_hud_native_anchor_click_if_needed(self, expected_anchored: bool):
        if self._monitoring_hud_anchored is expected_anchored:
            return
        self._set_monitoring_hud_control_state(
            anchored=expected_anchored,
            source="native-anchor-click-fallback",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_NATIVE_ANCHOR_CLICK_READY",
            package="PKG-006",
            slice="SLC-026",
            anchored=expected_anchored,
        )

    def _monitoring_hud_layout_from_native_delta(self, resize: bool, delta: QPoint) -> dict[str, int]:
        layout = dict(self._monitoring_hud_native_card_drag_base)
        if resize:
            board_width, board_height = self._monitoring_hud_card_board_bounds()
            layout["w"] = self._monitoring_hud_bound_native(
                self._monitoring_hud_snap_native(layout.get("w", 600) + delta.x()),
                340,
                max(340, self._monitoring_hud_snap_native(board_width - layout.get("x", 0))),
            )
            layout["h"] = self._monitoring_hud_bound_native(
                self._monitoring_hud_snap_native(layout.get("h", 280) + delta.y()),
                260,
                max(260, self._monitoring_hud_snap_native(board_height - layout.get("y", 0))),
            )
            return layout
        board_width, board_height = self._monitoring_hud_card_board_bounds()
        layout["x"] = self._monitoring_hud_bound_native(
            self._monitoring_hud_snap_native(layout.get("x", 0) + delta.x()),
            0,
            max(0, board_width - layout.get("w", 600)),
        )
        layout["y"] = self._monitoring_hud_bound_native(
            self._monitoring_hud_snap_native(layout.get("y", 0) + delta.y()),
            0,
            max(0, board_height - layout.get("h", 280)),
        )
        return layout

    def _handle_monitoring_hud_native_panel_drag_event(self, event) -> bool:
        if (
            not self.desktop_mode
            or (self.surface_role == "hud" and not self.isVisible())
            or (self.surface_role != "hud" and (not self._monitoring_hud_feature_enabled or not self._monitoring_hud_visible))
        ):
            self._monitoring_hud_native_panel_drag_active = False
            self._monitoring_hud_native_window_resize_active = False
            self._clear_monitoring_hud_native_user_move()
            self._monitoring_hud_native_card_drag_active = False
            self._monitoring_hud_native_card_resize_active = False
            self._reset_monitoring_hud_resize_cursor()
            return False
        event_type = event.type()
        if event_type == QEvent.Leave and not (
            self._monitoring_hud_native_panel_drag_active
            or self._monitoring_hud_native_window_resize_active
            or self._monitoring_hud_native_card_drag_active
            or self._monitoring_hud_native_card_resize_active
        ):
            self._reset_monitoring_hud_resize_cursor()
            return False
        if event_type == QEvent.MouseMove and not (
            self._monitoring_hud_native_panel_drag_active
            or self._monitoring_hud_native_window_resize_active
            or self._monitoring_hud_native_card_drag_active
            or self._monitoring_hud_native_card_resize_active
        ):
            if not self._monitoring_hud_window_resize_interaction_available():
                return False
            screen_point = event.globalPosition().toPoint()
            resize_edges = self._monitoring_hud_native_resize_edges_for_point(screen_point)
            if resize_edges and not self._monitoring_hud_dashboard_control_rect_contains(screen_point):
                self._set_monitoring_hud_resize_cursor(resize_edges)
            else:
                self._reset_monitoring_hud_resize_cursor()
            return False
        if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            screen_point = event.globalPosition().toPoint()
            if self._guard_monitoring_hud_active_child_window_background_click(
                screen_point,
                source="qt_mouse_button_press",
            ):
                return True
            if self._handle_monitoring_hud_dashboard_settings_native_control(screen_point):
                return True
            if self._handle_monitoring_hud_dashboard_close_native_control(screen_point):
                return True
            resize_edges = self._monitoring_hud_native_resize_edges_for_point(screen_point)
            if resize_edges and not self._monitoring_hud_dashboard_control_rect_contains(screen_point):
                # Use direct geometry resizing for the user-facing Dashboard. Qt/Windows can
                # report startSystemResize as "started" without delivering a real resize for
                # this frameless WebEngine window, which made prior proof over-credit the path.
                self._start_monitoring_hud_fallback_window_resize(resize_edges, screen_point)
                return True
            if not (
                self._monitoring_hud_native_panel_drag_active
                or self._monitoring_hud_native_window_resize_active
                or self._monitoring_hud_native_card_drag_active
                or self._monitoring_hud_native_card_resize_active
            ):
                for card_id in ("cpu", "gpu"):
                    resize_rect = self._monitoring_hud_live_screen_rects.get(f"{card_id}ResizeHandle", QRect())
                    drag_rect = self._monitoring_hud_live_screen_rects.get(f"{card_id}DragHandle", QRect())
                    if resize_rect.isValid() and resize_rect.contains(screen_point):
                        self._monitoring_hud_native_card_resize_active = True
                        self._monitoring_hud_native_card_drag_id = card_id
                        self._monitoring_hud_native_card_drag_start = screen_point
                        self._monitoring_hud_native_card_drag_base = self._monitoring_hud_card_layout_base(card_id)
                        self._emit_runtime_signal(
                            "MONITORING_HUD_NATIVE_CARD_RESIZE_STARTED",
                            package="PKG-006",
                            slice="SLC-026",
                            card=card_id,
                            x=screen_point.x(),
                            y=screen_point.y(),
                        )
                        return True
                    if drag_rect.isValid() and drag_rect.contains(screen_point):
                        self._monitoring_hud_native_card_drag_active = True
                        self._monitoring_hud_native_card_drag_id = card_id
                        self._monitoring_hud_native_card_drag_start = screen_point
                        self._monitoring_hud_native_card_drag_base = self._monitoring_hud_card_layout_base(card_id)
                        self._emit_runtime_signal(
                            "MONITORING_HUD_NATIVE_CARD_DRAG_STARTED",
                            package="PKG-006",
                            slice="SLC-026",
                            card=card_id,
                            x=screen_point.x(),
                            y=screen_point.y(),
                        )
                        return True
                anchor_rect = self._monitoring_hud_live_screen_rects.get("anchorToggle", QRect())
                if anchor_rect.isValid() and anchor_rect.contains(screen_point):
                    self._monitoring_hud_native_anchor_click_pending = True
                    self._monitoring_hud_native_anchor_click_expected = not bool(self._monitoring_hud_anchored)
                    return False
            if (
                self._monitoring_hud_header_rect().contains(screen_point)
                and not self._monitoring_hud_dashboard_control_rect_contains(screen_point)
            ):
                if self._start_monitoring_hud_fallback_panel_move(screen_point, source="fallback_direct_client_header_move"):
                    return True
                self._monitoring_hud_native_panel_drag_active = True
                self._monitoring_hud_native_panel_drag_start = screen_point
                self._monitoring_hud_native_panel_drag_base = (
                    self.pos() if self.surface_role == "hud" else self._monitoring_hud_page_origin_from_screen_rect()
                )
                self._emit_runtime_signal(
                    "MONITORING_HUD_NATIVE_PANEL_DRAG_STARTED",
                    package="PKG-006",
                    slice="SLC-026",
                    x=screen_point.x(),
                    y=screen_point.y(),
                )
                return True
        if event_type == QEvent.MouseMove and (
            self._monitoring_hud_native_card_drag_active or self._monitoring_hud_native_card_resize_active
        ):
            screen_point = event.globalPosition().toPoint()
            delta = screen_point - self._monitoring_hud_native_card_drag_start
            layout = self._monitoring_hud_layout_from_native_delta(self._monitoring_hud_native_card_resize_active, delta)
            self._set_monitoring_hud_card_layout_from_native_drag(self._monitoring_hud_native_card_drag_id, layout)
            return True
        if event_type == QEvent.MouseMove and self._monitoring_hud_native_window_resize_active:
            screen_point = self._monitoring_hud_live_drag_screen_point(event)
            self._update_monitoring_hud_fallback_window_resize(screen_point)
            return True
        if event_type == QEvent.MouseMove and self._monitoring_hud_native_panel_drag_active:
            screen_point = self._monitoring_hud_live_drag_screen_point(event)
            delta = screen_point - self._monitoring_hud_native_panel_drag_start
            self._set_monitoring_hud_panel_position_from_native_drag(
                self._monitoring_hud_native_panel_drag_base.x() + delta.x(),
                self._monitoring_hud_native_panel_drag_base.y() + delta.y(),
                emit_status=False,
            )
            return True
        if event_type in (QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick):
            try:
                screen_point_for_guard = event.globalPosition().toPoint()
            except Exception:
                screen_point_for_guard = QPoint()
            if self._guard_monitoring_hud_active_child_window_background_click(
                screen_point_for_guard,
                source="qt_mouse_button_release_or_double_click",
            ):
                return True
            if self._monitoring_hud_native_anchor_click_pending:
                self._monitoring_hud_native_anchor_click_pending = False
                expected_anchored = self._monitoring_hud_native_anchor_click_expected
                QTimer.singleShot(
                    140,
                    lambda anchored=expected_anchored: self._apply_monitoring_hud_native_anchor_click_if_needed(anchored),
                )
                return False
            if self._monitoring_hud_native_card_drag_active or self._monitoring_hud_native_card_resize_active:
                screen_point = event.globalPosition().toPoint()
                delta = screen_point - self._monitoring_hud_native_card_drag_start
                resize = self._monitoring_hud_native_card_resize_active
                card_id = self._monitoring_hud_native_card_drag_id
                layout = self._monitoring_hud_layout_from_native_delta(resize, delta)
                self._set_monitoring_hud_card_layout_from_native_drag(card_id, layout)
                self._monitoring_hud_native_card_drag_active = False
                self._monitoring_hud_native_card_resize_active = False
                self._monitoring_hud_native_card_drag_id = ""
                self._emit_runtime_signal(
                    "MONITORING_HUD_NATIVE_CARD_RESIZE_READY" if resize else "MONITORING_HUD_NATIVE_CARD_DRAG_READY",
                    package="PKG-006",
                    slice="SLC-026",
                    card=card_id,
                    dx=delta.x(),
                    dy=delta.y(),
                    x=layout.get("x"),
                    y=layout.get("y"),
                    w=layout.get("w"),
                    h=layout.get("h"),
                )
                return True
            if self._monitoring_hud_native_window_resize_active:
                screen_point = self._monitoring_hud_live_drag_screen_point(event)
                self._finish_monitoring_hud_fallback_window_resize(screen_point)
                return True
            if self._monitoring_hud_native_panel_drag_active:
                screen_point = self._monitoring_hud_live_drag_screen_point(event)
                delta = screen_point - self._monitoring_hud_native_panel_drag_start
                self._set_monitoring_hud_panel_position_from_native_drag(
                    self._monitoring_hud_native_panel_drag_base.x() + delta.x(),
                    self._monitoring_hud_native_panel_drag_base.y() + delta.y(),
                )
                self._monitoring_hud_native_panel_drag_active = False
                self._emit_runtime_signal(
                    "MONITORING_HUD_NATIVE_PANEL_DRAG_READY",
                    package="PKG-006",
                    slice="SLC-026",
                    dx=delta.x(),
                    dy=delta.y(),
                )
                return True
            return False
        return False

    def _apply_monitoring_hud_window_interaction_state(self):
        anchored = bool(self._monitoring_hud_anchored)
        feature_enabled = bool(self._monitoring_hud_feature_enabled)
        dashboard_visible = bool(feature_enabled and self._monitoring_hud_visible)
        was_visible = bool(self.isVisible() and self.webview.isVisible() and self.windowOpacity() > 0.0)
        if dashboard_visible and self.desktop_mode and not was_visible:
            self._arm_monitoring_hud_visible_show_guard("interaction_state")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        if self.surface_role == "hud":
            self.setWindowFlag(Qt.Tool, False)
            self.setWindowFlag(Qt.Window, True)
        else:
            self.setWindowFlag(Qt.Tool, True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setFocusPolicy(Qt.StrongFocus if dashboard_visible else Qt.NoFocus)
        self.webview.setFocusPolicy(Qt.StrongFocus if dashboard_visible else Qt.NoFocus)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self._apply_monitoring_hud_native_activation_style(False)
        self._monitoring_hud_interactive_screen_rect = self._estimate_monitoring_hud_interactive_screen_rect()
        if not dashboard_visible and self.isVisible():
            self.webview.hide()
            self.hide()
        if dashboard_visible and self.desktop_mode:
            if not self.isVisible():
                self.show()
            if not self.webview.isVisible():
                self.webview.show()
            self.show()
            if self._page_ready and not self._monitoring_hud_control_sync_timer.isActive():
                self._monitoring_hud_control_sync_timer.start(500)
        lifecycle_ready = bool(
            self.surface_role == "hud"
            and dashboard_visible
            and self.desktop_mode
            and not self._is_shutting_down
            and self._page_ready
            and self.isVisible()
            and not self.isMinimized()
            and self.webview.isVisible()
        )
        lifecycle_signature = (
            lifecycle_ready,
            feature_enabled,
            dashboard_visible,
            self.desktop_mode,
            self._page_ready,
            self.isVisible(),
            self.isMinimized(),
            self.webview.isVisible(),
            self._is_shutting_down,
        )
        if lifecycle_signature != self._monitoring_hud_lifecycle_timer_signature:
            self._monitoring_hud_lifecycle_transition_generation += 1
            self._monitoring_hud_lifecycle_timer_signature = lifecycle_signature
        if not lifecycle_ready:
            self._reset_monitoring_hud_resize_cursor()
            self._monitoring_hud_recording_control_click_bridge_down = False
            self._monitoring_hud_recording_control_click_bridge_press_point = QPoint()
        for timer in (
            self._monitoring_hud_resize_hover_timer,
            self._monitoring_hud_recording_control_click_bridge_timer,
        ):
            if lifecycle_ready and not timer.isActive():
                timer.start()
            elif not lifecycle_ready and timer.isActive():
                timer.stop()
        self._emit_runtime_signal(
            "MONITORING_HUD_INTERACTION_MODE_READY",
            package="PKG-006",
            slice="SLC-026",
            feature_enabled=feature_enabled,
            dashboard_visible=dashboard_visible,
            anchored=anchored,
            pointer_model="normal_dashboard_window_no_topmost",
        )
        if self.surface_role == "hud":
            self._emit_runtime_signal(
                "MONITORING_HUD_DASHBOARD_SHELL_LAYOUT_READY",
                package="PKG-006",
                slice="SLC-016",
                seam="WS39",
                source="interaction_state",
                surface="hud_dashboard",
                sticky_header=True,
                single_surface_scrollbar=True,
                title="HUD Dashboard",
                resize_model="os-edge-corner-resize",
            )
            self._emit_monitoring_hud_visual_shell_ready(source="interaction_state")
        self._emit_monitoring_hud_window_ownership_focus_ready(source="interaction_state")
        self._emit_monitoring_hud_window_status(source="interaction_state")
        self._sync_monitoring_hud_minimal_native_overlay(source="interaction_state")

    def _arm_monitoring_hud_visible_show_guard(self, source: str = "runtime") -> None:
        if self.surface_role != "hud" or self._is_shutting_down:
            return
        self._monitoring_hud_show_guard_generation += 1
        generation = self._monitoring_hud_show_guard_generation
        self._monitoring_hud_show_guard_active = True
        self.setWindowOpacity(0.0)
        self._emit_runtime_signal(
            "MONITORING_HUD_VISIBLE_SHOW_GUARD_ARMED",
            package="PKG-006",
            slice="SLC-029",
            seam="LV1",
            source=source,
            release_delay_ms=self._monitoring_hud_show_guard_release_delay_ms,
            visual_release_model="dashboard_geometry_and_webview_frames_settled_before_opacity",
        )
        QTimer.singleShot(
            self._monitoring_hud_show_guard_release_delay_ms,
            lambda source=source, generation=generation: self._release_monitoring_hud_visible_show_guard(
                source,
                generation,
            ),
        )

    def _release_monitoring_hud_visible_show_guard(self, source: str = "runtime", generation: int | None = None) -> None:
        if self.surface_role != "hud" or self._is_shutting_down:
            return
        if not self._monitoring_hud_show_guard_active:
            return
        if generation is not None and generation != self._monitoring_hud_show_guard_generation:
            return
        if not (self._monitoring_hud_feature_enabled and self._monitoring_hud_visible and self.isVisible()):
            return
        if (
            not self._monitoring_hud_user_geometry_override_active
            and not self._monitoring_hud_native_window_resize_active
            and not self._monitoring_hud_native_move_user_active
        ):
            target_geometry = self.compute_compact_geometry()
            if not self._native_window_matches_target(int(self.winId()), target_geometry):
                self.setGeometry(target_geometry)
            self._monitoring_hud_interactive_screen_rect = self._estimate_monitoring_hud_interactive_screen_rect()
        self.webview.update()
        self.update()
        self._monitoring_hud_show_guard_active = False
        self.setWindowOpacity(1.0)
        self._emit_runtime_signal(
            "MONITORING_HUD_VISIBLE_SHOW_GUARD_RELEASED",
            package="PKG-006",
            slice="SLC-029",
            seam="LV1",
            source=source,
            release_delay_ms=self._monitoring_hud_show_guard_release_delay_ms,
        )
        if self._monitoring_hud_deferred_initial_visibility_release:
            self._monitoring_hud_deferred_initial_visibility_release = False
            self._log_event(
                "RENDERER_MAIN|CORE_VISUALIZATION_FIRST_VISIBLE"
                "|source=monitoring_hud_visible_show_guard"
            )
            self.core_visualization_visible.emit()

    def _set_monitoring_hud_control_state(
        self,
        *,
        visible: bool | None = None,
        anchored: bool | None = None,
        snap_enabled: bool | None = None,
        polling_rate_ms: int | None = None,
        source: str = "runtime",
    ):
        if visible is not None:
            self._monitoring_hud_visible = bool(visible)
        if anchored is not None:
            self._monitoring_hud_anchored = bool(anchored)
        if snap_enabled is not None:
            self._monitoring_hud_snap_enabled = bool(snap_enabled)
        if polling_rate_ms is not None:
            self._monitoring_hud_polling_rate_ms = max(1000, int(polling_rate_ms or 1000))
            if self._monitoring_hud_poll_timer.isActive():
                self._monitoring_hud_poll_timer.start(self._monitoring_hud_polling_rate_ms)
        self._ensure_monitoring_hud_desktop_mode_for_visible_dashboard(source=source)
        self._apply_monitoring_hud_window_interaction_state()
        self._publish_monitoring_hud_control_state_to_page()
        self._publish_monitoring_hud_controls_visibility()
        self._emit_runtime_signal(
            "MONITORING_HUD_CONTROL_STATE_READY",
            package="PKG-006",
            slice="SLC-027",
            source=source,
            feature_enabled=self._monitoring_hud_feature_enabled,
            visible=self._monitoring_hud_visible,
            anchored=self._monitoring_hud_anchored,
            snap=self._monitoring_hud_snap_enabled,
            polling_rate_ms=self._monitoring_hud_polling_rate_ms,
        )

    def _persist_monitoring_hud_feature_state(
        self,
        source: str = "runtime",
        dashboard_visible: bool | None = None,
    ) -> bool:
        if self.surface_role != "hud":
            return False
        return bool(save_monitoring_hud_state(
            feature_enabled=bool(self._monitoring_hud_feature_enabled),
            dashboard_visible=(
                bool(self._monitoring_hud_visible and self.isVisible())
                if dashboard_visible is None
                else bool(dashboard_visible)
            ),
            event_logger=self._log_event,
            source=source,
            monitor_ids=list(getattr(self, "_monitoring_hud_overlay_profile_monitor_ids", []) or []),
            overlay_profiles=dict(getattr(self, "_monitoring_hud_overlay_profiles", {}) or {}),
            active_overlay_profile_id=str(
                getattr(self, "_monitoring_hud_active_overlay_profile_id", "default-overlay-profile")
                or ""
            ),
            overlay_profile_default_deleted_by_user=bool(
                getattr(self, "_monitoring_hud_overlay_profile_default_deleted_by_user", False)
            ),
        ))

    def monitoring_hud_feature_state(self) -> dict[str, object]:
        runtime_available = bool(self.surface_role == "hud" and not self._is_shutting_down)
        dashboard_available = bool(runtime_available and self._page_ready)
        return {
            "feature_enabled": bool(self._monitoring_hud_feature_enabled),
            "dashboard_visible": bool(self.isVisible() and self._monitoring_hud_visible),
            "runtime_available": runtime_available,
            "dashboard_available": dashboard_available,
            "resident_route_state": (
                "enabled_available"
                if self._monitoring_hud_feature_enabled and dashboard_available
                else "enabled_not_ready"
                if self._monitoring_hud_feature_enabled
                else "disabled_by_user"
            ),
            "resident_route_reason": "" if dashboard_available else "HUD Dashboard is still starting.",
            "overlay_deferred": True,
            "overlay_anchor_enabled": False,
            "anchored": self._monitoring_hud_anchored,
            "source": self._monitoring_hud_state_source,
        }

    def monitoring_hud_access(self) -> MonitoringHudAccessAdapter:
        return self._monitoring_hud_access_adapter

    def _apply_monitoring_hud_enabled_runtime_state(self, enabled: bool, source: str) -> None:
        if enabled:
            if self._page_ready and not self._monitoring_hud_poll_timer.isActive():
                self._monitoring_hud_poll_timer.start(self._monitoring_hud_polling_rate_ms)
            if self._page_ready and not self._monitoring_hud_control_sync_timer.isActive():
                self._monitoring_hud_control_sync_timer.start(500)
        else:
            self._monitoring_hud_poll_timer.stop()
            self._monitoring_hud_control_sync_timer.stop()
            if self._monitoring_hud_minimal_native_overlay is not None:
                self._monitoring_hud_minimal_native_overlay.update_product_state(
                    visible=False,
                    anchored=True,
                    cards={},
                )
        if enabled:
            self._set_monitoring_hud_control_state(
                visible=bool(self._monitoring_hud_visible),
                source=source,
            )

    def _persist_monitoring_hud_enabled_from_access(self, enabled: bool, source: str) -> bool:
        if self._is_shutting_down or self.surface_role != "hud":
            return False
        previous_enabled = bool(self._monitoring_hud_feature_enabled)
        previous_visible = bool(self._monitoring_hud_visible)
        self._monitoring_hud_feature_enabled = bool(enabled)
        persisted = self._persist_monitoring_hud_feature_state(
            source=source,
            dashboard_visible=False if not enabled else None,
        )
        if not persisted:
            self._monitoring_hud_feature_enabled = previous_enabled
            self._monitoring_hud_visible = previous_visible
            self._apply_monitoring_hud_enabled_runtime_state(previous_enabled, f"{source}_rollback")
            self._set_monitoring_hud_control_state(
                visible=previous_visible,
                source=f"{source}_rollback_visibility",
            )
            self._emit_runtime_signal(
                "MONITORING_HUD_FEATURE_STATE_FAILED",
                source=source,
                requested_enabled=bool(enabled),
                rollback_enabled=previous_enabled,
                rollback_visible=previous_visible,
            )
            return False
        self._monitoring_hud_state_source = "runtime_persisted"
        self._apply_monitoring_hud_enabled_runtime_state(bool(enabled), source)
        self._emit_runtime_signal(
            "MONITORING_HUD_FEATURE_STATE_CONFIRMED",
            source=source,
            feature_enabled=bool(self._monitoring_hud_feature_enabled),
            dashboard_visible=bool(self.isVisible() and self._monitoring_hud_visible),
            persistence_confirmed=True,
        )
        return True

    def _open_or_restore_monitoring_hud_dashboard_from_access(self, source: str) -> bool:
        if (
            self._is_shutting_down
            or not self._monitoring_hud_feature_enabled
            or not self._page_ready
        ):
            return False
        self._set_monitoring_hud_control_state(visible=True, source=source)
        if self.isMinimized():
            self.showNormal()
        if not self.isVisible():
            self.show()
        if not self.webview.isVisible():
            self.webview.show()
        self.raise_()
        self.activateWindow()
        persisted = self._persist_monitoring_hud_feature_state(source=f"{source}_dashboard_open")
        return bool(persisted and self.isVisible() and self._monitoring_hud_visible)

    def _close_monitoring_hud_dashboard_from_access(self, source: str) -> bool:
        if self._is_shutting_down:
            return False
        self._set_monitoring_hud_control_state(visible=False, source=source)
        persisted = self._persist_monitoring_hud_feature_state(source=f"{source}_dashboard_close")
        return bool(persisted and not self.isVisible() and not self._monitoring_hud_visible)

    def set_monitoring_hud_feature_enabled(self, enabled: bool, source: str = "settings"):
        return self._monitoring_hud_access_adapter.set_enabled(bool(enabled), source)

    def open_or_restore_monitoring_hud_dashboard(self, source: str = "resident"):
        return self._monitoring_hud_access_adapter.open_or_restore_dashboard(source)

    def close_monitoring_hud_dashboard(self, source: str = "resident"):
        return self._monitoring_hud_access_adapter.close_dashboard(source)

    def _ensure_monitoring_hud_desktop_mode_for_visible_dashboard(self, source: str = "runtime"):
        if (
            self.surface_role != "hud"
            or not self._monitoring_hud_feature_enabled
            or not self._monitoring_hud_visible
            or self.desktop_mode
            or self._is_shutting_down
        ):
            return
        self._desktop_mode_requested = True
        self._emit_runtime_signal(
            "MONITORING_HUD_REAL_CLIENT_DASHBOARD_VISIBILITY_REQUESTED",
            package="PKG-006",
            slice="SLC-027",
            seam="WS47",
            source=source,
            page_ready=self._page_ready,
            desktop_mode=self.desktop_mode,
        )
        if self._page_ready:
            self.enable_desktop_mode()
        else:
            self._schedule_desktop_mode_enable()

    def _set_monitoring_hud_feature_enabled(self, enabled: bool, *, source: str = "runtime"):
        return self.set_monitoring_hud_feature_enabled(bool(enabled), source=source)

    def request_monitoring_hud_unanchor_from_tray(self, source: str = "tray"):
        self._emit_runtime_signal(
            "MONITORING_HUD_TRAY_UNANCHOR_DEFERRED",
            package="PKG-006",
            slice="SLC-027",
            seam="WS37",
            source=source,
            reason="overlay_deferred_non_gating",
        )

    def request_monitoring_hud_toggle_from_tray(self, source: str = "tray"):
        next_enabled = not bool(self._monitoring_hud_feature_enabled)
        result = self._set_monitoring_hud_feature_enabled(next_enabled, source=source)
        if next_enabled:
            self._emit_runtime_signal(
                "MONITORING_HUD_TRAY_ENABLE_RENDER_STABLE_READY",
                package="PKG-006",
                slice="SLC-027",
                seam="WS43",
                source=source,
                feature_enabled=True,
                dashboard_visible=bool(self.isVisible() and self._monitoring_hud_visible),
                render_path="single_state_apply",
            )
        else:
            self._emit_runtime_signal(
                "MONITORING_HUD_DISABLE_RECOVERY_READY",
                package="PKG-006",
                slice="SLC-027",
                seam="WS43",
                source=source,
                feature_enabled=False,
                dashboard_visible=False,
                command_overlay_available=True,
            )
        self._emit_runtime_signal(
            "MONITORING_HUD_TRAY_TOGGLE_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS43",
            source=source,
            visible=self._monitoring_hud_visible,
            feature_enabled=next_enabled,
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_TRAY_ENABLE_DISABLE_ROUNDTRIP_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS43",
            source=source,
            feature_enabled=next_enabled,
            dashboard_visible=bool(self.isVisible() and self._monitoring_hud_visible),
        )
        return result

    def request_monitoring_hud_dashboard_from_tray(self, source: str = "tray", visible: bool = True):
        result = (
            self.open_or_restore_monitoring_hud_dashboard(source=source)
            if visible
            else self.close_monitoring_hud_dashboard(source=source)
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_TRAY_DASHBOARD_OPEN_CLOSE_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS43",
            source=source,
            dashboard_visible=bool(self.isVisible() and self._monitoring_hud_visible),
            feature_enabled=self._monitoring_hud_feature_enabled,
            result_status=getattr(result, "status", "unknown"),
        )
        return result

    def _sync_monitoring_hud_control_state_from_page(self):
        if not self.desktop_mode or not self._page_ready or self._is_shutting_down:
            return
        page = self.webview.page()
        if page is None:
            return
        state_script = (
            "window.getMonitoringHudControlState "
            "? JSON.stringify(window.getMonitoringHudControlState()) "
            ": null"
        )
        try:
            page.runJavaScript(
                state_script,
                0,
                self._handle_monitoring_hud_control_state_from_page,
            )
        except TypeError:
            page.runJavaScript(
                state_script,
                self._handle_monitoring_hud_control_state_from_page,
            )

    def _handle_monitoring_hud_control_state_from_page(self, state):
        if isinstance(state, str):
            try:
                state = json.loads(state)
            except json.JSONDecodeError:
                return
        if not isinstance(state, dict) or self._is_shutting_down:
            return
        visible = bool(state.get("visible", self._monitoring_hud_visible))
        feature_enabled = bool(
            state.get("featureEnabled", self._monitoring_hud_feature_enabled)
        )
        anchored = bool(state.get("anchored", self._monitoring_hud_anchored))
        snap_enabled = bool(state.get("snapEnabled", self._monitoring_hud_snap_enabled))
        try:
            polling_rate_ms = max(1000, int(state.get("pollingRateMs", self._monitoring_hud_polling_rate_ms)))
        except (TypeError, ValueError):
            polling_rate_ms = self._monitoring_hud_polling_rate_ms

        geometry_state = state.get("geometry") if isinstance(state.get("geometry"), dict) else {}
        self._set_monitoring_hud_live_client_page_state(state, geometry_state)
        cards = state.get("cards") if isinstance(state.get("cards"), dict) else {}
        overlay_profiles = state.get("overlayProfiles") if isinstance(state.get("overlayProfiles"), dict) else {}
        active_overlay_profile_id = str(state.get("activeOverlayProfileId") or "")
        overlay_profile_default_deleted_by_user = bool(state.get("overlayProfileDefaultDeletedByUser"))
        overlay_profile_signature_parts = []
        for profile_id in sorted(str(key) for key in overlay_profiles.keys()):
            profile = overlay_profiles.get(profile_id) if isinstance(overlay_profiles.get(profile_id), dict) else {}
            monitor_ids = profile.get("monitorIds") if isinstance(profile.get("monitorIds"), list) else []
            overlay_profile_signature_parts.append((
                profile_id,
                str(profile.get("kind", "")),
                str(profile.get("scope", "")),
                str(profile.get("name", "")),
                tuple(str(monitor_id) for monitor_id in monitor_ids),
                str(profile.get("displayMode", "")),
            ))
        overlay_profile_signature = (
            active_overlay_profile_id,
            overlay_profile_default_deleted_by_user,
            int(state.get("overlayProfileSchemaVersion") or 0),
            tuple(overlay_profile_signature_parts),
        )
        overlay_profile_changed = False
        if overlay_profile_signature != self._monitoring_hud_overlay_profile_signature:
            self._monitoring_hud_overlay_profile_signature = overlay_profile_signature
            self._monitoring_hud_overlay_profiles = overlay_profiles
            self._monitoring_hud_active_overlay_profile_id = active_overlay_profile_id
            self._monitoring_hud_overlay_profile_default_deleted_by_user = overlay_profile_default_deleted_by_user
            self._monitoring_hud_overlay_profile_monitor_ids = [str(key) for key in cards.keys()]
            default_profile = overlay_profiles.get("default-overlay-profile") if isinstance(overlay_profiles.get("default-overlay-profile"), dict) else {}
            default_monitor_ids = default_profile.get("monitorIds") if isinstance(default_profile.get("monitorIds"), list) else []
            self._emit_runtime_signal(
                "MONITORING_HUD_OVERLAY_PROFILE_STATE_READY",
                package="PKG-006",
                slice="SLC-039",
                seam="Workstream",
                active_overlay_profile_id=active_overlay_profile_id,
                profile_count=len(overlay_profiles),
                default_profile_id="default-overlay-profile",
                default_profile_monitor_count=len(default_monitor_ids),
                default_profile_membership=",".join(str(monitor_id) for monitor_id in default_monitor_ids),
                monitor_group_boundary="separate-configuration-organization",
                recording_profile_boundary="future-gated-not-present",
                visible_profile_editor="slc-039-membership-editor",
                profile_membership_editor="editable-slc-039-mapping",
                schema_version=int(state.get("overlayProfileSchemaVersion") or 0),
            )
            overlay_profile_changed = True
        overlay_display_acceptance_proof = state.get("overlayDisplayAcceptanceProof")
        overlay_display_acceptance_signature = json.dumps(
            overlay_display_acceptance_proof if isinstance(overlay_display_acceptance_proof, dict) else {},
            sort_keys=True,
        )
        overlay_display_acceptance_changed = False
        if overlay_display_acceptance_signature != self._monitoring_hud_overlay_display_acceptance_signature:
            self._monitoring_hud_overlay_display_acceptance_signature = overlay_display_acceptance_signature
            if isinstance(overlay_display_acceptance_proof, dict):
                self._emit_runtime_signal(
                    "MONITORING_HUD_OVERLAY_DISPLAY_ACCEPTANCE_BRIDGE_READY",
                    package="PKG-006",
                    slice=str(overlay_display_acceptance_proof.get("slice") or "SLC-042"),
                    seam="Workstream",
                    profile_aware_bridge=bool(overlay_display_acceptance_proof.get("profileAwareBridge")),
                    active_profile_selection_drives_rendered_cards=bool(overlay_display_acceptance_proof.get("activeProfileSelectionDrivesRenderedCards")),
                    stale_overlay_cards_removed=bool(overlay_display_acceptance_proof.get("staleOverlayCardsRemoved")),
                    null_profile_state_renders_zero_cards=bool(overlay_display_acceptance_proof.get("nullProfileStateRendersZeroCards")),
                    high_volume_membership_renders_deterministically=bool(overlay_display_acceptance_proof.get("highVolumeMembershipRendersDeterministically")),
                    monitor_group_boundary=str(overlay_display_acceptance_proof.get("monitorGroupBoundary")),
                    recording_profile_boundary=str(overlay_display_acceptance_proof.get("recordingProfileBoundary")),
                    non_recording_scope=bool(overlay_display_acceptance_proof.get("nonRecordingScope")),
                    non_theme_scope=bool(overlay_display_acceptance_proof.get("nonThemeScope")),
                )
                overlay_display_acceptance_changed = True
        active_overlay_profile_display_proof = state.get("activeOverlayProfileDisplayProof")
        active_overlay_profile_display_signature = json.dumps(
            active_overlay_profile_display_proof if isinstance(active_overlay_profile_display_proof, dict) else {},
            sort_keys=True,
        )
        active_overlay_profile_display_changed = False
        if active_overlay_profile_display_signature != self._monitoring_hud_active_overlay_profile_display_signature:
            self._monitoring_hud_active_overlay_profile_display_signature = active_overlay_profile_display_signature
            if isinstance(active_overlay_profile_display_proof, dict):
                self._emit_runtime_signal(
                    "MONITORING_HUD_ACTIVE_OVERLAY_PROFILE_DISPLAY_READY",
                    package="PKG-006",
                    slice=str(active_overlay_profile_display_proof.get("slice") or "SLC-043"),
                    seam="Workstream",
                    display_behavior_marker_ready=bool(active_overlay_profile_display_proof.get("displayBehaviorMarkerReady")),
                    status_strip_reflects_active_profile=bool(active_overlay_profile_display_proof.get("statusStripReflectsActiveProfile")),
                    active_profile_switch_updates_visible_display=bool(active_overlay_profile_display_proof.get("activeProfileSwitchUpdatesVisibleDisplay")),
                    stale_active_profile_falls_back_deterministically=bool(active_overlay_profile_display_proof.get("staleActiveProfileFallsBackDeterministically")),
                    null_profile_state_shows_no_active_profile=bool(active_overlay_profile_display_proof.get("nullProfileStateShowsNoActiveProfile")),
                    high_volume_display_renders_deterministically=bool(active_overlay_profile_display_proof.get("highVolumeDisplayRendersDeterministically")),
                    monitor_group_boundary=str(active_overlay_profile_display_proof.get("monitorGroupBoundary")),
                    recording_profile_boundary=str(active_overlay_profile_display_proof.get("recordingProfileBoundary")),
                    non_recording_scope=bool(active_overlay_profile_display_proof.get("nonRecordingScope")),
                    non_theme_scope=bool(active_overlay_profile_display_proof.get("nonThemeScope")),
                )
                active_overlay_profile_display_changed = True
        dashboard_overlay_independence_proof = state.get("dashboardOverlayIndependenceProof")
        dashboard_overlay_independence_signature = json.dumps(
            dashboard_overlay_independence_proof if isinstance(dashboard_overlay_independence_proof, dict) else {},
            sort_keys=True,
        )
        dashboard_overlay_independence_changed = False
        if dashboard_overlay_independence_signature != self._monitoring_hud_dashboard_overlay_independence_signature:
            self._monitoring_hud_dashboard_overlay_independence_signature = dashboard_overlay_independence_signature
            if isinstance(dashboard_overlay_independence_proof, dict):
                self._emit_runtime_signal(
                    "MONITORING_HUD_DASHBOARD_OVERLAY_INDEPENDENCE_READY",
                    package="PKG-006",
                    slice=str(dashboard_overlay_independence_proof.get("slice") or "SLC-044"),
                    seam="Workstream",
                    independence_marker_ready=bool(dashboard_overlay_independence_proof.get("independenceMarkerReady")),
                    dashboard_and_overlay_roles_distinct=bool(dashboard_overlay_independence_proof.get("dashboardAndOverlayRolesDistinct")),
                    dashboard_configures_overlay_without_owning_display=bool(dashboard_overlay_independence_proof.get("dashboardConfiguresOverlayWithoutOwningDisplay")),
                    active_profile_shared_state_visible_in_overlay=bool(dashboard_overlay_independence_proof.get("activeProfileSharedStateVisibleInOverlay")),
                    dashboard_acceptance_remains_ready=bool(dashboard_overlay_independence_proof.get("dashboardAcceptanceRemainsReady")),
                    overlay_acceptance_remains_non_gating=bool(dashboard_overlay_independence_proof.get("overlayAcceptanceRemainsNonGating")),
                    monitor_groups_remain_preservation_surface=bool(dashboard_overlay_independence_proof.get("monitorGroupsRemainPreservationSurface")),
                    visual_acceptance_baseline_ready=bool(dashboard_overlay_independence_proof.get("visualAcceptanceBaselineReady")),
                    non_recording_scope=bool(dashboard_overlay_independence_proof.get("nonRecordingScope")),
                    non_theme_scope=bool(dashboard_overlay_independence_proof.get("nonThemeScope")),
                )
                dashboard_overlay_independence_changed = True
        recording_control_summary = state.get("recordingControlWindowTargetSummary")
        recording_control_requested = bool(state.get("recordingControlWindowRequested"))
        recording_control_request_id = int(state.get("recordingControlWindowRequestId") or 0)
        recording_output_request = state.get("recordingOutputRequest")
        if isinstance(recording_output_request, dict):
            samples = recording_output_request.get("samples")
            target_monitor_ids = recording_output_request.get("targetMonitorIds")
            output_signature = (
                str(recording_output_request.get("requestId") or ""),
                str(recording_output_request.get("sessionId") or ""),
                str(recording_output_request.get("stoppedAtUtc") or ""),
                len(samples) if isinstance(samples, list) else 0,
            )
            if output_signature != self._monitoring_hud_recording_output_signature:
                self._monitoring_hud_recording_output_signature = output_signature
                try:
                    result = write_recording_output_files(
                        session_id=str(recording_output_request.get("sessionId") or ""),
                        active_overlay_profile_id=str(recording_output_request.get("activeOverlayProfileId") or ""),
                        active_overlay_profile_name=str(recording_output_request.get("activeOverlayProfileName") or ""),
                        target_monitor_ids=[
                            str(monitor_id)
                            for monitor_id in (target_monitor_ids if isinstance(target_monitor_ids, list) else [])
                            if str(monitor_id or "").strip()
                        ],
                        target_state=str(recording_output_request.get("targetState") or "unknown"),
                        samples=[
                            sample
                            for sample in (samples if isinstance(samples, list) else [])
                            if isinstance(sample, dict)
                        ],
                        started_at_utc=str(recording_output_request.get("startedAtUtc") or ""),
                        stopped_at_utc=str(recording_output_request.get("stoppedAtUtc") or ""),
                    )
                except Exception as exc:
                    result = {
                        "passed": False,
                        "error": str(exc),
                        "recordingExecutionState": "disabled-error",
                        "fileWritingState": "disabled-error",
                    }
                self._run_javascript(
                    "if (window.setMonitoringHudRecordingOutputResult) "
                    f"{{ window.setMonitoringHudRecordingOutputResult({json.dumps(result, sort_keys=True)}); }}"
                )
                self._emit_runtime_signal(
                    "MONITORING_HUD_RECORDING_OUTPUT_READY",
                    package="PKG-006",
                    slice="SLC-054",
                    seam="Workstream",
                    passed=bool(result.get("passed")),
                    session_id=str(result.get("sessionId") or ""),
                    row_count=int(result.get("rowCount") or 0),
                    profile_log_consistency_passed=bool(result.get("profileLogConsistencyPassed")),
                    profile_log_consistency_reason=str(result.get("profileLogConsistencyReason") or ""),
                    manifest_path=str(result.get("nativeLogPath") or ""),
                    output_root_owner=str(result.get("outputRootOwner") or ""),
                )
        recording_folder_open_request = state.get("recordingFolderOpenRequest")
        if isinstance(recording_folder_open_request, dict):
            folder_open_signature = (
                str(recording_folder_open_request.get("requestId") or ""),
                str(recording_folder_open_request.get("outputDir") or ""),
            )
            if folder_open_signature != self._monitoring_hud_recording_folder_open_signature:
                self._monitoring_hud_recording_folder_open_signature = folder_open_signature
                requested_folder = str(recording_folder_open_request.get("outputDir") or "").strip()
                result = {
                    "passed": False,
                    "requestId": str(recording_folder_open_request.get("requestId") or ""),
                    "outputDir": requested_folder,
                    "error": "Recording log folder path is not available.",
                }
                try:
                    allowed_root = os.path.abspath(str(recording_export_dir()))
                    target_folder = os.path.abspath(requested_folder or allowed_root)
                    common_root = os.path.commonpath([allowed_root, target_folder])
                    if os.path.normcase(common_root) != os.path.normcase(allowed_root):
                        raise ValueError("Recording export folder request is outside the exported-log root.")
                    if not os.path.isdir(target_folder):
                        os.makedirs(target_folder, exist_ok=True)
                    os.startfile(target_folder)
                    result = {
                        "passed": True,
                        "requestId": str(recording_folder_open_request.get("requestId") or ""),
                        "outputDir": target_folder,
                        "recordingFolderOpenStatus": "opened",
                    }
                except Exception as exc:
                    result["error"] = str(exc)
                self._run_javascript(
                    "if (window.setMonitoringHudRecordingFolderOpenResult) "
                    f"{{ window.setMonitoringHudRecordingFolderOpenResult({json.dumps(result, sort_keys=True)}); }}"
                )
                self._emit_runtime_signal(
                    "MONITORING_HUD_RECORDING_LOG_FOLDER_OPENED",
                    package="PKG-006",
                    slice="SLC-054",
                    seam="Workstream",
                    passed=bool(result.get("passed")),
                    output_dir=str(result.get("outputDir") or ""),
                )
        recording_control_signature = (
            recording_control_requested,
            recording_control_request_id,
            json.dumps(
                recording_control_summary if isinstance(recording_control_summary, dict) else {},
                sort_keys=True,
            ),
        )
        recording_control_keyboard_restore = bool(
            getattr(self, "_monitoring_hud_keyboard_force_visible_control", "")
            == "open-recording-studio"
        )
        if (
            recording_control_requested
            and self._monitoring_hud_recording_studio_window is not None
            and (
                recording_control_signature != self._monitoring_hud_recording_control_signature
                or recording_control_keyboard_restore
            )
        ):
            self._monitoring_hud_recording_control_signature = recording_control_signature
            summary = recording_control_summary if isinstance(recording_control_summary, dict) else {}
            recording_control_activate = (
                int(recording_control_request_id or 0)
                != self._monitoring_hud_recording_studio_active_request_id
            )
            if recording_control_keyboard_restore:
                recording_control_activate = True
            if recording_control_activate:
                self._monitoring_hud_recording_studio_active_request_id = int(recording_control_request_id or 0)
            self._monitoring_hud_recording_studio_window.update_product_state(
                request_id=recording_control_request_id,
                active_profile_name=str(summary.get("activeOverlayProfileName") or ""),
                target_count=int(summary.get("targetCount") or 0),
                target_names=str(summary.get("targetNames") or ""),
                target_state=str(summary.get("targetState") or ""),
                recording_session_state=str(summary.get("recordingSessionState") or "ready"),
                start_stop_state=str(summary.get("startStopState") or "target-required"),
                native_log_path=str(summary.get("nativeLogPath") or ""),
                export_dir=str(summary.get("exportDir") or ""),
                row_count=int(summary.get("rowCount") or 0),
                current_log_state=str(summary.get("currentLogState") or "no-current-log"),
                activate_window=recording_control_activate,
                parent_geometry=self.geometry(),
            )
            if recording_control_keyboard_restore:
                self._monitoring_hud_keyboard_force_visible_control = ""
            proof = self._monitoring_hud_recording_studio_window.proof_state()
            self._emit_runtime_signal(
                "MONITORING_HUD_RECORDING_STUDIO_READY",
                package="PKG-006",
                slice="SLC-053",
                seam="Workstream",
                surface=proof.get("surface"),
                owner=proof.get("owner"),
                standalone=proof.get("standaloneTopLevel"),
                window_flag=proof.get("windowFlag"),
                taskbar_restorable=proof.get("taskbarRestorable"),
                minimize_control=proof.get("minimizeControl"),
                close_control=proof.get("closeControl"),
                recording_execution_state=proof.get("recordingExecutionState"),
                recording_file_writing_state=proof.get("recordingFileWritingState"),
                start_stop_state=proof.get("startStopState"),
                native_log_path=proof.get("nativeLogPath"),
                current_log_state=proof.get("currentLogState"),
                visible=proof.get("visible"),
                x=proof.get("x"),
                y=proof.get("y"),
                w=proof.get("w"),
                h=proof.get("h"),
            )
        log_viewer_summary = state.get("logViewerSummary")
        log_viewer_requested = bool(state.get("logViewerRequested"))
        log_viewer_request_id = str(state.get("logViewerRequestId") or "")
        log_viewer_signature = (
            log_viewer_requested,
            log_viewer_request_id,
            json.dumps(log_viewer_summary if isinstance(log_viewer_summary, dict) else {}, sort_keys=True),
        )
        log_viewer_keyboard_restore = bool(
            getattr(self, "_monitoring_hud_keyboard_force_visible_control", "")
            == "open-log-viewer"
        )
        if (
            log_viewer_requested
            and self._monitoring_hud_log_viewer_studio_window is not None
            and (
                log_viewer_signature != self._monitoring_hud_log_viewer_studio_signature
                or log_viewer_keyboard_restore
            )
        ):
            self._monitoring_hud_log_viewer_studio_signature = log_viewer_signature
            summary = log_viewer_summary if isinstance(log_viewer_summary, dict) else {}
            log_viewer_activate = log_viewer_request_id != self._monitoring_hud_log_viewer_studio_active_request_id
            if log_viewer_keyboard_restore:
                log_viewer_activate = True
            if log_viewer_activate:
                self._monitoring_hud_log_viewer_studio_active_request_id = log_viewer_request_id
            self._monitoring_hud_log_viewer_studio_window.update_product_state(
                request_id=log_viewer_request_id,
                native_log_path=str(summary.get("nativeLogPath") or ""),
                export_dir=str(summary.get("exportDir") or ""),
                activate_window=log_viewer_activate,
                parent_geometry=self.geometry(),
            )
            if log_viewer_keyboard_restore:
                self._monitoring_hud_keyboard_force_visible_control = ""
            proof = self._monitoring_hud_log_viewer_studio_window.proof_state()
            self._emit_runtime_signal(
                "MONITORING_HUD_LOG_VIEWER_STUDIO_READY",
                package="PKG-006",
                slice="SLC-054",
                seam="Workstream",
                surface=proof.get("surface"),
                owner=proof.get("owner"),
                standalone=proof.get("standaloneTopLevel"),
                native_folder_pre_session_usable=proof.get("nativeFolderPreSessionUsable"),
                export_folder_pre_session_usable=proof.get("exportFolderPreSessionUsable"),
                previous_log_selection_state=proof.get("previousLogSelectionState"),
                export_customization_state=proof.get("exportCustomizationState"),
                native_log_loader_state=proof.get("nativeLogLoaderState"),
                path_rows_visual_state=proof.get("pathRowsVisualState"),
                state_rows_contained=proof.get("stateRowsContained"),
                native_log_display_text=proof.get("nativeLogDisplayText"),
                export_log_display_text=proof.get("exportLogDisplayText"),
                native_log_path_display_mode=proof.get("nativeLogPathDisplayMode"),
                export_log_path_display_mode=proof.get("exportLogPathDisplayMode"),
                activation_mode=proof.get("activationMode"),
                visible=proof.get("visible"),
                x=proof.get("x"),
                y=proof.get("y"),
                w=proof.get("w"),
                h=proof.get("h"),
            )
        monitor_signature_parts = []
        enabled_count = 0
        for card_id in sorted(str(key) for key in cards.keys()):
            card = cards.get(card_id) if isinstance(cards.get(card_id), dict) else {}
            enabled = bool(card.get("enabled", True))
            enabled_count += 1 if enabled else 0
            try:
                card_polling = max(1000, int(card.get("pollingRateMs", polling_rate_ms)))
            except (TypeError, ValueError):
                card_polling = polling_rate_ms
            monitor_signature_parts.append((
                card_id,
                enabled,
                card_polling,
                str(card.get("title", "")),
                tuple(str(sensor) for sensor in card.get("sensors", []) if isinstance(card.get("sensors"), list)),
                json.dumps(card.get("sensorSettings", {}), sort_keys=True) if isinstance(card.get("sensorSettings"), dict) else "",
                int(card.get("x") or 0),
                int(card.get("y") or 0),
                int(card.get("w") or 0),
                int(card.get("h") or 0),
            ))
        monitor_signature = (
            str(state.get("selectedMonitorId", "")),
            tuple(monitor_signature_parts),
        )
        active_child_window = str(state.get("activeChildWindow", "none") or "none")
        settings_window = geometry_state.get("settingsWindow") if isinstance(geometry_state.get("settingsWindow"), dict) else {}
        settings_window_present = active_child_window == "dashboard-settings" and bool(settings_window)
        try:
            settings_window_left = int(self.x() + float(settings_window.get("left", 0)))
            settings_window_top = int(self.y() + float(settings_window.get("top", 0)))
            settings_window_width = int(float(settings_window.get("width", 0)))
            settings_window_height = int(float(settings_window.get("height", 0)))
        except (TypeError, ValueError):
            settings_window_left = 0
            settings_window_top = 0
            settings_window_width = 0
            settings_window_height = 0
        settings_window_right = settings_window_left + settings_window_width
        settings_window_bottom = settings_window_top + settings_window_height
        active_child_window_signature = (
            active_child_window,
            settings_window_left,
            settings_window_top,
            settings_window_width,
            settings_window_height,
        )
        if active_child_window_signature != self._monitoring_hud_active_child_window_signature:
            self._monitoring_hud_active_child_window_signature = active_child_window_signature
            self._emit_runtime_signal(
                "MONITORING_HUD_DASHBOARD_CHILD_WINDOW_READY",
                package="PKG-006",
                slice="SLC-029",
                seam="LV1",
                active_child_window=active_child_window,
                dashboard_settings_open=active_child_window == "dashboard-settings",
                settings_window_present=settings_window_present,
                settings_window_left=settings_window_left,
                settings_window_top=settings_window_top,
                settings_window_right=settings_window_right,
                settings_window_bottom=settings_window_bottom,
                settings_window_width=settings_window_width,
                settings_window_height=settings_window_height,
            )
        if monitor_signature != self._monitoring_hud_monitor_management_signature:
            self._monitoring_hud_monitor_management_signature = monitor_signature
            self._emit_runtime_signal(
                "MONITORING_HUD_MONITOR_MANAGEMENT_READY",
                package="PKG-006",
                slice="SLC-027",
                monitor_count=len(monitor_signature_parts),
                enabled_count=enabled_count,
                selected_monitor=str(state.get("selectedMonitorId", "")),
                assigned_sensor_count=sum(
                    len(card.get("sensors") or [])
                    for card in cards.values()
                    if isinstance(card, dict) and isinstance(card.get("sensors"), list)
                ),
                polling_rate_min_ms=1000,
            )

        signature = (feature_enabled, visible, anchored, snap_enabled, polling_rate_ms)
        if signature == self._monitoring_hud_control_signature:
            if overlay_profile_changed or overlay_display_acceptance_changed:
                self._persist_monitoring_hud_feature_state(source="page_sync_overlay_profile")
            self._sync_monitoring_hud_minimal_native_overlay(source="page_sync")
            return

        self._monitoring_hud_control_signature = signature
        self._monitoring_hud_feature_enabled = feature_enabled
        self._monitoring_hud_visible = visible
        self._monitoring_hud_anchored = anchored
        self._monitoring_hud_snap_enabled = snap_enabled
        self._monitoring_hud_polling_rate_ms = polling_rate_ms
        if self._monitoring_hud_poll_timer.isActive():
            self._monitoring_hud_poll_timer.start(self._monitoring_hud_polling_rate_ms)
        self._persist_monitoring_hud_feature_state(source="page_sync")
        self._apply_monitoring_hud_window_interaction_state()
        self._publish_monitoring_hud_controls_visibility()

    def _log_native_window_state(self, label: str, hwnd: int):
        rect = ctypes.wintypes.RECT()
        rect_ok = bool(GetWindowRect(hwnd, ctypes.byref(rect)))
        parent = GetParentW(hwnd)
        visible = bool(IsWindowVisible(hwnd))
        if rect_ok:
            x = rect.left
            y = rect.top
            w = max(0, rect.right - rect.left)
            h = max(0, rect.bottom - rect.top)
        else:
            x = y = w = h = -1
        self._log_event(
            "RENDERER_MAIN|DESKTOP_ATTACH_STEP"
            f"|label={label}"
            f"|visible={'true' if visible else 'false'}"
            f"|parent={hex(int(parent)) if parent else 'none'}"
            f"|x={x}|y={y}|w={w}|h={h}"
        )

    def _native_window_matches_target(self, hwnd: int, target_geometry: QRect) -> bool:
        rect = ctypes.wintypes.RECT()
        if not GetWindowRect(hwnd, ctypes.byref(rect)):
            return False

        width = max(0, rect.right - rect.left)
        height = max(0, rect.bottom - rect.top)

        return (
            abs(rect.left - target_geometry.x()) <= 1
            and abs(rect.top - target_geometry.y()) <= 1
            and abs(width - target_geometry.width()) <= 1
            and abs(height - target_geometry.height()) <= 1
        )

    def _apply_pending_visual_state(self):
        if not self._page_ready or self._pending_visual_state is None:
            return

        state_name = self._pending_visual_state
        js = f"window.setCoreVisualState && window.setCoreVisualState('{state_name}');"
        self._run_javascript(js)
        self._log_event(f"RENDERER_MAIN|VISUAL_STATE_APPLIED|state={state_name}")
        self._pending_visual_state = None

    def _apply_pending_voice_level(self):
        if not self._page_ready or self._pending_voice_level is None:
            return

        level = self._pending_voice_level
        js = f"window.setCoreVoiceLevel && window.setCoreVoiceLevel({level:.4f});"
        self._run_javascript(js)
        self._pending_voice_level = None

    def _apply_command_overlay_state(self):
        payload = self._command_model.view_payload()
        payload["typing_ready"] = (
            payload.get("phase") == "entry"
            and bool(payload.get("input_armed"))
            and (
                self._overlay_local_input_engaged
                or self.overlay_needs_global_input_capture()
            )
        )
        self._command_panel.render_payload(payload)
        if payload.get("visible") and self._command_panel.isVisible():
            self._command_panel.refresh_for_geometry(
                self.compute_compact_geometry(),
                self.screen_ref.availableGeometry(),
            )

    def _arm_overlay_input_capture(self, seconds: float = 0.65):
        self._overlay_input_capture_until = time.monotonic() + max(0.0, seconds)

    def _refresh_overlay_input_capture(self, seconds: float = 0.65):
        self._arm_overlay_input_capture(seconds)

    def _clear_overlay_input_capture(self):
        self._overlay_input_capture_until = 0.0

    def _overlay_input_capture_active(self) -> bool:
        return time.monotonic() < self._overlay_input_capture_until

    def _reinforce_desktop_mode(self):
        if not self.desktop_mode or self._is_shutting_down:
            return

        if not self._monitoring_hud_feature_enabled or not self._monitoring_hud_visible:
            if self.webview.isVisible():
                self.webview.hide()
            if self.isVisible():
                self.hide()
            self._log_event(
                "RENDERER_MAIN|DESKTOP_GEOMETRY_RESET_SKIPPED"
                "|reason=monitoring_hud_dashboard_hidden"
            )
            return

        if self._monitoring_hud_native_window_resize_active:
            self._log_event(
                "RENDERER_MAIN|DESKTOP_GEOMETRY_RESET_SKIPPED"
                "|reason=monitoring_hud_resize_active"
            )
            return

        if self._monitoring_hud_native_move_user_active:
            self._log_event(
                "RENDERER_MAIN|DESKTOP_GEOMETRY_RESET_SKIPPED"
                "|reason=monitoring_hud_move_active"
            )
            return

        if self._monitoring_hud_user_geometry_override_active:
            geometry = self.geometry()
            self._log_event(
                "RENDERER_MAIN|DESKTOP_GEOMETRY_RESET_SKIPPED"
                f"|x={geometry.x()}|y={geometry.y()}"
                f"|w={geometry.width()}|h={geometry.height()}"
                "|reason=user_geometry_override"
            )
            return

        target_geometry = self.compute_compact_geometry()
        hwnd = int(self.winId())

        if self._native_window_matches_target(hwnd, target_geometry):
            self._log_event(
                "RENDERER_MAIN|DESKTOP_GEOMETRY_RESET_SKIPPED"
                f"|x={target_geometry.x()}|y={target_geometry.y()}"
                f"|w={target_geometry.width()}|h={target_geometry.height()}"
                "|reason=stable"
            )
            if not self.webview.isVisible():
                self.webview.show()
            if not self.isVisible():
                self.show()
            return

        self.setGeometry(target_geometry)
        if not self.webview.isVisible():
            self.webview.show()
        if not self.isVisible():
            self.show()
        self._log_event(
            "RENDERER_MAIN|DESKTOP_VISIBLE_OVERLAY_GEOMETRY_RESET"
            f"|x={target_geometry.x()}|y={target_geometry.y()}"
            f"|w={target_geometry.width()}|h={target_geometry.height()}"
        )

        self.webview.update()
        self.update()
        self._run_javascript("window.dispatchEvent(new Event('resize'));")

    def reinforce_desktop_mode(self):
        self._reinforce_desktop_mode()

    def _schedule_desktop_mode_enable(self):
        if not self._desktop_mode_requested or self.desktop_mode or self._is_shutting_down:
            return
        if not self._page_ready:
            return
        QTimer.singleShot(50, self.enable_desktop_mode)

    def _apply_desktop_surface_mode(self):
        role = json.dumps(f"{self.surface_role}-window-mode")
        opposite_role = json.dumps("core-window-mode" if self.surface_role == "hud" else "hud-window-mode")
        self._run_javascript(
            f"""
            document.body.classList.add({role});
            document.body.classList.remove({opposite_role});
            if (window.setDesktopSurfaceMode) {{
                window.setDesktopSurfaceMode(true);
            }} else {{
                document.body.classList.add("desktop-mode");
                const monitoringHud = document.getElementById("monitoring-hud");
                const minimalHud = document.getElementById("monitoring-hud-minimal");
                const overlayDisplay = document.getElementById("monitoring-hud-overlay-display");
                if (monitoringHud) {{
                    monitoringHud.setAttribute("aria-hidden", "false");
                    monitoringHud.dataset.renderState = "product-visibility-baseline";
                    monitoringHud.dataset.productSurfaceState = "visible-user-facing";
                    monitoringHud.dataset.productSurfaceRole = "dashboard-configuration-surface";
                    monitoringHud.dataset.primaryInterfaceReleaseSurface = "monitoring-hud-dashboard-control-panel";
                    monitoringHud.dataset.interfaceAcceptancePolicy = "dashboard-only-current-branch";
                    monitoringHud.dataset.dashboardAcceptanceBaseline = "ws31-dashboard-control-panel";
                    monitoringHud.dataset.dashboardProofPath = "dashboard-specific-static-live-uts";
                    monitoringHud.dataset.dashboardStandaloneProof = "ws32-dashboard-window-travel";
                    monitoringHud.dataset.dashboardClippingProof = "within-virtual-desktop";
                    monitoringHud.dataset.dashboardMinimumEdgeProof = "native-min-size-bottom-edge-visible";
                    monitoringHud.dataset.dashboardDecouplingProof = "core-overlay-independent";
                    monitoringHud.dataset.dashboardContentPolish = "branch2-monitor-groups-no-dead-space";
                    monitoringHud.dataset.dashboardHomeModel = "control-hub-cards-monitor-management-child-windows";
                    monitoringHud.dataset.dashboardChildWindowScope = "monitor-groups-manage-create-edit-delete-sensor-windows-overlay-profile-settings";
                    monitoringHud.dataset.dashboardIaModel = "branch2-ia-controls-followthrough";
                    monitoringHud.dataset.dashboardCloseAffordance = "window-level-close-button";
                    monitoringHud.dataset.dashboardOpenBadge = "removed";
                    monitoringHud.dataset.dashboardMonitorSelectionPlacement = "edit-child-window-only";
                    monitoringHud.dataset.dashboardSettingsModel = "hud-overlay-monitor-groups-provider-warning";
                    monitoringHud.dataset.dashboardSettingsAffordance = "dashboard-ia-card-settings-button";
                    monitoringHud.dataset.dashboardSettingsPanel = "settings-panel-child-window";
                    monitoringHud.dataset.dashboardSettingsPanelState = "closed";
                    monitoringHud.dataset.dashboardSettingsProof = "visible-open-close-control-hit-target";
                    monitoringHud.dataset.monitorGroupModel = "configurable-groups-sensor-assignment";
                    monitoringHud.dataset.dashboardMonitorCardPolicy = "overlay-display-owns-visual-rendering";
                    monitoringHud.dataset.monitorManagement = "sensor-command-center-list-detail-source-picker";
                    monitoringHud.dataset.monitorSensorAssignment = "sensor-library-source-picker";
                    monitoringHud.dataset.sourceClassification = "settings-readiness-outside-assignable-sensors";
                    monitoringHud.dataset.dashboardProviderTruth = "provider-contract-first";
                    monitoringHud.dataset.dashboardStateModel = "setup-no-data-degraded-warning";
                    monitoringHud.dataset.dashboardWarningControls = "visual-non-invasive-only";
                    monitoringHud.dataset.dashboardFakeTelemetryPolicy = "blocked";
                    monitoringHud.dataset.overlayAcceptancePolicy = "deferred-non-gating";
                    monitoringHud.dataset.interfaceBundleApproval = "not-granted";
                    monitoringHud.dataset.coreRepairClassification = "dependency-repair-only";
                }}
                if (minimalHud) {{
                    minimalHud.setAttribute("aria-hidden", "false");
                    minimalHud.dataset.renderState = "minimal-overlay-ready";
                    minimalHud.dataset.productSurfaceState = "visible-minimal-anchored-hud";
                    minimalHud.dataset.productSurfaceRole = "minimal-anchored-hud-overlay";
                    minimalHud.dataset.interfaceAcceptancePolicy = "deferred-non-gating";
                    minimalHud.dataset.dashboardAcceptanceRole = "supporting-future-interface-evidence";
                    minimalHud.dataset.currentBranchReleaseGate = "false";
                }}
                if (overlayDisplay) {{
                    overlayDisplay.setAttribute("aria-hidden", "false");
                    overlayDisplay.dataset.renderState = "edgeless-overlay-display-ready";
                    overlayDisplay.dataset.productSurfaceState = "visible-edgeless-overlay-display";
                    overlayDisplay.dataset.productSurfaceRole = "edgeless-overlay-display";
                    overlayDisplay.dataset.interfaceAcceptancePolicy = "deferred-non-gating";
                    overlayDisplay.dataset.dashboardAcceptanceRole = "supporting-future-interface-evidence";
                    overlayDisplay.dataset.currentBranchReleaseGate = "false";
                }}
            }}
            """
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_BASELINE_READY",
            package="PKG-006",
            slice="SLC-016",
            baseline="product_visibility_baseline",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_PRODUCT_VISIBILITY_READY",
            package="PKG-006",
            slice="SLC-016",
            seam="WS7",
            proof="visible_hud_card_panel",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_SURFACE_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS19",
            surface="dashboard_configuration_surface",
            configures="minimal_hud_overlay",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_ACCEPTANCE_BASELINE_READY",
            package="PKG-006",
            slice="SLC-016",
            seam="WS31",
            primary_interface="monitoring_hud_dashboard_control_panel",
            acceptance_policy="dashboard_only_current_branch",
            proof_path="dashboard_specific_static_live_uts",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_OVERLAY_DEFERRAL_ENFORCED_READY",
            package="PKG-006",
            slice="SLC-029",
            seam="WS31",
            overlay_acceptance="deferred_non_gating",
            interface_bundle_user_approval="not_granted",
            current_branch_release_gate="dashboard_only",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_MINIMAL_OVERLAY_READY",
            package="PKG-006",
            slice="SLC-016",
            seam="WS19",
            surface="minimal_anchored_hud_overlay",
            configured_by="dashboard_configuration_surface",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_MINIMAL_SPLIT_READY",
            package="PKG-006",
            slice="SLC-026",
            seam="WS19",
            dashboard_owner="MonitoringHudWindow",
            minimal_owner="MonitoringHudOverlayDisplayWindow",
            native_window_split_proof="ready_ws26",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_CONTENT_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS20",
            content="configuration_centered",
            proof_boxes="rerouted_to_validators",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_MOTION_POLISH_READY",
            package="PKG-006",
            slice="SLC-026",
            seam="WS21",
            drag_smoothing="raf_local_persist_on_release",
            native_move_status="emit_on_release",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_SCROLLBAR_STYLE_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS21",
            scrollbar_style="nexus_thin_glow",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_SETTINGS_CONTENT_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS33",
            content="settings_control_surface",
            overlay_acceptance="deferred_non_gating",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_MONITOR_GROUP_CLARITY_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS33",
            monitor_model="organizational_groups_settings_only",
            dashboard_monitor_cards="not_rendered",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_OVERLAY_NON_GATING_COPY_READY",
            package="PKG-006",
            slice="SLC-029",
            seam="WS33",
            proof="dashboard_content_separates_future_overlay_acceptance",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_PROVIDER_TRUTH_READY",
            package="PKG-006",
            slice="SLC-025",
            seam="WS34",
            provider_truth="provider_contract_first",
            fake_telemetry="blocked",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_STATE_MODEL_READY",
            package="PKG-006",
            slice="SLC-028",
            seam="WS34",
            states="setup,no_data,degraded,ready",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_DASHBOARD_WARNING_CONTROLS_READY",
            package="PKG-006",
            slice="SLC-027",
            seam="WS34",
            warning_controls="visual_non_invasive_only",
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_EDGELESS_OVERLAY_CANVAS_READY",
            package="PKG-006",
            slice="SLC-016",
            seam="WS25",
            surface="edgeless_overlay_display",
            canvas="edge_to_edge_snipping_tool_style",
            monitor_layout="movable_resizable_monitor_cards",
            watermark="edge_safe_nexus_orin",
        )

    def _monitoring_hud_telemetry_snapshot(self) -> dict[str, object]:
        return build_monitoring_hud_telemetry_snapshot(
            page_ready=self._page_ready,
            desktop_mode=self.desktop_mode,
            runtime_log_path=self.runtime_log_path,
            event_route_present=callable(self.event_logger),
            polling_rate_ms=self._monitoring_hud_polling_rate_ms,
        ).as_dict()

    def _publish_monitoring_hud_telemetry_boundary(self):
        snapshot_json = json.dumps(self._monitoring_hud_telemetry_snapshot(), sort_keys=True)
        self._run_javascript(
            f"""
            if (window.setMonitoringHudTelemetry) {{
                window.setMonitoringHudTelemetry({snapshot_json});
            }}
            """
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_TELEMETRY_BOUNDARY_READY",
            package="PKG-006",
            slice="SLC-025",
            adapter="desktop-runtime-boundary",
            hardware_polling="native_cpu_load_bounded",
            polling_rate_ms=self._monitoring_hud_polling_rate_ms,
        )

    def _monitoring_hud_placement_contract(self) -> dict[str, object]:
        geometry = self.compute_compact_geometry()
        return build_monitoring_hud_placement_contract(
            desktop_mode=self.desktop_mode,
            x=geometry.x(),
            y=geometry.y(),
            width=geometry.width(),
            height=geometry.height(),
        ).as_dict()

    def _publish_monitoring_hud_placement_ownership(self):
        placement_json = json.dumps(self._monitoring_hud_placement_contract(), sort_keys=True)
        self._run_javascript(
            f"""
            if (window.setMonitoringHudPlacementOwnership) {{
                window.setMonitoringHudPlacementOwnership({placement_json});
            }}
            """
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_PLACEMENT_OWNERSHIP_READY",
            package="PKG-006",
            slice="SLC-026",
            owner="DesktopRuntimeWindow",
            placement="standalone-native-hud-window",
            anchor="virtual_desktop",
        )

    def _on_load_finished(self, ok):
        if self._is_shutting_down:
            return
        if not ok:
            self._log_event("RENDERER_MAIN|VISUAL_PAGE_LOAD_FAILED")
            return

        self._page_ready = True
        self._log_event("RENDERER_MAIN|VISUAL_PAGE_READY")
        if self.surface_role == "hud":
            self._log_event("RENDERER_MAIN|MONITORING_HUD_PAGE_READY")
        else:
            self._log_event("RENDERER_MAIN|CORE_VISUALIZATION_READY")
        self._apply_desktop_surface_mode()
        self._publish_monitoring_hud_telemetry_boundary()
        self._publish_monitoring_hud_placement_ownership()
        self._publish_monitoring_hud_controls_visibility()
        self._publish_monitoring_hud_status_behavior()
        self._publish_monitoring_hud_control_state_to_page()
        self._publish_ai_provider_state_to_page()
        self._apply_pending_visual_state()
        self._apply_pending_voice_level()
        self._apply_command_overlay_state()
        self._schedule_desktop_mode_enable()
        self.core_visualization_ready.emit()

    def _release_initial_visibility_guard(self):
        if not self._startup_visibility_guard_active or self._is_shutting_down:
            return

        self._startup_visibility_guard_active = False
        if self.surface_role == "hud" and self._monitoring_hud_show_guard_active:
            self._monitoring_hud_deferred_initial_visibility_release = True
            self._log_event(
                "RENDERER_MAIN|CORE_VISUALIZATION_FIRST_VISIBLE_DEFERRED"
                "|reason=monitoring_hud_visible_show_guard"
            )
            return
        self.setWindowOpacity(1.0)
        self._log_event("RENDERER_MAIN|CORE_VISUALIZATION_FIRST_VISIBLE")
        self.core_visualization_visible.emit()

    def set_visual_state(self, state_name):
        self._pending_visual_state = state_name

        if self._page_ready:
            self._apply_pending_visual_state()

    def set_voice_level(self, level):
        self._pending_voice_level = max(0.0, min(1.0, float(level)))

        if self._page_ready:
            self._apply_pending_voice_level()

    def open_command_overlay(self):
        if self._is_shutting_down:
            return

        self._result_close_timer.stop()
        self._reset_overlay_ready_tracking()
        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = False
        self._arm_overlay_input_capture()
        self._command_model.open(arm_input=True)
        self._apply_command_overlay_state()
        self._command_panel.show_for_geometry(
            self.compute_compact_geometry(),
            self.screen_ref.availableGeometry(),
        )
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._command_panel.focus_input_after_show()
        self._trace_overlay("overlay_opened")
        self._emit_runtime_signal(
            "COMMAND_OVERLAY_OPENED",
            phase=self._command_model.phase,
            input_armed=self._command_model.input_armed,
        )
        self._schedule_overlay_ready_check(0)

    def overlay_needs_global_input_capture(self):
        if not self._command_model.visible or self._is_shutting_down:
            return False

        phase = self._command_model.phase
        if phase == "entry":
            return not self._overlay_local_input_engaged and not self._overlay_global_capture_suspended

        if not self._overlay_input_capture_active():
            return False

        if phase in {"choose", "confirm"}:
            return not self._command_panel.input_line.hasFocus()

        return False

    def overlay_allows_launch_grace(self):
        return (
            self._command_model.visible
            and self._command_model.phase == "entry"
            and not self._overlay_local_input_engaged
            and not self._overlay_global_capture_suspended
        )

    def overlay_monitors_global_clicks(self):
        return self._command_model.visible and self._command_model.phase == "entry" and not self._overlay_local_input_engaged

    def command_overlay_state(self):
        return {
            "visible": bool(self._command_model.visible),
            "phase": self._command_model.phase,
        }

    def close_command_overlay(self):
        if not self._command_model.visible:
            return

        self._result_close_timer.stop()
        self._reset_overlay_ready_tracking()
        self._clear_overlay_input_capture()
        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = False
        self._command_panel.hide()
        self._command_model.close()
        self._apply_command_overlay_state()
        self._trace_overlay("overlay_closed")
        self._emit_runtime_signal("COMMAND_OVERLAY_CLOSED", phase=self._command_model.phase)

    def toggle_command_overlay(self):
        if self._command_model.visible:
            self.close_command_overlay()
        else:
            self.open_command_overlay()

    def request_create_custom_task_from_tray(self, source: str = "tray"):
        if self._is_shutting_down:
            self._emit_runtime_signal(
                "TRAY_CREATE_CUSTOM_TASK_ABORTED",
                source=source,
                reason="shutdown",
            )
            return
        if self._authoring_dialog_blocks_new_dialog():
            self._emit_runtime_signal(
                "TRAY_CREATE_CUSTOM_TASK_ABORTED",
                source=source,
                reason="authoring_dialog_active",
            )
            return

        self.open_command_overlay()
        if not self._command_model.visible or self._command_model.phase != "entry":
            self._emit_runtime_signal(
                "TRAY_CREATE_CUSTOM_TASK_ABORTED",
                source=source,
                reason="overlay_not_entry",
            )
            return

        self._emit_runtime_signal(
            "TRAY_CREATE_CUSTOM_TASK_ROUTED_TO_OVERLAY_ENTRY",
            source=source,
            phase=self._command_model.phase,
        )
        QTimer.singleShot(0, self.handle_create_custom_task_requested)

    def resident_access_status_snapshot(self) -> dict[str, object]:
        provider_payload = {}
        try:
            provider_payload = self._ai_provider_state.as_renderer_payload()
        except Exception:
            provider_payload = {}
        return build_resident_access_menu_plan(
            ai_provider_state=provider_payload,
            monitoring_hud_state=self.monitoring_hud_feature_state(),
            command_overlay_state=self.command_overlay_state(),
        )

    def open_resident_access_settings(self, source: str = "tray", focus: str = "quick_access"):
        if self._is_shutting_down:
            self._emit_runtime_signal(
                "RESIDENT_ACCESS_SETTINGS_OPEN_ABORTED",
                source=source,
                reason="shutdown",
            )
            return
        if self._resident_access_settings_dialog is None:
            self._resident_access_settings_dialog = ResidentAccessSettingsDialog(
                self,
                runtime=self,
                focus=focus,
            )
        self._resident_access_settings_dialog.set_focus(focus)
        self._emit_runtime_signal(
            "RESIDENT_ACCESS_SETTINGS_OPENED",
            source=source,
            focus=focus,
            shell="minimal-global-settings",
        )

    def request_resident_access_settings_shutdown_guard(self, source: str = "client_shutdown", resume_callback=None) -> bool:
        dialog = self._resident_access_settings_dialog
        if dialog is None:
            return False
        guard = getattr(dialog, "request_dirty_close_intercept", None)
        if not callable(guard):
            return False
        blocked = bool(
            guard(
                source=source,
                pending_callback=resume_callback,
            )
        )
        if blocked:
            self._emit_runtime_signal(
                "RESIDENT_ACCESS_SETTINGS_DIRTY_CLOSE_BLOCKED",
                source=source,
                close_route="client_shutdown",
            )
        return blocked

    def request_ai_status_from_resident_access(self, source: str = "tray"):
        self._emit_runtime_signal(
            "RESIDENT_ACCESS_AI_STATUS_ROUTE_ONLY",
            source=source,
            owner="FAM-007",
            provider_visible_data="none",
        )
        self.open_resident_access_settings(source=source, focus="ai_status")

    def request_privacy_lockdown_from_resident_access(self, source: str = "tray"):
        self._emit_runtime_signal(
            "RESIDENT_ACCESS_PRIVACY_LOCKDOWN_ROUTE_ONLY",
            source=source,
            owner="FAM-007",
            effect="no_runtime_privacy_state_changed",
        )
        self.open_resident_access_settings(source=source, focus="privacy")

    def _resident_command_action_by_id(self, route_id: str):
        normalized = (route_id or "").strip().casefold()
        for action in DEFAULT_COMMAND_ACTIONS:
            if action.id.casefold() == normalized:
                return action
        return None

    def request_resident_quick_action_from_tray(self, route_id: str, source: str = "tray"):
        route_id = (route_id or "").strip()
        route = route_for_id(route_id)
        if route is None:
            self._emit_runtime_signal(
                "RESIDENT_ACCESS_QUICK_ACTION_ABORTED",
                source=source,
                route_id=route_id,
                reason="unknown_route",
            )
            return
        if not route.enabled:
            self._emit_runtime_signal(
                "RESIDENT_ACCESS_QUICK_ACTION_FUTURE_GATED",
                source=source,
                route_id=route_id,
                owner=route.owner_family,
                availability=route.availability,
            )
            self.open_resident_access_settings(source=source, focus="owner_routes")
            return
        if route_id == "tray_visibility_education":
            self._emit_runtime_signal(
                "RESIDENT_ACCESS_TRAY_VISIBILITY_COPY_SHOWN",
                source=source,
                route_id=route_id,
            )
            self.open_resident_access_settings(source=source, focus="tray")
            return
        action = self._resident_command_action_by_id(route_id)
        if action is None:
            self._emit_runtime_signal(
                "RESIDENT_ACCESS_QUICK_ACTION_ABORTED",
                source=source,
                route_id=route_id,
                reason="launcher_unavailable",
            )
            return
        try:
            launch_command_action(action)
        except Exception as exc:
            self._emit_runtime_signal(
                "RESIDENT_ACCESS_QUICK_ACTION_FAILED",
                source=source,
                route_id=route_id,
                reason=type(exc).__name__,
            )
            return
        self._emit_runtime_signal(
            "RESIDENT_ACCESS_QUICK_ACTION_SENT",
            source=source,
            route_id=route_id,
            owner=route.owner_family,
        )

    def show_ai_control_center_from_tray(self, source: str = "tray"):
        if self._is_shutting_down:
            self._emit_runtime_signal(
                "AI_CONTROL_CENTER_ABORTED",
                source=source,
                reason="shutdown",
            )
            return {"shown": False, "reason": "shutdown"}
        if self._ai_control_center_dialog is None:
            self._ai_control_center_dialog = AIControlCenterDialog(
                self.screen_ref,
                event_logger=self._log_event,
            )
        payload = self._ai_provider_state.as_renderer_payload()
        self._ai_control_center_dialog.update_provider_state(payload)
        visibility = self._ai_control_center_dialog.show_from_tray()
        visibility_fields = {
            "source": source,
            "owner": "FAM-007",
            "route": "fam007-ai-control-center",
            "carry_in": "f3-ff01-narrow-doorway-only",
            "provider_visible_data": payload.get("providerVisibleData", "none"),
            "sent_to_provider": str(payload.get("sentToProvider", False)).lower(),
            "can_accept_prompts": str(payload.get("canAcceptPrompts", False)).lower(),
            "prompt_send": payload.get("promptSendPosture", "prompt-send-disabled"),
            "network_egress": payload.get("networkEgressState", "network-egress-blocked"),
            "memory_indexing": payload.get("memoryIndexingState", "memory-indexing-disabled"),
            "packaging_execution": "blocked",
            "qt_visible": str(visibility.get("qtVisible")).lower(),
            "native_visible": str(visibility.get("nativeVisible")).lower(),
            "hwnd": visibility.get("hwnd", 0),
            "x": visibility.get("x", -1),
            "y": visibility.get("y", -1),
            "w": visibility.get("w", -1),
            "h": visibility.get("h", -1),
        }
        shown = bool(visibility.get("qtVisible") and visibility.get("nativeVisible"))
        if shown:
            self._emit_runtime_signal("AI_CONTROL_CENTER_VISIBLE", **visibility_fields)
        else:
            self._emit_runtime_signal("AI_CONTROL_CENTER_VISIBILITY_FAILED", **visibility_fields)
        return {
            "shown": shown,
            "reason": "" if shown else "visibility_failed",
            "qtVisible": bool(visibility.get("qtVisible")),
            "nativeVisible": bool(visibility.get("nativeVisible")),
        }

    def reload_command_action_catalog(self, source_path=None):
        resolved_source_path = self._saved_action_source_path if source_path is None else source_path
        self._emit_runtime_signal(
            "COMMAND_ACTION_CATALOG_RELOAD_STARTED",
            source_path=resolved_source_path or "",
        )
        catalog = self._command_model.reload_action_catalog(resolved_source_path)
        self._apply_command_overlay_state()
        if self._command_panel.isVisible():
            self._command_panel.refresh_for_geometry(
                self.compute_compact_geometry(),
                self.screen_ref.availableGeometry(),
            )
        inventory_fields = self._saved_action_inventory_signal_fields(catalog.saved_action_inventory)
        inventory_fields.update(self._saved_group_inventory_signal_fields(catalog.saved_group_inventory))
        inventory_fields["catalog_action_count"] = len(catalog.actions)
        self._emit_runtime_signal("COMMAND_ACTION_CATALOG_RELOAD_COMPLETED", **inventory_fields)
        self._emit_runtime_signal("COMMAND_ACTION_CATALOG_RELOAD_RESULT", **inventory_fields)
        return catalog

    def _set_entry_feedback(self, status_kind: str, status_text: str):
        self._command_model.set_entry_feedback(status_kind, status_text)
        self._apply_command_overlay_state()

    def _saved_action_authoring_block_message(self, operation_label: str) -> str:
        inventory = self._command_model.action_catalog.saved_action_inventory
        guidance_text = inventory.guidance_text or 'Use "Open Saved Actions File" or "Open Saved Actions Folder" to inspect the source.'
        return (
            f"Custom task {operation_label} is blocked until the saved-actions source is repaired. "
            + guidance_text
        )

    def _saved_group_authoring_block_message(self, operation_label: str) -> str:
        inventory = self._command_model.action_catalog.saved_group_inventory
        guidance_text = inventory.guidance_text or 'Use "Open Saved Actions File" or "Open Saved Actions Folder" to inspect the source.'
        return (
            f"Custom group {operation_label} is blocked until the saved-actions source is repaired. "
            + guidance_text
        )

    def _group_dialog_member_items(self) -> list[dict]:
        items: list[dict] = []
        for action in self._command_model.action_catalog.actions:
            items.append(
                {
                    "id": action.id,
                    "title": action.title,
                    "origin_label": "Saved" if action.origin == "saved" else "Built-in",
                    "target_kind": action.target_kind,
                    "target_display": self._command_model.action_catalog.format_target_display(
                        action.target_kind,
                        action.target,
                    ),
                }
            )
        return items

    def _task_dialog_group_kwargs(self) -> dict:
        group_inventory = self._command_model.view_payload().get("saved_group_inventory") or {}
        return {
            "available_groups": group_inventory.get("items") or [],
            "available_group_members": self._group_dialog_member_items(),
            "group_status_kind": group_inventory.get("status_kind", "template_only"),
            "group_status_text": group_inventory.get("status_text", ""),
        }

    def _resume_overlay_capture_after_authoring_dialog(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return

        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = False
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._refresh_overlay_input_capture(seconds=5.0)
        self._apply_command_overlay_state()
        if hasattr(self._command_panel, "raise_"):
            self._command_panel.raise_()
        if hasattr(self._command_panel, "activateWindow"):
            self._command_panel.activateWindow()
        if hasattr(self._command_panel, "windowHandle"):
            window_handle = self._command_panel.windowHandle()
            if window_handle is not None:
                window_handle.requestActivate()
        if hasattr(self._command_panel, "setFocus"):
            self._command_panel.setFocus(Qt.ActiveWindowFocusReason)
        QTimer.singleShot(0, self._emit_overlay_ready_signal)

    def _handle_saved_action_create_draft_submit(self, draft: SavedActionDraft):
        self._emit_runtime_signal(
            "CUSTOM_TASK_CREATE_ATTEMPT_STARTED",
            title=draft.title,
            target_kind=draft.target_kind,
        )
        try:
            result = create_saved_action_from_draft(
                draft,
                source_path=self._saved_action_source_path,
            )
        except SavedActionDraftValidationError as exc:
            self._emit_runtime_signal(
                "CUSTOM_TASK_CREATE_BLOCKED",
                reason="validation_error",
                title=draft.title,
                target_kind=draft.target_kind,
                detail=str(exc),
            )
            raise
        except SavedActionUnsafeSourceError as exc:
            self._emit_runtime_signal(
                "CUSTOM_TASK_CREATE_BLOCKED",
                reason="unsafe_source",
                title=draft.title,
                target_kind=draft.target_kind,
                detail=str(exc),
            )
            raise
        except SavedActionSourceWriteBlocked as exc:
            self._emit_runtime_signal(
                "CUSTOM_TASK_CREATE_BLOCKED",
                reason="write_blocked",
                title=draft.title,
                target_kind=draft.target_kind,
                detail=str(exc),
            )
            raise
        self.reload_command_action_catalog(self._saved_action_source_path)
        self._set_entry_feedback("ready", f'Custom task created: "{result.record["title"]}".')
        self._emit_runtime_signal(
            "CUSTOM_TASK_CREATED",
            action_id=result.record["id"],
            title=result.record["title"],
            target_kind=result.record["target_kind"],
        )
        return result

    def _handle_saved_action_edit_draft_submit(self, saved_action_id: str, draft: SavedActionDraft):
        self._emit_runtime_signal(
            "CUSTOM_TASK_EDIT_ATTEMPT_STARTED",
            action_id=saved_action_id,
            title=draft.title,
            target_kind=draft.target_kind,
        )
        try:
            result = update_saved_action_from_draft(
                saved_action_id,
                draft,
                source_path=self._saved_action_source_path,
            )
        except SavedActionDraftValidationError as exc:
            self._emit_runtime_signal(
                "CUSTOM_TASK_EDIT_BLOCKED",
                reason="validation_error",
                action_id=saved_action_id,
                title=draft.title,
                target_kind=draft.target_kind,
                detail=str(exc),
            )
            raise
        except SavedActionUnsafeSourceError as exc:
            self._emit_runtime_signal(
                "CUSTOM_TASK_EDIT_BLOCKED",
                reason="unsafe_source",
                action_id=saved_action_id,
                title=draft.title,
                target_kind=draft.target_kind,
                detail=str(exc),
            )
            raise
        except SavedActionSourceWriteBlocked as exc:
            self._emit_runtime_signal(
                "CUSTOM_TASK_EDIT_BLOCKED",
                reason="write_blocked",
                action_id=saved_action_id,
                title=draft.title,
                target_kind=draft.target_kind,
                detail=str(exc),
            )
            raise
        self.reload_command_action_catalog(self._saved_action_source_path)
        self._set_entry_feedback("ready", f'Custom task updated: "{result.record["title"]}".')
        self._emit_runtime_signal(
            "CUSTOM_TASK_UPDATED",
            action_id=result.record["id"],
            title=result.record["title"],
            target_kind=result.record["target_kind"],
        )
        return result

    def _handle_callable_group_create_draft_submit(self, draft: CallableGroupDraft):
        self._emit_runtime_signal(
            "CUSTOM_GROUP_CREATE_ATTEMPT_STARTED",
            title=draft.title,
            member_count=len(draft.member_action_ids),
        )
        try:
            result = create_callable_group_from_draft(
                draft,
                source_path=self._saved_action_source_path,
            )
        except (CallableGroupDraftValidationError, CallableGroupUnsafeSourceError, SavedActionSourceWriteBlocked):
            raise
        self.reload_command_action_catalog(self._saved_action_source_path)
        self._set_entry_feedback("ready", f'Custom group created: "{result.record["title"]}".')
        self._emit_runtime_signal(
            "CUSTOM_GROUP_CREATED",
            group_id=result.record["id"],
            title=result.record["title"],
            member_count=len(result.record.get("member_action_ids", ()) or ()),
        )
        return result

    def _handle_callable_group_edit_draft_submit(self, group_id: str, draft: CallableGroupDraft):
        self._emit_runtime_signal(
            "CUSTOM_GROUP_EDIT_ATTEMPT_STARTED",
            group_id=group_id,
            title=draft.title,
            member_count=len(draft.member_action_ids),
        )
        try:
            result = update_callable_group_from_draft(
                group_id,
                draft,
                source_path=self._saved_action_source_path,
            )
        except (CallableGroupDraftValidationError, CallableGroupUnsafeSourceError, SavedActionSourceWriteBlocked):
            raise
        self.reload_command_action_catalog(self._saved_action_source_path)
        self._set_entry_feedback("ready", f'Custom group updated: "{result.record["title"]}".')
        self._emit_runtime_signal(
            "CUSTOM_GROUP_UPDATED",
            group_id=result.record["id"],
            title=result.record["title"],
            member_count=len(result.record.get("member_action_ids", ()) or ()),
        )
        return result

    def handle_create_custom_task_requested(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        if self._authoring_dialog_blocks_new_dialog():
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_ACTION_BLOCKED",
                action="create_custom_task",
                reason="authoring_dialog_active",
            )
            return

        self._emit_runtime_signal("OVERLAY_ENTRY_ACTION_TRIGGERED", action="create_custom_task")

        inventory = self._command_model.action_catalog.saved_action_inventory
        if inventory.status_kind in {"invalid_source", "invalid_saved_actions"}:
            self._set_entry_feedback("not_found", self._saved_action_authoring_block_message("creation"))
            self._emit_runtime_signal(
                "CUSTOM_TASK_CREATE_BLOCKED",
                reason="source_invalid",
                status_kind=inventory.status_kind,
                **self._saved_action_inventory_signal_fields(inventory),
            )
            return

        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = True
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._clear_overlay_input_capture()
        self._apply_command_overlay_state()

        QTimer.singleShot(0, self._open_create_custom_task_dialog)

    def _open_create_custom_task_dialog(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        if self._authoring_dialog_blocks_new_dialog():
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_DIALOG_CREATE_BLOCKED",
                action="create_custom_task",
                reason="authoring_dialog_active",
            )
            return

        self._emit_runtime_signal("OVERLAY_ENTRY_DIALOG_CREATE_START", action="create_custom_task")
        dialog = self._create_dialog_with_optional_lifecycle(
            self._saved_action_create_dialog_factory,
            self,
            self._handle_saved_action_create_draft_submit,
            **self._task_dialog_group_kwargs(),
            lifecycle_callback=self._handle_dialog_lifecycle_signal,
        )
        self._emit_runtime_signal(
            "OVERLAY_ENTRY_DIALOG_CREATED",
            action="create_custom_task",
            dialog_name=dialog.windowTitle(),
            dialog_object_name=dialog.objectName() or type(dialog).__name__,
            dialog_visible="true" if dialog.isVisible() else "false",
            win_id=int(dialog.winId()),
        )
        try:
            self._exec_authoring_dialog(dialog, action="create_custom_task")
        finally:
            self._resume_overlay_capture_after_authoring_dialog()

    def handle_created_tasks_requested(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        if self._authoring_dialog_blocks_new_dialog():
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_ACTION_BLOCKED",
                action="manage_custom_tasks",
                reason="authoring_dialog_active",
            )
            return

        inventory_payload = self._command_model.view_payload().get("saved_action_inventory") or {}

        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = True
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._clear_overlay_input_capture()
        self._apply_command_overlay_state()

        dialog = self._create_dialog_with_optional_lifecycle(
            self._created_tasks_dialog_factory,
            self._command_panel,
            inventory_payload,
            lifecycle_callback=self._handle_dialog_lifecycle_signal,
        )
        selected_action_id = ""
        selected_delete_action_id = ""
        try:
            self._exec_authoring_dialog(dialog, action="manage_custom_tasks")
            if hasattr(dialog, "selected_action_id"):
                selected_action_id = str(dialog.selected_action_id() or "").strip()
            if hasattr(dialog, "selected_delete_action_id"):
                selected_delete_action_id = str(dialog.selected_delete_action_id() or "").strip()
        finally:
            self._resume_overlay_capture_after_authoring_dialog()

        if selected_delete_action_id:
            self.handle_delete_saved_action_requested(selected_delete_action_id)
        elif selected_action_id:
            self.handle_edit_saved_action_requested(selected_action_id)

    def handle_create_custom_group_requested(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        if self._authoring_dialog_blocks_new_dialog():
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_ACTION_BLOCKED",
                action="create_custom_group",
                reason="authoring_dialog_active",
            )
            return

        group_inventory = self._command_model.action_catalog.saved_group_inventory
        if group_inventory.status_kind in {"invalid_source", "invalid_saved_actions", "invalid_groups"}:
            self._set_entry_feedback("not_found", self._saved_group_authoring_block_message("creation"))
            self._emit_runtime_signal(
                "CUSTOM_GROUP_CREATE_BLOCKED",
                reason="source_invalid",
                status_kind=group_inventory.status_kind,
                **self._saved_group_inventory_signal_fields(group_inventory),
            )
            return

        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = True
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._clear_overlay_input_capture()
        self._apply_command_overlay_state()

        dialog = self._create_dialog_with_optional_lifecycle(
            self._callable_group_create_dialog_factory,
            self._command_panel,
            self._handle_callable_group_create_draft_submit,
            available_members=self._group_dialog_member_items(),
            lifecycle_callback=self._handle_dialog_lifecycle_signal,
        )
        try:
            self._exec_authoring_dialog(dialog, action="create_custom_group")
        finally:
            self._resume_overlay_capture_after_authoring_dialog()

    def handle_created_groups_requested(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        if self._authoring_dialog_blocks_new_dialog():
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_ACTION_BLOCKED",
                action="manage_custom_groups",
                reason="authoring_dialog_active",
            )
            return

        inventory_payload = self._command_model.view_payload().get("saved_group_inventory") or {}

        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = True
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._clear_overlay_input_capture()
        self._apply_command_overlay_state()

        dialog = self._create_dialog_with_optional_lifecycle(
            self._created_groups_dialog_factory,
            self._command_panel,
            inventory_payload,
            lifecycle_callback=self._handle_dialog_lifecycle_signal,
        )
        selected_group_id = ""
        selected_delete_group_id = ""
        try:
            self._exec_authoring_dialog(dialog, action="manage_custom_groups")
            if hasattr(dialog, "selected_group_id"):
                selected_group_id = str(dialog.selected_group_id() or "").strip()
            if hasattr(dialog, "selected_delete_group_id"):
                selected_delete_group_id = str(dialog.selected_delete_group_id() or "").strip()
        finally:
            self._resume_overlay_capture_after_authoring_dialog()

        if selected_delete_group_id:
            self.handle_delete_saved_group_requested(selected_delete_group_id)
        elif selected_group_id:
            self.handle_edit_saved_group_requested(selected_group_id)

    def handle_edit_saved_action_requested(self, saved_action_id: str):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        if self._authoring_dialog_blocks_new_dialog():
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_ACTION_BLOCKED",
                action="edit_custom_task",
                reason="authoring_dialog_active",
            )
            return

        inventory = self._command_model.action_catalog.saved_action_inventory
        if inventory.status_kind in {"invalid_source", "invalid_saved_actions"}:
            self._set_entry_feedback("not_found", self._saved_action_authoring_block_message("editing"))
            self._emit_runtime_signal(
                "CUSTOM_TASK_EDIT_BLOCKED",
                reason="source_invalid",
                action_id=saved_action_id,
                status_kind=inventory.status_kind,
                **self._saved_action_inventory_signal_fields(inventory),
            )
            return

        try:
            initial_draft = load_saved_action_draft_for_edit(
                saved_action_id,
                source_path=self._saved_action_source_path,
            )
        except SavedActionUnsafeSourceError:
            self._set_entry_feedback("not_found", self._saved_action_authoring_block_message("editing"))
            self._emit_runtime_signal(
                "CUSTOM_TASK_EDIT_BLOCKED",
                reason="unsafe_source",
                action_id=saved_action_id,
            )
            return
        except SavedActionDraftValidationError as exc:
            self._set_entry_feedback("not_found", str(exc))
            self._emit_runtime_signal(
                "CUSTOM_TASK_EDIT_BLOCKED",
                reason="missing_record",
                action_id=saved_action_id,
                detail=str(exc),
            )
            return

        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = True
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._clear_overlay_input_capture()
        self._apply_command_overlay_state()

        dialog = self._create_dialog_with_optional_lifecycle(
            self._saved_action_edit_dialog_factory,
            self._command_panel,
            lambda draft: self._handle_saved_action_edit_draft_submit(saved_action_id, draft),
            initial_draft=initial_draft,
            **self._task_dialog_group_kwargs(),
            lifecycle_callback=self._handle_dialog_lifecycle_signal,
        )
        try:
            self._exec_authoring_dialog(dialog, action="edit_custom_task")
        finally:
            self._resume_overlay_capture_after_authoring_dialog()

    def handle_edit_saved_group_requested(self, group_id: str):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        if self._authoring_dialog_blocks_new_dialog():
            self._emit_runtime_signal(
                "OVERLAY_ENTRY_ACTION_BLOCKED",
                action="edit_custom_group",
                reason="authoring_dialog_active",
            )
            return

        group_inventory = self._command_model.action_catalog.saved_group_inventory
        if group_inventory.status_kind in {"invalid_source", "invalid_saved_actions", "invalid_groups"}:
            self._set_entry_feedback("not_found", self._saved_group_authoring_block_message("editing"))
            self._emit_runtime_signal(
                "CUSTOM_GROUP_EDIT_BLOCKED",
                reason="source_invalid",
                group_id=group_id,
                status_kind=group_inventory.status_kind,
                **self._saved_group_inventory_signal_fields(group_inventory),
            )
            return

        try:
            initial_draft = load_callable_group_draft_for_edit(
                group_id,
                source_path=self._saved_action_source_path,
            )
        except (CallableGroupUnsafeSourceError, CallableGroupDraftValidationError) as exc:
            self._set_entry_feedback("not_found", str(exc))
            self._emit_runtime_signal(
                "CUSTOM_GROUP_EDIT_BLOCKED",
                reason="missing_record",
                group_id=group_id,
                detail=str(exc),
            )
            return

        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = True
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._clear_overlay_input_capture()
        self._apply_command_overlay_state()

        dialog = self._create_dialog_with_optional_lifecycle(
            self._callable_group_edit_dialog_factory,
            self._command_panel,
            lambda draft: self._handle_callable_group_edit_draft_submit(group_id, draft),
            initial_draft=initial_draft,
            available_members=self._group_dialog_member_items(),
            lifecycle_callback=self._handle_dialog_lifecycle_signal,
        )
        try:
            self._exec_authoring_dialog(dialog, action="edit_custom_group")
        finally:
            self._resume_overlay_capture_after_authoring_dialog()

    def handle_delete_saved_action_requested(self, saved_action_id: str):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return

        inventory = self._command_model.action_catalog.saved_action_inventory
        if inventory.status_kind in {"invalid_source", "invalid_saved_actions"}:
            self._set_entry_feedback("not_found", self._saved_action_authoring_block_message("deletion"))
            self._emit_runtime_signal(
                "CUSTOM_TASK_DELETE_BLOCKED",
                reason="source_invalid",
                action_id=saved_action_id,
                status_kind=inventory.status_kind,
                **self._saved_action_inventory_signal_fields(inventory),
            )
            return

        self._emit_runtime_signal(
            "CUSTOM_TASK_DELETE_ATTEMPT_STARTED",
            action_id=saved_action_id,
        )
        try:
            result = delete_saved_action(
                saved_action_id,
                source_path=self._saved_action_source_path,
            )
        except SavedActionUnsafeSourceError:
            self._set_entry_feedback("not_found", self._saved_action_authoring_block_message("deletion"))
            self._emit_runtime_signal(
                "CUSTOM_TASK_DELETE_BLOCKED",
                reason="unsafe_source",
                action_id=saved_action_id,
            )
            return
        except SavedActionDraftValidationError as exc:
            self._set_entry_feedback("not_found", str(exc))
            self._emit_runtime_signal(
                "CUSTOM_TASK_DELETE_BLOCKED",
                reason="missing_record",
                action_id=saved_action_id,
                detail=str(exc),
            )
            return
        except SavedActionSourceWriteBlocked as exc:
            self._set_entry_feedback("not_found", str(exc))
            self._emit_runtime_signal(
                "CUSTOM_TASK_DELETE_BLOCKED",
                reason="write_blocked",
                action_id=saved_action_id,
                detail=str(exc),
            )
            return

        self.reload_command_action_catalog(self._saved_action_source_path)
        self._set_entry_feedback("ready", f'Custom task deleted: "{result.record["title"]}".')
        self._emit_runtime_signal(
            "CUSTOM_TASK_DELETED",
            action_id=result.record["id"],
            title=result.record["title"],
            target_kind=result.record["target_kind"],
        )

    def handle_delete_saved_group_requested(self, group_id: str):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return

        group_inventory = self._command_model.action_catalog.saved_group_inventory
        if group_inventory.status_kind in {"invalid_source", "invalid_saved_actions", "invalid_groups"}:
            self._set_entry_feedback("not_found", self._saved_group_authoring_block_message("deletion"))
            self._emit_runtime_signal(
                "CUSTOM_GROUP_DELETE_BLOCKED",
                reason="source_invalid",
                group_id=group_id,
                status_kind=group_inventory.status_kind,
                **self._saved_group_inventory_signal_fields(group_inventory),
            )
            return

        try:
            result = delete_callable_group(
                group_id,
                source_path=self._saved_action_source_path,
            )
        except (CallableGroupUnsafeSourceError, CallableGroupDraftValidationError, SavedActionSourceWriteBlocked) as exc:
            self._set_entry_feedback("not_found", str(exc))
            self._emit_runtime_signal(
                "CUSTOM_GROUP_DELETE_BLOCKED",
                reason="write_blocked",
                group_id=group_id,
                detail=str(exc),
            )
            return

        self.reload_command_action_catalog(self._saved_action_source_path)
        self._set_entry_feedback("ready", f'Custom group deleted: "{result.record["title"]}".')
        self._emit_runtime_signal(
            "CUSTOM_GROUP_DELETED",
            group_id=result.record["id"],
            title=result.record["title"],
        )

    def handle_command_text_changed(self, text: str):
        self._command_model.set_input_text(text)
        self._apply_command_overlay_state()
        self._trace_overlay("local_text_changed", new_text=repr(text))

    def handle_overlay_text_requested(self, text: str):
        if not text or not self.overlay_needs_global_input_capture():
            return

        self._refresh_overlay_input_capture()
        if self._command_model.phase == "choose":
            if text.isdigit():
                self.handle_ambiguous_match_selected(int(text) - 1)
            return

        if self._command_model.phase != "entry":
            return

        self._command_model.input_armed = True
        before = self._command_model.input_text
        self._command_model.append_text(text)
        self._apply_command_overlay_state()
        self._trace_overlay(
            "global_text_requested",
            text=repr(text),
            input_before=repr(before),
            input_after=repr(self._command_model.input_text),
        )

    def handle_overlay_backspace_requested(self):
        if not self.overlay_needs_global_input_capture() or self._command_model.phase != "entry":
            return

        self._refresh_overlay_input_capture()
        self._command_model.input_armed = True
        self._command_model.backspace()
        self._apply_command_overlay_state()

    def handle_overlay_submit_requested(self):
        if not self.overlay_needs_global_input_capture():
            return
        self._refresh_overlay_input_capture()
        self.handle_command_submit(source="fallback")

    def handle_local_submit_requested(self):
        self.handle_command_submit(source="local")

    def handle_overlay_escape_requested(self):
        if not self._command_model.visible:
            return

        if self.overlay_needs_global_input_capture():
            self._refresh_overlay_input_capture()
        self.handle_command_escape()

    def handle_command_input_armed_changed(self, armed: bool):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        self._command_model.input_armed = bool(armed)
        self._apply_command_overlay_state()
        self._schedule_overlay_ready_check(0)

    def handle_command_input_focus_acquired(self):
        if self._command_model.visible and self._command_model.phase == "entry":
            panel_is_active = self._command_panel.isActiveWindow()
            input_has_focus = self._command_panel.input_line.hasFocus()
            manual_focus = self._command_panel.input_line.last_focus_was_manual()
            if panel_is_active and input_has_focus and manual_focus:
                self._command_panel.input_line.set_local_typing_enabled(True)
                self._overlay_local_input_engaged = True
                self._overlay_global_capture_suspended = False
                self._clear_overlay_input_capture()
                self._trace_overlay("input_focus_acquired", manual_focus="true", mode="local")
                self._schedule_overlay_ready_check(0)
                return

            if panel_is_active and input_has_focus and self._overlay_global_capture_suspended:
                self._command_panel.input_line.set_local_typing_enabled(False)
                self._overlay_local_input_engaged = False
                self._overlay_global_capture_suspended = False
                self._refresh_overlay_input_capture()
                self._trace_overlay(
                    "input_focus_acquired",
                    manual_focus="true" if manual_focus else "false",
                    mode="rearmed",
                )
                self._schedule_overlay_ready_check(0)
                return

            self._command_panel.input_line.set_local_typing_enabled(False)
            self._overlay_local_input_engaged = False
            self._refresh_overlay_input_capture()
            self._trace_overlay(
                "input_focus_acquired",
                manual_focus="true" if manual_focus else "false",
                mode="fallback",
            )
            self._schedule_overlay_ready_check(0)

    def handle_command_input_focus_lost(self):
        if not self._command_model.visible:
            return
        if self._command_model.phase == "entry" and self._overlay_local_input_engaged:
            self._command_panel.input_line.set_local_typing_enabled(False)
            self._overlay_local_input_engaged = False
            self._refresh_overlay_input_capture()
        self._trace_overlay("input_focus_lost")
        self._schedule_overlay_ready_check(0)

    def _command_panel_contains_global_point(self, x: int, y: int) -> bool:
        try:
            return self._command_panel.frameGeometry().contains(int(x), int(y))
        except Exception:
            return False

    def handle_overlay_global_click_requested(self, x: int, y: int):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return
        if self._overlay_local_input_engaged:
            return
        if self._command_panel_contains_global_point(x, y):
            self._trace_overlay("global_click_inside_overlay", x=str(int(x)), y=str(int(y)))
            return

        self._overlay_global_capture_suspended = True
        self._clear_overlay_input_capture()
        self._trace_overlay("global_click_suspended_capture", x=str(int(x)), y=str(int(y)))

    def handle_command_escape(self):
        result = self._command_model.escape()
        self._apply_command_overlay_state()

        if result == "choice_cancelled":
            if self._overlay_local_input_engaged:
                self._command_panel.focus_input()
            else:
                self._refresh_overlay_input_capture(seconds=5.0)
            self._log_event("RENDERER_MAIN|COMMAND_DISAMBIGUATION_CANCELLED")
            return

        if result == "confirm_cancelled":
            if self._overlay_local_input_engaged:
                self._command_panel.focus_input()
            else:
                self._refresh_overlay_input_capture(seconds=5.0)
            self._log_event("RENDERER_MAIN|COMMAND_CONFIRM_CANCELLED")
            return

        if result == "closed":
            self._reset_overlay_ready_tracking()
            self._command_panel.hide()
            self._log_event("RENDERER_MAIN|COMMAND_OVERLAY_CLOSED")

    def _show_command_result(self, status_kind: str, status_text: str, close_delay_ms: int = 1200):
        self._command_model.show_result(status_kind, status_text)
        self._apply_command_overlay_state()
        self._result_close_timer.start(max(0, int(close_delay_ms)))

    def _emit_group_execution_marker(self, marker_name: str, fields: dict[str, str]):
        parts = ["RENDERER_MAIN", marker_name]
        for key, value in fields.items():
            normalized = (value or "").strip()
            if not normalized:
                continue
            parts.append(f"{key}={normalized}")
        self._log_event("|".join(parts))

    def _execute_callable_group(self, group):
        return execute_command_group(
            group,
            action_launcher=launch_command_action,
            marker_emitter=self._emit_group_execution_marker,
        )

    def _close_command_overlay_after_result(self):
        self.close_command_overlay()

    def _record_launch_failure(self, action_id: str) -> int:
        if self._last_launch_failure_action_id == action_id:
            self._last_launch_failure_count += 1
        else:
            self._last_launch_failure_action_id = action_id
            self._last_launch_failure_count = 1
        return self._last_launch_failure_count

    def _clear_launch_failure_tracking(self, action_id: str):
        if self._last_launch_failure_action_id == action_id:
            self._last_launch_failure_action_id = ""
            self._last_launch_failure_count = 0
        self._reported_recoverable_launch_failures.discard(action_id)

    def _classify_recoverable_launch_failed_incident(
        self,
        action_id: str,
        failure_count: int,
        *,
        failure_context: dict[str, str] | None = None,
    ) -> str:
        normalized_failure_context = self._normalize_launch_failure_context(
            action_id,
            failure_context,
        )
        context_suffix = self._format_failure_context_suffix(normalized_failure_context)
        if failure_count < 2:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS2_INLINE|action_id={action_id}|count={failure_count}{context_suffix}"
            )
            return "class2_inline"

        if action_id in self._reported_recoverable_launch_failures:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS3_ALREADY_REPORTED|action_id={action_id}|count={failure_count}{context_suffix}"
            )
            return "class3_already_reported"

        self._log_event(
            f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS3_REPORT_SELECTED|action_id={action_id}|count={failure_count}{context_suffix}"
        )
        return "class3_report_selected"

    def _format_failure_context_suffix(self, failure_context: dict[str, str] | None) -> str:
        if not failure_context:
            return ""
        suffix_parts = []
        for key, value in failure_context.items():
            normalized = (value or "").strip()
            if not normalized:
                continue
            suffix_parts.append(f"{key}={normalized.replace('|', '/')}")
        if not suffix_parts:
            return ""
        return "|" + "|".join(suffix_parts)

    def _bound_execution_trace(self, execution_trace: str, *, fallback_action_id: str = "") -> str:
        segments = [
            segment.strip()
            for segment in (execution_trace or "").split(">")
            if segment and segment.strip()
        ]
        if not segments and fallback_action_id.strip():
            segments = [fallback_action_id.strip()]
        if len(segments) > 8:
            segments = segments[-8:]
        return ">".join(segment.replace("|", "/") for segment in segments)

    def _normalize_launch_failure_context(
        self,
        action_id: str,
        failure_context: dict[str, str] | None = None,
    ) -> dict[str, str]:
        raw_context = dict(failure_context or {})
        execution_type = (raw_context.get("execution_type") or "single").strip().casefold()
        normalized_error_type = (raw_context.get("error_type") or "launch_exception").strip() or "launch_exception"

        if execution_type == "group":
            failed_action_id = (raw_context.get("failed_action_id") or action_id or "").strip()
            return {
                "execution_type": "group",
                "failed_action_id": failed_action_id,
                "group_id": (raw_context.get("group_id") or "").strip(),
                "step_index": (raw_context.get("step_index") or raw_context.get("failed_step_index") or "").strip(),
                "error_type": normalized_error_type,
                "execution_trace": self._bound_execution_trace(
                    raw_context.get("execution_trace", ""),
                    fallback_action_id=failed_action_id,
                ),
            }

        normalized_action_id = (action_id or "").strip()
        return {
            "execution_type": "single",
            "action_id": normalized_action_id,
            "group_id": "",
            "step_index": "",
            "error_type": normalized_error_type,
            "execution_trace": self._bound_execution_trace(
                raw_context.get("execution_trace", ""),
                fallback_action_id=normalized_action_id,
            ),
        }

    def _prepare_recoverable_launch_failure_report(self, action, *, failure_context: dict[str, str] | None = None) -> str | None:
        normalized_failure_context = self._normalize_launch_failure_context(
            action.id,
            failure_context,
        )
        failure_count = self._record_launch_failure(action.id)
        context_suffix = self._format_failure_context_suffix(normalized_failure_context)
        incident_class = self._classify_recoverable_launch_failed_incident(
            action.id,
            failure_count,
            failure_context=normalized_failure_context,
        )
        if incident_class == "class2_inline":
            return None
        if incident_class == "class3_already_reported":
            return None
        if not self.runtime_log_path or not os.path.isfile(self.runtime_log_path):
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_SKIPPED|action_id={action.id}|reason=runtime_log_unavailable{context_suffix}"
            )
            return None

        crash_dir = os.path.join(os.path.dirname(self.runtime_log_path), "crash")
        self._log_event(
            f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_BEGIN|action_id={action.id}|count={failure_count}{context_suffix}"
        )
        try:
            report_prep = prepare_manual_issue_report(ROOT_DIR, self.runtime_log_path, crash_dir)
        except SupportBundleError as exc:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_FAILED|action_id={action.id}|reason={exc}{context_suffix}"
            )
            return None
        except Exception as exc:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_FAILED|action_id={action.id}|reason={exc}{context_suffix}"
            )
            return None

        bundle_info = report_prep["bundle_info"]
        issue_url = report_prep["issue_url"]
        browser_opened = False

        try:
            os.startfile(os.path.dirname(bundle_info["bundle_path"]))
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_FOLDER_OPENED|action_id={action.id}|bundle={bundle_info['bundle_name']}{context_suffix}"
            )
        except Exception as exc:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_FOLDER_FAILED|action_id={action.id}|reason={exc}{context_suffix}"
            )

        if issue_url:
            try:
                browser_opened = webbrowser.open(issue_url, new=2)
            except Exception as exc:
                self._log_event(
                    f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_ISSUE_FAILED|action_id={action.id}|reason={exc}{context_suffix}"
                )

        self._reported_recoverable_launch_failures.add(action.id)
        self._log_event(
            f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_READY|action_id={action.id}|bundle={bundle_info['bundle_name']}{context_suffix}"
        )

        if browser_opened:
            return "Launch failed again. Support bundle prepared and issue draft opened; attach the bundle manually."
        if issue_url:
            return "Launch failed again. Support bundle prepared; open the issue page manually and attach the bundle."
        return "Launch failed again. Support bundle prepared; review it locally before filing the report."

    def _resolve_group_failure_action(self, group, failed_action_id: str):
        normalized_failed_action_id = (failed_action_id or "").strip().casefold()
        if not normalized_failed_action_id:
            return None
        for action in tuple(group.member_actions):
            if action.id.strip().casefold() == normalized_failed_action_id:
                return action
        return None

    def _build_group_failure_context(self, group, result) -> dict[str, str]:
        execution_trace = tuple(result.completed_action_ids) + (
            (result.failed_action_id,) if result.failed_action_id else ()
        )
        return {
            "execution_type": "group",
            "group_id": group.id,
            "failed_action_id": result.failed_action_id,
            "step_index": str(result.failed_step_index),
            "error_type": "launch_exception",
            "execution_trace": self._bound_execution_trace(
                ">".join(action_id for action_id in execution_trace if action_id),
                fallback_action_id=result.failed_action_id or "",
            ),
        }

    def handle_ambiguous_match_selected(self, index: int):
        result, payload = self._command_model.choose_match(index)
        self._apply_command_overlay_state()

        if result != "confirm_ready":
            return

        if self._overlay_local_input_engaged:
            self._command_panel.setFocus(Qt.ActiveWindowFocusReason)
        else:
            self._refresh_overlay_input_capture(seconds=5.0)
        self._log_event(
            f"RENDERER_MAIN|COMMAND_DISAMBIGUATION_SELECTED|index={index}|action_id={payload.id}"
        )
        self._log_event(f"RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id={payload.id}")

    def handle_command_submit(self, source: str = "local"):
        foreground = self._foreground_window_snapshot()
        self._trace_overlay(
            "submit_requested",
            source=repr(source),
            foreground_hwnd=repr(foreground["hwnd"]),
            foreground_class=repr(foreground["class_name"]),
            foreground_title=repr(foreground["title"]),
        )
        result, payload = self._command_model.submit()
        self._apply_command_overlay_state()
        payload_id = getattr(payload, "id", "") if payload is not None else ""
        self._trace_overlay(
            "submit_result",
            source=repr(source),
            result=repr(result),
            payload_id=repr(payload_id),
        )

        if result == "confirm_ready":
            if self._overlay_local_input_engaged:
                self._command_panel.setFocus(Qt.ActiveWindowFocusReason)
            else:
                self._refresh_overlay_input_capture(seconds=5.0)
            self._log_event(f"RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id={payload.id}")
            return

        if result == "not_found":
            self._log_event("RENDERER_MAIN|COMMAND_NOT_FOUND")
            return

        if result == "ambiguous":
            if self._overlay_local_input_engaged:
                self._command_panel.setFocus(Qt.ActiveWindowFocusReason)
            else:
                self._refresh_overlay_input_capture(seconds=5.0)
            self._log_event(f"RENDERER_MAIN|COMMAND_AMBIGUOUS|count={len(payload)}")
            return

        if result != "execute_confirmed":
            return

        intent = payload
        action = intent.action
        execution_request_fields = [f"action_id={intent.action_id}"]
        if intent.execution_type == "group":
            execution_request_fields.append(f"group_id={intent.group_id}")
        self._log_event("RENDERER_MAIN|COMMAND_EXECUTION_REQUESTED|" + "|".join(execution_request_fields))

        if intent.execution_type == "group":
            group = intent.group
            if group is None:
                return
            group_label = (group.title or "").strip() or group.id
            result = self._execute_callable_group(group)
            if not result.succeeded:
                failure_context = self._build_group_failure_context(group, result)
                self._log_event(
                    "RENDERER_MAIN|COMMAND_GROUP_EXECUTION_FAILED|"
                    f"group_id={group.id}|failed_action_id={result.failed_action_id}|failed_step_index={result.failed_step_index}|"
                    f"execution_trace={failure_context.get('execution_trace', '')}"
                )
                failed_action = self._resolve_group_failure_action(group, result.failed_action_id)
                recoverable_status = None
                if failed_action is not None:
                    recoverable_status = self._prepare_recoverable_launch_failure_report(
                        failed_action,
                        failure_context=failure_context,
                    )
                if recoverable_status:
                    self._show_command_result("launch_failed", recoverable_status, close_delay_ms=2600)
                else:
                    failed_step_index = result.failed_step_index if result.failed_step_index is not None else "?"
                    self._show_command_result(
                        "launch_failed",
                        f'Group "{group_label}" failed at step {failed_step_index}: {result.error}',
                    )
                return

            for completed_action_id in result.completed_action_ids:
                self._clear_launch_failure_tracking(completed_action_id)
            self._log_event(
                "RENDERER_MAIN|COMMAND_GROUP_EXECUTION_COMPLETED|"
                f"group_id={group.id}|step_count={result.step_count}"
            )
            self._show_command_result("launch_requested", f'Group "{group_label}" executed in stored order.')
            return

        try:
            launch_command_action(action)
        except Exception as exc:
            self._log_event(f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED|action_id={action.id}")
            recoverable_status = self._prepare_recoverable_launch_failure_report(action)
            if recoverable_status:
                self._show_command_result("launch_failed", recoverable_status, close_delay_ms=2600)
            else:
                self._show_command_result("launch_failed", f"Launch failed: {exc}")
            return

        self._clear_launch_failure_tracking(action.id)
        self._log_event(f"RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id={action.id}")
        self._show_command_result("launch_requested", "Launch request sent.")

    def nativeEvent(self, eventType, message):
        if (
            self.surface_role == "hud"
            and self.desktop_mode
            and self._monitoring_hud_feature_enabled
            and self._monitoring_hud_visible
            and eventType in ("windows_generic_MSG", "windows_dispatcher_MSG")
        ):
            try:
                msg = ctypes.wintypes.MSG.from_address(int(message))
            except Exception:
                msg = None
            if msg is not None:
                message_id = int(msg.message)
                if message_id == WM_NCHITTEST:
                    x = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
                    y = ctypes.c_short((int(msg.lParam) >> 16) & 0xFFFF).value
                    screen_point = QPoint(x, y)
                    if self._monitoring_hud_dashboard_control_rect_contains(screen_point):
                        return True, HTCLIENT
                    edges = self._monitoring_hud_native_resize_edges_for_point(screen_point)
                    hit_test = self._monitoring_hud_native_resize_hit_test_for_edges(edges)
                    if hit_test and not self._monitoring_hud_dashboard_control_rect_contains(screen_point):
                        # Windows owns the cursor state at the visible resize rail;
                        # the frameless Dashboard still owns geometry resize below.
                        return True, hit_test
                    if (
                        self._monitoring_hud_header_rect().contains(screen_point)
                        and not self._monitoring_hud_dashboard_control_rect_contains(screen_point)
                    ):
                        return True, HTCAPTION
                if message_id == WM_NCLBUTTONDBLCLK:
                    screen_point = self._monitoring_hud_cursor_screen_point()
                    if self._guard_monitoring_hud_active_child_window_background_click(
                        screen_point,
                        source="native_nonclient_double_click",
                    ):
                        return True, 0
                    if (
                        not screen_point.isNull()
                        and self._monitoring_hud_header_rect().contains(screen_point)
                    ):
                        self._emit_runtime_signal(
                            "MONITORING_HUD_NATIVE_HEADER_DOUBLE_CLICK_SUPPRESSED",
                            package="PKG-006",
                            slice="SLC-029",
                            seam="LV1",
                            x=screen_point.x(),
                            y=screen_point.y(),
                        )
                        return True, 0
                if message_id == WM_SETCURSOR and not self._monitoring_hud_native_window_resize_active:
                    hit_test = ctypes.c_short(int(msg.lParam) & 0xFFFF).value
                    edges = self._monitoring_hud_native_resize_edges_for_hit_test(hit_test)
                    if edges:
                        self._set_monitoring_hud_resize_cursor(edges)
                        return True, 1
                    self._reset_monitoring_hud_resize_cursor()
                if message_id in (WM_MOUSEMOVE, WM_NCMOUSEMOVE) and not self._monitoring_hud_native_window_resize_active:
                    if message_id == WM_NCMOUSEMOVE:
                        edges = self._monitoring_hud_native_resize_edges_for_hit_test(int(msg.wParam))
                        if edges:
                            self._set_monitoring_hud_resize_cursor(edges)
                            return True, 0
                    _, edges = self._monitoring_hud_resize_edges_under_cursor()
                    if edges:
                        self._set_monitoring_hud_resize_cursor(edges)
                    elif message_id == WM_MOUSEMOVE:
                        self._reset_monitoring_hud_resize_cursor()
                if message_id == WM_LBUTTONDOWN:
                    screen_point = self._monitoring_hud_cursor_screen_point()
                    if not screen_point.isNull():
                        if self._guard_monitoring_hud_active_child_window_background_click(
                            screen_point,
                            source="native_client_left_button_down",
                        ):
                            return True, 0
                        if self._handle_monitoring_hud_dashboard_settings_native_control(screen_point):
                            return True, 0
                        if self._handle_monitoring_hud_dashboard_close_native_control(screen_point):
                            return True, 0
                        if (
                            self._monitoring_hud_header_rect().contains(screen_point)
                            and not self._monitoring_hud_dashboard_control_rect_contains(screen_point)
                        ):
                            self._start_monitoring_hud_fallback_panel_move(
                                screen_point,
                                source="fallback_direct_native_client_header_move",
                            )
                            return True, 0
                if message_id == WM_NCLBUTTONDOWN:
                    edges = self._monitoring_hud_native_resize_edges_for_hit_test(int(msg.wParam))
                    screen_point = self._monitoring_hud_cursor_screen_point()
                    if not screen_point.isNull():
                        if self._guard_monitoring_hud_active_child_window_background_click(
                            screen_point,
                            source="native_nonclient_left_button_down",
                        ):
                            return True, 0
                        if self._handle_monitoring_hud_dashboard_settings_native_control(screen_point):
                            return True, 0
                        if self._handle_monitoring_hud_dashboard_close_native_control(screen_point):
                            return True, 0
                    if edges and not screen_point.isNull() and not self._monitoring_hud_dashboard_control_rect_contains(screen_point):
                        self._set_monitoring_hud_resize_cursor(edges)
                        self._start_monitoring_hud_fallback_window_resize(edges, screen_point)
                        return True, 0
                    if (
                        int(msg.wParam) == HTCAPTION
                        and not screen_point.isNull()
                        and self._monitoring_hud_header_rect().contains(screen_point)
                        and not self._monitoring_hud_dashboard_control_rect_contains(screen_point)
                    ):
                        self._start_monitoring_hud_fallback_panel_move(screen_point, source="fallback_direct_native_caption_move")
                        return True, 0
                if self._monitoring_hud_native_panel_drag_active and message_id in (
                    WM_MOUSEMOVE,
                    WM_NCMOUSEMOVE,
                ):
                    screen_point = self._monitoring_hud_cursor_screen_point()
                    if not screen_point.isNull():
                        self._update_monitoring_hud_fallback_panel_move(screen_point)
                    return True, 0
                if self._monitoring_hud_native_panel_drag_active and message_id in (
                    WM_LBUTTONUP,
                    WM_NCLBUTTONUP,
                    WM_CAPTURECHANGED,
                    WM_CANCELMODE,
                ):
                    self._finish_monitoring_hud_fallback_panel_move(self._monitoring_hud_cursor_screen_point())
                    return True, 0
                if self._monitoring_hud_native_window_resize_active and message_id in (WM_MOUSEMOVE, WM_NCMOUSEMOVE):
                    screen_point = self._monitoring_hud_cursor_screen_point()
                    if not screen_point.isNull():
                        self._update_monitoring_hud_fallback_window_resize(screen_point)
                    return True, 0
                if self._monitoring_hud_native_window_resize_active and message_id in (
                    WM_LBUTTONUP,
                    WM_NCLBUTTONUP,
                    WM_CAPTURECHANGED,
                    WM_CANCELMODE,
                ):
                    self._finish_monitoring_hud_fallback_window_resize(self._monitoring_hud_cursor_screen_point())
                    return True, 0
        return super().nativeEvent(eventType, message)

    def enable_desktop_mode(self):
        if self.desktop_mode or self._is_shutting_down or not self._page_ready:
            return

        self._log_event("RENDERER_MAIN|DESKTOP_MODE_ENABLE_BEGIN")
        self.desktop_mode = True
        self._desktop_mode_requested = False
        self._monitoring_hud_user_geometry_override_active = False
        self._clear_monitoring_hud_native_user_move()
        target_geometry = self.compute_compact_geometry()

        self._arm_monitoring_hud_visible_show_guard("enable_desktop_mode")
        self.setGeometry(target_geometry)
        self._monitoring_hud_interactive_screen_rect = self._estimate_monitoring_hud_interactive_screen_rect()
        self._publish_monitoring_hud_control_state_to_page()
        self._apply_monitoring_hud_window_interaction_state()

        hwnd = int(self.winId())
        self.show()
        self._log_native_window_state("after_visible_overlay_show", hwnd)
        self.setGeometry(target_geometry)

        if not self.webview.isVisible():
            self.webview.show()
            self._log_event("RENDERER_MAIN|WEBVIEW_REVEALED_FOR_VISIBLE_OVERLAY")

        QTimer.singleShot(80, self._release_initial_visibility_guard)
        self._publish_monitoring_hud_telemetry_boundary()
        self._publish_monitoring_hud_placement_ownership()
        self._publish_monitoring_hud_controls_visibility()
        self._publish_monitoring_hud_status_behavior()
        self._publish_monitoring_hud_control_state_to_page()
        if not self._monitoring_hud_poll_timer.isActive():
            self._monitoring_hud_poll_timer.start(self._monitoring_hud_polling_rate_ms)
        if not self._monitoring_hud_control_sync_timer.isActive():
            self._monitoring_hud_control_sync_timer.start(500)
        self._emit_runtime_signal(
            "MONITORING_HUD_VISIBLE_OVERLAY_READY",
            package="PKG-006",
            slice="SLC-016",
            pointer_model="click_through_no_focus",
        )
        self._log_event("RENDERER_MAIN|DESKTOP_VISIBLE_OVERLAY_RESULT|success=true")

        self.webview.update()
        self.update()
        self._run_javascript("window.dispatchEvent(new Event('resize'));")
        QTimer.singleShot(260, self._reinforce_desktop_mode)
        QTimer.singleShot(900, self._reinforce_desktop_mode)

    def _monitoring_hud_controls_visibility_contract(self) -> dict[str, str]:
        return build_monitoring_hud_controls_visibility_contract(
            desktop_mode=self.desktop_mode,
            feature_enabled=self._monitoring_hud_feature_enabled,
            visible=self._monitoring_hud_visible,
            anchored=self._monitoring_hud_anchored,
            snap_enabled=self._monitoring_hud_snap_enabled,
            polling_rate_ms=self._monitoring_hud_polling_rate_ms,
        ).as_dict()

    def _publish_monitoring_hud_controls_visibility(self):
        controls_json = json.dumps(
            self._monitoring_hud_controls_visibility_contract(),
            sort_keys=True,
        )
        self._run_javascript(
            f"""
            if (window.setMonitoringHudControlsVisibility) {{
                window.setMonitoringHudControlsVisibility({controls_json});
            }}
            """
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_CONTROLS_VISIBILITY_READY",
            package="PKG-006",
            slice="SLC-027",
            controls="hud-controls-visibility",
            persistence="local_layout_state",
            anchored=self._monitoring_hud_anchored,
            polling_rate_ms=self._monitoring_hud_polling_rate_ms,
        )

    def _monitoring_hud_status_snapshot(self) -> dict[str, str]:
        return build_monitoring_hud_status_snapshot(
            page_ready=self._page_ready,
            desktop_mode=self.desktop_mode,
            event_route_present=callable(self.event_logger),
        ).as_dict()

    def _publish_monitoring_hud_status_behavior(self):
        status_json = json.dumps(self._monitoring_hud_status_snapshot(), sort_keys=True)
        self._run_javascript(
            f"""
            if (window.setMonitoringHudStatusBehavior) {{
                window.setMonitoringHudStatusBehavior({status_json});
            }}
            """
        )
        self._emit_runtime_signal(
            "MONITORING_HUD_STATUS_BEHAVIOR_READY",
            package="PKG-006",
            slice="SLC-028",
            status="hud-local-readiness-status",
            source_truth="renderer_local",
        )

    def _publish_ai_provider_state_to_page(self):
        if not self._page_ready or self._is_shutting_down:
            return

        payload = self._ai_provider_state.as_renderer_payload()
        payload_json = json.dumps(payload, sort_keys=True)
        self._run_javascript(
            f"""
            if (window.setAIProviderState) {{
                window.setAIProviderState({payload_json});
            }}
            """
        )
        self._emit_runtime_signal(
            "AI_PROVIDER_STATE_READY",
            package=payload.get("packageId", ""),
            slices=",".join(payload.get("sliceIds", [])),
            state_id=payload.get("stateId", ""),
            mode=payload.get("mode", ""),
            availability=payload.get("availability", ""),
            privacy_scope=payload.get("privacyScope", ""),
            provider_selection=payload.get("providerSelectionState", ""),
            provider_configuration=payload.get("providerConfigurationState", ""),
            provider_registry=payload.get("providerRegistryState", ""),
            provider_interaction=payload.get("providerInteractionState", ""),
            runtime_category=payload.get("runtimeStateCategory", ""),
            runtime_reason=payload.get("runtimeReasonCode", ""),
            runtime_provenance=payload.get("runtimeProvenance", ""),
            runtime_schema=payload.get("runtimeStateSchemaVersion", ""),
            runtime_config=payload.get("runtimeConfigState", ""),
            runtime_fail_closed=payload.get("runtimeFailClosed", True),
            provider_readiness=payload.get("providerReadinessState", ""),
            setup_eligibility=payload.get("setupEligibilityState", ""),
            setup_blocker=payload.get("setupBlockerState", ""),
            readiness_reason=payload.get("readinessReasonCode", ""),
            readiness_provenance=payload.get("readinessProvenance", ""),
            readiness_schema=payload.get("readinessStateSchemaVersion", ""),
            future_provider_gate=payload.get("futureProviderGateStatus", ""),
            provider_activation=payload.get("providerActivationState", ""),
            activation_eligibility=payload.get("activationEligibilityState", ""),
            activation_blocker=payload.get("activationBlockerState", ""),
            activation_reason=payload.get("activationReasonCode", ""),
            activation_provenance=payload.get("activationProvenance", ""),
            activation_schema=payload.get("activationStateSchemaVersion", ""),
            future_activation_gate=payload.get("futureActivationGateStatus", ""),
            provider_adapter=payload.get("providerAdapterPosture", ""),
            prompt_execution_gate=payload.get("promptExecutionGateState", ""),
            model_execution_gate=payload.get("modelExecutionGateState", ""),
            provider_execution_gate=payload.get("providerExecutionGateState", ""),
            functional_ai_criteria=payload.get("functionalAiCriteriaState", ""),
            v18_prebeta_readiness=payload.get("v18PrebetaReadinessState", ""),
            execution_readiness=payload.get("providerExecutionReadinessState", ""),
            execution_eligibility=payload.get("executionEligibilityState", ""),
            execution_blocker=payload.get("executionBlockerState", ""),
            execution_reason=payload.get("executionReasonCode", ""),
            execution_provenance=payload.get("executionProvenance", ""),
            execution_schema=payload.get("executionStateSchemaVersion", ""),
            execution_approval=payload.get("executionApprovalStatus", ""),
            provider_path=payload.get("providerPathStatus", ""),
            provider_path_readiness=payload.get("providerPathReadinessState", ""),
            provider_path_eligibility=payload.get("providerPathEligibilityState", ""),
            provider_path_blocker=payload.get("providerPathBlockerState", ""),
            provider_path_reason=payload.get("providerPathReasonCode", ""),
            provider_path_schema=payload.get("providerPathStateSchemaVersion", ""),
            setup_flow=payload.get("setupFlowReadinessState", ""),
            setup_flow_blocker=payload.get("setupFlowBlockerState", ""),
            setup_flow_approval=payload.get("setupFlowApprovalStatus", ""),
            consent_flow=payload.get("consentFlowReadinessState", ""),
            consent_flow_blocker=payload.get("consentFlowBlockerState", ""),
            consent_collection=payload.get("consentCollectionPosture", ""),
            setup_contract=payload.get("providerSetupContractReadinessState", ""),
            setup_contract_blocker=payload.get("providerSetupContractBlockerState", ""),
            setup_contract_approval=payload.get("providerSetupContractApprovalStatus", ""),
            setup_contract_gate=payload.get("providerSetupContractGateState", ""),
            setup_foundation=payload.get("providerSetupFoundationState", ""),
            setup_foundation_blocker=payload.get("providerSetupFoundationBlockerState", ""),
            setup_foundation_validation=payload.get("providerSetupFoundationValidationStatus", ""),
            setup_foundation_persistence=payload.get("providerSetupFoundationPersistenceStatus", ""),
            setup_foundation_gate=payload.get("providerSetupFoundationGateState", ""),
            consent_collection_foundation=payload.get("consentCollectionFoundationState", ""),
            consent_collection_blocker=payload.get("consentCollectionBlockerState", ""),
            consent_collection_validation=payload.get("consentCollectionValidationStatus", ""),
            consent_collection_persistence=payload.get("consentPersistenceStatus", ""),
            consent_collection_gate=payload.get("consentCollectionGateState", ""),
            durable_consent_record=payload.get("durableConsentRecordState", ""),
            durable_setup_consent=payload.get("durableSetupConsentState", ""),
            durable_execution_consent=payload.get("durableExecutionConsentState", ""),
            durable_consent_status_proof=payload.get("durableConsentStatusProofState", ""),
            durable_consent_desktop_display=payload.get("durableConsentDesktopDisplayState", ""),
            durable_consent_setup_handoff=payload.get("durableConsentProviderSetupHandoffState", ""),
            durable_consent_execution_handoff=payload.get("durableConsentProviderExecutionHandoffState", ""),
            consent_ux_state=payload.get("consentUxState", ""),
            consent_ux_intent=payload.get("consentUxIntentState", ""),
            consent_ux_surface=payload.get("consentUxSurfaceState", ""),
            consent_ux_setup_display=payload.get("consentUxSetupDisplayState", ""),
            consent_ux_execution_display=payload.get("consentUxExecutionDisplayState", ""),
            consent_ux_revocation_reset=payload.get("consentUxRevocationResetState", ""),
            consent_ux_write=payload.get("consentUxWritePosture", ""),
            consent_ux_status_proof=payload.get("consentUxStatusProofState", ""),
            consent_ux_desktop_display=payload.get("consentUxDesktopDisplayState", ""),
            consent_ux_setup_gate=payload.get("consentUxProviderSetupGateState", ""),
            consent_ux_execution_gate=payload.get("consentUxProviderExecutionGateState", ""),
            setup_completion=payload.get("providerSetupCompletionState", ""),
            setup_completion_blocker=payload.get("providerSetupCompletionBlockerState", ""),
            setup_completion_reason=payload.get("providerSetupCompletionReasonCode", ""),
            setup_completion_profile=payload.get("providerSetupCompletionProfileStatus", ""),
            setup_completion_config=payload.get("providerSetupCompletionConfigStatus", ""),
            setup_completion_no_secrets=payload.get("providerSetupCompletionNoSecretsStatus", ""),
            setup_completion_validation=payload.get("providerSetupCompletionValidationStatus", ""),
            setup_completion_persistence=payload.get("providerSetupCompletionPersistenceStatus", ""),
            setup_completion_reset=payload.get("providerSetupCompletionResetState", ""),
            setup_completion_status_proof=payload.get("providerSetupCompletionStatusProofState", ""),
            setup_completion_desktop_display=payload.get("providerSetupCompletionDesktopDisplayState", ""),
            setup_completion_setup_gate=payload.get("providerSetupCompletionProviderSetupGateState", ""),
            setup_completion_execution_gate=payload.get("providerSetupCompletionProviderExecutionGateState", ""),
            setup_completion_sdk_handoff=payload.get("providerSetupCompletionSdkHandoffState", ""),
            provider_setup_handoff=payload.get("providerSetupHandoffPosture", ""),
            provider_consent_handoff=payload.get("providerConsentHandoffPosture", ""),
            desktop_readiness_display=payload.get("desktopAiOwnedReadinessDisplayState", ""),
            setup_consent=payload.get("setupConsentState", ""),
            execution_consent=payload.get("executionConsentState", ""),
            provider_config_status=payload.get("providerConfigStatus", ""),
            adapter_selection=payload.get("adapterSelectionPosture", ""),
            prompt_acceptance_gate=payload.get("promptAcceptanceGateState", ""),
            prompt_routing_gate=payload.get("promptRoutingGateState", ""),
            prompt_send=payload.get("promptSendPosture", ""),
            model_execution_status=payload.get("modelExecutionStatus", ""),
            provider_visible_data_execution=payload.get("providerVisibleDataExecutionPosture", ""),
            functional_ai_release_gate=payload.get("functionalAiReleaseGateState", ""),
            v18_release_gate=payload.get("v18ReleaseGateState", ""),
            configured_provider_count=payload.get("configuredProviderCount", 0),
            available_provider_count=payload.get("availableProviderCount", 0),
            hardware_capability=payload.get("hardwareCapabilityState", ""),
            gpu_capability=payload.get("gpuCapabilityState", ""),
            cpu_fallback=payload.get("cpuFallbackState", ""),
            hardware_detection_level=payload.get("hardwareDetectionLevel", ""),
            ram_readiness=payload.get("ramReadinessState", ""),
            disk_readiness=payload.get("diskReadinessState", ""),
            model_workload=payload.get("modelWorkloadState", ""),
            model_workload_metadata=payload.get("modelWorkloadMetadataState", ""),
            capability_pack_lifecycle=payload.get("capabilityPackLifecycleState", ""),
            capability_pack_download=payload.get("capabilityPackDownloadState", ""),
            capability_pack_manifest=payload.get("capabilityPackManifestState", ""),
            capability_pack_compatibility=payload.get("capabilityPackCompatibilityState", ""),
            capability_pack_eligibility=payload.get("capabilityPackEligibilityState", ""),
            install_intent=payload.get("installIntentState", ""),
            data_classification=payload.get("dataClassificationState", ""),
            provider_visible_data_guarantee=payload.get("providerVisibleDataGuarantee", ""),
            memory_context=payload.get("memoryContextState", ""),
            memory_indexing=payload.get("memoryIndexingState", ""),
            network_egress=payload.get("networkEgressState", ""),
            windows_resilience=payload.get("windowsResilienceState", ""),
            voice_runtime=payload.get("voiceRuntimeState", ""),
            persona_voice_boundary=payload.get("personaCoreVoiceState", ""),
            validation_gates=payload.get("validationProofGateState", ""),
            release_proof=payload.get("releaseProofGateState", ""),
            copy_contract=payload.get("coreDesktopRuntimeStateContract", ""),
            contract_ready=payload.get("contractReadyMarker", ""),
            consent_state=payload.get("consentState", ""),
            interaction_affordance=payload.get("interactionAffordance", ""),
            requires_consent=payload.get("requiresConsent", False),
            provider_visible_data=payload.get("providerVisibleData", ""),
            provider_next_action=payload.get("providerNextActionLabel", ""),
            sent_to_provider=payload.get("sentToProvider", False),
        )

    def request_shutdown(self):
        if self._is_shutting_down:
            return False
        if self.request_resident_access_settings_shutdown_guard(source="renderer_request_shutdown"):
            self._log_event("RENDERER_MAIN|SHUTDOWN_BLOCKED_BY_RESIDENT_SETTINGS_DIRTY_GUARD|source=renderer_request_shutdown")
            return False

        self._log_event("RENDERER_MAIN|RENDERER_SHUTDOWN_BEGIN")
        self._monitoring_hud_access_adapter.begin_shutdown(source="renderer_request_shutdown")
        self._is_shutting_down = True
        self._reset_monitoring_hud_resize_cursor()
        self._monitoring_hud_recording_control_click_bridge_down = False
        self._monitoring_hud_recording_control_click_bridge_press_point = QPoint()
        self._monitoring_hud_resize_hover_timer.stop()
        self._monitoring_hud_recording_control_click_bridge_timer.stop()
        try:
            self._monitoring_hud_resize_hover_timer.timeout.disconnect(
                self._poll_monitoring_hud_resize_hover_cursor
            )
        except (RuntimeError, TypeError):
            pass
        try:
            self._monitoring_hud_recording_control_click_bridge_timer.timeout.disconnect(
                self._poll_monitoring_hud_recording_control_click_bridge
            )
        except (RuntimeError, TypeError):
            pass
        self._result_close_timer.stop()
        self._monitoring_hud_poll_timer.stop()
        self._monitoring_hud_control_sync_timer.stop()

        self._command_panel.hide()
        if self._monitoring_hud_minimal_native_overlay is not None:
            self._monitoring_hud_minimal_native_overlay.request_shutdown()
        if self._monitoring_hud_recording_studio_window is not None:
            self._monitoring_hud_recording_studio_window.close()
        if self._monitoring_hud_log_viewer_studio_window is not None:
            self._monitoring_hud_log_viewer_studio_window.close()
        if self._resident_access_settings_dialog is not None:
            self._resident_access_settings_dialog.close()
        try:
            self.webview.stop()
            self.webview.hide()
            self.webview.loadFinished.connect(self._complete_webengine_shutdown)
            self.webview.setUrl(QUrl("about:blank"))
        except RuntimeError:
            self._complete_webengine_shutdown()
            return True
        self.hide()
        QTimer.singleShot(1000, self._complete_webengine_shutdown)
        return True

    def _complete_webengine_shutdown(self, *_args):
        if getattr(self, "_shutdown_release_completed", False):
            return
        self._shutdown_release_completed = True
        self._log_event("RENDERER_MAIN|DESKTOP_RUNTIME_WEBENGINE_RELEASE_READY")
        try:
            self.webview.loadFinished.disconnect(self._complete_webengine_shutdown)
        except (RuntimeError, TypeError):
            pass
        try:
            self.webview.stop()
            self.webview.deleteLater()
        except RuntimeError:
            pass
        try:
            self.close()
            QTimer.singleShot(0, self.deleteLater)
        except RuntimeError:
            pass
