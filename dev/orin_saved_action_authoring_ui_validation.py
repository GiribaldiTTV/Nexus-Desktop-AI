import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog, QFrame, QLabel, QPushButton, QToolButton
from PySide6.QtCore import Qt


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


def _flush_qt_events():
    app = _app()
    app.processEvents()
    app.processEvents()


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
        self.visible = True
        self.enabled = True
        self.focused = False

    def set_local_typing_enabled(self, enabled: bool):
        self.local_typing_enabled = bool(enabled)

    def hasFocus(self):
        return self.focused

    def isVisible(self):
        return self.visible

    def isEnabled(self):
        return self.enabled


class _FakeVisibleControl:
    def __init__(self, visible: bool = True):
        self.visible = visible

    def isVisible(self):
        return self.visible


class _FakePanel:
    def __init__(self):
        self.input_line = _FakeInputLine()
        self.create_custom_task_button = _FakeVisibleControl()
        self.created_tasks_button = _FakeVisibleControl()
        self.create_custom_group_button = _FakeVisibleControl()
        self.created_groups_button = _FakeVisibleControl()
        self.visible = True
        self._width = 720
        self._height = 420
        self.last_payload = None
        self.refresh_for_geometry_calls = 0

    def render_payload(self, payload):
        self.last_payload = payload

    def isVisible(self):
        return self.visible

    def isActiveWindow(self):
        return True

    def width(self):
        return self._width

    def height(self):
        return self._height

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
    window._created_tasks_dialog_factory = None
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


class _AutoSelectCreatedTasksDialog(renderer_mod.CreatedTasksDialog):
    def __init__(self, parent, inventory_payload, configure, sink):
        super().__init__(parent, inventory_payload)
        self._configure = configure
        self._sink = sink
        self._sink.append(self)

    def exec(self):
        self._configure(self)
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


def _test_created_tasks_trigger_is_present_and_clickable():
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
    panel.created_tasks_requested.connect(lambda: fired.append("clicked"))
    panel.render_payload(payload)

    panel.created_tasks_button.click()
    _assert(
        panel.created_tasks_button.text() == "Manage Custom Tasks",
        "entry-state UI should expose a Manage Custom Tasks trigger",
    )
    _assert(fired == ["clicked"], "Manage Custom Tasks trigger should be reachable and clickable")


def _test_create_custom_group_trigger_is_present_and_clickable():
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
            "guidance_text": "",
            "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "count": 1,
            "items": [],
        },
        "saved_group_inventory": {
            "visible": True,
            "status_kind": "template_only",
            "status_text": "No custom groups are active yet.",
            "guidance_text": "",
            "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "count": 0,
            "items": [],
        },
    }
    fired = []
    panel.create_custom_group_requested.connect(lambda: fired.append("clicked"))
    panel.render_payload(payload)
    panel.create_custom_group_button.click()

    _assert(
        panel.create_custom_group_button.text() == "Create Custom Group",
        "entry-state UI should expose a Create Custom Group trigger",
    )
    _assert(
        "savedActionCreateGroupDescription" in panel.styleSheet(),
        "entry-state styling should explicitly theme the Create Custom Group description instead of falling back to default black text",
    )
    _assert(
        "exact-match callable group" in panel.create_custom_group_button.toolTip().casefold(),
        "Create Custom Group should expose a specific tooltip instead of a generic one",
    )
    _assert(
        "QToolTip {" in panel.styleSheet(),
        "entry-state overlay should theme its tooltips instead of falling back to the default OS tooltip styling",
    )
    _assert(fired == ["clicked"], "Create Custom Group trigger should be reachable and clickable")


def _test_manage_custom_groups_trigger_is_present_and_clickable():
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
            "guidance_text": "",
            "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "count": 1,
            "items": [],
        },
        "saved_group_inventory": {
            "visible": True,
            "status_kind": "loaded",
            "status_text": "1 custom group is available.",
            "guidance_text": "",
            "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "count": 1,
            "items": [
                {
                    "id": "workspace_tools",
                    "title": "Workspace Tools",
                    "aliases": ["workspace tools"],
                    "member_count": 2,
                }
            ],
        },
    }
    fired = []
    panel.created_groups_requested.connect(lambda: fired.append("clicked"))
    panel.render_payload(payload)
    panel.created_groups_button.click()

    _assert(
        panel.created_groups_button.text() == "Manage Custom Groups",
        "entry-state UI should expose a Manage Custom Groups trigger",
    )
    _assert(
        "savedActionCreatedGroupsDescription" in panel.styleSheet(),
        "entry-state styling should explicitly theme the Manage Custom Groups description instead of falling back to default black text",
    )
    _assert(
        "which members each group can surface" in panel.created_groups_button.toolTip().casefold(),
        "Manage Custom Groups should expose a specific tooltip instead of a generic one",
    )
    _assert(fired == ["clicked"], "Manage Custom Groups trigger should be reachable and clickable")


def _test_entry_surface_keeps_inventory_details_out_of_landing_view():
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
            "status_text": "8 saved actions are available.",
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
    panel.render_payload(payload)

    landing_edit_buttons = [
        button
        for button in panel.findChildren(QPushButton)
        if button.text() == "Edit"
    ]

    _assert(
        not panel.saved_inventory_frame.isHidden(),
        "entry-state landing surface should remain visible in entry phase",
    )
    _assert(
        not landing_edit_buttons,
        "entry-state landing surface should stay button-led and should not expose inline edit buttons",
    )
    _assert(
        panel.saved_inventory_title.text() == "Custom tasks and groups",
        "entry-state landing surface should explain that both task and group authoring live here",
    )


