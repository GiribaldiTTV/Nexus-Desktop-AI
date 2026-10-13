import os
import sys
import ctypes
import datetime
import threading

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtGui import QCursor
from PySide6.QtCore import QObject, QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from desktop.core_visualization_renderer import CoreVisualizationWindow
from desktop.hotkeys import ShutdownBus, GlobalHotkeyManager
from desktop.monitoring_hud_state import load_monitoring_hud_state
from desktop.resident_access import build_resident_access_menu_plan
from desktop.single_instance import NamedSignal
from desktop.tray_controller import DesktopTrayEntry, TRAY_IDENTITY_LABEL, build_resident_tray_icon

try:
    from desktop.desktop_renderer import DesktopRuntimeWindow
    DESKTOP_RUNTIME_IMPORT_ERROR = None
except Exception as exc:
    DesktopRuntimeWindow = None
    DESKTOP_RUNTIME_IMPORT_ERROR = exc

RUNTIME_LOG_FILE = ""
STARTUP_ABORT_SIGNAL_FILE = ""
RUNTIME_RELAUNCH_EVENT = r"Local\NexusRuntimeRelaunchRequestV1"
RUNTIME_DESKTOP_SETTLED_EVENT = r"Local\NexusRuntimeDesktopSettledV1"
AUTHORITATIVE_DESKTOP_SETTLED_MARKER = "DESKTOP_OUTCOME|SETTLED|state=dormant"
MONITORING_HUD_STARTUP_ENV = "NEXUS_MONITORING_HUD_STARTUP_ENABLED"
SHUTDOWN_CONFIRMATION_ACCEPTED = "accepted"
SHUTDOWN_CONFIRMATION_CANCELLED = "cancelled"
SHUTDOWN_CONFIRMATION_TIMEOUT = "timeout"
SHUTDOWN_CONFIRMATION_DEFAULT_TIMEOUT_MS = 15000


class ShutdownConfirmationDispatcher(QObject):
    def __init__(self, handler, parent=None):
        super().__init__(parent)
        self._handler = handler

    @Slot(str)
    def request(self, source="hotkey"):
        self._handler(source)


