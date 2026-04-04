import datetime
import json
import os
import shutil
import sys
import tempfile
import zipfile


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
DEFAULT_BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "support_bundle_triage")
MANIFEST_FILENAME = "manifest.json"

DESKTOP_LAUNCHER_REGRESSION_HARNESS = os.path.join(ROOT_DIR, "dev", "jarvis_desktop_launcher_regression_harness.py")

SUPPORTED_CLASSES = {
    "launcher_repeated_identical_crash_threshold": {
        "label": "Launcher repeated-identical-crash threshold",
        "lane": "Desktop Launcher Regression Harness :: Repeated-Identical-Crash Threshold",
        "repro_path": DESKTOP_LAUNCHER_REGRESSION_HARNESS,
    },
    "launcher_startup_abort_threshold": {
        "label": "Launcher startup-abort threshold",
        "lane": "Desktop Launcher Regression Harness :: Startup-Abort Threshold",
        "repro_path": DESKTOP_LAUNCHER_REGRESSION_HARNESS,
    },
    "launcher_max_attempt_stable_non_threshold": {
        "label": "Launcher max-attempt stable non-threshold failure",
        "lane": "Desktop Launcher Regression Harness :: Max-Attempt Exhaustion: Stable Non-Threshold Failure",
        "repro_path": DESKTOP_LAUNCHER_REGRESSION_HARNESS,
    },
    "launcher_max_attempt_unstable_non_threshold": {
        "label": "Launcher max-attempt unstable non-threshold failure",
        "lane": "Desktop Launcher Regression Harness :: Max-Attempt Exhaustion: Unstable Non-Threshold Failure",
        "repro_path": DESKTOP_LAUNCHER_REGRESSION_HARNESS,
    },
}


class SupportBundleTriageError(RuntimeError):
    pass


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def read_lines(path):
    if not path or not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return [line.rstrip("\r\n") for line in handle]


def contains_line_fragment(lines, fragment):
    return any(fragment in line for line in lines)


def find_bundle_root(start_path):
    if os.path.isfile(start_path):
        raise SupportBundleTriageError("Expected a folder while locating the bundle root.")

    direct_manifest = os.path.join(start_path, MANIFEST_FILENAME)
    if os.path.isfile(direct_manifest):
        return start_path

    candidates = []
    for root, _, files in os.walk(start_path):
        if MANIFEST_FILENAME in files:
            candidates.append(root)

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise SupportBundleTriageError("No manifest.json was found in the provided support bundle path.")

    raise SupportBundleTriageError("Multiple manifest.json files were found; provide a single extracted support bundle folder.")


def resolve_base_log_root(log_root_override=None):
    if log_root_override:
        return os.path.abspath(log_root_override)
    return DEFAULT_BASE_LOG_ROOT


def reports_dir_for(base_log_root):
    return os.path.join(base_log_root, "reports")


def extract_bundle_if_needed(bundle_path, base_log_root):
    normalized = os.path.abspath(bundle_path)
    cleanup_dir = ""

    if os.path.isdir(normalized):
        return find_bundle_root(normalized), cleanup_dir

    if not zipfile.is_zipfile(normalized):
        raise SupportBundleTriageError("The support bundle path must be a .zip file or an extracted bundle folder.")

    temp_root = tempfile.mkdtemp(prefix="jarvis_support_bundle_", dir=base_log_root)
    cleanup_dir = temp_root
    with zipfile.ZipFile(normalized, "r") as archive:
        archive.extractall(temp_root)
    return find_bundle_root(temp_root), cleanup_dir


def load_manifest(bundle_root):
    manifest_path = os.path.join(bundle_root, MANIFEST_FILENAME)
    if not os.path.isfile(manifest_path):
        raise SupportBundleTriageError("The support bundle manifest.json file is missing.")
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    return manifest_path, manifest


def resolve_bundled_file(bundle_root, manifest, expected_kind):
    for entry in manifest.get("bundled_files", []):
        if entry.get("kind") != expected_kind:
            continue
        name = entry.get("name", "")
        if not name:
            continue
        path = os.path.join(bundle_root, name)
        if os.path.isfile(path):
            return path
    return ""


def make_check(ok, detail):
    return {"ok": bool(ok), "detail": detail}


