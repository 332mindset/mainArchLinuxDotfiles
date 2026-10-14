#!/usr/bin/env python3
"""Stream Cava bars to Waybar; hide the module after 1.5 seconds of silence."""

import json
from pathlib import Path
import signal
import subprocess
import time

GLYPHS = "▁▂▃▄▅▆▇█"
BARS = 12
HIDE_AFTER = 1.5
CONFIG = Path(__file__).resolve().parent.parent / "cava.conf"


def stop(_signum, _frame):
    raise SystemExit(0)


def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    previous_text = None

    def emit(text):
        nonlocal previous_text
        if text != previous_text:
            print(json.dumps({
                "text": text,
                "class": "playing" if text else "silent",
                "tooltip": "Cava • Left click: play / pause • Right click: next track",
            }, ensure_ascii=False), flush=True)
            previous_text = text

    emit("")
    process = subprocess.Popen(
        ["cava", "-p", str(CONFIG)],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    last_sound = float("-inf")
    try:
        for line in process.stdout:
            try:
                values = [int(value) for value in line.strip().split(";") if value]
            except ValueError:
                continue
            if len(values) != BARS:
                continue
            now = time.monotonic()
            if any(value > 0 for value in values):
                last_sound = now
            if now - last_sound < HIDE_AFTER:
                emit("".join(GLYPHS[max(0, min(7, value))] for value in values))
            else:
                emit("")
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        process.stdout.close()
        emit("")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
