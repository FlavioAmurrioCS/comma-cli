from __future__ import annotations

import json
import random
import string
from collections import defaultdict
from enum import Enum
from functools import lru_cache
from typing import ChainMap
from typing import NamedTuple

import typer
from comma.command import Command
from typedfzf import fzf
from typing_extensions import TypedDict

app_docker: typer.Typer = typer.Typer(
    name='docker',
    help='Docker related commands',
)


class _DockerContainerInfo(TypedDict):
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


class _DockerImageInfo(TypedDict):
    Containers: str
    CreatedAt: str
    CreatedSince: str
    Digest: str
    ID: str
    Repository: str
    SharedSize: str
    Size: str
    Tag: str
    UniqueSize: str
    VirtualSize: str


class DockerClient(NamedTuple):
    @lru_cache(maxsize=1)
    def list_containers(self) -> list[_DockerContainerInfo]:
        return [
            json.loads(x)
            for x in Command(
                cmd=('docker', 'container', 'ls', '--format={{json .}}'),
            )
            .quick_run()
            .splitlines()
        ]

    @lru_cache(maxsize=1)
    def list_images(self) -> list[_DockerImageInfo]:
        return [
            json.loads(x)
            for x in Command(
                cmd=('docker', 'image', 'ls', '--format={{json .}}'),
            )
            .quick_run()
            .splitlines()
        ]


DOCKER_CLIENT = DockerClient()


@lru_cache(maxsize=1)
def _image_lookup_dict() -> dict[str, _DockerImageInfo]:
    data = DOCKER_CLIENT.list_images()
    return ChainMap(
        {x['ID']: x for x in DOCKER_CLIENT.list_images()},
        {f"{image['Repository']}:{image['Tag']}": image for image in data},
        defaultdict(lambda: defaultdict(str)),  # type: ignore
    )


def _docker_image_repr(image: _DockerImageInfo) -> str:
    return f"{image['ID']} | {image['CreatedSince'].ljust(15)} | {image['Repository']}:{image['Tag']}"


def _docker_container_repr(container: _DockerContainerInfo) -> str:
    return f"{container['ID']} | {container['Names'].ljust(23)} | {_docker_image_repr(_image_lookup_dict()[container['Image']])}"


@app_docker.command()
def enter() -> None:
    """
    Enter container.
    """
    selection = fzf(
        DOCKER_CLIENT.list_containers(),
        key=_docker_container_repr,
        select_one=False,
    )
    if selection:
        Command(
            cmd=(
                'docker', 'exec', '-it',
                selection['Names'], 'sh', '-c', 'which bash >/dev/null 2>&1 && exec bash || exec sh',
            ),
        ).execvp()


@app_docker.command()
def stop() -> None:
    """
    Stop container.
    """
    selection = fzf(
        DOCKER_CLIENT.list_containers(),
        key=_docker_container_repr,
        select_one=False,
    )
    if selection:
        Command(cmd=('docker', 'stop', selection['Names'])).execvp()


class _DockerPlatform(str, Enum):
    amd64 = 'amd64'
    aarch64 = 'aarch64'


@app_docker.command()
def explore(
        image: str | None = typer.Argument(None),
        shell: str = 'sh',
        user: str | None = None,
        platform: _DockerPlatform | None = None,
) -> None:
    """
    Run a container and enter it.
    """
    if not image:
        image_selection = fzf(
            DOCKER_CLIENT.list_images(),
            key=_docker_image_repr,
            select_one=False,
        )
        if image_selection:
            image = (
                (image_selection['Repository'] + ':' + image_selection['Tag'])
                if image_selection['Tag'] != '<none>'
                else image_selection['ID']
            )
    if image:
        Command(
            cmd=(
                'docker', 'run',
                '-it', '--rm',
                *((f'--user={user}',) if user else ()),
                *((f'--platform=linux/{platform.value}',) if platform else ()),
                '--entrypoint', shell,
                f'--name=docker-explore-{"".join(random.choices(string.ascii_lowercase + string.digits, k=8))}',
                image,
            ),
        ).execvp()


if __name__ == '__main__':
    app_docker()
