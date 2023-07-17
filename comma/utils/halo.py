from __future__ import annotations

import functools
import typing
from types import TracebackType
from typing import Callable
from typing import Optional
from typing import Type
from typing import TypeVar

from rich.console import Console
from rich.console import RenderableType
from rich.status import Status
from rich.style import StyleType
if typing.TYPE_CHECKING:
    from typing_extensions import Literal
    from typing_extensions import ParamSpec
    from typing_extensions import Self

    SPINNER = Literal[
        'aesthetic', 'bounce', 'circleQuarters', 'dots4', 'dqpb', 'hearts',
        'noise', 'simpleDotsScrolling', 'toggle10', 'toggle5', 'arc',
        'bouncingBall', 'clock', 'dots5', 'earth', 'layer', 'pipe', 'smiley',
        'toggle11', 'toggle6', 'arrow', 'bouncingBar', 'dots', 'dots6', 'flip',
        'line', 'point', 'squareCorners', 'toggle12', 'toggle7', 'arrow2',
        'boxBounce', 'dots10', 'dots7', 'grenade', 'line2', 'pong', 'squish',
        'toggle13', 'toggle8', 'arrow3', 'boxBounce2', 'dots11', 'dots8',
        'growHorizontal', 'material', 'runner', 'star', 'toggle2', 'toggle9',
        'balloon', 'christmas', 'dots12', 'dots8Bit', 'growVertical', 'monkey',
        'shark', 'star2', 'toggle3', 'triangle', 'balloon2', 'circle', 'dots2',
        'dots9', 'hamburger', 'moon', 'simpleDots', 'toggle', 'toggle4', 'weather',
        'betaWave', 'circleHalves', 'dots3',
    ]
    _MAIN = {
        'info': '',
        'success': '',
        'warning': '',
        'error': '',
    }
    P = ParamSpec('P')
    R = TypeVar('R')


class FHalo(Status):
    def __init__(
        self,
        status: RenderableType,
        *,
        console: Optional[Console] = None,
        spinner: SPINNER = 'dots',
        spinner_style: StyleType = 'status.spinner',
        speed: float = 1,
        refresh_per_second: float = 12.5,
    ):
        super().__init__(
            status,
            console=console,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
            refresh_per_second=refresh_per_second,
        )
        self._success: str = f'✨ {status}'

    def __enter__(self) -> Self:
        return typing.cast('Self', super().__enter__())

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        self.console.print(self._success or self.status)
        return super().__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            with self:
                return func(*args, **kwargs)
        return wrapped

    def succeed(self, text: Optional[str] = None) -> None:
        self._success = f'[green bold]check[/green bold] {text or self.status}'

    def fail(self, text: Optional[str] = None) -> None:
        self._success = f'[red bold]cross[/red bold] {text or self.status}'

    def warn(self, text: Optional[str] = None) -> None:
        self._success = f'[yellow bold]warning[/yellow bold] {text or self.status}'