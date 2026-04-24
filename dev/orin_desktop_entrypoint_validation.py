import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "desktop_entrypoint_validation")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")

ENTRYPOINT_SCRIPT = os.path.join(ROOT_DIR, "launch_orin_desktop.vbs")
LAUNCHER_SCRIPT = os.path.join(ROOT_DIR, "desktop", "orin_desktop_launcher.pyw")
DEFAULT_TARGET_SCRIPT = os.path.join(ROOT_DIR, "desktop", "orin_desktop_main.py")
EXPECTED_DEFAULT_TARGET_LINE = re.compile(
    r'DEFAULT_TARGET_SCRIPT\s*=\s*os\.path\.join\(ROOT_DIR,\s*"desktop",\s*"orin_desktop_main\.py"\)'
)
EXPECTED_ENTRYPOINT_FALLBACK_MARKERS = (
    "Function ResolvePythonLaunchCommand()",
    'CommandExists("pyw.exe")',
    'CommandExists("pythonw.exe")',
    "NEXUS_DESKTOP_SKIP_PREFERRED_PYTHONW",
    "windowed Python launcher was not found",
)

EXPECTED_MILESTONES = [
    "RENDERER_MAIN|START",
    "RENDERER_MAIN|QAPPLICATION_CREATED",
    "RENDERER_MAIN|VISUAL_HTML_RESOLVED",
    "RENDERER_MAIN|WINDOW_CONSTRUCTED",
    "RENDERER_MAIN|SHUTDOWN_BUS_READY",
    "RENDERER_MAIN|TRAY_ENTRY_INITIALIZE_REQUESTED",
    "RENDERER_MAIN|TRAY_ENTRY_READY",
    "RENDERER_MAIN|HOTKEYS_STARTED",
    "RENDERER_MAIN|WINDOW_SHOW_DEFERRED_UNTIL_CORE_READY",
    "RENDERER_MAIN|CORE_VISUALIZATION_READY",
    "RENDERER_MAIN|WINDOW_SHOW_REQUESTED",
    "RENDERER_MAIN|CORE_VISUALIZATION_FIRST_VISIBLE",
    "RENDERER_MAIN|STARTUP_READY",
]

EXPECTED_LAUNCH_CHAIN_MARKERS = [
    "STATUS|START|LAUNCHER_RUNTIME",
    "STATUS|SUCCESS|RENDERER_PROCESS_SPAWN",
    "STATUS|SUCCESS|LAUNCHER_RUNTIME|STARTUP_READY_OBSERVED",
    "RENDERER_MAIN|START",
    "RENDERER_MAIN|WINDOW_SHOW_REQUESTED",
    "RENDERER_MAIN|STARTUP_READY",
    "RENDERER_MAIN|SHUTDOWN_REQUESTED",
    "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0",
]


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


def read_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.rstrip("\r\n") for line in f]


def line_status(ok, detail):
    return {"ok": bool(ok), "detail": detail}


def first_marker_index(lines, marker):
    for index, line in enumerate(lines):
        if marker in line:
            return index
    return -1


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


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "unavailable"


def launcher_default_target_line():
    for line in read_lines(LAUNCHER_SCRIPT):
        if line.strip().startswith("DEFAULT_TARGET_SCRIPT"):
            return line.strip()
    return "missing DEFAULT_TARGET_SCRIPT line"


def send_shutdown_hotkey():
    try:
        from pynput.keyboard import Controller, Key
    except Exception as exc:
        return False, f"hotkey import failed: {exc}"

    try:
        keyboard = Controller()
        with keyboard.pressed(Key.ctrl):
            with keyboard.pressed(Key.alt):
                keyboard.press(Key.end)
                keyboard.release(Key.end)
        return True, "Ctrl+Alt+End"
    except Exception as exc:
        return False, f"hotkey send failed: {exc}"


