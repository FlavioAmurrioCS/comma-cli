# flake8: noqa: C901, S603, S607, PLW1510, PLR0912, E501, RUF019
from __future__ import annotations

import csv
import subprocess
import tempfile
from collections.abc import Sequence
from typing import Callable
from typing import Literal
from typing import overload
from typing import TypeVar
from typing import Union

from fzf import select_helper
from typing_extensions import TypeAlias
from typing_extensions import TypedDict

#######################################################################################


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


class _GumChooseOptions(TypedDict, total=False):
    ordered: bool
    height: int
    cursor: str
    header: str
    cursor_prefix: str
    selected_prefix: str
    unselected_prefix: str
    selected: str
    timeout: int
    limit: int
    no_limit: bool


def _gum_choose_options(kwargs: _GumChooseOptions) -> list[str]:
    cmd = []
    if kwargs.get("ordered"):
        cmd.append("--ordered")
    if "height" in kwargs and kwargs["height"]:
        cmd.append(f'--height={kwargs["height"]}')
    if "cursor" in kwargs and kwargs["cursor"]:
        cmd.append(f'--cursor={kwargs["cursor"]}')
    if "header" in kwargs and kwargs["header"]:
        cmd.append(f'--header={kwargs["header"]}')
    if "cursor_prefix" in kwargs and kwargs["cursor_prefix"]:
        cmd.append(f'--cursor-prefix={kwargs["cursor_prefix"]}')
    if "selected_prefix" in kwargs and kwargs["selected_prefix"]:
        cmd.append(f'--selected-prefix={kwargs["selected_prefix"]}')
    if "unselected_prefix" in kwargs and kwargs["unselected_prefix"]:
        cmd.append(f'--unselected-prefix={kwargs["unselected_prefix"]}')
    if "selected" in kwargs and kwargs["selected"]:
        cmd.append(f'--selected={kwargs["selected"]}')
    if "timeout" in kwargs:
        cmd.append(f'--timeout={kwargs["timeout"]}')
    if "limit" in kwargs and kwargs["limit"]:
        cmd.append(f'--limit={kwargs["limit"]}')
    if kwargs.get("no_limit"):
        cmd.append("--no-limit")
    return cmd


T = TypeVar("T")


@overload
def gum_choose(  # type:ignore
    items: Sequence[T],
    *,
    multi: Literal[False] = False,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    options: _GumChooseOptions | None,
) -> T | None: ...


@overload
def gum_choose(
    items: Sequence[T],
    *,
    multi: Literal[True] = True,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    options: _GumChooseOptions | None,
) -> list[T]: ...


