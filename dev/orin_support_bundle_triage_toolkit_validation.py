import datetime
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "support_bundle_triage_toolkit_validation")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")

DEV_LAUNCHER_SCRIPT = os.path.join(ROOT_DIR, "dev", "launchers", "jarvis_dev_launcher.pyw")
TRIAGE_HELPER_SCRIPT = os.path.join(ROOT_DIR, "dev", "jarvis_support_bundle_triage.py")
TRIAGE_HARNESS_SCRIPT = os.path.join(ROOT_DIR, "dev", "jarvis_support_bundle_triage_harness.py")

RAW_TRIAGE_REPORTS_DIR = os.path.join(DEV_LOGS_DIR, "support_bundle_triage", "reports")
TRIAGE_HARNESS_REPORTS_DIR = os.path.join(DEV_LOGS_DIR, "support_bundle_triage_harness", "reports")
REPEATED_CRASH_SUPPORT_BUNDLES_DIR = os.path.join(
    DEV_LOGS_DIR,
    "desktop_launcher_regression_harness",
    "repeated_crash",
    "support_bundles",
)
UNSTABLE_EXTRACTED_BUNDLE_ROOT = os.path.join(
    DEV_LOGS_DIR,
    "support_bundle_triage_harness",
    "verification",
    "unstable_bundle_extracted",
)

REPORT_PREFIX = "SupportBundleTriageToolkitValidationReport_"
RAW_TRIAGE_REPORT_PREFIX = "SupportBundleTriageReport_"
EXPECTED_LANE_KEY = "supportBundleTriage"


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


def run_command(args, timeout_seconds=420):
    return subprocess.run(
        args,
        cwd=ROOT_DIR,
        timeout=timeout_seconds,
        **hidden_subprocess_kwargs(),
    )


def run_triage_harness_prerequisite():
    result = run_command([sys.executable, TRIAGE_HARNESS_SCRIPT], timeout_seconds=420)
    latest_report = latest_file_matching(
        TRIAGE_HARNESS_REPORTS_DIR,
        "SupportBundleTriageHarnessReport_",
        ".txt",
    )
    repeated_crash_bundle = latest_file_matching(
        REPEATED_CRASH_SUPPORT_BUNDLES_DIR,
        "JarvisSupport_",
        ".zip",
    )

    checks = {
        "triage_harness_exit_code_zero": line_status(
            result.returncode == 0,
            f"triage harness exit={result.returncode}",
        ),
        "triage_harness_report_created": line_status(
            bool(latest_report),
            latest_report or "missing triage harness report",
        ),
        "zip_bundle_available": line_status(
            bool(repeated_crash_bundle),
            repeated_crash_bundle or "missing repeated-crash support bundle zip",
        ),
        "extracted_folder_available": line_status(
            os.path.isdir(UNSTABLE_EXTRACTED_BUNDLE_ROOT),
            UNSTABLE_EXTRACTED_BUNDLE_ROOT,
        ),
    }

    return {
        "name": "Support Bundle Triage Harness Prerequisite",
        "artifact": latest_report,
        "zip_bundle_path": repeated_crash_bundle,
        "folder_bundle_path": UNSTABLE_EXTRACTED_BUNDLE_ROOT,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "checks": checks,
    }


