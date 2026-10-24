#!/usr/bin/env bash
# Waybar: pending pacman (and AUR, with yay or paru) updates. Hidden when up to date.
# `updates.sh upgrade` opens a terminal to upgrade, then refreshes the module.
set -u

aur_helper=""
for helper in yay paru; do
    command -v "$helper" >/dev/null && { aur_helper="$helper"; break; }
done

if [[ "${1:-}" == upgrade ]]; then
    terminal="$HOME/.local/bin/open-terminal"
    [[ -x "$terminal" ]] || terminal="kitty"
    upgrade="${aur_helper:+$aur_helper -Syu}"
    "$terminal" sh -c "${upgrade:-sudo pacman -Syu}; pkill -RTMIN+8 waybar; printf '\nDone. Press Enter to close.'; read -r _"
    exit 0
fi

command -v checkupdates >/dev/null || exit 0

repo="$(checkupdates 2>/dev/null)"
aur=""
[[ -n "$aur_helper" ]] && aur="$("$aur_helper" -Qua 2>/dev/null)"

count() { [[ -n "$1" ]] && printf '%s\n' "$1" | wc -l || echo 0; }
repo_count=$(count "$repo")
aur_count=$(count "$aur")
total=$(( repo_count + aur_count ))

# An empty text hides the module.
if (( total == 0 )); then
    echo '{"text": ""}'
    exit 0
fi

list="$(printf '%s\n%s' "$repo" "$aur" | sed '/^$/d' | head -n 25)"
(( total > 25 )) && list+=$'\n'"… and $(( total - 25 )) more"
tooltip="$repo_count from repos, $aur_count from AUR"$'\n\n'"$list"$'\n\n'"Click to upgrade · right click to refresh"
class="pending"
(( total >= 50 )) && class="many"

# JSON-escape backslashes, quotes and newlines.
tooltip="${tooltip//\\/\\\\}"
tooltip="${tooltip//\"/\\\"}"
tooltip="${tooltip//$'\n'/\\n}"
printf '{"text": "󰚰 %s", "tooltip": "%s", "class": "%s"}\n' "$total" "$tooltip" "$class"
