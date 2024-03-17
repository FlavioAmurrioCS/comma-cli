from __future__ import annotations

import itertools
import logging
import os
from dataclasses import dataclass
from functools import cached_property
from typing import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from collections.abc import Generator
    from typing_extensions import Self

from comma.command import Command
from comma.misc.file_utils import find_up_dir


def chunk_split(
    lines: Sequence[str], predicate: Callable[[str], bool] | None = None
) -> Generator[list[str], None, None]:
    predicate = predicate or (lambda x: not x.strip())
    buffer: list[str] = []
    for line in lines:
        line.rstrip()
        if predicate(line) and buffer:
            yield buffer
            buffer = []
        if line.strip():
            buffer.append(line)
    if buffer:
        yield buffer


@dataclass
class Git:
    PROJECTS_DIR = os.path.expanduser("~/projects")
    WORKTREES_DIR = os.path.expanduser("~/worktrees")
    _repository: str | None
    home: str
    is_bare: bool

    def __init__(
        self,
        *,
        repository: str | None = None,
        home: str | None = None,
        is_bare: bool = False,
    ) -> None:
        if not repository and not home:
            logging.error("Either repository or home must be provided.")
            raise SystemExit(1)
        self._repository = repository
        self.is_bare = is_bare
        self.home = home or os.path.join(
            Git.WORKTREES_DIR if self.is_bare else Git.PROJECTS_DIR,
            os.path.basename(repository or ""),
        )

    def _git_cmd(self, *args: str) -> Command:
        if not os.path.exists(self.home):
            self.clone()
        return Command(cmd=("git", "-C", self.home, *args), check=True)

    @cached_property
    def repository(self) -> str:
        return self._repository or self._git_cmd("config", "--get", "remote.origin.url").quick_run()

    @cached_property
    def branch(self) -> str:
        return self._git_cmd("rev-parse", "--abbrev-ref", "HEAD").quick_run()

    @cached_property
    def dirty_files(self) -> list[str]:
        return [x[3:] for x in self._git_cmd("status", "--porcelain").quick_run().splitlines()]

    @cached_property
    def is_dirty(self) -> bool:
        return bool(self.dirty_files)

    @cached_property
    def branches(self) -> list[str]:
        branches = []
        for branch in self._git_cmd("branch", "--all").quick_run().splitlines():
            parsed_branch = branch.split("origin/")[-1].strip()
            if not parsed_branch.startswith("*"):
                branches.append(parsed_branch)
        return branches

    def checkout(self, branch: str) -> None:
        self._git_cmd("checkout", branch).run()

    def clone(self) -> None:
        if os.path.exists(self.home):
            logging.error("Repository already cloned.")
            raise SystemExit(1)
        Command(
            cmd=(
                "git",
                "clone",
                ("--bare" if self.is_bare else "--recursive"),
                self.repository,
                self.home,
            ),
            check=True,
        ).run_with_spinner()

    def pull(self) -> None:
        self._git_cmd("pull").run_with_spinner()

    def push(self) -> None:
        self._git_cmd("push").run_with_spinner()

    @classmethod
    def from_dir(cls, directory: str | None = None) -> Self:
        directory = directory or os.getcwd()
        git_home = find_up_dir(
            predicate=lambda p: os.path.isdir(os.path.join(p, ".git")), start_dir=directory
        ) or find_up_dir(
            predicate=lambda p: os.path.isfile(os.path.join(p, "packed-refs")),
            start_dir=directory,
        )
        if not git_home:
            logging.error("No git repository found.")
            raise SystemExit(1)
        return cls(home=git_home)


class GitWorktree(Git):
    def __init__(self, *, repository: str | None = None, home: str | None = None) -> None:
        super().__init__(repository=repository, home=home, is_bare=True)

    def _git_cmd(self, *args: str) -> Command:
        return super()._git_cmd(*args)._replace(cwd=self.home)

    def add(self, branch_name: str, commit: str | None = None) -> None:
        self._git_cmd(
            "worktree",
            "add",
            "-b",
            branch_name,
            branch_name,
            (commit or self.branch),
        ).execvp()

    def remove(self, branch_name: str) -> None:
        self._git_cmd("worktree", "remove", branch_name).run()

    def list_wt(self) -> list[str]:
        ret: list[str] = []
        for chunk in itertools.islice(
            chunk_split(self._git_cmd("worktree", "list", "--porcelain").quick_run().splitlines()),
            1,
            None,
        ):
            a = dict(k.split() for k in chunk)
            ret.append(a["worktree"])
        return ret
