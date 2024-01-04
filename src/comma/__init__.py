from __future__ import annotations


try:
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)
except (ImportError, LookupError):
    try:
        from comma._version import (  # type: ignore[no-redef,unused-ignore] # noqa: F401
            __version__,  #
        )
    except ModuleNotFoundError:
        msg = "comma-cli is not correctly installed. Please install it with pip."
        raise RuntimeError(msg)  # noqa: B904, TRY200

import logging

from rich.logging import RichHandler

logging.basicConfig(
    level="DEBUG",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