def _test_entry_surface_positions_panel_as_right_sidecar():
    _app()
    panel = renderer_mod.CommandOverlayPanel()
    panel.render_payload(
        {
            "visible": True,
            "phase": "entry",
            "input_armed": True,
            "input_text": "",
            "status_kind": "idle",
            "status_text": "",
            "typed_request": "",
            "pending_action": None,
            "pending_group": None,
            "ambiguous_titles": [],
            "ambiguous_matches": [],
            "saved_action_inventory": {
                "visible": True,
                "status_kind": "loaded",
                "status_text": "",
                "guidance_text": "",
                "path": "",
                "path_display": "",
                "count": 0,
                "items": [],
            },
            "saved_group_inventory": {
                "visible": True,
                "status_kind": "loaded",
                "status_text": "",
                "guidance_text": "",
                "path": "",
                "path_display": "",
                "count": 0,
                "items": [],
            },
        }
    )

    host = renderer_mod.QRect(100, 100, 1100, 720)
    bounds = renderer_mod.QRect(0, 0, 1600, 900)
    panel._apply_geometry(host, bounds)
    frame = panel.frameGeometry()

    _assert(
        frame.x() >= host.x() + int(host.width() * 0.56),
        "entry-state overlay should sit as a right-sidecar instead of centering over the visualization",
    )
    _assert(
        560 <= frame.width() <= 680,
        "entry-state overlay should stay more horizontal while remaining bounded enough to avoid sprawling back across the visualization",
    )
    _assert(
        panel.saved_inventory_status.text() == "Create or manage exact-match tasks and callable groups.",
        "entry-state landing surface should explain the expanded exact-match task and group actions clearly",
    )
    _assert(
        "application, folder, file, or website" in panel.create_custom_task_description.text().casefold(),
        "create action should explain what creating a custom task actually does",
    )
    _assert(
        "review, edit, or remove" in panel.created_tasks_description.text().casefold(),
        "created-tasks action should explain that it opens the management surface for existing tasks",
    )
    _assert(
        "callable group" in panel.create_custom_group_description.text().casefold()
        and "built-ins and saved tasks" in panel.create_custom_group_description.text().casefold(),
        "create-group action should explain that callable groups can surface both built-ins and saved tasks",
    )
    _assert(
        "review, edit, or remove callable groups" in panel.created_groups_description.text().casefold(),
        "manage-groups action should explain that it opens the management surface for existing callable groups",
    )
    _assert(
        panel.create_action_frame.property("entryActionVariant") == "primary"
        and panel.manage_action_frame.property("entryActionVariant") == "secondary",
        "task entry actions should stay visually differentiated so the section feels like a real entry point",
    )
    _assert(
        panel.create_group_action_frame.property("entryActionVariant") == "primary"
        and panel.manage_group_action_frame.property("entryActionVariant") == "secondary",
        "group entry actions should mirror the same visual differentiation as the task actions",
    )
    panel.show()
    _app().processEvents()
    _assert(
        abs(panel.create_action_frame.y() - panel.manage_action_frame.y()) <= 4
        and abs(panel.create_group_action_frame.y() - panel.manage_group_action_frame.y()) <= 4
        and panel.create_group_action_frame.y() > panel.create_action_frame.y(),
        "entry-state landing surface should present tasks and groups as two aligned peer rows instead of collapsing back to a single task-only strip",
    )
    panel.close()


def _test_created_tasks_dialog_exposes_edit_trigger_for_saved_inventory_items():
    _app()
    inventory_payload = {
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
    }
    dialog = renderer_mod.CreatedTasksDialog(inventory_payload=inventory_payload)
    edit_buttons = [
        button
        for button in dialog.items_frame.findChildren(QPushButton)
        if button.text() == "Edit"
    ]

    _assert(edit_buttons, "Manage Custom Tasks dialog should expose edit triggers for saved actions")
    _assert(
        dialog.windowTitle() == "Manage Custom Tasks",
        "management dialog should expose the clearer Manage Custom Tasks window title",
    )
    _assert(
        bool(dialog.windowFlags() & renderer_mod.Qt.FramelessWindowHint),
        "management dialog should use integrated frameless chrome instead of the native title bar",
    )
    _assert(
        hasattr(dialog, "chrome_bar") and dialog.chrome_bar.close_button.text() == "\N{MULTIPLICATION SIGN}",
        "management dialog should expose an integrated dark close affordance in the custom chrome bar",
    )
    _assert(
        not dialog.chrome_bar.title_label.isVisible(),
        "management dialog should remove the visible title-bar label so the window reads as one continuous surface",
    )
    _assert(
        dialog.hint_label.text() == "Review, update, or remove tasks from the current saved-task source.",
        "management dialog should keep a lighter hint so the list stays visually central",
    )
    _assert(
        dialog.guidance_label.isHidden() and dialog.source_label.isHidden(),
        "management dialog should hide redundant guidance and source detail in the normal loaded state",
    )
    title_labels = [
        label
        for label in dialog.items_frame.findChildren(QLabel)
        if label.property("inventoryRole") == "itemTitle"
    ]
    meta_labels = [
        label
        for label in dialog.items_frame.findChildren(QLabel)
        if label.property("inventoryRole") == "itemMeta"
    ]
    target_labels = [
        label
        for label in dialog.items_frame.findChildren(QLabel)
        if label.property("inventoryRole") == "itemTarget"
    ]
    _assert(
        title_labels and meta_labels and target_labels,
        "management rows should separate title, metadata, and target into distinct labels for better hierarchy",
    )
    _assert(
        dialog.items_scroll.viewport().objectName() == "savedActionCreatedTasksViewport",
        "management dialog should theme the scroll viewport instead of leaving a white gutter behind the list",
    )
    _assert(
        "qscrollbar:vertical" in dialog.styleSheet().casefold(),
        "management dialog should style the vertical scrollbar explicitly instead of falling back to the default white scrollbar",
    )
    dialog.show()
    _app().processEvents()
    _assert(
        dialog.title_label.y() <= 18,
        "management dialog title should sit close to the true top edge instead of below a dead header band",
    )
    edit_buttons[0].click()
    _assert(
        dialog.selected_action_id() == "open_reports",
        "management dialog should preserve stable edit-button mapping for the selected saved action",
    )


def _test_created_tasks_dialog_exposes_delete_trigger_for_saved_inventory_items():
    _app()
    inventory_payload = {
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
    }
    dialog = renderer_mod.CreatedTasksDialog(inventory_payload=inventory_payload)
    delete_buttons = [
        button
        for button in dialog.items_frame.findChildren(QPushButton)
        if button.text() == "Delete"
    ]

    _assert(delete_buttons, "Manage Custom Tasks dialog should expose delete triggers for saved actions")
    _assert(
        dialog.guidance_label.isHidden() and dialog.source_label.isHidden(),
        "management delete surface should keep the loaded-state header stack light",
    )
    delete_buttons[0].click()
    _assert(
        dialog.selected_delete_action_id() == "open_reports",
        "management dialog should preserve stable delete-button mapping for the selected saved action",
    )
    _assert(
        dialog.selected_action_id() == "",
        "Created Tasks dialog delete selection should not leak into the edit-selection channel",
    )


def _test_created_tasks_dialog_edit_reachability_extends_beyond_six_items():
    _app()
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

    dialog = renderer_mod.CreatedTasksDialog(
        inventory_payload={
            "visible": True,
            "status_kind": "loaded",
            "status_text": "8 saved actions are available.",
            "guidance_text": 'Use "Open Saved Actions File" or "Open Saved Actions Folder" to inspect the source.',
            "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
            "count": 8,
            "items": items,
        }
    )

    edit_buttons = [
        button
        for button in dialog.items_frame.findChildren(QPushButton)
        if button.text() == "Edit"
    ]

    _assert(
        not dialog.items_scroll.isHidden(),
        "Created Tasks dialog should keep its scroll container enabled when many saved actions are present",
    )
    _assert(
        len(edit_buttons) == 8,
        "Created Tasks dialog should expose edit reachability for every saved action, not just the first six",
    )

    edit_buttons[-1].click()
    _assert(
        dialog.selected_action_id() == "open_reports_8",
        "Created Tasks dialog should preserve stable edit-button mapping for later saved actions",
    )


