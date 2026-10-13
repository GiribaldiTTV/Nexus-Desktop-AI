"""Validate the FAM-003 resident access / quick actions workstream contract."""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def assert_true(condition: bool, message: str, failures: list[str]):
    if not condition:
        failures.append(message)


def function_block(text: str, function_name: str) -> str:
    marker = f"    def {function_name}"
    start = text.find(marker)
    if start == -1:
        return ""
    end = text.find("\n    def ", start + len(marker))
    return text[start:] if end == -1 else text[start:end]


def validate_no_forced_arrow_release(renderer_text: str, failures: list[str]):
    cursor_helpers = (
        "_apply_settings_windows_resize_cursor",
        "_apply_ai_control_center_windows_resize_cursor",
        "_apply_monitoring_hud_windows_resize_cursor",
    )
    for helper_name in cursor_helpers:
        block = function_block(renderer_text, helper_name)
        assert_true(block, f"{helper_name} missing", failures)
        assert_true(
            "resize-cursor-no-forced-arrow-release" in block,
            f"{helper_name} must document no forced IDC_ARROW release",
            failures,
        )
        guard = "if not edges:\n            return"
        assert_true(
            guard in block,
            f"{helper_name} must return early when no resize edge is active",
            failures,
        )
        if guard in block and "LoadCursorW" in block:
            assert_true(
                block.index(guard) < block.index("LoadCursorW"),
                f"{helper_name} must skip LoadCursorW before no-edge cursor release",
                failures,
            )
        if guard in block and "SetCursor" in block:
            assert_true(
                block.index(guard) < block.index("SetCursor"),
                f"{helper_name} must skip SetCursor before no-edge cursor release",
                failures,
            )


