from __future__ import annotations

import logging
import os
from typing import Any
from typing import NamedTuple
from typing import TYPE_CHECKING

import typer
from comma.machine import SshMachine
from fzf import fzf
from persistent_cache.decorators import persistent_cache

if TYPE_CHECKING:
    from requests import Session
    from typing_extensions import Self


class ZeroTierMember(NamedTuple):
    name: str
    # online: bool
    ip_address: str

    @classmethod
    def from_json_items(cls, dct: dict[str, Any]) -> Self:
        return cls(
            name=dct["name"],
            # online=dct['online'],
            ip_address=dct["config"]["ipAssignments"][0],
        )


class ZeroTier:
    __INSTANCE__: ZeroTier | None = None

    def __init__(self) -> None:
        token = os.environ.get("ZERO_TIER_TOKEN", "")
        if not token:
            logging.error("ZERO_TIER_TOKEN is not define in shell")
            raise SystemExit(1)
        import requests

        self.session: Session = requests.Session()
        self.session.headers.update({"Authorization": f"token {token}"})

    @classmethod
    def instance(cls) -> ZeroTier:
        if cls.__INSTANCE__ is None:
            cls.__INSTANCE__ = ZeroTier()
        return cls.__INSTANCE__

    @classmethod
    @persistent_cache(minutes=5)
    def get(cls, url: str) -> Any:  # noqa: ANN401
        return cls.instance().session.get(url).json()

    @classmethod
    def network_ids(cls) -> list[str]:
        return [x["id"] for x in cls.get("https://api.zerotier.com/api/v1/network")]

    @classmethod
    @persistent_cache(minutes=10)
    def members(cls) -> list[ZeroTierMember]:
        network_id = cls.network_ids()[0]
        return [
            ZeroTierMember.from_json_items(x)
            for x in cls.get(f"https://api.zerotier.com/api/v1/network/{network_id}/member")
            if x["config"]["authorized"]
        ]


app_zerotier = typer.Typer(
    name="zt",
    help="ZeroTier",
)


@app_zerotier.command()
def connect() -> None:
    selection = fzf(ZeroTier.members())
    if selection:
        logging.debug(selection)
        machine = SshMachine(hostname=selection.ip_address)
        machine.create_cmd(()).execvp()
