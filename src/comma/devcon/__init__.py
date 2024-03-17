# flake8: noqa: E501
from __future__ import annotations

import logging
import os
import platform as _platform
from dataclasses import dataclass
from dataclasses import field
from textwrap import dedent
from typing import NamedTuple

import typer
from comma.command import Command
from comma.config import comma_utils
from comma.docker import DOCKER_CLIENT
from comma.machine import SshMachine
from persistent_cache.decorators import persistent_cache
from typing_extensions import Literal


_DOCKERFILE = os.path.join(comma_utils.opt_dir, "devcon", "Dockerfile")


class DockerPorts(NamedTuple):
    host: int
    container: int

    def __str__(self) -> str:
        return f"{self.host}:{self.container}"

    @classmethod
    def parse(cls, s: str) -> DockerPorts:
        host, container = map(int, s.split(":"))
        return cls(host, container)


class DockerVolumes(NamedTuple):
    host: str
    container: str

    def __str__(self) -> str:
        return f"{self.host}:{self.container}"

    @classmethod
    def parse(cls, s: str) -> DockerVolumes:
        host, container = s.split(":")
        return cls(host, container)


@persistent_cache(days=7)
def user_info() -> dict[Literal["group_id", "user_id", "username"], str]:
    return {
        "group_id": Command(("id", "-g")).quick_run(),
        "user_id": Command(("id", "-u")).quick_run(),
        "username": os.environ["USER"],
    }


