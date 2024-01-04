from __future__ import annotations

import logging
from typing import NamedTuple

import typer
from comma.machine import LocalMachine
from comma.machine import Machine
from comma.machine import SshMachine
from fzf import fzf


class Tmux(NamedTuple):
    machine: Machine

    def connect(self) -> None:
        if not self.machine.has_executable("tmux"):
            logging.error("Tmux not in machine")
            raise SystemExit(1)
        lines = [
            x
            for x in self.machine.quick_run(("tmux", "ls")).splitlines()
            if "no server running on" not in x and "error connecting" not in x
        ]
        create_new_session = "<create new session>"
        lines.append(create_new_session)
        selection = fzf(lines)
        if selection is None:
            return
        if selection == create_new_session:
            session_name = input("Session Name: ")
            self.machine.create_cmd(
                cmd=("tmux", "new-session", "-s", session_name),
            ).execvp()
        else:
            session_name = selection.split(":", maxsplit=1)[0]
            self.machine.create_cmd(
                cmd=("tmux", "attach-session", "-t", session_name),
            ).execvp()


app_mux = typer.Typer(
    name="mux",
    help="Mux utils.",
)


@app_mux.command()
def mux(remote: bool = typer.Option(False, "--remote")) -> None:  # noqa: FBT001, FBT003
    """Connect to tmux."""
    machine = SshMachine() if remote else LocalMachine()
    Tmux(machine).connect()


def rmux() -> None:
    """Connect to tmux remotely."""
    mux(remote=True)


if __name__ == "__name__":
    app_mux()
