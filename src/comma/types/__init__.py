from __future__ import annotations

from typing import List
from typing import Tuple
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

from typing_extensions import ParamSpec


P = ParamSpec("P")
T = TypeVar("T")
R = TypeVar("R")

CMD_ARGS: TypeAlias = Union[List[str], Tuple[str, ...]]
