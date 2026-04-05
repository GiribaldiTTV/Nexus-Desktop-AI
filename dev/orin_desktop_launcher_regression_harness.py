import datetime
import importlib.util
import json
import os
import shutil
import subprocess
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "desktop_launcher_regression_harness")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")

LAUNCHER_SCRIPT = os.path.join(ROOT_DIR, "desktop", "jarvis_desktop_launcher.pyw")
HEALTHY_VALIDATOR_SCRIPT = os.path.join(ROOT_DIR, "dev", "jarvis_desktop_launcher_healthy_validation.py")
FAILURE_TARGET = os.path.join(ROOT_DIR, "dev", "targets", "jarvis_manual_failure_target.pyw")
STARTUP_ABORT_TARGET = os.path.join(ROOT_DIR, "dev", "targets", "jarvis_manual_startup_abort_target.pyw")
MIXED_SEQUENCE_TARGET = os.path.join(ROOT_DIR, "dev", "targets", "jarvis_manual_mixed_sequence_target.pyw")
MIXED_SEQUENCE_STATE_FILE = "manual_mixed_sequence_state.txt"


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


def read_lines(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.rstrip("\r\n") for line in f]


def contains_line_fragment(lines, fragment):
    return any(fragment in line for line in lines)


def line_status(ok, detail):
    return {"ok": bool(ok), "detail": detail}


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "unavailable"


def run_command(args, env=None, timeout_seconds=120):
    return subprocess.run(
        args,
        cwd=ROOT_DIR,
        env=env,
        timeout=timeout_seconds,
        **hidden_subprocess_kwargs(),
    )


