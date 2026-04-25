import datetime
import json
import os
import subprocess
import sys
import time


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "boot_transition_verification")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")
BOOT_RUNTIME_ROOT = os.path.join(DEV_LOGS_DIR, "boot_auto_handoff_skip_import")
MAIN_SCRIPT = os.path.join(ROOT_DIR, "main.py")
LEGACY_DEV_LAUNCHER = os.path.join(ROOT_DIR, "dev", "launchers", "launch_orin_main_dev.vbs")
RUNTIME_RELAUNCH_EVENT = r"Local\JarvisRuntimeRelaunchRequestV1"

EXPECTED_SEQUENCE = [
    "BOOT_MAIN|START|profile=auto_handoff_skip_import|audio=quiet",
    "BOOT_MAIN|BOOT_SEQUENCE_START",
    "BOOT_MAIN|FIRST_COMMAND_ACCEPTED|command=engage_hud",
    "BOOT_MAIN|IMPORT_CHOICE_RESOLVED|choice=skip",
    "BOOT_MAIN|TRANSITION_BEGIN|import_home=false",
    "BOOT_MAIN|DESKTOP_SHOW_REQUESTED",
    "BOOT_MAIN|BOOT_WINDOWS_HIDDEN",
    "BOOT_MAIN|DESKTOP_VISIBLE",
    "BOOT_MAIN|DESKTOP_STATE_COMMITTED|state=dormant",
    "BOOT_MAIN|DESKTOP_SETTLED|state=dormant",
]

CLEAN_EXIT_MARKERS = [
    "BOOT_MAIN|RELAUNCH_REQUEST_RECEIVED",
    "BOOT_MAIN|SHUTDOWN_REQUESTED",
    "BOOT_MAIN|EVENT_LOOP_EXIT|code=0",
]

EXPECTED_LEGACY_DEV_LAUNCHER_MARKERS = (
    "--boot-profile manual",
    "--audio-mode voice",
)


def hidden_subprocess_kwargs():
    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }

    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        kwargs["startupinfo"] = startupinfo
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    return kwargs


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.rstrip("\r\n") for line in f]


def read_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def latest_file_matching(folder_path, prefix):
    if not os.path.isdir(folder_path):
        return ""

    best_path = ""
    best_mtime = -1.0
    for name in os.listdir(folder_path):
        if not name.lower().startswith(prefix.lower()):
            continue
        path = os.path.join(folder_path, name)
        if not os.path.isfile(path):
            continue
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        if mtime >= best_mtime:
            best_mtime = mtime
            best_path = path
    return best_path


def line_status(ok, detail):
    return {"ok": bool(ok), "detail": detail}


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "unavailable"


def find_new_runtime_file(before_set, timeout_seconds=25.0):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        current_files = {
            name for name in os.listdir(BOOT_RUNTIME_ROOT)
            if name.lower().startswith("runtime_") and name.lower().endswith("_quiet.txt")
        } if os.path.isdir(BOOT_RUNTIME_ROOT) else set()
        new_files = sorted(current_files - before_set)
        if new_files:
            return os.path.join(BOOT_RUNTIME_ROOT, new_files[-1])
        time.sleep(0.1)
    return ""


def wait_for_markers(runtime_log, expected_markers, timeout_seconds=45.0):
    deadline = time.time() + timeout_seconds
    runtime_lines = []
    while time.time() < deadline:
        runtime_lines = read_lines(runtime_log)
        if all(any(marker in line for line in runtime_lines) for marker in expected_markers):
            return runtime_lines, True
        time.sleep(0.2)
    return runtime_lines, False


def marker_line_indexes(runtime_lines, markers):
    indexes = {}
    for marker in markers:
        indexes[marker] = -1
        for index, line in enumerate(runtime_lines):
            if marker in line:
                indexes[marker] = index
                break
    return indexes


def send_runtime_relaunch_signal():
    from desktop.single_instance import NamedSignal

    signal = NamedSignal(RUNTIME_RELAUNCH_EVENT)
    try:
        return bool(signal.signal())
    finally:
        signal.close()


