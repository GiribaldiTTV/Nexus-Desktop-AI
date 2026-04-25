import os
import time
from PySide6.QtCore import QObject, Signal
from pynput import keyboard as pynput_keyboard, mouse as pynput_mouse


class ShutdownBus(QObject):
    shutdown_requested = Signal()
    command_overlay_toggle_requested = Signal()
    command_overlay_text_requested = Signal(str)
    command_overlay_backspace_requested = Signal()
    command_overlay_submit_requested = Signal()
    command_overlay_escape_requested = Signal()
    command_overlay_global_click_requested = Signal(int, int)


class GlobalHotkeyManager:
    _WM_KEYDOWN = 0x0100
    _WM_KEYUP = 0x0101
    _WM_SYSKEYDOWN = 0x0104
    _WM_SYSKEYUP = 0x0105
    _MODIFIER_VKS = {
        0x10,  # Shift
        0x11,  # Ctrl
        0x12,  # Alt
        0x5B,  # Left Windows
        0x5C,  # Right Windows
    }
    _SUPPRESSED_TEXT_VKS = set(range(0x30, 0x3A)) | set(range(0x41, 0x5B)) | {
        0x20,  # Space
        0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69,  # Numpad 0-9
        0x6A, 0x6B, 0x6D, 0x6E, 0x6F,  # Numpad operators
        0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF, 0xC0,  # Common OEM punctuation
        0xDB, 0xDC, 0xDD, 0xDE,
    }

    def __init__(self, bus: ShutdownBus):
        self.bus = bus
        self._listener = None
        self._mouse_listener = None
        self._pressed = set()
        self._shutdown_fired = False
        self._overlay_toggle_fired = False
        self._overlay_digit_chars = {"1"}
        self._overlay_digit_vks = {49}
        self._shutdown_digit_chars = {"2"}
        self._shutdown_digit_vks = {50}
        self._overlay_input_enabled_provider = lambda: False
        self._overlay_launch_grace_allowed_provider = lambda: True
        self._overlay_click_monitor_provider = lambda: False
        self._overlay_launch_grace_until = 0.0
        self._debug_logger = None

    def start(self) -> None:
        if self._listener is not None:
            return
        self._listener = pynput_keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            win32_event_filter=self._win32_event_filter,
        )
        self._listener.start()
        self._mouse_listener = pynput_mouse.Listener(on_click=self._on_click)
        self._mouse_listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            listener = self._listener
            listener.stop()
            try:
                listener.join(timeout=1.0)
            except Exception:
                pass
            self._listener = None
        if self._mouse_listener is not None:
            mouse_listener = self._mouse_listener
            mouse_listener.stop()
            try:
                mouse_listener.join(timeout=1.0)
            except Exception:
                pass
            self._mouse_listener = None
        self._pressed.clear()
        self._shutdown_fired = False
        self._overlay_toggle_fired = False
        self._overlay_launch_grace_until = 0.0

    def force_kill(self) -> None:
        os._exit(0)

    def set_overlay_input_enabled_provider(self, provider) -> None:
        self._overlay_input_enabled_provider = provider if callable(provider) else (lambda: False)

    def set_overlay_launch_grace_allowed_provider(self, provider) -> None:
        self._overlay_launch_grace_allowed_provider = provider if callable(provider) else (lambda: True)

    def set_overlay_click_monitor_provider(self, provider) -> None:
        self._overlay_click_monitor_provider = provider if callable(provider) else (lambda: False)

    def set_debug_logger(self, logger) -> None:
        self._debug_logger = logger if callable(logger) else None

    def _ctrl_down(self) -> bool:
        return pynput_keyboard.Key.ctrl_l in self._pressed or pynput_keyboard.Key.ctrl_r in self._pressed

    def _alt_down(self) -> bool:
        return (
            pynput_keyboard.Key.alt_l in self._pressed
            or pynput_keyboard.Key.alt_r in self._pressed
            or pynput_keyboard.Key.alt_gr in self._pressed
        )

    def _key_char(self, key):
        char = getattr(key, "char", None)
        if isinstance(char, str):
            return char.lower()
        return None

    def _key_vk(self, key):
        return getattr(key, "vk", None)

    def _key_matches_overlay_trigger(self, key) -> bool:
        if key == pynput_keyboard.Key.home:
            return True
        return self._key_char(key) in self._overlay_digit_chars or self._key_vk(key) in self._overlay_digit_vks

    def _key_matches_shutdown_trigger(self, key) -> bool:
        if key == pynput_keyboard.Key.end:
            return True
        return self._key_char(key) in self._shutdown_digit_chars or self._key_vk(key) in self._shutdown_digit_vks

    def _overlay_key_down(self) -> bool:
        return any(self._key_matches_overlay_trigger(key) for key in self._pressed)

    def _shutdown_key_down(self) -> bool:
        return any(self._key_matches_shutdown_trigger(key) for key in self._pressed)

    def _log_debug(self, event: str) -> None:
        if not callable(self._debug_logger):
            return
        try:
            self._debug_logger(f"OVERLAY_TRACE|source=hotkeys|{event}")
        except Exception:
            pass

    def _overlay_input_debug_state(self):
        try:
            provider_enabled = bool(self._overlay_input_enabled_provider())
        except Exception:
            provider_enabled = False
        try:
            grace_allowed = bool(self._overlay_launch_grace_allowed_provider())
        except Exception:
            grace_allowed = True
        grace_active = time.monotonic() < self._overlay_launch_grace_until
        enabled = provider_enabled or (grace_allowed and grace_active)
        return enabled, provider_enabled, grace_allowed, grace_active

    def _overlay_input_enabled(self) -> bool:
        enabled, _provider_enabled, _grace_allowed, _grace_active = self._overlay_input_debug_state()
        return enabled

    def _overlay_click_monitor_enabled(self) -> bool:
        try:
            return bool(self._overlay_click_monitor_provider())
        except Exception:
            return False

    def _overlay_text_from_key(self, key):
        if key == pynput_keyboard.Key.space:
            return " "
        char = self._key_char(key)
        if isinstance(char, str) and char.isprintable() and char:
            return char
        return None

    def _overlay_key_should_be_suppressed(self, key) -> bool:
        enabled, _provider_enabled, _grace_allowed, _grace_active = self._overlay_input_debug_state()
        if not enabled or self._ctrl_down() or self._alt_down():
            return False

        if key in (pynput_keyboard.Key.enter, pynput_keyboard.KeyCode.from_vk(13)):
            return True

        if key in (pynput_keyboard.Key.esc, pynput_keyboard.Key.backspace):
            return True

        return bool(self._overlay_text_from_key(key))

    def _overlay_vk_should_be_suppressed(self, vk: int) -> bool:
        enabled, _provider_enabled, _grace_allowed, _grace_active = self._overlay_input_debug_state()
        if not enabled or self._ctrl_down() or self._alt_down():
            return False

        if vk in self._MODIFIER_VKS:
            return False

        if vk in (0x0D, 0x1B, 0x08):
            return True

        return vk in self._SUPPRESSED_TEXT_VKS

    def _forward_overlay_submit(self, provider_enabled: bool, grace_allowed: bool, grace_active: bool, origin: str) -> None:
        self._log_debug(
            "event=submit_forwarded"
            f"|provider_enabled={'true' if provider_enabled else 'false'}"
            f"|grace_allowed={'true' if grace_allowed else 'false'}"
            f"|grace_active={'true' if grace_active else 'false'}"
            "|suppressed=true"
            f"|origin={origin}"
        )
        self.bus.command_overlay_submit_requested.emit()

    def _win32_event_filter(self, msg, data):
        if msg not in (
            self._WM_KEYDOWN,
            self._WM_KEYUP,
            self._WM_SYSKEYDOWN,
            self._WM_SYSKEYUP,
        ):
            return True

        listener = self._listener
        if listener is None:
            return True

        vk = int(getattr(data, "vkCode", 0) or 0)
        enabled, provider_enabled, grace_allowed, grace_active = self._overlay_input_debug_state()
        suppress_vk = enabled and not self._ctrl_down() and not self._alt_down() and self._overlay_vk_should_be_suppressed(vk)

        if msg in (self._WM_KEYDOWN, self._WM_SYSKEYDOWN) and suppress_vk and vk == 0x0D:
            try:
                listener._suppress = True
            except Exception:
                return True
            self._forward_overlay_submit(provider_enabled, grace_allowed, grace_active, origin="win32_filter")
            return False

        if not suppress_vk:
            try:
                listener._suppress = False
            except Exception:
                pass
            return True

        try:
            listener._suppress = True
        except Exception:
            return True
        return True

    def _on_press(self, key) -> None:
        self._pressed.add(key)
        suppress_current = self._overlay_key_should_be_suppressed(key)
        ctrl_down = self._ctrl_down()
        alt_down = self._alt_down()
        shutdown_down = self._key_matches_shutdown_trigger(key)
        overlay_down = self._key_matches_overlay_trigger(key)

        if ctrl_down and alt_down and shutdown_down and not self._shutdown_fired:
            self._shutdown_fired = True
            self._log_debug("event=shutdown_hotkey")
            self.bus.shutdown_requested.emit()
            return

        if ctrl_down and alt_down and overlay_down and not self._overlay_toggle_fired:
            self._overlay_toggle_fired = True
            self._overlay_launch_grace_until = time.monotonic() + 0.45
            self._log_debug("event=overlay_toggle_hotkey")
            self.bus.command_overlay_toggle_requested.emit()
            return

        enabled, provider_enabled, grace_allowed, grace_active = self._overlay_input_debug_state()
        if ctrl_down or alt_down or not enabled:
            return

        if key in (pynput_keyboard.Key.enter, pynput_keyboard.KeyCode.from_vk(13)):
            self._log_debug(
                "event=submit_forwarded"
                f"|provider_enabled={'true' if provider_enabled else 'false'}"
                f"|grace_allowed={'true' if grace_allowed else 'false'}"
                f"|grace_active={'true' if grace_active else 'false'}"
                f"|suppressed={'true' if suppress_current else 'false'}"
                "|origin=callback"
            )
            self.bus.command_overlay_submit_requested.emit()
            return

        if key == pynput_keyboard.Key.esc:
            self._log_debug(
                "event=escape_forwarded"
                f"|provider_enabled={'true' if provider_enabled else 'false'}"
                f"|grace_allowed={'true' if grace_allowed else 'false'}"
                f"|grace_active={'true' if grace_active else 'false'}"
                f"|suppressed={'true' if suppress_current else 'false'}"
            )
            self.bus.command_overlay_escape_requested.emit()
            return

        if key == pynput_keyboard.Key.backspace:
            self._log_debug(
                "event=backspace_forwarded"
                f"|provider_enabled={'true' if provider_enabled else 'false'}"
                f"|grace_allowed={'true' if grace_allowed else 'false'}"
                f"|grace_active={'true' if grace_active else 'false'}"
                f"|suppressed={'true' if suppress_current else 'false'}"
            )
            self.bus.command_overlay_backspace_requested.emit()
            return

        text = self._overlay_text_from_key(key)
        if text:
            self._log_debug(
                "event=text_forwarded"
                f"|text={repr(text)}"
                f"|provider_enabled={'true' if provider_enabled else 'false'}"
                f"|grace_allowed={'true' if grace_allowed else 'false'}"
                f"|grace_active={'true' if grace_active else 'false'}"
                f"|suppressed={'true' if suppress_current else 'false'}"
            )
            self.bus.command_overlay_text_requested.emit(text)

    def _on_release(self, key) -> None:
        self._pressed.discard(key)
        if (
            self._key_matches_shutdown_trigger(key)
            or self._key_matches_overlay_trigger(key)
            or key in (
                pynput_keyboard.Key.ctrl_l,
                pynput_keyboard.Key.ctrl_r,
                pynput_keyboard.Key.alt_l,
                pynput_keyboard.Key.alt_r,
                pynput_keyboard.Key.alt_gr,
            )
        ):
            if not (self._ctrl_down() and self._alt_down() and self._shutdown_key_down()):
                self._shutdown_fired = False
            if not (self._ctrl_down() and self._alt_down() and self._overlay_key_down()):
                self._overlay_toggle_fired = False

    def _on_click(self, x, y, button, pressed) -> None:
        if not pressed:
            return
        if button not in (pynput_mouse.Button.left, pynput_mouse.Button.right):
            return
        if not self._overlay_click_monitor_enabled():
            return
        self._log_debug(f"event=global_click|x={int(x)}|y={int(y)}")
        self.bus.command_overlay_global_click_requested.emit(int(x), int(y))
