#!/usr/bin/env python3
"""Waybar: current keyboard layout (EN/RU), updated from Hyprland socket2 events."""
import json
import os
import socket
import subprocess
import sys

NAMES = {"English": "EN", "Russian": "RU"}


def label(keymap):
    for prefix, short in NAMES.items():
        if keymap.startswith(prefix):
            return short
    return keymap[:2].upper()


last = None


def emit(keymap):
    global last
    if keymap == last:
        return
    last = keymap
    print(json.dumps({"text": label(keymap), "tooltip": keymap, "class": label(keymap).lower()}), flush=True)


def current_keymap():
    out = subprocess.run(["hyprctl", "devices", "-j"], capture_output=True, text=True).stdout
    keyboards = json.loads(out).get("keyboards", [])
    main = next((k for k in keyboards if k.get("main")), keyboards[0] if keyboards else None)
    return main["active_keymap"] if main else "?"


def main():
    emit(current_keymap())
    sock_path = os.path.join(os.environ["XDG_RUNTIME_DIR"], "hypr",
                             os.environ["HYPRLAND_INSTANCE_SIGNATURE"], ".socket2.sock")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(sock_path)
        buf = b""
        while chunk := s.recv(4096):
            buf += chunk
            *lines, buf = buf.split(b"\n")
            for line in lines:
                # Every keyboard device sends its own event; trust only the main one.
                if line.startswith(b"activelayout>>"):
                    emit(current_keymap())


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, BrokenPipeError):
        sys.exit(0)
