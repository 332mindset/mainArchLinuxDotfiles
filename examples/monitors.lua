-- Original two-monitor layout. Adjust output names using `hyprctl monitors`.
-- Replace the default hl.monitor line in config/hypr/hyprland.lua with these.
hl.monitor({ output = "DVI-D-1", mode = "1920x1080@60", position = "1366x0", scale = 1 })
hl.monitor({ output = "HDMI-A-1", mode = "1366x768@59.79", position = "0x156", scale = 1 })

-- To restore the original workspace assignments, add these inside the
-- workspace loop, before hl.workspace_rule(rule):
-- if i == 1 then rule.monitor = "DVI-D-1"; rule.default = true end
-- if i == 5 then rule.monitor = "HDMI-A-1"; rule.default = true end
