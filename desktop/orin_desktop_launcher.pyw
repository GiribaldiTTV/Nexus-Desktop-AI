# Version 1.3.2 rev 11 launcher

import os
import sys
import time
import re
import json
import shutil
import subprocess
import datetime
import platform
import secrets
import ctypes
from ctypes import wintypes

from single_instance import (
    NamedSignal,
    SingleInstanceGuard,
    acquire_or_prompt_replace,
    show_already_running_dialog,
)
from renderer_backend import (
    RENDERER_BACKEND_CLASSIFICATION,
    RENDERER_BACKEND_POLICY,
    WEBENGINE_SOFTWARE_COMPOSITOR_FLAG,
    build_renderer_environment,
)


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TARGET_SCRIPT = os.path.join(ROOT_DIR, "desktop", "orin_desktop_main.py")
DEFAULT_LOG_DIR = os.path.join(ROOT_DIR, "logs")
TARGET_SCRIPT = DEFAULT_TARGET_SCRIPT
LOG_DIR = DEFAULT_LOG_DIR
CRASH_DIR = os.path.join(LOG_DIR, "crash")
STATUS_FILE = os.path.join(LOG_DIR, "diagnostics_status.txt")
STOP_SIGNAL_FILE = os.path.join(LOG_DIR, "diagnostics_stop.signal")
STARTUP_ABORT_SIGNAL_FILE = os.path.join(LOG_DIR, "renderer_startup_abort.signal")
DESKTOP_SETTLED_SIGNAL_FILE = os.path.join(LOG_DIR, "desktop_settled.signal")
ACTIVE_RUNTIME_OWNER_FILE = os.path.join(LOG_DIR, "active_runtime_owner.json")
DIAGNOSTICS_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orin_diagnostics.pyw")
VOICE_SCRIPT = os.path.join(ROOT_DIR, "Audio", "orin_error_voice.py")
RUNTIME_INSTANCE_MUTEX = r"Local\NexusRuntimeSingletonV1"
RUNTIME_RELAUNCH_EVENT = r"Local\NexusRuntimeRelaunchRequestV1"
RUNTIME_DESKTOP_SETTLED_EVENT = r"Local\NexusRuntimeDesktopSettledV1"
runtime_instance_guard = SingleInstanceGuard(RUNTIME_INSTANCE_MUTEX)
runtime_relaunch_signal = NamedSignal(RUNTIME_RELAUNCH_EVENT)
runtime_desktop_settled_signal = NamedSignal(RUNTIME_DESKTOP_SETTLED_EVENT)

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE
CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

MAX_RECOVERY_ATTEMPTS = 3
RECOVERY_COOLDOWN_SECONDS = 1.2
COMPLETE_CLEANUP_DELAY_SECONDS = 0.35
STARTUP_OBSERVE_POLL_SECONDS = 0.05
STARTUP_READY_OBSERVE_WINDOW_SECONDS = 3.0
STARTUP_READY_STALL_CONFIRM_SECONDS = 8.0
STARTUP_ABORT_CONTROL_FLOW_RESULT = "STARTUP_ABORT"
CONSECUTIVE_STARTUP_ABORT_THRESHOLD = 2
CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD = 2
AUTHORITATIVE_DESKTOP_SETTLED_MARKER = "DESKTOP_OUTCOME|SETTLED|state=dormant"
HISTORY_SCHEMA_VERSION = 1
HISTORY_STABILITY_WINDOW_SIZE = 5
HISTORY_FILENAME = "nexus_history_v1.jsonl"
HISTORY_STATE_DIRNAME = "Nexus Desktop AI"
HISTORY_STATE_SUBDIR = "state"
ADVISORY_CONFIDENCE_DIRECT_EVIDENCE = "direct_evidence"
ADVISORY_CONFIDENCE_PATTERN_EVIDENCE = "pattern_evidence"

os.makedirs(LOG_DIR, exist_ok=True)

RUN_ID_STEM = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(2).upper()}"

RUNTIME_FILE = os.path.join(
    LOG_DIR,
    f"Runtime_{RUN_ID_STEM}.txt"
)


def environment_fingerprint():
    os_parts = [part for part in (platform.system(), platform.release(), platform.version()) if part]
    os_label = "-".join(os_parts) if os_parts else "Unknown-OS"
    arch_label = "64-bit" if sys.maxsize > 2 ** 32 else "32-bit"
    return f"Environment: {os_label} | {arch_label} | Python {platform.python_version()}"


ENVIRONMENT_FINGERPRINT = environment_fingerprint()


def create_run_id():
    return f"Run ID: {RUN_ID_STEM}"


def strip_label_prefix(value, prefix):
    text = (value or "").strip()
    if text.startswith(prefix):
        return text[len(prefix):].strip()
    return text


def normalize_policy_value(value, prefix=""):
    text = strip_label_prefix(value, prefix)
    return " ".join(text.split()).casefold()


def format_historical_context_line(message):
    return f"Historical context (derived from prior finalized recorded history only): {message}"


def format_advisory_inference_line(message):
    return (
        "Advisory inference (derived from prior finalized history, non-binding, non-authoritative): "
        f"{message}"
    )


def build_failure_fingerprint_parts(final_classification, failure_cause="", failure_origin=""):
    parts = []
    normalized_classification = normalize_policy_value(final_classification)
    normalized_cause = normalize_policy_value(failure_cause)
    normalized_origin = normalize_policy_value(failure_origin, "Failure origin: ")

    if normalized_classification:
        parts.append(("classification", normalized_classification))
    if normalized_cause:
        parts.append(("cause", normalized_cause))
    if normalized_origin:
        parts.append(("origin", normalized_origin))

    return parts


def normalize_failure_fingerprint_text(failure_fingerprint):
    text = (failure_fingerprint or "").strip()
    if not text:
        return ""

    normalized_parts = []
    for raw_part in text.split("|"):
        part = raw_part.strip()
        if not part or "=" not in part:
            return ""

        key, raw_value = part.split("=", 1)
        normalized_key = " ".join(key.split()).casefold()
        normalized_value = normalize_policy_value(raw_value)
        if not normalized_key or not normalized_value:
            return ""

        normalized_parts.append(f"{normalized_key}={normalized_value}")

    return "|".join(normalized_parts)


def recurrence_eligible_history_record(record):
    if not isinstance(record, dict):
        return False
    if (record.get("final_outcome") or "").strip() != "FAILURE":
        return False
    return bool(normalize_failure_fingerprint_text(record.get("failure_fingerprint")))


def repeated_identical_crash(previous_cause, previous_origin, current_cause, current_origin):
    if not previous_cause or not current_cause:
        return False
    if previous_cause != current_cause:
        return False
    if previous_origin and current_origin and previous_origin != current_origin:
        return False
    return True


def classify_mixed_failure_pattern(previous_kind, previous_cause, previous_origin, current_kind, current_cause, current_origin):
    if not previous_kind or not current_kind:
        return ""
    if previous_kind == STARTUP_ABORT_CONTROL_FLOW_RESULT and current_kind == "CRASH":
        return "STARTUP_ABORT_TO_CRASH"
    if previous_kind == "CRASH" and current_kind == STARTUP_ABORT_CONTROL_FLOW_RESULT:
        return "CRASH_TO_STARTUP_ABORT"
    if (
        previous_kind == "CRASH"
        and current_kind == "CRASH"
        and previous_cause
        and current_cause
        and previous_cause != current_cause
    ):
        return "CRASH_TO_DIFFERENT_CRASH"
    return ""


def build_incident_summary_lines(
    run_id,
    attempts_used,
    last_code,
    failure_cause="",
    failure_origin="",
    failure_assessment="",
    recovery_outcome="",
    attempt_pattern="",
    diagnostics_priority="",
    failure_stability="",
    triage_guidance="",
    crash_filename="",
    runtime_filename="",
):
    lines = [
        "INCIDENT SUMMARY",
        f"Run ID: {strip_label_prefix(run_id, 'Run ID: ') or 'Unavailable'}",
        f"Environment: {strip_label_prefix(ENVIRONMENT_FINGERPRINT, 'Environment: ') or 'Unavailable'}",
        f"Renderer: {os.path.basename(TARGET_SCRIPT) or 'Unavailable'}",
        f"Attempts Used: {attempts_used}",
        f"Last Exit Code: {last_code}",
        f"Failure Cause: {(failure_cause or '').strip() or 'Unavailable'}",
        f"Failure Origin: {strip_label_prefix(failure_origin, 'Failure origin: ') or 'Unavailable'}",
        f"Assessment: {strip_label_prefix(failure_assessment, 'Assessment: ') or 'Unavailable'}",
        f"Recovery Outcome: {(recovery_outcome or '').strip() or 'Unavailable'}",
        f"Attempt Pattern: {(attempt_pattern or '').strip() or 'Unavailable'}",
    ]
    if diagnostics_priority:
        lines.append(f"Diagnostics Priority: {diagnostics_priority.strip()}")
    if failure_stability:
        lines.append(f"Failure Stability: {failure_stability.strip()}")
    if triage_guidance:
        lines.append(f"Triage Guidance: {strip_label_prefix(triage_guidance, 'Triage: ') or 'Unavailable'}")
    lines.extend([
        f"Latest crash report: {(crash_filename or '').strip() or 'Unavailable'}",
        f"Latest runtime log: {(runtime_filename or '').strip() or 'Unavailable'}",
    ])
    return lines


def select_recovery_outcome(recovery_pipeline_end_reason, failure_causes):
    if recovery_pipeline_end_reason == "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED":
        return "Automatic recovery stopped after repeated startup aborts reached the launcher escalation threshold."
    if recovery_pipeline_end_reason == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED":
        return "Automatic recovery stopped after repeated identical crash outcomes reached the launcher escalation threshold."
    if (
        len(failure_causes) == MAX_RECOVERY_ATTEMPTS
        and all(failure_causes)
        and len(set(failure_causes)) == 1
    ):
        return "Automatic recovery did not change the underlying renderer failure."
    return "Automatic recovery completed without resolving the renderer failure."


