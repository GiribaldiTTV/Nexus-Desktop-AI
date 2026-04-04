import sys
import os
import asyncio
import threading
import time
import ctypes
import random
import math
import datetime
from ctypes import wintypes

from pynput import keyboard as pynput_keyboard

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QLineEdit, QProgressBar, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, QTimer, QObject, Signal, QPropertyAnimation, QUrl, QRect
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtWebEngineWidgets import QWebEngineView

from Audio.jarvis_voice import JarvisSpeaker


VALID_BOOT_PROFILES = {"manual", "auto_handoff_skip_import"}
VALID_AUDIO_MODES = {"voice", "quiet"}
BOOT_LOG_ROOTS = {
    "manual": os.path.join("dev", "logs", "boot_manual_flow"),
    "auto_handoff_skip_import": os.path.join("dev", "logs", "boot_auto_handoff_skip_import"),
}
AUTO_STAGE_COMMANDS = {
    "command_1": "engage hud",
    "command_2": "no",
}


def parse_dev_run_config(argv):
    boot_profile = "manual"
    audio_mode = "voice"
    qt_argv = [argv[0]]

    i = 1
    while i < len(argv):
        arg = argv[i]

        if arg == "--boot-profile" and i + 1 < len(argv):
            candidate = argv[i + 1].strip().lower()
            if candidate in VALID_BOOT_PROFILES:
                boot_profile = candidate
            i += 2
            continue

        if arg == "--audio-mode" and i + 1 < len(argv):
            candidate = argv[i + 1].strip().lower()
            if candidate in VALID_AUDIO_MODES:
                audio_mode = candidate
            i += 2
            continue

        qt_argv.append(arg)
        i += 1

    return {
        "boot_profile": boot_profile,
        "audio_mode": audio_mode,
        "qt_argv": qt_argv,
    }


def resolve_boot_runtime_log_paths(base_dir, boot_profile, audio_mode):
    relative_root = BOOT_LOG_ROOTS[boot_profile]
    runtime_root = os.path.join(base_dir, relative_root)
    os.makedirs(runtime_root, exist_ok=True)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    runtime_file = os.path.join(runtime_root, f"Runtime_{stamp}_{audio_mode}.txt")
    return runtime_root, runtime_file


def screen_marker(screen):
    g = screen.geometry()
    return (
        f"{screen.name()}"
        f"@x{g.x()}_y{g.y()}_w{g.width()}_h{g.height()}"
    )


# ---------------------------
# Win32 desktop / WorkerW helpers
# ---------------------------

user32 = ctypes.windll.user32

SendMessageTimeoutW = user32.SendMessageTimeoutW
EnumWindows = user32.EnumWindows
FindWindowW = user32.FindWindowW
FindWindowExW = user32.FindWindowExW
SetParent = user32.SetParent
ShowWindow = user32.ShowWindow
SetWindowPos = user32.SetWindowPos
GetWindowLongPtrW = user32.GetWindowLongPtrW
SetWindowLongPtrW = user32.SetWindowLongPtrW

SMTO_NORMAL = 0x0000
SW_SHOW = 5

HWND_BOTTOM = 1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_NOOWNERZORDER = 0x0200
SWP_NOSENDCHANGING = 0x0400

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TRANSPARENT = 0x00000020
WS_EX_NOACTIVATE = 0x08000000

WM_NCHITTEST = 0x0084
HTTRANSPARENT = -1

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)


def get_workerw():
    progman = FindWindowW("Progman", None)
    if progman:
        result = wintypes.DWORD()
        SendMessageTimeoutW(
            progman,
            0x052C,
            0,
            0,
            SMTO_NORMAL,
            1000,
            ctypes.byref(result)
        )

    workerw = None

    @WNDENUMPROC
    def enum_windows_proc(hwnd, lParam):
        nonlocal workerw
        shell_def_view = FindWindowExW(hwnd, None, "SHELLDLL_DefView", None)
        if shell_def_view:
            possible = FindWindowExW(None, hwnd, "WorkerW", None)
            if possible:
                workerw = possible
                return False
        return True

    EnumWindows(enum_windows_proc, 0)
    return workerw


def attach_window_to_desktop(hwnd):
    workerw = get_workerw()
    if not workerw:
        return False

    SetParent(hwnd, workerw)
    ShowWindow(hwnd, SW_SHOW)
    SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW | SWP_NOOWNERZORDER | SWP_NOSENDCHANGING
    )
    return True


def make_window_noninteractive(hwnd):
    exstyle = GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    exstyle |= WS_EX_TRANSPARENT | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
    SetWindowLongPtrW(hwnd, GWL_EXSTYLE, exstyle)

    SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW | SWP_NOOWNERZORDER | SWP_NOSENDCHANGING
    )