class DesktopRuntimeUnavailable(QObject):
    core_visualization_visible = Signal()

    def __init__(self, event_logger=None, reason="desktop runtime unavailable"):
        super().__init__()
        self.event_logger = event_logger or (lambda _event: None)
        self.reason = str(reason or "desktop runtime unavailable")
        self._emit("RENDERER_MAIN|DESKTOP_RUNTIME_UNAVAILABLE|reason=" + self.reason.replace("|", "/"))

    def _emit(self, event):
        try:
            self.event_logger(event)
        except Exception:
            pass

    def show(self):
        self._emit("RENDERER_MAIN|DESKTOP_RUNTIME_FALLBACK_VISIBLE|core_survived=true")
        self.core_visualization_visible.emit()

    def request_shutdown(self):
        self._emit("RENDERER_MAIN|DESKTOP_RUNTIME_FALLBACK_SHUTDOWN")

    def set_visual_state(self, _state_name):
        return

    def toggle_command_overlay(self):
        self._emit("RENDERER_MAIN|COMMAND_OVERLAY_UNAVAILABLE|reason=desktop_runtime_unavailable")

    def open_command_overlay(self):
        self.toggle_command_overlay()

    def command_overlay_state(self):
        return {"visible": False, "phase": "closed"}

    def request_create_custom_task_from_tray(self, source="tray"):
        self._emit(f"RENDERER_MAIN|TRAY_CREATE_CUSTOM_TASK_ABORTED|source={source}|reason=desktop_runtime_unavailable")

    def resident_access_status_snapshot(self):
        return build_resident_access_menu_plan(
            monitoring_hud_state=self.monitoring_hud_feature_state(),
            command_overlay_state=self.command_overlay_state(),
        )

    def open_resident_access_settings(self, source="tray", focus="quick_access"):
        self._emit(
            "RENDERER_MAIN|RESIDENT_ACCESS_SETTINGS_OPEN_ABORTED"
            f"|source={source}|focus={focus}|reason=desktop_runtime_unavailable"
        )

    def request_ai_status_from_resident_access(self, source="tray"):
        self._emit(
            "RENDERER_MAIN|RESIDENT_ACCESS_AI_STATUS_UNAVAILABLE"
            f"|source={source}|reason=desktop_runtime_unavailable"
        )

    def request_privacy_lockdown_from_resident_access(self, source="tray"):
        self._emit(
            "RENDERER_MAIN|RESIDENT_ACCESS_PRIVACY_LOCKDOWN_UNAVAILABLE"
            f"|source={source}|reason=desktop_runtime_unavailable"
        )

    def request_resident_quick_action_from_tray(self, route_id="", source="tray"):
        self._emit(
            "RENDERER_MAIN|RESIDENT_ACCESS_QUICK_ACTION_ABORTED"
            f"|source={source}|route_id={route_id}|reason=desktop_runtime_unavailable"
        )

    def show_ai_control_center_from_tray(self, source="tray"):
        self._emit(f"RENDERER_MAIN|AI_CONTROL_CENTER_ABORTED|source={source}|reason=desktop_runtime_unavailable")
        return {"shown": False, "reason": "desktop_runtime_unavailable"}

    def monitoring_hud_feature_state(self):
        return {
            "feature_enabled": False,
            "dashboard_visible": False,
            "overlay_deferred": True,
            "overlay_anchor_enabled": False,
        }

    def request_monitoring_hud_toggle_from_tray(self, source="tray"):
        self._emit(f"RENDERER_MAIN|TRAY_MONITORING_HUD_TOGGLE_ABORTED|source={source}|reason=desktop_runtime_unavailable")

    def request_monitoring_hud_dashboard_from_tray(self, source="tray", visible=True):
        self._emit(
            "RENDERER_MAIN|TRAY_MONITORING_HUD_DASHBOARD_ABORTED"
            f"|source={source}|visible={str(bool(visible)).lower()}|reason=desktop_runtime_unavailable"
        )

    def request_monitoring_hud_unanchor_from_tray(self, source="tray"):
        self._emit(f"RENDERER_MAIN|TRAY_MONITORING_HUD_UNANCHOR_ABORTED|source={source}|reason=desktop_runtime_unavailable")

    def handle_overlay_text_requested(self, _text):
        return

    def handle_overlay_backspace_requested(self):
        return

    def handle_overlay_submit_requested(self):
        return

    def handle_overlay_escape_requested(self):
        return

    def handle_overlay_global_click_requested(self, _x, _y):
        return

    def overlay_needs_global_input_capture(self):
        return False

    def overlay_allows_launch_grace(self):
        return False

    def overlay_monitors_global_clicks(self):
        return False


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


def normalize_shutdown_confirmation_decision(value):
    normalized = (str(value or "").strip().casefold())
    if normalized in {"accept", "accepted", "yes", "y", "true", "1"}:
        return SHUTDOWN_CONFIRMATION_ACCEPTED
    if normalized in {"cancel", "cancelled", "decline", "declined", "no", "n", "false", "0"}:
        return SHUTDOWN_CONFIRMATION_CANCELLED
    if normalized in {"timeout", "timed_out", "expired"}:
        return SHUTDOWN_CONFIRMATION_TIMEOUT
    return ""


def shutdown_confirmation_timeout_ms():
    return SHUTDOWN_CONFIRMATION_DEFAULT_TIMEOUT_MS


def shutdown_confirmation_allows_shutdown(decision):
    return normalize_shutdown_confirmation_decision(decision) == SHUTDOWN_CONFIRMATION_ACCEPTED


def shutdown_confirmation_runtime_markers(decision, source="hotkey"):
    normalized = normalize_shutdown_confirmation_decision(decision) or SHUTDOWN_CONFIRMATION_CANCELLED
    safe_source = str(source or "hotkey").replace("|", "_")
    if normalized == SHUTDOWN_CONFIRMATION_ACCEPTED:
        return (
            f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_ACCEPTED|source={safe_source}",
            f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_CLEAN_SHUTDOWN_REQUESTED|source={safe_source}",
        )
    if normalized == SHUTDOWN_CONFIRMATION_TIMEOUT:
        return (
            f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_TIMEOUT|source={safe_source}",
            f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_SESSION_PRESERVED|source={safe_source}|reason=timeout",
        )
    return (
        f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_CANCELLED|source={safe_source}",
        f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_SESSION_PRESERVED|source={safe_source}|reason=cancelled",
    )


