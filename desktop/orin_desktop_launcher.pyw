# Version 1.3.2 rev 11 launcher

import os
import sys
import time
import re
import json
import subprocess
import datetime
import platform
import secrets

from single_instance import NamedSignal, SingleInstanceGuard, acquire_or_prompt_replace


def env_flag(name):
    value = (os.environ.get(name) or "").strip().casefold()
    return value in {"1", "true", "yes", "on"}


def env_path_override(name, default_path):
    value = (os.environ.get(name) or "").strip()
    return os.path.abspath(value) if value else default_path


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TARGET_SCRIPT = os.path.join(ROOT_DIR, "desktop", "jarvis_desktop_main.py")
DEFAULT_LOG_DIR = os.path.join(ROOT_DIR, "logs")
TARGET_SCRIPT = env_path_override("JARVIS_HARNESS_TARGET_SCRIPT", DEFAULT_TARGET_SCRIPT)
LOG_DIR = env_path_override("JARVIS_HARNESS_LOG_ROOT", DEFAULT_LOG_DIR)
CRASH_DIR = os.path.join(LOG_DIR, "crash")
STATUS_FILE = os.path.join(LOG_DIR, "diagnostics_status.txt")
STOP_SIGNAL_FILE = os.path.join(LOG_DIR, "diagnostics_stop.signal")
STARTUP_ABORT_SIGNAL_FILE = os.path.join(LOG_DIR, "renderer_startup_abort.signal")
DIAGNOSTICS_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_diagnostics.pyw")
VOICE_SCRIPT = os.path.join(ROOT_DIR, "Audio", "jarvis_error_voice.py")
HARNESS_DISABLE_DIAGNOSTICS = env_flag("JARVIS_HARNESS_DISABLE_DIAGNOSTICS")
HARNESS_DISABLE_VOICE = env_flag("JARVIS_HARNESS_DISABLE_VOICE")
RUNTIME_INSTANCE_MUTEX = r"Local\JarvisRuntimeSingletonV1"
RUNTIME_RELAUNCH_EVENT = r"Local\JarvisRuntimeRelaunchRequestV1"
runtime_instance_guard = SingleInstanceGuard(RUNTIME_INSTANCE_MUTEX)
runtime_relaunch_signal = NamedSignal(RUNTIME_RELAUNCH_EVENT)

MAX_RECOVERY_ATTEMPTS = 3
RECOVERY_COOLDOWN_SECONDS = 1.2
COMPLETE_CLEANUP_DELAY_SECONDS = 0.35
STARTUP_OBSERVE_POLL_SECONDS = 0.05
STARTUP_READY_OBSERVE_WINDOW_SECONDS = 3.0
STARTUP_READY_STALL_CONFIRM_SECONDS = 8.0
STARTUP_ABORT_CONTROL_FLOW_RESULT = "STARTUP_ABORT"
CONSECUTIVE_STARTUP_ABORT_THRESHOLD = 2
CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD = 2
HISTORY_SCHEMA_VERSION = 1
HISTORY_STABILITY_WINDOW_SIZE = 5
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


def history_file():
    return os.path.join(LOG_DIR, "jarvis_history_v1.jsonl")


def history_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_history_run_id(run_id):
    return strip_label_prefix(run_id, "Run ID: ") or RUN_ID_STEM


def prepare_history_storage_path():
    path = os.path.abspath(history_file())
    parent_dir = os.path.dirname(path)
    if not parent_dir:
        raise ValueError("History storage path has no parent directory.")
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
        history_path = os.path.abspath(history_file())
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


def observe_renderer_startup_ready(proc, log_start_offset):
    ready_marker = "RENDERER_MAIN|STARTUP_READY"
    startup_abort_marker = "RENDERER_MAIN|STARTUP_ABORTED"
    warn_deadline = time.monotonic() + STARTUP_READY_OBSERVE_WINDOW_SECONDS
    stall_deadline = time.monotonic() + STARTUP_READY_STALL_CONFIRM_SECONDS
    warned_within_window = False
    stall_confirmed = False
    abort_requested_on_stall = False

    runtime_event("STATUS", "TRACE", "LAUNCHER_RUNTIME", "STARTUP_OBSERVE_BEGIN")

    while True:
        if runtime_log_contains_since(ready_marker, log_start_offset):
            runtime_event("STATUS", "SUCCESS", "LAUNCHER_RUNTIME", "STARTUP_READY_OBSERVED")
            return "ready", None, None

        if runtime_log_contains_since(startup_abort_marker, log_start_offset):
            runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_ABORT_OBSERVED")
            return "startup_aborted", None, None

        if (
            not warned_within_window
            and time.monotonic() >= warn_deadline
            and proc.poll() is None
        ):
            runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_READY_NOT_OBSERVED_WITHIN_WINDOW")
            warned_within_window = True

        if (
            not stall_confirmed
            and time.monotonic() >= stall_deadline
            and proc.poll() is None
        ):
            runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_READY_STALL_CONFIRMED")
            stall_confirmed = True
            if not abort_requested_on_stall and not runtime_log_contains_since(ready_marker, log_start_offset):
                if request_startup_abort("confirmed stall"):
                    runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_ABORT_REQUESTED_ON_CONFIRMED_STALL")
                    abort_requested_on_stall = True

        try:
            stdout_text, stderr_text = proc.communicate(timeout=STARTUP_OBSERVE_POLL_SECONDS)
            break
        except subprocess.TimeoutExpired:
            continue

    if runtime_log_contains_since(ready_marker, log_start_offset):
        runtime_event("STATUS", "SUCCESS", "LAUNCHER_RUNTIME", "STARTUP_READY_OBSERVED")
        return "ready", stdout_text, stderr_text

    if runtime_log_contains_since(startup_abort_marker, log_start_offset):
        runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_ABORT_OBSERVED")
        return "startup_aborted", stdout_text, stderr_text

    runtime_event("STATUS", "WARNING", "LAUNCHER_RUNTIME", "STARTUP_READY_NOT_OBSERVED_BEFORE_EXIT")
    return "not_ready_before_exit", stdout_text, stderr_text


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
        f.write("JARVIS CRASH REPORT\n")
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
    if HARNESS_DISABLE_DIAGNOSTICS:
        runtime("Diagnostics UI launch skipped by harness seam")
        runtime_event("STATUS", "SKIP", "DIAGNOSTICS_UI", "HARNESS_DISABLED")
        return None

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
    if HARNESS_DISABLE_VOICE:
        runtime(f"VOICE skipped by harness seam: {spoken_text}")
        runtime_event("VOICE", "SKIP", spoken_text, "HARNESS_DISABLED")
        return 0

    if not os.path.exists(VOICE_SCRIPT):
        runtime(f"Voice script missing: {VOICE_SCRIPT}")
        runtime_event("STATUS", "FAIL", "VOICE_SCRIPT", "MISSING")
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
    runtime_event("VOICE", "END", spoken_text, f"EXIT={result.returncode}")
    return result.returncode


