import datetime
import json
import os
import subprocess
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "dev_toolkit_smoke_validation")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")

BOOT_TOOLKIT_VALIDATION_SCRIPT = os.path.join(ROOT_DIR, "dev", "jarvis_boot_toolkit_validation.py")
DESKTOP_TOOLKIT_VALIDATION_SCRIPT = os.path.join(ROOT_DIR, "dev", "jarvis_desktop_toolkit_validation.py")

BOOT_TOOLKIT_REPORTS_DIR = os.path.join(DEV_LOGS_DIR, "boot_toolkit_validation", "reports")
DESKTOP_TOOLKIT_REPORTS_DIR = os.path.join(DEV_LOGS_DIR, "desktop_toolkit_validation", "reports")

REPORT_PREFIX = "DevToolkitSmokeValidationReport_"


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


def run_validation_case(name, script_path, report_root, report_prefix, timeout_seconds):
    before_reports = matching_files(report_root, report_prefix, ".txt")
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=ROOT_DIR,
        timeout=timeout_seconds,
        **hidden_subprocess_kwargs(),
    )

    after_reports = matching_files(report_root, report_prefix, ".txt")
    new_reports = after_reports - before_reports
    if len(new_reports) == 1:
        report_path = sorted(new_reports)[0]
    elif new_reports:
        report_path = latest_file_matching(report_root, report_prefix, ".txt")
    else:
        report_path = latest_file_matching(report_root, report_prefix, ".txt")

    report_text = read_text(report_path)
    checks = {
        "script_exit_zero": line_status(
            result.returncode == 0,
            f"exit={result.returncode}",
        ),
        "fresh_report_created": line_status(
            bool(report_path) and os.path.isfile(report_path) and os.path.abspath(report_path) in after_reports,
            report_path or "missing report",
        ),
        "report_overall_pass": line_status(
            "Overall Result: PASS" in report_text,
            report_path or "missing report",
        ),
        "traceback_absent": line_status(
            "Traceback" not in result.stdout and "Traceback" not in result.stderr,
            "no traceback in stdout/stderr",
        ),
    }

    return {
        "name": name,
        "script_path": script_path,
        "report_path": report_path,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
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
        "DEV TOOLKIT SMOKE VALIDATION",
        f"Report: {report_path}",
        f"Branch: {branch_state}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
    ]

    for section in sections:
        lines.append(f"{section['name']}:")
        lines.append(f"  script: {section['script_path']}")
        if section.get("report_path"):
            lines.append(f"  report: {section['report_path']}")
        for key, value in section["checks"].items():
            lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")
        if section.get("stdout"):
            lines.append("  stdout:")
            lines.extend(f"    {line}" for line in section["stdout"].splitlines())
        if section.get("stderr"):
            lines.append("  stderr:")
            lines.extend(f"    {line}" for line in section["stderr"].splitlines())
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    reset_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    sections = [
        run_validation_case(
            name="Boot Helper Toolkit Validation",
            script_path=BOOT_TOOLKIT_VALIDATION_SCRIPT,
            report_root=BOOT_TOOLKIT_REPORTS_DIR,
            report_prefix="BootToolkitValidationReport_",
            timeout_seconds=240,
        ),
        run_validation_case(
            name="Desktop Helper Toolkit Validation",
            script_path=DESKTOP_TOOLKIT_VALIDATION_SCRIPT,
            report_root=DESKTOP_TOOLKIT_REPORTS_DIR,
            report_prefix="DesktopToolkitValidationReport_",
            timeout_seconds=240,
        ),
    ]

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
