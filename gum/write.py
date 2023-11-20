from __future__ import annotations

import subprocess
from typing import NamedTuple
# Usage: gum write
# Prompt for long-form text
#       --width=50               Text area width (0 for terminal width) ($GUM_WRITE_WIDTH)
#       --height=5               Text area height ($GUM_WRITE_HEIGHT)
#       --header=""              Header value ($GUM_WRITE_HEADER)
#       --placeholder="Write something..." Placeholder value ($GUM_WRITE_PLACEHOLDER)
#       --prompt="┃ "            Prompt to display ($GUM_WRITE_PROMPT)
#       --show-cursor-line       Show cursor line ($GUM_WRITE_SHOW_CURSOR_LINE)
#       --show-line-numbers      Show line numbers ($GUM_WRITE_SHOW_LINE_NUMBERS)
#       --value=""               Initial value (can be passed via stdin) ($GUM_WRITE_VALUE)
#       --char-limit=400         Maximum value length (0 for no limit)
#       --cursor.mode="blink"    Cursor mode ($GUM_WRITE_CURSOR_MODE)


class GumWriteOptions(NamedTuple):
    width: int | None = None
    height: int | None = None
    header: str | None = None
    placeholder: str | None = None
    prompt: str | None = None
    show_cursor_line: bool = False
    show_line_numbers: bool = False
    value: str | None = None
    char_limit: int | None = None
    cursor_mode: str | None = None

    def build(self) -> list[str]:
        cmd = ['gum', 'write']
        if self.width is not None:
            cmd.append(f'--width={self.width}')
        if self.height is not None:
            cmd.append(f'--height={self.height}')
        if self.header is not None:
            cmd.append(f'--header={self.header}')
        if self.placeholder is not None:
            cmd.append(f'--placeholder={self.placeholder}')
        if self.prompt is not None:
            cmd.append(f'--prompt={self.prompt}')
        if self.show_cursor_line:
            cmd.append('--show-cursor-line')
        if self.show_line_numbers:
            cmd.append('--show-line-numbers')
        if self.value is not None:
            cmd.append(f'--value={self.value}')
        if self.char_limit is not None:
            cmd.append(f'--char-limit={self.char_limit}')
        if self.cursor_mode is not None:
            cmd.append(f'--cursor.mode={self.cursor_mode}')
        return cmd


def gum_write(options: GumWriteOptions | None) -> str:
    options = options or GumWriteOptions()
    return subprocess.run(options.build(), stdout=subprocess.PIPE, encoding='utf-8').stdout


if __name__ == '__main__':
    print(gum_write(GumWriteOptions(prompt='> ')))
