from __future__ import annotations

import os

try:
    from comma._version import (  # type: ignore[no-redef,unused-ignore]
        __version__,  #
    )
except ModuleNotFoundError:
    try:
        from setuptools_scm import get_version

        __version__ = get_version(root="..", relative_to=__file__)
    except (ImportError, LookupError):
        msg = "comma-cli is not correctly installed. Please install it with pip."
        raise RuntimeError(msg)  # noqa: B904, TRY200


import logging

if os.getenv("ENABLE_RICH_LOGGING"):
    from rich.logging import RichHandler

    logging.basicConfig(
        level="DEBUG",
        datefmt="[%X]",
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=False)],
    )
else:
    logging.basicConfig(
        level="DEBUG",
        format="[%(asctime)s] [%(levelname)-7s] [%(module)s] %(filename)s:%(lineno)d %(message)s",
        datefmt="%X",
    )
