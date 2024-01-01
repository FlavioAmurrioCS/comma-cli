from __future__ import annotations

import importlib.resources
import logging
import os

import typer

app_shell_scripts = typer.Typer()


# @sqlite_cache(minutes=5)
# def script_dir() -> str:
#     return str(importlib.resources.files(__package__))


def get_tool(tool: str) -> str:
    with importlib.resources.as_file(
        importlib.resources.files(__package__).joinpath(tool)
    ) as tool_path:
        return tool_path.as_posix()


# @sqlite_cache(minutes=1)
# def _tools() -> List[str]:
#     # (resource.name for resource in importlib.resources.files(__package__).iterdir() if resource.is_file())  # noqa: E501
#     return [
#         x
#         for x in os.listdir(script_dir())
#         if os.path.isfile(x) and os.access(x, os.X_OK) and not x.endswith('.py')
#     ]

__TOOLS__ = ("dev.sh",)  # Tool list should be generated from the files in the package


@app_shell_scripts.command(
    add_help_option=False,
    no_args_is_help=True,
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
)
def sh(
    ctx: typer.Context,
    tool: str = typer.Argument(
        "dev.sh",
        autocompletion=lambda: __TOOLS__,
        help=f'{" ".join(__TOOLS__)}',
    ),
    which: bool = typer.Option(False, "--which", help="Print the command instead of running it."),  # noqa: FBT001, FBT003
) -> int:
    """Installs (if needed) and runs a tool."""
    tool_path = get_tool(tool)

    if not os.path.exists(tool_path):
        if tool == "--help":
            print(ctx.get_help())
        else:
            logging.error("No tool named: %s", tool)
        return 1
    if which:
        print(tool_path)
        return 0
    cmd = (tool_path, *ctx.args)
    os.execvp(cmd[0], cmd)  # noqa: S606
    return None


if __name__ == "__main__":
    app_shell_scripts()