def run_hidden_command(args, env=None, timeout_seconds=20):
    return subprocess.run(
        args,
        cwd=ROOT_DIR,
        env=env,
        timeout=timeout_seconds,
        **hidden_subprocess_kwargs(),
    )


def terminate_process_tree(proc):
    if proc.poll() is not None:
        return False

    if os.name == "nt":
        try:
            run_hidden_command(["taskkill", "/PID", str(proc.pid), "/T", "/F"], timeout_seconds=10)
        except Exception:
            pass

        deadline = time.time() + 5.0
        while time.time() < deadline:
            if proc.poll() is not None:
                return True
            time.sleep(0.1)

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    return True


def list_launch_chain_processes_for_log_root(base_log_root):
    if os.name != "nt":
        return []

    script = r"""
$BaseLogRoot = $args[0]
Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -eq 'pythonw.exe' -or $_.Name -eq 'python.exe' -or $_.Name -eq 'pyw.exe') -and
    ($_.CommandLine -like '*orin_desktop_main.py*' -or $_.CommandLine -like '*orin_desktop_launcher.pyw*') -and
    $_.CommandLine -like ('*' + $BaseLogRoot + '*')
} | ForEach-Object {
    '{0}|{1}' -f $_.ProcessId, $_.CommandLine
}
"""

    try:
        result = run_hidden_command(
            ["powershell", "-NoProfile", "-Command", script, base_log_root],
            timeout_seconds=15,
        )
    except Exception:
        return []

    processes = []
    for raw_line in (result.stdout or "").splitlines():
        line = raw_line.strip()
        if not line or "|" not in line:
            continue
        pid_text, command_line = line.split("|", 1)
        try:
            pid = int(pid_text.strip())
        except ValueError:
            continue
        processes.append({"pid": pid, "command_line": command_line.strip()})
    return processes


def cleanup_launch_chain_processes_for_log_root(base_log_root):
    before = list_launch_chain_processes_for_log_root(base_log_root)
    killed = []

    for process in before:
        try:
            run_hidden_command(["taskkill", "/PID", str(process["pid"]), "/F"], timeout_seconds=10)
            killed.append(process["pid"])
        except Exception:
            pass

    time.sleep(0.3)
    after = list_launch_chain_processes_for_log_root(base_log_root)
    return before, killed, after


def entrypoint_shim_line():
    for line in read_lines(ENTRYPOINT_SCRIPT):
        if line.strip().startswith("LauncherPath"):
            return line.strip()
    return "missing LauncherPath line"


def validate_tray_overlay_route():
    previous_qt_platform = os.environ.get("QT_QPA_PLATFORM")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    try:
        if ROOT_DIR not in sys.path:
            sys.path.insert(0, ROOT_DIR)

        from PySide6.QtWidgets import QApplication

        from desktop.orin_desktop_main import DesktopTrayEntry

        app = QApplication.instance()
        created_app = False
        if app is None:
            app = QApplication(["orin_desktop_entrypoint_validation"])
            created_app = True

        events = []

        class FakeWindow:
            def __init__(self):
                self.toggle_count = 0
                self.create_custom_task_sources = []

            def toggle_command_overlay(self):
                self.toggle_count += 1

            def request_create_custom_task_from_tray(self, source=""):
                self.create_custom_task_sources.append(source)

        fake_window = FakeWindow()
        tray_entry = DesktopTrayEntry(app, fake_window, events.append)
        tray_entry.request_overlay_from_tray("validation")
        tray_entry.request_create_custom_task_from_tray("validation")

        if created_app:
            app.quit()

        return {
            "ok": True,
            "events": events,
            "toggle_count": fake_window.toggle_count,
            "create_custom_task_sources": fake_window.create_custom_task_sources,
            "error": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "events": [],
            "toggle_count": 0,
            "create_custom_task_sources": [],
            "error": f"{type(exc).__name__}: {exc}",
        }
    finally:
        if previous_qt_platform is None:
            os.environ.pop("QT_QPA_PLATFORM", None)
        else:
            os.environ["QT_QPA_PLATFORM"] = previous_qt_platform