# ---------------------------
# UI signals
# ---------------------------

class UIBus(QObject):
    set_overlay_title = Signal(str)
    set_overlay_status = Signal(str)
    set_overlay_log = Signal(str)
    append_overlay_log = Signal(str)
    clear_overlay_log = Signal()

    set_left_body = Signal(str)
    set_right_body = Signal(str)

    set_visual_state = Signal(str)
    set_voice_level = Signal(float)

    show_command_input = Signal()
    hide_command_input = Signal()
    clear_command_input = Signal()

    set_progress = Signal(int)
    show_progress = Signal()
    hide_progress = Signal()

    begin_desktop_handoff = Signal()
    shutdown_requested = Signal()


# ---------------------------
# Base windows
# ---------------------------

class BaseWindow(QWidget):
    def __init__(self, screen):
        super().__init__()
        self.screen_ref = screen
        self.desktop_mode = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.StrongFocus)

        geo = screen.geometry()
        self.setGeometry(geo)

    def closeEvent(self, event):
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        else:
            super().keyPressEvent(event)

    def nativeEvent(self, eventType, message):
        if self.desktop_mode:
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == WM_NCHITTEST:
                return True, HTTRANSPARENT
        return super().nativeEvent(eventType, message)

    def enable_desktop_mode(self):
        self.desktop_mode = True

        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.NoFocus)

        self.hide()
        self.show()

        hwnd = int(self.winId())
        attach_window_to_desktop(hwnd)
        make_window_noninteractive(hwnd)
        self.lower()


class BootSideWindow(BaseWindow):
    def __init__(self, screen, title):
        super().__init__(screen)
        self.setStyleSheet("background-color: rgb(0, 0, 0);")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.title.setStyleSheet("""
            color: rgb(0, 110, 160);
            font-size: 26px;
            font-weight: bold;
            background-color: rgb(0, 0, 0);
        """)

        self.body = QLabel("")
        self.body.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.body.setStyleSheet("""
            color: rgb(120, 220, 255);
            font-size: 18px;
            background-color: rgb(0, 0, 0);
        """)

        layout.addWidget(self.title)
        layout.addWidget(self.body)
        layout.addStretch()

    def set_body(self, text):
        self.body.setText(text)


class DesktopVisualWindow(BaseWindow):
    def __init__(self, screen, visual_html_path):
        super().__init__(screen)
        self.full_geo = screen.geometry()
        self.compact_geo = self.compute_compact_geometry()

        self.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.setGeometry(self.compact_geo)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.webview = QWebEngineView()
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setFocusPolicy(Qt.NoFocus)
        self.webview.setStyleSheet("background-color: rgb(0, 0, 0); border: none;")
        self.webview.load(QUrl.fromLocalFile(os.path.abspath(visual_html_path)))

        root.addWidget(self.webview)

    def compute_compact_geometry(self):
        g = self.screen_ref.geometry()

        width = int(g.width() * 0.46)
        height = int(g.height() * 0.68)

        x = g.x() + (g.width() - width) // 2
        y = g.y() + int((g.height() - height) * 0.40)

        return QRect(x, y, width, height)

    def prepare_desktop_geometry(self):
        self.compact_geo = self.compute_compact_geometry()
        self.setGeometry(self.compact_geo)

    def set_visual_state(self, state_name):
        js = f"window.setJarvisState && window.setJarvisState('{state_name}');"
        self.webview.page().runJavaScript(js)

    def set_voice_level(self, level):
        level = max(0.0, min(1.0, float(level)))
        js = f"window.setJarvisVoiceLevel && window.setJarvisVoiceLevel({level:.4f});"
        self.webview.page().runJavaScript(js)

    def fade_in(self, start_opacity=0.0, end_opacity=1.0, duration_ms=900):
        self.setWindowOpacity(start_opacity)
        self.fade_in_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_anim.setDuration(duration_ms)
        self.fade_in_anim.setStartValue(start_opacity)
        self.fade_in_anim.setEndValue(end_opacity)
        self.fade_in_anim.start()