def _test_created_tasks_dialog_caps_loaded_viewport_to_five_rows():
    _app()
    items = []
    for index in range(1, 7):
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

    dialog = renderer_mod.CreatedTasksDialog(
        inventory_payload={
            "visible": True,
            "status_kind": "loaded",
            "status_text": "6 saved actions are available.",
            "guidance_text": "",
            "path": "",
            "path_display": "",
            "count": 6,
            "items": items,
        }
    )
    dialog.show()
    _app().processEvents()
    expected_height = renderer_mod._visible_row_height_for_layout(dialog.items_layout, 5, extra_padding=2)
    _assert(
        dialog.items_scroll.maximumHeight() == expected_height,
        "Manage Custom Tasks should cap the loaded viewport to five visible rows before scrolling",
    )
    dialog.close()


def _test_created_groups_dialog_exposes_group_management_triggers():
    _app()
    inventory_payload = {
        "visible": True,
        "status_kind": "loaded",
        "status_text": "1 custom group is available.",
        "guidance_text": "",
        "path": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
        "path_display": r"C:\Users\Test\AppData\Local\Nexus Desktop AI\saved_actions.json",
        "count": 1,
        "items": [
            {
                "id": "workspace_tools",
                "title": "Workspace Tools",
                "aliases": ["workspace tools", "tools group"],
                "member_count": 2,
            }
        ],
    }
    dialog = renderer_mod.CreatedGroupsDialog(inventory_payload=inventory_payload)
    edit_buttons = [
        button
        for button in dialog.items_frame.findChildren(QPushButton)
        if button.text() == "Edit"
    ]
    delete_buttons = [
        button
        for button in dialog.items_frame.findChildren(QPushButton)
        if button.text() == "Delete"
    ]

    _assert(edit_buttons and delete_buttons, "Manage Custom Groups dialog should expose edit and delete triggers")
    _assert(
        dialog.windowTitle() == "Manage Custom Groups",
        "group management dialog should expose the clearer Manage Custom Groups window title",
    )
    _assert(
        dialog.title_label.text() == "Manage Custom Groups",
        "group management header should no longer duplicate the item count in the title itself",
    )
    _assert(
        dialog.guidance_label.isHidden() and dialog.source_label.isHidden(),
        "group management dialog should keep the loaded-state header stack light",
    )
    _assert(
        "QToolTip {" in dialog.styleSheet(),
        "group management dialog should theme its tooltips instead of inheriting the default tooltip style",
    )
    meta_labels = [
        label
        for label in dialog.items_frame.findChildren(QLabel)
        if label.property("inventoryRole") == "itemMeta"
    ]
    _assert(
        any("members" in (label.text() or "").casefold() for label in meta_labels),
        "group management rows should surface member-count metadata so the group surface stays legible",
    )
    alias_labels = [
        label
        for label in dialog.items_frame.findChildren(QLabel)
        if label.property("inventoryRole") == "itemTarget"
    ]
    _assert(
        alias_labels and "exact callable aliases" in alias_labels[0].toolTip().casefold(),
        "group management rows should expose group-specific alias tooltips instead of a raw generic preview",
    )
    _assert(
        "aliases or members" in edit_buttons[0].toolTip().casefold(),
        "group management edit tooltips should explain the real group edit scope",
    )
    _assert(
        "tasks stay saved" in delete_buttons[0].toolTip().casefold(),
        "group management delete tooltips should clarify that deleting a group does not delete tasks",
    )
    _assert(
        dialog.chrome_bar.close_button.toolTip().casefold() == "close manage custom groups",
        "group management close affordance should expose a specific tooltip",
    )
    edit_buttons[0].click()
    _assert(
        dialog.selected_group_id() == "workspace_tools",
        "group management dialog should preserve stable edit-button mapping for the selected group",
    )


def _test_created_groups_dialog_caps_loaded_viewport_to_five_rows():
    _app()
    items = []
    for index in range(1, 7):
        items.append(
            {
                "id": f"group_{index}",
                "title": f"Workspace Group {index}",
                "aliases": [f"workspace group {index}"],
                "member_count": index,
            }
        )

    dialog = renderer_mod.CreatedGroupsDialog(
        inventory_payload={
            "visible": True,
            "status_kind": "loaded",
            "status_text": "6 custom groups are available.",
            "guidance_text": "",
            "path": "",
            "path_display": "",
            "count": 6,
            "items": items,
        }
    )
    dialog.show()
    _app().processEvents()
    expected_height = renderer_mod._visible_row_height_for_layout(dialog.items_layout, 5, extra_padding=2)
    _assert(
        dialog.items_scroll.maximumHeight() == expected_height,
        "Manage Custom Groups should cap the loaded viewport to five visible rows before scrolling",
    )
    dialog.close()


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


