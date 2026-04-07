import os
import ctypes
import datetime
import time

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QFrame,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
)
from PySide6.QtCore import Qt, QTimer, QUrl, QRect, Signal
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView

from .interaction_overlay_model import CommandOverlayModel, launch_command_action
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
        self.setPlaceholderText("Type a saved action or alias")
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


class CommandOverlayPanel(QWidget):
    submit_requested = Signal()
    escape_requested = Signal()
    input_text_changed = Signal(str)
    input_armed_changed = Signal(bool)
    input_focus_acquired = Signal()
    input_focus_lost = Signal()
    ambiguous_match_selected = Signal(int)

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

        confirm_layout.addWidget(self._make_confirm_label("Target kind"), 2, 0)
        self.confirm_kind_value = self._make_confirm_value()
        confirm_layout.addWidget(self.confirm_kind_value, 2, 1)

        confirm_layout.addWidget(self._make_confirm_label("Target"), 3, 0)
        self.confirm_target_value = self._make_confirm_value()
        confirm_layout.addWidget(self.confirm_target_value, 3, 1)

        self.confirm_help_label = QLabel(
            "Press Enter to confirm or Esc to return.",
            self.confirmation_frame,
        )
        self.confirm_help_label.setObjectName("commandConfirmHelp")
        self.confirm_help_label.setWordWrap(True)
        confirm_layout.addWidget(self.confirm_help_label, 4, 0, 1, 2)

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
                color: rgba(118, 226, 255, 0.72);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.24em;
            }
            #commandTitle {
                margin-top: 8px;
                color: rgba(238, 250, 255, 0.96);
                font-size: 28px;
                font-weight: 600;
            }
            #commandHint {
                margin-top: 10px;
                color: rgba(172, 215, 235, 0.82);
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
                color: rgba(118, 226, 255, 0.84);
                font-size: 22px;
                font-weight: 600;
            }
            #commandInputLine {
                border: none;
                background: transparent;
                color: rgba(238, 248, 255, 0.96);
                font-size: 21px;
                selection-background-color: rgba(118, 226, 255, 0.28);
            }
            #commandInputLine:read-only {
                color: rgba(170, 194, 208, 0.92);
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
                color: rgba(174, 215, 232, 0.88);
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
                color: rgba(118, 226, 255, 0.66);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.12em;
            }
            QLabel[confirmRole="value"] {
                color: rgba(236, 247, 255, 0.94);
                font-size: 15px;
            }
            #commandConfirmHelp {
                margin-top: 14px;
                color: rgba(172, 215, 235, 0.84);
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

    def show_for_geometry(self, host_geometry: QRect, bounds_geometry: QRect | None = None):
        width = max(460, min(720, int(host_geometry.width() * 0.72)))
        self.panel.setFixedWidth(width)
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
        self.show()
        self.raise_()

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
            target_kind = match.get("target_kind", "")
            target_display = match.get("target_display") or match.get("target", "")
            button_text = f"{index + 1}. {title}"
            if target_display:
                button_text += f"\n{target_kind}: {target_display}"
            elif target_kind:
                button_text += f"\n{target_kind}"
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
            self.hint_label.setText("Review the resolved action before execution.")
        elif phase == "choose":
            self.hint_label.setText("Press a number key or click the intended saved action, then confirm it before launch.")
        elif phase == "result":
            self.hint_label.setText("Returning to passive desktop mode.")
        else:
            self.hint_label.setText(
                "Type a saved action or alias, then press Enter."
                if not armed
                else "Type a saved action or alias, then press Enter."
            )

        status_kind = payload.get("status_kind", "idle")
        self.status_label.setProperty("statusKind", status_kind)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        if payload.get("status_text"):
            self.status_label.setText(payload["status_text"])
        elif phase == "entry" and not armed:
            self.status_label.setText("Type a saved action or alias to begin.")
        else:
            self.status_label.setText("")

        titles = payload.get("ambiguous_titles") or []
        if phase == "choose" and titles:
            self.ambiguous_label.setText(
                "Multiple saved actions matched your request. Press a number key or click a choice after reviewing the destination detail below."
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
            self.confirm_kind_value.setText(action.get("target_kind", ""))
            self.confirm_target_value.setText(action.get("target_display") or action.get("target", ""))
            self.confirm_target_value.setToolTip(action.get("target", ""))


class DesktopRuntimeWindow(QWidget):

    def __init__(self, screen, visual_html_path: str, event_logger=None):
        super().__init__()

        self.screen_ref = screen
        self.visual_html_path = os.path.abspath(visual_html_path)
        self.event_logger = event_logger
        self._overlay_trace_enabled = (os.environ.get("NEXUS_OVERLAY_TRACE") or "").strip().casefold() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self._startup_snapshot_dir = (os.environ.get("JARVIS_HARNESS_STARTUP_SNAPSHOT_DIR") or "").strip()
        self.desktop_mode = False
        self._is_shutting_down = False
        self._page_ready = False
        self._desktop_mode_requested = False
        self._pending_visual_state = None
        self._pending_voice_level = None
        self._command_model = CommandOverlayModel()
        self._command_panel = CommandOverlayPanel()
        self._command_panel.submit_requested.connect(self.handle_local_submit_requested)
        self._command_panel.escape_requested.connect(self.handle_command_escape)
        self._command_panel.input_text_changed.connect(self.handle_command_text_changed)
        self._command_panel.input_armed_changed.connect(self.handle_command_input_armed_changed)
        self._command_panel.input_focus_acquired.connect(self.handle_command_input_focus_acquired)
        self._command_panel.input_focus_lost.connect(self.handle_command_input_focus_lost)
        self._command_panel.ambiguous_match_selected.connect(self.handle_ambiguous_match_selected)
        self._result_close_timer = QTimer(self)
        self._result_close_timer.setSingleShot(True)
        self._result_close_timer.timeout.connect(self._close_command_overlay_after_result)
        self._overlay_input_capture_until = 0.0
        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = False

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
        self._log_event("RENDERER_MAIN|COMMAND_OVERLAY_OPENED")

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
        self._clear_overlay_input_capture()
        self._overlay_local_input_engaged = False
        self._overlay_global_capture_suspended = False
        self._command_panel.hide()
        self._command_model.close()
        self._apply_command_overlay_state()
        self._trace_overlay("overlay_closed")
        self._log_event("RENDERER_MAIN|COMMAND_OVERLAY_CLOSED")

    def toggle_command_overlay(self):
        if self._command_model.visible:
            self.close_command_overlay()
        else:
            self.open_command_overlay()

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
                return

            self._command_panel.input_line.set_local_typing_enabled(False)
            self._overlay_local_input_engaged = False
            self._refresh_overlay_input_capture()
            self._trace_overlay(
                "input_focus_acquired",
                manual_focus="true" if manual_focus else "false",
                mode="fallback",
            )

    def handle_command_input_focus_lost(self):
        if not self._command_model.visible:
            return
        self._trace_overlay("input_focus_lost")

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
                self._arm_overlay_input_capture()
            self._log_event("RENDERER_MAIN|COMMAND_DISAMBIGUATION_CANCELLED")
            return

        if result == "confirm_cancelled":
            if self._overlay_local_input_engaged:
                self._command_panel.focus_input()
            else:
                self._arm_overlay_input_capture()
            self._log_event("RENDERER_MAIN|COMMAND_CONFIRM_CANCELLED")
            return

        if result == "closed":
            self._command_panel.hide()
            self._log_event("RENDERER_MAIN|COMMAND_OVERLAY_CLOSED")

    def _show_command_result(self, status_kind: str, status_text: str):
        self._command_model.show_result(status_kind, status_text)
        self._apply_command_overlay_state()
        self._result_close_timer.start(1200)

    def _close_command_overlay_after_result(self):
        self.close_command_overlay()

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
            self._show_command_result("launch_failed", f"Launch failed: {exc}")
            return

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
