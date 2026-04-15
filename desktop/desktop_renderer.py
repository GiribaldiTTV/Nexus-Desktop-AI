import os
import re
import ctypes
import datetime
import time
import webbrowser
from html import escape

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
)
from PySide6.QtCore import Qt, QTimer, QUrl, QRect, Signal, QPoint
from PySide6.QtGui import QColor, QFont
from PySide6.QtWebEngineWidgets import QWebEngineView

from .interaction_overlay_model import CommandOverlayModel
from .saved_action_authoring import (
    SavedActionDraft,
    SavedActionDraftValidationError,
    SavedActionUnsafeSourceError,
    create_saved_action_from_draft,
    delete_saved_action,
    load_saved_action_draft_for_edit,
    update_saved_action_from_draft,
)
from .saved_action_source import SavedActionSourceWriteBlocked
from .shared_action_model import (
    build_saved_action_callable_phrases,
    default_saved_action_trigger_mode,
    launch_command_action,
)
from .orin_support_reporting import SupportBundleError, prepare_manual_issue_report
from .workerw_utils import (
    attach_window_to_desktop,
    get_last_workerw_probe_events,
    make_window_noninteractive,
    position_desktop_child,
)

WM_NCHITTEST = 0x0084
HTTRANSPARENT = -1
user32 = ctypes.windll.user32
GetWindowRect = user32.GetWindowRect
GetWindowRect.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.wintypes.RECT)]
GetWindowRect.restype = ctypes.c_bool
GetForegroundWindow = user32.GetForegroundWindow
GetForegroundWindow.restype = ctypes.wintypes.HWND
GetClassNameW = user32.GetClassNameW
GetClassNameW.argtypes = [ctypes.wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]
GetClassNameW.restype = ctypes.c_int
GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = [ctypes.wintypes.HWND]
GetWindowTextLengthW.restype = ctypes.c_int
GetWindowTextW = user32.GetWindowTextW
GetWindowTextW.argtypes = [ctypes.wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]
GetWindowTextW.restype = ctypes.c_int
ShowWindowW = user32.ShowWindow
ShowWindowW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
ShowWindowW.restype = ctypes.c_bool
IsWindowVisible = user32.IsWindowVisible
IsWindowVisible.argtypes = [ctypes.wintypes.HWND]
IsWindowVisible.restype = ctypes.c_bool
GetParentW = user32.GetParent
GetParentW.argtypes = [ctypes.wintypes.HWND]
GetParentW.restype = ctypes.wintypes.HWND
SW_HIDE = 0
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_BORDER_COLOR = 34
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36
DWMWCP_ROUND = 2


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