def _test_create_dialog_surfaces_field_level_guidance():
    _app()
    dialog = renderer_mod.SavedActionCreateDialog()

    _assert(
        dialog.type_header_label.font().bold()
        and dialog.title_header_label.font().bold()
        and dialog.aliases_header_label.font().bold()
        and dialog.trigger_header_label.font().bold()
        and dialog.target_header_label.font().bold(),
        "field headers should be more prominent than the surrounding guidance copy",
    )
    help_icon_buttons = [
        button
        for button in dialog.findChildren(QToolButton)
        if button.property("createRole") == "helpIcon"
    ]
    _assert(
        not help_icon_buttons,
        "create dialog should move help discovery onto the field headers instead of keeping a separate icon column",
    )
    _assert(
        bool(dialog.windowFlags() & renderer_mod.Qt.FramelessWindowHint),
        "create dialog should use integrated frameless chrome instead of the native title bar",
    )
    _assert(
        hasattr(dialog, "chrome_bar") and dialog.chrome_bar.close_button.text() == "\N{MULTIPLICATION SIGN}",
        "create dialog should expose an integrated dark close affordance in the custom chrome bar",
    )
    _assert(
        not dialog.chrome_bar.title_label.isVisible(),
        "create dialog should remove the visible title-bar label so the window reads as one continuous surface",
    )
    _assert(
        "default trigger family" in dialog.type_help_button.toolTip().casefold(),
        "task type help icon should explain how task type shapes trigger and target behavior",
    )
    _assert(
        "display label" in dialog.title_help_button.toolTip().casefold(),
        "title help icon should explain what the title field does",
    )
    _assert(
        "calling comes from" in dialog.title_help_button.toolTip().casefold(),
        "title help icon should reinforce that the title is label-only for alias-root tasks",
    )
    _assert(
        "exact callable words or phrases" in dialog.aliases_help_button.toolTip().casefold(),
        "aliases help icon should explain what aliases are for",
    )
    _assert(
        "explicit call prefixes" in dialog.trigger_help_button.toolTip().casefold()
        or "explicit call prefixes placed before aliases" in dialog.trigger_help_button.toolTip().casefold(),
        "trigger help icon should explain what the trigger field does",
    )
    _assert(
        hasattr(dialog.title_help_button, "show_help_tooltip_now")
        and hasattr(dialog.trigger_help_button, "show_help_tooltip_now"),
        "field-header help affordances should support immediate tooltip display for faster response",
    )
    _assert(
        dialog.title_help_button.focusPolicy() == renderer_mod.Qt.StrongFocus,
        "field-header help affordances should remain keyboard-focusable for a more consistent immediate-help experience",
    )
    _assert(
        hasattr(dialog.type_help_button, "show_help_tooltip_now"),
        "task type header should also support immediate tooltip display",
    )
    _assert(
        dialog.type_help_button is dialog.type_header_label
        and dialog.title_help_button is dialog.title_header_label
        and dialog.aliases_help_button is dialog.aliases_header_label
        and dialog.trigger_help_button is dialog.trigger_header_label
        and dialog.target_help_button is dialog.target_header_label,
        "tooltip help should now live on the visible field labels themselves",
    )
    _assert(
        not hasattr(dialog, "title_guidance_label"),
        "create dialog should not keep a separate helper-text label under the title field",
    )
    _assert(
        not hasattr(dialog, "aliases_guidance_label"),
        "create dialog should not keep a separate helper-text label under the aliases field",
    )
    _assert(
        not hasattr(dialog, "aliases_suggestion_label"),
        "create dialog should not keep a separate alias-suggestions label under the aliases field",
    )
    _assert(
        not hasattr(dialog, "trigger_guidance_label"),
        "create dialog should not keep a separate helper-text label under the trigger field",
    )
    _assert(
        dialog.current_trigger_mode() == "launch",
        "application tasks should default to Launch until the trigger is changed manually",
    )
    _assert(
        not hasattr(dialog, "target_guidance_label"),
        "create dialog should not keep a separate helper-text label under the target field",
    )
    _assert(
        "callable surface" in dialog.target_examples_title.text().casefold(),
        "create dialog should show one boxed callable-examples section beside the fields",
    )
    _assert(
        5 <= dialog.form_layout.spacing() <= 8,
        "create dialog spacing should stay intentionally tightened without collapsing into a cramped layout",
    )
    _assert(
        34 <= dialog.create_button.minimumHeight() <= 36
        and 34 <= dialog.cancel_button.minimumHeight() <= 36,
        "dialog action buttons should keep the tighter but still comfortable padding rhythm",
    )
    _assert(
        dialog.title_header.property("createRole") == "fieldHeaderDivider"
        and dialog.target_header.property("createRole") == "fieldHeaderDivider",
        "task dialog headers should use slim divider rows for stronger field separation without boxed chrome",
    )
    _assert(
        dialog.type_header_divider.property("createRole") == "fieldHeaderDividerLine"
        and dialog.type_header_divider.sizePolicy().horizontalPolicy() == renderer_mod.QSizePolicy.Expanding,
        "task dialog divider rows should carry a full-width line instead of only decorating the label column",
    )
    dialog.show()
    _app().processEvents()
    _assert(
        dialog.type_header_label.y() > dialog.type_header_divider.y(),
        "task dialog headers should sit below the divider line instead of sharing the same row",
    )
    _assert(
        dialog.type_header_label.mapTo(dialog, dialog.type_header_label.rect().topLeft()).x() < dialog.type_combo.mapTo(dialog, dialog.type_combo.rect().topLeft()).x()
        and dialog.title_header_label.mapTo(dialog, dialog.title_header_label.rect().topLeft()).x() < dialog.title_input.mapTo(dialog, dialog.title_input.rect().topLeft()).x()
        and dialog.trigger_header_label.mapTo(dialog, dialog.trigger_header_label.rect().topLeft()).x() < dialog.trigger_combo.mapTo(dialog, dialog.trigger_combo.rect().topLeft()).x()
        and dialog.aliases_header_label.mapTo(dialog, dialog.aliases_header_label.rect().topLeft()).x() < dialog.aliases_input.mapTo(dialog, dialog.aliases_input.rect().topLeft()).x()
        and dialog.target_header_label.mapTo(dialog, dialog.target_header_label.rect().topLeft()).x() < dialog.target_input.mapTo(dialog, dialog.target_input.rect().topLeft()).x(),
        "task dialog field headers should live in a dedicated far-left label column with all section content to the right",
    )
    _assert(
        abs(dialog.type_header_label.mapTo(dialog, dialog.type_header_label.rect().center()).y() - dialog.type_combo.mapTo(dialog, dialog.type_combo.rect().center()).y()) <= 18
        and abs(dialog.title_header_label.mapTo(dialog, dialog.title_header_label.rect().center()).y() - dialog.title_input.mapTo(dialog, dialog.title_input.rect().center()).y()) <= 18
        and abs(dialog.aliases_header_label.mapTo(dialog, dialog.aliases_header_label.rect().center()).y() - dialog.aliases_input.mapTo(dialog, dialog.aliases_input.rect().center()).y()) <= 18,
        "task dialog field headers should be vertically centered inside each section instead of floating above the controls",
    )
    _assert(
        dialog.type_header.y() < dialog.title_header.y() < dialog.trigger_header.y() < dialog.aliases_header.y(),
        "Task type should remain the first full section, followed by Title, Trigger, and Aliases",
    )
    _assert(
        dialog.groups_header_label.mapTo(dialog, dialog.groups_header_label.rect().topLeft()).x()
        < dialog.groups_frame.mapTo(dialog, dialog.groups_frame.rect().topLeft()).x(),
        "task dialog group header should stay in the far-left label column instead of sharing space with the assignment controls",
    )
    _assert(
        dialog.type_header.height() >= dialog.type_combo.height()
        and dialog.groups_header.height() >= dialog.groups_frame.height() - 8,
        "task dialog sections should size around the section content so the left header column feels anchored to the whole band",
    )
    _assert(
        dialog.title_label.y() <= 18,
        "create dialog title should sit close to the true top edge instead of below a dead header band",
    )
    _assert(
        bool(dialog.title_label.alignment() & Qt.AlignHCenter),
        "create dialog title should center within the shell so the top composition does not feel lopsided against the close affordance",
    )
    _assert(
        dialog.target_examples_box.x() > dialog.aliases_input.x(),
        "callable-surface guidance should sit to the right of the form instead of consuming the full lower section",
    )
    _assert(
        36 <= dialog.title_input.height() <= 40
        and 36 <= dialog.aliases_input.height() <= 40,
        "form inputs should stay compact enough to reduce overall dialog scale without becoming cramped",
    )
    _assert(
        dialog.target_browse_button.y() > dialog.target_input.y(),
        "target browse action should sit below the target field so the input keeps more horizontal space",
    )

    dialog.title_input.setText("Nexus")
    _assert(
        "suggested aliases" in dialog.target_examples_label.text().casefold()
        and "nexus" in dialog.target_examples_label.text().casefold(),
        "alias suggestions should move into the single bottom guidance box",
    )

    dialog.type_combo.setCurrentText("Folder")
    _assert(
        dialog.current_trigger_mode() == "open",
        "folder tasks should default to Open while the trigger is still following the selected type",
    )
    _assert(
        "folder path nexus opens" in dialog.target_help_button.toolTip().casefold(),
        "target help icon should update with the current target-kind examples",
    )
    _assert(
        "border-radius: 10px" in dialog.target_examples_label.text().casefold(),
        "bottom guidance box should render the sectioned card presentation for better scanability",
    )

    dialog.type_combo.setCurrentText("Website URL")
    _assert(
        "full website address" in dialog.target_help_button.toolTip().casefold(),
        "website guidance should now live in the target tooltip instead of under the field",
    )
    dialog.close()


