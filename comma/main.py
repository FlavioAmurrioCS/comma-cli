from __future__ import annotations

import typer

from comma.api.server import server
from comma.cli.code import c
from comma.cli.code import rc
from comma.cli.docker import app_docker
from comma.cli.log_tool import app_logtool as app_logtool
from comma.cli.runtool2 import __run_which__ as run_which
from comma.cli.runtool2 import main as run
from comma.cli.shell_utils import app_sh
from comma.cli.tmux import mux
from comma.cli.tmux import rmux
from comma.cli.wt import app_wt
from comma.cli.zero_tier import app_zerotier
from comma.utils.typer_utils import typer_command_wrap

app_main: typer.Typer = typer.Typer(help='Set of tools made with flavor.')
app_main.command()(c)
app_main.command()(rc)
app_main.command()(mux)
app_main.command()(rmux)
app_main.add_typer(app_docker)
typer_command_wrap(app=app_main, func=run, name='run')
typer_command_wrap(app=app_main, func=run_which, name='run-which')
app_main.add_typer(app_logtool)
app_main.add_typer(app_zerotier)
app_main.add_typer(app_wt)
app_main.add_typer(app_sh)

app_main.command()(server)


if __name__ == '__main__':
    app_main()
