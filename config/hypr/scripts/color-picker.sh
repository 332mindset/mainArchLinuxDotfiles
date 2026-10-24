#!/usr/bin/env bash
# Pick a color anywhere on screen, copy its HEX and show it in a notification.
set -u
if ! command -v hyprpicker >/dev/null; then
    notify-send "Color picker" "Install hyprpicker: sudo pacman -S hyprpicker"
    exit 1
fi
pgrep -x hyprpicker >/dev/null && exit 0

color="$(hyprpicker -a -f hex 2>/dev/null)" || exit 0
[[ -n "$color" ]] || exit 0

# A swatch of the picked color as the notification icon.
swatch="${XDG_RUNTIME_DIR:-/tmp}/color-picker.png"
icon="color-picker"
if command -v magick >/dev/null && magick -size 96x96 xc:none -fill "$color" \
        -draw 'roundrectangle 0,0 95,95 22,22' "$swatch" 2>/dev/null; then
    icon="$swatch"
fi
notify-send -a "Color picker" -i "$icon" "$color" "Copied to clipboard"