def shutdown_confirmation_requested_marker(source="hotkey"):
    safe_source = str(source or "hotkey").replace("|", "_")
    return f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_REQUESTED|source={safe_source}"


def _screen_label(screen):
    if screen is None:
        return "none"
    try:
        name = screen.name()
    except Exception:
        name = ""
    geometry = screen.geometry()
    return (
        f"name={str(name or 'unknown').replace('|', '_')}"
        f"|x={geometry.x()}|y={geometry.y()}|w={geometry.width()}|h={geometry.height()}"
    )


def resolve_core_visualization_screen(app):
    """Keep the persona Core on the preset install monitor, not on HUD surfaces.

    Until installer-owned monitor preference exists in repo truth, the safest
    approximation is the center physical monitor when three or more screens are
    present, otherwise the OS primary screen.
    """
    screens = list(app.screens())
    primary = app.primaryScreen()
    if not screens:
        return primary, "primary-fallback"

    indexed = list(enumerate(screens))
    configured = (os.environ.get("NEXUS_CORE_MONITOR_INDEX") or "").strip()
    if configured:
        try:
            requested_index = int(configured)
        except ValueError:
            requested_index = -1
        if 0 <= requested_index < len(screens):
            return screens[requested_index], f"configured-index-{requested_index}"

    if len(screens) >= 3:
        by_x_center = sorted(indexed, key=lambda item: (item[1].geometry().center().x(), item[1].geometry().center().y()))
        original_index, screen = by_x_center[len(by_x_center) // 2]
        return screen, f"middle-monitor-default-{original_index}"

    return primary or screens[0], "primary-fallback"


def _show_shutdown_confirmation_dialog(timeout_ms, event_logger=None, source="hotkey"):
    safe_source = str(source or "hotkey").replace("|", "_")
    timeout_ms = max(1000, int(timeout_ms))
    if os.name == "nt":
        try:
            user32 = ctypes.windll.user32
            message_box_timeout = getattr(user32, "MessageBoxTimeoutW")
            flags = 0x00000004 | 0x00000030 | 0x00000100 | 0x00010000 | 0x00040000
            if callable(event_logger):
                event_logger(
                    "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_DIALOG_VISIBLE"
                    f"|source={safe_source}|timeout_ms={timeout_ms}|implementation=win32_message_box_timeout"
                )
            result = message_box_timeout(
                None,
                "Choose Yes to close the desktop runtime, or No to keep the current session running.",
                "Confirm shutdown",
                flags,
                0,
                timeout_ms,
            )
            if result == 6:
                return SHUTDOWN_CONFIRMATION_ACCEPTED
            if result == 32000:
                return SHUTDOWN_CONFIRMATION_TIMEOUT
            return SHUTDOWN_CONFIRMATION_CANCELLED
        except Exception as exc:
            if callable(event_logger):
                event_logger(
                    "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_NATIVE_FALLBACK"
                    f"|source={safe_source}|reason={type(exc).__name__}"
                )

    message_box = QMessageBox()
    message_box.setWindowTitle("Confirm shutdown")
    message_box.setText("Shut down Nexus Desktop AI?")
    message_box.setInformativeText(
        "Choose Yes to close the desktop runtime, or No to keep the current session running."
    )
    message_box.setIcon(QMessageBox.Icon.Warning)
    message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    message_box.setDefaultButton(QMessageBox.StandardButton.No)
    message_box.setEscapeButton(QMessageBox.StandardButton.No)
    message_box.setWindowModality(Qt.WindowModality.ApplicationModal)
    message_box.setWindowFlags(
        message_box.windowFlags()
        | Qt.WindowType.Window
        | Qt.WindowType.WindowStaysOnTopHint
    )

    timed_out = {"value": False}

    def expire_confirmation():
        timed_out["value"] = True
        message_box.reject()

    timer = QTimer(message_box)
    timer.setSingleShot(True)
    timer.timeout.connect(expire_confirmation)
    timer.start(timeout_ms)

    try:
        message_box.show()
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if screen is not None:
            geometry = message_box.frameGeometry()
            geometry.moveCenter(screen.availableGeometry().center())
            message_box.move(geometry.topLeft())
        message_box.raise_()
        message_box.activateWindow()
        QApplication.processEvents()
        if callable(event_logger):
            event_logger(
                "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_DIALOG_VISIBLE"
                f"|source={safe_source}|timeout_ms={timeout_ms}|implementation=qt_message_box"
            )
        result = message_box.exec()
    finally:
        timer.stop()

    if timed_out["value"]:
        return SHUTDOWN_CONFIRMATION_TIMEOUT
    if result == QMessageBox.StandardButton.Yes:
        return SHUTDOWN_CONFIRMATION_ACCEPTED
    return SHUTDOWN_CONFIRMATION_CANCELLED


def write_desktop_settled_signal_file():
    if not RUNTIME_LOG_FILE:
        return False
    try:
        signal_path = os.path.join(os.path.dirname(RUNTIME_LOG_FILE), "desktop_settled.signal")
        with open(signal_path, "w", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now(datetime.timezone.utc).isoformat()}|renderer authoritative settled\n")
        return True
    except Exception:
        return False


def monitoring_hud_startup_enabled():
    value = (os.environ.get(MONITORING_HUD_STARTUP_ENV) or "").strip().casefold()
    return value in {"1", "true", "yes", "on"}


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
    app.setWindowIcon(build_resident_tray_icon())
    app.setQuitOnLastWindowClosed(False)
    try:
        app.setApplicationDisplayName(TRAY_IDENTITY_LABEL)
    except Exception:
        pass
    runtime_milestone("RENDERER_MAIN|QAPPLICATION_CREATED")
    if exit_if_startup_abort_requested():
        return 0

    visual_html_path = os.path.join(ROOT_DIR, "nexus_visual", "orin_core_desktop.html")
    monitoring_hud_html_path = os.path.join(ROOT_DIR, "nexus_visual", "monitoring_hud.html")
    monitoring_hud_forced_startup_visible = monitoring_hud_startup_enabled()
    monitoring_hud_saved_state = load_monitoring_hud_state(runtime_milestone)
    monitoring_hud_saved_feature_enabled = bool(monitoring_hud_saved_state.get("featureEnabled"))
    monitoring_hud_feature_enabled_at_startup = (
        bool(monitoring_hud_forced_startup_visible) or monitoring_hud_saved_feature_enabled
    )
    monitoring_hud_dashboard_visible_at_startup = bool(monitoring_hud_forced_startup_visible)
    runtime_milestone(
        "RENDERER_MAIN|MONITORING_HUD_STARTUP_STATE_READY"
        f"|source={monitoring_hud_saved_state.get('source', 'unknown')}"
        f"|feature_enabled={str(monitoring_hud_feature_enabled_at_startup).lower()}"
        f"|dashboard_visible={str(monitoring_hud_dashboard_visible_at_startup).lower()}"
        f"|forced_visible={str(bool(monitoring_hud_forced_startup_visible)).lower()}"
    )
    runtime_milestone("RENDERER_MAIN|VISUAL_HTML_RESOLVED")
    if exit_if_startup_abort_requested():
        return 0

    screen = app.primaryScreen()
    core_screen, core_screen_source = resolve_core_visualization_screen(app)
    runtime_milestone(
        "RENDERER_MAIN|CORE_VISUALIZATION_PRESET_MONITOR_SELECTION_READY"
        f"|source={core_screen_source}|{_screen_label(core_screen)}"
    )
    core_window = CoreVisualizationWindow(
        core_screen or screen,
        visual_html_path,
        event_logger=runtime_milestone,
    )
    if DesktopRuntimeWindow is None:
        window = DesktopRuntimeUnavailable(
            event_logger=runtime_milestone,
            reason=repr(DESKTOP_RUNTIME_IMPORT_ERROR),
        )
    else:
        try:
            window = DesktopRuntimeWindow(
                screen,
                monitoring_hud_html_path,
                event_logger=runtime_milestone,
                runtime_log_path=RUNTIME_LOG_FILE,
                surface_role="hud",
                monitoring_hud_feature_enabled=monitoring_hud_feature_enabled_at_startup,
                monitoring_hud_dashboard_visible=monitoring_hud_dashboard_visible_at_startup,
                monitoring_hud_initial_state=monitoring_hud_saved_state,
            )
        except Exception as exc:
            window = DesktopRuntimeUnavailable(
                event_logger=runtime_milestone,
                reason=repr(exc),
            )
    runtime_milestone("RENDERER_MAIN|WINDOW_CONSTRUCTED")
    if exit_if_startup_abort_requested():
        return 0

    bus = ShutdownBus()
    runtime_milestone("RENDERER_MAIN|SHUTDOWN_BUS_READY")
    hotkeys = GlobalHotkeyManager(bus)
    relaunch_signal = NamedSignal(RUNTIME_RELAUNCH_EVENT)
    desktop_settled_signal = NamedSignal(RUNTIME_DESKTOP_SETTLED_EVENT)
    shutdown_started = False
    shutdown_confirmation_active = False
    shutdown_force_kill_timer = None
    if exit_if_startup_abort_requested():
        return 0

    def do_shutdown():
        nonlocal shutdown_started, shutdown_force_kill_timer
        if shutdown_started:
            return
        settings_guard = getattr(window, "request_resident_access_settings_shutdown_guard", None)
        if callable(settings_guard):
            try:
                if settings_guard(source="client_shutdown", resume_callback=do_shutdown):
                    runtime_milestone(
                        "RENDERER_MAIN|SHUTDOWN_BLOCKED_BY_RESIDENT_SETTINGS_DIRTY_GUARD"
                        "|source=client_shutdown"
                    )
                    return
            except TypeError:
                if settings_guard(source="client_shutdown"):
                    runtime_milestone(
                        "RENDERER_MAIN|SHUTDOWN_BLOCKED_BY_RESIDENT_SETTINGS_DIRTY_GUARD"
                        "|source=client_shutdown"
                    )
                    return
        shutdown_started = True
        runtime_milestone("RENDERER_MAIN|SHUTDOWN_REQUESTED")
        tray_entry.close()
        hotkeys.stop()
        core_window.request_shutdown()
        window.request_shutdown()
        shutdown_force_kill_timer = threading.Timer(1.2, hotkeys.force_kill)
        shutdown_force_kill_timer.daemon = True
        shutdown_force_kill_timer.start()

    def request_shutdown_confirmation(source="hotkey"):
        nonlocal shutdown_confirmation_active
        safe_source = str(source or "hotkey").replace("|", "_")
        if shutdown_started:
            runtime_milestone(
                f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_IGNORED|source={safe_source}|reason=shutdown_started"
            )
            return
        if shutdown_confirmation_active:
            runtime_milestone(
                f"RENDERER_MAIN|SHUTDOWN_CONFIRMATION_IGNORED|source={safe_source}|reason=already_active"
            )
            return
        settings_guard = getattr(window, "request_resident_access_settings_shutdown_guard", None)
        if callable(settings_guard):
            try:
                if settings_guard(
                    source=f"shutdown_confirmation_{safe_source}",
                    resume_callback=lambda: request_shutdown_confirmation(source=safe_source),
                ):
                    runtime_milestone(
                        "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_BLOCKED_BY_RESIDENT_SETTINGS_DIRTY_GUARD"
                        f"|source={safe_source}"
                    )
                    return
            except TypeError:
                if settings_guard(source=f"shutdown_confirmation_{safe_source}"):
                    runtime_milestone(
                        "RENDERER_MAIN|SHUTDOWN_CONFIRMATION_BLOCKED_BY_RESIDENT_SETTINGS_DIRTY_GUARD"
                        f"|source={safe_source}"
                    )
                    return

        shutdown_confirmation_active = True
        try:
            runtime_milestone(shutdown_confirmation_requested_marker(safe_source))
            decision = _show_shutdown_confirmation_dialog(
                shutdown_confirmation_timeout_ms(),
                event_logger=runtime_milestone,
                source=safe_source,
            )

            for marker in shutdown_confirmation_runtime_markers(decision, safe_source):
                runtime_milestone(marker)

            if shutdown_confirmation_allows_shutdown(decision):
                do_shutdown()
        finally:
            shutdown_confirmation_active = False

    def poll_relaunch_request():
        if relaunch_signal.consume():
            runtime_milestone("RENDERER_MAIN|RELAUNCH_REQUEST_RECEIVED")
            do_shutdown()

    shutdown_confirmation_dispatcher = ShutdownConfirmationDispatcher(
        request_shutdown_confirmation,
        app,
    )

    bus.shutdown_requested.connect(do_shutdown)
    bus.shutdown_confirmation_requested.connect(
        shutdown_confirmation_dispatcher.request,
        Qt.ConnectionType.QueuedConnection,
    )
    bus.command_overlay_toggle_requested.connect(window.toggle_command_overlay)
    bus.command_overlay_text_requested.connect(window.handle_overlay_text_requested)
    bus.command_overlay_backspace_requested.connect(window.handle_overlay_backspace_requested)
    bus.command_overlay_submit_requested.connect(window.handle_overlay_submit_requested)
    bus.command_overlay_escape_requested.connect(window.handle_overlay_escape_requested)
    bus.command_overlay_global_click_requested.connect(window.handle_overlay_global_click_requested)
    tray_entry = DesktopTrayEntry(
        app,
        window,
        runtime_milestone,
        shutdown_confirmation_requester=request_shutdown_confirmation,
    )
    tray_entry.initialize()
    hotkeys.set_overlay_input_enabled_provider(window.overlay_needs_global_input_capture)
    hotkeys.set_overlay_launch_grace_allowed_provider(window.overlay_allows_launch_grace)
    hotkeys.set_overlay_click_monitor_provider(window.overlay_monitors_global_clicks)
    hotkeys.start()
    runtime_milestone("RENDERER_MAIN|HOTKEYS_STARTED")
    if exit_if_startup_abort_requested(hotkeys, tray_entry):
        return 0

    print("Nexus Desktop AI Desktop Runtime - Version 1.02")
    print("Command Overlay: Ctrl + Alt + Home or Ctrl + Alt + 1")
    print("Hotkey: Ctrl + Alt + End or Ctrl + Alt + 2 (direct shutdown; tray exit asks for confirmation)")

    def settle_passive_default_handoff():
        if exit_if_startup_abort_requested(hotkeys, tray_entry):
            app.quit()
            return
        window.set_visual_state("dormant")
        core_window.set_visual_state("dormant")
        runtime_milestone("RENDERER_MAIN|PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant")
        if desktop_settled_signal.signal():
            runtime_milestone("RENDERER_MAIN|DESKTOP_SETTLED_SIGNAL_SET")
        if write_desktop_settled_signal_file():
            runtime_milestone("RENDERER_MAIN|DESKTOP_SETTLED_SIGNAL_FILE_SET")
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
        core_window.show()
        if monitoring_hud_dashboard_visible_at_startup:
            window.show()
            runtime_milestone("RENDERER_MAIN|WINDOW_SHOW_REQUESTED|reason=core_and_hud_visualization_ready|surfaces=core_and_dashboard|monitoring_hud_startup=enabled")
        else:
            runtime_milestone("RENDERER_MAIN|WINDOW_SHOW_REQUESTED|reason=core_visualization_ready|surfaces=core_only|monitoring_hud_startup=suppressed")
            runtime_milestone(
                "RENDERER_MAIN|MONITORING_HUD_STARTUP_SUPPRESSED"
                f"|surface=dashboard|overlay=deferred|feature_enabled={str(monitoring_hud_feature_enabled_at_startup).lower()}"
            )

    core_window.core_visualization_ready.connect(show_window_after_core_visualization_ready)
    if monitoring_hud_dashboard_visible_at_startup:
        window.core_visualization_visible.connect(mark_startup_ready)
    else:
        core_window.core_visualization_visible.connect(mark_startup_ready)
    runtime_milestone("RENDERER_MAIN|WINDOW_SHOW_DEFERRED_UNTIL_CORE_READY")
    if core_window.is_core_visualization_ready():
        QTimer.singleShot(0, show_window_after_core_visualization_ready)

    relaunch_timer = QTimer()
    relaunch_timer.timeout.connect(poll_relaunch_request)
    relaunch_timer.start(200)

    exit_code = app.exec()
    relaunch_timer.stop()
    relaunch_signal.close()
    desktop_settled_signal.close()
    tray_entry.close()
    hotkeys.stop()
    core_window.request_shutdown()
    runtime_milestone(f"RENDERER_MAIN|EVENT_LOOP_EXIT|code={exit_code}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
