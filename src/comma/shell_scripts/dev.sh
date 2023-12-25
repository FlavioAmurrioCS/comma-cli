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

function shUtil.withCache() {
    # TODO: FIX
    local cache_dir="/tmp/.command_cache" cmd_str_to_be_hash command_hash cache_file cmd_exit_code temp_cache_file
    mkdir -p "${cache_dir}"
    case "${1}" in
    --permanent) shift 1 && cmd_str_to_be_hash="${*}" ;;
    --hourly) shift 1 && cmd_str_to_be_hash="$(date +'%Y_%m_%d_%H') ${*}" ;;
    *) cmd_str_to_be_hash="$(date +'%Y_%m_%d') ${*}" ;;
    esac
    command_hash=$(echo "${cmd_str_to_be_hash}" | md5sum | grep -oE '[a-z0-9]+')
    cache_file="${cache_dir}/$(shUtil.joinBy '_' "${@}")_${command_hash}"

    if [ -f "${cache_file}" ] && [ -z "${BUST_CACHE}" ]; then
        : "Using cache: ${cache_file}" && cat "${cache_file}" && return 0
    else
        temp_cache_file=$(mktemp)
        {
            echo -n "1" >/tmp/cache_return_code
            "${@}"
            echo -n "$?" >/tmp/cache_return_code
        } | tee "${temp_cache_file}"
        cmd_exit_code="$(head -n 1 "/tmp/cache_return_code")" && shUtil.quiet rm /tmp/cache_return_code
        if [ "${cmd_exit_code}" -eq 0 ]; then
            shUtil.quiet mv "${temp_cache_file}" "${cache_file}"
        fi
        return "${cmd_exit_code}"
    fi
}

function ,noerror() { "${@}" 2>/dev/null; }
function ,nooutput() { "${@}" >/dev/null 2>&1; }
function ,cache_clear() { ,nooutput rm -rf "${HOME}/.cache/dev.sh"; }

function ,cache() {

    if [ -n "${NO_CACHE}" ]; then
        "${@}"
        return $?
    fi
    local cache_dir="${HOME}/.cache/dev.sh" \
        cache_file \
        temp_cache_file \
        temp_return_code \
        cmd_exit_code
    # TODO: Consider adding cache expiration
    # case "${1}" in
    # --permanent) shift 1 && cmd_str_to_be_hash="${*}" ;;
    # --hourly) shift 1 && cmd_str_to_be_hash="$(date +'%Y_%m_%d_%H') ${*}" ;;
    # *) cmd_str_to_be_hash="$(date +'%Y_%m_%d') ${*}" ;;
    # esac
    # command_hash=$(echo "${cmd_str_to_be_hash}" | md5sum | grep -oE '[a-z0-9]+')
    # cache_file="${cache_dir}/$(shUtil.joinBy '_' "${@}")_${command_hash}"
    cache_file="${cache_dir}/$(echo "${@}" | { md5sum 2>/dev/null || md5; } | cut -d' ' -f1)"

    if [ -f "${cache_file}" ]; then
        cat "${cache_file}"
        return 0
    fi

    temp_return_code=$(mktemp)
    temp_cache_file=$(mktemp)
    {
        echo -n "1" >"${temp_return_code}"
        "${@}"
        echo -n "$?" >"${temp_return_code}"
    } | tee "${temp_cache_file}"
    cmd_exit_code="$(head -n 1 "${temp_return_code}")"
    if [ "${cmd_exit_code}" -eq 0 ]; then
        mkdir -p "${cache_dir}"
        mv "${temp_cache_file}" "${cache_file}"
    fi

    return "${cmd_exit_code}"
}

function ,list_git_projects(){
    api_url
    for source in "${@}"; do

        case "${source}" in
        *github.com*)
            ,cache curl --silent https://api.github.com/users/FlavioAmurrioCS/repos?per_page=999 | jq -r '.[] | select(.fork == false) | .ssh_url'
            ;;
        *)
            echo "Unknown source: ${source}" >&2
            return 1
            ;;
        esac
    done
}

function ,git_projects() {
    local project domain owner repo project_path
    for project in $(,cache curl --silent https://api.github.com/users/FlavioAmurrioCS/repos?per_page=999 | jq -r '.[] | select(.fork == false) | .ssh_url' | fzf --multi --exit-0); do
        read -r domain owner repo <<<"$(echo "${project}" | sed -E 's/.*@(.+):(.+)\/(.+)\.git/\1 \2 \3/')"
        project_path="${HOME}/dev/${domain}/${owner}/${repo}"
        if [ ! -d "${project_path}" ]; then
            git clone "${project}" "${project_path}"
        fi
    done
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
