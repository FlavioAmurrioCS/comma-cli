#!/usr/bin/env bash
# TODO: Make sure this works for bash,zsh
# TODO: Add check for which shell is being used
# TODO: Add shims for fzf and gum
# TODO: Use gum for enhanced user experience
# TODO: Add support for zsh

###############################################################################
# region: SCRIPT SETUP DO NOT EDIT
###############################################################################
__DEV_SH_SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__DEV_SH_SCRIPT__="${__DEV_SH_SCRIPT_DIR__}/$(basename "${BASH_SOURCE[0]}")"
__DEV_SH_FUNCTION_LIST__=()
while IFS='' read -r line; do
    # TODO: ADD MARKER FUNCTIONS TO DIFFERENTIATE SOURCE AND EXECUTABLE FUNCTIONS
    __DEV_SH_FUNCTION_LIST__+=("$line")
done < <(grep -E "^function " "${__DEV_SH_SCRIPT__}" | cut -d' ' -f2 | cut -d'(' -f1 | grep -vE "^_")
###############################################################################
# endregion: SCRIPT SETUP DO NOT EDIT
###############################################################################

###############################################################################
# region: FUNCTIONS THAT ARE COMMON FOR BOTH SOURCED AND EXECUTED
###############################################################################
function _select_project() {
    local selected
    selected="$(find ~/{dev,worktrees,projects} -maxdepth 3 \( -name .git -or -name packed-refs \) -prune -exec dirname {} \; 2>/dev/null | fzf)"
    [ -n "${selected}" ] && echo "${selected}" && return 0
    return 1
}
###############################################################################
# endregion: FUNCTIONS THAT ARE COMMON FOR BOTH SOURCED AND EXECUTED
###############################################################################

if (return 0 2>/dev/null); then
    : File is being sourced
    ###############################################################################
    # region: FUNCTIONS THAT SHOULD ONLY BE AVAILABLE WHEN FILE IS BEING SOURCED
    ###############################################################################
    function ,cd() {
        local selected
        selected="$(_select_project)"
        [ -n "${selected}" ] && cd "${selected}" && return 0
        return 1
    }

    function ,activate() {
        local walker found
        walker=${PWD}
        while true; do
            found="$(find . -type f -name activate -not -path './.tox/*' -print -quit)"
            # shellcheck disable=SC1090
            [ -n "${found}" ] && source "${found}" && return 0
            [ "${walker}" = "/" ] && return 1
            walker="$(dirname "${walker}")"
        done
    }

    function ,code() {
        local selected
        selected="$(_select_project)"
        [ -n "${selected}" ] && code "${selected}" && return 0
        return 1
    }
    ###############################################################################
    # endregion: FUNCTIONS THAT SHOULD ONLY BE AVAILABLE WHEN FILE IS BEING SOURCED
    ###############################################################################

    ###############################################################################
    # region: DO NOT EDIT THE BLOCK BELOW
    ###############################################################################
    function dev.sh() {
        "${__DEV_SH_SCRIPT__}" "${@}"
    }
    export PATH="${PATH}:${HOME}/.local/bin"
    complete -W "${__DEV_SH_FUNCTION_LIST__[*]}" dev.sh
    complete -W "${__DEV_SH_FUNCTION_LIST__[*]}" ./dev.sh
    echo "You can now do dev.sh [tab][tab] for autocomplete :)" >&2
    return 0
    ###############################################################################
    # endregion: DO NOT EDIT THE BLOCK ABOVE
    ###############################################################################
fi

###############################################################################
# region: FUNCTIONS THAT SHOULD ONLY BE ACCESS WHEN FILE IS BEING EXECUTED
###############################################################################

function hello_world() {
    echo "Hello World!"
}
###############################################################################
# endregion: FUNCTIONS THAT SHOULD ONLY BE ACCESS WHEN FILE IS BEING EXECUTED
###############################################################################

###############################################################################
# region: SCRIPT SETUP DO NOT EDIT
###############################################################################
: File is being executed
[ "${1}" == 'debug' ] && set -x && shift 1

if [ -n "${1}" ] && [[ ${__DEV_SH_FUNCTION_LIST__[*]} =~ ${1} ]]; then
    "${@}"
    exit $?
else
    echo "Usage: ${0} [function_name] [args]" >&2
    echo "Available functions:" >&2
    for function in "${__DEV_SH_FUNCTION_LIST__[@]}"; do
        echo "    ${function}" >&2
    done
    exit 1
fi
###############################################################################
# endregion: SCRIPT SETUP DO NOT EDIT
###############################################################################
