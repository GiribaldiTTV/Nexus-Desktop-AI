import sys
import os
import asyncio
import tempfile
import subprocess
import shutil
import math
import wave
import struct
import random

import edge_tts
from PySide6.QtCore import QUrl, QEventLoop, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QApplication


DEFAULT_TEXT = "Uhm..... Sir, I seem to be malfunctioning."


def hidden_subprocess_kwargs():
    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }

    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        kwargs["startupinfo"] = startupinfo
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    return kwargs


def write_status(status_file: str, stop_signal_file: str, kind: str, msg: str):
    if not status_file:
        return
    if stop_signal_file and os.path.exists(stop_signal_file):
        return
    if not os.path.exists(status_file):
        return
    try:
        with open(status_file, "a", encoding="utf-8") as f:
            f.write(f"{kind}|{msg}\n")
    except Exception:
        pass


class JarvisErrorSpeaker:
    def __init__(self, status_file: str = "", display_text: str = "", stop_signal_file: str = ""):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self.audio_output.setVolume(0.40)
        self.status_file = status_file
        self.display_text = display_text or ""
        self.stop_signal_file = stop_signal_file or ""
        self.last_sync = ""
        self.media_started = False
        self.sync_timer = None
        self.stop_requested = False

    def should_stop(self):
        return bool(self.stop_signal_file) and os.path.exists(self.stop_signal_file)

    def build_general_sync_schedule(self, text: str, duration_ms: int):
        words = text.split()
        if not words:
            return []

        total_chars = sum(max(1, len(w.strip())) for w in words)
        if total_chars <= 0:
            total_chars = len(words)

        schedule = []
        cumulative = ""
        elapsed = 0.0

        for i, word in enumerate(words):
            weight = max(1, len(word.strip()))
            portion = weight / total_chars
            cumulative = f"{cumulative} {word}".strip()

            # Earlier than before so words appear during speech, not after it.
            target_ms = int(elapsed + (portion * duration_ms * 0.22))
            if i == 0:
                target_ms = max(80, target_ms)

            schedule.append((target_ms, cumulative))
            elapsed += portion * duration_ms

        return schedule

    def build_split_uhm_schedule(self, display_text: str, first_ms: int, second_ms: int):
        words = display_text.split()
        if len(words) < 2:
            return self.build_general_sync_schedule(display_text, first_ms + second_ms)

        first_word = words[0]
        rest_words = words[1:]

        schedule = []
        schedule.append((max(120, int(first_ms * 0.42)), first_word))

        cumulative = first_word
        total_chars = sum(max(1, len(w.strip())) for w in rest_words)
        elapsed = float(first_ms)

        for i, word in enumerate(rest_words):
            weight = max(1, len(word.strip()))
            portion = weight / total_chars if total_chars else 1.0 / max(1, len(rest_words))
            cumulative = f"{cumulative} {word}".strip()

            target_ms = int(elapsed + (portion * second_ms * 0.32))
            if i == 0:
                target_ms = max(target_ms, int(first_ms + 90))

            schedule.append((target_ms, cumulative))
            elapsed += portion * second_ms

        return schedule

    async def synthesize_segment(self, text: str, rate: str):
        fd, source_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        communicate = edge_tts.Communicate(
            text=text,
            voice="en-GB-RyanNeural",
            rate=rate,
            pitch="-2Hz",
        )
        await communicate.save(source_path)
        if not os.path.exists(source_path):
            raise RuntimeError(f"audio file was not created: {source_path}")
        return source_path

    def concat_audio_files(self, input_paths):
        exe = ffmpeg_exe()
        if not exe or not input_paths:
            return None

        fd, out_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        cmd = [exe]
        for path in input_paths:
            cmd.extend(["-i", path])

        filter_inputs = "".join(f"[{i}:a]" for i in range(len(input_paths)))
        cmd.extend([
            "-filter_complex", f"{filter_inputs}concat=n={len(input_paths)}:v=0:a=1[outa]",
            "-map", "[outa]",
            out_path,
        ])

        result = subprocess.run(cmd, **hidden_subprocess_kwargs())
        if result.returncode != 0 or not os.path.exists(out_path):
            try:
                os.remove(out_path)
            except Exception:
                pass
            return None
        return out_path

    def create_powerdown_tail(self):
        fd, out_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        sr = 44100
        duration = 0.40
        frames = int(sr * duration)

        try:
            with wave.open(out_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)

                for i in range(frames):
                    t = i / sr
                    freq = max(55.0, 420.0 - (340.0 * (t / duration)))
                    tone = math.sin(2.0 * math.pi * freq * t)
                    static = (random.random() * 2.0 - 1.0)
                    envelope = max(0.0, 1.0 - (t / duration)) ** 1.8
                    sample = (tone * 0.65 + static * 0.18) * envelope
                    value = max(-32767, min(32767, int(sample * 32767)))
                    wf.writeframesraw(struct.pack("<h", value))
            return out_path
        except Exception:
            try:
                os.remove(out_path)
            except Exception:
                pass
            return None

    async def prepare_audio(self, spoken_text: str, display_text: str):
        temp_paths = []
        try:
            normalized_display = normalize_line(display_text or spoken_text)

            if normalized_display == "Uhm..... Sir, I seem to be malfunctioning.":
                # rev 18b recovery: guarantee audible playback first, refine segmentation later
                source_path = await self.synthesize_segment("Uhm..... Sir, I seem to be malfunctioning.", "-10%")
                temp_paths.append(source_path)

                duration_ms = max(1, int(get_duration_seconds(source_path) * 1000))
                schedule = self.build_general_sync_schedule("Uhm..... Sir, I seem to be malfunctioning.", duration_ms)
                return source_path, temp_paths, schedule

            source_path = await self.synthesize_segment(spoken_text, "-10%")
            temp_paths.append(source_path)

            duration_ms = max(1, int(get_duration_seconds(source_path) * 1000))
            schedule = self.build_general_sync_schedule(display_text or spoken_text, duration_ms)
            return source_path, temp_paths, schedule

        except Exception:
            for path in temp_paths:
                try:
                    os.remove(path)
                except Exception:
                    pass
            raise

    async def speak(self, text: str):
        base_audio_path = None
        temp_paths = []
        processed_path = None

        try:
            base_audio_path, temp_paths, schedule = await self.prepare_audio(text, self.display_text or text)
            duration = get_duration_seconds(base_audio_path)

            if duration < 1.2:
                playback_path = base_audio_path
            else:
                effected = apply_error_effect(base_audio_path)
                playback_path = effected if effected and os.path.exists(effected) else base_audio_path

            if playback_path != base_audio_path:
                processed_path = playback_path

            loop = QEventLoop()

            def push_sync():
                if self.should_stop():
                    self.stop_requested = True
                    if self.sync_timer:
                        self.sync_timer.stop()
                    self.player.stop()
                    loop.quit()
                    return

                if not self.media_started:
                    return

                position = self.player.position()
                newest = self.last_sync

                for target_ms, content in schedule:
                    if position >= target_ms:
                        newest = content
                    else:
                        break

                if newest != self.last_sync:
                    self.last_sync = newest
                    write_status(self.status_file, self.stop_signal_file, "VOICE_SYNC", newest)

            def on_position_changed(_pos):
                push_sync()

            def on_playback_state_changed(state):
                if state == QMediaPlayer.PlaybackState.PlayingState and not self.media_started:
                    self.media_started = True

            def on_media_status_changed(status):
                if status == QMediaPlayer.MediaStatus.EndOfMedia:
                    if self.sync_timer:
                        self.sync_timer.stop()
                    if not self.should_stop():
                        final_text = self.display_text or text
                        write_status(self.status_file, self.stop_signal_file, "VOICE_FINAL", final_text)
                    loop.quit()
                elif status == QMediaPlayer.MediaStatus.InvalidMedia:
                    if self.sync_timer:
                        self.sync_timer.stop()
                    loop.quit()

            self.player.positionChanged.connect(on_position_changed)
            self.player.playbackStateChanged.connect(on_playback_state_changed)
            self.player.mediaStatusChanged.connect(on_media_status_changed)

            self.sync_timer = QTimer()
            self.sync_timer.timeout.connect(push_sync)
            self.sync_timer.start(30)

            self.player.setSource(QUrl.fromLocalFile(playback_path))
            self.player.play()

            QTimer.singleShot(25000, loop.quit)
            loop.exec()

            self.player.stop()
            self.player.setSource(QUrl())
            return 0

        finally:
            for path in temp_paths + ([processed_path] if processed_path else []):
                if path:
                    try:
                        os.remove(path)
                    except Exception:
                        pass


