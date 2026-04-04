import atexit
import ctypes
import time
from ctypes import wintypes
from typing import Callable


kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

CreateMutexW = kernel32.CreateMutexW
CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
CreateMutexW.restype = wintypes.HANDLE

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

GetLastError = kernel32.GetLastError
GetLastError.argtypes = []
GetLastError.restype = wintypes.DWORD

CreateEventW = kernel32.CreateEventW
CreateEventW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
CreateEventW.restype = wintypes.HANDLE

SetEvent = kernel32.SetEvent
SetEvent.argtypes = [wintypes.HANDLE]
SetEvent.restype = wintypes.BOOL

ResetEvent = kernel32.ResetEvent
ResetEvent.argtypes = [wintypes.HANDLE]
ResetEvent.restype = wintypes.BOOL

WaitForSingleObject = kernel32.WaitForSingleObject
WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
WaitForSingleObject.restype = wintypes.DWORD

MessageBoxW = user32.MessageBoxW
MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
MessageBoxW.restype = ctypes.c_int

ERROR_ALREADY_EXISTS = 183
MB_OK = 0x00000000
MB_YESNO = 0x00000004
MB_SYSTEMMODAL = 0x00001000
MB_SETFOREGROUND = 0x00010000
MB_TOPMOST = 0x00040000
MB_ICONINFORMATION = 0x00000040
MB_ICONQUESTION = 0x00000020
IDYES = 6
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258


FOREGROUND_DIALOG_FLAGS = MB_SYSTEMMODAL | MB_SETFOREGROUND | MB_TOPMOST
_qt_dialog_app = None


class SingleInstanceGuard:
    def __init__(self, mutex_name: str):
        self.mutex_name = mutex_name
        self.handle = None

    def acquire(self) -> bool:
        if self.handle:
            return True

        handle = CreateMutexW(None, False, self.mutex_name)
        if not handle:
            return False

        if GetLastError() == ERROR_ALREADY_EXISTS:
            CloseHandle(handle)
            return False

        self.handle = handle
        atexit.register(self.release)
        return True

    def release(self) -> None:
        if self.handle:
            CloseHandle(self.handle)
            self.handle = None


def show_already_running_dialog(
    title: str,
    message: str,
    eyebrow_text: str = "JARVIS",
    primary_button_text: str = "Close",
) -> None:
    if _show_qt_dialog(
        title,
        message,
        confirm=False,
        eyebrow_text=eyebrow_text,
        primary_button_text=primary_button_text,
    ) is not None:
        return
    try:
        MessageBoxW(None, message, title, MB_OK | MB_ICONINFORMATION | FOREGROUND_DIALOG_FLAGS)
    except Exception:
        pass


def show_replace_running_dialog(
    title: str,
    message: str,
    eyebrow_text: str = "JARVIS",
    primary_button_text: str = "Close Current And Relaunch",
    secondary_button_text: str = "Keep Current",
) -> bool:
    qt_result = _show_qt_dialog(
        title,
        message,
        confirm=True,
        eyebrow_text=eyebrow_text,
        primary_button_text=primary_button_text,
        secondary_button_text=secondary_button_text,
    )
    if qt_result is not None:
        return qt_result
    try:
        result = MessageBoxW(None, message, title, MB_YESNO | MB_ICONQUESTION | FOREGROUND_DIALOG_FLAGS)
        return result == IDYES
    except Exception:
        return False