def run_renderer():
    runtime(f"Starting renderer: {TARGET_SCRIPT}")
    runtime_event("STATUS", "START", "RENDERER_PROCESS")
    log_start_offset = os.path.getsize(RUNTIME_FILE) if os.path.exists(RUNTIME_FILE) else 0
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
        **hidden_window_kwargs(),
    )
    runtime(f"Renderer PID: {proc.pid}")
    runtime_event("STATUS", "SUCCESS", "RENDERER_PROCESS_SPAWN", f"PID={proc.pid}")
    startup_observation, stdout_text, stderr_text = observe_renderer_startup_ready(proc, log_start_offset)
    if stdout_text is None and stderr_text is None:
        stdout_text, stderr_text = proc.communicate()
    runtime(f"Renderer exit code: {proc.returncode}")
    runtime_event("STATUS", "END", "RENDERER_PROCESS", f"EXIT={proc.returncode}")
    failure_cause = extract_renderer_failure_cause(stderr_text or "", stdout_text or "")
    failure_origin = extract_renderer_failure_origin(stderr_text or "", stdout_text or "")
    stderr_excerpt_lines = extract_renderer_stderr_excerpt(stderr_text or "", failure_cause, failure_origin)
    startup_aborted = startup_observation == "startup_aborted"
    if proc.returncode != 0 and failure_cause:
        runtime(f"Renderer failure cause: {failure_cause}")
    if proc.returncode != 0 and failure_origin:
        runtime(failure_origin)
    return proc.returncode, failure_cause, failure_origin, stderr_excerpt_lines, startup_aborted


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

    def log_single_instance_event(event):
        runtime(f"Single-instance flow: {event}")
        runtime_event("STATUS", "TRACE", "LAUNCHER_RUNTIME", event)

    if not acquire_or_prompt_replace(
        runtime_instance_guard,
        runtime_relaunch_signal,
        "Jarvis Session Active",
        "Jarvis is already active on this computer.\n\nDo you want to close the current Jarvis session and relaunch Desktop Jarvis now?",
        eyebrow_text="DESKTOP JARVIS",
        primary_button_text="Relaunch Desktop Jarvis",
        secondary_button_text="Keep Current Session",
        event_logger=log_single_instance_event,
    ):
        runtime("Launcher start blocked: Jarvis is already running")
        runtime_event("STATUS", "SKIP", "LAUNCHER_RUNTIME", "ALREADY_RUNNING")
        return 0

    ensure_crash_dir("launcher startup")
    reset_status()

    runtime("==== Jarvis runtime started ====")
    runtime_event("STATUS", "START", "LAUNCHER_RUNTIME")
    runtime(run_id)
    runtime(ENVIRONMENT_FINGERPRINT)
    runtime(f"Python executable: {pythonw()}")
    runtime(f"Working directory: {ROOT_DIR}")
    runtime(f"Renderer target: {TARGET_SCRIPT}")

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
            return 0

        runtime(f"Renderer launch attempt {attempt}/{MAX_RECOVERY_ATTEMPTS}")
        runtime_event("STATUS", "START", "RECOVERY_ATTEMPT", f"INDEX={attempt}", f"MAX={MAX_RECOVERY_ATTEMPTS}")
        write_status("TRACE", f"Renderer launch attempt {attempt}/{MAX_RECOVERY_ATTEMPTS}")
        time.sleep(0.18)

        last_code, failure_cause, failure_origin, stderr_excerpt_lines, startup_aborted = run_renderer()

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

        if last_code == 0:
            runtime("Renderer exited normally")
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
            return 0

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


if __name__ == "__main__":
    main()
