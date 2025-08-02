from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from typing import NamedTuple

if TYPE_CHECKING:
    from typing_extensions import Literal

    ACTIVITY_TYPE = Literal[
        "education",
        "recreational",
        "social",
        "diy",
        "charity",
        "cooking",
        "relaxation",
        "music",
        "busywork",
    ]


class Activity(NamedTuple):
    id: str
    title: str
    description: str

    @classmethod
    def create_activity(cls, *, title: str, description: str) -> Activity:
        return cls(id=str(uuid.uuid4()), title=title, description=description)
