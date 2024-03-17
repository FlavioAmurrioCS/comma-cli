from __future__ import annotations

import logging
import os
import shlex
import shutil
import subprocess
from typing import NamedTuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


class Command(NamedTuple):
    cmd: list[str] | tuple[str, ...]
    label: str = ""
    text: bool = True
    check: bool = False
    cwd: str | None = None
    capture_output: bool = True
    input: str | None = None
    timeout: float | None = None
    env: Mapping[str, str] | None = None
    additional_env: Mapping[str, str] | None = None

    def run(self) -> subprocess.CompletedProcess[str]:
        self._exec_check()
        logging.debug(self)
        try:
            return subprocess.run(
                self.cmd,  # noqa: S603
                errors="ignore",
                encoding="utf-8",
                text=self.text,
                check=self.check,
                cwd=self.cwd,
                capture_output=self.capture_output,
                input=self.input,
                timeout=self.timeout,
                env=self.resolved_env,
            )
        except subprocess.CalledProcessError as e:
            logging.exception(e.stderr)
            raise

    @property
    def resolved_env(self) -> Mapping[str, str] | None:
        return (
            self.env
            if not self.additional_env
            else {**(self.env or os.environ), **self.additional_env}
        )

    def quick_run(self) -> str:
        return self.run().stdout.strip()

    def execvp(self, *, log_command: bool = True) -> None:
        import sys

        if "pytest" in sys.modules:
            self.run()
            return
        if self.resolved_env:
            for key, value in self.resolved_env.items():
                os.environ[key] = value
        if self.cwd:
            os.chdir(self.cwd)
        if log_command:
            logging.info(self)
        self._exec_check()
        os.execvp(self.cmd[0], self.cmd)  # noqa: S606

    def _exec_check(self) -> None:
        executable = self.cmd[0]
        if shutil.which(executable) is not None:
            return
        if not os.path.exists(executable):
            logging.warning("Executable does not exist: %s", executable)
        elif not os.access(executable, os.X_OK):
            logging.warning("File is not executable: %s", executable)

    def __repr__(self) -> str:
        """Return a string representation of the Command object."""
        return " ".join(map(shlex.quote, self.cmd))

    def run_with_spinner(self) -> subprocess.CompletedProcess[str]:
        from comma.rich.halo import FHalo

        with FHalo(status=self.label or repr(self)) as halo:
            try:
                result = self.run()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise
            if result.returncode == 0:
                halo.succeed()
            else:
                halo.fail()
            return result
