"""Runtime output contract for active-overlay recording logs.

The contract owns the native NDAI log shape, safe runtime output root, atomic
write, and readback proof for Dashboard Recording Start/Stop. User-facing export
formats such as CSV are separate from the normal product save flow.
"""

from __future__ import annotations

import csv
import datetime as _dt
import io
import json
import os
import re
from pathlib import Path
from typing import Any


RECORDING_OUTPUT_CONTRACT_VERSION = 5
RECORDING_OUTPUT_CONTRACT_ID = "slc-054-active-overlay-recording-output-contract"
RECORDING_OUTPUT_FORMAT = "ndai-native-recording-log"
RECORDING_OUTPUT_EXTENSION = ".ndailog"
RECORDING_OUTPUT_ENV = "NEXUS_MONITORING_HUD_RECORDING_OUTPUT_DIR"
RECORDING_EXPORT_ENV = "NEXUS_MONITORING_HUD_RECORDING_EXPORT_DIR"
RECORDING_OUTPUT_DIR_NAME = "Recordings"
RECORDING_EXPORT_DIR_NAME = "Exported Logs"
RECORDING_OUTPUT_INTERNAL_PATH_TERMS = (
    "fam-006",
    "fam006",
    "feature-fam-006",
    "feature_fam_006",
    "worktrees",
    "nexus governance state",
)
RECORDING_OUTPUT_HEADERS = (
    "timestamp_utc",
    "elapsed_ms",
    "overlay_profile_id",
    "overlay_profile_name",
    "monitor_id",
    "monitor_name",
    "sensor_id",
    "sensor_label",
    "value",
    "unit",
    "quality",
    "source_state",
)


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _safe_token(value: Any, fallback: str = "recording") -> str:
    token = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip()).strip("-._")
    return token[:80] or fallback


def recording_output_dir() -> Path:
    override = os.environ.get(RECORDING_OUTPUT_ENV, "").strip()
    if override:
        return Path(override)
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        return Path(local_app_data) / "Nexus Desktop AI" / RECORDING_OUTPUT_DIR_NAME
    return Path.home() / "AppData" / "Local" / "Nexus Desktop AI" / RECORDING_OUTPUT_DIR_NAME


def recording_export_dir() -> Path:
    override = os.environ.get(RECORDING_EXPORT_ENV, "").strip()
    if override:
        return Path(override)
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        return Path(local_app_data) / "Nexus Desktop AI" / RECORDING_EXPORT_DIR_NAME
    return Path.home() / "AppData" / "Local" / "Nexus Desktop AI" / RECORDING_EXPORT_DIR_NAME


def _path_has_internal_user_visible_segment(path_value: str | Path) -> bool:
    normalized = str(path_value or "").replace("\\", "/").casefold()
    return any(term in normalized for term in RECORDING_OUTPUT_INTERNAL_PATH_TERMS)


def recording_output_contract() -> dict[str, Any]:
    return {
        "contractId": RECORDING_OUTPUT_CONTRACT_ID,
        "schemaVersion": RECORDING_OUTPUT_CONTRACT_VERSION,
        "format": RECORDING_OUTPUT_FORMAT,
        "extension": RECORDING_OUTPUT_EXTENSION,
        "headers": list(RECORDING_OUTPUT_HEADERS),
        "timestampColumn": "timestamp_utc",
        "xAxisCandidates": ["timestamp_utc", "elapsed_ms"],
        "seriesIdentityColumns": ["monitor_id", "sensor_id"],
        "valueColumn": "value",
        "unitColumn": "unit",
        "qualityColumn": "quality",
        "graphPlotReady": True,
        "recordingExecutionState": "enabled",
        "fileWritingState": "enabled",
        "startStopState": "dashboard-card-enabled",
        "outputRootOwner": "runtime-local-app-data",
        "outputRoot": str(recording_output_dir()),
        "exportRootOwner": "user-requested-export-folder",
        "exportRoot": str(recording_export_dir()),
        "userVisibleStorageModel": "flat-user-recording-and-export-roots",
        "nativeRootFolderName": RECORDING_OUTPUT_DIR_NAME,
        "exportRootFolderName": RECORDING_EXPORT_DIR_NAME,
        "surfaceChildFolderState": "not-used",
        "internalPathLeakageAbsent": not (
            _path_has_internal_user_visible_segment(recording_output_dir())
            or _path_has_internal_user_visible_segment(recording_export_dir())
        ),
        "normalProductSaveCreatesExport": False,
        "csvExportState": "future-user-export-only",
        "nativeLogLoaderState": "future-separate-viewer",
        "exportShareState": "future-gated",
    }


