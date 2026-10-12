"""Validate the FAM-006 Monitoring HUD product surface baseline.

This helper is intentionally static. It proves the Dashboard-first HUD
Workstream handoff posture, current dashboard/control-panel markers,
provider-contract truth, no-data/degraded copy, warning posture, and
live/internal proof helper markers without inventing metric values or widening
into deferred product lanes.
Overlay/display markers remain supporting evidence unless source truth later
admits that interface as the active release surface.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _require_contains(text: str, needle: str, label: str, failures: list[str]) -> None:
    _require(needle in text, f"{label} is missing {needle!r}", failures)


def _require_css_block_properties(
    css: str,
    selector: str,
    properties: tuple[str, ...],
    label: str,
    failures: list[str],
) -> None:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>.*?)\}}", css, flags=re.DOTALL)
    if not match:
        failures.append(f"{label} is missing selector {selector!r}")
        return
    block = match.group("body")
    for prop in properties:
        _require(prop in block, f"{label} selector {selector!r} is missing {prop!r}", failures)


def _html_section(text: str) -> str:
    match = re.search(
        r'<section\s+id="monitoring-hud".*?</section>',
        text,
        flags=re.DOTALL,
    )
    return match.group(0) if match else ""


def _html_section_by_id(text: str, section_id: str) -> str:
    pattern = rf'<section\s+id="{re.escape(section_id)}".*?</section>'
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(0) if match else ""


def _require_no_collection_imports(text: str, label: str, failures: list[str]) -> None:
    for forbidden in ("psutil", "subprocess", "wmi", "pynvml", "win32", "powershell"):
        _require(
            forbidden not in text.casefold(),
            f"{label} must not perform {forbidden} collection in the WS7 product baseline",
            failures,
        )


def validate() -> list[str]:
    failures: list[str] = []

    core_html = _read("nexus_visual/orin_core.html")
    core_css = _read("nexus_visual/orin_core.css")
    core_desktop_html = _read("nexus_visual/orin_core_desktop.html")
    core_desktop_css = _read("nexus_visual/orin_core_desktop.css")
    core_js = _read("nexus_visual/orin_core.js")
    html = _read("nexus_visual/monitoring_hud.html")
    css = _read("nexus_visual/monitoring_hud.css")
    js = _read("nexus_visual/monitoring_hud.js")
    studio_html = _read("nexus_visual/monitoring_hud_studio.html")
    studio_js = _read("nexus_visual/monitoring_hud_studio.js")
    studio_primitives = _read("nexus_visual/nexus_window_primitives.css")
    studio_source = studio_html + "\n" + studio_js + "\n" + studio_primitives
    renderer = _read("desktop/desktop_renderer.py")
    family_vision = _read("Docs/family_visions/FAM-006_monitoring_and_hud.md")
    recording_feature_vision = _read("Docs/family_feature_visions/FAM-006_recording.md")
    output_contract = _read("desktop/recording_output_contract.py")
    core_renderer = _read("desktop/core_visualization_renderer.py")
    tray = (
        _read("desktop/orin_desktop_main.py")
        + "\n"
        + _read("desktop/tray_controller.py")
        + "\n"
        + _read("desktop/orin_desktop_launcher.pyw")
        + "\n"
        + _read("desktop/single_instance.py")
    )
    hud_state = _read("desktop/monitoring_hud_state.py")
    telemetry = _read("desktop/monitoring_hud_telemetry.py")
    placement = _read("desktop/monitoring_hud_placement.py")
    controls = _read("desktop/monitoring_hud_controls.py")
    status = _read("desktop/monitoring_hud_status.py")
    live_validation = _read("dev/orin_monitoring_hud_live_validation.ps1")
    human_client_validation = _read("dev/orin_monitoring_hud_human_client_validation.ps1")
    rounded_mask_probe = _read("dev/orin_dashboard_rounded_corner_mask_probe.py")

    for needle in (
        "--monitoring-hud-affordance-hover-shadow",
        "--monitoring-hud-affordance-active-shadow",
        "--monitoring-hud-affordance-focus-shadow",
        "--monitoring-hud-affordance-default-shadow",
        "--monitoring-hud-affordance-default-warning-shadow",
        "--monitoring-hud-affordance-default-danger-shadow",
        "--monitoring-hud-affordance-danger-shadow",
        "--monitoring-hud-affordance-safe-shadow",
        ".monitoring-hud__source-filter-option.is-hovered",
        ".monitoring-hud__bounded-dropdown-option.is-hovered",
        "box-sizing: border-box",
        ".monitoring-hud__bounded-dropdown-toggle:not(:disabled):not([aria-disabled=\"true\"]).is-hovered",
        ".monitoring-hud__hub-action:not(:disabled):not([aria-disabled=\"true\"]).is-hovered",
        ".monitoring-hud__sensor-option.is-hovered",
        ".monitoring-hud__sensor-option.is-pressed",
        ".monitoring-hud__monitor-manage-row:hover",
        "box-shadow: var(--monitoring-hud-affordance-hover-shadow)",
        "--monitoring-hud-scrollbar-size",
        "--monitoring-hud-divider-glow-size",
        "--monitoring-hud-divider-glow-size: 13px",
        "--monitoring-hud-button-neutral-bg",
        "--monitoring-hud-surface-solid",
        "background-size: 100% var(--monitoring-hud-divider-glow-size)",
        ".monitoring-hud__source-settings-body:focus-visible",
        ".monitoring-hud input[type=\"checkbox\"]:checked.is-hovered",
        ".monitoring-hud__overlay-profile-manager-row .monitoring-hud__overlay-profile-window-dropdown",
        "grid-template-columns: minmax(0, 1fr) minmax(0, 1fr)",
        "width: min(900px, calc(100% - 40px))",
        "grid-template-columns: minmax(0, 1fr)",
        "body.desktop-mode .monitoring-hud__child-window--overlay-profile",
        "scrollbar-gutter: auto",
        ".monitoring-hud__overlay-profile-choice-panel",
        "justify-self: stretch",
        "max-width: 100%",
        "@media (max-height: 620px)",
        "height: min(720px, calc(100% - 40px))",
        "max-height: 82px",
        "max-height: 102px",
        "@media (max-height: 560px)",
        "overflow: auto",
        "min-height: 54px",
        "max-height: 68px",
        "max-height: 88px",
    ):
        _require_contains(css, needle, "FAM-006 HUD-wide affordance CSS", failures)
    for needle in (
        "leftBuffer",
        "rightBuffer",
        "symmetricWindowBuffer",
        "choicePanelLeftInset",
        "choicePanelRightInset",
        "symmetricChoicePanelBuffer",
    ):
        _require_contains(js, needle, "FAM-006 Overlay Profile manager scaling proof", failures)
    for needle in (
        "window.runMonitoringHudVisualInspectionMatrixProof",
        "monitoringHudVisualInspectionStyleSnapshot",
        "buttonGlowUniformity",
        "defaultButtonGlowUniformity",
        "semanticHoverColorPreserved",
        "buttonTextDeadSpacePass",
        "perElementVisualInventory",
        "issueFormCoverageMatrix",
        "buttonRoleColorUniformity",
        "sourceRowHoverPersistence",
        "checkedControlHoverAffordance",
        "sourceSettingsFocusNoGold",
        "rowTitleTabsInspected",
        "responsiveWindowContract",
        "overlayManagerScaling",
        "windowSelectorSameRow",
        "windowSelectorStandardFootprint",
        "windowSelectorMenuUnclipped",
        "windowSelectorResponsiveCompact",
        "selector-stacked-oversized-or-clipped",
        "overlay-profile-minimum-functional-height",
        "oneFullMonitorVisible",
        "normal-no-scroll-emergency-compact-scroll",
        "dividerGlowReduced50Percent",
        "sameMonitorRowDirtyGuard",
        "defaultProfileDeletePersists",
        "defaultDeletePersistsWithoutAutoRecreate",
        "source-settings-shift-focus-frame",
        "dashboard-row-title-tabs",
        "dirtyGuardCoverage",
        "pageBreakVisualInspection",
        "backgroundBleedClippingInspection",
        "monitoringHudEffectivePollingRateMs",
        "pollingRateLiveCadence",
        "monitoringHudSourcePollingDropdownOpenSensorId",
        "monitoringHudOverlayProfileUnsavedGuard",
        'element.style.transition = "none"',
        'monitoringHudOpenChildWindow("monitor-group-edit");\n    monitoringHudRenderMonitorManagement();\n    inspectTarget("assigned-overlay-status"',
        "buttons-dropdowns-rows-chips-fields-page-breaks-backgrounds-bleed-clipping-scaling",
        "hudWideVisualInspectionMatrix",
    ):
        _require_contains(js, needle, "FAM-006 HUD-wide visual inspection proof JS", failures)
    for needle in (
        "hudWideVisualInspectionMatrix",
        "buttonGlowUniformity",
        "visualInspectionScopeCovered",
        "targetCount || 0) >= 40",
        "surfaceCount || 0) >= 3",
        "perElementVisualInventory",
        "issueFormCoverageMatrix",
    ):
        _require_contains(renderer, needle, "FAM-006 HUD-wide visual inspection renderer gate", failures)

    for label, text in (
        ("ORIN Core HTML", core_html),
        ("ORIN Core CSS", core_css),
        ("ORIN Core desktop HTML", core_desktop_html),
        ("ORIN Core desktop CSS", core_desktop_css),
        ("ORIN Core JavaScript", core_js),
    ):
        _require(
            "monitoring-hud" not in text and "Monitoring HUD" not in text,
            f"{label} must not contain Monitoring HUD surface markup, styles, or behavior",
            failures,
        )

    for needle in (
        '<div id="scene">',
        '<div id="core-wrap">',
        '<script src="orin_core.js"></script>',
    ):
        _require_contains(core_html, needle, "ORIN Core restored visual surface", failures)

    for needle in (
        '<body class="desktop-mode">',
        '<link rel="stylesheet" href="orin_core_desktop.css" />',
        '<script src="orin_core.js"></script>',
    ):
        _require_contains(core_desktop_html, needle, "ORIN Core desktop visual surface", failures)

    for needle in (
        "background: #000;",
        "radial-gradient(circle at center, #03070d",
        "rgba(0,0,0,0.58) 100%",
    ):
        _require_contains(core_css, needle, "ORIN Core restored visual CSS", failures)

    for needle in (
        "background: transparent !important;",
        "body.desktop-mode #scene",
        "pointer-events: none;",
    ):
        _require_contains(core_desktop_css, needle, "ORIN Core desktop transparent visual CSS", failures)

    hud_section = _html_section(html)
    minimal_hud_section = _html_section_by_id(html, "monitoring-hud-minimal")
    overlay_display_section = _html_section_by_id(html, "monitoring-hud-overlay-display")
    _require(bool(hud_section), "orin_core.html is missing the monitoring-hud section", failures)
    _require(bool(minimal_hud_section), "monitoring_hud.html is missing the monitoring-hud-minimal section", failures)
    _require(bool(overlay_display_section), "monitoring_hud.html is missing the monitoring-hud-overlay-display section", failures)
    for needle in (
        'data-package="PKG-006"',
        'data-slice="SLC-016"',
        'data-product-surface-role="dashboard-configuration-surface"',
        'data-configures-surface="monitoring-hud-minimal"',
        'data-native-dashboard-owner="DesktopRuntimeWindow"',
        'data-standalone-window-contract="dashboard-overlay-core-independent-native-surfaces"',
        'data-split-contract="dashboard-configures-minimal-overlay"',
        'data-slice="SLC-025"',
        'data-slice="SLC-026"',
        'data-slice="SLC-027"',
        'data-slice="SLC-028"',
        'data-hud-module="monitoring-hud-shell-module"',
        'data-product-surface="nexus-monitoring-hud"',
        'data-isolation-boundary="standalone-hud-layer"',
        'data-core-failure-isolation="hud-fail-does-not-hide-core"',
        'data-interaction-mode="standalone-dashboard-window"',
        'data-anchor-state="overlay-anchored"',
        'data-feature-enabled="false"',
        'data-overlay-deferred="true"',
        'data-visibility-state="hidden"',
        'data-snap-state="enabled"',
        'data-card-model="category-sensor-cards"',
        'data-provider-state="setup-required"',
        'data-warning-mode="visual-non-invasive"',
        'data-live-values="provider-required"',
        'data-polling-default-ms="1000"',
        'data-polling-options-ms="1000,2000,5000,10000"',
        'data-keybind-policy="none"',
        'data-drag-smoothing="native-os-window-move"',
        'data-scrollbar-style="nexus-thin-glow"',
        'data-resize-live-proof="invisible-real-ui-frame-pixel-signature-grow-shrink"',
        'data-resize-proof-visibility="normal-ui-no-proof-artifacts"',
        'data-resize-proof-visuals="none"',
        'data-frame-ownership="single-rounded-dashboard-chrome"',
        'data-scroll-owner="monitoring-hud-control-hub"',
        'data-scrollbar-boundary="inner-content-well-gutter"',
        'data-outer-frame-haze="removed-no-square-layer"',
        'data-grid-scope="control-hub-cards-only"',
        'data-deadzone-policy="auto-height-content-no-empty-hit-zones"',
        'data-sticky-header-mask="opaque-scroll-mask"',
        'data-native-resize-hit-zone="preclick-hover-cursor-aligned-14px-app-owned-resize-action"',
        'data-sandbox-state-matrix="setup,no-data,degraded,ready,warning"',
        'data-dashboard-control-panel="hud-overlay-monitor-management"',
        'data-monitor-management="sensor-command-center-list-detail-source-picker"',
        'data-monitor-management-scale="split-layout-search-filter-large-fixtures"',
        'data-monitor-management-layout="compact-list-right-detail-command-center"',
        'data-sensor-library-scale="search-facet-thousand-source-fixture"',
        'data-source-classification="settings-readiness-outside-assignable-sensors"',
        'data-monitor-management-scrollbars="nexus-styled-child-list-detail-sensor-panes"',
        'data-overlay-mode-controls="overlay-deferred-tray-owned"',
        'data-primary-interface-release-surface="monitoring-hud-dashboard-control-panel"',
        'data-interface-acceptance-policy="dashboard-only-current-branch"',
        'data-dashboard-acceptance-baseline="ws31-dashboard-control-panel"',
        'data-dashboard-proof-path="dashboard-specific-static-live"',
        'data-dashboard-standalone-proof="ws32-dashboard-window-travel"',
        'data-dashboard-clipping-proof="within-virtual-desktop"',
        'data-dashboard-minimum-edge-proof="native-min-size-bottom-edge-visible"',
        'data-dashboard-decoupling-proof="core-overlay-independent"',
        'data-dashboard-content-polish="branch2-monitor-groups-no-dead-space"',
        'data-dashboard-layout-proof="monitor-groups-measured-no-overlap"',
        'data-dashboard-home-model="control-hub-cards-monitor-management-child-windows"',
        'data-dashboard-child-window-scope="monitor-groups-manage-create-edit-delete-sensor-windows-overlay-profile-settings"',
        'data-dashboard-close-affordance="window-level-close-button"',
        'data-dashboard-close-layout="uiref-002-compact-top-right-symbol-control"',
        'data-dashboard-open-badge="removed"',
        'data-dashboard-settings-model="hud-overlay-monitor-groups-provider-warning"',
        'data-dashboard-ia-model="branch2-ia-controls-followthrough"',
        'data-dashboard-quick-access="warning-notifications-recording-start-stop"',
        'data-dashboard-global-feature-control="tray-owned"',
        'data-dashboard-deferred-action-policy="disabled-labeled-not-clickable"',
        'data-dashboard-card-order="hud-overlay-recording-monitor-groups-data-sources-readiness"',
        'data-dashboard-settings-affordance="dashboard-ia-card-settings-button"',
        'data-dashboard-settings-panel="settings-panel-child-window"',
        'data-dashboard-settings-panel-state="closed"',
        'data-dashboard-settings-proof="visible-open-close-control-hit-target"',
        'data-monitor-group-model="configurable-groups-sensor-assignment"',
        'data-dashboard-monitor-card-policy="overlay-display-owns-visual-rendering"',
        'data-dashboard-provider-truth="provider-contract-first"',
        'data-dashboard-state-model="setup-no-data-degraded-warning"',
        'data-dashboard-warning-controls="visual-non-invasive-only"',
        'data-dashboard-fake-telemetry-policy="blocked"',
        'data-overlay-acceptance-policy="deferred-non-gating"',
        'data-interface-bundle-approval="not-granted"',
        'data-core-repair-classification="dependency-repair-only"',
        'data-overlay-profile-state="slc-039-membership-mapping"',
        'data-overlay-profile-schema-version="1"',
        'data-active-overlay-profile-id="default-overlay-profile"',
        'data-overlay-profile-editor="slc-039-membership-editor"',
        'data-overlay-profile-membership="editable-slc-039-mapping"',
        'data-overlay-profile-integration="slc-040-readonly-manage-context"',
        'data-overlay-profile-mutation="assign-unassign-status-window"',
        'data-overlay-profile-context-layout="single-row-readonly"',
        'data-overlay-profile-route="assigned-overlay-status-window"',
        'id="monitoring-hud-monitor-overlay-profile-context"',
        'id="monitoring-hud-overlay-profile-editor"',
        'data-overlay-profile-editor-ui="slc-039-membership-editor"',
        'data-overlay-profile-proof="selector-settings-window-create-rename-membership-save-discard"',
        'id="monitoring-hud-overlay-profile-selector"',
        'data-bounded-dropdown="overlay-profile"',
        'id="monitoring-hud-overlay-profile-toggle"',
        'id="monitoring-hud-overlay-profile-menu"',
        'data-overlay-profile-option="default-overlay-profile"',
        'id="monitoring-hud-overlay-profile-open-settings"',
        'class="monitoring-hud__hub-action monitoring-hud__hub-action--compact monitoring-hud__dashboard-paired-action"',
        'data-dashboard-action-size="paired-overlay-manage-250"',
        'data-overlay-profile-actions="settings-window-entry"',
        'id="monitoring-hud-overlay-profile-window"',
        'data-child-window="overlay-profile-settings"',
        'data-overlay-profile-window="select-profile-to-edit-create-right-save-required"',
        'data-overlay-profile-workflow="select-loads-edit-create-draft-save-required"',
        'data-overlay-profile-volume-policy="max-five-visible-monitors-inner-scroll"',
        'data-overlay-profile-selector-policy="max-five-visible-profile-options-ndai-scrollbar"',
        'data-overlay-profile-outer-scroll-policy="normal-no-scroll-emergency-compact-scroll"',
        'id="monitoring-hud-overlay-profile-window-selector"',
        'data-visible-option-target="max-five"',
        'id="monitoring-hud-overlay-profile-name-input"',
        'id="monitoring-hud-overlay-profile-monitor-search"',
        'id="monitoring-hud-overlay-profile-monitor-filter"',
        'data-bounded-dropdown="overlay-profile-monitor-filter"',
        'id="monitoring-hud-overlay-profile-monitor-results"',
        'id="monitoring-hud-overlay-profile-membership-list"',
        'data-overlay-profile-membership-list="editable-monitor-membership"',
        'data-overlay-profile-visible-monitor-target="max-five"',
        'data-scrollbar-style="ndai-native"',
        'id="monitoring-hud-overlay-profile-create"',
        'id="monitoring-hud-overlay-profile-save"',
        'id="monitoring-hud-overlay-profile-discard"',
        'id="monitoring-hud-overlay-profile-delete"',
        'data-overlay-profile-actions="save-left-discard-delete-right"',
        'data-child-window="monitor-overlay-assignment"',
        'data-overlay-assignment-window="monitor-group-overlay-status-assignment"',
        'data-child-window="sensor-source-settings"',
        'data-source-settings-window="source-list-sensor-settings"',
        "Profile to Edit:",
        'data-recording-profile-state="recording-profile-state-absent-future-gated"',
        'aria-label="Nexus Desktop AI Monitoring HUD product surface"',
        'aria-label="HUD Dashboard control hub cards"',
        'aria-hidden="true"',
        "Nexus Desktop AI",
        "Monitoring HUD",
        "HUD Dashboard",
        'data-native-resize-model="os-edge-corner-resize"',
        "Configure HUD access, monitor groups, data sources, warning notifications, and future display behavior.",
        "Dashboard",
        "Settings and control hub",
        "HUD Overlay",
        "Deferred future overlay",
        "Dashboard configures overlay behavior",
        'class="monitoring-hud__surface-role-actions"',
        'aria-label="HUD Dashboard IA card controls"',
        "HUD Overlay deferred",
        'id="monitoring-hud-settings-action"',
        'data-control="open-dashboard-settings"',
        'aria-haspopup="dialog"',
        "Settings",
        'id="monitoring-hud-dashboard-close-action"',
        "monitoring-hud__chrome-button--close",
        'data-control="close-dashboard"',
        'data-window-control-cluster="UIREF-002-compact-window-control-cluster"',
        "Close HUD Dashboard",
        "        X",
        "Quick Access",
        'id="monitoring-hud-warning-toggle"',
        'id="monitoring-hud-edit-monitor-action"',
        'data-control-visual-parity="overlay-profile-settings"',
        "Warning Notifications",
        "Monitor Groups",
        "Data Sources",
        'id="monitoring-hud-monitor-list"',
        'data-dashboard-monitor-display-policy="settings-only-no-monitor-cards"',
        'data-dashboard-content="control-hub-cards"',
        'data-child-window-model="hub-actions-standalone-child-windows"',
        'data-dashboard-monitor-model="configurable-groups-sensor-assignment"',
        'data-dashboard-hub-card="hud-overlay"',
        'data-dashboard-hub-card="monitor-groups"',
        'data-dashboard-hub-card="data-sources"',
        'data-dashboard-hub-card="readiness"',
        'data-monitor-group-flow="sensor-command-center-list-detail-source-picker"',
        'id="monitoring-hud-child-window-layer"',
        'data-child-window="dashboard-settings"',
        'data-child-window="monitor-group-create"',
        'data-child-window="monitor-group-edit"',
        'id="monitoring-hud-settings-window"',
        'id="monitoring-hud-settings-warning-toggle"',
        "Settings Panel",
        "Tray owns HUD feature enablement; Dashboard close hides this window only",
        "Monitor group and Dashboard layout posture are stored locally",
        "Overlay Display Deferred",
        "Provider Setup Required",
        "Provider/model, external telemetry parity, and Overlay/display acceptance remain future USER decisions.",
        'id="monitoring-hud-edit-monitor-list"',
        'id="monitoring-hud-monitor-search"',
        'id="monitoring-hud-monitor-list-empty"',
        "2 Monitor Groups configured. Manage opens list, create, edit, delete, and supported sensor assignment controls.",
        "Create Monitor",
        "Manage Monitors",
        'id="monitoring-hud-manage-monitor-create-action"',
        'id="monitoring-hud-monitor-empty-create-action"',
        'data-monitor-empty-state-action="primary-create"',
        'id="monitoring-hud-monitor-delete-confirmation"',
        'id="monitoring-hud-monitor-sensor-assignment"',
        'id="monitoring-hud-monitor-sensor-settings"',
        'id="monitoring-hud-sensor-search"',
        'id="monitoring-hud-sensor-filter"',
        'data-source-filter-mode="nexus-dropdown-source-picker"',
        'id="monitoring-hud-sensor-filter-toggle"',
        'id="monitoring-hud-sensor-filter-label"',
        'class="monitoring-hud__source-filter-menu',
        'id="monitoring-hud-sensor-result-summary"',
        'id="monitoring-hud-sensor-preview"',
        'data-monitor-management-layout="compact-command-center-list-detail"',
        'data-sensor-library="search-filter-scalable"',
        'data-scroll-pane="monitor-list"',
        'data-scroll-pane="monitor-detail"',
        'data-scroll-pane="sensor-result-list"',
        'data-scroll-pane="sensor-preview"',
        'data-scroll-pane="sensor-settings"',
        'id="monitoring-hud-monitor-detail-delete"',
        "Delete Monitor",
        'data-unsaved-guard-actions="modal-save-discard-cancel"',
        'data-delete-confirmation-actions="delete-left-cancel-right"',
        'id="monitoring-hud-monitor-unsaved-guard"',
        'id="monitoring-hud-monitor-detail-empty"',
        "Create a monitor to assign sources and settings.",
        'data-control-row="polling-rate-inline"',
        'data-polling-rate-hitbox="toggle-only"',
        'data-bounded-control="polling-rate"',
        'id="monitoring-hud-monitor-polling-rate-control"',
        'data-bounded-dropdown="polling-rate"',
        'id="monitoring-hud-monitor-polling-rate-toggle"',
        'class="monitoring-hud__bounded-dropdown-menu',
        'data-polling-rate-option="5000"',
        "Polling Rate",
        'data-source-controls-layout="search-filter-inline"',
        'data-monitor-select="cpu"',
        'data-monitor-setting="warning-notifications"',
        'data-readiness-panel="provider-readiness-status"',
        'data-monitor-sensor-option="cpu-load"',
        'data-sensor-assignment="sensor-library-source-picker"',
        'role="listbox"',
        "Source filter options",
        "Provider Readiness",
        "Display mode",
        "CPU Group",
        "GPU Group",
        "Monitor Groups assign supported sources and settings. HUD Overlay owns future visual display; fake values remain blocked.",
        "Waiting for safe provider",
        "Feature Deferred",
        "Manage Data Sources",
        'data-feature-status="feature-deferred"',
        "Provider-first; no fake values",
        "HUD Overlay release acceptance is deferred.",
        "Deferred / non-gating",
        "Overlay settings are future branch scope",
        "Provider setup required",
        "Show unavailable; no fake values",
        "Name reconnect/setup gap",
    ):
        _require_contains(hud_section, needle, "monitoring HUD HTML", failures)

    _require(
        html.count('data-window-control-class="child-window-compact-symbol-close"') >= 6,
        "FAM-006 child-window header close controls must use the compact symbol window-control marker",
        failures,
    )
    for child_close_visual in (
        ".monitoring-hud__child-window-close::before",
        ".monitoring-hud__child-window-close::after",
        "color: transparent;",
        "font-size: 0;",
        "text-indent: -999px;",
        ".monitoring-hud__child-window-close:hover",
        ".monitoring-hud__child-window-close:focus-visible",
        ".monitoring-hud__child-window-close:active",
    ):
        _require_contains(
            css,
            child_close_visual,
            "FAM-006 child-window compact symbol close visual primitive CSS",
            failures,
        )

    for interactive_control_markup in (
        'id="monitoring-hud-monitor-detail-note"',
        'id="monitoring-hud-monitor-detail-actions"',
        'data-monitor-detail-actions="selected-monitor-footer"',
        'data-detail-action-row="save-left-discard-delete-right"',
        'id="monitoring-hud-edit-monitor-discard"',
        'data-control="discard-edit-monitor"',
        'data-control-state="clean-disabled"',
        ".monitoring-hud__child-note[hidden]",
        ".monitoring-hud__detail-action-row",
        ".monitoring-hud__child-actions--guard",
        "justify-self: stretch;",
        ".monitoring-hud__hub-action--safe-cancel",
    ):
        _require_contains(html + css, interactive_control_markup, "FAM-006 interactive-control visual QA HTML/CSS", failures)
    for dirty_guard_parity_markup in (
        'id="monitoring-hud-overlay-profile-unsaved-guard" data-unsaved-guard="closed"',
        'id="monitoring-hud-monitor-unsaved-guard" data-unsaved-guard="closed"',
        'id="monitoring-hud-overlay-profile-unsaved-save"',
        'id="monitoring-hud-monitor-unsaved-save"',
        'id="monitoring-hud-overlay-profile-unsaved-discard"',
        'id="monitoring-hud-monitor-unsaved-discard"',
        'id="monitoring-hud-overlay-profile-unsaved-cancel"',
        'id="monitoring-hud-monitor-unsaved-cancel"',
        '.monitoring-hud__child-window[data-hud-unsaved-state="open"] > .monitoring-hud__unsaved-guard--modal[data-unsaved-guard="open-save-discard"]',
        'grid-template-columns: repeat(3, minmax(96px, 1fr));',
        '[data-control="overlay-profile-unsaved-save"]',
        '[data-control="unsaved-save-monitor"]',
        '[data-control="overlay-profile-unsaved-discard"]',
        '[data-control="unsaved-discard-monitor"]',
        '[data-control="overlay-profile-unsaved-cancel"]',
        '[data-control="unsaved-cancel-monitor"]',
        'data-unsaved-guard-actions="modal-save-discard-cancel"',
    ):
        _require_contains(
            html + css,
            dirty_guard_parity_markup,
            "FAM-006 shared modal dirty-guard parity HTML/CSS",
            failures,
        )
    for dirty_guard_live_proof in (
        "Manage Monitors dirty guard matches shared modal Save Discard Cancel contract",
        "Manage Monitors dirty guard Cancel returns to dirty draft without queued close",
        "Manage Monitors dirty guard Discard completes queued close and clears dirty state",
        "manage_monitors_dirty_guard_save_discard_cancel_modal",
        "manage_monitors_dirty_guard_modal_uniform_with_overlay_profile",
        "manage_monitors_dirty_guard_background_blur_blocking",
        "manage_monitors_dirty_guard_close_button_functionality",
        "focused screenshots missing mandatory dirty-guard parity element",
    ):
        _require_contains(
            renderer + live_validation,
            dirty_guard_live_proof,
            "FAM-006 LV1 shared modal dirty-guard parity proof route",
            failures,
        )
    _require(
        'id="monitoring-hud-create-monitor-action"' not in hud_section
        and 'data-control="create-monitor"' not in hud_section,
        "HUD dashboard Monitor Groups card must remove the main Create Monitor action; creation stays inside Manage Monitors and empty state",
        failures,
    )
    _require(
        "Delete Selected Monitor" not in html,
        "HUD detail-pane delete action must say Delete Monitor, not Delete Selected Monitor",
        failures,
    )

    for forbidden_home_copy in (
        "Default polling",
        "Warning posture",
        "Monitor group to edit",
        "Monitor group editor",
        "Selected Monitor Group",
        "Dashboard proof",
        "Full desktop now; UTS only in Live Validation Stage 1",
        'id="monitoring-hud-monitor-selector"',
        "monitoring-hud__selector-control",
        'data-dashboard-content="dashboard-proof-next-actions"',
        'data-dashboard-content="monitor-group-management"',
    ):
        _require(
            forbidden_home_copy not in hud_section,
            f"monitoring HUD home surface must not include stale proof/inline-editor copy: {forbidden_home_copy}",
            failures,
        )

    for forbidden_dashboard_card in (
        'data-category-card="',
        'data-monitor-card="',
        'data-card-handle="',
        'data-card-resize="',
        "monitoring-hud-card",
        "monitoring-hud__monitor-row-actions",
        'data-monitor-delete="',
        'data-monitor-edit-select="',
        '<select id="monitoring-hud-sensor-filter"',
        'data-monitor-sensor-option="provider-state"',
    ):
        _require(
            forbidden_dashboard_card not in hud_section,
            "dashboard HTML must not render stale monitor-card or compact-modal actions/source-picker controls",
            failures,
        )

    _require(
        'body.desktop-mode #monitoring-hud[data-live-resize-active="true"] .monitoring-hud__chrome::after'
        not in css,
        "HUD CSS must not show resize proof artifacts in normal user-facing validation",
        failures,
    )
    _require(
        ".monitoring-hud__child-field--inline" in css
        and ".monitoring-hud__sensor-library-toolbar--inline" in css,
        "HUD CSS must keep bounded Sensor Command Center controls compact and inline where practical",
        failures,
    )
    _require(
        ".monitoring-hud__source-filter-dropdown" in css
        and ".monitoring-hud__source-filter-menu" in css
        and ".monitoring-hud__source-filter-option.is-hovered" in css,
        "HUD CSS must render Source Filter as a Nexus-styled dropdown with explicit hover reset styling",
        failures,
    )
    _require(
        ".monitoring-hud__bounded-dropdown" in css
        and ".monitoring-hud__bounded-dropdown-menu" in css
        and ".monitoring-hud__bounded-dropdown-option.is-hovered" in css
        and "data-polling-rate-option" in html
        and "monitoringHudSetPollingRateDropdownOpen" in js
        and "monitoringHudSetPollingRateValue" in js,
        "HUD must render Polling Rate as a Nexus-styled bounded dropdown with hover/open/select behavior",
        failures,
    )
    _require(
        ".monitoring-hud__overlay-profile-panel" in css
        and ".monitoring-hud__overlay-profile-dropdown" in css
        and ".monitoring-hud__bounded-dropdown.monitoring-hud__overlay-profile-dropdown" in css
        and "grid-template-columns: max-content minmax(300px, 1fr)" in css
        and "width: max-content" in css
        and "min-width: min(300px, 100%)" in css
        and "max-width: min(450px, 100%)" in css
        and ".monitoring-hud__overlay-profile-dropdown .monitoring-hud__bounded-dropdown-menu" in css
        and "<span>Active Overlay Profile</span>" in html
        and 'id="monitoring-hud-overlay-profile-active-name"' not in html
        and ".monitoring-hud__overlay-profile-actions" in css
        and ".monitoring-hud__overlay-profile-window-actions" in css
        and ".monitoring-hud__overlay-profile-membership-tools" in css
        and ".monitoring-hud__monitor-overlay-profile-context--compact" in css
        and "data-overlay-profile-option" in html
        and "data-child-window=\"overlay-profile-settings\"" in html
        and 'data-overlay-profile-window="select-profile-to-edit-create-right-save-required"' in html
        and 'data-overlay-profile-visual-repair="manager-selector-same-row-compact-unclipped-proof"' in html
        and 'data-overlay-profile-manager-row="selector-dropdown-create-right-equal"' in html
        and 'data-overlay-profile-visible-monitor-target="max-five"' in html
        and 'data-scrollbar-style="ndai-native"' in html
        and 'data-overlay-profile-route="assigned-overlay-status-window"' in html
        and 'data-overlay-profile-mutation="assign-unassign-status-window"' in html
        and 'data-control="assigned-overlay-status"' in html
        and 'data-monitor-detail-card="sensor-source"' in html
        and 'data-sensor-source-summary-placement="attached-to-sensor-source-card"' in html
        and 'data-monitor-detail-placement="below-sensor-source"' in html
        and html.find('data-monitor-detail-card="sensor-source"') < html.find('data-monitor-detail-placement="below-sensor-source"')
        and 'data-bounded-dropdown="overlay-profile-monitor-filter"' in html
        and 'id="monitoring-hud-overlay-profile-window-select-label"' not in html
        and 'id="monitoring-hud-overlay-profile-delete"' in html
        and 'data-child-window="monitor-overlay-assignment"' in html
        and 'data-source-settings-window="source-list-sensor-settings"' in html
        and "Enabled for Overlay" not in html
        and 'data-control="manage-overlay-profile-settings"' not in html
        and "monitoringHudSetOverlayProfileDropdownOpen" in js
        and "monitoringHudSetOverlayProfileWindowDropdownOpen" in js
        and "monitoringHudSetOverlayProfileMonitorFilterValue" in js
        and "monitoringHudToggleOverlayAssignment" in js
        and "monitoringHudOpenSourceSettings" in js
        and "windowSelectorReadable" in js
        and "windowSelectorSameRow" in js
        and "windowSelectorStandardFootprint" in js
        and "windowSelectorMenuUnclipped" in js
        and "windowSelectorResponsiveCompact" in js
        and "manageContextRowAffordanceVisible" in js
        and "manageContextBelowSensorSource" in js
        and "sensorSourceSummaryPlacement" in js
        and "largeProfileFixture" in js
        and "profileDropdownMaxFiveStress" in js
        and "profileDropdownNDAIScrollbar" in js
        and "dropdownNullStress" in js
        and "dropdownHighVolumeStress" in js
        and "dropdownStressSurfaceCount" in js
        and "deleteConfirmationVisualReviewable" in js
        and "detailActionsVisualReviewable" in js
        and "visualStressProfileCount" in renderer
        and "dropdownNullStress" in renderer
        and "dropdownHighVolumeStress" in renderer
        and "visualVisibleProfileOptions" in renderer
        and "deleteConfirmationVisualReviewable" in renderer
        and "detailActionsVisualReviewable" in renderer
        and "__monitoringHudOverlayProfileDropdownVisualProofState" in renderer
        and "selected source" in js
        and "monitoringHudOpenChildWindow(\"overlay-profile-settings\")" in js
        and "monitoringHudSaveOverlayProfileDraft" in js,
        "HUD must render follow-up returned-UTS Overlay Profile manager controls, NDAI filter dropdown, profile delete, clickable assignment surface, Enabled-for-Overlay removal, and source-list sensor settings entry points",
        failures,
    )
    _require(
        "grid-template-columns: minmax(0, 1fr) minmax(0, 1fr)" in css
        and "width: min(900px, calc(100% - 40px))" in css
        and "min-width: min(720px, calc(100% - 40px))" in css
        and "max-height: min(720px, calc(100% - 40px))" in css
        and "grid-template-columns: minmax(0, 1fr)" in css
        and "body.desktop-mode .monitoring-hud__child-window--overlay-profile" in css
        and "scrollbar-gutter: auto" in css
        and "justify-self: stretch" in css
        and "max-width: 100%" in css
        and "@media (max-height: 620px)" in css
        and "height: min(720px, calc(100% - 40px))" in css
        and "max-height: 82px" in css
        and "max-height: 102px" in css
        and "@media (max-height: 560px)" in css
        and "overflow: auto" in css
        and "min-height: 54px" in css
        and "max-height: 68px" in css
        and "max-height: 88px" in css
        and "max-width: none;" in css
        and ".monitoring-hud__overlay-profile-window-actions-right" in css
        and "monitoringHudOverlayProfilePendingCreate" in js
        and "monitorIds: []" in js
        and "select-loads-edit-create-draft-save-required" in js
        and "padding-right: 14px;" in css
        and ".monitoring-hud__overlay-profile-manager-row .monitoring-hud__overlay-profile-window-dropdown" in css
        and ".monitoring-hud__overlay-profile-manager-row .monitoring-hud__bounded-dropdown-toggle" in css
        and "height: 38px;" in css
        and "min-width: min(420px, calc(100% - 28px))" in css
        and "@media (max-width: 360px)" in css
        and "max-height: 132px;" in css
        and "min-height: 26px;" in css
        and "box-sizing: border-box;" in css
        and "min-height: 152px;" in css
        and 'data-overlay-profile-detail-state="open"' in css
        and "max-height: 132px;" in css
        and "min-height: 148px;" in css
        and css.rfind(".monitoring-hud__child-window--overlay-profile") > css.rfind(".monitoring-hud__child-window {")
        and "grid-template-columns: minmax(236px, auto) minmax(0, 1fr) minmax(78px, auto)" in css
        and ".monitoring-hud__unsaved-guard {\n  grid-template-columns: minmax(0, 1fr);" in css
        and ".monitoring-hud__monitor-overlay-profile-context.is-hovered" in css,
        "HUD CSS must keep the Overlay Profile manager selector compact/same-row/unclipped and make Assigned Overlay read as an actionable status row",
        failures,
    )
    _require(
        "Polling floor" not in html
        and "Polling Floor" not in html
        and 'data-bounded-control="polling-floor"' not in html,
        "HUD user-facing copy must rename Polling Floor to Polling Rate and remove polling-floor control markers",
        failures,
    )
    for interactive_runtime in (
        "normal-hover-active-focus-visible-disabled-open-selected",
        "first-click-stress-proof-required",
        "z-index-pointer-events-disabled-aria-dom-focus-timing",
        "monitoringHudWireReliableControl",
        "monitoringHudWireReliableDelegatedControl",
        "monitoringHudControlInterceptionSnapshot",
        "runMonitoringHudInteractiveControlStressProof",
        "interactiveControlFirstClickStress",
        "interactiveControlNoInterception",
        "runMonitoringHudSourcePickerCheckmarkStressProof",
        "sourcePickerCheckmarkStress",
        "sourcePickerCheckmarkMode",
        "sourcePickerCheckmarkLatency",
        "runMonitoringHudDisplayModeChipStressProof",
        "displayModeChipStress",
        "displayModeActivationPath",
        "displayModeSelectionLatency",
        "monitoringHudManageCloseHitboxProof",
        "manageCloseHitboxFullHeight",
        "manageCloseHitboxProof",
        "manage-close-hitbox-partial-interception",
        "_monitoring_hud_active_child_window_rect_contains",
        "editMonitorClose",
        "row-and-checkbox-immediate",
        "row-and-checkbox-immediate-deferred-settings",
        "immediate-visual-deferred-settings",
        "immediate-row-preview-deferred-settings",
        "sourcePickerRenderScope",
        "monitoringHudPollingRateHitboxProof",
        "pollingRateHitboxProof",
        "pollingRateHitboxToggleOnly",
        "polling-rate-hitbox-too-wide",
        "source-picker:checkmark",
        "detailActionRowAligned",
        "pollingRateDropdownNexusStyled",
        "04_polling_rate_dropdown_open_hover_reset",
        "pollingRateVisualSourceFilterClosed",
        "pollingRateVisualOpen",
        "pollingRateVisualMenuVisible",
        "pollingRateVisualHoverReset",
        "footerSaveDisabledWhenClean",
        "footerDiscardDisabledWhenClean",
        "footerSaveEnabledWhenDirty",
        "footerDiscardEnabledWhenDirty",
        "footerDiscardIlluminated",
        "unsavedGuardModalFocused",
        "unsavedGuardReveal",
        "runMonitoringHudMonitorGroupNameReuseProof",
        "delete-create-reuses-lowest-available-monitor-group-number",
        "monitoringHudNextMonitorGroupNumber",
        "Create after delete reuses Monitor Group 3 instead of skipping to a higher number",
        "manage_monitors_create_after_delete_reuses_monitor_group_number",
        "sourceFilterVisualOpen",
        "sourceFilterVisualHoverReset",
        "live self-QA step failure(s)",
    ):
        _require_contains(
            html + css + js + renderer,
            interactive_runtime,
            "FAM-006 interactive-control reliability runtime/proof",
            failures,
        )
    _require(
        ".monitoring-hud__source-filter-chips" not in html,
        "HUD HTML must not expose Source Filter as bulky always-visible chips",
        failures,
    )
    for guard_proof in (
        "monitoringHudPendingGuardAction",
        "pendingMonitorAction",
        "monitoringHudUpdateMonitorDraftFromWindow",
        "monitoringHudPersistCurrentMonitorDraft",
        "draft-preserved-before-queued-action",
        "unsavedSavePersistedDraft",
        "unsavedDiscardDroppedDraft",
        "unsavedGuardCancelRemoved",
        "unsavedDiscardRightAligned",
        "unsavedCreateQueuedAction",
        "unsavedDeleteQueuedAction",
        "unsavedCloseQueuedAction",
        "unsavedCloseDirtyBeforeClose",
        "unsavedCloseDraftBeforeClose",
        "unsavedCloseTargetedManageClose",
        "unsavedGuardModalFocused",
        "unsavedCloseSavePersistedDraft",
        "unsavedCloseSaveClosedWindow",
        "unsavedCloseDiscardDroppedDraft",
        "unsavedCloseDiscardClosedWindow",
        "deleteConfirmationCancelIlluminated",
    ):
        _require_contains(js + renderer, guard_proof, "HUD unsaved draft guard proof", failures)
    _require(
        '[data-resize-proof-visuals="test-visible"] .monitoring-hud__chrome::after' in css,
        "HUD CSS must gate visible resize proof artifacts behind an explicit test-visible marker",
        failures,
    )
    for repair_proof in (
        "sourceFilterDropdown",
        "sourceFilterHoverReset",
        "source_filter_dropdown",
        "source_filter_hover_reset",
        "firstOpenFlickerGuard",
        "dashboard_geometry_and_webview_frames_settled_before_opacity",
        "monitorManagementToolbar",
        "monitorDeletePlacement",
        "manageWindowSizing",
        "monitorListStressProof",
    ):
        _require_contains(js + renderer + css + html, repair_proof, "FAM-006 returned blocker repair proof", failures)


    for close_guard_runtime in (
        'document.querySelector(\'[data-child-window-close="monitor-group-edit"]\')',
        "webview_focused_visual_proof",
        "visualProofQualityGate",
        "monitorListRowsCompact",
        "monitorListCssPreventsStretch",
        "monitorListSmallSetHasSlack",
        "emptyStateNoSaveCancel",
        "emptyStateCreatePrimary",
        "emptyStateActionsBounded",
        "emptyStateProductCopy",
        "interactiveControlVisualQaGate",
        "hidden-no-monitor",
        "03_manage_monitors_open_state",
        "04_source_filter_dropdown_open_hover_reset",
        "05_unsaved_guard_close_queued",
        "unsavedGuardModalFocused",
        "06_unsaved_guard_modal_save_discard_cancel",
        "07_unsaved_close_save_closes_after_persist",
        "08_unsaved_close_discard_closes_after_drop",
        "09_delete_confirmation_bottom",
        "monitoring-hud-monitor-delete-confirmation",
        "deleteConfirmationVisualTargeted",
        "deleteConfirmationState",
        'scrollIntoView({ block: "center", inline: "nearest" })',
        "10_final_empty_state_create_recovery",
        "11_100_monitor_list_scrollbar_and_1200_source_picker",
    ):
        _require_contains(
            renderer,
            close_guard_runtime,
            "FAM-006 refreshed LV1 close-guard runtime proof",
            failures,
        )

    retired_product_name = "".join(chr(code) for code in (74, 97, 114, 118, 105, 115)).casefold()
    for forbidden in ("voice", "audio", "spoken", "microphone", retired_product_name):
        _require(
            forbidden not in hud_section.casefold(),
            f"monitoring HUD HTML must not introduce {forbidden} behavior in WS7",
            failures,
        )
    for needle in (
        'id="monitoring-hud-overlay-profile-editor"',
        'data-overlay-profile-editor-ui="slc-039-membership-editor"',
        'data-overlay-profile-membership="editable-slc-039-mapping"',
    ):
        _require_contains(html, needle, "SLC-039 Overlay Profile visible membership editor UI", failures)

    for needle in (
        "ACTIVE_OVERLAY_RECORDING_TARGET_KIND",
        "build_active_overlay_recording_target_snapshot",
        "active-overlay-recording-target",
        "target-session-truth-only",
        "active-overlay-profile-membership",
        "snapshot-at-recording-start",
        "hiddenRecordingTargetState",
        "recordingExecutionState",
        "fileWritingState",
        "separateRecordingProfileState",
        "recording-profile-state-absent-future-gated",
    ):
        _require_contains(hud_state, needle, "SLC-051 active Overlay recording target state foundation", failures)

    for needle in (
        "monitoringHudBuildActiveOverlayRecordingTargetSnapshot",
        "monitoringHudApplyActiveOverlayRecordingTargetProof",
        "runMonitoringHudActiveOverlayRecordingTargetProof",
        "slc-051-active-overlay-profile-membership-target",
        "activeOverlayRecordingTargetProof",
        "activeOverlayRecordingTargetSource",
        "activeOverlayRecordingTargetScope",
        "activeOverlayRecordingTargetMonitorCount",
        "snapshotAtStartModel",
        "recordingFileWritingState",
    ):
        _require_contains(js, needle, "SLC-051 active Overlay recording target JS proof", failures)

    for needle in (
        'id="monitoring-hud-recording-target-preview"',
        'data-dashboard-hub-card="recording"',
        'data-recording-card-placement="dashboard-recording-card-primary"',
        'data-recording-surface-owner="dashboard-card-not-hud-overlay"',
        'data-recording-target-preview="slc-052-dashboard-recording-card-target-status"',
        'data-active-monitor-transparency="slc-052-dashboard-visible-count-and-names"',
        'data-hud-overlay-recording-boundary="hud-overlay-overlay-focused"',
        'id="monitoring-hud-recording-control-launcher"',
        'id="monitoring-hud-recording-open-folder"',
        'data-recording-control-window-state="quick-access-start-stop"',
        'data-recording-control-window-state="recording-card-status-summary"',
        'id="monitoring-hud-recording-studio-open"',
        'data-recording-folder-action="native-and-export-folder-shell"',
        'data-recording-folder-path-available="pre-session-root"',
        'data-native-window-contract="dashboard-quick-access-start-stop"',
        'data-native-window-contract="recording-studio-focused-control-status"',
        'data-log-viewer-state="ready"',
        'data-recording-execution-state="ready"',
        'data-recording-file-writing-state="ready"',
        '<span>Target overlay profile</span>',
        'id="monitoring-hud-recording-target-count">2 active monitors</strong>',
    ):
        _require_contains(html, needle, "SLC-052 Dashboard Recording card target/status HTML", failures)

    for needle in (
        "monitoringHudRenderActiveOverlayRecordingTargetPreview",
        "monitoringHudToggleRecording",
        "monitoringHudRequestRecordingControlWindow",
        "monitoringHudRequestLogViewerWindow",
        "monitoringHudRequestOpenRecordingFolder",
        "setMonitoringHudRecordingFolderOpenResult",
        "runMonitoringHudRecordingTargetPreviewProof",
        "recordingTargetPreviewProof",
        "monitoringHudSyncActiveOverlayRecordingTargetFromOverlayProfile",
        "recordingTargetOverlayProfileMirrorProof",
        "activeProfileCreateMirrorsRecordingTarget",
        "savedActiveProfileSelectorSwitchesRecordingTarget",
        "slc-052-dashboard-recording-card-target-status",
        "slc-052-dashboard-visible-count-and-names",
        "dashboard-recording-card-primary",
        "dashboard-status-summary",
        "quick-access-start-stop",
        "hud-overlay-overlay-focused",
        "Start Recording",
        "Recording Suite",
        "Log Viewer",
        "recording-studio-focused-control-status",
        "native-and-export-folder-shell",
        "create-or-open-before-session",
        "trayRecordingControlState",
    ):
        _require_contains(js, needle, "SLC-052 Dashboard Recording card target/status JS proof", failures)

    for needle in (
        "class MonitoringHudRecordingStudioWindow",
        'self.setWindowTitle("Nexus Recording Suite")',
        "MONITORING_HUD_RECORDING_STUDIO_READY",
        'slice="SLC-053"',
        '"surface": "recording_studio_window"',
        '"taskbarRestorable": True',
        '"recordingExecutionState": "enabled"',
        '"recordingFileWritingState": "enabled"',
        '"startEnabled": self._start_stop_state == "start-enabled"',
        "recording_action_handler",
        "_dispatch_monitoring_hud_recording_studio_action",
    ):
        _require_contains(renderer, needle, "SLC-053 native Recording Suite window", failures)

    for needle in (
        "class MonitoringHudLogViewerStudioWindow",
        'self.setWindowTitle("Nexus Log Viewer")',
        "MONITORING_HUD_LOG_VIEWER_STUDIO_READY",
        'slice="SLC-054"',
        '"surface": "log_viewer_shell"',
        '"nativeFolderPreSessionUsable": True',
        '"exportFolderPreSessionUsable": True',
        '"previousLogSelectionState": "future-gated"',
        '"exportCustomizationState": "future-gated"',
        "recording_output_dir",
        "recording_export_dir",
    ):
        _require_contains(renderer, needle, "SLC-054 minimal Log Viewer shell", failures)

    for needle in (
        "RECORDING_OUTPUT_CONTRACT_ID",
        "slc-054-active-overlay-recording-output-contract",
        "RECORDING_OUTPUT_FORMAT",
        "ndai-native-recording-log",
        "RECORDING_OUTPUT_EXTENSION",
        ".ndailog",
        "RECORDING_VALIDATION_EXPORT_ENV",
        "normalProductSaveCreatesExport",
        "manual-validation-or-future-user-export-only",
        "nativeLogReadableOnlyByNDAI",
        "write_recording_csv_export",
        "RECORDING_OUTPUT_HEADERS",
        "timestamp_utc",
        "elapsed_ms",
        "overlay_profile_id",
        "monitor_id",
        "sensor_id",
        "value",
        "quality",
        "render_recording_output_csv",
        "parse_recording_output_csv",
        "validate_recording_output_contract",
        '"fileWritingState": "enabled"',
        '"recordingExecutionState": "enabled"',
        '"nativeLogLoaderState": "future-separate-viewer"',
    ):
        _require_contains(output_contract, needle, "SLC-054 durable recording output contract", failures)


    for needle in (
        "monitoring-hud__recording-target-preview",
        "monitoring-hud__recording-target-actions",
        "--recording-card-live-visual-proof: dashboard-card-system-sampled",
        "--recording-card-row-visual-contract: inherits-dashboard-state-row",
    ):
        _require_contains(css, needle, "SLC-052 Dashboard Recording card target/status CSS", failures)

    for needle in (
        'data-recording-card-visual-system="dashboard-hub-card-sampled"',
        'data-recording-card-sampled-elements="hud-overlay-monitor-groups-data-sources-readiness"',
    ):
        _require_contains(html, needle, "SLC-052 Dashboard Recording card visual-system inheritance markers", failures)

    for needle in (
        'recordingCardVisualSystem = "dashboard-hub-card-sampled"',
        'recordingCardSampledElements = "hud-overlay-monitor-groups-data-sources-readiness"',
    ):
        _require_contains(js, needle, "SLC-052 Dashboard Recording card active visual-system mirror", failures)

    for forbidden in (
        "--recording-card-live-visual-proof: focused-target-preview-required",
        "--recording-card-row-visual-contract: contained-row-no-sliced-divider",
        ".monitoring-hud__hub-card--recording {\n  border-color:",
        ".monitoring-hud__hub-card--recording .monitoring-hud__hub-card-topline span",
    ):
        _require(
            forbidden not in css,
            "SLC-052 Recording card must sample the Dashboard card visual system instead of carrying custom Recording-only chrome",
            failures,
        )

    for needle in (
        "New Dashboard, HUD, Overlay Profile, Monitor Group, Recording, Sensor Command Center, or child-window UI must sample from the existing FAM-006 visual system",
        "Visual-system inheritance means shared design DNA, not component cloning",
        "The Dashboard Recording card must look and behave like an existing Dashboard hub card",
    ):
        _require_contains(family_vision, needle, "FAM-006 family visual-system inheritance contract", failures)

    for needle in (
        "recordingCard: rectFor('[data-dashboard-hub-card=\"recording\"]')",
        'recordingTargetPreview: rectFor("#monitoring-hud-recording-target-preview")',
        'recordingControlLauncher: rectFor("#monitoring-hud-recording-control-launcher")',
        'recordingOpenFolder: rectFor("#monitoring-hud-recording-open-folder")',
    ):
        _require_contains(js, needle, "SLC-052 Dashboard Recording card live geometry proof", failures)

    for needle in (
        "dashboard-card-system-sampled",
        "inherits-dashboard-state-row",
        "02_recording_card_target_preview_standard_state_rows",
        "02_recording_card_log_viewer_studio_pre_session_ready_state",
        "02_recording_studio_native_window_ready_state",
        "02_log_viewer_studio_native_window_shell_state",
        "02_recording_card_log_viewer_studio_opened_state",
        "stateRowsContained",
        "hidden-from-default-body-supporting-tooltip-only",
        "supporting-tooltip-only",
        "titleHeaderBadgeState",
        "ai-control-center-title-group-no-extra-badge",
        "top-right-header",
        "fam006-unique-child-studio-shell-v5",
        "unique-child-standalone-feature-studio",
        "no-resize-recording-edge-resize-log-viewer",
        "attachedChildCornerResizeGripAbsent",
        "denseValidatorStatusPanelRejected",
        "nexus-window-primitives-v1-rendered-dom-css",
        "Bounded FAM-006 Shared Primitive Carry-In",
        "nexus_visual/nexus_window_primitives.css",
        "ai-control-center-symbol-window-control-cluster",
        "ai-control-center-symbol-window-control-pill",
        "sharedPrimitiveConsumer",
        "featureStudioPrimitive",
        "QWebEngineView/monitoring_hud.css DOM",
        "nativeLogRowsContained",
    ):
        _require_contains(renderer + "\n" + live_validation, needle, "SLC-052 live validation visual-system inheritance proof", failures)


    for needle in (
        "nexus_window_primitives.css",
        'data-shared-primitive-consumer="nexus-window-primitives-v1"',
        'data-feature-studio-primitive="fam006-unique-child-studio-shell-v5"',
        'data-window-taxonomy="unique-child-standalone-feature-studio"',
        'data-window-resize-taxonomy="no-resize-recording-edge-resize-log-viewer"',
        'data-attached-child-resize-grip="absent"',
        'data-window-control-primitive="nexus-uiref-002-compact-cluster-v1"',
        ".monitoring-hud__feature-studio-panel[hidden]",
        "display: none !important",
        'data-feature-studio-body-primitive="unique-child-purpose-stack-v6"',
        'data-log-shell-primitive="action-first-folder-access-shell-v6"',
        "monitoring-hud__detached-child-studio-header",
        "nexusMonitoringHudStudioApplyState",
        "data-product-surface=\"fam006-feature-studio\"",
        "data-feature-studio-purpose=\"ultra-lightweight-detached-recording-controller\"",
        "monitoring-hud-studio-open-log-viewer-action",
        "monitoring-hud-studio-start-action",
        "monitoring-hud-studio-pause-action",
        "monitoring-hud-studio-stop-action",
        "monitoring-hud-hub-action-content-fit-equal-gutter-v4",
        "height: 31px",
        "padding-inline: 14px",
        "font-weight: 720",
        "--monitoring-hud-studio-row-value-gutter: 8px",
        "--monitoring-hud-studio-row-label-column: max-content",
        "--monitoring-hud-studio-row-stack-vertical-gutter: 6px",
        "--monitoring-hud-studio-row-dropdown-edge-gutter: 1px",
        "grid-template-columns: var(--monitoring-hud-studio-row-label-column, max-content) minmax(0, 1fr)",
        "column-gap: var(--monitoring-hud-studio-row-value-gutter)",
        "gap: var(--monitoring-hud-studio-row-stack-vertical-gutter)",
        'data-row-stack-vertical-gutter="6"',
        'data-row-dropdown-edge-gutter="1"',
        'data-dropdown-layer-contract="overlay-owned-control-not-peer-row"',
        ".monitoring-hud__studio-truth-row [data-bounded-dropdown]",
        "margin-block: var(--monitoring-hud-studio-row-dropdown-edge-gutter)",
        "padding: 4px 0 2px",
        "syncStudioTruthRowValueColumns",
        "syncTruthRowValueColumn",
        "valueColumnAlignment",
        "enforced-single-row",
        "right: 14px",
        'data-element-group="recording-actions"',
        'data-action-layout="transport-pill-left-route-right"',
        'data-control-group="recording-transport-pill"',
        'data-action-layout="segmented-transport-pill-left"',
        "monitoring-hud__transport-pill",
        "monitoring-hud__transport-segment--first",
        "monitoring-hud__transport-segment--middle",
        "monitoring-hud__transport-segment--last",
        'data-element-group="recording-target-truth"',
        'data-element-group="log-folder-actions"',
        'data-action-layout="folder-actions-right-aligned"',
        'class="monitoring-hud__state-row monitoring-hud__studio-truth-row"',
        "monitoring-hud-studio-viewer-state",
        "detached-child-window-header-no-title-card",
        "titleCardState",
        "title-first-description-beneath-no-title-card",
        "background: transparent",
        "overflow: visible",
        "text-overflow: clip",
        'data-control="log-viewer-open-export"',
        'data-button-layout="content-fit"',
        "START",
        "PAUSE",
        "STOP",
        "OPEN LOG VIEWER",
        'data-resize-contract="not-resizable-position-memory-only"',
        'data-fixed-controller-height="154"',
        'data-row-primitive="ai-control-center-state-row"',
        "edge-resizable-log-access-shell",
        "edge-resize-native-top-level",
        "OPEN NATIVE LOGS",
        "OPEN EXPORTED LOGS",
        "VIEWER",
        "Deferred",
        "hub-action-content-fit-equal-gutter-32px-pill",
    ):
        _require_contains(studio_source, needle, "FAM-006 rendered Studio visual primitive source", failures)

    for forbidden in (
        "monitoring-hud-studio-recording-toggle-action",
        'data-control="recording-studio-toggle"',
        "runtime-current-single-toggle-candidate-selection-pending",
        "grid-template-columns: repeat(3, minmax(0, 1fr))",
        "monitoring-hud-hub-action-content-fit-v1",
        "monitoring-hud-hub-action-content-fit-equal-gutter-v2",
        'data-row-primitive="ai-control-center-fact-row"',
        'class="monitoring-hud__controller-target"',
        'class="monitoring-hud__controller-status"',
        'class="monitoring-hud__log-access-item"',
        "<span>Target Overlay Profile</span>",
        "<span>Recording State</span>",
        "<span>Native Log</span>",
        'data-element-group="recording-target-log-truth"',
        'id="monitoring-hud-studio-recording-log-state"',
        'id="monitoring-hud-studio-recording-log-detail"',
        "Available now</small>",
        "Empty until exported</small>",
        "--nexus-feature-studio-title-bg",
        'data-fixed-controller-height="238"',
        'data-fixed-controller-height="184"',
        'data-fixed-controller-height="210"',
        "HEIGHT = 238",
        'data-fixed-controller-height="176"',
        "HEIGHT = 176",
        'data-fixed-controller-height="292"',
        "HEIGHT = 292",
        "HEIGHT = 352",
        "HEIGHT = 330",
        "HEIGHT = 164",
        "MINIMUM_HEIGHT = 164",
        "log_viewer_studio_feature_studio_v4",
        "WIDTH = 480",
        "WIDTH = 560",
        "hub-action-content-fit-equal-gutter-38px-pill",
        "hub-action-content-fit-equal-gutter-34px-pill",
        "fam006-detached-child-studio-shell-v3",
        "child-window-row-stack",
        "monitoring-hud__resize-corner",
        "qsizegrip-bottom-right-enabled",
        "feature-studio-summary",
        "Folder Action",
        ):
        _require(
            forbidden not in studio_html + "\n" + studio_js,
            f"FAM-006 Recording Suite returned-UTS repair must reject stale UI primitive/content: {forbidden}",
            failures,
        )

    studio_selector_root = (
        'body.desktop-mode #monitoring-hud[data-feature-studio-primitive="fam006-unique-child-studio-shell-v5"]'
    )
    _require_css_block_properties(
        studio_primitives,
        f"{studio_selector_root} .monitoring-hud__title",
        ("font-size: 17px", "font-weight: 720", "letter-spacing: 0.04em"),
        "FAM-006 Studio title must use the accepted compact child-window title scale",
        failures,
    )
    _require_css_block_properties(
        studio_primitives,
        f"{studio_selector_root} .monitoring-hud__kicker",
        ("font-size: 11px", "font-weight: 720", "letter-spacing: 0.08em"),
        "FAM-006 Studio descriptor must use the accepted compact child-window descriptor scale",
        failures,
    )
    _require_css_block_properties(
        studio_primitives,
        f"{studio_selector_root} .monitoring-hud__controller-meta-strip",
        (
            "--monitoring-hud-studio-row-stack-vertical-gutter: 6px",
            "--monitoring-hud-studio-row-dropdown-edge-gutter: 1px",
            "gap: var(--monitoring-hud-studio-row-stack-vertical-gutter)",
            "padding: 0",
        ),
        "FAM-006 Recording Suite row stack must use AI Control Center row rhythm",
        failures,
    )
    _require_css_block_properties(
        studio_primitives,
        f"{studio_selector_root} .monitoring-hud__log-target-strip",
        (
            "--monitoring-hud-studio-row-stack-vertical-gutter: 6px",
            "--monitoring-hud-studio-row-dropdown-edge-gutter: 1px",
            "gap: var(--monitoring-hud-studio-row-stack-vertical-gutter)",
            "padding: 0",
        ),
        "FAM-006 Log Viewer row stack must use AI Control Center row rhythm",
        failures,
    )
    _require_css_block_properties(
        studio_primitives,
        f"{studio_selector_root} .monitoring-hud__studio-truth-row span",
        ("width: max-content", "font-size: 11px", "font-weight: 720"),
        "FAM-006 Studio row label must match current AI Dashboard row label grammar",
        failures,
    )
    _require_css_block_properties(
        studio_primitives,
        f"{studio_selector_root} .monitoring-hud__studio-truth-row strong",
        ("font-size: 11px", "font-weight: 720"),
        "FAM-006 Studio row status/value column must match the accepted row weight",
        failures,
    )

    for needle in (
        "monitoringHudStudioNativeDragHandle",
        "DRAG_HEADER_HEIGHT = 64",
        "HEIGHT = 154",
        "MINIMUM_HEIGHT = 154",
        "recording_studio_feature_studio_v5",
        "HEIGHT = 134",
        "MINIMUM_HEIGHT = 134",
        "log_viewer_studio_feature_studio_v6",
        "WM_NCHITTEST+manual-fallback-geometry-resize",
        "hub-action-content-fit-equal-gutter-32px-pill",
    ):
        _require_contains(renderer, needle, "FAM-006 native Studio geometry and drag contract", failures)

    for forbidden in (
        '_monitoring_hud_studio_badge("REC"',
        '_monitoring_hud_studio_badge("LOG"',
        'header.addWidget(_monitoring_hud_studio_badge',
        "log_viewer_studio_feature_studio_v5",
    ):
        _require(
            forbidden not in renderer,
            "FAM-006 Studio title/header grammar must not use REC/LOG title badges",
            failures,
        )

    for needle in (
        "profile-specific log consistency",
        "normal user activation",
        "ultra-lightweight detached Recording controller",
        "compact folder-access shell",
        "standalone window layout that is not a Dashboard card clone",
        "Recording Suite",
        "visual-system inheritance",
        "native and exported log folder access",
    ):
        _require_contains(
            recording_feature_vision,
            needle,
            "FAM-006 Recording returned-UTS determinism proof expectations",
            failures,
        )

    for needle in (
        'status = "PASS"',
    ):
        _require_contains(
            live_validation,
            needle,
            "FAM-006 returned-UTS deterministic Live Validation stop-loss",
            failures,
        )


    for needle in (
        "profileLogConsistencyPassed",
        "twoProfileLogConsistencyPassed",
        "rowProfileIds",
        "rowMonitorIds",
        "targetMonitorIds",
        "flat-user-recording-and-export-roots",
        "nativeRootFolderName",
        "exportRootFolderName",
        "surfaceChildFolderState",
        "surfaceChildFolderAbsent",
        "internalPathLeakageAbsent",
    ):
        _require_contains(
            output_contract,
            needle,
            "FAM-006 returned-UTS product repair recording-output proof",
            failures,
        )

    _require(
        'RECORDING_OUTPUT_FAMILY_DIR_NAME = "FAM-006"' not in output_contract,
        "FAM-006 returned-UTS product repair must not expose the FAM label as the default user-visible log folder",
        failures,
    )
    _require(
        'RECORDING_OUTPUT_SURFACE_DIR_NAME = "Monitoring HUD"' not in output_contract,
        "FAM-006 recording output must not create a Monitoring HUD child folder under Recordings or Exported Logs",
        failures,
    )

    for needle in (
        "always-openable-target-state-visible",
        "recording-studio-open-target-required",
        "recordingStudioUserPath",
        "recording-target-no-sensor-sample",
        "no-sensor-sample",
    ):
        _require_contains(
            js,
            needle,
            "FAM-006 returned-UTS product repair Recording Suite visible-button proof",
            failures,
        )

    for needle in (
        "nativeCursorRecordingStudioReopenProof",
        "MONITORING_HUD_STUDIO_VISUAL_INHERITANCE",
        "nexus-window-primitives-v1-rendered-dom-css",
        "fam006-unique-child-studio-shell-v5",
        "ai-control-center-uiref-001-002-003-primitives",
        "Bounded FAM-006 Shared Primitive Carry-In",
        '"primaryVisualComparator": "FAM-006 unique child feature-studio grammar"',
        '"compositionModel": "action-first-ultra-lightweight-detached-recording-controller"',
        '"compositionModel": "compact-current-branch-log-access-shell"',
        '"windowTaxonomy": "unique-child-standalone-feature-studio"',
        '"attachedChildResizeGrip": False',
        '"denseValidatorStatusPanelRejected": True',
        '"attachedChildCornerResizeGripAbsent": True',
        '"futureScopeVisualLeakageAbsent": True',
        '"edgeResizeProofRequired": True',
        '"visualPrimitiveAdoptionContract": _monitoring_hud_ai_control_center_primitive_contract()',
        '"acceptedReferenceSet": list(MONITORING_HUD_STUDIO_REFERENCE_SURFACES)',
        '"headerPrimitiveSeed": "AI-Control-Center-UIREF-001-title-group"',
        '"panelPrimitiveSeed": "FAM-006 action-first controller plus AI Control Center / HUD Dashboard state-row underglow"',
        '"panelPrimitiveSeed": "FAM-006 compact folder-action shell with AI Control Center / HUD Dashboard state-row underglow"',
        '"visualContractDeclared": MONITORING_HUD_STUDIO_VISUAL_CONTRACT',
        '"visualAdjudicationState": MONITORING_HUD_STUDIO_VISUAL_ADJUDICATION',
        '"visualProofAuthority": MONITORING_HUD_STUDIO_VISUAL_PROOF_AUTHORITY',
        '"visualRuntimeSelfAttestation": "rejected"',
        '"visualMatrixRequired": True',
        '"standaloneWindowLayout": "ultra-lightweight-detached-recording-controller"',
        '"standaloneWindowLayout": "compact-current-branch-log-access-shell"',
        '"dashboardLifecycleDependency": "independent-while-runtime-active"',
        '"logViewerRoute": "recording-studio-open-log-viewer-action"',
        '"sharedPrimitiveSourcePath": "nexus_visual/nexus_window_primitives.css"',
        '"sharedPrimitiveConsumer": "nexus-window-primitives-v1"',
        '"featureStudioPrimitive": MONITORING_HUD_STUDIO_VISUAL_CONTRACT',
        '"sharedVisualDna": "nexus-window-primitives-v1-rendered-dom-css"',
        '"genericShellRejected": "nexus-window-primitives-v1-rendered-dom-css"',
        '"titleHeaderBadgeState": "removed"',
        '"standaloneHeaderTreatment": "ai-control-center-title-group-no-extra-badge"',
        '"minimizeControlLocation": "top-right-header"',
        '"closeControlLocation": "top-right-header"',
        '"buttonVisualGrammar": "monitoring-hud-rendered-content-fit-equal-gutter-v4-button-primitive"',
        '"windowBodyVisualGrammar": MONITORING_HUD_STUDIO_BODY_VISUAL_GRAMMAR',
        "AI-Control-Center-UIREF-002-window-control-cluster",
        "AI-Control-Center-UIREF-003-action-button",
        "AI-Control-Center-UIREF-001-title-group",
        '"windowControlContainerVisualPolicy": "ai-control-center-symbol-window-control-cluster"',
        '"actionButtonGeometryPolicy": "monitoring-hud-hub-action-content-fit-equal-gutter-v4"',
        '"stateRowDensityPolicy": "action-first-controller-with-ai-control-center-state-rows-no-report-panels"',
        '"stateRowDensityPolicy": "doorway-shell-viewer-deferred-row-plus-bottom-folder-actions-no-technical-path-table"',
        '"titleGroupVisualPolicy": "detached-child-window-header-no-title-card"',
        "ai-control-center-symbol-window-control-pill",
        "hub-action-content-fit-equal-gutter-32px-pill",
        '"recordingStudioVisibleActionModel": "selected-REC-A-explicit-start-pause-stop-plus-open-log-viewer"',
        '"recordingStartControlProof": _monitoring_hud_studio_dom_control_proof("recording-start")',
        '"recordingPauseControlProof": _monitoring_hud_studio_dom_control_proof("recording-pause")',
        '"recordingStopControlProof": _monitoring_hud_studio_dom_control_proof("recording-stop")',
        '"logViewerRouteControlProof": _monitoring_hud_studio_dom_control_proof("open-log-viewer")',
        '"resizeBehavior": self.RESIZE_BEHAVIOR',
        'RESIZE_BEHAVIOR = "not-resizable-position-memory-only"',
        'RESIZE_BEHAVIOR = "edge-resize-native-top-level"',
        '"nativeLogRowsContained": bool',
        '"windowPlacementMemoryState": "enabled"',
        '"userVisibleStorageModel": "flat-user-recording-and-export-roots"',
        '"pathRowsVisualState": "hidden-from-default-body-supporting-tooltip-only"',
        '"nativeLogPathDisplayMode": "supporting-tooltip-only"',
        '"viewerDeferredRow": "VIEWER - Deferred"',
        '"visibleAnatomy": "doorway-shell-with-viewer-deferred-row-and-bottom-native-export-actions"',
        '"internalPathLeakageAbsent": not any(term in combined_roots for term in leakage_terms)',
        "Native NDAI logs",
    ):
        _require_contains(
            renderer,
            needle,
            "FAM-006 returned-UTS product repair Studio/Log Viewer runtime proof",
            failures,
        )

    for needle in (
        'data-package="PKG-006"',
        'data-slice="SLC-016"',
        'data-placement-slice="SLC-026"',
        'data-status-slice="SLC-028"',
        'data-proof-slice="SLC-029"',
        'data-product-surface="nexus-monitoring-hud-minimal"',
        'data-product-surface-role="minimal-anchored-hud-overlay"',
        'data-renderer-owner="MonitoringHudWindow"',
        'data-configured-by="monitoring-hud"',
        'data-dashboard-owner="monitoring-hud"',
        'data-split-contract="dashboard-configures-minimal-overlay"',
        'data-native-overlay-owner="MonitoringHudOverlayDisplayWindow"',
        'data-native-window-split-proof="ready-ws26"',
        'data-click-through-proof="native-transparent-input"',
        'data-focus-proof="native-no-focus-noactivate"',
        'data-interface-acceptance-policy="deferred-non-gating"',
        'data-dashboard-acceptance-role="supporting-future-interface-evidence"',
        'data-current-branch-release-gate="false"',
        'aria-label="Nexus Desktop AI minimal anchored Monitoring HUD overlay"',
        "Minimal HUD enabled",
        "Provider setup required",
        "Provider warming",
        "Provider required",
        "Visual warning baseline only",
    ):
        _require_contains(minimal_hud_section, needle, "minimal monitoring HUD HTML", failures)
    for forbidden in ("voice", "audio", "spoken", "microphone", retired_product_name):
        _require(
            forbidden not in minimal_hud_section.casefold(),
            f"minimal monitoring HUD HTML must not introduce {forbidden} behavior in WS19",
            failures,
        )

    for needle in (
        'id="monitoring-hud-overlay-display"',
        'data-product-surface="nexus-monitoring-hud-overlay-display"',
        'data-product-surface-role="edgeless-overlay-display"',
        'data-overlay-canvas="edge-to-edge-snipping-tool-style"',
        'data-overlay-edit-mode="unanchored-focusable-resizable-scrollable"',
        'data-overlay-anchor-mode="anchored-uninteractable-click-through"',
        'data-monitor-layout="movable-resizable-monitor-cards"',
        'data-watermark-identity="edge-safe-nexus-orin-watermark"',
        'data-edge-to-edge-posture="landscape-portrait-monitor-fit"',
        'data-interface-acceptance-policy="deferred-non-gating"',
        'data-dashboard-acceptance-role="supporting-future-interface-evidence"',
        'data-current-branch-release-gate="false"',
        'id="monitoring-hud-overlay-canvas"',
        'data-overlay-monitor-card="cpu"',
        'data-overlay-monitor-card="gpu"',
        "Nexus Desktop AI / ORIN",
    ):
        _require_contains(overlay_display_section, needle, "edgeless overlay display HTML", failures)
    for forbidden in ("voice", "audio", "spoken", "microphone", retired_product_name):
        _require(
            forbidden not in overlay_display_section.casefold(),
            f"edgeless overlay display HTML must not introduce {forbidden} behavior in WS25",
            failures,
        )

    fake_metric_pattern = re.compile(
        r"\b\d+(?:\.\d+)?\s?(?:\u00b0|c\b|%|rpm\b|mhz\b|ghz\b|w\b)",
        flags=re.IGNORECASE,
    )
    _require(
        fake_metric_pattern.search(hud_section) is None,
        "monitoring HUD HTML must not present numeric hardware values before provider proof exists",
        failures,
    )

    for needle in (
        "#monitoring-hud {",
        "#monitoring-hud-minimal {",
        "#monitoring-hud-overlay-display {",
        "display: none;",
        "body.desktop-mode #monitoring-hud",
        "body.desktop-mode #monitoring-hud-minimal",
        "body.desktop-mode #monitoring-hud-overlay-display",
        'body.desktop-mode #monitoring-hud-overlay-display[data-anchor-state="unanchored"]',
        "inset: 0;",
        "width: 100vw;",
        "overflow: hidden;",
        "clip-path: inset(0 round 28px);",
        "scrollbar-width: thin;",
        "scrollbar-color: rgba(108, 232, 255, 0.58) transparent;",
        "--monitoring-hud-scrollbar-size: 8px;",
        "width: var(--monitoring-hud-scrollbar-size);",
        "margin: 10px 0 14px;",
        "border: 1px solid rgba(4, 17, 32, 0.72);",
        "background-clip: padding-box;",
        "contain: paint;",
        "body.desktop-mode .monitoring-hud__control-hub::-webkit-scrollbar",
        "body.desktop-mode .monitoring-hud__control-hub::-webkit-scrollbar-thumb",
        "body.desktop-mode .monitoring-hud__control-hub::-webkit-scrollbar-corner",
        "body.desktop-mode .monitoring-hud__nexus-scroll-pane::-webkit-scrollbar",
        "body.desktop-mode .monitoring-hud__child-window::-webkit-scrollbar",
        'body.desktop-mode #monitoring-hud[data-live-resize-active="true"][data-resize-proof-visuals="test-visible"] .monitoring-hud__chrome',
        'body.desktop-mode #monitoring-hud[data-drag-smoothing="native-os-window-move"]',
        'font-family: "Bahnschrift", "Rajdhani", "Segoe UI", sans-serif;',
        "pointer-events: auto",
        'body.desktop-mode #monitoring-hud[data-anchor-state="unanchored"]',
        ".monitoring-hud__chrome",
        ".monitoring-hud__toolbar",
        "z-index: 24;",
        "--monitoring-hud-affordance-default-warning-shadow",
        ".monitoring-hud__surface-role",
        ".monitoring-hud__config-heading",
        ".monitoring-hud__anchor-rail",
        ".monitoring-hud__control-hub",
        "grid-template-columns: minmax(0, 1fr);",
        "grid-auto-flow: row;",
        "grid-auto-rows: max-content;",
        ".monitoring-hud__hub-card",
        ".monitoring-hud__chrome-button--settings",
        ".monitoring-hud__surface-role-actions",
        ".monitoring-hud__child-window--settings",
        ".monitoring-hud__child-window--monitor-management",
        ".monitoring-hud__monitor-management-shell",
        ".monitoring-hud__monitor-list-pane",
        ".monitoring-hud__monitor-detail-pane",
        ".monitoring-hud__sensor-library",
        ".monitoring-hud__sensor-library-toolbar",
        ".monitoring-hud__sensor-preview",
        ".monitoring-hud__settings-grid",
        ".monitoring-hud__setting-row",
        ".monitoring-hud__setting-toggle",
        "box-sizing: border-box;",
        "align-content: start;",
        "justify-content: flex-start;",
        ".monitoring-hud__hub-card-topline",
        ".monitoring-hud__hub-action",
        ".monitoring-hud__state-row",
        "#monitoring-hud-monitor-list-summary",
        ".monitoring-hud-minimal__frame",
        ".monitoring-hud-minimal__topline",
        ".monitoring-hud-minimal__cards",
        ".monitoring-hud-minimal-card",
        ".monitoring-hud-minimal__warning",
        ".monitoring-hud-overlay-display__frame",
        ".monitoring-hud-overlay-display__canvas",
        ".monitoring-hud-overlay-display__watermark",
        ".monitoring-hud-overlay-card",
        ".monitoring-hud-overlay-card__quick-actions",
        ".monitoring-hud-overlay-card__topline",
        ".monitoring-hud__title-group",
        "position: sticky;",
        "scrollbar-gutter: stable;",
        "scrollbar-gutter: auto;",
        "--dashboard-card-holder-inset-proof: scrollbar-exempt-equal-card-insets;",
        ".monitoring-hud__hub-card:has(.monitoring-hud__bounded-dropdown[data-dropdown-open=\"true\"])",
        ".monitoring-hud--validation-fault",
        "@media (max-width: 760px), (max-height: 620px)",
        "@keyframes monitoringHudSettle",
    ):
        _require_contains(css, needle, "monitoring HUD CSS", failures)
    minimum_size_media = re.search(
        r"@media\s*\(max-width:\s*760px\),\s*\(max-height:\s*620px\)\s*\{\s*body\.desktop-mode\s+#monitoring-hud\s*\{(?P<body>.*?)\}",
        css,
        flags=re.DOTALL,
    )
    minimum_size_rule = minimum_size_media.group("body") if minimum_size_media else ""
    for needle in (
        "top: 0;",
        "right: 0;",
        "bottom: 0;",
        "left: 0;",
        "height: 100vh;",
        "min-height: 0;",
        "max-height: 100vh;",
    ):
        _require_contains(
            minimum_size_rule,
            needle,
            "monitoring HUD minimum-size native edge CSS",
            failures,
        )
    monitor_manage_list_css = re.search(
        r"\.monitoring-hud__monitor-manage-list\s*\{(?P<body>.*?)\}",
        css,
        flags=re.DOTALL,
    )
    monitor_manage_list_rule = monitor_manage_list_css.group("body") if monitor_manage_list_css else ""
    for needle in (
        "align-content: start;",
        "grid-auto-rows: max-content;",
    ):
        _require_contains(
            monitor_manage_list_rule,
            needle,
            "monitoring HUD compact monitor list CSS",
            failures,
        )
    _require(
        ".monitoring-hud__selector-control" not in css,
        "monitoring HUD CSS must not keep legacy Dashboard monitor selector styling",
        failures,
    )

    for needle in (
        'const monitoringHud = document.getElementById("monitoring-hud")',
        'const monitoringHudMinimal = document.getElementById("monitoring-hud-minimal")',
        'const monitoringHudOverlayDisplay = document.getElementById("monitoring-hud-overlay-display")',
        'const monitoringHudOverlayCanvas = document.getElementById("monitoring-hud-overlay-canvas")',
        'const monitoringHudProviderState = document.getElementById("monitoring-hud-provider-state")',
        'const monitoringHudMinimalProviderState = document.getElementById("monitoring-hud-minimal-provider-state")',
        'const monitoringHudWarningPosture = document.getElementById("monitoring-hud-warning-posture")',
        'const monitoringHudTrayPath = document.getElementById("monitoring-hud-tray-path")',
        'const monitoringHudEditMonitor = document.getElementById("monitoring-hud-edit-monitor-action")',
        'const monitoringHudSettingsAction = document.getElementById("monitoring-hud-settings-action")',
        'const monitoringHudSettingsWindow = document.getElementById("monitoring-hud-settings-window")',
        'const monitoringHudSettingsWarningToggle = document.getElementById("monitoring-hud-settings-warning-toggle")',
        'const monitoringHudWarningToggle = document.getElementById("monitoring-hud-warning-toggle")',
        'const monitoringHudMonitorList = document.getElementById("monitoring-hud-monitor-list")',
        'const monitoringHudDashboardClose = document.getElementById("monitoring-hud-dashboard-close-action")',
        'const monitoringHudChildWindowLayer = document.getElementById("monitoring-hud-child-window-layer")',
        'const monitoringHudEditMonitorList = document.getElementById("monitoring-hud-edit-monitor-list")',
        "warningNotificationsMuted",
        "window.getMonitoringHudControlState = function()",
        "window.runMonitoringHudOverlayDisplayAcceptanceProof = function()",
        "window.runMonitoringHudActiveOverlayProfileDisplayProof = function()",
        "window.runMonitoringHudDashboardOverlayIndependenceProof = function()",
        "slc-042-active-profile-state-bridge",
        "slc-043-active-profile-display",
        "slc-044-dashboard-overlay-independent",
        "activeProfileSelectionDrivesRenderedCards",
        "activeProfileSwitchUpdatesVisibleDisplay",
        "staleActiveProfileFallsBackDeterministically",
        "nullProfileStateShowsNoActiveProfile",
        "highVolumeDisplayRendersDeterministically",
        "dashboardAndOverlayRolesDistinct",
        "dashboardConfiguresOverlayWithoutOwningDisplay",
        "visualAcceptanceBaselineReady",
        "staleOverlayCardsRemoved",
        "nullProfileStateRendersZeroCards",
        "highVolumeMembershipRendersDeterministically",
        "overlayDisplayAcceptanceProof",
        "activeOverlayProfileDisplayProof",
        "dashboardOverlayIndependenceProof",
        "window.getMonitoringHudLiveClientGeometry = function()",
        "minimalHud: rectFor(\"#monitoring-hud-minimal\")",
        "monitorGroupsCard: rectFor('[data-dashboard-hub-card=\"monitor-groups\"]')",
        "monitorGroupsSummaryGrid: rectFor('[data-dashboard-hub-card=\"monitor-groups\"] .monitoring-hud__monitor-summary-grid')",
        "monitorGroupsActions: rectFor('[data-dashboard-hub-card=\"monitor-groups\"] .monitoring-hud__hub-actions')",
        "monitorGroupsScope: rectFor(\"#monitoring-hud-monitor-editor-scope\")",
        "settingsAction: rectFor(\"#monitoring-hud-settings-action\")",
        "settingsWindow: rectFor(\"#monitoring-hud-settings-window\")",
        "settingsWarningToggle: rectFor(\"#monitoring-hud-settings-warning-toggle\")",
        "readinessCard: rectFor('[data-dashboard-hub-card=\"readiness\"]')",
        "window.getMonitoringHudSurfaceSplitState = function()",
        "window.getMonitoringHudDashboardAcceptanceState = function()",
        "window.getMonitoringHudIsolationState = function()",
        "dashboardAcceptanceBaseline",
        "dashboardProofPath",
        "dashboardStandaloneProof",
        "dashboardClippingProof",
        "dashboardDecouplingProof",
        "dashboardContentPolish",
        "dashboardSettingsModel",
        "dashboardSettingsAffordance",
        "dashboardSettingsPanel",
        "dashboardSettingsPanelState",
        "dashboardSettingsProof",
        "monitorGroupModel",
        "dashboardMonitorCardPolicy",
        "dashboardStandaloneMovementReady",
        "dashboardSettingsContentReady",
        "interfaceAcceptancePolicy",
        "overlayAcceptancePolicy",
        "interfaceBundleApproval",
        "dashboardAcceptanceBaselineReady",
        "overlayAcceptanceNonGating",
        "dashboardMinimalSplitReady",
        "minimal-anchored-hud-overlay",
        "dashboard-configuration-surface",
        "dashboard-configures-minimal-overlay",
        "MonitoringHudOverlayDisplayWindow",
        'monitoringHudMinimal.dataset.nativeWindowSplitProof = "ready-ws26"',
        'monitoringHudMinimal.dataset.clickThroughProof = monitoringHudControlState.anchored',
        'monitoringHudMinimal.dataset.focusProof = monitoringHudControlState.anchored',
        "monitoringHudPanelPositionFrame",
        "monitoringHudQueuedPanelPosition",
        "monitoringHudApplyPanelPosition",
        "window.requestAnimationFrame",
        "monitoringHudSetPanelPosition(rect.left + dx, rect.top + dy, false)",
        'monitoringHud.dataset.dragSmoothing = "native-os-window-move"',
        'monitoringHud.dataset.nativeResizeModel = "os-edge-corner-resize"',
        'document.body.classList.contains("desktop-mode")',
        'monitoringHud.dataset.scrollbarStyle = "nexus-thin-glow"',
        'monitoringHud.dataset.frameOwnership = "single-rounded-dashboard-chrome"',
        'monitoringHud.dataset.scrollOwner = "monitoring-hud-control-hub"',
        'monitoringHud.dataset.scrollbarBoundary = "inner-content-well-gutter"',
        'monitoringHud.dataset.outerFrameHaze = "removed-no-square-layer"',
        'monitoringHud.dataset.gridScope = "control-hub-cards-only"',
        'monitoringHud.dataset.deadzonePolicy = "auto-height-content-no-empty-hit-zones"',
        'monitoringHud.dataset.stickyHeaderMask = "opaque-scroll-mask"',
        'monitoringHud.dataset.nativeResizeHitZone = "preclick-hover-cursor-aligned-14px-app-owned-resize-action"',
        'monitoringHud.dataset.liveResizeProof = "invisible-real-ui-frame-pixel-signature-grow-shrink"',
        'monitoringHud.dataset.resizeProofVisibility = "normal-ui-no-proof-artifacts"',
        'monitoringHud.dataset.resizeProofVisuals = "none"',
        'monitoringHud.dataset.liveResizeVisualArtifact = "none"',
        'monitoringHud.dataset.primaryInterfaceReleaseSurface = "monitoring-hud-dashboard-control-panel"',
        'monitoringHud.dataset.dashboardAcceptanceBaseline = "ws31-dashboard-control-panel"',
        'monitoringHud.dataset.interfaceAcceptancePolicy = "dashboard-only-current-branch"',
        'monitoringHud.dataset.dashboardStandaloneProof = "ws32-dashboard-window-travel"',
        'monitoringHud.dataset.dashboardClippingProof = "within-virtual-desktop"',
        'monitoringHud.dataset.dashboardMinimumEdgeProof = "native-min-size-bottom-edge-visible"',
        'monitoringHud.dataset.dashboardDecouplingProof = "core-overlay-independent"',
        'monitoringHud.dataset.dashboardContentPolish = "branch2-monitor-groups-no-dead-space"',
        'monitoringHud.dataset.dashboardLayoutProof = "monitor-groups-measured-no-overlap"',
        'monitoringHud.dataset.dashboardHomeModel = "control-hub-cards-monitor-management-child-windows"',
        'monitoringHud.dataset.dashboardPollingPlacement = "monitor-group-editor-only"',
        'monitoringHud.dataset.dashboardProofContentPolicy = "validator-artifacts-not-home-surface"',
        'monitoringHud.dataset.dashboardChildWindowScope = "monitor-groups-manage-create-edit-delete-sensor-windows-overlay-profile-settings"',
        'monitoringHud.dataset.dashboardSettingsModel = "hud-overlay-monitor-groups-provider-warning"',
        'monitoringHud.dataset.dashboardSettingsAffordance = "dashboard-ia-card-settings-button"',
        'monitoringHud.dataset.dashboardSettingsPanel = "settings-panel-child-window"',
        'monitoringHud.dataset.dashboardSettingsProof = "visible-open-close-control-hit-target"',
        'monitoringHud.dataset.dashboardIaModel = "branch2-ia-controls-followthrough"',
        'monitoringHud.dataset.dashboardCloseAffordance = "window-level-close-button"',
        'monitoringHud.dataset.dashboardCloseLayout = "uiref-002-compact-top-right-symbol-control"',
        'monitoringHud.dataset.dashboardOpenBadge = "removed"',
        'monitoringHud.dataset.dashboardMonitorSelectionPlacement = "edit-child-window-only"',
        'monitoringHud.dataset.dashboardQuickAccess = "warning-notifications-recording-start-stop"',
        'monitoringHud.dataset.dashboardGlobalFeatureControl = "tray-owned"',
        'monitoringHud.dataset.dashboardDeferredActionPolicy = "disabled-labeled-not-clickable"',
        'monitoringHud.dataset.dashboardCardOrder = "hud-overlay-recording-monitor-groups-data-sources-readiness"',
        'monitoringHud.dataset.monitorGroupModel = "configurable-groups-sensor-assignment"',
        'monitoringHud.dataset.monitorManagementScale = "split-layout-search-filter-large-fixtures"',
        'monitoringHud.dataset.monitorManagementLayout = "compact-list-right-detail-command-center"',
        'monitoringHud.dataset.sensorLibraryScale = "search-facet-thousand-source-fixture"',
        'monitoringHud.dataset.sensorLibraryFixtures = `monitors-${monitoringHudLargeMonitorFixtureCount}-sources-${monitoringHudLargeSensorFixtureCount}`',
        'monitoringHud.dataset.monitorManagementScrollbars = "nexus-styled-child-list-detail-sensor-panes"',
        'monitoringHud.dataset.resizeLiveProof = "invisible-real-ui-frame-pixel-signature-grow-shrink"',
        'monitoringHud.dataset.resizeProofVisibility = "normal-ui-no-proof-artifacts"',
        'monitoringHud.dataset.dashboardMonitorCardPolicy = "overlay-display-owns-visual-rendering"',
        'monitoringHud.dataset.monitorSensorAssignment = "sensor-library-source-picker"',
        'monitoringHud.dataset.sourceClassification = "settings-readiness-outside-assignable-sensors"',
        'monitoringHud.dataset.dashboardProviderTruth = "provider-contract-first"',
        'monitoringHud.dataset.dashboardStateModel = "setup-no-data-degraded-warning"',
        'monitoringHud.dataset.dashboardWarningControls = "visual-non-invasive-only"',
        'monitoringHud.dataset.dashboardFakeTelemetryPolicy = "blocked"',
        "monitoringHud.dataset.warningControlPosture = monitoringHudControlState.warningNotificationsMuted",
        'monitoringHud.dataset.overlayAcceptancePolicy = "deferred-non-gating"',
        "standaloneHudWindow",
        "coreSceneHiddenInHudWindow",
        "hudWindowMode",
        "window.simulateMonitoringHudFaultForValidation = function(enabled)",
        "window.setMonitoringHudControlState = function(state)",
        "monitoringHudInitialCards",
        "monitoringHudHasOwnCards",
        "monitoringHudSafeCardsObject",
        "monitoringHudOverlayProfileSchemaVersion",
        "monitoringHudDefaultOverlayProfileId",
        "monitoringHudNormalizeOverlayProfileState",
        "monitoringHudActiveOverlayProfile",
        "monitoringHudRenderOverlayProfileControls",
        "monitoringHudSetOverlayProfileDropdownOpen",
        "monitoringHudSelectOverlayProfile",
        "monitoringHudCreateOverlayProfile",
        "monitoringHudSaveOverlayProfileDraft",
        "monitoringHudDiscardOverlayProfileDraft",
        "overlayProfiles",
        "activeOverlayProfileId",
        "window.runMonitoringHudOverlayProfileStateProof = function()",
        "window.runMonitoringHudOverlayProfileControlsProof = function()",
        "window.runMonitoringHudOverlayProfileIntegrationProof = function()",
        "monitoringHudOpenOverlayProfileSettingsFromManage",
        "manageContextClickable",
        "settingsRouteRemoved",
        "manageContextAssignedCount",
        "defaultProfileCreatedForLegacyCards",
        "visibleProfileEditorUi",
        "window.runMonitoringHudEmptyCardsPersistenceProof = function()",
        "explicitEmptyCardsPreserved",
        "defaultCardsOnlyWhenCardsAbsent",
        'monitoringHudMonitorListEmpty.dataset.monitorListEmpty = empty ? (count === 0 ? "true-empty-state" : "no-results") : "hidden";',
        "geometry: window.getMonitoringHudLiveClientGeometry",
        "monitoringHudWirePanelDrag",
        "monitoringHudWireCardInteractions",
        "monitoringHudWireControls",
        "monitoringHudRenderMonitorManagement",
        "monitoringHudRenderDashboardSettingsPanel",
        "monitoringHudRenderSensorAssignment",
        "monitoringHudRenderSensorSettings",
        "monitoringHudFilteredSensorDefinitions",
        "monitoringHudBuildLargeMonitorFixture",
        "let monitoringHudLargeFixtureModeEnabled = false;",
        "const sourceDefinitions = Object.values(base);",
        "return monitoringHudLargeFixtureModeEnabled ? sourceDefinitions.concat(monitoringHudLargeSensorFixtures()) : sourceDefinitions;",
        "const filterCandidates = [category, metric, state, sensor.id, sensor.label, sensor.source, sensor.provider, sensor.device, sensor.instance, sensor.reason]",
        'monitoringHudMonitorSensorAssignment.dataset.largeSourceFixtureMode = monitoringHudLargeFixtureModeEnabled ? "enabled-validation-support" : "available-validation-support";',
        "monitoringHudLargeFixtureModeEnabled = true;",
        "window.setMonitoringHudLargeFixtureMode",
        "window.clearMonitoringHudLargeFixtureMode",
        "window.monitoringHudRecordResizeFrame",
        "window.monitoringHudFinishResizeFrame",
        "monitoringHudLargeSensorFixtureCount = 1200",
        "monitoringHudLargeMonitorFixtureCount = 125",
        "monitoringHudConfirmDeleteMonitorGroup",
        'monitoringHudOpenChildWindow("dashboard-settings")',
        'document.querySelectorAll("[data-child-window-close]")',
        "monitoringHudCreateCardNode",
        "monitoringHudRenderOverlayDisplay",
        "monitoringHudCreateOverlayCardNode",
        "monitoringHudClearPanelPosition",
        "monitoringHudRenderSensorCards",
        "window.setDesktopSurfaceMode = function(enabled)",
        'monitoringHud.dataset.renderState = isEnabled ? "product-visibility-baseline" : "hidden"',
        'monitoringHud.dataset.productSurfaceState = (isEnabled && monitoringHudControlState.visible) ? "visible-user-facing" : "hidden"',
        'monitoringHudMinimal.dataset.productSurfaceState = "hidden-deferred"',
        "window.setMonitoringHudTelemetry = function(snapshot)",
        'monitoringHud.dataset.providerState = monitoringHudTelemetry.providerState || "setup-required"',
        'monitoringHud.dataset.liveValues = monitoringHudTelemetry.liveValues || "provider-required"',
        'monitoringHudProviderState.textContent = monitoringHudTelemetry.providerLabel || "Provider setup required"',
        "window.setMonitoringHudPlacementOwnership = function(contract)",
        'monitoringHud.dataset.interactionMode = "standalone-dashboard-window"',
        'monitoringHudPlacementAnchor.textContent = monitoringHudPlacement.anchor || "Deferred / non-gating"',
        'monitoringHudResizePosture.textContent = monitoringHudPlacement.resizePosture || "Overlay settings are future branch scope"',
        "window.setMonitoringHudControlsVisibility = function(contract)",
        '"feature-enabled-dashboard-open"',
        '"feature-enabled-dashboard-closed"',
        '"feature-disabled-dashboard-closed"',
        'monitoringHud.dataset.keybindPolicy = "none"',
        'monitoringHud.dataset.monitorManagement = "sensor-command-center-list-detail-source-picker"',
        'monitoringHud.dataset.overlayModeControls = "overlay-deferred-tray-owned"',
        'monitoringHudControlsVisibility.textContent = monitoringHudControls.visibilityState || "HUD feature disabled from dashboard/tray"',
        'monitoringHudControlsSurface.textContent = monitoringHudControls.controlSurface || "Tray controls HUD feature state; Dashboard open/close is separate; HUD Overlay remains deferred"',
        'monitoringHudControlsPersistence.textContent = monitoringHudControls.persistence || "Store group/layout posture locally"',
        'monitoringHudTrayPath.textContent = monitoringHudControls.trayPath || "Task tray enables/disables HUD feature and opens/closes Dashboard; HUD Overlay controls deferred"',
        "window.setMonitoringHudStatusBehavior = function(snapshot)",
        'monitoringHud.dataset.warningMode = "visual-non-invasive"',
        'monitoringHudWarningPosture.textContent = monitoringHudStatus.warningPosture || "Visual notifications enabled"',
        "monitoringHudInitializeControls();",
        "window.setDesktopSurfaceMode(false)",
        "window.setMonitoringHudTelemetry({})",
        "window.setMonitoringHudPlacementOwnership({})",
        "window.setMonitoringHudControlsVisibility({})",
        "window.setMonitoringHudStatusBehavior({})",
    ):
        _require_contains(js, needle, "monitoring HUD JavaScript", failures)

    for needle in (
        "from .monitoring_hud_controls import build_monitoring_hud_controls_visibility_contract",
        "from .monitoring_hud_placement import build_monitoring_hud_placement_contract",
        "from .monitoring_hud_status import build_monitoring_hud_status_snapshot",
        "from .monitoring_hud_telemetry import build_monitoring_hud_telemetry_snapshot",
        'surface_role: str = "hud"',
        "def _apply_desktop_surface_mode(self):",
        "hud-window-mode",
        "core-window-mode",
        'monitoringHud.dataset.renderState = "product-visibility-baseline"',
        'monitoringHud.dataset.productSurfaceState = "visible-user-facing"',
        "MONITORING_HUD_BASELINE_READY",
        'baseline="product_visibility_baseline"',
        "MONITORING_HUD_PRODUCT_VISIBILITY_READY",
        'seam="WS7"',
        'proof="visible_hud_card_panel"',
        "MONITORING_HUD_DASHBOARD_SURFACE_READY",
        "MONITORING_HUD_DASHBOARD_ACCEPTANCE_BASELINE_READY",
        "MONITORING_HUD_OVERLAY_DEFERRAL_ENFORCED_READY",
        'seam="WS31"',
        'acceptance_policy="dashboard_only_current_branch"',
        'overlay_acceptance="deferred_non_gating"',
        'surface="dashboard_configuration_surface"',
        "MONITORING_HUD_MINIMAL_OVERLAY_READY",
        'surface="minimal_anchored_hud_overlay"',
        "MONITORING_HUD_DASHBOARD_MINIMAL_SPLIT_READY",
        'native_window_split_proof="ready_ws26"',
        "MONITORING_HUD_DASHBOARD_CONTENT_READY",
        "MONITORING_HUD_DASHBOARD_MOTION_POLISH_READY",
        "MONITORING_HUD_DASHBOARD_SCROLLBAR_STYLE_READY",
        "MONITORING_HUD_DASHBOARD_SETTINGS_CONTENT_READY",
        "MONITORING_HUD_DASHBOARD_MONITOR_GROUP_CLARITY_READY",
        "MONITORING_HUD_DASHBOARD_OVERLAY_NON_GATING_COPY_READY",
        "MONITORING_HUD_DASHBOARD_PROVIDER_TRUTH_READY",
        "MONITORING_HUD_DASHBOARD_STATE_MODEL_READY",
        "MONITORING_HUD_DASHBOARD_WARNING_CONTROLS_READY",
        "MONITORING_HUD_EDGELESS_OVERLAY_CANVAS_READY",
        "class MonitoringHudOverlayDisplayWindow(QWidget):",
        "MONITORING_HUD_STANDALONE_OVERLAY_DISPLAY_WINDOW_READY",
        "MONITORING_HUD_ANCHORED_OVERLAY_UNINTERACTABLE_READY",
        "MONITORING_HUD_OVERLAY_POSITION_PRESERVED_READY",
        "MONITORING_HUD_STANDALONE_DASHBOARD_WINDOW_READY",
        "MONITORING_HUD_SURFACE_NATIVE_INDEPENDENCE_READY",
        "MONITORING_HUD_SURFACE_VIRTUAL_DESKTOP_TRAVEL_READY",
        "CORE_VISUALIZATION_HUD_SURFACE_SEPARATION_READY",
        "surfaceSeparationOk",
        "MONITORING_HUD_MINIMAL_NATIVE_OVERLAY_READY",
        "MONITORING_HUD_MINIMAL_ANCHORED_CLICK_THROUGH_READY",
        "MONITORING_HUD_MINIMAL_NON_FOCUS_READY",
        "WindowFromPoint",
        "native_overlay_center_click_through",
        "standalone overlay display proves anchored uninteractable/no-focus",
        "emit_status: bool = True",
        "emit_status=False",
        "MONITORING_HUD_VISIBLE_OVERLAY_READY",
        'pointer_model="click_through_no_focus"',
        "MONITORING_HUD_INTERACTION_MODE_READY",
        "MONITORING_HUD_CONTROL_STATE_READY",
        "MONITORING_HUD_TRAY_ENABLE_RENDER_STABLE_READY",
        "MONITORING_HUD_TRAY_ENABLE_DISABLE_ROUNDTRIP_READY",
        "MONITORING_HUD_TRAY_DASHBOARD_OPEN_CLOSE_READY",
        "MONITORING_HUD_DISABLE_RECOVERY_READY",
        "MONITORING_HUD_REAL_CLIENT_DASHBOARD_VISIBILITY_REQUESTED",
        "_ensure_monitoring_hud_desktop_mode_for_visible_dashboard",
        "MONITORING_HUD_MONITOR_MANAGEMENT_READY",
        "MONITORING_HUD_OVERLAY_PROFILE_STATE_READY",
        "MONITORING_HUD_OVERLAY_DISPLAY_ACCEPTANCE_BRIDGE_READY",
        "MONITORING_HUD_ACTIVE_OVERLAY_PROFILE_DISPLAY_READY",
        "MONITORING_HUD_DASHBOARD_OVERLAY_INDEPENDENCE_READY",
        "profile_aware_bridge",
        "null_profile_state_renders_zero_cards",
        "high_volume_membership_renders_deterministically",
        "active_profile_switch_updates_visible_display",
        "high_volume_display_renders_deterministically",
        "dashboard_and_overlay_roles_distinct",
        "visual_acceptance_baseline_ready",
        "self._monitoring_hud_overlay_profile_signature",
        "self._monitoring_hud_overlay_display_acceptance_signature",
        "self._monitoring_hud_active_overlay_profile_display_signature",
        "self._monitoring_hud_dashboard_overlay_independence_signature",
        "visible_profile_editor=\"slc-039-membership-editor\"",
        "profile_membership_editor=\"editable-slc-039-mapping\"",
        "03_overlay_profile_settings_window_create_clean",
        "03_overlay_profile_settings_window_dirty",
        "03_overlay_profile_manage_context",
        "Follow-up returned-UTS Overlay Profile manager selector/filter/delete proof prepared",
        "Follow-up returned-UTS Manage Monitors clickable Assigned Overlay proof prepared",
        "ok: Boolean(integrationProof.passed && context && manageWindow && !routeButton)",
        "contextBelowSensorSource",
        "SLC-039 Overlay Profile settings-window controls stay bounded and distinct",
        "SLC-041 Overlay Profile focused proof chain covers Dashboard selector, settings-window membership, compact Manage Monitors context, and LV1 UTS boundary",
        '"proofSeam": "SLC-041 Overlay Profile validation and live desktop proof"',
        "photo/video proof is the only LV1 acceptance proof",
        "nonPhotoVideoProofEscalation",
        "formalUserTestSummaryBoundary",
        "MONITORING_HUD_WINDOW_STATUS_READY",
        "MONITORING_HUD_WINDOW_OWNERSHIP_FOCUS_READY",
        "MONITORING_HUD_NATIVE_SYSTEM_MOVE_STARTED",
        "MONITORING_HUD_TRAY_UNANCHOR_DEFERRED",
        "MONITORING_HUD_TRAY_TOGGLE_READY",
        "request_monitoring_hud_dashboard_from_tray",
        "configure_monitoring_hud_live_client_self_qa",
        "MONITORING_HUD_LIVE_CLIENT_SELF_QA_CONFIGURED",
        "MONITORING_HUD_LIVE_CLIENT_SELF_QA_STEP",
        "MONITORING_HUD_LIVE_CLIENT_SELF_QA_INTERACTION_READY",
        "MONITORING_HUD_LIVE_CLIENT_SELF_QA_READY",
        "MONITORING_HUD_NATIVE_PANEL_DRAG_READY",
        "MONITORING_HUD_NATIVE_WINDOW_MOVE_READY",
        "_begin_monitoring_hud_native_user_move",
        "_clear_monitoring_hud_native_user_move",
        "_sync_monitoring_hud_move_frame",
        "user_initiated=move_was_user_initiated",
        "geometry_changed=geometry_changed",
        "reason=monitoring_hud_move_active",
        "MONITORING_HUD_NATIVE_WINDOW_RESIZE_READY",
        "MONITORING_HUD_NATIVE_SYSTEM_RESIZE_STARTED",
        "MONITORING_HUD_NATIVE_WINDOW_RESIZE_FALLBACK_STARTED",
        "_monitoring_hud_window_resize_interaction_available",
        "_monitoring_hud_resize_hit_zone_px",
        "findChildren(QWidget)",
        "_finish_monitoring_hud_fallback_window_resize",
        "_poll_monitoring_hud_fallback_window_resize",
        "_monitoring_hud_resize_refresh_rate_hz",
        "_monitoring_hud_resize_frame_interval_ms",
        "_monitoring_hud_native_window_resize_poll_timer",
        "_monitoring_hud_native_window_resize_frame_timer",
        "monitoringHudResizeProofOverlay",
        "_sync_monitoring_hud_resize_proof_overlay",
        "active-resize-native-repaint-proof",
        "Qt.PreciseTimer",
        "Windows owns the cursor state at the visible resize rail",
        "refresh-rate-paced-cursor-owned-fluid-geometry-resize",
        "WM_NCLBUTTONDOWN",
        "GetAsyncKeyState",
        "_monitoring_hud_windows_resize_cursor_id_for_edges",
        "resize-cursor-no-forced-arrow-release",
        "preclick-hover-cursor-aligned-14px-app-owned-resize-action",
        'overlay.setProperty("resizeProofVisibility", "invisible-test-gated-no-user-facing-artifacts")',
        "polls-real-cursor-before-click",
        "corner_diagonal_resize_arc_percent=50",
        "central-half-of-rounded-corner-arc",
        "_monitoring_hud_rounded_corner_diagonal_resize_edges_for_point",
        "22.5 <= angle <= 67.5",
        "resize_refresh_rate_hz=round(resize_refresh_rate_hz, 2)",
        "resize_frame_interval_ms=resize_frame_interval_ms",
        "resize_poll_interval_ms=resize_frame_interval_ms",
        "self._monitoring_hud_native_window_resize_poll_timer.setInterval(resize_frame_interval_ms)",
        "setMouseTracking(True)",
        "MONITORING_HUD_DASHBOARD_SHELL_LAYOUT_READY",
        "MONITORING_HUD_DASHBOARD_VISUAL_SHELL_READY",
        'minimum_edge_policy="native-min-size-bottom-edge-visible"',
        "def _monitoring_hud_effective_window_minimum_size",
        "min(max(self.minimumHeight(), 595), max(1, virtual.height()))",
        "def _apply_monitoring_hud_effective_window_minimum_size",
        "self.setMinimumSize(min_width, min_height)",
        "self._apply_monitoring_hud_effective_window_minimum_size()",
        "02_dashboard_minimum_size_bottom_edge_visible",
        "Dashboard minimum-size bottom edge remains visible in focused WebView proof",
        "Mandatory default-vs-compact Dashboard and child-window screenshot comparison proves functional readable UI",
        "19_window_size_default_dashboard",
        "19_window_size_compact_overlay_profiles",
        "defaultWindowCount",
        "compactWindowCount",
        "focusedScreenshotCount",
        "chrome_bottom_inside_viewport",
        "minimum_media_min_height_cleared",
        "WM_NCHITTEST",
        "WM_SETCURSOR",
        "WM_NCMOUSEMOVE",
        "HTBOTTOMRIGHT",
        "_monitoring_hud_native_resize_edges_for_hit_test(hit_test)",
        "ctypes.wintypes.MSG.from_address",
        "return 14",
        "save_monitoring_hud_state",
        "_persist_monitoring_hud_feature_state",
        "os-system-move-no-snap",
        "os-edge-corner-resize",
        "refresh-rate-paced-cursor-owned-fluid-geometry-resize",
        "all-edges-and-corners",
        "fallback-direct-move-no-snap",
        "startSystemMove",
        "startSystemResize",
        "WS_EX_APPWINDOW",
        "WS_EX_TOOLWINDOW",
        "self.setWindowFlag(Qt.Window, True)",
        "MONITORING_HUD_DASHBOARD_STANDALONE_WINDOW_TRAVEL_READY",
        "MONITORING_HUD_DASHBOARD_CLIPPING_BOUNDARY_READY",
        "MONITORING_HUD_DASHBOARD_CORE_OVERLAY_DECOUPLING_READY",
        "initial visible HUD identity/provider/no-fake-state",
        "dashboard and minimal HUD surfaces are split",
        "HUD standalone window preserves Core isolation contract",
        "real mouse hit targets are visible and large enough",
        "dashboard standalone window moves across virtual desktop without clipping while Core and Overlay remain decoupled",
        "independent_user_selected_monitor_scoped",
        "attachedToHudDashboardOrNcp",
        "active live-client Dashboard close affordance click sent",
        "active live-client Dashboard settings affordance opens settings panel",
        "Dashboard settings panel exposes truthful supported settings",
        "Dashboard settings panel closes without disabling Dashboard",
        "Dashboard close affordance hides only the Dashboard",
        "_monitoring_hud_dashboard_close_fallback_screen_rect",
        "_monitoring_hud_dashboard_close_last_screen_rect",
        "_monitoring_hud_settings_action_last_screen_rect",
        "_monitoring_hud_window_corner_radius_px = 28",
        "_monitoring_hud_rounded_window_mask_signature",
        "_apply_monitoring_hud_rounded_window_mask",
        "CreateRoundRectRgn",
        "SetWindowRgn",
        "_monitoring_hud_screen_point_inside_rounded_window_mask",
        "_monitoring_hud_window_region_corner_radius_px",
        "self.setAttribute(Qt.WA_NoSystemBackground, True)",
        "self.webview.setAttribute(Qt.WA_TranslucentBackground, True)",
        "path.addRoundedRect(QRectF(rect), float(region_radius), float(region_radius))",
        "self.setMask(region)",
        "MONITORING_HUD_DASHBOARD_ROUNDED_WINDOW_MASK_READY",
        "region_radius_px=region_radius",
        "visual_radius_px=radius",
        'mask_model="simple-native-roundrect-region-matches-css-chrome"',
        'mask_model="native-rounded-window-region-matches-css-chrome"',
        'corner_bleed_policy="no-opaque-rectangular-corners-over-light-backdrops"',
        'resize_hit_test_model="rounded-mask-clipped-visible-rail"',
        "_monitoring_hud_dashboard_settings_control_rect_contains",
        "_handle_monitoring_hud_dashboard_settings_native_control",
        "_handle_monitoring_hud_dashboard_close_native_control",
        "MONITORING_HUD_DASHBOARD_SETTINGS_NATIVE_CONTROL_READY",
        "MONITORING_HUD_DASHBOARD_CLOSE_NATIVE_CONTROL_READY",
        "MONITORING_HUD_DASHBOARD_CHILD_WINDOW_READY",
        "settings_window_present=settings_window_present",
        "settings_window_left=settings_window_left",
        "settings_window_top=settings_window_top",
        "settings_window_right=settings_window_right",
        "settings_window_bottom=settings_window_bottom",
        "MONITORING_HUD_NATIVE_HEADER_DOUBLE_CLICK_SUPPRESSED",
        "WM_LBUTTONDOWN",
        "message_id == WM_LBUTTONDOWN",
        "MONITORING_HUD_VISIBLE_SHOW_GUARD_ARMED",
        "MONITORING_HUD_VISIBLE_SHOW_GUARD_RELEASED",
        "CORE_VISUALIZATION_FIRST_VISIBLE_DEFERRED",
        "_monitoring_hud_deferred_initial_visibility_release",
        "source=monitoring_hud_visible_show_guard",
        "_monitoring_hud_show_guard_generation",
        "_monitoring_hud_show_guard_release_delay_ms = 620",
        'visual_release_model="dashboard_geometry_and_webview_frames_settled_before_opacity"',
        "WM_NCLBUTTONDBLCLK",
        "HTCLIENT",
        "self.webview.setGeometry(self.rect())",
        "frame_interval_s = max(0.004, self._monitoring_hud_native_window_resize_frame_interval_ms / 1000.0)",
        "js_interval_s = max(0.033, frame_interval_s * 2.0)",
        "window.requestAnimationFrame(() => window.dispatchEvent(new Event('resize')))",
        "liveClientGeometryClearedForNativeCloseProof",
        "nativeCloseFallbackRect",
        "dashboard monitor management create/edit/enable/polling state",
        "dashboard monitor editor control mutation sent",
        "hardeningH1MonitorManagementProof",
        "manageWindowCreateAddedMonitor",
        "deleteConfirmationOpened",
        "deleteCancelPreservedMonitor",
        "deleteConfirmRemovedMonitor",
        "deleteConfirmationClosed",
        "cleanup route available",
        "DESKTOP_VISIBLE_OVERLAY_RESULT|success=true",
        "MONITORING_HUD_TELEMETRY_BOUNDARY_READY",
        "MONITORING_HUD_PLACEMENT_OWNERSHIP_READY",
        "MONITORING_HUD_CONTROLS_VISIBILITY_READY",
        "MONITORING_HUD_STATUS_BEHAVIOR_READY",
        'package="PKG-006"',
        'slice="SLC-016"',
        'slice="SLC-025"',
        'slice="SLC-026"',
        'slice="SLC-027"',
        'slice="SLC-028"',
        'adapter="desktop-runtime-boundary"',
        'hardware_polling="native_cpu_load_bounded"',
        'owner="DesktopRuntimeWindow"',
        'placement="standalone-native-hud-window"',
        'controls="hud-controls-visibility"',
        'persistence="local_layout_state"',
        'status="hud-local-readiness-status"',
        'source_truth="renderer_local"',
    ):
        _require_contains(renderer, needle, "desktop renderer HUD hook", failures)

    for needle in (
        "Invoke-DashboardRoundedCornerMaskProbe",
        "Get-LatestSettingsWindowRectFromRuntimeLog",
        "orin_dashboard_rounded_corner_mask_probe.py",
        "dashboard_rounded_corner_mask_light_backdrop",
        "Dashboard rounded native window mask prevents black corner bleed over a white backdrop",
        "MONITORING_HUD_DASHBOARD_ROUNDED_WINDOW_MASK_READY",
        "Close-CommandOverlayBeforeDashboardResize",
        "Invoke-TrayIconActivation",
        "Command Overlay",
        "ncp_tray_icon_left_click_opens",
        "ncp_tray_menu_state_changes_to_close",
        "ncp_tray_icon_left_click_closes",
        "ncp_closed_before_dashboard_resize",
        "Measure-MoveTracking",
        "dashboard_move_fluidity",
        "Move-DashboardAwayFromTrayMenuIfNeeded",
        "dashboard_repositioned_clear_of_tray_menu_for_cleanup",
        "Capture-RectScreenshot",
        "UserElementScreenshotRoot",
        "Add-UserInspectableScreenshotEvidence",
        "focused-per-element-screenshot",
        "context_desktop_screenshots",
        "focused_element_screenshots",
        "Capture-DashboardLocalScreenshot",
        "Capture-DashboardRightEdgeScreenshot",
        "New-HumanClientShortVideoProof",
        "human_client_short_video_proof",
        "shortVideoOrFrameSequenceProof",
        "human_client_short_video.mp4",
        "Mandatory human-client short video/frame-sequence proof failed",
        "GetDpiForWindowValue",
        "Get-DashboardResizeProofContext",
        "Wait-DashboardPostResizeSettle",
        "Get-DashboardRightEdgeRediscoveryClassification",
        "dashboard_post_resize_settle_before_right_edge",
        "dashboard_right_edge_rediscovery_after_corner_resize",
        "diagnosticSamples",
        "offsetFromVisibleEdgePx",
        "rootWindowHandleAtPoint",
        "expectedDashboardHandle",
        "virtualDesktopBounds",
        "visibleEdgeCoordinates",
        "focusedDashboardScreenshot",
        "focusedRightEdgeScreenshot",
        "broad screenshots are locator/context only",
        "postResizeSettle",
        "failureClassification",
        "geometryStable",
        "roundedMaskApplied",
        "webViewVisible",
        "activeResizeStateCleared",
        "cursorReset",
        "repairSelection = \"proof-path handle/coordinate/timing reacquisition; no product edge-math adjustment\"",
        "targetAcquisitionStatus = \"PASS-codex-visible-user-level-right-click-opened-menu\"",
        "manualUserConfirmationDisposition = \"supporting-only-not-pass-proof\"",
        "Live Validation Control-Surface Acquisition Blocked",
        "do not probe nearby taskbar coordinates",
        "tooltip identity or USER manual confirmation is supporting evidence only",
    ):
        _require_contains(human_client_validation, needle, "monitoring HUD human-client validation helper", failures)
    for needle in (
        "NDAI rounded corner validation backdrop",
        "win32gui.GetPixel",
        "LIGHT_THRESHOLD = 210",
        "DASHBOARD_VISIBLE_THRESHOLD = 190",
        "_capture_virtual_desktop",
        "_bring_dashboard_front",
        "rounded corner exterior samples must show the white validation backdrop",
        "cornerSamples",
        "visibleSamples",
    ):
        _require_contains(rounded_mask_probe, needle, "Dashboard rounded-corner live mask probe", failures)

    for needle in (
        "from desktop.core_visualization_renderer import CoreVisualizationWindow",
        "DesktopRuntimeUnavailable",
        "DESKTOP_RUNTIME_UNAVAILABLE",
        'visual_html_path = os.path.join(ROOT_DIR, "nexus_visual", "orin_core_desktop.html")',
        "resolve_core_visualization_screen",
        "CORE_VISUALIZATION_PRESET_MONITOR_SELECTION_READY",
        "app.setQuitOnLastWindowClosed(False)",
        "SHUTDOWN_CONFIRMATION_DIALOG_VISIBLE",
        "REAL_CLIENT_TRAY_PRECHECK_MANIFEST_ENV",
        "REAL_CLIENT_TRAY_PRECHECK_STARTED",
        "MONITORING_HUD_LIVE_SELF_QA_MANIFEST_ENV",
        "MONITORING_HUD_LIVE_SELF_QA_ROOT_ENV",
        "MONITORING_HUD_LIVE_SELF_QA_STEP_DELAY_MS_ENV",
        "MONITORING_HUD_LIVE_SELF_QA_FINAL_HOLD_MS_ENV",
        "MONITORING_HUD_LIVE_SELF_QA_LANE_ENV",
        "from desktop.monitoring_hud_state import load_monitoring_hud_state",
        "MONITORING_HUD_STARTUP_STATE_READY",
        "monitoring_hud_feature_enabled_at_startup",
        "monitoring_hud_dashboard_visible_at_startup",
        "command_overlay_state",
        "Command Overlay",
        "command_overlay_action",
    ):
        _require_contains(tray, needle, "desktop launcher Core/HUD failure isolation", failures)
    for forbidden in (
        "RuntimeControlSurfaceWindow",
        "Nexus Desktop AI Runtime Controls",
        "RUNTIME_CONTROL_SURFACE_SIGNAL_RECEIVED",
        "RUNTIME_CONTROL_SURFACE_SIGNAL_HANDLED",
        "RUNTIME_CONTROL_SURFACE_VISIBLE",
        "ACTIVE_SESSION_CONTROL_SURFACE_SIGNAL_SENT",
    ):
        if forbidden in tray:
            failures.append(
                "desktop launcher Core/HUD failure isolation must not contain "
                f"validation-only runtime control surface marker {forbidden!r}"
            )

    for needle in (
        'MONITORING_HUD_STATE_ENV = "NEXUS_MONITORING_HUD_STATE_PATH"',
        "monitoring_hud_state_path",
        "DEFAULT_OVERLAY_PROFILE_ID",
        "OVERLAY_PROFILE_SCHEMA_VERSION",
        "default_overlay_profile_state",
        "normalize_monitoring_hud_overlay_profiles",
        "load_monitoring_hud_state",
        "save_monitoring_hud_state",
        "MONITORING_HUD_STATE_LOAD_READY",
        "MONITORING_HUD_STATE_SAVE_READY",
        '"overlayProfiles"',
        '"activeOverlayProfileId"',
        '"featureEnabled"',
        '"dashboardVisible"',
        "os.replace",
    ):
        _require_contains(hud_state, needle, "Monitoring HUD persisted state helper", failures)

    for needle in (
        "class CoreVisualizationWindow(QWidget):",
        "CORE_VISUALIZATION_WINDOW_READY|surface=separate_persona_core",
        "CORE_VISUALIZATION_DESKTOP_LAYER_READY",
        "CORE_VISUALIZATION_WINDOW_GEOMETRY_READY",
        "CORE_VISUALIZATION_WORKERW_COORDINATE_REBASE_READY",
        "CORE_VISUALIZATION_FIXED_PRESET_MONITOR_READY",
        "CORE_VISUALIZATION_WINDOW_VISIBLE|surface=separate_persona_core",
        "CORE_VISUALIZATION_INDEPENDENT_PRESET_MONITOR_READY",
        "surface=separate_persona_core",
        "background-color: transparent",
        "setFixedSize",
        "compute_core_parent_geometry",
        "coordinate_space=\"parent\"",
        "desktop_screen_geometry",
        "desktop_layer=workerw",
        "hud_attachment=none",
        "ncp_attachment=none",
        "position_desktop_child",
    ):
        _require_contains(core_renderer, needle, "independent ORIN Core renderer", failures)
    _require(
        "WindowStaysOnTopHint" not in core_renderer,
        "independent ORIN Core renderer must not request topmost foreground ownership",
        failures,
    )

    desktop_mode_method = re.search(
        r"def _apply_desktop_surface_mode\(self\):.*?def _monitoring_hud_telemetry_snapshot",
        renderer,
        flags=re.DOTALL,
    )
    method_text = desktop_mode_method.group(0).casefold() if desktop_mode_method else ""
    for forbidden in ("psutil", "subprocess", "wmi", "pynvml"):
        _require(
            forbidden not in method_text,
            f"desktop renderer HUD product hook must not implement {forbidden} behavior",
            failures,
        )

    for needle in (
        'PACKAGE_ID = "PKG-006"',
        'SLICE_ID = "SLC-025"',
        'ADAPTER_ID = "desktop-runtime-boundary"',
        "provider route is admitted",
        'DEFAULT_POLLING_RATE_MS = 1000',
        "NativeCpuLoadProbe",
        "GetSystemTimes",
        '"Waiting for safe provider"',
        '"Provider-first; no fake values"',
        '"1s after provider proof; CPU load warming"',
        '"sensorCards": [card.as_dict() for card in self.sensor_cards]',
        'MonitoringHudSensor(',
        'sensor_id="cpu-load"',
        'sensor_id="gpu-load"',
        'value="Unavailable"',
    ):
        _require_contains(telemetry, needle, "monitoring HUD telemetry adapter", failures)
    _require_no_collection_imports(telemetry, "monitoring HUD telemetry adapter", failures)

    for needle in (
        'PACKAGE_ID = "PKG-006"',
        'SLICE_ID = "SLC-026"',
        'PLACEMENT_ID = "standalone-native-hud-window"',
        'renderer_owner="Dashboard-first runtime window"',
        'surface_owner="Standalone Qt WebEngine Dashboard window"',
        'anchor="Overlay anchor deferred until future interface release"',
        'pointer_model="Normal dashboard window; OS-native move; no topmost/no focus steal"',
        'snap_model="Dashboard window movement is unsnapped; Overlay layout snap remains deferred"',
        'card_layout_model="cards resize and snap in overlay edit mode"',
        'z_index="normal-window-no-topmost"',
    ):
        _require_contains(placement, needle, "monitoring HUD placement contract", failures)
    _require_no_collection_imports(placement, "monitoring HUD placement contract", failures)

    for needle in (
        'PACKAGE_ID = "PKG-006"',
        'SLICE_ID = "SLC-027"',
        'CONTROLS_ID = "hud-controls-visibility"',
        "feature_enabled: bool | None = None",
        'visible: bool = True',
        'anchored: bool = True',
        'snap_enabled: bool = True',
        'polling_rate_ms: int = 1000',
        'control_surface="Tray controls HUD feature state; Dashboard open/close is separate; Overlay controls remain deferred"',
        'persistence="Store group/layout posture locally"',
        'operator_action="No default keybinds"',
        'anchor_state="overlay-deferred"',
        'tray_path="Task tray enables/disables HUD feature and opens/closes Dashboard; Overlay anchor controls deferred"',
        'snap_state="enabled" if snap_enabled else "disabled"',
        'monitor_management="Dashboard Sensor Command Center uses compact monitor selection, detail-pane delete, Nexus source-filter dropdown/facets, supported-source assignment, and monitor polling controls"',
        'overlay_mode_controls="Overlay display and anchor/unanchor controls are deferred/non-gating"',
    ):
        _require_contains(controls, needle, "monitoring HUD controls visibility contract", failures)
    _require_no_collection_imports(controls, "monitoring HUD controls visibility contract", failures)

    for needle in (
        'PACKAGE_ID = "PKG-006"',
        'SLICE_ID = "SLC-028"',
        'STATUS_ID = "hud-local-readiness-status"',
        'status_kind = "no-data"',
        'status_kind = "degraded"',
        'status_kind = "ready"',
        'status_label = "Provider setup required"',
        'status_label = "Reconnect/setup route unavailable"',
        'no_data_behavior="Show unavailable; no fake values"',
        'degraded_behavior="Name reconnect/setup gap with visual warning only"',
        'warning_posture="Visual badge, color state, and text label only"',
        'source_truth="Provider-contract-first local readiness only"',
    ):
        _require_contains(status, needle, "monitoring HUD status behavior contract", failures)
    _require_no_collection_imports(status, "monitoring HUD status behavior contract", failures)

    for needle in (
        "overlayDisplayAcceptance",
        "deferred-non-gating",
        "coreRepairClassification",
        "dependency-repair-only",
        "dashboardSpecificProof",
        "userTestSummaryExportRefreshed",
        "revisedOverlayProof",
        "fullVirtualDesktopScreenshot",
        "userInspectableScreenshot",
        "standaloneDashboardWindowReady",
        "surfaceNativeIndependenceReady",
        "dashboardStandaloneWindowTravelReady",
        "dashboardClippingBoundaryReady",
        "dashboardCoreOverlayDecouplingReady",
        "dashboardSettingsContentReady",
        "dashboardMonitorGroupClarityReady",
        "dashboardOverlayNonGatingCopyReady",
        "dashboardProviderTruthReady",
        "dashboardStateModelReady",
        "dashboardWarningControlsReady",
        "overlayCardsMovableReady",
        "surfaceVirtualDesktopTravelReady",
        "coreIndependentPresetMonitorReady",
        "coreHudSurfaceSeparationReady",
        "coreWorkerwCoordinateRebaseReady",
        "standaloneOverlayDisplayWindowReady",
        "anchoredOverlayUninteractableReady",
        "overlayPositionPreservedReady",
        "providerContractReady",
        "noFakeTelemetryPosture",
        "RunInteractionSelfQA",
        "VisibleClient",
        "ActiveUserFacingClient",
        "InteractionStepDelayMilliseconds",
        "FinalClientHoldSeconds",
        "ExactDesktopShortcutPath",
        "Get-ExactUserDesktopShortcutPath",
        "Resolve-ExactDesktopShortcutForActiveRoot",
        "Start-ExactDesktopShortcutRuntime",
        "C:\\Users\\anden\\OneDrive\\Desktop\\FAM-006 RED - Nexus Desktop AI Launcher.lnk",
        "NEXUS_MONITORING_HUD_LIVE_SELF_QA_MANIFEST",
        "NEXUS_MONITORING_HUD_LIVE_SELF_QA_ROOT",
        "NEXUS_MONITORING_HUD_LIVE_SELF_QA_LANE",
        "NEXUS_HARNESS_LOG_ROOT",
        "NEXUS_HARNESS_AUTO_ACCEPT_RELAUNCH",
        "NEXUS_HARNESS_SUPPRESS_ALREADY_RUNNING_DIALOGS",
        "NEXUS_HARNESS_RELAUNCH_WAIT_SECONDS",
        "exact-user-desktop-shortcut-launch",
        "exactUserDesktopShortcutLaunchProof",
        "InteractionManifest",
        "InteractionEvidenceRoot",
        "ElementScreenshotEvidenceRoot",
        "Copy-FocusedElementScreenshotsToUserEvidence",
        "perElementUserInspectableScreenshots",
        "issueFormCoverageMatrix",
        "02_recording_option_c_focused_lane_complete",
        "Get-HudIssueIdsForElementLabel",
        "minimum is $MinimumScreenshots",
        "focused_element_screenshots",
        "LV1 focused per-element screenshots missing or failed",
        "supporting-only-unless-launched-through-exact-user-desktop-shortcut",
        "ShortVideoFrameRoot",
        "monitoring_hud_lv1_short_video.mp4",
        "shortVideoProof",
        "LV1 short video/frame-sequence proof missing or failed",
        "generated mandatory LV1 short video proof",
        "activeUserFacingClient",
        "interactionSelfQARequested",
        "interactionStepDelayMs",
        "finalClientHoldMs",
        "interactionManifestStatus",
        "MONITORING_HUD_LIVE_CLIENT_SELF_QA_INTERACTION_READY",
        "MONITORING_HUD_LIVE_CLIENT_SELF_QA_READY",
        "CORE_VISUALIZATION_PRESET_MONITOR_SELECTION_READY",
        "CORE_VISUALIZATION_WINDOW_READY|surface=separate_persona_core",
        "CORE_VISUALIZATION_DESKTOP_LAYER_READY|surface=separate_persona_core",
        "CORE_VISUALIZATION_WINDOW_GEOMETRY_READY",
        "CORE_VISUALIZATION_WORKERW_COORDINATE_REBASE_READY",
        "CORE_VISUALIZATION_FIXED_PRESET_MONITOR_READY",
        "CORE_VISUALIZATION_WINDOW_VISIBLE|surface=separate_persona_core",
        "CORE_VISUALIZATION_INDEPENDENT_PRESET_MONITOR_READY",
        "CORE_VISUALIZATION_HUD_SURFACE_SEPARATION_READY",
        "MONITORING_HUD_DASHBOARD_STANDALONE_WINDOW_TRAVEL_READY",
        "MONITORING_HUD_DASHBOARD_CLIPPING_BOUNDARY_READY",
        "MONITORING_HUD_DASHBOARD_CORE_OVERLAY_DECOUPLING_READY",
        "MONITORING_HUD_DASHBOARD_SETTINGS_CONTENT_READY",
        "MONITORING_HUD_DASHBOARD_MONITOR_GROUP_CLARITY_READY",
        "MONITORING_HUD_DASHBOARD_OVERLAY_NON_GATING_COPY_READY",
        "MONITORING_HUD_WINDOW_STATUS_READY",
        "interaction self-QA manifest PASS",
        "MONITORING_HUD_BASELINE_READY",
        "MONITORING_HUD_PRODUCT_VISIBILITY_READY",
        "MONITORING_HUD_DASHBOARD_SURFACE_READY",
        "MONITORING_HUD_MINIMAL_OVERLAY_READY",
        "MONITORING_HUD_DASHBOARD_MINIMAL_SPLIT_READY",
        "MONITORING_HUD_DASHBOARD_CONTENT_READY",
        "MONITORING_HUD_DASHBOARD_MOTION_POLISH_READY",
        "MONITORING_HUD_DASHBOARD_SCROLLBAR_STYLE_READY",
        "MONITORING_HUD_DASHBOARD_SETTINGS_CONTENT_READY",
        "MONITORING_HUD_DASHBOARD_MONITOR_GROUP_CLARITY_READY",
        "MONITORING_HUD_DASHBOARD_OVERLAY_NON_GATING_COPY_READY",
        "MONITORING_HUD_EDGELESS_OVERLAY_CANVAS_READY",
        "MONITORING_HUD_STANDALONE_OVERLAY_DISPLAY_WINDOW_READY",
        "MONITORING_HUD_ANCHORED_OVERLAY_UNINTERACTABLE_READY",
        "MONITORING_HUD_OVERLAY_POSITION_PRESERVED_READY",
        "MONITORING_HUD_VISIBLE_OVERLAY_READY",
        "MONITORING_HUD_TELEMETRY_BOUNDARY_READY",
        "MONITORING_HUD_PLACEMENT_OWNERSHIP_READY",
        "MONITORING_HUD_CONTROLS_VISIBILITY_READY",
        "MONITORING_HUD_STATUS_BEHAVIOR_READY",
        "MONITORING_HUD_INTERACTION_MODE_READY",
        "MONITORING_HUD_CONTROL_STATE_READY",
        "MONITORING_HUD_TRAY_ENABLE_RENDER_STABLE_READY",
        "MONITORING_HUD_TRAY_ENABLE_DISABLE_ROUNDTRIP_READY",
        "MONITORING_HUD_TRAY_DASHBOARD_OPEN_CLOSE_READY",
        "MONITORING_HUD_DISABLE_RECOVERY_READY",
        "DESKTOP_VISIBLE_OVERLAY_RESULT|success=true",
        "DESKTOP_OUTCOME|SETTLED|state=dormant",
        "settling Dashboard-first client before full-desktop screenshot",
        "beforeLaunchScreenshot",
        "afterLaunchScreenshot",
        "monitoring_hud_desktop_before_launch.png",
        "monitoring_hud_desktop_after_launch.png",
        "beforeAfterDesktopComparisonReady",
        "manifest.json",
        "Stop-Process -Id $script:RuntimeProcess.Id -Force",
        "No-progress watchdog exceeded",
        "Assert-NoSyntheticLiveValidationInteraction",
        "no-synthetic-interaction preflight",
        "active route contains synthetic interaction code",
        "lacks real OS-level mouse input proof",
        "JavaScript clicks, synthetic DOM events, WebView native-message fallback, WebView handler calls, QTest widget-only events, and state mutation are banned",
        "real-input fallback policy PASS",
        "synthetic fallback requires explicit USER waiver",
        "Compact Overlay Profiles delete confirmation stays unclipped and non-overlapping",
    ):
        _require_contains(live_validation, needle, "monitoring HUD live validation helper", failures)
    for needle in (
        "real-os-mouse-cursor-move-down-up",
        "realOsInputProof",
        "automatedOsClickAttempted",
        "directJsClickUsed",
        "Overlay Profile manager selector real OS mouse click sent",
        "Overlay Profile manager selector option real OS mouse hover sent",
        "proof requires real OS-level mouse input before UTS",
        "Compact Overlay Profiles delete confirmation stays unclipped and non-overlapping",
        "compact_overlay_profile_delete_confirmation_unclipped",
        "overlayProfileUnsavedState",
        "hudUnsavedState",
        "modalGuard",
        "closeSuppressed",
        "Active child window prevents Dashboard click-through under overlapping controls",
        "UIREF-002-compact-window-control-cluster",
        "ai-control-center-symbol-visible-accessible-label",
        "default-hover-focus-pressed-disabled-keyboard-accessible",
        "controls-focusable-accessible-names-tooltips",
        "folder-open-blocked-status-visible",
        "Log Viewer folder action status",
    ):
        _require_contains(renderer, needle, "monitoring HUD renderer live interaction proof", failures)

    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("FAIL: FAM-006 Monitoring/HUD product visibility validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: FAM-006 HUD Dashboard-first source truth is bounded, provider-truthful, and marker-backed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