def parse_args(argv):
    text = None
    display_text = None
    status_file = ""
    stop_signal_file = ""
    i = 1
    positional = []

    while i < len(argv):
        arg = argv[i]

        if arg == "--text" and i + 1 < len(argv):
            text = argv[i + 1]
            i += 2
            continue

        if arg == "--display-text" and i + 1 < len(argv):
            display_text = argv[i + 1]
            i += 2
            continue

        if arg == "--status-file" and i + 1 < len(argv):
            status_file = argv[i + 1]
            i += 2
            continue

        if arg == "--stop-signal" and i + 1 < len(argv):
            stop_signal_file = argv[i + 1]
            i += 2
            continue

        if arg in {"--mode", "--effect"} and i + 1 < len(argv):
            i += 2
            continue

        positional.append(arg)
        i += 1

    if text is None:
        text = os.environ.get("JARVIS_VOICE_TEXT")

    if not text and positional:
        text = " ".join(positional)

    normalized_text = normalize_line(text or DEFAULT_TEXT)
    normalized_display = normalize_line(display_text or normalized_text)
    return normalized_text, normalized_display, status_file, stop_signal_file


def normalize_line(text: str) -> str:
    lowered = text.strip().lower()
    mapping = {
        "um..... sir, i seem to be malfunctioning.": "Uhm..... Sir, I seem to be malfunctioning.",
        "uhm..... sir, i seem to be malfunctioning.": "Uhm..... Sir, I seem to be malfunctioning.",
        "uhhhhmmmmmmmm..... sir, i seem to be malfunctioning.": "Uhm..... Sir, I seem to be malfunctioning.",
        "recovery failed.": "Recovery failed.",
        "attempting fix.": "Attempting fix.",
        "fix failed.": "Fix failed.",
        "shutting down.": "Shutting down.",
    }
    return mapping.get(lowered, text)


