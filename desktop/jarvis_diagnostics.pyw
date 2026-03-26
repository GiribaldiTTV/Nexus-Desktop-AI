# Version 1.3.2 rev 13 diagnostics UI

import os
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLabel, QHBoxLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QFont, QGuiApplication, QTextBlockFormat, QTextCharFormat

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
CRASH_FOLDER = os.path.join(LOG_DIR, "crash")
STATUS_FILE = os.path.join(LOG_DIR, "diagnostics_status.txt")
STOP_SIGNAL_FILE = os.path.join(LOG_DIR, "diagnostics_stop.signal")
RUNTIME_LOG_FILE = ""


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def summary_html(payload: str, payload_color: str = "#ff2b2b") -> str:
    return (
        '<div style="text-align: center;">'
        '<span style="color: #d4af37; font-weight: 700;">FAILURE SUMMARY</span>'
        '<span style="color: #00d8ff; font-weight: 700;"> // </span>'
        f'<span style="color: {payload_color}; font-weight: 700;">{html_escape(payload)}</span>'
        '</div>'
    )


def trace_signal_html(payload: str) -> str:
    styles = {
        "Failure cause:": ("#ff2b2b", "#ffd7d7", "#16090b"),
        "Assessment:": ("#d4af37", "#f3e2a3", "#151108"),
        "Triage:": ("#00e1ff", "#dffbff", "#08161b"),
    }

    for prefix, (accent_color, text_color, background_color) in styles.items():
        if payload.startswith(prefix):
            detail = payload[len(prefix):].lstrip()
            detail_html = f' <span style="color: {text_color};">{html_escape(detail)}</span>' if detail else ""
            return (
                f'<div style="margin-left: 10px; padding: 2px 0 2px 8px; '
                f'border-left: 2px solid {accent_color}; background: {background_color}; white-space: pre;">'
                f'<span style="color: {accent_color}; font-weight: 700;">{html_escape(prefix)}</span>'
                f'{detail_html}'
                '</div>'
            )

    return ""


def parse_runtime_log_arg(argv):
    global RUNTIME_LOG_FILE
    for i, arg in enumerate(argv):
        if arg == "--runtime-log" and i + 1 < len(argv):
            RUNTIME_LOG_FILE = argv[i + 1]
            return


