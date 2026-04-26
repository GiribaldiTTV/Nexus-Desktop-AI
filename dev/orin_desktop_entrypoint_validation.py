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
MAIN_SCRIPT = os.path.join(ROOT_DIR, "main.py")
EXPECTED_DEFAULT_TARGET_LINE = re.compile(
    r'DEFAULT_TARGET_SCRIPT\s*=\s*os\.path\.join\(ROOT_DIR,\s*"desktop",\s*"orin_desktop_main\.py"\)'
)
EXPECTED_ENTRYPOINT_FALLBACK_MARKERS = (
    "Function ResolvePythonLaunchCommand()",
    "Function PyLauncherSupportsPython3()",
    'CommandExists("pyw.exe")',
    'CommandExists("pythonw.exe")',
    "py -0p",
    "NEXUS_DESKTOP_SKIP_PREFERRED_PYTHONW",
    "windowed Python launcher was not found",
)
EXPECTED_MAIN_HANDOFF_MARKERS = (
    'CANONICAL_ENTRYPOINT_SCRIPT = os.path.join(ROOT_DIR, "launch_orin_desktop.vbs")',
    'DESKTOP_ENTRYPOINT_ARGS = {"--desktop-entrypoint"}',
    "def classify_direct_launch_mode(argv):",
    "def handoff_to_canonical_desktop_entrypoint():",
    "\\\\dev\\\\launchers\\\\launch_orin_main_",
)
MAIN_EXPLICIT_DESKTOP_ARG = "--desktop-entrypoint"
MAIN_INVALID_DIRECT_ARG = "--not-a-real-entrypoint-flag"
EXPECTED_MAIN_INVALID_ARG_MARKERS = (
    "Unrecognized direct-launch argument:",
    "--desktop-entrypoint",
    "--boot-profile/--audio-mode",
)
BOOT_RUNTIME_ROOTS = (
    os.path.join(ROOT_DIR, "dev", "logs", "boot_manual_flow"),
    os.path.join(ROOT_DIR, "dev", "logs", "boot_auto_handoff_skip_import"),
)
AUTHORITATIVE_DESKTOP_SETTLED_MARKER = "DESKTOP_OUTCOME|SETTLED|state=dormant"
LAUNCHER_SETTLED_OBSERVED_MARKER = (
    "STATUS|SUCCESS|LAUNCHER_RUNTIME|DESKTOP_SETTLED_OBSERVED|state=dormant"
)
POST_SETTLED_RUNTIME_EXIT_MARKER = "POST_SETTLED_RUNTIME_EXIT"
POST_SETTLED_RECOVERABLE_COMPLETE_MARKER = (
    "STATUS|SUCCESS|LAUNCHER_RUNTIME|POST_SETTLED_RECOVERABLE_COMPLETE"
)
RELAUNCH_REPLACEMENT_SESSION_ACTIVE_MARKER = (
    "STATUS|TRACE|LAUNCHER_RUNTIME|RELAUNCH_REPLACEMENT_SESSION_ACTIVE"
)
RELAUNCH_REPLACEMENT_SESSION_SETTLED_MARKER = (
    "STATUS|SUCCESS|LAUNCHER_RUNTIME|RELAUNCH_REPLACEMENT_SESSION_SETTLED|state=dormant"
)
SINGLE_INSTANCE_RELEASED_MARKER = "STATUS|TRACE|LAUNCHER_RUNTIME|SINGLE_INSTANCE_RELEASED"

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
    "RENDERER_MAIN|PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant",
    AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
]