def select_terminal_failure_message(recovery_pipeline_end_reason):
    if recovery_pipeline_end_reason == "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED":
        return "Renderer failed after repeated startup aborts reached the launcher escalation threshold."
    if recovery_pipeline_end_reason == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED":
        return "Renderer failed after repeated identical crash outcomes reached the launcher escalation threshold."
    return "Renderer failed after maximum recovery attempts."


def stable_max_attempt_identical_failure(failure_kinds, failure_causes):
    non_empty_kinds = [kind for kind in failure_kinds if kind]
    non_empty_causes = [cause for cause in failure_causes if cause]
    return (
        len(non_empty_kinds) == MAX_RECOVERY_ATTEMPTS
        and len(non_empty_causes) == MAX_RECOVERY_ATTEMPTS
        and set(non_empty_kinds) == {"CRASH"}
        and len(set(non_empty_causes)) == 1
    )


def select_attempt_pattern(recovery_pipeline_end_reason, mixed_failure_pattern_logged, failure_kinds, failure_causes):
    if recovery_pipeline_end_reason == "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED":
        return "repeated startup aborts"
    if recovery_pipeline_end_reason == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED":
        return "repeated identical crash"
    if stable_max_attempt_identical_failure(failure_kinds, failure_causes):
        return "repeated identical failure across recovery attempts"
    if mixed_failure_pattern_logged:
        return "mixed failure sequence observed"
    non_empty_kinds = [kind for kind in failure_kinds if kind]
    non_empty_causes = [cause for cause in failure_causes if cause]
    if len(set(non_empty_kinds)) > 1 or len(set(non_empty_causes)) > 1:
        return "varied failure outcomes across recovery attempts"
    return "varied failure outcomes across recovery attempts"


def select_failure_stability(mixed_failure_pattern_logged, failure_kinds, failure_causes):
    if stable_max_attempt_identical_failure(failure_kinds, failure_causes):
        return ""
    non_empty_kinds = [kind for kind in failure_kinds if kind]
    non_empty_causes = [cause for cause in failure_causes if cause]
    if mixed_failure_pattern_logged:
        return "unstable across recovery attempts"
    if len(set(non_empty_kinds)) > 1 or len(set(non_empty_causes)) > 1:
        return "unstable across recovery attempts"
    return ""


def select_diagnostics_priority(failure_stability):
    if (failure_stability or "").strip() == "unstable across recovery attempts":
        return "elevated attention due to unstable recovery pattern"
    return ""


def legacy_history_file_path(log_dir=DEFAULT_LOG_DIR):
    return os.path.join(os.path.abspath(log_dir), HISTORY_FILENAME)


def history_state_root(local_app_data=None, home_dir=None):
    resolved_local_app_data = local_app_data
    if resolved_local_app_data is None:
        resolved_local_app_data = os.environ.get("LOCALAPPDATA", "")
    resolved_local_app_data = resolved_local_app_data.strip()
    if resolved_local_app_data:
        return os.path.join(
            os.path.abspath(resolved_local_app_data),
            HISTORY_STATE_DIRNAME,
            HISTORY_STATE_SUBDIR,
        )

    resolved_home_dir = home_dir
    if resolved_home_dir is None:
        resolved_home_dir = os.path.expanduser("~")
    resolved_home_dir = resolved_home_dir.strip()
    if resolved_home_dir:
        return os.path.join(
            os.path.abspath(resolved_home_dir),
            "AppData",
            "Local",
            HISTORY_STATE_DIRNAME,
            HISTORY_STATE_SUBDIR,
        )

    raise ValueError("No launcher-owned state root is available for historical memory storage.")


def history_file(local_app_data=None, home_dir=None):
    state_root = history_state_root(
        local_app_data=local_app_data,
        home_dir=home_dir,
    )
    return os.path.join(state_root, HISTORY_FILENAME)


def migrate_history_file_if_needed(target_path, legacy_path):
    resolved_target_path = os.path.abspath(target_path)
    resolved_legacy_path = os.path.abspath(legacy_path)

    if resolved_target_path == resolved_legacy_path:
        return
    if os.path.exists(resolved_target_path):
        return
    if not os.path.isfile(resolved_legacy_path):
        return

    target_parent_dir = os.path.dirname(resolved_target_path)
    if not target_parent_dir:
        raise ValueError("Historical state target path has no parent directory.")
    os.makedirs(target_parent_dir, exist_ok=True)

    migration_temp_path = resolved_target_path + ".migrating"
    if os.path.exists(migration_temp_path):
        if os.path.isfile(migration_temp_path):
            os.remove(migration_temp_path)
        else:
            raise IsADirectoryError(f"Historical state migration temp path is a directory: {migration_temp_path}")

    target_created = False
    try:
        shutil.copy2(resolved_legacy_path, migration_temp_path)
        os.replace(migration_temp_path, resolved_target_path)
        target_created = True
        os.remove(resolved_legacy_path)
    except Exception:
        if os.path.isfile(migration_temp_path):
            try:
                os.remove(migration_temp_path)
            except Exception:
                pass
        if target_created and os.path.isfile(resolved_target_path) and os.path.isfile(resolved_legacy_path):
            try:
                os.remove(resolved_target_path)
            except Exception:
                pass
        raise


def history_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_history_run_id(run_id):
    return strip_label_prefix(run_id, "Run ID: ") or RUN_ID_STEM


def prepare_history_storage_path(path=None, legacy_path=None):
    path = os.path.abspath(path or history_file())
    parent_dir = os.path.dirname(path)
    if not parent_dir:
        raise ValueError("History storage path has no parent directory.")

    resolved_legacy_path = legacy_path
    if resolved_legacy_path is None:
        resolved_legacy_path = legacy_history_file_path()

    migrate_history_file_if_needed(path, resolved_legacy_path)
    os.makedirs(parent_dir, exist_ok=True)
    if os.path.isdir(path):
        raise IsADirectoryError(f"History storage path is a directory: {path}")
    return path


def validate_history_record(record):
    if not isinstance(record, dict):
        return "History record payload must be a dictionary."

    required_string_fields = (
        "run_id",
        "recorded_at",
        "final_outcome",
        "final_classification",
        "end_reason",
        "attempt_pattern",
        "failure_stability",
        "diagnostics_priority",
        "failure_fingerprint",
        "provenance",
    )

    if record.get("schema_version") != HISTORY_SCHEMA_VERSION:
        return f"History record schema_version must be {HISTORY_SCHEMA_VERSION}."

    attempt_count = record.get("attempt_count")
    if not isinstance(attempt_count, int) or attempt_count < 1:
        return "History record attempt_count must be a positive integer."

    if record.get("final_outcome") not in {"SUCCESS", "FAILURE"}:
        return "History record final_outcome must be SUCCESS or FAILURE."

    normalized_failure_fingerprint = normalize_failure_fingerprint_text(record.get("failure_fingerprint"))
    if record.get("final_outcome") == "SUCCESS" and record.get("failure_fingerprint", "").strip():
        return "History record failure_fingerprint must be empty for SUCCESS."
    if record.get("final_outcome") == "FAILURE" and not normalized_failure_fingerprint:
        return "History record failure_fingerprint must be a non-empty normalized fingerprint for FAILURE."
    if normalized_failure_fingerprint and record.get("failure_fingerprint") != normalized_failure_fingerprint:
        return "History record failure_fingerprint must already be normalized."

    for field_name in required_string_fields:
        field_value = record.get(field_name)
        if not isinstance(field_value, str):
            return f"History record field {field_name} must be a string."
        if field_name in {"run_id", "recorded_at", "final_outcome", "final_classification", "end_reason", "provenance"} and not field_value.strip():
            return f"History record field {field_name} must not be empty."

    if record.get("provenance") != "derived_from_finalized_v1.6.0_truth_surfaces":
        return "History record provenance marker is invalid."

    return ""


