import datetime
import importlib.machinery
import importlib.util
import json
import os
import shutil
import sys
import urllib.parse
import zipfile


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
BASE_LOG_ROOT = os.path.join(LOGS_DIR, "diagnostics_report_issue_validation")
VERIFICATION_DIR = os.path.join(BASE_LOG_ROOT, "verification")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")
DESKTOP_DIR = os.path.join(ROOT_DIR, "desktop")
DIAGNOSTICS_SCRIPT = os.path.join(DESKTOP_DIR, "jarvis_diagnostics.pyw")

REPORT_PREFIX = "DiagnosticsReportIssueValidationReport_"
MANIFEST_FILENAME = "manifest.json"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def reset_dir(path):
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    except Exception:
        return "unavailable"


def line_status(ok, detail):
    return {"ok": bool(ok), "detail": detail}


def read_text(path):
    if not path or not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def load_module_from_path(module_name, module_path):
    loader = importlib.machinery.SourceFileLoader(module_name, module_path)
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


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


def create_validation_inputs():
    ensure_dir(VERIFICATION_DIR)
    crash_dir = os.path.join(VERIFICATION_DIR, "crash")
    ensure_dir(crash_dir)

    runtime_log_path = os.path.join(VERIFICATION_DIR, "Runtime_report_issue_validation.txt")
    crash_log_path = os.path.join(crash_dir, "Crash_report_issue_validation.txt")

    runtime_lines = [
        "RUNTIME|report_issue_validation|start",
        "RUNTIME|phase|diagnostics_report_issue",
        "RUNTIME|note|validation input runtime log",
    ]
    with open(runtime_log_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(runtime_lines) + "\n")

    crash_lines = [
        f"Runtime Log: {runtime_log_path}",
        "Crash Type: synthetic_validation_crash",
        "Crash Detail: deterministic report issue validation input",
    ]
    with open(crash_log_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(crash_lines) + "\n")

    return {
        "runtime_log_path": runtime_log_path,
        "crash_log_path": crash_log_path,
        "crash_dir": crash_dir,
    }


def inspect_bundle(bundle_path):
    zip_entries = []
    manifest = {}
    manifest_archive_path = ""
    with zipfile.ZipFile(bundle_path, "r") as archive:
        zip_entries = sorted(archive.namelist())
        for entry in zip_entries:
            if entry.lower().endswith(f"/{MANIFEST_FILENAME}"):
                manifest_archive_path = entry
                with archive.open(entry, "r") as handle:
                    manifest = json.load(handle)
                break
    return {
        "zip_entries": zip_entries,
        "manifest": manifest,
        "manifest_archive_path": manifest_archive_path,
    }


def parse_issue_url(issue_url):
    parsed = urllib.parse.urlparse(issue_url)
    query = urllib.parse.parse_qs(parsed.query)
    return {
        "parsed": parsed,
        "query": query,
        "title": query.get("title", [""])[0],
        "body": query.get("body", [""])[0],
    }


