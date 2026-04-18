import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import desktop.desktop_renderer as renderer_mod
from desktop.interaction_overlay_model import CommandOverlayModel
from desktop.saved_action_authoring import (
    CallableGroupDraft,
    SavedActionDraft,
    create_callable_group_from_draft,
    create_saved_action_from_draft,
)
from desktop.shared_action_model import (
    CommandGroup,
    build_default_command_action_catalog,
    execute_command_group,
)


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _make_group(
    source_path: Path,
    *,
    group_title: str = "Workspace Tools",
    group_aliases: tuple[str, ...] = ("workspace tools",),
):
    create_saved_action_from_draft(
        SavedActionDraft(
            title="Open Reports",
            target_kind="folder",
            target=r"C:\Reports",
            aliases=("show reports",),
        ),
        source_path,
    )
    create_saved_action_from_draft(
        SavedActionDraft(
            title="Open Notes",
            target_kind="app",
            target="notepad.exe",
            aliases=("notes",),
        ),
        source_path,
    )
    create_callable_group_from_draft(
        CallableGroupDraft(
            title=group_title,
            aliases=group_aliases,
            member_action_ids=("open_reports", "open_saved_actions_folder", "open_notes"),
        ),
        source_path,
    )
    catalog = build_default_command_action_catalog(source_path)
    group = catalog.resolve_group(group_aliases[0])
    _assert(group is not None, "callable-group execution validation should resolve the created group")
    return group


def _make_window():
    window = SimpleNamespace(_events=[])
    window._log_event = lambda event: window._events.append(event)
    window._emit_group_execution_marker = lambda marker_name, fields: renderer_mod.DesktopRuntimeWindow._emit_group_execution_marker(
        window,
        marker_name,
        fields,
    )
    return window


def _make_dispatch_window(source_path: Path):
    window = SimpleNamespace(
        _events=[],
        _shown_results=[],
        _cleared_launch_failure_action_ids=[],
        _prepare_calls=[],
    )
    window._command_model = CommandOverlayModel(action_catalog=build_default_command_action_catalog(source_path))
    window._command_model.open(arm_input=True)
    window._overlay_local_input_engaged = False
    window._foreground_window_snapshot = lambda: {"hwnd": 0, "class_name": "", "title": ""}
    window._trace_overlay = lambda *_args, **_kwargs: None
    window._apply_command_overlay_state = lambda: None
    window._refresh_overlay_input_capture = lambda *_args, **_kwargs: None
    window._log_event = lambda event: window._events.append(event)
    window._bound_execution_trace = lambda execution_trace, *, fallback_action_id="": renderer_mod.DesktopRuntimeWindow._bound_execution_trace(
        window,
        execution_trace,
        fallback_action_id=fallback_action_id,
    )
    window._normalize_launch_failure_context = (
        lambda action_id, failure_context=None: renderer_mod.DesktopRuntimeWindow._normalize_launch_failure_context(
            window,
            action_id,
            failure_context,
        )
    )
    def _prepare_recoverable_launch_failure_report(action, *, failure_context=None):
        normalized_failure_context = renderer_mod.DesktopRuntimeWindow._normalize_launch_failure_context(
            window,
            action.id,
            failure_context,
        )
        window._prepare_calls.append(
            {
                "action_id": action.id,
                "failure_context": dict(failure_context or {}),
                "normalized_failure_context": dict(normalized_failure_context),
            }
        )
        return None

    window._prepare_recoverable_launch_failure_report = _prepare_recoverable_launch_failure_report

    def _show_command_result(status_kind: str, status_text: str, close_delay_ms: int = 1200):
        del close_delay_ms
        window._shown_results.append((status_kind, status_text))
        window._command_model.show_result(status_kind, status_text)

    def _clear_launch_failure_tracking(action_id: str):
        window._cleared_launch_failure_action_ids.append(action_id)

    window._show_command_result = _show_command_result
    window._clear_launch_failure_tracking = _clear_launch_failure_tracking
    window._format_failure_context_suffix = lambda failure_context: renderer_mod.DesktopRuntimeWindow._format_failure_context_suffix(
        window,
        failure_context,
    )
    window._classify_recoverable_launch_failed_incident = (
        lambda action_id, failure_count, *, failure_context=None: renderer_mod.DesktopRuntimeWindow._classify_recoverable_launch_failed_incident(
            window,
            action_id,
            failure_count,
            failure_context=failure_context,
        )
    )
    window._emit_group_execution_marker = lambda marker_name, fields: renderer_mod.DesktopRuntimeWindow._emit_group_execution_marker(
        window,
        marker_name,
        fields,
    )
    window._resolve_group_failure_action = lambda group, failed_action_id: renderer_mod.DesktopRuntimeWindow._resolve_group_failure_action(
        window,
        group,
        failed_action_id,
    )
    window._build_group_failure_context = lambda group, result: renderer_mod.DesktopRuntimeWindow._build_group_failure_context(
        window,
        group,
        result,
    )
    window._execute_callable_group = lambda group: renderer_mod.DesktopRuntimeWindow._execute_callable_group(window, group)
    return window


