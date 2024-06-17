from __future__ import annotations

from typing import Any
from typing import Callable
from typing import Optional
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Sequence
    import typer


def typer_command_wrap(
    *,
    app: typer.Typer,
    func: Callable[[Sequence[str]], Any],
    name: Optional[str] = None,  # noqa: UP007
    help: Optional[str] = None,  # noqa: A002, UP007
) -> Callable[..., Any]:
    """Convert a regular function into a typer command."""

    def __inner(ctx: typer.Context) -> Any:  # noqa: ANN401
        return func(ctx.args)

    __inner.__doc__ = func.__doc__
    return app.command(
        name,
        help=help,
        context_settings={
            "allow_extra_args": True,
            "ignore_unknown_options": True,
        },
    )(__inner)