class JarvisBootCenterWindow(BaseWindow):
    command_submitted = Signal(str)

    def __init__(self, screen, visual_html_path):
        super().__init__(screen)
        self.setStyleSheet("background-color: rgb(0, 0, 0);")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.visual_container = QFrame()
        self.visual_container.setStyleSheet("background-color: rgb(0, 0, 0);")
        visual_layout = QVBoxLayout(self.visual_container)
        visual_layout.setContentsMargins(0, 0, 0, 0)
        visual_layout.setSpacing(0)

        self.webview = QWebEngineView()
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setFocusPolicy(Qt.NoFocus)
        self.webview.setStyleSheet("background-color: rgb(0, 0, 0); border: none;")
        self.webview.load(QUrl.fromLocalFile(os.path.abspath(visual_html_path)))

        visual_layout.addWidget(self.webview)

        self.overlay = QFrame()
        self.overlay.setStyleSheet("background: transparent;")
        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setContentsMargins(40, 24, 40, 24)
        overlay_layout.setSpacing(10)

        overlay_layout.addStretch()

        self.overlay_title = QLabel("JARVIS")
        self.overlay_title.setAlignment(Qt.AlignHCenter)
        self.overlay_title.setStyleSheet("""
            color: rgb(0, 190, 255);
            font-size: 58px;
            font-weight: bold;
            background: transparent;
        """)

        self.overlay_sub = QLabel("PRIMARY SYSTEM INTELLIGENCE")
        self.overlay_sub.setAlignment(Qt.AlignHCenter)
        self.overlay_sub.setStyleSheet("""
            color: rgb(0, 110, 160);
            font-size: 18px;
            background: transparent;
        """)

        overlay_layout.addWidget(self.overlay_title)
        overlay_layout.addWidget(self.overlay_sub)
        overlay_layout.addStretch()

        self.console_zone = QFrame()
        self.console_zone.setStyleSheet("""
            background-color: rgba(0, 0, 0, 190);
            border-top: 1px solid rgb(0, 70, 100);
        """)

        console_layout = QVBoxLayout(self.console_zone)
        console_layout.setContentsMargins(40, 18, 40, 18)
        console_layout.setSpacing(10)

        self.status = QLabel("INITIALIZING")
        self.status.setAlignment(Qt.AlignLeft)
        self.status.setStyleSheet("""
            color: rgb(0, 120, 180);
            font-size: 20px;
            background: transparent;
        """)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgb(0, 170, 255);
                background-color: rgb(10, 10, 10);
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: rgb(0, 170, 255);
            }
        """)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            QTextEdit {
                color: rgb(120, 220, 255);
                background-color: rgba(0, 0, 0, 170);
                border: 1px solid rgb(0, 70, 100);
                font-size: 15px;
                padding: 8px;
            }
        """)

        self.command_box = QLineEdit()
        self.command_box.setPlaceholderText("Enter command...")
        self.command_box.setStyleSheet("""
            QLineEdit {
                color: rgb(120, 220, 255);
                background-color: rgba(10, 10, 10, 220);
                border: 2px solid rgb(0, 170, 255);
                padding: 10px;
                font-size: 18px;
            }
        """)
        self.command_box.returnPressed.connect(self.submit_command)
        self.command_box.hide()
        self.command_box.setEnabled(False)

        console_layout.addWidget(self.status)
        console_layout.addWidget(self.progress)
        console_layout.addWidget(self.log, stretch=1)
        console_layout.addWidget(self.command_box)

        overlay_layout.addWidget(self.console_zone)

        root.addWidget(self.visual_container)

        self.overlay.setParent(self)
        self.overlay.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(self.rect())

    def submit_command(self):
        text = self.command_box.text().strip()
        if not text:
            return

        self.command_box.setEnabled(False)
        self.command_box.hide()
        self.command_submitted.emit(text)

    def show_command_input(self):
        if not self.desktop_mode:
            self.command_box.setEnabled(True)
            self.command_box.show()
            self.command_box.raise_()
            self.command_box.setFocus()

    def hide_command_input(self):
        self.command_box.clear()
        self.command_box.setEnabled(False)
        self.command_box.hide()

    def clear_command_input(self):
        self.command_box.clear()

    def set_title(self, text):
        self.overlay_title.setText(text)

    def set_status(self, text):
        self.status.setText(text)

    def set_log(self, text):
        self.log.setPlainText(text)

    def append_log(self, text):
        self.log.append(text)

    def clear_log(self):
        self.log.clear()

    def set_progress(self, value):
        self.progress.setValue(value)

    def show_progress(self):
        self.progress.show()

    def hide_progress(self):
        self.progress.hide()

    def set_visual_state(self, state_name):
        js = f"window.setJarvisState && window.setJarvisState('{state_name}');"
        self.webview.page().runJavaScript(js)

    def set_voice_level(self, level):
        level = max(0.0, min(1.0, float(level)))
        js = f"window.setJarvisVoiceLevel && window.setJarvisVoiceLevel({level:.4f});"
        self.webview.page().runJavaScript(js)

    def enter_background_visual_mode(self):
        self.hide_command_input()
        self.progress.hide()
        self.console_zone.hide()
        self.overlay_title.setText("")
        self.overlay_sub.setText("")

    def fade_overlay(self, end_opacity=0.0, duration_ms=900):
        self.overlay_anim = QPropertyAnimation(self.overlay, b"windowOpacity")
        self.overlay_anim.setDuration(duration_ms)
        self.overlay_anim.setStartValue(self.overlay.windowOpacity())
        self.overlay_anim.setEndValue(end_opacity)
        self.overlay_anim.start()

    def fade_whole_window(self, end_opacity=0.0, duration_ms=1100):
        self.window_anim = QPropertyAnimation(self, b"windowOpacity")
        self.window_anim.setDuration(duration_ms)
        self.window_anim.setStartValue(self.windowOpacity())
        self.window_anim.setEndValue(end_opacity)
        self.window_anim.start()