def classify_bundle(runtime_lines, crash_lines):
    combined_lines = runtime_lines + crash_lines
    matches = []

    repeated_identical_crash = (
        contains_line_fragment(runtime_lines, "STATUS|FAIL|RECOVERY_PIPELINE|CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED")
        or contains_line_fragment(combined_lines, "Recovery Outcome: Automatic recovery stopped after repeated identical crash outcomes reached the launcher escalation threshold.")
        or contains_line_fragment(combined_lines, "Attempt Pattern: repeated identical crash")
    )
    if repeated_identical_crash:
        matches.append(
            {
                "key": "launcher_repeated_identical_crash_threshold",
                "confidence": "high",
                "matched_fragments": [
                    fragment
                    for fragment in [
                        "STATUS|FAIL|RECOVERY_PIPELINE|CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
                        "Recovery Outcome: Automatic recovery stopped after repeated identical crash outcomes reached the launcher escalation threshold.",
                        "Attempt Pattern: repeated identical crash",
                    ]
                    if contains_line_fragment(combined_lines, fragment)
                ],
            }
        )

    repeated_startup_abort = (
        contains_line_fragment(runtime_lines, "STATUS|FAIL|RECOVERY_PIPELINE|CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED")
        or contains_line_fragment(combined_lines, "Recovery Outcome: Automatic recovery stopped after repeated startup aborts reached the launcher escalation threshold.")
        or contains_line_fragment(combined_lines, "Attempt Pattern: repeated startup aborts")
    )
    if repeated_startup_abort:
        matches.append(
            {
                "key": "launcher_startup_abort_threshold",
                "confidence": "high",
                "matched_fragments": [
                    fragment
                    for fragment in [
                        "STATUS|FAIL|RECOVERY_PIPELINE|CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED",
                        "Recovery Outcome: Automatic recovery stopped after repeated startup aborts reached the launcher escalation threshold.",
                        "Attempt Pattern: repeated startup aborts",
                    ]
                    if contains_line_fragment(combined_lines, fragment)
                ],
            }
        )

    stable_max_attempt = (
        contains_line_fragment(runtime_lines, "STATUS|FAIL|RECOVERY_PIPELINE|MAX_ATTEMPTS_EXHAUSTED")
        and not contains_line_fragment(runtime_lines, "STATUS|FAIL|RECOVERY_PIPELINE|MAX_ATTEMPTS_EXHAUSTED_WITH_INSTABILITY")
        and contains_line_fragment(combined_lines, "Recovery Outcome: Automatic recovery did not change the underlying renderer failure.")
        and contains_line_fragment(combined_lines, "Attempt Pattern: repeated identical failure across recovery attempts")
        and not contains_line_fragment(combined_lines, "Failure Stability: unstable across recovery attempts")
    )
    if stable_max_attempt:
        matches.append(
            {
                "key": "launcher_max_attempt_stable_non_threshold",
                "confidence": "high",
                "matched_fragments": [
                    fragment
                    for fragment in [
                        "STATUS|FAIL|RECOVERY_PIPELINE|MAX_ATTEMPTS_EXHAUSTED",
                        "Recovery Outcome: Automatic recovery did not change the underlying renderer failure.",
                        "Attempt Pattern: repeated identical failure across recovery attempts",
                    ]
                    if contains_line_fragment(combined_lines, fragment)
                ],
            }
        )

    unstable_max_attempt = (
        contains_line_fragment(runtime_lines, "STATUS|FAIL|RECOVERY_PIPELINE|MAX_ATTEMPTS_EXHAUSTED_WITH_INSTABILITY")
        or (
            contains_line_fragment(combined_lines, "Failure Stability: unstable across recovery attempts")
            and contains_line_fragment(combined_lines, "Recovery Outcome: Automatic recovery completed without resolving the renderer failure.")
        )
    )
    if unstable_max_attempt:
        matched_fragments = [
            fragment
            for fragment in [
                "STATUS|FAIL|RECOVERY_PIPELINE|MAX_ATTEMPTS_EXHAUSTED_WITH_INSTABILITY",
                "Recovery Outcome: Automatic recovery completed without resolving the renderer failure.",
                "Failure Stability: unstable across recovery attempts",
                "Attempt Pattern: mixed failure sequence observed",
                "Attempt Pattern: varied failure outcomes across recovery attempts",
            ]
            if contains_line_fragment(combined_lines, fragment)
        ]
        matches.append(
            {
                "key": "launcher_max_attempt_unstable_non_threshold",
                "confidence": "high" if contains_line_fragment(combined_lines, "Attempt Pattern: mixed failure sequence observed") else "moderate",
                "matched_fragments": matched_fragments,
            }
        )

    if not matches:
        return {
            "classification_key": "unknown",
            "classification_label": "Unknown or unsupported support bundle class",
            "confidence": "low",
            "matched_fragments": [],
            "suggested_lane": "No confident internal repro lane suggestion yet",
            "suggested_repro_path": "",
            "reason": "The bundled evidence did not match the currently supported launcher-owned failure classes.",
        }

    match = matches[0]
    supported = SUPPORTED_CLASSES[match["key"]]
    return {
        "classification_key": match["key"],
        "classification_label": supported["label"],
        "confidence": match["confidence"],
        "matched_fragments": match["matched_fragments"],
        "suggested_lane": supported["lane"],
        "suggested_repro_path": supported["repro_path"],
        "reason": f"Matched current repo-truth launcher evidence for {supported['label'].lower()}.",
    }