EXPECTED_LAUNCH_CHAIN_MARKERS = [
    "STATUS|START|LAUNCHER_RUNTIME",
    "STATUS|SUCCESS|RENDERER_PROCESS_SPAWN",
    LAUNCHER_SETTLED_OBSERVED_MARKER,
    "RENDERER_MAIN|START",
    "RENDERER_MAIN|WINDOW_SHOW_REQUESTED",
    "RENDERER_MAIN|STARTUP_READY",
    AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
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


def files_matching_sorted(folder_path, prefix):
    if not os.path.isdir(folder_path):
        return []

    matches = []
    for name in os.listdir(folder_path):
        if not name.lower().startswith(prefix.lower()):
            continue
        path = os.path.join(folder_path, name)
        if not os.path.isfile(path):
            continue
        matches.append((name.lower(), path))

    matches.sort(key=lambda item: item[0])
    return [path for _name, path in matches]


def dir_entry_names(path):
    if not os.path.isdir(path):
        return []
    try:
        return sorted(os.listdir(path))
    except OSError:
        return []


def boot_runtime_files():
    runtime_files = set()
    for folder_path in BOOT_RUNTIME_ROOTS:
        if not os.path.isdir(folder_path):
            continue
        try:
            names = os.listdir(folder_path)
        except OSError:
            continue
        for name in names:
            if name.lower().startswith("runtime_") and name.lower().endswith(".txt"):
                runtime_files.add(os.path.join(folder_path, name))
    return runtime_files


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


def wait_for_no_launch_chain_processes_for_log_root(base_log_root, timeout_seconds=5.0):
    deadline = time.time() + timeout_seconds
    last_seen = []

    while time.time() < deadline:
        last_seen = list_launch_chain_processes_for_log_root(base_log_root)
        if not last_seen:
            return True, []
        time.sleep(0.2)

    last_seen = list_launch_chain_processes_for_log_root(base_log_root)
    return not last_seen, last_seen


def entrypoint_shim_line():
    for line in read_lines(ENTRYPOINT_SCRIPT):
        if line.strip().startswith("LauncherPath"):
            return line.strip()
    return "missing LauncherPath line"


def resolve_cscript_command():
    if os.name != "nt":
        return []

    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    preferred = os.path.join(system_root, "System32", "cscript.exe")
    if os.path.isfile(preferred):
        return [preferred]

    for candidate in ("cscript.exe", "cscript"):
        resolved = shutil.which(candidate)
        if resolved:
            return [resolved]

    return []


def build_harness_env(scenario_root, target_script="", extra_env=None):
    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = scenario_root
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"
    if target_script:
        env["JARVIS_HARNESS_TARGET_SCRIPT"] = target_script
    if extra_env:
        env.update(extra_env)
    return env


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


def run_launch_chain_scenario(
    scenario_name,
    launch_command,
    force_path_fallback=False,
    preflight_cleanup=True,
    postflight_cleanup=True,
):
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    if preflight_cleanup:
        preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
            cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
        )
    else:
        preexisting_processes_before = list_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
        preexisting_processes_killed = []
        preexisting_processes_after = list(preexisting_processes_before)
    reset_dir(scenario_root)
    scenario_root_entries_after_reset = dir_entry_names(scenario_root)

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = scenario_root
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"

    if force_path_fallback:
        env["NEXUS_DESKTOP_SKIP_PREFERRED_PYTHONW"] = "1"

    launch_attempted = False
    if scenario_root_entries_after_reset:
        shim_result = subprocess.CompletedProcess(
            launch_command or ["missing-launch-command"],
            1,
            "",
            "scenario log root not empty after reset: "
            + ", ".join(scenario_root_entries_after_reset[:5]),
        )
    elif not launch_command:
        shim_result = subprocess.CompletedProcess(
            ["missing-launch-command"],
            1,
            "",
            "launch command unavailable",
        )
    else:
        launch_attempted = True
        shim_result = run_hidden_command(
            launch_command,
            env=env,
            timeout_seconds=10,
        )

    runtime_log = ""
    runtime_lines = []
    settled_seen = False
    shutdown_requested_seen = False
    renderer_exit_seen = False
    launcher_settled_observed_seen = False
    hotkey_sent = False
    hotkey_detail = "hotkey not sent"
    hotkey_attempts = 0
    normal_exit_complete_seen = False
    failure_flow_seen = False
    post_settled_recoverable_seen = False

    if launch_attempted:
        ready_deadline = time.time() + 25.0
        while time.time() < ready_deadline:
            runtime_log = latest_file_matching(scenario_root, "Runtime_")
            runtime_lines = read_lines(runtime_log)
            if any(AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines):
                settled_seen = True
                break
            time.sleep(0.2)

        if settled_seen:
            hotkey_attempts += 1
            hotkey_sent, hotkey_detail = send_shutdown_hotkey()

        post_ready_deadline = time.time() + 20.0
        while time.time() < post_ready_deadline:
            runtime_log = latest_file_matching(scenario_root, "Runtime_")
            runtime_lines = read_lines(runtime_log)
            shutdown_requested_seen = any("RENDERER_MAIN|SHUTDOWN_REQUESTED" in line for line in runtime_lines)
            renderer_exit_seen = any("RENDERER_MAIN|EVENT_LOOP_EXIT|code=0" in line for line in runtime_lines)
            launcher_settled_observed_seen = any(
                LAUNCHER_SETTLED_OBSERVED_MARKER in line
                for line in runtime_lines
            )
            normal_exit_complete_seen = any(
                "STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE" in line for line in runtime_lines
            )
            post_settled_recoverable_seen = any(
                POST_SETTLED_RECOVERABLE_COMPLETE_MARKER in line for line in runtime_lines
            )
            failure_flow_seen = any(
                "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in runtime_lines
            )

            if (
                shutdown_requested_seen
                and renderer_exit_seen
                and launcher_settled_observed_seen
            ) or post_settled_recoverable_seen:
                break

            if settled_seen and not shutdown_requested_seen and hotkey_sent and hotkey_attempts < 2:
                hotkey_attempts += 1
                hotkey_sent, hotkey_detail = send_shutdown_hotkey()

            time.sleep(0.2)

    if postflight_cleanup:
        residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
            cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
        )
    else:
        residual_launch_chain_processes_before = list_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
        residual_launch_chain_killed = []
        residual_launch_chain_processes_after = list(residual_launch_chain_processes_before)

    checks = {
        "launch_invocation_ok": line_status(
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
        "launcher_authoritative_settled_observed": line_status(
            launcher_settled_observed_seen,
            LAUNCHER_SETTLED_OBSERVED_MARKER,
        ),
        "authoritative_desktop_settled_reached": line_status(
            settled_seen,
            AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
        ),
        "shutdown_hotkey_sent": line_status(
            hotkey_sent,
            hotkey_detail,
        ),
        "completion_path_classified": line_status(
            (shutdown_requested_seen and renderer_exit_seen) or post_settled_recoverable_seen,
            "clean shutdown markers or POST_SETTLED_RECOVERABLE_COMPLETE",
        ),
        "clean_shutdown_markers_optional": line_status(
            True,
            "seen"
            if shutdown_requested_seen and renderer_exit_seen
            else "not seen before validator cleanup",
        ),
        "post_settled_recoverable_complete_optional": line_status(
            True,
            "seen" if post_settled_recoverable_seen else "not seen",
        ),
        "post_settled_runtime_exit_marker_optional": line_status(
            True,
            "seen"
            if any(POST_SETTLED_RUNTIME_EXIT_MARKER in line for line in runtime_lines)
            else "not seen",
        ),
        "launcher_normal_exit_complete_optional": line_status(
            True,
            "seen" if normal_exit_complete_seen else "not seen before validator cleanup",
        ),
        "traceback_absent": line_status(
            "Traceback" not in shim_result.stdout and "Traceback" not in shim_result.stderr,
            (shim_result.stderr or shim_result.stdout).strip() or "no traceback in shim output",
        ),
        "scenario_log_root_cleared_before_launch": line_status(
            not scenario_root_entries_after_reset,
            "empty" if not scenario_root_entries_after_reset else ", ".join(scenario_root_entries_after_reset[:5]),
        ),
        "failure_flow_absent": line_status(
            not failure_flow_seen,
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "boot_markers_absent": line_status(
            not any("BOOT_MAIN|" in line for line in runtime_lines),
            "BOOT_MAIN| absent from launcher/runtime log",
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
            "skipped to preserve active-session state for follow-up launch"
            if not postflight_cleanup
            else (
                "no residual validation-owned launcher/runtime processes detected"
                if not residual_launch_chain_processes_before
                else (
                    f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                    f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
                )
            ),
        ),
        "scenario_preflight_cleanup_optional": line_status(
            not preexisting_processes_after if preflight_cleanup else True,
            "skipped to preserve prior launch state"
            if not preflight_cleanup
            else (
                "no prior validation-owned launcher/runtime processes detected"
                if not preexisting_processes_before
                else (
                    f"detected {len(preexisting_processes_before)} prior process(es); "
                    f"killed={','.join(str(pid) for pid in preexisting_processes_killed) or 'none'}"
                )
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
        "runtime_lines": runtime_lines,
        "stdout": (shim_result.stdout or "").strip(),
        "stderr": (shim_result.stderr or "").strip(),
        "checks": checks,
    }


def scenario_has_single_instance_conflict(scenario_result):
    return any(
        "SINGLE_INSTANCE_CONFLICT_DETECTED" in line
        for line in scenario_result.get("runtime_lines", [])
    )


def launch_scenario_core_ok(scenario_result):
    core_check_names = (
        "launch_invocation_ok",
        "runtime_log_created",
        "launcher_authoritative_settled_observed",
        "authoritative_desktop_settled_reached",
        "completion_path_classified",
        "failure_flow_absent",
    )
    checks = scenario_result.get("checks", {})
    return all(checks.get(name, {}).get("ok") for name in core_check_names)


def run_entrypoint_launch_scenario(
    scenario_name,
    force_path_fallback=False,
    preflight_cleanup=True,
    postflight_cleanup=True,
    allow_single_instance_retry=True,
):
    cscript_command = resolve_cscript_command()
    launch_command = []
    if cscript_command:
        launch_command = cscript_command + ["//nologo", ENTRYPOINT_SCRIPT]
    scenario_result = run_launch_chain_scenario(
        scenario_name,
        launch_command,
        force_path_fallback=force_path_fallback,
        preflight_cleanup=preflight_cleanup,
        postflight_cleanup=postflight_cleanup,
    )
    if allow_single_instance_retry and scenario_has_single_instance_conflict(scenario_result):
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
        time.sleep(0.5)
        scenario_result = run_launch_chain_scenario(
            scenario_name,
            launch_command,
            force_path_fallback=force_path_fallback,
            preflight_cleanup=preflight_cleanup,
            postflight_cleanup=postflight_cleanup,
        )
        scenario_result["checks"]["single_instance_conflict_retry_optional"] = line_status(
            True,
            "retried once after validator-observed single-instance conflict",
        )
    else:
        scenario_result["checks"]["single_instance_conflict_retry_optional"] = line_status(
            True,
            "not needed"
            if not scenario_has_single_instance_conflict(scenario_result)
            else "disabled to preserve repeated-launch state",
        )
    scenario_result["checks"]["cscript_available"] = line_status(
        bool(cscript_command),
        cscript_command[0] if cscript_command else "missing Windows Script Host entrypoint",
    )
    return scenario_result


def run_repeated_entrypoint_launch_scenario():
    first_result = run_entrypoint_launch_scenario(
        "vbs_repeated_launch_first",
        postflight_cleanup=False,
    )
    first_launch_released, first_launch_residual_processes = wait_for_no_launch_chain_processes_for_log_root(
        BASE_LOG_ROOT
    )
    second_result = run_entrypoint_launch_scenario(
        "vbs_repeated_launch_second",
        preflight_cleanup=False,
        allow_single_instance_retry=False,
    )

    checks = {
        "first_launch_core_path_ok": line_status(
            launch_scenario_core_ok(first_result),
            first_result["runtime_log"] or "missing first runtime log",
        ),
        "second_launch_core_path_ok": line_status(
            launch_scenario_core_ok(second_result),
            second_result["runtime_log"] or "missing second runtime log",
        ),
        "second_launch_no_failure_flow": line_status(
            second_result["checks"]["failure_flow_absent"]["ok"],
            second_result["checks"]["failure_flow_absent"]["detail"],
        ),
        "first_launch_released_before_second_launch": line_status(
            first_launch_released,
            "first launch released validator-owned launcher/runtime processes naturally"
            if first_launch_released
            else "; ".join(
                f"{process['pid']}::{process['command_line']}" for process in first_launch_residual_processes
            ),
        ),
        "second_launch_no_single_instance_conflict": line_status(
            not scenario_has_single_instance_conflict(second_result),
            "no validator-observed single-instance conflict on repeated launch"
            if not scenario_has_single_instance_conflict(second_result)
            else "validator observed single-instance conflict on repeated launch",
        ),
        "launch_state_preserved_between_attempts": line_status(
            first_result["checks"]["launch_chain_cleanup_optional"]["detail"]
            == "skipped to preserve active-session state for follow-up launch"
            and second_result["checks"]["scenario_preflight_cleanup_optional"]["detail"]
            == "skipped to preserve prior launch state"
            and second_result["checks"]["single_instance_conflict_retry_optional"]["detail"]
            in {
                "not needed",
                "disabled to preserve repeated-launch state",
            },
            "second launch reused first-launch state without validator cleanup or retry masking",
        ),
    }

    return {
        "scenario_name": "vbs_repeated_launch_cycle",
        "log_root": BASE_LOG_ROOT,
        "runtime_log": second_result["runtime_log"],
        "stdout": second_result["stdout"],
        "stderr": second_result["stderr"],
        "checks": checks,
    }


def run_accepted_relaunch_cycle_scenario(
    scenario_name="vbs_accepted_relaunch_cycle",
    first_session_extra_env=None,
):
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    reset_dir(scenario_root)
    scenario_root_entries_after_reset = dir_entry_names(scenario_root)

    cscript_command = resolve_cscript_command()
    launch_command = cscript_command + ["//nologo", ENTRYPOINT_SCRIPT] if cscript_command else []

    first_proc = None
    second_proc = None
    first_stdout = ""
    first_stderr = ""
    second_stdout = ""
    second_stderr = ""

    first_runtime_log = ""
    second_runtime_log = ""
    first_runtime_lines = []
    second_runtime_lines = []
    first_settled_seen = False
    second_settled_seen = False
    second_reacquired_seen = False
    second_shutdown_hotkey_sent = False
    second_shutdown_hotkey_detail = "hotkey not sent"
    second_shutdown_hotkey_attempts = 0

    expected_shutdown_delay = (
        (first_session_extra_env or {}).get("JARVIS_HARNESS_RELAUNCH_SHUTDOWN_DELAY_SECONDS", "").strip()
    )
    env = build_harness_env(scenario_root, extra_env=first_session_extra_env)

    launch_attempted = False
    second_launch_attempted = False

    try:
        if scenario_root_entries_after_reset or not launch_command:
            pass
        else:
            launch_attempted = True
            first_proc = subprocess.Popen(
                launch_command,
                cwd=ROOT_DIR,
                env=env,
                **hidden_subprocess_kwargs(),
            )

            first_deadline = time.time() + 25.0
            while time.time() < first_deadline:
                runtime_logs = files_matching_sorted(scenario_root, "Runtime_")
                if runtime_logs and not first_runtime_log:
                    first_runtime_log = runtime_logs[0]
                if first_runtime_log:
                    first_runtime_lines = read_lines(first_runtime_log)
                    if any(AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in first_runtime_lines):
                        first_settled_seen = True
                        break
                if first_proc.poll() is not None:
                    break
                time.sleep(0.2)

            second_env = build_harness_env(
                scenario_root,
                extra_env={"JARVIS_HARNESS_AUTO_ACCEPT_RELAUNCH": "1"},
            )
            second_launch_attempted = True
            second_proc = subprocess.Popen(
                launch_command,
                cwd=ROOT_DIR,
                env=second_env,
                **hidden_subprocess_kwargs(),
            )

            second_deadline = time.time() + 35.0
            while time.time() < second_deadline:
                runtime_logs = files_matching_sorted(scenario_root, "Runtime_")
                if runtime_logs and not first_runtime_log:
                    first_runtime_log = runtime_logs[0]
                new_second_logs = [path for path in runtime_logs if path != first_runtime_log]
                if new_second_logs and not second_runtime_log:
                    second_runtime_log = new_second_logs[0]

                first_runtime_lines = read_lines(first_runtime_log)
                second_runtime_lines = read_lines(second_runtime_log)
                second_reacquired_seen = any(
                    "RELAUNCH_ACQUIRED_AFTER_WAIT" in line for line in second_runtime_lines
                )
                second_settled_seen = any(
                    AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in second_runtime_lines
                )
                if second_reacquired_seen and second_settled_seen:
                    break
                if second_proc.poll() is not None:
                    break
                time.sleep(0.2)

            if second_settled_seen:
                second_shutdown_hotkey_attempts += 1
                second_shutdown_hotkey_sent, second_shutdown_hotkey_detail = send_shutdown_hotkey()

            shutdown_deadline = time.time() + 20.0
            while time.time() < shutdown_deadline:
                first_runtime_lines = read_lines(first_runtime_log)
                second_runtime_lines = read_lines(second_runtime_log)
                second_shutdown_seen = any(
                    "RENDERER_MAIN|SHUTDOWN_REQUESTED" in line for line in second_runtime_lines
                )
                second_exit_seen = any(
                    "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0" in line for line in second_runtime_lines
                )
                second_release_seen = any(
                    SINGLE_INSTANCE_RELEASED_MARKER in line for line in second_runtime_lines
                )
                if second_settled_seen and second_shutdown_hotkey_sent and not second_shutdown_seen and second_shutdown_hotkey_attempts < 2:
                    second_shutdown_hotkey_attempts += 1
                    second_shutdown_hotkey_sent, second_shutdown_hotkey_detail = send_shutdown_hotkey()

                if second_shutdown_seen and second_exit_seen and second_release_seen:
                    break
                if second_proc is not None and second_proc.poll() is not None and second_release_seen:
                    break
                time.sleep(0.2)
    finally:
        for proc in (first_proc, second_proc):
            if proc is None:
                continue
            try:
                if proc.poll() is None:
                    terminate_process_tree(proc)
                stdout_text, stderr_text = proc.communicate(timeout=5)
            except Exception:
                stdout_text = ""
                stderr_text = ""
            if proc is first_proc:
                first_stdout = (stdout_text or "").strip()
                first_stderr = (stderr_text or "").strip()
            else:
                second_stdout = (stdout_text or "").strip()
                second_stderr = (stderr_text or "").strip()

    first_runtime_lines = read_lines(first_runtime_log)
    second_runtime_lines = read_lines(second_runtime_log)

    residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    first_settled_index = first_marker_index(first_runtime_lines, AUTHORITATIVE_DESKTOP_SETTLED_MARKER)
    first_relaunch_request_index = first_marker_index(first_runtime_lines, "RENDERER_MAIN|RELAUNCH_REQUEST_RECEIVED")
    first_shutdown_index = first_marker_index(first_runtime_lines, "RENDERER_MAIN|SHUTDOWN_REQUESTED")
    first_exit_index = first_marker_index(first_runtime_lines, "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0")
    first_release_index = first_marker_index(first_runtime_lines, SINGLE_INSTANCE_RELEASED_MARKER)
    first_replacement_active_index = first_marker_index(
        first_runtime_lines,
        RELAUNCH_REPLACEMENT_SESSION_ACTIVE_MARKER,
    )
    first_replacement_settled_index = first_marker_index(
        first_runtime_lines,
        RELAUNCH_REPLACEMENT_SESSION_SETTLED_MARKER,
    )
    first_delay_marker_index = first_marker_index(
        first_runtime_lines,
        "RENDERER_MAIN|HARNESS_RELAUNCH_SHUTDOWN_DELAY|seconds=",
    )

    second_conflict_index = first_marker_index(second_runtime_lines, "SINGLE_INSTANCE_CONFLICT_DETECTED")
    second_prompt_accept_index = max(
        first_marker_index(second_runtime_lines, "REPLACE_PROMPT_ACCEPTED"),
        first_marker_index(second_runtime_lines, "REPLACE_PROMPT_AUTO_ACCEPTED"),
    )
    second_signal_sent_index = first_marker_index(second_runtime_lines, "RELAUNCH_SIGNAL_SENT")
    second_reacquire_index = first_marker_index(second_runtime_lines, "RELAUNCH_ACQUIRED_AFTER_WAIT")
    second_replacement_confirmed_index = first_marker_index(
        second_runtime_lines,
        "RELAUNCH_REPLACEMENT_SESSION_CONFIRMED",
    )
    second_replacement_active_index = first_marker_index(
        second_runtime_lines,
        RELAUNCH_REPLACEMENT_SESSION_ACTIVE_MARKER,
    )
    second_settled_index = first_marker_index(second_runtime_lines, AUTHORITATIVE_DESKTOP_SETTLED_MARKER)
    second_launcher_settled_observed_index = first_marker_index(
        second_runtime_lines,
        LAUNCHER_SETTLED_OBSERVED_MARKER,
    )
    second_replacement_settled_index = first_marker_index(
        second_runtime_lines,
        RELAUNCH_REPLACEMENT_SESSION_SETTLED_MARKER,
    )
    second_recoverable_complete_index = first_marker_index(
        second_runtime_lines,
        POST_SETTLED_RECOVERABLE_COMPLETE_MARKER,
    )
    second_shutdown_index = first_marker_index(second_runtime_lines, "RENDERER_MAIN|SHUTDOWN_REQUESTED")
    second_exit_index = first_marker_index(second_runtime_lines, "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0")
    second_release_index = first_marker_index(second_runtime_lines, SINGLE_INSTANCE_RELEASED_MARKER)

    ordering_detail = (
        f"first_settled={first_settled_index}, first_relaunch_request={first_relaunch_request_index}, "
        f"first_shutdown={first_shutdown_index}, first_exit={first_exit_index}, first_release={first_release_index}, "
        f"first_replacement_active={first_replacement_active_index}, "
        f"first_replacement_settled={first_replacement_settled_index}, first_delay_marker={first_delay_marker_index}, "
        f"second_conflict={second_conflict_index}, second_prompt_accept={second_prompt_accept_index}, "
        f"second_signal_sent={second_signal_sent_index}, second_reacquire={second_reacquire_index}, "
        f"second_replacement_confirmed={second_replacement_confirmed_index}, "
        f"second_replacement_active={second_replacement_active_index}, second_settled={second_settled_index}, "
        f"second_launcher_settled_observed={second_launcher_settled_observed_index}, "
        f"second_replacement_settled={second_replacement_settled_index}, second_recoverable_complete={second_recoverable_complete_index}, second_shutdown={second_shutdown_index}, "
        f"second_exit={second_exit_index}, second_release={second_release_index}"
    )

    checks = {
        "cscript_available": line_status(
            bool(cscript_command),
            cscript_command[0] if cscript_command else "missing Windows Script Host entrypoint",
        ),
        "scenario_log_root_cleared_before_launch": line_status(
            not scenario_root_entries_after_reset,
            "empty" if not scenario_root_entries_after_reset else ", ".join(scenario_root_entries_after_reset[:5]),
        ),
        "first_launch_started": line_status(
            launch_attempted,
            "first launcher process started" if launch_attempted else "first launcher process not started",
        ),
        "second_launch_started": line_status(
            second_launch_attempted,
            "replacement launcher process started" if second_launch_attempted else "replacement launcher process not started",
        ),
        "first_runtime_log_created": line_status(
            bool(first_runtime_log),
            first_runtime_log or "missing first runtime log",
        ),
        "second_runtime_log_created": line_status(
            bool(second_runtime_log) and second_runtime_log != first_runtime_log,
            second_runtime_log or "missing second runtime log",
        ),
        "first_session_settled_before_relaunch_request": line_status(
            first_settled_index >= 0 and first_relaunch_request_index > first_settled_index,
            ordering_detail,
        ),
        "first_session_received_relaunch_request": line_status(
            first_relaunch_request_index >= 0,
            "RENDERER_MAIN|RELAUNCH_REQUEST_RECEIVED",
        ),
        "first_session_shutdown_after_relaunch_request": line_status(
            first_shutdown_index > first_relaunch_request_index >= 0,
            ordering_detail,
        ),
        "first_session_exit_after_relaunch_request": line_status(
            first_exit_index > first_relaunch_request_index >= 0,
            ordering_detail,
        ),
        "first_session_released": line_status(
            first_release_index > first_exit_index >= 0,
            ordering_detail,
        ),
        "first_session_replacement_success_markers_absent": line_status(
            first_replacement_active_index < 0 and first_replacement_settled_index < 0,
            ordering_detail,
        ),
        "first_session_harness_delay_marker_optional": line_status(
            not expected_shutdown_delay or first_delay_marker_index >= 0,
            expected_shutdown_delay or "not requested",
        ),
        "second_session_conflict_detected": line_status(
            second_conflict_index >= 0,
            "SINGLE_INSTANCE_CONFLICT_DETECTED",
        ),
        "second_session_prompt_accepted": line_status(
            second_prompt_accept_index > second_conflict_index >= 0,
            ordering_detail,
        ),
        "second_session_signal_sent": line_status(
            second_signal_sent_index > second_prompt_accept_index >= 0,
            ordering_detail,
        ),
        "second_session_reacquired_after_wait": line_status(
            second_reacquire_index > second_signal_sent_index >= 0
            and second_replacement_confirmed_index >= second_reacquire_index,
            ordering_detail,
        ),
        "second_session_replacement_active_after_reacquire": line_status(
            second_replacement_active_index > second_reacquire_index >= 0,
            ordering_detail,
        ),
        "second_session_settled_after_reacquire": line_status(
            second_settled_index > second_reacquire_index >= 0
            and second_launcher_settled_observed_index >= second_settled_index
            and second_replacement_settled_index > second_settled_index,
            ordering_detail,
        ),
        "second_session_replacement_success_markers_not_premature": line_status(
            second_replacement_active_index >= second_reacquire_index >= 0
            and second_replacement_settled_index > second_settled_index > second_replacement_active_index,
            ordering_detail,
        ),
        "second_session_shutdown_hotkey_optional": line_status(
            True,
            second_shutdown_hotkey_detail if second_shutdown_hotkey_sent else "not needed before lifecycle completion",
        ),
        "second_session_lifecycle_completed_after_settled": line_status(
            (
                second_shutdown_index > second_settled_index >= 0
                and second_exit_index > second_shutdown_index
                and second_release_index > second_exit_index
            )
            or (
                second_recoverable_complete_index > second_settled_index >= 0
                and second_release_index > second_recoverable_complete_index
            ),
            ordering_detail,
        ),
        "no_relaunch_wait_timeout": line_status(
            not any("RELAUNCH_WAIT_TIMEOUT" in line for line in second_runtime_lines),
            "RELAUNCH_WAIT_TIMEOUT absent",
        ),
        "no_failure_flow_in_first_session": line_status(
            not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in first_runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "no_failure_flow_in_second_session": line_status(
            not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in second_runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "single_instance_guard_reacquired_without_dual_ownership": line_status(
            first_release_index > first_exit_index >= 0
            and second_reacquire_index >= 0
            and not any("SINGLE_INSTANCE_CONFLICT_DETECTED" in line for line in first_runtime_lines),
            "replacement launcher reacquired only after prior launcher release marker",
        ),
        "traceback_absent": line_status(
            "Traceback" not in first_stderr and "Traceback" not in second_stderr,
            (first_stderr or second_stderr or first_stdout or second_stdout).strip() or "no traceback in launcher output",
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
        "launch_chain_cleanup_optional": line_status(
            not residual_launch_chain_processes_after,
            "no residual validation-owned launcher/runtime processes detected"
            if not residual_launch_chain_processes_before
            else (
                f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
            ),
        ),
    }

    return {
        "scenario_name": scenario_name,
        "log_root": scenario_root,
        "runtime_log": second_runtime_log or first_runtime_log,
        "stdout": "\n".join(part for part in (first_stdout, second_stdout) if part),
        "stderr": "\n".join(part for part in (first_stderr, second_stderr) if part),
        "checks": checks,
    }


def run_relaunch_after_recoverable_exit_scenario():
    scenario_name = "vbs_relaunch_after_recoverable_exit"
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    reset_dir(scenario_root)
    scenario_root_entries_after_reset = dir_entry_names(scenario_root)

    fake_renderer_script = os.path.join(scenario_root, "fake_renderer_recoverable_then_relaunch.py")
    with open(fake_renderer_script, "w", encoding="utf-8") as handle:
        handle.write(
            "import sys\n"
            "import time\n"
            "\n"
            "def arg_value(flag):\n"
            "    for index, arg in enumerate(sys.argv):\n"
            "        if arg == flag and index + 1 < len(sys.argv):\n"
            "            return sys.argv[index + 1]\n"
            "    return ''\n"
            "\n"
            "runtime_log = arg_value('--runtime-log')\n"
            "\n"
            "def log(line):\n"
            "    with open(runtime_log, 'a', encoding='utf-8') as stream:\n"
            "        stream.write(line + '\\n')\n"
            "\n"
            "log('RENDERER_MAIN|START')\n"
            "log('RENDERER_MAIN|PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant')\n"
            "log('DESKTOP_OUTCOME|SETTLED|state=dormant')\n"
            "time.sleep(0.2)\n"
            "log('FAKE_RENDERER|FORCED_POST_SETTLED_EXIT')\n"
            "sys.stderr.write('[fake:gpu] Failed to make current since context is marked as lost\\n')\n"
            "sys.stderr.flush()\n"
            "raise SystemExit(5)\n"
        )

    first_env = build_harness_env(scenario_root, target_script=fake_renderer_script)
    first_result = run_hidden_command(
        [sys.executable, LAUNCHER_SCRIPT],
        env=first_env,
        timeout_seconds=45,
    )
    time.sleep(0.35)

    runtime_logs = files_matching_sorted(scenario_root, "Runtime_")
    first_runtime_log = runtime_logs[0] if runtime_logs else ""
    first_runtime_lines = read_lines(first_runtime_log)

    cscript_command = resolve_cscript_command()
    launch_command = cscript_command + ["//nologo", ENTRYPOINT_SCRIPT] if cscript_command else []
    second_proc = None
    second_stdout = ""
    second_stderr = ""
    second_runtime_log = ""
    second_runtime_lines = []
    second_settled_seen = False
    second_shutdown_hotkey_sent = False
    second_shutdown_hotkey_detail = "hotkey not sent"
    second_shutdown_hotkey_attempts = 0
    second_launch_attempted = False

    try:
        if not scenario_root_entries_after_reset and launch_command:
            second_launch_attempted = True
            second_proc = subprocess.Popen(
                launch_command,
                cwd=ROOT_DIR,
                env=build_harness_env(scenario_root),
                **hidden_subprocess_kwargs(),
            )

            second_deadline = time.time() + 25.0
            while time.time() < second_deadline:
                runtime_logs = files_matching_sorted(scenario_root, "Runtime_")
                if len(runtime_logs) >= 2:
                    second_runtime_log = runtime_logs[-1]
                    second_runtime_lines = read_lines(second_runtime_log)
                    second_settled_seen = any(
                        AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in second_runtime_lines
                    )
                    if second_settled_seen:
                        break
                if second_proc.poll() is not None:
                    break
                time.sleep(0.2)

            if second_settled_seen:
                second_shutdown_hotkey_attempts += 1
                second_shutdown_hotkey_sent, second_shutdown_hotkey_detail = send_shutdown_hotkey()

            shutdown_deadline = time.time() + 20.0
            while time.time() < shutdown_deadline:
                second_runtime_lines = read_lines(second_runtime_log)
                second_shutdown_seen = any(
                    "RENDERER_MAIN|SHUTDOWN_REQUESTED" in line for line in second_runtime_lines
                )
                second_exit_seen = any(
                    "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0" in line for line in second_runtime_lines
                )
                second_release_seen = any(
                    SINGLE_INSTANCE_RELEASED_MARKER in line for line in second_runtime_lines
                )
                if (
                    second_settled_seen
                    and second_shutdown_hotkey_sent
                    and not second_shutdown_seen
                    and second_shutdown_hotkey_attempts < 2
                ):
                    second_shutdown_hotkey_attempts += 1
                    second_shutdown_hotkey_sent, second_shutdown_hotkey_detail = send_shutdown_hotkey()
                if second_shutdown_seen and second_exit_seen and second_release_seen:
                    break
                if second_proc is not None and second_proc.poll() is not None and second_release_seen:
                    break
                time.sleep(0.2)
    finally:
        if second_proc is not None:
            try:
                if second_proc.poll() is None:
                    terminate_process_tree(second_proc)
                stdout_text, stderr_text = second_proc.communicate(timeout=5)
            except Exception:
                stdout_text = ""
                stderr_text = ""
            second_stdout = (stdout_text or "").strip()
            second_stderr = (stderr_text or "").strip()

    second_runtime_lines = read_lines(second_runtime_log)
    residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    first_settled_index = first_marker_index(first_runtime_lines, AUTHORITATIVE_DESKTOP_SETTLED_MARKER)
    first_recoverable_complete_index = first_marker_index(
        first_runtime_lines,
        POST_SETTLED_RECOVERABLE_COMPLETE_MARKER,
    )
    first_release_index = first_marker_index(first_runtime_lines, SINGLE_INSTANCE_RELEASED_MARKER)

    second_conflict_index = first_marker_index(second_runtime_lines, "SINGLE_INSTANCE_CONFLICT_DETECTED")
    second_settled_index = first_marker_index(second_runtime_lines, AUTHORITATIVE_DESKTOP_SETTLED_MARKER)
    second_launcher_settled_observed_index = first_marker_index(
        second_runtime_lines,
        LAUNCHER_SETTLED_OBSERVED_MARKER,
    )
    second_shutdown_index = first_marker_index(second_runtime_lines, "RENDERER_MAIN|SHUTDOWN_REQUESTED")
    second_exit_index = first_marker_index(second_runtime_lines, "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0")
    second_recoverable_complete_index = first_marker_index(
        second_runtime_lines,
        POST_SETTLED_RECOVERABLE_COMPLETE_MARKER,
    )
    second_release_index = first_marker_index(second_runtime_lines, SINGLE_INSTANCE_RELEASED_MARKER)

    ordering_detail = (
        f"first_settled={first_settled_index}, first_recoverable_complete={first_recoverable_complete_index}, "
        f"first_release={first_release_index}, second_conflict={second_conflict_index}, "
        f"second_settled={second_settled_index}, second_launcher_settled_observed={second_launcher_settled_observed_index}, "
        f"second_shutdown={second_shutdown_index}, second_exit={second_exit_index}, "
        f"second_recoverable_complete={second_recoverable_complete_index}, second_release={second_release_index}"
    )

    checks = {
        "cscript_available": line_status(
            bool(cscript_command),
            cscript_command[0] if cscript_command else "missing Windows Script Host entrypoint",
        ),
        "scenario_log_root_cleared_before_launch": line_status(
            not scenario_root_entries_after_reset,
            "empty" if not scenario_root_entries_after_reset else ", ".join(scenario_root_entries_after_reset[:5]),
        ),
        "first_runtime_log_created": line_status(
            bool(first_runtime_log),
            first_runtime_log or "missing first runtime log",
        ),
        "first_session_recoverable_complete_present": line_status(
            first_recoverable_complete_index > first_settled_index >= 0,
            ordering_detail,
        ),
        "first_session_released_after_recoverable_complete": line_status(
            first_release_index > first_recoverable_complete_index >= 0,
            ordering_detail,
        ),
        "first_session_failure_flow_absent": line_status(
            not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in first_runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "second_launch_started": line_status(
            second_launch_attempted,
            "post-recoverable relaunch started" if second_launch_attempted else "post-recoverable relaunch not started",
        ),
        "second_runtime_log_created": line_status(
            bool(second_runtime_log) and second_runtime_log != first_runtime_log,
            second_runtime_log or "missing second runtime log",
        ),
        "second_launch_no_single_instance_conflict": line_status(
            second_conflict_index < 0,
            ordering_detail,
        ),
        "second_session_settled_after_recoverable_exit": line_status(
            second_settled_index >= 0 and second_launcher_settled_observed_index >= second_settled_index,
            ordering_detail,
        ),
        "second_session_shutdown_hotkey_optional": line_status(
            True,
            second_shutdown_hotkey_detail if second_shutdown_hotkey_sent else "not needed before lifecycle completion",
        ),
        "second_session_lifecycle_completed_after_settled": line_status(
            (
                second_shutdown_index > second_settled_index >= 0
                and second_exit_index > second_shutdown_index
                and second_release_index > second_exit_index
            )
            or (
                second_recoverable_complete_index > second_settled_index >= 0
                and second_release_index > second_recoverable_complete_index
            ),
            ordering_detail,
        ),
        "no_failure_flow_in_second_session": line_status(
            not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in second_runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "traceback_absent": line_status(
            "Traceback" not in (first_result.stderr or "") and "Traceback" not in second_stderr,
            (first_result.stderr or second_stderr or first_result.stdout or second_stdout).strip() or "no traceback in launcher output",
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
        "launch_chain_cleanup_optional": line_status(
            not residual_launch_chain_processes_after,
            "no residual validation-owned launcher/runtime processes detected"
            if not residual_launch_chain_processes_before
            else (
                f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
            ),
        ),
    }

    return {
        "scenario_name": scenario_name,
        "log_root": scenario_root,
        "runtime_log": second_runtime_log or first_runtime_log,
        "stdout": "\n".join(
            part
            for part in ((first_result.stdout or "").strip(), second_stdout)
            if part
        ),
        "stderr": "\n".join(
            part
            for part in ((first_result.stderr or "").strip(), second_stderr)
            if part
        ),
        "checks": checks,
    }


def run_rapid_consecutive_accepted_relaunch_cycles_scenario():
    scenario_name = "vbs_consecutive_accepted_relaunch_cycles"
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    reset_dir(scenario_root)
    scenario_root_entries_after_reset = dir_entry_names(scenario_root)

    cscript_command = resolve_cscript_command()
    launch_command = cscript_command + ["//nologo", ENTRYPOINT_SCRIPT] if cscript_command else []
    first_env = build_harness_env(scenario_root)
    relaunch_env = build_harness_env(
        scenario_root,
        extra_env={"JARVIS_HARNESS_AUTO_ACCEPT_RELAUNCH": "1"},
    )

    processes = [None, None, None]
    stdouts = ["", "", ""]
    stderrs = ["", "", ""]
    runtime_logs = ["", "", ""]
    runtime_lines = [[], [], []]
    third_shutdown_hotkey_sent = False
    third_shutdown_hotkey_detail = "hotkey not sent"
    third_shutdown_hotkey_attempts = 0

    try:
        if scenario_root_entries_after_reset or not launch_command:
            pass
        else:
            processes[0] = subprocess.Popen(
                launch_command,
                cwd=ROOT_DIR,
                env=first_env,
                **hidden_subprocess_kwargs(),
            )

            first_deadline = time.time() + 25.0
            while time.time() < first_deadline:
                logs = files_matching_sorted(scenario_root, "Runtime_")
                if logs:
                    runtime_logs[0] = logs[0]
                    runtime_lines[0] = read_lines(runtime_logs[0])
                    if any(AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines[0]):
                        break
                if processes[0].poll() is not None:
                    break
                time.sleep(0.2)

            processes[1] = subprocess.Popen(
                launch_command,
                cwd=ROOT_DIR,
                env=relaunch_env,
                **hidden_subprocess_kwargs(),
            )

            second_deadline = time.time() + 35.0
            while time.time() < second_deadline:
                logs = files_matching_sorted(scenario_root, "Runtime_")
                if logs and not runtime_logs[0]:
                    runtime_logs[0] = logs[0]
                new_second_logs = [path for path in logs if path != runtime_logs[0]]
                if new_second_logs and not runtime_logs[1]:
                    runtime_logs[1] = new_second_logs[0]
                if runtime_logs[1]:
                    runtime_lines[0] = read_lines(runtime_logs[0])
                    runtime_lines[1] = read_lines(runtime_logs[1])
                    second_reacquired_seen = any(
                        "RELAUNCH_ACQUIRED_AFTER_WAIT" in line for line in runtime_lines[1]
                    )
                    second_settled_seen = any(
                        AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines[1]
                    )
                    if second_reacquired_seen and second_settled_seen:
                        break
                if processes[1].poll() is not None:
                    break
                time.sleep(0.2)

            processes[2] = subprocess.Popen(
                launch_command,
                cwd=ROOT_DIR,
                env=relaunch_env,
                **hidden_subprocess_kwargs(),
            )

            third_deadline = time.time() + 40.0
            while time.time() < third_deadline:
                logs = files_matching_sorted(scenario_root, "Runtime_")
                known_logs = {path for path in runtime_logs[:2] if path}
                new_third_logs = [path for path in logs if path not in known_logs]
                if new_third_logs and not runtime_logs[2]:
                    runtime_logs[2] = new_third_logs[0]
                if runtime_logs[2]:
                    runtime_lines[0] = read_lines(runtime_logs[0])
                    runtime_lines[1] = read_lines(runtime_logs[1])
                    runtime_lines[2] = read_lines(runtime_logs[2])
                    third_reacquired_seen = any(
                        "RELAUNCH_ACQUIRED_AFTER_WAIT" in line for line in runtime_lines[2]
                    )
                    third_settled_seen = any(
                        AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines[2]
                    )
                    if third_reacquired_seen and third_settled_seen:
                        break
                if processes[2].poll() is not None:
                    break
                time.sleep(0.2)

            if runtime_logs[2] and any(
                AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines[2]
            ):
                third_shutdown_hotkey_attempts += 1
                third_shutdown_hotkey_sent, third_shutdown_hotkey_detail = send_shutdown_hotkey()

            shutdown_deadline = time.time() + 20.0
            while time.time() < shutdown_deadline:
                runtime_lines[2] = read_lines(runtime_logs[2])
                third_shutdown_seen = any(
                    "RENDERER_MAIN|SHUTDOWN_REQUESTED" in line for line in runtime_lines[2]
                )
                third_exit_seen = any(
                    "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0" in line for line in runtime_lines[2]
                )
                third_release_seen = any(
                    SINGLE_INSTANCE_RELEASED_MARKER in line for line in runtime_lines[2]
                )
                if (
                    runtime_logs[2]
                    and third_shutdown_hotkey_sent
                    and not third_shutdown_seen
                    and third_shutdown_hotkey_attempts < 2
                ):
                    third_shutdown_hotkey_attempts += 1
                    third_shutdown_hotkey_sent, third_shutdown_hotkey_detail = send_shutdown_hotkey()
                if third_shutdown_seen and third_exit_seen and third_release_seen:
                    break
                if processes[2] is not None and processes[2].poll() is not None and third_release_seen:
                    break
                time.sleep(0.2)
    finally:
        for index, proc in enumerate(processes):
            if proc is None:
                continue
            try:
                if proc.poll() is None:
                    terminate_process_tree(proc)
                stdout_text, stderr_text = proc.communicate(timeout=5)
            except Exception:
                stdout_text = ""
                stderr_text = ""
            stdouts[index] = (stdout_text or "").strip()
            stderrs[index] = (stderr_text or "").strip()

    runtime_lines = [read_lines(path) for path in runtime_logs]
    residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    first_settled_index = first_marker_index(runtime_lines[0], AUTHORITATIVE_DESKTOP_SETTLED_MARKER)
    first_relaunch_request_index = first_marker_index(runtime_lines[0], "RENDERER_MAIN|RELAUNCH_REQUEST_RECEIVED")
    first_release_index = first_marker_index(runtime_lines[0], SINGLE_INSTANCE_RELEASED_MARKER)

    second_conflict_index = first_marker_index(runtime_lines[1], "SINGLE_INSTANCE_CONFLICT_DETECTED")
    second_reacquire_index = first_marker_index(runtime_lines[1], "RELAUNCH_ACQUIRED_AFTER_WAIT")
    second_replacement_active_index = first_marker_index(
        runtime_lines[1],
        RELAUNCH_REPLACEMENT_SESSION_ACTIVE_MARKER,
    )
    second_settled_index = first_marker_index(runtime_lines[1], AUTHORITATIVE_DESKTOP_SETTLED_MARKER)
    second_replacement_settled_index = first_marker_index(
        runtime_lines[1],
        RELAUNCH_REPLACEMENT_SESSION_SETTLED_MARKER,
    )
    second_relaunch_request_index = first_marker_index(runtime_lines[1], "RENDERER_MAIN|RELAUNCH_REQUEST_RECEIVED")
    second_release_index = first_marker_index(runtime_lines[1], SINGLE_INSTANCE_RELEASED_MARKER)

    third_conflict_index = first_marker_index(runtime_lines[2], "SINGLE_INSTANCE_CONFLICT_DETECTED")
    third_reacquire_index = first_marker_index(runtime_lines[2], "RELAUNCH_ACQUIRED_AFTER_WAIT")
    third_replacement_active_index = first_marker_index(
        runtime_lines[2],
        RELAUNCH_REPLACEMENT_SESSION_ACTIVE_MARKER,
    )
    third_settled_index = first_marker_index(runtime_lines[2], AUTHORITATIVE_DESKTOP_SETTLED_MARKER)
    third_replacement_settled_index = first_marker_index(
        runtime_lines[2],
        RELAUNCH_REPLACEMENT_SESSION_SETTLED_MARKER,
    )
    third_shutdown_index = first_marker_index(runtime_lines[2], "RENDERER_MAIN|SHUTDOWN_REQUESTED")
    third_exit_index = first_marker_index(runtime_lines[2], "RENDERER_MAIN|EVENT_LOOP_EXIT|code=0")
    third_recoverable_complete_index = first_marker_index(
        runtime_lines[2],
        POST_SETTLED_RECOVERABLE_COMPLETE_MARKER,
    )
    third_release_index = first_marker_index(runtime_lines[2], SINGLE_INSTANCE_RELEASED_MARKER)

    ordering_detail = (
        f"first_settled={first_settled_index}, first_relaunch_request={first_relaunch_request_index}, "
        f"first_release={first_release_index}, second_conflict={second_conflict_index}, "
        f"second_reacquire={second_reacquire_index}, second_replacement_active={second_replacement_active_index}, "
        f"second_settled={second_settled_index}, second_replacement_settled={second_replacement_settled_index}, "
        f"second_relaunch_request={second_relaunch_request_index}, second_release={second_release_index}, "
        f"third_conflict={third_conflict_index}, third_reacquire={third_reacquire_index}, "
        f"third_replacement_active={third_replacement_active_index}, third_settled={third_settled_index}, "
        f"third_replacement_settled={third_replacement_settled_index}, third_shutdown={third_shutdown_index}, "
        f"third_exit={third_exit_index}, third_recoverable_complete={third_recoverable_complete_index}, "
        f"third_release={third_release_index}"
    )

    checks = {
        "cscript_available": line_status(
            bool(cscript_command),
            cscript_command[0] if cscript_command else "missing Windows Script Host entrypoint",
        ),
        "scenario_log_root_cleared_before_launch": line_status(
            not scenario_root_entries_after_reset,
            "empty" if not scenario_root_entries_after_reset else ", ".join(scenario_root_entries_after_reset[:5]),
        ),
        "three_runtime_logs_created": line_status(
            all(runtime_logs) and len(set(runtime_logs)) == 3,
            ", ".join(path or "missing" for path in runtime_logs),
        ),
        "first_session_relaunch_received_after_settled": line_status(
            first_relaunch_request_index > first_settled_index >= 0,
            ordering_detail,
        ),
        "first_session_released_for_second_cycle": line_status(
            first_release_index > first_relaunch_request_index >= 0,
            ordering_detail,
        ),
        "second_session_reacquired_and_settled": line_status(
            second_reacquire_index >= 0
            and second_replacement_active_index > second_reacquire_index
            and second_settled_index > second_replacement_active_index
            and second_replacement_settled_index > second_settled_index,
            ordering_detail,
        ),
        "second_session_yielded_before_third_cycle": line_status(
            (
                second_relaunch_request_index > second_settled_index >= 0
                and second_release_index > second_relaunch_request_index
            )
            or (
                second_relaunch_request_index < 0
                and second_release_index > second_settled_index >= 0
            ),
            ordering_detail,
        ),
        "second_session_released_for_third_cycle": line_status(
            second_release_index > second_settled_index >= 0,
            ordering_detail,
        ),
        "third_session_reacquired_and_settled": line_status(
            third_conflict_index >= 0
            and third_reacquire_index >= 0
            and third_replacement_active_index > third_reacquire_index
            and third_settled_index > third_replacement_active_index
            and third_replacement_settled_index > third_settled_index,
            ordering_detail,
        ),
        "third_session_shutdown_hotkey_optional": line_status(
            True,
            third_shutdown_hotkey_detail if third_shutdown_hotkey_sent else "not needed before lifecycle completion",
        ),
        "third_session_lifecycle_completed_after_settled": line_status(
            (
                third_shutdown_index > third_settled_index >= 0
                and third_exit_index > third_shutdown_index
                and third_release_index > third_exit_index
            )
            or (
                third_recoverable_complete_index > third_settled_index >= 0
                and third_release_index > third_recoverable_complete_index
            ),
            ordering_detail,
        ),
        "no_relaunch_wait_timeout_in_replacement_sessions": line_status(
            not any("RELAUNCH_WAIT_TIMEOUT" in line for line in runtime_lines[1])
            and not any("RELAUNCH_WAIT_TIMEOUT" in line for line in runtime_lines[2]),
            "RELAUNCH_WAIT_TIMEOUT absent",
        ),
        "no_failure_flow_in_any_session": line_status(
            all(
                not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in lines)
                for lines in runtime_lines
            ),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "single_instance_guard_never_dual_owned": line_status(
            first_release_index >= 0
            and second_reacquire_index >= 0
            and second_release_index >= 0
            and third_reacquire_index >= 0,
            "each replacement session reacquired only after the previous session emitted a release marker",
        ),
        "traceback_absent": line_status(
            all("Traceback" not in stderr for stderr in stderrs),
            "\n".join(part for part in stderrs + stdouts if part) or "no traceback in launcher output",
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
        "launch_chain_cleanup_optional": line_status(
            not residual_launch_chain_processes_after,
            "no residual validation-owned launcher/runtime processes detected"
            if not residual_launch_chain_processes_before
            else (
                f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
            ),
        ),
    }

    return {
        "scenario_name": scenario_name,
        "log_root": scenario_root,
        "runtime_log": runtime_logs[2] or runtime_logs[1] or runtime_logs[0],
        "stdout": "\n".join(part for part in stdouts if part),
        "stderr": "\n".join(part for part in stderrs if part),
        "checks": checks,
    }


def run_main_default_handoff_scenario():
    scenario_result = run_launch_chain_scenario(
        "main_default_handoff",
        [sys.executable, MAIN_SCRIPT],
    )
    if scenario_has_single_instance_conflict(scenario_result):
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
        time.sleep(0.5)
        scenario_result = run_launch_chain_scenario(
            "main_default_handoff",
            [sys.executable, MAIN_SCRIPT],
        )
        scenario_result["checks"]["single_instance_conflict_retry_optional"] = line_status(
            True,
            "retried once after validator-observed single-instance conflict",
        )
    else:
        scenario_result["checks"]["single_instance_conflict_retry_optional"] = line_status(
            True,
            "not needed",
        )
    return scenario_result


def run_main_explicit_desktop_handoff_scenario():
    scenario_result = run_launch_chain_scenario(
        "main_explicit_desktop_handoff",
        [sys.executable, MAIN_SCRIPT, MAIN_EXPLICIT_DESKTOP_ARG],
    )
    if scenario_has_single_instance_conflict(scenario_result):
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
        time.sleep(0.5)
        scenario_result = run_launch_chain_scenario(
            "main_explicit_desktop_handoff",
            [sys.executable, MAIN_SCRIPT, MAIN_EXPLICIT_DESKTOP_ARG],
        )
        scenario_result["checks"]["single_instance_conflict_retry_optional"] = line_status(
            True,
            "retried once after validator-observed single-instance conflict",
        )
    else:
        scenario_result["checks"]["single_instance_conflict_retry_optional"] = line_status(
            True,
            "not needed",
        )
    return scenario_result


def run_main_invalid_argument_scenario():
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    boot_files_before = boot_runtime_files()
    result = run_hidden_command([sys.executable, MAIN_SCRIPT, MAIN_INVALID_DIRECT_ARG], timeout_seconds=20)
    time.sleep(0.35)
    boot_files_after = boot_runtime_files()
    residual_launch_chain_processes = list_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    new_boot_runtime_files = sorted(boot_files_after - boot_files_before)
    stderr_text = (result.stderr or "").strip()

    checks = {
        "invalid_argument_exit_code": line_status(result.returncode == 2, f"returncode={result.returncode}"),
        "invalid_argument_guidance_reported": line_status(
            all(marker in stderr_text for marker in EXPECTED_MAIN_INVALID_ARG_MARKERS),
            stderr_text or "missing stderr guidance",
        ),
        "boot_runtime_absent": line_status(
            not new_boot_runtime_files,
            "none" if not new_boot_runtime_files else ", ".join(new_boot_runtime_files[:5]),
        ),
        "launch_chain_process_absent": line_status(
            not residual_launch_chain_processes,
            "none"
            if not residual_launch_chain_processes
            else "; ".join(
                f"{process['pid']}::{process['command_line']}" for process in residual_launch_chain_processes
            ),
        ),
        "traceback_absent": line_status(
            "Traceback" not in (result.stdout or "") and "Traceback" not in (result.stderr or ""),
            stderr_text or (result.stdout or "").strip() or "no traceback in stdout/stderr",
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

    return {
        "scenario_name": "main_invalid_direct_argument",
        "runtime_log": "",
        "stdout": (result.stdout or "").strip(),
        "stderr": stderr_text,
        "checks": checks,
    }


def run_missing_settled_signal_scenario():
    scenario_name = "launcher_missing_settled_signal"
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    reset_dir(scenario_root)
    fake_renderer_script = os.path.join(scenario_root, "fake_renderer_no_settle.py")

    with open(fake_renderer_script, "w", encoding="utf-8") as handle:
        handle.write(
            "import time\n"
            "print('fake renderer start', flush=True)\n"
            "time.sleep(8.5)\n"
            "print('fake renderer clean exit without settled marker', flush=True)\n"
        )

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = scenario_root
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = fake_renderer_script
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"

    result = run_hidden_command(
        [sys.executable, LAUNCHER_SCRIPT],
        env=env,
        timeout_seconds=45,
    )
    time.sleep(0.35)

    runtime_log = latest_file_matching(scenario_root, "Runtime_")
    runtime_lines = read_lines(runtime_log)
    residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    checks = {
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "renderer_target_matches_fake_script": line_status(
            any(f"Renderer target: {fake_renderer_script}" in line for line in runtime_lines),
            fake_renderer_script,
        ),
        "settled_missing_within_window_warning_present": line_status(
            any("STATUS|WARNING|LAUNCHER_RUNTIME|DESKTOP_SETTLED_NOT_OBSERVED_WITHIN_WINDOW" in line for line in runtime_lines),
            "STATUS|WARNING|LAUNCHER_RUNTIME|DESKTOP_SETTLED_NOT_OBSERVED_WITHIN_WINDOW",
        ),
        "settled_stall_confirmed_warning_present": line_status(
            any("STATUS|WARNING|LAUNCHER_RUNTIME|DESKTOP_SETTLED_STALL_CONFIRMED" in line for line in runtime_lines),
            "STATUS|WARNING|LAUNCHER_RUNTIME|DESKTOP_SETTLED_STALL_CONFIRMED",
        ),
        "startup_abort_requested_on_stall_present": line_status(
            any("STATUS|WARNING|LAUNCHER_RUNTIME|STARTUP_ABORT_REQUESTED_ON_CONFIRMED_SETTLED_STALL" in line for line in runtime_lines),
            "STATUS|WARNING|LAUNCHER_RUNTIME|STARTUP_ABORT_REQUESTED_ON_CONFIRMED_SETTLED_STALL",
        ),
        "settled_missing_before_exit_warning_present": line_status(
            any("STATUS|WARNING|LAUNCHER_RUNTIME|DESKTOP_SETTLED_NOT_OBSERVED_BEFORE_EXIT" in line for line in runtime_lines),
            "STATUS|WARNING|LAUNCHER_RUNTIME|DESKTOP_SETTLED_NOT_OBSERVED_BEFORE_EXIT",
        ),
        "authoritative_settled_absent": line_status(
            not any(AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines),
            AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
        ),
        "launcher_settled_success_absent": line_status(
            not any(LAUNCHER_SETTLED_OBSERVED_MARKER in line for line in runtime_lines),
            LAUNCHER_SETTLED_OBSERVED_MARKER,
        ),
        "normal_exit_complete_absent": line_status(
            not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE" in line for line in runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE absent",
        ),
        "failure_flow_complete_present": line_status(
            any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE",
        ),
        "traceback_absent": line_status(
            "Traceback" not in (result.stdout or "") and "Traceback" not in (result.stderr or ""),
            (result.stderr or result.stdout).strip() or "no traceback in stdout/stderr",
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
        "launch_chain_cleanup_optional": line_status(
            not residual_launch_chain_processes_after,
            "no residual validation-owned launcher/runtime processes detected"
            if not residual_launch_chain_processes_before
            else (
                f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
            ),
        ),
    }

    return {
        "scenario_name": scenario_name,
        "log_root": scenario_root,
        "runtime_log": runtime_log,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "checks": checks,
    }


def run_rapid_pre_settled_exit_scenario():
    scenario_name = "launcher_rapid_pre_settled_exit"
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    reset_dir(scenario_root)
    fake_renderer_script = os.path.join(scenario_root, "fake_renderer_rapid_pre_settle_exit.py")

    with open(fake_renderer_script, "w", encoding="utf-8") as handle:
        handle.write(
            "import sys\n"
            "\n"
            "def arg_value(flag):\n"
            "    for index, arg in enumerate(sys.argv):\n"
            "        if arg == flag and index + 1 < len(sys.argv):\n"
            "            return sys.argv[index + 1]\n"
            "    return ''\n"
            "\n"
            "runtime_log = arg_value('--runtime-log')\n"
            "\n"
            "def log(line):\n"
            "    with open(runtime_log, 'a', encoding='utf-8') as stream:\n"
            "        stream.write(line + '\\n')\n"
            "\n"
            "log('RENDERER_MAIN|START')\n"
            "sys.stderr.write('[fake:rapid] renderer exited before settled\\n')\n"
            "sys.stderr.flush()\n"
            "raise SystemExit(7)\n"
        )

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = scenario_root
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = fake_renderer_script
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"

    result = run_hidden_command(
        [sys.executable, LAUNCHER_SCRIPT],
        env=env,
        timeout_seconds=45,
    )
    time.sleep(0.35)

    runtime_log = latest_file_matching(scenario_root, "Runtime_")
    runtime_lines = read_lines(runtime_log)
    residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    checks = {
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "authoritative_settled_absent": line_status(
            not any(AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines),
            AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
        ),
        "launcher_settled_success_absent": line_status(
            not any(LAUNCHER_SETTLED_OBSERVED_MARKER in line for line in runtime_lines),
            LAUNCHER_SETTLED_OBSERVED_MARKER,
        ),
        "post_settled_runtime_exit_absent": line_status(
            not any(POST_SETTLED_RUNTIME_EXIT_MARKER in line for line in runtime_lines),
            POST_SETTLED_RUNTIME_EXIT_MARKER,
        ),
        "post_settled_recoverable_complete_absent": line_status(
            not any(POST_SETTLED_RECOVERABLE_COMPLETE_MARKER in line for line in runtime_lines),
            POST_SETTLED_RECOVERABLE_COMPLETE_MARKER,
        ),
        "failure_flow_complete_present": line_status(
            any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE",
        ),
        "traceback_absent": line_status(
            "Traceback" not in (result.stdout or "") and "Traceback" not in (result.stderr or ""),
            (result.stderr or result.stdout).strip() or "no traceback in stdout/stderr",
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
        "launch_chain_cleanup_optional": line_status(
            not residual_launch_chain_processes_after,
            "no residual validation-owned launcher/runtime processes detected"
            if not residual_launch_chain_processes_before
            else (
                f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
            ),
        ),
    }

    return {
        "scenario_name": scenario_name,
        "log_root": scenario_root,
        "runtime_log": runtime_log,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "checks": checks,
    }


def run_post_settled_clean_exit_precedence_scenario():
    scenario_name = "launcher_post_settled_clean_exit_precedence"
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    reset_dir(scenario_root)
    fake_renderer_script = os.path.join(scenario_root, "fake_renderer_post_settled_clean_exit.py")

    with open(fake_renderer_script, "w", encoding="utf-8") as handle:
        handle.write(
            "import sys\n"
            "\n"
            "def arg_value(flag):\n"
            "    for index, arg in enumerate(sys.argv):\n"
            "        if arg == flag and index + 1 < len(sys.argv):\n"
            "            return sys.argv[index + 1]\n"
            "    return ''\n"
            "\n"
            "runtime_log = arg_value('--runtime-log')\n"
            "\n"
            "def log(line):\n"
            "    with open(runtime_log, 'a', encoding='utf-8') as stream:\n"
            "        stream.write(line + '\\n')\n"
            "\n"
            "log('RENDERER_MAIN|START')\n"
            "log('RENDERER_MAIN|PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant')\n"
            "log('DESKTOP_OUTCOME|SETTLED|state=dormant')\n"
            "log('RENDERER_MAIN|SHUTDOWN_REQUESTED')\n"
            "log('RENDERER_MAIN|EVENT_LOOP_EXIT|code=0')\n"
            "raise SystemExit(0)\n"
        )

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = scenario_root
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = fake_renderer_script
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"

    result = run_hidden_command(
        [sys.executable, LAUNCHER_SCRIPT],
        env=env,
        timeout_seconds=45,
    )
    time.sleep(0.35)

    runtime_log = latest_file_matching(scenario_root, "Runtime_")
    runtime_lines = read_lines(runtime_log)
    residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    checks = {
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "authoritative_settled_present": line_status(
            any(AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines),
            AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
        ),
        "launcher_settled_success_present": line_status(
            any(LAUNCHER_SETTLED_OBSERVED_MARKER in line for line in runtime_lines),
            LAUNCHER_SETTLED_OBSERVED_MARKER,
        ),
        "normal_exit_complete_present": line_status(
            any("STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE" in line for line in runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE",
        ),
        "post_settled_runtime_exit_absent": line_status(
            not any(POST_SETTLED_RUNTIME_EXIT_MARKER in line for line in runtime_lines),
            POST_SETTLED_RUNTIME_EXIT_MARKER,
        ),
        "post_settled_recoverable_complete_absent": line_status(
            not any(POST_SETTLED_RECOVERABLE_COMPLETE_MARKER in line for line in runtime_lines),
            POST_SETTLED_RECOVERABLE_COMPLETE_MARKER,
        ),
        "failure_flow_complete_absent": line_status(
            not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "traceback_absent": line_status(
            "Traceback" not in (result.stdout or "") and "Traceback" not in (result.stderr or ""),
            (result.stderr or result.stdout).strip() or "no traceback in stdout/stderr",
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
        "launch_chain_cleanup_optional": line_status(
            not residual_launch_chain_processes_after,
            "no residual validation-owned launcher/runtime processes detected"
            if not residual_launch_chain_processes_before
            else (
                f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
            ),
        ),
    }

    return {
        "scenario_name": scenario_name,
        "log_root": scenario_root,
        "runtime_log": runtime_log,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "checks": checks,
    }


def run_post_settled_recoverable_exit_scenario(
    scenario_name="launcher_post_settled_recoverable_exit",
    settle_delay_seconds=0.25,
):
    scenario_root = os.path.join(BASE_LOG_ROOT, scenario_name)
    preexisting_processes_before, preexisting_processes_killed, preexisting_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    reset_dir(scenario_root)
    fake_renderer_script = os.path.join(scenario_root, "fake_renderer_post_settled_exit.py")

    with open(fake_renderer_script, "w", encoding="utf-8") as handle:
        handle.write(
            "import sys\n"
            "import time\n"
            "\n"
            "def arg_value(flag):\n"
            "    for index, arg in enumerate(sys.argv):\n"
            "        if arg == flag and index + 1 < len(sys.argv):\n"
            "            return sys.argv[index + 1]\n"
            "    return ''\n"
            "\n"
            "runtime_log = arg_value('--runtime-log')\n"
            "\n"
            "def log(line):\n"
            "    with open(runtime_log, 'a', encoding='utf-8') as stream:\n"
            "        stream.write(line + '\\n')\n"
            "\n"
            "log('RENDERER_MAIN|START')\n"
            "log('RENDERER_MAIN|PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant')\n"
            "log('DESKTOP_OUTCOME|SETTLED|state=dormant')\n"
            f"time.sleep({settle_delay_seconds})\n"
            "log('FAKE_RENDERER|FORCED_POST_SETTLED_EXIT')\n"
            "sys.stderr.write('[fake:gpu] Failed to make current since context is marked as lost\\n')\n"
            "sys.stderr.flush()\n"
            "raise SystemExit(5)\n"
        )

    env = os.environ.copy()
    env["JARVIS_HARNESS_LOG_ROOT"] = scenario_root
    env["JARVIS_HARNESS_TARGET_SCRIPT"] = fake_renderer_script
    env["JARVIS_HARNESS_DISABLE_DIAGNOSTICS"] = "1"
    env["JARVIS_HARNESS_DISABLE_VOICE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"

    result = run_hidden_command(
        [sys.executable, LAUNCHER_SCRIPT],
        env=env,
        timeout_seconds=45,
    )
    time.sleep(0.35)

    runtime_log = latest_file_matching(scenario_root, "Runtime_")
    runtime_lines = read_lines(runtime_log)
    residual_launch_chain_processes_before, residual_launch_chain_killed, residual_launch_chain_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )

    checks = {
        "runtime_log_created": line_status(
            bool(runtime_log),
            runtime_log or "missing runtime log",
        ),
        "renderer_target_matches_fake_script": line_status(
            any(f"Renderer target: {fake_renderer_script}" in line for line in runtime_lines),
            fake_renderer_script,
        ),
        "authoritative_settled_present": line_status(
            any(AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines),
            AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
        ),
        "launcher_settled_success_present": line_status(
            any(LAUNCHER_SETTLED_OBSERVED_MARKER in line for line in runtime_lines),
            LAUNCHER_SETTLED_OBSERVED_MARKER,
        ),
        "post_settled_runtime_exit_warning_present": line_status(
            any(POST_SETTLED_RUNTIME_EXIT_MARKER in line for line in runtime_lines),
            POST_SETTLED_RUNTIME_EXIT_MARKER,
        ),
        "post_settled_recoverable_complete_present": line_status(
            any(POST_SETTLED_RECOVERABLE_COMPLETE_MARKER in line for line in runtime_lines),
            POST_SETTLED_RECOVERABLE_COMPLETE_MARKER,
        ),
        "clean_shutdown_markers_absent": line_status(
            not any("RENDERER_MAIN|SHUTDOWN_REQUESTED" in line for line in runtime_lines)
            and not any("RENDERER_MAIN|EVENT_LOOP_EXIT|code=0" in line for line in runtime_lines),
            "RENDERER_MAIN|SHUTDOWN_REQUESTED + RENDERER_MAIN|EVENT_LOOP_EXIT|code=0 absent",
        ),
        "normal_exit_complete_absent": line_status(
            not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE" in line for line in runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|NORMAL_EXIT_COMPLETE absent",
        ),
        "failure_flow_complete_absent": line_status(
            not any("STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE" in line for line in runtime_lines),
            "STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE absent",
        ),
        "traceback_absent": line_status(
            "Traceback" not in (result.stdout or "") and "Traceback" not in (result.stderr or ""),
            (result.stderr or result.stdout).strip() or "no traceback in stdout/stderr",
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
        "launch_chain_cleanup_optional": line_status(
            not residual_launch_chain_processes_after,
            "no residual validation-owned launcher/runtime processes detected"
            if not residual_launch_chain_processes_before
            else (
                f"detected {len(residual_launch_chain_processes_before)} residual process(es); "
                f"killed={','.join(str(pid) for pid in residual_launch_chain_killed) or 'none'}"
            ),
        ),
    }

    return {
        "scenario_name": scenario_name,
        "log_root": scenario_root,
        "runtime_log": runtime_log,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "checks": checks,
    }


def run_validation():
    ensure_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    entrypoint_text = read_text(ENTRYPOINT_SCRIPT)
    entrypoint_line = entrypoint_shim_line()
    launcher_text = read_text(LAUNCHER_SCRIPT)
    launcher_line = launcher_default_target_line()
    main_text = read_text(MAIN_SCRIPT)

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
                if any(AUTHORITATIVE_DESKTOP_SETTLED_MARKER in line for line in runtime_lines):
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
    direct_runtime_processes_before, direct_runtime_killed, direct_runtime_processes_after = (
        cleanup_launch_chain_processes_for_log_root(BASE_LOG_ROOT)
    )
    time.sleep(0.35)

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
    passive_handoff_index = first_marker_index(
        runtime_lines,
        "RENDERER_MAIN|PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant",
    )
    authoritative_settled_index = first_marker_index(
        runtime_lines,
        AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
    )
    ordering_detail = (
        f"deferred={deferred_index}, core_ready={core_ready_index}, "
        f"show={show_index}, first_visible={first_visible_index}, "
        f"startup_ready={startup_ready_index}, passive_handoff={passive_handoff_index}, "
        f"authoritative_settled={authoritative_settled_index}"
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
    checks["authoritative_settled_after_passive_handoff"] = line_status(
        authoritative_settled_index > passive_handoff_index >= 0,
        ordering_detail,
    )

    checks["authoritative_settled_reached_before_termination"] = line_status(
        ready_seen,
        AUTHORITATIVE_DESKTOP_SETTLED_MARKER,
    )
    checks["traceback_absent"] = line_status(
        "Traceback" not in stderr_text,
        stderr_text.strip() or "no traceback in stderr",
    )
    checks["direct_runtime_cleanup_optional"] = line_status(
        not direct_runtime_processes_after,
        "no residual direct-runtime validation processes detected"
        if not direct_runtime_processes_before
        else (
            f"detected {len(direct_runtime_processes_before)} residual direct-runtime process(es); "
            f"killed={','.join(str(pid) for pid in direct_runtime_killed) or 'none'}"
        ),
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
    checks["main_script_exists"] = line_status(
        os.path.exists(MAIN_SCRIPT),
        MAIN_SCRIPT,
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
    for marker in EXPECTED_MAIN_HANDOFF_MARKERS:
        checks[f"main_handoff_marker::{marker}"] = line_status(
            marker in main_text,
            marker,
        )

    default_launch_result = run_entrypoint_launch_scenario("vbs_default")
    fallback_launch_result = run_entrypoint_launch_scenario(
        "vbs_fallback",
        force_path_fallback=True,
    )
    main_handoff_result = run_main_default_handoff_scenario()
    main_explicit_handoff_result = run_main_explicit_desktop_handoff_scenario()
    repeated_entrypoint_result = run_repeated_entrypoint_launch_scenario()
    accepted_relaunch_result = run_accepted_relaunch_cycle_scenario()
    accepted_relaunch_slow_shutdown_result = run_accepted_relaunch_cycle_scenario(
        "vbs_accepted_relaunch_cycle_slow_shutdown",
        {"JARVIS_HARNESS_RELAUNCH_SHUTDOWN_DELAY_SECONDS": "1.6"},
    )
    relaunch_after_recoverable_result = run_relaunch_after_recoverable_exit_scenario()
    consecutive_relaunch_cycles_result = run_rapid_consecutive_accepted_relaunch_cycles_scenario()
    main_invalid_argument_result = run_main_invalid_argument_scenario()
    rapid_pre_settled_result = run_rapid_pre_settled_exit_scenario()
    missing_settled_result = run_missing_settled_signal_scenario()
    post_settled_clean_exit_result = run_post_settled_clean_exit_precedence_scenario()
    post_settled_recoverable_result = run_post_settled_recoverable_exit_scenario()
    post_settled_recoverable_immediate_result = run_post_settled_recoverable_exit_scenario(
        "launcher_post_settled_recoverable_exit_immediate",
        0.0,
    )

    for scenario_result in (
        default_launch_result,
        fallback_launch_result,
        main_handoff_result,
        main_explicit_handoff_result,
    ):
        scenario_name = scenario_result["scenario_name"]
        checks[f"{scenario_name}::runtime_log_recorded"] = line_status(
            bool(scenario_result["runtime_log"]),
            scenario_result["runtime_log"] or "missing runtime log",
        )
        for check_name, check_result in scenario_result["checks"].items():
            checks[f"{scenario_name}::{check_name}"] = check_result

    for check_name, check_result in main_invalid_argument_result["checks"].items():
        checks[f"{main_invalid_argument_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in repeated_entrypoint_result["checks"].items():
        checks[f"{repeated_entrypoint_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in accepted_relaunch_result["checks"].items():
        checks[f"{accepted_relaunch_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in accepted_relaunch_slow_shutdown_result["checks"].items():
        checks[f"{accepted_relaunch_slow_shutdown_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in relaunch_after_recoverable_result["checks"].items():
        checks[f"{relaunch_after_recoverable_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in consecutive_relaunch_cycles_result["checks"].items():
        checks[f"{consecutive_relaunch_cycles_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in rapid_pre_settled_result["checks"].items():
        checks[f"{rapid_pre_settled_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in missing_settled_result["checks"].items():
        checks[f"{missing_settled_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in post_settled_clean_exit_result["checks"].items():
        checks[f"{post_settled_clean_exit_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in post_settled_recoverable_result["checks"].items():
        checks[f"{post_settled_recoverable_result['scenario_name']}::{check_name}"] = check_result
    for check_name, check_result in post_settled_recoverable_immediate_result["checks"].items():
        checks[f"{post_settled_recoverable_immediate_result['scenario_name']}::{check_name}"] = check_result

    return {
        "branch_state": detect_branch_state(),
        "entrypoint_script": ENTRYPOINT_SCRIPT,
        "entrypoint_line": entrypoint_line,
        "runtime_log": runtime_log,
        "target_script": DEFAULT_TARGET_SCRIPT,
        "launcher_line": launcher_line,
        "launch_scenarios": [
            default_launch_result,
            fallback_launch_result,
            main_handoff_result,
            main_explicit_handoff_result,
        ],
        "nonlaunch_scenarios": [
            repeated_entrypoint_result,
            accepted_relaunch_result,
            accepted_relaunch_slow_shutdown_result,
            relaunch_after_recoverable_result,
            consecutive_relaunch_cycles_result,
            main_invalid_argument_result,
            rapid_pre_settled_result,
            missing_settled_result,
            post_settled_clean_exit_result,
            post_settled_recoverable_result,
            post_settled_recoverable_immediate_result,
        ],
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
    if result.get("nonlaunch_scenarios"):
        for scenario_result in result["nonlaunch_scenarios"]:
            lines.extend(
                [
                    "",
                    f"Non-launch scenario: {scenario_result['scenario_name']}",
                    f"  Log root: {scenario_result.get('log_root', 'n/a')}",
                    f"  Runtime log: {scenario_result.get('runtime_log', '') or 'missing runtime log'}",
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
