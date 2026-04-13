import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog, QPushButton


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import desktop.desktop_renderer as renderer_mod
from desktop.interaction_overlay_model import CommandOverlayModel
from desktop.shared_action_model import build_default_command_action_catalog


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

    def contains(self, x, y):
        return self._x <= int(x) < (self._x + self._width) and self._y <= int(y) < (self._y + self._height)


class _FakeInputLine:
    def __init__(self):
        self.local_typing_enabled = False

    def set_local_typing_enabled(self, enabled: bool):
        self.local_typing_enabled = bool(enabled)


class _FakePanel:
    def __init__(self):
        self.input_line = _FakeInputLine()
        self.visible = True
        self.last_payload = None
        self.refresh_for_geometry_calls = 0

    def render_payload(self, payload):
        self.last_payload = payload

    def isVisible(self):
        return self.visible

    def refresh_for_geometry(self, *_args, **_kwargs):
        self.refresh_for_geometry_calls += 1


def _make_window(source_path: Path):
    window = renderer_mod.DesktopRuntimeWindow.__new__(renderer_mod.DesktopRuntimeWindow)
    window.screen_ref = SimpleNamespace(availableGeometry=lambda: _FakeRect())
    window.compute_compact_geometry = lambda: _FakeRect()
    window._is_shutting_down = False
    window._overlay_trace_enabled = False
    window._saved_action_source_path = source_path
    window._saved_action_create_dialog_factory = None
    window._saved_action_edit_dialog_factory = None
    window._command_model = CommandOverlayModel(action_catalog=build_default_command_action_catalog(source_path))
    window._command_panel = _FakePanel()
    window._overlay_input_capture_until = 0.0
    window._overlay_local_input_engaged = False
    window._overlay_global_capture_suspended = False
    window._trace_overlay = lambda *_args, **_kwargs: None
    window._log_event = lambda *_args, **_kwargs: None
    window._command_model.open(arm_input=True)
    renderer_mod.DesktopRuntimeWindow._apply_command_overlay_state(window)
    return window


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


def _test_create_trigger_is_present_and_clickable():
    _app()
    panel = renderer_mod.CommandOverlayPanel()
    payload = {
        "visible": True,
        "phase": "entry",
        "input_armed": True,
        "input_text": "",
        "status_kind": "idle",
        "status_text": "",
        "typed_request": "",
        "pending_action": None,
        "ambiguous_titles": [],
        "ambiguous_matches": [],
        "saved_action_inventory": {
            "visible": True,
            "status_kind": "template_only",
            "status_text": "No saved actions are active yet.",
            "guidance_text": 'Use "Open Saved Actions File" or "Open Saved Actions Folder" to inspect the source.',
            "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "count": 0,
            "items": [],
        },
    }
    fired = []
    panel.create_custom_task_requested.connect(lambda: fired.append("clicked"))
    panel.render_payload(payload)
    panel.create_custom_task_button.click()

    _assert(
        panel.create_custom_task_button.text() == "Create Custom Task",
        "entry-state UI should expose a Create Custom Task trigger",
    )
    _assert(fired == ["clicked"], "Create Custom Task trigger should be reachable and clickable")


def _test_edit_trigger_is_present_and_clickable_for_saved_inventory_items():
    _app()
    panel = renderer_mod.CommandOverlayPanel()
    payload = {
        "visible": True,
        "phase": "entry",
        "input_armed": True,
        "input_text": "",
        "status_kind": "idle",
        "status_text": "",
        "typed_request": "",
        "pending_action": None,
        "ambiguous_titles": [],
        "ambiguous_matches": [],
        "saved_action_inventory": {
            "visible": True,
            "status_kind": "loaded",
            "status_text": "1 saved action is available.",
            "guidance_text": 'Use "Open Saved Actions File" or "Open Saved Actions Folder" to inspect the source.',
            "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "count": 1,
            "items": [
                {
                    "id": "open_reports",
                    "title": "Open Reports",
                    "origin": "saved",
                    "origin_label": "Saved",
                    "target_kind": "folder",
                    "target": r"C:\Reports",
                    "target_display": r"C:\Reports",
                }
            ],
        },
    }
    fired = []
    panel.edit_saved_action_requested.connect(lambda action_id: fired.append(action_id))
    panel.render_payload(payload)
    edit_buttons = [
        button
        for button in panel.saved_inventory_items_frame.findChildren(QPushButton)
        if button.text() == "Edit"
    ]

    _assert(edit_buttons, "saved inventory items should expose an Edit trigger")
    edit_buttons[0].click()
    _assert(
        fired == ["open_reports"],
        "saved inventory edit trigger should be reachable and emit the selected saved-action id",
    )


