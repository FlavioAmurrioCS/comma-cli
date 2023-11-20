from __future__ import annotations

import csv
import subprocess
import tempfile
from typing import Any
from typing import Callable
from typing import Literal
from typing import NamedTuple
from typing import overload
from typing import Sequence
from typing import TYPE_CHECKING
from typing import TypeAlias
from typing import TypeVar

from tool_wrapper import select_helper

if TYPE_CHECKING:
    from subprocess import _CMD

# gum version v0.11.0 (f5b09a4)
# $ gum --help
# Usage: gum <command>
# A tool for glamorous shell scripts.
# Flags:
#   -h, --help       Show context-sensitive help.
#   -v, --version    Print the version number
# Commands:
#   choose     Choose an option from a list of choices
#   confirm    Ask a user to confirm an action
#   file       Pick a file from a folder
#   filter     Filter items from a list
#   format     Format a string using a template
#   input      Prompt for some input
#   join       Join text vertically or horizontally
#   pager      Scroll through a file
#   spin       Display spinner while running a command
#   style      Apply coloring, borders, spacing to text
#   table      Render a table of data
#   write      Prompt for long-form text
# Run "gum <command> --help" for more information on a command.
####################################################################################################
# Usage: gum choose [<options> ...]
# Choose an option from a list of choices
# Arguments:
#   [<options> ...]    Options to choose from.
# Flags:
#   -h, --help                        Show context-sensitive help.
#   -v, --version                     Print the version number
#       --ordered                     Maintain the order of the selected options ($GUM_CHOOSE_ORDERED)
#       --height=10                   Height of the list ($GUM_CHOOSE_HEIGHT)
#       --cursor="> "                 Prefix to show on item that corresponds to the cursor position
#                                     ($GUM_CHOOSE_CURSOR)
#       --header=""                   Header value ($GUM_CHOOSE_HEADER)
#       --cursor-prefix="○ "          Prefix to show on the cursor item (hidden if limit is 1)
#                                     ($GUM_CHOOSE_CURSOR_PREFIX)
#       --selected-prefix="◉ "        Prefix to show on selected items (hidden if limit is 1)
#                                     ($GUM_CHOOSE_SELECTED_PREFIX)
#       --unselected-prefix="○ "      Prefix to show on unselected items (hidden if limit is 1)
#                                     ($GUM_CHOOSE_UNSELECTED_PREFIX)
#       --selected=,...               Options that should start as selected ($GUM_CHOOSE_SELECTED)
#       --timeout=0                   Timeout until choose returns selected element ($GUM_CCHOOSE_TIMEOUT)
# Selection
#   --limit=1     Maximum number of options to pick
#   --no-limit    Pick unlimited number of options (ignores limit)


class GumChooseOptions(NamedTuple):
    ordered: bool = False
    height: int | None = None
    cursor: str | None = None
    header: str | None = None
    cursor_prefix: str | None = None
    selected_prefix: str | None = None
    unselected_prefix: str | None = None
    selected: str | None = None
    timeout: int | None = None
    limit: int | None = None
    no_limit: bool = False

    def build(self) -> list[str]:
        cmd = ['gum', 'choose']
        if self.ordered:
            cmd.append('--ordered')
        if self.height is not None:
            cmd.append(f'--height={self.height}')
        if self.cursor is not None:
            cmd.append(f'--cursor={self.cursor}')
        if self.header is not None:
            cmd.append(f'--header={self.header}')
        if self.cursor_prefix is not None:
            cmd.append(f'--cursor-prefix={self.cursor_prefix}')
        if self.selected_prefix is not None:
            cmd.append(f'--selected-prefix={self.selected_prefix}')
        if self.unselected_prefix is not None:
            cmd.append(f'--unselected-prefix={self.unselected_prefix}')
        if self.selected is not None:
            cmd.append(f'--selected={self.selected}')
        if self.timeout is not None:
            cmd.append(f'--timeout={self.timeout}')
        if self.limit is not None:
            cmd.append(f'--limit={self.limit}')
        if self.no_limit:
            cmd.append('--no-limit')
        return cmd


T = TypeVar('T')


@overload
def gum_choose(  # type:ignore
    items: Sequence[T],
    *,
    multi: Literal[False] = False,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    options: GumChooseOptions | None = ...,
) -> T | None:
    ...


@overload
def gum_choose(
    items: Sequence[T],
    *,
    multi: Literal[True] = True,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    options: GumChooseOptions | None = ...,
) -> list[T]:
    ...


def gum_choose(
    items: Sequence[T],
    *,
    multi: bool = False,
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
    options: GumChooseOptions | None = None,
) -> T | None | list[T]:
    options = options or GumChooseOptions()
    if multi:
        options = options._replace(limit=None, no_limit=True)
    else:
        options = options._replace(limit=1, no_limit=False)

    return select_helper(
        cmd=options.build(),
        items=items,
        multi=multi,  # type:ignore
        select_one=select_one,
        key=key,
    )


