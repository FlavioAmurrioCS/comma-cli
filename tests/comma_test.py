from __future__ import annotations

import itertools
import pkgutil
from typing import TYPE_CHECKING

import comma as comma_pkg
import gron as gron_pkg
import gum as gum_pkg
import pytest
from comma.main import app_main
from comma.typer.reflection import TyperReflection
from typer.testing import CliRunner

if TYPE_CHECKING:
    from collections.abc import Sequence
    from collections.abc import Generator
    from types import ModuleType
    from comma.typer.reflection import TyperNode


runner = CliRunner()
ignore_commands = {
    ("dev", "reflection", "run"),
    ("dev", "reflection", "show"),
}

modules = (
    name
    for _, name, _ in itertools.chain(
        *(
            pkgutil.walk_packages(pkg.__path__, f"{pkg.__name__}.")
            for pkg in (comma_pkg, gron_pkg, gum_pkg)
        )
    )
)

ignore_modules = {
    "comma._personal.lazy_meetup",
}


@pytest.mark.parametrize("node", TyperReflection(app=app_main)._traverse_nodes_())  # noqa: SLF001
def test_help(node: TyperNode) -> None:
    if node.path in ignore_commands:
        return
    result = runner.invoke(app_main, [*node.path[1:], "--help"])
    assert result.exit_code == 0


# def test_resource_loading() -> None:
#     from comma.resources.ol import COMMA_RESOURCE_LOADER
#     assert COMMA_RESOURCE_LOADER.get_resource_json('main.json') is not None


@pytest.mark.parametrize("import_name", modules)
def test_module_imports(import_name: str) -> None:
    if import_name in ignore_modules:
        return
    print(f"Importing {import_name}")
    __import__(import_name, fromlist=["_trash"])


def iter_modules(modules: Sequence[ModuleType]) -> Generator[ModuleType, None, None]:
    seen = set()
    for _, name, _ in itertools.chain(
        *(pkgutil.walk_packages(pkg.__path__, f"{pkg.__name__}.") for pkg in modules)
    ):
        if name not in seen:
            seen.add(name)
            yield __import__(name, fromlist=["_trash"])
