from __future__ import annotations

from typing import Optional

import typer

from comma.cli.m_git import GitWorktree
from comma.utils.fzf import fzf

app_wt: typer.Typer = typer.Typer(name='wt')


@app_wt.command()
def clone(repository: str) -> None:
    """
    Clone project in ~/worktrees.
    """
    g = GitWorktree(repository=repository)
    g.clone()
    print(g.home)


@app_wt.command()
def add(branch_name: str) -> None:
    """
    Create new worktree.
    """
    g = GitWorktree.from_dir()
    g.add(branch_name)


@app_wt.command()
def ls() -> None:
    """
    List worktrees.
    """
    g = GitWorktree.from_dir()
    for line in g.list():
        print(line)


@app_wt.command()
def remove(worktree: Optional[str] = None) -> None:
    """
    Remove worktree.
    """
    g = GitWorktree.from_dir()

    worktree = worktree or fzf(g.list())
    if not worktree:
        return
    g.remove(worktree)


if __name__ == '__main__':
    app_wt()