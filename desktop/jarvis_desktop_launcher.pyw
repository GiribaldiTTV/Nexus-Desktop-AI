# Version 1.3.2 rev 11 launcher

import os
import sys
import time
import re
import subprocess
import datetime
import platform
import secrets

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_SCRIPT = os.path.join(ROOT_DIR, "jarvis_desktop_main.py")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
CRASH_DIR = os.path.join(LOG_DIR, "crash")
STATUS_FILE = os.path.join(LOG_DIR, "diagnostics_status.txt")
STOP_SIGNAL_FILE = os.path.join(LOG_DIR, "diagnostics_stop.signal")
STARTUP_ABORT_SIGNAL_FILE = os.path.join(LOG_DIR, "renderer_startup_abort.signal")
DIAGNOSTICS_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_diagnostics.pyw")
VOICE_SCRIPT = os.path.join(ROOT_DIR, "Audio", "jarvis_error_voice.py")

MAX_RECOVERY_ATTEMPTS = 3
RECOVERY_COOLDOWN_SECONDS = 1.2
COMPLETE_CLEANUP_DELAY_SECONDS = 0.35
STARTUP_OBSERVE_POLL_SECONDS = 0.05
STARTUP_READY_OBSERVE_WINDOW_SECONDS = 3.0
STARTUP_READY_STALL_CONFIRM_SECONDS = 8.0
STARTUP_ABORT_CONTROL_FLOW_RESULT = "STARTUP_ABORT"

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


def build_incident_summary_lines(
    run_id,
    attempts_used,
    last_code,
    failure_cause="",
    failure_origin="",
    failure_assessment="",
    recovery_outcome="",
    crash_filename="",
    runtime_filename="",
):
    return [
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
        f"Latest crash report: {(crash_filename or '').strip() or 'Unavailable'}",
        f"Latest runtime log: {(runtime_filename or '').strip() or 'Unavailable'}",
    ]


def write_runtime_incident_summary(
    run_id,
    attempts_used,
    last_code,
    failure_cause="",
    failure_origin="",
    failure_assessment="",
    recovery_outcome="",
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
        crash_filename,
        runtime_filename,
    ):
        runtime(line)


def pythonw():
    exe = sys.executable
    alt = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return alt if os.path.exists(alt) else exe


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


def triage_renderer_failure(failure_cause):
    cause = (failure_cause or "").strip()

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


def crash_log(
    message,
    attempts,
    last_code,
    failure_cause="",
    failure_origin="",
    stderr_excerpt_lines=None,
    failure_assessment="",
    recovery_outcome="",
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
    proc = subprocess.Popen([pythonw(), DIAGNOSTICS_SCRIPT, "--runtime-log", RUNTIME_FILE])
    runtime(f"Diagnostics PID: {proc.pid}")
    runtime_event("STATUS", "SUCCESS", "DIAGNOSTICS_UI", f"PID={proc.pid}")
    return proc


def speak(spoken_text, display_text=None):
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
    result = subprocess.run(cmd)
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
    crash_filename="",
    run_id="",
):
    runtime("Beginning final immersive shutdown sequence")
    runtime_event("STATUS", "START", "FINAL_IMMERSIVE_SHUTDOWN")
    speak("Recovery failed.")
    speak("Shutting down.")
    runtime("Final immersive shutdown sequence finished")
    runtime_event("STATUS", "SUCCESS", "FINAL_IMMERSIVE_SHUTDOWN")

    write_status("TRACE", triage_renderer_failure(failure_cause))
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
        "Renderer failed after maximum recovery attempts.",
        attempts_used,
        last_code or -1,
        failure_cause,
        failure_origin,
        stderr_excerpt_lines or [],
        failure_assessment,
        recovery_outcome,
        crash_filename,
        run_id,
    )


def main():
    run_id = create_run_id()
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
    assessment_emitted = False

    for attempt in range(1, MAX_RECOVERY_ATTEMPTS + 1):
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
            return 0

        last_failure_cause = failure_cause or last_failure_cause
        last_failure_origin = failure_origin or last_failure_origin
        last_failure_stderr_excerpt = stderr_excerpt_lines or last_failure_stderr_excerpt
        failure_causes.append((failure_cause or "").strip())
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

    runtime("All recovery attempts exhausted")
    runtime_event("STATUS", "FAIL", "RECOVERY_PIPELINE", "MAX_ATTEMPTS_EXHAUSTED")
    write_status("TRACE", "Recovery attempts exhausted")
    recovery_outcome = "Automatic recovery completed without resolving the renderer failure."
    if (
        len(failure_causes) == MAX_RECOVERY_ATTEMPTS
        and all(failure_causes)
        and len(set(failure_causes)) == 1
    ):
        recovery_outcome = "Automatic recovery did not change the underlying renderer failure."
        write_status("SUMMARY", "Automatic recovery did not change the underlying renderer failure.")
        write_status("TRACE", "Same failure cause persisted across all recovery attempts.")
    write_status("SUMMARY", "Automatic recovery has completed. Manual investigation is required.")
    crash_filename = f"Crash_{RUN_ID_STEM}.txt"
    write_status("SUMMARY", "I have prepared the latest crash report and runtime log. Review the crash report first.")
    finalize_failure(
        MAX_RECOVERY_ATTEMPTS,
        last_code,
        last_failure_cause,
        last_failure_origin,
        last_failure_stderr_excerpt,
        last_failure_assessment,
        recovery_outcome,
        crash_filename,
        run_id,
    )
    write_runtime_incident_summary(
        run_id,
        MAX_RECOVERY_ATTEMPTS,
        last_code or -1,
        last_failure_cause,
        last_failure_origin,
        last_failure_assessment,
        recovery_outcome,
        crash_filename,
        os.path.basename(RUNTIME_FILE),
    )
    write_runtime_stderr_excerpt(last_failure_stderr_excerpt)
    runtime_event("STATUS", "SUCCESS", "LAUNCHER_RUNTIME", "FAILURE_FLOW_COMPLETE")


if __name__ == "__main__":
    main()
