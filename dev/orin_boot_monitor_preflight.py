import datetime
import json
import os
import sys

from PySide6.QtGui import QGuiApplication


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_LOGS_DIR = os.path.join(ROOT_DIR, "dev", "logs")
BASE_LOG_ROOT = os.path.join(DEV_LOGS_DIR, "boot_monitor_preflight")
REPORTS_DIR = os.path.join(BASE_LOG_ROOT, "reports")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def line_status(ok, detail):
    return {"ok": bool(ok), "detail": detail}


def detect_branch_state():
    head_path = os.path.join(ROOT_DIR, ".git", "HEAD")
    try:
        with open(head_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "unavailable"


def screen_marker(screen):
    geometry = screen.geometry()
    return (
        f"{screen.name()}@x{geometry.x()}_y{geometry.y()}_w{geometry.width()}_h{geometry.height()}"
    )


def resolve_boot_screens(screens, primary_screen):
    center_screen = primary_screen
    other_screens = [screen for screen in screens if screen != center_screen]
    if len(other_screens) < 2:
        screens_sorted = sorted(screens, key=lambda screen: screen.geometry().x())
        return screens_sorted[0], screens_sorted[1], screens_sorted[2]
    other_sorted = sorted(other_screens, key=lambda screen: screen.geometry().x())
    return other_sorted[0], center_screen, other_sorted[1]


def run_preflight():
    ensure_dir(BASE_LOG_ROOT)
    ensure_dir(REPORTS_DIR)

    app = QGuiApplication(sys.argv)
    screens = QGuiApplication.screens()
    primary_screen = QGuiApplication.primaryScreen()

    checks = {
        "screen_count_at_least_three": line_status(len(screens) >= 3, f"screen_count={len(screens)}"),
        "primary_screen_present": line_status(primary_screen is not None, primary_screen.name() if primary_screen else "missing"),
    }

    left_screen = None
    center_screen = None
    right_screen = None

    if len(screens) >= 3 and primary_screen is not None:
        try:
            left_screen, center_screen, right_screen = resolve_boot_screens(screens, primary_screen)
        except Exception as exc:
            checks["boot_screen_resolution"] = line_status(False, f"resolution error: {type(exc).__name__}: {exc}")
        else:
            checks["boot_screen_resolution"] = line_status(
                True,
                f"left={screen_marker(left_screen)} | center={screen_marker(center_screen)} | right={screen_marker(right_screen)}",
            )

            left_x = left_screen.geometry().x()
            center_x = center_screen.geometry().x()
            right_x = right_screen.geometry().x()
            checks["left_center_right_order_valid"] = line_status(
                left_x < center_x < right_x,
                f"left_x={left_x} center_x={center_x} right_x={right_x}",
            )
            checks["center_matches_primary_screen"] = line_status(
                center_screen == primary_screen,
                f"center={center_screen.name()} primary={primary_screen.name()}",
            )

    checks["screen_markers_captured"] = line_status(
        bool(screens),
        " | ".join(screen_marker(screen) for screen in screens) if screens else "no screens reported",
    )

    app.quit()

    return {
        "branch_state": detect_branch_state(),
        "checks": checks,
    }


def build_report_text(report_path, result, overall_ok):
    lines = [
        "BOOT MONITOR PREFLIGHT",
        f"Report: {report_path}",
        f"Branch: {result['branch_state']}",
        f"Overall Result: {'PASS' if overall_ok else 'FAIL'}",
        "",
        "Checks:",
    ]

    for key, value in result["checks"].items():
        lines.append(f"  {'PASS' if value['ok'] else 'FAIL'} :: {key} :: {value['detail']}")

    return "\n".join(lines) + "\n"


def main(argv):
    open_report = "--open-report" in argv

    result = run_preflight()
    failures = [key for key, value in result["checks"].items() if not value["ok"]]
    overall_ok = not failures

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"BootMonitorPreflightReport_{stamp}.txt")
    json_path = os.path.join(REPORTS_DIR, f"BootMonitorPreflightReport_{stamp}.json")

    report_text = build_report_text(report_path, result, overall_ok)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(report_text)

    if open_report:
        try:
            os.startfile(report_path)
        except Exception:
            pass

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
