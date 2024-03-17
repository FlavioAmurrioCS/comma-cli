from __future__ import annotations

import os
from typing import TYPE_CHECKING

from comma.command import Command
from comma.machine import Machine

if TYPE_CHECKING:
    from collections.abc import Sequence


_ssh_options = (
    "-oCompression=yes",
    "-oControlMaster=auto",
    "-oControlPersist=yes",
    "-oForwardAgent=yes",
    "-oGSSAPIAuthentication=yes",
    "-oGSSAPIDelegateCredentials=yes",
    "-oKeepAlive=yes",
    "-oLogLevel=FATAL",
    "-oServerAliveCountMax=6",
    "-oServerAliveInterval=15",
    "-oStrictHostKeyChecking=no",
    "-oUserKnownHostsFile=/dev/null",
    "-oControlPath=/tmp/%r@%h:%p",
)

# function ssh() { command ssh -tq "${__quick_ssh_options[@]}" "${@}"; }
# function ssh_new() { command ssh -tq "${__default_ssh_options[@]}" "${@}"; }


class SshMachine(Machine):
    ssh_command: Sequence[str]

    def __init__(
        self,
        hostname: str = os.environ.get("REMOTE_MACHINE", "vdi"),
        user: str | None = None,
        port: int | None = None,
    ) -> None:
        _ssh_command = [
            "ssh",
            *_ssh_options,
            "-tq",
        ]
        if port is not None:
            _ssh_command.extend(("-p", f"{port}"))

        _ssh_command.append(hostname if not user else f"{user}@{hostname}")
        self.ssh_command = tuple(_ssh_command)

    def create_cmd(self, cmd: Sequence[str]) -> Command:
        return Command(cmd=(*self.ssh_command, *cmd))

    def code_open(self, path: str) -> None:
        full_path = self.full_path(path)
        cmd = ["code"]
        if self.is_dir(full_path):
            cmd.append("--folder-uri")
        else:
            cmd.append("--file-uri")
        cmd.append(
            f"vscode-remote://ssh-remote+{self.ssh_command[-1]}{full_path}",
        )

        Command(cmd=cmd).execvp()
