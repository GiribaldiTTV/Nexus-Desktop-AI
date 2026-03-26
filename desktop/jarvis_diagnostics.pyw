import os
import sys
import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLabel, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QFont, QGuiApplication, QCursor

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
CRASH_FOLDER = os.path.join(LOG_DIR, "crash")
STATUS_FILE = os.path.join(LOG_DIR, "diagnostics_status.txt")
STOP_SIGNAL_FILE = os.path.join(LOG_DIR, "diagnostics_stop.signal")

RUNTIME_LOG_FILE = ""
RESIZE_MARGIN = 8
MIN_WINDOW_WIDTH = 760
MIN_WINDOW_HEIGHT = 540


def parse_runtime_log_arg(argv):
    global RUNTIME_LOG_FILE

    for index, arg in enumerate(argv):
        if arg == "--runtime-log" and index + 1 < len(argv):
            RUNTIME_LOG_FILE = argv[index + 1]
            return

    RUNTIME_LOG_FILE = os.environ.get("JARVIS_RUNTIME_LOG", "")


def ui_runtime(message: str):
    if not RUNTIME_LOG_FILE:
        return

    try:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        with open(RUNTIME_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] DIAG_UI|{message}\n")
    except Exception:
        pass


class DiagnosticsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Window |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setMouseTracking(True)
        self.resize(920, 660)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self._drag_active = False
        self._drag_offset = QPoint()
        self._resize_active = False
        self._resize_edges = ""
        self._resize_start_pos = QPoint()
        self._resize_start_geometry = QRect()
        self._last_hover_edges = ""

        self.setStyleSheet("""
        QWidget {
            background: #05090d;
            color: #6ee7ff;
        }

        QLabel {
            color: #6ee7ff;
        }

        QFrame.panel {
            border: 1px solid #00e1ff;
            border-radius: 8px;
            background: #031018;
        }

        QTextEdit {
            background: #02070b;
            border: 1px solid #00e1ff;
            border-radius: 6px;
            color: #6ee7ff;
            font-family: Consolas;
            font-size: 11pt;
            padding: 4px;
            selection-background-color: #0a3a46;
        }

        QTextEdit QScrollBar:vertical {
            background: #031018;
            width: 12px;
            margin: 2px;
            border: 1px solid #00b8d9;
            border-radius: 6px;
        }

        QTextEdit QScrollBar::handle:vertical {
            background: #00cfff;
            min-height: 24px;
            border-radius: 5px;
            border: 1px solid #7befff;
        }

        QTextEdit QScrollBar::add-line:vertical,
        QTextEdit QScrollBar::sub-line:vertical {
            background: transparent;
            height: 0px;
            border: none;
        }

        QTextEdit QScrollBar::add-page:vertical,
        QTextEdit QScrollBar::sub-page:vertical {
            background: #031018;
            border-radius: 4px;
        }

        QPushButton {
            background: #07151b;
            border: 1px solid #00e1ff;
            border-radius: 8px;
            padding: 8px;
            color: #6ee7ff;
        }

        QPushButton:hover {
            background: #0f2a35;
        }
        """)

        root = QVBoxLayout()
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(10)

        self.stark = QLabel("STARK INDUSTRIES")
        self.stark.setAlignment(Qt.AlignCenter)
        self.stark.setFont(QFont("Consolas", 18, QFont.Bold))
        self.stark.setStyleSheet("color:#d4af37;")
        root.addWidget(self.stark)

        self.title = QLabel("J.A.R.V.I.S. SYSTEM DIAGNOSTICS")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Consolas", 13, QFont.Bold))
        root.addWidget(self.title)

        self.summary = QLabel("Failure Summary: waiting for diagnostic input...")
        self.summary.setAlignment(Qt.AlignCenter)
        root.addWidget(self.summary)

        trace_title = QLabel("DIAGNOSTIC TRACE")
        trace_title.setFont(QFont("Consolas", 11, QFont.Bold))
        trace_title.setContentsMargins(0, 12, 0, 4)
        root.addWidget(trace_title)

        trace_panel = QFrame()
        trace_panel.setObjectName("panel")
        trace_layout = QVBoxLayout()
        trace_layout.setContentsMargins(4, 3, 4, 4)

        self.trace = QTextEdit()
        self.trace.setReadOnly(True)
        trace_layout.addWidget(self.trace)
        trace_panel.setLayout(trace_layout)
        root.addWidget(trace_panel, 3)

        jarvis_title = QLabel("JARVIS")
        jarvis_title.setFont(QFont("Consolas", 11, QFont.Bold))
        jarvis_title.setContentsMargins(0, 12, 0, 4)
        root.addWidget(jarvis_title)

        speech_panel = QFrame()
        speech_panel.setObjectName("panel")
        speech_layout = QVBoxLayout()
        speech_layout.setContentsMargins(4, 3, 4, 4)

        self.speech = QTextEdit()
        self.speech.setReadOnly(True)
        self.speech.setMinimumHeight(120)
        speech_layout.addWidget(self.speech)
        speech_panel.setLayout(speech_layout)
        root.addWidget(speech_panel, 1)

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open Crash Folder")
        open_btn.clicked.connect(self.open_crash)

        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.clicked.connect(self.dismiss_diagnostics)

        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(dismiss_btn)
        root.addLayout(btn_layout)

        self.setLayout(root)

        self._seen = 0
        self.voice_history = []
        self.voice_current = ""
        self.current_state = "STARTED"
        self._last_rendered_state = ""

        self.move_to_right_monitor()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_status)
        self.timer.start(80)

        ui_runtime(
            f"DiagnosticsWindow init :: frameless=1 min_width={MIN_WINDOW_WIDTH} min_height={MIN_WINDOW_HEIGHT}"
        )

    def move_to_right_monitor(self):
        screens = QGuiApplication.screens()
        target = max(screens, key=lambda s: s.geometry().x())
        geo = target.geometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)
        ui_runtime(
            f"move_to_right_monitor :: screen={target.name()} x={x} y={y} width={self.width()} height={self.height()}"
        )

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.raise_)
        QTimer.singleShot(25, self.raise_)
        ui_runtime(f"showEvent :: x={self.x()} y={self.y()} width={self.width()} height={self.height()}")

    def closeEvent(self, event):
        ui_runtime(f"closeEvent accepted :: current_state={self.current_state}")
        event.accept()
        self.cleanup_and_exit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()
        ui_runtime(f"resizeEvent :: width={size.width()} height={size.height()}")

    def _edge_hits(self, pos):
        x = pos.x()
        y = pos.y()
        w = self.width()
        h = self.height()

        left = x <= RESIZE_MARGIN
        right = x >= w - RESIZE_MARGIN
        top = y <= RESIZE_MARGIN
        bottom = y >= h - RESIZE_MARGIN

        edges = ""
        if left:
            edges += "L"
        elif right:
            edges += "R"

        if top:
            edges += "T"
        elif bottom:
            edges += "B"

        return edges

    def _set_cursor_for_edges(self, edges):
        cursor_map = {
            "L": Qt.SizeHorCursor,
            "R": Qt.SizeHorCursor,
            "T": Qt.SizeVerCursor,
            "B": Qt.SizeVerCursor,
            "LT": Qt.SizeFDiagCursor,
            "RB": Qt.SizeFDiagCursor,
            "RT": Qt.SizeBDiagCursor,
            "LB": Qt.SizeBDiagCursor,
        }
        self.setCursor(cursor_map.get(edges, Qt.ArrowCursor))

    def _can_drag_from(self, pos):
        widget = self.childAt(pos)
        return widget is None or widget in {self, self.stark, self.title, self.summary}

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return super().mousePressEvent(event)

        edges = self._edge_hits(event.position().toPoint())
        if edges:
            self._resize_active = True
            self._resize_edges = edges
            self._resize_start_pos = event.globalPosition().toPoint()
            self._resize_start_geometry = self.geometry()
            ui_runtime(f"resize begin :: edges={edges} geometry={self.geometry().getRect()}")
            event.accept()
            return

        if self._can_drag_from(event.position().toPoint()):
            self._drag_active = True
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            ui_runtime(f"drag begin :: x={self.x()} y={self.y()}")
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        global_pos = event.globalPosition().toPoint()

        if self._resize_active:
            new_geo = QRect(self._resize_start_geometry)
            delta = global_pos - self._resize_start_pos

            if "L" in self._resize_edges:
                new_left = self._resize_start_geometry.left() + delta.x()
                max_left = self._resize_start_geometry.right() - self.minimumWidth() + 1
                new_geo.setLeft(min(new_left, max_left))
            if "R" in self._resize_edges:
                new_geo.setRight(max(self._resize_start_geometry.left() + self.minimumWidth() - 1,
                                     self._resize_start_geometry.right() + delta.x()))
            if "T" in self._resize_edges:
                new_top = self._resize_start_geometry.top() + delta.y()
                max_top = self._resize_start_geometry.bottom() - self.minimumHeight() + 1
                new_geo.setTop(min(new_top, max_top))
            if "B" in self._resize_edges:
                new_geo.setBottom(max(self._resize_start_geometry.top() + self.minimumHeight() - 1,
                                      self._resize_start_geometry.bottom() + delta.y()))

            self.setGeometry(new_geo.normalized())
            event.accept()
            return

        if self._drag_active:
            self.move(global_pos - self._drag_offset)
            event.accept()
            return

        edges = self._edge_hits(pos)
        if edges != self._last_hover_edges:
            self._last_hover_edges = edges
            self._set_cursor_for_edges(edges)
            if edges:
                ui_runtime(f"resize hover :: edges={edges}")
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._resize_active:
                ui_runtime(f"resize end :: geometry={self.geometry().getRect()}")
            if self._drag_active:
                ui_runtime(f"drag end :: x={self.x()} y={self.y()}")
            self._resize_active = False
            self._resize_edges = ""
            self._drag_active = False
            self._set_cursor_for_edges(self._edge_hits(event.position().toPoint()))
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def dismiss_diagnostics(self):
        ui_runtime("dismiss button clicked")
        self.cleanup_and_exit()

    def cleanup_and_exit(self):
        ui_runtime(f"cleanup_and_exit begin :: current_state={self.current_state}")

        try:
            self.timer.stop()
        except Exception:
            pass

        if self.current_state in ("STARTED", "RECOVERING"):
            try:
                with open(STOP_SIGNAL_FILE, "w", encoding="utf-8") as f:
                    f.write("dismissed")
                ui_runtime(f"stop signal written :: {STOP_SIGNAL_FILE}")
            except Exception as exc:
                ui_runtime(f"stop signal write failed :: {exc}")

        if self.current_state == "COMPLETE":
            for cleanup_path in (STOP_SIGNAL_FILE, STATUS_FILE):
                try:
                    if os.path.exists(cleanup_path):
                        os.remove(cleanup_path)
                        ui_runtime(f"cleanup deleted :: {cleanup_path}")
                except Exception as exc:
                    ui_runtime(f"cleanup delete failed :: {cleanup_path} :: {exc}")

        try:
            self.hide()
            ui_runtime("window hidden")
        except Exception as exc:
            ui_runtime(f"window hide failed :: {exc}")

        app = QApplication.instance()
        if app:
            app.quit()
            ui_runtime("QApplication quit requested")

        os._exit(0)

    def render_voice_panel(self):
        lines = list(self.voice_history)
        if self.voice_current:
            lines.append(self.voice_current)
        self.speech.setPlainText("\n".join(lines))
        self.speech.verticalScrollBar().setValue(self.speech.verticalScrollBar().maximum())

    def append_trace(self, payload):
        self.trace.append(payload)
        self.trace.verticalScrollBar().setValue(self.trace.verticalScrollBar().maximum())

    def poll_status(self):
        if not os.path.exists(STATUS_FILE):
            return

        try:
            with open(STATUS_FILE, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return

        new = lines[self._seen:]
        self._seen = len(lines)

        for raw in new:
            line = raw.strip()
            if not line or "|" not in line:
                continue

            kind, payload = line.split("|", 1)

            if kind == "SUMMARY":
                self.summary.setText("Failure Summary: " + payload)

            elif kind == "STATE":
                state = payload.strip()
                self.current_state = state

                mapping = {
                    "STARTED": "Jarvis State: Starting Diagnostics",
                    "RECOVERING": "Jarvis State: Attempting Recovery",
                    "COMPLETE": "Jarvis State: Offline",
                }

                should_render = True
                if state == "RECOVERING" and self._last_rendered_state == "RECOVERING":
                    should_render = False

                if should_render:
                    display = mapping.get(state, f"Jarvis State: {state}")
                    ui_runtime(f"State updated :: {state}")
                    self.append_trace("")
                    self.append_trace(display)
                    self.append_trace("---------------------------------------------------")
                    self.append_trace("")
                    self._last_rendered_state = state

            elif kind == "TRACE":
                self.append_trace(payload)

            elif kind == "VOICE_CLEAR":
                self.voice_current = ""
                self.render_voice_panel()

            elif kind == "VOICE_SYNC":
                self.voice_current = payload
                self.render_voice_panel()

            elif kind == "VOICE_FINAL":
                final_line = payload.strip()
                self.voice_current = ""
                if final_line and (not self.voice_history or self.voice_history[-1] != final_line):
                    self.voice_history.append(final_line)
                    ui_runtime(f"VOICE_FINAL appended :: {final_line}")
                self.render_voice_panel()

    def open_crash(self):
        ui_runtime(f"open_crash clicked :: exists={int(os.path.exists(CRASH_FOLDER))}")
        if os.path.exists(CRASH_FOLDER):
            os.startfile(CRASH_FOLDER)


def main():
    parse_runtime_log_arg(sys.argv)
    ui_runtime(f"Diagnostics process starting :: runtime_log={RUNTIME_LOG_FILE or 'UNSET'}")
    ui_runtime(f"Diagnostics status target :: {STATUS_FILE}")
    ui_runtime(f"Diagnostics stop target :: {STOP_SIGNAL_FILE}")
    app = QApplication(sys.argv)
    w = DiagnosticsWindow()
    w.show()
    ui_runtime("Diagnostics window shown")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
