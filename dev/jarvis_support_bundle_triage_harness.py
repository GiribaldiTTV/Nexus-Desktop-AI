import datetime
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import zipfile


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
BASE_LOG_ROOT = os.path.join(LOGS_DIR, "support_bundle_triage_harness")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")
TRIAGE_LOG_ROOT = os.path.join(BASE_LOG_ROOT, "triage")
VERIFICATION_DIR = os.path.join(BASE_LOG_ROOT, "verification")

TRIAGE_SCRIPT = os.path.join(ROOT_DIR, "dev", "jarvis_support_bundle_triage.py")
SUPPORT_REPORTING_SCRIPT = os.path.join(ROOT_DIR, "desktop", "jarvis_support_reporting.py")
LAUNCHER_REGRESSION_HARNESS_SCRIPT = os.path.join(ROOT_DIR, "dev", "jarvis_desktop_launcher_regression_harness.py")

DESKTOP_LAUNCHER_REGRESSION_HARNESS = os.path.join(ROOT_DIR, "dev", "jarvis_desktop_launcher_regression_harness.py")
LAUNCHER_REGRESSION_REPORTS_DIR = os.path.join(LOGS_DIR, "desktop_launcher_regression_harness", "reports")

LANE_ROOTS = {
    "repeated_crash": os.path.join(LOGS_DIR, "desktop_launcher_regression_harness", "repeated_crash"),
    "startup_abort": os.path.join(LOGS_DIR, "desktop_launcher_regression_harness", "startup_abort"),
    "stable_max_attempt": os.path.join(LOGS_DIR, "desktop_launcher_regression_harness", "stable_max_attempt"),
    "unstable_max_attempt": os.path.join(LOGS_DIR, "desktop_launcher_regression_harness", "unstable_max_attempt"),
}


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
        shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


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


def path_is_contained(path, root):
    if not path:
        return False

    try:
        normalized_path = os.path.normcase(os.path.abspath(path))
        normalized_root = os.path.normcase(os.path.abspath(root))
        return os.path.commonpath([normalized_path, normalized_root]) == normalized_root
    except ValueError:
        return False


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    except Exception:
        return "unavailable"


def run_command(args, timeout_seconds=300):
    return subprocess.run(
        args,
        cwd=ROOT_DIR,
        timeout=timeout_seconds,
        **hidden_subprocess_kwargs(),
    )


