# Version 1.3.2 rev 11 launcher

import os
import sys
import time
import subprocess
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_SCRIPT = os.path.join(ROOT_DIR, "jarvis_desktop_test.py")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
CRASH_DIR = os.path.join(LOG_DIR, "crash")
STATUS_FILE = os.path.join(LOG_DIR, "diagnostics_status.txt")
STOP_SIGNAL_FILE = os.path.join(LOG_DIR, "diagnostics_stop.signal")
DIAGNOSTICS_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_diagnostics.pyw")
VOICE_SCRIPT = os.path.join(ROOT_DIR, "Audio", "jarvis_error_voice.py")

MAX_RECOVERY_ATTEMPTS = 3
RECOVERY_COOLDOWN_SECONDS = 1.2
COMPLETE_CLEANUP_DELAY_SECONDS = 0.35

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CRASH_DIR, exist_ok=True)

RUNTIME_FILE = os.path.join(
    LOG_DIR,
    f"Runtime_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)


def pythonw():
    exe = sys.executable
    alt = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return alt if os.path.exists(alt) else exe


def runtime(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    with open(RUNTIME_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def runtime_event(category, *parts):
    payload = "|".join(str(part) for part in parts)
    runtime(f"{category}|{payload}" if payload else category)


def reset_status():
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write("")
    runtime(f"Reset diagnostics status file: {STATUS_FILE}")
    runtime_event("FILE", "CREATE_OR_RESET", os.path.basename(STATUS_FILE), "SUCCESS", "startup")
    delete_file(STOP_SIGNAL_FILE, "startup reset")


def write_status(kind, msg):
    with open(STATUS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{kind}|{msg}\n")
    runtime(f"STATUS WRITE: {kind}|{msg}")
    runtime_event("STATUS", kind, msg)


def write_state(state):
    write_status("STATE", state)
    runtime_event("PHASE", state)


def delete_file(path, reason):
    try:
        if os.path.exists(path):
            os.remove(path)
            runtime(f"Deleted file ({reason}): {path}")
            runtime_event("FILE", "DELETE", os.path.basename(path), "SUCCESS", reason)
            return True
        runtime(f"File already absent ({reason}): {path}")
        runtime_event("FILE", "DELETE", os.path.basename(path), "ABSENT", reason)
        return False
    except Exception as exc:
        runtime(f"Failed deleting file ({reason}): {path} :: {exc}")
        runtime_event("FILE", "DELETE", os.path.basename(path), "FAILED", reason, exc)
        return False


def crash_log(message, attempts, last_code):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(CRASH_DIR, f"Crash_{ts}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("JARVIS CRASH REPORT\n")
        f.write(f"Time: {ts}\n")
        f.write(f"Python: {pythonw()}\n")
        f.write(f"Working Directory: {ROOT_DIR}\n")
        f.write(f"Renderer: {TARGET_SCRIPT}\n")
        f.write(f"Max Recovery Attempts: {MAX_RECOVERY_ATTEMPTS}\n")
        f.write(f"Attempts Used: {attempts}\n")
        f.write(f"Last Exit Code: {last_code}\n")
        f.write(f"Runtime Log: {RUNTIME_FILE}\n")
        f.write(f"Failure Reason: {message}\n")
    runtime(f"Crash log written: {path}")
    runtime_event("STATUS", "SUCCESS", "CRASH_LOG_WRITTEN", os.path.basename(path))
    return path


def launch_diag():
    runtime("Launching diagnostics UI")
    runtime_event("STATUS", "START", "DIAGNOSTICS_UI")
    write_status("TRACE", "Launching diagnostics UI")
    proc = subprocess.Popen([pythonw(), DIAGNOSTICS_SCRIPT])
    runtime(f"Diagnostics PID: {proc.pid}")
    runtime_event("STATUS", "SUCCESS", "DIAGNOSTICS_UI", f"PID={proc.pid}")
    return proc


def speak(spoken_text, display_text=None):
    if not os.path.exists(VOICE_SCRIPT):
        runtime(f"Voice script missing: {VOICE_SCRIPT}")
        runtime_event("STATUS", "FAIL", "VOICE_SCRIPT", "MISSING")
        return 1

    display_text = display_text or spoken_text
    runtime(f"VOICE: {spoken_text}")
    runtime_event("VOICE", "START", spoken_text)
    write_status("VOICE_CLEAR", "")

    cmd = [
        pythonw(),
        VOICE_SCRIPT,
        "--text", spoken_text,
        "--display-text", display_text,
        "--status-file", STATUS_FILE,
        "--stop-signal", STOP_SIGNAL_FILE,
    ]
    runtime(f"VOICE CMD: {' '.join(cmd[2:])}")
    result = subprocess.run(cmd)
    runtime(f"VOICE EXIT CODE: {result.returncode} :: {spoken_text}")
    runtime_event("VOICE", "END", spoken_text, f"EXIT={result.returncode}")
    return result.returncode


def run_renderer():
    runtime(f"Starting renderer: {TARGET_SCRIPT}")
    runtime_event("STATUS", "START", "RENDERER_PROCESS")
    proc = subprocess.Popen([pythonw(), TARGET_SCRIPT])
    runtime(f"Renderer PID: {proc.pid}")
    runtime_event("STATUS", "SUCCESS", "RENDERER_PROCESS_SPAWN", f"PID={proc.pid}")
    proc.wait()
    runtime(f"Renderer exit code: {proc.returncode}")
    runtime_event("STATUS", "END", "RENDERER_PROCESS", f"EXIT={proc.returncode}")
    return proc.returncode


def finalize_failure(attempts_used, last_code):
    runtime("Beginning final immersive shutdown sequence")
    runtime_event("STATUS", "START", "FINAL_IMMERSIVE_SHUTDOWN")
    speak("Recovery failed.")
    speak("Shutting down.")
    runtime("Final immersive shutdown sequence finished")
    runtime_event("STATUS", "SUCCESS", "FINAL_IMMERSIVE_SHUTDOWN")

    write_state("COMPLETE")
    runtime("Backend completion reached after final voice line")

    if COMPLETE_CLEANUP_DELAY_SECONDS > 0:
        runtime(f"Waiting {COMPLETE_CLEANUP_DELAY_SECONDS:.2f}s before backend cleanup")
        time.sleep(COMPLETE_CLEANUP_DELAY_SECONDS)

    delete_file(STOP_SIGNAL_FILE, "backend completion")
    delete_file(STATUS_FILE, "backend completion")

    crash_log("Renderer failed after maximum recovery attempts.", attempts_used, last_code or -1)


def main():
    reset_status()

    runtime("==== Jarvis runtime started ====")
    runtime_event("STATUS", "START", "LAUNCHER_RUNTIME")
    runtime(f"Python executable: {pythonw()}")
    runtime(f"Working directory: {ROOT_DIR}")
    runtime(f"Renderer target: {TARGET_SCRIPT}")

    diagnostics_opened = False
    recovery_voice_spoken = False
    last_code = None

    for attempt in range(1, MAX_RECOVERY_ATTEMPTS + 1):
        runtime(f"Renderer launch attempt {attempt}/{MAX_RECOVERY_ATTEMPTS}")
        runtime_event("STATUS", "START", "RECOVERY_ATTEMPT", f"INDEX={attempt}", f"MAX={MAX_RECOVERY_ATTEMPTS}")
        write_status("TRACE", f"Renderer launch attempt {attempt}/{MAX_RECOVERY_ATTEMPTS}")
        time.sleep(0.18)

        last_code = run_renderer()

        if last_code == 0:
            runtime("Renderer exited normally")
            runtime_event("STATUS", "SUCCESS", "RECOVERY_ATTEMPT", f"INDEX={attempt}", "RENDERER_EXIT=0")
            write_status("TRACE", "Renderer exited normally")
            runtime_event("STATUS", "SUCCESS", "LAUNCHER_RUNTIME")
            return 0

        runtime("Renderer exited unexpectedly")
        runtime_event("STATUS", "FAIL", "RECOVERY_ATTEMPT", f"INDEX={attempt}", f"RENDERER_EXIT={last_code}")
        write_status("SUMMARY", "Desktop renderer exited unexpectedly")
        write_status("TRACE", f"Renderer exited unexpectedly with code {last_code}")

        if not diagnostics_opened:
            write_state("STARTED")
            write_status("TRACE", "Scanning runtime environment")
            time.sleep(0.18)
            write_status("TRACE", "Checking desktop engine")
            time.sleep(0.18)
            launch_diag()
            speak("Uhm..... Sir, I seem to be malfunctioning.")
            diagnostics_opened = True

        if attempt < MAX_RECOVERY_ATTEMPTS:
            runtime(f"Preparing recovery attempt {attempt}")
            runtime_event("STATUS", "START", "RECOVERY_COOLDOWN", f"INDEX={attempt}", f"SECONDS={RECOVERY_COOLDOWN_SECONDS:.1f}")
            write_state("RECOVERING")
            write_status("TRACE", f"Attempting recovery ({attempt}/{MAX_RECOVERY_ATTEMPTS})")
            write_status("TRACE", f"Cooldown before next attempt: {RECOVERY_COOLDOWN_SECONDS:.1f}s")

            if not recovery_voice_spoken:
                speak("Attempting recovery.")
                recovery_voice_spoken = True

            time.sleep(RECOVERY_COOLDOWN_SECONDS)
            runtime_event("STATUS", "SUCCESS", "RECOVERY_COOLDOWN", f"INDEX={attempt}")

    runtime("All recovery attempts exhausted")
    runtime_event("STATUS", "FAIL", "RECOVERY_PIPELINE", "MAX_ATTEMPTS_EXHAUSTED")
    write_status("TRACE", "Recovery attempts exhausted")
    finalize_failure(MAX_RECOVERY_ATTEMPTS, last_code)
    runtime_event("STATUS", "SUCCESS", "LAUNCHER_RUNTIME", "FAILURE_FLOW_COMPLETE")


if __name__ == "__main__":
    main()