def _test_create_dialog_supports_group_assignment_and_inline_group_queue():
    _app()
    dialog = renderer_mod.SavedActionCreateDialog(
        available_groups=[
            {
                "id": "workspace_tools",
                "title": "Workspace Tools",
                "aliases": ["workspace tools"],
                "member_count": 2,
            },
            {
                "id": "daily_flow",
                "title": "Daily Flow",
                "aliases": ["daily flow"],
                "member_count": 1,
            },
        ],
        group_status_kind="loaded",
        group_status_text="",
    )

    _assert(
        dialog.groups_header_label.text() == "Groups",
        "task dialog should expose a dedicated Groups field when callable groups are available",
    )
    _assert(
        dialog.groups_new_button.text() == "Assign Group...",
        "task dialog should route group membership through a dedicated assignment window instead of inline checkboxes",
    )
    _assert(
        dialog.groups_remove_button.text() == "Unassign Group",
        "task dialog should expose a dedicated unassign action for the single-group model",
    )
    dialog.title_input.setText("Open Reports")
    dialog.aliases_input.setText("reports")
    dialog.target_input.setText(r"C:\Reports")
    assignment_dialog = renderer_mod.TaskGroupAssignmentDialog(
        available_groups=dialog._available_groups,
        available_members=[],
        selected_group_ids=(),
        inline_group_draft=renderer_mod.CallableGroupDraft(
            title="Reports Suite",
            aliases=("reports suite",),
            member_action_ids=(),
        ),
        inline_group_assigned=False,
        group_status_kind="loaded",
        group_status_text="",
    )
    _assert(
        assignment_dialog.title_label.text() == "Manage Custom Groups",
        "task-path group assignment should reuse the same management-family title instead of a lighter standalone surface",
    )
    _assert(
        assignment_dialog.create_group_button.text() == "Create New Group",
        "task-path group management should expose a dedicated Create New Group action in the footer",
    )
    assignment_dialog._toggle_existing_group("workspace_tools")
    dialog._selected_group_ids_state = assignment_dialog.selected_group_ids()
    dialog._inline_group_draft = assignment_dialog.inline_group_draft()
    dialog._inline_group_assigned = assignment_dialog.inline_group_assigned()
    dialog._refresh_groups_ui()
    draft = dialog.build_draft()

    _assert(
        draft.group_ids == ("workspace_tools",),
        "task dialog should carry assigned existing group ids into the saved-action draft",
    )
    _assert(
        draft.inline_group is None,
        "task dialog should not carry an unassigned inline group draft into save",
    )
    _assert(
        "assigned group:" in dialog.groups_summary_label.text().casefold(),
        "task dialog should surface the single assigned group directly instead of the older boxed summary",
    )
    _assert(
        not dialog.groups_remove_button.isHidden() and dialog.groups_new_button.isHidden(),
        "task dialog should swap the assign action for an unassign action once a group is attached",
    )
    assignment_dialog.close()


def _test_group_create_dialog_surfaces_members_and_exact_alias_guidance():
    _app()
    dialog = renderer_mod.CallableGroupCreateDialog(
        available_members=[
            {
                "id": "open_reports",
                "title": "Open Reports",
                "origin_label": "Saved",
                "target_kind": "folder",
            },
            {
                "id": "open_saved_actions_folder",
                "title": "Open Saved Actions Folder",
                "origin_label": "Built-in",
                "target_kind": "folder",
            },
            {
                "id": "open_docs",
                "title": "Open Docs",
                "origin_label": "Built-in",
                "target_kind": "url",
            },
        ]
    )

    _assert(
        dialog.windowTitle() == "Create Custom Group",
        "group authoring should expose a dedicated Create Custom Group dialog",
    )
    member_header_labels = [
        label
        for label in dialog.members_header.findChildren(QLabel)
        if label.property("createRole") == "fieldHeaderHelp"
    ]
    _assert(
        member_header_labels and member_header_labels[0].text() == "Available Tasks",
        "group dialog should expose an Available Tasks picker field",
    )
    _assert(
        dialog.name_header.property("createRole") == "fieldHeaderDivider",
        "group dialog headers should use the same slim divider styling as the task dialog",
    )
    _assert(
        len(dialog._member_checkboxes) == 3,
        "group dialog should expose checkboxes for both saved-task and built-in members",
    )
    _assert(
        "QCheckBox::indicator" in dialog.styleSheet(),
        "group dialog should strengthen unchecked checkbox visibility instead of relying on the default subtle indicator",
    )
    _assert(
        620 <= dialog.maximumWidth() <= 680,
        "group dialog should stay wider and more horizontal while still remaining width-bounded",
    )
    _assert(
        bool(dialog.title_label.alignment() & Qt.AlignHCenter),
        "group dialog title should center within the shell so it matches the other callable-management windows",
    )
    _assert(
        "QToolTip {" in dialog.styleSheet(),
        "group authoring should theme tooltips instead of falling back to the default tooltip styling",
    )
    _assert(
        dialog.members_scroll.maximumHeight() <= 116
        and dialog.members_scroll.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff,
        "group dialog should cap the Available Tasks list to roughly five visible rows with vertical-only scrolling",
    )
    _assert(
        "chromeRole=\"close\"" in dialog.styleSheet(),
        "group dialog should explicitly style the custom close button instead of falling back to the default chrome look",
    )
    name_help = dialog.findChild(QLabel, "callableGroupCreateNameHelp")
    aliases_help = dialog.findChild(QLabel, "callableGroupCreateAliasesHelp")
    members_help = dialog.findChild(QLabel, "callableGroupCreateMembersHelp")
    _assert(
        name_help is not None
        and "display label" in name_help.toolTip().casefold()
        and "aliases, not the name" in name_help.toolTip().casefold(),
        "group name help should explain that the label is visual while aliases remain the callable surface",
    )
    _assert(
        aliases_help is not None
        and "exact phrases" in aliases_help.toolTip().casefold()
        and "member chooser" in aliases_help.toolTip().casefold(),
        "group alias help should explain that aliases are exact phrases that open the group chooser",
    )
    _assert(
        members_help is not None
        and "built-ins and saved tasks" in members_help.toolTip().casefold()
        and "only show these members" in members_help.toolTip().casefold(),
        "group member help should explain that the chooser is limited to the selected members",
    )
    _assert(
        dialog.chrome_bar.close_button.toolTip().casefold() == "close create custom group",
        "group create close affordance should expose a specific tooltip",
    )
    _assert(
        any("becomes selectable when this group's alias is used." in checkbox.toolTip().casefold() for checkbox in dialog._member_checkboxes),
        "group member rows should expose specific tooltips instead of a generic origin-only label",
    )
    dialog.show()
    _app().processEvents()
    _assert(
        dialog.name_header.findChildren(QLabel)[-1].y() > dialog.name_header.findChildren(QFrame)[0].y(),
        "group dialog section titles should sit below the divider line instead of sharing it",
    )
    _assert(
        dialog.name_header_label.mapTo(dialog, dialog.name_header_label.rect().topLeft()).x() < dialog.name_input.mapTo(dialog, dialog.name_input.rect().topLeft()).x()
        and dialog.aliases_header_label.mapTo(dialog, dialog.aliases_header_label.rect().topLeft()).x() < dialog.aliases_input.mapTo(dialog, dialog.aliases_input.rect().topLeft()).x()
        and (
            dialog.members_header_label.mapTo(dialog, dialog.members_header_label.rect().topLeft()).x()
            < dialog.members_scroll.mapTo(dialog, dialog.members_scroll.rect().topLeft()).x()
            if dialog.members_header is not None
            else True
        ),
        "group dialog field headers should live in the far-left label column with all section content to the right",
    )
    _assert(
        abs(dialog.name_header_label.mapTo(dialog, dialog.name_header_label.rect().center()).y() - dialog.name_header.mapTo(dialog, dialog.name_header.rect().center()).y()) <= 22
        and abs(dialog.aliases_header_label.mapTo(dialog, dialog.aliases_header_label.rect().center()).y() - dialog.aliases_header.mapTo(dialog, dialog.aliases_header.rect().center()).y()) <= 26,
        "group dialog field headers should be vertically centered inside each section instead of floating above the controls",
    )
    dialog.name_input.setText("Workspace Tools")
    dialog.aliases_input.setText("workspace tools, tools group")
    dialog._member_checkboxes[0].setChecked(True)
    draft = dialog.build_draft()

    _assert(
        draft.aliases == ("workspace tools", "tools group"),
        "group dialog should preserve exact alias phrases without inventing trigger variants",
    )
    _assert(
        draft.member_action_ids == ("open_reports",),
        "group dialog should carry the explicitly selected member ids only",
    )
    _assert(
        "workspace tools" in dialog.examples_label.text().casefold()
        and "tools group" in dialog.examples_label.text().casefold(),
        "group dialog callable surface should preview exact group aliases only",
    )
    dialog.close()