def load_module_from_path(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_launcher_regression_prerequisite():
    result = run_command([sys.executable, LAUNCHER_REGRESSION_HARNESS_SCRIPT], timeout_seconds=360)
    latest_report = latest_file_matching(LAUNCHER_REGRESSION_REPORTS_DIR, "DesktopLauncherRegressionHarnessReport_")
    checks = {
        "launcher_regression_exit_code_zero": line_status(
            result.returncode == 0,
            f"launcher regression exit={result.returncode}",
        ),
        "launcher_regression_report_created": line_status(
            bool(latest_report),
            latest_report or "missing launcher regression report",
        ),
    }
    return {
        "name": "Launcher Regression Prerequisite",
        "runtime_log": latest_report,
        "checks": checks,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def create_support_bundle(support_module, lane_root):
    runtime_log = latest_file_matching(lane_root, "Runtime_")
    crash_dir = os.path.join(lane_root, "crash")
    bundle_info = support_module.create_support_bundle(ROOT_DIR, runtime_log, crash_dir)
    return runtime_log, crash_dir, bundle_info


def extract_bundle(zip_path, destination_root):
    reset_dir(destination_root)
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(destination_root)
    return destination_root


def create_unknown_bundle(destination_root):
    reset_dir(destination_root)
    manifest_path = os.path.join(destination_root, "manifest.json")
    runtime_log_path = os.path.join(destination_root, "Runtime_synthetic_unknown.txt")

    manifest = {
        "jarvis_version": "v1.8.0",
        "run_identity": "synthetic_unknown",
        "bundle_created_at": "2026-03-28T21:01:00Z",
        "environment_summary": {
            "platform": "test",
            "python_version": platform_python_version(),
            "python_implementation": platform_python_implementation(),
        },
        "bundled_files": [
            {"name": os.path.basename(runtime_log_path), "kind": "runtime_log"},
            {"name": "manifest.json", "kind": "manifest"},
        ],
        "manual_review_required": True,
        "manual_issue_submission_required": True,
    }

    with open(runtime_log_path, "w", encoding="utf-8") as handle:
        handle.write("[00:00:01] STATUS|START|LAUNCHER_RUNTIME\n")
        handle.write("[00:00:02] STATUS|TRACE|LAUNCHER_RUNTIME|NO_CLASSIFIABLE_TERMINAL_MARKERS\n")

    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)

    return destination_root


def platform_python_version():
    return "{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)


def platform_python_implementation():
    return getattr(sys, "implementation", None).name.capitalize() if getattr(sys, "implementation", None) else "Python"


def run_triage_case(
    triage_module,
    triage_log_root,
    name,
    input_path,
    input_mode,
    expected_key,
    expected_lane,
    expected_confidence,
    expected_fragments,
    expect_repro_path,
):
    report_path, json_path, _ = triage_module.triage_bundle(input_path, log_root_override=triage_log_root)
    triage_json = read_json(json_path)
    classification = triage_json["classification"]
    triage_checks = triage_json["checks"]

    checks = {
        "input_mode_expected": line_status(
            input_mode == ("zip" if os.path.isfile(input_path) else "folder"),
            f"{input_mode} :: {input_path}",
        ),
        "triage_report_created": line_status(
            os.path.isfile(report_path),
            report_path,
        ),
        "triage_json_created": line_status(
            os.path.isfile(json_path),
            json_path,
        ),
        "triage_report_contained": line_status(
            path_is_contained(report_path, triage_log_root),
            report_path,
        ),
        "triage_json_contained": line_status(
            path_is_contained(json_path, triage_log_root),
            json_path,
        ),
        "classification_key_expected": line_status(
            classification["classification_key"] == expected_key,
            classification["classification_key"],
        ),
        "classification_confidence_expected": line_status(
            classification["confidence"] == expected_confidence,
            classification["confidence"],
        ),
        "manifest_loaded": line_status(
            triage_checks["manifest_loaded"]["ok"],
            triage_checks["manifest_loaded"]["detail"],
        ),
        "runtime_log_present": line_status(
            triage_checks["runtime_log_present"]["ok"],
            triage_checks["runtime_log_present"]["detail"],
        ),
        "safe_classification_or_fallback": line_status(
            triage_checks["classification_confident_or_safe_fallback"]["ok"],
            triage_checks["classification_confident_or_safe_fallback"]["detail"],
        ),
    }

    if input_mode == "zip":
        checks["temp_manifest_contained"] = line_status(
            path_is_contained(triage_json["manifest_path"], triage_log_root),
            triage_json["manifest_path"],
        )
        checks["temp_runtime_log_contained"] = line_status(
            path_is_contained(triage_json["runtime_log_path"], triage_log_root),
            triage_json["runtime_log_path"],
        )
        crash_log_path = triage_json.get("crash_log_path", "")
        checks["temp_crash_log_contained_or_optional"] = line_status(
            (not crash_log_path) or path_is_contained(crash_log_path, triage_log_root),
            crash_log_path or "crash log not bundled",
        )

    if expected_lane:
        checks["suggested_lane_expected"] = line_status(
            classification["suggested_lane"] == expected_lane,
            classification["suggested_lane"],
        )
    else:
        checks["safe_unknown_lane"] = line_status(
            classification["suggested_lane"] == "No confident internal repro lane suggestion yet",
            classification["suggested_lane"],
        )

    if expect_repro_path:
        checks["repro_path_expected"] = line_status(
            classification["suggested_repro_path"] == DESKTOP_LAUNCHER_REGRESSION_HARNESS,
            classification["suggested_repro_path"],
        )
    else:
        checks["repro_path_absent"] = line_status(
            not classification["suggested_repro_path"],
            classification["suggested_repro_path"] or "none",
        )

    for fragment in expected_fragments:
        checks[f"matched::{fragment}"] = line_status(
            fragment in classification["matched_fragments"],
            fragment,
        )

    if expected_key == "unknown":
        checks["matched_fragments_empty"] = line_status(
            not classification["matched_fragments"],
            "matched fragments empty",
        )

    return {
        "name": name,
        "input_path": input_path,
        "report_path": report_path,
        "json_path": json_path,
        "classification_key": classification["classification_key"],
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
        "JARVIS SUPPORT BUNDLE TRIAGE HARNESS",
        f"Report: {report_path}",
        f"Branch: {branch_state}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
    ]

    for section in sections:
        lines.append(f"{section['name']}:")
        if section.get("input_path"):
            lines.append(f"  input: {section['input_path']}")
        if section.get("runtime_log"):
            lines.append(f"  artifact: {section['runtime_log']}")
        if section.get("report_path"):
            lines.append(f"  triage report: {section['report_path']}")
        if section.get("json_path"):
            lines.append(f"  triage json: {section['json_path']}")
        if section.get("classification_key"):
            lines.append(f"  classification: {section['classification_key']}")
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
    ensure_dir(VERIFICATION_DIR)

    branch_state = detect_branch_state()

    prerequisite_section = run_launcher_regression_prerequisite()

    support_module = load_module_from_path("jarvis_support_reporting_module", SUPPORT_REPORTING_SCRIPT)
    triage_module = load_module_from_path("jarvis_support_bundle_triage_module", TRIAGE_SCRIPT)

    _, _, repeated_crash_bundle = create_support_bundle(support_module, LANE_ROOTS["repeated_crash"])
    _, _, startup_abort_bundle = create_support_bundle(support_module, LANE_ROOTS["startup_abort"])
    _, _, stable_bundle = create_support_bundle(support_module, LANE_ROOTS["stable_max_attempt"])
    _, _, unstable_bundle = create_support_bundle(support_module, LANE_ROOTS["unstable_max_attempt"])

    unstable_extracted_root = extract_bundle(
        unstable_bundle["bundle_path"],
        os.path.join(VERIFICATION_DIR, "unstable_bundle_extracted"),
    )
    synthetic_unknown_root = create_unknown_bundle(os.path.join(VERIFICATION_DIR, "synthetic_unknown_bundle"))

    repeated_crash_section = run_triage_case(
        triage_module=triage_module,
        triage_log_root=TRIAGE_LOG_ROOT,
        name="Triage Zip Input: Repeated-Identical-Crash Threshold",
        input_path=repeated_crash_bundle["bundle_path"],
        input_mode="zip",
        expected_key="launcher_repeated_identical_crash_threshold",
        expected_lane="Desktop Launcher Regression Harness :: Repeated-Identical-Crash Threshold",
        expected_confidence="high",
        expected_fragments=[
            "Recovery Outcome: Automatic recovery stopped after repeated identical crash outcomes reached the launcher escalation threshold.",
            "Attempt Pattern: repeated identical crash",
        ],
        expect_repro_path=True,
    )

    startup_abort_section = run_triage_case(
        triage_module=triage_module,
        triage_log_root=TRIAGE_LOG_ROOT,
        name="Triage Zip Input: Startup-Abort Threshold",
        input_path=startup_abort_bundle["bundle_path"],
        input_mode="zip",
        expected_key="launcher_startup_abort_threshold",
        expected_lane="Desktop Launcher Regression Harness :: Startup-Abort Threshold",
        expected_confidence="high",
        expected_fragments=[
            "Recovery Outcome: Automatic recovery stopped after repeated startup aborts reached the launcher escalation threshold.",
            "Attempt Pattern: repeated startup aborts",
        ],
        expect_repro_path=True,
    )

    stable_max_attempt_section = run_triage_case(
        triage_module=triage_module,
        triage_log_root=TRIAGE_LOG_ROOT,
        name="Triage Zip Input: Stable Max-Attempt Exhaustion",
        input_path=stable_bundle["bundle_path"],
        input_mode="zip",
        expected_key="launcher_max_attempt_stable_non_threshold",
        expected_lane="Desktop Launcher Regression Harness :: Max-Attempt Exhaustion: Stable Non-Threshold Failure",
        expected_confidence="high",
        expected_fragments=[
            "Recovery Outcome: Automatic recovery did not change the underlying renderer failure.",
            "Attempt Pattern: repeated identical failure across recovery attempts",
        ],
        expect_repro_path=True,
    )

    unstable_max_attempt_section = run_triage_case(
        triage_module=triage_module,
        triage_log_root=TRIAGE_LOG_ROOT,
        name="Triage Extracted Input: Unstable Max-Attempt Exhaustion",
        input_path=unstable_extracted_root,
        input_mode="folder",
        expected_key="launcher_max_attempt_unstable_non_threshold",
        expected_lane="Desktop Launcher Regression Harness :: Max-Attempt Exhaustion: Unstable Non-Threshold Failure",
        expected_confidence="high",
        expected_fragments=[
            "Recovery Outcome: Automatic recovery completed without resolving the renderer failure.",
            "Failure Stability: unstable across recovery attempts",
            "Attempt Pattern: mixed failure sequence observed",
        ],
        expect_repro_path=True,
    )

    unknown_section = run_triage_case(
        triage_module=triage_module,
        triage_log_root=TRIAGE_LOG_ROOT,
        name="Triage Extracted Input: Safe Unknown Fallback",
        input_path=synthetic_unknown_root,
        input_mode="folder",
        expected_key="unknown",
        expected_lane="",
        expected_confidence="low",
        expected_fragments=[],
        expect_repro_path=False,
    )

    sections = [
        prerequisite_section,
        repeated_crash_section,
        startup_abort_section,
        stable_max_attempt_section,
        unstable_max_attempt_section,
        unknown_section,
    ]

    failures = []
    for section in sections:
        failures.extend(collect_failures(section))

    overall_ok = not failures
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"SupportBundleTriageHarnessReport_{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"SupportBundleTriageHarnessReport_{stamp}.json")
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
