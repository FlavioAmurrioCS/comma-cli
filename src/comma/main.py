#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

import typer
from comma.devcon import app_devcon
from comma.docker import app_docker
from comma.misc.tmux import mux
from comma.typer.reflection import TyperReflection


app_main: typer.Typer = typer.Typer(
    help="Set of tools made with flavor.", pretty_exceptions_show_locals=False
)
app_main.command()(mux)
app_main.add_typer(app_docker)
app_main.add_typer(app_devcon)
app_main.add_typer(TyperReflection(app=app_main).get_app())


if os.environ.get("USER", "").upper() in ("FLAVIO", "FMM597", "TASHA"):
    panel_name = "Secret Commands"
    from comma._personal.zero_tier import app_zerotier

    app_main.add_typer(app_zerotier, rich_help_panel=panel_name)

    from comma.misc.wt import app_wt

    app_main.add_typer(app_wt, rich_help_panel=panel_name)

    from comma.misc.code import rc

    app_main.command(rich_help_panel=panel_name)(rc)

    from comma.misc.tmux import rmux

    app_main.command(rich_help_panel=panel_name)(rmux)

    from comma.misc.code import c

    app_main.command(rich_help_panel=panel_name)(c)

    from comma.shell_scripts.shell_utils import app_sh

    app_main.add_typer(app_sh, rich_help_panel=panel_name)

    if {"fastapi", "uvicorn"}.issubset(sys.modules.keys()):
        from comma._personal.server import server

        app_main.command(rich_help_panel=panel_name)(server)

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
