from __future__ import annotations

from typing import Any


def singleton(cls: type) -> type[Any]:
    class Singleton(type):
        _instances: dict[type, Any] = {}  # noqa: RUF012

        def __call__(cls, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            if cls not in Singleton._instances:
                Singleton._instances[cls] = super().__call__(*args, **kwargs)
            return Singleton._instances[cls]

    return Singleton(cls.__name__, cls.__bases__, dict(cls.__dict__))