def validate_resident_model(failures: list[str]):
    from desktop.resident_access import (
        DEFAULT_QUICK_SLOT_COUNT,
        DEFAULT_QUICK_SLOT_ROUTE_IDS,
        IMMUTABLE_ROUTE_IDS,
        MAX_QUICK_SLOT_COUNT,
        OPTIONAL_FEATURE_ROUTE_DISABLED_BY_USER,
        OPTIONAL_FEATURE_ROUTE_ENABLED_AVAILABLE,
        OPTIONAL_FEATURE_ROUTE_ENABLED_ERRORED,
        OPTIONAL_FEATURE_ROUTE_ENABLED_NOT_READY,
        OPTIONAL_FEATURE_ROUTE_ENABLED_TEMPORARILY_BLOCKED,
        OPTIONAL_FEATURE_ROUTE_NOT_INSTALLED,
        OPTIONAL_FEATURE_ROUTE_UNKNOWN,
        OPTIONAL_FEATURE_ROUTE_UNSUPPORTED,
        TRAY_DISCOVERY_MESSAGE,
        TRAY_IDENTITY_LABEL,
        TRAY_MENU_STRUCTURE,
        TRAY_TOOLTIP_TEXT,
        WINDOWS_TRAY_VISIBILITY_LIMITATION,
        build_monitoring_hud_route_model,
        build_optional_feature_route_state_model,
        build_resident_access_menu_plan,
        normalize_resident_access_settings,
        quick_slot_candidate_routes,
    )

    plan = build_resident_access_menu_plan()
    immutable_ids = [route["routeId"] for route in plan["immutableRoutes"]]
    quick_ids = [route["routeId"] for route in plan["quickSlots"]]
    candidate_ids = [route["routeId"] for route in plan["candidateRoutes"]]
    future_gated_candidate_ids = [route["routeId"] for route in plan["futureGatedCandidateRoutes"]]
    route_owner = {route["routeId"]: route["ownerFamily"] for route in plan["immutableRoutes"]}
    menu_structure = plan["menuStructure"]

    assert_true(TRAY_IDENTITY_LABEL == "Nexus Desktop AI", "tray identity label drifted", failures)
    assert_true(
        TRAY_TOOLTIP_TEXT.startswith("Nexus Desktop AI - ")
        and "Provider-visible data: none" in TRAY_TOOLTIP_TEXT,
        "tray icon hover tooltip must carry compact FAM-003 resident AI/privacy status",
        failures,
    )
    assert_true(tuple(immutable_ids) == IMMUTABLE_ROUTE_IDS, "immutable route order drifted", failures)
    assert_true(
        set(IMMUTABLE_ROUTE_IDS)
        == {
            "global_settings",
            "hud_dashboard",
            "ai_status_command_center",
            "exit_nexus",
        },
        "immutable route set is incomplete",
        failures,
    )
    assert_true(
        immutable_ids[0] == "global_settings",
        f"Global Settings must be the first immutable command route: {immutable_ids}",
        failures,
    )
    assert_true(route_owner.get("hud_dashboard") == "FAM-006", "HUD Dashboard owner must remain FAM-006", failures)
    assert_true(
        plan["hudState"]["routeState"] == OPTIONAL_FEATURE_ROUTE_UNKNOWN,
        f"default missing HUD route state must hide as unknown optional route: {plan['hudState']}",
        failures,
    )
    assert_true(
        plan["hudState"]["visibleInActiveMenu"] is False
        and plan["hudState"]["enabledInActiveMenu"] is False,
        f"default HUD route must be hidden from active menu: {plan['hudState']}",
        failures,
    )
    assert_true(
        route_owner.get("ai_status_command_center") == "FAM-007",
        "AI Status / Command Center owner must remain FAM-007",
        failures,
    )
    assert_true(
        tuple(quick_ids) == DEFAULT_QUICK_SLOT_ROUTE_IDS,
        f"default quick slots drifted: {quick_ids}",
        failures,
    )
    assert_true(
        all(route.enabled for route in quick_slot_candidate_routes()),
        f"active quick-slot candidates must expose only enabled routes: {candidate_ids}",
        failures,
    )
    assert_true(
        "recording_studio" not in candidate_ids
        and "log_viewer" not in candidate_ids
        and tuple(future_gated_candidate_ids) == ("recording_studio", "log_viewer"),
        f"future-gated FAM-006 quick-slot routes must stay out of active UI candidates: active={candidate_ids}; future={future_gated_candidate_ids}",
        failures,
    )
    assert_true(
        plan["menuBudget"]["defaultQuickSlots"] == DEFAULT_QUICK_SLOT_COUNT,
        "default quick-slot count must remain three",
        failures,
    )
    assert_true(
        plan["menuBudget"]["maximumQuickSlots"] == MAX_QUICK_SLOT_COUNT == 5,
        "maximum quick-slot budget must remain five",
        failures,
    )
    assert_true(
        "cannot force permanent tray placement" in WINDOWS_TRAY_VISIBILITY_LIMITATION,
        "Windows tray visibility limitation proof wording is missing force-placement honesty",
        failures,
    )
    assert_true(
        "hidden icons" in TRAY_DISCOVERY_MESSAGE,
        "tray discovery message must mention hidden icons",
        failures,
    )
    assert_true(
        "single tray icon" in plan["singleTrayIconContract"],
        "single tray icon contract is missing",
        failures,
    )
    assert_true(
        "Provider-visible data: none" in plan["aiPrivacy"]["providerVisibleDataLabel"],
        "AI/privacy status must preserve provider-visible data none",
        failures,
    )
    assert_true(
        str(plan.get("tooltipText", "")).startswith("Nexus Desktop AI - ")
        and "Provider-visible data: none" in str(plan.get("tooltipText", ""))
        and "Provider-visible data: none" in str(plan.get("statusLabel", "")),
        "resident access plan must carry compact AI/privacy status in both tray icon hover tooltip and visible status label",
        failures,
    )
    assert_true(
        TRAY_MENU_STRUCTURE["nativeStatusRow"] is False
        and menu_structure["nativeStatusRow"] is False,
        "native tray menu must not carry a long status/header row",
        failures,
    )
    assert_true(
        tuple(menu_structure["topLevel"]) == ("Global Settings", "Quick Access", "AI", "Exit Nexus Desktop AI"),
        f"native tray menu top-level structure drifted: {menu_structure['topLevel']}",
        failures,
    )
    assert_true(
        tuple(menu_structure["quickAccessMenu"]) == DEFAULT_QUICK_SLOT_ROUTE_IDS
        or tuple(menu_structure["quickAccessMenu"])
        == ("Command Overlay", "Create Task", "Saved Actions"),
        f"Quick Access submenu structure drifted: {menu_structure['quickAccessMenu']}",
        failures,
    )
    assert_true(
        tuple(menu_structure["aiMenu"]) == ("AI Status / Command Center",),
        f"AI submenu structure drifted: {menu_structure['aiMenu']}",
        failures,
    )
    assert_true(
        tuple(menu_structure["deferredOwnerMenus"]) == ("Developer", "Owner")
        and "Deferred to FAM-007" in menu_structure["developerOwnerDisposition"],
        "Developer/Owner tray categories must remain deferred to FAM-007 planning",
        failures,
    )

    normalized = normalize_resident_access_settings(
        {
            "quickSlotIds": [
                "command_overlay",
                "command_overlay",
                "recording_studio",
                "unknown",
                "log_viewer",
                "tray_visibility_education",
                "open_saved_actions_folder",
            ],
            "menuBudget": 99,
        }
    )
    assert_true(
        normalized.quick_slot_ids
        == (
            "command_overlay",
            "tray_visibility_education",
            "open_saved_actions_folder",
        ),
        f"quick-slot normalization failed: {normalized.quick_slot_ids}",
        failures,
    )
    assert_true(normalized.menu_budget == 5, "quick-slot menu budget did not clamp to five", failures)

    state_matrix = {
        OPTIONAL_FEATURE_ROUTE_ENABLED_AVAILABLE: (True, True),
        OPTIONAL_FEATURE_ROUTE_ENABLED_TEMPORARILY_BLOCKED: (True, False),
        OPTIONAL_FEATURE_ROUTE_ENABLED_ERRORED: (True, False),
        OPTIONAL_FEATURE_ROUTE_ENABLED_NOT_READY: (True, False),
        OPTIONAL_FEATURE_ROUTE_DISABLED_BY_USER: (False, False),
        OPTIONAL_FEATURE_ROUTE_NOT_INSTALLED: (False, False),
        OPTIONAL_FEATURE_ROUTE_UNSUPPORTED: (False, False),
        OPTIONAL_FEATURE_ROUTE_UNKNOWN: (False, False),
    }
    for state_id, (expected_visible, expected_enabled) in state_matrix.items():
        model = build_optional_feature_route_state_model(
            raw_state=state_id,
            feature_enabled=state_id.startswith("enabled"),
            reason="Owner-bounded reason",
        )
        assert_true(
            model["visibleInActiveMenu"] is expected_visible
            and model["enabledInActiveMenu"] is expected_enabled,
            f"optional feature state model drifted for {state_id}: {model}",
            failures,
        )

    for state_id in (
        OPTIONAL_FEATURE_ROUTE_DISABLED_BY_USER,
        OPTIONAL_FEATURE_ROUTE_NOT_INSTALLED,
        OPTIONAL_FEATURE_ROUTE_UNSUPPORTED,
        OPTIONAL_FEATURE_ROUTE_UNKNOWN,
    ):
        hud_model = build_monitoring_hud_route_model(
            {
                "feature_enabled": False,
                "resident_route_state": state_id,
                "resident_route_reason": "Owner-bounded reason",
            }
        )
        assert_true(
            hud_model["visibleInActiveMenu"] is False,
            f"HUD {state_id} must hide tray/menu rows: {hud_model}",
            failures,
        )

    blocked_hud_model = build_monitoring_hud_route_model(
        {
            "feature_enabled": True,
            "resident_route_state": OPTIONAL_FEATURE_ROUTE_ENABLED_TEMPORARILY_BLOCKED,
            "resident_route_reason": "Dashboard is warming up",
        }
    )
    assert_true(
        blocked_hud_model["visibleInActiveMenu"] is True
        and blocked_hud_model["enabledInActiveMenu"] is False
        and blocked_hud_model["disabledWithReason"] is True
        and blocked_hud_model["ownerBoundedReason"] == "Dashboard is warming up",
        f"temporarily blocked HUD route must show disabled with reason: {blocked_hud_model}",
        failures,
    )


