import datetime as _dt
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication


CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import desktop.desktop_renderer as renderer_mod
from desktop.interaction_overlay_model import CommandOverlayModel
from desktop.shared_action_model import build_default_command_action_catalog


LOG_ROOT = ROOT_DIR / "dev" / "logs" / "fb_036_authoring_live_validation"
REPORTS_DIR = LOG_ROOT / "reports"
ARTIFACTS_DIR = LOG_ROOT / "artifacts"


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _app():
    return QApplication.instance() or QApplication([])


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


class _HarnessInputLine:
    def __init__(self):
        self.local_typing_enabled = False

    def set_local_typing_enabled(self, enabled: bool):
        self.local_typing_enabled = bool(enabled)

    def hasFocus(self):
        return False


class _HarnessPanel:
    def __init__(self):
        self.input_line = _HarnessInputLine()
        self.visible = False
        self.last_payload = None
        self.refresh_for_geometry_calls = 0

    def render_payload(self, payload):
        self.last_payload = payload

    def isVisible(self):
        return self.visible

    def refresh_for_geometry(self, *_args, **_kwargs):
        self.refresh_for_geometry_calls += 1

    def show_for_geometry(self, *_args, **_kwargs):
        self.visible = True

    def focus_input_after_show(self):
        return

    def hide(self):
        self.visible = False


class _AutoSubmitCreateDialog(renderer_mod.SavedActionCreateDialog):
    def __init__(self, parent, submit_handler, configure, sink):
        super().__init__(parent, submit_handler)
        self._configure = configure
        self._sink = sink
        self._sink.append(self)

    def exec(self):
        self._configure(self)
        self._handle_create_clicked()
        return self.result()


class _AutoSubmitEditDialog(renderer_mod.SavedActionEditDialog):
    def __init__(self, parent, submit_handler, initial_draft, configure, sink):
        super().__init__(parent, submit_handler, initial_draft=initial_draft)
        self._configure = configure
        self._sink = sink
        self._sink.append(self)

    def exec(self):
        self._configure(self)
        self._handle_create_clicked()
        return self.result()


class _AutoSelectCreatedTasksDialog(renderer_mod.CreatedTasksDialog):
    def __init__(self, parent, inventory_payload, configure, sink):
        super().__init__(parent, inventory_payload)
        self._configure = configure
        self._sink = sink
        self._sink.append(self)

    def exec(self):
        self._configure(self)
        return self.result()


def _make_window(source_path: Path):
    window = renderer_mod.DesktopRuntimeWindow.__new__(renderer_mod.DesktopRuntimeWindow)
    window.screen_ref = SimpleNamespace(availableGeometry=lambda: _FakeRect())
    window.compute_compact_geometry = lambda: _FakeRect()
    window._is_shutting_down = False
    window._overlay_trace_enabled = False
    window._saved_action_source_path = source_path
    window._saved_action_create_dialog_factory = None
    window._created_tasks_dialog_factory = None
    window._saved_action_edit_dialog_factory = None
    window._result_close_timer = SimpleNamespace(stop=lambda: None)
    window._overlay_input_capture_until = 0.0
    window._overlay_local_input_engaged = False
    window._overlay_global_capture_suspended = False
    window._command_model = CommandOverlayModel(action_catalog=build_default_command_action_catalog(source_path))
    window._command_panel = _HarnessPanel()
    window._events = []
    window._trace_overlay = lambda *_args, **_kwargs: None
    window._log_event = lambda event: window._events.append(event)
    renderer_mod.DesktopRuntimeWindow.open_command_overlay(window)
    return window


def _payload(window):
    return window._command_model.view_payload()


def _inventory_items(window):
    return (_payload(window).get("saved_action_inventory") or {}).get("items") or []


def _copy_artifact(source_path: Path, stamp: str, slug: str) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = ARTIFACTS_DIR / f"{stamp}_{slug}.json"
    shutil.copyfile(source_path, artifact_path)
    return artifact_path


