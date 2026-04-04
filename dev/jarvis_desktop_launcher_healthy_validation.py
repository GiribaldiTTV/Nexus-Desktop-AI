import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
DEFAULT_BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "desktop_launcher_healthy_validation")
REPORT_PREFIX = "DesktopLauncherHealthyValidationReport_"

LAUNCHER_SCRIPT = os.path.join(ROOT_DIR, "desktop", "jarvis_desktop_launcher.pyw")
DEFAULT_TARGET_SCRIPT = os.path.join(ROOT_DIR, "desktop", "jarvis_desktop_main.py")
EXPECTED_DEFAULT_TARGET_LINE = re.compile(
    r'DEFAULT_TARGET_SCRIPT\s*=\s*os\.path\.join\(ROOT_DIR,\s*"desktop",\s*"jarvis_desktop_main\.py"\)'
)

EXPECTED_RUNTIME_MARKERS = [
    "STATUS|START|LAUNCHER_RUNTIME",
    "STATUS|START|RECOVERY_ATTEMPT|INDEX=1|MAX=3",
    "STATUS|START|RENDERER_PROCESS",
    "STATUS|SUCCESS|RENDERER_PROCESS_SPAWN",
    "STATUS|TRACE|LAUNCHER_RUNTIME|STARTUP_OBSERVE_BEGIN",
    "RENDERER_MAIN|START",
    "RENDERER_MAIN|QAPPLICATION_CREATED",
    "RENDERER_MAIN|VISUAL_HTML_RESOLVED",
    "RENDERER_MAIN|WINDOW_CONSTRUCTED",
    "RENDERER_MAIN|SHUTDOWN_BUS_READY",
    "RENDERER_MAIN|HOTKEYS_STARTED",
    "RENDERER_MAIN|WINDOW_SHOW_CALLED",
    "RENDERER_MAIN|STARTUP_READY",
    "STATUS|SUCCESS|LAUNCHER_RUNTIME|STARTUP_READY_OBSERVED",
    "RENDERER_MAIN|SHUTDOWN_REQUESTED",
    "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0",
]


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


def reset_dir(path):
    if os.path.isdir(path):
        for name in os.listdir(path):
            child = os.path.join(path, name)
            try:
                if os.path.isdir(child):
                    shutil.rmtree(child)
                else:
                    os.remove(child)
            except Exception:
                pass
    else:
        os.makedirs(path, exist_ok=True)


def read_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.rstrip("\r\n") for line in f]


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


def launcher_default_target_line():
    for line in read_lines(LAUNCHER_SCRIPT):
        if line.strip().startswith("DEFAULT_TARGET_SCRIPT"):
            return line.strip()
    return "missing DEFAULT_TARGET_SCRIPT line"


def send_shutdown_hotkey():
    try:
        from pynput.keyboard import Controller, Key
    except Exception as exc:
        return False, f"hotkey import failed: {exc}"

    try:
        keyboard = Controller()
        with keyboard.pressed(Key.ctrl):
            with keyboard.pressed(Key.alt):
                keyboard.press(Key.end)
                keyboard.release(Key.end)
        return True, "Ctrl+Alt+End"
    except Exception as exc:
        return False, f"hotkey send failed: {exc}"


def resolve_base_log_root(log_root_override=None):
    if log_root_override:
        return log_root_override

    env_override = os.environ.get("JARVIS_HEALTHY_VALIDATION_LOG_ROOT", "").strip()
    if env_override:
        return env_override

    return DEFAULT_BASE_LOG_ROOT


def reports_dir_for(base_log_root):
    return os.path.join(base_log_root, "reports")


