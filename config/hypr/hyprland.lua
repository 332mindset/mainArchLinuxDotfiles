-- This is an example Hyprland Lua config file.
-- Refer to the wiki for more information.
-- https://wiki.hypr.land/Configuring/Start/

-- Please note not all available settings / options are set here.
-- For a full list, see the wiki

-- You can (and should!!) split this configuration into multiple files
-- Create your files separately and then require them like this:
-- require("myColors")


------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
-- Portable default: use the preferred mode and arrange outputs automatically.
-- Customize this for your displays; see examples/monitors.lua.
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1 })


---------------------
---- MY PROGRAMS ----
---------------------

-- Set programs that you use
local terminal    = os.getenv("HOME") .. "/.local/bin/open-terminal"
local fileManager = os.getenv("HOME") .. "/.local/bin/dolphin"
local menu        = "rofi -show drun"


-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/Configuring/Basics/Autostart/

-- Autostart necessary processes (like notifications daemons, status bars, etc.)
-- Or execute your favorite apps at launch like this:
--
-- hl.on("hyprland.start", function () 
--   hl.exec_cmd(terminal)
--   hl.exec_cmd("nm-applet")
--   hl.exec_cmd("waybar & hyprpaper & firefox")
-- end)


-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/

-- Optional NVIDIA overrides from the original setup (enable only if needed):
-- hl.env("LIBVA_DRIVER_NAME", "nvidia")
-- hl.env("__GLX_VENDOR_LIBRARY_NAME", "nvidia")
-- hl.env("WLR_NO_HARDWARE_CURSORS", "1")
hl.env("TERMINAL", terminal)
hl.env("XCURSOR_THEME", "Breeze_Light")
hl.env("HYPRCURSOR_THEME", "Breeze_Light")
hl.on("hyprland.start", function()
    hl.exec_cmd("~/.config/hypr/scripts/cursor.sh")
    hl.exec_cmd("~/.config/hypr/scripts/wallpaper_picker.py --restore")
    hl.exec_cmd("sleep 3 && waybar")
    hl.exec_cmd("swaync")
    hl.exec_cmd("~/.config/hypr/scripts/clipboard-start.sh")
end)

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")


-----------------------
----- PERMISSIONS -----
-----------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Permissions/
-- Please note permission changes here require a Hyprland restart and are not applied on-the-fly
-- for security reasons

-- hl.config({
--   ecosystem = {
--     enforce_permissions = true,
--   },
-- })

-- hl.permission("/usr/(bin|local/bin)/grim", "screencopy", "allow")
-- hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
-- hl.permission("/usr/(bin|local/bin)/hyprpm", "plugin", "allow")


-----------------------
---- LOOK AND FEEL ----
-----------------------

-- Refer to https://wiki.hypr.land/Configuring/Basics/Variables/
hl.config({
    general = {
        gaps_in  = 5,
        gaps_out = 20,

        border_size = 3,

        col = {
            active_border   = "rgba(606060ee)",
            inactive_border = "rgba(202020aa)",
        },

        -- Set to true to enable resizing windows by clicking and dragging on borders and gaps
        resize_on_border = false,

        -- Please see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Tearing/ before you turn this on
        allow_tearing = false,

        layout = "dwindle",
    },

    decoration = {
        rounding       = 16,
        rounding_power = 2,

        -- Change transparency of focused and unfocused windows
        active_opacity   = 1.0,
        inactive_opacity = 0.96,

        shadow = {
            enabled      = true,
            range        = 14,
            render_power = 2,
            color        = 0x66000000,
        },

        blur = {
            enabled   = true,
            size      = 8,
            passes    = 3,
            new_optimizations = true,
            xray = false,
        },
    },

    animations = {
        enabled = true,
    },
})

-- Smooth motion: soft window entrance, cinematic workspace slides.
-- https://wiki.hypr.land/Configuring/Advanced-and-Cool/Animations/
hl.curve("smoothOut", { type = "bezier", points = { {0.16, 1}, {0.30, 1} } })
hl.curve("smoothIn", { type = "bezier", points = { {0.40, 0}, {0.85, 0.35} } })
hl.curve("workspaceGlide", { type = "bezier", points = { {0.22, 0.80}, {0.25, 1} } })
hl.curve("softFade", { type = "bezier", points = { {0.25, 0.10}, {0.25, 1} } })
hl.curve("softSpring", { type = "spring", mass = 1, stiffness = 190, dampening = 25 })

