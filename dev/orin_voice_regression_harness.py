import datetime
import json
import os
import shutil
import subprocess
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "voice_regression_harness")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")

LAUNCHER_SCRIPT = os.path.join(ROOT_DIR, "desktop", "jarvis_desktop_launcher.pyw")
ERROR_VOICE_SCRIPT = os.path.join(ROOT_DIR, "Audio", "jarvis_error_voice.py")
NORMAL_VOICE_SCRIPT = os.path.join(ROOT_DIR, "Audio", "jarvis_voice.py")

FAILURE_TARGET = os.path.join(ROOT_DIR, "dev", "targets", "jarvis_manual_failure_target.pyw")
STARTUP_ABORT_TARGET = os.path.join(ROOT_DIR, "dev", "targets", "jarvis_manual_startup_abort_target.pyw")

EXPECTED_LAUNCHER_LINES = [
    "Uhm..... Sir, I seem to be malfunctioning.",
    "Attempting recovery.",
    "Recovery failed.",
    "Shutting down.",
]

EXPECTED_DIAGNOSTICS_LINES = [
    "Uhm..... Sir, I seem to be malfunctioning.",
    "Attempting recovery.",
    "Recovery failed.",
    "Shutting down.",
]

NORMAL_VOICE_PROBE_TEXT = "Jarvis normal voice path validation."


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


def run_command(args, env=None, timeout_seconds=120):
    return subprocess.run(
        args,
        cwd=ROOT_DIR,
        env=env,
        timeout=timeout_seconds,
        **hidden_subprocess_kwargs()
    )


def run_launcher_lane(name, target_script, log_root, expected_lane_markers):
    reset_dir(log_root)

    env = os.environ.copy()
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = target_script
    env["JARVIS_HARNESS_LOG_ROOT"] = log_root
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env.pop("JARVIS_HARNESS_DISABLE_VOICE", None)

    result = run_command([sys.executable, LAUNCHER_SCRIPT], env=env, timeout_seconds=120)

    runtime_log = latest_file_matching(log_root, "Runtime_")
    crash_dir = os.path.join(log_root, "crash")
    crash_log = latest_file_matching(crash_dir, "Crash_")
    runtime_lines = read_lines(runtime_log)

    checks = {}
    checks["launcher_exit_code"] = line_status(
        result.returncode == 0,
        f"launcher exit={result.returncode}"
    )
    checks["runtime_log_created"] = line_status(
        bool(runtime_log),
        runtime_log or "missing runtime log"
    )
    checks["crash_log_created"] = line_status(
        bool(crash_log),
        crash_log or "missing crash log"
    )

    for marker in expected_lane_markers:
        key = f"marker::{marker}"
        checks[key] = line_status(
            contains_line_fragment(runtime_lines, marker),
            marker
        )

    for line in EXPECTED_LAUNCHER_LINES:
        start_fragment = f"VOICE|START|{line}"
        end_fragment = f"VOICE|END|{line}|EXIT=0"
        checks[f"voice_start::{line}"] = line_status(
            contains_line_fragment(runtime_lines, start_fragment),
            start_fragment
        )
        checks[f"voice_end::{line}"] = line_status(
            contains_line_fragment(runtime_lines, end_fragment),
            end_fragment
        )

    checks["final_shutdown_complete"] = line_status(
        contains_line_fragment(runtime_lines, "Final immersive shutdown sequence finished"),
        "Final immersive shutdown sequence finished"
    )
    checks["diagnostics_status_cleaned"] = line_status(
        not os.path.exists(os.path.join(log_root, "diagnostics_status.txt")),
        os.path.join(log_root, "diagnostics_status.txt")
    )
    checks["diagnostics_stop_cleaned"] = line_status(
        not os.path.exists(os.path.join(log_root, "diagnostics_stop.signal")),
        os.path.join(log_root, "diagnostics_stop.signal")
    )
    checks["startup_abort_signal_cleaned"] = line_status(
        not os.path.exists(os.path.join(log_root, "renderer_startup_abort.signal")),
        os.path.join(log_root, "renderer_startup_abort.signal")
    )

    return {
        "name": name,
        "runtime_log": runtime_log,
        "crash_log": crash_log,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "checks": checks,
    }


