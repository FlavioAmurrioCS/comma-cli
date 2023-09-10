from __future__ import annotations

from dataclasses import astuple
from dataclasses import dataclass
from typing import Callable
from typing import Generic
from typing import Iterator
from typing import NamedTuple
from typing import TypeVar
from typing import Union


L = TypeVar('L')
R = TypeVar('R')

try:
    class Pair(NamedTuple, Generic[L, R]):  # type: ignore
        """
        A generic Pair class that represents a pair of values.

        Attributes:
        -----------
        left : L
            The left value of the pair.
        right : R
            The right value of the pair.
        """
        left: L
        right: R

        def flip(self) -> Pair[R, L]:
            """
            Returns a new Pair with the left and right values swapped.

            Returns:
            --------
            Pair[R, L]
                A new Pair with the left and right values swapped.
            """
            return Pair(self.right, self.left)

except TypeError:
    @dataclass(frozen=True, unsafe_hash=True)
    class Pair(Generic[L, R]):  # type: ignore[no-redef]
        """
        A generic Pair class that represents a pair of values.

        Attributes:
        -----------
        left : L
            The left value of the pair.
        right : R
            The right value of the pair.
        """
        left: L
        right: R

        def flip(self) -> Pair[R, L]:
            """
            Returns a new Pair with the left and right values swapped.

            Returns:
            --------
            Pair[R, L]
                A new Pair with the left and right values swapped.
            """
            return Pair(self.right, self.left)

        def __iter__(self) -> Iterator[Union[L, R]]:
            """
            Returns an iterator over the left and right values of the Pair.

            Returns:
            --------
            Iterator[Union[L, R]]
                An iterator over the left and right values of the Pair.
            """
            yield from astuple(self)


def pair_parse(left_func: Callable[[str], L], right_func: Callable[[str], R], delim: str = ',') -> Callable[[str], Pair[L, R]]:
    """
    Returns a function that parses a string into a Pair.

    Parameters:
    -----------
    left_func : Callable[[str], L]
        A function that converts a string into the left value of the Pair.
    right_func : Callable[[str], R]
        A function that converts a string into the right value of the Pair.
    delim : str, optional
        The delimiter used to separate the left and right values of the Pair. Default is ','.

    Returns:
    --------
    Callable[[str], Pair[L, R]]
        A function that parses a string into a Pair.
    """
    def parse_pair(value: str) -> Pair[L, R]:
        left, right = value.split(delim, maxsplit=1)
        return Pair(left_func(left), right_func(right))
    return parse_pair
