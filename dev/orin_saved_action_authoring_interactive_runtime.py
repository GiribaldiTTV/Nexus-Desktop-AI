import argparse
import datetime
import sys
from pathlib import Path

from PySide6.QtCore import QTimer

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import desktop.orin_desktop_main as runtime_main


AUTO_OPEN_OVERLAY = False
AUTO_OPEN_ATTEMPTS = 6
AUTO_OPEN_DELAY_MS = 2200
AUTO_OPEN_RETRY_MS = 700


def _build_logger(log_path: Path):
    log_path.parent.mkdir(parents=True, exist_ok=True)

    def _log(event: str) -> None:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{ts}] {event}\n")
            handle.flush()

    return _log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-log", required=True)
    parser.add_argument("--auto-open-overlay", action="store_true")
    args = parser.parse_args(argv)

    global AUTO_OPEN_OVERLAY
    AUTO_OPEN_OVERLAY = bool(args.auto_open_overlay)

    if AUTO_OPEN_OVERLAY:
        base_window_class = runtime_main.DesktopRuntimeWindow

        class InteractiveValidationDesktopRuntimeWindow(base_window_class):
            def __init__(self, *window_args, **window_kwargs):
                super().__init__(*window_args, **window_kwargs)
                self._interactive_auto_open_attempt = 0
                self._interactive_auto_open_show_rearm_scheduled = False
                self._interactive_auto_open_timer = QTimer(self)
                self._interactive_auto_open_timer.setSingleShot(True)
                self._interactive_auto_open_timer.timeout.connect(self._interactive_auto_open_overlay)
                runtime_main.runtime_milestone(
                    f"RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_SCHEDULED|delay_ms={AUTO_OPEN_DELAY_MS}"
                )
                self._interactive_auto_open_timer.start(AUTO_OPEN_DELAY_MS)

            def showEvent(self, event):
                super().showEvent(event)
                if self._interactive_auto_open_show_rearm_scheduled:
                    return
                self._interactive_auto_open_show_rearm_scheduled = True
                runtime_main.runtime_milestone(
                    "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_SHOW_REARMED"
                    f"|delay_ms={AUTO_OPEN_DELAY_MS}"
                )
                try:
                    runtime_main.runtime_milestone(
                        "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_SHOW_ATTEMPT"
                    )
                    self._interactive_auto_open_overlay()
                except Exception as exc:
                    runtime_main.runtime_milestone(
                        f"RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_SHOW_FAILED|reason={exc}"
                    )
                QTimer.singleShot(AUTO_OPEN_DELAY_MS, self._interactive_auto_open_overlay)

            def _interactive_overlay_visible(self) -> bool:
                return bool(getattr(self._command_model, "visible", False) and self._command_panel.isVisible())

            def _schedule_interactive_auto_open_retry(self, delay_ms: int) -> None:
                runtime_main.runtime_milestone(
                    "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_RETRY_SCHEDULED"
                    f"|delay_ms={delay_ms}|next_attempt={self._interactive_auto_open_attempt + 1}"
                )
                self._interactive_auto_open_timer.start(delay_ms)

            def _interactive_auto_open_overlay(self):
                if getattr(self, "_is_shutting_down", False):
                    return
                if self._interactive_overlay_visible():
                    runtime_main.runtime_milestone(
                        "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_SKIPPED|reason=already_visible"
                    )
                    return
                self._interactive_auto_open_attempt += 1
                try:
                    runtime_main.runtime_milestone(
                        "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_ATTEMPT"
                        f"|count={self._interactive_auto_open_attempt}"
                    )
                    self.open_command_overlay()
                    if self._interactive_overlay_visible():
                        runtime_main.runtime_milestone("RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPENED")
                        return
                    if self._interactive_auto_open_attempt < AUTO_OPEN_ATTEMPTS:
                        self._schedule_interactive_auto_open_retry(AUTO_OPEN_RETRY_MS)
                        return
                    runtime_main.runtime_milestone(
                        "RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_GAVE_UP|reason=overlay_not_visible"
                    )
                except Exception as exc:
                    if self._interactive_auto_open_attempt < AUTO_OPEN_ATTEMPTS:
                        self._schedule_interactive_auto_open_retry(AUTO_OPEN_RETRY_MS)
                    runtime_main.runtime_milestone(
                        f"RENDERER_MAIN|INTERACTIVE_VALIDATION_AUTO_OPEN_FAILED|reason={exc}"
                    )

        runtime_main.DesktopRuntimeWindow = InteractiveValidationDesktopRuntimeWindow

    runtime_log_path = Path(args.runtime_log).resolve()
    runtime_main.RUNTIME_LOG_FILE = str(runtime_log_path)
    runtime_main.runtime_milestone = _build_logger(runtime_log_path)
    sys.argv = [
        "desktop/orin_desktop_main.py",
        "--runtime-log",
        str(runtime_log_path),
    ]
    return runtime_main.main()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