def _clear_layout_widgets(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.deleteLater()
        elif child_layout is not None:
            _clear_layout_widgets(child_layout)


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
        item_text += f"\n{' • '.join(metadata_bits)}"
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
        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(12, 12, 12, 12)
        item_layout.setSpacing(12)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)

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
            button_layout.setContentsMargins(7, 7, 7, 7)
            button_layout.setSpacing(6)

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
    def __init__(self, title: str, dialog: QDialog, *, object_prefix: str, parent=None, show_title: bool = False):
        super().__init__(parent or dialog)
        self._dialog = dialog
        self._drag_offset: QPoint | None = None
        self.setObjectName(f"{object_prefix}ChromeBar")
        self.setProperty("chromeRole", "bar")
        self.setProperty("showTitle", bool(show_title))
        self.setCursor(Qt.OpenHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 0)
        layout.setSpacing(6)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName(f"{object_prefix}ChromeTitle")
        self.title_label.setProperty("chromeRole", "title")
        self.title_label.setVisible(bool(show_title))
        layout.addWidget(self.title_label, 0, Qt.AlignVCenter)
        layout.addStretch(1)

        self.close_button = QPushButton("\N{MULTIPLICATION SIGN}", self)
        self.close_button.setObjectName(f"{object_prefix}ChromeClose")
        self.close_button.setProperty("chromeRole", "close")
        self.close_button.setToolTip("Close")
        close_font = QFont("Segoe UI Symbol")
        close_font.setPointSize(11)
        close_font.setWeight(QFont.DemiBold)
        self.close_button.setFont(close_font)
        self.close_button.setFixedSize(24, 20)
        self.close_button.clicked.connect(self._dialog.reject)
        layout.addWidget(self.close_button, 0, Qt.AlignVCenter)
        self.setFixedHeight(28)

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
        lifecycle_callback=None,
        dialog_signal_name: str = "CUSTOM_TASK_CREATE_DIALOG",
    ):
        super().__init__(parent)
        self._submit_handler = submit_handler
        self._lifecycle_callback = lifecycle_callback
        self._dialog_signal_name = dialog_signal_name
        self._ready_signal_emitted = False
        self._syncing_trigger_selection = False
        self._trigger_manually_changed = False
        self._loaded_trigger_follows_default = True
        self._preserve_legacy_bare_trigger = False
        self._invocation_mode = "aliases_only"
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle(dialog_title)
        self.setObjectName("savedActionCreateDialog")
        self.setMinimumWidth(820)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("savedActionCreateShell")
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.content = QWidget(self.shell)
        self.content.setObjectName("savedActionCreateContent")
        shell_layout.addWidget(self.content)

        self.chrome_bar = DialogChromeBar(
            dialog_title,
            self,
            object_prefix="savedActionCreate",
            parent=self.shell,
            show_title=False,
        )
        self.chrome_bar.raise_()

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(24, 10, 24, 16)
        layout.setSpacing(10)

        self.title_label = QLabel(heading_text, self)
        self.title_label.setObjectName("savedActionCreateTitle")
        layout.addWidget(self.title_label)

        self.hint_label = QLabel(hint_text, self)
        self.hint_label.setObjectName("savedActionCreateHint")
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        form = QGridLayout()
        self.form_layout = form
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)
        form.setColumnMinimumWidth(0, 128)
        form.setColumnStretch(1, 1)

        self.type_header, self.type_header_label, self.type_help_button = self._make_form_header(
            "Task type",
            tooltip_text=self.TASK_TYPE_TOOLTIP_TEXT,
            object_name="savedActionCreateTypeHeader",
            help_object_name="savedActionCreateTypeHelp",
        )
        form.addWidget(self.type_header, 0, 0)
        self.type_combo = QComboBox(self)
        self.type_combo.setObjectName("savedActionCreateType")
        self.type_combo.setMinimumHeight(42)
        for label, target_kind in self.ACTION_TYPE_OPTIONS:
            self.type_combo.addItem(label, target_kind)
        self.type_combo.currentIndexChanged.connect(self._handle_target_kind_changed)
        form.addWidget(self.type_combo, 0, 1)

        self.title_header, self.title_header_label, self.title_help_button = self._make_form_header(
            "Title",
            tooltip_text=self.TITLE_TOOLTIP_TEXT,
            object_name="savedActionCreateTitleHeader",
            help_object_name="savedActionCreateTitleHelp",
        )
        form.addWidget(self.title_header, 1, 0)
        self.title_input = QLineEdit(self)
        self.title_input.setObjectName("savedActionCreateTitleInput")
        self.title_input.setMinimumHeight(42)
        self.title_input.setPlaceholderText("Open Reports")
        self.title_input.textChanged.connect(self._refresh_examples_box)
        form.addWidget(self.title_input, 1, 1)

        self.trigger_header, self.trigger_header_label, self.trigger_help_button = self._make_form_header(
            "Trigger",
            tooltip_text=self.TRIGGER_TOOLTIP_TEXT,
            object_name="savedActionCreateTriggerHeader",
            help_object_name="savedActionCreateTriggerHelp",
        )
        form.addWidget(self.trigger_header, 2, 0)
        self.trigger_combo = QComboBox(self)
        self.trigger_combo.setObjectName("savedActionCreateTrigger")
        self.trigger_combo.setMinimumHeight(42)
        for label, trigger_mode in self.TRIGGER_OPTIONS:
            self.trigger_combo.addItem(label, trigger_mode)
        self.trigger_combo.currentIndexChanged.connect(self._handle_trigger_selection_changed)
        self.custom_triggers_input = QLineEdit(self)
        self.custom_triggers_input.setObjectName("savedActionCreateCustomTriggersInput")
        self.custom_triggers_input.setMinimumHeight(42)
        self.custom_triggers_input.setPlaceholderText("Force Open, Duck Duck Goose")
        self.custom_triggers_input.textChanged.connect(self._refresh_examples_box)
        trigger_row = QVBoxLayout()
        trigger_row.setContentsMargins(0, 0, 0, 0)
        trigger_row.setSpacing(6)
        trigger_row.addWidget(self.trigger_combo)
        trigger_row.addWidget(self.custom_triggers_input)
        form.addLayout(trigger_row, 2, 1)

        self.aliases_header, self.aliases_header_label, self.aliases_help_button = self._make_form_header(
            "Aliases",
            tooltip_text=self.ALIASES_TOOLTIP_TEXT,
            object_name="savedActionCreateAliasesHeader",
            help_object_name="savedActionCreateAliasesHelp",
        )
        form.addWidget(self.aliases_header, 3, 0)
        self.aliases_input = QLineEdit(self)
        self.aliases_input.setObjectName("savedActionCreateAliasesInput")
        self.aliases_input.setMinimumHeight(42)
        self.aliases_input.setPlaceholderText("Required, comma-separated")
        self.aliases_input.textChanged.connect(self._refresh_examples_box)
        form.addWidget(self.aliases_input, 3, 1)

        self.target_header, self.target_header_label, self.target_help_button = self._make_form_header(
            "Target",
            tooltip_text="",
            object_name="savedActionCreateTargetHeader",
            help_object_name="savedActionCreateTargetHelp",
        )
        form.addWidget(self.target_header, 4, 0)
        self.target_input = QLineEdit(self)
        self.target_input.setObjectName("savedActionCreateTargetInput")
        self.target_input.setMinimumHeight(42)
        self.target_browse_button = QPushButton("Browse...", self)
        self.target_browse_button.setObjectName("savedActionCreateTargetBrowseButton")
        self.target_browse_button.setMinimumHeight(42)
        self.target_browse_button.setMinimumWidth(112)
        self.target_browse_button.clicked.connect(self._handle_target_browse_clicked)
        target_row = QHBoxLayout()
        target_row.setContentsMargins(0, 0, 0, 0)
        target_row.setSpacing(8)
        target_row.addWidget(self.target_input, 1)
        target_row.addWidget(self.target_browse_button, 0)
        form.addLayout(target_row, 4, 1)

        content_row = QHBoxLayout()
        self.content_row = content_row
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(16)
        content_row.addLayout(form, 1)

        self.status_label = QLabel("", self)
        self.status_label.setObjectName("savedActionCreateStatus")
        self.status_label.setWordWrap(True)

        self.target_examples_box = QFrame(self)
        self.target_examples_box.setObjectName("savedActionCreateTargetExamplesBox")
        self.target_examples_box.setMinimumWidth(268)
        self.target_examples_box.setMaximumWidth(292)
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

        content_row.addWidget(self.target_examples_box, 0, Qt.AlignTop)

        layout.addLayout(content_row)
        layout.addWidget(self.status_label)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 2, 0, 0)
        button_row.setSpacing(8)
        button_row.addStretch(1)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setObjectName("savedActionCreateCancelButton")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self.cancel_button)

        self.create_button = QPushButton(submit_button_text, self)
        self.create_button.setObjectName("savedActionCreateSubmitButton")
        self.create_button.setMinimumHeight(40)
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self._handle_create_clicked)
        button_row.addWidget(self.create_button)

        layout.addLayout(button_row)

        self.setStyleSheet(
            """
            #savedActionCreateDialog {
                background: transparent;
            }
            #savedActionCreateShell {
                border-radius: 20px;
                border: 1px solid rgba(118, 226, 255, 0.16);
                background: rgb(9, 18, 28);
            }
            #savedActionCreateContent {
                background: transparent;
            }
            #savedActionCreateChromeBar {
                border: none;
                background: transparent;
            }
            #savedActionCreateChromeTitle {
                color: rgba(126, 171, 181, 0.84);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.08em;
            }
            #savedActionCreateChromeClose {
                min-width: 24px;
                max-width: 24px;
                min-height: 20px;
                max-height: 20px;
                padding: 0 0 1px 0;
                text-align: center;
                border-radius: 8px;
                border: 1px solid rgba(118, 226, 255, 0.10);
                background: rgba(11, 26, 40, 0.52);
                color: rgba(191, 212, 207, 0.94);
                font-size: 12px;
                font-weight: 600;
            }
            #savedActionCreateChromeClose:hover {
                border: 1px solid rgba(102, 219, 204, 0.24);
                background: rgba(15, 36, 52, 0.70);
            }
            #savedActionCreateTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 24px;
                font-weight: 650;
            }
            #savedActionCreateHint {
                color: rgba(136, 165, 174, 0.88);
                font-size: 12px;
                line-height: 1.45em;
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
                border-radius: 15px;
                border: 1px solid rgba(118, 226, 255, 0.10);
                background: rgba(7, 20, 34, 176);
            }
            #savedActionCreateTargetExamplesTitle {
                color: rgba(84, 192, 181, 0.88);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            #savedActionCreateTargetExamples {
                color: rgba(168, 193, 199, 0.93);
                font-size: 12px;
                line-height: 1.45em;
            }
            #savedActionCreateStatus {
                min-height: 14px;
                color: rgba(255, 189, 176, 0.96);
                font-size: 13px;
            }
            QLabel[createRole="label"] {
                color: rgba(78, 176, 173, 0.76);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.08em;
            }
            QLabel[createRole="fieldHeader"], QLabel[createRole="fieldHeaderHelp"] {
                color: rgba(182, 206, 198, 0.96);
                font-size: 15px;
                font-weight: 650;
            }
            QLabel[createRole="fieldHeaderHelp"] {
                padding-bottom: 2px;
                border-bottom: 1px dotted rgba(102, 219, 204, 0.24);
            }
            QLabel[createRole="fieldHeaderHelp"]:hover {
                color: rgba(198, 218, 211, 0.99);
                border-bottom: 1px dotted rgba(102, 219, 204, 0.50);
            }
            QLabel[createRole="fieldHeaderHelp"]:focus {
                color: rgba(198, 218, 211, 0.99);
                border-bottom: 1px solid rgba(102, 219, 204, 0.50);
            }
            QLineEdit, QComboBox {
                min-height: 42px;
                border-radius: 13px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(193, 213, 208, 0.96);
                padding: 7px 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid rgba(118, 226, 255, 0.42);
                background: rgba(8, 23, 38, 216);
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
                min-height: 40px;
                padding: 0 18px;
                border-radius: 11px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(6, 18, 30, 196);
                color: rgba(191, 212, 207, 0.96);
            }
            QPushButton:hover {
                border: 1px solid rgba(118, 226, 255, 0.34);
            }
            #savedActionCreateCancelButton {
                background: rgba(7, 18, 30, 184);
            }
            #savedActionCreateSubmitButton {
                border: 1px solid rgba(118, 226, 255, 0.34);
                background: rgba(18, 52, 78, 230);
                font-weight: 600;
            }
            #savedActionCreateSubmitButton:hover {
                border: 1px solid rgba(118, 226, 255, 0.52);
                background: rgba(22, 61, 90, 238);
            }
            """
        )

        self._apply_default_trigger_mode(force=True)
        self._sync_trigger_ui_from_selection(mark_manual=False)
        self._trigger_manually_changed = False
        self._update_target_guidance()
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
        self._emit_lifecycle_event("opened")
        QTimer.singleShot(0, self._emit_ready_signal)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_chrome_overlay_geometry()

    def done(self, result):
        self._emit_lifecycle_event(
            "closed",
            result="accepted" if result == QDialog.Accepted else "rejected",
        )
        super().done(result)

    def _update_chrome_overlay_geometry(self):
        if not hasattr(self, "chrome_bar") or not hasattr(self, "shell"):
            return
        self.chrome_bar.setGeometry(6, 6, max(72, self.shell.width() - 12), self.chrome_bar.height())
        self.chrome_bar.raise_()

    def _make_form_header(
        self,
        text: str,
        *,
        tooltip_text: str,
        object_name: str,
        help_object_name: str,
    ) -> tuple[QWidget, QLabel, QLabel]:
        container = QWidget(self)
        container.setObjectName(object_name)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = ImmediateHelpButton(container)
        label.setObjectName(help_object_name)
        label.setProperty("createRole", "fieldHeaderHelp")
        label.setText(text)
        label.setToolTip(tooltip_text)
        header_font = label.font()
        header_font.setPointSize(max(16, header_font.pointSize()))
        header_font.setBold(True)
        label.setFont(header_font)
        layout.addWidget(label, 0, Qt.AlignVCenter)
        layout.addStretch(1)
        return container, label, label

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
            "<div style=\"margin: 0; padding: 6px 8px; "
            "border-radius: 10px; border: 1px solid rgba(102, 219, 204, 0.08); "
            "background: rgba(11, 29, 44, 0.34);\">"
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
        self.status_label.setText(self._format_error_text(text))

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


