from __future__ import annotations

import json
from typing import List

import typer
from comma.utils.command import Command
from comma.utils.fzf import fzf
from typing_extensions import TypedDict

app_docker: typer.Typer = typer.Typer(
    name='docker',
    help='Docker related commands',
)


class DockerLS(TypedDict):
    Command: str
    CreatedAt: str
    ID: str
    Image: str
    Labels: str
    LocalVolumes: str
    Mounts: str
    Names: str
    Networks: str
    Ports: str
    RunningFor: str
    Size: str
    State: str
    Status: str


def list_containers() -> List[DockerLS]:
    return [
        json.loads(x)
        for x in Command(
            cmd=('docker', 'container', 'ls', '--format={{json .}}'),
        )
        .quick_run()
        .splitlines()
    ]


@app_docker.command()
def _() -> None:
    ...


@app_docker.command()
def enter() -> None:
    selection = fzf(
        list_containers(),
        key=lambda x: str((x['ID'], x['Names'], x['Image'])),
    )
    if selection:
        Command(
            cmd=(
                'docker', 'exec', '-it',
                selection['ID'], 'bash',
            ),
        ).execvp()


if __name__ == '__main__':
    app_docker()