def _freeze_result_state(window):
    def _show_command_result(status_kind: str, status_text: str, close_delay_ms: int = 1200):
        del close_delay_ms
        window._shown_results.append((status_kind, status_text))

    window._show_command_result = _show_command_result


def _group_events(window):
    return [event for event in window._events if event.startswith("RENDERER_MAIN|GROUP_EXECUTION_")]


def _parse_group_event(event: str):
    parts = event.split("|")
    marker_name = parts[1] if len(parts) > 1 else ""
    fields = {}
    for part in parts[2:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        fields[key] = value
    return marker_name, fields


def _test_result_hint_text_remains_unchanged():
    renderer_source = (ROOT_DIR / "desktop" / "desktop_renderer.py").read_text(encoding="utf-8").replace("\r\n", "\n")
    _assert(
        'elif phase == "result":\n            self.hint_label.setText("Returning to passive desktop mode.")' in renderer_source,
        "result hint text should remain unchanged",
    )


def _test_group_result_text_uses_execution_intent_group_name():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        group = _make_group(
            source_path,
            group_title="Alpha Toolchain",
            group_aliases=("alpha toolchain",),
        )
        window = _make_dispatch_window(source_path)

        original_launch = renderer_mod.launch_command_action
        renderer_mod.launch_command_action = lambda _action: None
        try:
            window._command_model.set_input_text("alpha toolchain")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            renderer_mod.DesktopRuntimeWindow.handle_ambiguous_match_selected(window, 0)
            intent = window._command_model.pending_execution_intent
            _assert(intent is not None, "group confirm should bind an execution intent before dispatch")
            _assert(
                intent.group is not None and intent.group.title == "Alpha Toolchain",
                "group execution intent should carry the selected group's title",
            )
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(
            window._shown_results[-1] == ("launch_requested", 'Group "Alpha Toolchain" executed in stored order.'),
            "group success result text should use the execution intent group title",
        )
        _assert(
            group.title == "Alpha Toolchain",
            "the validation fixture should preserve the expected group title for comparison",
        )


def _test_group_result_text_is_stable_under_overlay_mutation():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        group = _make_group(source_path)
        window = _make_dispatch_window(source_path)

        original_launch = renderer_mod.launch_command_action
        renderer_mod.launch_command_action = lambda _action: None
        try:
            window._command_model.set_input_text("workspace tools")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            renderer_mod.DesktopRuntimeWindow.handle_ambiguous_match_selected(window, 0)
            intent = window._command_model.pending_execution_intent
            _assert(intent is not None and intent.group is not None, "group confirm should bind an execution intent before dispatch")
            window._command_model.pending_group = CommandGroup(
                id="wrong_overlay_group",
                title="Wrong Overlay Name",
                aliases=("wrong overlay name",),
                member_action_ids=group.member_action_ids,
                member_actions=group.member_actions,
            )
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
        finally:
            renderer_mod.launch_command_action = original_launch

        shown_status = window._shown_results[-1][1]
        _assert(
            shown_status == 'Group "Workspace Tools" executed in stored order.',
            "result text should remain bound to the execution intent group title after overlay mutation",
        )
        _assert(
            "Wrong Overlay Name" not in shown_status,
            "overlay pending_group mutation should not change the group name shown in result text",
        )


def _test_group_result_text_is_not_hardcoded():
    with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
        first_source_path = Path(first_dir) / "saved_actions.json"
        second_source_path = Path(second_dir) / "saved_actions.json"
        _make_group(
            first_source_path,
            group_title="Alpha Toolchain",
            group_aliases=("alpha toolchain",),
        )
        _make_group(
            second_source_path,
            group_title="Beta Utilities",
            group_aliases=("beta utilities",),
        )
        first_window = _make_dispatch_window(first_source_path)
        second_window = _make_dispatch_window(second_source_path)

        original_launch = renderer_mod.launch_command_action
        renderer_mod.launch_command_action = lambda _action: None
        try:
            first_window._command_model.set_input_text("alpha toolchain")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(first_window)
            renderer_mod.DesktopRuntimeWindow.handle_ambiguous_match_selected(first_window, 0)
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(first_window)

            second_window._command_model.set_input_text("beta utilities")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(second_window)
            renderer_mod.DesktopRuntimeWindow.handle_ambiguous_match_selected(second_window, 0)
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(second_window)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(
            first_window._shown_results[-1] == ("launch_requested", 'Group "Alpha Toolchain" executed in stored order.'),
            "first group result text should use its own dynamic title",
        )
        _assert(
            second_window._shown_results[-1] == ("launch_requested", 'Group "Beta Utilities" executed in stored order.'),
            "second group result text should use its own dynamic title",
        )
        _assert(
            first_window._shown_results[-1][1] != second_window._shown_results[-1][1],
            "group result text should vary with the executed group's title rather than a fixed string",
        )


def _test_group_execution_runs_in_persisted_order_with_gap_free_markers():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        group = _make_group(source_path)
        window = _make_window()

        original_launch = renderer_mod.launch_command_action
        launched_action_ids = []
        renderer_mod.launch_command_action = lambda action: launched_action_ids.append(action.id)
        try:
            result = renderer_mod.DesktopRuntimeWindow._execute_callable_group(window, group)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(result.succeeded, "group execution should succeed when every step launcher succeeds")
        _assert(
            result.completed_action_ids == group.member_action_ids,
            "successful group execution should report every completed action id in persisted stored order",
        )
        _assert(
            launched_action_ids == list(group.member_action_ids),
            "group execution should launch member actions exactly in persisted stored order",
        )

        parsed_events = [_parse_group_event(event) for event in _group_events(window)]
        marker_names = [marker_name for marker_name, _fields in parsed_events]
        _assert(
            marker_names
            == [
                "GROUP_EXECUTION_STARTED",
                "GROUP_EXECUTION_STEP_STARTED",
                "GROUP_EXECUTION_STEP_SUCCEEDED",
                "GROUP_EXECUTION_STEP_STARTED",
                "GROUP_EXECUTION_STEP_SUCCEEDED",
                "GROUP_EXECUTION_STEP_STARTED",
                "GROUP_EXECUTION_STEP_SUCCEEDED",
                "GROUP_EXECUTION_COMPLETED",
            ],
            "group execution should emit deterministic start, per-step, and completion markers",
        )

        started_steps = [fields for marker_name, fields in parsed_events if marker_name == "GROUP_EXECUTION_STEP_STARTED"]
        completed_steps = [fields for marker_name, fields in parsed_events if marker_name == "GROUP_EXECUTION_STEP_SUCCEEDED"]
        _assert(
            [int(fields["step_index"]) for fields in started_steps] == [1, 2, 3],
            "step-start markers should advance monotonically without gaps",
        )
        _assert(
            [fields["action_id"] for fields in started_steps] == list(group.member_action_ids),
            "step-start markers should reflect persisted member ids in order",
        )
        _assert(
            [int(fields["step_index"]) for fields in completed_steps] == [1, 2, 3],
            "step-success markers should advance monotonically without gaps",
        )


def _test_group_execution_stops_on_first_failure_and_reports_terminal_failure():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        group = _make_group(source_path)
        window = _make_window()

        original_launch = renderer_mod.launch_command_action
        launched_action_ids = []

        def _failing_launcher(action):
            launched_action_ids.append(action.id)
            if action.id == "open_saved_actions_folder":
                raise RuntimeError("expected failure")

        renderer_mod.launch_command_action = _failing_launcher
        try:
            result = renderer_mod.DesktopRuntimeWindow._execute_callable_group(window, group)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(not result.succeeded, "group execution should fail when a member launcher raises")
        _assert(
            result.completed_action_ids == ("open_reports",),
            "group execution should report only the successfully completed prefix before failure",
        )
        _assert(
            result.failed_action_id == "open_saved_actions_folder" and result.failed_step_index == 2,
            "group execution should surface the exact failed member id and step index",
        )
        _assert(
            launched_action_ids == ["open_reports", "open_saved_actions_folder"],
            "group execution should stop immediately after the first failed member",
        )

        parsed_events = [_parse_group_event(event) for event in _group_events(window)]
        marker_names = [marker_name for marker_name, _fields in parsed_events]
        _assert(
            marker_names
            == [
                "GROUP_EXECUTION_STARTED",
                "GROUP_EXECUTION_STEP_STARTED",
                "GROUP_EXECUTION_STEP_SUCCEEDED",
                "GROUP_EXECUTION_STEP_STARTED",
                "GROUP_EXECUTION_STEP_FAILED",
                "GROUP_EXECUTION_FAILED",
            ],
            "group execution should emit a terminal failure marker immediately after the failed step",
        )
        started_steps = [fields for marker_name, fields in parsed_events if marker_name == "GROUP_EXECUTION_STEP_STARTED"]
        _assert(
            [int(fields["step_index"]) for fields in started_steps] == [1, 2],
            "group execution should not emit later step markers after the first failure",
        )


def _test_group_execution_rejects_ambiguous_member_order():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        group = _make_group(source_path)
        ambiguous_group = CommandGroup(
            id="ambiguous_workspace_tools",
            title="Ambiguous Workspace Tools",
            aliases=("ambiguous workspace tools",),
            member_action_ids=("open_saved_actions_folder", "open_reports"),
            member_actions=(
                group.member_actions[0],
                group.member_actions[1],
            ),
        )

        try:
            execute_command_group(
                ambiguous_group,
                action_launcher=lambda _action: None,
            )
        except ValueError as exc:
            _assert(
                "ambiguous" in str(exc).casefold(),
                "ambiguous member ordering should fail with an explicit ambiguity error",
            )
        else:
            raise AssertionError("group execution should reject ambiguous member ordering before any launch")


def _test_group_execution_intent_is_consumed_once_before_dispatch():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        group = _make_group(source_path)
        model = CommandOverlayModel(action_catalog=build_default_command_action_catalog(source_path))
        model.open(arm_input=True)
        model.set_input_text("workspace tools")

        result, payload = model.submit()
        _assert(result == "ambiguous", "group input should still enter choose before confirm")
        _assert(payload == group.member_actions, "group choose payload should expose the resolved member actions")

        result, payload = model.choose_match(1)
        _assert(result == "confirm_ready", "group member selection should enter confirm")
        _assert(payload.id == "open_saved_actions_folder", "chosen member should remain the confirm payload")
        _assert(model.pending_execution_intent is not None, "confirm should bind a group execution intent")

        result, payload = model.submit()
        _assert(result == "execute_confirmed", "first confirm submit should consume the bound group intent")
        _assert(
            payload.execution_type == "group"
            and payload.group_id == "workspace_tools"
            and payload.action_id == "open_saved_actions_folder"
            and payload.resolved_member_action_ids == group.member_action_ids,
            "consumed group intent should preserve execution type, selected action, group id, and stored member order",
        )
        _assert(model.pending_execution_intent is None, "group execution intent should clear immediately after the first submit")

        result, payload = model.submit()
        _assert(
            result == "ignored" and payload is None,
            "a second confirm submit must not be able to reuse the already-consumed group intent",
        )


def _test_single_execution_intent_is_consumed_once_before_dispatch():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _make_group(source_path)
        model = CommandOverlayModel(action_catalog=build_default_command_action_catalog(source_path))
        model.open(arm_input=True)
        model.set_input_text("show reports")

        result, payload = model.submit()
        _assert(result == "confirm_ready", "exact single-action input should enter confirm")
        _assert(payload.id == "open_reports", "single-action confirm payload should preserve the matched action")
        _assert(model.pending_execution_intent is not None, "single-action confirm should bind an execution intent")

        result, payload = model.submit()
        _assert(result == "execute_confirmed", "first confirm submit should consume the single-action intent")
        _assert(
            payload.execution_type == "single"
            and payload.action_id == "open_reports"
            and payload.group_id == ""
            and payload.resolved_member_action_ids == (),
            "consumed single-action intent should remain single-scoped without group metadata",
        )
        _assert(model.pending_execution_intent is None, "single-action intent should clear immediately after the first submit")

        result, payload = model.submit()
        _assert(
            result == "ignored" and payload is None,
            "a second confirm submit must not be able to reuse the already-consumed single-action intent",
        )


def _test_execution_intent_clears_on_cancel_and_reset():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _make_group(source_path)
        model = CommandOverlayModel(action_catalog=build_default_command_action_catalog(source_path))
        model.open(arm_input=True)

        model.set_input_text("show reports")
        result, _payload = model.submit()
        _assert(result == "confirm_ready", "single-action setup should reach confirm before cancel testing")
        _assert(model.pending_execution_intent is not None, "confirm should bind intent before cancellation")
        _assert(model.escape() == "confirm_cancelled", "escape from confirm should cancel the pending execution")
        _assert(model.pending_execution_intent is None, "confirm cancel should clear any pending execution intent")

        model.set_input_text("show reports")
        result, _payload = model.submit()
        _assert(result == "confirm_ready", "single-action setup should reach confirm before reset testing")
        _assert(model.pending_execution_intent is not None, "confirm should bind intent before reset testing")
        model.show_result("launch_requested", "Launch request sent.")
        _assert(model.pending_execution_intent is None, "result transitions should clear any pending execution intent")

        model.open(arm_input=True)
        model.set_input_text("show reports")
        result, _payload = model.submit()
        _assert(result == "confirm_ready", "single-action setup should reach confirm before close testing")
        _assert(model.pending_execution_intent is not None, "confirm should bind intent before close testing")
        model.close()
        _assert(model.pending_execution_intent is None, "overlay close should clear any pending execution intent")


def _test_confirm_surface_copy_is_group_aware_only_for_group_context():
    window = SimpleNamespace()

    group_copy = renderer_mod.CommandOverlayPanel._build_confirm_surface_copy(
        window,
        "group",
        {"title": "Workspace Tools"},
    )
    _assert(
        group_copy
        == {
            "title_label": "Selected member",
            "hint_text": 'Review the selected member details below. Press Enter to run "Workspace Tools" group in stored order.',
            "help_text": 'Press Enter to run "Workspace Tools" group in stored order, or Esc to return.',
        },
        "group confirm surface copy should clarify that Enter runs the full group in stored order while the selected member stays inspection context",
    )

    single_copy = renderer_mod.CommandOverlayPanel._build_confirm_surface_copy(
        window,
        "",
        {},
    )
    _assert(
        single_copy
        == {
            "title_label": "Resolved action",
            "hint_text": "Review the resolved action origin and destination before execution.",
            "help_text": "Press Enter to confirm or Esc to return.",
        },
        "single-action confirm surface copy should remain unchanged",
    )


def _test_dispatch_routes_group_execution_without_double_launch():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        group = _make_group(source_path)
        window = _make_dispatch_window(source_path)

        original_launch = renderer_mod.launch_command_action
        launched_action_ids = []
        renderer_mod.launch_command_action = lambda action: launched_action_ids.append(action.id)
        try:
            window._command_model.set_input_text("workspace tools")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            match_ids = [match.get("id") for match in window._command_model.view_payload().get("ambiguous_matches") or []]
            selected_index = match_ids.index("open_saved_actions_folder")
            renderer_mod.DesktopRuntimeWindow.handle_ambiguous_match_selected(window, selected_index)
            intent = window._command_model.pending_execution_intent
            _assert(intent is not None, "group chooser selection should bind an execution intent before dispatch")
            _assert(
                intent.execution_type == "group"
                and intent.group_id == "workspace_tools"
                and intent.action_id == "open_saved_actions_folder"
                and intent.resolved_member_action_ids == group.member_action_ids,
                "group execution intent should capture execution type, selected action id, group id, and resolved member order",
            )
            window._command_model.pending_group = None
            window._command_model.pending_action = None
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
        finally:
            renderer_mod.launch_command_action = original_launch

        expected_status_text = 'Group "Workspace Tools" executed in stored order.'
        _assert(
            launched_action_ids == list(group.member_action_ids),
            "dispatch integration should route group execution through the deterministic helper in persisted order",
        )
        _assert(
            window._shown_results[-1] == ("launch_requested", expected_status_text),
            "successful group dispatch should emit group-aware success result text",
        )
        _assert(
            window._prepare_calls == [],
            "successful group dispatch should not populate any recoverable failure payloads",
        )
        _assert(
            len(window._shown_results) == 1,
            "successful group dispatch should emit exactly one result event",
        )
        result_payload = window._command_model.view_payload()
        _assert(
            result_payload["phase"] == "result"
            and result_payload["status_text"] == expected_status_text
            and result_payload["pending_action"] is None
            and result_payload["pending_group"] is None
            and result_payload["selection_context"] == "",
            "successful group dispatch should not retain confirm payload or group context beyond status text",
        )
        _assert(
            any("COMMAND_GROUP_EXECUTION_COMPLETED|group_id=workspace_tools|step_count=3" in event for event in window._events),
            "dispatch integration should log explicit group completion after deterministic execution",
        )
        _assert(
            not any("COMMAND_LAUNCH_REQUEST_SENT|action_id=open_saved_actions_folder" in event for event in window._events),
            "group dispatch should not fall back into the single-action launch path after helper execution",
        )
        parsed_group_events = [_parse_group_event(event) for event in _group_events(window)]
        _assert(
            [marker_name for marker_name, _fields in parsed_group_events][-1] == "GROUP_EXECUTION_COMPLETED",
            "group dispatch should emit terminal group markers only through the deterministic helper",
        )


def _test_dispatch_preserves_single_action_execution_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _make_group(source_path)
        window = _make_dispatch_window(source_path)

        original_launch = renderer_mod.launch_command_action
        launched_action_ids = []
        renderer_mod.launch_command_action = lambda action: launched_action_ids.append(action.id)
        try:
            window._command_model.set_input_text("show reports")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            intent = window._command_model.pending_execution_intent
            _assert(intent is not None, "single-action confirm should bind an execution intent before dispatch")
            _assert(
                intent.execution_type == "single"
                and intent.action_id == "open_reports"
                and not intent.group_id
                and intent.resolved_member_action_ids == (),
                "single-action execution intent should stay single-scoped without group metadata",
            )
            window._command_model.pending_group = object()
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(
            launched_action_ids == ["open_reports"],
            "single-action dispatch should still execute through the original launch path only once",
        )
        _assert(
            window._shown_results[-1] == ("launch_requested", "Launch request sent."),
            "single-action dispatch should preserve the exact existing result copy",
        )
        _assert(
            any("COMMAND_LAUNCH_REQUEST_SENT|action_id=open_reports" in event for event in window._events),
            "single-action dispatch should preserve the existing launch-request marker",
        )
        _assert(
            not _group_events(window),
            "single-action dispatch should not emit group execution markers",
        )
        _assert(
            window._prepare_calls == [],
            "successful single-action dispatch should not populate any recoverable failure payloads",
        )


def _test_dispatch_does_not_reuse_consumed_group_intent_on_success():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        group = _make_group(source_path)
        window = _make_dispatch_window(source_path)
        _freeze_result_state(window)

        original_launch = renderer_mod.launch_command_action
        launched_action_ids = []
        renderer_mod.launch_command_action = lambda action: launched_action_ids.append(action.id)
        try:
            window._command_model.set_input_text("workspace tools")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            renderer_mod.DesktopRuntimeWindow.handle_ambiguous_match_selected(window, 0)
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            _assert(
                window._command_model.phase == "confirm" and window._command_model.pending_execution_intent is None,
                "group intent should be gone immediately after dispatch even if the confirm surface is still present",
            )
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(
            launched_action_ids == list(group.member_action_ids),
            "repeated dispatch attempts must not replay a successfully consumed group intent",
        )
        _assert(
            len([event for event in window._events if "COMMAND_EXECUTION_REQUESTED|" in event]) == 1,
            "group success should emit only one execution-request event for a single consumed intent",
        )
        _assert(
            len(window._shown_results) == 1,
            "group success should surface only one result when the same confirm cycle is submitted twice",
        )


def _test_dispatch_does_not_reuse_consumed_single_intent_on_success():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _make_group(source_path)
        window = _make_dispatch_window(source_path)
        _freeze_result_state(window)

        original_launch = renderer_mod.launch_command_action
        launched_action_ids = []
        renderer_mod.launch_command_action = lambda action: launched_action_ids.append(action.id)
        try:
            window._command_model.set_input_text("show reports")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            _assert(
                window._command_model.pending_execution_intent is not None,
                "single-action confirm should bind intent before the first execution dispatch",
            )
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            _assert(
                window._command_model.phase == "confirm" and window._command_model.pending_execution_intent is None,
                "single-action intent should be gone immediately after dispatch even if the confirm surface is still present",
            )
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(
            launched_action_ids == ["open_reports"],
            "repeated dispatch attempts must not replay a successfully consumed single-action intent",
        )
        _assert(
            len([event for event in window._events if "COMMAND_EXECUTION_REQUESTED|" in event]) == 1,
            "single-action success should emit only one execution-request event for a single consumed intent",
        )
        _assert(
            len(window._shown_results) == 1,
            "single-action success should surface only one result when the same confirm cycle is submitted twice",
        )


def _test_dispatch_group_failure_stops_without_later_execution():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _make_group(source_path)
        window = _make_dispatch_window(source_path)
        _freeze_result_state(window)

        original_launch = renderer_mod.launch_command_action
        launched_action_ids = []

        def _failing_launcher(action):
            launched_action_ids.append(action.id)
            if action.id == "open_saved_actions_folder":
                raise RuntimeError("expected failure")

        renderer_mod.launch_command_action = _failing_launcher
        try:
            window._command_model.set_input_text("workspace tools")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            renderer_mod.DesktopRuntimeWindow.handle_ambiguous_match_selected(window, 0)
            window._command_model.pending_group = None
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            _assert(
                window._command_model.phase == "confirm" and window._command_model.pending_execution_intent is None,
                "group failure should still consume the execution intent before failure handling completes",
            )
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(
            launched_action_ids == ["open_reports", "open_saved_actions_folder"],
            "group dispatch should stop immediately after the first failed member and never launch later steps",
        )
        _assert(
            len(window._prepare_calls) == 1,
            "group dispatch failure should call the shared recoverable failure helper exactly once",
        )
        _assert(
            window._prepare_calls[0]["action_id"] == "open_saved_actions_folder",
            "group dispatch failure should reuse the shared helper with the failing member action id",
        )
        _assert(
            window._prepare_calls[0]["failure_context"]
            == {
                "execution_type": "group",
                "group_id": "workspace_tools",
                "failed_action_id": "open_saved_actions_folder",
                "step_index": "2",
                "error_type": "launch_exception",
                "execution_trace": "open_reports>open_saved_actions_folder",
            },
            "group dispatch failure should pass the complete structured group payload into the shared helper",
        )
        _assert(
            window._prepare_calls[0]["normalized_failure_context"]
            == {
                "execution_type": "group",
                "failed_action_id": "open_saved_actions_folder",
                "group_id": "workspace_tools",
                "step_index": "2",
                "error_type": "launch_exception",
                "execution_trace": "open_reports>open_saved_actions_folder",
            },
            "group dispatch failure should preserve the complete normalized group payload through the shared helper pipeline",
        )
        expected_status_text = 'Group "Workspace Tools" failed at step 2: expected failure'
        _assert(
            window._shown_results[-1] == ("launch_failed", expected_status_text),
            "group dispatch fallback failure should emit group-aware failure result text",
        )
        _assert(
            len([event for event in window._events if "COMMAND_GROUP_EXECUTION_FAILED|" in event]) == 1,
            "group dispatch should emit exactly one explicit group failure event",
        )
        _assert(
            len(window._shown_results) == 1,
            "failed group dispatch should emit exactly one result event",
        )
        _assert(
            any("GROUP_EXECUTION_STEP_FAILED" in event for event in _group_events(window))
            and any("GROUP_EXECUTION_FAILED" in event for event in _group_events(window)),
            "group dispatch failure should emit deterministic step-failure and terminal-failure markers",
        )
        _assert(
            not any("COMMAND_LAUNCH_REQUEST_SENT|action_id=" in event for event in window._events)
            and not any("COMMAND_LAUNCH_FAILED|action_id=" in event for event in window._events),
            "failed group dispatch should not emit single-action launch success or failure events",
        )


def _test_single_action_failure_behavior_remains_unchanged():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _make_group(source_path)
        window = _make_dispatch_window(source_path)
        _freeze_result_state(window)

        original_launch = renderer_mod.launch_command_action

        def _failing_launcher(_action):
            raise RuntimeError("expected single failure")

        renderer_mod.launch_command_action = _failing_launcher
        try:
            window._command_model.set_input_text("show reports")
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            _assert(
                window._command_model.pending_execution_intent is not None,
                "single-action confirm should bind intent before the failure-path dispatch",
            )
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
            _assert(
                window._command_model.phase == "confirm" and window._command_model.pending_execution_intent is None,
                "single-action failure should still consume the execution intent before failure handling completes",
            )
            renderer_mod.DesktopRuntimeWindow.handle_command_submit(window)
        finally:
            renderer_mod.launch_command_action = original_launch

        _assert(
            len(window._prepare_calls) == 1
            and window._prepare_calls[0]["action_id"] == "open_reports"
            and window._prepare_calls[0]["failure_context"] == {},
            "single-action failure dispatch should remain unchanged at the caller boundary",
        )
        _assert(
            window._prepare_calls[0]["normalized_failure_context"]
            == {
                "execution_type": "single",
                "action_id": "open_reports",
                "group_id": "",
                "step_index": "",
                "error_type": "launch_exception",
                "execution_trace": "open_reports",
            },
            "single-action failure should normalize into the same structured payload schema inside the shared helper pipeline",
        )
        _assert(
            any("COMMAND_LAUNCH_FAILED|action_id=open_reports" in event for event in window._events),
            "single-action failure behavior should preserve the existing single-action failure event",
        )
        _assert(
            not any("COMMAND_GROUP_EXECUTION_FAILED|" in event for event in window._events),
            "single-action failure behavior should not emit group failure events",
        )
        _assert(
            window._shown_results[-1] == ("launch_failed", "Launch failed: expected single failure"),
            "single-action failure should preserve the exact existing failure result copy",
        )


def main():
    tests = [
        (
            "result hint text remains unchanged",
            _test_result_hint_text_remains_unchanged,
        ),
        (
            "group result text uses execution intent group name",
            _test_group_result_text_uses_execution_intent_group_name,
        ),
        (
            "group result text is stable under overlay mutation",
            _test_group_result_text_is_stable_under_overlay_mutation,
        ),
        (
            "group result text is not hardcoded",
            _test_group_result_text_is_not_hardcoded,
        ),
        (
            "group execution runs in persisted order with gap-free markers",
            _test_group_execution_runs_in_persisted_order_with_gap_free_markers,
        ),
        (
            "group execution stops on first failure",
            _test_group_execution_stops_on_first_failure_and_reports_terminal_failure,
        ),
        (
            "group execution rejects ambiguous member order",
            _test_group_execution_rejects_ambiguous_member_order,
        ),
        (
            "group execution intent is consumed once before dispatch",
            _test_group_execution_intent_is_consumed_once_before_dispatch,
        ),
        (
            "single execution intent is consumed once before dispatch",
            _test_single_execution_intent_is_consumed_once_before_dispatch,
        ),
        (
            "execution intent clears on cancel and reset",
            _test_execution_intent_clears_on_cancel_and_reset,
        ),
        (
            "confirm surface copy is group-aware only for group context",
            _test_confirm_surface_copy_is_group_aware_only_for_group_context,
        ),
        (
            "dispatch routes group execution without double launch",
            _test_dispatch_routes_group_execution_without_double_launch,
        ),
        (
            "dispatch preserves single-action execution path",
            _test_dispatch_preserves_single_action_execution_path,
        ),
        (
            "dispatch does not reuse consumed group intent on success",
            _test_dispatch_does_not_reuse_consumed_group_intent_on_success,
        ),
        (
            "dispatch does not reuse consumed single intent on success",
            _test_dispatch_does_not_reuse_consumed_single_intent_on_success,
        ),
        (
            "dispatch group failure stops without later execution",
            _test_dispatch_group_failure_stops_without_later_execution,
        ),
        (
            "single-action failure behavior remains unchanged",
            _test_single_action_failure_behavior_remains_unchanged,
        ),
    ]

    for name, fn in tests:
        fn()
        print(f"PASS: {name}")

    print("CALLABLE GROUP EXECUTION VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