def load_history_records():
    try:
        history_path = prepare_history_storage_path()
        if not os.path.exists(history_path):
            return []
        if os.path.isdir(history_path):
            return []

        records = []
        with open(history_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except Exception:
                    continue

                validation_error = validate_history_record(record)
                if validation_error:
                    continue

                records.append(record)

        return records
    except Exception:
        return []


def count_history_recurrence(records, failure_fingerprint):
    fingerprint = normalize_failure_fingerprint_text(failure_fingerprint)
    if not fingerprint:
        return 0
    return sum(
        1
        for record in records
        if recurrence_eligible_history_record(record)
        and normalize_failure_fingerprint_text(record.get("failure_fingerprint")) == fingerprint
    )


def characterize_history_stability(records):
    recent_records = [
        record
        for record in records
        if recurrence_eligible_history_record(record)
    ][-HISTORY_STABILITY_WINDOW_SIZE:]

    if not recent_records:
        return "stable"

    recent_fingerprints = {
        normalize_failure_fingerprint_text(record.get("failure_fingerprint"))
        for record in recent_records
        if recurrence_eligible_history_record(record)
    }

    if len(recent_fingerprints) <= 1:
        return "stable"
    return "varied"


def summarize_loaded_history(records):
    if not records:
        return {
            "history_loaded": False,
            "history_record_count": 0,
            "latest_failure_recurrence": 0,
            "recent_history_stability": "stable",
        }

    latest_record = records[-1]
    latest_failure_fingerprint = ""
    if recurrence_eligible_history_record(latest_record):
        latest_failure_fingerprint = normalize_failure_fingerprint_text(latest_record.get("failure_fingerprint"))

    return {
        "history_loaded": True,
        "history_record_count": len(records),
        "latest_failure_recurrence": count_history_recurrence(records, latest_failure_fingerprint),
        "recent_history_stability": characterize_history_stability(records),
    }


def summarize_prior_history_for_diagnostics(records, current_failure_fingerprint):
    relevant_failure_records = [
        record
        for record in records
        if recurrence_eligible_history_record(record)
    ]

    if not relevant_failure_records:
        return {
            "history_loaded": False,
            "matching_failure_recurrence": 0,
            "recent_history_stability": "stable",
        }

    return {
        "history_loaded": True,
        "matching_failure_recurrence": count_history_recurrence(relevant_failure_records, current_failure_fingerprint),
        "recent_history_stability": characterize_history_stability(relevant_failure_records),
    }


def build_historical_advisory_inference(prior_history_context):
    if not prior_history_context.get("history_loaded"):
        return {}

    matching_failure_recurrence = int(prior_history_context.get("matching_failure_recurrence", 0) or 0)
    if matching_failure_recurrence > 0:
        return {
            "message": (
                f"this finalized failure fingerprint has appeared in {matching_failure_recurrence} "
                "prior finalized failed run(s)."
            ),
            "confidence": ADVISORY_CONFIDENCE_DIRECT_EVIDENCE,
        }

    if (prior_history_context.get("recent_history_stability") or "").strip() == "varied":
        return {
            "message": (
                "recent prior finalized failed runs have been varied, so this run appears within a changing "
                "failure history."
            ),
            "confidence": ADVISORY_CONFIDENCE_PATTERN_EVIDENCE,
        }

    return {}


def select_historical_advisory_hint(prior_history_context):
    advisory_inference = build_historical_advisory_inference(prior_history_context)
    if not advisory_inference:
        return ""
    return format_advisory_inference_line(advisory_inference["message"])


def build_failure_fingerprint(final_outcome, final_classification, failure_cause="", failure_origin=""):
    if final_outcome != "FAILURE":
        return ""

    return "|".join(
        f"{key}={value}"
        for key, value in build_failure_fingerprint_parts(
            final_classification,
            failure_cause,
            failure_origin,
        )
    )


def build_history_record(
    run_id,
    final_outcome,
    final_classification,
    end_reason,
    attempt_count,
    attempt_pattern="",
    failure_stability="",
    diagnostics_priority="",
    failure_cause="",
    failure_origin="",
):
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "run_id": normalize_history_run_id(run_id),
        "recorded_at": history_timestamp(),
        "final_outcome": (final_outcome or "").strip(),
        "final_classification": (final_classification or "").strip(),
        "end_reason": (end_reason or "").strip(),
        "attempt_count": int(attempt_count),
        "attempt_pattern": (attempt_pattern or "").strip(),
        "failure_stability": (failure_stability or "").strip(),
        "diagnostics_priority": (diagnostics_priority or "").strip(),
        "failure_fingerprint": build_failure_fingerprint(
            (final_outcome or "").strip(),
            (final_classification or "").strip(),
            failure_cause,
            failure_origin,
        ),
        "provenance": "derived_from_finalized_v1.6.0_truth_surfaces",
    }


def record_finalized_history(
    run_id,
    final_outcome,
    final_classification,
    end_reason,
    attempt_count,
    attempt_pattern="",
    failure_stability="",
    diagnostics_priority="",
    failure_cause="",
    failure_origin="",
):
    record = build_history_record(
        run_id,
        final_outcome,
        final_classification,
        end_reason,
        attempt_count,
        attempt_pattern,
        failure_stability,
        diagnostics_priority,
        failure_cause,
        failure_origin,
    )

    try:
        validation_error = validate_history_record(record)
        if validation_error:
            runtime(f"Historical recorder skipped invalid finalized record; continuing without history: {validation_error}")
            return False

        history_path = prepare_history_storage_path()
        serialized_record = json.dumps(record, sort_keys=True)
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(serialized_record + "\n")
        _ = summarize_loaded_history(load_history_records())
        runtime(f"Historical recorder wrote finalized run record: {os.path.basename(history_path)}")
        return True
    except Exception as exc:
        runtime(f"Historical recorder failed; continuing without history: {exc}")
        return False


def write_runtime_incident_summary(
    run_id,
    attempts_used,
    last_code,
    failure_cause="",
    failure_origin="",
    failure_assessment="",
    recovery_outcome="",
    attempt_pattern="",
    diagnostics_priority="",
    failure_stability="",
    triage_guidance="",
    crash_filename="",
    runtime_filename="",
):
    for line in build_incident_summary_lines(
        run_id,
        attempts_used,
        last_code,
        failure_cause,
        failure_origin,
        failure_assessment,
        recovery_outcome,
        attempt_pattern,
        diagnostics_priority,
        failure_stability,
        triage_guidance,
        crash_filename,
        runtime_filename,
    ):
        runtime(line)


def pythonw():
    exe = sys.executable
    alt = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return alt if os.path.exists(alt) else exe


def hidden_window_kwargs():
    if os.name != "nt":
        return {}

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0

    return {
        "startupinfo": startupinfo,
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
    }


