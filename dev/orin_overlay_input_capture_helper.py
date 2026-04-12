import os
import sys
import time
from types import SimpleNamespace

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import desktop.desktop_renderer as renderer_mod
import desktop.hotkeys as hotkeys_mod
from desktop.interaction_overlay_model import CommandOverlayModel
from pynput import keyboard as pynput_keyboard


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


def _make_window():
    window = renderer_mod.DesktopRuntimeWindow.__new__(renderer_mod.DesktopRuntimeWindow)
    window.screen_ref = SimpleNamespace(availableGeometry=lambda: _FakeRect())
    window.compute_compact_geometry = lambda: _FakeRect()
    window._is_shutting_down = False
    window._overlay_trace_enabled = False
    window._command_model = CommandOverlayModel()
    window._command_panel = _FakePanel()
    window._result_close_timer = _FakeTimer()
    window._overlay_input_capture_until = 0.0
    window._overlay_local_input_engaged = False
    window._overlay_global_capture_suspended = False
    window._last_launch_failure_action_id = ""
    window._last_launch_failure_count = 0
    window._reported_recoverable_launch_failures = set()
    window.runtime_log_path = ""
    window._log_event = lambda *_args, **_kwargs: None
    window._apply_command_overlay_state = lambda: renderer_mod.DesktopRuntimeWindow._apply_command_overlay_state(window)
    window._show_command_result = lambda kind, text: (
        window._command_model.show_result(kind, text),
        window._apply_command_overlay_state(),
    )
    return window


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


class _RecorderSignal:
    def __init__(self, sink, label):
        self._sink = sink
        self._label = label

    def emit(self, *args):
        self._sink.append((self._label, args))


class _FakeBus:
    def __init__(self):
        self.events = []
        self.shutdown_requested = _RecorderSignal(self.events, "shutdown")
        self.command_overlay_toggle_requested = _RecorderSignal(self.events, "toggle")
        self.command_overlay_text_requested = _RecorderSignal(self.events, "text")
        self.command_overlay_backspace_requested = _RecorderSignal(self.events, "backspace")
        self.command_overlay_submit_requested = _RecorderSignal(self.events, "submit")
        self.command_overlay_escape_requested = _RecorderSignal(self.events, "escape")


def _assert_clean_entry_baseline(window, message_prefix="overlay"):
    _assert(window._command_model.phase == "entry", f"{message_prefix} should reopen in entry phase")
    _assert(window._command_model.input_armed, f"{message_prefix} should reopen with input armed")
    _assert(window._command_model.input_text == "", f"{message_prefix} should reopen with no stale input text")
    _assert(window._command_model.last_request == "", f"{message_prefix} should reopen with no stale typed request")
    _assert(window._command_model.pending_action is None, f"{message_prefix} should reopen with no stale pending action")
    _assert(window._command_model.pending_matches == (), f"{message_prefix} should reopen with no stale pending matches")
    _assert(window._command_model.status_kind == "idle", f"{message_prefix} should reopen with idle status")
    _assert(window._command_model.status_text == "", f"{message_prefix} should reopen with no stale status text")
    _assert(window._command_panel.last_payload.get("phase") == "entry", f"{message_prefix} payload should reopen in entry phase")
    _assert(window._command_panel.last_payload.get("input_text", "") == "", f"{message_prefix} payload should reopen with no stale input")
    _assert(window._command_panel.last_payload.get("typed_request", "") == "", f"{message_prefix} payload should reopen with no stale typed request")
    _assert(window._command_panel.last_payload.get("pending_action") is None, f"{message_prefix} payload should reopen with no pending action")
    _assert(window._command_panel.last_payload.get("ambiguous_matches") == [], f"{message_prefix} payload should reopen with no stale choices")
    _assert(window._command_panel.last_payload.get("status_kind") == "idle", f"{message_prefix} payload should reopen idle")


def _assert_clean_retry_state(window, message_prefix="overlay retry"):
    _assert(window._command_model.phase == "entry", f"{message_prefix} should be in entry phase")
    _assert(window._command_model.last_request == "", f"{message_prefix} should not retain stale typed request state")
    _assert(window._command_model.pending_action is None, f"{message_prefix} should not retain stale pending action state")
    _assert(window._command_model.pending_matches == (), f"{message_prefix} should not retain stale ambiguous matches")
    _assert(window._command_panel.last_payload.get("typed_request", "") == "", f"{message_prefix} payload should not retain stale typed request state")
    _assert(window._command_panel.last_payload.get("pending_action") is None, f"{message_prefix} payload should not retain stale confirm metadata")
    _assert(window._command_panel.last_payload.get("ambiguous_matches") == [], f"{message_prefix} payload should not retain stale choice metadata")