class CreatedTasksDialog(QDialog):
    def __init__(self, parent=None, inventory_payload: dict | None = None, lifecycle_callback=None):
        super().__init__(parent)
        self._selected_action_id = ""
        self._selected_delete_action_id = ""
        self._lifecycle_callback = lifecycle_callback
        self._ready_signal_emitted = False
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("Manage Custom Tasks")
        self.setObjectName("savedActionCreatedTasksDialog")
        self.setMinimumWidth(660)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)

        self.shell = QFrame(self)
        self.shell.setObjectName("savedActionCreatedTasksShell")
        root_layout.addWidget(self.shell)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.content = QWidget(self.shell)
        self.content.setObjectName("savedActionCreatedTasksContent")
        shell_layout.addWidget(self.content)

        self.chrome_bar = DialogChromeBar(
            "Manage Custom Tasks",
            self,
            object_prefix="savedActionCreatedTasks",
            parent=self.shell,
            show_title=False,
        )
        self.chrome_bar.raise_()

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(20, 10, 20, 14)
        layout.setSpacing(8)

        self.title_label = QLabel("Manage Custom Tasks", self)
        self.title_label.setObjectName("savedActionCreatedTasksTitle")
        layout.addWidget(self.title_label)

        self.hint_label = QLabel(
            "Review, update, or remove tasks from the current saved-task source.",
            self,
        )
        self.hint_label.setObjectName("savedActionCreatedTasksHint")
        self.hint_label.setWordWrap(True)
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
        self.items_layout.setSpacing(8)

        self.items_scroll = QScrollArea(self)
        self.items_scroll.setObjectName("savedActionCreatedTasksItemsScroll")
        self.items_scroll.setFrameShape(QFrame.NoFrame)
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.items_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.items_scroll.setFocusPolicy(Qt.NoFocus)
        self.items_scroll.setMaximumHeight(300)
        self.items_scroll.viewport().setObjectName("savedActionCreatedTasksViewport")
        self.items_scroll.viewport().setAutoFillBackground(False)
        self.items_scroll.setWidget(self.items_frame)
        layout.addWidget(self.items_scroll)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 2, 0, 0)
        button_row.setSpacing(8)
        button_row.addStretch(1)

        self.close_button = QPushButton("Close", self)
        self.close_button.setObjectName("savedActionCreatedTasksClose")
        self.close_button.setMinimumHeight(36)
        self.close_button.clicked.connect(self.reject)
        button_row.addWidget(self.close_button)

        layout.addLayout(button_row)

        self.setStyleSheet(
            """
            #savedActionCreatedTasksDialog {
                background: transparent;
            }
            #savedActionCreatedTasksShell {
                border-radius: 20px;
                border: 1px solid rgba(118, 226, 255, 0.14);
                background: rgba(4, 16, 28, 244);
            }
            #savedActionCreatedTasksContent {
                background: transparent;
            }
            #savedActionCreatedTasksChromeBar {
                border: none;
                background: transparent;
            }
            #savedActionCreatedTasksChromeTitle {
                color: rgba(126, 171, 181, 0.84);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.08em;
            }
            #savedActionCreatedTasksChromeClose {
                min-width: 24px;
                max-width: 24px;
                min-height: 20px;
                max-height: 20px;
                padding: 0 0 1px 0;
                text-align: center;
                border-radius: 8px;
                border: 1px solid rgba(118, 226, 255, 0.10);
                background: rgba(11, 26, 40, 0.52);
                color: rgba(191, 212, 207, 0.94);
                font-size: 12px;
                font-weight: 600;
            }
            #savedActionCreatedTasksChromeClose:hover {
                border: 1px solid rgba(102, 219, 204, 0.24);
                background: rgba(15, 36, 52, 0.70);
            }
            #savedActionCreatedTasksTitle {
                color: rgba(188, 212, 203, 0.97);
                font-size: 24px;
                font-weight: 650;
            }
            #savedActionCreatedTasksHint {
                color: rgba(136, 165, 174, 0.88);
                font-size: 12px;
                line-height: 1.45em;
            }
            #savedActionCreatedTasksStatus {
                color: rgba(148, 180, 178, 0.89);
                font-size: 12px;
                font-weight: 600;
            }
            #savedActionCreatedTasksStatus[statusKind="invalid_source"], #savedActionCreatedTasksStatus[statusKind="invalid_saved_actions"], #savedActionCreatedTasksStatus[statusKind="missing"] {
                color: rgba(255, 189, 176, 0.96);
            }
            #savedActionCreatedTasksSource {
                color: rgba(126, 157, 171, 0.78);
                font-size: 11px;
            }
            #savedActionCreatedTasksGuidance {
                color: rgba(110, 201, 164, 0.86);
                font-size: 11px;
                line-height: 1.4em;
            }
            #savedActionCreatedTasksItemsScroll {
                border: none;
                background: transparent;
            }
            #savedActionCreatedTasksViewport {
                border-radius: 18px;
                background: rgba(8, 20, 34, 0.96);
            }
            #savedActionCreatedTasksItems {
                background: transparent;
            }
            QFrame[inventoryRole="itemFrame"] {
                border-radius: 16px;
                border: 1px solid rgba(118, 226, 255, 0.12);
                background: rgba(7, 20, 34, 0.96);
            }
            QFrame[inventoryRole="actionShell"] {
                border-radius: 14px;
                border: 1px solid rgba(118, 226, 255, 0.10);
                background: rgba(10, 25, 39, 0.86);
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
                min-height: 34px;
                padding: 0 14px;
                border-radius: 11px;
                border: 1px solid rgba(118, 226, 255, 0.18);
                background: rgba(8, 24, 38, 220);
                color: rgba(191, 212, 207, 0.96);
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton[inventoryRole="editButton"], QPushButton[inventoryRole="deleteButton"] {
                min-width: 92px;
            }
            QPushButton[inventoryRole="editButton"] {
                border: 1px solid rgba(118, 226, 255, 0.30);
                background: rgba(18, 52, 78, 214);
            }
            QPushButton[inventoryRole="deleteButton"] {
                border: 1px solid rgba(255, 138, 138, 0.26);
                background: rgba(34, 12, 16, 212);
                color: rgba(255, 231, 231, 0.96);
            }
            QPushButton[inventoryRole="editButton"]:hover, QPushButton[inventoryRole="deleteButton"]:hover, #savedActionCreatedTasksClose:hover {
                border: 1px solid rgba(118, 226, 255, 0.36);
            }
            QPushButton[inventoryRole="deleteButton"]:hover {
                border: 1px solid rgba(255, 166, 166, 0.42);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar:vertical {
                width: 10px;
                margin: 6px 2px 6px 0;
                border-radius: 5px;
                background: rgba(10, 24, 38, 0.74);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::handle:vertical {
                min-height: 42px;
                border-radius: 5px;
                background: rgba(118, 226, 255, 0.28);
            }
            #savedActionCreatedTasksItemsScroll QScrollBar::handle:vertical:hover {
                background: rgba(118, 226, 255, 0.42);
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
        self._emit_lifecycle_event("opened")
        QTimer.singleShot(0, self._emit_ready_signal)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_chrome_overlay_geometry()

    def done(self, result):
        self._emit_lifecycle_event(
            "closed",
            result="accepted" if result == QDialog.Accepted else "rejected",
        )
        super().done(result)

    def _update_chrome_overlay_geometry(self):
        if not hasattr(self, "chrome_bar") or not hasattr(self, "shell"):
            return
        self.chrome_bar.setGeometry(6, 6, max(72, self.shell.width() - 12), self.chrome_bar.height())
        self.chrome_bar.raise_()

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
        item_count = int(inventory_payload.get("count", 0))
        self.title_label.setText(
            f"Manage Custom Tasks ({item_count})" if item_count else "Manage Custom Tasks"
        )

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
            desired_height = min(320, max(112, self.items_frame.sizeHint().height() + 2))
            self.items_scroll.setFixedHeight(desired_height)
        else:
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
    edit_saved_action_requested = Signal(str)

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setObjectName("commandOverlayWindow")
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

        self.saved_inventory_title = QLabel("Custom tasks", self.saved_inventory_frame)
        self.saved_inventory_title.setObjectName("savedActionInventoryTitle")
        saved_inventory_layout.addWidget(self.saved_inventory_title)

        self.saved_inventory_status = QLabel(
            "Create a new task or manage the tasks you already saved.",
            self.saved_inventory_frame,
        )
        self.saved_inventory_status.setObjectName("savedActionInventoryStatus")
        self.saved_inventory_status.setWordWrap(True)
        saved_inventory_layout.addWidget(self.saved_inventory_status)

        self.entry_actions_layout = QGridLayout()
        self.entry_actions_layout.setContentsMargins(0, 0, 0, 0)
        self.entry_actions_layout.setHorizontalSpacing(12)
        self.entry_actions_layout.setVerticalSpacing(0)
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

        confirm_layout.addWidget(self._make_confirm_label("Resolved action"), 1, 0)
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
            #savedActionCreateDescription, #savedActionCreatedTasksDescription {
                color: rgba(147, 174, 182, 0.87);
                font-size: 12px;
                line-height: 1.4em;
            }
            QPushButton[entryAction="true"] {
                min-height: 40px;
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
        width = max(460, min(720, int(host_geometry.width() * 0.72)))
        self.panel.setFixedWidth(width)
        self.panel.adjustSize()
        self.adjustSize()

        x = host_geometry.x() + (host_geometry.width() - self.width()) // 2
        y = host_geometry.y() + int(host_geometry.height() * 0.68)

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
                button_text += f"\n{' • '.join(metadata_bits)}"
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

        if phase == "confirm":
            self.hint_label.setText("Review the resolved action origin and destination before execution.")
        elif phase == "choose":
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
        show_inventory = phase == "entry" and bool(saved_action_inventory.get("visible"))
        self.saved_inventory_frame.setVisible(show_inventory)
        if show_inventory:
            self.create_custom_task_button.setEnabled(True)
            self.created_tasks_button.setEnabled(True)
            self.saved_inventory_title.setText("Custom tasks")
            self.saved_inventory_status.setProperty("statusKind", "idle")
            self.saved_inventory_status.style().unpolish(self.saved_inventory_status)
            self.saved_inventory_status.style().polish(self.saved_inventory_status)
            self.saved_inventory_status.setText("Create a new task or manage the tasks you already saved.")
        else:
            self.saved_inventory_status.setText("")

        titles = payload.get("ambiguous_titles") or []
        if phase == "choose" and titles:
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
            self.confirm_request_value.setText(payload.get("typed_request", ""))
            self.confirm_title_value.setText(action.get("title", ""))
            self.confirm_origin_value.setText(action.get("origin_label", ""))
            self.confirm_kind_value.setText(action.get("target_kind", ""))
            self.confirm_target_value.setText(action.get("target_display") or action.get("target", ""))
            self.confirm_target_value.setToolTip(action.get("target", ""))


class DesktopRuntimeWindow(QWidget):

    def __init__(self, screen, visual_html_path: str, event_logger=None, runtime_log_path: str = ""):
        super().__init__()

        self.screen_ref = screen
        self.visual_html_path = os.path.abspath(visual_html_path)
        self.event_logger = event_logger
        self.runtime_log_path = os.path.abspath(runtime_log_path) if runtime_log_path else ""
        self._overlay_trace_enabled = (os.environ.get("NEXUS_OVERLAY_TRACE") or "").strip().casefold() in {
            "1",
            "true",
            "yes",
            "on",
        }
        startup_snapshot_dir = (os.environ.get("JARVIS_HARNESS_STARTUP_SNAPSHOT_DIR") or "").strip()
        self._startup_snapshot_dir = os.path.abspath(startup_snapshot_dir) if startup_snapshot_dir else ""
        self.desktop_mode = False
        self._is_shutting_down = False
        self._page_ready = False
        self._desktop_mode_requested = False
        self._pending_visual_state = None
        self._pending_voice_level = None
        self._saved_action_source_path = None
        self._saved_action_create_dialog_factory = SavedActionCreateDialog
        self._created_tasks_dialog_factory = CreatedTasksDialog
        self._saved_action_edit_dialog_factory = SavedActionEditDialog
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
        self._command_panel.edit_saved_action_requested.connect(self.handle_edit_saved_action_requested)
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
        self._last_launch_failure_action_id = ""
        self._last_launch_failure_count = 0
        self._reported_recoverable_launch_failures = set()

        # Align the standalone desktop route with the proven Boot handoff window model.
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("background-color: rgb(0, 0, 0);")

        self.setGeometry(self.compute_compact_geometry())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.webview = QWebEngineView(self)
        self.webview.setStyleSheet("background-color: rgb(0, 0, 0); border: none;")
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setFocusPolicy(Qt.NoFocus)
        self.webview.hide()

        self.webview.page().setBackgroundColor(QColor(0, 0, 0))
        self.webview.loadFinished.connect(self._on_load_finished)
        self.webview.load(QUrl.fromLocalFile(self.visual_html_path))

        root.addWidget(self.webview)

    def compute_compact_geometry(self):
        g = self.screen_ref.geometry()

        width = int(g.width() * 0.46)
        height = int(g.height() * 0.68)

        x = g.x() + (g.width() - width) // 2
        y = g.y() + int(g.height() * 0.08)

        return QRect(x, y, width, height)

    def prepare_desktop_geometry(self):
        self.setGeometry(self.compute_compact_geometry())

    def showEvent(self, event):
        super().showEvent(event)

        if not self.desktop_mode:
            self._desktop_mode_requested = True
            self._schedule_desktop_mode_enable()

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
        self._emit_runtime_signal(signal_name, **fields)

    def _create_dialog_with_optional_lifecycle(self, factory, *args, **kwargs):
        try:
            return factory(*args, **kwargs)
        except TypeError as exc:
            if "lifecycle_callback" not in str(exc):
                raise
            fallback_kwargs = dict(kwargs)
            fallback_kwargs.pop("lifecycle_callback", None)
            return factory(*args, **fallback_kwargs)

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

    def _capture_startup_snapshot(self, label: str):
        if not self._startup_snapshot_dir or self._is_shutting_down:
            return

        try:
            os.makedirs(self._startup_snapshot_dir, exist_ok=True)
            stamp = datetime.datetime.now().strftime("%H%M%S_%f")
            path = os.path.join(self._startup_snapshot_dir, f"{stamp}_{label}.png")
            if self.grab().save(path, "PNG"):
                self._log_event(f"RENDERER_MAIN|STARTUP_SNAPSHOT|label={label}|path={path}")
            else:
                self._log_event(f"RENDERER_MAIN|STARTUP_SNAPSHOT_FAILED|label={label}|reason=save_failed")
        except Exception as exc:
            self._log_event(f"RENDERER_MAIN|STARTUP_SNAPSHOT_FAILED|label={label}|reason={exc}")

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

        parent = GetParentW(hwnd)
        width = max(0, rect.right - rect.left)
        height = max(0, rect.bottom - rect.top)

        return bool(parent) and (
            rect.left == target_geometry.x()
            and rect.top == target_geometry.y()
            and width == target_geometry.width()
            and height == target_geometry.height()
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

        target_geometry = self.compute_compact_geometry()
        hwnd = int(self.winId())

        if self._native_window_matches_target(hwnd, target_geometry):
            self._log_event(
                "RENDERER_MAIN|DESKTOP_GEOMETRY_RESET_SKIPPED"
                f"|x={target_geometry.x()}|y={target_geometry.y()}"
                f"|w={target_geometry.width()}|h={target_geometry.height()}"
                "|reason=stable"
            )
            self.lower()
            return

        self.setGeometry(target_geometry)
        attached = attach_window_to_desktop(hwnd)
        if attached:
            make_window_noninteractive(hwnd)
            position_desktop_child(
                hwnd,
                target_geometry.x(),
                target_geometry.y(),
                target_geometry.width(),
                target_geometry.height(),
            )
            self._log_event(
                "RENDERER_MAIN|DESKTOP_GEOMETRY_RESET"
                f"|x={target_geometry.x()}|y={target_geometry.y()}"
                f"|w={target_geometry.width()}|h={target_geometry.height()}"
            )

        self.webview.update()
        self.update()
        self._run_javascript("window.dispatchEvent(new Event('resize'));")
        self.lower()

    def reinforce_desktop_mode(self):
        self._reinforce_desktop_mode()

    def _schedule_desktop_mode_enable(self):
        if not self._desktop_mode_requested or self.desktop_mode or self._is_shutting_down:
            return
        if not self._page_ready:
            return
        QTimer.singleShot(50, self.enable_desktop_mode)

    def _on_load_finished(self, ok):
        if not ok:
            self._log_event("RENDERER_MAIN|VISUAL_PAGE_LOAD_FAILED")
            return

        self._page_ready = True
        self._log_event("RENDERER_MAIN|VISUAL_PAGE_READY")
        self._apply_pending_visual_state()
        self._apply_pending_voice_level()
        self._apply_command_overlay_state()
        self._schedule_desktop_mode_enable()

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

    def _resume_overlay_capture_after_authoring_dialog(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return

        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = False
        self._command_panel.input_line.set_local_typing_enabled(False)
        self._refresh_overlay_input_capture(seconds=5.0)
        self._apply_command_overlay_state()
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

    def handle_create_custom_task_requested(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
            return

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

        dialog = self._create_dialog_with_optional_lifecycle(
            self._saved_action_create_dialog_factory,
            self._command_panel,
            self._handle_saved_action_create_draft_submit,
            lifecycle_callback=self._handle_dialog_lifecycle_signal,
        )
        try:
            dialog.exec()
        finally:
            self._resume_overlay_capture_after_authoring_dialog()

    def handle_created_tasks_requested(self):
        if not self._command_model.visible or self._command_model.phase != "entry":
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
            dialog.exec()
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

    def handle_edit_saved_action_requested(self, saved_action_id: str):
        if not self._command_model.visible or self._command_model.phase != "entry":
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
            lifecycle_callback=self._handle_dialog_lifecycle_signal,
        )
        try:
            dialog.exec()
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

    def _classify_recoverable_launch_failed_incident(self, action_id: str, failure_count: int) -> str:
        if failure_count < 2:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS2_INLINE|action_id={action_id}|count={failure_count}"
            )
            return "class2_inline"

        if action_id in self._reported_recoverable_launch_failures:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS3_ALREADY_REPORTED|action_id={action_id}|count={failure_count}"
            )
            return "class3_already_reported"

        self._log_event(
            f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS3_REPORT_SELECTED|action_id={action_id}|count={failure_count}"
        )
        return "class3_report_selected"

    def _prepare_recoverable_launch_failure_report(self, action) -> str | None:
        failure_count = self._record_launch_failure(action.id)
        incident_class = self._classify_recoverable_launch_failed_incident(action.id, failure_count)
        if incident_class == "class2_inline":
            return None
        if incident_class == "class3_already_reported":
            return None
        if not self.runtime_log_path or not os.path.isfile(self.runtime_log_path):
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_SKIPPED|action_id={action.id}|reason=runtime_log_unavailable"
            )
            return None

        crash_dir = os.path.join(os.path.dirname(self.runtime_log_path), "crash")
        self._log_event(
            f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_BEGIN|action_id={action.id}|count={failure_count}"
        )
        try:
            report_prep = prepare_manual_issue_report(ROOT_DIR, self.runtime_log_path, crash_dir)
        except SupportBundleError as exc:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_FAILED|action_id={action.id}|reason={exc}"
            )
            return None
        except Exception as exc:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_FAILED|action_id={action.id}|reason={exc}"
            )
            return None

        bundle_info = report_prep["bundle_info"]
        issue_url = report_prep["issue_url"]
        browser_opened = False

        try:
            os.startfile(os.path.dirname(bundle_info["bundle_path"]))
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_FOLDER_OPENED|action_id={action.id}|bundle={bundle_info['bundle_name']}"
            )
        except Exception as exc:
            self._log_event(
                f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_FOLDER_FAILED|action_id={action.id}|reason={exc}"
            )

        if issue_url:
            try:
                browser_opened = webbrowser.open(issue_url, new=2)
            except Exception as exc:
                self._log_event(
                    f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_ISSUE_FAILED|action_id={action.id}|reason={exc}"
                )

        self._reported_recoverable_launch_failures.add(action.id)
        self._log_event(
            f"RENDERER_MAIN|COMMAND_LAUNCH_FAILED_RECOVERABLE_REPORT_READY|action_id={action.id}|bundle={bundle_info['bundle_name']}"
        )

        if browser_opened:
            return "Launch failed again. Support bundle prepared and issue draft opened; attach the bundle manually."
        if issue_url:
            return "Launch failed again. Support bundle prepared; open the issue page manually and attach the bundle."
        return "Launch failed again. Support bundle prepared; review it locally before filing the report."

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

        action = payload
        self._log_event(f"RENDERER_MAIN|COMMAND_EXECUTION_REQUESTED|action_id={action.id}")
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
        if self.desktop_mode:
            msg = ctypes.wintypes.MSG.from_address(int(message))

            if msg.message == WM_NCHITTEST:
                return True, HTTRANSPARENT

        return super().nativeEvent(eventType, message)

    def enable_desktop_mode(self):
        if self.desktop_mode or self._is_shutting_down or not self._page_ready:
            return

        self._log_event("RENDERER_MAIN|DESKTOP_MODE_ENABLE_BEGIN")
        self.desktop_mode = True
        self._desktop_mode_requested = False
        target_geometry = self.compute_compact_geometry()

        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setGeometry(target_geometry)

        self.hide()
        hwnd = int(self.winId())
        self.show()
        self._log_native_window_state("after_show_before_attach", hwnd)
        ShowWindowW(hwnd, SW_HIDE)
        self._log_native_window_state("after_native_hide_before_attach", hwnd)
        self.setGeometry(target_geometry)

        attached = attach_window_to_desktop(hwnd)
        self._log_native_window_state("after_attach", hwnd)
        if attached:
            ShowWindowW(hwnd, SW_HIDE)
            self._log_native_window_state("after_hide_post_attach", hwnd)
            make_window_noninteractive(hwnd)
            self._log_native_window_state("after_make_noninteractive", hwnd)
            ShowWindowW(hwnd, SW_HIDE)
            self._log_native_window_state("after_hide_post_noninteractive", hwnd)
            position_desktop_child(
                hwnd,
                target_geometry.x(),
                target_geometry.y(),
                target_geometry.width(),
                target_geometry.height(),
            )
            self._log_native_window_state("after_position_child", hwnd)
        else:
            self._log_event("RENDERER_MAIN|DESKTOP_ATTACH_FALLBACK_VISIBLE_MODE")

        if not self.webview.isVisible():
            self.webview.show()
            self._log_event("RENDERER_MAIN|WEBVIEW_REVEALED_AFTER_ATTACH")
            QTimer.singleShot(50, lambda: self._capture_startup_snapshot("after_attach_reveal"))
            QTimer.singleShot(300, lambda: self._capture_startup_snapshot("after_300ms"))
            QTimer.singleShot(600, lambda: self._capture_startup_snapshot("after_600ms"))
            QTimer.singleShot(1000, lambda: self._capture_startup_snapshot("after_1000ms"))
            QTimer.singleShot(1600, lambda: self._capture_startup_snapshot("after_1600ms"))
            QTimer.singleShot(2200, lambda: self._capture_startup_snapshot("after_2200ms"))

        self._log_event(
            f"RENDERER_MAIN|DESKTOP_ATTACH_RESULT|success={'true' if attached else 'false'}"
        )
        for probe_event in get_last_workerw_probe_events():
            self._log_event(f"RENDERER_MAIN|{probe_event}")

        self.webview.update()
        self.update()
        self._run_javascript("window.dispatchEvent(new Event('resize'));")
        self.lower()
        if attached:
            QTimer.singleShot(260, self._reinforce_desktop_mode)
            QTimer.singleShot(900, self._reinforce_desktop_mode)

    def request_shutdown(self):
        if self._is_shutting_down:
            return

        self._log_event("RENDERER_MAIN|RENDERER_SHUTDOWN_BEGIN")
        self._is_shutting_down = True
        self._result_close_timer.stop()

        self._command_panel.hide()
        self.webview.stop()
        self.hide()
        self.close()

        app = QApplication.instance()

        if app is not None:
            QTimer.singleShot(0, app.quit)