def run_error_voice_probe(line_text, probe_root):
    reset_dir(probe_root)
    status_file = os.path.join(probe_root, "diagnostics_status.txt")
    stop_signal_file = os.path.join(probe_root, "diagnostics_stop.signal")

    with open(status_file, "w", encoding="utf-8") as f:
        f.write("")

    result = run_command(
        [
            sys.executable,
            ERROR_VOICE_SCRIPT,
            "--text", line_text,
            "--display-text", line_text,
            "--status-file", status_file,
            "--stop-signal", stop_signal_file,
        ],
        timeout_seconds=60,
    )

    status_lines = read_lines(status_file)
    sync_lines = [line for line in status_lines if line.startswith("VOICE_SYNC|")]
    final_line = f"VOICE_FINAL|{line_text}"

    return {
        "line": line_text,
        "status_file": status_file,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "checks": {
            "exit_code": line_status(result.returncode == 0, f"voice exit={result.returncode}"),
            "voice_sync_emitted": line_status(bool(sync_lines), sync_lines[-1] if sync_lines else "missing VOICE_SYNC"),
            "voice_final_emitted": line_status(final_line in status_lines, final_line),
            "stop_signal_absent": line_status(not os.path.exists(stop_signal_file), stop_signal_file),
        },
    }


def parse_last_json_line(stdout_text):
    for line in reversed([line.strip() for line in stdout_text.splitlines() if line.strip()]):
        try:
            return json.loads(line)
        except Exception:
            continue
    return None


def run_normal_voice_probe(probe_root):
    reset_dir(probe_root)
    probe_script = f"""
import asyncio
import importlib.util
import json

module_path = r"{NORMAL_VOICE_SCRIPT}"
spec = importlib.util.spec_from_file_location("jarvis_voice_probe", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

speaker = module.JarvisSpeaker()
statuses = []
states = []

def enum_name(value):
    return getattr(value, "name", str(value))

speaker.player.mediaStatusChanged.connect(lambda status: statuses.append(enum_name(status)))
speaker.player.playbackStateChanged.connect(lambda state: states.append(enum_name(state)))

asyncio.run(speaker.speak(r"{NORMAL_VOICE_PROBE_TEXT}"))

print(json.dumps({{
    "statuses": statuses,
    "states": states,
    "playing_seen": "PlayingState" in states,
    "end_seen": "EndOfMedia" in statuses,
    "invalid_seen": "InvalidMedia" in statuses,
}}))
"""

    result = run_command([sys.executable, "-c", probe_script], timeout_seconds=60)
    payload = parse_last_json_line(result.stdout.strip())

    return {
        "text": NORMAL_VOICE_PROBE_TEXT,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "payload": payload or {},
        "checks": {
            "exit_code": line_status(result.returncode == 0, f"voice exit={result.returncode}"),
            "probe_payload_parsed": line_status(bool(payload), "normal voice probe payload"),
            "playing_state_seen": line_status(bool(payload and payload.get("playing_seen")), payload.get("states") if payload else "missing payload"),
            "end_of_media_seen": line_status(bool(payload and payload.get("end_seen")), payload.get("statuses") if payload else "missing payload"),
            "invalid_media_absent": line_status(bool(payload) and not payload.get("invalid_seen"), payload.get("statuses") if payload else "missing payload"),
        },
    }


def collect_failures(section):
    failures = []
    for key, value in section["checks"].items():
        if not value["ok"]:
            failures.append(f"{key}: {value['detail']}")
    return failures


