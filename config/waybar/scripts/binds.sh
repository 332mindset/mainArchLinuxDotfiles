#!/usr/bin/env bash
# Tooltip with the non-obvious Hyprland binds (keep in sync with ~/.config/hypr/hyprland.lua).
binds=(
    "Скриншоты|"
    "Ctrl + End|область"
    "Ctrl + Shift + End|весь экран"
    "Ctrl + Alt + End|область → редактор"
    "Утилиты|"
    "Super + Shift + C|пипетка цвета"
    "Ctrl + Super + V|история буфера"
    "Super + F|выбор обоев"
    "Super + R|перезапуск waybar"
    "Super + N|уведомления"
    "Super + M|медиаплеер"
    "Система|"
    "Super + L|блокировка"
    "Super + Shift + D|блокировка"
    "Super + Shift + E|меню питания"
    "Окна и столы|"
    "Super + Shift + стрелки|двигать окно"
    "Super + S|scratchpad"
    "Super + Shift + S|окно → scratchpad"
    "Super + колесо|столы этого монитора"
    "Super + P|pseudo-tile"
    "Super + J|сменить сплит"
    "Super + ЛКМ / ПКМ|двигать / ресайз"
)
tooltip=""
for entry in "${binds[@]}"; do
    key="${entry%%|*}" desc="${entry#*|}"
    if [ -z "$desc" ]; then
        [ -n "$tooltip" ] && tooltip+="\n"
        tooltip+="<b>$key</b>\n"
    else
        pad=$(( 27 - ${#key} ))
        tooltip+="<tt>$key$(printf '%*s' "$pad" '')</tt> $desc\n"
    fi
done
printf '{"text": "󰌌", "tooltip": "%s"}\n' "${tooltip%\\n}"
