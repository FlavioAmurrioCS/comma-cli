from __future__ import annotations

from typing import Callable
from typing import Literal
from typing import NamedTuple
from typing import overload
from typing import Sequence
from typing import TypeVar

from tool_wrapper import select_helper
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


T = TypeVar('T')


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


if __name__ == '__main__':
    b1: list[int] = gum_filter(items=list(range(10_000)), multi=True)
    b2: int | None = gum_filter(items=list(range(10_000)), multi=False)
    b3: int | None = gum_filter(items=list(range(10_000)))
