import datetime
import json
import os
import shutil
import sys
import urllib.parse
import zipfile
from types import SimpleNamespace


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import desktop.desktop_renderer as renderer_mod
import desktop.orin_support_reporting as support_reporting_mod


BASE_LOG_ROOT = os.path.join(CURRENT_DIR, "logs", "recoverable_launch_failed_validation")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")
REPORT_PREFIX = "RecoverableLaunchFailedValidationReport_"


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


def inspect_bundle_manifest(bundle_path):
    if not bundle_path or not os.path.isfile(bundle_path):
        return {}

    with zipfile.ZipFile(bundle_path, "r") as archive:
        for entry in archive.namelist():
            if entry.lower().endswith("/manifest.json"):
                with archive.open(entry, "r") as handle:
                    return json.load(handle)
    return {}


def extract_issue_draft_body(browser_open_calls):
    if not browser_open_calls:
        return ""

    issue_url = browser_open_calls[0]["url"]
    parsed = urllib.parse.urlparse(issue_url)
    query = urllib.parse.parse_qs(parsed.query)
    return query.get("body", [""])[0]


def make_window(runtime_log_path):
    window = renderer_mod.DesktopRuntimeWindow.__new__(renderer_mod.DesktopRuntimeWindow)
    events = []
    window._last_launch_failure_action_id = ""
    window._last_launch_failure_count = 0
    window._reported_recoverable_launch_failures = set()
    window.runtime_log_path = runtime_log_path
    window._log_event = lambda message: events.append(message)
    return window, events


def run_validation():
    reset_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    runtime_log_path = os.path.join(BASE_LOG_ROOT, "Runtime_recoverable_launch_failed_validation.txt")
    crash_dir = os.path.join(BASE_LOG_ROOT, "crash")
    ensure_dir(crash_dir)
    crash_log_path = os.path.join(crash_dir, "Crash_recoverable_launch_failed_validation.txt")

    with open(runtime_log_path, "w", encoding="utf-8") as handle:
        handle.write("RUNTIME|recoverable_launch_failed_validation|start\n")
        handle.write("RUNTIME|note|fb034 validation input\n")

    with open(crash_log_path, "w", encoding="utf-8") as handle:
        handle.write("Crash Type: synthetic_launch_failed_validation\n")
        handle.write(f"Runtime Log: {runtime_log_path}\n")

    action = SimpleNamespace(id="open_file_explorer")
    window, events = make_window(runtime_log_path)
    support_dir = os.path.join(BASE_LOG_ROOT, "support_bundles")
    expected_public_release_tag = support_reporting_mod.get_product_release_label(ROOT_DIR)
    expected_release_context = support_reporting_mod.get_product_release_context(ROOT_DIR)

    folder_open_calls = []
    browser_open_calls = []
    original_startfile = renderer_mod.os.startfile
    original_webbrowser_open = renderer_mod.webbrowser.open

    def fake_startfile(path):
        folder_open_calls.append(os.path.abspath(path))
        return None

    def fake_webbrowser_open(url, new=0, autoraise=True):
        browser_open_calls.append({"url": url, "new": new, "autoraise": autoraise})
        return True

    renderer_mod.os.startfile = fake_startfile
    renderer_mod.webbrowser.open = fake_webbrowser_open

    try:
        first_status = renderer_mod.DesktopRuntimeWindow._prepare_recoverable_launch_failure_report(window, action)
        first_bundle = latest_file_matching(support_dir, "NexusDesktopAI_Support_", ".zip")

        second_status = renderer_mod.DesktopRuntimeWindow._prepare_recoverable_launch_failure_report(window, action)
        second_bundle = latest_file_matching(support_dir, "NexusDesktopAI_Support_", ".zip")
        second_manifest = inspect_bundle_manifest(second_bundle)
        second_issue_body = extract_issue_draft_body(browser_open_calls)

        folder_calls_after_second = len(folder_open_calls)
        browser_calls_after_second = len(browser_open_calls)

        third_status = renderer_mod.DesktopRuntimeWindow._prepare_recoverable_launch_failure_report(window, action)
        third_bundle = latest_file_matching(support_dir, "NexusDesktopAI_Support_", ".zip")

        renderer_mod.DesktopRuntimeWindow._clear_launch_failure_tracking(window, action.id)
        fourth_status = renderer_mod.DesktopRuntimeWindow._prepare_recoverable_launch_failure_report(window, action)
    finally:
        renderer_mod.os.startfile = original_startfile
        renderer_mod.webbrowser.open = original_webbrowser_open

    checks = {
        "first_failure_stays_inline": line_status(
            first_status is None,
            repr(first_status),
        ),
        "first_failure_logs_class2_inline": line_status(
            any("RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS2_INLINE|action_id=open_file_explorer|count=1" in line for line in events),
            "RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS2_INLINE|action_id=open_file_explorer|count=1",
        ),
        "first_failure_does_not_prepare_bundle": line_status(
            not first_bundle,
            first_bundle or "no bundle after first failure",
        ),
        "second_failure_selects_class3_report": line_status(
            any("RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS3_REPORT_SELECTED|action_id=open_file_explorer|count=2" in line for line in events),
            "RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS3_REPORT_SELECTED|action_id=open_file_explorer|count=2",
        ),
        "second_failure_prepares_bundle_once": line_status(
            bool(second_bundle) and os.path.isfile(second_bundle),
            second_bundle or "missing support bundle zip",
        ),
        "second_failure_status_preserves_manual_attach_boundary": line_status(
            second_status == "Launch failed again. Support bundle prepared and issue draft opened; attach the bundle manually.",
            second_status or "missing second failure status",
        ),
        "second_failure_opens_bundle_folder_once": line_status(
            folder_calls_after_second == 1 and folder_open_calls[0] == os.path.abspath(support_dir),
            folder_open_calls or "missing folder open call",
        ),
        "second_failure_opens_issue_draft_once": line_status(
            browser_calls_after_second == 1 and "issues/new" in browser_open_calls[0]["url"],
            browser_open_calls or "missing browser open call",
        ),
        "bundle_manifest_requires_manual_review": line_status(
            second_manifest.get("manual_review_required") is True,
            str(second_manifest.get("manual_review_required")),
        ),
        "bundle_manifest_requires_manual_submission": line_status(
            second_manifest.get("manual_issue_submission_required") is True,
            str(second_manifest.get("manual_issue_submission_required")),
        ),
        "bundle_manifest_carries_current_public_release_tag": line_status(
            second_manifest.get("jarvis_version") == expected_public_release_tag,
            repr(second_manifest.get("jarvis_version")),
        ),
        "bundle_manifest_carries_truthful_release_context": line_status(
            second_manifest.get("release_context") == expected_release_context
            and "v1.0.0-prebeta" not in second_manifest.get("release_context", ""),
            repr(second_manifest.get("release_context")),
        ),
        "issue_draft_carries_truthful_release_context": line_status(
            expected_release_context in second_issue_body and "v1.0.0-prebeta" not in second_issue_body,
            second_issue_body or "missing issue draft body",
        ),
        "third_failure_does_not_reopen_report": line_status(
            third_status is None and len(folder_open_calls) == folder_calls_after_second and len(browser_open_calls) == browser_calls_after_second,
            repr(third_status),
        ),
        "third_failure_logs_class3_already_reported": line_status(
            any("RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS3_ALREADY_REPORTED|action_id=open_file_explorer|count=3" in line for line in events),
            "RENDERER_MAIN|COMMAND_LAUNCH_FAILED_CLASS3_ALREADY_REPORTED|action_id=open_file_explorer|count=3",
        ),
        "reset_returns_next_failure_to_class2_inline": line_status(
            fourth_status is None
            and window._last_launch_failure_count == 1
            and action.id not in window._reported_recoverable_launch_failures,
            repr(fourth_status),
        ),
    }

    return {
        "branch_state": detect_branch_state(),
        "runtime_log_path": runtime_log_path,
        "bundle_path": second_bundle,
        "folder_open_calls": folder_open_calls,
        "browser_open_calls": browser_open_calls,
        "event_count": len(events),
        "events": events,
        "checks": checks,
    }