def run_toolkit_case(dev_launcher_module, window, app, name, source_mode, source_path, expected_classification_key):
    file_dialog_calls = 0
    folder_dialog_calls = 0
    launch_records = []
    opened_paths = []
    selection_status = ""
    selection_summary = ""
    launch_status = ""
    open_status = ""
    new_report_path = ""
    selection_buttons_present = False

    before_reports = matching_files(RAW_TRIAGE_REPORTS_DIR, RAW_TRIAGE_REPORT_PREFIX, ".txt")
    original_file_dialog = dev_launcher_module.QFileDialog.getOpenFileName
    original_folder_dialog = dev_launcher_module.QFileDialog.getExistingDirectory
    original_popen = subprocess.Popen
    original_open_path = window.open_path

    def fake_get_open_file_name(*args, **kwargs):
        nonlocal file_dialog_calls
        file_dialog_calls += 1
        if source_mode == "zip":
            return source_path, "Support Bundle Zip (*.zip)"
        return "", ""

    def fake_get_existing_directory(*args, **kwargs):
        nonlocal folder_dialog_calls
        folder_dialog_calls += 1
        if source_mode == "folder":
            return source_path
        return ""

    def fake_open_path(path, success_message):
        opened_paths.append({"path": os.path.abspath(path), "message": success_message})
        window.set_status(success_message)

    def fake_popen(args, cwd=None, **kwargs):
        original_args = list(args)
        actual_args = list(args)

        if len(actual_args) >= 3 and os.path.normcase(actual_args[1]) == os.path.normcase(TRIAGE_HELPER_SCRIPT):
            actual_args = [sys.executable] + actual_args[1:]

        proc = original_popen(
            actual_args,
            cwd=cwd,
            **hidden_subprocess_kwargs(),
        )
        stdout_text, stderr_text = proc.communicate(timeout=300)
        launch_records.append(
            {
                "original_args": original_args,
                "actual_args": actual_args,
                "cwd": cwd or "",
                "returncode": proc.returncode,
                "stdout": stdout_text.strip(),
                "stderr": stderr_text.strip(),
            }
        )
        return proc

    dev_launcher_module.QFileDialog.getOpenFileName = staticmethod(fake_get_open_file_name)
    dev_launcher_module.QFileDialog.getExistingDirectory = staticmethod(fake_get_existing_directory)
    subprocess.Popen = fake_popen
    window.open_path = fake_open_path

    try:
        selection_buttons_present = all(
            hasattr(window, attr_name)
            for attr_name in (
                "select_support_bundle_zip_btn",
                "select_support_bundle_folder_btn",
                "run_support_bundle_triage_btn",
                "open_selected_support_bundle_source_btn",
                "clear_selected_support_bundle_source_btn",
                "support_bundle_source_label",
            )
        )
        app.processEvents()

        if source_mode == "zip":
            window.select_support_bundle_zip_btn.click()
        else:
            window.select_support_bundle_folder_btn.click()
        app.processEvents()
        selection_status = window.status_label.text()
        selection_summary = window.support_bundle_source_label.text() if hasattr(window, "support_bundle_source_label") else ""

        if hasattr(window, "run_support_bundle_triage_btn"):
            window.run_support_bundle_triage_btn.click()
        else:
            window.launch_selected_support_bundle_triage()
        app.processEvents()
        launch_status = window.status_label.text()

        new_reports = matching_files(RAW_TRIAGE_REPORTS_DIR, RAW_TRIAGE_REPORT_PREFIX, ".txt") - before_reports
        if len(new_reports) == 1:
            new_report_path = sorted(new_reports)[0]
        elif new_reports:
            new_report_path = latest_file_matching(RAW_TRIAGE_REPORTS_DIR, RAW_TRIAGE_REPORT_PREFIX, ".txt")

        window.open_latest_report()
        app.processEvents()
        open_status = window.status_label.text()
    finally:
        subprocess.Popen = original_popen
        window.open_path = original_open_path
        dev_launcher_module.QFileDialog.getOpenFileName = original_file_dialog
        dev_launcher_module.QFileDialog.getExistingDirectory = original_folder_dialog

    latest_opened_path = opened_paths[-1]["path"] if opened_paths else ""
    report_text = read_text(new_report_path)
    launch_record = launch_records[0] if launch_records else {}
    expected_kind_text = "Zip Archive" if source_mode == "zip" else "Extracted Folder"

    checks = {
        "intake_widgets_present": line_status(
            selection_buttons_present,
            "uploads intake controls discovered" if selection_buttons_present else "missing uploads intake controls",
        ),
        "selected_lane_expected": line_status(
            window.current_lane_key() == EXPECTED_LANE_KEY,
            window.current_lane_key(),
        ),
        "input_exists": line_status(
            os.path.exists(source_path),
            source_path,
        ),
        "file_dialog_called_once": line_status(
            file_dialog_calls == (1 if source_mode == "zip" else 0),
            f"file dialog calls={file_dialog_calls}",
        ),
        "folder_dialog_called_once": line_status(
            folder_dialog_calls == (1 if source_mode == "folder" else 0),
            f"folder dialog calls={folder_dialog_calls}",
        ),
        "selection_status_expected": line_status(
            selection_status.startswith("Selected support bundle zip: ")
            if source_mode == "zip"
            else selection_status.startswith("Selected extracted support bundle folder: "),
            selection_status or "missing selection status",
        ),
        "selected_source_displayed": line_status(
            expected_kind_text in selection_summary and os.path.abspath(source_path) in selection_summary,
            selection_summary or "missing selected source summary",
        ),
        "run_button_enabled_after_selection": line_status(
            hasattr(window, "run_support_bundle_triage_btn") and window.run_support_bundle_triage_btn.isEnabled(),
            "run button enabled" if hasattr(window, "run_support_bundle_triage_btn") and window.run_support_bundle_triage_btn.isEnabled() else "run button disabled",
        ),
        "helper_process_invoked_once": line_status(
            len(launch_records) == 1,
            f"launch records={len(launch_records)}",
        ),
        "helper_pythonw_path_expected": line_status(
            bool(launch_record) and len(launch_record["original_args"]) >= 3 and launch_record["original_args"][0] == dev_launcher_module.PYTHONW_PATH,
            launch_record.get("original_args", ["missing"])[0] if launch_record else "missing launch",
        ),
        "helper_script_path_expected": line_status(
            bool(launch_record) and len(launch_record["original_args"]) >= 3 and os.path.normcase(launch_record["original_args"][1]) == os.path.normcase(TRIAGE_HELPER_SCRIPT),
            launch_record.get("original_args", ["", "missing"])[1] if launch_record else "missing launch",
        ),
        "helper_source_path_expected": line_status(
            bool(launch_record) and len(launch_record["original_args"]) >= 3 and os.path.normcase(os.path.abspath(launch_record["original_args"][2])) == os.path.normcase(os.path.abspath(source_path)),
            launch_record.get("original_args", ["", "", "missing"])[2] if launch_record else "missing launch",
        ),
        "helper_cwd_expected": line_status(
            bool(launch_record) and os.path.normcase(os.path.abspath(launch_record.get("cwd") or ROOT_DIR)) == os.path.normcase(ROOT_DIR),
            launch_record.get("cwd") or ROOT_DIR,
        ),
        "helper_exit_code_zero": line_status(
            bool(launch_record) and launch_record["returncode"] == 0,
            f"helper exit={launch_record.get('returncode', 'missing')}",
        ),
        "launch_status_expected": line_status(
            launch_status.startswith("Test in progress: Support Bundle Triage Helper")
            or launch_status.startswith("Test complete: Support Bundle Triage Helper"),
            launch_status or "missing launch status",
        ),
        "new_report_created": line_status(
            bool(new_report_path) and os.path.isfile(new_report_path),
            new_report_path or "missing new triage report",
        ),
        "report_contains_expected_classification": line_status(
            f"Key: {expected_classification_key}" in report_text,
            expected_classification_key,
        ),
        "latest_report_opened": line_status(
            bool(latest_opened_path),
            latest_opened_path or "no opened report path captured",
        ),
        "opened_report_matches_new_report": line_status(
            bool(new_report_path) and latest_opened_path and os.path.normcase(os.path.abspath(latest_opened_path)) == os.path.normcase(os.path.abspath(new_report_path)),
            latest_opened_path or "no opened report path captured",
        ),
        "open_status_expected": line_status(
            open_status.startswith("Opened latest report: "),
            open_status or "missing open status",
        ),
    }

    return {
        "name": name,
        "input_path": source_path,
        "report_path": new_report_path,
        "opened_report_path": latest_opened_path,
        "selection_status": selection_status,
        "selection_summary": selection_summary,
        "launch_status": launch_status,
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
        "JARVIS SUPPORT BUNDLE TRIAGE TOOLKIT VALIDATION",
        f"Report: {report_path}",
        f"Branch: {branch_state}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
    ]

    for section in sections:
        lines.append(f"{section['name']}:")
        if section.get("artifact"):
            lines.append(f"  artifact: {section['artifact']}")
        if section.get("input_path"):
            lines.append(f"  input: {section['input_path']}")
        if section.get("selection_status"):
            lines.append(f"  selection status: {section['selection_status']}")
        if section.get("selection_summary"):
            lines.append("  selected source:")
            for line in section["selection_summary"].splitlines():
                lines.append(f"    {line}")
        if section.get("report_path"):
            lines.append(f"  triage report: {section['report_path']}")
        if section.get("opened_report_path"):
            lines.append(f"  opened report: {section['opened_report_path']}")
        if section.get("launch_status"):
            lines.append(f"  launch status: {section['launch_status']}")
        if section.get("open_status"):
            lines.append(f"  open status: {section['open_status']}")
        for key, value in section["checks"].items():
            lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")
        if section.get("stderr"):
            lines.append("  stderr:")
            lines.append(f"  {section['stderr']}")
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    reset_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    prerequisite_section = run_triage_harness_prerequisite()
    zip_bundle_path = prerequisite_section["zip_bundle_path"]
    folder_bundle_path = prerequisite_section["folder_bundle_path"]

    dev_launcher_module = load_module_from_path(
        "jarvis_dev_launcher_toolkit_validation_module",
        DEV_LAUNCHER_SCRIPT,
    )

    app = dev_launcher_module.QApplication.instance() or dev_launcher_module.QApplication([])
    window = dev_launcher_module.DevLauncherWindow()

    try:
        zip_section = run_toolkit_case(
            dev_launcher_module=dev_launcher_module,
            window=window,
            app=app,
            name="Toolkit Raw Helper: Zip Input",
            source_mode="zip",
            source_path=zip_bundle_path,
            expected_classification_key="launcher_repeated_identical_crash_threshold",
        )

        folder_section = run_toolkit_case(
            dev_launcher_module=dev_launcher_module,
            window=window,
            app=app,
            name="Toolkit Raw Helper: Extracted Folder Input",
            source_mode="folder",
            source_path=folder_bundle_path,
            expected_classification_key="launcher_max_attempt_unstable_non_threshold",
        )
    finally:
        window.close()
        app.quit()

    sections = [prerequisite_section, zip_section, folder_section]
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