def validate_static_wiring(failures: list[str]):
    tray_text = read("desktop/tray_controller.py")
    renderer_text = read("desktop/desktop_renderer.py")
    main_text = read("desktop/orin_desktop_main.py")

    ast.parse(tray_text, filename="desktop/tray_controller.py")
    ast.parse(renderer_text, filename="desktop/desktop_renderer.py")
    ast.parse(main_text, filename="desktop/orin_desktop_main.py")
    validate_no_forced_arrow_release(renderer_text, failures)
    settings_dialog_start = renderer_text.index("class ResidentAccessSettingsDialog")
    settings_dialog_end = renderer_text.index("class AIControlCenterCommandPage")
    settings_dialog_text = renderer_text[settings_dialog_start:settings_dialog_end]

    assert_true("SP_ComputerIcon" not in tray_text, "tray icon still falls back to monitor/computer icon", failures)
    assert_true(
        'focus="tray_visibility"' not in renderer_text,
        "Tray Help quick action must not route to an unsupported tray_visibility focus",
        failures,
    )
    assert_true(
        'self.open_resident_access_settings(source=source, focus="tray")' in renderer_text
        and "Tray visibility help and future click behavior settings." in settings_dialog_text
        and "WINDOWS_TRAY_VISIBILITY_LIMITATION" in settings_dialog_text,
        "Tray Help quick action must open the Tray parent page with honest Windows tray visibility copy",
        failures,
    )
    assert_true(
        "SETTINGS_FOCUS_ALIASES" in settings_dialog_text
        and '"ai_status": "tray"' in settings_dialog_text
        and '"privacy": "tray"' in settings_dialog_text
        and '"owner_routes": "tray"' in settings_dialog_text
        and "self._focus_context = requested_focus" in settings_dialog_text
        and "SETTINGS_TRAY_CONTEXT_DETAILS" in settings_dialog_text,
        "route-only settings focus targets must preserve context on the Tray parent page instead of falling through to Quick Access",
        failures,
    )
    for token in (
        "build_resident_tray_icon",
        "TRAY_RESIDENT_ACCESS_TRAY_ICON_READY",
        "_monitoring_hud_route_model",
        "_monitoring_hud_dashboard_menu_text",
        "route_hidden",
        "route_unavailable",
        "request_global_settings_from_tray",
        "request_ai_status_from_tray",
        "TRAY_AI_STATUS_COMMAND_CENTER_ROUTED",
        "request_privacy_lockdown_from_tray",
        "request_quick_slot_from_tray",
        "TRAY_RESIDENT_ACCESS_ACTIONS_REFRESHED",
        "_resident_menu_identity_text",
        "self.quick_access_menu = self.tray_menu.addMenu(\"Quick Access\")",
        "self.ai_menu = self.tray_menu.addMenu(\"AI\")",
        "parent_menu=self.quick_access_menu",
        "parent_menu=self.ai_menu",
        "MF_POPUP",
        "UINT_PTR = getattr(ctypes.wintypes, \"UINT_PTR\", ctypes.c_size_t)",
        "user32.CreatePopupMenu.restype = HMENU",
        "user32.AppendMenuW.argtypes = [HMENU, UINT, UINT_PTR, LPCWSTR]",
        "UINT_PTR(int(submenu))",
        "append_submenu(menu, quick_access_menu, \"Quick Access\", True)",
        "append_submenu(menu, ai_menu, \"AI\", True)",
        "nexusDesktopTrayStatus",
        "#07111f",
    ):
        assert_true(token in tray_text, f"tray resident access token missing: {token}", failures)
    assert_true(
        '"AI Control Center"' not in tray_text
        and "self.ai_control_center_action = self._add_button_action(" not in tray_text
        and 'append(ai_menu, 90, "AI Control Center", True)' not in tray_text,
        "tray AI submenu must expose only the compact AI Status / Command Center doorway",
        failures,
    )
    assert_true(
        '"AI Status / Command Center"' in tray_text
        and 'append(ai_menu, 120, "AI Status / Command Center", True)' in tray_text,
        "native tray menu must keep the single FAM-007-owned AI Status / Command Center doorway",
        failures,
    )
    assert_true(
        'self.global_settings_action = self._add_button_action(' in tray_text
        and tray_text.index('self.global_settings_action = self._add_button_action(')
        < tray_text.index('self.quick_access_menu = self.tray_menu.addMenu("Quick Access")')
        < tray_text.index('self.ai_menu = self.tray_menu.addMenu("AI")')
        < tray_text.index('self.monitoring_hud_primary_action = self._add_button_action(')
        and tray_text.index('append(menu, 110, "Global Settings", True)')
        < tray_text.index('append_submenu(menu, quick_access_menu, "Quick Access", True)')
        < tray_text.index('append_submenu(menu, ai_menu, "AI", True)')
        < tray_text.index('if hud_route_visible:'),
        "Global Settings and Quick Access must lead the native tray/menu command order",
        failures,
    )
    assert_true(
        'self.global_settings_button = self.tray_popup.add_button(' in tray_text
        and tray_text.index('self.global_settings_button = self.tray_popup.add_button(')
        < tray_text.index('self.quick_slot_buttons.append(button)')
        < tray_text.index('self.ai_status_button = self.tray_popup.add_button(')
        < tray_text.index('self.monitoring_hud_status_label = QLabel('),
        "Global Settings and Quick Access must lead the resident fallback popup order",
        failures,
    )
    assert_true(
        "app.setWindowIcon(build_resident_tray_icon())" in main_text,
        "runtime QApplication must bind the branch-local resident icon for taskbar/window identity proof",
        failures,
    )
    assert_true(
        "_native_menu_status_text" not in tray_text
        and "append(80," not in tray_text
        and "nativeStatusRow\": False" not in tray_text,
        "native tray menu must not keep a long status/header row implementation",
        failures,
    )
    assert_true(
        'self.privacy_lockdown_action = self._add_button_action(' not in tray_text
        and 'self.privacy_lockdown_button = self.tray_popup.add_button(' not in tray_text
        and 'append(130, "Privacy Lockdown"' not in tray_text
        and "130: self.request_privacy_lockdown_from_tray" not in tray_text,
        "Privacy Lockdown must not appear as a top-level tray/menu action until FAM-007 admits a real immediate action",
        failures,
    )
    assert_true(
        'append(100, "Enable HUD Feature"' not in tray_text
        and "append(100, feature_text" not in tray_text,
        "native tray menu must not expose a forced Enable HUD Feature row",
        failures,
    )
    assert_true(
        "settings_owned_optional_feature_configuration" in tray_text,
        "tray HUD toggle fallback must redirect to settings-owned optional feature configuration",
        failures,
    )

    for token in (
        "class ResidentAccessSettingsDialog",
        "open_resident_access_settings",
        "resident_access_status_snapshot",
        "request_ai_status_from_resident_access",
        "request_privacy_lockdown_from_resident_access",
        "request_resident_quick_action_from_tray",
        "self._replace_quick_slots(self._selected_slot_ids())",
        "setAccessibleName(\"Add Quick Access Slot\")",
        "BASE_MINIMUM_SIZE = (684, 388)",
        "MAXIMUM_SIZE = (840, 610)",
        "DEFAULT_SIZE = (780, 458)",
        "QUICK_SLOT_ROW_HEIGHT = 38",
        "setMinimumSize(*self.BASE_MINIMUM_SIZE)",
        "setMaximumSize(*self.MAXIMUM_SIZE)",
        "surfaceClassification\", \"Nexus-Owned Product Surface",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-deterministic-rail-v22",
        "settingsVisualRepair\", \"lv1-global-settings-compact-ndai-grammar-close-intercept-v32",
        "referenceDerivedHeader\", \"ndai-global-settings-centered-settings-chrome-v22",
        "dirtyGuardReference\", \"manage-monitors-modal-save-discard-cancel",
        "standardWindowArchitecture\", \"pyside-dialogchrome-native-edge-corner-hit-test-reference-derived",
        "windowResizeBehavior\", \"uiref-007-frameless-top-level-hover-polled-edge-corner-cursor-app-owned-fallback-8px-edge-12px-corner-no-visible-grip-splitter-travel-76-270-horizontal-overflow-minimum-684x388-dynamic-content-minimum-maximum-840x610-close-intercept-cursor-release-hysteresis-v42",
        "quickAccessLayoutPolicy\", \"uiref-007-deterministic-row-width-combo-integrated-action-capsule-row-count-close-intercept-v42",
        "settingsRailPolishPolicy\", \"fixed-gap-deterministic-text-width-sharpened-icons-horizontal-overflow-splitter-travel-v41",
        "settingsNavSizingPolicy\", \"font-metric-default-min-clamped-v39",
        "categoryIconRenderPolicy\", \"high-contrast-contained-12px-v38",
        "contentScalePolicy\", \"control-pill-anchored-proportional-content-scale-v32",
        "dirtyCloseRouteCoverage\", \"window-close-system-close-keybind-client-shutdown-save-discard-cancel-v32",
        "dirtyCloseInterceptState\", \"idle",
        "visibleResizeGrip\", \"removed",
        "deferredWatermarkConcept\", \"future-centered-global-settings-watermark-deferred-no-runtime-exposure-v22",
        "runtimeWatermarkVisible\", \"false",
        "uiExposureContract\", \"real-enabled-meaningful-visible-ui-v1",
        "sharedPrimitiveClaim\", \"none-promoted-reference-derived-only",
        "referenceComparatorRequired\", \"ui-reference-plus-product-grade-same-defect-comparator-v22",
        "RESIZE_MARGIN = 8",
        "RESIZE_CORNER_MARGIN = 12",
        "RESIZE_CURSOR_RELEASE_MARGIN = 2",
        "_settings_resize_hover_timer",
        "_poll_settings_resize_hover_cursor",
        "_settings_should_clear_resize_cursor",
        "_settings_point_belongs_to_window",
        "_install_settings_resize_event_filters",
        "_start_settings_resize",
        "_finish_settings_resize",
        "def eventFilter",
        "_settings_resize_edges_for_hit_test",
        "_apply_settings_windows_resize_cursor",
        "def resizeEvent",
        "NexusSettingsSplitter(Qt.Horizontal, body)",
        "residentAccessSettingsSplitter",
        "setHandleWidth(9)",
        "quiet-default-hover-dots-9px-hit-zone-v28",
        "Resize Global Settings navigation pane",
        "settings_header=True",
        "\"Settings\"",
        "SETTINGS_NAV_MAX_WIDTH = 270",
        "setMaximumWidth(self.SETTINGS_NAV_MAX_WIDTH)",
        "setMinimumWidth(486)",
        "setMaximumWidth(660)",
        "content_layout.addWidget(self.settings_page_frame, 0, Qt.AlignTop)",
        "_quick_slot_combo_width_for_row",
        "combo.setMinimumWidth(self.QUICK_SLOT_COMBO_MIN_WIDTH)",
        "combo.setMaximumWidth(self.QUICK_SLOT_COMBO_MAX_WIDTH)",
        "action_cluster.setFixedWidth(self.QUICK_SLOT_ACTION_CLUSTER_WIDTH)",
        "def nativeEvent",
        "_settings_native_hit_test",
        "NexusCategoryIcon(\"tray\"",
        "NexusCategoryIcon(\"quick-access\"",
        "NexusGlyphButton(\"up\"",
        "NexusGlyphButton(\"down\"",
        "NexusGlyphButton(\"close\"",
        "residentAccessSettingsWindowControls",
        "residentAccessSettingsChromeMinimize",
        "residentAccessSettingsChromeClose",
        "residentAccessSettingsNavShell",
        "residentAccessSettingsCategoryItem",
        "residentAccessSettingsCategoryButton",
        "settingsCategoryRole\", \"selectable-parent-page",
        "slim-parent-row",
        "SETTINGS_NAV_MIN_WIDTH = 76",
        "setMinimumWidth(self.SETTINGS_NAV_MIN_WIDTH)",
        "setMaximumWidth(self.SETTINGS_NAV_MAX_WIDTH)",
        "residentAccessSettingsNavScrollArea",
        "setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)",
        "setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)",
        "residentAccessSettingsNavContent",
        "SETTINGS_NAV_CONTENT_MIN_WIDTH = 144",
        "setMinimumWidth(self.SETTINGS_NAV_CONTENT_MIN_WIDTH)",
        "residentAccessSettingsNavPrimaryIcon",
        "residentAccessSettingsNavExpander",
        "def _toggle_tray_children",
        "contains-selected",
        "self._nav_buttons[\"tray\"]",
        "self.set_focus(\"tray\")",
        "residentAccessTrayOverviewContainer",
        "Tray visibility help and future click behavior settings.",
        "WINDOWS_TRAY_VISIBILITY_LIMITATION",
        "residentAccessSettingsSubpageRail",
        "settingsShellIdentity\", \"ndai-slim-global-settings",
        "residentAccessSettingsNavItem",
        "two-level-subpage-row",
        "settingsNavIdentity\", \"ndai-signal-leaf",
        "residentAccessSettingsNavButton",
        "residentAccessSettingsNavCaption",
        "quick_access_label = \"Quick Access\"",
        "QPushButton(quick_access_label",
        "quick_access_nav_caption.setVisible(False)",
        "Tray",
        "residentAccessSettingsSectionBadge",
        "self.section_badge.setVisible(False)",
        "residentAccessSettingsPageFrame",
        "residentAccessSettingsStateText",
        "_apply_quick_slot_row_geometry",
        "combo.setMinimumWidth(self.QUICK_SLOT_COMBO_MIN_WIDTH)",
        "setMaxVisibleItems(4)",
        "popup.setMinimumHeight(132)",
        "popup.setMaximumHeight(136)",
        "Quick Access",
        "slot_count_badge",
        "residentAccessSettingsSlotCount",
        "residentAccessSettingsFooter",
        "#residentAccessSettingsFooter",
        "border: none;",
        "QPushButton(\"Defaults\"",
        "quick_help.setVisible(False)",
        "def _available_quick_slot_limit",
        "self.add_slot_button.setEnabled(len(selected_ids) < self._available_quick_slot_limit())",
        "residentAccessQuickSlotActions",
        "residentAccessQuickSlotReorderGroup",
        "residentAccessQuickSlotMoveUp",
        "residentAccessQuickSlotMoveDown",
        "residentAccessQuickSlotDelete",
        "residentAccessQuickSlotReorderDivider",
        "QuickSlotReorderPill(action_cluster)",
        "quickSlotActionControlPolicy\", \"two-pill-reorder-delete-parent-painted-segment-fill-v47",
        "quickSlotReorderSplitPolicy\", \"parent-painted-25-1-25-exact-segment-fill-v47",
        "setProperty(\"glyphZoneButton\", True)",
        "setProperty(\"glyphSegment\", \"left\")",
        "setProperty(\"glyphSegment\", \"right\")",
        "setProperty(\"glyphSegment\", \"standalone-danger\")",
        "up_button.setFixedSize(25, 27)",
        "delete_button.setFixedSize(28, 27)",
        "Default shortcut order staged.",
        "QPushButton(\"Save\"",
        "Discard",
        "residentAccessCloseGuardOverlay",
        "residentAccessCloseGuardPanel",
        "residentAccessCloseGuardSave",
        "residentAccessCloseGuardDiscard",
        "residentAccessCloseGuardCancel",
        "guardActionLayout\", \"modal-save-discard-cancel",
        "guardVisualRole\", \"primary-save",
        "guardVisualRole\", \"destructive-discard",
        "guardVisualRole\", \"neutral-cancel",
        "Unsaved Quick Access changes",
        "Save changes or discard the draft before continuing.",
        "def _has_unsaved_changes",
        "def closeEvent",
        "def keyPressEvent",
        "def done",
        "request_dirty_close_intercept",
        "_close_guard_pending_callback",
        "request_resident_access_settings_shutdown_guard",
        "RESIDENT_ACCESS_SETTINGS_DIRTY_CLOSE_BLOCKED",
        "_open_close_guard",
        "WM_CLOSE = 0x0010",
        "WM_SYSCOMMAND = 0x0112",
        "SC_CLOSE = 0xF060",
        "quietGlyph",
        "compact_labels = {",
        "RESIDENT_ACCESS_PRIVACY_LOCKDOWN_ROUTE_ONLY",
    ):
        assert_true(token in renderer_text, f"renderer resident access token missing: {token}", failures)

    for token in (
        "Connected Surfaces",
        "connected_surfaces",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-quick-access-v9",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-category-quick-access-subpage-v10",
        "settingsVisualRepair\", \"settings-specific-conformance-v9-tray-scoped-ndai-slim",
        "settingsVisualRepair\", \"settings-ia-exposure-contract-v10",
        "settingsInformationArchitecture\", \"global-settings-shell-selectable-tray-parent-quick-access-child-v11",
        "settingsVisualRepair\", \"settings-ia-self-adjudication-v11",
        "referenceDerivedHeader\", \"compact-ndai-settings-window-frame-v11",
        "settingsInformationArchitecture\", \"global-settings-shell-selectable-tray-parent-quick-access-child-v12",
        "settingsVisualRepair\", \"settings-ia-window-behavior-v12",
        "referenceDerivedHeader\", \"compact-ndai-settings-window-frame-v12",
        "windowResizeBehavior\", \"frameless-top-level-qsizegrip-minimum-760x350-v12",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-v13",
        "settingsVisualRepair\", \"visual-udl-conformance-v13",
        "referenceDerivedHeader\", \"integrated-ndai-settings-window-frame-v13",
        "windowResizeBehavior\", \"frameless-top-level-qsizegrip-minimum-760x320-v13",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-g2-v14",
        "settingsVisualRepair\", \"vat-opt-g2-implementation-match-v14",
        "referenceDerivedHeader\", \"integrated-ndai-settings-window-frame-g2-v14",
        "windowResizeBehavior\", \"frameless-top-level-qsizegrip-minimum-760x320-v14",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-resizable-rail-v15",
        "settingsVisualRepair\", \"lv1-user-fail-repair-v15",
        "referenceDerivedHeader\", \"integrated-ndai-settings-window-frame-v15",
        "windowResizeBehavior\", \"frameless-top-level-qsizegrip-splitter-minimum-800x340-v15",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-resizable-rail-v16",
        "settingsVisualRepair\", \"lv1-false-retest-defect-closure-repair-v16",
        "referenceDerivedHeader\", \"ai-control-center-compact-hero-settings-frame-v16",
        "windowResizeBehavior\", \"frameless-top-level-native-edge-hit-test-qsizegrip-splitter-minimum-700x360-v16",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-resizable-rail-v17",
        "settingsVisualRepair\", \"lv1-global-settings-window-class-repair-v17",
        "referenceDerivedHeader\", \"ndai-global-settings-single-row-chrome-v17",
        "windowResizeBehavior\", \"frameless-top-level-native-edge-hit-test-qsizegrip-splitter-minimum-700x360-v17",
        "referenceComparatorRequired\", \"ui-reference-plus-broad-ndai-comparator-v17",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-deterministic-rail-v18",
        "settingsVisualRepair\", \"lv1-global-settings-deterministic-layout-repair-v18",
        "referenceDerivedHeader\", \"ndai-global-settings-single-row-chrome-v18",
        "windowResizeBehavior\", \"frameless-top-level-native-edge-hit-test-qsizegrip-splitter-minimum-620x318-v18",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-deterministic-rail-v19",
        "settingsVisualRepair\", \"lv1-global-settings-manage-monitors-dirty-guard-alignment-v19",
        "referenceDerivedHeader\", \"ndai-global-settings-single-row-chrome-v19",
        "windowResizeBehavior\", \"frameless-top-level-native-edge-hit-test-qsizegrip-splitter-minimum-620x318-v19",
        "referenceComparatorRequired\", \"ui-reference-plus-manage-monitors-dirty-guard-comparator-v19",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-deterministic-rail-v20",
        "settingsVisualRepair\", \"lv1-global-settings-product-grade-same-defect-repair-v20",
        "referenceDerivedHeader\", \"ndai-global-settings-single-row-chrome-v20",
        "windowResizeBehavior\", \"frameless-top-level-native-edge-hit-test-qsizegrip-splitter-minimum-640x330-v20",
        "QSizeGrip(self.shell)",
        "residentAccessSettingsResizeGrip",
        "resizeAffordance\", \"bottom-right-qsizegrip",
        "settingsInformationArchitecture\", \"global-settings-shell-tray-parent-quick-access-child-deterministic-rail-v21",
        "settingsVisualRepair\", \"lv1-global-settings-standard-window-architecture-repair-v21",
        "referenceDerivedHeader\", \"ndai-global-settings-grouped-single-row-chrome-v21",
        "windowResizeBehavior\", \"frameless-top-level-native-edge-corner-hit-test-14px-no-visible-grip-splitter-minimum-640x318-v21",
        "referenceComparatorRequired\", \"ui-reference-plus-product-grade-same-defect-comparator-v21",
        "grouped_title = f\"{kicker} / {title}\" if kicker else title",
        "kicker=\"NEXUS DESKTOP AI\"",
        "referenceComparatorRequired\", \"ui-reference-plus-broad-ndai-comparator-v18",
        "3 active of",
        "self._notice_text = \"Saved\"",
        "setHandleWidth(8)",
        "setFixedWidth(150)",
        "self.nav_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)",
        "referenceComparatorRequired\", \"accepted-ai-control-center-contact-sheet",
        "hero_header=True",
        "compact_hero=True",
        "setMinimumSize(760, 320)",
        "setMinimumSize(800, 340)",
        "setFixedWidth(122)",
        "residentAccessTrayOverviewRow",
        "residentAccessTrayOverviewOpen",
        "residentAccessSettingsStateChip",
        "setMinimumWidth(156)",
        "setFixedSize(54, 22)",
        "No active Tray behavior settings are available yet.",
        "Save, discard, or cancel.",
        "QPushButton(\"Done\"",
        "residentAccessCloseButton",
        "Done With Global Settings",
        "referenceDerivedHeader\", \"compact-ndai-settings-window-frame-v9",
        "referenceDerivedHeader\", \"compact-ndai-settings-window-frame-v10",
        "settingsCategoryRole\", \"real-category-no-direct-page",
        "primary_nav_rail.setVisible(False)",
        "QPushButton(\"\\N{GEAR}\"",
        "Move Up",
        "Move Down",
        "UPWARDS ARROW",
        "DOWNWARDS ARROW",
        'QPushButton("Up"',
        'QPushButton("Down"',
        'QPushButton("X"',
        "Quick Access Slots",
        "Rows appear in tray order. Use Save Changes to apply them.",
        "Keep Editing",
        'suffix = "" if route.enabled else " (unavailable)"',
        "residentAccessQuickSlotRemove",
        "setMinimumSize(860, 560)",
        "settingsInformationArchitecture\", \"global-settings-shell-settings-navigation-quick-access-page-v6",
        "settingsInformationArchitecture\", \"global-settings-shell-two-level-tray-quick-access-v8",
        "settingsVisualRepair\", \"settings-specific-conformance-v6-product-ui",
        "settingsVisualRepair\", \"settings-specific-conformance-v8-exclusive-ndai-slim",
        "referenceDerivedHeader\", \"ai-control-center-family-comparator-settings-shell-v6",
        "referenceDerivedHeader\", \"compact-ndai-settings-window-frame-v8",
        "Settings for Nexus behavior.",
        "GLOBAL SETTINGS",
        "Tray doorway settings.",
        "Configure the tray submenu.",
        "residentAccessSettingsOverviewPanel",
        "residentAccessSettingsSummaryTitle",
        "residentAccessSettingsSummaryDetail",
        "setMinimumWidth(250)",
        "Choose up to {MAX_QUICK_SLOT_COUNT} shortcuts for the tray submenu.",
        "Reset Quick Access",
        "Restore Defaults",
        "Save Changes",
        "setMinimumSize(820, 520)",
        "setMinimumSize(700, 460)",
        "setMinimumSize(680, 408)",
        "setMinimumSize(880, 600)",
        "settingsInformationArchitecture\", \"left-navigation-active-settings-only",
        "settingsInformationArchitecture\", \"compact-settings-organizer-quick-access-page",
        "settingsInformationArchitecture\", \"global-settings-shell-settings-navigation-quick-access-page-v4",
        "settingsVisualRepair\", \"user-visual-fail-reference-conformance-v2",
        "settingsVisualRepair\", \"settings-specific-conformance-v4",
        "settingsVisualRepair\", \"settings-specific-conformance-v5-product-ui",
        "referenceDerivedHeader\", \"ai-control-center-reference-conformant-settings-shell-v2",
        "referenceDerivedHeader\", \"ai-control-center-family-comparator-settings-shell-v4",
        "referenceDerivedHeader\", \"ai-control-center-family-comparator-settings-shell-v5",
        "settingsInformationArchitecture\", \"global-settings-shell-settings-navigation-quick-access-page-v5",
        "compact-left-navigation-active-settings-page",
        "ai-control-center-window-anatomy",
        "Configure the Nexus tray.",
        "Quick Access is the active settings page.",
        "Nexus Tray Settings",
        "Native tray > Quick Access",
        "Shortcut Order",
        "Save applies Quick Access edits to the tray menu.",
        'suffix = "" if route.enabled else " (future-gated)"',
        "Nexus Tray and Quick Access settings.",
        "Resident tray shortcuts and menu preferences.",
        "Tray menu shortcuts",
        "PAGE\", \"QUICK ACCESS",
        "SCOPE\", \"TRAY MENU",
        "Active sections only.",
        "Future sections stay hidden until they become real settings.",
        "(\"SETTINGS AREA\", \"NEXUS TRAY\")",
        "(\"ACTIVE SETTING\", \"QUICK ACCESS\")",
        "Quick Access menu",
        "No pending changes",
        "residentAccessSettingsFactRow",
        "residentAccessSettingsFactLabel",
        "residentAccessSettingsFactValue",
        "Use Default Quick Access Shortcuts",
        "Use Defaults",
        "Order the shortcuts that appear in the tray submenu.",
        "Save Changes applies Quick Access edits to the tray menu.",
        "Stage Default Quick Access Slots",
        "Stage Defaults",
        "Tray Menu Shortcuts",
        "Discard Changes",
        "Top to bottom sets the Quick Access order.",
        "setMinimumWidth(320)",
        "Saved changes update only the tray Quick Access submenu.",
        "Saved - No pending Quick Access changes.",
        "Only active settings are shown.",
        "Core tray commands stay fixed",
        "Tray hover status:",
        "Provider-visible data: none",
        "Privacy Lockdown remains future-gated",
        "Choose the shortcuts shown in the tray Quick Access submenu.",
        "Tray menu and quick access.",
        "Tray shortcuts",
        "Nexus behavior and quick actions.",
        '("quick_access", "Resident Access")',
        '("ai_status", "AI Status")',
        '("privacy", "Privacy / Trust")',
        '("tray_visibility", "Tray Visibility")',
        '("owner_routes", "Owner Routes")',
    ):
        assert_true(
            token not in settings_dialog_text,
            f"Global Settings must not present stale fake settings category token: {token}",
            failures,
        )

    resident_settings_tooltip_tokens = (
        "Open the {label} settings section.",
        "Add one compact quick-access slot.",
        "Restore the default quick-access slots.",
        "Save Resident Access quick-slot settings.",
        "Close Global Settings.",
        "Select the route for quick-access slot",
        "Move quick-access slot",
        "Remove quick-access slot",
    )
    for token in resident_settings_tooltip_tokens:
        assert_true(
            token not in settings_dialog_text,
            f"FAM-003 resident settings tooltip text must stay suppressed until readable tooltip styling is admitted: {token}",
            failures,
        )

    assert_true(
        "button.setMinimumWidth(240)" in tray_text,
        "tray resident action buttons must keep a stable readable hitbox",
        failures,
    )
    assert_true(
        'else ""' in tray_text,
        "hidden unused quick slots must not keep visible placeholder labels",
        failures,
    )
    for token in (
        '"AI Control Center",',
        '"Open Command Overlay"',
        '"Close Command Overlay"',
        '"Create Custom Task"',
        '"Open Saved Actions Folder"',
        '"Saved Actions Folder"',
        '"Tray Visibility Help"',
    ):
        assert_true(
            token not in tray_text,
            f"tray menu must not expose stale or duplicate FAM-003 label token: {token}",
            failures,
        )

    for token in (
        "build_resident_access_menu_plan",
        "resident_access_status_snapshot",
        "RESIDENT_ACCESS_QUICK_ACTION_ABORTED",
        "NEXUS_FAM003_SETTINGS_LIVE_RESIZE_MANIFEST",
        "run_fam003_settings_live_resize_precheck",
        "FAM003_SETTINGS_LIVE_RESIZE_PRECHECK_MANIFEST_WRITTEN",
        "normal desktop shortcut launch plus Windows resize cursor hover proof plus SetCursorPos held Win32 left-button drag",
        "cursorBeforeDrag",
        "matchesResizeCursor",
    ):
        assert_true(token in main_text, f"runtime fallback resident access token missing: {token}", failures)

    assert_true(
        '" border-top: 1px solid rgba(118, 226, 255, 0.10);"' not in main_text,
        "Global Settings footer still has a top divider above Revert/Save",
        failures,
    )



