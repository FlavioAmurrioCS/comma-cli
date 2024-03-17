from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console
    from rich.syntax import Syntax


class LazyLoader:
    @cached_property
    def Console(self) -> type[Console]:  # noqa: N802
        from rich.console import Console

        return Console

    @cached_property
    def Syntax(self) -> type[Syntax]:  # noqa: N802
        from rich.syntax import Syntax

        return Syntax

    @cached_property
    def rprint(self):  # type:ignore[no-untyped-def] # noqa: ANN201
        from rich import print as rprint

        return rprint

    @cached_property
    def print_json(self):  # type:ignore[no-untyped-def] # noqa: ANN201
        from rich import print as print_json

        return print_json


ll = LazyLoader()
