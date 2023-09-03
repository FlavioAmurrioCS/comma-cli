from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from dataclasses import field
from textwrap import dedent
from typing import List
from typing import NamedTuple

import typer
from typing_extensions import Literal

from comma.cli.docker import list_containers
from comma.comma_config import comma_utils
from comma.utils.command import Command
from comma.utils.machine.ssh_machine import SshMachine
from comma.utils.persistent_cache import sqlite_cache

_DOCKERFILE = os.path.join(comma_utils.opt_dir, 'devcon', 'Dockerfile')

app_devcon: typer.Typer = typer.Typer(
    name='devcon',
    help=dedent(f'''
            Development container.
            \b


            To customize container, modify the following file: {_DOCKERFILE}'''),
)


@sqlite_cache(days=7)
def user_info() -> dict[Literal['group_id', 'user_id', 'username'], str]:
    return {
        'group_id': Command(('id', '-g')).quick_run(),
        'user_id': Command(('id', '-u')).quick_run(),
        'username': os.environ['USER'],
    }


@dataclass
class DevContainer:
    base_image: str = 'ubuntu:jammy'
    _group_id: str | None = None
    _user_id: str | None = None
    _username: str | None = None
    image_name: str = 'devcon'
    ssh_port: int = 2222
    volumes: List[tuple[str, str]] = field(default_factory=list)
    ports: List[tuple[int, int]] = field(default_factory=list)
    envs: List[tuple[str, str]] = field(default_factory=list)
    additional_args: List[str] = field(default_factory=list)

    @property
    def group_id(self) -> str:
        self._group_id = self._group_id or user_info()['group_id']
        return self._group_id

    @property
    def user_id(self) -> str:
        self._user_id = self._user_id or user_info()['user_id']
        return self._user_id

    @property
    def username(self) -> str:
        self._username = self._username or user_info()['username']
        return self._username

    def template(self) -> str:
        return dedent(rf'''
            FROM {self.base_image}
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
                && /tmp/_venv/bin/pip install --upgrade pip pipx \
                && /tmp/_venv/bin/pipx install pipx \
                && /tmp/_venv/bin/pipx install git+https://github.com/FlavioAmurrioCS/comma.git \
                && echo 'export PATH="${{HOME}}/.local/bin:${{PATH}}"' >> ~/.bashrc \
                && rm -rf /tmp/_venv/bin/pipx \
                && :

            WORKDIR /home/"${{DEVENV_USERNAME}}"
            ENTRYPOINT [ "/tmp/entrypoint" ]
            CMD [ "/bin/bash" ]
            ''').strip()

    def start(self) -> None:
        if not os.path.exists(_DOCKERFILE):
            os.makedirs(os.path.dirname(_DOCKERFILE), exist_ok=True)
            with open(_DOCKERFILE, 'w') as f:
                f.write(self.template())
        logging.info('Building docker image based on %s', _DOCKERFILE)
        Command(
            cmd=('docker', 'build', '--tag', self.image_name, '.'),
            input=self.template(),
            capture_output=True,
            check=True,
            label='Building docker image',
            cwd=os.path.dirname(_DOCKERFILE),
        ).run_with_spinner()
        Command(
            cmd=(
                'docker', 'run',
                f'-p={self.ssh_port}:22',
                '--privileged',
                '-it',
                '--detach',
                '--rm',
                # '--restart=unless-stopped',
                *(f'-v={volume_pair[0]}:{volume_pair[1]}' for volume_pair in self.volumes),
                *(f'-p={port_pair[0]}:{port_pair[1]}' for port_pair in self.ports),
                *(f'-e={env_pair[0]}={env_pair[1]}' for env_pair in self.envs),
                *self.additional_args,
                '--name', self.image_name,
                self.image_name,
            ),
            label='Starting docker container',
            # capture_output=False,
        ).run_with_spinner()

    def stop(self) -> None:
        Command(
            cmd=('docker', 'stop', self.image_name),
            label='Stopping docker container',
        ).run_with_spinner()

    def enter(self) -> None:
        Command(
            cmd=('docker', 'exec', '-it', self.image_name, '/bin/bash'),
        ).execvp()

    def is_running(self) -> bool:
        for container in list_containers():
            if container['Names'] == self.image_name:
                return True
        return False

    def sshMachine(self) -> SshMachine:
        return SshMachine(hostname='localhost', port=self.ssh_port, user=self.username)


_devcon = DevContainer()


class DockerPorts(NamedTuple):
    host: int
    container: int

    def __str__(self) -> str:
        return f'{self.host}:{self.container}'

    @classmethod
    def parse(cls, s: str) -> DockerPorts:
        host, container = map(int, s.split(':'))
        return cls(host, container)


class DockerVolumes(NamedTuple):
    host: str
    container: str

    def __str__(self) -> str:
        return f'{self.host}:{self.container}'

    @classmethod
    def parse(cls, s: str) -> DockerVolumes:
        host, container = s.split(':')
        return cls(host, container)


@app_devcon.command()
def start(
    ports: List[DockerPorts] = typer.Option(
        [], '-p', '--expose',
        help="Publish a container's port(s) to the host. ie -p=8080:9090",
        parser=DockerPorts.parse,
    ),
    volumes: List[DockerVolumes] = typer.Option(
        [], '-v', '--volume',
        help='Bind mount a volume. ie -v=/host:/container',
        parser=DockerVolumes.parse,
    ),
) -> None:
    """
    Start devcon.
    """
    if _devcon.is_running():
        logging.info('devcon is already running')
        return

    _devcon.ports.extend(ports)
    _devcon.volumes.extend(volumes)

    _devcon.start()


@app_devcon.command()
def stop() -> None:
    """
    Stop devcon.
    """
    if not _devcon.is_running():
        logging.info('devcon is not running')
        return
    _devcon.stop()


@app_devcon.command()
def enter() -> None:
    """
    Enter devcon.
    """
    if not _devcon.is_running():
        logging.info('devcon is not running')
        return
    DevContainer().enter()


@app_devcon.command()
def ssh_copy_id() -> None:
    """
    Copy ssh public key to docker container.
    """
    if not _devcon.is_running():
        logging.info('devcon is not running')
        return
    Command(cmd=('ssh-copy-id', '-p', str(_devcon.ssh_port), 'localhost')).execvp()


@app_devcon.command()
def ssh() -> None:
    """
    SSH into devcon.
    """
    if not _devcon.is_running():
        logging.info('devcon is not running')
        return
    _devcon.sshMachine().create_cmd(()).execvp()


@app_devcon.command()
def template() -> None:
    """
    Print template for devcon Dockerfile.
    """
    print(_devcon.template())


if __name__ == '__main__':
    app_devcon()
