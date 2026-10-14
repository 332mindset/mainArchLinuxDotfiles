#!/usr/bin/env bash
set -eu
if ! command -v waybar >/dev/null 2>&1; then
    printf '%s\n' 'Waybar is not installed. Run: sudo pacman -S --needed waybar' >&2
    exit 1
fi
pkill -x waybar || true
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
state_home="${XDG_STATE_HOME:-$HOME/.local/state}"
mkdir -p "$state_home/waybar"
nohup waybar -c "$config_home/waybar/config.jsonc" -s "$config_home/waybar/style.css" >"$state_home/waybar/waybar.log" 2>&1 </dev/null &
