from __future__ import annotations

import pytest
from typer.testing import CliRunner

from comma.cli.reflection import __traverse_nodes__
from comma.cli.reflection import TyperNode
from comma.main import app_main


runner = CliRunner()
ignore_commands = {
    ('dev', 'reflection', 'run'),
    ('dev', 'reflection', 'show'),
}


@pytest.mark.parametrize('node', __traverse_nodes__())
def test_help(node: TyperNode) -> None:
    print(node.path)
    if node.path in ignore_commands:
        return
    result = runner.invoke(app_main, [*node.path[1:], '--help'])
    assert result.exit_code == 0
