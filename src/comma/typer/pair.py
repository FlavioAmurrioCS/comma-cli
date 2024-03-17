from __future__ import annotations

from dataclasses import astuple
from dataclasses import dataclass
from typing import Callable
from typing import Generic
from typing import NamedTuple
from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterator


_L = TypeVar("_L")
_R = TypeVar("_R")

try:

    class Pair(NamedTuple, Generic[_L, _R]):
        """
        A generic Pair class that represents a pair of values.

        Attributes
        ----------
        left : L
            The left value of the pair.
        right : R
            The right value of the pair.

        """

        left: _L
        right: _R

        def flip(self) -> Pair[_R, _L]:
            """
            Returns a new Pair with the left and right values swapped.

            Returns
            -------
            Pair[R, L]
                A new Pair with the left and right values swapped.

            """
            return Pair(self.right, self.left)

except TypeError:

    @dataclass(frozen=True, unsafe_hash=True)
    class Pair(Generic[_L, _R]):  # type: ignore[no-redef]
        """
        A generic Pair class that represents a pair of values.

        Attributes
        ----------
        left : L
            The left value of the pair.
        right : R
            The right value of the pair.

        """

        left: _L
        right: _R

        def flip(self) -> Pair[_R, _L]:
            """
            Returns a new Pair with the left and right values swapped.

            Returns
            -------
            Pair[R, L]
                A new Pair with the left and right values swapped.

            """
            return Pair(self.right, self.left)

        def __iter__(self) -> Iterator[_L | _R]:
            """
            Returns an iterator over the left and right values of the Pair.

            Returns
            -------
            Iterator[Union[L, R]]
                An iterator over the left and right values of the Pair.

            """
            yield from astuple(self)


def pair_parse(
    left_func: Callable[[str], _L], right_func: Callable[[str], _R], delim: str = ","
) -> Callable[[str], Pair[_L, _R]]:
    """
    Returns a function that parses a string into a Pair.

    Parameters
    ----------
    left_func : Callable[[str], L]
        A function that converts a string into the left value of the Pair.
    right_func : Callable[[str], R]
        A function that converts a string into the right value of the Pair.
    delim : str, optional
        The delimiter used to separate the left and right values of the Pair. Default is ','.

    Returns
    -------
    Callable[[str], Pair[L, R]]
        A function that parses a string into a Pair.

    """

    def parse_pair(value: str) -> Pair[_L, _R]:
        left, right = value.split(delim, maxsplit=1)
        return Pair(left_func(left), right_func(right))

    return parse_pair
