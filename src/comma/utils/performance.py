from __future__ import annotations

import functools
import logging
import time
from contextlib import contextmanager
from typing import Callable
from typing import Generator
from typing import TypeVar

from typing_extensions import ParamSpec


P = ParamSpec('P')
R = TypeVar('R')


@contextmanager
def time_it_ctx(*, label: str) -> Generator[None, None, None]:
    start = time.monotonic_ns()
    yield
    delta_ms = (time.monotonic_ns() - start) / 1_000_000
    logging.debug(f'Time taken by {label}: {delta_ms} ms')


def time_it(*, label: str | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with time_it_ctx(label=(label or func.__name__)):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# start = time.monotonic_ns()
# result = func(*args, **kwargs)
# delta_ms = (time.monotonic_ns() - start) / 1_000_000
# logging.debug(f'Time taken by {label or func.__name__}: {delta_ms} ms')
# return result