def _run_create_edit_reopen_cycle(stamp: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        window = _make_window(source_path)
        create_dialogs = []
        edit_dialogs = []
        created_tasks_dialogs = []

        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Folder"),
                    dialog.title_input.setText("Open Reports"),
                    dialog.aliases_input.setText("show reports"),
                    dialog.target_input.setText(r"C:\Reports"),
                ),
                create_dialogs,
            )
        )
        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)
        first_inventory = _inventory_items(window)
        _assert(create_dialogs, "create flow should open the create dialog")
        _assert(len(first_inventory) == 1, "create flow should produce one saved action immediately")
        _assert(first_inventory[0].get("title") == "Open Reports", "create flow should surface the created title immediately")

        renderer_mod.DesktopRuntimeWindow.close_command_overlay(window)
        renderer_mod.DesktopRuntimeWindow.open_command_overlay(window)
        reopened_payload = _payload(window)
        _assert(reopened_payload.get("phase") == "entry", "overlay should reopen into entry state")
        _assert(not reopened_payload.get("status_text"), "overlay reopen should not preserve stale status text")
        _assert((_inventory_items(window) or [{}])[0].get("title") == "Open Reports", "created item should persist after reopen")

        window._saved_action_edit_dialog_factory = (
            lambda parent, submit_handler, initial_draft: _AutoSubmitEditDialog(
                None,
                submit_handler,
                initial_draft,
                lambda dialog: (
                    _assert(dialog.title_input.text() == "Open Reports", "edit dialog should preload the current title"),
                    dialog.type_combo.setCurrentText("File"),
                    dialog.title_input.setText("Open Weekly Reports"),
                    dialog.aliases_input.setText("show weekly reports"),
                    dialog.target_input.setText(r"C:\Reports\weekly.txt"),
                ),
                edit_dialogs,
            )
        )
        window._created_tasks_dialog_factory = (
            lambda parent, inventory_payload: _AutoSelectCreatedTasksDialog(
                None,
                inventory_payload,
                lambda dialog: dialog._handle_edit_requested("open_reports"),
                created_tasks_dialogs,
            )
        )
        renderer_mod.DesktopRuntimeWindow.handle_created_tasks_requested(window)
        edited_inventory = _inventory_items(window)
        _assert(created_tasks_dialogs, "Created Tasks navigation should open before edit in the live-style harness")
        _assert(edit_dialogs, "edit flow should open the edit dialog")
        _assert(len(edited_inventory) == 1, "edit should preserve inventory count")
        _assert(edited_inventory[0].get("id") == "open_reports", "edit should preserve saved-action identity")
        _assert(edited_inventory[0].get("title") == "Open Weekly Reports", "edit should update the visible title immediately")

        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Application"),
                    dialog.title_input.setText("Open Notepad"),
                    dialog.aliases_input.setText("start notepad"),
                    dialog.target_input.setText("notepad.exe"),
                ),
                create_dialogs,
            )
        )
        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)
        second_inventory = _inventory_items(window)
        _assert(len(second_inventory) == 2, "second create should keep repeated create/edit cycles stable")

        renderer_mod.DesktopRuntimeWindow.close_command_overlay(window)
        renderer_mod.DesktopRuntimeWindow.open_command_overlay(window)
        reopened_again = _payload(window)
        _assert(reopened_again.get("phase") == "entry", "second reopen should still enter clean entry state")
        _assert(not reopened_again.get("typed_request"), "reopen should not preserve stale typed request")
        _assert(len(_inventory_items(window)) == 2, "saved actions should persist across repeated reopen cycles")

        artifact_path = _copy_artifact(source_path, stamp, "create_edit_reopen_cycle_saved_actions")
        event_markers = [event for event in window._events if "CUSTOM_TASK_" in event]
        _assert(any("CUSTOM_TASK_CREATED" in event for event in event_markers), "event evidence should include custom task creation")
        _assert(any("CUSTOM_TASK_UPDATED" in event for event in event_markers), "event evidence should include custom task update")
        return {
            "artifact_path": artifact_path,
            "event_markers": event_markers,
            "final_titles": [item.get("title") for item in _inventory_items(window)],
            "created_tasks_navigation": True,
        }


def _run_invalid_and_collision_paths():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        window = _make_window(source_path)
        dialog_instances = []

        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Application"),
                    dialog.title_input.setText("Bad App"),
                    dialog.aliases_input.setText("bad app"),
                    dialog.target_input.setText("notepad.exe --help"),
                ),
                dialog_instances,
            )
        )
        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)
        _assert(dialog_instances, "invalid app path should still open the create dialog")
        _assert(
            bool((dialog_instances[-1].status_label.text() or "").strip()),
            "invalid app targets should surface a non-empty blocking dialog error",
        )
        _assert(not source_path.exists(), "invalid app targets should not write the source")

        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Application"),
                    dialog.title_input.setText("Explorer Helper"),
                    dialog.aliases_input.setText("open windows explorer"),
                    dialog.target_input.setText("explorer.exe"),
                ),
                dialog_instances,
            )
        )
        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)
        _assert(
            bool((dialog_instances[-1].status_label.text() or "").strip()),
            "built-in collisions should surface a non-empty blocking dialog error",
        )
        _assert(not source_path.exists(), "collision paths should not write the source")

        return {
            "invalid_app_error": dialog_instances[-2].status_label.text(),
            "builtin_collision_error": dialog_instances[-1].status_label.text(),
        }


