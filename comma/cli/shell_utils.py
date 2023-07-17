from __future__ import annotations

import typer

from comma.utils.fzf import fzf
from comma.utils.machine.local_machine import LocalMachine

app_sh: typer.Typer = typer.Typer(name='sh')


@app_sh.command()
def _() -> None:
    ...


@app_sh.command()
def select_project() -> None:
    """
    Select project.
    """
    selection = fzf(LocalMachine().project_list())
    if selection:
        print(selection)


if __name__ == '__main__':
    app_sh()