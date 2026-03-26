import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from desktop.desktop_renderer import DesktopJarvisWindow
from desktop.hotkeys import ShutdownBus, GlobalHotkeyManager


def main():
    app = QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    visual_html_path = os.path.join(base_dir, "jarvis_visual", "jarvis_core_desktop.html")

    screen = app.primaryScreen()
    window = DesktopJarvisWindow(screen, visual_html_path)

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

    exit_code = app.exec()
    hotkeys.stop()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
