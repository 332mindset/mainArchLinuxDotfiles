# Hyprlock dashboard

Open with **Super+L** or **Super+Shift+D**, or run:

```sh
~/.config/hypr/scripts/lock.sh
```

The background is a blurred snapshot of the desktop captured by Hyprlock at lock
time. A dark translucent overlay and glass cards keep text readable. The current
wallpaper from `~/.local/state/wallpaper/current.json` is the fallback when
screencopy is unavailable. The launcher queries monitor sizes on each launch.
The generated native Hyprlock layout is
`~/.config/hypr/hyprlock-dashboard.conf`. The password field uses Hyprlock's normal
PAM authentication. Existing authentication settings were not modified.

`scripts/lock-dashboard.py` renders SVG content with the installed `rsvg-convert`.
Panel backgrounds and borders are native Hyprlock shapes; icons use consistent
SVG strokes. The date is in Russian and the current calendar day has dark text
on its light accent. Track titles wrap across two lines.
The worker refreshes the cards once per second and exits when Hyprlock exits.
If preparing the dashboard fails, the launcher uses the classic fallback theme.

Controls:

- Music: previous, play/pause, next. Chooses a playing MPRIS player first.
- Calendar: arrows change month; opening the lock resets to the current month.
- Volume: speaker toggles mute; click the bar to select a volume in steps of 10%;
  the minus/plus controls lower/raise volume by 5%.
- Notifications: bell toggles SwayNC Do Not Disturb; trash clears SwayNC.
- Bottom row: lock status, logout, reboot, power off. Logout/reboot/power off
  require a second click on the same button within five seconds.

Notifications show SwayNC's current count and up to two notifications received
while the lock is running. SwayNC does not expose existing notification bodies
through its control API, so older messages are not copied into this panel.
Message content stays in worker memory and is not written to a history file.

System data comes from `/proc`, hwmon, and `nvidia-smi` or DRM sysfs. Unavailable
sources display a dash. Player and audio controls need the existing `playerctl`
and `wpctl`; SwayNC uses `busctl` and `dbus-monitor` on the session bus.

Preview (renders over the wallpaper without locking; the real lock uses the
desktop snapshot):

```sh
~/.config/hypr/scripts/lock-dashboard.py --preview /tmp/hyprlock-preview.png
```

Logs: `~/.cache/hyprlock-dashboard/prepare.log` and `worker.log`.

If the dashboard cannot be prepared, `lock.sh` falls back to the classic
lock screen in `~/.config/hypr/hyprlock-fallback.conf`.

Configuration reference: https://wiki.hypr.land/Hypr-Ecosystem/hyprlock/
