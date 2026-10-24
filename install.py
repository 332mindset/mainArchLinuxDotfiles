#!/usr/bin/env python3
"""Preview or install the desktop configuration, backing up replaced files."""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import shutil
import tempfile

REPO = Path(__file__).resolve().parent
# Folders that also hold other programs' data (e.g. gtk-3.0/bookmarks):
# install their files one by one instead of replacing the whole folder.
SHARED = {"gtk-3.0", "gtk-4.0", "fontconfig"}


def entries():
    for path in sorted((REPO / "config").iterdir()):
        if path.name in SHARED:
            for file in sorted(p for p in path.rglob("*") if p.is_file()):
                yield file, Path(".config") / file.relative_to(REPO / "config")
        else:
            yield path, Path(".config") / path.name
    for path in sorted((REPO / "bin").iterdir()):
        yield path, Path(".local/bin") / path.name
    for name in [".inputrc", ".gtkrc-2.0", ".icons/default"]:
        yield REPO / "home" / name, Path(name)
    for path in sorted((REPO / "wallpapers").iterdir()):
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            yield path, Path("Pictures/Wallpapers") / path.name


def check_destination(home, relative):
    path = home
    for part in relative.parts:
        path /= part
        if path.is_symlink():
            raise RuntimeError(f"Refusing to replace or follow a symlink: {path}")
        if path != home / relative and path.exists() and not path.is_dir():
            raise RuntimeError(f"Parent is not a directory: {path}")


def prepare(source, target, home):
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    paths = list(target.rglob("*")) if target.is_dir() else [target]
    for path in paths:
        if not path.is_file():
            continue
        try:
            content = path.read_text()
        except UnicodeDecodeError:
            continue
        if "@HOME@" in content:
            path.write_text(content.replace("@HOME@", str(home)))
        # Executable bits can be lost during uploads through a browser.
        if content.startswith("#!"):
            path.chmod(0o755)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Install; without this flag, only print the plan")
    args = parser.parse_args()
    home = Path.home().absolute()
    # These paths are embedded in several config syntaxes and shell commands.
    if not re.fullmatch(r"/[A-Za-z0-9_./-]+", str(home)):
        parser.error("This installer requires a home path without spaces or special characters")
    if os.environ.get("XDG_CONFIG_HOME", str(home / ".config")) != str(home / ".config"):
        parser.error("This setup uses ~/.config; custom XDG_CONFIG_HOME is not supported")
    items = list(entries())
    for _, relative in items:
        check_destination(home, relative)
        destination = home / relative
        if destination == REPO or destination in REPO.parents:
            parser.error(f"Move this repository outside {destination} before installing")
        print(f"{'Replace (with backup)' if destination.exists() else 'Create':24} ~/{relative}")
    if not args.apply:
        print("\nPreview only. To install: python3 install.py --apply")
        return
    if os.geteuid() == 0:
        parser.error("Run as your desktop user, without sudo")

    backup_relative = Path(".local/state/dotfiles/backups")
    check_destination(home, backup_relative)
    backup_root = home / backup_relative
    backup_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-")
    backup = Path(tempfile.mkdtemp(prefix=timestamp, dir=backup_root))
    touched = []
    try:
        with tempfile.TemporaryDirectory(prefix="dotfiles-stage-") as directory:
            stage = Path(directory)
            for source, relative in items:
                (stage / relative).parent.mkdir(parents=True, exist_ok=True)
                prepare(source, stage / relative, home)
            for _, relative in items:
                destination = home / relative
                saved = backup / relative
                existed = destination.exists()
                if existed:
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(destination), str(saved))
                touched.append((relative, existed))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(stage / relative), str(destination))
    except BaseException:
        for relative, existed in reversed(touched):
            destination = home / relative
            if destination.is_dir():
                shutil.rmtree(destination)
            elif destination.exists():
                destination.unlink()
            if existed:
                shutil.move(str(backup / relative), str(destination))
        raise
    print(f"\nInstalled. Previous files: {backup}")
    print("Your .zshrc and login configuration were not changed. See README.md for shell setup.")
    print("Check your monitor settings, then log out and start Hyprland again when ready.")


if __name__ == "__main__":
    main()
