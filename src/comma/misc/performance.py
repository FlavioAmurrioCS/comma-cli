from __future__ import annotations

import functools
import logging
import time
from contextlib import contextmanager
from typing import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing_extensions import ParamSpec
    from typing import TypeVar

    P = ParamSpec("P")
    R = TypeVar("R")


@contextmanager
def time_it_ctx(
    *,
    label: str,
    printer: Callable[[str], None] = logging.debug,
) -> Generator[None, None, None]:
    """
    A context manager that measures the time taken by a block of code.

    Args:
    ----
        label (str): A label to identify the block of code being measured.
        printer (Callable[[str], None], optional): A function used to print the time measurement. Defaults to logging.debug.

    Yields:
    ------
        None: The context manager does not return any value.

    Example:
    -------
        >>> with time_it_ctx(label="my_function"):
        ...     my_function()
        Time taken by my_function: 123.45 ms

    """  # noqa: E501
    start = time.monotonic_ns()
    yield
    delta_ms = (time.monotonic_ns() - start) / 1_000_000
    printer(f"Time taken by {label}: {delta_ms} ms")


def time_it(
    *,
    label: str | None = None,
    printer: Callable[[str], None] = logging.debug,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator that measures the time taken by a function.

    Args:
    ----
        label (str, optional): A label to identify the function being measured. Defaults to None.
        printer (Callable[[str], None], optional): A function used to print the time measurement. Defaults to logging.debug.

    Returns:
    -------
        Callable[[Callable[P, R]], Callable[P, R]]: A decorated function that measures the time taken by the original function.

    Example:
    -------
        >>> @time_it(label="my_function")
        ... def my_function():
        ...     pass

    """  # noqa: E501

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with time_it_ctx(label=(label or func.__name__), printer=printer):
                return func(*args, **kwargs)

        return wrapper

    return decorator
