import os
import sys
import time


ABORT_POLL_SECONDS = 0.1
ABORT_TIMEOUT_SECONDS = 30.0
SEQUENCE_ENV = "JARVIS_MANUAL_MIXED_SEQUENCE"
STATE_FILE_NAME = "manual_mixed_sequence_state.txt"


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


def read_step_index(state_path):
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            return max(0, int(f.read().strip() or "0"))
    except Exception:
        return 0


def write_step_index(state_path, value):
    with open(state_path, "w", encoding="utf-8") as f:
        f.write(str(value))


def delete_file(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def crash_generic():
    raise RuntimeError("Manual mixed-sequence crash step")


def crash_phase_a():
    raise RuntimeError("persistent startup failure")


def crash_phase_b():
    raise RuntimeError("persistent startup failure")


def crash_phase_c():
    raise RuntimeError("persistent startup failure")


def crash_phase_beta():
    raise ValueError("crash beta")


CRASH_STEP_HANDLERS = {
    "crash": crash_generic,
    "crash_a": crash_phase_a,
    "crash_b": crash_phase_b,
    "crash_c": crash_phase_c,
    "crash_beta": crash_phase_beta,
}


def parse_sequence():
    raw = os.environ.get(SEQUENCE_ENV, "").strip().lower()
    if not raw:
        raise RuntimeError(f"Missing {SEQUENCE_ENV}")

    sequence = [token.strip() for token in raw.split(",") if token.strip()]
    allowed = set(CRASH_STEP_HANDLERS) | {"abort", "success"}
    if not sequence or any(token not in allowed for token in sequence):
        raise RuntimeError(f"Invalid {SEQUENCE_ENV}: {raw}")
    return sequence


def wait_for_abort(startup_abort_signal, runtime_log):
    if not startup_abort_signal:
        raise RuntimeError("Mixed sequence abort step requires --startup-abort-signal")

    deadline = time.monotonic() + ABORT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if os.path.exists(startup_abort_signal):
            append_runtime_line(runtime_log, "RENDERER_MAIN|STARTUP_ABORTED")
            append_runtime_line(runtime_log, "MANUAL_TEST|mixed sequence startup abort signal observed")
            return
        time.sleep(ABORT_POLL_SECONDS)

    raise RuntimeError("Mixed sequence abort step timed out waiting for launcher abort signal")


def delete_state_if_last_step(state_path, step_index, sequence):
    if step_index >= len(sequence) - 1:
        delete_file(state_path)


def main():
    runtime_log = arg_value(sys.argv, "--runtime-log")
    startup_abort_signal = arg_value(sys.argv, "--startup-abort-signal")

    sequence = parse_sequence()
    state_root = os.path.dirname(runtime_log) if runtime_log else os.getcwd()
    state_path = os.path.join(state_root, STATE_FILE_NAME)

    step_index = read_step_index(state_path)
    write_step_index(state_path, step_index + 1)
    outcome = sequence[step_index] if step_index < len(sequence) else sequence[-1]

    append_runtime_line(runtime_log, f"MANUAL_TEST|mixed sequence target invoked|STEP={step_index + 1}|OUTCOME={outcome.upper()}")

    if outcome in CRASH_STEP_HANDLERS:
        delete_state_if_last_step(state_path, step_index, sequence)
        sys.stderr.write(f"MANUAL_TEST|Mixed sequence crash step|TOKEN={outcome}\n")
        sys.stderr.flush()
        CRASH_STEP_HANDLERS[outcome]()

    if outcome == "abort":
        delete_state_if_last_step(state_path, step_index, sequence)
        append_runtime_line(runtime_log, "MANUAL_TEST|Awaiting launcher startup abort signal")
        wait_for_abort(startup_abort_signal, runtime_log)
        return

    append_runtime_line(runtime_log, "MANUAL_TEST|mixed sequence success step")
    delete_file(state_path)


if __name__ == "__main__":
    main()