def _show_qt_dialog(
    title: str,
    message: str,
    confirm: bool,
    eyebrow_text: str = "JARVIS",
    primary_button_text: str = "Close Current And Relaunch",
    secondary_button_text: str = "Keep Current",
):
    try:
        from PySide6.QtCore import QTimer, Qt
        from PySide6.QtGui import QFont, QGuiApplication
        from PySide6.QtWidgets import (
            QApplication,
            QDialog,
            QFrame,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QVBoxLayout,
        )
    except Exception:
        return None

    global _qt_dialog_app

    class JarvisPromptDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.choice = False

            self.setWindowTitle(title)
            self.setModal(True)
            self.setWindowFlags(
                Qt.Dialog
                | Qt.FramelessWindowHint
                | Qt.WindowStaysOnTopHint
                | Qt.CustomizeWindowHint
            )
            self.setAttribute(Qt.WA_DeleteOnClose, True)
            self.setMinimumWidth(540)

            self.setStyleSheet(
                """
                QDialog {
                    background: #04080d;
                    color: #8df3ff;
                    border: 1px solid #0fe1ff;
                }
                QFrame#shell {
                    background: #07131b;
                    border: 1px solid #0fe1ff;
                }
                QLabel#eyebrow {
                    color: #00d8ff;
                    font-size: 13px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    border: none;
                }
                QLabel#heading {
                    color: #e8fdff;
                    font-size: 28px;
                    font-weight: 700;
                    border: none;
                }
                QLabel#detail {
                    color: #8dd9e6;
                    font-size: 15px;
                    line-height: 1.35em;
                    border: none;
                }
                QPushButton {
                    min-height: 42px;
                    padding: 0 18px;
                    border-radius: 0;
                    font-size: 14px;
                    font-weight: 700;
                }
                QPushButton#secondary {
                    color: #8df3ff;
                    background: #0a1b26;
                    border: 1px solid #0fe1ff;
                }
                QPushButton#secondary:hover {
                    background: #12303e;
                }
                QPushButton#primary {
                    color: #041017;
                    background: #0fe1ff;
                    border: 1px solid #6ff6ff;
                }
                QPushButton#primary:hover {
                    background: #6ff6ff;
                }
                """
            )

            root = QVBoxLayout(self)
            root.setContentsMargins(18, 18, 18, 18)

            shell = QFrame()
            shell.setObjectName("shell")
            shell_layout = QVBoxLayout(shell)
            shell_layout.setContentsMargins(22, 20, 22, 20)
            shell_layout.setSpacing(14)

            eyebrow = QLabel(eyebrow_text)
            eyebrow.setObjectName("eyebrow")

            heading = QLabel(title)
            heading.setObjectName("heading")
            heading.setWordWrap(True)

            detail = QLabel(message.replace("\n", "<br>"))
            detail.setObjectName("detail")
            detail.setWordWrap(True)
            detail.setTextFormat(Qt.RichText)

            shell_layout.addWidget(eyebrow)
            shell_layout.addWidget(heading)
            shell_layout.addWidget(detail)

            actions = QHBoxLayout()
            actions.setContentsMargins(0, 8, 0, 0)
            actions.setSpacing(10)
            actions.addStretch()

            if confirm:
                keep_button = QPushButton(secondary_button_text)
                keep_button.setObjectName("secondary")
                keep_button.clicked.connect(self.reject_dialog)
                actions.addWidget(keep_button)

                replace_button = QPushButton(primary_button_text)
                replace_button.setObjectName("primary")
                replace_button.clicked.connect(self.accept_dialog)
                actions.addWidget(replace_button)
            else:
                close_button = QPushButton(primary_button_text)
                close_button.setObjectName("primary")
                close_button.clicked.connect(self.accept_dialog)
                actions.addWidget(close_button)

            shell_layout.addLayout(actions)
            root.addWidget(shell)

        def showEvent(self, event):
            super().showEvent(event)
            self.raise_()
            self.activateWindow()
            try:
                user32.SetForegroundWindow(int(self.winId()))
            except Exception:
                pass

        def center_on_primary(self):
            screen = QGuiApplication.primaryScreen()
            if not screen:
                return
            geometry = screen.availableGeometry()
            self.adjustSize()
            x = geometry.x() + (geometry.width() - self.width()) // 2
            y = geometry.y() + (geometry.height() - self.height()) // 2
            self.move(x, y)

        def accept_dialog(self):
            self.choice = True
            self.accept()

        def reject_dialog(self):
            self.choice = False
            self.reject()

    app = QApplication.instance()
    if app is None:
        if _qt_dialog_app is None:
            _qt_dialog_app = QApplication([])
            _qt_dialog_app.setFont(QFont("Segoe UI", 10))
        app = _qt_dialog_app

    dialog = JarvisPromptDialog()
    dialog.center_on_primary()
    QTimer.singleShot(0, dialog.raise_)
    QTimer.singleShot(0, dialog.activateWindow)
    dialog.exec()
    result = dialog.choice if confirm else True

    return result


class NamedSignal:
    def __init__(self, signal_name: str):
        self.signal_name = signal_name
        self.handle = CreateEventW(None, True, False, self.signal_name)
        if self.handle:
            atexit.register(self.close)

    def signal(self) -> bool:
        if not self.handle:
            return False
        return bool(SetEvent(self.handle))

    def clear(self) -> bool:
        if not self.handle:
            return False
        return bool(ResetEvent(self.handle))

    def consume(self) -> bool:
        if not self.handle:
            return False

        wait_result = WaitForSingleObject(self.handle, 0)
        if wait_result != WAIT_OBJECT_0:
            return False

        ResetEvent(self.handle)
        return True

    def close(self) -> None:
        if self.handle:
            CloseHandle(self.handle)
            self.handle = None


def acquire_or_prompt_replace(
    guard: SingleInstanceGuard,
    relaunch_signal: NamedSignal,
    title: str,
    message: str,
    wait_seconds: float = 8.0,
    poll_interval_seconds: float = 0.1,
    event_logger: Callable[[str], None] | None = None,
    eyebrow_text: str = "JARVIS",
    primary_button_text: str = "Close Current And Relaunch",
    secondary_button_text: str = "Keep Current",
) -> bool:
    def log_event(event: str) -> None:
        if not callable(event_logger):
            return
        try:
            event_logger(event)
        except Exception:
            pass

    if guard.acquire():
        relaunch_signal.clear()
        log_event("SINGLE_INSTANCE_ACQUIRED")
        return True

    log_event("SINGLE_INSTANCE_CONFLICT_DETECTED")

    if not show_replace_running_dialog(
        title,
        message,
        eyebrow_text=eyebrow_text,
        primary_button_text=primary_button_text,
        secondary_button_text=secondary_button_text,
    ):
        log_event("REPLACE_PROMPT_DECLINED")
        return False

    log_event("REPLACE_PROMPT_ACCEPTED")

    if not relaunch_signal.signal():
        log_event("RELAUNCH_SIGNAL_FAILED")
        show_already_running_dialog(
            title,
            "Jarvis could not signal the current instance to close. Please close it manually and try again.",
            eyebrow_text=eyebrow_text,
            primary_button_text="Close",
        )
        return False

    log_event("RELAUNCH_SIGNAL_SENT")

    deadline = time.time() + max(0.5, wait_seconds)
    while time.time() < deadline:
        if guard.acquire():
            relaunch_signal.clear()
            log_event("RELAUNCH_ACQUIRED_AFTER_WAIT")
            return True
        time.sleep(max(0.05, poll_interval_seconds))

    log_event("RELAUNCH_WAIT_TIMEOUT")
    show_already_running_dialog(
        title,
        "Jarvis is still closing. Please wait a moment and try again.",
        eyebrow_text=eyebrow_text,
        primary_button_text="Close",
    )
    return False
