-- Original two-monitor layout. Adjust output names using `hyprctl monitors`.
-- Replace the default hl.monitor line in config/hypr/hyprland.lua with these.
-- LG on the right; Samsung on the left, vertically centered.
hl.monitor({ output = "DVI-D-1", mode = "1920x1080@60", position = "1366x0", scale = 1 })
hl.monitor({ output = "HDMI-A-1", mode = "1366x768@59.79", position = "0x156", scale = 1 })

-- Desktops 1-5 on the main monitor, 6-9 on the second one.
-- Replace the "Six persistent desktops" loop at the end of hyprland.lua with these.
for i = 1, 5 do
    hl.workspace_rule({ workspace = tostring(i), monitor = "DVI-D-1", persistent = true, default = i == 1 })
end
for i = 6, 9 do
    hl.workspace_rule({ workspace = tostring(i), monitor = "HDMI-A-1", persistent = true, default = i == 6 })
end

-- Second-monitor desktops 6-9 also on Super+Alt+1..4 (add after the Super+1..9 loop).
for i = 1, 4 do
    hl.bind(mainMod .. " + ALT + " .. i, hl.dsp.focus({ workspace = 5 + i }))
    hl.bind(mainMod .. " + ALT + SHIFT + " .. i, hl.dsp.window.move({ workspace = 5 + i }))
end

-- Matching Waybar setting: in config/waybar/Modules, replace
-- "persistent-workspaces" of "hyprland/workspaces#letters" with:
--   "persistent-workspaces": { "DVI-D-1": [1, 2, 3, 4, 5], "HDMI-A-1": [6, 7, 8, 9] }
