#!/usr/bin/env bash
###############################################################################
# ADD FUNCTIONS THAT SHOULD ONLY BE AVAILABLE WHEN FILE IS BEING SOURCED BELOW
###############################################################################

###############################################################################
# START: DO NOT EDIT THE BLOCK BELOW
###############################################################################
__DEV_SH_SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__DEV_SH_SCRIPT__="${__DEV_SH_SCRIPT_DIR__}/$(basename "${BASH_SOURCE[0]}")"
__DEV_SH_FUNCTION_LIST__=()
while IFS='' read -r line; do
    # TODO: ADD MARKER FUNCTIONS TO DIFFERENTIATE SOURCE AND EXECUTABLE FUNCTIONS
    __DEV_SH_FUNCTION_LIST__+=("$line")
done < <(grep -E "^function " "${__DEV_SH_SCRIPT__}" | cut -d' ' -f2 | cut -d'(' -f1 | grep -vE "^__")

if (return 0 2>/dev/null); then
    : File is being sourced
    function dev.sh() {
        "${__DEV_SH_SCRIPT__}" "${@}"
    }
    export PATH="${PATH}:${HOME}/.local/bin"
    complete -W "${__DEV_SH_FUNCTION_LIST__[*]}" dev.sh
    complete -W "${__DEV_SH_FUNCTION_LIST__[*]}" ./dev.sh
    echo "You can now do dev.sh [tab][tab] for autocomplete :)" >&2
    return 0
fi
###############################################################################
# END: DO NOT EDIT THE IF BLOCK ABOVE
###############################################################################

###############################################################################
# ADD FUNCTIONS THAT SHOULD ONLY BE AVAILABLE WHEN FILE IS BEING EXECUTED BELOW
###############################################################################

function foobat() {
    echo "foobat"
}

###############################################################################
# DO NOT EDIT BELOW THIS LINE
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
