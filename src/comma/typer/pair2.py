from __future__ import annotations

import json
import shutil
from collections import defaultdict
from collections.abc import Generator
from collections.abc import Hashable
from collections.abc import Iterable
from collections.abc import Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from functools import lru_cache
from typing import Callable
from typing import Generic
from typing import NamedTuple
from typing import TypeVar

from comma.command import Command
from comma.typer.pair import Pair
from typing_extensions import TypedDict

L = TypeVar("L")
R = TypeVar("R")
T = TypeVar("T")


H = TypeVar("H", bound=Hashable)


def uniqued(iterable: Iterable[H]) -> Generator[H, None, None]:
    seen: set[H] = set()
    for item in iterable:
        if item not in seen:
            yield item
            seen.add(item)


class Graph(Generic[T]):
    adjeacency_list: dict[T, list[T]]

    def __init__(self, connections: Iterable[Pair[T, T]]) -> None:
        self.adjeacency_list = defaultdict(list)
        for left, right in connections:
            self.adjeacency_list[left].append(right)

    @staticmethod
    def from_indent_hierarchy(lines: Iterable[str], root_name: str | None = None) -> Graph[str]:
        pairs = (Pair(len(line) - len(line.lstrip()), line.strip()) for line in lines)

        queue: list[Pair[int, str]] = [Pair(-1, root_name or "ROOT")]
        connections: list[Pair[str, str]] = []

        for current in pairs:
            curr_indent, curr_line = current
            prev_indent, prev_line = queue[-1]
            if curr_indent > prev_indent:
                ...
            elif curr_indent == prev_indent:
                queue.pop()
            else:  # indent < prev_indent
                while queue[-1].left >= curr_indent:
                    queue.pop()
            prev_indent, prev_line = queue[-1]
            connections.append(Pair(prev_line, curr_line))
            queue.append(current)

        return (
            Graph(connections) if root_name else Graph(x for x in connections if x.right != "ROOT")
        )

    @staticmethod
    def from_lines(
        lines: Iterable[str],
        spliter: Callable[
            [str],
            Pair[str, str],
        ] = lambda x: Pair(*x.split(maxsplit=1)),
    ) -> Graph[str]:
        return Graph(spliter(line) for line in lines)


class PlantUML:
    def __init__(self, graph: Graph[str]) -> None:
        self.graph = graph

    def __str__(self) -> str:
        return "\n".join(self.lines())

    def lines(self) -> Generator[str, None, None]:
        yield "@startuml"
        for left, rights in self.graph.adjeacency_list.items():
            for right in rights:
                yield f"{left} --> {right}"
        yield "@enduml"

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(str(self))


class ContainerLS(TypedDict):
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


class ImageLS(TypedDict):
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


class DockerContainer(NamedTuple):
    docker_ls: ContainerLS

    def enter(self) -> None:
        shell = (
            Command(
                cmd=(
                    "docker",
                    "exec",
                    "-it",
                    self.docker_ls["ID"],
                    "which",
                    "bash",
                ),
            ).quick_run()
            or "sh"
        )
        Command(
            cmd=(
                "docker",
                "exec",
                "-it",
                self.docker_ls["ID"],
                shell,
            ),
        ).execvp()


@dataclass
class ContainerRunConfig:
    image: str
    name: str
    volumes: list[tuple[str, str]] = field(default_factory=list)
    ports: list[tuple[int, int]] = field(default_factory=list)
    envs: list[tuple[str, str]] = field(default_factory=list)
    additional_args: list[str] = field(default_factory=list)

    def run(
        self,
        entrypoint: str | None = None,
        command: Sequence[str] = (),
        *,
        detached: bool = False,
        privileged: bool = False,
    ) -> None:
        Command(
            cmd=(
                "docker",
                "run",
                "-it",
                *(("--detach") if detached else ()),
                *(("--privileged") if privileged else ()),
                *((f"--entrypoint={entrypoint}") if entrypoint else ()),
                "--rm",
                # '--restart=unless-stopped',
                *(f"-v={volume_pair[0]}:{volume_pair[1]}" for volume_pair in self.volumes),
                *(f"-p={port_pair[0]}:{port_pair[1]}" for port_pair in self.ports),
                *(f"-e={env_pair[0]}={env_pair[1]}" for env_pair in self.envs),
                *self.additional_args,
                "--name",
                self.name,
                self.image,
                *command,
            ),
            label="Starting docker container",
            capture_output=False,
        ).run()


class Docker:
    @property
    def binary(self) -> str:
        return "docker"

    @lru_cache(maxsize=1)  # noqa: B019
    def docker_bin_check(self) -> None:
        if not shutil.which(self.binary):
            msg = f"{self.binary} not found in path"
            raise Exception(msg)  # noqa: TRY002

        if Command(cmd=(self.binary, "ps")).run().returncode != 0:
            msg = f"{self.binary} daemon not running"
            raise Exception(msg)  # noqa: TRY002

    def list_containers(self) -> list[ContainerLS]:
        return [
            json.loads(x)
            for x in Command(
                cmd=(self.binary, "container", "ls", "--format={{json .}}"),
            )
            .quick_run()
            .splitlines()
        ]

    def list_images(self) -> list[ImageLS]:
        return [
            json.loads(x)
            for x in Command(
                cmd=(self.binary, "image", "ls", "--format={{json .}}"),
            )
            .quick_run()
            .splitlines()
        ]

    def stop(self, config: ContainerRunConfig) -> None:
        Command(
            cmd=(self.binary, "stop", config.name),
            label="Stopping docker container",
        ).run_with_spinner()

    def start(self, config: ContainerRunConfig) -> None:
        ...
        # Command(
        #     cmd=(self.binary, 'start', id),
        #     label='Starting docker container',
        # ).run_with_spinner()

    @contextmanager
    def container(self, container_run_config: ContainerRunConfig) -> Generator[None, None, None]:
        try:
            self.start(container_run_config)
            yield
        finally:
            self.stop(container_run_config)


if __name__ == "__main__":
    ContainerRunConfig(image="alpine", name="pine").run()
