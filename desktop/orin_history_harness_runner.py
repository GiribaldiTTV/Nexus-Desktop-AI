import argparse
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
LAUNCHER_SCRIPT = Path(__file__).with_name("jarvis_desktop_launcher.pyw")
LIVE_LOG_DIR = ROOT_DIR / "logs"
HISTORY_FILENAME = "jarvis_history_v1.jsonl"
HISTORY_STABILITY_WINDOW_SIZE = 5

def historical_context_match_line(count):
    return (
        "Historical context (derived from prior finalized recorded history only): "
        f"matching failure fingerprint observed in {count} prior run(s)."
    )


HISTORICAL_CONTEXT_STABILITY_LINE = (
    "Historical context (derived from prior finalized recorded history only): "
    "recent recorded failure history stability = stable."
)


def historical_advisory_line(count):
    return (
        "Advisory inference (derived from prior finalized history, non-binding, non-authoritative): "
        f"this finalized failure fingerprint has appeared in {count} prior finalized failed run(s)."
    )


HISTORICAL_CONTEXT_MATCH_LINE = historical_context_match_line(1)
HISTORICAL_ADVISORY_LINE = historical_advisory_line(1)
HISTORICAL_CONTEXT_VARIED_LINE = (
    "Historical context (derived from prior finalized recorded history only): "
    "recent recorded failure history stability = varied."
)
HISTORICAL_VARIED_ADVISORY_LINE = (
    "Advisory inference (derived from prior finalized history, non-binding, non-authoritative): "
    "recent prior finalized failed runs have been varied, so this run appears within a changing failure history."
)
HISTORY_FAILURE_RUNTIME_PREFIX = "Historical recorder failed; continuing without history:"
FORBIDDEN_CONFIDENCE_SURFACE_TOKENS = (
    "Confidence:",
    "direct_evidence",
    "pattern_evidence",
)

HEALTHY_RENDERER_SCRIPT = """import sys
from pathlib import Path

runtime_log = ""
for index, arg in enumerate(sys.argv):
    if arg == "--runtime-log" and index + 1 < len(sys.argv):
        runtime_log = sys.argv[index + 1]
        break

if runtime_log:
    Path(runtime_log).parent.mkdir(parents=True, exist_ok=True)
    with open(runtime_log, "a", encoding="utf-8") as handle:
        handle.write("[00:00:00] RENDERER_MAIN|STARTUP_READY\\n")

raise SystemExit(0)
"""

FAILURE_RENDERER_SCRIPT = """import sys
from pathlib import Path

runtime_log = ""
for index, arg in enumerate(sys.argv):
    if arg == "--runtime-log" and index + 1 < len(sys.argv):
        runtime_log = sys.argv[index + 1]
        break

if runtime_log:
    Path(runtime_log).parent.mkdir(parents=True, exist_ok=True)
    with open(runtime_log, "a", encoding="utf-8") as handle:
        handle.write("[00:00:00] RENDERER_MAIN|STARTUP_READY\\n")

raise RuntimeError("Synthetic renderer failure")
"""


class HarnessAssertionError(RuntimeError):
    pass


def strip_label_prefix(value, prefix):
    text = (value or "").strip()
    if text.startswith(prefix):
        return text[len(prefix):].strip()
    return text


def normalize_policy_value(value, prefix=""):
    text = strip_label_prefix(value, prefix)
    return " ".join(text.split()).casefold()


def normalize_failure_fingerprint_text(failure_fingerprint):
    text = (failure_fingerprint or "").strip()
    if not text:
        return ""

    normalized_parts = []
    for raw_part in text.split("|"):
        part = raw_part.strip()
        if not part or "=" not in part:
            return ""

        key, raw_value = part.split("=", 1)
        normalized_key = " ".join(key.split()).casefold()
        normalized_value = normalize_policy_value(raw_value)
        if not normalized_key or not normalized_value:
            return ""

        normalized_parts.append(f"{normalized_key}={normalized_value}")

    return "|".join(normalized_parts)


def parse_failure_fingerprint(failure_fingerprint):
    components = {}
    normalized = normalize_failure_fingerprint_text(failure_fingerprint)
    if not normalized:
        return components

    for part in normalized.split("|"):
        key, value = part.split("=", 1)
        components[key] = value
    return components


