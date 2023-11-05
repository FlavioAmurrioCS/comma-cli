from __future__ import annotations

import logging
import os
from typing import List

import typer

from comma.misc.performance import time_it
from persistent_cache import sqlite_cache

app_shell_scripts = typer.Typer()


@sqlite_cache(minutes=5)
def script_dir() -> str:
    from src.resources import GenericResourceHelper
    loader = GenericResourceHelper('comma.resources.shell_scripts')
    with loader.get_resource('.') as bb:
        return bb.as_posix()


@time_it()
@sqlite_cache(minutes=1)
def _tools() -> List[str]:
    return [x for x in os.listdir(script_dir()) if os.path.isfile(x) and x != '__init__.py']


@app_shell_scripts.command(
    add_help_option=False,
    no_args_is_help=True,
    context_settings={
        'allow_extra_args': True,
        'ignore_unknown_options': True,
    },
)
def sh(
    ctx: typer.Context,
    tool: str = typer.Argument('bb', autocompletion=_tools, help=f'{" ".join(_tools())}'),
    which: bool = typer.Option(False, '--which', help='Print the command instead of running it.'),
) -> int:
    """
    Installs (if needed) and runs a tool.
    """

    if tool not in _tools():
        if tool == '--help':
            print(ctx.get_help())
        else:
            logging.error(f'No tool named: {tool}')
        return 1
    cmd = (os.path.join(script_dir(), tool), *ctx.args)
    os.execvp(cmd[0], cmd)


if __name__ == '__main__':
    app_shell_scripts()
