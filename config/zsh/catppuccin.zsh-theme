# Catppuccin Mocha prompt:
#    ~/path   branch ●                                   ✘ 1  22:47
#   ❯
# The arrow turns red and the exit code shows after a failed command.
ZSH_THEME_GIT_PROMPT_PREFIX="  %F{#cba6f7} "
ZSH_THEME_GIT_PROMPT_SUFFIX="%f"
ZSH_THEME_GIT_PROMPT_DIRTY=" %F{#fab387}●"
ZSH_THEME_GIT_PROMPT_CLEAN=""

# Blank line between a command's output and the next prompt (not above the first one).
_prompt_spacer() { [[ -n $_prompt_drawn ]] && print; _prompt_drawn=1 }
precmd_functions+=(_prompt_spacer)

PROMPT='%F{#89b4fa} %B%~%b%f$(git_prompt_info)
%(?.%F{#cba6f7}.%F{#f38ba8})❯%f '
RPROMPT='%(?..%F{#f38ba8}✘ %?%f  )%F{#585b70}%*%f'
