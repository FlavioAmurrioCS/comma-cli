from __future__ import annotations

import os
from typing import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


def ancestors(path: str) -> Generator[str, None, None]:
    """Generate all ancestors of a path."""
    path = os.path.abspath(path)
    yield path
    while path != "/":
        path = os.path.dirname(path)
        yield path


def find_up_dir(predicate: Callable[[str], bool], start_dir: str) -> str | None:
    """Find directory where the predicate is true."""
    for path in ancestors(start_dir):
        if predicate(path):
            return path
    return None
