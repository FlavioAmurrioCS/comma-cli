from __future__ import annotations

import sys

from comma.command import Command


def lazy_install(packages: list[str]) -> None:
    if packages:
        Command(cmd=(sys.executable, "-m", "pip", "install", *packages)).run_with_spinner()
