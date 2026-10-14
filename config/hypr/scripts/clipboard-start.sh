#!/usr/bin/env bash
set -eu
command -v wl-paste >/dev/null || exit 0
command -v cliphist >/dev/null || exit 0
# Lock survives in the watcher processes, preventing duplicate collectors.
exec 9>"${XDG_RUNTIME_DIR:?}/hypr-clipboard.lock"
flock -n 9 || exit 0
wl-paste --type text --watch cliphist store &
text_pid=$!
wl-paste --type image --watch cliphist store &
image_pid=$!
trap 'kill "$text_pid" "$image_pid" 2>/dev/null || true' EXIT
trap 'exit 0' INT TERM
wait
