import os
import sys
from types import SimpleNamespace


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import desktop.desktop_renderer as renderer_mod
from desktop.interaction_overlay_model import CommandOverlayModel
from desktop.shared_action_model import CommandAction, CommandActionCatalog


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

    def contains(self, x, y):
        return self._x <= int(x) < (self._x + self._width) and self._y <= int(y) < (self._y + self._height)


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
        self._last_focus_was_manual = False
        self.value = ""
        self.local_typing_enabled = False

    def hasFocus(self):
        return self.focused

    def last_focus_was_manual(self):
        return self._last_focus_was_manual

    def text(self):
        return self.value

    def set_local_typing_enabled(self, enabled: bool):
        self.local_typing_enabled = bool(enabled)


class _FakePanel:
    def __init__(self):
        self.input_line = _FakeInputLine()
        self.active = False
        self.visible = False
        self.last_payload = None
        self.focus_after_show_calls = 0
        self.refresh_for_geometry_calls = 0
        self._frame_rect = _FakeRect(100, 100, 400, 220)

    def render_payload(self, payload):
        self.last_payload = payload
        self.input_line.value = payload.get("input_text", "")

    def show_for_geometry(self, *_args, **_kwargs):
        self.visible = True

    def refresh_for_geometry(self, *_args, **_kwargs):
        self.refresh_for_geometry_calls += 1

    def isVisible(self):
        return self.visible

    def focus_input_after_show(self):
        self.focus_after_show_calls += 1

    def focus_input(self, *_args, **_kwargs):
        self.active = True
        self.input_line.focused = True

    def isActiveWindow(self):
        return self.active

    def hide(self):
        self.visible = False

    def setFocus(self, *_args, **_kwargs):
        self.active = True

    def frameGeometry(self):
        return self._frame_rect


def _make_window(action_catalog: CommandActionCatalog | None = None):
    window = renderer_mod.DesktopRuntimeWindow.__new__(renderer_mod.DesktopRuntimeWindow)
    window.screen_ref = SimpleNamespace(availableGeometry=lambda: _FakeRect())
    window.compute_compact_geometry = lambda: _FakeRect()
    window._is_shutting_down = False
    window._overlay_trace_enabled = False
    window._command_model = CommandOverlayModel(action_catalog=action_catalog)
    window._command_panel = _FakePanel()
    window._result_close_timer = _FakeTimer()
    window._overlay_input_capture_until = 0.0
    window._overlay_local_input_engaged = False
    window._overlay_global_capture_suspended = False
    window._last_launch_failure_action_id = ""
    window._last_launch_failure_count = 0
    window._reported_recoverable_launch_failures = set()
    window.runtime_log_path = ""
    window._trace_overlay = lambda *_args, **_kwargs: None
    window._foreground_window_snapshot = lambda: {"hwnd": 0, "class_name": "", "title": ""}
    window._log_event = lambda *_args, **_kwargs: None
    window._apply_command_overlay_state = lambda: renderer_mod.DesktopRuntimeWindow._apply_command_overlay_state(window)
    window._show_command_result = lambda kind, text, close_delay_ms=1200: (
        window._command_model.show_result(kind, text),
        window._apply_command_overlay_state(),
        window._result_close_timer.start(max(0, int(close_delay_ms))),
    )
    return window


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _type_request(window, text: str):
    for char in text:
        window.handle_overlay_text_requested(char)


def _assert_clean_entry_baseline(window, message_prefix="overlay"):
    _assert(window._command_model.phase == "entry", f"{message_prefix} should reopen in entry phase")
    _assert(window._command_model.input_armed, f"{message_prefix} should reopen with input armed")
    _assert(window._command_model.input_text == "", f"{message_prefix} should reopen with no stale input text")
    _assert(window._command_model.last_request == "", f"{message_prefix} should reopen with no stale typed request")
    _assert(window._command_model.pending_action is None, f"{message_prefix} should reopen with no stale pending action")
    _assert(window._command_model.pending_matches == (), f"{message_prefix} should reopen with no stale pending matches")
    _assert(window._command_panel.last_payload.get("phase") == "entry", f"{message_prefix} payload should reopen in entry phase")
    _assert(window._command_panel.last_payload.get("input_text", "") == "", f"{message_prefix} payload should reopen with no stale input")
    _assert(window._command_panel.last_payload.get("typed_request", "") == "", f"{message_prefix} payload should reopen with no stale typed request")
    _assert(window._command_panel.last_payload.get("pending_action") is None, f"{message_prefix} payload should reopen with no pending action")
    _assert(window._command_panel.last_payload.get("ambiguous_matches") == [], f"{message_prefix} payload should reopen with no stale ambiguous matches")


def _test_open_starts_in_typed_first_entry_mode():
    window = _make_window()
    window.open_command_overlay()

    _assert(window._command_model.visible, "opening the overlay should make the command surface visible")
    _assert(window._command_model.phase == "entry", "opening the overlay should start in entry phase")
    _assert(window._command_model.input_armed, "opening the overlay should arm entry input")
    _assert(window.overlay_needs_global_input_capture(), "opening the overlay should allow immediate typed interaction")
    _assert(window._command_panel.focus_after_show_calls == 1, "opening the overlay should request input focus after show")
    _assert(window._command_panel.last_payload.get("typing_ready"), "opening the overlay should render typing-ready state")


