from __future__ import annotations

import subprocess
# Usage: gum confirm [<prompt>]
# Ask a user to confirm an action
# Arguments:
#   [<prompt>]    Prompt to display.
# Flags:
#   -h, --help                 Show context-sensitive help.
#   -v, --version              Print the version number
#       --default              Default confirmation action
#       --affirmative="Yes"    The title of the affirmative action
#       --negative="No"        The title of the negative action
#       --timeout=0            Timeout until confirm returns selected value or default if provided
#                              ($GUM_CONFIRM_TIMEOUT)


def gum_confirm(
    prompt: str,
    default: bool = False,
    affirmative: str | None = None,
    negative: str | None = None,
    timeout: int | None = None,
) -> bool:
    cmd = ['gum', 'confirm']
    if default:
        cmd.append('--default')
    if affirmative is not None:
        cmd.append(f'--affirmative={affirmative}')
    if negative is not None:
        cmd.append(f'--negative={negative}')
    if timeout is not None:
        cmd.append(f'--timeout={timeout}')
    cmd.append(prompt)
    return subprocess.run(cmd).returncode == 0
