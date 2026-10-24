#!/usr/bin/env bash
set -eu
pgrep -x hyprlock >/dev/null && exit 0

state_dir="${XDG_CACHE_HOME:-$HOME/.cache}/hyprlock-dashboard"
mkdir -p "$state_dir"
chmod 700 "$state_dir"
exec 9>"$state_dir/launcher.lock"
flock -n 9 || exit 0

helper="$HOME/.config/hypr/scripts/lock-dashboard.py"
if ! "$helper" --prepare 2>"$state_dir/prepare.log"; then
    exec hyprlock -c "$HOME/.config/hypr/hyprlock-fallback.conf"
fi

"$helper" --serve 9>&- >"$state_dir/worker.log" 2>&1 &
worker_pid=$!
cleanup() {
    kill "$worker_pid" 2>/dev/null || true
    wait "$worker_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
hyprlock -c "$HOME/.config/hypr/hyprlock.conf" 9>&-
