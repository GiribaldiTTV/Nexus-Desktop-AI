import os
import sys
import datetime

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from desktop.desktop_renderer import DesktopJarvisWindow
from desktop.hotkeys import ShutdownBus, GlobalHotkeyManager

RUNTIME_LOG_FILE = ""


def parse_runtime_log_arg(argv):
    global RUNTIME_LOG_FILE
    for i, arg in enumerate(argv):
        if arg == "--runtime-log" and i + 1 < len(argv):
            RUNTIME_LOG_FILE = argv[i + 1]
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


def main():
    parse_runtime_log_arg(sys.argv)
    runtime_milestone("RENDERER_MAIN|START")

    app = QApplication(sys.argv)
    runtime_milestone("RENDERER_MAIN|QAPPLICATION_CREATED")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    visual_html_path = os.path.join(base_dir, "jarvis_visual", "jarvis_core_desktop.html")
    runtime_milestone("RENDERER_MAIN|VISUAL_HTML_RESOLVED")

    screen = app.primaryScreen()
    window = DesktopJarvisWindow(screen, visual_html_path)
    runtime_milestone("RENDERER_MAIN|WINDOW_CONSTRUCTED")

    bus = ShutdownBus()
    runtime_milestone("RENDERER_MAIN|SHUTDOWN_BUS_READY")
    hotkeys = GlobalHotkeyManager(bus)

    def do_shutdown():
        runtime_milestone("RENDERER_MAIN|SHUTDOWN_REQUESTED")
        hotkeys.stop()
        window.request_shutdown()
        QTimer.singleShot(1200, hotkeys.force_kill)

    bus.shutdown_requested.connect(do_shutdown)
    hotkeys.start()
    runtime_milestone("RENDERER_MAIN|HOTKEYS_STARTED")

    print("Jarvis Desktop Concept 1 - Version 1.02")
    print("Hotkey: Ctrl + Alt + End")

    window.show()
    runtime_milestone("RENDERER_MAIN|WINDOW_SHOW_CALLED")
    QTimer.singleShot(0, lambda: runtime_milestone("RENDERER_MAIN|STARTUP_READY"))

    exit_code = app.exec()
    hotkeys.stop()
    runtime_milestone(f"RENDERER_MAIN|EVENT_LOOP_EXIT|code={exit_code}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
