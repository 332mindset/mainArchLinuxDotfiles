#!/usr/bin/env bash
set -euo pipefail
for tool in cliphist wl-copy; do
    if ! command -v "$tool" >/dev/null; then
        notify-send "Clipboard" "Install cliphist and wl-clipboard" || true
        exit 1
    fi
done
# Only the id column is decoded, so the visible text can be prettified for images.
history=$(cliphist list | sed -E 's/\[\[ binary data ([0-9.]+ [KMG]?i?B) ([a-z]+) ([0-9]+)x([0-9]+) \]\]/󰋩  image · \2 \3×\4 · \1/')
if [[ -z "$history" ]]; then
    notify-send "Clipboard" "History is empty. Copy some text or an image." || true
    exit 0
fi
selection=$(printf '%s\n' "$history" | rofi -dmenu -i -p "Clipboard" -display-columns 2 -theme "${XDG_CONFIG_HOME:-$HOME/.config}/rofi/clipboard.rasi" -no-show-icons -no-custom) || exit 0
[[ -n "$selection" ]] || exit 0
printf '%s\n' "$selection" | cliphist decode | wl-copy
