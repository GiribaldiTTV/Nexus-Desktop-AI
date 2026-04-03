import datetime
import os
import subprocess
import sys
import textwrap

from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QFont, QFontMetrics, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEV_DIR = os.path.join(ROOT_DIR, "dev")
DEV_LAUNCHERS_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")
DEV_LOGS_DIR = os.path.join(DEV_DIR, "logs")
SUPPORT_BUNDLE_TRIAGE_SCRIPT = os.path.join(ROOT_DIR, "dev", "jarvis_support_bundle_triage.py")

PYTHONW_PATH = r"C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"

LANE_CONFIG = {
    "diagnostics": {
        "label": "Diagnostics UI Test",
        "detail": (
            "Launches the standalone diagnostics window with safe manual test content. "
            "Best for focus, monitor, dismiss, and passive-window checks."
        ),
        "quiet_launcher": "launch_jarvis_diagnostics_manual_test.vbs",
        "voice_launcher": "",
        "supports_voice": False,
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
        "quiet_launcher": "launch_jarvis_launcher_failure_manual_test.vbs",
        "voice_launcher": "launch_jarvis_launcher_failure_manual_test_with_voice.vbs",
        "supports_voice": True,
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
        "quiet_launcher": "launch_jarvis_launcher_startup_abort_manual_test.vbs",
        "voice_launcher": "launch_jarvis_launcher_startup_abort_manual_test_with_voice.vbs",
        "supports_voice": True,
        "log_root": os.path.join(DEV_LOGS_DIR, "manual_launcher_startup_abort_test"),
        "log_root_with_voice": os.path.join(DEV_LOGS_DIR, "manual_launcher_startup_abort_test_with_voice"),
        "crash_folder": "crash",
    },
    "voiceRegression": {
        "label": "Voice Regression Harness",
        "detail": (
            "Runs the contained FB-018 voice regression harness across the current launcher-owned "
            "voice lanes and direct diagnostics voice probes, then writes a pass/fail report."
        ),
        "quiet_launcher": "launch_jarvis_voice_regression_harness.vbs",
        "voice_launcher": "",
        "supports_voice": False,
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
        "quiet_launcher": "launch_jarvis_desktop_entrypoint_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
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
        "quiet_launcher": "launch_jarvis_desktop_launcher_healthy_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
        "log_root": os.path.join(DEV_LOGS_DIR, "desktop_launcher_healthy_validation"),
        "report_root": os.path.join(DEV_LOGS_DIR, "desktop_launcher_healthy_validation", "reports"),
        "report_prefix": "DesktopLauncherHealthyValidationReport_",
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
        "quiet_launcher": "launch_jarvis_desktop_launcher_regression_harness.vbs",
        "voice_launcher": "",
        "supports_voice": False,
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
        "quiet_launcher": "launch_jarvis_support_bundle_triage_harness.vbs",
        "voice_launcher": "",
        "supports_voice": False,
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
        "quiet_launcher": "launch_jarvis_support_bundle_triage_toolkit_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
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
        "quiet_launcher": "launch_jarvis_diagnostics_report_issue_validation.vbs",
        "voice_launcher": "",
        "supports_voice": False,
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
        "label": "Voice, Healthy Start, & Regression",
        "lane_keys": ("voiceRegression", "desktopHealthy", "launcherHealthy", "launcherRegression"),
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


class TitleBar(QFrame):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.drag_active = False
        self.drag_pos = QPoint()
        self.setObjectName("titleBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        title = QLabel("JARVIS DEV TOOLKIT // INTERNAL")
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
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)

        title = QLabel(title_text)
        title.setObjectName("panelTitle")
        self.layout.addWidget(title)


class DevLauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis Dev Toolkit")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.resize(980, 720)
        self.setMinimumSize(840, 620)

        self._drag_active = False
        self._resize_active = False
        self._resize_edges = set()
        self._resize_start_pos = QPoint()
        self._resize_start_geom = QRect()
        self._edge_margin = 8
        self.setMouseTracking(True)

        self.pending_launch_key = ""
        self.selected_lane_key = "diagnostics"
        self.session_launch_records = {}
        self.previous_launch_entries = []

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
                font-size: 12pt;
                font-weight: 700;
                letter-spacing: 1px;
            }

            QPushButton#titleBarButton {
                min-width: 76px;
                padding: 5px 8px;
                border: 1px solid #00d8ff;
                background: #0a1b26;
                color: #f4fbff;
                font-size: 10pt;
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
                font-size: 11pt;
                font-weight: 700;
                letter-spacing: 1px;
            }

            QLabel#bannerTitle {
                color: #d4af37;
                font-size: 24pt;
                font-weight: 700;
            }

            QLabel#bannerSubtitle {
                color: #ff4c4c;
                font-size: 12pt;
                font-weight: 700;
            }

            QFrame#panel {
                border: 1px solid #0fe1ff;
                background: #08131c;
            }

            QLabel#panelTitle {
                color: #d4af37;
                font-size: 13pt;
                font-weight: 700;
            }

            QLabel#fieldLabel {
                color: #9feeff;
                font-size: 9.5pt;
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

            QLabel#detailBox, QLabel#noteBox, QLabel#statusBox {
                border: 1px solid #134353;
                background: #06111a;
                padding: 8px;
                color: #9fd7df;
                font-size: 9pt;
            }

            QLabel#statusBox {
                color: #d4af37;
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
        root.setSpacing(10)

        shell = QFrame()
        shell.setObjectName("shell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(14, 14, 14, 14)
        shell_layout.setSpacing(12)

        self.title_bar = TitleBar(self)
        shell_layout.addWidget(self.title_bar)

        banner = QFrame()
        banner.setObjectName("banner")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(12, 12, 12, 12)
        banner_layout.setSpacing(4)

        banner_top = QLabel("STARK INDUSTRIES // INTERNAL TOOLING")
        banner_top.setObjectName("bannerTop")
        banner_top.setAlignment(Qt.AlignCenter)
        banner_layout.addWidget(banner_top)

        banner_title = QLabel("JARVIS DEV TOOLKIT")
        banner_title.setObjectName("bannerTitle")
        banner_title.setAlignment(Qt.AlignCenter)
        banner_layout.addWidget(banner_title)

        banner_subtitle = QLabel("Manual validation launch surface")
        banner_subtitle.setObjectName("bannerSubtitle")
        banner_subtitle.setAlignment(Qt.AlignCenter)
        banner_layout.addWidget(banner_subtitle)

        shell_layout.addWidget(banner)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        status_panel = Panel("Status")
        self.status_label = QLabel("Ready.")
        self.status_label.setObjectName("statusBox")
        self.status_label.setWordWrap(True)
        status_panel.layout.addWidget(self.status_label)
        content_layout.addWidget(status_panel)

        global_utils_panel = Panel("Global Utilities")
        self._build_global_utilities_panel(global_utils_panel.layout)
        content_layout.addWidget(global_utils_panel)

        current_launch_panel = Panel("Custom Launch")
        self._build_current_launch_group_panel(current_launch_panel.layout)
        content_layout.addWidget(current_launch_panel)

        previous_launch_panel = Panel("Previous Launches")
        self._build_previous_launch_group_panel(previous_launch_panel.layout)
        content_layout.addWidget(previous_launch_panel)

        notes_panel = Panel("Notes")
        notes_label = QLabel(
            "- Custom Launch utilities only light up for evidence created by launches started in this Dev Toolkit session.\n"
            "- Previous Launches lets you reopen earlier dev evidence without mixing it into the active Custom Launch flow.\n"
            "- Global Utilities only open stable developer locations and never depend on the selected lane.\n"
            "- Dev Toolkit evidence writes under C:\\Jarvis\\dev\\logs lane roots instead of the active client-facing logs root.\n"
            "- Support Bundle Triage Helper still reads bundles from the client logs area when you pick them manually."
        )
        notes_label.setObjectName("noteBox")
        notes_label.setWordWrap(True)
        notes_panel.layout.addWidget(notes_label)
        content_layout.addWidget(notes_panel)
        content_layout.addStretch(1)

        scroll.setWidget(content)
        shell_layout.addWidget(scroll, 1)
        root.addWidget(shell)

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

        self.audio_combo = QComboBox()
        self.audio_combo.addItems(["Quiet (No Audio / No Voice)", "With Voice / Audio"])
        self.audio_combo.setMinimumWidth(0)
        self.audio_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_combo.currentIndexChanged.connect(self.on_launch_mode_changed)
        layout.addWidget(self.audio_combo)

        lane_group_label = QLabel("Purpose")
        lane_group_label.setObjectName("fieldLabel")
        layout.addWidget(lane_group_label)

        self.lane_group_combo = QComboBox()
        self.lane_group_combo.setMinimumWidth(0)
        self.lane_group_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for group in CONFIG_LANE_GROUPS:
            self.lane_group_combo.addItem(group["label"])
        self.lane_group_combo.currentIndexChanged.connect(self.on_lane_group_changed)
        layout.addWidget(self.lane_group_combo)

        lane_choice_label = QLabel("Test / Helper")
        lane_choice_label.setObjectName("fieldLabel")
        layout.addWidget(lane_choice_label)

        self.lane_combo = QComboBox()
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

        self.delay_combo = QComboBox()
        self.delay_combo.addItems(["Now", "3s", "5s", "10s"])
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

        self.populate_lane_group_choices("diagnostics")

    def _build_global_utilities_panel(self, layout):
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        button_row.addStretch(1)

        buttons = [
            ("Open Jarvis Root", self.open_jarvis_root),
            ("Open Dev Folder", self.open_dev_folder),
            ("Open Dev Logs Root", self.open_dev_logs_root),
            ("Open Dev Launchers Folder", self.open_launchers_folder),
        ]
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            btn.setMinimumWidth(180)
            button_row.addWidget(btn)

        button_row.addStretch(1)
        layout.addLayout(button_row)

        note = QLabel(
            "Global utilities always open the same stable developer locations and never depend on the selected lane."
        )
        note.setObjectName("noteBox")
        note.setWordWrap(True)
        layout.addWidget(note)

    def _create_group_subsection(self, title_text: str):
        frame = QFrame()
        frame.setObjectName("panel")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        inner_layout = QVBoxLayout(frame)
        inner_layout.setContentsMargins(12, 12, 12, 12)
        inner_layout.setSpacing(10)

        title = QLabel(title_text)
        title.setObjectName("fieldLabel")
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
        layout.addWidget(note)
        layout.addStretch(1)

    def _build_previous_launches_panel(self, layout):
        load_label = QLabel("Load Previous Launches")
        load_label.setObjectName("fieldLabel")
        layout.addWidget(load_label)

        refresh_btn = QPushButton("Refresh Previous Launches")
        refresh_btn.clicked.connect(self.refresh_previous_launches)
        layout.addWidget(refresh_btn)

        previous_choice_label = QLabel("Previous Launch")
        previous_choice_label.setObjectName("fieldLabel")
        layout.addWidget(previous_choice_label)

        self.previous_launch_combo = QComboBox()
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
        layout.addWidget(note)
        layout.addStretch(1)

    def current_lane_group(self) -> dict:
        groups = self.filtered_lane_groups()
        if not groups:
            return {"label": "No Matching Lanes", "lane_keys": ()}
        index = self.lane_group_combo.currentIndex()
        if index < 0 or index >= len(groups):
            index = 0
        return groups[index]

    def filtered_lane_groups(self) -> list[dict]:
        wants_voice = self.audio_combo.currentIndex() == 1
        groups = []
        for group in CONFIG_LANE_GROUPS:
            lane_keys = []
            for lane_key in group["lane_keys"]:
                lane = LANE_CONFIG[lane_key]
                if wants_voice and not lane.get("supports_voice", False):
                    continue
                lane_keys.append(lane_key)
            if lane_keys:
                groups.append({"label": group["label"], "lane_keys": tuple(lane_keys)})
        return groups

    def populate_lane_group_choices(self, preferred_lane_key: str = ""):
        groups = self.filtered_lane_groups()
        self.lane_group_combo.blockSignals(True)
        self.lane_group_combo.clear()
        preferred_group_index = 0
        for index, group in enumerate(groups):
            self.lane_group_combo.addItem(group["label"])
            if preferred_lane_key and preferred_lane_key in group["lane_keys"]:
                preferred_group_index = index
        if groups:
            self.lane_group_combo.setCurrentIndex(preferred_group_index)
        self.lane_group_combo.blockSignals(False)
        self.populate_lane_choices(preferred_lane_key)

    def populate_lane_choices(self, preferred_lane_key: str = ""):
        group = self.current_lane_group()
        self.lane_combo.blockSignals(True)
        self.lane_combo.clear()
        preferred_index = 0
        for index, lane_key in enumerate(group["lane_keys"]):
            lane = LANE_CONFIG[lane_key]
            self.lane_combo.addItem(lane["label"], lane_key)
            if lane_key == preferred_lane_key:
                preferred_index = index
        self.lane_combo.setCurrentIndex(preferred_index)
        self.lane_combo.blockSignals(False)
        self.selected_lane_key = self.lane_combo.currentData() or group["lane_keys"][0]
        self.update_ui()

    def on_lane_group_changed(self, *_args):
        self.populate_lane_choices()

    def on_launch_mode_changed(self, *_args):
        preferred_lane_key = self.current_lane_key()
        self.populate_lane_group_choices(preferred_lane_key)

    def on_lane_choice_changed(self, *_args):
        lane_key = self.lane_combo.currentData()
        if lane_key:
            self.selected_lane_key = lane_key
        self.update_ui()

    def current_lane_key(self) -> str:
        return self.selected_lane_key or "diagnostics"

    def current_lane(self) -> dict:
        return LANE_CONFIG[self.current_lane_key()]

    def voice_requested(self) -> bool:
        return self.audio_combo.currentIndex() == 1 and self.current_lane().get("supports_voice", False)

    def current_launch_mode_key(self) -> str:
        return "voice" if self.voice_requested() else "quiet"

    def current_session_artifact_key(self) -> str:
        return f"{self.current_lane_key()}::{self.current_launch_mode_key()}"

    def active_evidence_root(self) -> str:
        lane = self.current_lane()
        if self.voice_requested() and lane.get("log_root_with_voice"):
            return lane["log_root_with_voice"]
        return lane["log_root"]

    def active_report_root(self) -> str:
        return self.current_lane().get("report_root", "")

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
        return self.session_launch_records.get(self.current_session_artifact_key(), {})

    def build_current_launch_record(self) -> dict:
        lane = self.current_lane()
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
        if self.voice_requested() and lane.get("voice_launcher"):
            return lane["voice_launcher"]
        return lane["quiet_launcher"]

    def active_label(self) -> str:
        lane = self.current_lane()
        if self.voice_requested() and lane.get("supports_voice"):
            return lane["label"] + " With Voice"
        return lane["label"]

    def select_lane(self, lane_key: str):
        if self.audio_combo.currentIndex() == 1 and not LANE_CONFIG[lane_key].get("supports_voice", False):
            self.audio_combo.blockSignals(True)
            self.audio_combo.setCurrentIndex(0)
            self.audio_combo.blockSignals(False)
        self.populate_lane_group_choices(lane_key)

    def audio_mode_summary(self, lane: dict) -> str:
        if lane.get("supports_voice", False):
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
        return f"{lane_label} | {mode_label} | {timestamp_text}"

    def previous_entry_detail(self, entry: dict) -> str:
        wrap_width = self.detail_wrap_width_for_label(self.previous_detail_label)
        lines = [
            f"Lane: {entry['lane_label']}",
            f"Mode: {self.compact_previous_mode_label(entry['mode_label'])}",
            f"Saved Evidence Time: {entry.get('timestamp_text', 'Unknown time')}",
        ]
        self.append_wrapped_detail(lines, "Evidence Root", entry["evidence_root"], width=wrap_width)
        if entry.get("runtime_log"):
            self.append_wrapped_detail(lines, "Runtime", entry["runtime_log"], width=wrap_width)
        if entry.get("report_path"):
            self.append_wrapped_detail(lines, "Report", entry["report_path"], width=wrap_width)
        if entry.get("crash_folder"):
            self.append_wrapped_detail(lines, "Crash Folder", entry["crash_folder"], width=wrap_width)
        return "\n".join(lines)

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
            candidates = [("quiet", lane.get("log_root", ""), "Quiet (No Audio / No Voice)")]
            if lane.get("log_root_with_voice"):
                candidates.append(("voice", lane["log_root_with_voice"], "With Voice / Audio"))

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

                runtime_log = self.latest_runtime_log_for_record(record)
                report_path = self.latest_report_for_record(record)
                crash_folder = self.crash_folder_for_record(record)

                candidates_with_times = []
                for path in (runtime_log, report_path, crash_folder):
                    if not path:
                        continue
                    try:
                        candidates_with_times.append((os.path.getmtime(path), path))
                    except OSError:
                        continue

                if not candidates_with_times and not os.path.isdir(evidence_root):
                    continue

                if candidates_with_times:
                    best_time, _ = max(candidates_with_times, key=lambda item: item[0])
                else:
                    try:
                        best_time = os.path.getmtime(evidence_root)
                    except OSError:
                        continue

                entries.append(
                    {
                        **record,
                        "runtime_log": runtime_log,
                        "report_path": report_path,
                        "crash_folder": crash_folder,
                        "last_activity": best_time,
                        "timestamp_text": datetime.datetime.fromtimestamp(best_time).strftime("%Y-%m-%d %I:%M:%S %p"),
                    }
                )

        entries.sort(key=lambda entry: entry["last_activity"], reverse=True)
        return entries

    def refresh_previous_launches(self):
        self.previous_launch_entries = self.scan_previous_launch_entries()
        if not hasattr(self, "previous_launch_combo"):
            return

        previous_value = self.previous_launch_combo.currentData()
        self.previous_launch_combo.blockSignals(True)
        self.previous_launch_combo.clear()
        self.previous_launch_combo.addItem("Choose a previous launch...", None)
        selected_index = 0
        for index, entry in enumerate(self.previous_launch_entries, start=1):
            key = f"{entry['lane_key']}::{entry['mode_key']}::{int(entry['last_activity'])}"
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
        self.detail_label.setText(self.detail_text_for_lane(lane))

        supports_voice = lane.get("supports_voice", False)
        if self.audio_combo.currentIndex() == 1 and not supports_voice:
            self.audio_combo.blockSignals(True)
            self.audio_combo.setCurrentIndex(0)
            self.audio_combo.blockSignals(False)
        self.audio_label.setText(
            "Choose whether this launch should stay quiet or run with live voice/audio. "
            f"Current lane support: {self.audio_mode_summary(lane)}"
        )

        self.apply_group_section_widths()
        self.update_mode_line(lane)
        self.cancel_btn.setEnabled(self.launch_timer.isActive())
        self.refresh_utility_buttons()

    def set_status(self, text: str):
        self.status_label.setText(text)
        self.refresh_utility_buttons()

    def refresh_utility_buttons(self):
        current_record = self.current_session_record()
        current_cutoff = current_record.get("launched_at_ts", 0.0) if current_record else 0.0
        if hasattr(self, "selected_evidence_btn"):
            evidence_root = current_record.get("evidence_root", "")
            evidence_exists = bool(current_record) and os.path.isdir(evidence_root)
            self.selected_evidence_btn.setEnabled(evidence_exists)
            self.selected_evidence_btn.setToolTip(
                evidence_root
                if evidence_exists
                else "Run this Custom Launch in the current Dev Toolkit session to enable its evidence root."
            )

        if hasattr(self, "latest_runtime_btn"):
            runtime_path = self.latest_runtime_log_for_record(current_record, current_cutoff) if current_record else ""
            self.latest_runtime_btn.setEnabled(bool(runtime_path))
            self.latest_runtime_btn.setToolTip(
                runtime_path or "No current-session runtime log is available yet for the selected lane."
            )

        if hasattr(self, "latest_report_btn"):
            report_root = current_record.get("report_root", "")
            report_path = self.latest_report_for_record(current_record, current_cutoff) if current_record else ""
            supports_reports = bool(current_record and current_record.get("report_root"))
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

        previous_entry = self.selected_previous_entry()
        if hasattr(self, "previous_evidence_btn"):
            previous_root = previous_entry.get("evidence_root", "")
            previous_exists = bool(previous_entry) and os.path.isdir(previous_root)
            self.previous_evidence_btn.setEnabled(previous_exists)
            self.previous_evidence_btn.setToolTip(
                previous_root
                if previous_exists
                else "Choose a previous launch entry with saved evidence."
            )

        if hasattr(self, "previous_runtime_btn"):
            previous_runtime = previous_entry.get("runtime_log", "")
            self.previous_runtime_btn.setEnabled(bool(previous_runtime))
            self.previous_runtime_btn.setToolTip(
                previous_runtime or "No saved runtime log is available for the selected previous launch."
            )

        if hasattr(self, "previous_report_btn"):
            previous_report = previous_entry.get("report_path", "")
            self.previous_report_btn.setEnabled(bool(previous_report))
            self.previous_report_btn.setToolTip(
                previous_report or "No saved report is available for the selected previous launch."
            )

        if hasattr(self, "previous_crash_btn"):
            previous_crash = previous_entry.get("crash_folder", "")
            self.previous_crash_btn.setEnabled(bool(previous_crash))
            self.previous_crash_btn.setToolTip(
                previous_crash or "No saved crash folder is available for the selected previous launch."
            )

    def schedule_or_launch(self):
        self.cancel_launch(silent=True)
        delay_text = self.delay_combo.currentText()
        if delay_text == "Now":
            self.run_selected_launcher()
            return

        delay_seconds = int(delay_text.rstrip("s"))
        self.pending_launch_key = self.current_lane_key()
        self.launch_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.launch_timer.start(delay_seconds * 1000)
        self.set_status(f"Launching {self.active_label()} in {delay_seconds} second(s)...")

    def cancel_launch(self, silent: bool = False):
        if self.launch_timer.isActive():
            self.launch_timer.stop()
        self.pending_launch_key = ""
        self.launch_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if not silent:
            self.set_status("Pending launch cancelled.")

    def run_selected_launcher(self):
        try:
            lane = self.current_lane()
            if lane.get("requires_bundle_input"):
                source_path = self.select_support_bundle_source()
                if not source_path:
                    self.set_status("Launch cancelled: no support bundle selected.")
                    return
                launch_key = self.current_session_artifact_key()
                self.session_launch_records[launch_key] = self.build_current_launch_record()
                subprocess.Popen([PYTHONW_PATH, lane["script_path"], source_path], cwd=ROOT_DIR)
                self.set_status(f"Launched: {self.active_label()} :: {source_path}")
                return

            launcher_path = os.path.join(DEV_LAUNCHERS_DIR, self.active_launcher_filename())
            launch_key = self.current_session_artifact_key()
            self.session_launch_records[launch_key] = self.build_current_launch_record()
            subprocess.Popen(["wscript.exe", launcher_path], cwd=DEV_LAUNCHERS_DIR)
            self.set_status(f"Launched: {self.active_label()}")
        except Exception as exc:
            if 'launch_key' in locals():
                self.session_launch_records.pop(launch_key, None)
            self.set_status(f"Launch failed: {self.active_label()} :: {exc}")
        finally:
            self.launch_timer.stop()
            self.launch_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)

    def select_support_bundle_source(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Support Bundle Zip",
            CLIENT_LOGS_DIR,
            "Support Bundle Zip (*.zip);;All Files (*)",
        )
        if file_path:
            return file_path

        return QFileDialog.getExistingDirectory(
            self,
            "Select Extracted Support Bundle Folder",
            CLIENT_LOGS_DIR,
        )

    def open_jarvis_root(self):
        self.open_path(ROOT_DIR, f"Opened: Jarvis root :: {ROOT_DIR}")

    def open_dev_folder(self):
        self.open_path(DEV_DIR, f"Opened: Dev folder :: {DEV_DIR}")

    def open_dev_logs_root(self):
        os.makedirs(DEV_LOGS_DIR, exist_ok=True)
        self.open_path(DEV_LOGS_DIR, f"Opened: Dev logs root :: {DEV_LOGS_DIR}")

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
            self.set_status(f"{self.current_lane()['label']} does not produce a report artifact.")
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
        if not crash_path:
            crash_folder_name = record.get("crash_folder_name", "") if record else ""
            if not crash_folder_name:
                self.set_status(f"{self.current_lane()['label']} does not use a lane-local crash folder.")
                return
            self.set_status(f"Crash folder not found yet: {os.path.join(record.get('evidence_root', self.active_evidence_root()), crash_folder_name)}")
            return
        self.open_path(
            crash_path,
            f"Opened latest dev crash folder for {self.current_lane()['label']}: {crash_path}",
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


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 10))
    window = DevLauncherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