def summarize_bundle(bundle_root, source_path, manifest_path, manifest, runtime_log_path, crash_log_path):
    runtime_lines = read_lines(runtime_log_path)
    crash_lines = read_lines(crash_log_path)
    classification = classify_bundle(runtime_lines, crash_lines)

    checks = {
        "manifest_loaded": make_check(bool(manifest), manifest_path),
        "runtime_log_present": make_check(bool(runtime_log_path), runtime_log_path or "runtime log missing from bundle"),
        "crash_log_present_or_optional": make_check(bool(crash_log_path) or not any(entry.get("kind") == "crash_log" for entry in manifest.get("bundled_files", [])), crash_log_path or "crash log not bundled"),
        "run_identity_present": make_check(bool(manifest.get("run_identity")), manifest.get("run_identity") or "missing run_identity"),
        "jarvis_version_present": make_check(bool(manifest.get("jarvis_version")), manifest.get("jarvis_version") or "missing jarvis_version"),
        "classification_confident_or_safe_fallback": make_check(
            classification["classification_key"] != "unknown" or classification["confidence"] == "low",
            classification["classification_label"],
        ),
    }

    return {
        "source_path": source_path,
        "bundle_root": bundle_root,
        "manifest_path": manifest_path,
        "runtime_log_path": runtime_log_path,
        "crash_log_path": crash_log_path,
        "manifest": manifest,
        "classification": classification,
        "checks": checks,
    }


def build_report_text(report_path, result):
    classification = result["classification"]
    lines = [
        "JARVIS SUPPORT BUNDLE TRIAGE",
        f"Report: {report_path}",
        f"Source: {result['source_path']}",
        f"Bundle Root: {result['bundle_root']}",
        f"Manifest: {result['manifest_path']}",
        f"Runtime Log: {result['runtime_log_path'] or 'missing'}",
        f"Crash Log: {result['crash_log_path'] or 'not bundled'}",
        "",
        "Bundle Context:",
        f"  Run Identity: {result['manifest'].get('run_identity', 'unknown')}",
        f"  Jarvis Version: {result['manifest'].get('jarvis_version', 'unknown')}",
        f"  Bundle Created At: {result['manifest'].get('bundle_created_at', 'unknown')}",
        "",
        "Classification:",
        f"  Key: {classification['classification_key']}",
        f"  Label: {classification['classification_label']}",
        f"  Confidence: {classification['confidence']}",
        f"  Reason: {classification['reason']}",
        f"  Suggested Repro Lane: {classification['suggested_lane']}",
        f"  Suggested Repro Path: {classification['suggested_repro_path'] or 'none'}",
        "",
        "Matched Evidence:",
    ]

    if classification["matched_fragments"]:
        for fragment in classification["matched_fragments"]:
            lines.append(f"  - {fragment}")
    else:
        lines.append("  - none")

    lines.append("")
    lines.append("Checks:")
    for key, value in result["checks"].items():
        lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

    lines.append("")
    lines.append("Next Steps:")
    if classification["classification_key"] == "unknown":
        lines.append("  - Review the bundled runtime/crash logs manually.")
        lines.append("  - Add or extend a contained validation lane only if this becomes a recurring unsupported class.")
    else:
        lines.append(f"  - Start with: {classification['suggested_lane']}")
        if classification["suggested_repro_path"]:
            lines.append(f"  - Primary script: {classification['suggested_repro_path']}")
        lines.append("  - Compare the bundled summary lines against the existing harness evidence before changing production behavior.")

    return "\n".join(lines) + "\n"


def write_reports(result, reports_dir):
    ensure_dir(reports_dir)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    report_path = os.path.join(reports_dir, f"SupportBundleTriageReport_{stamp}.txt")
    json_path = os.path.join(reports_dir, f"SupportBundleTriageReport_{stamp}.json")
    report_text = build_report_text(report_path, result)

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report_text)

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "source_path": result["source_path"],
                "bundle_root": result["bundle_root"],
                "manifest_path": result["manifest_path"],
                "runtime_log_path": result["runtime_log_path"],
                "crash_log_path": result["crash_log_path"],
                "manifest": result["manifest"],
                "classification": result["classification"],
                "checks": result["checks"],
                "report_path": report_path,
            },
            handle,
            indent=2,
            sort_keys=True,
        )

    return report_path, json_path, report_text


def triage_bundle(source_path, log_root_override=None):
    base_log_root = resolve_base_log_root(log_root_override)
    reports_dir = reports_dir_for(base_log_root)
    ensure_dir(base_log_root)
    bundle_root, cleanup_dir = extract_bundle_if_needed(source_path, base_log_root)
    try:
        manifest_path, manifest = load_manifest(bundle_root)
        runtime_log_path = resolve_bundled_file(bundle_root, manifest, "runtime_log")
        crash_log_path = resolve_bundled_file(bundle_root, manifest, "crash_log")
        result = summarize_bundle(bundle_root, os.path.abspath(source_path), manifest_path, manifest, runtime_log_path, crash_log_path)
        return write_reports(result, reports_dir)
    finally:
        if cleanup_dir:
            shutil.rmtree(cleanup_dir, ignore_errors=True)


def main(argv):
    if not argv:
        print("Usage: python dev/jarvis_support_bundle_triage.py <support_bundle_zip_or_folder>")
        return 1

    source_path = argv[0]
    try:
        report_path, json_path, report_text = triage_bundle(source_path)
    except SupportBundleTriageError as exc:
        print(f"Support bundle triage failed: {exc}")
        return 1

    print(report_text)
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
