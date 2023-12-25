from __future__ import annotations

import errno
import itertools
import subprocess
import typing
from typing import Callable
from typing import Iterable
from typing import Literal
from typing import overload
from typing import TYPE_CHECKING
from typing import TypeVar


if TYPE_CHECKING:
    from subprocess import _CMD


def piped_exec(
    cmd: subprocess._CMD,
    iterable: Iterable[str],
) -> list[str]:
    """
    Executes a command with input from an iterable and returns the output as a list of strings.

    Args:
        cmd (_CMD): The command to execute.
        iterable (Iterable[str]): An iterable containing the input to be passed to the command.

    Returns:
        list[str]: A list of strings representing the output of the command.
    """
    empty_return: list[str] = []
    proc = subprocess.Popen(
        args=cmd, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=None, encoding='utf-8',
    )

    stdin = proc.stdin

    if stdin is None:
        return empty_return

    for line in iterable:
        try:
            stdin.write(line + '\n')
            stdin.flush()
        except OSError as os_error:
            if os_error.errno != errno.EPIPE and errno.EPIPE != 32:
                raise
            break
    try:
        stdin.close()
    except OSError as os_error:
        if os_error.errno != errno.EPIPE and errno.EPIPE != 32:
            raise
    if proc.wait() not in [0, 1]:
        return empty_return
    stdout = proc.stdout
    if stdout is None:
        return empty_return

    return [line[:-1] for line in stdout]


T = TypeVar('T')


@overload
def select_helper(*, cmd: _CMD, items: Iterable[T], multi: Literal[True], select_one: bool = True, key: Callable[[T], str] | None = None) -> list[T]:
    ...


@overload
def select_helper(*, cmd: _CMD, items: Iterable[T], multi: Literal[False], select_one: bool = True, key: Callable[[T], str] | None = None) -> T | None:
    ...


def select_helper(*, cmd: _CMD, items: Iterable[T], multi: bool = False, select_one: bool = True, key: Callable[[T], str] | None = None) -> list[T] | T | None:
    """
    Helper function to select items from a list using a command line tool.

    Args:
        cmd (str): The command line tool to use for selection.
        items (Iterable[T]): The items to select from.
        multi (bool, optional): Whether to allow multiple selections. Defaults to False.
        select_one (bool, optional): Whether to select only one item. Defaults to True.
        key (Callable[[T], str] | None, optional): A function to extract a key from each item. Defaults to None.

    Returns:
        list[T] | T | None: The selected item(s).
    """
    empty_return: None | list[T] = [] if multi else None
    sentinel = object()
    iterator = iter(items)
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

    lines = piped_exec(cmd, _iterable)

    if not lines:
        return empty_return

    converted: list[T] = [dct[x] for x in lines] if dct else lines  # type:ignore
    return converted if multi else converted[0]
