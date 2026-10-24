#!/usr/bin/env bash
set -euo pipefail
# Modes: area (default), full, edit (area opened in Satty for annotations).
mode="${1:-area}"
for tool in grim slurp wl-copy; do
    if ! command -v "$tool" >/dev/null; then
        notify-send "Screenshot" "Install grim, slurp and wl-clipboard" || true
        exit 1
    fi
done
# Avoid concurrent selectors from repeated key presses.
# Use a fresh lock name: older wl-copy processes may still hold the old lock.
exec 9>"${XDG_RUNTIME_DIR:?}/hypr-screenshot-v2.lock"
flock -n 9 || exit 0
geometry=""
if [[ "$mode" != full ]]; then
    geometry=$(slurp -b '#11111b88' -c '#cba6f7' -w 2) || exit 0
    [[ -n "$geometry" ]] || exit 0
fi
directory="$HOME/Pictures/Screenshots"
mkdir -p "$directory"
if [[ "$mode" == edit ]]; then
    if ! command -v satty >/dev/null; then
        notify-send "Screenshot" "Install satty: sudo pacman -S satty" || true
        exit 1
    fi
    # Satty saves and copies by itself (see ~/.config/satty/config.toml).
    grim -g "$geometry" - | satty --filename - 9>&-
    exit 0
fi
file="$directory/Screenshot_$(date +'%Y-%m-%d_%H-%M-%S_%N').png"
if [[ -n "$geometry" ]]; then
    grim -g "$geometry" "$file"
else
    grim -o DVI-D-1 "$file"
fi
# wl-copy forks to serve the clipboard; its child must not inherit our lock.
wl-copy --type image/png < "$file" 9>&-
notify-send "Screenshot saved" "Copied to clipboard: $file" || true