def build_recording_output_payload(
    *,
    active_overlay_profile_id: str,
    active_overlay_profile_name: str,
    target_monitor_ids: list[str],
    target_state: str,
    session_id: str = "",
    started_at_utc: str = "",
    stopped_at_utc: str = "",
    snapshot_mode: str = "snapshot-at-recording-start",
) -> dict[str, Any]:
    monitor_ids = [str(monitor_id) for monitor_id in target_monitor_ids if str(monitor_id).strip()]
    return {
        "contractId": RECORDING_OUTPUT_CONTRACT_ID,
        "schemaVersion": RECORDING_OUTPUT_CONTRACT_VERSION,
        "format": RECORDING_OUTPUT_FORMAT,
        "fileExtension": RECORDING_OUTPUT_EXTENSION,
        "sessionId": str(session_id or ""),
        "activeOverlayProfileId": str(active_overlay_profile_id or ""),
        "activeOverlayProfileName": str(active_overlay_profile_name or ""),
        "targetMonitorIds": monitor_ids,
        "targetMonitorCount": len(monitor_ids),
        "targetState": str(target_state or "unknown"),
        "snapshotMode": snapshot_mode,
        "startedAtUtc": str(started_at_utc or ""),
        "stoppedAtUtc": str(stopped_at_utc or ""),
        "finalizedAtUtc": _utc_now_iso(),
        "recordingExecutionState": "saved-complete",
        "fileWritingState": "saved-complete",
        "nativeLogReadableOnlyByNDAI": True,
        "nativeLogLoaderState": "future-separate-viewer",
        "exportShareState": "future-gated",
    }


def normalize_recording_output_row(row: dict[str, Any]) -> dict[str, str]:
    normalized = {header: "" for header in RECORDING_OUTPUT_HEADERS}
    for header in RECORDING_OUTPUT_HEADERS:
        value = row.get(header, "")
        normalized[header] = "" if value is None else str(value)
    return normalized


def build_recording_output_rows(samples: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = [normalize_recording_output_row(sample) for sample in samples]
    rows.sort(
        key=lambda row: (
            row["timestamp_utc"],
            row["elapsed_ms"].zfill(16),
            row["monitor_id"],
            row["sensor_id"],
        )
    )
    return rows


def render_recording_output_csv(rows: list[dict[str, Any]]) -> str:
    normalized_rows = build_recording_output_rows(rows)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(RECORDING_OUTPUT_HEADERS), lineterminator="\n")
    writer.writeheader()
    writer.writerows(normalized_rows)
    return buffer.getvalue()


def parse_recording_output_csv(csv_text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(csv_text or ""))
    if tuple(reader.fieldnames or ()) != RECORDING_OUTPUT_HEADERS:
        raise ValueError("Recording output CSV headers do not match the SLC-054 contract")
    return [normalize_recording_output_row(row) for row in reader]