####################################################################################################

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


####################################################################################################
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


####################################################################################################

# Usage: gum filter
# Filter items from a list
# Flags:
#   -h, --help                       Show context-sensitive help.
#   -v, --version                    Print the version number
#       --indicator="•"              Character for selection
#                                    ($GUM_FILTER_INDICATOR)
#       --selected-prefix=" ◉ "      Character to indicate selected items (hidden
#                                    if limit is 1) ($GUM_FILTER_SELECTED_PREFIX)
#       --unselected-prefix=" ○ "
#                                    Character to indicate unselected
#                                    items (hidden if limit is 1)
#                                    ($GUM_FILTER_UNSELECTED_PREFIX)
#       --header=""                  Header value ($GUM_FILTER_HEADER)
#       --placeholder="Filter..."    Placeholder value ($GUM_FILTER_PLACEHOLDER)
#       --prompt="> "                Prompt to display ($GUM_FILTER_PROMPT)
#       --width=20                   Input width ($GUM_FILTER_WIDTH)
#       --height=0                   Input height ($GUM_FILTER_HEIGHT)
#       --value=""                   Initial filter value ($GUM_FILTER_VALUE)
#       --reverse                    Display from the bottom of the screen
#                                    ($GUM_FILTER_REVERSE)
#       --[no-]fuzzy                 Enable fuzzy matching ($GUM_FILTER_FUZZY)
#       --[no-]sort                  Sort the results ($GUM_FILTER_SORT)
#       --timeout=0                  Timeout until filter command aborts
#                                    ($GUM_FILTER_TIMEOUT)
# Selection
#   --limit=1        Maximum number of options to pick
#   --no-limit       Pick unlimited number of options (ignores limit)
#   --[no-]strict    Only returns if anything matched. Otherwise return Filter


class GumFilterOptions(NamedTuple):
    executable: str = 'gum'
    indicator: str | None = None
    selected_prefix: str | None = None
    unselected_prefix: str | None = None
    header: str | None = None
    placeholder: str | None = None
    prompt: str | None = None
    width: int | None = None
    height: int | None = None
    value: str | None = None
    reverse: bool = False
    fuzzy: bool | None = None
    sort: bool | None = None
    timeout: int | None = None
    limit: int | None = None
    no_limit: bool = False
    strict: bool | None = None

    def build(self) -> list[str]:
        cmd = [self.executable, 'filter']
        if self.indicator is not None:
            cmd.append(f'--indicator={self.indicator}')
        if self.selected_prefix is not None:
            cmd.append(f'--selected-prefix={self.selected_prefix}')
        if self.unselected_prefix is not None:
            cmd.append(f'--unselected-prefix={self.unselected_prefix}')
        if self.header is not None:
            cmd.append(f'--header={self.header}')
        if self.placeholder is not None:
            cmd.append(f'--placeholder={self.placeholder}')
        if self.prompt is not None:
            cmd.append(f'--prompt={self.prompt}')
        if self.width is not None:
            cmd.append(f'--width={self.width}')
        if self.height is not None:
            cmd.append(f'--height={self.height}')
        if self.value is not None:
            cmd.append(f'--value={self.value}')
        if self.reverse:
            cmd.append('--reverse')
        if self.fuzzy is not None:
            cmd.append(f'--{"no-" if not self.fuzzy else ""}fuzzy')
        if self.sort is not None:
            cmd.append(f'--{"no-" if not self.sort else ""}sort')
        if self.timeout is not None:
            cmd.append(f'--timeout={self.timeout}')
        if self.limit is not None:
            cmd.append(f'--limit={self.limit}')
        if self.no_limit:
            cmd.append('--no-limit')
        if self.strict is not None:
            cmd.append(f'--{"no-" if not self.strict else ""}strict')
        return cmd


@overload
def gum_filter(  # type:ignore
    items: Sequence[T],
    *,
    multi: Literal[False] = False,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    options: GumFilterOptions | None = ...,
) -> T | None:
    ...


@overload
def gum_filter(
    items: Sequence[T],
    *,
    multi: Literal[True] = True,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    options: GumFilterOptions | None = ...,
) -> list[T]:
    ...


