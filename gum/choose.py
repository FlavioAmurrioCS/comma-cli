from __future__ import annotations

from typing import Callable
from typing import Literal
from typing import NamedTuple
from typing import overload
from typing import Sequence
from typing import TypeVar

from tool_wrapper import select_helper
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


if __name__ == '__main__':
    selected1: list[int] = gum_choose(items=list(range(10_000)), multi=True)
    selected2: int | None = gum_choose(items=list(range(10_000)), multi=False)
    selected3: int | None = gum_choose(items=list(range(10_000)))
    print(selected1)
    print(selected2)
    print(selected3)
