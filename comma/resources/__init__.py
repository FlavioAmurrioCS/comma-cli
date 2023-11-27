from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from importlib.resources import Package
from importlib.resources import path
from pathlib import Path
from typing import Any
from typing import Generic
from typing import TypeVar


JSONT = TypeVar('JSONT', bound=str)
OTHERT = TypeVar('OTHERT', bound=str)


@dataclass
class TypedResourceHelper(Generic[JSONT, OTHERT]):
    package: Package

    def get_resource(self, resource: JSONT | OTHERT) -> AbstractContextManager[Path]:
        return path(self.package, resource)

    def get_resource_json(self, resource: JSONT) -> Any:
        with path(self.package, resource) as file:
            with file.open() as f:
                import json
                return json.load(f)


class GenericResourceHelper(TypedResourceHelper[str, str]):
    ...
