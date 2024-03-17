from __future__ import annotations

import json
from typing import TYPE_CHECKING

from comma.simple_argparser import CLIApp
from gron import gron
from gron import ungron

if TYPE_CHECKING:
    from collections.abc import Sequence


class Gron(CLIApp):
    """Gron is a command line tool that makes JSON greppable."""

    COMMAND_NAME = "gron"
    ARG_HELP = {  # noqa: RUF012
        "file": "File to read from. Defaults to stdin.",
        "ungron": "Ungron the input.",
    }
    file: str = "/dev/stdin"
    ungron: bool = False

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        args = cls.parse_args(argv)
        if args.ungron:
            with open(args.file) as f:
                print(
                    json.dumps(
                        ungron(f),
                        indent=2,
                        sort_keys=True,
                    ),
                )
            return 0
        with open(args.file) as f:
            for line in gron(json.load(f)):
                print(line)
        return 0


if __name__ == "__main__":
    # prog = f'python3 -m {__package__}' if __package__ and not sys.argv[0].endswith('__main_.py') else None  # noqa: E501
    # CLIApp.main(prog=prog)
    Gron.run()
