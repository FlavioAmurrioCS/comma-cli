from __future__ import annotations

import re
from typing import NamedTuple
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import requests
import typer
from fzf import fzf
from persistent_cache.decorators import persistent_cache
from rich import print

if TYPE_CHECKING:
    from collections.abc import Iterable

INDEX_ROOT = "https://pypi.org/simple/"

app_temp: typer.Typer = typer.Typer(
    name="temp",
    help="temporary commands",
)


@persistent_cache()
def request_url(url: str) -> str:
    response = requests.get(url, timeout=5)
    return response.text


PATTERN_ATAG = re.compile(r'<a .*href="([^"]*?)".*>(.*?)</a>')


class ATag(NamedTuple):
    href: str
    text: str
    tag: str


def extract_links(response: str, domain: str | None = None) -> Iterable[ATag]:
    for find in PATTERN_ATAG.finditer(response):
        href, text = find.groups()
        yield ATag(urljoin(domain, href), text, find.group(0))  # type:ignore[type-var,arg-type]


@app_temp.command()
def list_projects() -> None:
    choice = fzf(
        extract_links(request_url(INDEX_ROOT), domain=INDEX_ROOT),  #
        key=lambda x: x.text,  #
    )
    if choice:
        print(f"https://pypi.org/project/{choice.text}/")
        print(choice.href)
        choice2 = fzf(
            extract_links(request_url(choice.href), domain=choice.href),  #
            key=lambda x: x.text,  #
            _options={"tac": True},
        )
        if choice2:
            print(choice2.href)
            # print(f"{text2} ({href2})")


if __name__ == "__main__":
    app_temp()
