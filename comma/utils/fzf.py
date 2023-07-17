# #!/usr/bin/env python3
from __future__ import annotations

import errno
import itertools
import shutil
import subprocess
import sys
import typing
from typing import Callable
from typing import Iterable
from typing import NamedTuple
from typing import overload
from typing import TYPE_CHECKING
from typing import TypeVar


if TYPE_CHECKING:
    from typing import Literal

T = TypeVar('T')


class FzfOptions(NamedTuple):
    fzf_executable: str | None = None
    #   Search
    #     -x, --extended        Extended-search mode
    #                           (enabled by default; +x or --no-extended to disable)
    extended: bool = True

    #     -e, --exact           Enable Exact-match
    exact: bool = False

    #     --algo=TYPE           Fuzzy matching algorithm: [v1|v2] (default: v2)
    algo: Literal['v1', 'v2'] | None = None

    #     -i                    Case-insensitive match (default: smart-case match)
    #     +i                    Case-sensitive match
    case: Literal['case-insensitive', 'case-sensitive', 'smart-case'] | None = None

    #     --literal             Do not normalize latin script letters before matching
    literal: bool = False

    #     -n, --nth=N[,..]      Comma-separated list of field index expressions
    #                           for limiting search scope. Each can be a non-zero
    #                           integer or a range expression ([BEGIN]..[END]).
    #     --with-nth=N[,..]     Transform the presentation of each line using
    #                           field index expressions

    #     -d, --delimiter=STR   Field delimiter regex (default: AWK-style)
    delimiter: str | None = None

    #     +s, --no-sort         Do not sort the result
    no_sort: bool = False

    #     --tac                 Reverse the order of the input
    tac: bool = False

    #     --disabled            Do not perform search
    disabled: bool = False

    #     --tiebreak=CRI[,..]   Comma-separated list of sort criteria to apply
    #                           when the scores are tied [length|begin|end|index]
    #                           (default: length)
    tiebreak: tuple[Literal['length', 'begin', 'end', 'index'], ...] | None = None

    #   Interface
    #     -m, --multi[=MAX]     Enable multi-select with tab/shift-tab
    # multi: Literal[True, False] = False

    #     --no-mouse            Disable mouse
    no_mouse: bool = False

    #     --bind=KEYBINDS       Custom key bindings. Refer to the man page.
    bind: str = 'ctrl-a:select-all,ctrl-d:deselect-all,ctrl-t:toggle-all'

    #     --cycle               Enable cyclic scroll
    cycle: bool = False

    #     --keep-right          Keep the right end of the line visible on overflow
    keep_right: bool = False

    #     --scroll-off=LINES    Number of screen lines to keep above or below when
    #                           scrolling to the top or to the bottom (default: 0)
    scroll_off: int | None = None

    #     --no-hscroll          Disable horizontal scroll
    no_hscroll: bool = False

    #     --hscroll-off=COLS    Number of screen columns to keep to the right of the
    #                           highlighted substring (default: 10)
    hscroll_off: int | None = None

    #     --filepath-word       Make word-wise movements respect path separators
    filepath_word: bool = False

    #     --jump-labels=CHARS   Label characters for jump and jump-accept
    jump_labels: str | None = None

    #   Layout
    #     --height=HEIGHT[%]    Display fzf window below the cursor with the given
    #                           height instead of using fullscreen
    #     --min-height=HEIGHT   Minimum height when --height is given in percent
    #                           (default: 10)
    #     --layout=LAYOUT       Choose layout: [default|reverse|reverse-list]
    #     --border[=STYLE]      Draw border around the finder
    #                           [rounded|sharp|horizontal|vertical|
    #                            top|bottom|left|right|none] (default: rounded)
    #     --margin=MARGIN       Screen margin (TRBL | TB,RL | T,RL,B | T,R,B,L)
    #     --padding=PADDING     Padding inside border (TRBL | TB,RL | T,RL,B | T,R,B,L)
    #     --info=STYLE          Finder info style [default|inline|hidden]

    #     --prompt=STR          Input prompt (default: '> ')
    prompt: str | None = None

    #     --pointer=STR         Pointer to the current line (default: '>')
    pointer: str | None = None

    #     --marker=STR          Multi-select marker (default: '>')
    marker: str | None = None

    #     --header=STR          String to print as header
    header: str | None = None

    #     --header-lines=N      The first N lines of the input are treated as header
    header_lines: int | None = None

    #     --header-first        Print header before the prompt line
    head_first: bool = True

    #     --ellipsis=STR        Ellipsis to show when line is truncated (default: '..')
    ellipsis: str | None = None

    #   Display
    #     --ansi                Enable processing of ANSI color codes
    #     --tabstop=SPACES      Number of spaces for a tab character (default: 8)
    #     --color=COLSPEC       Base scheme (dark|light|16|bw) and/or custom colors
    #     --no-bold             Do not use bold text

    #   History
    #     --history=FILE        History file
    history: str | None = None

    #     --history-size=N      Maximum number of history entries (default: 1000)
    history_size: int | None = None

    #   Preview
    #     --preview=COMMAND     Command to preview highlighted line ({})
    preview: str | None = None

    #     --preview-window=OPT  Preview window layout (default: right:50%)
    #                           [up|down|left|right][,SIZE[%]]
    #                           [,[no]wrap][,[no]cycle][,[no]follow][,[no]hidden]
    #                           [,border-BORDER_OPT]
    #                           [,+SCROLL[OFFSETS][/DENOM]][,~HEADER_LINES]
    #                           [,default]
    preview_window: str | None = None

    #   Scripting

    #     -q, --query=STR       Start the finder with the given query
    query: str | None = None

    #     -1, --select-1        Automatically select the only match
    # select_one: bool = False

    #     -0, --exit-0          Exit immediately when there's no match
    exit_zero: bool = True

    #     -f, --filter=STR      Filter mode. Do not start interactive finder.
    # filter: Optional[str] = None

    #     --print-query         Print query as the first line
    #     --expect=KEYS         Comma-separated list of keys to complete fzf
    #     --read0               Read input delimited by ASCII NUL characters
    #     --print0              Print output delimited by ASCII NUL characters
    #     --sync                Synchronous search for multi-staged filtering
    #     --version             Display version information and exit

    #   Environment variables
    #     FZF_DEFAULT_COMMAND   Default command to use when input is tty
    #     FZF_DEFAULT_OPTS      Default options
    #                           (e.g. '--layout=reverse --inline-info')
    def command(self, *, multi: bool, select_one: bool, fzf_executable: str | None) -> tuple[str, ...]:
        executable = fzf_executable or self.fzf_executable or shutil.which('fzf')
        if executable is None:
            print('No fzf executable found in PATH', file=sys.stderr)
            raise SystemExit(1)

        cmd = [executable]
        # Search
        cmd.append('--extended' if self.extended else '--no-extended')
        if self.exact:
            cmd.append('--exact')
        if self.algo is not None:
            cmd.append(f'--algo={self.algo}')
        if self.case is not None:
            if self.case == 'case-insensitive':
                cmd.append('-i')
            elif self.case == 'case-sensitive':
                cmd.append('+i')
        if self.literal:
            cmd.append('--literal')
        if self.delimiter is not None:
            cmd.append(f'--delimiter={self.delimiter}')
        if self.no_sort:
            cmd.append('--no-sort')
        if self.tac:
            cmd.append('--tac')
        if self.disabled:
            cmd.append('--disable')
        if self.tiebreak:
            cmd.append(f'--tiebreak={",".join(self.tiebreak)}')

        header = self.header
        # Interface
        if multi:
            cmd.append('--multi')
            header = f'{header or ""}(MULTI SELECTED)({self.bind})'

        if self.no_mouse:
            cmd.append('--no-mouse')
        cmd.append(f'--bind={self.bind}')
        if self.cycle:
            cmd.append('--cycle')
        if self.keep_right:
            cmd.append('--keep_right')
        if self.scroll_off is not None:
            cmd.append(f'--scroll-off={self.scroll_off}')
        if self.no_hscroll:
            cmd.append('--no-hscroll')
        if self.hscroll_off is not None:
            cmd.append(f'--keep_right={self.hscroll_off}')
        if self.filepath_word:
            cmd.append('--filepath-word')
        if self.jump_labels is not None:
            cmd.append(f'--jump-labels={self.jump_labels}')

        # Layout
        if self.prompt is not None:
            cmd.append(f'--prompt={self.prompt}')
        if self.pointer is not None:
            cmd.append(f'--pointer={self.pointer}')
        if self.marker is not None:
            cmd.append(f'--marker={self.marker}')
        if header is not None:
            cmd.append(f'--header={header}')
        if self.header_lines is not None:
            cmd.append(f'--header-lines={self.header_lines}')
        if self.head_first:
            cmd.append('--header-first')
        if self.ellipsis is not None:
            cmd.append(f'--ellipsis={self.header_lines}')

        # History
        if self.history is not None:
            cmd.append(f'--history={self.history}')
        if self.history_size is not None:
            cmd.append(f'--history-size={self.history_size}')

        # Preview
        if self.preview is not None:
            cmd.append(f'--preview={self.preview}')
        if self.preview_window is not None:
            cmd.append(f'--preview-window={self.preview_window}')

        # Scripting
        if self.query is not None:
            cmd.append(f'--query={self.query}')
        if select_one:
            cmd.append('--select-1')
        if self.exit_zero:
            cmd.append('--exit-0')
        # if filter is not None: cmd.append(f'--filter={filter}')
        return tuple(cmd)


