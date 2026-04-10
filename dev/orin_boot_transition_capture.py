import datetime
import json
import os
import subprocess
import sys
import time

from PySide6.QtGui import QGuiApplication


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from desktop.single_instance import NamedSignal  # noqa: E402


DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "boot_transition_capture")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")
CAPTURES_DIR = os.path.join(BASE_LOG_ROOT, "captures")
BOOT_RUNTIME_ROOT = os.path.join(DEV_LOGS_DIR, "boot_auto_handoff_skip_import")
MAIN_SCRIPT = os.path.join(ROOT_DIR, "main.py")
RUNTIME_RELAUNCH_EVENT = "Local\\JarvisRuntimeRelaunchRequestV1"

REPORT_PREFIX = "BootTransitionCaptureReport_"
CAPTURE_MARKERS = (
    ("01_command_accepted", "BOOT_MAIN|FIRST_COMMAND_ACCEPTED|command=engage_hud"),
    ("02_transition_begin", "BOOT_MAIN|TRANSITION_BEGIN|import_home=false"),
    ("03_desktop_show_requested", "BOOT_MAIN|DESKTOP_SHOW_REQUESTED"),
    ("04_boot_hidden", "BOOT_MAIN|BOOT_WINDOWS_HIDDEN"),
    ("05_desktop_visible", "BOOT_MAIN|DESKTOP_VISIBLE"),
    ("06_desktop_committed", "BOOT_MAIN|DESKTOP_STATE_COMMITTED|state=dormant"),
    ("07_desktop_settled", "BOOT_MAIN|DESKTOP_SETTLED|state=dormant"),
)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    except Exception:
        return "unavailable"


def latest_file_matching(folder_path, prefix, suffix=""):
    if not os.path.isdir(folder_path):
        return ""

    best_path = ""
    best_mtime = -1.0
    for name in os.listdir(folder_path):
        if not name.lower().startswith(prefix.lower()):
            continue
        if suffix and not name.lower().endswith(suffix.lower()):
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


def matching_files(folder_path, prefix, suffix):
    if not os.path.isdir(folder_path):
        return set()

    matches = set()
    for name in os.listdir(folder_path):
        if not name.lower().startswith(prefix.lower()):
            continue
        if suffix and not name.lower().endswith(suffix.lower()):
            continue
        path = os.path.join(folder_path, name)
        if os.path.isfile(path):
            matches.add(os.path.abspath(path))
    return matches


def read_text(path):
    if not path or not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def line_status(ok, detail):
    return {"ok": bool(ok), "detail": detail}


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


def resolve_python_gui_executable():
    current = os.path.abspath(sys.executable)
    folder = os.path.dirname(current)
    if os.path.basename(current).lower() == "pythonw.exe":
        return current
    candidate = os.path.join(folder, "pythonw.exe")
    if os.path.isfile(candidate):
        return candidate
    return current


def wait_for_runtime_log(before_logs, timeout_seconds=20):
    deadline = time.time() + max(5, timeout_seconds)
    latest = ""
    while time.time() < deadline:
        current_logs = matching_files(BOOT_RUNTIME_ROOT, "Runtime_", ".txt")
        new_logs = current_logs - before_logs
        if len(new_logs) == 1:
            return sorted(new_logs)[0]
        if new_logs:
            latest = latest_file_matching(BOOT_RUNTIME_ROOT, "Runtime_", ".txt")
            if latest:
                return latest
        time.sleep(0.2)
    return latest


def capture_primary_screen(screen, capture_path):
    pixmap = screen.grabWindow(0, 0, 0, screen.geometry().width(), screen.geometry().height())
    return bool(pixmap.save(capture_path, "PNG"))