def validate_no_forbidden_runtime_work(failures: list[str]):
    model_text = read("desktop/resident_access.py").casefold()
    forbidden = (
        "openai",
        "anthropic",
        "provider sdk",
        "memory index",
        "cache migration",
        "shortcut",
        "installer",
        "startup behavior",
    )
    for token in forbidden:
        assert_true(token not in model_text, f"resident_access.py contains out-of-scope token {token!r}", failures)


def main() -> int:
    previous_settings = os.environ.get("NEXUS_RESIDENT_ACCESS_SETTINGS_PATH")
    os.environ["NEXUS_RESIDENT_ACCESS_SETTINGS_PATH"] = str(
        ROOT / "dev" / "logs" / "fam003_resident_access_validation" / "settings.json"
    )
    failures: list[str] = []
    try:
        validate_resident_model(failures)
        validate_static_wiring(failures)
        validate_no_forbidden_runtime_work(failures)
    finally:
        if previous_settings is None:
            os.environ.pop("NEXUS_RESIDENT_ACCESS_SETTINGS_PATH", None)
        else:
            os.environ["NEXUS_RESIDENT_ACCESS_SETTINGS_PATH"] = previous_settings

    if failures:
        print("FAIL: FAM-003 resident access validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS: FAM-003 resident access / quick actions contract is wired and bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