def replace_failure_fingerprint_component(failure_fingerprint, key, new_value):
    components = parse_failure_fingerprint(failure_fingerprint)
    assert_true(bool(components), f"Cannot replace component in invalid failure fingerprint: {failure_fingerprint}")
    assert_true(key in components, f"Failure fingerprint missing component {key}: {failure_fingerprint}")
    components[key] = normalize_policy_value(new_value)
    ordered_keys = ("classification", "cause", "origin")
    return "|".join(f"{component_key}={components[component_key]}" for component_key in ordered_keys if component_key in components)


def is_contract_valid_history_record(record):
    if not isinstance(record, dict):
        return False

    final_outcome = (record.get("final_outcome") or "").strip()
    failure_fingerprint = record.get("failure_fingerprint")
    if not isinstance(failure_fingerprint, str):
        return False

    normalized_failure_fingerprint = normalize_failure_fingerprint_text(failure_fingerprint)
    if final_outcome == "SUCCESS":
        return failure_fingerprint == ""
    if final_outcome == "FAILURE":
        return bool(normalized_failure_fingerprint) and failure_fingerprint == normalized_failure_fingerprint
    return False


def assert_failure_fingerprint_contract(record):
    fingerprint = record["failure_fingerprint"]
    if record["final_outcome"] == "SUCCESS":
        assert_true(fingerprint == "", "SUCCESS history records must keep an empty failure_fingerprint.")
        return

    normalized_fingerprint = normalize_failure_fingerprint_text(fingerprint)
    assert_true(bool(normalized_fingerprint), "FAILURE history records must keep a non-empty normalized failure_fingerprint.")
    assert_true(fingerprint == normalized_fingerprint, "FAILURE history records must keep a normalized failure_fingerprint.")
    components = parse_failure_fingerprint(fingerprint)
    assert_true("classification" in components, "FAILURE history fingerprints must include classification.")
    assert_true(set(components).issubset({"classification", "cause", "origin"}), "FAILURE history fingerprints contain unsupported components.")


def parse_args():
    parser = argparse.ArgumentParser(description="Contained historical-memory harness runner.")
    parser.add_argument(
        "--workspace-root",
        default="",
        help="Base directory for contained workspaces. Defaults to a temporary directory outside the live logs tree.",
    )
    return parser.parse_args()


def is_relative_to(path, parent):
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def assert_true(condition, message):
    if not condition:
        raise HarnessAssertionError(message)


def resolve_workspace_root(raw_value):
    if raw_value:
        workspace_root = Path(raw_value).resolve()
        workspace_root.mkdir(parents=True, exist_ok=True)
    else:
        workspace_root = Path(tempfile.mkdtemp(prefix="jarvis_fb014_rev1b_")).resolve()

    assert_true(
        not is_relative_to(workspace_root, LIVE_LOG_DIR),
        f"Contained workspace root must not be inside the live logs tree: {workspace_root}",
    )
    return workspace_root