def _run_trigger_phrase_resolution():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        window = _make_window(source_path)
        dialog_instances = []

        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Application"),
                    dialog.title_input.setText("Open Nexus"),
                    dialog.aliases_input.setText("Nexus, NDAI"),
                    dialog.trigger_combo.setCurrentText("Launch and Open"),
                    dialog.target_input.setText("notepad.exe"),
                ),
                dialog_instances,
            )
        )
        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)

        _assert(dialog_instances, "trigger phrase validation should still open the create dialog")
        inventory = _inventory_items(window)
        _assert(len(inventory) == 1, "trigger phrase validation should create one saved action")

        catalog = window._command_model.action_catalog
        expected_id = inventory[0].get("id")
        for phrase in ("Nexus", "NDAI", "Open Nexus", "Launch Nexus", "Open NDAI", "Launch NDAI"):
            matches = catalog.resolve_actions(phrase)
            _assert(
                tuple(action.id for action in matches) == (expected_id,),
                f"live validation should resolve '{phrase}' through the reloaded catalog",
            )
        _assert(
            tuple(action.id for action in catalog.resolve_actions("Open Open Nexus")) == (),
            "live validation should confirm new tasks do not generate trigger phrases from the title label",
        )

        return {
            "action_id": expected_id,
            "trigger_mode": catalog.actions[-1].trigger_mode,
            "resolved_phrases": ["Nexus", "NDAI", "Open Nexus", "Launch Nexus", "Open NDAI", "Launch NDAI"],
        }


def _run_unsafe_source_blocking():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        source_path.write_text("{ not valid json", encoding="utf-8")
        original_text = source_path.read_text(encoding="utf-8")
        window = _make_window(source_path)
        create_opened = []
        edit_opened = []
        window._saved_action_create_dialog_factory = lambda *_args, **_kwargs: create_opened.append(True)
        window._saved_action_edit_dialog_factory = lambda *_args, **_kwargs: edit_opened.append(True)

        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)
        create_status = window._command_model.status_text
        renderer_mod.DesktopRuntimeWindow.handle_edit_saved_action_requested(window, "missing_action")
        edit_status = window._command_model.status_text

        _assert(not create_opened, "unsafe source should block the create dialog before open")
        _assert(not edit_opened, "unsafe source should block the edit dialog before open")
        _assert("blocked" in create_status.casefold(), "unsafe source should surface blocked create feedback")
        _assert("blocked" in edit_status.casefold(), "unsafe source should surface blocked edit feedback")
        _assert(source_path.read_text(encoding="utf-8") == original_text, "unsafe source should remain untouched")

        return {
            "create_status": create_status,
            "edit_status": edit_status,
            "event_markers": [event for event in window._events if "CUSTOM_TASK_" in event],
        }


