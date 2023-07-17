from __future__ import annotations

from typing import Any
from typing import Type


def singleton(cls: type) -> Type[Any]:
    class Singleton(type):
        _instances: dict[type, Any] = {}

        def __call__(cls, *args: Any, **kwargs: Any) -> Any:
            if cls not in Singleton._instances:
                Singleton._instances[cls] = super().__call__(*args, **kwargs)
            return Singleton._instances[cls]
    return Singleton(cls.__name__, cls.__bases__, dict(cls.__dict__))
