from __future__ import annotations

from typing import Optional

import typer
from comma.misc.m_git import GitWorktree
from fzf import fzf

app_wt: typer.Typer = typer.Typer(
    name="wt",
    help="Git worktree utilities.",
)


@app_wt.command()
def clone(repository: str) -> None:
    """Clone project in ~/worktrees."""
    g = GitWorktree(repository=repository)
    g.clone()
    print(g.home)


@app_wt.command()
def add(branch_name: str) -> None:
    """Create new worktree."""
    g = GitWorktree.from_dir()
    g.add(branch_name)


@app_wt.command()
def ls() -> None:
    """List worktrees."""
    g = GitWorktree.from_dir()
    for line in g.list_wt():
        print(line)


@app_wt.command()
def remove(worktree: Optional[str] = None) -> None:  # noqa: UP007
    """Remove worktree."""
    g = GitWorktree.from_dir()

    worktree = worktree or fzf(g.list_wt())
    if not worktree:
        return
    g.remove(worktree)


if __name__ == "__main__":
    app_wt()