def run_validation():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    reset_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    inputs = create_validation_inputs()
    support_dir = os.path.join(VERIFICATION_DIR, "support_bundles")
    before_bundle = latest_file_matching(support_dir, "JarvisSupport_", ".zip")

    sys.path.insert(0, DESKTOP_DIR)
    diagnostics_module = load_module_from_path(
        "jarvis_diagnostics_report_issue_validation_module",
        DIAGNOSTICS_SCRIPT,
    )

    diagnostics_module.configure_launch_args(
        [DIAGNOSTICS_SCRIPT, "--runtime-log", inputs["runtime_log_path"]]
    )

    app = diagnostics_module.QApplication.instance() or diagnostics_module.QApplication([])
    window = diagnostics_module.DiagnosticsWindow()

    folder_open_calls = []
    browser_open_calls = []

    original_startfile = diagnostics_module.os.startfile
    original_webbrowser_open = diagnostics_module.webbrowser.open

    def fake_startfile(path):
        folder_open_calls.append(os.path.abspath(path))
        return None

    def fake_webbrowser_open(url, new=0, autoraise=True):
        browser_open_calls.append(
            {
                "url": url,
                "new": new,
                "autoraise": autoraise,
            }
        )
        return True

    diagnostics_module.os.startfile = fake_startfile
    diagnostics_module.webbrowser.open = fake_webbrowser_open

    trace_text = ""
    passive_attribute = False
    report_button_enabled = False

    try:
        window.show()
        app.processEvents()
        passive_attribute = window.testAttribute(diagnostics_module.Qt.WA_ShowWithoutActivating)
        window.report_issue()
        app.processEvents()
        trace_text = window.trace.toPlainText()
        report_button_enabled = window.report_btn.isEnabled()
    finally:
        diagnostics_module.os.startfile = original_startfile
        diagnostics_module.webbrowser.open = original_webbrowser_open
        try:
            window.timer.stop()
        except Exception:
            pass
        try:
            window.hide()
        except Exception:
            pass
        try:
            sys.path.remove(DESKTOP_DIR)
        except ValueError:
            pass

    bundle_path = latest_file_matching(support_dir, "JarvisSupport_", ".zip")
    bundle_info = inspect_bundle(bundle_path) if bundle_path else {"zip_entries": [], "manifest": {}, "manifest_archive_path": ""}
    manifest = bundle_info["manifest"]

    runtime_log_name = os.path.basename(inputs["runtime_log_path"])
    crash_log_name = os.path.basename(inputs["crash_log_path"])
    expected_issue_url = ""
    captured_issue_url = browser_open_calls[0]["url"] if browser_open_calls else ""
    if bundle_path and manifest:
        expected_issue_url = diagnostics_module.build_issue_prefill_url(
            diagnostics_module.ROOT_DIR,
            {
                "bundle_name": os.path.basename(bundle_path),
                "runtime_log_name": runtime_log_name,
                "crash_log_name": crash_log_name if any(entry.get("name") == crash_log_name for entry in manifest.get("bundled_files", [])) else None,
                "run_identity": manifest.get("run_identity", ""),
                "jarvis_version": manifest.get("jarvis_version", ""),
            },
        )

    issue_url_info = parse_issue_url(captured_issue_url) if captured_issue_url else {"parsed": None, "query": {}, "title": "", "body": ""}
    runtime_log_text = read_text(inputs["runtime_log_path"])
    leftover_staging_dirs = []
    if os.path.isdir(support_dir):
        leftover_staging_dirs = [
            os.path.join(support_dir, name)
            for name in os.listdir(support_dir)
            if name.startswith("JarvisSupport_") and os.path.isdir(os.path.join(support_dir, name))
        ]

    expected_bundle_dir = os.path.dirname(bundle_path) if bundle_path else ""
    bundled_file_names = [entry.get("name") for entry in manifest.get("bundled_files", [])]
    zip_entries = bundle_info["zip_entries"]
    expected_bundle_names = {
        runtime_log_name,
        crash_log_name,
        MANIFEST_FILENAME,
    }
    archive_leaf_names = {entry.replace("\\", "/").split("/")[-1] for entry in zip_entries}

    checks = {
        "diagnostics_root_expected": line_status(
            os.path.normcase(diagnostics_module.ROOT_DIR) == os.path.normcase(ROOT_DIR),
            diagnostics_module.ROOT_DIR,
        ),
        "diagnostics_log_dir_expected": line_status(
            os.path.normcase(diagnostics_module.LOG_DIR) == os.path.normcase(VERIFICATION_DIR),
            diagnostics_module.LOG_DIR,
        ),
        "window_passive_attribute_preserved": line_status(
            passive_attribute,
            f"WA_ShowWithoutActivating={passive_attribute}",
        ),
        "report_button_reenabled": line_status(
            report_button_enabled,
            f"report_button_enabled={report_button_enabled}",
        ),
        "bundle_created": line_status(
            bool(bundle_path) and os.path.isfile(bundle_path) and bundle_path != before_bundle,
            bundle_path or "missing bundle zip",
        ),
        "manifest_present_in_archive": line_status(
            bool(bundle_info["manifest_archive_path"]),
            bundle_info["manifest_archive_path"] or "missing manifest entry",
        ),
        "zip_contains_expected_files": line_status(
            expected_bundle_names.issubset(archive_leaf_names),
            ", ".join(sorted(archive_leaf_names)) or "missing archive entries",
        ),
        "manifest_lists_expected_files": line_status(
            expected_bundle_names.issubset(set(bundled_file_names)),
            ", ".join(str(name) for name in bundled_file_names) or "missing bundled_files",
        ),
        "manifest_manual_review_required": line_status(
            manifest.get("manual_review_required") is True,
            str(manifest.get("manual_review_required")),
        ),
        "manifest_manual_issue_submission_required": line_status(
            manifest.get("manual_issue_submission_required") is True,
            str(manifest.get("manual_issue_submission_required")),
        ),
        "manifest_run_identity_expected": line_status(
            manifest.get("run_identity") == "report_issue_validation",
            manifest.get("run_identity", "missing"),
        ),
        "crash_log_included": line_status(
            manifest.get("bundled_files") and any(entry.get("name") == crash_log_name for entry in manifest.get("bundled_files", [])),
            crash_log_name,
        ),
        "bundle_folder_open_attempt_captured": line_status(
            len(folder_open_calls) == 1,
            json.dumps(folder_open_calls),
        ),
        "bundle_folder_open_target_expected": line_status(
            len(folder_open_calls) == 1 and expected_bundle_dir and os.path.normcase(folder_open_calls[0]) == os.path.normcase(expected_bundle_dir),
            folder_open_calls[0] if folder_open_calls else "missing folder open",
        ),
        "issue_open_attempt_captured": line_status(
            len(browser_open_calls) == 1,
            json.dumps(browser_open_calls),
        ),
        "issue_open_new_tab_requested": line_status(
            len(browser_open_calls) == 1 and browser_open_calls[0]["new"] == 2,
            str(browser_open_calls[0]["new"]) if browser_open_calls else "missing browser open",
        ),
        "issue_url_github_targeted": line_status(
            bool(issue_url_info["parsed"]) and issue_url_info["parsed"].scheme in {"http", "https"} and issue_url_info["parsed"].netloc.lower() == "github.com" and issue_url_info["parsed"].path.endswith("/issues/new"),
            captured_issue_url or "missing issue url",
        ),
        "issue_url_matches_current_builder": line_status(
            bool(expected_issue_url) and captured_issue_url == expected_issue_url,
            captured_issue_url or "missing issue url",
        ),
        "issue_title_contains_run_identity": line_status(
            issue_url_info["title"] == "Support bundle report: report_issue_validation",
            issue_url_info["title"] or "missing title",
        ),
        "issue_body_contains_manual_attach_guidance": line_status(
            "Attach the bundle manually before submitting" in issue_url_info["body"],
            issue_url_info["body"] or "missing body",
        ),
        "trace_mentions_bundle_created": line_status(
            bool(bundle_path) and f"Support bundle created: {os.path.basename(bundle_path)}" in trace_text,
            trace_text or "missing trace output",
        ),
        "trace_mentions_manual_submission": line_status(
            "Attach the support bundle manually and submit the issue manually." in trace_text,
            trace_text or "missing trace output",
        ),
        "runtime_log_records_report_issue_start": line_status(
            "UI|report_issue|start|" in runtime_log_text,
            runtime_log_text or "missing runtime log",
        ),
        "runtime_log_records_bundle_folder_opened": line_status(
            "UI|report_issue|bundle_folder_opened|" in runtime_log_text,
            runtime_log_text or "missing runtime log",
        ),
        "runtime_log_records_issue_opened": line_status(
            "UI|report_issue|issue_opened|" in runtime_log_text,
            runtime_log_text or "missing runtime log",
        ),
        "artifact_cleanup_no_staging_dirs": line_status(
            not leftover_staging_dirs,
            json.dumps(leftover_staging_dirs),
        ),
    }

    return {
        "name": "Diagnostics Report Issue Flow",
        "bundle_path": bundle_path,
        "issue_url": captured_issue_url,
        "opened_folder_path": folder_open_calls[0] if folder_open_calls else "",
        "runtime_log_path": inputs["runtime_log_path"],
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
        "JARVIS DIAGNOSTICS REPORT ISSUE VALIDATION",
        f"Report: {report_path}",
        f"Branch: {branch_state}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
    ]

    for section in sections:
        lines.append(f"{section['name']}:")
        if section.get("bundle_path"):
            lines.append(f"  bundle: {section['bundle_path']}")
        if section.get("issue_url"):
            lines.append(f"  issue url: {section['issue_url']}")
        if section.get("opened_folder_path"):
            lines.append(f"  opened folder: {section['opened_folder_path']}")
        if section.get("runtime_log_path"):
            lines.append(f"  runtime log: {section['runtime_log_path']}")
        for key, value in section["checks"].items():
            lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    section = run_validation()
    sections = [section]
    failures = collect_failures(section)
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
