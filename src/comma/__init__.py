from __future__ import annotations

import logging
import os

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
        level="INFO",
        format="[%(asctime)s] [%(levelname)-7s] [%(module)s] %(filename)s:%(lineno)d %(message)s",
        datefmt="%X",
    )