def _test_assignment_group_create_reuses_group_dialog_without_member_picker():
    _app()
    dialog = renderer_mod.CallableGroupCreateDialog(
        heading_text="Create Custom Group",
        hint_text="Pick a group name and exact aliases below. You will return to Manage Custom Groups for this task after the group is created.",
        submit_button_text="Create",
        available_members=[],
        show_member_picker=False,
    )

    _assert(
        dialog.windowTitle() == "Create Custom Group",
        "inline group creation should reuse the same Create Custom Group window title",
    )
    _assert(
        dialog.members_header is not None and dialog.members_scroll is not None,
        "assignment-driven group creation should keep the same Available Tasks section shell as the direct group dialog",
    )
    _assert(
        dialog.task_flow_note is not None
        and "returns you to manage custom groups for the current task" in dialog.task_flow_note.findChild(QLabel, "callableGroupCreateTaskFlowBody").text().casefold(),
        "assignment-driven group creation should keep the same dialog family while swapping the picker contents for a task-scoped handoff note",
    )
    _assert(
        dialog.members_header_label.text() == "Available Tasks",
        "assignment-driven group creation should preserve the normal Available Tasks section heading for parity",
    )
    dialog.close()


def _test_create_dialog_trigger_controls_and_dynamic_examples():
    _app()
    dialog = renderer_mod.SavedActionCreateDialog()

    _assert(
        dialog.custom_triggers_input.isHidden(),
        "custom trigger input should stay hidden until Custom trigger mode is selected",
    )

    dialog.type_combo.setCurrentText("Website URL")
    dialog.title_input.setText("Open Nexus")
    dialog.aliases_input.setText("Nexus, NDAI")
    dialog.trigger_combo.setCurrentText("Launch and Open")
    examples_text = dialog.target_examples_label.text().casefold()

    _assert(
        "real callable phrases" in examples_text and "exact phrases, case-insensitive" in examples_text,
        "examples box should explain the real callable phrases for the current draft",
    )
    _assert(
        "nexus" in examples_text
        and "launch nexus" in examples_text
        and "open ndai" in examples_text
        and "launch ndai" in examples_text,
        "launch-and-open mode should show both trigger families for aliases and not rely on the title label",
    )
    _assert(
        "open open nexus" not in examples_text and "launch open nexus" not in examples_text,
        "examples box should not generate trigger phrases from the title label when the task is alias-root",
    )
    _assert(
        "target format: https://example.com/docs" in examples_text,
        "examples box should keep only the relevant target-kind format reminder",
    )
    _assert(
        "notepad.exe" not in examples_text and r"c:\reports\weekly.txt" not in examples_text,
        "examples box should remove irrelevant target-kind examples",
    )
    _assert(
        "suggested aliases" not in examples_text,
        "alias suggestions should drop out of the bottom box once they no longer add value over the typed aliases",
    )

    dialog.trigger_combo.setCurrentText("Custom")
    _assert(
        not dialog.custom_triggers_input.isHidden(),
        "custom trigger mode should reveal the comma-separated custom trigger input",
    )
    dialog.custom_triggers_input.setText("Force Open, Duck Duck Goose")
    custom_examples_text = dialog.target_examples_label.text().casefold()
    custom_example_lines = {
        line.strip()
        for line in custom_examples_text.splitlines()
        if line.strip()
    }
    _assert(
        "force open nexus" in custom_examples_text
        and "duck duck goose ndai" in custom_examples_text,
        "custom trigger mode should show examples using the entered custom trigger phrases with aliases",
    )
    _assert(
        "launch nexus" not in custom_example_lines and "open nexus" not in custom_example_lines,
        "custom trigger mode should replace the standard trigger families in the examples box",
    )
    _assert(
        "force open open nexus" not in custom_examples_text,
        "custom trigger mode should not generate custom trigger phrases from the title label",
    )


