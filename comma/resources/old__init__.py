from __future__ import annotations

from typing import Literal
from typing import Union

from typing_extensions import TypeAlias

from comma.resources import TypedResourceHelper

_CommaRourcesJson: TypeAlias = Literal['main.json']
_CommaRourcesOther: TypeAlias = Union[_CommaRourcesJson, Literal['']]
COMMA_RESOURCE_LOADER = TypedResourceHelper[_CommaRourcesJson, _CommaRourcesOther](__package__)
