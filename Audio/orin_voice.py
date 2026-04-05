import sys
import os
import asyncio
import tempfile
import math
import array

import edge_tts
from PySide6.QtCore import QUrl, QEventLoop, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QApplication


class JarvisSpeaker:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.60)

    async def speak(self, text, voice="en-GB-RyanNeural", rate="+8%", pitch="-2Hz", mode="normal"):
        fd, source_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        processed_path = None
        media_status_connected = False

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch,
            )
            await communicate.save(source_path)

            if not os.path.exists(source_path):
                print(f"ERROR: audio file was not created: {source_path}")
                return

            playback_path = source_path

            if mode == "malfunction":
                try:
                    processed_path = apply_malfunction_effect(source_path)
                    if processed_path and os.path.exists(processed_path):
                        playback_path = processed_path
                except Exception as e:
                    print(f"WARNING: malfunction post-process failed, using clean TTS: {e}")

            loop = QEventLoop()

            def on_media_status_changed(status):
                if status == QMediaPlayer.MediaStatus.EndOfMedia:
                    loop.quit()
                elif status == QMediaPlayer.MediaStatus.InvalidMedia:
                    print("ERROR: Invalid media")
                    loop.quit()

            self.player.mediaStatusChanged.connect(on_media_status_changed)
            media_status_connected = True
            self.player.setSource(QUrl.fromLocalFile(playback_path))
            self.player.play()

            QTimer.singleShot(20000, loop.quit)
            loop.exec()

        finally:
            self.player.stop()
            self.player.setSource(QUrl())
            if media_status_connected:
                try:
                    self.player.mediaStatusChanged.disconnect(on_media_status_changed)
                except Exception:
                    pass
            for path in (source_path, processed_path):
                if path:
                    try:
                        os.remove(path)
                    except Exception:
                        pass


def parse_args(argv):
    text = None
    mode = "normal"

    i = 1
    positional = []

    while i < len(argv):
        arg = argv[i]

        if arg == "--text" and i + 1 < len(argv):
            text = argv[i + 1]
            i += 2
            continue

        if arg == "--mode" and i + 1 < len(argv):
            mode = argv[i + 1].strip().lower()
            i += 2
            continue

        positional.append(arg)
        i += 1

    if text is None:
        if positional:
            text = " ".join(positional)
        else:
            text = "Hello sir. How can I be of assistance?"

    return text, mode


def malfunction_text(text: str) -> str:
    t = text.strip()

    known = {
        "um..... sir, i seem to be malfunctioning.": "Uhm... Sir, I seem to be malfunctioning.",
        "uhm..... sir, i seem to be malfunctioning.": "Uhm... Sir, I seem to be malfunctioning.",
        "um... sir, i seem to be malfunctioning.": "Uhm... Sir, I seem to be malfunctioning.",
        "uhm... sir, i seem to be malfunctioning.": "Uhm... Sir, I seem to be malfunctioning.",
        "attempting restart.": "Attempting restart.",
        "restart failed.": "Restart failed.",
        "attempting fix.": "Attempting fix.",
        "fix failed.": "Fix failed.",
    }

    lowered = t.lower()
    if lowered in known:
        return known[lowered]

    return t


def mode_settings(mode, text):
    if mode == "malfunction":
        return {
            "text": malfunction_text(text),
            "voice": "en-GB-RyanNeural",
            "rate": "+10%",
            "pitch": "-3Hz",
            "mode": "malfunction",
        }

    return {
        "text": text,
        "voice": "en-GB-RyanNeural",
        "rate": "+8%",
        "pitch": "-2Hz",
        "mode": "normal",
    }


def soft_clip(segment, drive=2.0):
    samples = array.array(segment.array_type, segment.raw_data)
    max_val = float(2 ** (8 * segment.sample_width - 1) - 1)
    norm = math.tanh(drive)

    for i, s in enumerate(samples):
        x = float(s) / max_val
        y = math.tanh(drive * x) / norm
        samples[i] = int(max(-1.0, min(1.0, y)) * max_val)

    return segment._spawn(samples.tobytes())


def ring_mod(segment, hz=72.0, depth=0.38):
    """Full-clip robotic modulation that remains intelligible."""
    samples = array.array(segment.array_type, segment.raw_data)
    max_val = float(2 ** (8 * segment.sample_width - 1) - 1)
    frame_rate = float(segment.frame_rate)

    channels = max(1, segment.channels)
    for i, s in enumerate(samples):
        frame_index = i // channels
        t = frame_index / frame_rate
        mod = (1.0 - depth) + depth * ((math.sin(2.0 * math.pi * hz * t) + 1.0) * 0.5)
        y = (float(s) / max_val) * mod
        samples[i] = int(max(-1.0, min(1.0, y)) * max_val)

    return segment._spawn(samples.tobytes())


def comb_delay(segment, delay_ms=22, gain_db=-8):
    from pydub import AudioSegment
    return segment.overlay(AudioSegment.silent(duration=delay_ms, frame_rate=segment.frame_rate) + (segment + gain_db))


def apply_malfunction_effect(source_path: str) -> str:
    """
    Sustained full-line robotic corruption.
    Designed so the effect is audible for the entire sentence, not just the opening word.
    """
    from pydub import AudioSegment
    from pydub.generators import WhiteNoise

    seg = AudioSegment.from_file(source_path).set_channels(1)

    clean = seg.high_pass_filter(140).low_pass_filter(4200)
    base = clean - 1

    # Continuous robot tone across the whole line.
    robot_a = ring_mod(base, hz=68.0, depth=0.34) - 2
    robot_b = ring_mod(base, hz=103.0, depth=0.18) - 7

    # Metallic upper band kept present throughout.
    metallic = clean.high_pass_filter(1150).low_pass_filter(2900) - 8

    # Small comb delay for synthetic machine smear across the full clip.
    smeared = comb_delay(clean - 5, delay_ms=24, gain_db=-8)

    mixed = base.overlay(robot_a).overlay(robot_b).overlay(metallic).overlay(smeared)

    # Constant restrained static across the full clip.
    static = WhiteNoise().to_audio_segment(duration=len(mixed)).high_pass_filter(2500) - 31
    mixed = mixed.overlay(static)

    # Regular tiny digital ticks across the whole line.
    tick = WhiteNoise().to_audio_segment(duration=12).high_pass_filter(3300) - 16
    tick_track = AudioSegment.silent(duration=len(mixed), frame_rate=mixed.frame_rate)
    for pos in range(0, len(mixed), 82):
        tick_track = tick_track.overlay(tick, position=pos)
    mixed = mixed.overlay(tick_track)

    effected = soft_clip(mixed, drive=2.0) - 1

    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    effected.export(out_path, format="wav")
    return out_path


if __name__ == "__main__":
    text, mode = parse_args(sys.argv)
    settings = mode_settings(mode, text)

    speaker = JarvisSpeaker()
    asyncio.run(
        speaker.speak(
            text=settings["text"],
            voice=settings["voice"],
            rate=settings["rate"],
            pitch=settings["pitch"],
            mode=settings["mode"],
        )
    )