def build_report_text(report_path, result, overall_ok):
    lines = [
        "RECOVERABLE LAUNCH_FAILED VALIDATION",
        f"Report: {report_path}",
        f"Branch: {result['branch_state']}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
        f"Runtime log: {result['runtime_log_path']}",
        f"Support bundle: {result['bundle_path'] or 'not created'}",
        f"Event count: {result['event_count']}",
        "",
        "Checks:",
    ]

    for key, value in result["checks"].items():
        lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

    if result["folder_open_calls"]:
        lines.extend(["", "folder_open_calls:"])
        lines.extend(result["folder_open_calls"])

    if result["browser_open_calls"]:
        lines.extend(["", "browser_open_calls:"])
        for call in result["browser_open_calls"]:
            lines.append(call["url"])

    lines.extend(["", "events:"])
    lines.extend(result["events"])

    return "\n".join(lines) + "\n"


def main():
    result = run_validation()
    failures = [key for key, value in result["checks"].items() if not value["ok"]]
    overall_ok = not failures

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"{REPORT_PREFIX}{stamp}.txt")

    report_text = build_report_text(report_path, result, overall_ok)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report_text)

    print("RECOVERABLE LAUNCH_FAILED VALIDATION")
    print(f"Report: {report_path}")
    print(f"Branch: {result['branch_state']}")
    print(f"Overall Result: {'PASS' if overall_ok else 'FAIL'}")
    print("")
    print(f"Runtime log: {result['runtime_log_path']}")
    print(f"Support bundle: {result['bundle_path'] or 'not created'}")
    print("")
    print("Checks:")
    for key, value in result["checks"].items():
        print(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
