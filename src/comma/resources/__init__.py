from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import Package
from importlib.resources import path
from typing import Any
from typing import Generic
from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:
    from pathlib import Path
    from contextlib import AbstractContextManager


JSONT = TypeVar("JSONT", bound=str)
OTHERT = TypeVar("OTHERT", bound=str)


@dataclass
class TypedResourceHelper(Generic[JSONT, OTHERT]):
    package: Package

    def get_resource(self, resource: JSONT | OTHERT) -> AbstractContextManager[Path]:
        return path(self.package, resource)

    def get_resource_json(self, resource: JSONT) -> Any:  # noqa: ANN401
        with path(self.package, resource) as file, file.open() as f:
            import json

            return json.load(f)


class GenericResourceHelper(TypedResourceHelper[str, str]): ...
