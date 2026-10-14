#!/usr/bin/env bash
set -eu
# Apply the prepared appearance in the user's active desktop session.
hyprctl reload
errors="$(hyprctl configerrors)"
if [ -n "$errors" ]; then
    printf '%s\n' "$errors" >&2
    exit 1
fi
"$HOME/.config/hypr/scripts/cursor.sh"
"$HOME/.config/waybar/scripts/launch.sh"
if command -v swaync-client >/dev/null 2>&1; then
    swaync-client -R -sw || true
    swaync-client -rs -sw || true
fi
printf '%s\n' 'Desktop configuration reloaded.'