@dataclass
class DevContainer:
    """Base image must be ubuntu based."""

    base_image: str = "ubuntu:jammy"
    _group_id: str | None = None
    _user_id: str | None = None
    _username: str | None = None
    image_name: str = "devcon"
    ssh_port: int = 2222
    volumes: list[tuple[str, str]] = field(default_factory=list)
    ports: list[tuple[int, int]] = field(default_factory=list)
    envs: list[tuple[str, str]] = field(default_factory=list)
    additional_args: list[str] = field(default_factory=list)
    additional_setup: str = ""
    platform: Literal["linux/arm64", "linux/amd64"] = (
        "linux/arm64" if _platform.machine() == "arm64" else "linux/amd64"
    )

    @property
    def group_id(self) -> str:
        self._group_id = self._group_id or user_info()["group_id"]
        return self._group_id

    @property
    def user_id(self) -> str:
        self._user_id = self._user_id or user_info()["user_id"]
        return self._user_id

    @property
    def username(self) -> str:
        self._username = self._username or user_info()["username"]
        return self._username

    def template(self) -> str:
        return (
            dedent(
                rf"""
            FROM --platform={self.platform} {self.base_image}
            USER root

            ENV LANG=C.UTF-8
            ENV TERM=xterm-256color
            ENV COLORTERM=truecolor

            ARG DEVENV_GROUP_ID={self.group_id}
            ARG DEVENV_USER_ID={self.user_id}
            ARG DEVENV_USERNAME={self.username}

            SHELL ["/bin/bash", "-c"]

            # hadolint ignore=DL3008,DL3009,DL3013,SC2086
            RUN : \
                && echo "================================================ CREATE USER ===============================================" \
                && DEBIAN_FRONTEND=noninteractive apt-get update \
                && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y sudo curl wget git bash apt-utils gpg-agent zip unzip \
                && groupadd --force --gid "${{DEVENV_GROUP_ID}}" domain_users \
                && useradd -ms /bin/bash --no-log-init "${{DEVENV_USERNAME}}" "--uid=${{DEVENV_USER_ID}}" "--gid=${{DEVENV_GROUP_ID}}" \
                && chpasswd < <(echo "${{DEVENV_USERNAME}}:docker") \
                && usermod -aG sudo "${{DEVENV_USERNAME}}" \
                && :

            RUN : \
                && echo "============================================ ADD USER TO SUDOERS ===========================================" \
                && echo "${{DEVENV_USERNAME}} ALL=(ALL) NOPASSWD: ALL" >>/etc/sudoers \
                && echo "${{DEVENV_USERNAME}} ALL=(ALL) NOPASSWD: ALL" >>/etc/sudoers \
                && echo "Defaults:${{DEVENV_USERNAME}} "'!requiretty' >>/etc/sudoers \
                && echo "Defaults:${{DEVENV_USERNAME}} "'!requiretty' >>/etc/sudoers \
                && :

            # hadolint ignore=DL3008,DL3009,SC2016
            RUN : \
                && echo "============================================== INSTALL COMMON TOOLS ========================================" \
                && DEBIAN_FRONTEND=noninteractive apt-get update \
                && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
                && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y software-properties-common neovim krb5-user openssh-server openssh-client \
                && echo -e '#!/usr/bin/env sh\nsudo service ssh start\nsudo service docker start\n"${{@}}"' > "/tmp/entrypoint" \
                && chmod +x "/tmp/entrypoint" \
                && :

            # hadolint ignore=DL3008,DL3009
            RUN : \
                && echo "========================================== INSTALL LATEST PYTHON ==========================================" \
                && DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:deadsnakes/ppa  \
                && DEBIAN_FRONTEND=noninteractive apt-get update  \
                && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y python3.11 python3.11-dev python3.11-venv python3.11-dev \
                && DEBIAN_FRONTEND=noninteractive add-apt-repository --remove ppa:deadsnakes/ppa  \
                && DEBIAN_FRONTEND=noninteractive apt-get update \
                && echo "==================================================== DONE ====================================================" \
                && :

            RUN : \
                && echo "========================================== Docker Install ==========================================" \
                && curl -fsSL https://get.docker.com -o /tmp/get-docker.sh \
                && sh /tmp/get-docker.sh \
                && usermod -aG docker "${{DEVENV_USERNAME}}" \
                && rm /tmp/get-docker.sh \
                && :

            USER "${{DEVENV_USERNAME}}"

            RUN : \
                && echo "====================== INSTALL SDKMAN PIPX ===================" \
                && curl -s "https://get.sdkman.io" -o /tmp/sdkman \
                && bash /tmp/sdkman \
                && rm /tmp/sdkman \
                && python3.11 -m venv /tmp/_venv \
                && /tmp/_venv/bin/pip install --upgrade pip shiv \
                && mkdir -p ${{HOME}}/.local/bin/ \
                && /tmp/_venv/bin/shiv -o ${{HOME}}/.local/bin/dev -c dev comma-cli \
                && /tmp/_venv/bin/shiv -o ${{HOME}}/.local/bin/runtool -c runtool runtool \
                && echo 'export PATH="${{HOME}}/.local/bin:${{PATH}}"' >> ~/.bashrc \
                && rm -rf /tmp/_venv/bin/pipx \
                && :

            WORKDIR /home/"${{DEVENV_USERNAME}}"
            ENTRYPOINT [ "/tmp/entrypoint" ]
            CMD [ "/bin/bash" ]
            """
            ).strip()
            + "\n"
            + self.additional_setup
        )

    def start(self) -> None:
        if not os.path.exists(_DOCKERFILE):
            os.makedirs(os.path.dirname(_DOCKERFILE), exist_ok=True)
            with open(_DOCKERFILE, "w") as f:
                f.write(self.template())
        logging.info("Building docker image based on %s", _DOCKERFILE)
        result = Command(
            cmd=("docker", "build", "--tag", self.image_name, "."),
            input=self.template(),
            capture_output=False,
            check=False,
            label="Building docker image",
            cwd=os.path.dirname(_DOCKERFILE),
        ).run()
        if result.returncode != 0:
            logging.error("Failed to build docker image")
            raise SystemExit(1)
        Command(
            cmd=(
                "docker",
                "run",
                f"-p={self.ssh_port}:22",
                "--privileged",
                "-it",
                "--detach",
                "--rm",
                # '--restart=unless-stopped',
                *(f"-v={volume_pair[0]}:{volume_pair[1]}" for volume_pair in self.volumes),
                *(f"-p={port_pair[0]}:{port_pair[1]}" for port_pair in self.ports),
                *(f"-e={env_pair[0]}={env_pair[1]}" for env_pair in self.envs),
                *self.additional_args,
                "--name",
                self.image_name,
                self.image_name,
            ),
            label="Starting docker container",
            # capture_output=False,
        ).run_with_spinner()

    def stop(self) -> None:
        Command(
            cmd=("docker", "stop", self.image_name),
            label="Stopping docker container",
        ).run_with_spinner()

    def enter(self) -> None:
        Command(
            cmd=("docker", "exec", "-it", self.image_name, "/bin/bash"),
        ).execvp()

    def is_running(self) -> bool:
        return any(
            container["Names"] == self.image_name for container in DOCKER_CLIENT.list_containers()
        )

    def ssh_machine(self) -> SshMachine:
        return SshMachine(hostname="localhost", port=self.ssh_port, user=self.username)

    # region: CLI

    def start_cmd(
        self,
        ports: list[DockerPorts] = typer.Option(  # noqa: B008
            [],
            "-p",
            "--expose",
            help="Publish a container's port(s) to the host. ie -p=8080:9090",
            parser=DockerPorts.parse,
        ),
        volumes: list[DockerVolumes] = typer.Option(  # noqa: B008
            [],
            "-v",
            "--volume",
            help="Bind mount a volume. ie -v=/host:/container",
            parser=DockerVolumes.parse,
        ),
    ) -> None:
        """Start devcon."""
        if self.is_running():
            logging.info("devcon is already running")
            return

        self.ports.extend(ports)
        self.volumes.extend(volumes)

        self.start()

    def stop_cmd(self) -> None:
        """Stop devcon."""
        if not self.is_running():
            logging.info("devcon is not running")
            return
        self.stop()

    def enter_cmd(self) -> None:
        """Enter devcon."""
        if not self.is_running():
            logging.info("devcon is not running")
            return
        DevContainer().enter()

    def ssh_copy_id(self) -> None:
        """Copy ssh public key to docker container."""
        if not self.is_running():
            logging.info("devcon is not running")
            return
        Command(cmd=("ssh-copy-id", "-p", str(self.ssh_port), "localhost")).execvp()

    def ssh(self) -> None:
        """SSH into devcon."""
        if not self.is_running():
            logging.info("devcon is not running")
            return
        self.ssh_machine().create_cmd(()).execvp()

    def template_cmd(self) -> None:
        """Print template for devcon Dockerfile."""
        print(self.template())

    def get_app(self) -> typer.Typer:
        app_devcon: typer.Typer = typer.Typer(
            name="devcon",
            help=dedent(
                f"""
            Development container.
            \b


            To customize container, modify the following file: {_DOCKERFILE}"""
            ),
        )

        app_devcon.command(name="start")(self.start_cmd)
        app_devcon.command(name="stop")(self.stop_cmd)
        app_devcon.command(name="enter")(self.enter_cmd)
        app_devcon.command(name="ssh-copy-id")(self.ssh_copy_id)
        app_devcon.command(name="ssh")(self.ssh)
        app_devcon.command(name="template")(self.template_cmd)

        return app_devcon

    # endregion: CLI


app_devcon = DevContainer(platform="linux/amd64").get_app()

if __name__ == "__main__":
    app_devcon()