def build_report_text(branch_state, report_path, runtime_log_path, capture_dir, captures, checks, stdout_text, stderr_text):
    lines = [
        "BOOT TRANSITION CAPTURE",
        f"Report: {report_path}",
        f"Branch: {branch_state}",
        f"Overall Result: {'PASS' if all(item['ok'] for item in checks.values()) else 'FAIL'}",
        "",
        f"Boot runtime log: {runtime_log_path}",
        f"Capture directory: {capture_dir}",
        "",
        "Checks:",
    ]

    for key, value in checks.items():
        lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

    lines.append("")
    lines.append("Captures:")
    if captures:
        for capture in captures:
            lines.append(
                f"  {capture['label']} :: {capture['marker']} :: {capture['path']} :: saved={capture['saved']}"
            )
    else:
        lines.append("  none")

    if stdout_text:
        lines.append("")
        lines.append("stdout:")
        lines.append(stdout_text)

    if stderr_text:
        lines.append("")
        lines.append("stderr:")
        lines.append(stderr_text)

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    ensure_dir(REPORTS_DIR)
    ensure_dir(CAPTURES_DIR)

    app = QGuiApplication.instance() or QGuiApplication([])
    screen = app.primaryScreen()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = os.path.join(CAPTURES_DIR, stamp)
    ensure_dir(capture_dir)

    before_logs = matching_files(BOOT_RUNTIME_ROOT, "Runtime_", ".txt")
    runtime_process = None
    signal = NamedSignal(RUNTIME_RELAUNCH_EVENT)
    runtime_log_path = ""
    captures = []
    stdout_text = ""
    stderr_text = ""
    signal_sent = False

    try:
        python_executable = resolve_python_gui_executable()
        runtime_process = subprocess.Popen(
            [
                python_executable,
                MAIN_SCRIPT,
                "--boot-profile",
                "auto_handoff_skip_import",
                "--audio-mode",
                "quiet",
            ],
            cwd=ROOT_DIR,
            **hidden_subprocess_kwargs(),
        )

        runtime_log_path = wait_for_runtime_log(before_logs, timeout_seconds=20)
        captured_labels = set()
        deadline = time.time() + 60

        while time.time() < deadline and len(captured_labels) < len(CAPTURE_MARKERS):
            app.processEvents()
            log_text = read_text(runtime_log_path)
            for label, marker in CAPTURE_MARKERS:
                if label in captured_labels or marker not in log_text:
                    continue
                capture_path = os.path.join(capture_dir, f"{label}.png")
                saved = bool(screen and capture_primary_screen(screen, capture_path))
                captures.append(
                    {
                        "label": label,
                        "marker": marker,
                        "path": capture_path,
                        "saved": saved,
                    }
                )
                captured_labels.add(label)
            if "BOOT_MAIN|DESKTOP_SETTLED|state=dormant" in log_text and len(captured_labels) >= 5:
                break
            time.sleep(0.2)

        time.sleep(0.5)
        signal_sent = signal.signal()

        if runtime_process is not None:
            try:
                stdout_text, stderr_text = runtime_process.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                runtime_process.kill()
                stdout_text, stderr_text = runtime_process.communicate(timeout=5)
    finally:
        if runtime_process is not None and runtime_process.poll() is None:
            try:
                runtime_process.kill()
            except Exception:
                pass
        app.processEvents()

    runtime_text = read_text(runtime_log_path)
    capture_saved_count = sum(1 for capture in captures if capture["saved"])

    checks = {
        "primary_screen_present": line_status(
            screen is not None,
            screen.name() if screen else "missing primary screen",
        ),
        "runtime_log_created": line_status(
            bool(runtime_log_path) and os.path.isfile(runtime_log_path),
            runtime_log_path or "missing runtime log",
        ),
        "expected_sequence_reached": line_status(
            all(marker in runtime_text for _, marker in CAPTURE_MARKERS),
            "all capture markers observed" if runtime_text else "capture markers missing",
        ),
        "captures_saved": line_status(
            capture_saved_count == len(CAPTURE_MARKERS),
            f"saved {capture_saved_count} of {len(CAPTURE_MARKERS)} capture(s)",
        ),
        "cleanup_signal_sent": line_status(
            signal_sent,
            RUNTIME_RELAUNCH_EVENT if signal_sent else "signal failed",
        ),
        "cleanup_markers_present": line_status(
            "BOOT_MAIN|RELAUNCH_REQUEST_RECEIVED" in runtime_text
            and "BOOT_MAIN|SHUTDOWN_REQUESTED" in runtime_text
            and "BOOT_MAIN|EVENT_LOOP_EXIT|code=0" in runtime_text,
            "cleanup markers observed" if runtime_text else "cleanup markers missing",
        ),
        "process_exit_zero": line_status(
            runtime_process is not None and runtime_process.returncode == 0,
            f"exit={runtime_process.returncode if runtime_process is not None else 'missing'}",
        ),
        "traceback_absent": line_status(
            "Traceback" not in stdout_text and "Traceback" not in stderr_text and "Traceback" not in runtime_text,
            "no traceback in runtime/stdout/stderr" if runtime_text or stdout_text or stderr_text else "traceback check unavailable",
        ),
    }

    branch_state = detect_branch_state()
    report_path = os.path.join(REPORTS_DIR, f"{REPORT_PREFIX}{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"{REPORT_PREFIX}{stamp}.json")
    report_text = build_report_text(
        branch_state,
        report_path,
        runtime_log_path,
        capture_dir,
        captures,
        checks,
        stdout_text.strip(),
        stderr_text.strip(),
    )

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report_text)

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "branch_state": branch_state,
                "runtime_log_path": runtime_log_path,
                "capture_dir": capture_dir,
                "captures": captures,
                "checks": checks,
                "report_path": report_path,
            },
            handle,
            indent=2,
            sort_keys=True,
        )

    if open_report and os.name == "nt":
        try:
            os.startfile(report_path)
        except Exception:
            pass

    print(report_text)
    return 0 if all(item["ok"] for item in checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
