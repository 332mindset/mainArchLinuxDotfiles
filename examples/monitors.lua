-- Original two-monitor layout. Adjust output names using `hyprctl monitors`.
-- Replace the default hl.monitor line in config/hypr/hyprland.lua with these.
hl.monitor({ output = "DVI-D-1", mode = "1920x1080@60", position = "1366x0", scale = 1 })
hl.monitor({ output = "HDMI-A-1", mode = "1366x768@59.79", position = "0x156", scale = 1 })

-- Desktops 1-6 on the main monitor, 7-9 on the second one.
-- Replace the "Six persistent desktops" loop at the end of hyprland.lua with these.
for i = 1, 6 do
    hl.workspace_rule({ workspace = tostring(i), monitor = "DVI-D-1", persistent = true, default = i == 1 })
end
for i = 7, 9 do
    hl.workspace_rule({ workspace = tostring(i), monitor = "HDMI-A-1", persistent = true, default = i == 7 })
end

-- Second-monitor desktops 7-9 also on Super+Alt+1..3 (add after the Super+1..9 loop).
for i = 1, 3 do
    hl.bind(mainMod .. " + ALT + " .. i, hl.dsp.focus({ workspace = 6 + i }))
    hl.bind(mainMod .. " + ALT + SHIFT + " .. i, hl.dsp.window.move({ workspace = 6 + i }))
end

-- Matching Waybar setting: in config/waybar/Modules, replace
-- "persistent-workspaces" of "hyprland/workspaces#letters" with:
--   "persistent-workspaces": { "DVI-D-1": [1, 2, 3, 4, 5, 6], "HDMI-A-1": [7, 8, 9] }