def readback_recording_output_files(native_log_path: str | Path, manifest_path: str | Path | None = None) -> dict[str, Any]:
    payload = json.loads(Path(native_log_path).read_text(encoding="utf-8"))
    rows = [normalize_recording_output_row(row) for row in payload.get("rows", []) if isinstance(row, dict)]
    expected_profile_id = str(payload.get("activeOverlayProfileId") or "")
    expected_profile_name = str(payload.get("activeOverlayProfileName") or "")
    expected_monitor_ids = sorted({str(monitor_id) for monitor_id in payload.get("targetMonitorIds", []) if str(monitor_id).strip()})
    row_profile_ids = sorted({row["overlay_profile_id"] for row in rows if row["overlay_profile_id"].strip()})
    row_profile_names = sorted({row["overlay_profile_name"] for row in rows if row["overlay_profile_name"].strip()})
    row_monitor_ids = sorted({row["monitor_id"] for row in rows if row["monitor_id"].strip()})
    profile_log_consistency_passed = (
        bool(rows)
        and row_profile_ids == ([expected_profile_id] if expected_profile_id else [])
        and row_profile_names == ([expected_profile_name] if expected_profile_name else [])
        and row_monitor_ids == expected_monitor_ids
    )
    profile_log_consistency_reason = "profile-and-monitor-rows-match-target-snapshot"
    if not profile_log_consistency_passed:
        profile_log_consistency_reason = (
            "profile/log mismatch: expected "
            f"profileId={expected_profile_id!r}, profileName={expected_profile_name!r}, "
            f"monitorIds={expected_monitor_ids!r}; observed "
            f"profileIds={row_profile_ids!r}, profileNames={row_profile_names!r}, "
            f"monitorIds={row_monitor_ids!r}"
        )
    return {
        "passed": (
            bool(rows)
            and payload.get("contractId") == RECORDING_OUTPUT_CONTRACT_ID
            and payload.get("format") == RECORDING_OUTPUT_FORMAT
            and payload.get("nativeLogReadableOnlyByNDAI") is True
            and profile_log_consistency_passed
        ),
        "rowCount": len(rows),
        "profileLogConsistencyPassed": profile_log_consistency_passed,
        "profileLogConsistencyReason": profile_log_consistency_reason,
        "expectedProfileId": expected_profile_id,
        "expectedProfileName": expected_profile_name,
        "targetMonitorIds": expected_monitor_ids,
        "rowProfileIds": row_profile_ids,
        "rowProfileNames": row_profile_names,
        "rowMonitorIds": row_monitor_ids,
        "manifest": payload,
        "rows": rows,
    }


def write_recording_output_files(
    *,
    session_id: str,
    active_overlay_profile_id: str,
    active_overlay_profile_name: str,
    target_monitor_ids: list[str],
    target_state: str,
    samples: list[dict[str, Any]],
    started_at_utc: str = "",
    stopped_at_utc: str = "",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    rows = build_recording_output_rows(samples)
    if not rows:
        raise ValueError("Recording output requires at least one usable sample row")
    output_root = Path(output_dir) if output_dir is not None else recording_output_dir()
    output_root.mkdir(parents=True, exist_ok=True)
    export_root = recording_export_dir()
    safe_session = _safe_token(session_id, "recording-session")
    safe_profile = _safe_token(active_overlay_profile_name or active_overlay_profile_id, "overlay-profile")
    stem = f"{_safe_token(stopped_at_utc or _utc_now_iso(), 'recording-time')}_{safe_profile}_{safe_session}"
    native_log_path = output_root / f"{stem}{RECORDING_OUTPUT_EXTENSION}"
    payload = build_recording_output_payload(
        active_overlay_profile_id=active_overlay_profile_id,
        active_overlay_profile_name=active_overlay_profile_name,
        target_monitor_ids=target_monitor_ids,
        target_state=target_state,
        session_id=session_id,
        started_at_utc=started_at_utc,
        stopped_at_utc=stopped_at_utc,
    )
    payload["nativeLogPath"] = str(native_log_path)
    payload["rowCount"] = len(rows)
    payload["rows"] = rows
    tmp_path = native_log_path.with_suffix(native_log_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp_path, native_log_path)
    readback = readback_recording_output_files(native_log_path)
    return {
        "passed": bool(readback.get("passed")),
        "sessionId": str(session_id or ""),
        "outputDir": str(output_root),
        "nativeLogPath": str(native_log_path),
        "exportDir": str(export_root),
        "csvPath": "",
        "manifestPath": "",
        "normalProductSaveCreatesExport": False,
        "nativeLogReadableOnlyByNDAI": True,
        "rowCount": len(rows),
        "readbackPassed": bool(readback.get("passed")),
        "profileLogConsistencyPassed": bool(readback.get("profileLogConsistencyPassed")),
        "profileLogConsistencyReason": str(readback.get("profileLogConsistencyReason") or ""),
        "rowProfileIds": list(readback.get("rowProfileIds") or []),
        "rowProfileNames": list(readback.get("rowProfileNames") or []),
        "rowMonitorIds": list(readback.get("rowMonitorIds") or []),
        "targetMonitorIds": list(readback.get("targetMonitorIds") or []),
        "fileWritingState": "saved-complete",
        "recordingExecutionState": "saved-complete",
        "outputRootOwner": "runtime-local-app-data",
    }