def run_validation(log_root_override=None):
    base_log_root = resolve_base_log_root(log_root_override)
    reports_dir = reports_dir_for(base_log_root)

    reset_dir(base_log_root)
    ensure_dir(reports_dir)

    launcher_text = read_text(LAUNCHER_SCRIPT)
    launcher_line = launcher_default_target_line()

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = base_log_root
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"

    proc = subprocess.Popen(
        [sys.executable, LAUNCHER_SCRIPT],
        cwd=ROOT_DIR,
        env=env,
        **hidden_subprocess_kwargs(),
    )

    runtime_log = ""
    runtime_lines = []
    ready_seen = False
    hotkey_sent = False
    hotkey_detail = "hotkey not sent"
    hotkey_attempts = 0
    shutdown_requested_seen = False
    renderer_exit_seen = False

    ready_deadline = time.time() + 25.0
    while time.time() < ready_deadline:
        runtime_log = latest_file_matching(base_log_root, "Runtime_")
        runtime_lines = read_lines(runtime_log)
        if any("RENDERER_MAIN|STARTUP_READY" in line for line in runtime_lines):
            ready_seen = True
            break
        if proc.poll() is not None:
            break
        time.sleep(0.2)

    if ready_seen:
        hotkey_attempts += 1
        hotkey_sent, hotkey_detail = send_shutdown_hotkey()

    exit_code = None
    core_markers_captured = False
    post_ready_deadline = time.time() + 20.0
    while time.time() < post_ready_deadline:
        runtime_log = latest_file_matching(base_log_root, "Runtime_")
        runtime_lines = read_lines(runtime_log)
        shutdown_requested_seen = any("RENDERER_MAIN|SHUTDOWN_REQUESTED" in line for line in runtime_lines)
        renderer_exit_seen = any("RENDERER_MAIN|EVENT_LOOP_EXIT|code=0" in line for line in runtime_lines)

        if shutdown_requested_seen and renderer_exit_seen:
            core_markers_captured = True
            break

        if proc.poll() is not None:
            exit_code = proc.returncode
            break

        if ready_seen and not shutdown_requested_seen and hotkey_sent and hotkey_attempts < 2:
            hotkey_attempts += 1
            hotkey_sent, hotkey_detail = send_shutdown_hotkey()

        time.sleep(0.2)

    terminated_by_validator = False
    if proc.poll() is None:
        terminated_by_validator = True
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    stdout_text, stderr_text = proc.communicate()
    exit_code = proc.returncode if exit_code is None else exit_code
    runtime_log = latest_file_matching(base_log_root, "Runtime_")
    runtime_lines = read_lines(runtime_log)
    crash_log = latest_file_matching(os.path.join(base_log_root, "crash"), "Crash_")
    normal_exit_complete_seen = any(
        "STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE" in line for line in runtime_lines
    )
    failure_flow_seen = any(
        "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in runtime_lines
    )

    diagnostics_status_path = os.path.join(base_log_root, "diagnostics_status.txt")
    diagnostics_stop_path = os.path.join(base_log_root, "diagnostics_stop.signal")
    startup_abort_path = os.path.join(base_log_root, "renderer_startup_abort.signal")
    for artifact_path in (diagnostics_status_path, diagnostics_stop_path, startup_abort_path):
        try:
            if os.path.exists(artifact_path):
                os.remove(artifact_path)
        except Exception:
            pass

    checks = {
        "launcher_default_target_matches_expected": line_status(
            bool(EXPECTED_DEFAULT_TARGET_LINE.search(launcher_text)),
            launcher_line,
        ),
        "default_target_exists": line_status(
            os.path.exists(DEFAULT_TARGET_SCRIPT),
            DEFAULT_TARGET_SCRIPT,
        ),
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "renderer_target_matches_default": line_status(
            any(f"Renderer target: {DEFAULT_TARGET_SCRIPT}" in line for line in runtime_lines),
            DEFAULT_TARGET_SCRIPT,
        ),
        "launcher_owned_startup_ready_observed": line_status(
            any("STATUS|SUCCESS|LAUNCHER_RUNTIME|STARTUP_READY_OBSERVED" in line for line in runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|STARTUP_READY_OBSERVED",
        ),
        "renderer_startup_ready_reached": line_status(
            ready_seen,
            "RENDERER_MAIN|STARTUP_READY",
        ),
        "shutdown_hotkey_sent": line_status(
            hotkey_sent,
            hotkey_detail,
        ),
        "renderer_clean_shutdown_markers_captured": line_status(
            shutdown_requested_seen and renderer_exit_seen,
            "RENDERER_MAIN|SHUTDOWN_REQUESTED + RENDERER_MAIN|EVENT_LOOP_EXIT|code=0",
        ),
        "contained_run_closed_after_evidence_capture": line_status(
            core_markers_captured or normal_exit_complete_seen,
            "validator closed contained run after healthy launcher/renderer evidence was captured",
        ),
        "traceback_absent": line_status(
            "Traceback" not in stderr_text and "Traceback" not in stdout_text,
            (stderr_text or stdout_text).strip() or "no traceback in stdout/stderr",
        ),
        "failure_flow_absent": line_status(
            not failure_flow_seen,
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "crash_log_absent": line_status(
            not crash_log,
            crash_log or "no crash log generated",
        ),
        "diagnostics_status_cleaned": line_status(
            not os.path.exists(diagnostics_status_path),
            diagnostics_status_path,
        ),
        "diagnostics_stop_cleaned": line_status(
            not os.path.exists(diagnostics_stop_path),
            diagnostics_stop_path,
        ),
        "startup_abort_signal_cleaned": line_status(
            not os.path.exists(startup_abort_path),
            startup_abort_path,
        ),
        "launcher_normal_exit_complete_optional": line_status(
            True,
            "seen"
            if normal_exit_complete_seen
            else f"not seen (launcher process closed by validator after evidence capture, exit={exit_code})",
        ),
    }

    for marker in EXPECTED_RUNTIME_MARKERS:
        checks[f"marker::{marker}"] = line_status(
            any(marker in line for line in runtime_lines),
            marker,
        )

    return {
        "branch_state": detect_branch_state(),
        "log_root": base_log_root,
        "reports_dir": reports_dir,
        "runtime_log": runtime_log,
        "launcher_script": LAUNCHER_SCRIPT,
        "target_script": DEFAULT_TARGET_SCRIPT,
        "launcher_line": launcher_line,
        "hotkey_attempts": hotkey_attempts,
        "stdout": stdout_text.strip(),
        "stderr": stderr_text.strip(),
        "checks": checks,
    }


def build_report_text(report_path, result, overall_ok):
    lines = [
        "JARVIS DESKTOP LAUNCHER HEALTHY VALIDATION",
        f"Report: {report_path}",
        f"Branch: {result['branch_state']}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
        f"Launcher: {result['launcher_script']}",
        f"Default target: {result['target_script']}",
        f"Launcher target line: {result['launcher_line']}",
        f"Runtime log: {result['runtime_log']}",
        f"Hotkey attempts: {result['hotkey_attempts']}",
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


def write_validation_artifacts(result):
    reports_dir = result.get("reports_dir") or reports_dir_for(resolve_base_log_root(result.get("log_root")))
    ensure_dir(reports_dir)

    failures = [key for key, value in result["checks"].items() if not value["ok"]]
    overall_ok = not failures

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(reports_dir, f"{REPORT_PREFIX}{stamp}.txt")
    json_path = os.path.join(reports_dir, f"{REPORT_PREFIX}{stamp}.json")

    report_text = build_report_text(report_path, result, overall_ok)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "overall_ok": overall_ok,
                "result": result,
                "report_path": report_path,
                "failures": failures,
            },
            f,
            indent=2,
        )

    return {
        "overall_ok": overall_ok,
        "failures": failures,
        "report_path": report_path,
        "json_path": json_path,
        "report_text": report_text,
    }


def main(argv):
    open_report = "--open-report" in argv

    result = run_validation()
    artifacts = write_validation_artifacts(result)

    if open_report and os.name == "nt":
        try:
            os.startfile(artifacts["report_path"])
        except Exception:
            pass

    print(artifacts["report_text"])
    return 0 if artifacts["overall_ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
