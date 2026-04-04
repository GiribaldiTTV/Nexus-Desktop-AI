import datetime
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "desktop_toolkit_validation")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")

DEV_LAUNCHER_SCRIPT = os.path.join(ROOT_DIR, "dev", "launchers", "jarvis_dev_launcher.pyw")
DEV_LAUNCHERS_DIR = os.path.join(ROOT_DIR, "dev", "launchers")

REPORT_PREFIX = "DesktopToolkitValidationReport_"

DESKTOP_CASES = (
    {
        "name": "Toolkit Desktop Helper: Healthy Desktop Validation",
        "lane_key": "desktopHealthy",
        "lane_label": "Healthy Desktop Launch Validation",
        "expected_launcher": "launch_jarvis_desktop_entrypoint_validation.vbs",
        "report_root": os.path.join(DEV_LOGS_DIR, "desktop_entrypoint_validation", "reports"),
        "report_prefix": "DesktopEntrypointValidationReport_",
        "timeout_seconds": 60,
    },
    {
        "name": "Toolkit Desktop Helper: Healthy Launcher Validation",
        "lane_key": "launcherHealthy",
        "lane_label": "Healthy Launcher Path Validation",
        "expected_launcher": "launch_jarvis_desktop_launcher_healthy_validation.vbs",
        "report_root": os.path.join(DEV_LOGS_DIR, "desktop_launcher_healthy_validation", "reports"),
        "report_prefix": "DesktopLauncherHealthyValidationReport_",
        "timeout_seconds": 90,
    },
)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def reset_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return

    for name in os.listdir(path):
        child = os.path.join(path, name)
        try:
            if os.path.isdir(child):
                for root, dirs, files in os.walk(child, topdown=False):
                    for file_name in files:
                        os.remove(os.path.join(root, file_name))
                    for dir_name in dirs:
                        os.rmdir(os.path.join(root, dir_name))
                os.rmdir(child)
            else:
                os.remove(child)
        except Exception:
            pass


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


def load_module_from_path(module_name, module_path):
    loader = importlib.machinery.SourceFileLoader(module_name, module_path)
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def wait_for_new_report(report_root, report_prefix, before_reports, timeout_seconds, app):
    deadline = time.time() + max(5, timeout_seconds)
    latest = ""
    while time.time() < deadline:
        current_reports = matching_files(report_root, report_prefix, ".txt")
        new_reports = current_reports - before_reports
        if len(new_reports) == 1:
            return sorted(new_reports)[0]
        if new_reports:
            latest = latest_file_matching(report_root, report_prefix, ".txt")
            if latest:
                return latest
        app.processEvents()
        time.sleep(0.2)
    return latest