def gum_filter(
    items: Sequence[T],
    *,
    multi: bool = False,
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
    options: GumFilterOptions | None = None,
) -> T | None | list[T]:
    """
    Selects one or more items from the given iterable using GumFilter.

    Args:
        items (Iterable[T]): The iterable to select items from.
        multi (bool, optional): Whether to allow selecting multiple items. Defaults to False.
        select_one (bool, optional): Whether to select only one item. Defaults to True.
        key (Callable[[T], str] | None, optional): A function to extract a string from each item for filtering. Defaults to None.
        options (GumFilterOptions | None, optional): Options for the GumFilter command. Defaults to None.

    Returns:
        Union[list[T], T, None]: The selected item(s), or None if no items were selected.
    """
    options = options or GumFilterOptions()
    if multi:
        options = options._replace(limit=None, no_limit=True)
    else:
        options = options._replace(limit=1, no_limit=False)
    return select_helper(
        cmd=options.build(),
        items=items,
        multi=multi,  # type:ignore
        select_one=select_one,
        key=key,
    )
####################################################################################################
# Usage: gum format [<template> ...]
# Format a string using a template
# Arguments:
#   [<template> ...]    Template string to format (can also be provided via stdin)
# Flags:
#   -h, --help               Show context-sensitive help.
#   -v, --version            Print the version number
#       --theme="pink"       Glamour theme to use for markdown formatting
#                            ($GUM_FORMAT_THEME)
#   -l, --language=""        Programming language to parse code
#                            ($GUM_FORMAT_LANGUAGE)
#   -t, --type="markdown"    Format to use (markdown,template,code,emoji)
#                            ($GUM_FORMAT_TYPE)


def gum_format(template: str, theme: str | None = None, language: str | None = None, type: str | None = None) -> str:
    cmd = ['gum', 'format']
    if theme is not None:
        cmd.append(f'--theme={theme}')
    if language is not None:
        cmd.append(f'--language={language}')
    if type is not None:
        cmd.append(f'--type={type}')
    cmd.append(template)
    return subprocess.run(cmd, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=None).stdout.strip()

####################################################################################################
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


####################################################################################################
# Usage: gum join <text> ...
# Join text vertically or horizontally
# Arguments:
#   <text> ...    Text to join.
# Flags:
#   -h, --help            Show context-sensitive help.
#   -v, --version         Print the version number
#       --align="left"    Text alignment
#       --horizontal      Join (potentially multi-line) strings horizontally
#       --vertical        Join (potentially multi-line) strings vertically

def gum_join(text: str, align: Literal['left', 'center', 'right'] | None = None, horizontal: bool = False, vertical: bool = False) -> str:
    cmd = ['gum', 'join']
    if align is not None:
        cmd.append(f'--align={align}')
    if horizontal:
        cmd.append('--horizontal')
    if vertical:
        cmd.append('--vertical')
    cmd.append(text)
    return subprocess.run(cmd, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=None).stdout.strip()

####################################################################################################
# Usage: gum pager [<content>]
# Scroll through a file
# Arguments:
#   [<content>]    Display content to scroll
# Flags:
#   -h, --help                 Show context-sensitive help.
#   -v, --version              Print the version number
#       --show-line-numbers    Show line numbers
#       --soft-wrap            Soft wrap lines
#       --timeout=0            Timeout until command exits ($GUM_PAGER_TIMEOUT)


def gum_pager(content: str, show_line_numbers: bool = False, soft_wrap: bool = False, timeout: int | None = None) -> None:
    cmd = ['gum', 'pager']
    if show_line_numbers:
        cmd.append('--show-line-numbers')
    if soft_wrap:
        cmd.append('--soft-wrap')
    if timeout is not None:
        cmd.append(f'--timeout={timeout}')
    cmd.append(content)
    subprocess.run(cmd, encoding='utf-8', errors='ignore')

####################################################################################################
# Usage: gum spin <command> ...
# Display spinner while running a command
# Arguments:
#   <command> ...    Command to run
# Flags:
#   -h, --help                  Show context-sensitive help.
#   -v, --version               Print the version number
#       --show-output           Show or pipe output of command during execution
#                               ($GUM_SPIN_SHOW_OUTPUT)
#   -s, --spinner="dot"         Spinner type ($GUM_SPIN_SPINNER)
#       --title="Loading..."    Text to display to user while spinning
#                               ($GUM_SPIN_TITLE)
#   -a, --align="left"          Alignment of spinner with regard to the title
#                               ($GUM_SPIN_ALIGN)
#       --timeout=0             Timeout until spin command aborts
#                               ($GUM_SPIN_TIMEOUT)


def gum_spin(
    command: Sequence[str],
    show_output: bool = False,
    spinner: str | None = None,
    title: str | None = None,
    align: Literal['left', 'center', 'right'] | None = None,
    timeout: int | None = None
) -> str:
    cmd: list[Any] = ['gum', 'spin']
    if show_output:
        cmd.append('--show-output')
    if spinner is not None:
        cmd.append(f'--spinner={spinner}')
    if title is not None:
        cmd.append(f'--title={title}')
    if align is not None:
        cmd.append(f'--align={align}')
    if timeout is not None:
        cmd.append(f'--timeout={timeout}')
    cmd.extend(command)
    return subprocess.run(cmd, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=None).stdout.strip()

