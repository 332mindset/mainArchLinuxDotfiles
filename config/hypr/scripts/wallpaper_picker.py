#!/usr/bin/env python3
"""Choose a wallpaper in Rofi, or restore the last successful selection."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import fcntl
import hashlib
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
THUMBS = Path(os.environ.get("XDG_CACHE_HOME") or HOME_DIR / ".cache") / "wallpaper-picker"
THUMB_W, THUMB_H, THUMB_RADIUS = 270, 480, 20
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


def thumbnail(path):
    """Portrait card with rounded corners, cached by path and mtime; falls back to the original."""
    try:
        stamp = f"{path.resolve()}:{path.stat().st_mtime_ns}:{THUMB_W}x{THUMB_H}r{THUMB_RADIUS}"
    except OSError:
        return path
    thumb = THUMBS / (hashlib.sha1(stamp.encode()).hexdigest() + ".png")
    if thumb.is_file():
        return thumb
    if not shutil.which("ffmpeg"):
        return path
    w, h, r = THUMB_W, THUMB_H, THUMB_RADIUS
    # Alpha is 0 outside a quarter circle of radius r in each corner.
    alpha = f"if(lte(hypot(max(0,abs(X-W/2+0.5)-(W/2-{r})),max(0,abs(Y-H/2+0.5)-(H/2-{r}))),{r}),255,0)"
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},format=rgba,"
          f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='{alpha}'")
    temporary = thumb.with_suffix(".tmp.png")
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(path), "-frames:v", "1", "-vf", vf, str(temporary)],
        capture_output=True, timeout=60,
    )
    if result.returncode or not temporary.is_file():
        temporary.unlink(missing_ok=True)
        return path
    temporary.replace(thumb)
    return thumb


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
    # Keep installed theme lockscreens on the last successfully applied image.
    for theme_name in ("roseglass", "ember"):
        theme_dir = HOME_DIR / ".config" / theme_name
        if theme_dir.is_dir():
            link = theme_dir / "wallpaper.tmp"
            if link.is_symlink() or link.exists():
                link.unlink()
            link.symlink_to(path)
            link.replace(theme_dir / "wallpaper")
    if not restore:
        apply_colors(path)
        notify("Wallpaper changed", path.name)


def apply_colors(path):
    """Recolour Waybar, Kitty, Rofi, SwayNC, Hyprland, Hyprlock and Firefox from the image (~/.config/matugen)."""
    matugen = shutil.which("matugen")
    if not matugen:
        notify("Colours not updated", "Install matugen: sudo pacman -S matugen")
        return
    # Index 0 is the best-scored (dominant) colour and avoids the interactive prompt.
    result = subprocess.run(
        [matugen, "image", str(path), "--source-color-index", "0", "-t", "scheme-monochrome", "-m", "dark", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode:
        notify("Colours not updated", result.stderr.strip()[-300:] or "matugen failed")


def choose_wallpaper():
    if not shutil.which("rofi"):
        raise RuntimeError("Rofi was not found")
    available = images()
    if not available:
        notify("No wallpapers found", "Add images to ~/Pictures/Wallpapers, then press Super + F.")
        return
    THUMBS.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        thumbs = list(pool.map(thumbnail, available))
    rows = []
    for path, thumb in zip(available, thumbs):
        label = str(path.relative_to(WALLPAPERS))
        # Rofi uses newlines and control characters as row metadata delimiters.
        label = "".join(c if c.isprintable() else " " for c in label)
        icon = str(thumb)
        if any(c in icon for c in "\n\r\x1f"):
            rows.append(label + "\n")
        else:
            rows.append(label + "\0icon\x1f" + icon + "\n")
    command = [
        "rofi", "-dmenu", "-i", "-no-custom", "-show-icons", "-format", "i",
        "-p", "Wallpapers", "-theme", str(THEME),
        # The cards form one horizontal strip: arrows move between cards, not the text cursor.
        "-kb-move-char-back", "Control+b", "-kb-move-char-forward", "Control+f",
        "-kb-element-prev", "ISO_Left_Tab,Left", "-kb-element-next", "Tab,Right",
        "-mesg", "←  →  choose  ·  Enter — apply  ·  Esc — close",
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--restore", action="store_true", help="Restore the saved wallpaper without a menu")
    mode.add_argument("--set", type=Path, metavar="IMAGE", help="Apply an image without opening the menu")
    args = parser.parse_args()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    # Repeated shortcut presses must not open multiple menus or start two daemons.
    with (STATE_DIR / "picker.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        try:
            if args.set is not None:
                apply_wallpaper(args.set)
            elif args.restore:
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
