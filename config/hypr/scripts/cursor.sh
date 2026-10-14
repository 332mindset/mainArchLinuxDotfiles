#!/usr/bin/env bash
set -eu
export XCURSOR_THEME=Breeze_Light
export XCURSOR_SIZE=24
export HYPRCURSOR_THEME=Breeze_Light
export HYPRCURSOR_SIZE=24
hyprctl setcursor Breeze_Light 24
gsettings set org.gnome.desktop.interface cursor-theme 'Breeze_Light'
gsettings set org.gnome.desktop.interface cursor-size 24
