# flake8: noqa: S603
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from dataclasses import field
from typing import IO
from typing import TYPE_CHECKING
from typing import TypedDict

from typing_extensions import Any
from typing_extensions import Unpack

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class CMD:
    binary: str
    flags: list[str] = field(default_factory=list)


class _GrepOptions(TypedDict, total=False):
    ignore_case: bool
    invert_match: bool


def _grep_options(options: _GrepOptions) -> list[str]:
    flags = []
    if options.get("ignore_case"):
        flags.append("-i")
    if options.get("invert_match"):
        flags.append("-v")
    return flags


def grep(**kwargs: Unpack[_GrepOptions]) -> CMD:
    return CMD("grep", _grep_options(kwargs))


def foo(cmd: list[str]) -> Iterator[str]:
    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=None, encoding="utf-8", errors="ignore"
    ) as p1:
        if p1.stdout:
            yield from p1.stdout


def pipe(cmd1: list[str], cmd2: list[str]) -> Iterator[str]:
    with subprocess.Popen(  # noqa: SIM117
        cmd1, stdout=subprocess.PIPE, stderr=None, encoding="utf-8", errors="ignore"
    ) as p1:
        with subprocess.Popen(
            cmd2,
            stdin=p1.stdout,
            stdout=subprocess.PIPE,
            stderr=None,
            encoding="utf-8",
            errors="ignore",
        ) as p2:
            if p2.stdout:
                yield from p2.stdout


class Proxy(IO[str]):
    def __getattribute__(self, __name: str) -> Any:  # noqa: ANN401
        attr = object.__getattribute__(self, __name)
        if callable(attr):

            def newfunc(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
                print("before calling %s" % attr.__name__)
                result = attr(*args, **kwargs)
                print("done calling %s" % attr.__name__)
                return result

            return newfunc
        return attr

    def fileno(self) -> int:
        return 1
