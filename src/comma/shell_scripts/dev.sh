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
    selected="$(find ~/{dev,worktrees,projects,dev/*git*/*} -maxdepth 3 \( -name .git -or -name packed-refs \) -prune -exec dirname {} \; 2>/dev/null | grep -v /trash/ | fzf --keep-right)"
    [ -n "${selected}" ] && echo "${selected}" && return 0
    return 1
}

function ,noerror() { "${@}" 2>/dev/null; }
function ,nooutput() { "${@}" >/dev/null 2>&1; }
function ,cache_clear() { ,nooutput rm -rf "${HOME}/.cache/dev.sh"; }
function ,uniq() { awk '!x[$0]++' "${@}"; }
function grep() { command grep --color=auto --line-buffered "${@}"; }

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

function __get_repos__() {
    local domain user repo api_url complete_url_user complete_url_org curl_cmd
    read -r domain user repo <<<"$(echo "${1}" | awk -F[/:] '{print $4,$5,$6}')"
    curl_cmd=(curl --silent --fail)

    case "${domain}" in
    github.com) api_url="https://api.github.com" ;;
    *)
        api_url="https://${domain}/api/v3"
        curl_cmd+=(-H "Authorization: token ${GITHUB_TOKEN}")
        ;;
    esac
    complete_url_user="${api_url}/users/${user}/repos?per_page=99999"
    complete_url_org="${api_url}/orgs/${user}/repos?per_page=99999"
    "${curl_cmd[@]}" "${complete_url_org}" || "${curl_cmd[@]}" "${complete_url_user}"
}

function ,clone() {
    local project domain owner repo project_path projects
    projects=${1:-"$({
        for i in $(echo "${GITHUB_FOLLOW}" | tr ' ' '\n' | sort -u); do
            ,cache __get_repos__ "${i}" &
        done
    } | grep "ssh_url" | cut -d '"' -f4 | sort -u | fzf --multi --exit-0)"}

    if [ -z "${projects}" ] && [ -z "${GITHUB_FOLLOW}" ]; then
        echo "Set GITHUB_FOLLOW to a list of github users/orgs to follow or pass in clone url directly. If github enterprise, set GITHUB_TOKEN as well." >&2
        return 1
    fi

    for project in ${projects}; do
        case "${project}" in
        https*) read -r domain owner repo <<<"$(echo "${project}" | sed -E 's|https://([^/]+)/(.+)\/(.+).*|\1 \2 \3|')" ;;
        *) read -r domain owner repo <<<"$(echo "${project}" | sed -E 's/.*@(.+):(.+)\/(.+)\.git/\1 \2 \3/')" ;;
        esac

        project_path="${HOME}/dev/${domain}/${owner}/${repo}"
        if [ ! -d "${project_path}" ]; then
            git clone "${project}" "${project_path}"
        fi
    done
}

function ,mv-project() {
    local domain owner repo new_project_path git_remote original_project_path
    for original_project_path in "${@}"; do
        echo "- ${original_project_path}"
        original_project_path=$(realpath "${original_project_path}")
        git_remote=$(git -C "${original_project_path}" remote get-url origin 2>/dev/null)
        if [ -z "${git_remote}" ]; then
            echo "${original_project_path} does not have a remote origin" >&2
            continue
        fi
        case "${git_remote}" in
        https*) read -r domain owner repo <<<"$(echo "${git_remote}" | sed -E 's|https://([^/]+)/(.+)\/(.+).*|\1 \2 \3|')" ;;
        *) read -r domain owner repo <<<"$(echo "${git_remote}" | sed -E 's/.*@(.+):(.+)\/(.+)\.git/\1 \2 \3/')" ;;
        esac
        new_project_path="${HOME}/dev/${domain}/${owner}/$(basename "${original_project_path}")"
        if [ ! -d "${new_project_path}" ]; then
            mkdir -p "$(dirname "${new_project_path}")"
            mv "${original_project_path}" "${new_project_path}"
        else
            echo "${new_project_path} already exists. Skipping..." >&2
        fi
    done
}

function ,release_python_package() {
    local latest_tag project_version &&
        git checkout main &&
        git pull &&
        latest_tag=$(git describe --tags --abbrev=0) &&
        project_version="v$(hatch version)" || return 1
    if [[ "$latest_tag" == "$project_version" ]]; then
        echo "No new version to release"
        return 0
    fi
    git tag "${project_version}" &&
        git push origin --tags
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
        [ -n "${selected}" ] && code "${selected}" "${@}" && return 0
        return 1
    }

    function ,env() { env | fzf --multi; }
    # shellcheck disable=SC2139
    alias ,source="source ${__DEV_SH_SCRIPT__}"
    function ,runtool() { runtool "${@}"; }
    function ,web() {
        local git_url
        git_url=$(git remote get-url origin) || return 1
        case "${git_url}" in
        https*) : ;;
        *) git_url="$(echo "${git_url}" | sed -E 's|.*@(.+):(.+)\/(.+)\.git|https://\1/\2/\3|')" ;;
        esac
        ,runtool run rifle "${git_url}"
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
    export HATCH_ENV_TYPE_VIRTUAL_PATH=venv
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
