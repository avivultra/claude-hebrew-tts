"""
speak.py — Hebrew TTS helper using edge-tts (Microsoft Azure Neural voices).

Usage:
    python scripts/speak.py "טקסט לקריאה"
    python scripts/speak.py --voice hila "טקסט"
    python scripts/speak.py --file text.txt             # read from UTF-8 file
    echo "טקסט" | python scripts/speak.py -             # read from stdin
    python scripts/speak.py --save out.mp3 "טקסט"       # save without playing

Options:
    --voice {avri,hila}   Male (Avri) or female (Hila). Default: avri.
    --rate   RATE         Speech rate, e.g. "+0%", "-10%", "+15%". Default: "+0%".
    --save   PATH         Write MP3 to PATH instead of playing.

Notes:
    - Requires edge-tts (pip install edge-tts). Network access needed (calls
      Microsoft's free neural TTS endpoint — no API key).
    - On Windows we play the MP3 through the default shell association
      (WMP, Groove, Edge, etc.). Use --save if that's not desirable.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.stderr.write(
        "edge-tts is not installed. Run the one-time setup script:\n"
        "    Windows: powershell -ExecutionPolicy Bypass -File scripts/setup.ps1\n"
        "    macOS/Linux: bash scripts/setup.sh\n"
    )
    sys.exit(2)


VOICES = {
    "avri": "he-IL-AvriNeural",   # male
    "hila": "he-IL-HilaNeural",   # female
}


async def synthesize(text: str, voice: str, rate: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(str(out_path))


def play(mp3_path: Path) -> None:
    """Play the MP3 exactly once, in an isolated detached process.

    On Windows we deliberately avoid ``os.startfile`` — it delegates to
    whatever app is registered for ``.mp3`` (Groove Music, Windows Media
    Player, etc.), which typically maintains a playlist/queue and will
    replay previously-opened MP3s after the new one. Using MCI via a
    detached helper process guarantees: one file, one playback, no queue.
    """
    if os.name == "nt":
        # Spawn a detached Python that plays via MCI (mciSendStringW) and exits.
        # This decouples playback from the main process and from any
        # file-association handler, so the audio plays exactly once.
        code = (
            "import ctypes, sys\n"
            "m = ctypes.windll.winmm.mciSendStringW\n"
            "p = sys.argv[1]\n"
            "m(f'open \"{p}\" type mpegvideo alias s', None, 0, None)\n"
            "m('play s wait', None, 0, None)\n"
            "m('close s', None, 0, None)\n"
        )
        flags = 0
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            flags |= subprocess.CREATE_NO_WINDOW
        if hasattr(subprocess, "DETACHED_PROCESS"):
            flags |= subprocess.DETACHED_PROCESS
        subprocess.Popen(
            [sys.executable, "-c", code, str(mp3_path)],
            creationflags=flags,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    elif sys.platform == "darwin":
        subprocess.Popen(["afplay", str(mp3_path)])  # noqa: S603,S607
    else:
        # Try common Linux players
        for cmd in (["mpg123", "-q"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"], ["cvlc", "--play-and-exit"]):
            try:
                subprocess.Popen([*cmd, str(mp3_path)])  # noqa: S603
                return
            except FileNotFoundError:
                continue
        sys.stderr.write("No audio player found. Use --save to write MP3 instead.\n")


def read_text(args: argparse.Namespace) -> str:
    if args.file:
        data = Path(args.file).read_text(encoding="utf-8")
    elif args.text == "-" or args.text is None:
        # Read raw bytes from stdin and decode as UTF-8 explicitly.
        # On Windows the default stdin codec is often cp1252, which
        # mangles Hebrew into surrogates and breaks the TTS call.
        data = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    else:
        data = args.text
    data = data.strip()
    if not data:
        sys.stderr.write("No text provided.\n")
        sys.exit(1)
    return data


def main() -> None:
    p = argparse.ArgumentParser(description="Hebrew TTS via edge-tts neural voices")
    p.add_argument("text", nargs="?", help="Text to speak (use '-' for stdin)")
    p.add_argument("--voice", choices=VOICES.keys(), default="avri",
                   help="Voice name (default: avri / male)")
    p.add_argument("--rate", default="+35%", help="Speech rate, e.g. '+10%%', '-5%%'. Default: +35%% (~1.35x, comfortable conversational pace — neural voices at +0%% feel unnaturally slow)")
    p.add_argument("--save", type=Path, default=None,
                   help="Save MP3 to this path instead of playing")
    p.add_argument("--file", type=Path, default=None,
                   help="Read text from a UTF-8 file (safer on Windows than stdin)")
    args = p.parse_args()

    text = read_text(args)
    voice = VOICES[args.voice]

    if args.save:
        out_path = args.save.resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.close()
        out_path = Path(tmp.name)

    try:
        asyncio.run(synthesize(text, voice=voice, rate=args.rate, out_path=out_path))
    except Exception as e:
        sys.stderr.write(f"TTS failed: {e}\n")
        if not args.save and out_path.exists():
            out_path.unlink(missing_ok=True)
        sys.exit(1)

    if args.save:
        print(f"Saved: {out_path}")
    else:
        play(out_path)
        # Don't delete — OS handler plays async. Let temp cleanup do its job.


if __name__ == "__main__":
    main()
