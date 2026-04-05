import datetime
import os
import subprocess
import sys
import textwrap
import time

from PySide6.QtCore import QEvent, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QFont, QFontMetrics, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from desktop.single_instance import NamedSignal, SingleInstanceGuard, acquire_or_prompt_replace

DEV_DIR = os.path.join(ROOT_DIR, "dev")
DEV_LAUNCHERS_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")
DEV_LOGS_DIR = os.path.join(DEV_DIR, "logs")
DEV_TOOLKIT_SESSION_LOG_DIR = os.path.join(DEV_LOGS_DIR, "dev_toolkit_session")
DEV_TOOLKIT_SMOKE_REPORT_DIR = os.path.join(DEV_LOGS_DIR, "dev_toolkit_smoke_validation", "reports")
BOOT_TRANSITION_CAPTURE_ROOT = os.path.join(DEV_LOGS_DIR, "boot_transition_capture")
BOOT_TRANSITION_CAPTURE_REPORT_DIR = os.path.join(BOOT_TRANSITION_CAPTURE_ROOT, "reports")
BOOT_TRANSITION_CAPTURE_FRAMES_DIR = os.path.join(BOOT_TRANSITION_CAPTURE_ROOT, "captures")
SUPPORT_BUNDLE_TRIAGE_SCRIPT = os.path.join(ROOT_DIR, "dev", "orin_support_bundle_triage.py")

PYTHONW_PATH = r"C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
DEV_TOOLKIT_MUTEX = r"Local\JarvisDevToolkitSingletonV1"
DEV_TOOLKIT_RELAUNCH_EVENT = r"Local\JarvisDevToolkitRelaunchRequestV1"
dev_toolkit_guard = SingleInstanceGuard(DEV_TOOLKIT_MUTEX)
dev_toolkit_relaunch_signal = NamedSignal(DEV_TOOLKIT_RELAUNCH_EVENT)


