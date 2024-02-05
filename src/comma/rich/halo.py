from __future__ import annotations

import functools
import platform
import typing
from typing import Callable
from typing import TypeVar

from rich.status import Status
from typing_extensions import TypedDict

if typing.TYPE_CHECKING:
    from types import TracebackType
    from rich.console import Console
    from rich.console import RenderableType
    from rich.style import StyleType
    from typing_extensions import Literal
    from typing_extensions import ParamSpec
    from typing_extensions import Self

    SPINNER = Literal[
        "aesthetic",
        "bounce",
        "circleQuarters",
        "dots4",
        "dqpb",
        "hearts",
        "noise",
        "simpleDotsScrolling",
        "toggle10",
        "toggle5",
        "arc",
        "bouncingBall",
        "clock",
        "dots5",
        "earth",
        "layer",
        "pipe",
        "smiley",
        "toggle11",
        "toggle6",
        "arrow",
        "bouncingBar",
        "dots",
        "dots6",
        "flip",
        "line",
        "point",
        "squareCorners",
        "toggle12",
        "toggle7",
        "arrow2",
        "boxBounce",
        "dots10",
        "dots7",
        "grenade",
        "line2",
        "pong",
        "squish",
        "toggle13",
        "toggle8",
        "arrow3",
        "boxBounce2",
        "dots11",
        "dots8",
        "growHorizontal",
        "material",
        "runner",
        "star",
        "toggle2",
        "toggle9",
        "balloon",
        "christmas",
        "dots12",
        "dots8Bit",
        "growVertical",
        "monkey",
        "shark",
        "star2",
        "toggle3",
        "triangle",
        "balloon2",
        "circle",
        "dots2",
        "dots9",
        "hamburger",
        "moon",
        "simpleDots",
        "toggle",
        "toggle4",
        "weather",
        "betaWave",
        "circleHalves",
        "dots3",
    ]

    P = ParamSpec("P")
    R = TypeVar("R")


class _Symbols(TypedDict):
    info: str
    success: str
    warning: str
    error: str


# pip install log_symbols
symbols: _Symbols = (
    {
        "info": "ℹ",  # noqa: RUF001
        "success": "✔",
        "warning": "⚠",
        "error": "✖",
    }
    if platform.system() != "Windows"
    else {
        "info": "¡",
        "success": "v",
        "warning": "!!",
        "error": "×",  # noqa: RUF001
    }
)


class FHalo(Status):
    def __init__(  # noqa: PLR0913
        self,
        status: RenderableType,
        *,
        console: Console | None = None,
        spinner: SPINNER = "dots",
        spinner_style: StyleType = "status.spinner",
        speed: float = 1,
        refresh_per_second: float = 12.5,
    ) -> None:
        super().__init__(
            status,
            console=console,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
            refresh_per_second=refresh_per_second,
        )
        self._success: str = f'{symbols["info"]} {status}'

    def __enter__(self) -> Self:
        return typing.cast("Self", super().__enter__())

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.console.print(self._success or self.status)
        return super().__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            with self:
                return func(*args, **kwargs)

        return wrapped

    def succeed(self, text: str | None = None) -> None:
        self._success = f'[green bold]{symbols["success"]}[/green bold] {text or self.status}'

    def fail(self, text: str | None = None) -> None:
        self._success = f'[red bold]{symbols["error"]}[/red bold] {text or self.status}'

    def warn(self, text: str | None = None) -> None:
        self._success = f'[yellow bold]{symbols["warning"]}[/yellow bold] {text or self.status}'


def spinner(
    *title: str | None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that adds a spinner animation to a function.

    Args:
    ----
        *title: The title of the spinner animation. If not provided, the function name will be used.

    Returns:
    -------
        A decorated function that displays a spinner animation while the function is executing.

    Raises:
    ------
        Any exception raised by the decorated function will be propagated.

    Example:
    -------
        @spinner("Processing")
        def process_data(data: List[int]) -> List[int]:
            # Function implementation
            pass

    """

    def _inner_(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            with FHalo(
                status=f"{title or func.__name__}",
            ) as halo:
                try:
                    result = func(*args, **kwargs)
                    halo.succeed()
                except Exception:
                    halo.fail()
                    raise
                else:
                    return result

        return wrapped

    return _inner_
