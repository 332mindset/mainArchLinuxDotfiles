#!/usr/bin/env bash
# Hyprlock helper: now-playing text and cover art from the active MPRIS player.
# Usage: lock-music.sh title|artist|status|art
set -u

cache="${XDG_CACHE_HOME:-$HOME/.cache}/hyprlock-music"
placeholder="$cache/placeholder.png"

# Labels use Pango markup: escape it and keep long titles on one line.
clean() {
    local text="$1" max="$2"
    (( ${#text} > max )) && text="${text:0:max-1}…"
    text="${text//&/&amp;}"
    text="${text//</&lt;}"
    printf '%s\n' "${text//>/&gt;}"
}

meta() { playerctl metadata --format "$1" 2>/dev/null; }

case "${1:-}" in
    title)
        title="$(meta '{{title}}')"
        clean "${title:-Nothing playing}" 24
        ;;
    artist)
        artist="$(meta '{{artist}}')"
        [[ -z "$artist" ]] && artist="$(meta '{{playerName}}')"
        clean "${artist:-—}" 34
        ;;
    status)
        case "$(playerctl status 2>/dev/null)" in
            Playing) echo "󰏤" ;;
            *)       echo "󰐊" ;;
        esac
        ;;
    art)
        mkdir -p "$cache"
        if [[ ! -f "$placeholder" ]]; then
            magick -size 256x256 gradient:'#45475a-#313244' \
                -gravity center -fill '#cba6f7' -font "$(fc-match -f '%{file}' 'JetBrainsMono Nerd Font:style=Bold')" \
                -pointsize 110 -annotate +0+0 '󰝚' "$placeholder" 2>/dev/null \
                || magick -size 256x256 xc:'#313244' "$placeholder"
        fi
        url="$(meta '{{mpris:artUrl}}')"
        case "$url" in
            file://*)
                path="${url#file://}"
                [[ -f "$path" ]] || path="$placeholder"
                # Browsers reuse one temp file for every track: copy it so Hyprlock
                # sees a new path and reloads the cover when the song changes.
                if [[ "$path" != "$placeholder" ]]; then
                    sum="$(md5sum "$path" | cut -c1-16)"
                    [[ -f "$cache/$sum" ]] || cp "$path" "$cache/$sum"
                    path="$cache/$sum"
                fi
                ;;
            http://*|https://*)
                path="$cache/$(printf '%s' "$url" | md5sum | cut -c1-16)"
                [[ -s "$path" ]] || curl -fsSL --max-time 4 -o "$path" "$url" || path="$placeholder"
                ;;
            *) path="$placeholder" ;;
        esac
        # Keep the cache small: the twenty most recent covers are plenty.
        ls -1t "$cache" | grep -v '^placeholder.png$' | tail -n +21 | sed "s#^#$cache/#" | xargs -r rm -f
        echo "$path"
        ;;
    *)
        echo "usage: $0 title|artist|status|art" >&2
        exit 1
        ;;
esac
