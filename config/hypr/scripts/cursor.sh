#!/usr/bin/env bash
# Bibata Modern Classic cursors, dark GTK theme and Papirus icons.
set -eu
cursor=Bibata-Modern-Classic
export XCURSOR_THEME=$cursor
export XCURSOR_SIZE=24
export HYPRCURSOR_THEME=$cursor
export HYPRCURSOR_SIZE=24
hyprctl setcursor "$cursor" 24
gsettings set org.gnome.desktop.interface cursor-theme "$cursor"
gsettings set org.gnome.desktop.interface cursor-size 24
gsettings set org.gnome.desktop.interface gtk-theme 'catppuccin-mocha-mauve-standard+default'
gsettings set org.gnome.desktop.interface icon-theme 'Papirus-Dark'
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