def load_launcher_probe_namespace(workspace_root):
    probe_root = workspace_root / "_launcher_confidence_probe"
    probe_log_root = probe_root / "logs"
    probe_root.mkdir(parents=True, exist_ok=True)

    env_names = (
        "JARVIS_HARNESS_LOG_ROOT",
        "JARVIS_HARNESS_TARGET_SCRIPT",
        "JARVIS_HARNESS_DISABLE_DIAGNOSTICS",
        "JARVIS_HARNESS_DISABLE_VOICE",
    )
    original_env = {name: os.environ.get(name) for name in env_names}
    os.environ["JARVIS_HARNESS_LOG_ROOT"] = str(probe_log_root)
    os.environ["JARVIS_HARNESS_TARGET_SCRIPT"] = str(probe_root / "probe_renderer.py")
    os.environ["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    os.environ["JARVIS_HARNESS_DISABLE_VOICE"] = "1"

    try:
        return runpy.run_path(str(LAUNCHER_SCRIPT), run_name="jarvis_launcher_probe")
    finally:
        for name, value in original_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def snapshot_live_log_tree():
    if not LIVE_LOG_DIR.exists():
        return {}

    snapshot = {}
    for path in LIVE_LOG_DIR.rglob("*"):
        if path.is_file():
            stat = path.stat()
            snapshot[str(path.resolve())] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def serialize_history_record(record):
    return json.dumps(record, sort_keys=True)


def prepare_workspace(workspace_root, scenario_name):
    scenario_root = workspace_root / scenario_name
    if scenario_root.exists():
        shutil.rmtree(scenario_root)
    scenario_root.mkdir(parents=True)
    return scenario_root


def create_renderer_script(path, script_text):
    write_text(path, script_text)


def parse_history_file(path):
    raw_lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    valid_lines = []
    records = []
    for line in raw_lines:
        try:
            record = json.loads(line)
        except Exception:
            continue
        if not is_contract_valid_history_record(record):
            continue
        valid_lines.append(line)
        records.append(record)
    return raw_lines, valid_lines, records


def collect_single_file(directory, pattern, required):
    matches = sorted(directory.glob(pattern))
    if required:
        assert_true(len(matches) == 1, f"Expected exactly one {pattern} in {directory}, found {len(matches)}.")
        return matches[0]
    assert_true(len(matches) <= 1, f"Expected at most one {pattern} in {directory}, found {len(matches)}.")
    return matches[0] if matches else None


def run_launcher_scenario(scenario_root, renderer_script, seed_history_lines=None, precreate_history_directory=False):
    log_root = scenario_root / "logs"
    log_root.mkdir(parents=True, exist_ok=True)
    history_path = log_root / HISTORY_FILENAME
    if precreate_history_directory:
        history_path.mkdir(parents=True, exist_ok=True)
    elif seed_history_lines:
        write_text(history_path, "\n".join(seed_history_lines) + "\n")

    live_log_snapshot_before = snapshot_live_log_tree()

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = str(log_root)
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = str(renderer_script)
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"

    result = subprocess.run(
        [sys.executable, str(LAUNCHER_SCRIPT)],
        cwd=str(scenario_root),
        env=env,
        capture_output=True,
        text=True,
    )

    live_log_snapshot_after = snapshot_live_log_tree()
    assert_true(
        live_log_snapshot_before == live_log_snapshot_after,
        "Contained scenario wrote to or modified the live production logs tree.",
    )

    runtime_file = collect_single_file(log_root, "Runtime_*.txt", required=True)
    crash_dir = log_root / "crash"
    crash_file = collect_single_file(crash_dir, "Crash_*.txt", required=False) if crash_dir.exists() else None
    assert_true(history_path.exists(), f"Missing history file for scenario: {history_path}")

    raw_history_lines = []
    history_lines = []
    history_records = []
    if history_path.is_file():
        raw_history_lines, history_lines, history_records = parse_history_file(history_path)
    runtime_text = runtime_file.read_text(encoding="utf-8")
    crash_text = crash_file.read_text(encoding="utf-8") if crash_file else ""

    lingering_paths = {
        "diagnostics_status": log_root / "diagnostics_status.txt",
        "diagnostics_stop": log_root / "diagnostics_stop.signal",
        "startup_abort": log_root / "renderer_startup_abort.signal",
    }

    return {
        "scenario_root": scenario_root,
        "log_root": log_root,
        "renderer_script": renderer_script,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "runtime_file": runtime_file,
        "runtime_text": runtime_text,
        "crash_file": crash_file,
        "crash_text": crash_text,
        "history_path": history_path,
        "history_is_directory": history_path.is_dir(),
        "raw_history_lines": raw_history_lines,
        "history_lines": history_lines,
        "history_records": history_records,
        "lingering_paths": lingering_paths,
    }


def assert_no_lingering_artifacts(result):
    for label, path in result["lingering_paths"].items():
        assert_true(not path.exists(), f"Lingering {label} artifact detected: {path}")


def assert_no_historical_output(text):
    assert_true("Historical context (derived from prior finalized recorded history only):" not in text, "Unexpected historical context output present.")
    assert_true("Advisory inference (derived from prior finalized history, non-binding, non-authoritative):" not in text, "Unexpected historical advisory output present.")


def assert_no_confidence_output(text):
    for token in FORBIDDEN_CONFIDENCE_SURFACE_TOKENS:
        assert_true(token not in text, f"Unexpected surfaced confidence output present: {token}")


def validate_internal_confidence_contract(workspace_root):
    namespace = load_launcher_probe_namespace(workspace_root)
    build_historical_advisory_inference = namespace["build_historical_advisory_inference"]
    select_historical_advisory_hint = namespace["select_historical_advisory_hint"]
    direct_confidence = namespace["ADVISORY_CONFIDENCE_DIRECT_EVIDENCE"]
    pattern_confidence = namespace["ADVISORY_CONFIDENCE_PATTERN_EVIDENCE"]

    direct_context = {
        "history_loaded": True,
        "matching_failure_recurrence": 2,
        "recent_history_stability": "stable",
    }
    direct_inference = build_historical_advisory_inference(direct_context)
    assert_true(direct_inference["confidence"] == direct_confidence, "Exact recurrence advisory should map to direct evidence confidence.")
    assert_true(
        select_historical_advisory_hint(direct_context) == historical_advisory_line(2),
        "Exact recurrence advisory output should remain unchanged while confidence stays internal.",
    )

    varied_context = {
        "history_loaded": True,
        "matching_failure_recurrence": 0,
        "recent_history_stability": "varied",
    }
    varied_inference = build_historical_advisory_inference(varied_context)
    assert_true(varied_inference["confidence"] == pattern_confidence, "Varied-history advisory should map to pattern evidence confidence.")
    assert_true(
        select_historical_advisory_hint(varied_context) == HISTORICAL_VARIED_ADVISORY_LINE,
        "Varied-history advisory output should remain unchanged while confidence stays internal.",
    )

    assert_true(
        build_historical_advisory_inference(
            {
                "history_loaded": True,
                "matching_failure_recurrence": 0,
                "recent_history_stability": "stable",
            }
        ) == {},
        "Stable no-match history should not produce an advisory inference payload.",
    )
    assert_true(
        build_historical_advisory_inference(
            {
                "history_loaded": False,
                "matching_failure_recurrence": 0,
                "recent_history_stability": "stable",
            }
        ) == {},
        "History-unloaded context should not produce an advisory inference payload.",
    )


def validate_healthy(result):
    assert_true(result["returncode"] == 0, "Healthy scenario launcher exit code was not 0.")
    assert_true(result["crash_file"] is None, "Healthy scenario should not produce a crash log.")
    assert_true(len(result["history_records"]) == 1, "Healthy scenario should write exactly one history record.")
    record = result["history_records"][0]
    assert_true(record["final_outcome"] == "SUCCESS", "Healthy scenario history final_outcome must be SUCCESS.")
    assert_true(record["final_classification"] == "NORMAL_EXIT_COMPLETE", "Healthy scenario final_classification must be NORMAL_EXIT_COMPLETE.")
    assert_true(record["attempt_count"] == 1, "Healthy scenario attempt_count must be 1.")
    assert_failure_fingerprint_contract(record)
    assert_true("STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE" in result["runtime_text"], "Healthy scenario missing NORMAL_EXIT_COMPLETE runtime marker.")
    assert_no_historical_output(result["runtime_text"])
    assert_no_confidence_output(result["runtime_text"])
    assert_no_lingering_artifacts(result)


def validate_failed_no_history(result):
    assert_true(result["returncode"] == 0, "Failed scenario launcher exit code was not 0.")
    assert_true(result["crash_file"] is not None, "Failed scenario should produce a crash log.")
    assert_true(len(result["history_records"]) == 1, "Failed scenario with no prior history should end with exactly one history record.")
    record = result["history_records"][0]
    assert_true(record["final_outcome"] == "FAILURE", "Failed scenario final_outcome must be FAILURE.")
    assert_true(
        record["final_classification"] == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
        "Failed scenario final_classification must reflect the repeated identical crash threshold.",
    )
    assert_true(record["attempt_pattern"] == "repeated identical crash", "Failed scenario attempt_pattern drifted from repeated identical crash.")
    assert_failure_fingerprint_contract(record)
    assert_true("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in result["runtime_text"], "Failed scenario missing FAILURE_FLOW_COMPLETE marker.")
    assert_no_historical_output(result["runtime_text"])
    assert_no_historical_output(result["crash_text"])
    assert_no_confidence_output(result["runtime_text"])
    assert_no_confidence_output(result["crash_text"])
    assert_no_lingering_artifacts(result)


def validate_failed_matching_prior(result):
    assert_true(result["returncode"] == 0, "Matching-prior scenario launcher exit code was not 0.")
    assert_true(result["crash_file"] is not None, "Matching-prior scenario should produce a crash log.")
    assert_true(len(result["history_records"]) == 2, "Matching-prior scenario should end with two history records.")
    record = result["history_records"][-1]
    assert_true(record["final_outcome"] == "FAILURE", "Matching-prior scenario final_outcome must be FAILURE.")
    assert_true(
        record["final_classification"] == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
        "Matching-prior scenario final_classification must reflect the repeated identical crash threshold.",
    )
    assert_true(record["attempt_pattern"] == "repeated identical crash", "Matching-prior scenario attempt_pattern drifted from repeated identical crash.")
    assert_failure_fingerprint_contract(record)
    assert_true(result["history_records"][0]["failure_fingerprint"] == record["failure_fingerprint"], "Matching-prior scenario must match on the full normalized fingerprint.")
    assert_true(HISTORICAL_CONTEXT_MATCH_LINE in result["runtime_text"], "Matching-prior scenario missing historical recurrence context line.")
    assert_true(HISTORICAL_CONTEXT_STABILITY_LINE in result["runtime_text"], "Matching-prior scenario missing historical stability context line.")
    assert_true(HISTORICAL_ADVISORY_LINE in result["runtime_text"], "Matching-prior scenario missing historical advisory line.")
    assert_no_historical_output(result["crash_text"])
    assert_no_confidence_output(result["runtime_text"])
    assert_no_confidence_output(result["crash_text"])
    assert_no_lingering_artifacts(result)


def validate_failed_varied_prior(result):
    assert_true(result["returncode"] == 0, "Varied-prior scenario launcher exit code was not 0.")
    assert_true(result["crash_file"] is not None, "Varied-prior scenario should produce a crash log.")
    assert_true(len(result["history_records"]) == 3, "Varied-prior scenario should end with three valid history records.")
    record = result["history_records"][-1]
    assert_true(record["final_outcome"] == "FAILURE", "Varied-prior scenario final_outcome must be FAILURE.")
    assert_true(
        record["final_classification"] == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
        "Varied-prior scenario final_classification must reflect the repeated identical crash threshold.",
    )
    assert_failure_fingerprint_contract(record)
    first_seed_components = parse_failure_fingerprint(result["history_records"][0]["failure_fingerprint"])
    record_components = parse_failure_fingerprint(record["failure_fingerprint"])
    assert_true(first_seed_components.get("classification") == record_components.get("classification"), "Varied-prior scenario should keep classification equal for the near-match seed.")
    assert_true(first_seed_components.get("cause") == record_components.get("cause"), "Varied-prior scenario should keep cause equal for the near-match seed.")
    assert_true(first_seed_components.get("origin") != record_components.get("origin"), "Varied-prior scenario should differ only by origin for the near-match seed.")
    assert_true(HISTORICAL_CONTEXT_MATCH_LINE not in result["runtime_text"], "Varied-prior scenario should not emit a matching recurrence line.")
    assert_true(HISTORICAL_CONTEXT_VARIED_LINE in result["runtime_text"], "Varied-prior scenario missing varied historical stability line.")
    assert_true(HISTORICAL_VARIED_ADVISORY_LINE in result["runtime_text"], "Varied-prior scenario missing varied-history advisory line.")
    assert_no_historical_output(result["crash_text"])
    assert_no_confidence_output(result["runtime_text"])
    assert_no_confidence_output(result["crash_text"])
    assert_no_lingering_artifacts(result)


def validate_failed_success_only_prior(result):
    assert_true(result["returncode"] == 0, "Success-only-prior scenario launcher exit code was not 0.")
    assert_true(result["crash_file"] is not None, "Success-only-prior scenario should produce a crash log.")
    assert_true(len(result["history_records"]) == 2, "Success-only-prior scenario should end with two valid history records.")
    record = result["history_records"][-1]
    assert_true(record["final_outcome"] == "FAILURE", "Success-only-prior scenario final_outcome must be FAILURE.")
    assert_true(
        record["final_classification"] == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
        "Success-only-prior scenario final_classification must reflect the repeated identical crash threshold.",
    )
    assert_failure_fingerprint_contract(result["history_records"][0])
    assert_failure_fingerprint_contract(record)
    assert_no_historical_output(result["runtime_text"])
    assert_no_historical_output(result["crash_text"])
    assert_no_confidence_output(result["runtime_text"])
    assert_no_confidence_output(result["crash_text"])
    assert_no_lingering_artifacts(result)


def validate_failed_stable_window_boundary(result):
    assert_true(result["returncode"] == 0, "Stable-window-boundary scenario launcher exit code was not 0.")
    assert_true(result["crash_file"] is not None, "Stable-window-boundary scenario should produce a crash log.")
    assert_true(len(result["history_records"]) == 7, "Stable-window-boundary scenario should end with seven valid history records.")
    record = result["history_records"][-1]
    assert_true(record["final_outcome"] == "FAILURE", "Stable-window-boundary scenario final_outcome must be FAILURE.")
    assert_true(
        record["final_classification"] == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
        "Stable-window-boundary scenario final_classification must reflect the repeated identical crash threshold.",
    )
    assert_failure_fingerprint_contract(record)
    assert_true(result["history_records"][0]["failure_fingerprint"] != record["failure_fingerprint"], "Oldest seeded failure fingerprint should differ from the final failure fingerprint.")
    for seeded_record in result["history_records"][1 : HISTORY_STABILITY_WINDOW_SIZE + 1]:
        assert_true(seeded_record["failure_fingerprint"] == record["failure_fingerprint"], "Most recent seeded failure fingerprints should match the final failure fingerprint.")
    assert_true(historical_context_match_line(HISTORY_STABILITY_WINDOW_SIZE) in result["runtime_text"], "Stable-window-boundary scenario missing expected recurrence line for the recent five-record window.")
    assert_true(HISTORICAL_CONTEXT_STABILITY_LINE in result["runtime_text"], "Stable-window-boundary scenario should remain stable across the recent five-record window.")
    assert_true(historical_advisory_line(HISTORY_STABILITY_WINDOW_SIZE) in result["runtime_text"], "Stable-window-boundary scenario missing advisory line for the recent five-record window.")
    assert_true(HISTORICAL_CONTEXT_VARIED_LINE not in result["runtime_text"], "Stable-window-boundary scenario should not emit a varied stability line.")
    assert_no_historical_output(result["crash_text"])
    assert_no_confidence_output(result["runtime_text"])
    assert_no_confidence_output(result["crash_text"])
    assert_no_lingering_artifacts(result)


def validate_failed_malformed_history(result):
    assert_true(result["returncode"] == 0, "Malformed-history scenario launcher exit code was not 0.")
    assert_true(result["crash_file"] is not None, "Malformed-history scenario should produce a crash log.")
    assert_true(len(result["raw_history_lines"]) > len(result["history_records"]), "Malformed-history scenario should preserve malformed history lines.")
    assert_true(len(result["history_records"]) == 1, "Malformed-history scenario should end with exactly one valid history record.")
    record = result["history_records"][-1]
    assert_true(record["final_outcome"] == "FAILURE", "Malformed-history scenario final_outcome must be FAILURE.")
    assert_true(
        record["final_classification"] == "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
        "Malformed-history scenario final_classification must reflect the repeated identical crash threshold.",
    )
    assert_true(any('"failure_fingerprint": ""' in line for line in result["raw_history_lines"]), "Malformed-history scenario should seed an empty-fingerprint failure record.")
    assert_failure_fingerprint_contract(record)
    assert_no_historical_output(result["runtime_text"])
    assert_no_historical_output(result["crash_text"])
    assert_no_confidence_output(result["runtime_text"])
    assert_no_confidence_output(result["crash_text"])
    assert_no_lingering_artifacts(result)


def validate_failed_hostile_history_storage(result):
    assert_true(result["returncode"] == 0, "Hostile-history scenario launcher exit code was not 0.")
    assert_true(result["crash_file"] is not None, "Hostile-history scenario should produce a crash log.")
    assert_true(result["history_is_directory"], "Hostile-history scenario should leave the history path as a directory.")
    assert_true(len(result["history_records"]) == 0, "Hostile-history scenario should not produce readable history records.")
    assert_true(HISTORY_FAILURE_RUNTIME_PREFIX in result["runtime_text"], "Hostile-history scenario missing recorder failure fallback log.")
    assert_no_historical_output(result["runtime_text"])
    assert_no_historical_output(result["crash_text"])
    assert_no_confidence_output(result["runtime_text"])
    assert_no_confidence_output(result["crash_text"])
    assert_no_lingering_artifacts(result)


def print_result_summary(name, result):
    print(f"{name}: PASS")
    print(f"  workspace: {result['scenario_root']}")
    print(f"  runtime:   {result['runtime_file']}")
    if result["crash_file"] is not None:
        print(f"  crash:     {result['crash_file']}")
    print(f"  history:   {result['history_path']}")


def main():
    args = parse_args()
    workspace_root = resolve_workspace_root(args.workspace_root)
    validate_internal_confidence_contract(workspace_root)

    healthy_root = prepare_workspace(workspace_root, "healthy_run")
    healthy_renderer = healthy_root / "renderer_ready.py"
    create_renderer_script(healthy_renderer, HEALTHY_RENDERER_SCRIPT)
    healthy_result = run_launcher_scenario(healthy_root, healthy_renderer)
    validate_healthy(healthy_result)
    print_result_summary("healthy_run", healthy_result)

    failed_no_history_root = prepare_workspace(workspace_root, "failed_no_prior_history")
    failed_renderer = failed_no_history_root / "renderer_failure.py"
    create_renderer_script(failed_renderer, FAILURE_RENDERER_SCRIPT)
    failed_no_history_result = run_launcher_scenario(failed_no_history_root, failed_renderer)
    validate_failed_no_history(failed_no_history_result)
    print_result_summary("failed_no_prior_history", failed_no_history_result)

    failed_matching_prior_root = prepare_workspace(workspace_root, "failed_matching_prior_history")
    matching_renderer = failed_matching_prior_root / "renderer_failure.py"
    create_renderer_script(matching_renderer, FAILURE_RENDERER_SCRIPT)
    failed_matching_prior_result = run_launcher_scenario(
        failed_matching_prior_root,
        matching_renderer,
        seed_history_lines=failed_no_history_result["history_lines"],
    )
    validate_failed_matching_prior(failed_matching_prior_result)
    print_result_summary("failed_matching_prior_history", failed_matching_prior_result)

    base_failure_record = dict(failed_no_history_result["history_records"][0])
    varied_seed_lines = [
        serialize_history_record(
            {
                **base_failure_record,
                "run_id": "SEED_NEAR_MATCH_ORIGIN_ONLY",
                "recorded_at": "2026-03-27T00:00:00Z",
                "failure_fingerprint": replace_failure_fingerprint_component(
                    base_failure_record["failure_fingerprint"],
                    "origin",
                    "synthetic alternate origin",
                ),
            }
        ),
        serialize_history_record(
            {
                **base_failure_record,
                "run_id": "SEED_VARIED_B",
                "recorded_at": "2026-03-27T00:00:01Z",
                "failure_fingerprint": "classification=synthetic-varied-b|cause=synthetic failure b|origin=synthetic/b",
                "final_classification": "SYNTHETIC_VARIED_B",
                "end_reason": "SYNTHETIC_VARIED_B",
            }
        ),
    ]

    failed_varied_prior_root = prepare_workspace(workspace_root, "failed_varied_prior_history")
    varied_renderer = failed_varied_prior_root / "renderer_failure.py"
    create_renderer_script(varied_renderer, FAILURE_RENDERER_SCRIPT)
    failed_varied_prior_result = run_launcher_scenario(
        failed_varied_prior_root,
        varied_renderer,
        seed_history_lines=varied_seed_lines,
    )
    validate_failed_varied_prior(failed_varied_prior_result)
    print_result_summary("failed_varied_prior_history", failed_varied_prior_result)

    failed_success_only_prior_root = prepare_workspace(workspace_root, "failed_success_only_prior_history")
    success_only_renderer = failed_success_only_prior_root / "renderer_failure.py"
    create_renderer_script(success_only_renderer, FAILURE_RENDERER_SCRIPT)
    failed_success_only_prior_result = run_launcher_scenario(
        failed_success_only_prior_root,
        success_only_renderer,
        seed_history_lines=healthy_result["history_lines"],
    )
    validate_failed_success_only_prior(failed_success_only_prior_result)
    print_result_summary("failed_success_only_prior_history", failed_success_only_prior_result)

    stable_window_boundary_seed_lines = [
        serialize_history_record(
            {
                **base_failure_record,
                "run_id": "SEED_WINDOW_OLDEST_DIFFERENT",
                "recorded_at": "2026-03-27T00:00:02Z",
                "failure_fingerprint": "classification=synthetic-window-oldest|cause=synthetic oldest failure|origin=synthetic/window-oldest",
                "final_classification": "SYNTHETIC_WINDOW_OLDEST",
                "end_reason": "SYNTHETIC_WINDOW_OLDEST",
            }
        )
    ]
    for index in range(HISTORY_STABILITY_WINDOW_SIZE):
        stable_window_boundary_seed_lines.append(
            serialize_history_record(
                {
                    **base_failure_record,
                    "run_id": f"SEED_WINDOW_RECENT_{index + 1}",
                    "recorded_at": f"2026-03-27T00:00:0{index + 3}Z",
                }
            )
        )

    failed_stable_window_boundary_root = prepare_workspace(workspace_root, "failed_stable_window_boundary")
    stable_window_renderer = failed_stable_window_boundary_root / "renderer_failure.py"
    create_renderer_script(stable_window_renderer, FAILURE_RENDERER_SCRIPT)
    failed_stable_window_boundary_result = run_launcher_scenario(
        failed_stable_window_boundary_root,
        stable_window_renderer,
        seed_history_lines=stable_window_boundary_seed_lines,
    )
    validate_failed_stable_window_boundary(failed_stable_window_boundary_result)
    print_result_summary("failed_stable_window_boundary", failed_stable_window_boundary_result)

    failed_malformed_history_root = prepare_workspace(workspace_root, "failed_malformed_history")
    malformed_renderer = failed_malformed_history_root / "renderer_failure.py"
    create_renderer_script(malformed_renderer, FAILURE_RENDERER_SCRIPT)
    failed_malformed_history_result = run_launcher_scenario(
        failed_malformed_history_root,
        malformed_renderer,
        seed_history_lines=[
            serialize_history_record(
                {
                    **base_failure_record,
                    "run_id": "SEED_EMPTY_FINGERPRINT",
                    "recorded_at": "2026-03-27T00:00:02Z",
                    "failure_fingerprint": "",
                }
            ),
            "{not-json",
            "not a valid json line",
        ],
    )
    validate_failed_malformed_history(failed_malformed_history_result)
    print_result_summary("failed_malformed_history", failed_malformed_history_result)

    failed_hostile_history_root = prepare_workspace(workspace_root, "failed_hostile_history_storage")
    hostile_renderer = failed_hostile_history_root / "renderer_failure.py"
    create_renderer_script(hostile_renderer, FAILURE_RENDERER_SCRIPT)
    failed_hostile_history_result = run_launcher_scenario(
        failed_hostile_history_root,
        hostile_renderer,
        precreate_history_directory=True,
    )
    validate_failed_hostile_history_storage(failed_hostile_history_result)
    print_result_summary("failed_hostile_history_storage", failed_hostile_history_result)

    print(f"Workspace root: {workspace_root}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except HarnessAssertionError as exc:
        print(f"FB-014 harness failure: {exc}", file=sys.stderr)
        raise SystemExit(1)
