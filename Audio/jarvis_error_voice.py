import sys
import os
import asyncio
import tempfile
import subprocess
import shutil
import math
import struct
import wave

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

        self.audio_output.setVolume(0.60)
        self.status_file = status_file
        self.display_text = display_text or ""
        self.stop_signal_file = stop_signal_file or ""
        self.last_sync = ""
        self.media_started = False
        self.sync_timer = None

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

    async def synthesize_segment(self, text: str, rate: str, pitch: str = "-2Hz"):
        fd, source_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        communicate = edge_tts.Communicate(
            text=text,
            voice="en-GB-RyanNeural",
            rate=rate,
            pitch=pitch,
        )
        await communicate.save(source_path)
        if not os.path.exists(source_path):
            raise RuntimeError(f"audio file was not created: {source_path}")
        return source_path

    async def synthesize_shutdown_source(self):
        temp_paths = []
        try:
            # Preserve the natural whole-line prosody, then reshape only the
            # active speech region so the slowdown lands on "down" without
            # making the second word sound like a separate utterance.
            source_path = await self.synthesize_segment("Shutting down.", "-10%")
            temp_paths.append(source_path)

            slowed_path = apply_shutdown_source_slowdown(source_path)
            if not slowed_path:
                raise RuntimeError("failed to assemble shutdown slowed source")

            temp_paths.append(slowed_path)
            return slowed_path, temp_paths
        except Exception:
            for path in temp_paths:
                try:
                    os.remove(path)
                except Exception:
                    pass
            raise

    async def prepare_audio(self, spoken_text: str, display_text: str):
        temp_paths = []
        try:
            normalized_display = normalize_line(display_text or spoken_text)
            effect_mode = effect_mode_for_display_text(normalized_display)

            if normalized_display == "Uhm..... Sir, I seem to be malfunctioning.":
                # rev 18b recovery: guarantee audible playback first, refine segmentation later
                source_path = await self.synthesize_segment("Uhm..... Sir, I seem to be malfunctioning.", "-10%")
                temp_paths.append(source_path)

                duration_ms = max(1, int(get_duration_seconds(source_path) * 1000))
                schedule = self.build_general_sync_schedule("Uhm..... Sir, I seem to be malfunctioning.", duration_ms)
                return source_path, temp_paths, schedule, effect_mode

            if normalized_display == "Shutting down.":
                source_path, generated_paths = await self.synthesize_shutdown_source()
                temp_paths.extend(generated_paths)

                duration_ms = max(1, int(get_duration_seconds(source_path) * 1000))
                schedule = self.build_general_sync_schedule(normalized_display, duration_ms)
                return source_path, temp_paths, schedule, effect_mode

            source_path = await self.synthesize_segment(spoken_text, "-10%")
            temp_paths.append(source_path)

            duration_ms = max(1, int(get_duration_seconds(source_path) * 1000))
            schedule = self.build_general_sync_schedule(display_text or spoken_text, duration_ms)
            return source_path, temp_paths, schedule, effect_mode

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
        position_changed_connected = False
        playback_state_connected = False
        media_status_connected = False

        try:
            self.last_sync = ""
            self.media_started = False
            base_audio_path, temp_paths, schedule, effect_mode = await self.prepare_audio(text, self.display_text or text)
            duration = get_duration_seconds(base_audio_path)

            if duration < 1.2:
                playback_path = base_audio_path
            else:
                effected = apply_error_effect(base_audio_path)
                playback_path = effected if effected and os.path.exists(effected) else base_audio_path

            if playback_path != base_audio_path:
                processed_path = playback_path

            playback_duration_ms = max(1, int(get_duration_seconds(playback_path) * 1000))
            base_duration_ms = max(1, int(get_duration_seconds(base_audio_path) * 1000))
            if schedule and playback_duration_ms != base_duration_ms:
                stretch_ratio = playback_duration_ms / base_duration_ms
                schedule = [
                    (max(1, int(target_ms * stretch_ratio)), content)
                    for target_ms, content in schedule
                ]

            loop = QEventLoop()

            def push_sync():
                if self.should_stop():
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
            position_changed_connected = True
            self.player.playbackStateChanged.connect(on_playback_state_changed)
            playback_state_connected = True
            self.player.mediaStatusChanged.connect(on_media_status_changed)
            media_status_connected = True

            self.sync_timer = QTimer()
            self.sync_timer.timeout.connect(push_sync)
            self.sync_timer.start(30)

            self.player.setSource(QUrl.fromLocalFile(playback_path))
            self.player.play()

            QTimer.singleShot(25000, loop.quit)
            loop.exec()

            return 0

        finally:
            if self.sync_timer:
                try:
                    self.sync_timer.stop()
                    self.sync_timer.timeout.disconnect(push_sync)
                except Exception:
                    pass
                self.sync_timer = None
            self.player.stop()
            self.player.setSource(QUrl())
            if position_changed_connected:
                try:
                    self.player.positionChanged.disconnect(on_position_changed)
                except Exception:
                    pass
            if playback_state_connected:
                try:
                    self.player.playbackStateChanged.disconnect(on_playback_state_changed)
                except Exception:
                    pass
            if media_status_connected:
                try:
                    self.player.mediaStatusChanged.disconnect(on_media_status_changed)
                except Exception:
                    pass
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


