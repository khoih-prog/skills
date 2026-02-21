#!/usr/bin/env python3
"""
Generate a Kokoro TTS voice reply as a native iMessage voice message.

On macOS: uses afconvert → CAF/Opus at 48kHz mono (identical to Messages.app format).
On other platforms: uses ffmpeg → MP3 fallback.

Usage:
    generate_voice_reply.py "text to speak" [output_path]
    generate_voice_reply.py "text" --voice af_heart --speed 1.15 --lang en-us

Stdout line 1: output file path (for piping to other tools).
Stderr: human-readable status.
"""

import sys
import os
import subprocess
import tempfile
import argparse
import shutil

import numpy as np


def encode_caf_afconvert(wav_path: str, out_path: str) -> None:
    """Encode to CAF/Opus using Apple's native afconvert (macOS only)."""
    wav48 = tempfile.mktemp(suffix="_48k.wav")
    try:
        subprocess.run(
            ["afconvert", wav_path, "-o", wav48, "-d", "LEI16", "-c", "1", "-r", "48000"],
            capture_output=True, check=True,
        )
        subprocess.run(
            ["afconvert", wav48, "-o", out_path, "-f", "caff", "-d", "opus", "-b", "32000"],
            capture_output=True, check=True,
        )
    finally:
        if os.path.exists(wav48):
            os.unlink(wav48)


def encode_mp3_ffmpeg(wav_path: str, out_path: str) -> None:
    """Encode to MP3 using ffmpeg (cross-platform fallback)."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-ar", "44100", "-ac", "1",
         "-c:a", "libmp3lame", "-b:a", "128k", out_path],
        capture_output=True, check=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate Kokoro TTS iMessage voice reply")
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("output", nargs="?", default=None, help="Output file path")
    parser.add_argument("--voice", default="af_heart", help="Kokoro voice (default: af_heart)")
    parser.add_argument("--speed", type=float, default=1.15, help="Speed (default: 1.15)")
    parser.add_argument("--lang", default="en-us", help="Language code (default: en-us)")
    args = parser.parse_args()

    if not args.text.strip():
        print("Error: empty text", file=sys.stderr)
        sys.exit(1)

    from kokoro_onnx import Kokoro
    import soundfile as sf

    model_dir = os.path.expanduser("~/.cache/kokoro-onnx")
    kokoro = Kokoro(
        os.path.join(model_dir, "kokoro-v1.0.onnx"),
        os.path.join(model_dir, "voices-v1.0.bin"),
    )
    samples, sr = kokoro.create(args.text, voice=args.voice, speed=args.speed, lang=args.lang)

    # Prepend 150ms silence — iMessage player clips the first few ms
    silence = np.zeros(int(sr * 0.15), dtype=samples.dtype)
    samples = np.concatenate([silence, samples])

    # Write intermediate WAV
    wav_path = tempfile.mktemp(suffix=".wav")
    sf.write(wav_path, samples, sr)

    # Choose encoder and output format
    has_afconvert = shutil.which("afconvert") is not None

    if has_afconvert:
        ext = ".caf"
        encode = encode_caf_afconvert
    else:
        ext = ".mp3"
        encode = encode_mp3_ffmpeg

    out_path = args.output or tempfile.mktemp(suffix=ext, prefix="voice_reply_")
    encode(wav_path, out_path)
    os.unlink(wav_path)

    duration = len(samples) / sr
    size = os.path.getsize(out_path)
    fmt = "CAF/Opus" if has_afconvert else "MP3"
    print(out_path)
    print(f"Generated {duration:.1f}s {fmt} audio ({size} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
