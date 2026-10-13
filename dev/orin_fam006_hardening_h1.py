"""Validate recording source contracts and isolated local output readback."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from desktop.recording_output_contract import validate_recording_output_contract




def _repo_root() -> Path:
    return ROOT


def _read_repo_text(relative_path: str) -> str:
    return (_repo_root() / relative_path).read_text(encoding="utf-8")


def _contains_all(text: str, markers: tuple[str, ...]) -> bool:
    return all(marker in text for marker in markers)


def validate_recording_visual_source(source_text: str) -> list[str]:
    failures: list[str] = []
    required_source_markers = (
        "fam006-unique-child-studio-shell-v5",
        "unique-child-purpose-stack-v6",
        "detached-child-window-header-no-title-card",
        "title-first-description-beneath-no-title-card",
        "action-first-controller-with-ai-control-center-state-rows-no-report-panels",
        "doorway-shell-viewer-deferred-row-plus-bottom-folder-actions-no-technical-path-table",
        "boxedTablePanelRejected",
        "tableRowTruthLayoutRejected",
        "statusReportPanelRejected",
        "technicalPathViewerRejected",
        "action-first-folder-access-shell-v6",
        "monitoring-hud__controller-meta-strip",
        'data-element-group="recording-actions"',
        'data-element-group="log-folder-actions"',
        'class="monitoring-hud__state-row monitoring-hud__studio-truth-row"',
        "monitoring-hud__studio-truth-row",
        "monitoring-hud__log-target-strip",
        'data-row-primitive="ai-control-center-state-row"',
        "monitoring-hud-hub-action-content-fit-equal-gutter-v4",
        "hub-action-content-fit-equal-gutter-32px-pill",
        "HEIGHT = 154",
        "MINIMUM_HEIGHT = 154",
        "recording_studio_feature_studio_v5",
        "HEIGHT = 134",
        "MINIMUM_HEIGHT = 134",
        "log_viewer_studio_feature_studio_v6",
        "right: 14px",
        "height: 31px",
        "padding-inline: 14px",
        "font-weight: 720",
        "font-size: 17px",
        "font-size: 11px",
        "--monitoring-hud-studio-row-value-gutter: 8px",
        "--monitoring-hud-studio-row-label-column: max-content",
        "grid-template-columns: var(--monitoring-hud-studio-row-label-column, max-content) minmax(0, 1fr)",
        "gap: 6px",
        "column-gap: var(--monitoring-hud-studio-row-value-gutter)",
        "syncStudioTruthRowValueColumns",
        "valueColumnAlignment",
        "padding: 4px 0 2px",
        "not-resizable-position-memory-only",
        "edge-resize-native-top-level",
        "WM_NCHITTEST+manual-fallback-geometry-resize",
        'data-fixed-controller-height="154"',
    )
    for marker in required_source_markers:
        if marker not in source_text:
            failures.append(f"source marker missing: {marker}")
    forbidden_source_markers = (
        "fam006-unique-child-studio-shell-v4",
        "unique-child-purpose-stack-v4",
        "unique-child-purpose-stack-v5",
        'data-fixed-controller-height="330"',
        'data-fixed-controller-height="210"',
        'data-fixed-controller-height="184"',
        "HEIGHT = 184",
        "MINIMUM_HEIGHT = 184",
        "recording_studio_feature_studio_v4",
        "HEIGHT = 210",
        "HEIGHT = 352",
        "HEIGHT = 164",
        "MINIMUM_HEIGHT = 164",
        "log_viewer_studio_feature_studio_v4",
        "log_viewer_studio_feature_studio_v5",
        "WIDTH = 480",
        "WIDTH = 560",
        "action-first-recording-controller-v6",
        "monitoring-hud__controller-hero",
        "monitoring-hud__controller-route-strip",
        '"stateRowDensityPolicy": "rejected-dense-row-stack-not-used"',
        '"titleGroupVisualPolicy": "fam006-detached-child-window-title-row"',
        '"childWindowTitleGrammar": "category-line-plus-strong-title"',
        "<span>Recording State</span>",
        "<span>Native Log</span>",
        'class="monitoring-hud__controller-target"',
        'class="monitoring-hud__controller-status"',
        'class="monitoring-hud__log-access-item"',
        "<span>Native Logs</span>",
        "<span>Exported Logs</span>",
        "<span>Status</span>",
        "ultra-light-recording-controller",
        "compact-folder-access-shell",
        "monitoring-hud-hub-action-content-fit-equal-gutter-v2",
        "monitoring-hud-hub-action-content-fit-equal-gutter-v3",
        'data-row-primitive="ai-control-center-fact-row"',
        "monitoring-hud__controller-summary",
        "monitoring-hud__controller-log-card",
        "monitoring-hud__log-destination-card",
        '"stateRowDensityPolicy": "divider-rows-no-boxed-table"',
        "--nexus-feature-studio-title-bg",
        "ai-control-center-status-truth-row",
    )
    for marker in forbidden_source_markers:
        if marker in source_text:
            failures.append(f"stale source marker present: {marker}")
    return failures


def build_recording_contract_proof() -> dict[str, Any]:
    output_contract = validate_recording_output_contract()

    hud_state = _read_repo_text("desktop/monitoring_hud_state.py")
    hud_js = _read_repo_text("nexus_visual/monitoring_hud.js")
    hud_html = _read_repo_text("nexus_visual/monitoring_hud.html")
    studio_html = _read_repo_text("nexus_visual/monitoring_hud_studio.html")
    studio_js = _read_repo_text("nexus_visual/monitoring_hud_studio.js")
    studio_css = _read_repo_text("nexus_visual/nexus_window_primitives.css")
    renderer = _read_repo_text("desktop/desktop_renderer.py")
    main_entry = _read_repo_text("desktop/orin_desktop_main.py")
    output_source = _read_repo_text("desktop/recording_output_contract.py")

    slc_results = [
        {
            "slice": "SLC-051",
            "result": _contains_all(
                hud_state + hud_js,
                (
                    "activeOverlayRecordingTarget",
                    "activeOverlayRecordingTargetProof",
                    "recordingExecutionState",
                    "fileWritingState",
                ),
            ),
            "hardeningCheck": "active Overlay Profile target/session truth markers",
        },
        {
            "slice": "SLC-052",
            "result": _contains_all(
                hud_html + hud_js,
                (
                    'data-dashboard-hub-card="recording"',
                    "Dashboard Recording",
                    "slc-052-dashboard-recording-card-target-status",
                    "dashboard-recording-card-primary",
                    "hud-overlay-overlay-focused",
                    "dashboard-status-summary",
                    "quick-access-start-stop",
                    "recording-studio-focused-control-status",
                    "monitoringHudToggleRecording",
                    "Log Viewer",
                ),
            ),
            "hardeningCheck": "Dashboard Quick Access Start/Stop plus Recording card target/status markers",
        },
        {
            "slice": "SLC-053",
            "result": _contains_all(
                renderer + hud_js + studio_html + studio_js + studio_css,
                (
                    "Recording Suite",
                    "recording_studio_window",
                    "MONITORING_HUD_RECORDING_STUDIO_READY",
                    "_dispatch_monitoring_hud_recording_studio_action",
                    "recordingExecutionState",
                    "recordingFileWritingState",
                    "fam006-unique-child-studio-shell-v5",
                    "unique-child-standalone-feature-studio",
                    "no-resize-recording-edge-resize-log-viewer",
                    "attachedChildCornerResizeGripAbsent",
                    "denseValidatorStatusPanelRejected",
                    "nexus-window-primitives-v1-rendered-dom-css",
                    "Bounded FAM-006 Shared Primitive Carry-In",
                    "nexus_visual/nexus_window_primitives.css",
                    "sharedPrimitiveConsumer",
                    "featureStudioPrimitive",
                    "primaryVisualComparator",
                    "visualPrimitiveAdoptionContract",
                    "acceptedReferenceSet",
                    "photo-video-comparison-required",
                    "photo-video-comparison-not-runtime-self-attestation",
                    "visualRuntimeSelfAttestation",
                    "visualMatrixRequired",
                    "ultra-lightweight-detached-recording-controller",
                    "dashboardLifecycleDependency",
                    "recording-studio-open-log-viewer-action",
                    "recording-studio-start-action",
                    "recording-studio-pause-action",
                    "recording-studio-stop-action",
                    "selected-REC-A-explicit-start-pause-stop-plus-open-log-viewer",
                    "monitoring-hud-studio-start-action",
                    "monitoring-hud-studio-pause-action",
                    "monitoring-hud-studio-stop-action",
                    "recording-transport-pill",
                    "transport-pill-left-route-right",
                    "segmented-transport-pill-left",
                    "monitoring-hud__transport-pill",
                    "monitoring-hud__transport-segment--first",
                    "monitoring-hud__transport-segment--middle",
                    "monitoring-hud__transport-segment--last",
                    "monitoring-hud-hub-action-content-fit-equal-gutter-v4",
                    "height: 31px",
                    "padding-inline: 14px",
                    "font-weight: 720",
                    "font-size: 17px",
                    "font-size: 11px",
                    "--monitoring-hud-studio-row-value-gutter: 8px",
                    "--monitoring-hud-studio-row-label-column: max-content",
                    "--monitoring-hud-studio-row-stack-vertical-gutter: 6px",
                    "--monitoring-hud-studio-row-dropdown-edge-gutter: 1px",
                    "grid-template-columns: var(--monitoring-hud-studio-row-label-column, max-content) minmax(0, 1fr)",
                    "gap: var(--monitoring-hud-studio-row-stack-vertical-gutter)",
                    "column-gap: var(--monitoring-hud-studio-row-value-gutter)",
                    'data-row-stack-vertical-gutter="6"',
                    'data-row-dropdown-edge-gutter="1"',
                    'data-dropdown-layer-contract="overlay-owned-control-not-peer-row"',
                    ".monitoring-hud__studio-truth-row [data-bounded-dropdown]",
                    "margin-block: var(--monitoring-hud-studio-row-dropdown-edge-gutter)",
                    "syncStudioTruthRowValueColumns",
                    "valueColumnAlignment",
                    "padding: 4px 0 2px",
                    "detached-child-window-header-no-title-card",
                    "titleCardState",
                    "title-first-description-beneath-no-title-card",
                    "overflow: visible",
                    "text-overflow: clip",
                    "not-resizable-position-memory-only",
                    "data-resize-contract=\"not-resizable-position-memory-only\"",
                    "data-fixed-controller-height=\"154\"",
                    "HEIGHT = 154",
                    "MINIMUM_HEIGHT = 154",
                    "recording_studio_feature_studio_v5",
                    "WM_NCHITTEST+manual-fallback-geometry-resize",
                    "monitoringHudStudioNativeDragHandle",
                    "hub-action-content-fit-equal-gutter-32px-pill",
                    "windowPlacementMemoryState",
                    "titleHeaderBadgeState",
                    "ai-control-center-title-group-no-extra-badge",
                    "top-right-header",
                    "AI-Control-Center-UIREF-001-title-group",
                    "AI-Control-Center-UIREF-002-window-control-cluster",
                    "AI-Control-Center-UIREF-003-action-button",
                    "ai-control-center-symbol-window-control-cluster",
                    "monitoring-hud-hub-action-content-fit-equal-gutter-v4",
                    "text-overflow: clip",
                    "log-viewer-open-export",
                    "folder-actions-right-aligned",
                    "action-first-controller-with-ai-control-center-state-rows-no-report-panels",
                    "unique-child-purpose-stack-v6",
                    "action-first controller plus AI Control Center / HUD Dashboard state-row underglow",
                    "data-row-primitive=\"ai-control-center-state-row\"",
                    "ai-control-center-symbol-window-control-pill",
                    "nativeLogRowsContained",
                ),
            ),
            "hardeningCheck": "standalone Recording Suite is active while tray/keybind/export customization remains future-gated",
        },
        {
            "slice": "SLC-054-SHELL",
            "result": _contains_all(
                renderer + hud_js + studio_html + studio_css,
                (
                    "Log Viewer",
                    "log_viewer_shell",
                    "MONITORING_HUD_LOG_VIEWER_STUDIO_READY",
                    "recording_output_dir",
                    "recording_export_dir",
                    "create-or-open-before-session",
                    "exportCustomizationState",
                    "fam006-unique-child-studio-shell-v5",
                    "unique-child-standalone-feature-studio",
                    "attachedChildCornerResizeGripAbsent",
                    "nexus-window-primitives-v1-rendered-dom-css",
                    "Bounded FAM-006 Shared Primitive Carry-In",
                    "nexus_visual/nexus_window_primitives.css",
                    "sharedPrimitiveConsumer",
                    "featureStudioPrimitive",
                    "primaryVisualComparator",
                    "visualPrimitiveAdoptionContract",
                    "acceptedReferenceSet",
                    "photo-video-comparison-required",
                    "photo-video-comparison-not-runtime-self-attestation",
                    "visualRuntimeSelfAttestation",
                    "visualMatrixRequired",
                    "compact-current-branch-log-access-shell",
                    "edge-resize-native-top-level",
                    "windowPlacementMemoryState",
                    "ai-control-center-state-row",
                    "stateRowsContained",
                    "titleHeaderBadgeState",
                    "ai-control-center-title-group-no-extra-badge",
                    "top-right-header",
                    "AI-Control-Center-UIREF-001-title-group",
                    "AI-Control-Center-UIREF-002-window-control-cluster",
                    "AI-Control-Center-UIREF-003-action-button",
                    "ai-control-center-symbol-window-control-cluster",
                    "monitoring-hud-hub-action-content-fit-equal-gutter-v4",
                    "detached-child-window-header-no-title-card",
                    "titleCardState",
                    "title-first-description-beneath-no-title-card",
                    "hub-action-content-fit-equal-gutter-32px-pill",
                    "HEIGHT = 134",
                    "MINIMUM_HEIGHT = 134",
                    "log_viewer_studio_feature_studio_v6",
                    "right: 14px",
                    "doorway-shell-viewer-deferred-row-plus-bottom-folder-actions-no-technical-path-table",
                    "compact folder-action shell with AI Control Center / HUD Dashboard state-row underglow",
                    "action-first-folder-access-shell-v6",
                    "data-row-primitive=\"ai-control-center-state-row\"",
                    "font-size: 17px",
                    "font-size: 11px",
                    "nativeFolderPreSessionUsable",
                    "exportFolderPreSessionUsable",
                    "openNativeControlProof",
                    "openExportControlProof",
                    "data-control=\"log-viewer-open-native\"",
                    "data-control=\"log-viewer-open-export\"",
                    "ai-control-center-symbol-window-control-pill",
                ),
            ),
            "hardeningCheck": "minimal Log Viewer shell opens native/export roots pre-session and keeps full viewer/export customization future-gated",
        },
        {
            "slice": "SLC-054",
            "result": bool(
                output_contract.get("passed")
                and output_contract.get("fileWritingEnabled")
                and output_contract.get("recordingExecutionEnabled")
                and output_contract.get("writeReadbackPassed")
                and output_contract.get("profileLogConsistencyPassed")
                and output_contract.get("twoProfileLogConsistencyPassed")
                and _contains_all(
                    output_source,
                    (
                        "recording_output_contract",
                        "write_recording_output_files",
                        "readback_recording_output_files",
                        "ndai-native-recording-log",
                        ".ndailog",
                        "nativeLogReadableOnlyByNDAI",
                        "normalProductSaveCreatesExport",
                        "render_recording_output_csv",
                        "parse_recording_output_csv",
                        '"fileWritingState": "enabled"',
                        '"recordingExecutionState": "enabled"',
                    ),
                )
            ),
            "hardeningCheck": "output contract schema/write/readback and active execution markers",
        },
        {
            "slice": "ISSUE-258",
            "result": _contains_all(
                renderer + main_entry,
                (
                    "monitoring_hud_initial_state",
                    "monitoring_hud_saved_state",
                    "overlayProfiles",
                    "activeOverlayProfileId",
                    "overlayProfileDefaultDeletedByUser",
                ),
            ),
            "hardeningCheck": "Overlay Profile restart persistence hydration markers",
        },
    ]

    stale_recording_studio_model_absent = not any(
        marker in studio_html + studio_css
        for marker in (
            "monitoring-hud-studio-recording-toggle-action",
            'data-control="recording-studio-toggle"',
            "runtime-current-single-toggle-candidate-selection-pending",
            "grid-template-columns: repeat(3, minmax(0, 1fr))",
            "monitoring-hud-hub-action-content-fit-equal-gutter-v2",
            'class="monitoring-hud__controller-target"',
            'class="monitoring-hud__controller-status"',
            'class="monitoring-hud__log-access-item"',
            "monitoring-hud-hub-action-content-fit-v1",
            "<span>Target Overlay Profile</span>",
            "<span>Recording State</span>",
            "<span>Native Log</span>",
            "fam006-detached-child-studio-shell-v3",
            "child-window-row-stack",
            "monitoring-hud__resize-corner",
            "qsizegrip-bottom-right-enabled",
        )
    )
    visual_ledger_source = "\n".join(
        [
            _read_repo_text("desktop/desktop_renderer.py"),
            _read_repo_text("nexus_visual/monitoring_hud_studio.html"),
            _read_repo_text("nexus_visual/monitoring_hud_studio.js"),
            _read_repo_text("nexus_visual/nexus_window_primitives.css"),
        ]
    )
    visual_source_failures = validate_recording_visual_source(visual_ledger_source)

    proof = {
        "sourceResults": slc_results,
        "allSourceChecksPassed": all(item["result"] for item in slc_results),
        "outputContractProofPassed": output_contract["passed"],
        "fileWritingEnabled": output_contract["fileWritingEnabled"],
        "recordingExecutionEnabled": output_contract["recordingExecutionEnabled"],
        "writeReadbackPassed": output_contract["writeReadbackPassed"],
        "profileLogConsistencyPassed": output_contract["profileLogConsistencyPassed"],
        "twoProfileLogConsistencyPassed": output_contract["twoProfileLogConsistencyPassed"],
        "staleRecordingStudioModelAbsent": stale_recording_studio_model_absent,
        "visualSourceContractPassed": not visual_source_failures,
        "visualSourceContractFailures": visual_source_failures,
    }
    proof["productCheckPassed"] = all(proof[key] for key in (
        "allSourceChecksPassed", "outputContractProofPassed", "fileWritingEnabled",
        "recordingExecutionEnabled", "writeReadbackPassed", "profileLogConsistencyPassed",
        "twoProfileLogConsistencyPassed", "staleRecordingStudioModelAbsent", "visualSourceContractPassed",
    ))
    return deepcopy(proof)


def main() -> int:
    proof = build_recording_contract_proof()
    print(json.dumps(proof, indent=2, sort_keys=True))
    if proof["productCheckPassed"]:
        print("PASS: recording product contracts passed")
        return 0
    print("FAIL: recording product contracts failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