def _test_edit_dialog_default_trigger_follows_type_until_changed():
    _app()
    dialog = renderer_mod.SavedActionEditDialog(
        initial_draft=renderer_mod.SavedActionDraft(
            title="Open Nexus",
            target_kind="app",
            target="notepad.exe",
            aliases=("Nexus",),
            invocation_mode="aliases_only",
            trigger_mode="launch",
        )
    )

    _assert(
        dialog.current_trigger_mode() == "launch",
        "edit dialog should preload the saved trigger mode for alias-root tasks",
    )

    dialog.type_combo.setCurrentText("Folder")
    examples_text = dialog.target_examples_label.text()
    _assert(
        dialog.current_trigger_mode() == "open",
        "edit dialog should keep following the selected type when the saved trigger only mirrored the prior default",
    )
    _assert(
        "Open Nexus" in examples_text and "Launch Nexus" not in examples_text,
        "edit dialog examples should switch to the new default trigger family for alias-root tasks when no manual trigger was chosen",
    )

    dialog.trigger_combo.setCurrentText("Launch and Open")
    dialog.type_combo.setCurrentText("File")
    examples_text = dialog.target_examples_label.text()
    _assert(
        dialog.current_trigger_mode() == "launch_and_open",
        "edit dialog should preserve an explicitly chosen trigger once the user changes it",
    )
    _assert(
        "Launch Nexus" in examples_text and "Open Nexus" in examples_text,
        "edit dialog examples should preserve the explicitly chosen trigger family after later type changes",
    )


def _test_legacy_edit_dialog_preserves_bare_callable_examples_until_trigger_changes():
    _app()
    dialog = renderer_mod.SavedActionEditDialog(
        initial_draft=renderer_mod.SavedActionDraft(
            title="Knowledge Base",
            target_kind="url",
            target="https://example.com/docs",
            aliases=("KB Docs",),
            invocation_mode="legacy",
            trigger_mode="",
        )
    )

    examples_text = dialog.target_examples_label.text()
    draft = dialog.build_draft()
    _assert(
        "Knowledge Base" in examples_text and "Open Knowledge Base" not in examples_text,
        "legacy edit examples should stay aligned to the current bare-only callable phrases until a trigger is explicitly chosen",
    )
    _assert(
        draft.trigger_mode == "",
        "legacy edits should preserve the absence of an explicit trigger when the user has not changed it",
    )

    dialog.trigger_combo.setCurrentText("Launch")
    dialog.trigger_combo.setCurrentText("Open")
    draft = dialog.build_draft()
    _assert(
        draft.trigger_mode == "open",
        "legacy edits should persist a trigger once the user explicitly chooses one",
    )


