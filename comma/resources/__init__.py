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
YAMLT = TypeVar('YAMLT', bound=str)
OTHERT = TypeVar('OTHERT', bound=str)


def load_yaml(filename: str) -> Any:
    try:
        import warnings
        from ruamel import yaml
        from ruamel.yaml.error import UnsafeLoaderWarning
        warnings.simplefilter('ignore', UnsafeLoaderWarning)
        with open(filename) as f:
            return yaml.load(f)
    except Exception:
        from runtool import GithubReleaseLinks
        import json
        return json.loads(
            GithubReleaseLinks(user='mikefarah', project='yq').run(
                filename, '--tojson',
            ).stdout,
        )


@dataclass
class TypedResourceHelper(Generic[JSONT, YAMLT, OTHERT]):
    package: Package

    def get_resource(self, resource: JSONT | YAMLT | OTHERT) -> AbstractContextManager[Path]:
        return path(self.package, resource)

    def get_resource_json(self, resource: JSONT) -> Any:
        with path(self.package, resource) as file:
            with file.open() as f:
                import json
                return json.load(f)

    def get_resource_yaml(self, resource: YAMLT) -> Any:
        with path(self.package, resource) as file:
            print(file.as_posix())
            return load_yaml(file.as_posix())


class GenericResourceHelper(TypedResourceHelper[str, str, str]):
    ...