def create_dev_toolkit_runtime_log() -> str:
    os.makedirs(DEV_TOOLKIT_SESSION_LOG_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return os.path.join(DEV_TOOLKIT_SESSION_LOG_DIR, f"Runtime_{stamp}.txt")


def write_dev_toolkit_runtime_marker(runtime_log_file: str, event: str) -> None:
    if not runtime_log_file:
        return
    try:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        with open(runtime_log_file, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {event}\n")
    except Exception:
        pass

LANE_CONFIG = {
    "diagnostics": {
        "label": "Diagnostics UI Test",
        "detail": (
            "Launches the standalone diagnostics window with safe manual test content. "
            "Best for focus, monitor, dismiss, and passive-window checks."
        ),
        "quiet_launcher": "launch_orin_diagnostics_manual_test.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": True,
        "log_root": os.path.join(DEV_LOGS_DIR, "diagnostics_ui"),
        "runtime_fixed": os.path.join(DEV_LOGS_DIR, "diagnostics_ui", "Runtime_manual_diagnostics_test.txt"),
        "crash_folder": "",
    },
    "repeatedCrash": {
        "label": "Repeated-Crash Failure Lane",
        "detail": (
            "Exercises the real launcher recovery path using a deterministic repeated crash "
            "target until diagnostics completion."
        ),
        "quiet_launcher": "launch_orin_launcher_failure_manual_test.vbs",
        "voice_launcher": "launch_orin_launcher_failure_manual_test_with_voice.vbs",
        "supports_voice": True,
        "available_modes": ("quiet", "voice"),
        "opens_window": True,
        "log_root": os.path.join(DEV_LOGS_DIR, "manual_launcher_failure_test"),
        "log_root_with_voice": os.path.join(DEV_LOGS_DIR, "manual_launcher_failure_test_with_voice"),
        "crash_folder": "crash",
    },
    "startupAbort": {
        "label": "Startup-Abort Lane",
        "detail": (
            "Exercises launcher stall observation, cooperative startup abort, recovery, "
            "and diagnostics completion."
        ),
        "quiet_launcher": "launch_orin_launcher_startup_abort_manual_test.vbs",
        "voice_launcher": "launch_orin_launcher_startup_abort_manual_test_with_voice.vbs",
        "supports_voice": True,
        "available_modes": ("quiet", "voice"),
        "opens_window": True,
        "log_root": os.path.join(DEV_LOGS_DIR, "manual_launcher_startup_abort_test"),
        "log_root_with_voice": os.path.join(DEV_LOGS_DIR, "manual_launcher_startup_abort_test_with_voice"),
        "crash_folder": "crash",
    },
    "bootManualFlow": {
        "label": "Boot ORIN Manual Flow",
        "detail": (
            "Launches the dev-only main.py boot harness in manual mode so Boot ORIN reaches "
            "the first prompt and waits for operator input."
        ),
        "quiet_launcher": "launch_orin_main_manual_test.vbs",
        "voice_launcher": "launch_orin_main_manual_test_with_voice.vbs",
        "supports_voice": True,
        "available_modes": ("quiet", "voice"),
        "opens_window": True,
        "log_root": os.path.join(DEV_LOGS_DIR, "boot_manual_flow"),
        "crash_folder": "",
    },
    "bootAutoHandoffSkipImport": {
        "label": "Boot ORIN Auto Handoff (Skip Import)",
        "detail": (
            "Launches the dev-only main.py boot harness in auto-handoff mode so Boot ORIN "
            "drives the existing engage hud -> no chain and hands off into Desktop ORIN."
        ),
        "quiet_launcher": "launch_orin_main_auto_handoff_skip_import.vbs",
        "voice_launcher": "launch_orin_main_auto_handoff_skip_import_with_voice.vbs",
        "supports_voice": True,
        "available_modes": ("quiet", "voice"),
        "opens_window": True,
        "log_root": os.path.join(DEV_LOGS_DIR, "boot_auto_handoff_skip_import"),
        "crash_folder": "",
    },
    "bootTransitionVerification": {
        "label": "Boot To Desktop Handoff Verification",
        "detail": (
            "Runs a contained quiet boot-to-desktop verification pass, validates the current "
            "handoff milestone order, then writes a compact pass/fail report."
        ),
        "quiet_launcher": "launch_orin_boot_transition_verification.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "boot_transition_verification"),
        "report_root": os.path.join(DEV_LOGS_DIR, "boot_transition_verification", "reports"),
        "report_prefix": "BootTransitionVerificationReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "bootTransitionCapture": {
        "label": "Boot Transition Capture",
        "detail": (
            "Runs the quiet auto-handoff boot path, captures primary-screen transition frames at key "
            "handoff markers, and writes a compact report with the saved PNG sequence."
        ),
        "quiet_launcher": "launch_orin_boot_transition_capture.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "boot_transition_capture"),
        "report_root": os.path.join(DEV_LOGS_DIR, "boot_transition_capture", "reports"),
        "report_prefix": "BootTransitionCaptureReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "bootMonitorPreflight": {
        "label": "Boot Monitor Preflight",
        "detail": (
            "Captures the current monitor topology using the same left/center/right assumptions "
            "as Boot ORIN and writes a compact readiness report before you run a boot lane."
        ),
        "quiet_launcher": "launch_orin_boot_monitor_preflight.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "boot_monitor_preflight"),
        "report_root": os.path.join(DEV_LOGS_DIR, "boot_monitor_preflight", "reports"),
        "report_prefix": "BootMonitorPreflightReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "bootToolkitValidation": {
        "label": "Boot Helper Toolkit Validation",
        "detail": (
            "Runs a contained offscreen validation of the Boot & Transition helper lanes and verifies "
            "the Dev Toolkit can launch Boot Monitor Preflight and Boot To Desktop Handoff Verification "
            "and then reopen their fresh reports."
        ),
        "quiet_launcher": "launch_orin_boot_toolkit_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "boot_toolkit_validation"),
        "report_root": os.path.join(DEV_LOGS_DIR, "boot_toolkit_validation", "reports"),
        "report_prefix": "BootToolkitValidationReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "voiceRegression": {
        "label": "Voice Regression Harness",
        "detail": (
            "Runs the contained FB-018 voice regression harness across the current launcher-owned "
            "voice lanes and direct diagnostics voice probes, then writes a pass/fail report."
        ),
        "quiet_launcher": "launch_orin_voice_regression_harness.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("voice",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "voice_regression_harness"),
        "report_root": os.path.join(DEV_LOGS_DIR, "voice_regression_harness", "reports"),
        "report_prefix": "VoiceRegressionReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "desktopHealthy": {
        "label": "Healthy Desktop Launch Validation",
        "detail": (
            "Runs a contained offscreen validation of the current default desktop renderer target "
            "and verifies healthy startup milestones such as WINDOW_SHOW_CALLED and STARTUP_READY."
        ),
        "quiet_launcher": "launch_orin_desktop_entrypoint_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "desktop_entrypoint_validation"),
        "report_root": os.path.join(DEV_LOGS_DIR, "desktop_entrypoint_validation", "reports"),
        "report_prefix": "DesktopEntrypointValidationReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "launcherHealthy": {
        "label": "Healthy Launcher Path Validation",
        "detail": (
            "Runs the real desktop launcher against its current default target, waits for "
            "launcher-owned healthy startup markers, then triggers a controlled shutdown and "
            "captures reusable pass/fail evidence for the contained healthy path."
        ),
        "quiet_launcher": "launch_orin_desktop_launcher_healthy_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "desktop_launcher_healthy_validation"),
        "report_root": os.path.join(DEV_LOGS_DIR, "desktop_launcher_healthy_validation", "reports"),
        "report_prefix": "DesktopLauncherHealthyValidationReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "desktopToolkitValidation": {
        "label": "Desktop Helper Toolkit Validation",
        "detail": (
            "Runs a contained offscreen validation of the desktop helper lanes and verifies the "
            "Dev Toolkit can launch Healthy Desktop Launch Validation and Healthy Launcher Path "
            "Validation and reopen their fresh reports."
        ),
        "quiet_launcher": "launch_orin_desktop_toolkit_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "desktop_toolkit_validation"),
        "report_root": os.path.join(DEV_LOGS_DIR, "desktop_toolkit_validation", "reports"),
        "report_prefix": "DesktopToolkitValidationReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "devToolkitSmokeValidation": {
        "label": "Dev Toolkit Smoke Validation",
        "detail": (
            "Runs the boot-side Toolkit validation and the desktop-side Toolkit validation in sequence, "
            "then writes one consolidated smoke report so the current helper-lane wiring can be checked "
            "with a single background run."
        ),
        "quiet_launcher": "launch_orin_dev_toolkit_smoke_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "dev_toolkit_smoke_validation"),
        "report_root": os.path.join(DEV_LOGS_DIR, "dev_toolkit_smoke_validation", "reports"),
        "report_prefix": "DevToolkitSmokeValidationReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "launcherRegression": {
        "label": "Desktop Launcher Regression Harness",
        "detail": (
            "Runs the contained desktop launcher regression harness across the current healthy, "
            "repeated-crash, and startup-abort launcher paths, then writes one consolidated "
            "pass/fail report."
        ),
        "quiet_launcher": "launch_orin_desktop_launcher_regression_harness.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "desktop_launcher_regression_harness"),
        "report_root": os.path.join(DEV_LOGS_DIR, "desktop_launcher_regression_harness", "reports"),
        "report_prefix": "DesktopLauncherRegressionHarnessReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "supportBundleTriageHarness": {
        "label": "Support Bundle Triage Harness",
        "detail": (
            "Runs the contained FB-019 support-bundle triage regression harness across the "
            "current supported launcher-owned bundle classes and safe unknown fallback, then "
            "writes one consolidated pass/fail report."
        ),
        "quiet_launcher": "launch_orin_support_bundle_triage_harness.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "support_bundle_triage_harness"),
        "report_root": os.path.join(DEV_LOGS_DIR, "support_bundle_triage_harness", "reports"),
        "report_prefix": "SupportBundleTriageHarnessReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "supportBundleTriageToolkitValidation": {
        "label": "Support Bundle Triage Toolkit Validation",
        "detail": (
            "Runs the contained offscreen validator for the raw FB-019 toolkit flow and verifies "
            "toolkit-driven zip-input triage, extracted-folder triage, and latest-report reachability."
        ),
        "quiet_launcher": "launch_orin_support_bundle_triage_toolkit_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "support_bundle_triage_toolkit_validation"),
        "report_root": os.path.join(DEV_LOGS_DIR, "support_bundle_triage_toolkit_validation", "reports"),
        "report_prefix": "SupportBundleTriageToolkitValidationReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "diagnosticsReportIssueValidation": {
        "label": "Diagnostics Report Issue Validation",
        "detail": (
            "Runs the contained offscreen validator for the production diagnostics Report Issue flow "
            "and verifies support-bundle creation, manifest manual-submission contract fields, and "
            "GitHub issue-prefill open-attempt handling."
        ),
        "quiet_launcher": "launch_orin_diagnostics_report_issue_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "diagnostics_report_issue_validation"),
        "report_root": os.path.join(DEV_LOGS_DIR, "diagnostics_report_issue_validation", "reports"),
        "report_prefix": "DiagnosticsReportIssueValidationReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
    },
    "supportBundleTriage": {
        "label": "Support Bundle Triage Helper",
        "detail": (
            "Runs the raw FB-019 support-bundle triage helper against a selected support-bundle "
            ".zip or extracted bundle folder, then writes a compact internal triage report with "
            "the closest current repro lane suggestion."
        ),
        "quiet_launcher": "",
        "voice_launcher": "",
        "supports_voice": False,
        "available_modes": ("quiet",),
        "opens_window": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "support_bundle_triage"),
        "report_root": os.path.join(DEV_LOGS_DIR, "support_bundle_triage", "reports"),
        "report_prefix": "SupportBundleTriageReport_",
        "report_suffix": ".txt",
        "crash_folder": "",
        "requires_bundle_input": True,
        "script_path": SUPPORT_BUNDLE_TRIAGE_SCRIPT,
    },
}

CONFIG_LANE_GROUPS = (
    {
        "label": "Diagnostics & Recovery Checks",
        "lane_keys": ("diagnostics", "repeatedCrash", "startupAbort"),
    },
    {
        "label": "Boot & Transition Checks",
        "lane_keys": (
            "bootManualFlow",
            "bootAutoHandoffSkipImport",
            "bootTransitionVerification",
            "bootTransitionCapture",
            "bootMonitorPreflight",
            "bootToolkitValidation",
        ),
    },
    {
        "label": "Voice, Healthy Start, & Regression",
        "lane_keys": (
            "voiceRegression",
            "desktopHealthy",
            "launcherHealthy",
            "desktopToolkitValidation",
            "devToolkitSmokeValidation",
            "launcherRegression",
        ),
    },
    {
        "label": "Support Bundles & Reporting",
        "lane_keys": (
            "supportBundleTriageHarness",
            "supportBundleTriageToolkitValidation",
            "diagnosticsReportIssueValidation",
            "supportBundleTriage",
        ),
    },
)


def latest_file_matching(folder_path: str, prefix: str, suffix: str = "") -> str:
    if not os.path.isdir(folder_path):
        return ""
    best_path = ""
    best_time = -1.0
    for name in os.listdir(folder_path):
        if not name.lower().startswith(prefix.lower()):
            continue
        if suffix and not name.lower().endswith(suffix.lower()):
            continue
        path = os.path.join(folder_path, name)
        if not os.path.isfile(path):
            continue
        try:
            modified = os.path.getmtime(path)
        except OSError:
            continue
        if modified >= best_time:
            best_time = modified
            best_path = path
    return best_path


def matching_files(folder_path: str, prefix: str, suffix: str = "") -> list[str]:
    if not os.path.isdir(folder_path):
        return []

    matches = []
    for name in os.listdir(folder_path):
        if not name.lower().startswith(prefix.lower()):
            continue
        if suffix and not name.lower().endswith(suffix.lower()):
            continue
        path = os.path.join(folder_path, name)
        if not os.path.isfile(path):
            continue
        try:
            modified = os.path.getmtime(path)
        except OSError:
            continue
        matches.append((modified, path))
    matches.sort(key=lambda item: item[0], reverse=True)
    return [path for _modified, path in matches]


def latest_directory_named(root_path: str, folder_name: str) -> str:
    if not os.path.isdir(root_path):
        return ""

    best_path = ""
    best_time = -1.0
    for current_root, dir_names, _file_names in os.walk(root_path):
        for dir_name in dir_names:
            if dir_name.lower() != folder_name.lower():
                continue
            path = os.path.join(current_root, dir_name)
            try:
                modified = os.path.getmtime(path)
            except OSError:
                continue
            if modified >= best_time:
                best_time = modified
                best_path = path
    return best_path


def latest_subdirectory(root_path: str) -> str:
    if not os.path.isdir(root_path):
        return ""

    best_path = ""
    best_time = -1.0
    for name in os.listdir(root_path):
        path = os.path.join(root_path, name)
        if not os.path.isdir(path):
            continue
        try:
            modified = os.path.getmtime(path)
        except OSError:
            continue
        if modified >= best_time:
            best_time = modified
            best_path = path
    return best_path


BACKGROUND_PROGRESS_PROFILES = {
    "default": {
        "expected_seconds": 28.0,
        "stages": (
            (12, "Initializing the selected helper lane."),
            (34, "Launching the helper process and waiting for its first artifact."),
            (62, "Running the core validation or capture work."),
            (86, "Finalizing evidence and writing the latest artifact."),
            (96, "Waiting for the lane to finish cleanly."),
        ),
    },
    "bootMonitorPreflight": {
        "expected_seconds": 10.0,
        "stages": (
            (18, "Preparing the current monitor-topology probe."),
            (52, "Reading the left, center, and right monitor assumptions."),
            (82, "Writing the compact preflight report."),
            (96, "Waiting for the fresh report artifact to land."),
        ),
    },
    "bootTransitionVerification": {
        "expected_seconds": 24.0,
        "stages": (
            (12, "Preparing the quiet boot-to-desktop verification run."),
            (34, "Launching the boot harness and waiting for handoff markers."),
            (68, "Checking the handoff ordering against the expected milestone chain."),
            (88, "Writing the verification summary report."),
            (96, "Waiting for the fresh report artifact to land."),
        ),
    },
    "bootTransitionCapture": {
        "expected_seconds": 26.0,
        "stages": (
            (10, "Preparing the quiet auto-handoff capture lane."),
            (32, "Launching Boot ORIN and waiting for the transition window."),
            (70, "Capturing the handoff frames and saving the PNG sequence."),
            (90, "Writing the capture report and indexing the newest frame set."),
            (96, "Waiting for the fresh capture artifact to land."),
        ),
    },
    "bootToolkitValidation": {
        "expected_seconds": 24.0,
        "stages": (
            (10, "Preparing the boot-side Toolkit validation run."),
            (36, "Launching Boot Monitor Preflight through the Toolkit surface."),
            (68, "Launching Boot To Desktop Handoff Verification through the Toolkit surface."),
            (88, "Writing the consolidated boot-helper Toolkit validation report."),
            (96, "Waiting for the fresh report artifact to land."),
        ),
    },
    "desktopToolkitValidation": {
        "expected_seconds": 26.0,
        "stages": (
            (10, "Preparing the desktop-side Toolkit validation run."),
            (38, "Launching Healthy Desktop Launch Validation through the Toolkit surface."),
            (68, "Launching Healthy Launcher Path Validation through the Toolkit surface."),
            (88, "Writing the consolidated desktop-helper Toolkit validation report."),
            (96, "Waiting for the fresh report artifact to land."),
        ),
    },
    "devToolkitSmokeValidation": {
        "expected_seconds": 42.0,
        "stages": (
            (8, "Preparing the top-level Dev Toolkit smoke validation."),
            (28, "Running the boot-helper Toolkit validation."),
            (62, "Running the desktop-helper Toolkit validation."),
            (90, "Writing the consolidated smoke report."),
            (96, "Waiting for the fresh smoke artifact to land."),
        ),
    },
}


class TitleBar(QFrame):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.drag_active = False
        self.drag_pos = QPoint()
        self.setObjectName("titleBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)

        title = QLabel("NEXUS DESKTOP AI DEV TOOLKIT // INTERNAL")
        title.setObjectName("titleBarLabel")
        layout.addWidget(title, 1)

        minimize_btn = QPushButton("MIN")
        minimize_btn.setObjectName("titleBarButton")
        minimize_btn.clicked.connect(self.owner.showMinimized)
        layout.addWidget(minimize_btn)

        dismiss_btn = QPushButton("DISMISS")
        dismiss_btn.setObjectName("titleBarButton")
        dismiss_btn.clicked.connect(self.owner.close)
        layout.addWidget(dismiss_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = True
            self.drag_pos = event.globalPosition().toPoint() - self.owner.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_active and (event.buttons() & Qt.LeftButton):
            self.owner.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_active = False
        super().mouseReleaseEvent(event)


class Panel(QFrame):
    def __init__(self, title_text: str):
        super().__init__()
        self.setObjectName("panel")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(6)

        title = QLabel(title_text)
        title.setObjectName("panelTitle")
        self.layout.addWidget(title)


class GuardedComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.ClickFocus)

    def wheelEvent(self, event):
        if self.hasFocus() or self.view().isVisible() or self.view().hasFocus():
            super().wheelEvent(event)
            return
        event.accept()


class DevLauncherWindow(QWidget):
    def __init__(self, runtime_logger=None):
        super().__init__()
        self.runtime_logger = runtime_logger
        self.setWindowTitle("Nexus Desktop AI Dev Toolkit")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.resize(980, 900)
        self.setMinimumSize(840, 720)

        self._drag_active = False
        self._drag_pos = QPoint()
        self._resize_active = False
        self._resize_edges = set()
        self._resize_start_pos = QPoint()
        self._resize_start_geom = QRect()
        self._edge_margin = 8
        self.setMouseTracking(True)
        self._drag_source_widgets = []

        self.pending_launch_key = ""
        self.selected_lane_key = ""
        self.session_launch_records = {}
        self.previous_launch_entries = []
        self.active_background_run = {}
        self.selected_support_bundle_source = ""
        self.selected_support_bundle_source_kind = ""

        self.launch_timer = QTimer(self)
        self.launch_timer.setSingleShot(True)
        self.launch_timer.timeout.connect(self.run_selected_launcher)

        self.artifact_refresh_timer = QTimer(self)
        self.artifact_refresh_timer.timeout.connect(self.refresh_utility_buttons)
        self.artifact_refresh_timer.start(1000)

        self.setStyleSheet(
            """
            QWidget {
                background: #04080d;
                color: #6ee7ff;
                font-family: Consolas;
            }

            QFrame#shell {
                background: #061019;
                border: 1px solid #0fe1ff;
            }

            QFrame#titleBar {
                background: #07131b;
                border: 1px solid #0fe1ff;
            }

            QLabel#titleBarLabel {
                color: #9feeff;
                font-size: 10.5pt;
                font-weight: 700;
                letter-spacing: 1px;
            }

            QPushButton#titleBarButton {
                min-width: 72px;
                padding: 3px 8px;
                border: 1px solid #00d8ff;
                background: #0a1b26;
                color: #f4fbff;
                font-size: 9pt;
            }

            QPushButton#titleBarButton:hover {
                background: #133444;
            }

            QFrame#banner {
                border: 1px solid #0fe1ff;
                background: #07131b;
            }

            QLabel#bannerTop {
                color: #d4af37;
                font-size: 8.75pt;
                font-weight: 700;
                letter-spacing: 1px;
            }

            QLabel#bannerTitle {
                color: #d4af37;
                font-size: 18pt;
                font-weight: 700;
            }

            QLabel#bannerSubtitle {
                color: #ff4c4c;
                font-size: 9pt;
                font-weight: 700;
            }

            QFrame#panel {
                border: 1px solid #0fe1ff;
                background: #08131c;
            }

            QLabel#panelTitle {
                color: #d4af37;
                font-size: 11pt;
                font-weight: 700;
            }

            QLabel#fieldLabel {
                color: #7bffd5;
                font-size: 10pt;
                font-weight: 700;
            }

            QLabel#subsectionTitle {
                color: #ff4c4c;
                font-size: 10.5pt;
                font-weight: 700;
            }

            QPushButton, QComboBox {
                background: #0a1b26;
                border: 1px solid #00d8ff;
                border-radius: 6px;
                color: #f4fbff;
                padding: 8px 7px;
                font-size: 10pt;
            }

            QPushButton:hover, QComboBox:hover {
                background: #12303e;
            }

            QPushButton:disabled, QComboBox:disabled {
                color: #5e8994;
                border-color: #24606d;
                background: #071118;
            }

            QPushButton[checkable="true"] {
                text-align: left;
            }

            QPushButton:checked {
                background: #173847;
                border-color: #7fefff;
                color: #f0fdff;
            }

            QPushButton#utilityButton {
                font-size: 9.5pt;
                padding: 8px 6px;
            }

            QPushButton#headerUtilityButton {
                font-size: 8.75pt;
                padding: 5px 6px;
            }

            QLabel#detailBox, QLabel#noteBox, QLabel#statusBox {
                border: 1px solid #134353;
                background: #06111a;
                padding: 6px;
                color: #9fd7df;
                font-size: 8.75pt;
            }

            QLabel#statusBox {
                color: #d4af37;
            }

            QLabel#statusSubtext {
                color: #8cc6cf;
                font-size: 8pt;
                padding-left: 2px;
                padding-right: 2px;
            }

            QProgressBar#statusProgress {
                border: 1px solid #134353;
                background: #06111a;
                color: #d4af37;
                text-align: center;
                padding: 1px;
                font-size: 8pt;
                min-height: 16px;
            }

            QProgressBar#statusProgress::chunk {
                background: #0fe1ff;
                width: 12px;
            }

            QLabel#headerHint {
                color: #8cc6cf;
                font-size: 8pt;
                background: transparent;
                border: none;
                padding: 0px;
            }

            QLabel#modeLine {
                color: #8cc6cf;
                font-size: 8.5pt;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollBar:vertical {
                background: #031018;
                width: 12px;
                margin: 2px;
                border: 1px solid #00b8d9;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #00cfff;
                min-height: 24px;
                border-radius: 5px;
                border: 1px solid #7befff;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: transparent;
                height: 0px;
                border: none;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: #031018;
                border-radius: 4px;
            }

            QScrollBar:horizontal {
                background: #031018;
                height: 12px;
                margin: 2px;
                border: 1px solid #00b8d9;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #00cfff;
                min-width: 24px;
                border-radius: 5px;
                border: 1px solid #7befff;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: transparent;
                width: 0px;
                border: none;
            }

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: #031018;
                border-radius: 4px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        shell = QFrame()
        shell.setObjectName("shell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(14, 14, 14, 14)
        shell_layout.setSpacing(6)
        self.shell_frame = shell

        self.title_bar = TitleBar(self)
        self.title_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.title_bar.setMaximumHeight(42)
        shell_layout.addWidget(self.title_bar)

        banner = QFrame()
        banner.setObjectName("banner")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(8, 6, 8, 6)
        banner_layout.setSpacing(1)
        self.banner_frame = banner

        banner_top = QLabel("NEXUS DESKTOP AI // INTERNAL TOOLING")
        banner_top.setObjectName("bannerTop")
        banner_top.setAlignment(Qt.AlignCenter)
        banner_layout.addWidget(banner_top)
        self.banner_top_label = banner_top

        banner_title = QLabel("DEV TOOLKIT")
        banner_title.setObjectName("bannerTitle")
        banner_title.setAlignment(Qt.AlignCenter)
        banner_layout.addWidget(banner_title)
        self.banner_title_label = banner_title

        banner_subtitle = QLabel("Manual validation launch surface")
        banner_subtitle.setObjectName("bannerSubtitle")
        banner_subtitle.setAlignment(Qt.AlignCenter)
        banner_layout.addWidget(banner_subtitle)
        self.banner_subtitle_label = banner_subtitle
        banner.setMaximumHeight(70)

        shell_layout.addWidget(banner)

        status_panel = Panel("Status")
        status_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        status_panel.layout.setContentsMargins(8, 8, 8, 8)
        status_panel.layout.setSpacing(4)
        self.status_label = QLabel("Ready.")
        self.status_label.setObjectName("statusBox")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_label.setMaximumHeight(26)
        status_panel.layout.addWidget(self.status_label)
        self.status_detail_label = QLabel("No background lane is running right now.")
        self.status_detail_label.setObjectName("statusSubtext")
        self.status_detail_label.setWordWrap(True)
        self.status_detail_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.status_detail_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        status_panel.layout.addWidget(self.status_detail_label)
        self.status_progress = QProgressBar()
        self.status_progress.setObjectName("statusProgress")
        self.status_progress.setRange(0, 100)
        self.status_progress.setValue(0)
        self.status_progress.setTextVisible(True)
        self.status_progress.setFormat("Idle")
        self.status_progress.setFixedHeight(18)
        status_panel.layout.addWidget(self.status_progress)
        self.status_panel = status_panel

        global_utils_panel = Panel("Global Utilities")
        global_utils_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        global_utils_panel.layout.setContentsMargins(8, 8, 8, 8)
        global_utils_panel.layout.setSpacing(4)
        self._build_global_utilities_panel(global_utils_panel.layout)
        self.global_utils_panel = global_utils_panel

        shell_layout.addWidget(global_utils_panel)
        shell_layout.addWidget(status_panel)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scroll_area = scroll
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        self.scroll_content = content

        current_launch_panel = Panel("Custom Launch")
        self._build_current_launch_group_panel(current_launch_panel.layout)
        content_layout.addWidget(current_launch_panel)

        previous_launch_panel = Panel("Previous Launches")
        self._build_previous_launch_group_panel(previous_launch_panel.layout)
        content_layout.addWidget(previous_launch_panel)

        uploads_panel = Panel("Uploads")
        self._build_support_bundle_intake_group_panel(uploads_panel.layout)
        content_layout.addWidget(uploads_panel)

        notes_panel = Panel("Notes")
        notes_label = QLabel(
            "- Custom Launch utilities only light up for evidence created by launches started in this Dev Toolkit session.\n"
            "- Previous Launches lets you reopen earlier dev evidence without mixing it into the active Custom Launch flow.\n"
            "- Global Utilities only open stable developer locations and never depend on the selected lane.\n"
            "- Dev Toolkit evidence writes under C:\\Jarvis\\dev\\logs lane roots instead of the active client-facing logs root.\n"
            "- Uploads stages a support-bundle zip or extracted folder and routes it into the existing Support Bundle Triage Helper."
        )
        notes_label.setObjectName("noteBox")
        notes_label.setWordWrap(True)
        notes_panel.layout.addWidget(notes_label)
        content_layout.addWidget(notes_panel)
        content_layout.addStretch(1)

        scroll.setWidget(content)
        shell_layout.addWidget(scroll, 1)
        root.addWidget(shell)

        self._install_background_drag_filters()

        self.center_on_primary()
        self.refresh_previous_launches()
        self.apply_group_section_widths()
        self.update_ui()

    def _build_configurable_panel(self, layout):
        launch_mode_label = QLabel("Launch Mode")
        launch_mode_label.setObjectName("fieldLabel")
        layout.addWidget(launch_mode_label)

        self.audio_label = QLabel("Choose whether this launch should stay quiet or run with live voice/audio.")
        self.audio_label.setObjectName("noteBox")
        self.audio_label.setWordWrap(True)
        self.audio_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.audio_label.setMaximumHeight(70)
        layout.addWidget(self.audio_label)

        self.audio_combo = GuardedComboBox()
        self.audio_combo.addItem("Choose a launch mode...", None)
        self.audio_combo.addItem("Quiet (No Audio / No Voice)", "quiet")
        self.audio_combo.addItem("With Voice / Audio", "voice")
        self.audio_combo.setMinimumWidth(0)
        self.audio_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_combo.currentIndexChanged.connect(self.on_launch_mode_changed)
        layout.addWidget(self.audio_combo)

        lane_group_label = QLabel("Purpose")
        lane_group_label.setObjectName("fieldLabel")
        layout.addWidget(lane_group_label)

        self.lane_group_combo = GuardedComboBox()
        self.lane_group_combo.setMinimumWidth(0)
        self.lane_group_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lane_group_combo.currentIndexChanged.connect(self.on_lane_group_changed)
        layout.addWidget(self.lane_group_combo)

        lane_choice_label = QLabel("Test / Helper")
        lane_choice_label.setObjectName("fieldLabel")
        layout.addWidget(lane_choice_label)

        self.lane_combo = GuardedComboBox()
        self.lane_combo.setMinimumWidth(0)
        self.lane_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lane_combo.currentIndexChanged.connect(self.on_lane_choice_changed)
        layout.addWidget(self.lane_combo)

        self.detail_label = QLabel()
        self.detail_label.setObjectName("detailBox")
        self.detail_label.setWordWrap(True)
        self.detail_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.detail_label.setMinimumHeight(96)
        self.detail_label.setMaximumHeight(145)
        layout.addWidget(self.detail_label)

        delay_label = QLabel("Launch Delay")
        delay_label.setObjectName("fieldLabel")
        layout.addWidget(delay_label)

        self.delay_combo = GuardedComboBox()
        self.delay_combo.addItem("Choose a launch delay...", None)
        self.delay_combo.addItem("Now", "Now")
        self.delay_combo.addItem("3s", "3s")
        self.delay_combo.addItem("5s", "5s")
        self.delay_combo.addItem("10s", "10s")
        self.delay_combo.setMinimumWidth(0)
        self.delay_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.delay_combo.currentIndexChanged.connect(self.update_ui)
        layout.addWidget(self.delay_combo)

        self.launch_btn = QPushButton("Launch Selected Lane")
        self.launch_btn.clicked.connect(self.schedule_or_launch)
        layout.addWidget(self.launch_btn)

        self.cancel_btn = QPushButton("Cancel Pending Launch")
        self.cancel_btn.clicked.connect(self.cancel_launch)
        layout.addWidget(self.cancel_btn)

        self.mode_line = QLabel()
        self.mode_line.setObjectName("modeLine")
        self.mode_line.setWordWrap(True)
        self.mode_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.mode_line)

        layout.addStretch(1)

        self.populate_lane_group_choices("")

    def _build_global_utilities_panel(self, layout):
        button_rows = (
            [
                ("Project Root", self.open_jarvis_root, "Open Project Root"),
                ("Dev Folder", self.open_dev_folder, "Open Dev Folder"),
                ("Dev Logs", self.open_dev_logs_root, "Open Dev Logs Root"),
                ("Latest Toolkit Log", self.open_latest_toolkit_session_log, "Open Latest Toolkit Session Log"),
            ],
            [
                ("Latest Smoke Report", self.open_latest_smoke_report, "Open Latest Dev Toolkit Smoke Report"),
                ("Latest Transition Capture", self.open_latest_transition_capture, "Open Latest Boot Transition Capture"),
                ("Dev Launchers", self.open_launchers_folder, "Open Dev Launchers Folder"),
            ],
        )
        for row_buttons in button_rows:
            button_row = QHBoxLayout()
            button_row.setContentsMargins(0, 0, 0, 0)
            button_row.setSpacing(6)
            button_row.addStretch(1)
            for text, handler, tooltip in row_buttons:
                btn = QPushButton(text)
                btn.setObjectName("headerUtilityButton")
                btn.clicked.connect(handler)
                btn.setToolTip(tooltip)
                btn.setMinimumWidth(132)
                btn.setFixedHeight(30)
                btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
                button_row.addWidget(btn)
            button_row.addStretch(1)
            layout.addLayout(button_row)

        note = QLabel(
            "Stable developer locations and newest top-level helper artifacts that never depend on the selected lane."
        )
        note.setObjectName("headerHint")
        note.setWordWrap(False)
        note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(note)

    def _create_group_subsection(self, title_text: str):
        frame = QFrame()
        frame.setObjectName("panel")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        inner_layout = QVBoxLayout(frame)
        inner_layout.setContentsMargins(12, 12, 12, 12)
        inner_layout.setSpacing(10)

        title = QLabel(title_text)
        title.setObjectName("subsectionTitle")
        title.setAlignment(Qt.AlignCenter)
        inner_layout.addWidget(title)
        return frame, inner_layout

    def _build_current_launch_group_panel(self, layout):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        launch_frame, launch_layout = self._create_group_subsection("Launch Settings")
        self._build_configurable_panel(launch_layout)
        self.current_launch_frame = launch_frame

        utils_frame, utils_layout = self._create_group_subsection("Launch Utilities")
        self._build_custom_utilities_panel(utils_layout)
        self.current_utils_frame = utils_frame

        row.addWidget(launch_frame, 1, Qt.AlignTop)
        row.addWidget(utils_frame, 0, Qt.AlignTop)
        layout.addLayout(row)

    def _build_previous_launch_group_panel(self, layout):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        launch_frame, launch_layout = self._create_group_subsection("Previous Launch Selection")
        self._build_previous_launches_panel(launch_layout)
        self.previous_launch_frame = launch_frame

        utils_frame, utils_layout = self._create_group_subsection("Previous Launch Utilities")
        self._build_previous_launch_utilities_panel(utils_layout)
        self.previous_utils_frame = utils_frame

        row.addWidget(launch_frame, 1, Qt.AlignTop)
        row.addWidget(utils_frame, 0, Qt.AlignTop)
        layout.addLayout(row)

    def _build_support_bundle_intake_group_panel(self, layout):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        intake_frame, intake_layout = self._create_group_subsection("Bundle Intake")
        self._build_support_bundle_intake_panel(intake_layout)
        self.support_bundle_intake_frame = intake_frame

        utils_frame, utils_layout = self._create_group_subsection("Bundle Utilities")
        self._build_support_bundle_intake_utilities_panel(utils_layout)
        self.support_bundle_intake_utils_frame = utils_frame

        row.addWidget(intake_frame, 1, Qt.AlignTop)
        row.addWidget(utils_frame, 0, Qt.AlignTop)
        layout.addLayout(row)

    def _build_custom_utilities_panel(self, layout):
        buttons = [
            ("Open Selected Evidence Root", self.open_selected_evidence_root, "selected_evidence_btn"),
            ("Open Latest Runtime Log", self.open_latest_runtime_log, "latest_runtime_btn"),
            ("Open Latest Report", self.open_latest_report, "latest_report_btn"),
            ("Open Latest Dev Crash Folder", self.open_selected_crash_folder, "selected_crash_btn"),
        ]
        for text, handler, attr_name in buttons:
            btn = QPushButton(text)
            btn.setObjectName("utilityButton")
            btn.clicked.connect(handler)
            setattr(self, attr_name, btn)
            layout.addWidget(btn)

        note = QLabel(
            "Custom Launch utilities follow the currently selected lane and only enable after that lane has evidence to open."
        )
        note.setObjectName("noteBox")
        note.setWordWrap(True)
        note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.custom_utilities_note_label = note
        layout.addWidget(note)
        layout.addStretch(1)

    def _build_previous_launches_panel(self, layout):
        load_label = QLabel("Load Previous Launches")
        load_label.setObjectName("fieldLabel")
        layout.addWidget(load_label)

        refresh_btn = QPushButton("Refresh Previous Launches")
        refresh_btn.clicked.connect(self.refresh_previous_launches)
        layout.addWidget(refresh_btn)

        self.previous_summary_label = QLabel("Scanning saved dev evidence...")
        self.previous_summary_label.setObjectName("noteBox")
        self.previous_summary_label.setWordWrap(True)
        self.previous_summary_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.previous_summary_label)

        previous_choice_label = QLabel("Previous Launch")
        previous_choice_label.setObjectName("fieldLabel")
        layout.addWidget(previous_choice_label)

        self.previous_launch_combo = GuardedComboBox()
        self.previous_launch_combo.setMinimumWidth(0)
        self.previous_launch_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.previous_launch_combo.currentIndexChanged.connect(self.on_previous_launch_changed)
        layout.addWidget(self.previous_launch_combo)

        self.previous_detail_label = QLabel()
        self.previous_detail_label.setObjectName("detailBox")
        self.previous_detail_label.setWordWrap(True)
        self.previous_detail_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.previous_detail_label.setMinimumHeight(104)
        self.previous_detail_label.setMaximumHeight(172)
        layout.addWidget(self.previous_detail_label)
        layout.addStretch(1)

    def _build_previous_launch_utilities_panel(self, layout):
        buttons = [
            ("Open Previous Evidence Root", self.open_previous_evidence_root, "previous_evidence_btn"),
            ("Open Previous Runtime Log", self.open_previous_runtime_log, "previous_runtime_btn"),
            ("Open Previous Report", self.open_previous_report, "previous_report_btn"),
            ("Open Previous Crash Folder", self.open_previous_crash_folder, "previous_crash_btn"),
        ]
        for text, handler, attr_name in buttons:
            btn = QPushButton(text)
            btn.setObjectName("utilityButton")
            btn.clicked.connect(handler)
            setattr(self, attr_name, btn)
            layout.addWidget(btn)

        note = QLabel(
            "Previous Launch utilities reopen older dev evidence after you choose a saved launch entry."
        )
        note.setObjectName("noteBox")
        note.setWordWrap(True)
        note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.previous_utilities_note_label = note
        layout.addWidget(note)
        layout.addStretch(1)

    def _build_support_bundle_intake_panel(self, layout):
        selected_source_label = QLabel("Selected Source")
        selected_source_label.setObjectName("fieldLabel")
        layout.addWidget(selected_source_label)

        self.support_bundle_source_label = QLabel()
        self.support_bundle_source_label.setObjectName("detailBox")
        self.support_bundle_source_label.setWordWrap(True)
        self.support_bundle_source_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.support_bundle_source_label.setMinimumHeight(110)
        self.support_bundle_source_label.setMaximumHeight(178)
        layout.addWidget(self.support_bundle_source_label)

        picker_row = QHBoxLayout()
        picker_row.setContentsMargins(0, 0, 0, 0)
        picker_row.setSpacing(8)

        self.select_support_bundle_zip_btn = QPushButton("Select Zip")
        self.select_support_bundle_zip_btn.clicked.connect(self.select_support_bundle_zip)
        picker_row.addWidget(self.select_support_bundle_zip_btn, 1)

        self.select_support_bundle_folder_btn = QPushButton("Select Extracted Folder")
        self.select_support_bundle_folder_btn.clicked.connect(self.select_support_bundle_folder)
        picker_row.addWidget(self.select_support_bundle_folder_btn, 1)

        layout.addLayout(picker_row)

        note = QLabel(
            "Pick a support-bundle .zip or an already extracted bundle folder. The selected source stays staged here until you clear it or choose another one."
        )
        note.setObjectName("noteBox")
        note.setWordWrap(True)
        note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.support_bundle_intake_note_label = note
        layout.addWidget(note)
        layout.addStretch(1)

    def _build_support_bundle_intake_utilities_panel(self, layout):
        buttons = [
            ("Run Support Bundle Triage", self.launch_selected_support_bundle_triage, "run_support_bundle_triage_btn"),
            ("Open Selected Source", self.open_selected_support_bundle_source, "open_selected_support_bundle_source_btn"),
            ("Clear Selected Source", self.clear_selected_support_bundle_source, "clear_selected_support_bundle_source_btn"),
        ]
        for text, handler, attr_name in buttons:
            btn = QPushButton(text)
            btn.setObjectName("utilityButton")
            btn.clicked.connect(handler)
            setattr(self, attr_name, btn)
            layout.addWidget(btn)

        note = QLabel(
            "This dev-only intake routes the staged source into the existing Support Bundle Triage Helper without changing production reporting behavior."
        )
        note.setObjectName("noteBox")
        note.setWordWrap(True)
        note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.support_bundle_utilities_note_label = note
        layout.addWidget(note)
        layout.addStretch(1)

    def _install_background_drag_filters(self):
        self._drag_source_widgets = [
            self.shell_frame,
            self.banner_frame,
            self.banner_top_label,
            self.banner_title_label,
            self.banner_subtitle_label,
            self.scroll_area.viewport(),
            self.scroll_content,
        ]
        for widget in self._drag_source_widgets:
            widget.installEventFilter(self)

    def _begin_window_drag(self, global_pos: QPoint) -> bool:
        self._drag_active = True
        self._drag_pos = global_pos - self.frameGeometry().topLeft()
        return True

    def _move_window_drag(self, global_pos: QPoint) -> bool:
        if not self._drag_active:
            return False
        self.move(global_pos - self._drag_pos)
        return True

    def _end_window_drag(self):
        self._drag_active = False

    def _is_background_drag_zone(self, source, local_pos: QPoint) -> bool:
        if source is None:
            return False
        global_pos = source.mapToGlobal(local_pos)
        window_pos = self.mapFromGlobal(global_pos)
        if self._hit_test_edges(window_pos):
            return False

        if source in (self.banner_top_label, self.banner_title_label, self.banner_subtitle_label):
            return True

        child = source.childAt(local_pos)
        return child is None

    def current_lane_group(self) -> dict:
        groups = self.filtered_lane_groups()
        selected_group = self.lane_group_combo.currentData()
        if not groups or not selected_group:
            return {"label": "No Matching Lanes", "lane_keys": ()}
        for group in groups:
            if group["label"] == selected_group:
                return group
        return {"label": "No Matching Lanes", "lane_keys": ()}

    def filtered_lane_groups(self) -> list[dict]:
        selected_mode = self.audio_combo.currentData()
        if not selected_mode:
            return []
        groups = []
        for group in CONFIG_LANE_GROUPS:
            lane_keys = []
            for lane_key in group["lane_keys"]:
                lane = LANE_CONFIG[lane_key]
                if not self.lane_supports_mode(lane, selected_mode):
                    continue
                lane_keys.append(lane_key)
            if lane_keys:
                groups.append({"label": group["label"], "lane_keys": tuple(lane_keys)})
        return groups

    def populate_lane_group_choices(self, preferred_lane_key: str = ""):
        groups = self.filtered_lane_groups()
        self.lane_group_combo.blockSignals(True)
        self.lane_group_combo.clear()
        self.lane_group_combo.addItem("Choose a purpose...", None)
        preferred_group_index = 0
        for index, group in enumerate(groups):
            combo_index = index + 1
            self.lane_group_combo.addItem(group["label"], group["label"])
            if preferred_lane_key and preferred_lane_key in group["lane_keys"]:
                preferred_group_index = combo_index
        self.lane_group_combo.setCurrentIndex(preferred_group_index)
        self.lane_group_combo.blockSignals(False)
        self.populate_lane_choices(preferred_lane_key)

    def populate_lane_choices(self, preferred_lane_key: str = ""):
        group = self.current_lane_group()
        self.lane_combo.blockSignals(True)
        self.lane_combo.clear()
        self.lane_combo.addItem("Choose a test / helper...", None)
        preferred_index = 0
        for index, lane_key in enumerate(group["lane_keys"]):
            lane = LANE_CONFIG[lane_key]
            combo_index = index + 1
            self.lane_combo.addItem(lane["label"], lane_key)
            if lane_key == preferred_lane_key:
                preferred_index = combo_index
        self.lane_combo.setCurrentIndex(preferred_index)
        self.lane_combo.blockSignals(False)
        self.selected_lane_key = self.lane_combo.currentData() or ""
        self.update_ui()

    def on_lane_group_changed(self, *_args):
        self.populate_lane_choices()

    def on_launch_mode_changed(self, *_args):
        preferred_lane_key = self.current_lane_key()
        if not self.audio_combo.currentData():
            preferred_lane_key = ""
        self.populate_lane_group_choices(preferred_lane_key)

    def on_lane_choice_changed(self, *_args):
        lane_key = self.lane_combo.currentData()
        self.selected_lane_key = lane_key or ""
        self.update_ui()

    def current_lane_key(self) -> str:
        return self.selected_lane_key or ""

    def current_lane(self) -> dict:
        lane_key = self.current_lane_key()
        return LANE_CONFIG.get(lane_key, {})

    def has_current_lane_selection(self) -> bool:
        return bool(self.current_lane_key())

    def launch_delay_value(self) -> str:
        return self.delay_combo.currentData() or ""

    def launch_mode_value(self) -> str:
        return self.audio_combo.currentData() or ""

    def lane_available_modes(self, lane: dict) -> tuple[str, ...]:
        available = lane.get("available_modes", ())
        if available:
            return tuple(available)
        if lane.get("supports_voice", False):
            return ("quiet", "voice")
        return ("quiet",)

    def lane_supports_mode(self, lane: dict, mode: str) -> bool:
        if not lane or not mode:
            return False
        return mode in self.lane_available_modes(lane)

    def current_launch_ready(self) -> bool:
        return bool(
            self.launch_mode_value()
            and self.lane_group_combo.currentData()
            and self.current_lane_key()
            and self.launch_delay_value()
        )

    def voice_requested(self) -> bool:
        lane = self.current_lane()
        return (
            self.launch_mode_value() == "voice"
            and self.lane_supports_mode(lane, "voice")
            and bool(lane.get("voice_launcher"))
        )

    def current_launch_mode_key(self) -> str:
        lane = self.current_lane()
        selected_mode = self.launch_mode_value()
        if not lane or not selected_mode:
            return ""
        if self.lane_supports_mode(lane, selected_mode):
            return selected_mode
        available = self.lane_available_modes(lane)
        return available[0] if available else ""

    def current_session_artifact_key(self) -> str:
        lane_key = self.current_lane_key()
        mode_key = self.current_launch_mode_key()
        if not lane_key or not mode_key:
            return ""
        return f"{lane_key}::{mode_key}"

    def active_evidence_root(self) -> str:
        lane = self.current_lane()
        if not lane:
            return ""
        if self.voice_requested() and lane.get("log_root_with_voice"):
            return lane["log_root_with_voice"]
        return lane["log_root"]

    def active_report_root(self) -> str:
        lane = self.current_lane()
        return lane.get("report_root", "") if lane else ""

    def latest_runtime_log_for_record(self, record: dict, newer_than_ts: float = 0.0) -> str:
        fixed = record.get("runtime_fixed", "")
        if fixed and os.path.isfile(fixed):
            if newer_than_ts:
                try:
                    if os.path.getmtime(fixed) < newer_than_ts:
                        return ""
                except OSError:
                    return ""
            return fixed

        root = record.get("evidence_root", "")
        if not os.path.isdir(root):
            return ""
        latest = latest_file_matching(root, "Runtime_")
        if not latest or not newer_than_ts:
            return latest
        try:
            return latest if os.path.getmtime(latest) >= newer_than_ts else ""
        except OSError:
            return ""

    def latest_report_for_record(self, record: dict, newer_than_ts: float = 0.0) -> str:
        report_root = record.get("report_root", "")
        report_prefix = record.get("report_prefix", "")
        report_suffix = record.get("report_suffix", "")
        if not report_root or not report_prefix or not os.path.isdir(report_root):
            return ""
        latest = latest_file_matching(report_root, report_prefix, report_suffix)
        if not latest or not newer_than_ts:
            return latest
        try:
            return latest if os.path.getmtime(latest) >= newer_than_ts else ""
        except OSError:
            return ""

    def latest_crash_file_for_record(self, record: dict, newer_than_ts: float = 0.0) -> str:
        crash_folder = self.crash_folder_for_record(record)
        if not crash_folder:
            return ""
        latest = latest_file_matching(crash_folder, "Crash_")
        if not latest or not newer_than_ts:
            return latest
        try:
            return latest if os.path.getmtime(latest) >= newer_than_ts else ""
        except OSError:
            return ""

    def crash_folder_for_record(self, record: dict) -> str:
        crash_folder_name = record.get("crash_folder_name", "")
        evidence_root = record.get("evidence_root", "")
        if not crash_folder_name or not evidence_root:
            return ""
        path = os.path.join(evidence_root, crash_folder_name)
        if not os.path.isdir(path):
            return ""
        return path

    def current_session_record(self) -> dict:
        artifact_key = self.current_session_artifact_key()
        if not artifact_key:
            return {}
        return self.session_launch_records.get(artifact_key, {})

    def build_current_launch_record(self) -> dict:
        lane = self.current_lane()
        if not lane:
            return {}
        return {
            "artifact_key": self.current_session_artifact_key(),
            "lane_key": self.current_lane_key(),
            "lane_label": lane["label"],
            "mode_key": self.current_launch_mode_key(),
            "mode_label": self.audio_combo.currentText(),
            "evidence_root": self.active_evidence_root(),
            "runtime_fixed": lane.get("runtime_fixed", ""),
            "report_root": lane.get("report_root", ""),
            "report_prefix": lane.get("report_prefix", ""),
            "report_suffix": lane.get("report_suffix", ""),
            "crash_folder_name": lane.get("crash_folder", ""),
            "launched_at": datetime.datetime.now(),
            "launched_at_ts": datetime.datetime.now().timestamp(),
        }

    def latest_runtime_log_path(self) -> str:
        return self.latest_runtime_log_for_record(self.build_current_launch_record())

    def latest_report_path(self) -> str:
        return self.latest_report_for_record(self.build_current_launch_record())

    def selected_crash_folder_path(self) -> str:
        return self.crash_folder_for_record(self.build_current_launch_record())

    def active_launcher_filename(self) -> str:
        lane = self.current_lane()
        if not lane:
            return ""
        if self.voice_requested() and lane.get("voice_launcher"):
            return lane["voice_launcher"]
        return lane["quiet_launcher"]

    def active_label(self) -> str:
        lane = self.current_lane()
        if not lane:
            return "Selected lane"
        if self.voice_requested() and lane.get("supports_voice"):
            return lane["label"] + " With Voice"
        return lane["label"]

    def select_lane(self, lane_key: str):
        lane = LANE_CONFIG[lane_key]
        if self.launch_mode_value() and not self.lane_supports_mode(lane, self.launch_mode_value()):
            target_mode = self.lane_available_modes(lane)[0]
            self.audio_combo.blockSignals(True)
            self.audio_combo.setCurrentIndex(1 if target_mode == "quiet" else 2)
            self.audio_combo.blockSignals(False)
        elif not self.launch_mode_value():
            target_mode = self.lane_available_modes(lane)[0]
            self.audio_combo.blockSignals(True)
            self.audio_combo.setCurrentIndex(1 if target_mode == "quiet" else 2)
            self.audio_combo.blockSignals(False)
        self.populate_lane_group_choices(lane_key)

    def audio_mode_summary(self, lane: dict) -> str:
        available = self.lane_available_modes(lane)
        if available == ("voice",):
            return "With Voice / Audio only"
        if "voice" in available and "quiet" in available:
            return "Quiet or With Voice / Audio"
        return "Quiet only"

    def audio_mode_label_text(self, lane: dict) -> str:
        if lane.get("supports_voice", False):
            return "Audio Mode"
        return "Audio Mode (Quiet only for this lane)"

    def detail_text_for_lane(self, lane: dict) -> str:
        return (
            f"Lane: {lane['label']}\n"
            f"Purpose: {lane['detail']}\n"
            f"Audio Support: {self.audio_mode_summary(lane)}"
        )

    def update_mode_line(self, lane: dict):
        if not lane or not self.current_launch_ready():
            self.mode_line.setText(
                "Choose a launch mode, purpose, test / helper, and launch delay to enable the selected Custom Launch flow."
            )
            return
        selected_audio = self.audio_combo.currentText()
        self.mode_line.setText(
            f"Launch Mode: {selected_audio} | "
            f"Selected Group: {self.current_lane_group()['label']} | "
            f"Lane: {lane['label']} | "
            f"Delay: {self.delay_combo.currentText()}"
        )

    def compact_previous_mode_label(self, mode_label: str) -> str:
        if mode_label.startswith("Quiet"):
            return "Quiet"
        if "Voice" in mode_label or "Audio" in mode_label:
            return "Voice / Audio"
        return mode_label

    def compact_previous_timestamp(self, entry: dict) -> str:
        last_activity = entry.get("last_activity")
        if last_activity:
            return datetime.datetime.fromtimestamp(last_activity).strftime("%m-%d %I:%M %p")
        return "Unknown time"

    def previous_entry_run_tag(self, entry: dict) -> str:
        run_key = entry.get("run_key", "")
        if "::" not in run_key:
            return ""
        token = run_key.split("::", 1)[1]
        stamp = self.normalized_run_stamp(token)
        if token.startswith(stamp) and len(token) > len(stamp):
            return token[len(stamp):].strip("_")
        return ""

    def compact_previous_lane_label(self, lane_label: str) -> str:
        compact = lane_label
        for suffix in (" Validation", " Harness", " Helper", " Test", " Lane"):
            if compact.endswith(suffix):
                compact = compact[: -len(suffix)]
                break
        return compact

    def wrap_detail_value(self, value: str, width: int = 62) -> list[str]:
        normalized = value.replace("/", "\\")
        lines = []
        for raw_line in normalized.splitlines():
            if "\\" in raw_line:
                segments = raw_line.split("\\")
                tokens = []
                for index, segment in enumerate(segments):
                    token = segment
                    if index < len(segments) - 1:
                        token += "\\"
                    tokens.append(token)
                wrapped = []
                current = ""
                for token in tokens:
                    if current and len(current) + len(token) <= width:
                        current += token
                        continue
                    if current:
                        wrapped.append(current)
                    if len(token) <= width:
                        current = token
                        continue
                    token_lines = textwrap.wrap(
                        token,
                        width=width,
                        break_long_words=True,
                        break_on_hyphens=False,
                    )
                    wrapped.extend(token_lines[:-1])
                    current = token_lines[-1] if token_lines else ""
                if current:
                    wrapped.append(current)
            else:
                wrapped = textwrap.wrap(
                    raw_line,
                    width=width,
                    break_long_words=True,
                    break_on_hyphens=False,
                )
            lines.extend(wrapped or [""])
        return lines or [""]

    def append_wrapped_detail(self, lines: list[str], label: str, value: str, width: int = 62):
        lines.append(f"{label}:")
        wrapped_lines = self.wrap_detail_value(value, width=width)
        for wrapped_line in wrapped_lines:
            lines.append(f"  {wrapped_line}")

    def detail_wrap_width_for_label(self, label: QLabel, fallback: int = 62) -> int:
        metrics = QFontMetrics(label.font())
        average_char_width = max(1, metrics.averageCharWidth())
        usable_pixel_width = max(220, label.width() - 24)
        return max(34, usable_pixel_width // average_char_width)

    def previous_entry_summary(self, entry: dict) -> str:
        lane_label = self.compact_previous_lane_label(entry["lane_label"])
        mode_label = self.compact_previous_mode_label(entry["mode_label"])
        timestamp_text = self.compact_previous_timestamp(entry)
        run_tag = self.previous_entry_run_tag(entry)
        if run_tag:
            return f"{lane_label} | {mode_label} | {timestamp_text} #{run_tag}"
        return f"{lane_label} | {mode_label} | {timestamp_text}"

    def previous_entry_artifact_summary(self, entry: dict) -> str:
        parts = ["Evidence Root"]
        if entry.get("runtime_log"):
            parts.append("Runtime")
        if entry.get("report_path"):
            parts.append("Report")
        if entry.get("crash_folder"):
            parts.append("Crash Folder")
        return ", ".join(parts)

    def previous_entry_detail(self, entry: dict) -> str:
        wrap_width = self.detail_wrap_width_for_label(self.previous_detail_label)
        run_tag = self.previous_entry_run_tag(entry)
        lines = [
            f"Lane: {entry['lane_label']}",
            f"Mode: {self.compact_previous_mode_label(entry['mode_label'])}",
            f"Saved Evidence Time: {entry.get('timestamp_text', 'Unknown time')}",
            f"Artifacts Available: {self.previous_entry_artifact_summary(entry)}",
        ]
        if run_tag:
            lines.append(f"Run Tag: {run_tag}")
        self.append_wrapped_detail(lines, "Evidence Root", entry["evidence_root"], width=wrap_width)
        if entry.get("runtime_log"):
            self.append_wrapped_detail(lines, "Runtime", entry["runtime_log"], width=wrap_width)
        if entry.get("report_path"):
            self.append_wrapped_detail(lines, "Report", entry["report_path"], width=wrap_width)
        if entry.get("crash_folder"):
            self.append_wrapped_detail(lines, "Crash Folder", entry["crash_folder"], width=wrap_width)
        return "\n".join(lines)

    def lane_shows_runtime_button(self, lane_key: str) -> bool:
        return lane_key in {"diagnostics", "repeatedCrash", "startupAbort", "desktopHealthy", "launcherHealthy"}

    def lane_shows_report_button(self, lane: dict) -> bool:
        return bool(lane.get("report_root"))

    def lane_shows_crash_button(self, lane: dict) -> bool:
        return bool(lane.get("crash_folder"))

    def artifact_token_from_path(self, path: str, prefix: str, suffix: str = "") -> str:
        if not path:
            return ""
        name = os.path.basename(path)
        if name.lower().startswith(prefix.lower()):
            name = name[len(prefix):]
        if suffix and name.lower().endswith(suffix.lower()):
            name = name[: -len(suffix)]
        return name

    def normalized_run_stamp(self, token: str) -> str:
        if len(token) >= 15 and token[8:9] == "_" and token[:8].isdigit() and token[9:15].isdigit():
            return token[:15]
        return token

    def build_previous_history_entries(self, record: dict) -> list[dict]:
        entries = []
        evidence_root = record.get("evidence_root", "")
        report_root = record.get("report_root", "")
        report_prefix = record.get("report_prefix", "")
        report_suffix = record.get("report_suffix", "")
        crash_folder_name = record.get("crash_folder_name", "")

        runtime_paths = matching_files(evidence_root, "Runtime_", ".txt")
        crash_root = os.path.join(evidence_root, crash_folder_name) if crash_folder_name else ""
        crash_paths = matching_files(crash_root, "Crash_", ".txt")
        report_paths = matching_files(report_root, report_prefix, report_suffix) if report_root and report_prefix else []

        crash_by_token = {
            self.artifact_token_from_path(path, "Crash_", ".txt"): path
            for path in crash_paths
        }
        reports_by_stamp = {}
        for path in report_paths:
            report_token = self.artifact_token_from_path(path, report_prefix, report_suffix)
            report_stamp = self.normalized_run_stamp(report_token)
            reports_by_stamp.setdefault(report_stamp, []).append(path)

        used_reports = set()
        for runtime_path in runtime_paths:
            runtime_token = self.artifact_token_from_path(runtime_path, "Runtime_", ".txt")
            runtime_stamp = self.normalized_run_stamp(runtime_token)
            report_path = ""
            for candidate in reports_by_stamp.get(runtime_stamp, []):
                if candidate in used_reports:
                    continue
                report_path = candidate
                used_reports.add(candidate)
                break

            crash_path = crash_by_token.get(runtime_token, "")
            artifact_times = []
            for path in (runtime_path, report_path, crash_path):
                if not path:
                    continue
                try:
                    artifact_times.append(os.path.getmtime(path))
                except OSError:
                    continue
            if not artifact_times:
                continue

            best_time = max(artifact_times)
            entries.append(
                {
                    **record,
                    "runtime_log": runtime_path,
                    "report_path": report_path,
                    "crash_folder": crash_root if crash_path and os.path.isdir(crash_root) else "",
                    "last_activity": best_time,
                    "timestamp_text": datetime.datetime.fromtimestamp(best_time).strftime("%Y-%m-%d %I:%M:%S %p"),
                    "run_key": f"runtime::{runtime_token}",
                }
            )

        fixed_runtime = record.get("runtime_fixed", "")
        if fixed_runtime and fixed_runtime not in runtime_paths and os.path.isfile(fixed_runtime):
            try:
                fixed_time = os.path.getmtime(fixed_runtime)
            except OSError:
                fixed_time = 0.0
            if fixed_time:
                entries.append(
                    {
                        **record,
                        "runtime_log": fixed_runtime,
                        "report_path": "",
                        "crash_folder": "",
                        "last_activity": fixed_time,
                        "timestamp_text": datetime.datetime.fromtimestamp(fixed_time).strftime("%Y-%m-%d %I:%M:%S %p"),
                        "run_key": f"fixed::{os.path.basename(fixed_runtime)}",
                    }
                )

        for report_path in report_paths:
            if report_path in used_reports:
                continue
            try:
                report_time = os.path.getmtime(report_path)
            except OSError:
                continue
            report_token = self.artifact_token_from_path(report_path, report_prefix, report_suffix)
            entries.append(
                {
                    **record,
                    "runtime_log": "",
                    "report_path": report_path,
                    "crash_folder": "",
                    "last_activity": report_time,
                    "timestamp_text": datetime.datetime.fromtimestamp(report_time).strftime("%Y-%m-%d %I:%M:%S %p"),
                    "run_key": f"report::{report_token}",
                }
            )

        return entries

    def utility_section_target_width(self) -> int:
        base_width = 268
        max_width = 332
        growth_start = 1180
        current_width = self.width()
        if current_width <= growth_start:
            return base_width
        growth = (current_width - growth_start) // 5
        return min(max_width, base_width + growth)

    def required_utility_section_width(self) -> int:
        button_widths = []
        for attr_name in (
            "selected_evidence_btn",
            "latest_runtime_btn",
            "latest_report_btn",
            "selected_crash_btn",
            "previous_evidence_btn",
            "previous_runtime_btn",
            "previous_report_btn",
            "previous_crash_btn",
            "run_support_bundle_triage_btn",
            "open_selected_support_bundle_source_btn",
            "clear_selected_support_bundle_source_btn",
        ):
            button = getattr(self, attr_name, None)
            if not button:
                continue
            button_widths.append(button.sizeHint().width())

        if not button_widths:
            return 300
        return max(button_widths) + 26

    def apply_group_section_widths(self):
        target_width = max(self.utility_section_target_width(), self.required_utility_section_width())
        for attr_name in (
            "current_utils_frame",
            "previous_utils_frame",
            "support_bundle_intake_utils_frame",
        ):
            frame = getattr(self, attr_name, None)
            if not frame:
                continue
            frame.setMinimumWidth(target_width)
            frame.setMaximumWidth(target_width)
            frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)

        for attr_name in (
            "current_launch_frame",
            "previous_launch_frame",
            "support_bundle_intake_frame",
        ):
            frame = getattr(self, attr_name, None)
            if not frame:
                continue
            frame.setMinimumWidth(0)
            frame.setMaximumWidth(16777215)
            frame.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)

    def scan_previous_launch_entries(self) -> list[dict]:
        entries = []
        for lane_key, lane in LANE_CONFIG.items():
            candidates = []
            available_modes = self.lane_available_modes(lane)
            if "quiet" in available_modes and lane.get("log_root"):
                candidates.append(("quiet", lane.get("log_root", ""), "Quiet (No Audio / No Voice)"))
            if "voice" in available_modes:
                voice_root = lane.get("log_root_with_voice") or lane.get("log_root", "")
                if voice_root:
                    candidates.append(("voice", voice_root, "With Voice / Audio"))

            for mode_key, evidence_root, mode_label in candidates:
                if not evidence_root:
                    continue
                runtime_fixed = lane.get("runtime_fixed", "")
                record = {
                    "lane_key": lane_key,
                    "lane_label": lane["label"],
                    "mode_key": mode_key,
                    "mode_label": mode_label,
                    "evidence_root": evidence_root,
                    "runtime_fixed": runtime_fixed if mode_key == "quiet" else "",
                    "report_root": lane.get("report_root", ""),
                    "report_prefix": lane.get("report_prefix", ""),
                    "report_suffix": lane.get("report_suffix", ""),
                    "crash_folder_name": lane.get("crash_folder", ""),
                }

                entries.extend(self.build_previous_history_entries(record))

        entries.sort(key=lambda entry: entry["last_activity"], reverse=True)
        return entries

    def update_previous_summary(self):
        if not hasattr(self, "previous_summary_label"):
            return

        entry_count = len(self.previous_launch_entries)
        if not entry_count:
            self.previous_summary_label.setText(
                "No saved previous launches were found yet under the current dev evidence roots."
            )
            return

        lane_count = len({entry["lane_key"] for entry in self.previous_launch_entries})
        latest = self.previous_launch_entries[0]
        latest_mode = self.compact_previous_mode_label(latest["mode_label"])
        latest_time = latest.get("timestamp_text", "Unknown time")
        self.previous_summary_label.setText(
            f"Found {entry_count} saved launch artifact set(s) across {lane_count} lane(s). "
            f"Latest: {latest['lane_label']} | {latest_mode} | {latest_time}."
        )

    def refresh_previous_launches(self):
        self.previous_launch_entries = self.scan_previous_launch_entries()
        self.update_previous_summary()
        if not hasattr(self, "previous_launch_combo"):
            return

        previous_value = self.previous_launch_combo.currentData()
        self.previous_launch_combo.blockSignals(True)
        self.previous_launch_combo.clear()
        self.previous_launch_combo.addItem("Choose a previous launch...", None)
        selected_index = 0
        for index, entry in enumerate(self.previous_launch_entries, start=1):
            key = f"{entry['lane_key']}::{entry['mode_key']}::{entry.get('run_key', int(entry['last_activity']))}"
            summary = self.previous_entry_summary(entry)
            full_summary = (
                f"{entry['lane_label']} | {entry['mode_label']} | "
                f"{entry.get('timestamp_text', 'Unknown time')}"
            )
            self.previous_launch_combo.addItem(summary, key)
            self.previous_launch_combo.setItemData(index, full_summary, Qt.ToolTipRole)
            entry["combo_key"] = key
            if previous_value and key == previous_value:
                selected_index = index
        if selected_index == 0 and self.previous_launch_entries:
            selected_index = 1
        self.previous_launch_combo.setCurrentIndex(selected_index)
        self.previous_launch_combo.blockSignals(False)
        self.on_previous_launch_changed()

    def selected_previous_entry(self) -> dict:
        if not hasattr(self, "previous_launch_combo"):
            return {}
        combo_key = self.previous_launch_combo.currentData()
        if not combo_key:
            return {}
        for entry in self.previous_launch_entries:
            if entry.get("combo_key") == combo_key:
                return entry
        return {}

    def on_previous_launch_changed(self, *_args):
        entry = self.selected_previous_entry()
        if hasattr(self, "previous_detail_label"):
            if entry:
                self.previous_detail_label.setText(self.previous_entry_detail(entry))
                self.previous_launch_combo.setToolTip(
                    f"{entry['lane_label']} | {entry['mode_label']} | {entry.get('timestamp_text', 'Unknown time')}"
                )
            else:
                self.previous_detail_label.setText(
                    "Choose a previous launch entry to enable its evidence utilities."
                )
                self.previous_launch_combo.setToolTip("Choose a previous launch entry to reopen saved dev evidence.")
        self.refresh_utility_buttons()

    def update_ui(self):
        lane = self.current_lane()
        if lane:
            if self.launch_mode_value() and not self.lane_supports_mode(lane, self.launch_mode_value()):
                target_mode = self.lane_available_modes(lane)[0]
                self.audio_combo.blockSignals(True)
                self.audio_combo.setCurrentIndex(1 if target_mode == "quiet" else 2)
                self.audio_combo.blockSignals(False)
            self.detail_label.setText(self.detail_text_for_lane(lane))
            self.audio_label.setText(
                "Choose whether this launch should stay quiet or run with live voice/audio. "
                f"Current lane support: {self.audio_mode_summary(lane)}"
            )
        else:
            self.detail_label.setText(
                "Choose a launch mode, purpose, and test / helper to preview the lane details here."
            )
            self.audio_label.setText(
                "Choose whether this launch should stay quiet or run with live voice/audio."
            )

        self.apply_group_section_widths()
        self.update_mode_line(lane)
        self.launch_btn.setEnabled(self.current_launch_ready() and not self.launch_timer.isActive())
        self.cancel_btn.setEnabled(self.launch_timer.isActive())
        self.refresh_utility_buttons()

    def apply_status_widgets(self, text: str, detail: str, progress: int):
        progress_value = max(0, min(100, int(progress)))
        self.status_label.setText(text)
        self.status_detail_label.setText(detail)
        self.status_progress.setValue(progress_value)
        self.status_progress.setFormat("Idle" if progress_value <= 0 else f"{progress_value}%")

    def set_status(self, text: str, detail: str | None = None, progress: int | None = None):
        if detail is None:
            detail = (
                "A background lane is still running."
                if self.active_background_run
                else "No background lane is running right now."
            )
        if progress is None:
            progress = self.status_progress.value() if self.active_background_run else 0
        self.apply_status_widgets(text, detail, progress)
        self.refresh_utility_buttons()

    def runtime_milestone(self, event: str):
        if not callable(self.runtime_logger):
            return
        try:
            self.runtime_logger(event)
        except Exception:
            pass

    def lane_runs_in_background(self, lane: dict) -> bool:
        return bool(lane) and not lane.get("opens_window", False)

    def completion_artifact_for_record(self, record: dict) -> str:
        if not record:
            return ""
        cutoff = record.get("launched_at_ts", 0.0)
        report_path = self.latest_report_for_record(record, cutoff)
        if report_path:
            return report_path
        runtime_path = self.latest_runtime_log_for_record(record, cutoff)
        if runtime_path:
            return runtime_path
        return ""

    def background_progress_profile(self, lane_key: str) -> dict:
        return BACKGROUND_PROGRESS_PROFILES.get(lane_key, BACKGROUND_PROGRESS_PROFILES["default"])

    def background_progress_snapshot(self, run: dict, record: dict) -> tuple[int, str]:
        lane_key = record.get("lane_key", "")
        profile = self.background_progress_profile(lane_key)
        expected_seconds = max(1.0, float(profile.get("expected_seconds", 28.0)))
        started_at_ts = float(run.get("started_at_ts", record.get("launched_at_ts", time.time())))
        elapsed = max(0.0, time.time() - started_at_ts)
        progress_value = min(96, max(3, int((elapsed / expected_seconds) * 96)))
        detail = "Running the selected helper lane."
        for threshold, stage_text in profile.get("stages", ()):
            if progress_value <= threshold:
                detail = stage_text
                break
            detail = stage_text
        return progress_value, detail

    def refresh_background_run_status(self):
        run = self.active_background_run
        if not run:
            return

        record = self.session_launch_records.get(run.get("artifact_key", ""), {})
        if not record:
            self.active_background_run = {}
            return

        report_path = self.latest_report_for_record(record, record.get("launched_at_ts", 0.0))
        artifact_path = report_path or self.latest_runtime_log_for_record(record, record.get("launched_at_ts", 0.0))
        if artifact_path:
            artifact_label = "fresh report artifact" if report_path else "fresh runtime artifact"
            self.active_background_run = {}
            self.apply_status_widgets(
                f"Test complete: {run.get('label', 'Selected lane')}",
                f"Finished cleanly and wrote a {artifact_label}. You can open it from the utilities now.",
                100,
            )
            return

        progress_value, detail = self.background_progress_snapshot(run, record)
        self.apply_status_widgets(
            f"Test in progress: {run.get('label', 'Selected lane')}",
            detail,
            progress_value,
        )

    def refresh_utility_buttons(self):
        current_record = self.current_session_record()
        current_cutoff = current_record.get("launched_at_ts", 0.0) if current_record else 0.0
        current_lane = self.current_lane()
        has_lane_selection = bool(current_lane)

        if hasattr(self, "selected_evidence_btn"):
            evidence_root = current_record.get("evidence_root", "")
            evidence_exists = bool(current_record) and os.path.isdir(evidence_root)
            self.selected_evidence_btn.setVisible(has_lane_selection)
            self.selected_evidence_btn.setEnabled(evidence_exists)
            self.selected_evidence_btn.setToolTip(
                evidence_root
                if evidence_exists
                else "Run this Custom Launch in the current Dev Toolkit session to enable its evidence root."
            )

        if hasattr(self, "latest_runtime_btn"):
            runtime_path = self.latest_runtime_log_for_record(current_record, current_cutoff) if current_record else ""
            show_runtime = has_lane_selection and self.lane_shows_runtime_button(self.current_lane_key())
            self.latest_runtime_btn.setVisible(show_runtime)
            self.latest_runtime_btn.setEnabled(bool(runtime_path))
            self.latest_runtime_btn.setToolTip(
                runtime_path or "No current-session runtime log is available yet for the selected lane."
            )

        if hasattr(self, "latest_report_btn"):
            report_root = current_record.get("report_root", "")
            report_path = self.latest_report_for_record(current_record, current_cutoff) if current_record else ""
            supports_reports = bool(current_record and current_record.get("report_root"))
            show_report = has_lane_selection and self.lane_shows_report_button(current_lane)
            self.latest_report_btn.setVisible(show_report)
            self.latest_report_btn.setEnabled(bool(report_path))
            self.latest_report_btn.setToolTip(
                report_path
                if report_path
                else (
                    f"No report is available yet in: {report_root}"
                    if supports_reports
                    else "This lane has not produced a current-session report artifact yet."
                )
            )

        if hasattr(self, "selected_crash_btn"):
            crash_file = self.latest_crash_file_for_record(current_record, current_cutoff) if current_record else ""
            crash_path = self.crash_folder_for_record(current_record) if crash_file else ""
            crash_folder_name = current_record.get("crash_folder_name", "") if current_record else ""
            show_crash = has_lane_selection and self.lane_shows_crash_button(current_lane)
            self.selected_crash_btn.setVisible(show_crash)
            self.selected_crash_btn.setEnabled(bool(crash_path))
            self.selected_crash_btn.setToolTip(
                crash_path
                if crash_path
                else (
                    f"No current-session lane-local crash folder exists yet under: {current_record.get('evidence_root', '')}"
                    if crash_folder_name
                    else "This lane has not produced a current-session crash folder."
                )
            )
        if hasattr(self, "custom_utilities_note_label"):
            if not has_lane_selection:
                self.custom_utilities_note_label.setText(
                    "Choose a launch mode, purpose, and test / helper to reveal the utilities for that Custom Launch."
                )
            else:
                self.custom_utilities_note_label.setText(
                    "Custom Launch utilities follow the currently selected lane and only enable after that lane has evidence to open."
                )

        selected_bundle_path = self.selected_support_bundle_source
        selected_bundle_exists = self.support_bundle_source_exists()
        if hasattr(self, "support_bundle_source_label"):
            self.support_bundle_source_label.setText(self.support_bundle_source_detail_text())

        if hasattr(self, "run_support_bundle_triage_btn"):
            enabled = selected_bundle_exists and not self.launch_timer.isActive()
            self.run_support_bundle_triage_btn.setEnabled(enabled)
            if self.launch_timer.isActive():
                tooltip = "Cancel the pending delayed launch before routing a staged support bundle."
            elif selected_bundle_exists:
                tooltip = selected_bundle_path
            elif selected_bundle_path:
                tooltip = f"Selected source no longer exists: {selected_bundle_path}"
            else:
                tooltip = "Choose a support-bundle zip or extracted folder first."
            self.run_support_bundle_triage_btn.setToolTip(tooltip)

        if hasattr(self, "open_selected_support_bundle_source_btn"):
            self.open_selected_support_bundle_source_btn.setEnabled(selected_bundle_exists)
            self.open_selected_support_bundle_source_btn.setToolTip(
                selected_bundle_path
                if selected_bundle_exists
                else (
                    f"Selected source no longer exists: {selected_bundle_path}"
                    if selected_bundle_path
                    else "Choose a support-bundle zip or extracted folder to enable this utility."
                )
            )

        if hasattr(self, "clear_selected_support_bundle_source_btn"):
            self.clear_selected_support_bundle_source_btn.setEnabled(bool(selected_bundle_path))
            self.clear_selected_support_bundle_source_btn.setToolTip(
                selected_bundle_path or "No staged support-bundle source is selected right now."
            )

        if hasattr(self, "support_bundle_utilities_note_label"):
            if selected_bundle_exists:
                self.support_bundle_utilities_note_label.setText(
                    "The staged source is ready to route into the existing Support Bundle Triage Helper."
                )
            elif selected_bundle_path:
                self.support_bundle_utilities_note_label.setText(
                    "The staged source path is no longer available. Choose another zip or extracted bundle folder before running triage."
                )
            else:
                self.support_bundle_utilities_note_label.setText(
                    "Choose a support-bundle zip or extracted folder below to enable the triage route."
                )

        previous_entry = self.selected_previous_entry()
        if hasattr(self, "previous_evidence_btn"):
            previous_root = previous_entry.get("evidence_root", "")
            previous_exists = bool(previous_entry) and os.path.isdir(previous_root)
            self.previous_evidence_btn.setVisible(bool(previous_entry))
            self.previous_evidence_btn.setEnabled(previous_exists)
            self.previous_evidence_btn.setToolTip(
                previous_root
                if previous_exists
                else "Choose a previous launch entry with saved evidence."
            )

        if hasattr(self, "previous_runtime_btn"):
            previous_runtime = previous_entry.get("runtime_log", "")
            self.previous_runtime_btn.setVisible(bool(previous_runtime))
            self.previous_runtime_btn.setEnabled(bool(previous_runtime))
            self.previous_runtime_btn.setToolTip(
                previous_runtime or "No saved runtime log is available for the selected previous launch."
            )

        if hasattr(self, "previous_report_btn"):
            previous_report = previous_entry.get("report_path", "")
            self.previous_report_btn.setVisible(bool(previous_report))
            self.previous_report_btn.setEnabled(bool(previous_report))
            self.previous_report_btn.setToolTip(
                previous_report or "No saved report is available for the selected previous launch."
            )

        if hasattr(self, "previous_crash_btn"):
            previous_crash = previous_entry.get("crash_folder", "")
            self.previous_crash_btn.setVisible(bool(previous_crash))
            self.previous_crash_btn.setEnabled(bool(previous_crash))
            self.previous_crash_btn.setToolTip(
                previous_crash or "No saved crash folder is available for the selected previous launch."
            )
        if hasattr(self, "previous_utilities_note_label"):
            if previous_entry:
                self.previous_utilities_note_label.setText(
                    "Previous Launch utilities reopen the exact saved artifacts for the selected historical run."
                )
            else:
                self.previous_utilities_note_label.setText(
                    "Choose a previous launch entry to reveal its saved evidence utilities."
                )

        self.refresh_background_run_status()

    def schedule_or_launch(self):
        self.cancel_launch(silent=True)
        if not self.current_launch_ready():
            self.set_status("Choose a launch mode, purpose, test / helper, and launch delay before launching.")
            return
        delay_text = self.launch_delay_value()
        if delay_text == "Now":
            self.run_selected_launcher()
            return

        delay_seconds = int(delay_text.rstrip("s"))
        self.pending_launch_key = self.current_lane_key()
        self.launch_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.launch_timer.start(delay_seconds * 1000)
        self.set_status(
            f"Launching {self.active_label()} in {delay_seconds} second(s)...",
            "Waiting for the launch delay to elapse before the selected lane starts.",
            0,
        )

    def cancel_launch(self, silent: bool = False):
        if self.launch_timer.isActive():
            self.launch_timer.stop()
        self.pending_launch_key = ""
        self.launch_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if not silent:
            self.set_status("Pending launch cancelled.", "No background lane is running right now.", 0)

    def run_selected_launcher(self):
        try:
            lane = self.current_lane()
            lane_key = self.current_lane_key()
            mode_key = self.current_launch_mode_key()
            lane_label = lane.get("label", "Unknown lane")
            if lane.get("requires_bundle_input"):
                source_path = self.selected_support_bundle_source if self.support_bundle_source_exists() else ""
                if self.selected_support_bundle_source and not source_path:
                    self.clear_selected_support_bundle_source(announce=False)
                if not source_path:
                    source_path = self.select_support_bundle_source()
                if not source_path:
                    self.runtime_milestone(
                        f"TOOLKIT_MAIN|LANE_LAUNCH_CANCELLED|lane={lane_key}|mode={mode_key}|reason=no_source_selected"
                    )
                    self.set_status("Launch cancelled: no support bundle selected.")
                    return
                launch_key = self.launch_bundle_input_lane(
                    lane=lane,
                    lane_key=lane_key,
                    mode_key=mode_key,
                    lane_label=lane_label,
                    source_path=source_path,
                )
                return

            launcher_path = os.path.join(DEV_LAUNCHERS_DIR, self.active_launcher_filename())
            launch_key = self.current_session_artifact_key()
            self.session_launch_records[launch_key] = self.build_current_launch_record()
            if self.lane_runs_in_background(lane):
                self.active_background_run = {
                    "artifact_key": launch_key,
                    "label": self.active_label(),
                    "started_at_ts": time.time(),
                }
            subprocess.Popen(["wscript.exe", launcher_path], cwd=DEV_LAUNCHERS_DIR)
            self.runtime_milestone(
                f"TOOLKIT_MAIN|LANE_LAUNCHED|lane={lane_key}|mode={mode_key}|label={lane_label}"
            )
            if self.lane_runs_in_background(lane):
                self.set_status(
                    f"Test in progress: {self.active_label()}",
                    "Launching the selected helper lane and waiting for its first artifact.",
                    3,
                )
            else:
                self.set_status(f"Launched: {self.active_label()}")
        except Exception as exc:
            if 'launch_key' in locals():
                self.session_launch_records.pop(launch_key, None)
            self.active_background_run = {}
            self.runtime_milestone(
                f"TOOLKIT_MAIN|LANE_LAUNCH_FAILED|lane={self.current_lane_key()}|mode={self.current_launch_mode_key()}|reason={type(exc).__name__}"
            )
            self.set_status(f"Launch failed: {self.active_label()} :: {exc}")
        finally:
            self.launch_timer.stop()
            self.launch_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)

    def select_support_bundle_source(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Support Bundle Zip",
            self.support_bundle_dialog_root(),
            "Support Bundle Zip (*.zip);;All Files (*)",
        )
        if file_path:
            return self.remember_support_bundle_source(file_path, "zip")

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Extracted Support Bundle Folder",
            self.support_bundle_dialog_root(),
        )
        if folder_path:
            return self.remember_support_bundle_source(folder_path, "folder")
        return ""

    def support_bundle_dialog_root(self) -> str:
        selected_source = self.selected_support_bundle_source
        if selected_source:
            if os.path.isdir(selected_source):
                return selected_source
            parent = os.path.dirname(selected_source)
            if os.path.isdir(parent):
                return parent
        return CLIENT_LOGS_DIR

    def support_bundle_source_exists(self) -> bool:
        return bool(self.selected_support_bundle_source) and os.path.exists(self.selected_support_bundle_source)

    def support_bundle_source_kind_label(self) -> str:
        if self.selected_support_bundle_source_kind == "zip":
            return "Zip Archive"
        if self.selected_support_bundle_source_kind == "folder":
            return "Extracted Folder"
        if self.selected_support_bundle_source.lower().endswith(".zip"):
            return "Zip Archive"
        if os.path.isdir(self.selected_support_bundle_source):
            return "Extracted Folder"
        return "Bundle Source"

    def support_bundle_source_detail_text(self) -> str:
        source_path = self.selected_support_bundle_source
        if not source_path:
            return (
                "No support-bundle source is staged yet.\n"
                "Choose a .zip archive or an extracted bundle folder here, then route it into Support Bundle Triage."
            )
        status_text = "Ready" if self.support_bundle_source_exists() else "Missing"
        return (
            f"Type: {self.support_bundle_source_kind_label()}\n"
            f"Status: {status_text}\n"
            f"Path:\n{source_path}"
        )

    def remember_support_bundle_source(self, source_path: str, source_kind: str, status_message: str = "") -> str:
        if not source_path:
            return ""
        normalized = os.path.abspath(source_path)
        self.selected_support_bundle_source = normalized
        self.selected_support_bundle_source_kind = source_kind
        self.refresh_utility_buttons()
        if status_message:
            self.set_status(status_message)
        return normalized

    def clear_selected_support_bundle_source(self, *args, announce: bool = True):
        if not self.selected_support_bundle_source and not self.selected_support_bundle_source_kind:
            if announce:
                self.set_status("No staged support bundle source is selected right now.")
            return
        self.selected_support_bundle_source = ""
        self.selected_support_bundle_source_kind = ""
        self.refresh_utility_buttons()
        if announce:
            self.set_status("Cleared staged support bundle source.")

    def select_support_bundle_zip(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Support Bundle Zip",
            self.support_bundle_dialog_root(),
            "Support Bundle Zip (*.zip);;All Files (*)",
        )
        if not file_path:
            return
        self.remember_support_bundle_source(
            file_path,
            "zip",
            f"Selected support bundle zip: {os.path.abspath(file_path)}",
        )

    def select_support_bundle_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Extracted Support Bundle Folder",
            self.support_bundle_dialog_root(),
        )
        if not folder_path:
            return
        self.remember_support_bundle_source(
            folder_path,
            "folder",
            f"Selected extracted support bundle folder: {os.path.abspath(folder_path)}",
        )

    def launch_bundle_input_lane(self, lane: dict, lane_key: str, mode_key: str, lane_label: str, source_path: str) -> str:
        source_path = os.path.abspath(source_path)
        launch_key = self.current_session_artifact_key()
        self.session_launch_records[launch_key] = self.build_current_launch_record()
        if self.lane_runs_in_background(lane):
            self.active_background_run = {
                "artifact_key": launch_key,
                "label": self.active_label(),
                "started_at_ts": time.time(),
            }
        subprocess.Popen([PYTHONW_PATH, lane["script_path"], source_path], cwd=ROOT_DIR)
        self.runtime_milestone(
            f"TOOLKIT_MAIN|LANE_LAUNCHED|lane={lane_key}|mode={mode_key}|label={lane_label}"
        )
        if self.lane_runs_in_background(lane):
            self.set_status(
                f"Test in progress: {self.active_label()} :: {source_path}",
                "Launching the selected helper lane with the chosen support bundle source.",
                3,
            )
        else:
            self.set_status(f"Launched: {self.active_label()} :: {source_path}")
        return launch_key

    def launch_selected_support_bundle_triage(self):
        if self.launch_timer.isActive():
            self.set_status("Cancel the pending delayed launch before routing a staged support bundle.")
            return
        if self.selected_support_bundle_source and not self.support_bundle_source_exists():
            self.set_status(f"Selected support bundle source not found: {self.selected_support_bundle_source}")
            return
        if not self.selected_support_bundle_source:
            self.set_status("Choose a support-bundle zip or extracted folder first.")
            return

        self.select_lane("supportBundleTriage")
        lane = self.current_lane()
        lane_key = self.current_lane_key()
        mode_key = self.current_launch_mode_key()
        lane_label = lane.get("label", "Support Bundle Triage Helper")
        launch_key = ""
        try:
            launch_key = self.launch_bundle_input_lane(
                lane=lane,
                lane_key=lane_key,
                mode_key=mode_key,
                lane_label=lane_label,
                source_path=self.selected_support_bundle_source,
            )
        except Exception as exc:
            if launch_key:
                self.session_launch_records.pop(launch_key, None)
            self.active_background_run = {}
            self.runtime_milestone(
                f"TOOLKIT_MAIN|LANE_LAUNCH_FAILED|lane={lane_key}|mode={mode_key}|reason={type(exc).__name__}"
            )
            self.set_status(f"Launch failed: {lane_label} :: {exc}")

    def open_selected_support_bundle_source(self):
        source_path = self.selected_support_bundle_source
        if not source_path:
            self.set_status("No staged support bundle source is selected right now.")
            return
        if not os.path.exists(source_path):
            self.set_status(f"Selected support bundle source not found: {source_path}")
            return
        self.open_path(source_path, f"Opened selected support bundle source: {source_path}")

    def open_jarvis_root(self):
        self.open_path(ROOT_DIR, f"Opened: Project root :: {ROOT_DIR}")

    def open_dev_folder(self):
        self.open_path(DEV_DIR, f"Opened: Dev folder :: {DEV_DIR}")

    def open_dev_logs_root(self):
        os.makedirs(DEV_LOGS_DIR, exist_ok=True)
        self.open_path(DEV_LOGS_DIR, f"Opened: Dev logs root :: {DEV_LOGS_DIR}")

    def open_latest_toolkit_session_log(self):
        latest = latest_file_matching(DEV_TOOLKIT_SESSION_LOG_DIR, "Runtime_")
        if not latest:
            self.set_status(f"No toolkit session log found yet in: {DEV_TOOLKIT_SESSION_LOG_DIR}")
            return
        self.open_path(latest, f"Opened latest toolkit session log: {latest}")

    def open_latest_smoke_report(self):
        latest = latest_file_matching(DEV_TOOLKIT_SMOKE_REPORT_DIR, "DevToolkitSmokeValidationReport_", ".txt")
        if not latest:
            self.set_status(f"No smoke report found yet in: {DEV_TOOLKIT_SMOKE_REPORT_DIR}")
            return
        self.open_path(latest, f"Opened latest smoke report: {latest}")

    def open_latest_transition_capture(self):
        latest_capture = latest_subdirectory(BOOT_TRANSITION_CAPTURE_FRAMES_DIR)
        if latest_capture:
            self.open_path(latest_capture, f"Opened latest transition capture: {latest_capture}")
            return
        latest_report = latest_file_matching(BOOT_TRANSITION_CAPTURE_REPORT_DIR, "BootTransitionCaptureReport_", ".txt")
        if latest_report:
            self.open_path(latest_report, f"Opened latest transition capture report: {latest_report}")
            return
        self.set_status(
            f"No transition capture artifact found yet under: {BOOT_TRANSITION_CAPTURE_ROOT}"
        )

    def open_launchers_folder(self):
        self.open_path(DEV_LAUNCHERS_DIR, "Opened: Dev launchers folder")

    def open_selected_evidence_root(self):
        record = self.current_session_record()
        root = record.get("evidence_root", "")
        if not os.path.isdir(root):
            self.set_status(f"Selected evidence root not found yet: {root}")
            return
        self.open_path(root, f"Opened selected evidence root: {root}")

    def open_latest_runtime_log(self):
        record = self.current_session_record()
        latest = self.latest_runtime_log_for_record(record, record.get("launched_at_ts", 0.0)) if record else ""
        if not latest:
            root = record.get("evidence_root", self.active_evidence_root())
            if record and record.get("runtime_fixed"):
                self.set_status("No diagnostics runtime log found yet.")
                return
            self.set_status(f"No runtime log found yet in: {root}")
            return
        self.open_path(latest, f"Opened latest runtime log: {latest}")

    def open_latest_report(self):
        record = self.current_session_record()
        report_root = record.get("report_root", "")
        if not report_root:
            lane = self.current_lane()
            lane_label = lane.get("label", "Selected lane")
            self.set_status(f"{lane_label} does not produce a report artifact.")
            return
        latest = self.latest_report_for_record(record, record.get("launched_at_ts", 0.0))
        if not latest:
            self.set_status(f"No report found yet in: {report_root}")
            return
        self.open_path(latest, f"Opened latest report: {latest}")

    def open_selected_crash_folder(self):
        record = self.current_session_record()
        crash_file = self.latest_crash_file_for_record(record, record.get("launched_at_ts", 0.0)) if record else ""
        crash_path = self.crash_folder_for_record(record) if crash_file else ""
        lane = self.current_lane()
        lane_label = lane.get("label", "Selected lane")
        if not crash_path:
            crash_folder_name = record.get("crash_folder_name", "") if record else ""
            if not crash_folder_name:
                self.set_status(f"{lane_label} does not use a lane-local crash folder.")
                return
            self.set_status(f"Crash folder not found yet: {os.path.join(record.get('evidence_root', self.active_evidence_root()), crash_folder_name)}")
            return
        self.open_path(
            crash_path,
            f"Opened latest dev crash folder for {lane_label}: {crash_path}",
        )

    def open_previous_evidence_root(self):
        entry = self.selected_previous_entry()
        path = entry.get("evidence_root", "")
        if not path or not os.path.isdir(path):
            self.set_status("No previous evidence root is available for the selected entry.")
            return
        self.open_path(path, f"Opened previous evidence root: {path}")

    def open_previous_runtime_log(self):
        entry = self.selected_previous_entry()
        path = entry.get("runtime_log", "")
        if not path or not os.path.isfile(path):
            self.set_status("No previous runtime log is available for the selected entry.")
            return
        self.open_path(path, f"Opened previous runtime log: {path}")

    def open_previous_report(self):
        entry = self.selected_previous_entry()
        path = entry.get("report_path", "")
        if not path or not os.path.isfile(path):
            self.set_status("No previous report is available for the selected entry.")
            return
        self.open_path(path, f"Opened previous report: {path}")

    def open_previous_crash_folder(self):
        entry = self.selected_previous_entry()
        path = entry.get("crash_folder", "")
        if not path or not os.path.isdir(path):
            self.set_status("No previous crash folder is available for the selected entry.")
            return
        self.open_path(path, f"Opened previous crash folder: {path}")

    def open_path(self, path: str, success_message: str):
        try:
            os.startfile(path)
            self.set_status(success_message)
        except Exception as exc:
            self.set_status(f"Open failed: {path} :: {exc}")

    def center_on_primary(self):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)

    def _hit_test_edges(self, pos):
        rect = self.rect()
        x = pos.x()
        y = pos.y()
        margin = self._edge_margin
        edges = set()

        if x <= margin:
            edges.add("left")
        elif x >= rect.width() - margin:
            edges.add("right")

        if y <= margin:
            edges.add("top")
        elif y >= rect.height() - margin:
            edges.add("bottom")

        return edges

    def _apply_cursor_for_edges(self, edges):
        if {"left", "top"} <= edges or {"right", "bottom"} <= edges:
            self.setCursor(Qt.SizeFDiagCursor)
        elif {"right", "top"} <= edges or {"left", "bottom"} <= edges:
            self.setCursor(Qt.SizeBDiagCursor)
        elif "left" in edges or "right" in edges:
            self.setCursor(Qt.SizeHorCursor)
        elif "top" in edges or "bottom" in edges:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def _resize_geometry(self, global_pos):
        delta = global_pos - self._resize_start_pos
        rect = QRect(self._resize_start_geom)

        if "left" in self._resize_edges:
            new_left = rect.left() + delta.x()
            max_left = rect.right() - self.minimumWidth()
            rect.setLeft(min(new_left, max_left))

        if "right" in self._resize_edges:
            new_width = max(self.minimumWidth(), rect.width() + delta.x())
            rect.setWidth(new_width)

        if "top" in self._resize_edges:
            new_top = rect.top() + delta.y()
            max_top = rect.bottom() - self.minimumHeight()
            rect.setTop(min(new_top, max_top))

        if "bottom" in self._resize_edges:
            new_height = max(self.minimumHeight(), rect.height() + delta.y())
            rect.setHeight(new_height)

        self.setGeometry(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edges = self._hit_test_edges(event.position().toPoint())
            if edges:
                self._resize_active = True
                self._resize_edges = edges
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geom = self.geometry()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        global_pos = event.globalPosition().toPoint()

        if self._resize_active:
            self._resize_geometry(global_pos)
            event.accept()
            return

        self._apply_cursor_for_edges(self._hit_test_edges(pos))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._end_window_drag()
        self._resize_active = False
        self._resize_edges = set()
        self._apply_cursor_for_edges(self._hit_test_edges(event.position().toPoint()))
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_group_section_widths()
        if hasattr(self, "previous_launch_combo") and self.previous_launch_combo.currentData():
            self.on_previous_launch_changed()

    def leaveEvent(self, event):
        if not self._resize_active:
            self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def eventFilter(self, source, event):
        if source in self._drag_source_widgets and not self._resize_active:
            event_type = event.type()
            if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                if self._is_background_drag_zone(source, event.position().toPoint()):
                    self._begin_window_drag(event.globalPosition().toPoint())
                    event.accept()
                    return True
            elif event_type == QEvent.MouseMove and self._drag_active and (event.buttons() & Qt.LeftButton):
                if self._move_window_drag(event.globalPosition().toPoint()):
                    event.accept()
                    return True
            elif event_type == QEvent.MouseButtonRelease and self._drag_active:
                self._end_window_drag()
                event.accept()
                return True
        return super().eventFilter(source, event)


def install_dev_toolkit_relaunch_monitor(window: DevLauncherWindow, runtime_logger=None):
    timer = QTimer(window)

    def poll_relaunch_request():
        if not dev_toolkit_relaunch_signal.consume():
            return
        if callable(runtime_logger):
            runtime_logger("TOOLKIT_MAIN|RELAUNCH_REQUEST_RECEIVED")
        window.set_status("Relaunch request received. Closing current Dev Toolkit window.")
        window.close()
        app = QApplication.instance()
        if app is not None:
            QTimer.singleShot(0, app.quit)

    timer.timeout.connect(poll_relaunch_request)
    timer.start(200)
    return timer


def main():
    runtime_log_file = create_dev_toolkit_runtime_log()

    def runtime_milestone(event: str):
        write_dev_toolkit_runtime_marker(runtime_log_file, event)

    runtime_milestone("TOOLKIT_MAIN|START")

    def log_single_instance_event(event: str):
        runtime_milestone(f"TOOLKIT_MAIN|{event}")

    if not acquire_or_prompt_replace(
        dev_toolkit_guard,
        dev_toolkit_relaunch_signal,
        "Dev Toolkit Session Active",
        "A Nexus Desktop AI Dev Toolkit session is already open.\n\nDo you want to close the current toolkit window and relaunch a fresh Dev Toolkit session?",
        eyebrow_text="NEXUS DESKTOP AI DEV TOOLKIT",
        primary_button_text="Relaunch Dev Toolkit",
        secondary_button_text="Keep Current Toolkit",
        event_logger=log_single_instance_event,
    ):
        runtime_milestone("TOOLKIT_MAIN|SINGLE_INSTANCE_BLOCKED")
        runtime_milestone("TOOLKIT_MAIN|EXIT|code=0")
        return 0

    app = QApplication.instance() or QApplication(sys.argv)
    runtime_milestone("TOOLKIT_MAIN|QAPPLICATION_READY")
    app.setFont(QFont("Consolas", 10))
    window = DevLauncherWindow(runtime_logger=runtime_milestone)
    runtime_milestone("TOOLKIT_MAIN|WINDOW_CONSTRUCTED")
    window.show()
    runtime_milestone("TOOLKIT_MAIN|WINDOW_SHOWN")
    relaunch_timer = install_dev_toolkit_relaunch_monitor(window, runtime_milestone)
    try:
        exit_code = app.exec()
        runtime_milestone(f"TOOLKIT_MAIN|EXIT|code={exit_code}")
        return exit_code
    finally:
        relaunch_timer.stop()
        dev_toolkit_guard.release()
        dev_toolkit_relaunch_signal.close()


if __name__ == "__main__":
    raise SystemExit(main())
