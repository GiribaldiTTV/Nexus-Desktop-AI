import os
import ctypes
import json

from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QTimer, QUrl, QRect, Signal
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView

from .interaction_overlay_model import CommandOverlayModel, launch_command_action
from .workerw_utils import (
    attach_window_to_desktop,
    get_last_workerw_probe_events,
    make_window_noninteractive,
)

WM_NCHITTEST = 0x0084
HTTRANSPARENT = -1


class DesktopJarvisWindow(QWidget):
    command_mode_changed = Signal(bool)

    def __init__(self, screen, visual_html_path: str, event_logger=None):
        super().__init__()

        self.screen_ref = screen
        self.visual_html_path = os.path.abspath(visual_html_path)
        self.event_logger = event_logger

        self.desktop_mode = False
        self._is_shutting_down = False
        self._page_ready = False
        self._pending_visual_state = None
        self._pending_voice_level = None
        self._command_model = CommandOverlayModel()
        self._result_close_timer = QTimer(self)
        self._result_close_timer.setSingleShot(True)
        self._result_close_timer.timeout.connect(self._close_command_overlay_after_result)

        # Window configuration (Concept 2 test)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("background: transparent;")

        self.setGeometry(self.compute_compact_geometry())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.webview = QWebEngineView(self)
        self.webview.setAttribute(Qt.WA_TranslucentBackground, True)
        self.webview.setStyleSheet("background: transparent; border: none;")
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setFocusPolicy(Qt.NoFocus)

        self.webview.page().setBackgroundColor(QColor(0, 0, 0, 0))
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

    def showEvent(self, event):
        super().showEvent(event)

        if not self.desktop_mode:
            QTimer.singleShot(50, self.enable_desktop_mode)

    def _log_event(self, event):
        if callable(self.event_logger):
            try:
                self.event_logger(event)
            except Exception:
                pass

    def _run_javascript(self, script):
        page = self.webview.page()
        if page is not None:
            page.runJavaScript(script)

    def _apply_pending_visual_state(self):
        if not self._page_ready or self._pending_visual_state is None:
            return

        state_name = self._pending_visual_state
        js = f"window.setJarvisState && window.setJarvisState('{state_name}');"
        self._run_javascript(js)
        self._log_event(f"RENDERER_MAIN|VISUAL_STATE_APPLIED|state={state_name}")
        self._pending_visual_state = None

    def _apply_pending_voice_level(self):
        if not self._page_ready or self._pending_voice_level is None:
            return

        level = self._pending_voice_level
        js = f"window.setJarvisVoiceLevel && window.setJarvisVoiceLevel({level:.4f});"
        self._run_javascript(js)
        self._pending_voice_level = None

    def _apply_command_overlay_state(self):
        if not self._page_ready:
            return

        payload = json.dumps(self._command_model.view_payload())
        self._run_javascript(
            f"window.setCommandOverlayState && window.setCommandOverlayState({payload});"
        )

    def _on_load_finished(self, ok):
        if not ok:
            self._log_event("RENDERER_MAIN|VISUAL_PAGE_LOAD_FAILED")
            return

        self._page_ready = True
        self._log_event("RENDERER_MAIN|VISUAL_PAGE_READY")
        self._apply_pending_visual_state()
        self._apply_pending_voice_level()
        self._apply_command_overlay_state()

    def set_visual_state(self, state_name):
        self._pending_visual_state = state_name

        if self._page_ready:
            self._apply_pending_visual_state()

    def set_voice_level(self, level):
        self._pending_voice_level = max(0.0, min(1.0, float(level)))

        if self._page_ready:
            self._apply_pending_voice_level()

    def _set_command_mode_active(self, active: bool):
        self.command_mode_changed.emit(bool(active))

    def open_command_overlay(self):
        if self._is_shutting_down:
            return

        self._result_close_timer.stop()
        self._command_model.open()
        self._apply_command_overlay_state()
        self._set_command_mode_active(True)
        self._log_event("RENDERER_MAIN|COMMAND_OVERLAY_OPENED")

    def close_command_overlay(self):
        if not self._command_model.visible:
            return

        self._result_close_timer.stop()
        self._command_model.close()
        self._apply_command_overlay_state()
        self._set_command_mode_active(False)
        self._log_event("RENDERER_MAIN|COMMAND_OVERLAY_CLOSED")

    def toggle_command_overlay(self):
        if self._command_model.visible:
            self.close_command_overlay()
        else:
            self.open_command_overlay()

    def handle_command_character(self, char: str):
        self._command_model.append_text(char)
        self._apply_command_overlay_state()

    def handle_command_backspace(self):
        self._command_model.backspace()
        self._apply_command_overlay_state()

    def handle_command_escape(self):
        result = self._command_model.escape()
        self._apply_command_overlay_state()

        if result == "confirm_cancelled":
            self._log_event("RENDERER_MAIN|COMMAND_CONFIRM_CANCELLED")
            return

        if result == "closed":
            self._set_command_mode_active(False)
            self._log_event("RENDERER_MAIN|COMMAND_OVERLAY_CLOSED")

    def _show_command_result(self, status_kind: str, status_text: str):
        self._command_model.show_result(status_kind, status_text)
        self._apply_command_overlay_state()
        self._set_command_mode_active(False)
        self._result_close_timer.start(1200)

    def _close_command_overlay_after_result(self):
        self.close_command_overlay()

    def handle_command_submit(self):
        result, payload = self._command_model.submit()
        self._apply_command_overlay_state()

        if result == "confirm_ready":
            self._log_event(f"RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id={payload.id}")
            return

        if result == "not_found":
            self._log_event("RENDERER_MAIN|COMMAND_NOT_FOUND")
            return

        if result == "ambiguous":
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
        if self.desktop_mode or self._is_shutting_down:
            return

        self._log_event("RENDERER_MAIN|DESKTOP_MODE_ENABLE_BEGIN")
        self.desktop_mode = True

        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.hide()
        self.show()

        hwnd = int(self.winId())

        attached = attach_window_to_desktop(hwnd)
        make_window_noninteractive(hwnd)
        self._log_event(
            f"RENDERER_MAIN|DESKTOP_ATTACH_RESULT|success={'true' if attached else 'false'}"
        )
        for probe_event in get_last_workerw_probe_events():
            self._log_event(f"RENDERER_MAIN|{probe_event}")

        self.lower()

    def request_shutdown(self):
        if self._is_shutting_down:
            return

        self._log_event("RENDERER_MAIN|RENDERER_SHUTDOWN_BEGIN")
        self._is_shutting_down = True
        self._result_close_timer.stop()

        self.webview.stop()
        self.hide()
        self.close()

        app = QApplication.instance()

        if app is not None:
            QTimer.singleShot(0, app.quit)
