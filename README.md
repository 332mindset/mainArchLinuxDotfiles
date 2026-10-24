# Arch Linux + Hyprland dotfiles

My desktop configuration: translucent windows, smooth animations, a compact
Waybar, One Dark Rofi menus, a dashboard lock screen and a matching terminal.

[Watch the desktop showcase on YouTube](https://www.youtube.com/watch?v=beIpVuMDd-8).

**Install the dependencies below before applying these dotfiles.**
`install.py` copies configuration files, scripts and wallpapers and backs up
the files it replaces. Package installation, graphics driver setup and shell
integration are manual steps described below. Running `python3 install.py`
only previews the changes; add `--apply` to install the files.

## What's included

| Component | Configuration |
| --- | --- |
| Hyprland | Lua config, animations, window rules and keybindings |
| Waybar | Workspaces A–F, media, tray, volume, keyboard layout (EN/RU), idle inhibitor and notifications |
| Rofi | One Dark launcher (apps, configuration folders, file browser), clipboard, wallpaper carousel and power menu |
| Foot + Bash | Monochrome terminal, prompt, completion and Fastfetch welcome card |
| Hyprlock | Dashboard lock screen: music, calendar, system stats, volume and notifications ([details](config/hypr/assets/hyprlock/dashboard/README.md)) |
| SwayNC | Notification popups and control center |
| Cava | Standalone audio visualizer |
| Dolphin | Custom stylesheet and launcher |
| GTK + Fontconfig | Fonts and Breeze Light cursor settings |
| Scripts | Clipboard history, screenshots, wallpaper switching and power menu |

The wallpaper picker reads `~/Pictures/Wallpapers`. Wallpapers from the
[`wallpapers`](wallpapers) folder are installed there; add your own images
for more choices. On first open the picker caches rounded preview cards in
`~/.cache/wallpaper-picker`.

## Compatibility

Prepared from an Arch Linux installation with Hyprland **0.56.2**, Waybar 0.15.0,
Rofi 2.0.0, Foot 1.28.0, Hyprlock 0.9.6, SwayNC 0.12.6, Cava 1.0.0 and
awww 0.12.1. These are the source machine's versions, not a guarantee that
every future update will behave the same.

This config uses Hyprland's **Lua API** (`hyprland.lua`). Older installations
that only support `hyprland.conf` cannot use it directly.
See the [Hyprland configuration documentation](https://wiki.hypr.land/configuring/core/).

The shared version selects monitor modes automatically. NVIDIA overrides from
the original machine are commented out. The original two-monitor layout is in
[`examples/monitors.lua`](examples/monitors.lua).

This setup expects Bash, a standard home path without spaces or special
characters, and the default `~/.config` location.

## Dependencies

These instructions start from an already installed Arch Linux system.
Review and install the packages below before following the installation steps.
The installer does not install packages or configure your graphics drivers.

You can apply these dotfiles from either a graphical session or a TTY.
On a minimal Arch installation with only a TTY, first set up a regular user,
working internet, access to `sudo`, and the graphics drivers appropriate for
your GPU. Then install the dependencies below (including Git and Python),
apply the dotfiles as that user, and launch Hyprland using the command in the
installation section. The Python installer alone does not prepare a bare
Arch installation for a graphical desktop.

```sh
sudo pacman -Syu --needed \
  hyprland hyprlock waybar rofi foot swaync cava awww \
  git python wl-clipboard cliphist grim slurp libnotify \
  wireplumber pipewire pipewire-pulse playerctl pavucontrol \
  fastfetch dolphin fontconfig ttf-jetbrains-mono-nerd adwaita-fonts \
  breeze-cursors breeze-icons glib2 util-linux procps-ng coreutils \
  xdg-desktop-portal-hyprland ffmpeg librsvg
```

`ffmpeg` renders wallpaper previews; `librsvg` (`rsvg-convert`) draws the lock
screen dashboard. Optional: `brightnessctl` enables the brightness keys; `code` (Visual Studio
Code) enables the Rofi **Configs** tab. The desktop itself does not need VS Code.

## Installation

1. Clone the repository and open its folder:

   ```sh
   git clone https://github.com/332mindset/mainArchLinuxDotfiles.git
   cd mainArchLinuxDotfiles
   ```

   Alternatively, use **Code → Download ZIP**, extract it, and open a terminal
   in the extracted folder.
2. Review the configuration and preview the changes:

   ```sh
   python3 install.py
   ```

3. Install as your desktop user, **without sudo**:

   ```sh
   python3 install.py --apply
   ```

The installer copies files into your home directory, fills in your home path
where the templates contain `@HOME@`, and sets executable permissions on
scripts. Existing component folders/files are moved to a dated backup under
`~/.local/state/dotfiles/backups/`. Each listed config folder is replaced as a
whole, so settings from your old folder remain in the backup. Shared folders
(`gtk-3.0`, `gtk-4.0`, `fontconfig`) are updated file by file, so other data
there, such as GTK bookmarks, stays in place.

Symlinked destinations are refused: if you already manage your configuration
with Stow or another dotfiles manager, adapt the files through that manager.
The installer leaves `~/.bashrc` and your login configuration alone.

4. To enable the matching Bash prompt and welcome card, append the contents
   of [`examples/bashrc.snippet`](examples/bashrc.snippet) to your `~/.bashrc`.
5. Review `~/.config/hypr/hyprland.lua`. Keyboard layouts are **US + Russian**;
   **Super + Space** switches them. Set `kb_layout = "us"` and `kb_options = ""`
   if you only want English.
6. Log out and start Hyprland again when ready. From a TTY, you can use:

   ```sh
   start-hyprland -- --config "$HOME/.config/hypr/hyprland.lua"
   ```

7. Press **Super + F** and choose a wallpaper. It will be restored on subsequent
   sessions after the first successful selection.

## Keybindings

`Super` is the Windows key.

| Keys | Action |
| --- | --- |
| Super + Q | Open Foot |
| Super + C | Close the focused window |
| Super + E | Open Dolphin |
| Super + D | Open Rofi |
| Super + F | Choose a wallpaper |
| Super + N | Toggle notifications |
| Super + R | Restart Waybar |
| Super + L / Super + Shift + D | Lock the screen |
| Ctrl + Super + V | Clipboard history |
| Ctrl + End / Ctrl + Shift + End | Area / full screenshot, saved and copied |
| Super + Shift + E | Power menu |
| Super + 1…9 | Switch workspace |
| Super + Shift + 1…9 | Move window to workspace |
| Super + Space | Switch keyboard layout (EN/RU) |
| Super + arrows | Move focus |
| Super + V | Toggle floating |
| Super + P / Super + J | Pseudotile / toggle split |
| Super + S / Super + Shift + S | Toggle / move to scratchpad |
| Super + mouse wheel | Next / previous workspace on this monitor |
| Super + mouse drag | Move or resize a window |

The clipboard collector stores copied text/images locally; its history is
runtime data and is not included in this repository.

## Troubleshooting and backups

Check configuration errors with `hyprctl configerrors`. Reload an already
running desktop with `~/.config/hypr/scripts/apply-desktop.sh` after checking
your monitor settings. A fresh session also starts the clipboard collector
and notification daemon.

If symbols look like boxes, check that JetBrainsMono Nerd Font is installed.
The wallpaper picker requires **awww**, not hyprpaper.

To restore a previous configuration, use the backup directory printed by the
installer. It mirrors the replaced paths in your home (for example,
`BACKUP/.config/hypr` is the old `~/.config/hypr`). From another TTY/session,
remove or rename the corresponding installed component folder, then copy
its backed-up version into place. Files that did not exist before installation
have no backup. Your other configuration folders are not part of this install.

## Credits

Existing source comments and attributions are preserved:

- Waybar styling credits [JaKooLit](https://github.com/JaKooLit).
- The Rofi theme is based on
  [adi1090x/rofi](https://github.com/adi1090x/rofi/blob/master/files/launchers/type-1/style-5.rasi)
  (type-1, style-5) with the One Dark colors.
