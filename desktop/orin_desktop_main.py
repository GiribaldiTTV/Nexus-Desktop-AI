import os
import sys
import datetime
import threading
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtGui import QAction
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon

from desktop.desktop_renderer import DesktopRuntimeWindow
from desktop.hotkeys import ShutdownBus, GlobalHotkeyManager
from desktop.single_instance import NamedSignal

RUNTIME_LOG_FILE = ""
STARTUP_ABORT_SIGNAL_FILE = ""
RUNTIME_RELAUNCH_EVENT = r"Local\JarvisRuntimeRelaunchRequestV1"
TRAY_IDENTITY_LABEL = "Nexus Desktop AI"
TRAY_DISCOVERY_MESSAGE = (
    "Nexus Desktop AI is running in the Windows notification area. "
    "If you do not see the icon, open hidden icons (^)."
)
TRAY_DISCOVERY_DURATION_MS = 4500
AUTHORITATIVE_DESKTOP_SETTLED_MARKER = "DESKTOP_OUTCOME|SETTLED|state=dormant"


def parse_runtime_log_arg(argv):
    global RUNTIME_LOG_FILE
    for i, arg in enumerate(argv):
        if arg == "--runtime-log" and i + 1 < len(argv):
            RUNTIME_LOG_FILE = argv[i + 1]
            return


def parse_startup_abort_signal_arg(argv):
    global STARTUP_ABORT_SIGNAL_FILE
    for i, arg in enumerate(argv):
        if arg == "--startup-abort-signal" and i + 1 < len(argv):
            STARTUP_ABORT_SIGNAL_FILE = argv[i + 1]
            return


