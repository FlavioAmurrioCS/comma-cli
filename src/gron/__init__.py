#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Any
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Sequence
from typing import Union

from typing_extensions import TypeAlias


JSON_TYPE: TypeAlias = Union[str, int, float, bool, None, List[Any], Dict[str, Any]]


def _gron_helper(obj: JSON_TYPE, path: str = "json") -> Generator[tuple[str, str], None, None]:
    if isinstance(obj, dict):
        yield path, "{}"
        for key, value in obj.items():
            key = f".{key}" if key.isalnum() else f'["{key}"]'
            yield from _gron_helper(value, f"{path}{key}")
    elif isinstance(obj, list):
        yield path, "[]"
        for i, value in enumerate(obj):
            yield from _gron_helper(value, f"{path}[{i}]")
    elif isinstance(obj, bool):
        yield path, "true" if obj else "false"
    elif obj is None:
        yield path, "null"
    elif isinstance(obj, str):
        yield path, f'"{obj}"'
    else:
        yield path, str(obj)


def gron(obj: JSON_TYPE) -> list[str]:
    return sorted(f"{path} = {value};" for path, value in _gron_helper(obj))


def _ungron_helper(data: Sequence[tuple[str, str]], _walker: int = 0) -> tuple[JSON_TYPE, int]:  # noqa: C901
    (head_path, head_value) = data[_walker]
    if head_value == "[]":
        ret: list[Any] = []
        pattern = re.escape(head_path) + r"\[(\d+)\]"
        _walker += 1
        while _walker < len(data):
            (path, value) = data[_walker]
            pattern_match = re.match(pattern, path)
            if pattern_match:
                index = int(pattern_match.group(1))
                d, _walker = _ungron_helper(data, _walker)
                ret.insert(index, d)
            else:
                break
        return ret, _walker
    if head_value == "{}":
        ret_dict = {}
        pattern_base = re.escape(head_path)
        _walker += 1
        while _walker < len(data):
            (path, value) = data[_walker]
            pattern_match = re.match(
                pattern_base + r"\.(\w+)",
                path,
            ) or re.match(pattern_base + r'\["(.+?)"\]', path)
            if pattern_match:
                key = pattern_match.group(1)
                d, _walker = _ungron_helper(data, _walker)
                ret_dict[key] = d
            else:
                break
        return ret_dict, _walker
    if head_value == "true":
        return True, _walker + 1
    if head_value == "false":
        return False, _walker + 1
    if head_value == "null":
        return None, _walker + 1
    if head_value.startswith('"'):
        return head_value[1:-1], _walker + 1
    if head_value.isnumeric():
        return int(head_value), _walker + 1

    return float(head_value), _walker + 1


def ungron(lines: Iterable[str]) -> JSON_TYPE:
    result, _ = _ungron_helper(
        [
            line.strip().rstrip(";").split(" = ", maxsplit=1)  # type: ignore
            for line in lines
        ]
    )
    return result