def run_toolkit_case(dev_launcher_module, window, app, case):
    before_reports = matching_files(case["report_root"], case["report_prefix"], ".txt")
    launch_records = []
    opened_paths = []
    toolkit_events = []

    original_popen = subprocess.Popen
    original_open_path = window.open_path
    original_runtime_logger = window.runtime_logger

    def runtime_logger(event):
        toolkit_events.append(event)
        if callable(original_runtime_logger):
            original_runtime_logger(event)

    def fake_open_path(path, success_message):
        opened_paths.append({"path": os.path.abspath(path), "message": success_message})
        window.set_status(success_message)

    def recording_popen(args, cwd=None, **kwargs):
        launch_records.append(
            {
                "args": list(args),
                "cwd": os.path.abspath(cwd or ROOT_DIR),
            }
        )
        launch_env = os.environ.copy()
        launch_env.pop("QT_QPA_PLATFORM", None)
        kwargs["env"] = launch_env
        return original_popen(args, cwd=cwd, **kwargs)

    window.runtime_logger = runtime_logger
    window.open_path = fake_open_path
    subprocess.Popen = recording_popen

    launch_status = ""
    complete_status = ""
    open_status = ""
    new_report_path = ""
    try:
        window.select_lane(case["lane_key"])
        app.processEvents()
        window.delay_combo.setCurrentIndex(1)
        app.processEvents()

        QTest.mouseClick(window.launch_btn, Qt.LeftButton)
        app.processEvents()
        launch_status = window.status_label.text()

        new_report_path = wait_for_new_report(
            case["report_root"],
            case["report_prefix"],
            before_reports,
            case["timeout_seconds"],
            app,
        )

        window.refresh_background_run_status()
        app.processEvents()
        complete_status = window.status_label.text()

        window.open_latest_report()
        app.processEvents()
        open_status = window.status_label.text()
    finally:
        subprocess.Popen = original_popen
        window.open_path = original_open_path
        window.runtime_logger = original_runtime_logger

    latest_opened_path = opened_paths[-1]["path"] if opened_paths else ""
    report_text = read_text(new_report_path)
    launch_record = launch_records[0] if launch_records else {}
    expected_launcher_path = os.path.join(DEV_LAUNCHERS_DIR, case["expected_launcher"])
    expected_launch_marker = (
        f"TOOLKIT_MAIN|LANE_LAUNCHED|lane={case['lane_key']}|mode=quiet|label={case['lane_label']}"
    )

    checks = {
        "selected_lane_expected": line_status(
            window.current_lane_key() == case["lane_key"],
            window.current_lane_key(),
        ),
        "launch_mode_quiet": line_status(
            window.current_launch_mode_key() == "quiet",
            window.current_launch_mode_key(),
        ),
        "launcher_process_invoked_once": line_status(
            len(launch_records) == 1,
            f"launch records={len(launch_records)}",
        ),
        "launcher_host_is_wscript": line_status(
            bool(launch_record)
            and len(launch_record["args"]) >= 2
            and os.path.basename(launch_record["args"][0]).lower() == "wscript.exe",
            launch_record.get("args", ["missing"])[0] if launch_record else "missing launch",
        ),
        "launcher_path_expected": line_status(
            bool(launch_record)
            and len(launch_record["args"]) >= 2
            and os.path.normcase(os.path.abspath(launch_record["args"][1]))
            == os.path.normcase(os.path.abspath(expected_launcher_path)),
            launch_record.get("args", ["", "missing"])[1] if launch_record else "missing launch",
        ),
        "launcher_cwd_expected": line_status(
            bool(launch_record)
            and os.path.normcase(os.path.abspath(launch_record.get("cwd", "")))
            == os.path.normcase(os.path.abspath(DEV_LAUNCHERS_DIR)),
            launch_record.get("cwd", "missing cwd") if launch_record else "missing launch",
        ),
        "launch_marker_emitted": line_status(
            expected_launch_marker in toolkit_events,
            expected_launch_marker,
        ),
        "launch_status_expected": line_status(
            launch_status.startswith(f"Test in progress: {case['lane_label']}"),
            launch_status or "missing launch status",
        ),
        "new_report_created": line_status(
            bool(new_report_path) and os.path.isfile(new_report_path),
            new_report_path or "missing new report",
        ),
        "report_overall_pass": line_status(
            "Overall Result: PASS" in report_text,
            new_report_path or "missing report",
        ),
        "complete_status_expected": line_status(
            complete_status == f"Test complete: {case['lane_label']}",
            complete_status or "missing completion status",
        ),
        "latest_report_opened": line_status(
            bool(latest_opened_path),
            latest_opened_path or "no opened report path captured",
        ),
        "opened_report_matches_new_report": line_status(
            bool(new_report_path)
            and bool(latest_opened_path)
            and os.path.normcase(os.path.abspath(latest_opened_path))
            == os.path.normcase(os.path.abspath(new_report_path)),
            latest_opened_path or "no opened report path captured",
        ),
        "open_status_expected": line_status(
            open_status.startswith("Opened latest report: "),
            open_status or "missing open status",
        ),
    }

    return {
        "name": case["name"],
        "lane_label": case["lane_label"],
        "report_path": new_report_path,
        "opened_report_path": latest_opened_path,
        "launch_status": launch_status,
        "complete_status": complete_status,
        "open_status": open_status,
        "launch_record": launch_record,
        "checks": checks,
    }


def collect_failures(section):
    failures = []
    for key, value in section["checks"].items():
        if not value["ok"]:
            failures.append(f"{section['name']} :: {key}: {value['detail']}")
    return failures


def build_report_text(branch_state, report_path, sections, overall_ok):
    lines = [
        "JARVIS DESKTOP TOOLKIT VALIDATION",
        f"Report: {report_path}",
        f"Branch: {branch_state}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
    ]

    for section in sections:
        lines.append(f"{section['name']}:")
        lines.append(f"  lane: {section['lane_label']}")
        if section.get("report_path"):
            lines.append(f"  report: {section['report_path']}")
        if section.get("opened_report_path"):
            lines.append(f"  opened report: {section['opened_report_path']}")
        if section.get("launch_status"):
            lines.append(f"  launch status: {section['launch_status']}")
        if section.get("complete_status"):
            lines.append(f"  completion status: {section['complete_status']}")
        if section.get("open_status"):
            lines.append(f"  open status: {section['open_status']}")
        for key, value in section["checks"].items():
            lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    reset_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    dev_launcher_module = load_module_from_path(
        "jarvis_dev_launcher_desktop_toolkit_validation_module",
        DEV_LAUNCHER_SCRIPT,
    )

    app = dev_launcher_module.QApplication.instance() or dev_launcher_module.QApplication([])
    window = dev_launcher_module.DevLauncherWindow()
    window.show()
    app.processEvents()

    try:
        sections = [
            run_toolkit_case(dev_launcher_module, window, app, case)
            for case in DESKTOP_CASES
        ]
    finally:
        window.close()
        app.quit()

    failures = []
    for section in sections:
        failures.extend(collect_failures(section))

    overall_ok = not failures
    branch_state = detect_branch_state()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"{REPORT_PREFIX}{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"{REPORT_PREFIX}{stamp}.json")
    report_text = build_report_text(branch_state, report_path, sections, overall_ok)

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report_text)

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "branch_state": branch_state,
                "overall_ok": overall_ok,
                "sections": sections,
                "failures": failures,
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
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
