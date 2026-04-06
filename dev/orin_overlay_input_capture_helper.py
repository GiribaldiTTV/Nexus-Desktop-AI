import os
import sys
import time
from types import SimpleNamespace

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import desktop.desktop_renderer as renderer_mod
from desktop.interaction_overlay_model import CommandOverlayModel


class _FakeRect:
    def __init__(self, x=0, y=0, width=1280, height=720):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def x(self):
        return self._x

    def y(self):
        return self._y

    def width(self):
        return self._width

    def height(self):
        return self._height


class _FakeTimer:
    def __init__(self):
        self.started_with = None

    def stop(self):
        self.started_with = None

    def start(self, duration_ms):
        self.started_with = duration_ms


class _FakeInputLine:
    def __init__(self):
        self.focused = False

    def hasFocus(self):
        return self.focused


class _FakePanel:
    def __init__(self):
        self.input_line = _FakeInputLine()
        self.active = False
        self.visible = False
        self.last_payload = None

    def render_payload(self, payload):
        self.last_payload = payload

    def show_for_geometry(self, *_args, **_kwargs):
        self.visible = True

    def focus_input_after_show(self):
        return None

    def focus_input(self, *_args, **_kwargs):
        self.active = True
        self.input_line.focused = True

    def isActiveWindow(self):
        return self.active

    def hide(self):
        self.visible = False

    def setFocus(self, *_args, **_kwargs):
        self.active = True


def _make_window():
    window = renderer_mod.DesktopRuntimeWindow.__new__(renderer_mod.DesktopRuntimeWindow)
    window.screen_ref = SimpleNamespace(availableGeometry=lambda: _FakeRect())
    window.compute_compact_geometry = lambda: _FakeRect()
    window._is_shutting_down = False
    window._command_model = CommandOverlayModel()
    window._command_panel = _FakePanel()
    window._result_close_timer = _FakeTimer()
    window._overlay_input_capture_until = 0.0
    window._overlay_local_input_engaged = False
    window._log_event = lambda *_args, **_kwargs: None
    window._apply_command_overlay_state = lambda: window._command_panel.render_payload(
        window._command_model.view_payload()
    )
    window._show_command_result = lambda kind, text: (
        window._command_model.show_result(kind, text),
        window._apply_command_overlay_state(),
    )
    return window


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _test_first_open_capture_allows_typing():
    window = _make_window()
    window.open_command_overlay()
    _assert(window.overlay_needs_global_input_capture(), "capture should arm on first open")
    window.handle_overlay_text_requested("o")
    _assert(window._command_model.input_text == "o", "first typed character should reach the overlay")


def _test_active_panel_without_input_focus_still_uses_capture():
    window = _make_window()
    window.open_command_overlay()
    window._command_panel.active = True
    window._command_panel.input_line.focused = False
    _assert(
        window.overlay_needs_global_input_capture(),
        "entry capture should stay on when the panel is active but the input line still lacks focus",
    )


def _test_local_focus_clears_capture_and_stops_mirroring():
    window = _make_window()
    window.open_command_overlay()
    window._command_panel.active = True
    window._command_panel.input_line.focused = True
    window.handle_command_input_focus_acquired()
    _assert(
        not window.overlay_needs_global_input_capture(),
        "capture should stand down once the panel really owns active focused input",
    )
    window._command_panel.active = False
    window._command_panel.input_line.focused = False
    _assert(
        not window.overlay_needs_global_input_capture(),
        "capture should stay off after focus leaves a real local-input session",
    )
    before = window._command_model.input_text
    window.handle_overlay_text_requested("x")
    _assert(
        window._command_model.input_text == before,
        "typing elsewhere should no longer mirror into the overlay after focus loss",
    )


def _test_reopen_rearms_capture():
    window = _make_window()
    window.open_command_overlay()
    window._command_panel.active = True
    window._command_panel.input_line.focused = True
    window.handle_command_input_focus_acquired()
    window._command_panel.active = False
    window._command_panel.input_line.focused = False
    window.close_command_overlay()
    window.open_command_overlay()
    _assert(window.overlay_needs_global_input_capture(), "reopen should arm a fresh capture session")


def _test_ambiguous_choose_confirm_execute_path():
    window = _make_window()
    launches = []
    original_launch = renderer_mod.launch_command_action
    renderer_mod.launch_command_action = lambda action: launches.append((action.id, action.target))
    try:
        window.open_command_overlay()
        for char in "open nexus folder":
            window.handle_overlay_text_requested(char)
        window.handle_overlay_submit_requested()
        _assert(window._command_model.phase == "choose", "open nexus folder should enter choose state")
        window.handle_overlay_text_requested("2")
        _assert(window._command_model.phase == "confirm", "digit choice should enter confirm state")
        window.handle_overlay_submit_requested()
        _assert(
            launches and launches[0][0] == "open_jarvis_docs",
            "confirm path should launch the selected docs action",
        )
    finally:
        renderer_mod.launch_command_action = original_launch


def _test_capture_expiry_stands_down_fallback():
    window = _make_window()
    window.open_command_overlay()
    window._overlay_input_capture_until = time.monotonic() - 0.01
    _assert(not window.overlay_needs_global_input_capture(), "expired capture session should not keep forwarding keys")


def main():
    tests = [
        ("first-open capture", _test_first_open_capture_allows_typing),
        ("entry capture while input lacks focus", _test_active_panel_without_input_focus_still_uses_capture),
        ("local focus clears mirroring", _test_local_focus_clears_capture_and_stops_mirroring),
        ("reopen rearms capture", _test_reopen_rearms_capture),
        ("choose-confirm execute path", _test_ambiguous_choose_confirm_execute_path),
        ("capture expiry", _test_capture_expiry_stands_down_fallback),
    ]

    for name, fn in tests:
        fn()
        print(f"PASS: {name}")

    print("OVERLAY INPUT HELPER: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