def _test_saved_inventory_edit_reachability_extends_beyond_six_items():
    _app()
    panel = renderer_mod.CommandOverlayPanel()
    items = []
    for index in range(1, 9):
        items.append(
            {
                "id": f"open_reports_{index}",
                "title": f"Open Reports {index}",
                "origin": "saved",
                "origin_label": "Saved",
                "target_kind": "folder",
                "target": fr"C:\Reports\{index}",
                "target_display": fr"C:\Reports\{index}",
            }
        )

    payload = {
        "visible": True,
        "phase": "entry",
        "input_armed": True,
        "input_text": "",
        "status_kind": "idle",
        "status_text": "",
        "typed_request": "",
        "pending_action": None,
        "ambiguous_titles": [],
        "ambiguous_matches": [],
        "saved_action_inventory": {
            "visible": True,
            "status_kind": "loaded",
            "status_text": "8 saved actions are available.",
            "guidance_text": 'Use "Open Saved Actions File" or "Open Saved Actions Folder" to inspect the source.',
            "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "count": 8,
            "items": items,
        },
    }
    fired = []
    panel.edit_saved_action_requested.connect(lambda action_id: fired.append(action_id))
    panel.render_payload(payload)

    edit_buttons = [
        button
        for button in panel.saved_inventory_items_frame.findChildren(QPushButton)
        if button.text() == "Edit"
    ]

    _assert(
        not panel.saved_inventory_items_scroll.isHidden(),
        "saved inventory should keep its scroll container enabled when many saved actions are present",
    )
    _assert(
        len(edit_buttons) == 8,
        "saved inventory should expose edit reachability for every saved action, not just the first six",
    )

    edit_buttons[-1].click()
    _assert(
        fired == ["open_reports_8"],
        "saved inventory should preserve stable edit-button mapping for items beyond the previous six-item cap",
    )


def _test_type_first_dialog_maps_all_supported_kinds():
    _app()
    dialog = renderer_mod.SavedActionCreateDialog()

    cases = [
        ("Application", "app", "notepad.exe"),
        ("Folder", "folder", r"C:\Reports"),
        ("File", "file", r"C:\Reports\weekly.txt"),
        ("Website URL", "url", "https://example.com/docs"),
    ]

    for index, (label, target_kind, target) in enumerate(cases, start=1):
        dialog.type_combo.setCurrentText(label)
        dialog.title_input.setText(f"Task {index}")
        dialog.aliases_input.setText("alpha, beta")
        dialog.target_input.setText(target)
        draft = dialog.build_draft()

        _assert(
            draft.target_kind == target_kind,
            f"type-first dialog should map {label} directly to {target_kind}",
        )
        _assert(draft.target == target, "type-first dialog should preserve the entered target")
        _assert(draft.aliases == ("alpha", "beta"), "type-first dialog should parse comma-separated aliases")


def _test_successful_create_flow_reloads_inventory_immediately():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        window = _make_window(source_path)
        dialog_instances = []
        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Folder"),
                    dialog.title_input.setText("Open Reports"),
                    dialog.aliases_input.setText("view reports"),
                    dialog.target_input.setText(r"C:\Reports"),
                ),
                dialog_instances,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)

        inventory = window._command_model.view_payload().get("saved_action_inventory") or {}
        items = inventory.get("items") or []

        _assert(dialog_instances, "successful create flow should open the create dialog")
        _assert(window._command_model.phase == "entry", "successful create flow should preserve entry phase")
        _assert(window._command_model.status_kind == "ready", "successful create flow should surface success feedback")
        _assert(inventory.get("count") == 1, "successful create flow should reload inventory immediately")
        _assert(items and items[0].get("title") == "Open Reports", "successful create flow should surface the new saved action immediately")
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "successful create flow should restore fallback input capture readiness",
        )


def _test_invalid_input_shows_dialog_error_and_does_not_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        window = _make_window(source_path)
        dialog_instances = []
        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Website URL"),
                    dialog.title_input.setText(""),
                    dialog.aliases_input.setText("view docs"),
                    dialog.target_input.setText("https://example.com/docs"),
                ),
                dialog_instances,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)

        _assert(dialog_instances, "invalid input path should still open the create dialog")
        _assert(
            "title" in dialog_instances[0].status_label.text().casefold(),
            "invalid input should surface a clear validation error inside the dialog",
        )
        _assert(
            not source_path.exists(),
            "invalid input should not write the saved-action source",
        )
        _assert(window._command_model.phase == "entry", "invalid input should preserve entry phase")
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "invalid input should still restore fallback input capture readiness after the dialog path",
        )