def diag_runtime(message: str):
    if not RUNTIME_LOG_FILE:
        return
    try:
        with open(RUNTIME_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception:
        pass


def diag_event(*parts):
    diag_runtime("UI|" + "|".join(str(part) for part in parts))

class DiagnosticsWindow(QWidget):
    def __init__(self):
        super().__init__()
        diag_event('DiagnosticsWindow.__init__', 'start')

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.resize(920, 660)
        self.setMinimumSize(720, 520)
        diag_event('window_flags', 'frameless_tool_ontop')

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

        QTextEdit QScrollBar:horizontal {
            background: #031018;
            height: 12px;
            margin: 2px;
            border: 1px solid #00b8d9;
            border-radius: 6px;
        }

        QTextEdit QScrollBar::handle:horizontal {
            background: #00cfff;
            min-width: 24px;
            border-radius: 5px;
            border: 1px solid #7befff;
        }

        QTextEdit QScrollBar::add-line:horizontal,
        QTextEdit QScrollBar::sub-line:horizontal {
            background: transparent;
            width: 0px;
            border: none;
        }

        QTextEdit QScrollBar::add-page:horizontal,
        QTextEdit QScrollBar::sub-page:horizontal {
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
        self.stark.setFont(QFont("Consolas", 19, QFont.Bold))
        self.stark.setStyleSheet("color:#d4af37;")
        root.addWidget(self.stark)

        title = QLabel("J.A.R.V.I.S. SYSTEM DIAGNOSTICS")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 14, QFont.Bold))
        title.setStyleSheet("color:#ff2b2b;")
        root.addWidget(title)

        self.summary = QLabel()
        self.summary.setAlignment(Qt.AlignCenter)
        self.summary.setTextFormat(Qt.RichText)
        self.summary.setStyleSheet(
            "QLabel {"
            "background: #140d10;"
            "border: 1px solid #00e1ff;"
            "border-radius: 4px;"
            "padding: 5px 10px;"
            "}"
        )
        summary_font = self.summary.font()
        if summary_font.pointSize() > 0:
            summary_font.setPointSize(summary_font.pointSize() + 1)
        self.summary.setFont(summary_font)
        self.summary.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.summary.setText(summary_html("waiting for diagnostic input...", "#6ee7ff"))
        root.addWidget(self.summary)
        root.setAlignment(self.summary, Qt.AlignHCenter)

        trace_title = QLabel("DIAGNOSTIC TRACE")
        trace_title.setFont(QFont("Consolas", 12, QFont.Bold))
        trace_section = QVBoxLayout()
        trace_section.setContentsMargins(0, 0, 0, 0)
        trace_section.setSpacing(4)
        trace_section.addWidget(trace_title)

        trace_panel = QFrame()
        trace_panel.setObjectName("panel")
        trace_layout = QVBoxLayout()
        trace_layout.setContentsMargins(4, 3, 4, 4)

        self.trace = QTextEdit()
        self.trace.setReadOnly(True)
        self.trace.setLineWrapMode(QTextEdit.NoWrap)
        trace_layout.addWidget(self.trace)
        trace_panel.setLayout(trace_layout)
        trace_section.addWidget(trace_panel, 1)
        root.addLayout(trace_section, 3)

        jarvis_title = QLabel("JARVIS")
        jarvis_title.setFont(QFont("Consolas", 12, QFont.Bold))
        jarvis_section = QVBoxLayout()
        jarvis_section.setContentsMargins(0, 8, 0, 0)
        jarvis_section.setSpacing(4)
        jarvis_section.addWidget(jarvis_title)

        speech_panel = QFrame()
        speech_panel.setObjectName("panel")
        speech_layout = QVBoxLayout()
        speech_layout.setContentsMargins(4, 3, 4, 4)

        self.speech = QTextEdit()
        self.speech.setReadOnly(True)
        self.speech.setMinimumHeight(120)
        speech_layout.addWidget(self.speech)
        speech_panel.setLayout(speech_layout)
        jarvis_section.addWidget(speech_panel, 1)
        root.addLayout(jarvis_section, 1)

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open Crash Folder")
        button_font = open_btn.font()
        if button_font.pointSize() > 0:
            button_font.setPointSize(button_font.pointSize() + 1)
        open_btn.setFont(button_font)
        open_btn.clicked.connect(self.open_crash)

        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.setFont(button_font)
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
        diag_event('initial_state', self.current_state)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_status)
        self.timer.start(80)
        diag_event('timer_start', '80ms')
        diag_event('DiagnosticsWindow.__init__', 'complete')

    def move_to_right_monitor(self):
        screens = QGuiApplication.screens()
        target = max(screens, key=lambda s: s.geometry().x())
        geo = target.geometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)
        diag_event('move_to_right_monitor', f'screens={len(screens)}', f'target={geo.x()},{geo.y()},{geo.width()}x{geo.height()}', f'pos={x},{y}')

    def showEvent(self, event):
        super().showEvent(event)
        diag_event('showEvent', f'geom={self.geometry().x()},{self.geometry().y()},{self.geometry().width()}x{self.geometry().height()}')
        QTimer.singleShot(0, self.raise_)
        QTimer.singleShot(25, self.raise_)

    def dismiss_diagnostics(self):
        diag_event('dismiss_clicked')
        self.cleanup_and_exit()

    def cleanup_and_exit(self):
        diag_event('cleanup_and_exit', f'state={self.current_state}')
        try:
            self.timer.stop()
            diag_event('timer_stop', 'success')
        except Exception as exc:
            diag_event('timer_stop', f'failed={exc}')
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
        diag_event('closeEvent', 'accepted')
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

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def moveEvent(self, event):
        super().moveEvent(event)

    def render_voice_panel(self):

        lines = list(self.voice_history)
        if self.voice_current:
            lines.append(self.voice_current)
        self.speech.setPlainText("\n".join(lines))
        self.speech.verticalScrollBar().setValue(self.speech.verticalScrollBar().maximum())

    def append_state_trace(self, payload):
        cursor = self.trace.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.trace.setTextCursor(cursor)

        outer_line = "#0a2730"
        accent_line = "#00d8ff"
        band_background = "#071c24"
        band_text = "#d4af37"
        band_border_top = "#3feaff"
        band_border_bottom = "#0b2b35"

        viewport_width = self.trace.viewport().width()
        if viewport_width > 0 and self.trace.document().textWidth() != viewport_width:
            self.trace.document().setTextWidth(viewport_width)

        cursor.insertHtml(
            '<div style="margin: 8px 10px 10px 10px;">'
            f'<div style="font-size: 1px; line-height: 1px; background: {outer_line};">&nbsp;</div>'
            f'<div style="font-size: 2px; line-height: 2px; background: {accent_line};">&nbsp;</div>'
            '<p align="center" style="margin: 3px 0; padding: 5px 12px; '
            f'background: {band_background}; color: {band_text}; font-weight: 700; '
            f'border-top: 1px solid {band_border_top}; border-bottom: 1px solid {band_border_bottom};">'
            f'{html_escape(payload)}'
            '</p>'
            f'<div style="font-size: 2px; line-height: 2px; background: {accent_line};">&nbsp;</div>'
            f'<div style="font-size: 1px; line-height: 1px; background: {outer_line};">&nbsp;</div>'
            '</div>'
        )

        plain_block = QTextBlockFormat()
        plain_block.setAlignment(Qt.AlignLeft)
        plain_block.setTopMargin(0)
        plain_block.setBottomMargin(0)
        plain_block.setLeftMargin(10)
        plain_block.setRightMargin(0)
        cursor.insertBlock(plain_block, QTextCharFormat())
        self.trace.setTextCursor(cursor)
        self.trace.verticalScrollBar().setValue(self.trace.verticalScrollBar().maximum())

    def append_trace(self, payload):
        cursor = self.trace.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.trace.setTextCursor(cursor)

        stripped = payload.strip()
        signal_html = trace_signal_html(payload)

        if stripped and set(stripped) == {"-"}:
            self.trace.insertPlainText("\n")
        elif payload == "":
            self.trace.insertPlainText("\n")
        elif signal_html:
            self.trace.insertHtml(signal_html)
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
                self.summary.setText(summary_html(payload))

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
                    diag_event('state_transition', f'raw={state}', f'display={display}')
                    self.append_trace("")
                    self.append_state_trace(display)
                    self.append_trace("")
                    self._last_rendered_state = state
                else:
                    diag_event('state_transition_skipped', f'raw={state}')

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
                    diag_event('voice_final_append', final_line)
                self.render_voice_panel()

    def open_crash(self):
        if os.path.exists(CRASH_FOLDER):
            os.startfile(CRASH_FOLDER)

def main():
    parse_runtime_log_arg(sys.argv)
    diag_event('main', 'start', f'runtime_log={RUNTIME_LOG_FILE or "none"}')
    app = QApplication(sys.argv)
    w = DiagnosticsWindow()
    w.show()
    code = app.exec()
    diag_event('main', 'exit', f'code={code}')
    sys.exit(code)

if __name__ == "__main__":
    main()