def runtime_milestone(event):
    if not RUNTIME_LOG_FILE:
        return
    try:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        with open(RUNTIME_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {event}\n")
    except Exception:
        pass


def overlay_trace_enabled():
    value = (os.environ.get("NEXUS_OVERLAY_TRACE") or "").strip().casefold()
    return value in {"1", "true", "yes", "on"}


def harness_relaunch_shutdown_delay_seconds():
    value = (os.environ.get("JARVIS_HARNESS_RELAUNCH_SHUTDOWN_DELAY_SECONDS") or "").strip()
    if not value:
        return 0.0
    try:
        return max(0.0, float(value))
    except ValueError:
        return 0.0


class DesktopTrayEntry:
    def __init__(self, app, window, event_logger=None):
        self.app = app
        self.window = window
        self.event_logger = event_logger or (lambda _event: None)
        self.tray_icon = None
        self.tray_menu = None
        self.identity_action = None
        self.open_overlay_action = None
        self.create_custom_task_action = None
        self._discovery_cue_shown = False

    def _emit(self, event):
        try:
            self.event_logger(event)
        except Exception:
            pass

    def initialize(self):
        self._emit("RENDERER_MAIN|TRAY_ENTRY_INITIALIZE_REQUESTED")
        try:
            tray_available = QSystemTrayIcon.isSystemTrayAvailable()

            if not tray_available:
                self._emit("RENDERER_MAIN|TRAY_ENTRY_READY|available=false")
                return False

            icon = self.app.windowIcon()
            if icon.isNull():
                icon = self.app.style().standardIcon(QStyle.SP_ComputerIcon)

            self.tray_menu = QMenu(TRAY_IDENTITY_LABEL)
            self.tray_menu.setTitle(TRAY_IDENTITY_LABEL)
            self.identity_action = QAction(TRAY_IDENTITY_LABEL, self.tray_menu)
            self.identity_action.setEnabled(False)
            self.tray_menu.addAction(self.identity_action)
            self.tray_menu.addSeparator()
            self.open_overlay_action = QAction("Open Command Overlay", self.tray_menu)
            self.open_overlay_action.triggered.connect(
                lambda _checked=False: self.request_overlay_from_tray("menu")
            )
            self.tray_menu.addAction(self.open_overlay_action)
            self.create_custom_task_action = QAction("Create Custom Task", self.tray_menu)
            self.create_custom_task_action.triggered.connect(
                lambda _checked=False: self.request_create_custom_task_from_tray("menu")
            )
            self.tray_menu.addAction(self.create_custom_task_action)

            self.tray_icon = QSystemTrayIcon(icon, self.app)
            self.tray_icon.setToolTip(TRAY_IDENTITY_LABEL)
            self.tray_icon.setContextMenu(self.tray_menu)
            self.tray_icon.activated.connect(self._handle_activation)
            self.tray_icon.show()
            self._emit("RENDERER_MAIN|TRAY_ENTRY_READY|available=true")
            self._emit(
                f"RENDERER_MAIN|TRAY_IDENTITY_READY|label={TRAY_IDENTITY_LABEL}|hidden_overflow_hint=true"
            )
            self._emit("RENDERER_MAIN|TRAY_ICON_SHOWN")
            return True
        except Exception as exc:
            self.close()
            self._emit(
                f"RENDERER_MAIN|TRAY_ENTRY_READY|available=false|reason={type(exc).__name__}"
            )
            return False

    def _handle_activation(self, reason):
        reason_name = getattr(reason, "name", str(reason))
        trigger_reason = QSystemTrayIcon.ActivationReason.Trigger
        double_click_reason = QSystemTrayIcon.ActivationReason.DoubleClick
        if reason in (trigger_reason, double_click_reason):
            self.request_overlay_from_tray(f"activation_{reason_name}")
            return

        self._emit(f"RENDERER_MAIN|TRAY_ACTIVATION_IGNORED|reason={reason_name}")

    def request_overlay_from_tray(self, source):
        self._emit(f"RENDERER_MAIN|TRAY_ACTIVATION_REQUESTED|source={source}")
        self.window.toggle_command_overlay()
        self._emit(f"RENDERER_MAIN|TRAY_ACTIVATION_ROUTED_TO_OVERLAY|source={source}")

    def request_create_custom_task_from_tray(self, source):
        self._emit(f"RENDERER_MAIN|TRAY_CREATE_CUSTOM_TASK_REQUESTED|source={source}")
        self.window.request_create_custom_task_from_tray(source=source)

    def show_discovery_cue(self):
        if self.tray_icon is None:
            self._emit("RENDERER_MAIN|TRAY_DISCOVERY_CUE_SKIPPED|reason=tray_unavailable")
            return False

        if self._discovery_cue_shown:
            self._emit("RENDERER_MAIN|TRAY_DISCOVERY_CUE_SKIPPED|reason=already_shown")
            return False

        self._discovery_cue_shown = True
        try:
            supports_messages = QSystemTrayIcon.supportsMessages()
        except Exception:
            supports_messages = True

        if not supports_messages:
            self._emit("RENDERER_MAIN|TRAY_DISCOVERY_CUE_SKIPPED|reason=messages_unavailable")
            return False

        try:
            message_icon = getattr(getattr(QSystemTrayIcon, "MessageIcon", object), "Information", None)
            if message_icon is None:
                message_icon = getattr(QSystemTrayIcon, "Information", 1)
            self.tray_icon.showMessage(
                TRAY_IDENTITY_LABEL,
                TRAY_DISCOVERY_MESSAGE,
                message_icon,
                TRAY_DISCOVERY_DURATION_MS,
            )
            self._emit("RENDERER_MAIN|TRAY_DISCOVERY_CUE_REQUESTED|hidden_overflow_hint=true")
            return True
        except Exception as exc:
            self._emit(
                f"RENDERER_MAIN|TRAY_DISCOVERY_CUE_FAILED|reason={type(exc).__name__}"
            )
            return False

    def close(self):
        if self.tray_icon is None:
            return

        try:
            self.tray_icon.hide()
            self._emit("RENDERER_MAIN|TRAY_ICON_HIDDEN")
        except Exception as exc:
            self._emit(f"RENDERER_MAIN|TRAY_ICON_HIDE_FAILED|reason={type(exc).__name__}")
        finally:
            self.tray_icon = None


def startup_abort_requested():
    return bool(STARTUP_ABORT_SIGNAL_FILE) and os.path.exists(STARTUP_ABORT_SIGNAL_FILE)


def exit_if_startup_abort_requested(hotkeys=None, tray_entry=None):
    if not startup_abort_requested():
        return False

    runtime_milestone("RENDERER_MAIN|STARTUP_ABORTED")

    if tray_entry is not None:
        try:
            tray_entry.close()
        except Exception:
            pass

    if hotkeys is not None:
        try:
            hotkeys.stop()
        except Exception:
            pass

    return True


def main():
    parse_runtime_log_arg(sys.argv)
    parse_startup_abort_signal_arg(sys.argv)
    runtime_milestone("RENDERER_MAIN|START")
    if exit_if_startup_abort_requested():
        return 0

    app = QApplication(sys.argv)
    app.setApplicationName(TRAY_IDENTITY_LABEL)
    try:
        app.setApplicationDisplayName(TRAY_IDENTITY_LABEL)
    except Exception:
        pass
    runtime_milestone("RENDERER_MAIN|QAPPLICATION_CREATED")
    if exit_if_startup_abort_requested():
        return 0

    visual_html_path = os.path.join(ROOT_DIR, "jarvis_visual", "orin_core.html")
    runtime_milestone("RENDERER_MAIN|VISUAL_HTML_RESOLVED")
    if exit_if_startup_abort_requested():
        return 0

    screen = app.primaryScreen()
    window = DesktopRuntimeWindow(
        screen,
        visual_html_path,
        event_logger=runtime_milestone,
        runtime_log_path=RUNTIME_LOG_FILE,
    )
    runtime_milestone("RENDERER_MAIN|WINDOW_CONSTRUCTED")
    if exit_if_startup_abort_requested():
        return 0

    bus = ShutdownBus()
    runtime_milestone("RENDERER_MAIN|SHUTDOWN_BUS_READY")
    hotkeys = GlobalHotkeyManager(bus)
    relaunch_signal = NamedSignal(RUNTIME_RELAUNCH_EVENT)
    shutdown_started = False
    shutdown_force_kill_timer = None
    if exit_if_startup_abort_requested():
        return 0

    def do_shutdown():
        nonlocal shutdown_started, shutdown_force_kill_timer
        if shutdown_started:
            return
        shutdown_started = True
        runtime_milestone("RENDERER_MAIN|SHUTDOWN_REQUESTED")
        tray_entry.close()
        hotkeys.stop()
        window.request_shutdown()
        shutdown_force_kill_timer = threading.Timer(1.2, hotkeys.force_kill)
        shutdown_force_kill_timer.daemon = True
        shutdown_force_kill_timer.start()

    def poll_relaunch_request():
        if relaunch_signal.consume():
            runtime_milestone("RENDERER_MAIN|RELAUNCH_REQUEST_RECEIVED")
            delay_seconds = harness_relaunch_shutdown_delay_seconds()
            if delay_seconds > 0:
                runtime_milestone(
                    f"RENDERER_MAIN|HARNESS_RELAUNCH_SHUTDOWN_DELAY|seconds={delay_seconds:g}"
                )
                time.sleep(delay_seconds)
            do_shutdown()

    bus.shutdown_requested.connect(do_shutdown)
    bus.command_overlay_toggle_requested.connect(window.toggle_command_overlay)
    bus.command_overlay_text_requested.connect(window.handle_overlay_text_requested)
    bus.command_overlay_backspace_requested.connect(window.handle_overlay_backspace_requested)
    bus.command_overlay_submit_requested.connect(window.handle_overlay_submit_requested)
    bus.command_overlay_escape_requested.connect(window.handle_overlay_escape_requested)
    bus.command_overlay_global_click_requested.connect(window.handle_overlay_global_click_requested)
    tray_entry = DesktopTrayEntry(app, window, runtime_milestone)
    tray_entry.initialize()
    hotkeys.set_overlay_input_enabled_provider(window.overlay_needs_global_input_capture)
    hotkeys.set_overlay_launch_grace_allowed_provider(window.overlay_allows_launch_grace)
    hotkeys.set_overlay_click_monitor_provider(window.overlay_monitors_global_clicks)
    if overlay_trace_enabled():
        hotkeys.set_debug_logger(runtime_milestone)
    hotkeys.start()
    runtime_milestone("RENDERER_MAIN|HOTKEYS_STARTED")
    if exit_if_startup_abort_requested(hotkeys, tray_entry):
        return 0

    print("Nexus Desktop AI Desktop Runtime - Version 1.02")
    print("Command Overlay: Ctrl + Alt + Home or Ctrl + Alt + 1")
    print("Hotkey: Ctrl + Alt + End or Ctrl + Alt + 2")

    def settle_passive_default_handoff():
        if exit_if_startup_abort_requested(hotkeys, tray_entry):
            app.quit()
            return
        window.set_visual_state("dormant")
        runtime_milestone("RENDERER_MAIN|PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant")
        runtime_milestone(AUTHORITATIVE_DESKTOP_SETTLED_MARKER)

    startup_ready_marked = False

    def mark_startup_ready():
        nonlocal startup_ready_marked
        if startup_ready_marked:
            return
        if exit_if_startup_abort_requested(hotkeys, tray_entry):
            app.quit()
            return
        startup_ready_marked = True
        runtime_milestone("RENDERER_MAIN|STARTUP_READY")
        tray_entry.show_discovery_cue()
        settle_passive_default_handoff()

    window_show_requested = False

    def show_window_after_core_visualization_ready():
        nonlocal window_show_requested
        if window_show_requested:
            return
        if exit_if_startup_abort_requested(hotkeys, tray_entry):
            app.quit()
            return
        window_show_requested = True
        window.show()
        runtime_milestone("RENDERER_MAIN|WINDOW_SHOW_REQUESTED|reason=core_visualization_ready")

    window.core_visualization_ready.connect(show_window_after_core_visualization_ready)
    window.core_visualization_visible.connect(mark_startup_ready)
    runtime_milestone("RENDERER_MAIN|WINDOW_SHOW_DEFERRED_UNTIL_CORE_READY")
    if window.is_core_visualization_ready():
        QTimer.singleShot(0, show_window_after_core_visualization_ready)

    relaunch_timer = QTimer()
    relaunch_timer.timeout.connect(poll_relaunch_request)
    relaunch_timer.start(200)

    exit_code = app.exec()
    relaunch_timer.stop()
    relaunch_signal.close()
    tray_entry.close()
    hotkeys.stop()
    runtime_milestone(f"RENDERER_MAIN|EVENT_LOOP_EXIT|code={exit_code}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
