import datetime
import json
import os
import re
import subprocess
import sys
import time


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "desktop_entrypoint_validation")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")

LAUNCHER_SCRIPT = os.path.join(ROOT_DIR, "desktop", "orin_desktop_launcher.pyw")
DEFAULT_TARGET_SCRIPT = os.path.join(ROOT_DIR, "desktop", "orin_desktop_main.py")
EXPECTED_DEFAULT_TARGET_LINE = re.compile(
    r'DEFAULT_TARGET_SCRIPT\s*=\s*os\.path\.join\(ROOT_DIR,\s*"desktop",\s*"orin_desktop_main\.py"\)'
)

EXPECTED_MILESTONES = [
    "RENDERER_MAIN|START",
    "RENDERER_MAIN|QAPPLICATION_CREATED",
    "RENDERER_MAIN|VISUAL_HTML_RESOLVED",
    "RENDERER_MAIN|WINDOW_CONSTRUCTED",
    "RENDERER_MAIN|SHUTDOWN_BUS_READY",
    "RENDERER_MAIN|HOTKEYS_STARTED",
    "RENDERER_MAIN|WINDOW_SHOW_REQUESTED",
    "RENDERER_MAIN|STARTUP_READY",
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


def run_validation():
    ensure_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    launcher_text = read_text(LAUNCHER_SCRIPT)
    launcher_line = launcher_default_target_line()

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    runtime_log = os.path.join(BASE_LOG_ROOT, f"Runtime_{stamp}.txt")

    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"

    proc = subprocess.Popen(
        [
            sys.executable,
            DEFAULT_TARGET_SCRIPT,
            "--runtime-log",
            runtime_log,
        ],
        cwd=ROOT_DIR,
        env=env,
        **hidden_subprocess_kwargs(),
    )

    ready_seen = False
    deadline = time.time() + 20.0
    runtime_lines = []

    try:
        while time.time() < deadline:
            if os.path.exists(runtime_log):
                runtime_lines = read_lines(runtime_log)
                if any("RENDERER_MAIN|STARTUP_READY" in line for line in runtime_lines):
                    ready_seen = True
                    break

            if proc.poll() is not None:
                break

            time.sleep(0.25)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    stdout_text, stderr_text = proc.communicate()
    runtime_lines = read_lines(runtime_log)

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
            os.path.exists(runtime_log),
            runtime_log,
        ),
    }

    for milestone in EXPECTED_MILESTONES:
        checks[f"milestone::{milestone}"] = line_status(
            any(milestone in line for line in runtime_lines),
            milestone,
        )

    checks["startup_ready_reached_before_termination"] = line_status(
        ready_seen,
        "RENDERER_MAIN|STARTUP_READY",
    )
    checks["traceback_absent"] = line_status(
        "Traceback" not in stderr_text,
        stderr_text.strip() or "no traceback in stderr",
    )

    return {
        "branch_state": detect_branch_state(),
        "runtime_log": runtime_log,
        "target_script": DEFAULT_TARGET_SCRIPT,
        "launcher_line": launcher_line,
        "stdout": stdout_text.strip(),
        "stderr": stderr_text.strip(),
        "checks": checks,
    }


def build_report_text(report_path, result, overall_ok):
    lines = [
        "JARVIS DESKTOP ENTRYPOINT VALIDATION",
        f"Report: {report_path}",
        f"Branch: {result['branch_state']}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
        f"Default target: {result['target_script']}",
        f"Launcher target line: {result['launcher_line']}",
        f"Runtime log: {result['runtime_log']}",
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

    result = run_validation()
    failures = [key for key, value in result["checks"].items() if not value["ok"]]
    overall_ok = not failures

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"DesktopEntrypointValidationReport_{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"DesktopEntrypointValidationReport_{stamp}.json")

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

    if open_report and os.name == "nt":
        try:
            os.startfile(report_path)
        except Exception:
            pass

    print(report_text)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
