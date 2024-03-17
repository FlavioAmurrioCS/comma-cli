from __future__ import annotations

from contextlib import ExitStack
from typing import TextIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import TracebackType
    from typing_extensions import Self


class DualWriter:
    """
    A context manager that writes to two files simultaneously.

    Attributes
    ----------
        __left__ (str): The path to the left file.
        __right__ (str): The path to the right file.
        __stack__ (ExitStack): The exit stack used to manage the context.
        left_writer (TextIO): The file object for the left file.
        right_writer (TextIO): The file object for the right file.

    """

    __left__: str
    __right__: str
    __stack__: ExitStack
    left_writer: TextIO
    right_writer: TextIO

    def __init__(self, left: str, right: str) -> None:
        """
        Initializes a DualWriter instance.

        Args:
        ----
            left (str): The path to the left file.
            right (str): The path to the right file.

        """
        self.__left__ = left
        self.__right__ = right

    def __enter__(self) -> Self:
        """
        Enters the context and opens the left and right files for writing.

        Returns
        -------
            Self: The DualWriter instance.

        """
        self.__stack__ = ExitStack().__enter__()
        try:
            self.left_writer = self.__stack__.enter_context(open(self.__left__, "w"))  # noqa: SIM115
            self.right_writer = self.__stack__.enter_context(open(self.__right__, "w"))  # noqa: SIM115
        except BaseException:
            self.__stack__.close()
            raise
        return self

    def __exit__(
        self,
        tp: type[BaseException] | None,
        inst: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        """
        Exits the context and closes the left and right files.

        Args:
        ----
            tp (Optional[Type[BaseException]]): The type of the exception raised, if any.
            inst (Optional[BaseException]): The exception instance raised, if any.
            tb (Optional[TracebackType]): The traceback object for the exception, if any.

        Returns:
        -------
            Optional[bool]: True if the exception was handled, False otherwise.

        """
        return self.__stack__.__exit__(tp, inst, tb)

    def write(self, s: str) -> int:
        """
        Writes a string to both the left and right files.

        Args:
        ----
            s (str): The string to write.

        Returns:
        -------
            int: The number of characters written to the right file.

        """
        self.left_writer.write(s)
        return self.right_writer.write(s)

    def flush(self) -> None:
        """Flushes the buffers for both the left and right files."""
        self.left_writer.flush()
        self.right_writer.flush()

    def writelines(self, lines: Iterable[str]) -> None:
        """
        Writes a sequence of strings to both the left and right files.

        Args:
        ----
            lines (Iterable[str]): The sequence of strings to write.

        """
        self.left_writer.writelines(lines)
        self.right_writer.writelines(lines)
