#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

import typer
from comma.devcon import app_devcon
from comma.docker import app_docker
from comma.logtool import app_logtool
from comma.misc.code import c
from comma.misc.tmux import mux
from comma.shell_scripts.shell_utils import app_sh
from comma.typer.reflection import app_reflection
# from runtool.runtool_cli import run


app_main: typer.Typer = typer.Typer(help="Set of tools made with flavor.")
app_main.command()(c)
app_main.command()(mux)
app_main.add_typer(app_docker)
app_main.add_typer(app_logtool)
app_main.add_typer(app_devcon)
app_main.add_typer(app_reflection)

app_main.add_typer(app_sh)

if os.environ.get("USER", "").upper() in ("FLAVIO", "FMM597", "TASHA"):
    from comma._personal.zero_tier import app_zerotier

    app_main.add_typer(app_zerotier)

    from comma.misc.wt import app_wt

    app_main.add_typer(app_wt)

    from comma.misc.code import rc

    app_main.command()(rc)

    from comma.misc.tmux import rmux

    app_main.command()(rmux)

    if {"fastapi", "uvicorn"}.issubset(sys.modules.keys()):
        from comma._personal.server import server

        app_main.command()(server)

############

# app_main.command(
#     add_help_option=False,
#     no_args_is_help=True,
#     context_settings={
#         'allow_extra_args': True,
#         'ignore_unknown_options': True,
#     },
# )(run)


if __name__ == "__main__":
    app_main()
