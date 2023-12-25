from __future__ import annotations

import os
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence

from typing_extensions import Literal


class FindCommand(NamedTuple):
    paths: Sequence[str]
    maxdepth: Optional[int] = None
    mindepth: Optional[int] = None
    expand_paths: bool = False
    type: Optional[Literal['d', 'f']] = None
    follow: bool = False

    def cmd(self) -> List[str]:
        ret_cmd: list[str] = (
            ['find', *self.paths]
            if not self.expand_paths
            else ['find', *map(os.path.expanduser, self.paths)]  # type:ignore
        )

        if self.maxdepth is not None:
            ret_cmd.extend(('-maxdepth', f'{self.maxdepth}'))

        if self.mindepth is not None:
            ret_cmd.extend(('-mindepth', f'{self.mindepth}'))

        if self.follow:
            ret_cmd.append('-follow')

        if self.type is not None:
            ret_cmd.extend(('-type', self.type))

        return ret_cmd