hl.animation({ leaf = "global", enabled = true, speed = 5, bezier = "smoothOut" })
hl.animation({ leaf = "windows", enabled = true, speed = 5, bezier = "smoothOut" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 5, spring = "softSpring", style = "popin 88%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 3, bezier = "smoothIn", style = "popin 94%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 4.5, bezier = "smoothOut" })
hl.animation({ leaf = "fade", enabled = true, speed = 3.5, bezier = "softFade" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 3.5, bezier = "softFade" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 2.8, bezier = "softFade" })
hl.animation({ leaf = "fadeSwitch", enabled = true, speed = 3, bezier = "softFade" })
hl.animation({ leaf = "fadeShadow", enabled = true, speed = 4, bezier = "softFade" })
hl.animation({ leaf = "fadeDim", enabled = true, speed = 4, bezier = "softFade" })
hl.animation({ leaf = "border", enabled = true, speed = 4, bezier = "softFade" })
hl.animation({ leaf = "layers", enabled = true, speed = 4, bezier = "smoothOut" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 4, bezier = "smoothOut", style = "slide" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 3, bezier = "smoothIn", style = "slide" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 3, bezier = "softFade" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 2.5, bezier = "softFade" })
hl.animation({ leaf = "fadePopupsIn", enabled = true, speed = 2.5, bezier = "smoothOut" })
hl.animation({ leaf = "fadePopupsOut", enabled = true, speed = 2, bezier = "softFade" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 6, bezier = "workspaceGlide", style = "slidefade 25%" })
hl.animation({ leaf = "workspacesIn", enabled = true, speed = 6, bezier = "workspaceGlide", style = "slidefade 25%" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 6, bezier = "workspaceGlide", style = "slidefade 25%" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 5, bezier = "smoothOut", style = "slidefadevert 20%" })
hl.animation({ leaf = "specialWorkspaceIn", enabled = true, speed = 5, bezier = "smoothOut", style = "slidefadevert 20%" })
hl.animation({ leaf = "specialWorkspaceOut", enabled = true, speed = 4, bezier = "smoothIn", style = "slidefadevert 20%" })
hl.animation({ leaf = "zoomFactor", enabled = true, speed = 5, bezier = "smoothOut" })

-- Ref https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/
-- "Smart gaps" / "No gaps when only"
-- uncomment all if you wish to use that.
-- hl.workspace_rule({ workspace = "w[tv1]", gaps_out = 0, gaps_in = 0 })
-- hl.workspace_rule({ workspace = "f[1]",   gaps_out = 0, gaps_in = 0 })
-- hl.window_rule({
--     name  = "no-gaps-wtv1",
--     match = { float = false, workspace = "w[tv1]" },
--     border_size = 0,
--     rounding    = 0,
-- })
-- hl.window_rule({
--     name  = "no-gaps-f1",
--     match = { float = false, workspace = "f[1]" },
--     border_size = 0,
--     rounding    = 0,
-- })

-- See https://wiki.hypr.land/Configuring/Layouts/Dwindle-Layout/ for more
hl.config({
    dwindle = {
        preserve_split = true, -- You probably want this
    },
})

-- See https://wiki.hypr.land/Configuring/Layouts/Master-Layout/ for more
hl.config({
    master = {
        new_status = "master",
    },
})

-- See https://wiki.hypr.land/Configuring/Layouts/Scrolling-Layout/ for more
hl.config({
    scrolling = {
        fullscreen_on_one_column = true,
    },
})

----------------
----  MISC  ----
----------------

hl.config({
    misc = {
        force_default_wallpaper = -1,    -- Set to 0 or 1 to disable the anime mascot wallpapers
        disable_hyprland_logo   = false, -- If true disables the random hyprland logo / anime girl background. :(
    },
})


---------------
---- INPUT ----
---------------

hl.config({
    input = {
        kb_layout  = "us,ru",
        kb_variant = "",
        kb_model   = "",
        kb_options = "grp:win_space_toggle",
        kb_rules   = "",

        follow_mouse = 1,

        sensitivity = -0.3, -- -1.0 - 1.0, 0 means no modification.

        touchpad = {
            natural_scroll = false,
        },
    },
})

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace"
})