def validate_tray_initialization_failure_is_bounded():
    previous_qt_platform = os.environ.get("QT_QPA_PLATFORM")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    try:
        if ROOT_DIR not in sys.path:
            sys.path.insert(0, ROOT_DIR)

        from PySide6.QtWidgets import QApplication

        import desktop.orin_desktop_main as runtime_mod

        app = QApplication.instance()
        created_app = False
        if app is None:
            app = QApplication(["orin_desktop_entrypoint_validation"])
            created_app = True

        events = []

        class FakeWindow:
            def toggle_command_overlay(self):
                raise AssertionError("initialize should not route overlay")

        class FailingTrayIcon:
            class ActivationReason:
                Trigger = object()
                DoubleClick = object()

            @staticmethod
            def isSystemTrayAvailable():
                return True

            def __init__(self, *_args, **_kwargs):
                raise RuntimeError("synthetic tray init failure")

        original_tray_icon = runtime_mod.QSystemTrayIcon
        runtime_mod.QSystemTrayIcon = FailingTrayIcon
        try:
            tray_entry = runtime_mod.DesktopTrayEntry(app, FakeWindow(), events.append)
            initialized = tray_entry.initialize()
        finally:
            runtime_mod.QSystemTrayIcon = original_tray_icon

        if created_app:
            app.quit()

        return {
            "ok": True,
            "initialized": initialized,
            "events": events,
            "error": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "initialized": True,
            "events": [],
            "error": f"{type(exc).__name__}: {exc}",
        }
    finally:
        if previous_qt_platform is None:
            os.environ.pop("QT_QPA_PLATFORM", None)
        else:
            os.environ["QT_QPA_PLATFORM"] = previous_qt_platform


def validate_tray_identity_initialization():
    previous_qt_platform = os.environ.get("QT_QPA_PLATFORM")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    try:
        if ROOT_DIR not in sys.path:
            sys.path.insert(0, ROOT_DIR)

        from PySide6.QtWidgets import QApplication

        import desktop.orin_desktop_main as runtime_mod

        app = QApplication.instance()
        created_app = False
        if app is None:
            app = QApplication(["orin_desktop_entrypoint_validation"])
            created_app = True

        events = []

        class FakeWindow:
            def toggle_command_overlay(self):
                raise AssertionError("initialize should not route overlay")

            def request_create_custom_task_from_tray(self, source=""):
                raise AssertionError("initialize should not route authoring")

        class FakeSignal:
            def __init__(self):
                self.callback = None

            def connect(self, callback):
                self.callback = callback

        class FakeTrayIcon:
            latest_instance = None

            class ActivationReason:
                Trigger = object()
                DoubleClick = object()

            class MessageIcon:
                Information = "information"

            @staticmethod
            def isSystemTrayAvailable():
                return True

            @staticmethod
            def supportsMessages():
                return True

            def __init__(self, *_args, **_kwargs):
                self.activated = FakeSignal()
                self.tooltip = ""
                self.context_menu = None
                self.shown = False
                self.hidden = False
                self.messages = []
                FakeTrayIcon.latest_instance = self

            def setToolTip(self, tooltip):
                self.tooltip = tooltip

            def setContextMenu(self, menu):
                self.context_menu = menu

            def show(self):
                self.shown = True

            def hide(self):
                self.hidden = True

            def showMessage(self, title, message, icon, duration_ms):
                self.messages.append(
                    {
                        "title": title,
                        "message": message,
                        "icon": icon,
                        "duration_ms": duration_ms,
                    }
                )

        original_tray_icon = runtime_mod.QSystemTrayIcon
        runtime_mod.QSystemTrayIcon = FakeTrayIcon
        try:
            tray_entry = runtime_mod.DesktopTrayEntry(app, FakeWindow(), events.append)
            initialized = tray_entry.initialize()
            discovery_cue_requested = tray_entry.show_discovery_cue()
            actions = [
                action
                for action in tray_entry.tray_menu.actions()
                if not action.isSeparator()
            ]
            action_texts = [action.text() for action in actions]
            identity_action_enabled = actions[0].isEnabled() if actions else None
            fake_icon = FakeTrayIcon.latest_instance
            tooltip = fake_icon.tooltip if fake_icon is not None else ""
            messages = fake_icon.messages if fake_icon is not None else []
        finally:
            runtime_mod.QSystemTrayIcon = original_tray_icon

        tray_entry.close()

        if created_app:
            app.quit()

        return {
            "ok": True,
            "initialized": initialized,
            "events": events,
            "action_texts": action_texts,
            "identity_action_enabled": identity_action_enabled,
            "tooltip": tooltip,
            "discovery_cue_requested": discovery_cue_requested,
            "messages": messages,
            "error": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "initialized": False,
            "events": [],
            "action_texts": [],
            "identity_action_enabled": None,
            "tooltip": "",
            "discovery_cue_requested": False,
            "messages": [],
            "error": f"{type(exc).__name__}: {exc}",
        }
    finally:
        if previous_qt_platform is None:
            os.environ.pop("QT_QPA_PLATFORM", None)
        else:
            os.environ["QT_QPA_PLATFORM"] = previous_qt_platform


