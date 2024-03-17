from __future__ import annotations

import argparse
import functools
import inspect
import json
import re
from typing import Any
from typing import Callable
from typing import Generic
from typing import Literal
from typing import TYPE_CHECKING
from typing import TypeVar


if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing_extensions import ParamSpec

    P = ParamSpec("P")
    from typing import Annotated
    from typing_extensions import TypedDict

    class _ArgumentOptions(TypedDict, total=False):
        action: str
        nargs: str
        default: Any
        help: str
        type: Any
        choices: Sequence[Any]


FUNC = TypeVar("FUNC", bound=Callable)  # type: ignore

# Argument List:
# - Optional
# - Has Default Value
# - Boolean


def _fun(var_name: str, param: inspect.Parameter) -> tuple[str, _ArgumentOptions]:
    annotation = param.annotation
    default = param.default
    if annotation is inspect.Parameter.empty and default is inspect.Parameter.empty:
        msg = f"{var_name=} has no annotation or default value"
        raise ValueError(msg)

    if annotation is inspect.Parameter.empty:
        annotation = type(default).__name__

    annotation = str(annotation)  # Just in case future annotations is not enabled

    kwargs: _ArgumentOptions = {}

    has_default = default is not inspect.Parameter.empty
    if has_default:
        kwargs["default"] = default

    help_text = ""
    # extract help text from Annotated
    if annotation.startswith("Annotated["):
        annotation, help_text = annotation[10:-1].rsplit(", ", maxsplit=1)
        help_text = help_text[1:-1]
        annotation = annotation.strip()

    field_arg = var_name.replace("_", "-")

    # Check if Optional
    optional_match = (
        re.match(r"^Optional\[(.*)\]$", annotation)
        or re.match(
            r"^(.*) \| None$",
            annotation,
        )
        or re.match(r"^Union\[(.*), None\]$", annotation)
    )
    # is_optional = optional_match is not None
    if optional_match:
        annotation = optional_match.group(1).strip()

    if has_default:
        field_arg = f"--{field_arg}"

    # check if container type
    container_match = re.match(r"^(.*)\[(.*)\]$", annotation, re.IGNORECASE)
    container_type = None

    if container_match:
        container_type = container_match.group(1).strip().lower()
        annotation = container_match.group(2).strip()
        if container_type == "literal":
            choices = eval(annotation)  # noqa: S307, PGH001
            annotation = type(choices[0]).__name__
        else:
            # WHICH ONE SHOULD I BE USING?
            # kwargs['action'] = 'append'
            kwargs["nargs"] = "+"

    if annotation == "bool":
        kwargs["action"] = "store_true" if default is True else "store_false"
    else:
        kwargs["type"] = eval(annotation)  # noqa: S307, PGH001

    # kwargs['help'] = help_text

    return field_arg, kwargs


class _CliApp(Generic[FUNC]):
    def __init__(self, func: FUNC, command_name: str | None = None) -> None:
        self.__wrapped__ = func
        self.__argument_parser__ = argparse.ArgumentParser(
            prog=command_name or func.__name__,
            description=self.__wrapped__.__doc__,
        )
        functools.update_wrapper(self, func)

    def __parse_args__(self, argv: Sequence[str] | None = None) -> dict[str, Any]:
        parser = self.__argument_parser__
        unknown_args_var_name = None

        for var_name, param in inspect.signature(main.__wrapped__).parameters.items():
            if param.kind is inspect.Parameter.VAR_POSITIONAL:
                unknown_args_var_name = var_name
                continue
            field_arg, kwargs = _fun(var_name, param)

            # logging.error(f'{field_arg=}, {kwargs=}')

            parser.add_argument(field_arg, **kwargs)
        if unknown_args_var_name is None:
            return parser.parse_args(argv).__dict__
        args, unknonw = parser.parse_known_args(argv)
        return {**args.__dict__, unknown_args_var_name: unknonw}

    def __call__(self, argv: Sequence[str] | None = None) -> FUNC:
        args = self.__parse_args__(argv)
        result = self.__wrapped__(**args)
        raise SystemExit(result)


def cli_app(command_name: str | None = None):  # type: ignore  # noqa: ANN201
    def inner(func: FUNC) -> _CliApp[FUNC]:
        return _CliApp(func=func, command_name=command_name)

    return inner


@cli_app()
def main(
    name: Annotated[str | None, "SOME 'METADATA"],
    color: Literal["red", "green", "blue"],
    age: int,
    last: str | None,
    has_kids: bool,  # noqa: FBT001
    *args: str,
) -> int:
    """HEOMOE."""
    print(json.dumps(locals(), indent=4))
    return 1


if __name__ == "__main__":
    a = main()
