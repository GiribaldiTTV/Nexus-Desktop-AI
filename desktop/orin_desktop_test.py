import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from desktop.desktop_renderer import DesktopRuntimeWindow
from desktop.hotkeys import ShutdownBus, GlobalHotkeyManager


def main():
    app = QApplication(sys.argv)

    visual_html_path = os.path.join(ROOT_DIR, "jarvis_visual", "jarvis_core_desktop.html")

    screen = app.primaryScreen()
    window = DesktopRuntimeWindow(screen, visual_html_path)

    bus = ShutdownBus()
    hotkeys = GlobalHotkeyManager(bus)

    def do_shutdown():
        hotkeys.stop()
        window.request_shutdown()
        QTimer.singleShot(1200, hotkeys.force_kill)

    bus.shutdown_requested.connect(do_shutdown)
    hotkeys.start()

    print("Jarvis Desktop Concept 1 - Version 1.02")
    print("Hotkey: Ctrl + Alt + End")

    window.show()

    raise RuntimeError("Jarvis test crash triggered intentionally")

    exit_code = app.exec()
    hotkeys.stop()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
