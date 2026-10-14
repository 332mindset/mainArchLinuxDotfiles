#!/usr/bin/env bash
set -euo pipefail
for tool in cliphist wl-copy; do
    if ! command -v "$tool" >/dev/null; then
        notify-send "Clipboard" "Install cliphist and wl-clipboard" || true
        exit 1
    fi
done
history=$(cliphist list)
if [[ -z "$history" ]]; then
    notify-send "Clipboard" "History is empty. Copy some text or an image." || true
    exit 0
fi
selection=$(printf '%s\n' "$history" | rofi -dmenu -i -p "Clipboard" -display-columns 2 -theme-str 'window { width: 680px; } listview { lines: 10; }' -no-custom) || exit 0
[[ -n "$selection" ]] || exit 0
printf '%s\n' "$selection" | cliphist decode | wl-copy
