from __future__ import annotations

import subprocess
# Usage: gum file [<path>]
# Pick a file from a folder
# Arguments:
#   [<path>]    The path to the folder to begin traversing ($GUM_FILE_PATH)
# Flags:
#   -h, --help          Show context-sensitive help.
#   -v, --version       Print the version number
#   -c, --cursor=">"    The cursor character ($GUM_FILE_CURSOR)
#   -a, --all           Show hidden and 'dot' files ($GUM_FILE_ALL)
#       --file          Allow files selection ($GUM_FILE_FILE)
#       --directory     Allow directories selection ($GUM_FILE_DIRECTORY)
#       --height=0      Maximum number of files to display ($GUM_FILE_HEIGHT)
#       --timeout=0     Timeout until command aborts without a selection
#                       ($GUM_FILE_TIMEOUT)


def gum_file(
        path: str | None = None,
        cursor: str | None = None,
        all: bool = False,
        file: bool = False,
        directory: bool = False,
        height: int | None = None,
        timeout: int | None = None,
) -> str | None:

    cmd = ['gum', 'file']
    if cursor is not None:
        cmd.append(f'--cursor={cursor}')
    if all:
        cmd.append('--all')
    if file:
        cmd.append('--file')
    if directory:
        cmd.append('--directory')
    if height is not None:
        cmd.append(f'--height={height}')
    if timeout is not None:
        cmd.append(f'--timeout={timeout}')
    if path is not None:
        cmd.append(path)

    return subprocess.run(cmd, encoding='utf-8', errors='ignore', capture_output=True).stdout.strip()
