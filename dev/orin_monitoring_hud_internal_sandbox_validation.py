"""Internal sandbox validation for the FAM-006 Monitoring HUD Workstream.

This helper proves the current-branch Dashboard-first Workstream handoff without
asking the USER for a User Test Summary during Workstream or Branch Readiness.
It validates the bounded runtime seams for the HUD shell, controls,
provider-truthful telemetry, no-data/degraded states, visual warnings, source
truth, naming sterilization, and SLC-041 Overlay Profile proof-readiness.
Overlay/display proof remains supporting evidence unless that interface is later
re-admitted.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from desktop.monitoring_hud_controls import build_monitoring_hud_controls_visibility_contract
from desktop.monitoring_hud_placement import build_monitoring_hud_placement_contract
from desktop.monitoring_hud_status import build_monitoring_hud_status_snapshot
from desktop.monitoring_hud_state import (
    ACTIVE_OVERLAY_RECORDING_TARGET_KIND,
    DEFAULT_OVERLAY_PROFILE_ID,
    MONITORING_HUD_STATE_ENV,
    build_active_overlay_recording_target_snapshot,
    load_monitoring_hud_state,
    normalize_monitoring_hud_overlay_profiles,
    save_monitoring_hud_state,
)
from desktop.monitoring_hud_telemetry import build_monitoring_hud_telemetry_snapshot
from desktop.recording_output_contract import validate_recording_output_contract


LOG_ROOT = ROOT / "dev" / "logs" / "fam_006_monitoring_hud_internal_sandbox"


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _require_contains(text: str, needle: str, label: str, failures: list[str]) -> None:
    _require(needle in text, f"{label} is missing {needle!r}", failures)


def _retired_name() -> str:
    return "".join(chr(code) for code in (74, 97, 114, 118, 105, 115))


def _tracked_text_files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        parts = set(relative.parts)
        if ".git" in parts or "__pycache__" in parts:
            continue
        if len(relative.parts) >= 2 and relative.parts[0] == "dev" and relative.parts[1] == "logs":
            continue
        if parts & {"dev", "desktop", "nexus_visual", "Docs", "Audio"} or path.name == "main.py":
            if path.suffix.lower() in {".py", ".pyw", ".ps1", ".md", ".txt", ".html", ".css", ".js", ".json"}:
                result.append(path)
    return result


def _validate_naming_sterilization(failures: list[str]) -> None:
    retired = _retired_name().casefold()
    for path in _tracked_text_files():
        relative = path.relative_to(ROOT)
        _require(retired not in str(relative).casefold(), f"{relative}: path contains retired product name", failures)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if retired in line.casefold():
                failures.append(f"{relative}:{line_number}: content contains retired product name")


def _validate_static_surface(failures: list[str]) -> None:
    core_html = _read("nexus_visual/orin_core.html")
    core_css = _read("nexus_visual/orin_core.css")
    core_desktop_html = _read("nexus_visual/orin_core_desktop.html")
    core_desktop_css = _read("nexus_visual/orin_core_desktop.css")
    core_js = _read("nexus_visual/orin_core.js")
    html = _read("nexus_visual/monitoring_hud.html")
    css = _read("nexus_visual/monitoring_hud.css")
    js = _read("nexus_visual/monitoring_hud.js")
    live_validation = _read("dev/orin_monitoring_hud_live_validation.ps1")
    renderer = _read("desktop/desktop_renderer.py")
    core_renderer = _read("desktop/core_visualization_renderer.py")
    tray = _read("desktop/orin_desktop_main.py") + "\n" + _read("desktop/tray_controller.py")
    hud_state = _read("desktop/monitoring_hud_state.py")
    human_client_validation = _read("dev/orin_monitoring_hud_human_client_validation.ps1")
    rounded_mask_probe = _read("dev/orin_dashboard_rounded_corner_mask_probe.py")

    for needle in (
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
        "overlayProfileUnsavedState",
        "hudUnsavedState",
        "modalGuard",
        "closeSuppressed",
    ):
        _require_contains(renderer, needle, "monitoring HUD renderer live interaction proof", failures)
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
        for forbidden in (
            "monitoring-hud",
            "Monitoring HUD",
            "monitoringHud",
            "MONITORING_HUD_",
        ):
            _require(
                forbidden not in text,
                f"{label} must remain HUD-free after standalone HUD split; found {forbidden!r}",
                failures,
            )

    for needle in (
        '<div id="scene">',
        '<div id="core-wrap">',
        '<script src="orin_core.js"></script>',
    ):
        _require_contains(core_html, needle, "ORIN Core restored visual markup", failures)

    for needle in (
        '<body class="desktop-mode">',
        '<link rel="stylesheet" href="orin_core_desktop.css" />',
        '<script src="orin_core.js"></script>',
    ):
        _require_contains(core_desktop_html, needle, "ORIN Core desktop visual markup", failures)

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
        _require_contains(core_desktop_css, needle, "ORIN Core desktop transparent CSS", failures)

    for needle in (
        'data-hud-module="monitoring-hud-shell-module"',
        'data-product-surface-role="dashboard-configuration-surface"',
        'data-configures-surface="monitoring-hud-minimal"',
        'data-split-contract="dashboard-configures-minimal-overlay"',
        'id="monitoring-hud-minimal"',
        'data-product-surface-role="minimal-anchored-hud-overlay"',
        'data-configured-by="monitoring-hud"',
        'data-native-overlay-owner="MonitoringHudOverlayDisplayWindow"',
        'data-native-window-split-proof="ready-ws26"',
        'data-click-through-proof="native-transparent-input"',
        'data-focus-proof="native-no-focus-noactivate"',
        'id="monitoring-hud-overlay-display"',
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
        "HUD Dashboard",
        'data-native-resize-model="os-edge-corner-resize"',
        'id="monitoring-hud-dashboard-close-action"',
        'data-control="close-dashboard"',
        'data-anchor-state="anchored"',
        'data-visibility-state="hidden-deferred"',
        'data-snap-state="enabled"',
        'data-card-model="category-sensor-cards"',
        'data-polling-default-ms="1000"',
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
        "Select an existing profile or create a new one first",
        'id="monitoring-hud-warning-toggle"',
        'id="monitoring-hud-settings-action"',
        'data-control="open-dashboard-settings"',
        'aria-haspopup="dialog"',
        "Settings",
        'id="monitoring-hud-edit-monitor-action"',
        'data-control-visual-parity="overlay-profile-settings"',
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
        "CPU Group",
        "GPU Group",
        "2 Monitor Groups configured. Manage opens list, create, edit, delete, and supported sensor assignment controls.",
        "Create Monitor",
        "Manage Monitors",
        'id="monitoring-hud-manage-monitor-create-action"',
        'id="monitoring-hud-monitor-empty-create-action"',
        'data-monitor-empty-state-action="primary-create"',
        'id="monitoring-hud-monitor-detail-note"',
        'id="monitoring-hud-monitor-detail-actions"',
        'data-monitor-detail-actions="selected-monitor-footer"',
        'data-detail-action-row="save-left-discard-delete-right"',
        'id="monitoring-hud-edit-monitor-discard"',
        'data-control="discard-edit-monitor"',
        'data-control-state="clean-disabled"',
        'class="monitoring-hud__detail-action-row"',
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
        "Monitor Groups",
        "Data Sources",
        "HUD Overlay",
        "Warning Notifications",
        "Readiness",
        "Waiting for safe provider",
        "Feature Deferred",
        "Manage Data Sources",
        'data-feature-status="feature-deferred"',
        "Provider-first; no fake values",
        "HUD Overlay release acceptance is deferred.",
        "Deferred / non-gating",
        "Overlay settings are future branch scope",
        "Show unavailable; no fake values",
        "Dashboard configures overlay behavior",
        "Monitor Groups assign supported sources and settings. HUD Overlay owns future visual display; fake values remain blocked.",
    ):
        _require_contains(html, needle, "HUD HTML product surface", failures)
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
        "Delete Selected Monitor" not in html,
        "HUD detail-pane delete action must say Delete Monitor, not Delete Selected Monitor",
        failures,
    )
    _require(
        'id="monitoring-hud-create-monitor-action"' not in html
        and 'data-control="create-monitor"' not in html,
        "HUD dashboard must remove the main Create Monitor action; creation remains inside Manage Monitors and empty state",
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
    ):
        _require(
            forbidden_home_copy not in html,
            f"dashboard home must not include stale proof/inline-editor copy: {forbidden_home_copy}",
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
        _require(forbidden_dashboard_card not in html, "dashboard must not render stale monitor cards/actions or old source-picker controls", failures)

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
        "HUD CSS must gate visible resize proof artifacts behind explicit test-visible mode",
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
        "code, DOM, marker, log, manifest, and helper output are diagnostic evidence only",
        "nonPhotoVideoProofEscalation",
        "Claims that cannot be proven in a photo or video must be elevated to the USER for manual validation",
        "formalUserTestSummaryBoundary",
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

    for needle in (
        'body.desktop-mode #monitoring-hud[data-anchor-state="unanchored"]',
        "body.desktop-mode #monitoring-hud-minimal",
        "body.desktop-mode #monitoring-hud-overlay-display",
        'body.desktop-mode #monitoring-hud-overlay-display[data-anchor-state="unanchored"]',
        ".monitoring-hud__toolbar",
        "z-index: 24;",
        "--monitoring-hud-affordance-default-warning-shadow",
        ".monitoring-hud__surface-role",
        ".monitoring-hud__config-heading",
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
        ".monitoring-hud-minimal-card",
        ".monitoring-hud-overlay-display__frame",
        ".monitoring-hud-overlay-display__canvas",
        ".monitoring-hud-overlay-display__watermark",
        ".monitoring-hud-overlay-card",
        ".monitoring-hud-overlay-card__quick-actions",
        ".monitoring-hud-overlay-card__topline",
        "scrollbar-width: thin",
        "body.desktop-mode .monitoring-hud__control-hub::-webkit-scrollbar",
        "body.desktop-mode .monitoring-hud__nexus-scroll-pane::-webkit-scrollbar",
        "body.desktop-mode .monitoring-hud__child-window::-webkit-scrollbar",
        'body.desktop-mode #monitoring-hud[data-live-resize-active="true"][data-resize-proof-visuals="test-visible"] .monitoring-hud__chrome',
        "--monitoring-hud-scrollbar-size: 8px;",
        "width: var(--monitoring-hud-scrollbar-size);",
        "margin: 10px 0 14px;",
        'body.desktop-mode #monitoring-hud[data-drag-smoothing="native-os-window-move"]',
        "scrollbar-gutter: stable;",
        "scrollbar-gutter: auto;",
        "--dashboard-card-holder-inset-proof: scrollbar-exempt-equal-card-insets;",
        ".monitoring-hud__hub-card:has(.monitoring-hud__bounded-dropdown[data-dropdown-open=\"true\"])",
        ".monitoring-hud__child-actions--guard",
        "justify-self: stretch;",
    ):
        _require_contains(css, needle, "HUD CSS interaction surface", failures)
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
            "HUD minimum-size native edge CSS",
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
            "HUD compact monitor list CSS",
            failures,
        )
    _require(
        ".monitoring-hud__selector-control" not in css,
        "HUD CSS interaction surface must not keep legacy Dashboard monitor selector styling",
        failures,
    )

    for needle in (
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
        "window.setMonitoringHudControlState = function(state)",
        "monitoringHudInitialCards",
        "monitoringHudHasOwnCards",
        "monitoringHudSafeCardsObject",
        "window.runMonitoringHudEmptyCardsPersistenceProof = function()",
        "explicitEmptyCardsPreserved",
        "defaultCardsOnlyWhenCardsAbsent",
        'monitoringHudMonitorListEmpty.dataset.monitorListEmpty = empty ? (count === 0 ? "true-empty-state" : "no-results") : "hidden";',
        "geometry: window.getMonitoringHudLiveClientGeometry",
        "monitoringHudUpdateSurfaceSplit",
        "primaryInterfaceReleaseSurface",
        "dashboardAcceptanceBaseline",
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
        "dashboardAcceptanceBaselineReady",
        "overlayAcceptanceNonGating",
        "monitoringHudPanelPositionFrame",
        "monitoringHudQueuedPanelPosition",
        "monitoringHudApplyPanelPosition",
        "window.requestAnimationFrame",
        'monitoringHud.dataset.scrollbarStyle = "nexus-thin-glow"',
        'monitoringHud.dataset.scrollbarBoundary = "inner-content-well-gutter"',
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
        "MonitoringHudOverlayDisplayWindow",
        'monitoringHudMinimal.dataset.nativeWindowSplitProof = "ready-ws26"',
        'monitoringHudMinimal.dataset.clickThroughProof = monitoringHudControlState.anchored',
        'monitoringHudMinimal.dataset.focusProof = monitoringHudControlState.anchored',
        "monitoringHudRenderOverlayDisplay",
        "monitoringHudCreateOverlayCardNode",
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
        "minimal-anchored-hud-overlay",
        "dashboard-configuration-surface",
        "monitoringHudWirePanelDrag",
        'monitoringHud.dataset.nativeResizeModel = "os-edge-corner-resize"',
        'monitoringHud.dataset.frameOwnership = "single-rounded-dashboard-chrome"',
        'monitoringHud.dataset.outerFrameHaze = "removed-no-square-layer"',
        'monitoringHud.dataset.scrollOwner = "monitoring-hud-control-hub"',
        'monitoringHud.dataset.gridScope = "control-hub-cards-only"',
        'monitoringHud.dataset.deadzonePolicy = "auto-height-content-no-empty-hit-zones"',
        'monitoringHud.dataset.stickyHeaderMask = "opaque-scroll-mask"',
        'monitoringHud.dataset.nativeResizeHitZone = "preclick-hover-cursor-aligned-14px-app-owned-resize-action"',
        'monitoringHud.dataset.liveResizeProof = "invisible-real-ui-frame-pixel-signature-grow-shrink"',
        'monitoringHud.dataset.resizeProofVisuals = "none"',
        'monitoringHud.dataset.liveResizeVisualArtifact = "none"',
        'document.body.classList.contains("desktop-mode")',
        "monitoringHudWireCardInteractions",
        "monitoringHudWireControls",
        "monitoringHudRenderMonitorManagement",
        "monitoringHudRenderDashboardSettingsPanel",
        "monitoringHudRenderSensorAssignment",
        "monitoringHudRenderSensorSettings",
        "monitoringHudConfirmDeleteMonitorGroup",
        'monitoringHudOpenChildWindow("dashboard-settings")',
        'document.querySelectorAll("[data-child-window-close]")',
        "monitoringHudCreateCardNode",
        "monitoringHudRenderSensorCards",
        "monitoringHudStorageKey",
        "monitoringHudPollingRate.addEventListener",
        "monitoringHudControlState.snapEnabled",
        'monitoringHud.dataset.interactionMode = "standalone-dashboard-window"',
    ):
        _require_contains(js, needle, "HUD JavaScript controls", failures)

    for needle in (
        "MONITORING_HUD_WINDOW_STATUS_READY",
        "MONITORING_HUD_DASHBOARD_SURFACE_READY",
        "MONITORING_HUD_DASHBOARD_ACCEPTANCE_BASELINE_READY",
        "MONITORING_HUD_OVERLAY_DEFERRAL_ENFORCED_READY",
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
        "MONITORING_HUD_MINIMAL_NATIVE_OVERLAY_READY",
        "MONITORING_HUD_MINIMAL_ANCHORED_CLICK_THROUGH_READY",
        "MONITORING_HUD_MINIMAL_NON_FOCUS_READY",
        "standalone overlay display proves anchored uninteractable/no-focus",
        "emit_status=False",
        "MONITORING_HUD_WINDOW_OWNERSHIP_FOCUS_READY",
        "MONITORING_HUD_NATIVE_SYSTEM_MOVE_STARTED",
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
        "MONITORING_HUD_DASHBOARD_CORE_OVERLAY_DECOUPLING_READY",
        "request_monitoring_hud_unanchor_from_tray",
        "request_monitoring_hud_toggle_from_tray",
        "request_monitoring_hud_dashboard_from_tray",
        "MONITORING_HUD_INTERACTION_MODE_READY",
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
        "active live-client Dashboard settings affordance opens settings panel",
        "Dashboard settings panel exposes truthful supported settings",
        "Dashboard settings panel closes without disabling Dashboard",
        "liveClientGeometryClearedForNativeCloseProof",
        "nativeCloseFallbackRect",
        "MONITORING_HUD_CONTROL_STATE_READY",
        "MONITORING_HUD_TRAY_ENABLE_RENDER_STABLE_READY",
        "MONITORING_HUD_TRAY_ENABLE_DISABLE_ROUNDTRIP_READY",
        "MONITORING_HUD_TRAY_DASHBOARD_OPEN_CLOSE_READY",
        "MONITORING_HUD_DISABLE_RECOVERY_READY",
        "MONITORING_HUD_REAL_CLIENT_DASHBOARD_VISIBILITY_REQUESTED",
        "_ensure_monitoring_hud_desktop_mode_for_visible_dashboard",
        "MONITORING_HUD_MONITOR_MANAGEMENT_READY",
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
        "self._monitoring_hud_overlay_display_acceptance_signature",
        "self._monitoring_hud_active_overlay_profile_display_signature",
        "self._monitoring_hud_dashboard_overlay_independence_signature",
        "hardeningH1MonitorManagementProof",
        "manageWindowCreateAddedMonitor",
        "deleteConfirmationOpened",
        "deleteCancelPreservedMonitor",
        "deleteConfirmRemovedMonitor",
        "deleteConfirmationClosed",
        "MONITORING_HUD_TRAY_UNANCHOR_DEFERRED",
        "MONITORING_HUD_TRAY_TOGGLE_READY",
        "CORE_VISUALIZATION_HUD_SURFACE_SEPARATION_READY",
        "surfaceSeparationOk",
        "native_cpu_load_bounded",
    ):
        _require_contains(renderer, needle, "desktop renderer HUD runtime", failures)

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
        "from desktop.monitoring_hud_state import load_monitoring_hud_state",
        "MONITORING_HUD_STARTUP_STATE_READY",
        "monitoring_hud_feature_enabled_at_startup",
        "monitoring_hud_dashboard_visible_at_startup",
        "from desktop.tray_controller import DesktopTrayEntry, TRAY_IDENTITY_LABEL",
    ):
        _require_contains(tray, needle, "desktop launcher Core/HUD failure isolation", failures)

    for needle in (
        'MONITORING_HUD_STATE_ENV = "NEXUS_MONITORING_HUD_STATE_PATH"',
        "monitoring_hud_state_path",
        "load_monitoring_hud_state",
        "save_monitoring_hud_state",
        "MONITORING_HUD_STATE_LOAD_READY",
        "MONITORING_HUD_STATE_SAVE_READY",
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
        "CORE_VISUALIZATION_INDEPENDENT_PRESET_MONITOR_READY",
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

    for needle in (
        "monitoring_hud_html_path",
        'surface_role="hud"',
        "HUD Feature Settings",
        "Open HUD Dashboard",
        "Close HUD Dashboard",
        "HUD Overlay Deferred",
        "Unanchor HUD Overlay",
        "command_overlay_state",
        "Command Overlay",
        "command_overlay_action",
        "TRAY_MONITORING_HUD_TOGGLE_REDIRECTED",
        "TRAY_MONITORING_HUD_DASHBOARD_REQUESTED",
        "TRAY_MONITORING_HUD_UNANCHOR_REQUESTED",
        "dashboard_open_action_enabled",
        "dashboard_close_action_enabled",
    ):
        _require_contains(tray, needle, "desktop tray HUD controls", failures)


def _validate_contracts(failures: list[str]) -> dict[str, object]:
    first = build_monitoring_hud_telemetry_snapshot(
        page_ready=True,
        desktop_mode=True,
        runtime_log_path=str(LOG_ROOT / "runtime_log.txt"),
        event_route_present=True,
        polling_rate_ms=1000,
    ).as_dict()
    time.sleep(0.05)
    second = build_monitoring_hud_telemetry_snapshot(
        page_ready=True,
        desktop_mode=True,
        runtime_log_path=str(LOG_ROOT / "runtime_log.txt"),
        event_route_present=True,
        polling_rate_ms=1000,
    ).as_dict()
    placement = build_monitoring_hud_placement_contract(
        desktop_mode=True,
        x=100,
        y=120,
        width=900,
        height=700,
    ).as_dict()
    controls = build_monitoring_hud_controls_visibility_contract(
        desktop_mode=True,
        visible=True,
        anchored=False,
        snap_enabled=True,
        polling_rate_ms=1000,
    ).as_dict()
    status = build_monitoring_hud_status_snapshot(
        page_ready=True,
        desktop_mode=True,
        event_route_present=True,
    ).as_dict()
    output_contract = validate_recording_output_contract()

    cards = second.get("sensorCards") or []
    sensors = {
        sensor.get("id"): sensor
        for card in cards
        for sensor in card.get("sensors", [])
        if isinstance(sensor, dict)
    }
    _require(second.get("pollingRateMs") == 1000, "telemetry contract must use 1s default polling", failures)
    _require(second.get("liveValues") in {"native-cpu-load-only", "provider-required"}, "telemetry contract has invalid live value state", failures)
    _require("cpu-load" in sensors, "telemetry contract is missing CPU load sensor", failures)
    _require(sensors.get("gpu-load", {}).get("value") == "Unavailable", "GPU load must remain provider-unavailable", failures)
    _require(sensors.get("gpu-thermal", {}).get("value") == "Unavailable", "GPU thermal must remain provider-unavailable", failures)
    _require(sensors.get("cpu-thermal", {}).get("value") == "Provider required", "CPU thermal must remain provider-required", failures)
    _require(
        placement.get("snapModel") == "Dashboard window movement is unsnapped; Overlay layout snap remains deferred",
        "placement contract must describe Dashboard unsnapped movement posture",
        failures,
    )
    _require(placement.get("cardLayoutModel") == "cards resize and snap in overlay edit mode", "placement contract must describe card layout", failures)
    _require(controls.get("anchorState") == "overlay-deferred", "controls contract must keep overlay anchor controls deferred", failures)
    _require(controls.get("pollingRateMs") == "1000", "controls contract must preserve 1s default polling", failures)
    _require(
        controls.get("monitorManagement") == "Dashboard Sensor Command Center uses compact monitor selection, detail-pane delete, Nexus source-filter dropdown/facets, supported-source assignment, and monitor polling controls",
        "controls contract must describe dashboard monitor management",
        failures,
    )
    _require(
        controls.get("overlayModeControls") == "Overlay display and anchor/unanchor controls are deferred/non-gating",
        "controls contract must describe overlay mode controls",
        failures,
    )
    _require(
        controls.get("warningControls") == "Visual badge, text label, and color state only; no audio or screen flash",
        "controls contract must preserve visual/non-invasive warning controls",
        failures,
    )
    _require(status.get("warningPosture") == "Visual badge, color state, and text label only", "status contract must preserve visual warning posture", failures)
    _require(output_contract.get("passed") is True, "SLC-054 recording output contract proof must pass", failures)
    _require(output_contract.get("parseReadback") is True, "SLC-054 output contract must parse/read back in memory", failures)
    _require(output_contract.get("fileWritingEnabled") is True, "SLC-054 output contract must admit bounded local file writing", failures)
    _require(output_contract.get("recordingExecutionEnabled") is True, "SLC-054 output contract must admit bounded recording execution", failures)
    _require(output_contract.get("writeReadbackPassed") is True, "SLC-054 output contract must prove write/readback", failures)

    persisted_state = {}
    previous_state_path = os.environ.get(MONITORING_HUD_STATE_ENV)
    with tempfile.TemporaryDirectory(prefix="fam006_hud_state_") as temp_dir:
        os.environ[MONITORING_HUD_STATE_ENV] = str(Path(temp_dir) / "monitoring_hud_state.json")
        try:
            saved = save_monitoring_hud_state(
                feature_enabled=True,
                dashboard_visible=False,
                source="internal_sandbox_validation",
                monitor_ids=["cpu", "gpu"],
                overlay_profiles={
                    "custom-overlay": {
                        "id": "custom-overlay",
                        "name": "Custom Overlay Profile",
                        "monitorIds": ["gpu", "gpu", "missing", "cpu"],
                        "recordingProfileId": "must-not-survive",
                        "monitorGroupId": "must-not-survive",
                    }
                },
                active_overlay_profile_id="missing-overlay",
            )
            persisted_state = load_monitoring_hud_state()
            _require(saved, "HUD feature state persistence save must succeed", failures)
            _require(
                persisted_state.get("featureEnabled") is True,
                "HUD feature state persistence must remember enabled state",
                failures,
            )
            _require(
                persisted_state.get("dashboardVisible") is False,
                "HUD feature state persistence must allow Dashboard to stay closed on startup",
                failures,
            )
            _require(
                persisted_state.get("activeOverlayProfileId") == DEFAULT_OVERLAY_PROFILE_ID,
                "Overlay Profile active pointer must fall back to the default profile",
                failures,
            )
            default_profile = (persisted_state.get("overlayProfiles") or {}).get(DEFAULT_OVERLAY_PROFILE_ID, {})
            _require(
                default_profile.get("monitorIds") == ["cpu", "gpu"],
                "Default Overlay Profile must preserve legacy monitor membership across save/load",
                failures,
            )
            custom_profile = (persisted_state.get("overlayProfiles") or {}).get("custom-overlay", {})
            _require(
                custom_profile.get("monitorIds") == ["gpu", "cpu"],
                "Overlay Profile normalization must remove duplicate and stale monitor ids",
                failures,
            )
            _require(
                "recordingProfileId" not in custom_profile and "monitorGroupId" not in custom_profile,
                "Overlay Profile state must stay distinct from Recording Profile and Monitor Group fields",
                failures,
            )
            persisted_target = persisted_state.get("activeOverlayRecordingTarget", {})
            _require(
                persisted_target.get("kind") == ACTIVE_OVERLAY_RECORDING_TARGET_KIND,
                "SLC-051 active Overlay recording target snapshot must be present in persisted HUD state",
                failures,
            )
            _require(
                persisted_target.get("source") == "active-overlay-profile-membership",
                "SLC-051 recording target must derive from active Overlay Profile membership",
                failures,
            )
            _require(
                persisted_target.get("scope") == "target-session-truth-only",
                "SLC-051 recording target must stay target/session truth only",
                failures,
            )
            _require(
                persisted_target.get("membershipSnapshotCandidate") == ["cpu", "gpu"],
                "SLC-051 fallback target must expose the normalized active Overlay Profile membership snapshot candidate",
                failures,
            )
            _require(
                persisted_target.get("snapshotAtStartModel") == "snapshot-at-recording-start",
                "SLC-051 recording target must preserve active snapshot-at-start semantics",
                failures,
            )
            _require(
                persisted_target.get("hiddenRecordingTargetState") == "absent"
                and persisted_target.get("recordingExecutionState") == "ready"
                and persisted_target.get("fileWritingState") == "ready",
                "SLC-051 target proof must block hidden target state while allowing ready recording execution and file writing",
                failures,
            )
            normalized_legacy = normalize_monitoring_hud_overlay_profiles({}, ["cpu", "gpu"])
            _require(
                normalized_legacy.get("overlayProfiles", {}).get(DEFAULT_OVERLAY_PROFILE_ID, {}).get("monitorIds") == ["cpu", "gpu"],
                "Legacy card state without overlayProfiles must create a default Overlay Profile",
                failures,
            )
            normalized_deleted_default = normalize_monitoring_hud_overlay_profiles(
                {
                    "monitorIds": ["cpu", "gpu"],
                    "overlayProfiles": {},
                    "activeOverlayProfileId": "",
                    "overlayProfileDefaultDeletedByUser": True,
                },
                ["cpu", "gpu"],
            )
            _require(
                normalized_deleted_default.get("overlayProfiles") == {},
                "Persisted empty Overlay Profile set must not recreate a deleted default profile",
                failures,
            )
            _require(
                normalized_deleted_default.get("activeOverlayProfileId") == "",
                "Persisted empty Overlay Profile set must preserve an empty active profile pointer",
                failures,
            )
            _require(
                normalized_deleted_default.get("overlayProfileDefaultDeletedByUser") is True,
                "Persisted empty Overlay Profile set must keep the default-deleted marker",
                failures,
            )
            _require(
                normalized_deleted_default.get("activeOverlayRecordingTarget", {}).get("targetState") == "deleted-default-empty",
                "SLC-051 target proof must classify deleted default / null active profile state",
                failures,
            )
            normalized_empty_membership = normalize_monitoring_hud_overlay_profiles(
                {
                    "monitorIds": ["cpu", "gpu"],
                    "overlayProfiles": {
                        "empty-target": {
                            "id": "empty-target",
                            "name": "Empty Target",
                            "monitorIds": [],
                        }
                    },
                    "activeOverlayProfileId": "empty-target",
                },
                ["cpu", "gpu"],
            )
            _require(
                normalized_empty_membership.get("activeOverlayRecordingTarget", {}).get("targetState") == "empty-membership",
                "SLC-051 target proof must classify empty active Overlay Profile membership",
                failures,
            )
            normalized_high_volume = normalize_monitoring_hud_overlay_profiles(
                {
                    "monitorIds": [f"monitor-{index:03d}" for index in range(125)],
                    "overlayProfiles": {
                        "high-volume-target": {
                            "id": "high-volume-target",
                            "name": "High Volume Target",
                            "monitorIds": [f"monitor-{index:03d}" for index in range(125)]
                            + ["missing-monitor", "monitor-000"],
                            "recordingProfileId": "must-not-survive",
                        }
                    },
                    "activeOverlayProfileId": "high-volume-target",
                },
            )
            high_volume_target = normalized_high_volume.get("activeOverlayRecordingTarget", {})
            high_volume_profile = (normalized_high_volume.get("overlayProfiles") or {}).get("high-volume-target", {})
            _require(
                high_volume_target.get("targetState") == "high-volume-membership"
                and high_volume_target.get("membershipSnapshotCandidateCount") == 125
                and "missing-monitor" not in high_volume_target.get("membershipSnapshotCandidate", []),
                "SLC-051 target proof must normalize high-volume active Overlay Profile membership",
                failures,
            )
            _require(
                "recordingProfileId" not in high_volume_profile,
                "SLC-051 target proof must not preserve hidden Recording Profile state",
                failures,
            )
            direct_target = build_active_overlay_recording_target_snapshot(
                active_profile_id="direct-target",
                requested_active_profile_id="direct-target",
                profiles={
                    "direct-target": {
                        "id": "direct-target",
                        "name": "Direct Target",
                        "monitorIds": ["gpu"],
                    }
                },
            )
            _require(
                direct_target.get("membershipSnapshotCandidate") == ["gpu"]
                and direct_target.get("separateRecordingProfileState") == "not-created",
                "SLC-051 direct target helper must expose target/session truth without a separate Recording Profile",
                failures,
            )
            saved_deleted_default = save_monitoring_hud_state(
                feature_enabled=True,
                dashboard_visible=True,
                source="internal_sandbox_deleted_default_overlay_profile",
                monitor_ids=["cpu", "gpu"],
                overlay_profiles={},
                active_overlay_profile_id="",
                overlay_profile_default_deleted_by_user=True,
            )
            deleted_default_state = load_monitoring_hud_state()
            _require(saved_deleted_default, "Deleted default Overlay Profile state save must succeed", failures)
            _require(
                deleted_default_state.get("overlayProfiles") == {},
                "Deleted default Overlay Profile state must remain empty across save/load",
                failures,
            )
            _require(
                deleted_default_state.get("activeOverlayProfileId") == "",
                "Deleted default Overlay Profile state must keep empty active id across save/load",
                failures,
            )
            _require(
                deleted_default_state.get("overlayProfileDefaultDeletedByUser") is True,
                "Deleted default Overlay Profile state must preserve the deletion marker across save/load",
                failures,
            )
            saved_selection = save_monitoring_hud_state(
                feature_enabled=True,
                dashboard_visible=True,
                source="internal_sandbox_slc039_membership_mapping",
                monitor_ids=["cpu", "gpu"],
                overlay_profiles={
                    DEFAULT_OVERLAY_PROFILE_ID: default_profile,
                    "custom-overlay": {
                        "id": "custom-overlay",
                        "name": "Focused Overlay Profile",
                        "monitorIds": ["gpu"],
                        "displayMode": "monitor-cards",
                    },
                },
                active_overlay_profile_id="custom-overlay",
            )
            selected_state = load_monitoring_hud_state()
            _require(saved_selection, "SLC-039 Overlay Profile selection save must succeed", failures)
            _require(
                selected_state.get("activeOverlayProfileId") == "custom-overlay",
                "SLC-039 active Overlay Profile selection must persist across save/load",
                failures,
            )
            selected_profile = (selected_state.get("overlayProfiles") or {}).get("custom-overlay", {})
            _require(
                selected_profile.get("name") == "Focused Overlay Profile",
                "SLC-039 Overlay Profile rename metadata must persist across save/load",
                failures,
            )
            _require(
                selected_profile.get("monitorIds") == ["gpu"],
                "SLC-039 Overlay Profile membership mapping must persist across save/load",
                failures,
            )
        finally:
            if previous_state_path is None:
                os.environ.pop(MONITORING_HUD_STATE_ENV, None)
            else:
                os.environ[MONITORING_HUD_STATE_ENV] = previous_state_path

    return {
        "firstTelemetry": first,
        "secondTelemetry": second,
        "placement": placement,
        "controls": controls,
        "status": status,
        "recordingOutputContract": output_contract,
        "persistedState": persisted_state,
    }


def _write_manifest(status: str, failures: list[str], contracts: dict[str, object]) -> Path:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    manifest_path = LOG_ROOT / f"{stamp}_manifest.json"
    payload = {
        "status": status,
        "contracts": contracts,
        "failures": failures,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest_path


def validate() -> tuple[list[str], Path]:
    failures: list[str] = []
    _validate_naming_sterilization(failures)
    _validate_static_surface(failures)
    contracts = _validate_contracts(failures)
    status = "PASS" if not failures else "FAIL"
    manifest_path = _write_manifest(status, failures, contracts)
    return failures, manifest_path


def main() -> int:
    failures, manifest_path = validate()
    if failures:
        print("FAIL: FAM-006 Monitoring HUD internal sandbox validation failed")
        for failure in failures:
            print(f"- {failure}")
        print(f"manifest: {manifest_path}")
        return 1

    print("PASS: FAM-006 Monitoring HUD internal sandbox validation is green")
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
