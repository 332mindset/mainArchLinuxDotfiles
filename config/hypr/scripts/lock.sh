#!/usr/bin/env bash
set -eu
pgrep -x hyprlock >/dev/null && exit 0
exec hyprlock -c "$HOME/.config/hypr/hyprlock.conf"