# ---------------------------
# Main Jarvis system
# ---------------------------

class JarvisSystem:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.dev_config = parse_dev_run_config(sys.argv)
        self.boot_profile = self.dev_config["boot_profile"]
        self.audio_mode = self.dev_config["audio_mode"]
        self.runtime_log_root, self.runtime_log_file = resolve_boot_runtime_log_paths(
            self.base_dir,
            self.boot_profile,
            self.audio_mode,
        )

        self.prompt_markers_emitted = set()
        self.auto_command_pending_stages = set()
        self.desktop_settled_logged = False

        self.runtime_milestone(
            f"BOOT_MAIN|START|profile={self.boot_profile}|audio={self.audio_mode}"
        )

        self.app = QApplication(self.dev_config["qt_argv"])
        self.app.setQuitOnLastWindowClosed(False)

        self.bus = UIBus()
        self.speaker = JarvisSpeaker() if self.audio_mode == "voice" else None

        self.awaiting_stage = "boot"
        self.voice_busy = False
        self.pending_input_after_voice = False
        self.voice_anim_stop = threading.Event()
        self.voice_anim_thread = None
        self.command_lock = threading.Lock()

        self.hotkeys_pressed = set()
        self.hotkey_listener = pynput_keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

        screens = QGuiApplication.screens()
        if len(screens) < 3:
            self.runtime_milestone(f"BOOT_MAIN|TOPOLOGY_INVALID|screen_count={len(screens)}")
            print("Error: Need 3 monitors connected.")
            sys.exit(1)

        self.center_screen = QGuiApplication.primaryScreen()

        other_screens = [s for s in screens if s != self.center_screen]
        if len(other_screens) < 2:
            screens_sorted = sorted(screens, key=lambda s: s.geometry().x())
            self.left_screen = screens_sorted[0]
            self.center_screen = screens_sorted[1]
            self.right_screen = screens_sorted[2]
        else:
            other_sorted = sorted(other_screens, key=lambda s: s.geometry().x())
            self.left_screen = other_sorted[0]
            self.right_screen = other_sorted[1]

        visual_html = os.path.join(self.base_dir, "jarvis_visual", "jarvis_core.html")

        self.left_window = BootSideWindow(self.left_screen, "LEFT MODULE")
        self.boot_center_window = JarvisBootCenterWindow(self.center_screen, visual_html)
        self.desktop_center_window = DesktopVisualWindow(self.center_screen, visual_html)
        self.right_window = BootSideWindow(self.right_screen, "RIGHT MODULE")

        self.desktop_center_window.hide()

        self.bus.set_overlay_title.connect(self.boot_center_window.set_title)
        self.bus.set_overlay_status.connect(self.boot_center_window.set_status)
        self.bus.set_overlay_log.connect(self.boot_center_window.set_log)
        self.bus.append_overlay_log.connect(self.boot_center_window.append_log)
        self.bus.clear_overlay_log.connect(self.boot_center_window.clear_log)

        self.bus.set_left_body.connect(self.left_window.set_body)
        self.bus.set_right_body.connect(self.right_window.set_body)

        self.bus.set_visual_state.connect(self.set_visual_state_all)
        self.bus.set_voice_level.connect(self.set_voice_level_all)

        self.bus.show_command_input.connect(self.boot_center_window.show_command_input)
        self.bus.hide_command_input.connect(self.boot_center_window.hide_command_input)
        self.bus.clear_command_input.connect(self.boot_center_window.clear_command_input)

        self.bus.set_progress.connect(self.boot_center_window.set_progress)
        self.bus.show_progress.connect(self.boot_center_window.show_progress)
        self.bus.hide_progress.connect(self.boot_center_window.hide_progress)

        self.bus.begin_desktop_handoff.connect(self.begin_desktop_handoff)
        self.bus.shutdown_requested.connect(self.shutdown_interface)

        self.boot_center_window.command_submitted.connect(self.start_command_thread)

        for label, screen in [
            ("LEFT", self.left_screen),
            ("CENTER", self.center_screen),
            ("RIGHT", self.right_screen),
        ]:
            g = screen.geometry()
            print(f"{label}: {screen.name()} | x={g.x()} y={g.y()} w={g.width()} h={g.height()}")

        self.runtime_milestone(
            "BOOT_MAIN|TOPOLOGY_RESOLVED|"
            f"screen_count={len(screens)}|"
            f"left={screen_marker(self.left_screen)}|"
            f"center={screen_marker(self.center_screen)}|"
            f"right={screen_marker(self.right_screen)}"
        )
        self.runtime_milestone("BOOT_MAIN|WINDOWS_CONSTRUCTED")

    def set_visual_state_all(self, state_name):
        self.boot_center_window.set_visual_state(state_name)
        self.desktop_center_window.set_visual_state(state_name)

    def set_voice_level_all(self, level):
        self.boot_center_window.set_voice_level(level)
        self.desktop_center_window.set_voice_level(level)

    def on_key_press(self, key):
        self.hotkeys_pressed.add(key)
        try:
            if (
                (pynput_keyboard.Key.ctrl_l in self.hotkeys_pressed or pynput_keyboard.Key.ctrl_r in self.hotkeys_pressed)
                and
                (pynput_keyboard.Key.alt_l in self.hotkeys_pressed or pynput_keyboard.Key.alt_r in self.hotkeys_pressed)
                and
                pynput_keyboard.Key.end in self.hotkeys_pressed
            ):
                self.bus.shutdown_requested.emit()
        except Exception:
            pass

    def on_key_release(self, key):
        if key in self.hotkeys_pressed:
            self.hotkeys_pressed.remove(key)

    def shutdown_interface(self):
        self.runtime_milestone("BOOT_MAIN|SHUTDOWN_REQUESTED")
        try:
            self.hotkey_listener.stop()
        except Exception:
            pass
        self.stop_voice_visualizer()
        QApplication.quit()

    def runtime_milestone(self, event):
        if not self.runtime_log_file:
            return

        try:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            with open(self.runtime_log_file, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {event}\n")
        except Exception:
            pass

    def sleep_ms(self, ms):
        time.sleep(ms / 1000.0)

    def log_event(self, text):
        self.bus.append_overlay_log.emit(text)

    def set_status(self, text):
        self.bus.set_overlay_status.emit(text)

    def set_visual_state(self, state):
        self.bus.set_visual_state.emit(state)

    def set_voice_level(self, level):
        self.bus.set_voice_level.emit(level)

    def mark_prompt_shown(self):
        marker = ""
        if self.awaiting_stage == "command_1":
            marker = "BOOT_MAIN|FIRST_PROMPT_SHOWN"
        elif self.awaiting_stage == "command_2":
            marker = "BOOT_MAIN|IMPORT_PROMPT_SHOWN"

        if not marker or marker in self.prompt_markers_emitted:
            return

        self.prompt_markers_emitted.add(marker)
        self.runtime_milestone(marker)

    def maybe_schedule_auto_command(self):
        if self.boot_profile != "auto_handoff_skip_import":
            return

        stage = self.awaiting_stage
        command = AUTO_STAGE_COMMANDS.get(stage, "")
        if not command or stage in self.auto_command_pending_stages:
            return

        command_marker = command.replace(" ", "_")
        self.auto_command_pending_stages.add(stage)
        self.runtime_milestone(
            f"BOOT_MAIN|AUTO_COMMAND_QUEUED|stage={stage}|command={command_marker}"
        )

        def worker():
            self.sleep_ms(220)
            try:
                if self.awaiting_stage != stage or self.voice_busy:
                    return
                self.runtime_milestone(
                    f"BOOT_MAIN|AUTO_COMMAND_SUBMITTED|stage={stage}|command={command_marker}"
                )
                self.start_command_thread(command)
            finally:
                self.auto_command_pending_stages.discard(stage)

        threading.Thread(target=worker, daemon=True).start()

    def start_voice_visualizer(self, text: str):
        self.stop_voice_visualizer()
        self.voice_anim_stop.clear()

        word_count = max(1, len(text.split()))
        base_speed = 0.095 if word_count < 8 else 0.075

        def worker():
            phase = 0.0
            accent_timer = 0.0
            while not self.voice_anim_stop.is_set():
                phase += 0.34
                accent_timer += base_speed

                carrier = 0.38 + 0.22 * (0.5 + 0.5 * math.sin(phase))
                syllable = 0.18 + 0.22 * (0.5 + 0.5 * math.sin(phase * 2.7 + 1.1))
                micro = random.uniform(0.0, 0.16)

                punch = 0.0
                if accent_timer >= random.uniform(0.22, 0.55):
                    accent_timer = 0.0
                    punch = random.uniform(0.18, 0.42)

                level = min(1.0, carrier + syllable + micro + punch)
                level = max(0.06, level)

                self.set_voice_level(level)
                time.sleep(base_speed)

            for level in [0.34, 0.22, 0.12, 0.04, 0.0]:
                self.set_voice_level(level)
                time.sleep(0.03)

        self.voice_anim_thread = threading.Thread(target=worker, daemon=True)
        self.voice_anim_thread.start()

    def stop_voice_visualizer(self):
        self.voice_anim_stop.set()
        if self.voice_anim_thread and self.voice_anim_thread.is_alive():
            self.voice_anim_thread.join(timeout=0.4)
        self.voice_anim_thread = None
        self.set_voice_level(0.0)

    def run_voice(self, text, show_input_after=False):
        self.voice_busy = True
        self.pending_input_after_voice = show_input_after

        self.bus.hide_command_input.emit()

        if self.audio_mode == "quiet":
            self.runtime_milestone(f"BOOT_MAIN|VOICE_BYPASSED|stage={self.awaiting_stage}")
            self.voice_busy = False
            self.set_visual_state("idle")

            if self.pending_input_after_voice and self.awaiting_stage != "complete":
                self.sleep_ms(80)
                self.bus.show_command_input.emit()
                self.mark_prompt_shown()
                self.maybe_schedule_auto_command()

            self.pending_input_after_voice = False
            return

        self.set_visual_state("speaking")
        self.start_voice_visualizer(text)
        self.runtime_milestone(f"BOOT_MAIN|VOICE_STARTED|stage={self.awaiting_stage}")

        try:
            asyncio.run(self.speaker.speak(text))
        finally:
            self.stop_voice_visualizer()
            self.voice_busy = False
            self.set_visual_state("idle")
            self.runtime_milestone(f"BOOT_MAIN|VOICE_COMPLETED|stage={self.awaiting_stage}")

            if self.pending_input_after_voice and self.awaiting_stage != "complete":
                self.sleep_ms(180)
                self.bus.show_command_input.emit()
                self.mark_prompt_shown()
                self.maybe_schedule_auto_command()

            self.pending_input_after_voice = False

    def animate_progress_to(self, target, duration_ms=500):
        current = self.boot_center_window.progress.value()
        steps = 18
        delta = max(1, int((target - current) / max(1, steps)))
        if current >= target:
            self.bus.set_progress.emit(target)
            return

        value = current
        while value < target:
            value = min(target, value + delta)
            self.bus.set_progress.emit(value)
            self.sleep_ms(max(10, duration_ms // steps))

    def stage_hud_subroutines(self):
        left_lines = []
        right_lines = []

        staged_updates = [
            ("HUD LINK ........... ACTIVE", "HUD LINK ........... ACTIVE"),
            ("LEFT MODULE ........ STAGING", "RIGHT MODULE ....... STAGING"),
            ("TELEMETRY BUS ...... INITIALIZING", "STATUS BUS ......... INITIALIZING"),
            ("DISPLAY ROUTING .... PREPARING", "DISPLAY ROUTING .... PREPARING"),
            ("STATE .............. AWAITING CONFIRMATION", "STATE .............. AWAITING CONFIRMATION"),
        ]

        for left_text, right_text in staged_updates:
            left_lines.append(left_text)
            right_lines.append(right_text)

            self.bus.set_left_body.emit("\n".join(left_lines))
            self.bus.set_right_body.emit("\n".join(right_lines))
            self.sleep_ms(300)

    def boot_sequence(self):
        self.awaiting_stage = "boot"
        self.runtime_milestone("BOOT_MAIN|BOOT_SEQUENCE_START")

        self.set_visual_state("boot")
        self.bus.set_overlay_title.emit("Installing Jarvis")
        self.set_status("PREPARING INSTALLATION")
        self.bus.set_overlay_log.emit("")
        self.bus.show_progress.emit()
        self.bus.set_progress.emit(0)
        self.set_voice_level(0.0)

        self.bus.set_left_body.emit("")
        self.bus.set_right_body.emit("")

        install_steps = [
            (8,  "Allocating core memory"),
            (16, "Installing Jarvis kernel"),
            (24, "Registering voice interface"),
            (34, "Binding command parser"),
            (46, "Initializing cinematic core"),
            (58, "Connecting primary display"),
            (70, "Loading orchestration layer"),
            (82, "Preparing module launch hooks"),
            (92, "Finalizing installation"),
            (100, "Installation complete"),
        ]

        for value, text in install_steps:
            self.set_status(text)
            self.log_event(f"> {text}")
            self.animate_progress_to(value, duration_ms=420)
            self.sleep_ms(500)

        self.sleep_ms(500)

        self.bus.set_overlay_title.emit("JARVIS")
        self.set_status("COMING ONLINE")
        self.log_event("")
        self.log_event("> Jarvis installation verified")
        self.log_event("> Bringing primary intelligence core online")

        online_steps = [
            "Loading voice engine",
            "Loading visual runtime",
            "Loading desktop handoff layer",
            "Loading future module controller",
            "Loading center monitor core scene",
        ]

        for step in online_steps:
            self.log_event(f"> {step}")
            self.sleep_ms(420)

        self.sleep_ms(700)

        self.bus.hide_progress.emit()
        self.set_status("ONLINE")

        self.awaiting_stage = "command_1"
        self.set_status("AWAITING COMMAND")
        self.set_visual_state("idle")
        self.run_voice("Hello Sir, I am now online. What can I do for you?", show_input_after=True)

    def start_command_thread(self, text):
        if not self.command_lock.acquire(blocking=False):
            return
        threading.Thread(target=self._command_worker, args=(text,), daemon=True).start()

    def _command_worker(self, text):
        try:
            self.handle_command(text)
        finally:
            self.command_lock.release()

    def handle_command(self, text):
        user_input = text.strip().lower()
        self.bus.clear_command_input.emit()

        if self.voice_busy:
            return

        if self.awaiting_stage == "command_1":
            if user_input in {"engage hud", "engage heads up display"}:
                self.runtime_milestone("BOOT_MAIN|FIRST_COMMAND_ACCEPTED|command=engage_hud")
                self.awaiting_stage = "command_2"
                self.set_status("CONFIRM IMPORT")
                self.log_event("> Heads up display request accepted")
                self.log_event("> Initializing HUD subroutines")
                self.log_event("> Awaiting home interface import confirmation")

                self.stage_hud_subroutines()

                self.run_voice("Would you like me to import your home preferences?", show_input_after=True)

            elif user_input == "shutdown interface":
                self.run_voice("Understood. Shutting down interface.")
                self.bus.shutdown_requested.emit()

            else:
                self.run_voice("Command not recognized.", show_input_after=True)
                self.set_status("AWAITING COMMAND")

        elif self.awaiting_stage == "command_2":
            if user_input in {"yes", "yes sir", "affirmative"}:
                self.runtime_milestone("BOOT_MAIN|IMPORT_CHOICE_RESOLVED|choice=import_home")
                self.awaiting_stage = "complete"
                self.bus.hide_command_input.emit()
                self.run_voice("Importing home preferences.")
                self.transition_to_hud(import_home=True)

            elif user_input in {"no", "negative"}:
                self.runtime_milestone("BOOT_MAIN|IMPORT_CHOICE_RESOLVED|choice=skip")
                self.awaiting_stage = "complete"
                self.bus.hide_command_input.emit()
                self.run_voice("Proceeding without home preferences.")
                self.transition_to_hud(import_home=False)

            elif user_input == "shutdown interface":
                self.run_voice("Understood. Shutting down interface.")
                self.bus.shutdown_requested.emit()

            else:
                self.set_status("CONFIRM IMPORT")
                self.run_voice("Please answer yes or no.", show_input_after=True)

    def transition_to_hud(self, import_home=True):
        import_marker = "true" if import_home else "false"
        self.runtime_milestone(f"BOOT_MAIN|TRANSITION_BEGIN|import_home={import_marker}")
        self.set_status("ENGAGING HEADS UP DISPLAY")
        self.set_visual_state("processing")

        self.log_event("> Preparing desktop handoff")
        self.log_event("> Preserving center monitor Jarvis core")
        self.log_event("> Initializing compact desktop background core")
        self.log_event("> Left and right displays reserved for external modules")
        self.sleep_ms(550)

        if import_home:
            self.log_event("> Home preferences imported")
        else:
            self.log_event("> Home preferences skipped")

        self.bus.set_left_body.emit(
            "LEFT MODULE ....... RESERVED\n"
            "TARGET ROLE ....... TELEMETRY / SENSORS\n"
            "APP OWNER ......... FUTURE EXTERNAL MODULE\n"
            "STATE ............. READY"
        )

        self.bus.set_right_body.emit(
            "RIGHT MODULE ...... RESERVED\n"
            "TARGET ROLE ....... STATUS / SENSOR WALL\n"
            "APP OWNER ......... FUTURE EXTERNAL MODULE\n"
            "STATE ............. READY"
        )

        self.sleep_ms(250)
        self.log_event("> Desktop handoff complete")
        self.log_event("> Center Jarvis core stabilizing into desktop mode")
        self.sleep_ms(120)

        self.bus.begin_desktop_handoff.emit()

    def begin_desktop_handoff(self):
        desktop_reveal_delay_ms = 140
        desktop_state_commit_delay_ms = 220
        desktop_settle_delay_ms = desktop_reveal_delay_ms + desktop_state_commit_delay_ms + 320

        self.desktop_center_window.prepare_desktop_geometry()
        self.desktop_center_window.setWindowOpacity(1.0)
        self.desktop_center_window.show()
        self.desktop_center_window.set_voice_level(0.0)
        self.runtime_milestone("BOOT_MAIN|DESKTOP_SHOWN")

        self.desktop_center_window.enable_desktop_mode()
        self.reinforce_desktop_mode()
        QTimer.singleShot(300, self.reinforce_desktop_mode)
        QTimer.singleShot(900, self.reinforce_desktop_mode)
        QTimer.singleShot(2200, self.reinforce_desktop_mode)
        QTimer.singleShot(5000, self.reinforce_desktop_mode)
        QTimer.singleShot(desktop_settle_delay_ms, self.mark_desktop_settled)

        self.boot_center_window.enter_background_visual_mode()
        self.boot_center_window.fade_overlay(end_opacity=0.0, duration_ms=260)

        self.left_anim = QPropertyAnimation(self.left_window, b"windowOpacity")
        self.left_anim.setDuration(500)
        self.left_anim.setStartValue(self.left_window.windowOpacity())
        self.left_anim.setEndValue(0.0)
        self.left_anim.start()

        self.right_anim = QPropertyAnimation(self.right_window, b"windowOpacity")
        self.right_anim.setDuration(500)
        self.right_anim.setStartValue(self.right_window.windowOpacity())
        self.right_anim.setEndValue(0.0)
        self.right_anim.start()

        QTimer.singleShot(
            desktop_reveal_delay_ms,
            lambda: self.complete_desktop_visual_handoff(
                desktop_state_commit_delay_ms,
            ),
        )

    def complete_desktop_visual_handoff(self, state_commit_delay_ms=220):
        self.boot_center_window.hide()
        self.left_window.hide()
        self.right_window.hide()
        self.runtime_milestone("BOOT_MAIN|BOOT_WINDOWS_HIDDEN")
        self.desktop_center_window.setWindowOpacity(1.0)
        self.runtime_milestone("BOOT_MAIN|DESKTOP_VISIBLE")
        QTimer.singleShot(state_commit_delay_ms, self.commit_desktop_state)

    def commit_desktop_state(self):
        self.desktop_center_window.set_visual_state("dormant")
        self.runtime_milestone("BOOT_MAIN|DESKTOP_STATE_COMMITTED|state=dormant")

    def reinforce_desktop_mode(self):
        hwnd = int(self.desktop_center_window.winId())
        attach_window_to_desktop(hwnd)
        make_window_noninteractive(hwnd)
        self.desktop_center_window.lower()

    def mark_desktop_settled(self):
        if self.desktop_settled_logged:
            return
        self.desktop_settled_logged = True
        self.runtime_milestone("BOOT_MAIN|DESKTOP_SETTLED|state=dormant")

    def start(self):
        self.left_window.show()
        self.boot_center_window.show()
        self.right_window.show()
        self.runtime_milestone("BOOT_MAIN|WINDOWS_SHOWN")

        self.boot_center_window.set_title("JARVIS")
        self.boot_center_window.set_status("BOOTING")
        self.boot_center_window.set_log("")
        self.boot_center_window.set_visual_state("boot")
        self.boot_center_window.set_voice_level(0.0)

        self.desktop_center_window.set_visual_state("dormant")
        self.desktop_center_window.set_voice_level(0.0)

        QTimer.singleShot(500, self.start_boot_thread)

        exit_code = self.app.exec()
        self.runtime_milestone(f"BOOT_MAIN|EVENT_LOOP_EXIT|code={exit_code}")
        return exit_code

    def start_boot_thread(self):
        threading.Thread(target=self.boot_sequence, daemon=True).start()


if __name__ == "__main__":
    jarvis = JarvisSystem()
    raise SystemExit(jarvis.start())
