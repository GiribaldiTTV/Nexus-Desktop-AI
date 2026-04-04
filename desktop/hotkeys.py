import os
from PySide6.QtCore import QObject, Signal
from pynput import keyboard as pynput_keyboard


class ShutdownBus(QObject):
    shutdown_requested = Signal()
    command_overlay_toggle_requested = Signal()
    command_character_typed = Signal(str)
    command_backspace_requested = Signal()
    command_enter_requested = Signal()
    command_escape_requested = Signal()


class GlobalHotkeyManager:
    def __init__(self, bus: ShutdownBus):
        self.bus = bus
        self._listener = None
        self._pressed = set()
        self._shutdown_fired = False
        self._overlay_toggle_fired = False
        self._command_mode_active = False

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
        self._command_mode_active = False

    def force_kill(self) -> None:
        os._exit(0)

    def set_command_mode_active(self, active: bool) -> None:
        self._command_mode_active = bool(active)

    def _on_press(self, key) -> None:
        self._pressed.add(key)
        ctrl_down = pynput_keyboard.Key.ctrl_l in self._pressed or pynput_keyboard.Key.ctrl_r in self._pressed
        alt_down = (
            pynput_keyboard.Key.alt_l in self._pressed
            or pynput_keyboard.Key.alt_r in self._pressed
            or pynput_keyboard.Key.alt_gr in self._pressed
        )
        end_down = key == pynput_keyboard.Key.end
        home_down = key == pynput_keyboard.Key.home

        if ctrl_down and alt_down and end_down and not self._shutdown_fired:
            self._shutdown_fired = True
            self.bus.shutdown_requested.emit()
            return

        if ctrl_down and alt_down and home_down and not self._overlay_toggle_fired:
            self._overlay_toggle_fired = True
            self.bus.command_overlay_toggle_requested.emit()
            return

        if not self._command_mode_active or ctrl_down or alt_down:
            return

        if key == pynput_keyboard.Key.esc:
            self.bus.command_escape_requested.emit()
            return

        if key == pynput_keyboard.Key.enter:
            self.bus.command_enter_requested.emit()
            return

        if key == pynput_keyboard.Key.backspace:
            self.bus.command_backspace_requested.emit()
            return

        if key == pynput_keyboard.Key.space:
            self.bus.command_character_typed.emit(" ")
            return

        char = getattr(key, "char", None)
        if isinstance(char, str) and char.isprintable():
            self.bus.command_character_typed.emit(char)

    def _on_release(self, key) -> None:
        self._pressed.discard(key)
        if key in (
            pynput_keyboard.Key.end,
            pynput_keyboard.Key.home,
            pynput_keyboard.Key.ctrl_l,
            pynput_keyboard.Key.ctrl_r,
            pynput_keyboard.Key.alt_l,
            pynput_keyboard.Key.alt_r,
            pynput_keyboard.Key.alt_gr,
        ):
            self._shutdown_fired = False
            self._overlay_toggle_fired = False
