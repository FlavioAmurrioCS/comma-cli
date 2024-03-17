from __future__ import annotations

import os
from typing import NamedTuple
from typing import TYPE_CHECKING

from typing_extensions import Literal

if TYPE_CHECKING:
    from collections.abc import Sequence


class FindCommand(NamedTuple):
    paths: Sequence[str]
    maxdepth: int | None = None
    mindepth: int | None = None
    expand_paths: bool = False
    type: Literal["d", "f"] | None = None
    follow: bool = False

    def cmd(self) -> list[str]:
        ret_cmd: list[str] = (
            ["find", *self.paths]
            if not self.expand_paths
            else ["find", *map(os.path.expanduser, self.paths)]
        )

        if self.maxdepth is not None:
            ret_cmd.extend(("-maxdepth", f"{self.maxdepth}"))

        if self.mindepth is not None:
            ret_cmd.extend(("-mindepth", f"{self.mindepth}"))

        if self.follow:
            ret_cmd.append("-follow")

        if self.type is not None:
            ret_cmd.extend(("-type", self.type))

        return ret_cmd
