from __future__ import annotations

import itertools
import re
import typing
import warnings
from typing import Callable
from typing import List
from typing import NamedTuple
from typing import Sequence
from typing import Set
from typing import TYPE_CHECKING
from typing import TypeVar

import typer
from functional import seq
from rich import print as rprint
from rich.console import Console
from ruamel import yaml
from ruamel.yaml.error import UnsafeLoaderWarning
from typing_extensions import TypedDict
warnings.simplefilter('ignore', UnsafeLoaderWarning)

if TYPE_CHECKING:
    from functional.pipeline import Sequence as FunctionalStream


LOG_TOOL_CONSOLE = Console(highlight=False, soft_wrap=True)

app_logtool = typer.Typer(
    name='lt',
    help='Log Tool.',
)

_T = TypeVar('_T')


class LogLine(NamedTuple):
    line: str
    parts: dict[str, str]


class LogToolConfig(TypedDict):
    log_pattern: str
    print_format: str
    MSG: List[str]


def cast_to_non_none(item: _T | None) -> _T:
    return typing.cast(_T, item)


class LogTool():
    config_file: str
    log_tool_config: LogToolConfig
    log_pattern: str
    log_files: Sequence[str]
    stream: FunctionalStream[LogLine]
    processed_stream: FunctionalStream[LogLine]

    def __init__(self, log_tool_config_file: str, logs: Sequence[str]) -> None:
        self.config_file = log_tool_config_file
        self.log_files = [('/dev/stdin' if file == '-' else file) for file in logs]
        self.log_pattern = ''
        self.reload_config()

    def reload_config(self) -> None:
        with open(self.config_file, 'rb') as f:
            self.log_tool_config = yaml.load(f)
            # typing.cast(LogToolConfig, tomli.load(f))
        log_pattern = self.log_tool_config['log_pattern']
        if self.log_pattern != log_pattern:
            self.log_pattern = log_pattern
            pattern = re.compile(self.log_pattern)

            def line_to_logline(line: str) -> LogLine | None:
                result = pattern.search(line)
                return LogLine(line.rstrip(), result.groupdict()) if result else None

            self.stream = (
                seq(self.log_files)
                .flat_map(lambda file: seq.open(file, errors='ignore', encoding='utf-8'))
                .map(line_to_logline)
                .filter(lambda x: x is not None)
                .map(cast_to_non_none)
            )

        # TODO: Conditional Stream when items changes
        self.processed_stream = self.__process__()

    def __process__(self) -> FunctionalStream[LogLine]:
        predicates: list[Callable[[LogLine], bool]] = []
        loglevels: Set[str] = set(*self.log_tool_config.get('LOGLEVEL', []))
        if loglevels:
            predicates.append(lambda x: x.parts['LOGLEVEL'] in loglevels)

        classes: Set[str] = set(*self.log_tool_config.get('CLASS', []))
        if classes:
            predicates.append(lambda x: x.parts['CLASS'] in classes)

        msg_patterns: List[str] = self.log_tool_config.get('MSG', [])
        if msg_patterns:
            pattern = re.compile('|'.join(msg_patterns))
            predicates.append(lambda x: bool(pattern.search(x.parts['MSG'])))

        if not predicates:
            return self.stream

        return self.stream.filter(lambda x: any(p(x) for p in predicates))

    def print(self, original_stream: bool = False) -> None:
        stream = self.stream if original_stream else self.processed_stream
        print_format: str = self.log_tool_config.get('print_format', '')
        if print_format is None:
            def func(log_line: LogLine) -> str:
                return log_line.line
        elif print_format is not None:
            def func(log_line: LogLine) -> str:
                return print_format.format_map(log_line.parts)

        stream.map(func).for_each(rprint)


@app_logtool.command()
def pretty_search(
    config_yaml: str,
    files: List[str] = typer.Option([], '--file', '-f', help='Files to search.'),
    # interactive: bool = typer.Option(False, '--interactive', help='Prompt for file edit'),
) -> None:
    """
    Use config file to search thru files.
    """
    log_tool = LogTool(log_tool_config_file=config_yaml, logs=(files or ['/dev/stdin']))
    log_tool.print()


@app_logtool.command()
def search(
    search_patterns: List[str],
    ignore_case: bool = typer.Option(False, '--ignore-case', '-i', help='Perform case insensitive matching.'),
    enable_regex: bool = typer.Option(False, '--regex', '-E', help='Enable Regex.'),
    files: List[str] = typer.Option(['/dev/stdin'], '--file', '-f', help='Files to search.'),
    ignore_patterns: List[str] = typer.Option([], '-v', help='Specify ignore pattern'),
) -> None:
    """Search and color text files"""
    files = [('/dev/stdin' if file == '-' else file) for file in files]
    stream: FunctionalStream[str] = (
        seq(files)
        .flat_map(
            lambda file: seq.open(file, errors='ignore', encoding='utf-8'),
        )
    )
    search_patterns.sort(key=len, reverse=True)
    if not enable_regex:
        search_patterns = [re.escape(x) for x in search_patterns]
    flag = re.IGNORECASE if ignore_case else 0
    joined_search_pattern: str = '|'.join(search_patterns)
    pat = re.compile(joined_search_pattern, flag)

    stream = stream.filter(lambda x: bool(pat.search(x))).map(str.strip)

    if ignore_patterns:
        ignore_patterns.sort(key=len, reverse=True)
        ignore_pat = re.compile('|'.join(ignore_patterns), flag)
        stream = stream.filter_not(lambda x: bool(ignore_pat.search(x)))

    colors = (
        # "black",
        'red',
        'green',
        'yellow',
        'blue',
        'magenta',
        'cyan',
        # "white",
        # "bright_black",
        'bright_red',
        'bright_green',
        'bright_yellow',
        'bright_blue',
        'bright_magenta',
        'bright_cyan',
        # "bright_white",
    )

    patterns_and_colors: list[tuple[re.Pattern[str], str]] = [
        (re.compile(f'({pattern})', flag), rf'[bold underline {color}]\1[/bold underline {color}]')
        for pattern, color in zip(search_patterns, itertools.cycle(colors))
    ]

    def __inner__(line: str) -> str:
        for pat, color in patterns_and_colors:
            line = pat.sub(color, line)
        return line

    stream.map(__inner__).for_each(LOG_TOOL_CONSOLE.print)


if __name__ == '__main__':
    app_logtool()
