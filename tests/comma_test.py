from __future__ import annotations

import pkgutil

import pytest
from typer.testing import CliRunner

import comma as pkg
from comma.cli.reflection import __traverse_nodes__
from comma.cli.reflection import TyperNode
from comma.main import app_main
from comma.resources import COMMA_RESOURCE_LOADER


runner = CliRunner()
ignore_commands = {
    ('dev', 'reflection', 'run'),
    ('dev', 'reflection', 'show'),
}

modules = (
    name
    for _, name, _ in pkgutil.walk_packages(pkg.__path__, f'{pkg.__name__}.')
)

ignore_modules = {
    'comma.cli.lazy_meetup',
}


@pytest.mark.parametrize('node', __traverse_nodes__())
def test_help(node: TyperNode) -> None:
    if node.path in ignore_commands:
        return
    result = runner.invoke(app_main, [*node.path[1:], '--help'])
    assert result.exit_code == 0


def test_resource_loading() -> None:
    assert COMMA_RESOURCE_LOADER.get_resource_json('main.json') is not None


@pytest.mark.parametrize('import_name', modules)
def test_module_imports(import_name: str) -> None:
    if import_name in ignore_modules:
        return
    print(f'Importing {import_name}')
    __import__(import_name, fromlist=['_trash'])
