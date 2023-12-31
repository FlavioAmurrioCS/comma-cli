# flake8: noqa: E501
from __future__ import annotations

import itertools
import logging
import os
import re
import sys
import typing
from configparser import ConfigParser
from dataclasses import dataclass
from importlib.resources import path as resource_path
from typing import Callable
from typing import Iterable
from typing import NamedTuple
from typing import Sequence
from typing import TYPE_CHECKING
from typing import TypeVar

import typer
from rich import print as rprint
from rich.console import Console
from typing_extensions import TypedDict


if TYPE_CHECKING:
    from functional.pipeline import Sequence as FunctionalStream
    from _typeshed import FileDescriptorOrPath


LOG_TOOL_CONSOLE = Console(highlight=False, soft_wrap=True)

app_logtool = typer.Typer(
    name="lt",
    help="Log Tool.",
)

_T = TypeVar("_T")


class LogLine(NamedTuple):
    line: str
    parts: dict[str, str]


class LogToolConfig(TypedDict):
    log_pattern: str
    print_format: str
    loglevel: list[str]
    clazz: list[str]
    msg: list[str]


def cast_to_non_none(item: _T | None) -> _T:
    return typing.cast(_T, item)


@dataclass
class LogToolConfigParser:
    config_file: str
    config: ConfigParser

    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        self.config = ConfigParser()
        if os.path.exists(config_file):
            self.config.read(config_file)
        else:
            logging.warning("Config file %s does not exist.", config_file)

    def get(self, section_name: str) -> LogToolConfig:
        if section_name not in self.config.sections():
            msg = f"Section {section_name} does not exist."
            raise KeyError(msg)

        selection = self.config[section_name]

        return {
            "log_pattern": (
                selection["log_pattern"]
                if "log_pattern" in selection
                else r"(?P<TIMESTAMP>^[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}) (?P<LOGLEVEL>[A-Z]+)[ ]*:[\.]+(?P<CLASS>[^:]+): (?P<MSG>.*)"
            ),
            "print_format": (
                selection["print_format"]
                if "print_format" in selection
                else r"[cyan]{TIMESTAMP} [yellow][{LOGLEVEL: ^7}] [red]{CLASS: >22}: [reset]{MSG}"
            ),
            "loglevel": (selection["loglevel"].splitlines() if "loglevel" in selection else ["INFO", "WARN", "ERROR", "FATAL", "CRITICAL"]),
            "clazz": (selection["clazz"].splitlines() if "clazz" in selection else []),
            "msg": (selection["msg"].splitlines() if "msg" in selection else []),
        }

    def sections(self) -> list[str]:
        return self.config.sections()

    def reload(self) -> None:
        self.config.read(self.config_file)


def seq_open_file(file: FileDescriptorOrPath) -> Iterable[str]:
    from functional import seq

    return seq.open(file, errors="ignore", encoding="utf-8") if file not in ("/dev/stdin", "-") else sys.stdin