def ffmpeg_exe():
    return shutil.which("ffmpeg") or ""


def ffprobe_exe():
    return shutil.which("ffprobe") or ""


def get_duration_seconds(path):
    exe = ffprobe_exe()
    if not exe:
        return 0.0

    cmd = [
        exe,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]

    result = subprocess.run(cmd, **hidden_subprocess_kwargs())

    if result.returncode != 0:
        return 0.0

    try:
        return max(0.0, float(result.stdout.strip()))
    except Exception:
        return 0.0


def seg_filter(level):
    if level == "extreme":
        return (
            "highpass=f=90,"
            "lowpass=f=2850,"
            "acrusher=bits=5:mix=0.95:mode=lin,"
            "chorus=0.86:0.94:80|62:0.42|0.28:0.90|0.94:0.34|0.44,"
            "tremolo=f=15:d=0.68,"
            "aphaser=in_gain=0.68:out_gain=0.88:delay=2.8:decay=0.64:speed=1.8,"
            "aecho=0.88:0.72:28:0.40,"
            "volume=2.25"
        )

    return (
        "highpass=f=100,"
        "lowpass=f=3200,"
        "acrusher=bits=7:mix=0.78:mode=lin,"
        "chorus=0.80:0.90:70|52:0.36|0.24:0.86|0.92:0.30|0.36,"
        "tremolo=f=12:d=0.54,"
        "aphaser=in_gain=0.60:out_gain=0.80:delay=2.2:decay=0.55:speed=1.4,"
        "aecho=0.82:0.55:18:0.30,"
        "acompressor=threshold=-18dB:ratio=2.8:attack=5:release=65,"
        "volume=2.05"
    )


def build_chunked_filter_complex(duration, segment_len=0.40, fade_len=0.050):
    pattern = ["raised", "extreme", "raised", "raised", "extreme", "raised", "extreme", "raised"]
    segments = []
    count = max(1, math.ceil(duration / segment_len))

    for i in range(count):
        start = i * segment_len
        end = min(duration, (i + 1) * segment_len)
        if end <= start:
            continue

        level = pattern[i % len(pattern)]
        label = f"s{i}"
        seg_dur = end - start
        chain = seg_filter(level)

        actual_fade = min(fade_len, max(0.010, seg_dur / 4))
        fade_out_start = max(0.0, seg_dur - actual_fade)

        segments.append(
            f"[0:a]atrim=start={start:.3f}:end={end:.3f},"
            f"asetpts=PTS-STARTPTS,{chain},"
            f"afade=t=in:st=0:d={actual_fade:.3f},"
            f"afade=t=out:st={fade_out_start:.3f}:d={actual_fade:.3f}"
            f"[{label}]"
        )

    concat_inputs = "".join(f"[s{i}]" for i in range(len(segments)))
    return ";".join(segments + [f"{concat_inputs}concat=n={len(segments)}:v=0:a=1[outa]"])


def apply_error_effect(source_path):
    exe = ffmpeg_exe()
    if not exe:
        return None

    duration = get_duration_seconds(source_path)
    if duration <= 0:
        return None

    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    filter_complex = build_chunked_filter_complex(duration)

    cmd = [
        exe,
        "-y",
        "-i", source_path,
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        out_path,
    ]

    result = subprocess.run(cmd, **hidden_subprocess_kwargs())

    if result.returncode != 0 or not os.path.exists(out_path):
        try:
            os.remove(out_path)
        except Exception:
            pass
        return None

    return out_path


if __name__ == "__main__":
    text, display_text, status_file, stop_signal_file = parse_args(sys.argv)
    speaker = JarvisErrorSpeaker(
        status_file=status_file,
        display_text=display_text,
        stop_signal_file=stop_signal_file,
    )
    sys.exit(asyncio.run(speaker.speak(text)))