def gum_choose(
    items: Sequence[T],
    *,
    multi: bool = False,
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
    options: _GumChooseOptions | None = None,
) -> T | None | list[T]:
    options = options or {}
    if multi:
        options["no_limit"] = True
        options.pop("limit", None)
    else:
        options["limit"] = 1
        options.pop("no_limit", None)

    return select_helper(
        cmd=["gum", "choose", *_gum_choose_options(options)],
        items=items,
        multi=multi,  # pyright: ignore[reportGeneralTypeIssues]
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


class _GumConfirmOptions(TypedDict, total=False):
    default: bool
    affirmative: str
    negative: str
    timeout: int


def _gum_confirm_options(kwargs: _GumConfirmOptions) -> list[str]:
    cmd = []
    if kwargs.get("default"):
        cmd.append("--default")
    if "affirmative" in kwargs and kwargs["affirmative"]:
        cmd.append(f'--affirmative={kwargs["affirmative"]}')
    if "negative" in kwargs and kwargs["negative"]:
        cmd.append(f'--negative={kwargs["negative"]}')
    if "timeout" in kwargs:
        cmd.append(f'--timeout={kwargs["timeout"]}')
    return cmd


def gum_confirm(
    prompt: str,
    options: _GumConfirmOptions | None = None,
) -> bool:
    options = options or {}
    return (
        subprocess.run(["gum", "confirm", *_gum_confirm_options(options), prompt]).returncode == 0
    )


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


class _GumFileOptions(TypedDict, total=False):
    cursor: str
    all: bool
    file: bool
    directory: bool
    height: int
    timeout: int


def _gum_file_options(kwargs: _GumFileOptions) -> list[str]:
    cmd = []
    if "cursor" in kwargs and kwargs["cursor"]:
        cmd.append(f'--cursor={kwargs["cursor"]}')
    if kwargs.get("all"):
        cmd.append("--all")
    if kwargs.get("file"):
        cmd.append("--file")
    if kwargs.get("directory"):
        cmd.append("--directory")
    if "height" in kwargs and kwargs["height"]:
        cmd.append(f'--height={kwargs["height"]}')
    if "timeout" in kwargs:
        cmd.append(f'--timeout={kwargs["timeout"]}')
    return cmd


def gum_file(
    path: str | None = None,
    options: _GumFileOptions | None = None,
) -> str | None:
    options = options or {}
    cmd = ["gum", "file", *_gum_file_options(options)]
    if path is not None:
        cmd.append(path)
    result = subprocess.run(
        cmd,
        encoding="utf-8",
        errors="ignore",
        capture_output=True,
    ).stdout.strip()
    return result if result else None


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


class _GumFilterOptions(TypedDict, total=False):
    indicator: str
    selected_prefix: str
    unselected_prefix: str
    header: str
    placeholder: str
    prompt: str
    width: int
    height: int
    value: str
    reverse: bool
    fuzzy: bool
    sort: bool
    timeout: int
    limit: int
    no_limit: bool
    strict: bool


def _gum_filter_options(kwargs: _GumFilterOptions) -> list[str]:
    cmd = []
    if "indicator" in kwargs and kwargs["indicator"]:
        cmd.append(f'--indicator={kwargs["indicator"]}')
    if "selected_prefix" in kwargs and kwargs["selected_prefix"]:
        cmd.append(f'--selected-prefix={kwargs["selected_prefix"]}')
    if "unselected_prefix" in kwargs and kwargs["unselected_prefix"]:
        cmd.append(f'--unselected-prefix={kwargs["unselected_prefix"]}')
    if "header" in kwargs and kwargs["header"]:
        cmd.append(f'--header={kwargs["header"]}')
    if "placeholder" in kwargs and kwargs["placeholder"]:
        cmd.append(f'--placeholder={kwargs["placeholder"]}')
    if "prompt" in kwargs and kwargs["prompt"]:
        cmd.append(f'--prompt={kwargs["prompt"]}')
    if "width" in kwargs and kwargs["width"]:
        cmd.append(f'--width={kwargs["width"]}')
    if "height" in kwargs and kwargs["height"]:
        cmd.append(f'--height={kwargs["height"]}')
    if "value" in kwargs and kwargs["value"]:
        cmd.append(f'--value={kwargs["value"]}')
    if kwargs.get("reverse"):
        cmd.append("--reverse")
    if "fuzzy" in kwargs:
        cmd.append(f'--{"no-" if not kwargs["fuzzy"] else ""}fuzzy')
    if "sort" in kwargs:
        cmd.append(f'--{"no-" if not kwargs["sort"] else ""}sort')
    if "timeout" in kwargs:
        cmd.append(f'--timeout={kwargs["timeout"]}')
    if "limit" in kwargs and kwargs["limit"]:
        cmd.append(f'--limit={kwargs["limit"]}')
    if kwargs.get("no_limit"):
        cmd.append("--no-limit")
    if "strict" in kwargs:
        cmd.append(f'--{"no-" if not kwargs["strict"] else ""}strict')
    return cmd


@overload
def gum_filter(  # type:ignore
    items: Sequence[T],
    *,
    multi: Literal[False] = False,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    options: _GumFilterOptions | None = None,
) -> T | None: ...


@overload
def gum_filter(
    items: Sequence[T],
    *,
    multi: Literal[True] = True,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    options: _GumFilterOptions | None = None,
) -> list[T]: ...


def gum_filter(
    items: Sequence[T],
    *,
    multi: bool = False,
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
    options: _GumFilterOptions | None = None,
) -> T | None | list[T]:
    """
    Selects one or more items from the given iterable using GumFilter.

    Args:
    ----
        items (Iterable[T]): The iterable to select items from.
        multi (bool, optional): Whether to allow selecting multiple items. Defaults to False.
        select_one (bool, optional): Whether to select only one item. Defaults to True.
        key (Callable[[T], str] | None, optional): A function to extract a string from each item for filtering. Defaults to None.
        options (GumFilterOptions | None, optional): Options for the GumFilter command. Defaults to None.

    Returns:
    -------
        Union[list[T], T, None]: The selected item(s), or None if no items were selected.

    """
    options = options or {}
    if multi:
        options["no_limit"] = True
        options.pop("limit", None)
    else:
        options["limit"] = 1
        options.pop("no_limit", None)
    return select_helper(
        cmd=["gum", "filter", *_gum_filter_options(options)],
        items=items,
        multi=multi,  # pyright: ignore[reportGeneralTypeIssues]
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


class _GumFormatOptions(TypedDict, total=False):
    theme: str
    language: str
    type: str


def _gum_format_options(kwargs: _GumFormatOptions) -> list[str]:
    cmd = []
    if "theme" in kwargs and kwargs["theme"]:
        cmd.append(f'--theme={kwargs["theme"]}')
    if "language" in kwargs and kwargs["language"]:
        cmd.append(f'--language={kwargs["language"]}')
    if "type" in kwargs and kwargs["type"]:
        cmd.append(f'--type={kwargs["type"]}')
    return cmd


def gum_format(template: str, options: _GumFormatOptions | None = None) -> str:
    options = options or {}
    return subprocess.run(
        ["gum", "format", *_gum_format_options(options), template],
        encoding="utf-8",
        errors="ignore",
        stdout=subprocess.PIPE,
        stderr=None,
    ).stdout.strip()


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


class _GumInputOptions(TypedDict, total=False):
    placeholder: str
    prompt: str
    cursor_mode: Literal["blink", "hide", "static"]
    value: str
    char_limit: int
    width: int
    password: bool
    header: str
    timeout: int


def _gum_input_options(kwargs: _GumInputOptions) -> list[str]:
    cmd = []
    if "placeholder" in kwargs and kwargs["placeholder"]:
        cmd.append(f'--placeholder={kwargs["placeholder"]}')
    if "prompt" in kwargs and kwargs["prompt"]:
        cmd.append(f'--prompt={kwargs["prompt"]}')
    if "cursor_mode" in kwargs and kwargs["cursor_mode"]:
        cmd.append(f'--cursor.mode={kwargs["cursor_mode"]}')
    if "value" in kwargs and kwargs["value"]:
        cmd.append(f'--value={kwargs["value"]}')
    if "char_limit" in kwargs:
        cmd.append(f'--char-limit={kwargs["char_limit"]}')
    if "width" in kwargs:
        cmd.append(f'--width={kwargs["width"]}')
    if kwargs.get("password"):
        cmd.append("--password")
    if "header" in kwargs and kwargs["header"]:
        cmd.append(f'--header={kwargs["header"]}')
    if "timeout" in kwargs:
        cmd.append(f'--timeout={kwargs["timeout"]}')
    return cmd


def gum_input(
    options: _GumInputOptions | None = None,
) -> str:
    options = options or {}
    return subprocess.run(
        ["gum", "input", *_gum_input_options(options)],
        encoding="utf-8",
        errors="ignore",
        stdout=subprocess.PIPE,
        stderr=None,
    ).stdout.strip()


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


class _GumJoinOptions(TypedDict, total=False):
    align: Literal["left", "center", "right"]
    horizontal: bool
    vertical: bool


def _gum_join_options(kwargs: _GumJoinOptions) -> list[str]:
    cmd = []
    if "align" in kwargs and kwargs["align"]:
        cmd.append(f'--align={kwargs["align"]}')
    if kwargs.get("horizontal"):
        cmd.append("--horizontal")
    if kwargs.get("vertical"):
        cmd.append("--vertical")
    return cmd


def gum_join(text: str, options: _GumJoinOptions | None = None) -> str:
    options = options or {}
    return subprocess.run(
        ["gum", "join", *_gum_join_options(options), text],
        encoding="utf-8",
        errors="ignore",
        stdout=subprocess.PIPE,
        stderr=None,
    ).stdout.strip()


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


class _GumPagerOptions(TypedDict, total=False):
    show_line_numbers: bool
    soft_wrap: bool
    timeout: int


def _gum_pager_options(kwargs: _GumPagerOptions) -> list[str]:
    cmd = []
    if kwargs.get("show_line_numbers"):
        cmd.append("--show-line-numbers")
    if kwargs.get("soft_wrap"):
        cmd.append("--soft-wrap")
    if "timeout" in kwargs:
        cmd.append(f'--timeout={kwargs["timeout"]}')
    return cmd


def gum_pager(content: str, options: _GumPagerOptions | None = None) -> None:
    options = options or {}
    subprocess.run(
        [
            "gum",
            "pager",
            *_gum_pager_options(options),
            content,
        ],
        encoding="utf-8",
        errors="ignore",
    )


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


class _GumSpinOptions(TypedDict, total=False):
    show_output: bool
    spinner: str
    title: str
    align: Literal["left", "center", "right"]
    timeout: int


def _gum_spin_options(kwargs: _GumSpinOptions) -> list[str]:
    cmd = []
    if kwargs.get("show_output"):
        cmd.append("--show-output")
    if "spinner" in kwargs and kwargs["spinner"]:
        cmd.append(f'--spinner={kwargs["spinner"]}')
    if "title" in kwargs and kwargs["title"]:
        cmd.append(f'--title={kwargs["title"]}')
    if "align" in kwargs and kwargs["align"]:
        cmd.append(f'--align={kwargs["align"]}')
    if "timeout" in kwargs:
        cmd.append(f'--timeout={kwargs["timeout"]}')
    return cmd


def gum_spin(
    command: Sequence[str],
    options: _GumSpinOptions | None = None,
) -> str:
    options = options or {}
    return subprocess.run(
        ["gum", "spin", *_gum_spin_options(options), "--", *command],
        encoding="utf-8",
        errors="ignore",
        stdout=subprocess.PIPE,
        stderr=None,
    ).stdout.strip()


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


class _GumStyleOptions(TypedDict, total=False):
    background: str
    foreground: str
    border: Literal[
        "none",
        "single",
        "double",
        "round",
        "bold",
        "single_double",
        "double_single",
        "bold_round",
        "bold_double",
        "double_round",
        "bold_single_double",
        "bold_double_single",
    ]
    border_background: str
    border_foreground: str
    align: Literal["left", "center", "right"]
    height: int
    width: int
    margin: str
    padding: str
    bold: bool
    faint: bool
    italic: bool
    strikethrough: bool
    underline: bool


def _gum_style_options(kwargs: _GumStyleOptions) -> list[str]:
    cmd = []
    if "background" in kwargs and kwargs["background"]:
        cmd.append(f'--background={kwargs["background"]}')
    if "foreground" in kwargs and kwargs["foreground"]:
        cmd.append(f'--foreground={kwargs["foreground"]}')
    if "border" in kwargs and kwargs["border"]:
        cmd.append(f'--border={kwargs["border"]}')
    if "border_background" in kwargs and kwargs["border_background"]:
        cmd.append(f'--border-background={kwargs["border_background"]}')
    if "border_foreground" in kwargs and kwargs["border_foreground"]:
        cmd.append(f'--border-foreground={kwargs["border_foreground"]}')
    if "align" in kwargs and kwargs["align"]:
        cmd.append(f'--align={kwargs["align"]}')
    if "height" in kwargs and kwargs["height"]:
        cmd.append(f'--height={kwargs["height"]}')
    if "width" in kwargs and kwargs["width"]:
        cmd.append(f'--width={kwargs["width"]}')
    if "margin" in kwargs and kwargs["margin"]:
        cmd.append(f'--margin={kwargs["margin"]}')
    if "padding" in kwargs and kwargs["padding"]:
        cmd.append(f'--padding={kwargs["padding"]}')
    if kwargs.get("bold"):
        cmd.append("--bold")
    if kwargs.get("faint"):
        cmd.append("--faint")
    if kwargs.get("italic"):
        cmd.append("--italic")
    if kwargs.get("strikethrough"):
        cmd.append("--strikethrough")
    if kwargs.get("underline"):
        cmd.append("--underline")
    return cmd


def gum_style(
    text: str,
    options: _GumStyleOptions | None = None,
) -> str:
    options = options or {}
    return subprocess.run(
        ["gum", "style", *_gum_style_options(options), text],
        encoding="utf-8",
        errors="ignore",
        stdout=subprocess.PIPE,
        stderr=None,
    ).stdout.strip()


####################################################################################################

# Usage: gum table

# Render a table of data

# Flags:
#   -h, --help                   Show context-sensitive help.
#   -v, --version                Print the version number

#   -s, --separator=","          Row separator
#   -c, --columns=COLUMNS,...    Column names
#   -w, --widths=WIDTHS,...      Column widths
#       --height=10              Table height
#   -f, --file=""                file path


class _GumTableOptions(TypedDict, total=False):
    separator: str
    columns: list[str]
    widths: list[int]
    height: int
    # file: str


def _gum_table_options(kwargs: _GumTableOptions) -> list[str]:
    cmd = []
    if "separator" in kwargs and kwargs["separator"]:
        cmd.append(f'--separator={kwargs["separator"]}')
    if "columns" in kwargs and kwargs["columns"]:
        cmd.append(f'--columns={",".join(kwargs["columns"])}')
    if "widths" in kwargs and kwargs["widths"]:
        cmd.append(f'--widths={",".join(map(str, kwargs["widths"]))}')
    if "height" in kwargs and kwargs["height"]:
        cmd.append(f'--height={kwargs["height"]}')
    # if 'file' in kwargs and kwargs['file']:
    #     cmd.append(f'--file={kwargs["file"]}')
    return cmd


_CSV_CELL: TypeAlias = Union[str, int, float, bool]
_CSV_DATA: TypeAlias = Union[Sequence[dict[str, _CSV_CELL]], str]


def gum_table(
    data_or_file: _CSV_DATA,
    options: _GumTableOptions | None = None,
) -> str | None:
    if not data_or_file:
        return None
    options = options or {}
    cmd = ["gum", "table", *_gum_table_options(options)]

    with tempfile.NamedTemporaryFile(mode="w") as f:
        filename = data_or_file if isinstance(data_or_file, str) else f.name
        if not isinstance(data_or_file, str):
            dict_writer = csv.DictWriter(f, fieldnames=data_or_file[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(data_or_file)
        cmd.append(f"--file={filename}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=None,
            encoding="utf-8",
        ).stdout.strip()
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


class _GumWriteOptions(TypedDict, total=False):
    width: int
    height: int
    header: str
    placeholder: str
    prompt: str
    show_cursor_line: bool
    show_line_numbers: bool
    value: str
    char_limit: int
    cursor_mode: Literal["blink", "hide", "static"]


def _gum_write_options(kwargs: _GumWriteOptions) -> list[str]:
    cmd = []
    if "width" in kwargs:
        cmd.append(f'--width={kwargs["width"]}')
    if "height" in kwargs:
        cmd.append(f'--height={kwargs["height"]}')
    if "header" in kwargs and kwargs["header"]:
        cmd.append(f'--header={kwargs["header"]}')
    if "placeholder" in kwargs:
        cmd.append(f'--placeholder={kwargs["placeholder"]}')
    if "prompt" in kwargs and kwargs["prompt"]:
        cmd.append(f'--prompt={kwargs["prompt"]}')
    if kwargs.get("show_cursor_line"):
        cmd.append("--show-cursor-line")
    if kwargs.get("show_line_numbers"):
        cmd.append("--show-line-numbers")
    if "value" in kwargs and kwargs["value"]:
        cmd.append(f'--value={kwargs["value"]}')
    if "char_limit" in kwargs:
        cmd.append(f'--char-limit={kwargs["char_limit"]}')
    if "cursor_mode" in kwargs and kwargs["cursor_mode"]:
        cmd.append(f'--cursor.mode={kwargs["cursor_mode"]}')
    return cmd


def gum_write(options: _GumWriteOptions | None = None) -> str:
    options = options or {}
    return subprocess.run(
        ["gum", "write", *_gum_write_options(options)],
        stdout=subprocess.PIPE,
        encoding="utf-8",
    ).stdout


####################################################################################################
if __name__ == "__main__":
    gum_spin(["sleep", "5"], {"title": "Sleeping for 5 seconds...", "show_output": True})
