-- Optional snippet for Hyprland 0.55+. HyprMotion does not install this rule.
-- Replace any older rule that floats every window of this application.
hl.window_rule({
    name = "hyprmotion-quick-panel-float",
    match = {
        initial_class = [[^io\.github\.hyprmotion\.HyprMotion$]],
        initial_title = [[^HyprMotion — Quick Panel$]],
    },
    float = true,
})
