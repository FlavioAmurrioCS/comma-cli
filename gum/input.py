from __future__ import annotations

import subprocess
from typing import Literal
# Usage: gum input
# Prompt for some input
# Flags:
#   -h, --help                   Show context-sensitive help.
#   -v, --version                Print the version number
#       --placeholder="Type something..."
#                                Placeholder value ($GUM_INPUT_PLACEHOLDER)
#       --prompt="> "            Prompt to display ($GUM_INPUT_PROMPT)
#       --cursor.mode="blink"    Cursor mode ($GUM_INPUT_CURSOR_MODE)
#       --value=""               Initial value (can also be passed via stdin)
#       --char-limit=400         Maximum value length (0 for no limit)
#       --width=40               Input width (0 for terminal width)
#                                ($GUM_INPUT_WIDTH)
#       --password               Mask input characters
#       --header=""              Header value ($GUM_INPUT_HEADER)
#       --timeout=0              Timeout until input aborts ($GUM_INPUT_TIMEOUT)


def gum_input(
    placeholder: str | None = None,
    prompt: str | None = None,
    cursor_mode: Literal['blink', 'hide', 'static'] | None = None,
    value: str | None = None,
    char_limit: int | None = None,
    width: int | None = None,
    password: bool = False,
    header: str | None = None,
    timeout: int | None = None,
) -> str:
    cmd = ['gum', 'input']
    if placeholder is not None:
        cmd.append(f'--placeholder={placeholder}')
    if prompt is not None:
        cmd.append(f'--prompt={prompt}')
    if cursor_mode is not None:
        cmd.append(f'--cursor.mode={cursor_mode}')
    if value is not None:
        cmd.append(f'--value={value}')
    if char_limit is not None:
        cmd.append(f'--char-limit={char_limit}')
    if width is not None:
        cmd.append(f'--width={width}')
    if password:
        cmd.append('--password')
    if header is not None:
        cmd.append(f'--header={header}')
    if timeout is not None:
        cmd.append(f'--timeout={timeout}')
    return subprocess.run(cmd, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=None).stdout.strip()


if __name__ == '__main__':
    print(f"User typed: '{gum_input()}'")