def run_entrypoint_launch_scenario(scenario_name, force_path_fallback=False):
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    reset_dir(scenario_root)
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = scenario_root
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"

    if force_path_fallback:
        env["NEXUS_DESKTOP_SKIP_PREFERRED_PYTHONW"] = "1"

    shim_result = run_hidden_command(
        ["cscript.exe", "//nologo", ENTRYPOINT_SCRIPT],
        env=env,
        timeout_seconds=10,
    )

    runtime_log = ""
    runtime_lines = []
    ready_seen = False
    shutdown_requested_seen = False
    renderer_exit_seen = False
    launcher_ready_observed_seen = False
    hotkey_sent = False
    hotkey_detail = "hotkey not sent"
    hotkey_attempts = 0
    normal_exit_complete_seen = False
    failure_flow_seen = False

    ready_deadline = time.time() + 25.0
    while time.time() < ready_deadline:
        runtime_log = latest_file_matching(scenario_root, "Runtime_")
        runtime_lines = read_lines(runtime_log)
        if any("RENDERER_MAIN|STARTUP_READY" in line for line in runtime_lines):
            ready_seen = True
            break
        time.sleep(0.2)

    if ready_seen:
        hotkey_attempts += 1
        hotkey_sent, hotkey_detail = send_shutdown_hotkey()

    post_ready_deadline = time.time() + 20.0
    while time.time() < post_ready_deadline:
        runtime_log = latest_file_matching(scenario_root, "Runtime_")
        runtime_lines = read_lines(runtime_log)
        shutdown_requested_seen = any("RENDERER_MAIN|SHUTDOWN_REQUESTED" in line for line in runtime_lines)
        renderer_exit_seen = any("RENDERER_MAIN|EVENT_LOOP_EXIT|code=0" in line for line in runtime_lines)
        launcher_ready_observed_seen = any(
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|STARTUP_READY_OBSERVED" in line
            for line in runtime_lines
        )
        normal_exit_complete_seen = any(
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE" in line for line in runtime_lines
        )
        failure_flow_seen = any(
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in runtime_lines
        )

        if shutdown_requested_seen and renderer_exit_seen and launcher_ready_observed_seen:
            break

        if ready_seen and not shutdown_requested_seen and hotkey_sent and hotkey_attempts < 2:
            hotkey_attempts += 1
            hotkey_sent, hotkey_detail = send_shutdown_hotkey()

        time.sleep(0.2)

    residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    checks = {
        "shim_invocation_ok": line_status(
            shim_result.returncode == 0,
            f"returncode={shim_result.returncode}",
        ),
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "renderer_target_matches_default": line_status(
            any(f"Renderer target: {DEFAULT_TARGET_SCRIPT}" in line for line in runtime_lines),
            DEFAULT_TARGET_SCRIPT,
        ),
        "launcher_owned_startup_ready_observed": line_status(
            launcher_ready_observed_seen,
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|STARTUP_READY_OBSERVED",
        ),
        "renderer_startup_ready_reached": line_status(
            ready_seen,
            "RENDERER_MAIN|STARTUP_READY",
        ),
        "shutdown_hotkey_sent": line_status(
            hotkey_sent,
            hotkey_detail,
        ),
        "clean_shutdown_markers_captured": line_status(
            shutdown_requested_seen and renderer_exit_seen,
            "RENDERER_MAIN|SHUTDOWN_REQUESTED + RENDERER_MAIN|EVENT_LOOP_EXIT|code=0",
        ),
        "launcher_normal_exit_complete_optional": line_status(
            True,
            "seen" if normal_exit_complete_seen else "not seen before validator cleanup",
        ),
        "traceback_absent": line_status(
            "Traceback" not in shim_result.stdout and "Traceback" not in shim_result.stderr,
            (shim_result.stderr or shim_result.stdout).strip() or "no traceback in shim output",
        ),
        "failure_flow_absent": line_status(
            not failure_flow_seen,
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "no_residual_launch_chain_processes_for_log_root": line_status(
            not residual_launch_chain_processes_after,
            "none"
            if not residual_launch_chain_processes_after
            else "; ".join(
                f"{process['pid']}::{process['command_line']}" for process in residual_launch_chain_processes_after
            ),
        ),
        "launch_chain_cleanup_optional": line_status(
            True,
            "no residual validation-owned launcher/runtime processes detected"
            if not residual_launch_chain_processes_before
            else (
                f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
            ),
        ),
        "scenario_preflight_cleanup_optional": line_status(
            not preexisting_processes_after,
            "no prior validation-owned launcher/runtime processes detected"
            if not preexisting_processes_before
            else (
                f"detected {len(preexisting_processes_before)} prior process(es); "
                f"killed={','.join(str(pid) for pid in preexisting_processes_killed) or 'none'}"
            ),
        ),
    }

    for marker in EXPECTED_LAUNCH_CHAIN_MARKERS:
        checks[f"marker::{marker}"] = line_status(
            any(marker in line for line in runtime_lines),
            marker,
        )

    return {
        "scenario_name": scenario_name,
        "log_root": scenario_root,
        "runtime_log": runtime_log,
        "stdout": (shim_result.stdout or "").strip(),
        "stderr": (shim_result.stderr or "").strip(),
        "checks": checks,
    }


def run_validation():
    ensure_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    entrypoint_text = read_text(ENTRYPOINT_SCRIPT)
    entrypoint_line = entrypoint_shim_line()
    launcher_text = read_text(LAUNCHER_SCRIPT)
    launcher_line = launcher_default_target_line()

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    runtime_log = os.path.join(BASE_LOG_ROOT, f"Runtime_{stamp}.txt")

    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"

    proc = subprocess.Popen(
        [
            sys.executable,
            DEFAULT_TARGET_SCRIPT,
            "--runtime-log",
            runtime_log,
        ],
        cwd=ROOT_DIR,
        env=env,
        **hidden_subprocess_kwargs(),
    )

    ready_seen = False
    deadline = time.time() + 20.0
    runtime_lines = []

    try:
        while time.time() < deadline:
            if os.path.exists(runtime_log):
                runtime_lines = read_lines(runtime_log)
                if any("RENDERER_MAIN|STARTUP_READY" in line for line in runtime_lines):
                    ready_seen = True
                    break

            if proc.poll() is not None:
                break

            time.sleep(0.25)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    stdout_text, stderr_text = proc.communicate()
    runtime_lines = read_lines(runtime_log)

    checks = {
        "launcher_default_target_matches_expected": line_status(
            bool(EXPECTED_DEFAULT_TARGET_LINE.search(launcher_text)),
            launcher_line,
        ),
        "default_target_exists": line_status(
            os.path.exists(DEFAULT_TARGET_SCRIPT),
            DEFAULT_TARGET_SCRIPT,
        ),
        "runtime_log_created": line_status(
            os.path.exists(runtime_log),
            runtime_log,
        ),
    }

    for milestone in EXPECTED_MILESTONES:
        checks[f"milestone::{milestone}"] = line_status(
            any(milestone in line for line in runtime_lines),
            milestone,
        )

    deferred_index = first_marker_index(
        runtime_lines,
        "RENDERER_MAIN|WINDOW_SHOW_DEFERRED_UNTIL_CORE_READY",
    )
    core_ready_index = first_marker_index(
        runtime_lines,
        "RENDERER_MAIN|CORE_VISUALIZATION_READY",
    )
    show_index = first_marker_index(
        runtime_lines,
        "RENDERER_MAIN|WINDOW_SHOW_REQUESTED",
    )
    first_visible_index = first_marker_index(
        runtime_lines,
        "RENDERER_MAIN|CORE_VISUALIZATION_FIRST_VISIBLE",
    )
    startup_ready_index = first_marker_index(
        runtime_lines,
        "RENDERER_MAIN|STARTUP_READY",
    )
    ordering_detail = (
        f"deferred={deferred_index}, core_ready={core_ready_index}, "
        f"show={show_index}, first_visible={first_visible_index}, "
        f"startup_ready={startup_ready_index}"
    )
    checks["window_show_deferred_before_core_ready"] = line_status(
        deferred_index >= 0 and core_ready_index > deferred_index,
        ordering_detail,
    )
    checks["window_show_after_core_visualization_ready"] = line_status(
        show_index > core_ready_index >= 0,
        ordering_detail,
    )
    checks["core_visualization_visible_before_startup_ready"] = line_status(
        startup_ready_index > first_visible_index > show_index,
        ordering_detail,
    )

    checks["startup_ready_reached_before_termination"] = line_status(
        ready_seen,
        "RENDERER_MAIN|STARTUP_READY",
    )
    checks["traceback_absent"] = line_status(
        "Traceback" not in stderr_text,
        stderr_text.strip() or "no traceback in stderr",
    )

    tray_route_result = validate_tray_overlay_route()
    tray_events = tray_route_result["events"]
    checks["tray_route_validation_imported"] = line_status(
        tray_route_result["ok"],
        tray_route_result["error"] or "DesktopTrayEntry imported and exercised",
    )
    checks["tray_route_toggle_overlay_called"] = line_status(
        tray_route_result["toggle_count"] == 1,
        f"toggle_count={tray_route_result['toggle_count']}",
    )
    checks["tray_route_requested_marker"] = line_status(
        any(
            "RENDERER_MAIN|TRAY_ACTIVATION_REQUESTED|source=validation" in event
            for event in tray_events
        ),
        "TRAY_ACTIVATION_REQUESTED",
    )
    checks["tray_route_routed_marker"] = line_status(
        any(
            "RENDERER_MAIN|TRAY_ACTIVATION_ROUTED_TO_OVERLAY|source=validation" in event
            for event in tray_events
        ),
        "TRAY_ACTIVATION_ROUTED_TO_OVERLAY",
    )
    checks["tray_create_custom_task_marker"] = line_status(
        any(
            "RENDERER_MAIN|TRAY_CREATE_CUSTOM_TASK_REQUESTED|source=validation" in event
            for event in tray_events
        ),
        "TRAY_CREATE_CUSTOM_TASK_REQUESTED",
    )
    checks["tray_create_custom_task_route"] = line_status(
        tray_route_result["create_custom_task_sources"] == ["validation"],
        f"create_custom_task_sources={tray_route_result['create_custom_task_sources']}",
    )

    tray_identity_result = validate_tray_identity_initialization()
    tray_identity_events = tray_identity_result["events"]
    tray_identity_messages = tray_identity_result["messages"]
    checks["tray_identity_validation_imported"] = line_status(
        tray_identity_result["ok"],
        tray_identity_result["error"] or "DesktopTrayEntry identity path exercised",
    )
    checks["tray_identity_initializes"] = line_status(
        tray_identity_result["initialized"] is True,
        f"initialized={tray_identity_result['initialized']}",
    )
    checks["tray_identity_tooltip"] = line_status(
        tray_identity_result["tooltip"] == "Nexus Desktop AI",
        f"tooltip={tray_identity_result['tooltip']}",
    )
    checks["tray_identity_menu_header"] = line_status(
        tray_identity_result["action_texts"][:3]
        == ["Nexus Desktop AI", "Open Command Overlay", "Create Custom Task"],
        f"action_texts={tray_identity_result['action_texts']}",
    )
    checks["tray_identity_header_disabled"] = line_status(
        tray_identity_result["identity_action_enabled"] is False,
        f"identity_action_enabled={tray_identity_result['identity_action_enabled']}",
    )
    checks["tray_identity_ready_marker"] = line_status(
        any(
            "RENDERER_MAIN|TRAY_IDENTITY_READY|label=Nexus Desktop AI|hidden_overflow_hint=true"
            in event
            for event in tray_identity_events
        ),
        "TRAY_IDENTITY_READY",
    )
    checks["tray_discovery_cue_requested"] = line_status(
        tray_identity_result["discovery_cue_requested"] is True
        and any(
            "RENDERER_MAIN|TRAY_DISCOVERY_CUE_REQUESTED|hidden_overflow_hint=true"
            in event
            for event in tray_identity_events
        ),
        "TRAY_DISCOVERY_CUE_REQUESTED",
    )
    checks["tray_discovery_cue_hidden_overflow_hint"] = line_status(
        bool(tray_identity_messages)
        and "hidden icons" in tray_identity_messages[0]["message"],
        tray_identity_messages[0]["message"] if tray_identity_messages else "no message",
    )

    tray_failure_result = validate_tray_initialization_failure_is_bounded()
    tray_failure_events = tray_failure_result["events"]
    checks["tray_init_failure_validation_imported"] = line_status(
        tray_failure_result["ok"],
        tray_failure_result["error"] or "DesktopTrayEntry init failure path exercised",
    )
    checks["tray_init_failure_returns_false"] = line_status(
        tray_failure_result["initialized"] is False,
        f"initialized={tray_failure_result['initialized']}",
    )
    checks["tray_init_failure_ready_marker"] = line_status(
        any(
            "RENDERER_MAIN|TRAY_ENTRY_READY|available=false|reason=RuntimeError" in event
            for event in tray_failure_events
        ),
        "TRAY_ENTRY_READY failure marker",
    )

    checks["entrypoint_script_exists"] = line_status(
        os.path.exists(ENTRYPOINT_SCRIPT),
        ENTRYPOINT_SCRIPT,
    )
    checks["entrypoint_launcher_path_declared"] = line_status(
        "desktop\\orin_desktop_launcher.pyw" in entrypoint_text,
        entrypoint_line,
    )
    for marker in EXPECTED_ENTRYPOINT_FALLBACK_MARKERS:
        checks[f"entrypoint_fallback_marker::{marker}"] = line_status(
            marker in entrypoint_text,
            marker,
        )

    default_launch_result = run_entrypoint_launch_scenario("vbs_default")
    fallback_launch_result = run_entrypoint_launch_scenario(
        "vbs_fallback",
        force_path_fallback=True,
    )

    for scenario_result in (default_launch_result, fallback_launch_result):
        scenario_name = scenario_result["scenario_name"]
        checks[f"{scenario_name}::runtime_log_recorded"] = line_status(
            bool(scenario_result["runtime_log"]),
            scenario_result["runtime_log"] or "missing runtime log",
        )
        for check_name, check_result in scenario_result["checks"].items():
            checks[f"{scenario_name}::{check_name}"] = check_result

    return {
        "branch_state": detect_branch_state(),
        "entrypoint_script": ENTRYPOINT_SCRIPT,
        "entrypoint_line": entrypoint_line,
        "runtime_log": runtime_log,
        "target_script": DEFAULT_TARGET_SCRIPT,
        "launcher_line": launcher_line,
        "launch_scenarios": [default_launch_result, fallback_launch_result],
        "tray_route_events": tray_events,
        "tray_identity_events": tray_identity_events,
        "tray_identity_actions": tray_identity_result["action_texts"],
        "tray_identity_messages": tray_identity_messages,
        "tray_failure_events": tray_failure_events,
        "stdout": stdout_text.strip(),
        "stderr": stderr_text.strip(),
        "checks": checks,
    }


def build_report_text(report_path, result, overall_ok):
    lines = [
        "JARVIS DESKTOP ENTRYPOINT VALIDATION",
        f"Report: {report_path}",
        f"Branch: {result['branch_state']}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
        f"Entrypoint shim: {result['entrypoint_script']}",
        f"Entrypoint launcher line: {result['entrypoint_line']}",
        f"Default target: {result['target_script']}",
        f"Launcher target line: {result['launcher_line']}",
        f"Runtime log: {result['runtime_log']}",
        "",
        "Checks:",
    ]

    for key, value in result["checks"].items():
        lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

    if result["stdout"]:
        lines.extend(["", "stdout:", result["stdout"]])
    if result["stderr"]:
        lines.extend(["", "stderr:", result["stderr"]])
    if result.get("tray_route_events"):
        lines.extend(["", "Tray route events:"])
        lines.extend(f"  {event}" for event in result["tray_route_events"])
    if result.get("tray_identity_actions"):
        lines.extend(["", "Tray identity menu actions:"])
        lines.extend(f"  {action}" for action in result["tray_identity_actions"])
    if result.get("tray_identity_events"):
        lines.extend(["", "Tray identity events:"])
        lines.extend(f"  {event}" for event in result["tray_identity_events"])
    if result.get("tray_identity_messages"):
        lines.extend(["", "Tray identity discovery messages:"])
        lines.extend(
            f"  {message['title']} :: {message['message']}"
            for message in result["tray_identity_messages"]
        )
    if result.get("tray_failure_events"):
        lines.extend(["", "Tray init failure events:"])
        lines.extend(f"  {event}" for event in result["tray_failure_events"])
    if result.get("launch_scenarios"):
        for scenario_result in result["launch_scenarios"]:
            lines.extend(
                [
                    "",
                    f"Launch scenario: {scenario_result['scenario_name']}",
                    f"  Log root: {scenario_result['log_root']}",
                    f"  Runtime log: {scenario_result['runtime_log'] or 'missing runtime log'}",
                ]
            )
            if scenario_result["stdout"]:
                lines.extend(["  stdout:", f"    {scenario_result['stdout']}"])
            if scenario_result["stderr"]:
                lines.extend(["  stderr:", f"    {scenario_result['stderr']}"])

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    result = run_validation()
    failures = [key for key, value in result["checks"].items() if not value["ok"]]
    overall_ok = not failures

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"DesktopEntrypointValidationReport_{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"DesktopEntrypointValidationReport_{stamp}.json")

    report_text = build_report_text(report_path, result, overall_ok)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "overall_ok": overall_ok,
                "result": result,
                "report_path": report_path,
                "failures": failures,
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
