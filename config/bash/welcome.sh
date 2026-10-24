# Pastel system card for new graphical terminals.
_rice_terminal_welcome() {
    [[ $- == *i* && -t 0 && -t 1 ]] || return 0
    [[ ${TERM:-dumb} != dumb && -z ${BASH_EXECUTION_STRING:-} ]] || return 0
    [[ -n ${WAYLAND_DISPLAY:-}${DISPLAY:-} && -z ${SSH_CONNECTION:-} ]] || return 0
    command -v fastfetch >/dev/null 2>&1 || return 0

    local welcome_tty
    welcome_tty="$(tty 2>/dev/null)" || return 0
    [[ ${RICE_TERMINAL_WELCOME_TTY:-} != "$welcome_tty" ]] || return 0
    export RICE_TERMINAL_WELCOME_TTY="$welcome_tty"

    printf '\n'
    command fastfetch --config "${XDG_CONFIG_HOME:-$HOME/.config}/fastfetch/config.jsonc" 2>/dev/null
    printf '\n'
}
_rice_terminal_welcome
unset -f _rice_terminal_welcome