def run_verification():
    ensure_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)
    legacy_dev_launcher_text = read_text(LEGACY_DEV_LAUNCHER)

    before_files = {
        name for name in os.listdir(BOOT_RUNTIME_ROOT)
        if name.lower().startswith("runtime_") and name.lower().endswith("_quiet.txt")
    } if os.path.isdir(BOOT_RUNTIME_ROOT) else set()

    proc = subprocess.Popen(
        [
            sys.executable,
            MAIN_SCRIPT,
            "--boot-profile",
            "auto_handoff_skip_import",
            "--audio-mode",
            "quiet",
        ],
        cwd=ROOT_DIR,
        **hidden_subprocess_kwargs(),
    )

    runtime_log = find_new_runtime_file(before_files)
    runtime_lines = []
    reached_expected_sequence = False
    signal_sent = False

    try:
        if runtime_log:
            runtime_lines, reached_expected_sequence = wait_for_markers(runtime_log, EXPECTED_SEQUENCE)
    finally:
        signal_sent = send_runtime_relaunch_signal()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    stdout_text, stderr_text = proc.communicate()
    runtime_lines = read_lines(runtime_log) if runtime_log else []
    marker_indexes = marker_line_indexes(runtime_lines, EXPECTED_SEQUENCE)
    ordered = all(
        marker_indexes[EXPECTED_SEQUENCE[index]] >= 0
        and marker_indexes[EXPECTED_SEQUENCE[index + 1]] >= 0
        and marker_indexes[EXPECTED_SEQUENCE[index]] < marker_indexes[EXPECTED_SEQUENCE[index + 1]]
        for index in range(len(EXPECTED_SEQUENCE) - 1)
    )

    checks = {
        "runtime_log_created": line_status(bool(runtime_log and os.path.exists(runtime_log)), runtime_log or "missing"),
        "expected_sequence_reached": line_status(reached_expected_sequence, "all expected handoff markers observed"),
        "handoff_marker_order_valid": line_status(ordered, json.dumps(marker_indexes, indent=2)),
        "runtime_cleanup_signal_sent": line_status(signal_sent, RUNTIME_RELAUNCH_EVENT),
        "legacy_dev_launcher_explicit_boot_contract": line_status(
            all(marker in legacy_dev_launcher_text for marker in EXPECTED_LEGACY_DEV_LAUNCHER_MARKERS),
            LEGACY_DEV_LAUNCHER,
        ),
    }

    for marker in EXPECTED_SEQUENCE:
        checks[f"marker::{marker}"] = line_status(
            any(marker in line for line in runtime_lines),
            marker,
        )

    for marker in CLEAN_EXIT_MARKERS:
        checks[f"cleanup::{marker}"] = line_status(
            any(marker in line for line in runtime_lines),
            marker,
        )

    checks["process_exit_zero"] = line_status(proc.returncode == 0, f"exit={proc.returncode}")
    checks["traceback_absent"] = line_status(
        "Traceback" not in stdout_text and "Traceback" not in stderr_text,
        (stderr_text or stdout_text or "no traceback in stdout/stderr").strip(),
    )

    return {
        "branch_state": detect_branch_state(),
        "runtime_log": runtime_log,
        "checks": checks,
        "stdout": stdout_text.strip(),
        "stderr": stderr_text.strip(),
    }


def build_report_text(report_path, result, overall_ok):
    lines = [
        "BOOT TO DESKTOP HANDOFF VERIFICATION",
        f"Report: {report_path}",
        f"Branch: {result['branch_state']}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
        f"Boot runtime log: {result['runtime_log'] or 'missing'}",
        "",
        "Checks:",
    ]

    for key, value in result["checks"].items():
        lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

    if result["stdout"]:
        lines.extend(["", "stdout:", result["stdout"]])
    if result["stderr"]:
        lines.extend(["", "stderr:", result["stderr"]])

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    result = run_verification()
    failures = [key for key, value in result["checks"].items() if not value["ok"]]
    overall_ok = not failures

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"BootTransitionVerificationReport_{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"BootTransitionVerificationReport_{stamp}.json")

    report_text = build_report_text(report_path, result, overall_ok)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(report_text)

    if open_report:
        try:
            os.startfile(report_path)
        except Exception:
            pass

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
