import os
import sys
import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from desktop.desktop_renderer import DesktopJarvisWindow
from desktop.hotkeys import ShutdownBus, GlobalHotkeyManager
from desktop.single_instance import NamedSignal

RUNTIME_LOG_FILE = ""
STARTUP_ABORT_SIGNAL_FILE = ""
RUNTIME_RELAUNCH_EVENT = r"Local\JarvisRuntimeRelaunchRequestV1"


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


def startup_abort_requested():
    return bool(STARTUP_ABORT_SIGNAL_FILE) and os.path.exists(STARTUP_ABORT_SIGNAL_FILE)


def exit_if_startup_abort_requested(hotkeys=None):
    if not startup_abort_requested():
        return False

    runtime_milestone("RENDERER_MAIN|STARTUP_ABORTED")

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
    runtime_milestone("RENDERER_MAIN|QAPPLICATION_CREATED")
    if exit_if_startup_abort_requested():
        return 0

    visual_html_path = os.path.join(ROOT_DIR, "jarvis_visual", "jarvis_core_desktop.html")
    runtime_milestone("RENDERER_MAIN|VISUAL_HTML_RESOLVED")
    if exit_if_startup_abort_requested():
        return 0

    screen = app.primaryScreen()
    window = DesktopJarvisWindow(screen, visual_html_path, event_logger=runtime_milestone)
    runtime_milestone("RENDERER_MAIN|WINDOW_CONSTRUCTED")
    if exit_if_startup_abort_requested():
        return 0

    bus = ShutdownBus()
    runtime_milestone("RENDERER_MAIN|SHUTDOWN_BUS_READY")
    hotkeys = GlobalHotkeyManager(bus)
    relaunch_signal = NamedSignal(RUNTIME_RELAUNCH_EVENT)
    shutdown_started = False
    if exit_if_startup_abort_requested():
        return 0

    def do_shutdown():
        nonlocal shutdown_started
        if shutdown_started:
            return
        shutdown_started = True
        runtime_milestone("RENDERER_MAIN|SHUTDOWN_REQUESTED")
        hotkeys.stop()
        window.request_shutdown()
        QTimer.singleShot(1200, hotkeys.force_kill)

    def poll_relaunch_request():
        if relaunch_signal.consume():
            runtime_milestone("RENDERER_MAIN|RELAUNCH_REQUEST_RECEIVED")
            do_shutdown()

    bus.shutdown_requested.connect(do_shutdown)
    bus.command_overlay_toggle_requested.connect(window.toggle_command_overlay)
    bus.command_character_typed.connect(window.handle_command_character)
    bus.command_backspace_requested.connect(window.handle_command_backspace)
    bus.command_enter_requested.connect(window.handle_command_submit)
    bus.command_escape_requested.connect(window.handle_command_escape)
    window.command_mode_changed.connect(hotkeys.set_command_mode_active)
    hotkeys.start()
    runtime_milestone("RENDERER_MAIN|HOTKEYS_STARTED")
    if exit_if_startup_abort_requested(hotkeys):
        return 0

    print("Jarvis Desktop Concept 1 - Version 1.02")
    print("Command Overlay: Ctrl + Alt + Home")
    print("Hotkey: Ctrl + Alt + End")

    window.show()
    runtime_milestone("RENDERER_MAIN|WINDOW_SHOW_CALLED")
    if exit_if_startup_abort_requested(hotkeys):
        return 0

    def settle_passive_default_handoff():
        if exit_if_startup_abort_requested(hotkeys):
            app.quit()
            return
        window.set_visual_state("dormant")
        runtime_milestone("RENDERER_MAIN|PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant")

    def mark_startup_ready():
        if exit_if_startup_abort_requested(hotkeys):
            app.quit()
            return
        runtime_milestone("RENDERER_MAIN|STARTUP_READY")
        settle_passive_default_handoff()

    relaunch_timer = QTimer()
    relaunch_timer.timeout.connect(poll_relaunch_request)
    relaunch_timer.start(200)
    QTimer.singleShot(0, mark_startup_ready)

    exit_code = app.exec()
    relaunch_timer.stop()
    relaunch_signal.close()
    hotkeys.stop()
    runtime_milestone(f"RENDERER_MAIN|EVENT_LOOP_EXIT|code={exit_code}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