def _test_invalid_folder_target_shows_dialog_error_and_does_not_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        window = _make_window(source_path)
        dialog_instances = []
        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Folder"),
                    dialog.title_input.setText("Open Reports"),
                    dialog.aliases_input.setText("view reports"),
                    dialog.target_input.setText(r"Reports\Daily"),
                ),
                dialog_instances,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)

        _assert(dialog_instances, "invalid folder targets should still open the create dialog")
        _assert(
            "absolute windows paths" in dialog_instances[0].status_label.text().casefold(),
            "invalid folder targets should surface a clear path-structure error inside the dialog",
        )
        _assert(
            not source_path.exists(),
            "invalid folder targets should not write the saved-action source",
        )
        _assert(window._command_model.phase == "entry", "invalid folder targets should preserve entry phase")
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "invalid folder targets should still restore fallback input capture readiness",
        )


def _test_invalid_application_target_shows_dialog_error_and_does_not_write():
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
                    dialog.title_input.setText("Open Debug Notepad"),
                    dialog.aliases_input.setText("debug notepad"),
                    dialog.target_input.setText("notepad.exe --help"),
                ),
                dialog_instances,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)

        _assert(dialog_instances, "invalid application targets should still open the create dialog")
        _assert(
            "bare command like notepad.exe" in dialog_instances[0].status_label.text().casefold(),
            "invalid application targets should surface a clear application-target format error",
        )
        _assert(
            not source_path.exists(),
            "invalid application targets should not write the saved-action source",
        )
        _assert(window._command_model.phase == "entry", "invalid application targets should preserve entry phase")
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "invalid application targets should still restore fallback input capture readiness",
        )


def _test_invalid_file_target_shows_dialog_error_and_does_not_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        window = _make_window(source_path)
        dialog_instances = []
        window._saved_action_create_dialog_factory = (
            lambda parent, submit_handler: _AutoSubmitCreateDialog(
                None,
                submit_handler,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("File"),
                    dialog.title_input.setText("Open Weekly Report"),
                    dialog.aliases_input.setText("weekly report"),
                    dialog.target_input.setText(r"C:\Reports\bad?.txt"),
                ),
                dialog_instances,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)

        _assert(dialog_instances, "invalid file targets should still open the create dialog")
        _assert(
            "illegal windows path characters" in dialog_instances[0].status_label.text().casefold(),
            "invalid file targets should surface a clear path-structure error inside the dialog",
        )
        _assert(
            not source_path.exists(),
            "invalid file targets should not write the saved-action source",
        )
        _assert(window._command_model.phase == "entry", "invalid file targets should preserve entry phase")
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "invalid file targets should still restore fallback input capture readiness",
        )


def _test_unsafe_source_blocks_before_dialog_open():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        source_path.write_text("{ not valid json", encoding="utf-8")
        window = _make_window(source_path)
        opened = []
        window._saved_action_create_dialog_factory = lambda *_args, **_kwargs: opened.append(True)

        renderer_mod.DesktopRuntimeWindow.handle_create_custom_task_requested(window)

        _assert(not opened, "unsafe saved-action sources should block the dialog before create begins")
        _assert(window._command_model.phase == "entry", "unsafe-source block should preserve entry phase")
        _assert(window._command_model.status_kind == "not_found", "unsafe-source block should surface explicit feedback")
        _assert(
            "blocked" in window._command_model.status_text.casefold(),
            "unsafe-source block should explain that custom task creation is blocked",
        )
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "unsafe-source block should leave fallback input capture available for continued entry-state use",
        )


