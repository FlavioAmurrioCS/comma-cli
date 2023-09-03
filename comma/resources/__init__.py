from __future__ import annotations

from typing import Literal
from typing import TypeAlias

from comma.utils.resources import TypedResourceHelper

_CommaRourcesJson: TypeAlias = Literal['main.json']
_CommaRourcesYaml: TypeAlias = Literal['config.yaml']
_CommaRourcesOther: TypeAlias = _CommaRourcesJson | _CommaRourcesYaml | Literal['']
COMMA_RESOURCE_LOADER = TypedResourceHelper[_CommaRourcesJson, _CommaRourcesYaml, _CommaRourcesOther]('comma.resources')

COMMA_RESOURCE_LOADER.get_resource('main.json')