def build_report_text(branch_state, report_path, launcher_sections, probe_sections, normal_section, overall_ok):
    lines = [
        "JARVIS VOICE REGRESSION HARNESS",
        f"Report: {report_path}",
        f"Branch: {branch_state}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
        "Launcher lane coverage:",
    ]

    for section in launcher_sections:
        lines.append(f"- {section['name']}:")
        lines.append(f"  runtime log: {section['runtime_log'] or 'missing'}")
        lines.append(f"  crash log: {section['crash_log'] or 'missing'}")
        for key, value in section["checks"].items():
            lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")
        if section["stderr"]:
            lines.append("  stderr:")
            lines.append(f"  {section['stderr']}")
        lines.append("")

    lines.append("Direct diagnostics voice probes:")
    for section in probe_sections:
        lines.append(f"- {section['line']}:")
        lines.append(f"  status file: {section['status_file']}")
        for key, value in section["checks"].items():
            lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")
        if section["stderr"]:
            lines.append("  stderr:")
            lines.append(f"  {section['stderr']}")
        lines.append("")

    lines.append("Normal voice direct probe:")
    for key, value in normal_section["checks"].items():
        lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

    return "\n".join(lines) + "\n"


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "unavailable"


def main(argv):
    open_report = "--open-report" in argv

    ensure_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    branch_state = detect_branch_state()

    repeated_crash_root = os.path.join(BASE_LOG_ROOT, "repeated_crash")
    startup_abort_root = os.path.join(BASE_LOG_ROOT, "startup_abort")
    direct_probe_root = os.path.join(BASE_LOG_ROOT, "direct_error_voice")
    normal_probe_root = os.path.join(BASE_LOG_ROOT, "normal_voice")

    repeated_crash = run_launcher_lane(
        name="Repeated-Crash Failure Lane",
        target_script=FAILURE_TARGET,
        log_root=repeated_crash_root,
        expected_lane_markers=[
            "CONSECUTIVE_IDENTICAL_CRASH_THRESHOLD_REACHED",
            "VOICE: Uhm..... Sir, I seem to be malfunctioning.",
            "VOICE: Recovery failed.",
            "VOICE: Shutting down.",
        ],
    )

    startup_abort = run_launcher_lane(
        name="Startup-Abort Lane",
        target_script=STARTUP_ABORT_TARGET,
        log_root=startup_abort_root,
        expected_lane_markers=[
            "STARTUP_READY_STALL_CONFIRMED",
            "STARTUP_ABORT_REQUESTED_ON_CONFIRMED_STALL",
            "RENDERER_MAIN|STARTUP_ABORTED",
            "STARTUP_ABORT_COMPLETE",
            "CONSECUTIVE_STARTUP_ABORT_THRESHOLD_REACHED",
        ],
    )

    probe_sections = []
    for line_text in EXPECTED_DIAGNOSTICS_LINES:
        slug = (
            line_text.lower()
            .replace(" ", "_")
            .replace(".", "")
            .replace(",", "")
            .replace("!", "")
            .replace("?", "")
        )
        probe_sections.append(
            run_error_voice_probe(
                line_text=line_text,
                probe_root=os.path.join(direct_probe_root, slug),
            )
        )

    normal_section = run_normal_voice_probe(normal_probe_root)

    launcher_sections = [repeated_crash, startup_abort]
    failures = []

    for section in launcher_sections:
        failures.extend(collect_failures(section))
    for section in probe_sections:
        failures.extend(collect_failures(section))
    failures.extend(collect_failures(normal_section))

    overall_ok = not failures
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"VoiceRegressionReport_{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"VoiceRegressionReport_{stamp}.json")

    report_text = build_report_text(
        branch_state=branch_state,
        report_path=report_path,
        launcher_sections=launcher_sections,
        probe_sections=probe_sections,
        normal_section=normal_section,
        overall_ok=overall_ok,
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "branch_state": branch_state,
                "overall_ok": overall_ok,
                "launcher_sections": launcher_sections,
                "probe_sections": probe_sections,
                "normal_section": normal_section,
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
