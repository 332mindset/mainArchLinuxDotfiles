#!/usr/bin/env python3
"""Choose a wallpaper in Rofi, or restore the last successful selection."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


HOME_DIR = Path.home()
WALLPAPERS = HOME_DIR / "Pictures/Wallpapers"
THEME = HOME_DIR / ".config/rofi/wallpapers.rasi"
STATE_DIR = Path(os.environ.get("XDG_STATE_HOME") or HOME_DIR / ".local/state") / "wallpaper"
CURRENT = STATE_DIR / "current.json"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".avif", ".tga", ".qoi", ".pnm"}


def notify(title, message):
    print(f"{title}: {message}", file=sys.stderr)
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "-a", "Wallpapers", title, message], check=False, timeout=5)


def saved_wallpaper():
    try:
        data = json.loads(CURRENT.read_text())
        return Path(data["path"]) if isinstance(data.get("path"), str) else None
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return None


def images():
    WALLPAPERS.mkdir(parents=True, exist_ok=True)
    return sorted(
        (p for p in WALLPAPERS.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS),
        key=lambda p: str(p.relative_to(WALLPAPERS)).casefold(),
    )


def ensure_daemon():
    client = shutil.which("awww")
    daemon = shutil.which("awww-daemon")
    if not client or not daemon:
        raise RuntimeError("Install awww: sudo pacman -S --needed awww")
    query = [client, "query"]
    if subprocess.run(query, capture_output=True, timeout=3).returncode == 0:
        return client
    # Start separately from the menu; keep diagnostics for troubleshooting.
    with (STATE_DIR / "daemon.log").open("a") as log:
        child = subprocess.Popen(
            [daemon, "--no-cache"], stdin=subprocess.DEVNULL,
            stdout=log, stderr=log, start_new_session=True,
        )
    for _ in range(50):
        if subprocess.run(query, capture_output=True, timeout=3).returncode == 0:
            return client
        if child.poll() is not None:
            break
        time.sleep(0.1)
    raise RuntimeError("Could not start awww. See ~/.local/state/wallpaper/daemon.log")


def apply_wallpaper(path, restore=False):
    path = path.resolve()
    if not path.is_file():
        raise RuntimeError(f"Wallpaper file no longer exists: {path}")
    client = ensure_daemon()
    command = [client, "img", str(path), "--resize", "crop", "--transition-type", "none" if restore else "fade"]
    if not restore:
        command += ["--transition-duration", "1.2", "--transition-fps", "60", "--transition-bezier", "0.22,0.8,0.25,1"]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "awww could not apply the image")
    # Save only after awww accepts the image; replacement is atomic.
    temporary = CURRENT.with_suffix(".tmp")
    temporary.write_text(json.dumps({"path": str(path)}, ensure_ascii=False) + "\n")
    temporary.replace(CURRENT)
    if not restore:
        notify("Wallpaper changed", path.name)


def choose_wallpaper():
    if not shutil.which("rofi"):
        raise RuntimeError("Rofi was not found")
    available = images()
    if not available:
        notify("No wallpapers found", "Add images to ~/Pictures/Wallpapers, then press Super + F.")
        return
    rows = []
    for path in available:
        label = str(path.relative_to(WALLPAPERS))
        # Rofi uses newlines and control characters as row metadata delimiters.
        label = "".join(c if c.isprintable() else " " for c in label)
        icon = str(path)
        if any(c in icon for c in "\n\r\x1f"):
            rows.append(label + "\n")
        else:
            rows.append(label + "\0icon\x1f" + icon + "\n")
    command = [
        "rofi", "-dmenu", "-i", "-no-custom", "-show-icons", "-format", "i",
        "-p", "Wallpapers", "-theme", str(THEME),
        "-mesg", "~/Pictures/Wallpapers  ·  Enter — select  ·  Esc — close",
    ]
    current = saved_wallpaper()
    if current in available:
        index = str(available.index(current))
        command += ["-selected-row", index, "-a", index]
    result = subprocess.run(command, input="".join(rows), capture_output=True, text=True)
    if result.returncode == 1:
        return  # Escape, or no matching selection.
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Could not open the Rofi menu")
    try:
        index = int(result.stdout.strip())
    except ValueError:
        raise RuntimeError("Rofi returned an invalid selection") from None
    if not 0 <= index < len(available):
        raise RuntimeError("Rofi returned an invalid wallpaper index")
    apply_wallpaper(available[index])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore", action="store_true", help="Restore the saved wallpaper without a menu")
    args = parser.parse_args()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    # Repeated shortcut presses must not open multiple menus or start two daemons.
    with (STATE_DIR / "picker.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        try:
            if args.restore:
                previous = saved_wallpaper()
                if previous and previous.is_file():
                    apply_wallpaper(previous, restore=True)
            else:
                choose_wallpaper()
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            notify("Could not change the wallpaper", str(error))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
