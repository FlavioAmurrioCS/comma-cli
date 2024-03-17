from __future__ import annotations

import argparse
import sys
from contextlib import suppress
from textwrap import dedent
from typing import Literal
from typing import overload
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing_extensions import Protocol  # python3.8+
    from typing_extensions import Self
else:
    Protocol = object


class CLIApp(Protocol):
    COMMAND_NAME: str
    ADD_HELP: bool = True
    ARG_HELP: dict[str, str | None]

    @classmethod
    def _short_description(cls) -> str:
        return (cls.__doc__ or cls.__name__).splitlines()[0]

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description=cls._short_description(),
            add_help=cls.ADD_HELP,
        )
        with suppress(Exception):
            if sys.argv[1] == cls.COMMAND_NAME:
                parser.prog = f"{parser.prog} {cls.COMMAND_NAME}"
        for field, ztype_ in cls.__annotations__.items():
            if field in ("COMMAND_NAME", "ADD_HELP", "ARG_HELP"):
                continue
            ztype = str(ztype_)
            kwargs = {
                "help": cls.ARG_HELP.get(field),
            }

            field_arg = field.replace("_", "-")
            if ztype.startswith("list["):
                kwargs["nargs"] = "+"
            if ztype == "bool":
                kwargs["action"] = "store_true"
            if hasattr(cls, field):
                kwargs["default"] = getattr(cls, field)
                field_arg = f'--{field.replace("_", "-")}'
            if "None" in ztype:
                field_arg = f'--{field.replace("_", "-")}'
            if "Literal" in ztype:
                kwargs["choices"] = eval(ztype.split("Literal")[1].split("[")[1].split("]")[0])  # noqa: S307, PGH001
            parser.add_argument(field_arg, **kwargs)  # type:ignore
        return parser

    @overload
    @classmethod
    def parse_args(cls, argv: Sequence[str] | None) -> Self: ...

    @overload
    @classmethod
    def parse_args(
        cls, argv: Sequence[str] | None, *, allow_unknown_args: Literal[False]
    ) -> Self: ...

    @overload
    @classmethod
    def parse_args(
        cls, argv: Sequence[str] | None, *, allow_unknown_args: Literal[True]
    ) -> tuple[Self, list[str]]: ...

    @classmethod
    def parse_args(
        cls, argv: Sequence[str] | None = None, *, allow_unknown_args: bool = False
    ) -> tuple[Self, list[str]] | Self:
        return (
            cls.parser().parse_known_args(argv)  # type:ignore
            if allow_unknown_args
            else cls.parser().parse_args(argv)
        )

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int: ...

    @classmethod
    def main(cls, argv: Sequence[str] | None = None, prog: str | None = None) -> int:
        dct = {x.COMMAND_NAME: x for x in cls.__subclasses__()}

        parser = argparse.ArgumentParser(add_help=False, prog=prog)
        parser.add_argument("command", choices=dct.keys())
        help_text = dedent(
            f"""\
            {parser.prog} <command> [options] [args...]

            Available commands:
            """
        ) + "\n".join(f"  {k:20} {v._short_description()}" for k, v in dct.items())  # noqa: SLF001
        if sys.argv[1] in ("--help", "-h"):
            print(help_text)
            return 0
        args, rest = parser.parse_known_args(argv)
        raise SystemExit(dct[args.command].run(rest))