-- Example per-device config
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Devices/ for more
hl.device({
    name        = "epic-mouse-v1",
    sensitivity = -0.5,
})


---------------------
---- KEYBINDINGS ----
---------------------

local mainMod = "SUPER" -- Sets "Windows" key as main modifier

-- Example binds, see https://wiki.hypr.land/Configuring/Basics/Binds/ for more
hl.bind(mainMod .. " + Q", hl.dsp.exec_cmd(terminal))
local closeWindowBind = hl.bind(mainMod .. " + C", hl.dsp.window.close())
-- closeWindowBind:set_enabled(false)

hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
-- Use the custom launchers when installed, with working local fallbacks.
local home = os.getenv("HOME")
local function script_or(path, fallback)
    local file = io.open(home .. path, "r")
    if file then file:close(); return "~" .. path end
    return fallback
end
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(script_or("/.config/waybar/scripts/launch.sh", "pkill -x waybar; waybar")))
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + N", hl.dsp.exec_cmd("swaync-client -t -sw"))
hl.bind("CTRL + SUPER + V", hl.dsp.exec_cmd("~/.config/hypr/scripts/clipboard.sh"))
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd("~/.config/hypr/scripts/lock.sh"))
hl.bind("SUPER + SHIFT + D", hl.dsp.exec_cmd("~/.config/hypr/scripts/lock.sh"))
hl.bind("Print", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh area"))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh full"))
for _, entry in ipairs({
    { "SUPER + F", "/.config/hypr/scripts/wallpaper_picker.py" },
    { "SUPER + SHIFT + E", "/.config/hypr/scripts/power_menu.py" },
}) do
    local command = script_or(entry[2], nil)
    if command then hl.bind(entry[1], hl.dsp.exec_cmd(command)) end
end
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"))    -- dwindle only

-- Move focus with mainMod + arrow keys
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- Switch workspaces with mainMod + [0-9]
-- Move active window to a workspace with mainMod + SHIFT + [0-9]
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(mainMod .. " + " .. key,             hl.dsp.focus({ workspace = i}))
    hl.bind(mainMod .. " + SHIFT + " .. key,     hl.dsp.window.move({ workspace = i }))
end

-- Example special workspace (scratchpad)
hl.bind(mainMod .. " + S",         hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- Scroll through existing workspaces with mainMod + scroll
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Laptop multimedia keys for volume and LCD brightness
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),      { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true, repeating = true })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",  hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"),                  { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown",hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"),                  { locked = true, repeating = true })

-- Requires playerctl
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })


--------------------------------
---- WINDOWS AND WORKSPACES ----
--------------------------------

-- See https://wiki.hypr.land/Configuring/Basics/Window-Rules/
-- and https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/

-- Example window rules that are useful

local suppressMaximizeRule = hl.window_rule({
    -- Ignore maximize requests from all apps. You'll probably like this.
    name  = "suppress-maximize-events",
    match = { class = ".*" },

    suppress_event = "maximize",
})
-- suppressMaximizeRule:set_enabled(false)

hl.window_rule({
    -- Fix some dragging issues with XWayland
    name  = "fix-xwayland-drags",
    match = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },

    no_focus = true,
})

-- Layer rules also return a handle.
-- local overlayLayerRule = hl.layer_rule({
--     name  = "no-anim-overlay",
--     match = { namespace = "^my-overlay$" },
--     no_anim = true,
-- })
-- overlayLayerRule:set_enabled(false)

-- Hyprland-run windowrule
hl.window_rule({
    name  = "move-hyprland-run",
    match = { class = "hyprland-run" },

    move  = "20 monitor_h-120",
    float = true,
})

-- Preserve monitor workspace assignments.
for i = 1, 5 do
    local rule = { workspace = tostring(i), persistent = true }
    hl.workspace_rule(rule)
end
