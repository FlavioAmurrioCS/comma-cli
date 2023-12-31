from __future__ import annotations


import typer
from comma.machine import LocalMachine
from comma.machine import SshMachine
from typedfzf import fzf

app_c: typer.Typer = typer.Typer(name="c")


def code_open(machine: LocalMachine | SshMachine, path: str | None = None) -> None:
    selection: str | None = path or fzf(machine.project_list())
    if selection:
        machine.code_open(selection)


@app_c.command()
def c(path: str | None = typer.Argument(None)) -> None:
    """
    Open filepath in vscode.
    """
    code_open(LocalMachine(), path)


@app_c.command()
def rc(path: str | None = typer.Argument(None)) -> None:
    """
    Open vscode remotely.
    """
    code_open(SshMachine(), path)


if __name__ == "__main__":
    app_c()
