import datetime
import json
import os
import shutil
import subprocess
import sys
import time


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "startup_snapshot_harness_validation")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")
LIVE_LOG_ROOT = os.path.join(ROOT_DIR, "logs")
LAUNCHER_SCRIPT = os.path.join(ROOT_DIR, "desktop", "orin_desktop_launcher.pyw")
FAILURE_TARGET_SCRIPT = os.path.join(ROOT_DIR, "dev", "targets", "orin_manual_failure_target.pyw")

READY_MARKER = "RENDERER_MAIN|STARTUP_READY"
SNAPSHOT_SUCCESS_MARKER = "RENDERER_MAIN|STARTUP_SNAPSHOT|label="
SNAPSHOT_FAILURE_MARKER = "RENDERER_MAIN|STARTUP_SNAPSHOT_FAILED|label="
FAILURE_FLOW_COMPLETE_MARKER = "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE"
REPORT_PREFIX = "StartupSnapshotHarnessValidationReport_"
SCENARIOS = (
    {
        "name": "healthy_startup",
        "target_script": "",
        "expect_ready": True,
        "expect_snapshot": True,
        "expect_failure_flow": False,
    },
    {
        "name": "failure_target",
        "target_script": FAILURE_TARGET_SCRIPT,
        "expect_ready": False,
        "expect_snapshot": False,
        "expect_failure_flow": True,
    },
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


def read_lines(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return [line.rstrip("\r\n") for line in handle]


def line_status(ok, detail):
    return {"ok": bool(ok), "detail": detail}


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


def snapshot_tree(path_root):
    if not os.path.isdir(path_root):
        return {}

    snapshot = {}
    for root, _, files in os.walk(path_root):
        for name in files:
            path = os.path.join(root, name)
            try:
                stat = os.stat(path)
            except OSError:
                continue
            snapshot[os.path.abspath(path)] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    except Exception:
        return "unavailable"


def terminate_process_tree(proc):
    if proc.poll() is not None:
        return False

    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                cwd=ROOT_DIR,
                timeout=10,
                **hidden_subprocess_kwargs(),
            )
        except Exception:
            pass

        deadline = time.time() + 5.0
        while time.time() < deadline:
            if proc.poll() is not None:
                return True
            time.sleep(0.1)

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    return True


def run_scenario(scenario):
    scenario_name = scenario["name"]
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    log_root = os.path.join(scenario_root, "logs")
    snapshot_dir = os.path.join(scenario_root, "startup_snapshots")
    expect_ready = bool(scenario["expect_ready"])
    expect_snapshot = bool(scenario["expect_snapshot"])
    expect_failure_flow = bool(scenario["expect_failure_flow"])

    reset_dir(scenario_root)
    snapshot_dir_abs = os.path.abspath(snapshot_dir)
    log_root_abs = os.path.abspath(log_root)
    live_log_snapshot_before = snapshot_tree(LIVE_LOG_ROOT)

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = log_root_abs
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["JARVIS_HARNESS_STARTUP_SNAPSHOT_DIR"] = snapshot_dir_abs
    env["QT_QPA_PLATFORM"] = "offscreen"
    if scenario["target_script"]:
        env["JARVIS_HARNESS_TARGET_SCRIPT"] = os.path.abspath(scenario["target_script"])
    else:
        env.pop("JARVIS_HARNESS_TARGET_SCRIPT", None)

    proc = subprocess.Popen(
        [sys.executable, LAUNCHER_SCRIPT],
        cwd=ROOT_DIR,
        env=env,
        **hidden_subprocess_kwargs(),
    )

    runtime_log = ""
    runtime_lines = []
    ready_seen = False
    failure_flow_complete_seen = False
    snapshot_events = []
    snapshot_failures = []

    ready_deadline = time.time() + 25.0
    while time.time() < ready_deadline:
        runtime_log = latest_file_matching(log_root_abs, "Runtime_")
        runtime_lines = read_lines(runtime_log)
        ready_seen = any(READY_MARKER in line for line in runtime_lines)
        failure_flow_complete_seen = any(FAILURE_FLOW_COMPLETE_MARKER in line for line in runtime_lines)
        snapshot_events = [line for line in runtime_lines if SNAPSHOT_SUCCESS_MARKER in line]
        snapshot_failures = [line for line in runtime_lines if SNAPSHOT_FAILURE_MARKER in line]

        if expect_snapshot and ready_seen and snapshot_events:
            break
        if expect_failure_flow and failure_flow_complete_seen:
            break
        if proc.poll() is not None:
            break
        time.sleep(0.2)

    snapshot_wait_deadline = time.time() + 6.0
    while expect_snapshot and ready_seen and time.time() < snapshot_wait_deadline:
        runtime_log = latest_file_matching(log_root_abs, "Runtime_")
        runtime_lines = read_lines(runtime_log)
        failure_flow_complete_seen = any(FAILURE_FLOW_COMPLETE_MARKER in line for line in runtime_lines)
        snapshot_events = [line for line in runtime_lines if SNAPSHOT_SUCCESS_MARKER in line]
        snapshot_failures = [line for line in runtime_lines if SNAPSHOT_FAILURE_MARKER in line]
        if snapshot_events:
            break
        if proc.poll() is not None:
            break
        time.sleep(0.2)

    terminated_by_validator = False
    if proc.poll() is None:
        terminated_by_validator = terminate_process_tree(proc)

    stdout_text, stderr_text = proc.communicate()
    exit_code = proc.returncode
    runtime_log = latest_file_matching(log_root_abs, "Runtime_")
    runtime_lines = read_lines(runtime_log)
    failure_flow_complete_seen = any(FAILURE_FLOW_COMPLETE_MARKER in line for line in runtime_lines)
    snapshot_events = [line for line in runtime_lines if SNAPSHOT_SUCCESS_MARKER in line]
    snapshot_failures = [line for line in runtime_lines if SNAPSHOT_FAILURE_MARKER in line]

    snapshot_files = []
    if os.path.isdir(snapshot_dir_abs):
        for name in sorted(os.listdir(snapshot_dir_abs)):
            path = os.path.join(snapshot_dir_abs, name)
            if os.path.isfile(path):
                snapshot_files.append(os.path.abspath(path))

    live_log_snapshot_after = snapshot_tree(LIVE_LOG_ROOT)

    checks = {
        "launcher_script_exists": line_status(os.path.exists(LAUNCHER_SCRIPT), LAUNCHER_SCRIPT),
        "runtime_log_created": line_status(bool(runtime_log and os.path.exists(runtime_log)), runtime_log or "missing runtime log"),
        "snapshot_failure_events_absent": line_status(not snapshot_failures, snapshot_failures[0] if snapshot_failures else "no snapshot failures"),
        "live_root_logs_unchanged": line_status(
            live_log_snapshot_before == live_log_snapshot_after,
            "live root logs unchanged",
        ),
        "traceback_absent": line_status(
            "Traceback" not in stderr_text,
            stderr_text.strip() or "no traceback in stderr",
        ),
    }

    if scenario["target_script"]:
        checks["target_script_exists"] = line_status(
            os.path.exists(scenario["target_script"]),
            os.path.abspath(scenario["target_script"]),
        )
        checks["startup_ready_absent"] = line_status(not ready_seen, READY_MARKER)
        checks["failure_flow_complete_seen"] = line_status(
            failure_flow_complete_seen,
            FAILURE_FLOW_COMPLETE_MARKER,
        )
        checks["snapshot_success_events_absent"] = line_status(
            not snapshot_events,
            snapshot_events[0] if snapshot_events else "no startup snapshot events",
        )
        checks["snapshot_files_absent"] = line_status(
            not snapshot_files,
            "no startup snapshot files",
        )
        checks["snapshot_dir_absent_or_empty"] = line_status(
            (not os.path.isdir(snapshot_dir_abs)) or not snapshot_files,
            snapshot_dir_abs,
        )
    else:
        checks["startup_ready_seen"] = line_status(ready_seen, READY_MARKER)
        checks["snapshot_dir_created"] = line_status(os.path.isdir(snapshot_dir_abs), snapshot_dir_abs)
        checks["snapshot_success_event_seen"] = line_status(
            bool(snapshot_events),
            snapshot_events[0] if snapshot_events else "missing startup snapshot event",
        )
        checks["snapshot_file_created"] = line_status(
            bool(snapshot_files),
            snapshot_files[0] if snapshot_files else "missing snapshot file",
        )
        checks["snapshot_paths_confined_to_snapshot_dir"] = line_status(
            bool(snapshot_files) and all(path.startswith(snapshot_dir_abs + os.sep) or path == snapshot_dir_abs for path in snapshot_files),
            snapshot_dir_abs,
        )

    return {
        "name": scenario_name,
        "branch_state": detect_branch_state(),
        "runtime_log": runtime_log,
        "log_root": log_root_abs,
        "snapshot_dir": snapshot_dir_abs,
        "snapshot_files": snapshot_files,
        "snapshot_events": snapshot_events,
        "stdout": stdout_text.strip(),
        "stderr": stderr_text.strip(),
        "exit_code": exit_code,
        "terminated_by_validator": terminated_by_validator,
        "checks": checks,
    }


def build_report_text(report_path, scenario_results, overall_ok):
    lines = [
        "ORIN STARTUP SNAPSHOT HARNESS VALIDATION",
        f"Report: {report_path}",
        f"Branch: {scenario_results[0]['branch_state'] if scenario_results else 'unavailable'}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
    ]

    for result in scenario_results:
        lines.extend(
            [
                "",
                f"Scenario: {result['name']}",
                f"Runtime log: {result['runtime_log']}",
                f"Log root: {result['log_root']}",
                f"Snapshot dir: {result['snapshot_dir']}",
                f"Exit code: {result['exit_code']}",
                f"Terminated by validator: {result['terminated_by_validator']}",
                "",
                "Checks:",
            ]
        )

        for key, value in result["checks"].items():
            lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

        lines.append("")
        lines.append("Snapshot files:")
        if result["snapshot_files"]:
            for path in result["snapshot_files"]:
                lines.append(f"  {path}")
        else:
            lines.append("  none")

        if result["snapshot_events"]:
            lines.append("")
            lines.append("Snapshot events:")
            for event in result["snapshot_events"]:
                lines.append(f"  {event}")

        if result["stdout"]:
            lines.extend(["", "stdout:", result["stdout"]])
        if result["stderr"]:
            lines.extend(["", "stderr:", result["stderr"]])

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    ensure_dir(REPORTS_DIR)
    scenario_results = [run_scenario(scenario) for scenario in SCENARIOS]
    overall_ok = all(
        value["ok"]
        for result in scenario_results
        for value in result["checks"].values()
    )

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"{REPORT_PREFIX}{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"{REPORT_PREFIX}{stamp}.json")

    report_text = build_report_text(report_path, scenario_results, overall_ok)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report_text)
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump({"scenarios": scenario_results}, handle, indent=2)

    print(report_text)
    print(f"JSON: {json_path}")

    if open_report and os.name == "nt":
        os.startfile(report_path)

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