def effect_mode_for_display_text(normalized_display):
    if normalized_display == "Shutting down.":
        return "shutdown"
    return "generic"


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


def atempo_chain_for_factor(factor):
    factor = max(0.01, float(factor))
    filters = []

    while factor < 0.5:
        filters.append("atempo=0.500")
        factor /= 0.5

    while factor > 2.0:
        filters.append("atempo=2.000")
        factor /= 2.0

    filters.append(f"atempo={factor:.3f}")
    return ",".join(filters)


def convert_audio_to_wav(source_path):
    exe = ffmpeg_exe()
    if not exe:
        return ""

    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    result = subprocess.run(
        [exe, "-y", "-i", source_path, out_path],
        **hidden_subprocess_kwargs()
    )

    if result.returncode != 0 or not os.path.exists(out_path):
        try:
            os.remove(out_path)
        except Exception:
            pass
        return ""

    return out_path


def detect_active_audio_region(path, window_ms=25, rms_threshold=10.0):
    analysis_wav = convert_audio_to_wav(path)
    if not analysis_wav:
        duration = get_duration_seconds(path)
        return 0.0, duration

    try:
        with wave.open(analysis_wav, "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
            raw_data = wav_file.readframes(frame_count)

        if sample_width != 2:
            duration = frame_count / float(frame_rate or 1)
            return 0.0, duration

        samples = struct.unpack("<" + ("h" * (len(raw_data) // 2)), raw_data)
        if channels > 1:
            mono_samples = []
            for i in range(0, len(samples), channels):
                mono_samples.append(sum(samples[i:i + channels]) / channels)
            samples = mono_samples

        step = max(1, int(frame_rate * (window_ms / 1000.0)))
        active_indexes = []
        for index, start in enumerate(range(0, len(samples), step)):
            chunk = samples[start:start + step]
            if not chunk:
                continue
            mean_sq = sum(float(sample) * float(sample) for sample in chunk) / len(chunk)
            rms = math.sqrt(mean_sq)
            if rms >= rms_threshold:
                active_indexes.append(index)

        total_duration = len(samples) / float(frame_rate or 1)
        if not active_indexes:
            return 0.0, total_duration

        start_time = active_indexes[0] * (window_ms / 1000.0)
        end_time = min(total_duration, (active_indexes[-1] + 1) * (window_ms / 1000.0))
        return max(0.0, start_time), max(start_time, end_time)
    finally:
        try:
            os.remove(analysis_wav)
        except Exception:
            pass


def weighted_word_boundary_ratio(text: str, word_index: int) -> float:
    words = text.split()
    if not words:
        return 0.0

    def word_weight(word: str) -> int:
        cleaned = "".join(ch for ch in word if ch.isalnum())
        return max(1, len(cleaned) or len(word.strip()) or 1)

    total_weight = sum(word_weight(word) for word in words)
    if total_weight <= 0:
        return 0.0

    boundary_weight = sum(word_weight(word) for word in words[:word_index])
    return max(0.0, min(1.0, boundary_weight / total_weight))


def build_progressive_tempo_filter_complex(duration, segment_specs, fade_len=0.050, source_start=0.0):
    segments = []
    start = 0.0

    for index, spec in enumerate(segment_specs):
        end_ratio = max(0.0, min(1.0, float(spec["end_ratio"])))
        end = duration * end_ratio if index < len(segment_specs) - 1 else duration
        if end <= start:
            continue

        label = f"s{index}"
        seg_dur = end - start
        level = spec.get("level", "raised")
        tempo_factor = spec.get("tempo", 1.0)
        chain = f"{atempo_chain_for_factor(tempo_factor)},{seg_filter(level)}"

        actual_fade = min(fade_len, max(0.010, seg_dur / 4))
        fade_out_start = max(0.0, seg_dur - actual_fade)

        segments.append(
            f"[0:a]atrim=start={source_start + start:.3f}:end={source_start + end:.3f},"
            f"asetpts=PTS-STARTPTS,{chain},"
            f"afade=t=in:st=0:d={actual_fade:.3f},"
            f"afade=t=out:st={fade_out_start:.3f}:d={actual_fade:.3f}"
            f"[{label}]"
        )
        start = end

    concat_inputs = "".join(f"[s{i}]" for i in range(len(segments)))
    return ";".join(segments + [f"{concat_inputs}concat=n={len(segments)}:v=0:a=1[outa]"])


def build_smooth_progressive_tempo_filter_complex(duration, segment_specs, source_start=0.0, crossfade_duration=0.035):
    segments = []
    labels = []
    start = 0.0

    for index, spec in enumerate(segment_specs):
        end_ratio = max(0.0, min(1.0, float(spec["end_ratio"])))
        end = duration * end_ratio if index < len(segment_specs) - 1 else duration
        if end <= start:
            continue

        label = f"smooth{index}"
        tempo_factor = spec.get("tempo", 1.0)
        pitch_factor = max(0.50, min(1.0, float(spec.get("pitch", 1.0))))
        chain_parts = []
        effective_tempo = tempo_factor
        if abs(pitch_factor - 1.0) > 0.001:
            chain_parts.extend([
                f"asetrate=24000*{pitch_factor:.3f}",
                "aresample=24000",
            ])
            effective_tempo = tempo_factor / pitch_factor
        chain_parts.append(atempo_chain_for_factor(effective_tempo))
        segments.append(
            f"[0:a]atrim=start={source_start + start:.3f}:end={source_start + end:.3f},"
            f"asetpts=PTS-STARTPTS,{','.join(chain_parts)}[{label}]"
        )
        labels.append(label)
        start = end

    if not labels:
        return ""

    if len(labels) == 1:
        return ";".join(segments + [f"[{labels[0]}]anull[outa]"])

    current = labels[0]
    crossfades = []
    for index, label in enumerate(labels[1:], start=1):
        mixed_label = f"smoothmix{index}"
        crossfades.append(
            f"[{current}][{label}]acrossfade=d={crossfade_duration:.3f}:c1=tri:c2=tri[{mixed_label}]"
        )
        current = mixed_label

    return ";".join(segments + crossfades + [f"[{current}]anull[outa]"])


def apply_shutdown_source_slowdown(source_path):
    exe = ffmpeg_exe()
    if not exe:
        return ""

    duration = get_duration_seconds(source_path)
    if duration <= 0:
        return ""

    speech_start, speech_end = detect_active_audio_region(source_path)
    if speech_end <= speech_start:
        speech_start, speech_end = 0.0, duration

    lead_in = max(0.0, speech_start - 0.030)
    speech_duration = max(0.0, speech_end - lead_in)
    if speech_duration <= 0.0:
        speech_duration = duration
        lead_in = 0.0

    down_start_ratio = weighted_word_boundary_ratio("Shutting down.", 1)
    # Pre-shape the same spoken line from roughly -15% at the front to roughly
    # -80% by the tail, with the strongest drop landing around and after the
    # transition into "down".
    segment_specs = [
        {"end_ratio": max(0.28, down_start_ratio * 0.50), "tempo": 0.82, "pitch": 1.00},
        {"end_ratio": max(0.55, down_start_ratio + 0.00), "tempo": 0.62, "pitch": 0.88},
        {"end_ratio": min(0.78, down_start_ratio + 0.10), "tempo": 0.40, "pitch": 0.72},
        {"end_ratio": min(0.92, down_start_ratio + 0.22), "tempo": 0.24, "pitch": 0.64},
        {"end_ratio": 1.0, "tempo": 0.10, "pitch": 0.56},
    ]

    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    filter_complex = build_smooth_progressive_tempo_filter_complex(
        speech_duration,
        segment_specs,
        source_start=lead_in,
        crossfade_duration=0.020,
    )

    if not filter_complex:
        try:
            os.remove(out_path)
        except Exception:
            pass
        return ""

    result = subprocess.run(
        [
            exe,
            "-y",
            "-i",
            source_path,
            "-filter_complex",
            filter_complex,
            "-map",
            "[outa]",
            out_path,
        ],
        **hidden_subprocess_kwargs()
    )

    if result.returncode != 0 or not os.path.exists(out_path) or os.path.getsize(out_path) <= 0:
        try:
            os.remove(out_path)
        except Exception:
            pass
        return ""

    return out_path


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

    if result.returncode != 0 or not os.path.exists(out_path) or os.path.getsize(out_path) <= 0:
        try:
            os.remove(out_path)
        except Exception:
            pass
        return None

    return out_path


def build_shutdown_filter_complex(duration, speech_start=0.0, speech_end=None):
    # Keep the shutdown path isolated, but drive its slowdown from a word-
    # weighted boundary so more of "down" gets stretched instead of only the
    # final sliver of the clip.
    if speech_end is None:
        speech_end = duration

    speech_duration = max(0.0, speech_end - speech_start)
    if speech_duration <= 0.0:
        speech_duration = duration
        speech_start = 0.0
        speech_end = duration

    down_start_ratio = weighted_word_boundary_ratio("Shutting down.", 1)
    segment_specs = [
        {"end_ratio": max(0.18, down_start_ratio * 0.48), "tempo": 0.90, "level": "raised"},
        {"end_ratio": max(0.40, down_start_ratio * 0.82), "tempo": 0.80, "level": "extreme"},
        {"end_ratio": min(0.74, down_start_ratio + 0.03), "tempo": 0.62, "level": "raised"},
        {"end_ratio": min(0.86, down_start_ratio + 0.14), "tempo": 0.36, "level": "extreme"},
        {"end_ratio": min(0.95, down_start_ratio + 0.24), "tempo": 0.20, "level": "raised"},
        {"end_ratio": 1.0, "tempo": 0.10, "level": "extreme"},
    ]
    prefix_specs = []
    if speech_start > 0.0:
        prefix_specs.append(
            f"[0:a]atrim=start=0:end={speech_start:.3f},asetpts=PTS-STARTPTS[prefix]"
        )

    speech_filter = build_progressive_tempo_filter_complex(
        speech_duration,
        segment_specs,
        source_start=speech_start,
    )

    concat_inputs = "[prefix]" if prefix_specs else ""
    concat_inputs += "".join(f"[s{i}]" for i in range(len(segment_specs)))
    concat_count = len(segment_specs) + (1 if prefix_specs else 0)

    return ";".join(
        prefix_specs
        + [speech_filter]
        + [f"{concat_inputs}concat=n={concat_count}:v=0:a=1[outa]"]
    )


def apply_shutdown_effect(source_path):
    exe = ffmpeg_exe()
    if not exe:
        return None

    duration = get_duration_seconds(source_path)
    if duration <= 0:
        return None

    speech_start, speech_end = detect_active_audio_region(source_path)

    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    filter_complex = build_shutdown_filter_complex(duration, speech_start=speech_start, speech_end=speech_end)

    cmd = [
        exe,
        "-y",
        "-i", source_path,
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        out_path,
    ]

    result = subprocess.run(cmd, **hidden_subprocess_kwargs())

    if result.returncode != 0 or not os.path.exists(out_path) or os.path.getsize(out_path) <= 0:
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
