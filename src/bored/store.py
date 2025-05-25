from __future__ import annotations

import atexit
import pickle
from contextlib import suppress
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bored.models import Activity


class ActivityStore:
    filename: str
    _data: dict[str, Activity]

    def __init__(self, filename: str) -> None:
        self._data: dict[str, Activity] = {}
        self.filename = filename

    @cached_property
    def data(self) -> dict[str, Activity]:
        with suppress(FileNotFoundError), open(self.filename, "rb") as f:
            self._data = pickle.load(f)  # noqa: S301
        atexit.register(self.__save__)
        return self._data

    def __save__(self) -> None:
        with open(self.filename, "wb") as f:
            pickle.dump(self.data, f)

    def add(self, activity: Activity) -> None:
        self.data[activity.id] = activity

    def remove(self, activity: Activity) -> None:
        del self.data[activity.id]
