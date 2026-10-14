#!/usr/bin/env python3
"""Rofi power menu with confirmation for actions that close the session."""

import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

CONFIG = Path.home() / ".config"
SCRIPTS = CONFIG / "hypr/scripts"
THEME = CONFIG / "rofi/power-menu.rasi"
ICONS = CONFIG / "rofi/power-icons"
STATE = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "power-menu"
ACTIONS = [
    ("poweroff", "Shut down"),
    ("reboot", "Restart"),
    ("suspend", "Sleep"),
    ("logout", "Log out"),
    ("lock", "Lock"),
    ("cancel", "Cancel"),
]


def notify(message):
    print(message, file=sys.stderr)
    subprocess.run(["notify-send", "-a", "Power", "Power menu", message], check=False, timeout=5)


def choose(entries, prompt="Power", confirm=False):
    rows = "".join(f"{label}\0icon\x1f{ICONS / (action + '.svg')}\n" for action, label in entries)
    command = [
        "rofi", "-dmenu", "-i", "-no-custom", "-show-icons", "-format", "i",
        "-p", prompt, "-theme", str(THEME),
        "-selected-row", "0" if confirm else str(len(entries) - 1),
        "-mesg", "Enter — select  ·  Esc — close",
    ]
    if confirm:
        command += ["-theme-str", "window { width: 470px; } listview { lines: 1; columns: 2; }"]
    result = subprocess.run(command, input=rows, capture_output=True, text=True)
    if result.returncode == 1:
        return "cancel"
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Could not open Rofi")
    try:
        index = int(result.stdout.strip())
    except ValueError:
        raise RuntimeError("Invalid menu selection") from None
    if not 0 <= index < len(entries):
        raise RuntimeError("Invalid action index")
    return entries[index][0]


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Could not perform the action")


def suspend():
    with (STATE / "lock.log").open("a") as log:
        subprocess.Popen([str(SCRIPTS / "lock.sh")], stdin=subprocess.DEVNULL,
                         stdout=log, stderr=log, start_new_session=True)
    # Wait for the compositor to confirm the session lock, not just the process.
    for _ in range(50):
        result = subprocess.run(["hyprctl", "-j", "locked"], capture_output=True, text=True, timeout=3)
        try:
            status = json.loads(result.stdout)
        except ValueError:
            status = {}
        if result.returncode == 0 and isinstance(status, dict) and status.get("locked") is True:
            run_command(["systemctl", "suspend"])
            return
        time.sleep(0.1)
    raise RuntimeError("Sleep cancelled: the screen lock could not be confirmed")


def main():
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / "menu.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        try:
            action = choose(ACTIONS)
            if action == "cancel":
                return 0
            if action in {"poweroff", "reboot", "logout"}:
                label = dict(ACTIONS)[action]
                if choose([("cancel", "Cancel"), (action, label)], label + "?", confirm=True) != action:
                    return 0
            if action == "lock":
                subprocess.Popen([str(SCRIPTS / "lock.sh")], stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            elif action == "suspend":
                suspend()
            elif action == "logout":
                run_command(["hyprctl", "dispatch", "exit"])
            else:
                run_command(["systemctl", action])
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            notify(str(error))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