@overload
def fzf(  # type:ignore
    iterable: Iterable[T],
    *,
    multi: Literal[False] = False,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    fzf_executable: str | None = ...,
    options: FzfOptions | None = ...,
) -> T | None:
    ...


@overload
def fzf(
    iterable: Iterable[T],
    *,
    multi: Literal[True] = True,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    fzf_executable: str | None = ...,
    options: FzfOptions | None = ...,
) -> list[T]:
    ...


def fzf(
    iterable: Iterable[T],
    *,
    multi: bool = False,
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
    fzf_executable: str | None = None,
    options: FzfOptions | None = None,
) -> T | None | list[T]:

    options = options or FzfOptions()
    cmd = options.command(multi=multi, select_one=select_one, fzf_executable=fzf_executable)

    empty_return: None | list[T] = [] if multi else None
    sentinel = object()
    iterator = iter(iterable)
    _first_item = next(iterator, sentinel)
    if _first_item == sentinel:
        return empty_return
    first_item: T = typing.cast(T, _first_item)

    full_stream: Iterable[T]
    if select_one:
        _second_item = next(iterator, sentinel)
        if _second_item == sentinel:
            return [first_item] if multi else first_item
        second_item: T = typing.cast(T, _second_item)
        full_stream = itertools.chain((first_item, second_item), iterator)
    else:
        full_stream = itertools.chain((first_item,), iterator)

    dct: dict[str, T] = {}

    def __inner__(t: T, func: Callable[[T], str]) -> str:
        _key = func(t)
        dct[_key] = t
        return _key

    _iterable: Iterable[str]
    if key is not None:
        _iterable = (__inner__(x, key) for x in full_stream)
    elif not isinstance(first_item, str):
        _iterable = (__inner__(x, str) for x in full_stream)
    else:
        _iterable = typing.cast(Iterable[str], full_stream)

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None,
        encoding='utf-8',
    )

    stdin = proc.stdin

    if stdin is None:
        return empty_return

    for line in _iterable:
        try:
            stdin.write(line + '\n')
            stdin.flush()
        except OSError as os_error:
            if os_error.errno != errno.EPIPE and errno.EPIPE != 32:
                raise
            break
    if proc.wait() not in [0, 1]:
        return empty_return
    try:
        stdin.close()
    except OSError as os_error:
        if os_error.errno != errno.EPIPE and errno.EPIPE != 32:
            raise
    stdout = proc.stdout
    if stdout is None:
        return empty_return
    lines: list[str] = []
    for line in stdout:
        lines.append(line[:-1])

    if len(lines) == 0:
        return empty_return

    converted: list[T] = [dct[x] for x in lines] if dct else lines  # type:ignore
    return converted if multi else converted[0]
