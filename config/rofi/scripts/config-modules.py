#!/usr/bin/env python3
"""Rofi script mode: open a configuration folder and its main file in VS Code."""

import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


HOME_DIR = Path.home()
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME") or HOME_DIR / ".config")
CATALOG = CONFIG_DIR / "rofi/config-modules.json"


def modules():
    entries = json.loads(CATALOG.read_text())
    available = []
    for entry in entries:
        folder = CONFIG_DIR / entry["folder"]
        if folder.is_dir():
            available.append({**entry, "path": folder})
    return available


def emit(entries, message=None):
    print("\0no-custom\x1ftrue")
    if message:
        print("\0message\x1f" + html.escape(message).replace("\n", " "))
    for entry in entries:
        # Stable IDs select the catalog entry; labels and paths are never shell commands.
        label = entry["label"].replace("\n", " ").replace("\0", "")
        meta = f"config settings {entry['folder']} {entry.get('file', '')}"
        print(f"{label}\0icon\x1ffolder\x1finfo\x1f{entry['id']}\x1fmeta\x1f{meta}")


def editor():
    for candidate in [HOME_DIR / ".local/bin/code", HOME_DIR / ".local/opt/vscode/bin/code"]:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    executable = shutil.which("code")
    if executable:
        return executable
    raise RuntimeError("Visual Studio Code was not found")


def open_module(entry):
    folder = entry["path"]
    if not folder.is_dir():
        raise RuntimeError("The configuration folder no longer exists")
    command = [editor(), "--reuse-window", str(folder)]
    main_file = folder / entry.get("file", "")
    if main_file.is_file():
        command += ["--goto", str(main_file)]
    state = Path(os.environ.get("XDG_STATE_HOME") or HOME_DIR / ".local/state") / "rofi"
    state.mkdir(parents=True, exist_ok=True)
    with (state / "configs.log").open("a") as log:
        # Detach all stdio so Rofi can close while VS Code starts.
        subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log,
                         stderr=log, start_new_session=True)


def main():
    try:
        entries = modules()
        state = os.environ.get("ROFI_RETV", "0")
        if state == "1":
            selected = os.environ.get("ROFI_INFO", "")
            entry = next((entry for entry in entries if entry["id"] == selected), None)
            if entry is None:
                emit(entries, "Choose a configuration from the list")
            else:
                try:
                    open_module(entry)
                except (OSError, RuntimeError) as error:
                    emit(entries, str(error))
        else:
            emit(entries)
    except (OSError, ValueError, KeyError, TypeError) as error:
        emit([], "Could not read the configuration list: " + str(error))
    return 0


if __name__ == "__main__":
    sys.exit(main())