def _test_create_dialog_supports_browse_assisted_target_selection():
    _app()
    dialog = renderer_mod.SavedActionCreateDialog()

    _assert(
        not dialog.target_browse_button.isHidden(),
        "application tasks should expose a browse button beneath the target field",
    )
    dialog.show()
    _app().processEvents()
    _assert(
        dialog.target_browse_button.y() > dialog.target_input.y(),
        "target browse control should sit below the input so the address field keeps more horizontal room",
    )
    _assert(
        "application path" in dialog.target_browse_button.toolTip().casefold(),
        "application browse button should explain what it selects",
    )
    dialog._choose_application_target = lambda: r"C:\Program Files\Notepad++\notepad++.exe"
    dialog.target_browse_button.click()
    _assert(
        dialog.target_input.text() == r"C:\Program Files\Notepad++\notepad++.exe",
        "application browse should populate the validated target field directly",
    )

    dialog.type_combo.setCurrentText("Folder")
    _assert(
        not dialog.target_browse_button.isHidden(),
        "folder tasks should keep browse-assisted target selection visible",
    )
    _assert(
        "folder path" in dialog.target_browse_button.toolTip().casefold(),
        "folder browse button should explain what it selects",
    )
    dialog._choose_folder_target = lambda: r"C:\Reports"
    dialog.target_browse_button.click()
    _assert(
        dialog.target_input.text() == r"C:\Reports",
        "folder browse should populate the target field with the chosen folder path",
    )

    dialog.type_combo.setCurrentText("File")
    _assert(
        not dialog.target_browse_button.isHidden(),
        "file tasks should keep browse-assisted target selection visible",
    )
    _assert(
        "file path" in dialog.target_browse_button.toolTip().casefold(),
        "file browse button should explain what it selects",
    )
    dialog._choose_file_target = lambda: r"C:\Reports\weekly.txt"
    dialog.target_browse_button.click()
    _assert(
        dialog.target_input.text() == r"C:\Reports\weekly.txt",
        "file browse should populate the target field with the chosen file path",
    )

    dialog.type_combo.setCurrentText("Website URL")
    _assert(
        dialog.target_browse_button.isHidden(),
        "website tasks should remain direct-entry only and should hide the browse button",
    )
    prior_target = dialog.target_input.text()
    dialog.target_browse_button.click()
    _assert(
        dialog.target_input.text() == prior_target,
        "website tasks should ignore browse interaction and leave the direct-entry target unchanged",
    )


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
        _flush_qt_events()

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
        _flush_qt_events()

        _assert(dialog_instances, "invalid input path should still open the create dialog")
        _assert(
            "display label people will see" in dialog_instances[0].status_label.text().casefold(),
            "invalid input should explain the title as a label, not as a callable phrase",
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
        _flush_qt_events()

        _assert(dialog_instances, "invalid folder targets should still open the create dialog")
        _assert(
            "absolute windows paths" in dialog_instances[0].status_label.text().casefold(),
            "invalid folder targets should surface a clear path-structure error inside the dialog",
        )
        _assert(
            "folder tasks need an absolute windows path" in dialog_instances[0].status_label.text().casefold(),
            "invalid folder targets should explain why the target failed, not only the raw validation message",
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
        _flush_qt_events()

        _assert(dialog_instances, "invalid application targets should still open the create dialog")
        _assert(
            "bare command like notepad.exe" in dialog_instances[0].status_label.text().casefold(),
            "invalid application targets should surface a clear application-target format error",
        )
        _assert(
            "application tasks only accept a bare command" in dialog_instances[0].status_label.text().casefold(),
            "invalid application targets should explain what a valid application target looks like",
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
        _flush_qt_events()

        _assert(dialog_instances, "invalid file targets should still open the create dialog")
        _assert(
            "illegal windows path characters" in dialog_instances[0].status_label.text().casefold(),
            "invalid file targets should surface a clear path-structure error inside the dialog",
        )
        _assert(
            "file tasks need an absolute windows path" in dialog_instances[0].status_label.text().casefold(),
            "invalid file targets should explain what a valid file target looks like",
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
        _flush_qt_events()

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


def _test_created_tasks_navigation_routes_into_edit_dialog():
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
        created_tasks_dialogs = []
        edit_dialogs = []
        window._created_tasks_dialog_factory = (
            lambda parent, inventory_payload: _AutoSelectCreatedTasksDialog(
                None,
                inventory_payload,
                lambda dialog: (
                    _assert(
                        dialog.title_label.text() == "Manage Custom Tasks",
                        "Manage Custom Tasks dialog should keep a stable main header and leave counts to the status line",
                    ),
                    dialog._handle_edit_requested("open_reports"),
                ),
                created_tasks_dialogs,
            )
        )
        window._saved_action_edit_dialog_factory = (
            lambda parent, submit_handler, initial_draft: _AutoSubmitEditDialog(
                None,
                submit_handler,
                initial_draft,
                lambda dialog: (
                    _assert(
                        dialog.title_input.text() == "Open Reports",
                        "Created Tasks navigation should route into the existing edit dialog",
                    ),
                    dialog.type_combo.setCurrentText("File"),
                    dialog.title_input.setText("Open Weekly Reports"),
                    dialog.aliases_input.setText("weekly reports"),
                    dialog.target_input.setText(r"C:\Reports\weekly.txt"),
                ),
                edit_dialogs,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_created_tasks_requested(window)

        inventory = window._command_model.view_payload().get("saved_action_inventory") or {}
        items = inventory.get("items") or []

        _assert(created_tasks_dialogs, "Manage Custom Tasks navigation should open the secondary management dialog")
        _assert(edit_dialogs, "Manage Custom Tasks navigation should route selected items into the existing edit dialog")
        _assert(
            items and items[0].get("title") == "Open Weekly Reports",
            "Manage Custom Tasks navigation should preserve the existing edit/update behavior",
        )
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "Manage Custom Tasks navigation should still restore fallback input capture readiness afterward",
        )


def _test_created_tasks_navigation_routes_into_delete_flow():
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
    },
    {
      "id": "knowledge_pages",
      "title": "Knowledge Pages",
      "target_kind": "url",
      "target": "https://example.com/docs",
      "aliases": ["knowledge pages"]
    }
  ]
}
""",
            encoding="utf-8",
        )
        window = _make_window(source_path)
        created_tasks_dialogs = []
        window._created_tasks_dialog_factory = (
            lambda parent, inventory_payload: _AutoSelectCreatedTasksDialog(
                None,
                inventory_payload,
                lambda dialog: (
                    _assert(
                        dialog.title_label.text() == "Manage Custom Tasks",
                        "Manage Custom Tasks delete flow should keep a stable main header and leave counts to the status line",
                    ),
                    dialog._handle_delete_requested("open_reports"),
                ),
                created_tasks_dialogs,
            )
        )

        renderer_mod.DesktopRuntimeWindow.handle_created_tasks_requested(window)

        inventory = window._command_model.view_payload().get("saved_action_inventory") or {}
        items = inventory.get("items") or []

        _assert(created_tasks_dialogs, "Manage Custom Tasks delete flow should open the secondary management dialog")
        _assert(window._command_model.phase == "entry", "delete flow should preserve entry phase")
        _assert(window._command_model.status_kind == "ready", "delete flow should surface success feedback")
        _assert("deleted" in window._command_model.status_text.casefold(), "delete flow should confirm the removal")
        _assert(inventory.get("count") == 1, "delete flow should reduce the visible inventory count immediately")
        _assert(
            tuple(item.get("id") for item in items) == ("knowledge_pages",),
            "delete flow should remove the selected saved action from the visible inventory immediately",
        )
        _assert(
            "open_reports" not in source_path.read_text(encoding="utf-8"),
            "delete flow should persist the removal to the saved-action source",
        )
        _assert(
            renderer_mod.DesktopRuntimeWindow.overlay_needs_global_input_capture(window),
            "delete flow should still restore fallback input capture readiness afterward",
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
            "website tasks need the full address" in dialog_instances[0].status_label.text().casefold(),
            "invalid edit input should explain how the target should be fixed",
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
        ("Created Tasks trigger present and clickable", _test_created_tasks_trigger_is_present_and_clickable),
        ("Create Custom Group trigger present and clickable", _test_create_custom_group_trigger_is_present_and_clickable),
        ("Manage Custom Groups trigger present and clickable", _test_manage_custom_groups_trigger_is_present_and_clickable),
        ("entry surface stays button-led", _test_entry_surface_keeps_inventory_details_out_of_landing_view),
        ("entry surface positions panel as right sidecar", _test_entry_surface_positions_panel_as_right_sidecar),
        ("Created Tasks dialog exposes edit trigger", _test_created_tasks_dialog_exposes_edit_trigger_for_saved_inventory_items),
        ("Created Tasks dialog exposes delete trigger", _test_created_tasks_dialog_exposes_delete_trigger_for_saved_inventory_items),
        ("Created Tasks dialog keeps edit reachability beyond six items", _test_created_tasks_dialog_edit_reachability_extends_beyond_six_items),
        ("Created Tasks dialog caps loaded viewport to five rows", _test_created_tasks_dialog_caps_loaded_viewport_to_five_rows),
        ("Created Groups dialog exposes group management triggers", _test_created_groups_dialog_exposes_group_management_triggers),
        ("Created Groups dialog caps loaded viewport to five rows", _test_created_groups_dialog_caps_loaded_viewport_to_five_rows),
        ("type-first dialog maps supported kinds", _test_type_first_dialog_maps_all_supported_kinds),
        ("create dialog surfaces field-level guidance", _test_create_dialog_surfaces_field_level_guidance),
        ("create dialog supports group assignment and inline group queue", _test_create_dialog_supports_group_assignment_and_inline_group_queue),
        ("group create dialog surfaces members and exact alias guidance", _test_group_create_dialog_surfaces_members_and_exact_alias_guidance),
        ("assignment group create reuses group dialog without member picker", _test_assignment_group_create_reuses_group_dialog_without_member_picker),
        ("create dialog trigger controls and dynamic examples", _test_create_dialog_trigger_controls_and_dynamic_examples),
        ("edit dialog default trigger follows type until changed", _test_edit_dialog_default_trigger_follows_type_until_changed),
        ("legacy edit dialog preserves bare callable examples until trigger changes", _test_legacy_edit_dialog_preserves_bare_callable_examples_until_trigger_changes),
        ("create dialog supports browse-assisted target selection", _test_create_dialog_supports_browse_assisted_target_selection),
        ("successful create flow reloads inventory", _test_successful_create_flow_reloads_inventory_immediately),
        ("invalid input shows dialog error without write", _test_invalid_input_shows_dialog_error_and_does_not_write),
        ("invalid folder target shows dialog error without write", _test_invalid_folder_target_shows_dialog_error_and_does_not_write),
        ("invalid application target shows dialog error without write", _test_invalid_application_target_shows_dialog_error_and_does_not_write),
        ("invalid file target shows dialog error without write", _test_invalid_file_target_shows_dialog_error_and_does_not_write),
        ("unsafe source blocks before dialog open", _test_unsafe_source_blocks_before_dialog_open),
        ("Created Tasks navigation routes into edit dialog", _test_created_tasks_navigation_routes_into_edit_dialog),
        ("Created Tasks navigation routes into delete flow", _test_created_tasks_navigation_routes_into_delete_flow),
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
