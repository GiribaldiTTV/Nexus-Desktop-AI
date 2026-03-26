# Version 1.3.2 rev 13 diagnostics UI

import os
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLabel, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QFont, QGuiApplication

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
CRASH_FOLDER = os.path.join(LOG_DIR, "crash")
STATUS_FILE = os.path.join(LOG_DIR, "diagnostics_status.txt")
STOP_SIGNAL_FILE = os.path.join(LOG_DIR, "diagnostics_stop.signal")


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

class DiagnosticsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.resize(920, 660)
        self.setMinimumSize(720, 520)

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
            padding: 6px 8px;
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

        title = QLabel("J.A.R.V.I.S. SYSTEM DIAGNOSTICS")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 13, QFont.Bold))
        root.addWidget(title)

        self.summary = QLabel("Failure Summary: waiting for diagnostic input...")
        self.summary.setAlignment(Qt.AlignCenter)
        root.addWidget(self.summary)

        trace_title = QLabel("DIAGNOSTIC TRACE")
        trace_title.setFont(QFont("Consolas", 11, QFont.Bold))
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
        jarvis_title.setContentsMargins(0, 8, 0, 4)
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

        self.dragPos = QPoint()
        self._seen = 0
        self._drag_active = False
        self._resize_active = False
        self._resize_edges = set()
        self._resize_start_pos = QPoint()
        self._resize_start_geom = QRect()
        self._edge_margin = 8
        self.setMouseTracking(True)
        self.voice_history = []
        self.voice_current = ""
        self.current_state = "STARTED"
        self._last_rendered_state = ""

        self.move_to_right_monitor()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_status)
        self.timer.start(80)

    def move_to_right_monitor(self):
        screens = QGuiApplication.screens()
        target = max(screens, key=lambda s: s.geometry().x())
        geo = target.geometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.raise_)
        QTimer.singleShot(25, self.raise_)

    def dismiss_diagnostics(self):
        self.cleanup_and_exit()

    def cleanup_and_exit(self):
        try:
            self.timer.stop()
        except Exception:
            pass

        if self.current_state in ("STARTED", "RECOVERING"):
            try:
                with open(STOP_SIGNAL_FILE, "w", encoding="utf-8") as f:
                    f.write("dismissed")
            except Exception:
                pass

        if self.current_state == "COMPLETE":
            for cleanup_path in (STOP_SIGNAL_FILE, STATUS_FILE):
                try:
                    if os.path.exists(cleanup_path):
                        os.remove(cleanup_path)
                except Exception:
                    pass

        try:
            self.hide()
        except Exception:
            pass

        app = QApplication.instance()
        if app:
            app.quit()

        os._exit(0)

    def closeEvent(self, event):
        event.accept()
        self.cleanup_and_exit()

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
            else:
                self._drag_active = True
                self.dragPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
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

        if self._drag_active and (event.buttons() & Qt.LeftButton):
            self.move(global_pos - self.dragPos)
            event.accept()
            return

        self._apply_cursor_for_edges(self._hit_test_edges(pos))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        self._resize_active = False
        self._resize_edges = set()
        self._apply_cursor_for_edges(self._hit_test_edges(event.position().toPoint()))
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if not self._drag_active and not self._resize_active:
            self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def render_voice_panel(self):

        lines = list(self.voice_history)
        if self.voice_current:
            lines.append(self.voice_current)
        self.speech.setPlainText("\n".join(lines))
        self.speech.verticalScrollBar().setValue(self.speech.verticalScrollBar().maximum())

    def append_trace(self, payload):
        cursor = self.trace.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.trace.setTextCursor(cursor)

        stripped = payload.strip()

        if stripped and set(stripped) == {"-"}:
            self.trace.insertHtml(
                '<div style="margin: 8px 8px 10px 8px;">'
                '<div style="height: 2px; border-radius: 1px; background: qlineargradient('
                'x1:0, y1:0, x2:1, y2:0, '
                'stop:0 rgba(0, 225, 255, 28), '
                'stop:0.15 rgba(0, 225, 255, 165), '
                'stop:0.50 rgba(130, 245, 255, 255), '
                'stop:0.85 rgba(0, 225, 255, 165), '
                'stop:1 rgba(0, 225, 255, 28)'
                ');"></div>'
                '<div style="height: 1px; margin-top: 1px; background: qlineargradient('
                'x1:0, y1:0, x2:1, y2:0, '
                'stop:0 rgba(120, 240, 255, 0), '
                'stop:0.22 rgba(120, 240, 255, 70), '
                'stop:0.50 rgba(120, 240, 255, 135), '
                'stop:0.78 rgba(120, 240, 255, 70), '
                'stop:1 rgba(120, 240, 255, 0)'
                ');"></div></div>'
            )
            self.trace.insertPlainText("\n")
        elif payload == "":
            self.trace.insertPlainText("\n")
        else:
            self.trace.insertHtml(
                f'<div style="margin-left: 10px; white-space: pre;">{html_escape(payload)}</div>'
            )
            self.trace.insertPlainText("\n")

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
                self.render_voice_panel()

    def open_crash(self):
        if os.path.exists(CRASH_FOLDER):
            os.startfile(CRASH_FOLDER)

def main():
    app = QApplication(sys.argv)
    w = DiagnosticsWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
