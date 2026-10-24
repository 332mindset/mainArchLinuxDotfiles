# Catppuccin Mocha: path, git branch and an arrow that turns red after a failed command.
ZSH_THEME_GIT_PROMPT_PREFIX=" %F{#6c7086}on%f %F{#cba6f7} "
ZSH_THEME_GIT_PROMPT_SUFFIX="%f"
ZSH_THEME_GIT_PROMPT_DIRTY=" %F{#fab387}●"
ZSH_THEME_GIT_PROMPT_CLEAN=""

PROMPT='%F{#89b4fa}%~%f$(git_prompt_info)
%(?.%F{#cba6f7}.%F{#f38ba8})❯%f '