def load_module_from_path(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def path_is_within_root(path, root):
    if not path:
        return False
    try:
        return os.path.commonpath([os.path.abspath(path), os.path.abspath(root)]) == os.path.abspath(root)
    except ValueError:
        return False


def run_healthy_section():
    module = load_module_from_path("jarvis_desktop_launcher_healthy_validation_module", HEALTHY_VALIDATOR_SCRIPT)
    healthy_log_root = os.path.join(BASE_LOG_ROOT, "healthy")
    result = module.run_validation(log_root_override=healthy_log_root)
    artifacts = module.write_validation_artifacts(result)
    checks = dict(result.get("checks", {}))
    runtime_log = result.get("runtime_log", "")
    report_path = artifacts.get("report_path", "")
    checks["healthy_runtime_contained_under_harness_root"] = line_status(
        path_is_within_root(runtime_log, healthy_log_root),
        runtime_log or "missing runtime log",
    )
    checks["healthy_report_artifact_created"] = line_status(
        bool(report_path),
        report_path or "missing healthy report",
    )
    checks["healthy_report_contained_under_harness_root"] = line_status(
        path_is_within_root(report_path, healthy_log_root),
        report_path or "missing healthy report",
    )
    return {
        "name": "Healthy Default Launcher Path",
        "runtime_log": runtime_log,
        "report_path": report_path,
        "checks": checks,
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
    }


def run_failure_lane(name, target_script, log_root, expected_markers):
    reset_dir(log_root)

    env = os.environ.copy()
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = target_script
    env["JARVIS_HARNESS_LOG_ROOT"] = log_root
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"

    result = run_command([sys.executable, LAUNCHER_SCRIPT], env=env, timeout_seconds=180)

    runtime_log = latest_file_matching(log_root, "Runtime_")
    crash_log = latest_file_matching(os.path.join(log_root, "crash"), "Crash_")
    runtime_lines = read_lines(runtime_log)

    checks = {
        "launcher_exit_code_zero": line_status(
            result.returncode == 0,
            f"launcher exit={result.returncode}",
        ),
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "crash_log_created": line_status(
            bool(crash_log),
            crash_log or "missing crash log",
        ),
        "failure_flow_complete": line_status(
            contains_line_fragment(runtime_lines, "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE"),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE",
        ),
        "final_shutdown_complete": line_status(
            contains_line_fragment(runtime_lines, "Final immersive shutdown sequence finished"),
            "Final immersive shutdown sequence finished",
        ),
        "diagnostics_status_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "diagnostics_status.txt")),
            os.path.join(log_root, "diagnostics_status.txt"),
        ),
        "diagnostics_stop_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "diagnostics_stop.signal")),
            os.path.join(log_root, "diagnostics_stop.signal"),
        ),
        "startup_abort_signal_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "renderer_startup_abort.signal")),
            os.path.join(log_root, "renderer_startup_abort.signal"),
        ),
    }

    for marker in expected_markers:
        checks[f"marker::{marker}"] = line_status(
            contains_line_fragment(runtime_lines, marker),
            marker,
        )

    return {
        "name": name,
        "runtime_log": runtime_log,
        "crash_log": crash_log,
        "checks": checks,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def run_mixed_failure_lane(name, sequence_value, mixed_type, log_root):
    reset_dir(log_root)

    env = os.environ.copy()
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = MIXED_SEQUENCE_TARGET
    env["JARVIS_HARNESS_LOG_ROOT"] = log_root
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["JARVIS_MANUAL_MIXED_SEQUENCE"] = sequence_value

    result = run_command([sys.executable, LAUNCHER_SCRIPT], env=env, timeout_seconds=180)

    runtime_log = latest_file_matching(log_root, "Runtime_")
    crash_log = latest_file_matching(os.path.join(log_root, "crash"), "Crash_")
    runtime_lines = read_lines(runtime_log)

    mixed_marker = f"STATUS|WARNING|LAUNCHER_RUNTIME|MIXED_FAILURE_PATTERN_OBSERVED|TYPE={mixed_type}"
    checks = {
        "launcher_exit_code_zero": line_status(
            result.returncode == 0,
            f"launcher exit={result.returncode}",
        ),
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "mixed_pattern_observed": line_status(
            contains_line_fragment(runtime_lines, mixed_marker),
            mixed_marker,
        ),
        "normal_exit_complete": line_status(
            contains_line_fragment(runtime_lines, "STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE"),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE",
        ),
        "failure_flow_absent": line_status(
            not contains_line_fragment(runtime_lines, "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE"),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "no_false_identical_crash_threshold": line_status(
            not contains_line_fragment(runtime_lines, "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED"),
            "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED absent",
        ),
        "no_false_startup_abort_threshold": line_status(
            not contains_line_fragment(runtime_lines, "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED"),
            "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED absent",
        ),
        "crash_log_absent": line_status(
            not crash_log,
            crash_log or "no crash log generated",
        ),
        "diagnostics_status_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "diagnostics_status.txt")),
            os.path.join(log_root, "diagnostics_status.txt"),
        ),
        "diagnostics_stop_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "diagnostics_stop.signal")),
            os.path.join(log_root, "diagnostics_stop.signal"),
        ),
        "startup_abort_signal_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "renderer_startup_abort.signal")),
            os.path.join(log_root, "renderer_startup_abort.signal"),
        ),
    }

    return {
        "name": name,
        "runtime_log": runtime_log,
        "crash_log": crash_log,
        "checks": checks,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def contains_fragment_in_any(paths, fragment):
    for path in paths:
        if contains_line_fragment(read_lines(path), fragment):
            return True
    return False


def run_max_attempt_lane(name, sequence_value, expected_fragments, absent_fragments, log_root):
    reset_dir(log_root)

    env = os.environ.copy()
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = MIXED_SEQUENCE_TARGET
    env["JARVIS_HARNESS_LOG_ROOT"] = log_root
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["JARVIS_MANUAL_MIXED_SEQUENCE"] = sequence_value

    result = run_command([sys.executable, LAUNCHER_SCRIPT], env=env, timeout_seconds=180)

    runtime_log = latest_file_matching(log_root, "Runtime_")
    crash_log = latest_file_matching(os.path.join(log_root, "crash"), "Crash_")
    searchable_paths = [path for path in (runtime_log, crash_log) if path]

    checks = {
        "launcher_exit_code_zero": line_status(
            result.returncode == 0,
            f"launcher exit={result.returncode}",
        ),
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "crash_log_created": line_status(
            bool(crash_log),
            crash_log or "missing crash log",
        ),
        "failure_flow_complete": line_status(
            contains_fragment_in_any(searchable_paths, "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE"),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE",
        ),
        "final_shutdown_complete": line_status(
            contains_fragment_in_any(searchable_paths, "Final immersive shutdown sequence finished"),
            "Final immersive shutdown sequence finished",
        ),
        "diagnostics_status_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "diagnostics_status.txt")),
            os.path.join(log_root, "diagnostics_status.txt"),
        ),
        "diagnostics_stop_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "diagnostics_stop.signal")),
            os.path.join(log_root, "diagnostics_stop.signal"),
        ),
        "startup_abort_signal_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, "renderer_startup_abort.signal")),
            os.path.join(log_root, "renderer_startup_abort.signal"),
        ),
        "sequence_state_cleaned": line_status(
            not os.path.exists(os.path.join(log_root, MIXED_SEQUENCE_STATE_FILE)),
            os.path.join(log_root, MIXED_SEQUENCE_STATE_FILE),
        ),
    }

    for fragment in expected_fragments:
        checks[f"fragment::{fragment}"] = line_status(
            contains_fragment_in_any(searchable_paths, fragment),
            fragment,
        )

    for fragment in absent_fragments:
        checks[f"absent::{fragment}"] = line_status(
            not contains_fragment_in_any(searchable_paths, fragment),
            f"{fragment} absent",
        )

    return {
        "name": name,
        "runtime_log": runtime_log,
        "crash_log": crash_log,
        "checks": checks,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def collect_failures(section):
    failures = []
    for key, value in section["checks"].items():
        if not value["ok"]:
            failures.append(f"{section['name']} :: {key}: {value['detail']}")
    return failures


def build_report_text(branch_state, report_path, sections, overall_ok):
    lines = [
        "JARVIS DESKTOP LAUNCHER REGRESSION HARNESS",
        f"Report: {report_path}",
        f"Branch: {branch_state}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
    ]

    for section in sections:
        lines.append(f"{section['name']}:")
        if section.get("runtime_log"):
            lines.append(f"  runtime log: {section['runtime_log']}")
        if section.get("report_path"):
            lines.append(f"  report: {section['report_path']}")
        if section.get("crash_log") is not None:
            lines.append(f"  crash log: {section.get('crash_log') or 'none'}")
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

    branch_state = detect_branch_state()

    healthy_section = run_healthy_section()

    repeated_crash_section = run_failure_lane(
        name="Repeated-Identical-Crash Threshold",
        target_script=FAILURE_TARGET,
        log_root=os.path.join(BASE_LOG_ROOT, "repeated_crash"),
        expected_markers=[
            "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
            "STATUS|FAIL|RECOVERY_PIPELINE|CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
        ],
    )

    startup_abort_section = run_failure_lane(
        name="Startup-Abort Threshold",
        target_script=STARTUP_ABORT_TARGET,
        log_root=os.path.join(BASE_LOG_ROOT, "startup_abort"),
        expected_markers=[
            "STARTUP_READY_STALL_CONFIRMED",
            "STARTUP_ABORT_REQUESTED_ON_CONFIRMED_STALL",
            "RENDERER_MAIN|STARTUP_ABORTED",
            "STARTUP_ABORT_COMPLETE",
            "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED",
            "STATUS|FAIL|RECOVERY_PIPELINE|CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED",
        ],
    )

    crash_to_abort_section = run_mixed_failure_lane(
        name="Mixed Failure Sequence: Crash To Startup Abort",
        sequence_value="crash,abort,success",
        mixed_type="CRASH_TO_STARTUP_ABORT",
        log_root=os.path.join(BASE_LOG_ROOT, "mixed_crash_to_abort"),
    )

    abort_to_crash_section = run_mixed_failure_lane(
        name="Mixed Failure Sequence: Startup Abort To Crash",
        sequence_value="abort,crash,success",
        mixed_type="STARTUP_ABORT_TO_CRASH",
        log_root=os.path.join(BASE_LOG_ROOT, "mixed_abort_to_crash"),
    )

    stable_max_attempt_section = run_max_attempt_lane(
        name="Max-Attempt Exhaustion: Stable Non-Threshold Failure",
        sequence_value="crash_a,crash_b,crash_c",
        expected_fragments=[
            "STATUS|FAIL|RECOVERY_PIPELINE|MAX_ATTEMPTS_EXHAUSTED",
            "Automatic recovery did not change the underlying renderer failure.",
            "Attempt Pattern: repeated identical failure across recovery attempts",
        ],
        absent_fragments=[
            "STATUS|FAIL|RECOVERY_PIPELINE|MAX_ATTEMPTS_EXHAUSTED_WITH_INSTABILITY",
            "Failure Stability: unstable across recovery attempts",
            "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
            "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED",
            "MIXED_FAILURE_PATTERN_OBSERVED",
        ],
        log_root=os.path.join(BASE_LOG_ROOT, "stable_max_attempt"),
    )

    unstable_max_attempt_section = run_max_attempt_lane(
        name="Max-Attempt Exhaustion: Unstable Non-Threshold Failure",
        sequence_value="crash_a,abort,crash_beta",
        expected_fragments=[
            "STATUS|FAIL|RECOVERY_PIPELINE|MAX_ATTEMPTS_EXHAUSTED_WITH_INSTABILITY",
            "Failure Stability: unstable across recovery attempts",
            "Automatic recovery completed without resolving the renderer failure.",
            "Attempt Pattern: mixed failure sequence observed",
            "STATUS|WARNING|LAUNCHER_RUNTIME|MIXED_FAILURE_PATTERN_OBSERVED|TYPE=CRASH_TO_STARTUP_ABORT",
        ],
        absent_fragments=[
            "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
            "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED",
        ],
        log_root=os.path.join(BASE_LOG_ROOT, "unstable_max_attempt"),
    )

    sections = [
        healthy_section,
        repeated_crash_section,
        startup_abort_section,
        crash_to_abort_section,
        abort_to_crash_section,
        stable_max_attempt_section,
        unstable_max_attempt_section,
    ]
    failures = []
    for section in sections:
        failures.extend(collect_failures(section))

    overall_ok = not failures
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"DesktopLauncherRegressionHarnessReport_{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"DesktopLauncherRegressionHarnessReport_{stamp}.json")

    report_text = build_report_text(branch_state, report_path, sections, overall_ok)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "branch_state": branch_state,
                "overall_ok": overall_ok,
                "sections": sections,
                "failures": failures,
                "report_path": report_path,
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