####################################################################################################
# Usage: gum style [<text> ...]
# Apply coloring, borders, spacing to text
# Arguments:
#   [<text> ...]    Text to which to apply the style
# Flags:
#   -h, --help       Show context-sensitive help.
#   -v, --version    Print the version number
# Style Flags
#   --background=""           Background Color ($BACKGROUND)
#   --foreground=""           Foreground Color ($FOREGROUND)
#   --border="none"           Border Style ($BORDER)
#   --border-background=""    Border Background Color ($BORDER_BACKGROUND)
#   --border-foreground=""    Border Foreground Color ($BORDER_FOREGROUND)
#   --align="left"            Text Alignment ($ALIGN)
#   --height=0                Text height ($HEIGHT)
#   --width=0                 Text width ($WIDTH)
#   --margin="0 0"            Text margin ($MARGIN)
#   --padding="0 0"           Text padding ($PADDING)
#   --bold                    Bold text ($BOLD)
#   --faint                   Faint text ($FAINT)
#   --italic                  Italicize text ($ITALIC)
#   --strikethrough           Strikethrough text ($STRIKETHROUGH)
#   --underline               Underline text ($UNDERLINE)


def gum_style(
    text: str,
    background: str | None = None,
    foreground: str | None = None,
    border: Literal['none', 'single', 'double', 'round', 'bold', 'single-double', 'double-single', 'round-single', 'single-round', 'double-round', 'round-double'] | None = None,
    border_background: str | None = None,
    border_foreground: str | None = None,
    align: Literal['left', 'center', 'right'] | None = None,
    height: int | None = None,
    width: int | None = None,
    margin: str | None = None,
    padding: str | None = None,
    bold: bool = False,
    faint: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
) -> str:
    cmd = ['gum', 'style']
    if background is not None:
        cmd.append(f'--background={background}')
    if foreground is not None:
        cmd.append(f'--foreground={foreground}')
    if border is not None:
        cmd.append(f'--border={border}')
    if border_background is not None:
        cmd.append(f'--border-background={border_background}')
    if border_foreground is not None:
        cmd.append(f'--border-foreground={border_foreground}')
    if align is not None:
        cmd.append(f'--align={align}')
    if height is not None:
        cmd.append(f'--height={height}')
    if width is not None:
        cmd.append(f'--width={width}')
    if margin is not None:
        cmd.append(f'--margin={margin}')
    if padding is not None:
        cmd.append(f'--padding={padding}')
    if bold:
        cmd.append('--bold')
    if faint:
        cmd.append('--faint')
    if italic:
        cmd.append('--italic')
    if strikethrough:
        cmd.append('--strikethrough')
    if underline:
        cmd.append('--underline')
    cmd.append(text)
    return subprocess.run(cmd, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=None).stdout.strip()


####################################################################################################

_CSV_CELL: TypeAlias = str | int | float | bool
_CSV_DATA: TypeAlias = Sequence[dict[str, _CSV_CELL]] | str


def gum_table(
    data_or_file: _CSV_DATA,
    separator: str | None = None,
    columns: list[str] = [],
    widths: list[int] = [],
    height: int | None = None,
) -> str | None:
    if not data_or_file:
        return None
    cmd = ['gum', 'table']
    if separator:
        cmd.append(f'--separator={separator}')
    if columns:
        cmd.append(f"--columns={','.join(columns)}")
    if widths:
        cmd.append(f"--widths={','.join(map(str, widths))}")
    if height:
        cmd.append(f'--height={height}')
    with tempfile.NamedTemporaryFile(mode='w') as f:
        filename = data_or_file if isinstance(data_or_file, str) else f.name
        if not isinstance(data_or_file, str):
            dict_writer = csv.DictWriter(f, fieldnames=data_or_file[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(data_or_file)
        cmd.append(f'--file={filename}')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, encoding='utf-8').stdout.strip()
        return result if result else None


####################################################################################################
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


####################################################################################################
if __name__ == '__main__':
    selected1: list[int] = gum_choose(items=list(range(10_000)), multi=True)
    selected2: int | None = gum_choose(items=list(range(10_000)), multi=False)
    selected3: int | None = gum_choose(items=list(range(10_000)))
    print(selected1)
    print(selected2)
    print(selected3)
    b1: list[int] = gum_filter(items=list(range(10_000)), multi=True)
    b2: int | None = gum_filter(items=list(range(10_000)), multi=False)
    b3: int | None = gum_filter(items=list(range(10_000)))

    print(f"User typed: '{gum_input()}'")

    r = gum_table(data_or_file='/Users/flavio/Downloads/international-trade-june-2023-quarter/revised.csv')
    print(f'{r=}')

    print(gum_write(GumWriteOptions(prompt='> ')))
