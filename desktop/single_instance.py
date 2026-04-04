import atexit
import ctypes
import time
from ctypes import wintypes


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
MB_ICONINFORMATION = 0x00000040
MB_ICONQUESTION = 0x00000020
IDYES = 6
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258


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


def show_already_running_dialog(title: str, message: str) -> None:
    try:
        MessageBoxW(None, message, title, MB_OK | MB_ICONINFORMATION)
    except Exception:
        pass


def show_replace_running_dialog(title: str, message: str) -> bool:
    try:
        result = MessageBoxW(None, message, title, MB_YESNO | MB_ICONQUESTION)
        return result == IDYES
    except Exception:
        return False


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
) -> bool:
    if guard.acquire():
        relaunch_signal.clear()
        return True

    if not show_replace_running_dialog(title, message):
        return False

    if not relaunch_signal.signal():
        show_already_running_dialog(
            title,
            "Jarvis could not signal the current instance to close. Please close it manually and try again.",
        )
        return False

    deadline = time.time() + max(0.5, wait_seconds)
    while time.time() < deadline:
        if guard.acquire():
            relaunch_signal.clear()
            return True
        time.sleep(max(0.05, poll_interval_seconds))

    show_already_running_dialog(
        title,
        "Jarvis is still closing. Please wait a moment and try again.",
    )
    return False