def _run_large_inventory_late_edit(stamp: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        actions = []
        for index in range(1, 9):
            actions.append(
                {
                    "id": f"open_reports_{index}",
                    "title": f"Open Reports {index}",
                    "target_kind": "folder",
                    "target": fr"C:\Reports\{index}",
                    "aliases": [f"show reports {index}"],
                }
            )
        source_path.write_text(json.dumps({"schema_version": 1, "actions": actions}, indent=2) + "\n", encoding="utf-8")

        window = _make_window(source_path)
        edit_dialogs = []
        created_tasks_dialogs = []
        window._created_tasks_dialog_factory = (
            lambda parent, inventory_payload: _AutoSelectCreatedTasksDialog(
                None,
                inventory_payload,
                lambda dialog: dialog._handle_edit_requested("open_reports_8"),
                created_tasks_dialogs,
            )
        )
        window._saved_action_edit_dialog_factory = (
            lambda parent, submit_handler, initial_draft: _AutoSubmitEditDialog(
                None,
                submit_handler,
                initial_draft,
                lambda dialog: (
                    _assert(dialog.title_input.text() == "Open Reports 8", "late inventory edit should load the intended item"),
                    dialog.type_combo.setCurrentText("Folder"),
                    dialog.title_input.setText("Open Reports Eight"),
                    dialog.aliases_input.setText("show reports eight"),
                    dialog.target_input.setText(r"C:\Reports\8"),
                ),
                edit_dialogs,
            )
        )
        renderer_mod.DesktopRuntimeWindow.handle_created_tasks_requested(window)
        inventory = _inventory_items(window)
        late_item = next(item for item in inventory if item.get("id") == "open_reports_8")
        _assert(created_tasks_dialogs, "large-inventory late edit should pass through the Created Tasks dialog")
        _assert(edit_dialogs, "late inventory items should still open the edit dialog")
        _assert(late_item.get("title") == "Open Reports Eight", "late inventory edit should update the intended item")
        artifact_path = _copy_artifact(source_path, stamp, "large_inventory_late_edit_saved_actions")
        return {
            "artifact_path": artifact_path,
            "late_item_title": late_item.get("title"),
        }


def _run_delete_flow(stamp: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        source_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "actions": [
                        {
                            "id": "open_reports",
                            "title": "Open Reports",
                            "target_kind": "folder",
                            "target": r"C:\Reports",
                            "aliases": ["show reports"],
                        },
                        {
                            "id": "knowledge_pages",
                            "title": "Knowledge Pages",
                            "target_kind": "url",
                            "target": "https://example.com/docs",
                            "aliases": ["knowledge pages"],
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        window = _make_window(source_path)
        created_tasks_dialogs = []
        window._created_tasks_dialog_factory = (
            lambda parent, inventory_payload: _AutoSelectCreatedTasksDialog(
                None,
                inventory_payload,
                lambda dialog: dialog._handle_delete_requested("open_reports"),
                created_tasks_dialogs,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_created_tasks_requested(window)
        inventory = _inventory_items(window)
        artifact_path = _copy_artifact(source_path, stamp, "delete_flow_saved_actions")

        _assert(created_tasks_dialogs, "delete flow should pass through the Created Tasks dialog")
        _assert(len(inventory) == 1, "delete flow should remove one saved action from inventory")
        _assert(
            tuple(item.get("id") for item in inventory) == ("knowledge_pages",),
            "delete flow should preserve the remaining saved action in inventory order",
        )
        _assert(
            any("CUSTOM_TASK_DELETED" in event for event in window._events),
            "delete flow should emit deletion evidence in the live event log",
        )

        return {
            "artifact_path": artifact_path,
            "remaining_ids": [item.get("id") for item in inventory],
            "event_markers": [event for event in window._events if "CUSTOM_TASK_" in event],
        }


def _write_report(report_path: Path, *, checks: list[tuple[str, str]], details: dict[str, object]):
    lines = [
        "FB-036 SAVED-ACTION AUTHORING LIVE VALIDATION",
        f"Report: {report_path}",
        f"Timestamp: {_dt.datetime.now().isoformat(timespec='seconds')}",
        "",
        "Checks:",
    ]
    for name, status in checks:
        lines.append(f"  {status} :: {name}")
    lines.extend(
        [
            "",
            "Evidence:",
            json.dumps(details, indent=2, default=str),
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    _app()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"FB036SavedActionAuthoringLiveValidationReport_{stamp}.txt"
    checks: list[tuple[str, str]] = []
    details: dict[str, object] = {}

    try:
        details["create_edit_reopen_cycle"] = _run_create_edit_reopen_cycle(stamp)
        checks.append(("create/edit/reopen cycle", "PASS"))

        details["invalid_and_collision_paths"] = _run_invalid_and_collision_paths()
        checks.append(("invalid target and collision rejection", "PASS"))

        details["trigger_phrase_resolution"] = _run_trigger_phrase_resolution()
        checks.append(("trigger phrase resolution", "PASS"))

        details["unsafe_source_blocking"] = _run_unsafe_source_blocking()
        checks.append(("unsafe source blocking", "PASS"))

        details["large_inventory_late_edit"] = _run_large_inventory_late_edit(stamp)
        checks.append(("large inventory late-item edit", "PASS"))

        details["delete_flow"] = _run_delete_flow(stamp)
        checks.append(("delete flow through Created Tasks", "PASS"))
    except Exception as exc:
        checks.append(("live validation", f"FAIL ({exc})"))
        details["failure"] = repr(exc)
        _write_report(report_path, checks=checks, details=details)
        print("FB-036 SAVED-ACTION AUTHORING LIVE VALIDATION: FAIL")
        print(f"Report: {report_path}")
        raise

    _write_report(report_path, checks=checks, details=details)
    print("FB-036 SAVED-ACTION AUTHORING LIVE VALIDATION: PASS")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