def _test_not_found_stays_bounded():
    window = _make_window()
    window.open_command_overlay()
    _type_request(window, "zzzzzzz")
    window.handle_overlay_submit_requested()

    _assert(window._command_model.phase == "entry", "a no-match request should remain in entry phase")
    _assert(window._command_model.status_kind == "not_found", "a no-match request should surface not_found status")
    _assert(window._command_model.pending_action is None, "a no-match request should not leave a pending action")
    _assert(window._command_panel.last_payload.get("ambiguous_matches") == [], "a no-match request should not leave ambiguous matches")


def _test_typed_first_choose_confirm_result_flow():
    window = _make_window()
    launches = []
    original_launch = renderer_mod.launch_command_action
    renderer_mod.launch_command_action = lambda action: launches.append(action.id)
    try:
        window.open_command_overlay()
        _type_request(window, "open nexus folder")
        window.handle_overlay_submit_requested()

        _assert(window._command_model.phase == "choose", "an ambiguous request should enter choose phase")
        ambiguous_matches = window._command_panel.last_payload.get("ambiguous_matches") or []
        _assert(len(ambiguous_matches) >= 2, "an ambiguous request should surface multiple visible choices")

        window.handle_overlay_text_requested("2")
        _assert(window._command_model.phase == "confirm", "choosing an ambiguous match should enter confirm phase")

        pending_action = window._command_panel.last_payload.get("pending_action") or {}
        _assert(pending_action.get("id"), "confirm phase should surface one pending action")
        _assert(pending_action.get("target_kind"), "confirm phase should surface target kind detail")
        _assert(
            pending_action.get("target_display") or pending_action.get("target"),
            "confirm phase should surface a visible target detail",
        )

        expected_launch_id = pending_action["id"]
        window.handle_overlay_submit_requested()

        _assert(launches == [expected_launch_id], "confirm submit should execute the chosen pending action exactly once")
        _assert(window._command_model.phase == "result", "successful execution should enter result phase")
        _assert(window._command_model.status_kind == "launch_requested", "successful execution should produce launch_requested result status")
        _assert(window._command_model.input_text == "", "result phase should clear stale entry text")
        _assert(window._command_model.pending_action is None, "result phase should clear stale pending action state")
    finally:
        renderer_mod.launch_command_action = original_launch


def _test_result_close_and_reopen_is_clean():
    window = _make_window()
    original_launch = renderer_mod.launch_command_action
    renderer_mod.launch_command_action = lambda _action: None
    try:
        window.open_command_overlay()
        _type_request(window, "open file explorer")
        window.handle_overlay_submit_requested()
        _assert(window._command_model.phase == "confirm", "a single exact match should enter confirm phase")
        window.handle_overlay_submit_requested()
        _assert(window._command_model.phase == "result", "confirm submit should enter result phase before close")

        window._close_command_overlay_after_result()
        window.open_command_overlay()
        _assert_clean_entry_baseline(window, "result reopen")
    finally:
        renderer_mod.launch_command_action = original_launch


def _test_url_saved_action_confirm_result_flow():
    action_catalog = CommandActionCatalog(
        (
            CommandAction(
                id="open_nexus_docs_site",
                title="Open Nexus Docs Site",
                target_kind="url",
                target="https://example.com/docs/start",
                aliases=("open docs site",),
            ),
        )
    )
    window = _make_window(action_catalog=action_catalog)
    launches = []
    original_launch = renderer_mod.launch_command_action
    renderer_mod.launch_command_action = lambda action: launches.append(
        (action.id, action.target_kind, action.target)
    )
    try:
        window.open_command_overlay()
        _type_request(window, "open docs site")
        window.handle_overlay_submit_requested()

        _assert(window._command_model.phase == "confirm", "a single url exact match should enter confirm phase")
        pending_action = window._command_panel.last_payload.get("pending_action") or {}
        _assert(
            pending_action.get("target_kind") == "url",
            "confirm phase should surface url target kinds without changing the state machine",
        )
        _assert(
            pending_action.get("target_display") == "example.com/docs/start",
            "confirm phase should compact url targets for inspection before execution",
        )

        window.handle_overlay_submit_requested()

        _assert(
            launches == [("open_nexus_docs_site", "url", "https://example.com/docs/start")],
            "confirm submit should execute the url saved action exactly once through the existing baseline flow",
        )
        _assert(window._command_model.phase == "result", "successful url execution should enter result phase")
        _assert(
            window._command_model.status_kind == "launch_requested",
            "successful url execution should preserve the existing launch_requested result behavior",
        )

        window._close_command_overlay_after_result()
        window.open_command_overlay()
        _assert_clean_entry_baseline(window, "url result reopen")
    finally:
        renderer_mod.launch_command_action = original_launch


def main():
    tests = [
        ("typed-first open enters entry mode", _test_open_starts_in_typed_first_entry_mode),
        ("not-found stays bounded", _test_not_found_stays_bounded),
        ("choose-confirm-result baseline flow", _test_typed_first_choose_confirm_result_flow),
        ("result close and reopen is clean", _test_result_close_and_reopen_is_clean),
        ("url saved action confirm-result flow", _test_url_saved_action_confirm_result_flow),
    ]

    for name, fn in tests:
        fn()
        print(f"PASS: {name}")

    print("INTERACTION BASELINE VALIDATION: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
