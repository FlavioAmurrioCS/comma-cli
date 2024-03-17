from __future__ import annotations

import logging
import subprocess
from typing import TYPE_CHECKING

import pytest
import tomlkit

if TYPE_CHECKING:
    from collections.abc import Generator


def entrypoints() -> Generator[tuple[str, str], None, None]:
    with open("pyproject.toml", "rb") as f:
        pyproject = tomlkit.load(f)
    yield from pyproject["project"]["scripts"].items()


@pytest.mark.parametrize("pair", entrypoints())
def test_help(pair: tuple[str, str]) -> None:
    k, v = pair
    result = subprocess.run([k, "--help"], check=False, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        logging.error(result.stderr)
        msg = f"Error running {k} --help"
        raise AssertionError(msg)
    # print(k, v)