@dataclass
class LogTool:
    # config_file: str
    log_tool_config: LogToolConfig
    log_pattern: str
    # stream: FunctionalStream[LogLine]  # type:ignore
    # processed_stream: FunctionalStream[LogLine]  # type:ignore
    config_parser: LogToolConfigParser
    section: str
    log_files: list[str]

    def __init__(
        self,
        logs: Sequence[str],
        ini_config: str | None = None,
        section: str | None = None,
    ) -> None:
        if ini_config is None:
            with resource_path(__package__, "log_config.ini") as config_file:
                ini_config = config_file.as_posix()
        self.config_parser = LogToolConfigParser(ini_config)
        self.section = section or self.config_parser.sections()[0]
        self.log_files = list(logs)
        self.log_pattern = ""
        self.reload_config()

    def reload_config(self) -> None:
        from functional import seq

        self.config_parser.reload()
        self.log_tool_config = self.config_parser.get(self.section)
        if self.log_pattern != self.log_tool_config["log_pattern"]:  # Trigger reload
            self.log_pattern = self.log_tool_config["log_pattern"]
            pattern = re.compile(self.log_pattern)

            def line_to_logline(line: str) -> LogLine | None:
                result = pattern.search(line)
                return LogLine(line.rstrip(), result.groupdict()) if result else None

            self.stream = (
                seq(self.log_files)
                .flat_map(seq_open_file)
                .map(line_to_logline)  # type:ignore
                .filter(lambda x: x is not None)  # type:ignore
                .map(cast_to_non_none)  # type:ignore
            )

        # TODO: Conditional Stream when items changes
        self.processed_stream = self.__process__()

    def __process__(self) -> FunctionalStream[LogLine]:  # type:ignore
        predicates: list[Callable[[LogLine], bool]] = []

        loglevels = set(self.log_tool_config["loglevel"])
        if loglevels:
            predicates.append(lambda x: x.parts["LOGLEVEL"] in loglevels)

        classes = set(self.log_tool_config["clazz"])
        if classes:
            predicates.append(lambda x: x.parts["CLASS"] in classes)

        msg_patterns = self.log_tool_config["msg"]
        if msg_patterns:
            pattern = re.compile("|".join(msg_patterns))
            predicates.append(lambda x: bool(pattern.search(x.parts["MSG"])))

        if not predicates:
            return self.stream  # type:ignore

        return self.stream.filter(lambda x: any(p(x) for p in predicates))  # type:ignore

    def print_log(self, original_stream: bool = False) -> None:
        stream = self.stream if original_stream else self.processed_stream
        print_format: str = self.log_tool_config["print_format"]
        if not print_format:

            def func(log_line: LogLine) -> str:
                return log_line.line
        else:

            def func(log_line: LogLine) -> str:
                return print_format.format_map(log_line.parts)

        stream.map(func).for_each(rprint)  # type:ignore


@app_logtool.command()
def pretty_search(
    ini_config: str | None = None,
    files: list[str] = typer.Option(
        [],
        "--file",
        "-f",
        help="Files to search.",
    ),
    # interactive: bool = typer.Option(False, '--interactive', help='Prompt for file edit'),
) -> None:
    """
    Use config file to search thru files.
    """
    log_tool = LogTool(
        ini_config=ini_config,
        logs=(files or ["/dev/stdin"]),
    )
    rprint(log_tool)
    log_tool.print_log()


@app_logtool.command()
def search(
    search_patterns: list[str],
    ignore_case: bool = typer.Option(
        False,
        "--ignore-case",
        "-i",
        help="Perform case insensitive matching.",
    ),
    enable_regex: bool = typer.Option(False, "--regex", "-E", help="Enable Regex."),
    files: list[str] = typer.Option(["/dev/stdin"], "--file", "-f", help="Files to search."),
    ignore_patterns: list[str] = typer.Option([], "-v", help="Specify ignore pattern"),
) -> None:
    """Search and color text files"""
    from functional import seq

    stream: FunctionalStream[str] = (  # type:ignore
        seq(files).flat_map(seq_open_file)
    )
    search_patterns.sort(key=len, reverse=True)
    if not enable_regex:
        search_patterns = [re.escape(x) for x in search_patterns]
    flag = re.IGNORECASE if ignore_case else 0
    joined_search_pattern: str = "|".join(search_patterns)
    pat = re.compile(joined_search_pattern, flag)

    stream = stream.filter(lambda x: bool(pat.search(x))).map(str.strip)  # type:ignore

    if ignore_patterns:
        ignore_patterns.sort(key=len, reverse=True)
        ignore_pat = re.compile("|".join(ignore_patterns), flag)
        stream = stream.filter_not(lambda x: bool(ignore_pat.search(x)))  # type:ignore

    colors = (
        # "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        # "white",
        # "bright_black",
        "bright_red",
        "bright_green",
        "bright_yellow",
        "bright_blue",
        "bright_magenta",
        "bright_cyan",
        # "bright_white",
    )

    patterns_and_colors: list[tuple[re.Pattern[str], str]] = [
        (
            re.compile(f"({pattern})", flag),
            rf"[bold underline {color}]\1[/bold underline {color}]",
        )
        for pattern, color in zip(search_patterns, itertools.cycle(colors))
    ]

    def __inner__(line: str) -> str:
        for pat, color in patterns_and_colors:
            line = pat.sub(color, line)
        return line

    stream.map(__inner__).for_each(LOG_TOOL_CONSOLE.print)  # type:ignore


if __name__ == "__main__":
    app_logtool()
    # pretty_search(None, ['log.log2'])
