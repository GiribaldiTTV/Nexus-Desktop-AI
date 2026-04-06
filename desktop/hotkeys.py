import os
from PySide6.QtCore import QObject, Signal
from pynput import keyboard as pynput_keyboard


class ShutdownBus(QObject):
    shutdown_requested = Signal()
    command_overlay_toggle_requested = Signal()


class GlobalHotkeyManager:
    def __init__(self, bus: ShutdownBus):
        self.bus = bus
        self._listener = None
        self._pressed = set()
        self._shutdown_fired = False
        self._overlay_toggle_fired = False
        self._overlay_keys = {
            pynput_keyboard.Key.home,
            pynput_keyboard.KeyCode.from_char("1"),
        }
        self._shutdown_keys = {
            pynput_keyboard.Key.end,
            pynput_keyboard.KeyCode.from_char("2"),
        }

    def start(self) -> None:
        if self._listener is not None:
            return
        self._listener = pynput_keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        self._pressed.clear()
        self._shutdown_fired = False
        self._overlay_toggle_fired = False

    def force_kill(self) -> None:
        os._exit(0)

    def _ctrl_down(self) -> bool:
        return pynput_keyboard.Key.ctrl_l in self._pressed or pynput_keyboard.Key.ctrl_r in self._pressed

    def _alt_down(self) -> bool:
        return (
            pynput_keyboard.Key.alt_l in self._pressed
            or pynput_keyboard.Key.alt_r in self._pressed
            or pynput_keyboard.Key.alt_gr in self._pressed
        )

    def _overlay_key_down(self) -> bool:
        return any(key in self._pressed for key in self._overlay_keys)

    def _shutdown_key_down(self) -> bool:
        return any(key in self._pressed for key in self._shutdown_keys)

    def _on_press(self, key) -> None:
        self._pressed.add(key)
        ctrl_down = self._ctrl_down()
        alt_down = self._alt_down()
        shutdown_down = key in self._shutdown_keys
        overlay_down = key in self._overlay_keys

        if ctrl_down and alt_down and shutdown_down and not self._shutdown_fired:
            self._shutdown_fired = True
            self.bus.shutdown_requested.emit()
            return

        if ctrl_down and alt_down and overlay_down and not self._overlay_toggle_fired:
            self._overlay_toggle_fired = True
            self.bus.command_overlay_toggle_requested.emit()
            return

    def _on_release(self, key) -> None:
        self._pressed.discard(key)
        if key in (
            *self._shutdown_keys,
            *self._overlay_keys,
            pynput_keyboard.Key.ctrl_l,
            pynput_keyboard.Key.ctrl_r,
            pynput_keyboard.Key.alt_l,
            pynput_keyboard.Key.alt_r,
            pynput_keyboard.Key.alt_gr,
        ):
            if not (self._ctrl_down() and self._alt_down() and self._shutdown_key_down()):
                self._shutdown_fired = False
            if not (self._ctrl_down() and self._alt_down() and self._overlay_key_down()):
                self._overlay_toggle_fired = False
