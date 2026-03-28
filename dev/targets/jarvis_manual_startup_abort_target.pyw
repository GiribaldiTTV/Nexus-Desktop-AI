import os
import sys
import time


ABORT_POLL_SECONDS = 0.1
ABORT_TIMEOUT_SECONDS = 30.0


def arg_value(argv, flag_name):
    for i, arg in enumerate(argv):
        if arg == flag_name and i + 1 < len(argv):
            return argv[i + 1]
    return ""


def append_runtime_line(runtime_log, message):
    if not runtime_log:
        return
    try:
        with open(runtime_log, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception:
        pass


def main():
    runtime_log = arg_value(sys.argv, "--runtime-log")
    startup_abort_signal = arg_value(sys.argv, "--startup-abort-signal")

    append_runtime_line(runtime_log, "MANUAL_TEST|startup abort target invoked")
    append_runtime_line(runtime_log, "MANUAL_TEST|Awaiting launcher startup abort signal")

    if not startup_abort_signal:
        raise RuntimeError("Manual startup-abort test requires --startup-abort-signal")

    deadline = time.monotonic() + ABORT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if os.path.exists(startup_abort_signal):
            append_runtime_line(runtime_log, "RENDERER_MAIN|STARTUP_ABORTED")
            append_runtime_line(runtime_log, "MANUAL_TEST|startup abort signal observed")
            return
        time.sleep(ABORT_POLL_SECONDS)

    raise RuntimeError("Manual startup-abort test timed out waiting for launcher abort signal")


if __name__ == "__main__":
    main()