def _test_successful_edit_flow_loads_existing_values_and_reloads_inventory():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        source_path.write_text(
            """{
  "schema_version": 1,
  "actions": [
    {
      "id": "open_reports",
      "title": "Open Reports",
      "target_kind": "folder",
      "target": "C:\\\\Reports",
      "aliases": ["show reports"]
    }
  ]
}
""",
            encoding="utf-8",
        )
        window = _make_window(source_path)
        dialog_instances = []
        window._saved_action_edit_dialog_factory = (
            lambda parent, submit_handler, initial_draft: _AutoSubmitEditDialog(
                None,
                submit_handler,
                initial_draft,
                lambda dialog: (
                    _assert(dialog.title_input.text() == "Open Reports", "edit dialog should preload the current title"),
                    _assert(dialog.current_target_kind() == "folder", "edit dialog should preload the current target kind"),
                    _assert(dialog.target_input.text() == r"C:\Reports", "edit dialog should preload the current target"),
                    _assert(dialog.aliases_input.text() == "show reports", "edit dialog should preload current aliases"),
                    dialog.type_combo.setCurrentText("File"),
                    dialog.title_input.setText("Open Weekly Reports"),
                    dialog.aliases_input.setText("weekly reports"),
                    dialog.target_input.setText(r"C:\Reports\weekly.txt"),
                ),
                dialog_instances,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_edit_saved_action_requested(window, "open_reports")

        inventory = window._command_model.view_payload().get("saved_action_inventory") or {}
        items = inventory.get("items") or []

        _assert(dialog_instances, "successful edit flow should open the edit dialog")
        _assert(window._command_model.phase == "entry", "successful edit flow should preserve entry phase")
        _assert(window._command_model.status_kind == "ready", "successful edit flow should surface success feedback")
        _assert(inventory.get("count") == 1, "successful edit flow should preserve inventory count")
        _assert(items and items[0].get("id") == "open_reports", "successful edit flow should preserve the action id")
        _assert(
            items and items[0].get("title") == "Open Weekly Reports",
            "successful edit flow should surface the updated title immediately",
        )
        _assert(
            items and items[0].get("target_kind") == "file",
            "successful edit flow should surface the updated target kind immediately",
        )
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "successful edit flow should restore fallback input capture readiness",
        )


def _test_invalid_edit_input_shows_dialog_error_and_does_not_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        source_path.write_text(
            """{
  "schema_version": 1,
  "actions": [
    {
      "id": "open_docs",
      "title": "Open Knowledge Base",
      "target_kind": "url",
      "target": "https://example.com/knowledge",
      "aliases": ["show knowledge base"]
    }
  ]
}
""",
            encoding="utf-8",
        )
        original_text = source_path.read_text(encoding="utf-8")
        window = _make_window(source_path)
        dialog_instances = []
        window._saved_action_edit_dialog_factory = (
            lambda parent, submit_handler, initial_draft: _AutoSubmitEditDialog(
                None,
                submit_handler,
                initial_draft,
                lambda dialog: (
                    dialog.type_combo.setCurrentText("Website URL"),
                    dialog.title_input.setText("Open Knowledge Base"),
                    dialog.aliases_input.setText("show knowledge base"),
                    dialog.target_input.setText("example.com/docs"),
                ),
                dialog_instances,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_edit_saved_action_requested(window, "open_docs")

        _assert(dialog_instances, "invalid edit input path should still open the edit dialog")
        _assert(
            "absolute http or https url" in dialog_instances[0].status_label.text().casefold(),
            "invalid edit input should surface a clear dialog error",
        )
        _assert(
            source_path.read_text(encoding="utf-8") == original_text,
            "invalid edit input should not write the saved-action source",
        )
        _assert(window._command_model.phase == "entry", "invalid edit input should preserve entry phase")
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "invalid edit input should still restore fallback input capture readiness",
        )


def _test_unsafe_source_blocks_edit_before_dialog_open():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        source_path.write_text("{ not valid json", encoding="utf-8")
        window = _make_window(source_path)
        opened = []
        window._saved_action_edit_dialog_factory = lambda *_args, **_kwargs: opened.append(True)

        renderer_mod.DesktopRuntimeWindow.handle_edit_saved_action_requested(window, "open_reports")

        _assert(not opened, "unsafe saved-action sources should block the edit dialog before edit begins")
        _assert(window._command_model.phase == "entry", "unsafe edit block should preserve entry phase")
        _assert(window._command_model.status_kind == "not_found", "unsafe edit block should surface explicit feedback")
        _assert(
            "blocked" in window._command_model.status_text.casefold(),
            "unsafe edit block should explain that custom task editing is blocked",
        )
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "unsafe edit block should leave fallback input capture available for continued entry-state use",
        )


def main():
    tests = [
        ("create trigger present and clickable", _test_create_trigger_is_present_and_clickable),
        ("edit trigger present and clickable", _test_edit_trigger_is_present_and_clickable_for_saved_inventory_items),
        ("edit reachability extends beyond six items", _test_saved_inventory_edit_reachability_extends_beyond_six_items),
        ("type-first dialog maps supported kinds", _test_type_first_dialog_maps_all_supported_kinds),
        ("successful create flow reloads inventory", _test_successful_create_flow_reloads_inventory_immediately),
        ("invalid input shows dialog error without write", _test_invalid_input_shows_dialog_error_and_does_not_write),
        ("invalid folder target shows dialog error without write", _test_invalid_folder_target_shows_dialog_error_and_does_not_write),
        ("invalid application target shows dialog error without write", _test_invalid_application_target_shows_dialog_error_and_does_not_write),
        ("invalid file target shows dialog error without write", _test_invalid_file_target_shows_dialog_error_and_does_not_write),
        ("unsafe source blocks before dialog open", _test_unsafe_source_blocks_before_dialog_open),
        ("successful edit flow reloads inventory", _test_successful_edit_flow_loads_existing_values_and_reloads_inventory),
        ("invalid edit input shows dialog error without write", _test_invalid_edit_input_shows_dialog_error_and_does_not_write),
        ("unsafe source blocks edit before dialog open", _test_unsafe_source_blocks_edit_before_dialog_open),
    ]

    for name, fn in tests:
        fn()
        print(f"PASS: {name}")

    print("SAVED ACTION AUTHORING UI VALIDATION: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