def runtime(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    with open(RUNTIME_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def runtime_event(category, *parts):
    payload = "|".join(str(part) for part in parts)
    runtime(f"{category}|{payload}" if payload else category)


def ensure_crash_dir(reason):
    try:
        os.makedirs(CRASH_DIR, exist_ok=True)
        runtime(f"Crash directory ready ({reason}): {CRASH_DIR}")
        runtime_event("FILE", "ENSURE_DIR", os.path.basename(CRASH_DIR), "SUCCESS", reason)
        return True
    except Exception as exc:
        runtime(f"Crash directory ensure failed ({reason}): {CRASH_DIR} :: {exc}")
        runtime_event("FILE", "ENSURE_DIR", os.path.basename(CRASH_DIR), "FAILED", reason, exc)
        return False


def reset_status():
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write("")
    runtime(f"Reset diagnostics status file: {STATUS_FILE}")
    runtime_event("FILE", "CREATE_OR_RESET", os.path.basename(STATUS_FILE), "SUCCESS", "startup")
    delete_file(STOP_SIGNAL_FILE, "startup reset")
    delete_file(STARTUP_ABORT_SIGNAL_FILE, "startup reset")


def write_status(kind, msg):
    with open(STATUS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{kind}|{msg}\n")
    runtime(f"STATUS WRITE: {kind}|{msg}")
    runtime_event("STATUS", kind, msg)


def latest_voice_diagnostic():
    try:
        with open(STATUS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in reversed(f.read().splitlines()):
                if line.startswith("VOICE_DIAGNOSTIC|"):
                    return line.split("|", 1)[1]
                if line.startswith("VOICE_CLEAR|"):
                    break
    except Exception:
        pass
    return ""


def write_state(state):
    write_status("STATE", state)
    runtime_event("PHASE", state)


def runtime_log_contains_since(pattern, start_offset=0):
    try:
        with open(RUNTIME_FILE, "r", encoding="utf-8", errors="ignore") as f:
            if start_offset > 0:
                f.seek(start_offset)
            return pattern in f.read()
    except Exception:
        return False


def write_desktop_settled_signal_file(reason):
    try:
        with open(DESKTOP_SETTLED_SIGNAL_FILE, "w", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now(datetime.timezone.utc).isoformat()}|{reason}\n")
        runtime_event("FILE", "CREATE_OR_RESET", os.path.basename(DESKTOP_SETTLED_SIGNAL_FILE), "SUCCESS", reason)
        return True
    except Exception as exc:
        runtime_event("FILE", "CREATE_OR_RESET", os.path.basename(DESKTOP_SETTLED_SIGNAL_FILE), "FAILED", reason, exc)
        return False


def write_active_runtime_owner_file(reason):
    try:
        with open(ACTIVE_RUNTIME_OWNER_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "runtime_file": RUNTIME_FILE,
                    "run_id": RUN_ID_STEM,
                    "launcher_pid": os.getpid(),
                    "launcher_script": os.path.abspath(__file__),
                    "launcher_root": os.path.abspath(ROOT_DIR),
                    "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "reason": reason,
                },
                f,
            )
        runtime_event("FILE", "CREATE_OR_RESET", os.path.basename(ACTIVE_RUNTIME_OWNER_FILE), "SUCCESS", reason)
        return True
    except Exception as exc:
        runtime_event("FILE", "CREATE_OR_RESET", os.path.basename(ACTIVE_RUNTIME_OWNER_FILE), "FAILED", reason, exc)
        return False


def read_active_runtime_owner():
    try:
        with open(ACTIVE_RUNTIME_OWNER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def process_is_running(pid):
    try:
        process_id = int(pid)
    except (TypeError, ValueError):
        return False
    if process_id <= 0:
        return False

    handle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
    if not handle:
        return False
    try:
        return True
    finally:
        CloseHandle(handle)


def process_command_line(pid):
    try:
        process_id = int(pid)
    except (TypeError, ValueError):
        return ""
    if process_id <= 0 or os.name != "nt":
        return ""

    script = (
        f"$process = Get-CimInstance Win32_Process -Filter \"ProcessId={process_id}\"; "
        "if ($process -and $process.CommandLine) { $process.CommandLine }"
    )
    kwargs = hidden_window_kwargs()
    kwargs.update(
        {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
        }
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            timeout=5,
            **kwargs,
        )
    except Exception:
        return ""
    return (result.stdout or "").strip()


def owner_process_identity_matches(owner, command_line):
    if not command_line:
        return False

    owner_script = os.path.abspath(str(owner.get("launcher_script") or os.path.join(ROOT_DIR, "desktop", "orin_desktop_launcher.pyw")))
    owner_root = os.path.abspath(str(owner.get("launcher_root") or ROOT_DIR))
    normalized_command = os.path.normcase(command_line)

    return (
        os.path.normcase(owner_script) in normalized_command
        and os.path.normcase(owner_root) in normalized_command
    )


def active_owner_matches_current(owner):
    runtime_file = os.path.abspath(str(owner.get("runtime_file") or ""))
    if runtime_file and runtime_file == os.path.abspath(RUNTIME_FILE):
        return True
    return str(owner.get("run_id") or "") == RUN_ID_STEM


def active_owner_is_live(owner):
    if not process_is_running(owner.get("launcher_pid")):
        return False

    command_line = process_command_line(owner.get("launcher_pid"))
    if owner_process_identity_matches(owner, command_line):
        return True

    runtime_event(
        "STATUS",
        "WARNING",
        "LAUNCHER_RUNTIME",
        "ACTIVE_RUNTIME_OWNER_PID_UNVERIFIED",
        active_owner_summary(owner),
    )
    return False




def active_owner_summary(owner):
    if not owner:
        return "owner=none"
    runtime_file = os.path.basename(str(owner.get("runtime_file") or "")) or "unknown_runtime"
    return (
        f"owner_run={owner.get('run_id') or 'unknown'}"
        f"|owner_pid={owner.get('launcher_pid') or 'unknown'}"
        f"|owner_runtime={runtime_file}"
    )


def live_active_owner_conflict():
    owner = read_active_runtime_owner()
    return bool(owner and not active_owner_matches_current(owner) and active_owner_is_live(owner)), owner


def clear_active_runtime_owner(reason, allow_foreign_stale=False):
    owner = read_active_runtime_owner()
    if owner and not active_owner_matches_current(owner):
        if active_owner_is_live(owner) or not allow_foreign_stale:
            runtime_event(
                "FILE",
                "DELETE",
                os.path.basename(ACTIVE_RUNTIME_OWNER_FILE),
                "SKIPPED_FOREIGN_OWNER",
                reason,
                active_owner_summary(owner),
            )
            return False

    delete_file(DESKTOP_SETTLED_SIGNAL_FILE, reason)
    delete_file(ACTIVE_RUNTIME_OWNER_FILE, reason)
    return True


def claim_active_runtime_owner_file(reason):
    conflict, owner = live_active_owner_conflict()
    if conflict:
        runtime_event(
            "STATUS",
            "WARNING",
            "LAUNCHER_RUNTIME",
            "ACTIVE_RUNTIME_OWNER_CONFLICT_DETECTED",
            active_owner_summary(owner),
        )
        return False

    clear_active_runtime_owner(reason, allow_foreign_stale=True)
    return write_active_runtime_owner_file(reason)


def active_owner_runtime_log_contains(pattern):
    try:
        owner = read_active_runtime_owner()
        runtime_file = os.path.abspath(str(owner.get("runtime_file") or ""))
        if not runtime_file:
            return False
        if not runtime_file.startswith(os.path.abspath(LOG_DIR) + os.sep):
            return False
        if not os.path.isfile(runtime_file):
            return False
        with open(runtime_file, "r", encoding="utf-8", errors="ignore") as f:
            return pattern in f.read()
    except Exception:
        return False


def active_desktop_settled_signal_present():
    return os.path.isfile(DESKTOP_SETTLED_SIGNAL_FILE) or active_owner_runtime_log_contains(
        AUTHORITATIVE_DESKTOP_SETTLED_MARKER
    )


def observe_authoritative_desktop_settled(proc, log_start_offset):
    settled_marker = AUTHORITATIVE_DESKTOP_SETTLED_MARKER
    startup_abort_marker = "RENDERER_MAIN|STARTUP_ABORTED"
    warn_deadline = time.monotonic() + STARTUP_READY_OBSERVE_WINDOW_SECONDS
    stall_deadline = time.monotonic() + STARTUP_READY_STALL_CONFIRM_SECONDS
    warned_within_window = False
    stall_confirmed = False
    abort_requested_on_stall = False

    runtime_event("STATUS", "TRACE", "LAUNCHER_RUNTIME", "STARTUP_OBSERVE_BEGIN")

    while True:
        if runtime_log_contains_since(settled_marker, log_start_offset):
            runtime_desktop_settled_signal.signal()
            write_desktop_settled_signal_file("launcher observed authoritative settled")
            runtime_event(
                "STATUS",
                "SUCCESS",
                "LAUNCHER_RUNTIME",
                "DESKTOP_SETTLED_OBSERVED|state=dormant",
            )
            return "settled", None, None

        if runtime_log_contains_since(startup_abort_marker, log_start_offset):
            runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_ABORT_OBSERVED")
            return "startup_aborted", None, None

        if (
            not warned_within_window
            and time.monotonic() >= warn_deadline
            and proc.poll() is None
        ):
            runtime_event(
                "STATUS",
                "WARNING",
                "LAUNCHER_RUNTIME",
                "DESKTOP_SETTLED_NOT_OBSERVED_WITHIN_WINDOW",
            )
            warned_within_window = True

        if (
            not stall_confirmed
            and time.monotonic() >= stall_deadline
            and proc.poll() is None
        ):
            runtime_event(
                "STATUS",
                "WARNING",
                "LAUNCHER_RUNTIME",
                "DESKTOP_SETTLED_STALL_CONFIRMED",
            )
            stall_confirmed = True
            if not abort_requested_on_stall and not runtime_log_contains_since(settled_marker, log_start_offset):
                if request_startup_abort("confirmed stall"):
                    runtime_event(
                        "STATUS",
                        "WARNING",
                        "LAUNCHER_RUNTIME",
                        "STARTUP_ABORT_REQUESTED_ON_CONFIRMED_SETTLED_STALL",
                    )
                    abort_requested_on_stall = True

        try:
            stdout_text, stderr_text = proc.communicate(timeout=STARTUP_OBSERVE_POLL_SECONDS)
            break
        except subprocess.TimeoutExpired:
            continue

    if runtime_log_contains_since(settled_marker, log_start_offset):
        runtime_desktop_settled_signal.signal()
        write_desktop_settled_signal_file("launcher observed authoritative settled after exit")
        runtime_event(
            "STATUS",
            "SUCCESS",
            "LAUNCHER_RUNTIME",
            "DESKTOP_SETTLED_OBSERVED|state=dormant",
        )
        return "settled", stdout_text, stderr_text

    if runtime_log_contains_since(startup_abort_marker, log_start_offset):
        runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_ABORT_OBSERVED")
        return "startup_aborted", stdout_text, stderr_text

    runtime_event(
        "STATUS",
        "WARNING",
        "LAUNCHER_RUNTIME",
        "DESKTOP_SETTLED_NOT_OBSERVED_BEFORE_EXIT",
    )
    return "not_settled_before_exit", stdout_text, stderr_text


def capture_post_settled_exit_markers(log_start_offset):
    return {
        "shutdown_requested": runtime_log_contains_since(
            "RENDERER_MAIN|SHUTDOWN_REQUESTED",
            log_start_offset,
        ),
        "relaunch_requested": runtime_log_contains_since(
            "RENDERER_MAIN|RELAUNCH_REQUEST_RECEIVED",
            log_start_offset,
        ),
        "event_loop_exit_zero": runtime_log_contains_since(
            "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0",
            log_start_offset,
        ),
    }


def classify_post_settled_exit(exit_code, startup_observation, log_start_offset):
    exit_markers = capture_post_settled_exit_markers(log_start_offset)
    if (
        exit_code == 0
        and exit_markers["shutdown_requested"]
        and exit_markers["event_loop_exit_zero"]
    ):
        return "valid_termination", exit_markers

    if startup_observation != "settled":
        return "", exit_markers

    return "abnormal_termination", exit_markers


def renderer_environment():
    return build_renderer_environment(os.environ)


def extract_renderer_failure_cause(stderr_text, stdout_text):
    def cleaned_lines(text):
        for raw in reversed(text.splitlines()):
            line = raw.strip()
            if not line:
                continue
            if line.startswith("Traceback"):
                continue
            if line.startswith("File "):
                continue
            if line.startswith("During handling of the above exception"):
                continue
            yield line

    preferred_tokens = ("Error:", "Exception:", "failed", "Failed", "crash", "Crash")

    for text in (stderr_text, stdout_text):
        for line in cleaned_lines(text):
            if any(token in line for token in preferred_tokens):
                return line

    for line in cleaned_lines(stderr_text):
        return line

    for line in cleaned_lines(stdout_text):
        lowered = line.lower()
        if "error" in lowered or "exception" in lowered or "fail" in lowered or "crash" in lowered:
            return line

    return ""


def extract_renderer_failure_origin(stderr_text, stdout_text):
    frame_pattern = re.compile(r'^\s*File "([^"]+)", line (\d+), in (.+)$')

    def sanitize_frame_path(path):
        try:
            abs_path = os.path.abspath(path)
            root_abs = os.path.abspath(ROOT_DIR)
            if os.path.commonpath([root_abs, abs_path]) == root_abs:
                return os.path.relpath(abs_path, ROOT_DIR).replace("\\", "/")
        except Exception:
            pass
        return os.path.basename(path).replace("\\", "/")

    def parse_frames(text):
        frames = []
        for raw in text.splitlines():
            match = frame_pattern.match(raw)
            if match:
                frames.append(match.groups())
        return frames

    root_abs = os.path.abspath(ROOT_DIR)

    for text in (stderr_text, stdout_text):
        frames = parse_frames(text or "")
        if not frames:
            continue

        app_frames = []
        for path, line, func in frames:
            try:
                if os.path.commonpath([root_abs, os.path.abspath(path)]) == root_abs:
                    app_frames.append((path, line, func.strip()))
            except Exception:
                continue

        target_path, target_line, target_func = (app_frames[-1] if app_frames else frames[-1])
        return f"Failure origin: {sanitize_frame_path(target_path)}:{target_line} in {target_func.strip()}"

    return ""


def extract_renderer_stderr_excerpt(stderr_text, failure_cause="", failure_origin=""):
    if not stderr_text:
        return []

    frame_pattern = re.compile(r'^\s*File "([^"]+)", line (\d+), in (.+)$')
    generic_headers = (
        "Traceback (most recent call last):",
        "During handling of the above exception",
    )

    def sanitize_frame_path(path):
        try:
            abs_path = os.path.abspath(path)
            root_abs = os.path.abspath(ROOT_DIR)
            if os.path.commonpath([root_abs, abs_path]) == root_abs:
                return os.path.relpath(abs_path, ROOT_DIR).replace("\\", "/")
        except Exception:
            pass
        return os.path.basename(path).replace("\\", "/")

    lines = [raw.rstrip("\r") for raw in stderr_text.splitlines() if raw.strip()]
    if not lines:
        return []

    last_frame_index = -1
    for index, raw in enumerate(lines):
        if frame_pattern.match(raw):
            last_frame_index = index

    if last_frame_index >= 0:
        candidate_source = lines[last_frame_index:]
    else:
        candidate_source = lines[-3:]

    excerpt = []
    for raw in candidate_source:
        stripped = raw.strip()
        if not stripped:
            continue
        if any(stripped.startswith(header) for header in generic_headers):
            continue

        frame_match = frame_pattern.match(raw)
        if frame_match:
            path, line_number, func = frame_match.groups()
            excerpt.append(f'File "{sanitize_frame_path(path)}", line {line_number}, in {func.strip()}')
            continue

        if stripped == (failure_cause or "").strip():
            continue

        if ":\\" in stripped:
            continue

        excerpt.append(stripped)

    deduped = []
    seen = set()
    for line in excerpt:
        if line not in seen:
            deduped.append(line)
            seen.add(line)

    return deduped[:3]


def write_runtime_stderr_excerpt(stderr_excerpt_lines):
    if not stderr_excerpt_lines:
        return
    runtime("Renderer stderr excerpt:")
    for line in stderr_excerpt_lines:
        runtime(f"  {line}")


def assess_renderer_failure_cause(failure_cause):
    cause = (failure_cause or "").strip()
    if not cause:
        return ""

    internal_exception_prefixes = (
        "RuntimeError:",
        "ValueError:",
        "TypeError:",
        "AttributeError:",
        "NameError:",
        "KeyError:",
        "IndexError:",
        "AssertionError:",
        "NotImplementedError:",
    )

    if cause.startswith(internal_exception_prefixes):
        return "Assessment: the renderer is failing with an internal startup exception."

    return "Assessment: the failure cause was captured, but could not be classified confidently."


def triage_renderer_failure(failure_cause, failure_stability=""):
    cause = (failure_cause or "").strip()
    stability = (failure_stability or "").strip()

    internal_exception_prefixes = (
        "RuntimeError:",
        "ValueError:",
        "TypeError:",
        "AttributeError:",
        "NameError:",
        "KeyError:",
        "IndexError:",
        "AssertionError:",
        "NotImplementedError:",
    )

    if stability == "unstable across recovery attempts":
        return "Triage: compare attempt-to-attempt failure differences before focusing on the final failure cause."

    if cause.startswith(internal_exception_prefixes):
        return "Triage: begin with renderer startup code and recent initialization changes."

    return "Triage: no confident investigation lane could be derived. Begin with the crash report."


def delete_file(path, reason):
    try:
        if os.path.exists(path):
            os.remove(path)
            runtime(f"Deleted file ({reason}): {path}")
            runtime_event("FILE", "DELETE", os.path.basename(path), "SUCCESS", reason)
            return True
        runtime(f"File already absent ({reason}): {path}")
        runtime_event("FILE", "DELETE", os.path.basename(path), "ABSENT", reason)
        return False
    except Exception as exc:
        runtime(f"Failed deleting file ({reason}): {path} :: {exc}")
        runtime_event("FILE", "DELETE", os.path.basename(path), "FAILED", reason, exc)
        return False


def request_startup_abort(reason):
    try:
        with open(STARTUP_ABORT_SIGNAL_FILE, "w", encoding="utf-8") as f:
            f.write("abort startup\n")
        runtime(f"Created startup abort signal ({reason}): {STARTUP_ABORT_SIGNAL_FILE}")
        runtime_event("FILE", "CREATE_OR_RESET", os.path.basename(STARTUP_ABORT_SIGNAL_FILE), "SUCCESS", reason)
        return True
    except Exception as exc:
        runtime(f"Failed creating startup abort signal ({reason}): {STARTUP_ABORT_SIGNAL_FILE} :: {exc}")
        runtime_event("FILE", "CREATE_OR_RESET", os.path.basename(STARTUP_ABORT_SIGNAL_FILE), "FAILED", reason, exc)
        return False


def crash_log(
    message,
    attempts,
    last_code,
    failure_cause="",
    failure_origin="",
    stderr_excerpt_lines=None,
    failure_assessment="",
    recovery_outcome="",
    attempt_pattern="",
    diagnostics_priority="",
    failure_stability="",
    triage_guidance="",
    crash_filename="",
    run_id="",
):
    if crash_filename:
        path = os.path.join(CRASH_DIR, crash_filename)
        stem = os.path.splitext(crash_filename)[0].replace("Crash_", "", 1)
        stem_parts = stem.split("_")
        ts = "_".join(stem_parts[:2]) if len(stem_parts) >= 2 else stem
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(CRASH_DIR, f"Crash_{ts}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("NEXUS DESKTOP AI CRASH REPORT\n")
        f.write(f"Time: {ts}\n")
        if run_id:
            f.write(f"{run_id}\n")
        f.write(f"Python: {pythonw()}\n")
        f.write(f"{ENVIRONMENT_FINGERPRINT}\n")
        f.write(f"Working Directory: {ROOT_DIR}\n")
        f.write(f"Renderer: {TARGET_SCRIPT}\n")
        f.write(f"Max Recovery Attempts: {MAX_RECOVERY_ATTEMPTS}\n")
        f.write(f"Attempts Used: {attempts}\n")
        f.write(f"Last Exit Code: {last_code}\n")
        f.write(f"Runtime Log: {RUNTIME_FILE}\n")
        f.write("\n")
        for line in build_incident_summary_lines(
            run_id,
            attempts,
            last_code,
            failure_cause,
            failure_origin,
            failure_assessment,
            recovery_outcome,
            attempt_pattern,
            diagnostics_priority,
            failure_stability,
            triage_guidance,
            os.path.basename(path),
            os.path.basename(RUNTIME_FILE),
        ):
            f.write(f"{line}\n")
        if stderr_excerpt_lines:
            f.write("Renderer stderr excerpt:\n")
            for line in stderr_excerpt_lines:
                f.write(f"  {line}\n")
        f.write("\n")
        f.write(f"Failure Reason: {message}\n")
        if failure_cause:
            f.write(f"Failure Cause: {failure_cause}\n")
        if failure_origin:
            f.write(f"{failure_origin}\n")
    runtime(f"Crash log written: {path}")
    runtime_event("STATUS", "SUCCESS", "CRASH_LOG_WRITTEN", os.path.basename(path))
    return path


def launch_diag():
    runtime("Launching diagnostics UI")
    runtime_event("STATUS", "START", "DIAGNOSTICS_UI")
    write_status("TRACE", "Launching diagnostics UI")
    proc = subprocess.Popen(
        [pythonw(), DIAGNOSTICS_SCRIPT, "--runtime-log", RUNTIME_FILE],
        **hidden_window_kwargs(),
    )
    runtime(f"Diagnostics PID: {proc.pid}")
    runtime_event("STATUS", "SUCCESS", "DIAGNOSTICS_UI", f"PID={proc.pid}")
    return proc


def speak(spoken_text, display_text=None):
    if not os.path.exists(VOICE_SCRIPT):
        runtime(f"Voice script missing: {VOICE_SCRIPT}")
        runtime_event("STATUS", "FAIL", "VOICE_SCRIPT", "MISSING")
        diagnostic = "state=unavailable|available=false|degraded=false|reason=script_missing|mode=launcher"
        write_status("VOICE_DIAGNOSTIC", diagnostic)
        runtime_event("VOICE", "DIAGNOSTIC", spoken_text, diagnostic)
        return 1

    display_text = display_text or spoken_text
    runtime(f"VOICE: {spoken_text}")
    runtime_event("VOICE", "START", spoken_text)
    write_status("VOICE_CLEAR", "")

    cmd = [
        pythonw(),
        VOICE_SCRIPT,
        "--text", spoken_text,
        "--display-text", display_text,
        "--status-file", STATUS_FILE,
        "--stop-signal", STOP_SIGNAL_FILE,
    ]
    runtime(f"VOICE CMD: {' '.join(cmd[2:])}")
    result = subprocess.run(cmd, **hidden_window_kwargs())
    runtime(f"VOICE EXIT CODE: {result.returncode} :: {spoken_text}")
    diagnostic = latest_voice_diagnostic()
    if not diagnostic:
        if result.returncode == 0:
            diagnostic = "state=available|available=true|degraded=false|reason=legacy_exit_zero|mode=launcher"
        else:
            diagnostic = f"state=unavailable|available=false|degraded=false|reason=voice_exit_{result.returncode}|mode=launcher"
    runtime_event("VOICE", "DIAGNOSTIC", spoken_text, diagnostic)
    runtime_event("VOICE", "END", spoken_text, f"EXIT={result.returncode}")
    return result.returncode


def run_renderer():
    runtime(f"Starting renderer: {TARGET_SCRIPT}")
    runtime_event("STATUS", "START", "RENDERER_PROCESS")
    log_start_offset = os.path.getsize(RUNTIME_FILE) if os.path.exists(RUNTIME_FILE) else 0
    renderer_env = renderer_environment()
    effective_webengine_flags = renderer_env.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
    parent_webengine_flags = renderer_env.get(
        "NEXUS_RENDERER_PARENT_QTWEBENGINE_CHROMIUM_FLAGS",
        "",
    )
    effective_webengine_switches = [
        token.split("=", 1)[0] for token in effective_webengine_flags.split()
    ]
    runtime_event(
        "STATUS",
        "TRACE",
        "RENDERER_PROCESS",
        "WEBENGINE_RENDERING_BACKEND_REQUEST=" + (
            "explicit_parent_software_compositor"
            if WEBENGINE_SOFTWARE_COMPOSITOR_FLAG in effective_webengine_switches
            else "inherited_platform_default"
        ),
        "REASON=preserve_platform_default_and_explicit_parent_flags",
        f"POLICY={RENDERER_BACKEND_POLICY}",
        f"CLASSIFICATION={RENDERER_BACKEND_CLASSIFICATION}",
        "AUTOMATIC_GPU_DISABLE=false",
        f"PARENT_QTWEBENGINE_CHROMIUM_FLAGS={parent_webengine_flags or '<empty>'}",
        f"QTWEBENGINE_CHROMIUM_FLAGS={effective_webengine_flags}",
        f"DISABLE_GPU_COUNT={effective_webengine_switches.count(WEBENGINE_SOFTWARE_COMPOSITOR_FLAG)}",
    )
    proc = subprocess.Popen(
        [
            pythonw(),
            TARGET_SCRIPT,
            "--runtime-log", RUNTIME_FILE,
            "--startup-abort-signal", STARTUP_ABORT_SIGNAL_FILE,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=renderer_env,
        **hidden_window_kwargs(),
    )
    runtime(f"Renderer PID: {proc.pid}")
    runtime_event("STATUS", "SUCCESS", "RENDERER_PROCESS_SPAWN", f"PID={proc.pid}")
    startup_observation, stdout_text, stderr_text = observe_authoritative_desktop_settled(proc, log_start_offset)
    if stdout_text is None and stderr_text is None:
        stdout_text, stderr_text = proc.communicate()
    runtime(f"Renderer exit code: {proc.returncode}")
    runtime_event("STATUS", "END", "RENDERER_PROCESS", f"EXIT={proc.returncode}")
    failure_cause = extract_renderer_failure_cause(stderr_text or "", stdout_text or "")
    failure_origin = extract_renderer_failure_origin(stderr_text or "", stdout_text or "")
    stderr_excerpt_lines = extract_renderer_stderr_excerpt(stderr_text or "", failure_cause, failure_origin)
    post_settled_classification, post_settled_exit_markers = classify_post_settled_exit(
        proc.returncode,
        startup_observation,
        log_start_offset,
    )
    if proc.returncode != 0 and failure_cause:
        runtime(f"Renderer failure cause: {failure_cause}")
    if proc.returncode != 0 and failure_origin:
        runtime(failure_origin)
    return (
        proc.returncode,
        failure_cause,
        failure_origin,
        stderr_excerpt_lines,
        startup_observation,
        post_settled_classification,
        post_settled_exit_markers,
    )


def finalize_failure(
    attempts_used,
    last_code,
    failure_cause="",
    failure_origin="",
    stderr_excerpt_lines=None,
    failure_assessment="",
    recovery_outcome="",
    attempt_pattern="",
    diagnostics_priority="",
    failure_stability="",
    triage_guidance="",
    terminal_failure_message="",
    crash_filename="",
    run_id="",
):
    runtime("Beginning final immersive shutdown sequence")
    runtime_event("STATUS", "START", "FINAL_IMMERSIVE_SHUTDOWN")
    speak("Recovery failed.")
    speak("Shutting down.")
    runtime("Final immersive shutdown sequence finished")
    runtime_event("STATUS", "SUCCESS", "FINAL_IMMERSIVE_SHUTDOWN")

    write_status("TRACE", triage_guidance or triage_renderer_failure(failure_cause, failure_stability))
    write_state("COMPLETE")
    if crash_filename:
        write_status("TRACE", f"Latest crash report: {crash_filename}")
    write_status("TRACE", f"Latest runtime log: {os.path.basename(RUNTIME_FILE)}")
    runtime("Backend completion reached after final voice line")

    if COMPLETE_CLEANUP_DELAY_SECONDS > 0:
        runtime(f"Waiting {COMPLETE_CLEANUP_DELAY_SECONDS:.2f}s before backend cleanup")
        time.sleep(COMPLETE_CLEANUP_DELAY_SECONDS)

    delete_file(STOP_SIGNAL_FILE, "backend completion")
    delete_file(STATUS_FILE, "backend completion")

    crash_log(
        terminal_failure_message or "Renderer failed after maximum recovery attempts.",
        attempts_used,
        last_code or -1,
        failure_cause,
        failure_origin,
        stderr_excerpt_lines or [],
        failure_assessment,
        recovery_outcome,
        attempt_pattern,
        diagnostics_priority,
        failure_stability,
        triage_guidance,
        crash_filename,
        run_id,
    )


def main():
    run_id = create_run_id()
    single_instance_state = {
        "declined_relaunch": False,
        "pre_settled_conflict": False,
        "signal_failed_relaunch": False,
        "wait_timeout_relaunch": False,
        "replacement_session": False,
        "replacement_session_settled_recorded": False,
        "released": False,
        "active_owner_conflict": False,
    }

    def log_single_instance_event(event):
        if event == "SINGLE_INSTANCE_ACQUIRED":
            if claim_active_runtime_owner_file("startup owner acquired"):
                runtime_desktop_settled_signal.clear()
            else:
                single_instance_state["active_owner_conflict"] = True
        if event in {"REPLACE_PROMPT_DECLINED", "REPLACE_PROMPT_AUTO_DECLINED"}:
            single_instance_state["declined_relaunch"] = True
        if event == "PRE_SETTLED_CONFLICT_SESSION_PRESERVED":
            single_instance_state["pre_settled_conflict"] = True
        if event == "RELAUNCH_SIGNAL_FAILED":
            single_instance_state["signal_failed_relaunch"] = True
        if event == "RELAUNCH_WAIT_TIMEOUT":
            single_instance_state["wait_timeout_relaunch"] = True
        if event in {"RELAUNCH_ACQUIRED_AFTER_WAIT", "RELAUNCH_REPLACEMENT_SESSION_CONFIRMED"}:
            single_instance_state["replacement_session"] = True
        runtime(f"Single-instance flow: {event}")
        runtime_event("STATUS", "TRACE", "LAUNCHER_RUNTIME", event)

    def record_relaunch_replacement_settled():
        if (
            not single_instance_state["replacement_session"]
            or single_instance_state["replacement_session_settled_recorded"]
        ):
            return

        single_instance_state["replacement_session_settled_recorded"] = True
        runtime("Replacement session reached authoritative desktop-settled state after relaunch")
        runtime_event(
            "STATUS",
            "SUCCESS",
            "LAUNCHER_RUNTIME",
            "RELAUNCH_REPLACEMENT_SESSION_SETTLED",
            "state=dormant",
        )

    def release_single_instance_resources():
        if single_instance_state["released"]:
            return

        single_instance_state["released"] = True
        owner_conflict, _owner = live_active_owner_conflict()
        if not owner_conflict:
            runtime_desktop_settled_signal.clear()
        clear_active_runtime_owner("runtime release")
        runtime_instance_guard.release()
        runtime_relaunch_signal.close()
        runtime_desktop_settled_signal.close()
        runtime("Single-instance flow: SINGLE_INSTANCE_RELEASED")
        runtime_event("STATUS", "TRACE", "LAUNCHER_RUNTIME", "SINGLE_INSTANCE_RELEASED")

    if not acquire_or_prompt_replace(
        runtime_instance_guard,
        runtime_relaunch_signal,
        "Nexus Desktop AI Session Active",
        "Nexus Desktop AI is already active on this computer.\n\nDo you want to close the current session and relaunch the desktop runtime now?",
        eyebrow_text="NEXUS DESKTOP AI",
        primary_button_text="Relaunch Desktop Runtime",
        secondary_button_text="Keep Current Session",
        event_logger=log_single_instance_event,
        active_session_settled_signal=runtime_desktop_settled_signal,
        active_session_settled_checker=active_desktop_settled_signal_present,
        pre_settled_conflict_message=(
            "Nexus Desktop AI is still starting. Please wait for the current startup to finish "
            "before relaunching the desktop runtime."
        ),
    ):
        if single_instance_state["pre_settled_conflict"]:
            runtime(
                "Incoming launch exited cleanly: active session is still starting; "
                "startup-phase owner preserved"
            )
            runtime_event(
                "STATUS",
                "SKIP",
                "LAUNCHER_RUNTIME",
                "PRE_SETTLED_INCOMING_CONFLICT_SESSION_PRESERVED",
            )
        elif single_instance_state["declined_relaunch"]:
            runtime("Incoming launch exited cleanly: current session preserved after relaunch decline")
            runtime_event(
                "STATUS",
                "SUCCESS",
                "LAUNCHER_RUNTIME",
                "RELAUNCH_DECLINED_SESSION_PRESERVED",
            )
        elif single_instance_state["signal_failed_relaunch"]:
            runtime(
                "Incoming launch exited after accepted relaunch signal failure: current session preserved"
            )
            runtime_event(
                "STATUS",
                "WARNING",
                "LAUNCHER_RUNTIME",
                "RELAUNCH_SIGNAL_FAILED_SESSION_PRESERVED",
            )
        elif single_instance_state["wait_timeout_relaunch"]:
            runtime(
                "Incoming launch exited after accepted relaunch wait timeout: replacement session not confirmed"
            )
            runtime_event(
                "STATUS",
                "WARNING",
                "LAUNCHER_RUNTIME",
                "RELAUNCH_WAIT_TIMEOUT_REPLACEMENT_UNCONFIRMED",
            )
        else:
            runtime("Launcher start blocked: Nexus Desktop AI is already running")
            runtime_event("STATUS", "SKIP", "LAUNCHER_RUNTIME", "ALREADY_RUNNING")
        return 0

    if single_instance_state["active_owner_conflict"]:
        runtime(
            "Launcher start blocked: active runtime owner file belongs to another live launcher; "
            "preserving current session and suppressing duplicate renderer startup"
        )
        runtime_event(
            "STATUS",
            "SKIP",
            "LAUNCHER_RUNTIME",
            "ACTIVE_RUNTIME_OWNER_CONFLICT_SESSION_PRESERVED",
        )
        show_already_running_dialog(
            "Nexus Desktop AI Session Active",
            "Nexus Desktop AI is still starting or recovering. Please wait for the current session to finish.",
            eyebrow_text="NEXUS DESKTOP AI",
            primary_button_text="Close",
        )
        release_single_instance_resources()
        return 0

    ensure_crash_dir("launcher startup")
    reset_status()

    runtime("==== Nexus Desktop AI runtime started ====")
    runtime_event("STATUS", "START", "LAUNCHER_RUNTIME")
    runtime(run_id)
    runtime(ENVIRONMENT_FINGERPRINT)
    runtime(f"Python executable: {pythonw()}")
    runtime(f"Working directory: {ROOT_DIR}")
    runtime(f"Renderer target: {TARGET_SCRIPT}")
    if single_instance_state["replacement_session"]:
        runtime("Replacement session confirmed after accepted relaunch")
        runtime_event("STATUS", "TRACE", "LAUNCHER_RUNTIME", "RELAUNCH_REPLACEMENT_SESSION_ACTIVE")

    diagnostics_opened = False
    recovery_voice_spoken = False
    last_code = None
    last_failure_cause = ""
    last_failure_origin = ""
    last_failure_stderr_excerpt = []
    last_failure_assessment = ""
    failure_causes = []
    failure_kinds = []
    assessment_emitted = False
    consecutive_startup_abort_count = 0
    consecutive_identical_crash_count = 0
    last_normalized_crash_cause = ""
    last_normalized_crash_origin = ""
    previous_failure_kind = ""
    previous_failure_cause = ""
    previous_failure_origin = ""
    mixed_failure_pattern_logged = False
    recovery_pipeline_end_reason = "MAX_ATTEMPTS_EXHAUSTED"

    def exit_if_relaunch_requested(phase_label=""):
        if not runtime_relaunch_signal.consume():
            return False

        runtime("Launcher relaunch request received")
        if phase_label:
            runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "RELAUNCH_REQUEST_RECEIVED", f"PHASE={phase_label}")
        else:
            runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "RELAUNCH_REQUEST_RECEIVED")
        delete_file(STOP_SIGNAL_FILE, "launcher relaunch")
        delete_file(STARTUP_ABORT_SIGNAL_FILE, "launcher relaunch")
        delete_file(STATUS_FILE, "launcher relaunch")
        return True

    for attempt in range(1, MAX_RECOVERY_ATTEMPTS + 1):
        if exit_if_relaunch_requested("before_renderer_attempt"):
            release_single_instance_resources()
            return 0
        if attempt > 1:
            owner_conflict, owner = live_active_owner_conflict()
            if owner_conflict:
                runtime(
                    "Recovery suppressed: another live launcher owns the active runtime session; "
                    "not spawning an orphan renderer"
                )
                runtime_event(
                    "STATUS",
                    "SKIP",
                    "LAUNCHER_RUNTIME",
                    "RECOVERY_SUPPRESSED_BY_ACTIVE_OWNER",
                    active_owner_summary(owner),
                )
                release_single_instance_resources()
                return 0

        runtime(f"Renderer launch attempt {attempt}/{MAX_RECOVERY_ATTEMPTS}")
        runtime_event("STATUS", "START", "RECOVERY_ATTEMPT", f"INDEX={attempt}", f"MAX={MAX_RECOVERY_ATTEMPTS}")
        write_status("TRACE", f"Renderer launch attempt {attempt}/{MAX_RECOVERY_ATTEMPTS}")
        time.sleep(0.18)

        (
            last_code,
            failure_cause,
            failure_origin,
            stderr_excerpt_lines,
            startup_observation,
            post_settled_classification,
            post_settled_exit_markers,
        ) = run_renderer()
        startup_aborted = startup_observation == "startup_aborted"

        if last_code == 0 and startup_aborted:
            runtime("Renderer startup aborted cooperatively")
            runtime_event("STATUS", "WARNING", "RECOVERY_ATTEMPT", f"INDEX={attempt}", "RENDERER_STARTUP_ABORTED")
            delete_file(STOP_SIGNAL_FILE, "startup abort")
            delete_file(STARTUP_ABORT_SIGNAL_FILE, "startup abort")
            runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_ABORT_COMPLETE")
            last_code = STARTUP_ABORT_CONTROL_FLOW_RESULT
            failure_cause = "Renderer startup aborted cooperatively before readiness."
            failure_origin = ""
            stderr_excerpt_lines = []

        if post_settled_classification == "valid_termination":
            if startup_observation == "settled":
                record_relaunch_replacement_settled()
                runtime("Renderer exited normally")
            else:
                runtime(
                    "Renderer exited normally before authoritative desktop-settled signal "
                    "after user-requested shutdown"
                )
                runtime_event(
                    "STATUS",
                    "SUCCESS",
                    "LAUNCHER_RUNTIME",
                    "PRE_SETTLED_USER_SHUTDOWN_COMPLETE",
                )
            runtime_event("STATUS", "SUCCESS", "RECOVERY_ATTEMPT", f"INDEX={attempt}", "RENDERER_EXIT=0")
            write_status("TRACE", "Renderer exited normally")
            delete_file(STOP_SIGNAL_FILE, "normal exit")
            delete_file(STARTUP_ABORT_SIGNAL_FILE, "normal exit")
            delete_file(STATUS_FILE, "normal exit")
            runtime_event("STATUS", "SUCCESS", "LAUNCHER_RUNTIME", "NORMAL_EXIT_COMPLETE")
            record_finalized_history(
                run_id,
                "SUCCESS",
                "NORMAL_EXIT_COMPLETE",
                "NORMAL_EXIT_COMPLETE",
                attempt,
            )
            release_single_instance_resources()
            return 0

        if last_code == 0 and startup_observation != "settled":
            runtime("Renderer exited before authoritative desktop-settled signal was observed")
            runtime_event(
                "STATUS",
                "WARNING",
                "RECOVERY_ATTEMPT",
                f"INDEX={attempt}",
                "DESKTOP_SETTLED_NOT_REACHED_BEFORE_EXIT",
            )
            failure_cause = (
                failure_cause
                or "Renderer exited before the authoritative desktop-settled signal was observed."
            )
            failure_origin = (
                failure_origin
                or "Failure origin: launcher startup observation ended before the authoritative desktop-settled signal."
            )

        if startup_observation == "settled" and post_settled_classification == "abnormal_termination":
            marker_details = [
                f"EXIT={last_code}",
                f"RELAUNCH_REQUESTED={'true' if post_settled_exit_markers['relaunch_requested'] else 'false'}",
                f"SHUTDOWN_REQUESTED={'true' if post_settled_exit_markers['shutdown_requested'] else 'false'}",
                f"EVENT_LOOP_EXIT_ZERO={'true' if post_settled_exit_markers['event_loop_exit_zero'] else 'false'}",
            ]
            runtime(
                "Renderer exited after the authoritative desktop-settled state was already reached; "
                "classifying as an abnormal post-settled termination"
            )
            runtime_event(
                "STATUS",
                "FAIL",
                "RECOVERY_ATTEMPT",
                f"INDEX={attempt}",
                "POST_SETTLED_ABNORMAL_TERMINATION",
                f"EXIT={last_code}",
            )
            write_status(
                "TRACE",
                "Renderer exited after authoritative desktop-settled proof; "
                "classified as abnormal and non-green.",
            )
            if failure_cause:
                runtime(f"Post-settled exit cause: {failure_cause}")
                write_status("TRACE", f"Post-settled exit cause: {failure_cause}")
            if failure_origin:
                runtime(f"Post-settled exit origin: {failure_origin}")
                write_status("TRACE", failure_origin)
            delete_file(STOP_SIGNAL_FILE, "post-settled abnormal termination")
            delete_file(STARTUP_ABORT_SIGNAL_FILE, "post-settled abnormal termination")
            runtime_event(
                "STATUS",
                "FAIL",
                "LAUNCHER_RUNTIME",
                "POST_SETTLED_ABNORMAL_TERMINATION",
                *marker_details,
            )
            record_finalized_history(
                run_id,
                "FAILURE",
                "POST_SETTLED_ABNORMAL_TERMINATION",
                "POST_SETTLED_ABNORMAL_TERMINATION",
                attempt,
                failure_cause=failure_cause or f"Renderer exited with native code {last_code}.",
                failure_origin=failure_origin,
            )
            release_single_instance_resources()
            return 1

        if last_code == STARTUP_ABORT_CONTROL_FLOW_RESULT:
            consecutive_startup_abort_count += 1
            consecutive_identical_crash_count = 0
            last_normalized_crash_cause = ""
            last_normalized_crash_origin = ""
            current_failure_kind = STARTUP_ABORT_CONTROL_FLOW_RESULT
            current_failure_cause = ""
            current_failure_origin = ""
        else:
            consecutive_startup_abort_count = 0
            normalized_failure_cause = normalize_policy_value(failure_cause)
            normalized_failure_origin = normalize_policy_value(failure_origin, "Failure origin: ")
            if repeated_identical_crash(
                last_normalized_crash_cause,
                last_normalized_crash_origin,
                normalized_failure_cause,
                normalized_failure_origin,
            ):
                consecutive_identical_crash_count += 1
            elif normalized_failure_cause:
                consecutive_identical_crash_count = 1
            else:
                consecutive_identical_crash_count = 0
            last_normalized_crash_cause = normalized_failure_cause
            last_normalized_crash_origin = normalized_failure_origin
            current_failure_kind = "CRASH"
            current_failure_cause = normalized_failure_cause
            current_failure_origin = normalized_failure_origin

        last_failure_cause = failure_cause or last_failure_cause
        last_failure_origin = failure_origin or last_failure_origin
        last_failure_stderr_excerpt = stderr_excerpt_lines or last_failure_stderr_excerpt
        failure_causes.append((failure_cause or "").strip())
        failure_kinds.append(current_failure_kind)
        runtime("Renderer exited unexpectedly")
        runtime_event("STATUS", "FAIL", "RECOVERY_ATTEMPT", f"INDEX={attempt}", f"RENDERER_EXIT={last_code}")
        write_status("SUMMARY", failure_cause or "Desktop renderer exited unexpectedly")
        write_status("TRACE", f"Renderer exited unexpectedly with code {last_code}")
        if failure_cause:
            write_status("TRACE", f"Failure cause: {failure_cause}")
            if not assessment_emitted:
                failure_assessment = assess_renderer_failure_cause(failure_cause)
                if failure_assessment:
                    last_failure_assessment = failure_assessment
                    runtime(f"Renderer failure assessment: {failure_assessment}")
                    write_status("TRACE", failure_assessment)
                    assessment_emitted = True

        if not diagnostics_opened:
            write_state("STARTED")
            write_status("TRACE", "Scanning runtime environment")
            time.sleep(0.18)
            write_status("TRACE", "Checking desktop engine")
            time.sleep(0.18)
            ensure_crash_dir("first failure detected")
            write_status("TRACE", "Crash folder ready")
            launch_diag()
            speak("Uhm..... Sir, I seem to be malfunctioning.")
            diagnostics_opened = True

        mixed_failure_pattern = classify_mixed_failure_pattern(
            previous_failure_kind,
            previous_failure_cause,
            previous_failure_origin,
            current_failure_kind,
            current_failure_cause,
            current_failure_origin,
        )
        if not mixed_failure_pattern_logged and mixed_failure_pattern:
            runtime(f"Mixed failure pattern observed: {mixed_failure_pattern}")
            runtime_event(
                "STATUS",
                "WARNING",
                "LAUNCHER_RUNTIME",
                "MIXED_FAILURE_PATTERN_OBSERVED",
                f"TYPE={mixed_failure_pattern}",
            )
            write_status("TRACE", f"Mixed failure pattern observed: {mixed_failure_pattern}")
            mixed_failure_pattern_logged = True

        previous_failure_kind = current_failure_kind
        previous_failure_cause = current_failure_cause
        previous_failure_origin = current_failure_origin

        if consecutive_startup_abort_count >= CONSECUTIVE_STARTUP_ABORT_THRESHOLD:
            runtime("Consecutive startup abort threshold reached")
            runtime_event(
                "STATUS",
                "WARNING",
                "LAUNCHER_RUNTIME",
                "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED",
                f"COUNT={consecutive_startup_abort_count}",
            )
            recovery_pipeline_end_reason = "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED"
            break

        if consecutive_identical_crash_count >= CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD:
            runtime("Repeated identical crash threshold reached")
            runtime_event(
                "STATUS",
                "WARNING",
                "LAUNCHER_RUNTIME",
                "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
                f"COUNT={consecutive_identical_crash_count}",
            )
            recovery_pipeline_end_reason = "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED"
            break

        if attempt < MAX_RECOVERY_ATTEMPTS:
            runtime(f"Preparing recovery attempt {attempt}")
            runtime_event("STATUS", "START", "RECOVERY_COOLDOWN", f"INDEX={attempt}", f"SECONDS={RECOVERY_COOLDOWN_SECONDS:.1f}")
            write_state("RECOVERING")
            write_status("TRACE", f"Attempting recovery ({attempt}/{MAX_RECOVERY_ATTEMPTS})")
            write_status("TRACE", f"Cooldown before next attempt: {RECOVERY_COOLDOWN_SECONDS:.1f}s")

            if not recovery_voice_spoken:
                speak("Attempting recovery.")
                recovery_voice_spoken = True

            time.sleep(RECOVERY_COOLDOWN_SECONDS)
            runtime_event("STATUS", "SUCCESS", "RECOVERY_COOLDOWN", f"INDEX={attempt}")

    if exit_if_relaunch_requested("before_failure_finalization"):
        release_single_instance_resources()
        return 0

    failure_stability = select_failure_stability(
        mixed_failure_pattern_logged,
        failure_kinds,
        failure_causes,
    )
    if recovery_pipeline_end_reason == "MAX_ATTEMPTS_EXHAUSTED" and failure_stability:
        recovery_pipeline_end_reason = "MAX_ATTEMPTS_EXHAUSTED_WITH_INSTABILITY"

    if recovery_pipeline_end_reason == "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED":
        runtime("Recovery pipeline escalated after repeated startup aborts")
        runtime_event("STATUS", "FAIL", "RECOVERY_PIPELINE", recovery_pipeline_end_reason)
        write_status("TRACE", "Repeated startup aborts reached escalation threshold.")
    elif recovery_pipeline_end_reason == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED":
        runtime("Recovery pipeline escalated after repeated identical crash outcomes")
        runtime_event("STATUS", "FAIL", "RECOVERY_PIPELINE", recovery_pipeline_end_reason)
        write_status("TRACE", "Repeated identical crash outcomes reached escalation threshold.")
    elif recovery_pipeline_end_reason == "MAX_ATTEMPTS_EXHAUSTED_WITH_INSTABILITY":
        runtime("All recovery attempts exhausted with instability observed")
        runtime_event("STATUS", "FAIL", "RECOVERY_PIPELINE", recovery_pipeline_end_reason)
        write_status("TRACE", "Recovery attempts exhausted with instability observed.")
    else:
        runtime("All recovery attempts exhausted")
        runtime_event("STATUS", "FAIL", "RECOVERY_PIPELINE", "MAX_ATTEMPTS_EXHAUSTED")
        write_status("TRACE", "Recovery attempts exhausted")
    recovery_outcome = select_recovery_outcome(recovery_pipeline_end_reason, failure_causes)
    attempt_pattern = select_attempt_pattern(
        recovery_pipeline_end_reason,
        mixed_failure_pattern_logged,
        failure_kinds,
        failure_causes,
    )
    triage_guidance = triage_renderer_failure(last_failure_cause, failure_stability)
    diagnostics_priority = select_diagnostics_priority(failure_stability)
    prior_history_context = summarize_prior_history_for_diagnostics(
        load_history_records(),
        build_failure_fingerprint(
            "FAILURE",
            recovery_pipeline_end_reason,
            last_failure_cause,
            last_failure_origin,
        ),
    )
    if diagnostics_priority:
        write_status("SUMMARY", f"Diagnostics Priority: {diagnostics_priority}")
    if failure_stability:
        write_status("SUMMARY", f"Failure Stability: {failure_stability}")
    if recovery_outcome == "Automatic recovery did not change the underlying renderer failure.":
        write_status("SUMMARY", "Automatic recovery did not change the underlying renderer failure.")
        write_status("TRACE", "Same failure cause persisted across all recovery attempts.")
    if prior_history_context["history_loaded"]:
        if prior_history_context["matching_failure_recurrence"] > 0:
            write_status(
                "TRACE",
                format_historical_context_line(
                    f"matching failure fingerprint observed in {prior_history_context['matching_failure_recurrence']} prior run(s)."
                ),
            )
        write_status(
            "TRACE",
            format_historical_context_line(
                f"recent recorded failure history stability = {prior_history_context['recent_history_stability']}."
            ),
        )
    historical_advisory_hint = select_historical_advisory_hint(prior_history_context)
    if historical_advisory_hint:
        write_status("TRACE", historical_advisory_hint)
    attempts_used = len(failure_kinds)
    terminal_failure_message = select_terminal_failure_message(recovery_pipeline_end_reason)
    if recovery_pipeline_end_reason in {
        "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED",
        "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
    }:
        write_status("SUMMARY", recovery_outcome)
    write_status("SUMMARY", "Automatic recovery has completed. Manual investigation is required.")
    crash_filename = f"Crash_{RUN_ID_STEM}.txt"
    write_status("SUMMARY", "I have prepared the latest crash report and runtime log. Review the crash report first.")
    finalize_failure(
        attempts_used,
        last_code,
        last_failure_cause,
        last_failure_origin,
        last_failure_stderr_excerpt,
        last_failure_assessment,
        recovery_outcome,
        attempt_pattern,
        diagnostics_priority,
        failure_stability,
        triage_guidance,
        terminal_failure_message,
        crash_filename,
        run_id,
    )
    write_runtime_incident_summary(
        run_id,
        attempts_used,
        last_code or -1,
        last_failure_cause,
        last_failure_origin,
        last_failure_assessment,
        recovery_outcome,
        attempt_pattern,
        diagnostics_priority,
        failure_stability,
        triage_guidance,
        crash_filename,
        os.path.basename(RUNTIME_FILE),
    )
    write_runtime_stderr_excerpt(last_failure_stderr_excerpt)
    runtime_event("STATUS", "SUCCESS", "LAUNCHER_RUNTIME", "FAILURE_FLOW_COMPLETE")
    record_finalized_history(
        run_id,
        "FAILURE",
        recovery_pipeline_end_reason,
        recovery_pipeline_end_reason,
        len(failure_kinds),
        attempt_pattern,
        failure_stability,
        diagnostics_priority,
        last_failure_cause,
        last_failure_origin,
    )
    release_single_instance_resources()


if __name__ == "__main__":
    raise SystemExit(main() or 0)
