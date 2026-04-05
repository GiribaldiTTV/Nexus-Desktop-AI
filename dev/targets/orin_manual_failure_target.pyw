import os
import sys


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
    append_runtime_line(runtime_log, "MANUAL_TEST|launcher failure target invoked")
    sys.stderr.write("MANUAL_TEST|Deterministic launcher-path failure target invoked\n")
    sys.stderr.flush()
    raise RuntimeError("Manual launcher-path diagnostics test failure")


if __name__ == "__main__":
    main()