def _test_first_open_capture_allows_typing():
    window = _make_window()
    window.open_command_overlay()
    _assert(window._command_panel.focus_after_show_calls == 1, "open should request local input focus after show")
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


def _test_active_entry_keeps_capture_after_timeout():
    window = _make_window()
    window.open_command_overlay()
    window._command_panel.active = True
    window._command_panel.input_line.focused = True
    window._overlay_input_capture_until = time.monotonic() - 0.01
    _assert(
        window.overlay_needs_global_input_capture(),
        "entry capture should stay alive while the overlay remains the active window, even after the short launch timer expires",
    )


def _test_programmatic_focus_does_not_disable_capture():
    window = _make_window()
    window.open_command_overlay()
    window._command_panel.active = True
    window._command_panel.input_line.focused = True
    window._command_panel.input_line._last_focus_was_manual = False
    window.handle_command_input_focus_acquired()
    _assert(
        window.overlay_needs_global_input_capture(),
        "programmatic first-open focus should not disable fallback capture before real keyboard ownership exists",
    )


def _test_local_focus_clears_capture_and_stops_mirroring():
    window = _make_window()
    window.open_command_overlay()
    window._command_panel.active = True
    window._command_panel.input_line.focused = True
    window._command_panel.input_line._last_focus_was_manual = True
    window.handle_command_input_focus_acquired()
    _assert(
        not window.overlay_needs_global_input_capture(),
        "capture should stand down once the panel really owns active focused input",
    )
    _assert(
        window._command_panel.input_line.local_typing_enabled,
        "manual focus should enable local typing once the user explicitly clicks into the line edit",
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


def _test_false_focus_acquire_keeps_capture_alive():
    window = _make_window()
    window.open_command_overlay()
    window._command_panel.active = False
    window._command_panel.input_line.focused = True
    window._command_panel.input_line._last_focus_was_manual = False
    window.handle_command_input_focus_acquired()
    _assert(
        not window._overlay_local_input_engaged,
        "local input should not be marked engaged when the line edit flashes focus but the panel never becomes active",
    )
    _assert(
        window.overlay_needs_global_input_capture(),
        "fallback capture should stay alive in the fake-focused but not really active first-open case",
    )


def _test_reopen_rearms_capture():
    window = _make_window()
    window.open_command_overlay()
    window._command_panel.active = True
    window._command_panel.input_line.focused = True
    window._command_panel.input_line._last_focus_was_manual = True
    window.handle_command_input_focus_acquired()
    window._command_panel.active = False
    window._command_panel.input_line.focused = False
    window.close_command_overlay()
    window.open_command_overlay()
    _assert(window.overlay_needs_global_input_capture(), "reopen should arm a fresh capture session")


def _test_no_click_external_click_suspends_capture():
    window = _make_window()
    window.open_command_overlay()
    window.handle_overlay_text_requested("a")
    _assert(window.overlay_needs_global_input_capture(), "no-click entry path should start with fallback capture active")
    window.handle_overlay_global_click_requested(900, 700)
    _assert(
        not window.overlay_needs_global_input_capture(),
        "clicking outside the overlay should suspend no-click fallback capture so outside typing no longer mirrors",
    )
    before = window._command_model.input_text
    window.handle_overlay_text_requested("x")
    _assert(window._command_model.input_text == before, "typing after external click should not change the overlay text")


def _test_no_click_external_click_clears_typing_ready_visual():
    window = _make_window()
    window.open_command_overlay()
    _assert(
        window._command_panel.last_payload.get("typing_ready"),
        "first-open entry should visually present as typing-ready while fallback capture is active",
    )
    window.handle_overlay_global_click_requested(900, 700)
    window._apply_command_overlay_state()
    _assert(
        not window._command_panel.last_payload.get("typing_ready"),
        "outside click should stop the typing-ready visual once fallback capture is suspended",
    )


def _test_confirm_capture_stays_on_when_panel_is_active_but_input_lacks_focus():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.phase = "confirm"
    window._command_model.pending_action = window._command_model.actions[0]
    window._overlay_input_capture_until = time.monotonic() + 5.0
    window._command_panel.active = True
    window._command_panel.input_line.focused = False
    _assert(
        window.overlay_needs_global_input_capture(),
        "confirm capture should stay on when the panel looks active but the input itself no longer owns focus",
    )


def _test_confirm_ready_rearms_capture_for_human_confirm_delay():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open file explorer"
    before = time.monotonic()
    window.handle_command_submit(source="fallback")
    remaining = window._overlay_input_capture_until - before
    _assert(
        remaining > 4.0,
        "confirm-ready should keep fallback capture armed long enough for a human second Enter",
    )


def _test_ambiguous_ready_rearms_capture_for_human_choice_delay():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open nexus folder"
    before = time.monotonic()
    window.handle_command_submit(source="fallback")
    remaining = window._overlay_input_capture_until - before
    _assert(window._command_model.phase == "choose", "open nexus folder should enter choose state")
    _assert(
        remaining > 4.0,
        "ambiguous-ready should keep fallback capture armed long enough for a human number choice",
    )


def _test_ambiguous_choice_rearms_capture_for_human_confirm_delay():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open nexus folder"
    window.handle_command_submit(source="fallback")
    before = time.monotonic()
    window.handle_ambiguous_match_selected(1)
    remaining = window._overlay_input_capture_until - before
    _assert(window._command_model.phase == "confirm", "number choice should enter confirm state")
    _assert(
        remaining > 4.0,
        "choose-selection should keep fallback capture armed long enough for a human confirm Enter",
    )


def _test_choice_cancel_rearms_capture_for_human_retry_delay():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open nexus folder"
    window.handle_command_submit(source="fallback")
    before = time.monotonic()
    window.handle_command_escape()
    remaining = window._overlay_input_capture_until - before
    _assert(window._command_model.phase == "entry", "Esc from choose should return to entry state")
    _assert(
        remaining > 4.0,
        "choose-cancel should keep fallback capture armed long enough for a human retry",
    )


def _test_confirm_cancel_rearms_capture_for_human_retry_delay():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open file explorer"
    window.handle_command_submit(source="fallback")
    before = time.monotonic()
    window.handle_command_escape()
    remaining = window._overlay_input_capture_until - before
    _assert(window._command_model.phase == "entry", "Esc from confirm should return to entry state")
    _assert(
        remaining > 4.0,
        "confirm-cancel should keep fallback capture armed long enough for a human retry",
    )


def _test_choose_cancel_refreshes_panel_layout_after_return_to_entry():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open nexus folder"
    window.handle_command_submit(source="fallback")
    before = window._command_panel.refresh_for_geometry_calls
    window.handle_command_escape()
    _assert(
        window._command_panel.refresh_for_geometry_calls > before,
        "Esc from choose should refresh the overlay panel layout after returning to entry",
    )


def _test_confirm_cancel_refreshes_panel_layout_after_return_to_entry():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open file explorer"
    window.handle_command_submit(source="fallback")
    before = window._command_panel.refresh_for_geometry_calls
    window.handle_command_escape()
    _assert(
        window._command_panel.refresh_for_geometry_calls > before,
        "Esc from confirm should refresh the overlay panel layout after returning to entry",
    )


def _test_not_found_retry_edit_clears_stale_request_state():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "zzzzzzz"
    window.handle_command_submit(source="fallback")
    _assert(window._command_model.status_kind == "not_found", "no-match request should surface not_found status")
    _assert(window._command_model.last_request == "zzzzzzz", "not_found should record the attempted request before retry")
    window.handle_command_text_changed("open file explorer")
    _assert(window._command_model.status_kind == "idle", "editing after not_found should clear the stale not_found status")
    _assert_clean_retry_state(window, "not-found retry")


def _test_ambiguous_back_out_clears_stale_request_state_for_retry():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open nexus folder"
    window.handle_command_submit(source="fallback")
    _assert(window._command_model.phase == "choose", "ambiguous request should enter choose state")
    _assert(window._command_model.last_request == "open nexus folder", "ambiguous request should record the attempted request before back-out")
    window.handle_command_escape()
    _assert_clean_retry_state(window, "ambiguous back-out retry")
    window.handle_command_text_changed("open file explorer")
    _assert(window._command_model.status_kind == "idle", "retry editing after ambiguous back-out should stay in idle entry state")
    _assert_clean_retry_state(window, "ambiguous back-out retry after edit")


def _test_confirm_back_out_clears_stale_request_state_for_retry():
    window = _make_window()
    window.open_command_overlay()
    window._command_model.input_text = "open file explorer"
    window.handle_command_submit(source="fallback")
    _assert(window._command_model.phase == "confirm", "single match should enter confirm state")
    _assert(window._command_model.last_request == "open file explorer", "confirm path should record the attempted request before back-out")
    window.handle_command_escape()
    _assert_clean_retry_state(window, "confirm back-out retry")
    window.handle_command_text_changed("zzzzzzz")
    _assert(window._command_model.status_kind == "idle", "retry editing after confirm back-out should stay in idle entry state")
    _assert_clean_retry_state(window, "confirm back-out retry after edit")


def _test_launch_requested_result_clears_transient_state_immediately():
    window = _make_window()
    original_launch = renderer_mod.launch_command_action
    renderer_mod.launch_command_action = lambda _action: None
    try:
        window.open_command_overlay()
        window._command_model.input_text = "open file explorer"
        window.handle_command_submit(source="fallback")
        window.handle_command_submit(source="fallback")
        _assert(window._command_model.phase == "result", "successful launch should enter result state")
        _assert(window._command_model.input_text == "", "result state should clear stale input text immediately")
        _assert(window._command_model.last_request == "", "result state should clear stale typed request immediately")
        _assert(window._command_model.pending_action is None, "result state should clear stale pending action immediately")
        _assert(window._command_model.pending_matches == (), "result state should clear stale pending matches immediately")
        _assert(window._command_panel.last_payload.get("pending_action") is None, "result payload should not retain confirm metadata")
        _assert(window._command_panel.last_payload.get("typed_request", "") == "", "result payload should not retain typed request metadata")
    finally:
        renderer_mod.launch_command_action = original_launch


def _test_launch_requested_timeout_close_and_reopen_is_clean():
    window = _make_window()
    original_launch = renderer_mod.launch_command_action
    renderer_mod.launch_command_action = lambda _action: None
    try:
        window.open_command_overlay()
        window._command_model.input_text = "open file explorer"
        window.handle_command_submit(source="fallback")
        window.handle_command_submit(source="fallback")
        window._close_command_overlay_after_result()
        window.open_command_overlay()
        _assert_clean_entry_baseline(window, "launch-requested reopen")
    finally:
        renderer_mod.launch_command_action = original_launch


def _test_launch_failed_result_clears_transient_state_and_reopen_is_clean():
    window = _make_window()
    original_launch = renderer_mod.launch_command_action
    renderer_mod.launch_command_action = lambda _action: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        window.open_command_overlay()
        window._command_model.input_text = "open file explorer"
        window.handle_command_submit(source="fallback")
        window.handle_command_submit(source="fallback")
        _assert(window._command_model.phase == "result", "launch failure should enter result state")
        _assert(window._command_model.status_kind == "launch_failed", "launch failure should surface launch_failed status")
        _assert(window._command_model.input_text == "", "launch-failed result should clear stale input text immediately")
        _assert(window._command_model.last_request == "", "launch-failed result should clear stale typed request immediately")
        _assert(window._command_model.pending_action is None, "launch-failed result should clear stale pending action immediately")
        window._close_command_overlay_after_result()
        window.open_command_overlay()
        _assert_clean_entry_baseline(window, "launch-failed reopen")
    finally:
        renderer_mod.launch_command_action = original_launch


def _test_manual_result_close_and_reopen_is_clean():
    window = _make_window()
    original_launch = renderer_mod.launch_command_action
    renderer_mod.launch_command_action = lambda _action: None
    try:
        window.open_command_overlay()
        window._command_model.input_text = "open file explorer"
        window.handle_command_submit(source="fallback")
        window.handle_command_submit(source="fallback")
        window.close_command_overlay()
        window.open_command_overlay()
        _assert_clean_entry_baseline(window, "manual-close reopen")
    finally:
        renderer_mod.launch_command_action = original_launch


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
    window._command_model.phase = "confirm"
    window._overlay_input_capture_until = time.monotonic() - 0.01
    _assert(
        not window.overlay_needs_global_input_capture(),
        "expired capture session should still stand down fallback outside the entry-phase typing path",
    )


def _test_line_edit_focus_methods_present():
    _assert(
        "focusInEvent" in renderer_mod.CommandInputLineEdit.__dict__,
        "the input line edit must override focusInEvent so local-focus engagement is tracked",
    )
    _assert(
        "focusOutEvent" in renderer_mod.CommandInputLineEdit.__dict__,
        "the input line edit must override focusOutEvent so local-focus loss can be observed",
    )


def _test_hotkey_launch_grace_bridges_open_gap():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager.set_overlay_input_enabled_provider(lambda: False)

    manager._on_press(pynput_keyboard.Key.ctrl_l)
    manager._on_press(pynput_keyboard.Key.alt_l)
    manager._on_press(pynput_keyboard.Key.home)
    manager._on_release(pynput_keyboard.Key.home)
    manager._on_release(pynput_keyboard.Key.alt_l)
    manager._on_release(pynput_keyboard.Key.ctrl_l)
    manager._on_press(pynput_keyboard.KeyCode.from_char("o"))

    _assert(bus.events[0][0] == "toggle", "overlay hotkey should toggle first")
    _assert(
        ("text", ("o",)) in bus.events,
        "launch grace should forward immediate typing even before the provider is ready",
    )


def _test_hotkey_grace_expires_cleanly():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager.set_overlay_input_enabled_provider(lambda: False)
    manager._overlay_launch_grace_until = time.monotonic() - 0.01
    manager._on_press(pynput_keyboard.KeyCode.from_char("x"))
    _assert(not bus.events, "expired hotkey grace should not keep forwarding stray typing")


def _test_hotkey_grace_stands_down_after_manual_local_engagement():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager.set_overlay_input_enabled_provider(lambda: False)
    manager.set_overlay_launch_grace_allowed_provider(lambda: False)
    manager._overlay_launch_grace_until = time.monotonic() + 5.0
    manager._on_press(pynput_keyboard.KeyCode.from_char("x"))
    _assert(not bus.events, "launch grace should not keep forwarding typing after real local input ownership is established")


def _test_shutdown_hotkey_still_emits_shutdown():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager._on_press(pynput_keyboard.Key.ctrl_l)
    manager._on_press(pynput_keyboard.Key.alt_l)
    manager._on_press(pynput_keyboard.KeyCode.from_char("2"))
    _assert(("shutdown", ()) in bus.events, "shutdown hotkey should still emit shutdown after reset hardening changes")


def _test_fallback_text_is_suppressed_underlay_and_forwarded():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager.set_overlay_input_enabled_provider(lambda: True)
    manager._on_press(pynput_keyboard.KeyCode.from_char("a"))
    _assert(("text", ("a",)) in bus.events, "fallback typing should still be forwarded into the overlay")


def _test_fallback_submit_is_suppressed_underlay_and_forwarded():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager.set_overlay_input_enabled_provider(lambda: True)
    manager._on_press(pynput_keyboard.Key.enter)
    _assert(("submit", ()) in bus.events, "fallback Enter should still be forwarded into the overlay")


def _test_win32_text_suppression_happens_before_callback_delivery():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager._listener = SimpleNamespace(_suppress=False)
    manager.set_overlay_input_enabled_provider(lambda: True)
    manager._win32_event_filter(manager._WM_KEYDOWN, SimpleNamespace(vkCode=0x4F))
    _assert(manager._listener._suppress, "Win32 filter should arm suppression for the current text key before the callback path runs")


def _test_win32_submit_suppression_happens_before_callback_delivery():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager._listener = SimpleNamespace(_suppress=False)
    manager.set_overlay_input_enabled_provider(lambda: True)
    result = manager._win32_event_filter(manager._WM_KEYDOWN, SimpleNamespace(vkCode=0x0D))
    _assert(("submit", ()) in bus.events, "Win32 filter should forward Enter directly into the overlay before callback delivery")
    _assert(manager._listener._suppress, "Win32 filter should arm suppression for the current Enter key before the callback path runs")
    _assert(result is False, "Win32 filter should stop callback posting for fallback Enter once it has already been forwarded")


def _test_win32_unsuppressed_key_clears_suppression_flag():
    bus = _FakeBus()
    manager = hotkeys_mod.GlobalHotkeyManager(bus)
    manager._listener = SimpleNamespace(_suppress=True)
    manager.set_overlay_input_enabled_provider(lambda: False)
    manager._win32_event_filter(manager._WM_KEYDOWN, SimpleNamespace(vkCode=0x41))
    _assert(not manager._listener._suppress, "Win32 filter should clear suppression when the current key is not owned by the overlay")


def main():
    tests = [
        ("first-open capture", _test_first_open_capture_allows_typing),
        ("entry capture while input lacks focus", _test_active_panel_without_input_focus_still_uses_capture),
        ("active entry survives timeout", _test_active_entry_keeps_capture_after_timeout),
        ("programmatic focus keeps capture", _test_programmatic_focus_does_not_disable_capture),
        ("local focus clears mirroring", _test_local_focus_clears_capture_and_stops_mirroring),
        ("false focus acquire keeps capture", _test_false_focus_acquire_keeps_capture_alive),
        ("reopen rearms capture", _test_reopen_rearms_capture),
        ("no-click external click suspends capture", _test_no_click_external_click_suspends_capture),
        ("no-click external click clears typing-ready visual", _test_no_click_external_click_clears_typing_ready_visual),
        ("confirm capture survives false panel-active state", _test_confirm_capture_stays_on_when_panel_is_active_but_input_lacks_focus),
        ("confirm-ready rearms capture for human delay", _test_confirm_ready_rearms_capture_for_human_confirm_delay),
        ("ambiguous-ready rearms capture for human choice delay", _test_ambiguous_ready_rearms_capture_for_human_choice_delay),
        ("ambiguous choice rearms capture for human confirm delay", _test_ambiguous_choice_rearms_capture_for_human_confirm_delay),
        ("choose cancel rearms capture for human retry", _test_choice_cancel_rearms_capture_for_human_retry_delay),
        ("confirm cancel rearms capture for human retry", _test_confirm_cancel_rearms_capture_for_human_retry_delay),
        ("choose cancel refreshes layout after return to entry", _test_choose_cancel_refreshes_panel_layout_after_return_to_entry),
        ("confirm cancel refreshes layout after return to entry", _test_confirm_cancel_refreshes_panel_layout_after_return_to_entry),
        ("not-found retry clears stale request state", _test_not_found_retry_edit_clears_stale_request_state),
        ("ambiguous back-out retry clears stale request state", _test_ambiguous_back_out_clears_stale_request_state_for_retry),
        ("confirm back-out retry clears stale request state", _test_confirm_back_out_clears_stale_request_state_for_retry),
        ("launch-requested result clears transient state", _test_launch_requested_result_clears_transient_state_immediately),
        ("launch-requested timeout close reopens clean", _test_launch_requested_timeout_close_and_reopen_is_clean),
        ("launch-failed result clears and reopens clean", _test_launch_failed_result_clears_transient_state_and_reopen_is_clean),
        ("manual result close reopens clean", _test_manual_result_close_and_reopen_is_clean),
        ("choose-confirm execute path", _test_ambiguous_choose_confirm_execute_path),
        ("capture expiry", _test_capture_expiry_stands_down_fallback),
        ("line edit focus methods", _test_line_edit_focus_methods_present),
        ("hotkey launch grace", _test_hotkey_launch_grace_bridges_open_gap),
        ("hotkey grace expiry", _test_hotkey_grace_expires_cleanly),
        ("hotkey grace stops after local engagement", _test_hotkey_grace_stands_down_after_manual_local_engagement),
        ("shutdown hotkey remains available", _test_shutdown_hotkey_still_emits_shutdown),
        ("fallback text suppresses underlay", _test_fallback_text_is_suppressed_underlay_and_forwarded),
        ("fallback submit suppresses underlay", _test_fallback_submit_is_suppressed_underlay_and_forwarded),
        ("win32 text suppression is synchronous", _test_win32_text_suppression_happens_before_callback_delivery),
        ("win32 submit suppression is synchronous", _test_win32_submit_suppression_happens_before_callback_delivery),
        ("win32 clears suppression on unrelated key", _test_win32_unsuppressed_key_clears_suppression_flag),
    ]

    for name, fn in tests:
        fn()
        print(f"PASS: {name}")

    print("OVERLAY INPUT HELPER: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
