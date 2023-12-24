from __future__ import annotations
# import json
# from inspect import _empty
# from inspect import Parameter
# from typing import TYPE_CHECKING
# import pytest
# from simple_argparser.simple_rick import _fun
# if TYPE_CHECKING:
#     from simple_argparser.simple_rick import _argument_options
# _kind = Parameter.POSITIONAL_OR_KEYWORD
# @pytest.mark.parametrize(
#     'data,expected', [
#         # Basic
#         (Parameter('foo', _kind, default=_empty, annotation='int'), ('foo', {'type': int})),
#         (Parameter('foo', _kind, default=_empty, annotation='str'), ('foo', {'type': str})),
#         (Parameter('foo', _kind, default=_empty, annotation='float'), ('foo', {'type': float})),
#         # Optional
#         (Parameter('foo', _kind, default=_empty, annotation='Optional[int]'), ('--foo', {'type': int, 'default': None})),
#         (Parameter('foo', _kind, default=_empty, annotation='Optional[str]'), ('--foo', {'type': str, 'default': None})),
#         (Parameter('foo', _kind, default=_empty, annotation='Optional[float]'), ('--foo', {'type': float, 'default': None})),
#         (Parameter('foo', _kind, default=_empty, annotation='int | None'), ('--foo', {'type': int, 'default': None})),
#         (Parameter('foo', _kind, default=_empty, annotation='str | None'), ('--foo', {'type': str, 'default': None})),
#         (Parameter('foo', _kind, default=_empty, annotation='float | None'), ('--foo', {'type': float, 'default': None})),
#         (Parameter('foo', _kind, default=_empty, annotation='Union[int, None]'), ('--foo', {'type': int, 'default': None})),
#         (Parameter('foo', _kind, default=_empty, annotation='Union[str, None]'), ('--foo', {'type': str, 'default': None})),
#         (Parameter('foo', _kind, default=_empty, annotation='Union[float, None]'), ('--foo', {'type': float, 'default': None})),
#         # Containers
#         (Parameter('foo', _kind, default=_empty, annotation='list[int]'), ('foo', {'type': int, 'nargs': '+', 'default': []})),
#         (Parameter('foo', _kind, default=_empty, annotation='list[str]'), ('foo', {'type': str, 'nargs': '+', 'default': []})),
#         (Parameter('foo', _kind, default=_empty, annotation='list[float]'), ('foo', {'type': float, 'nargs': '+', 'default': []})),
#         (Parameter('foo', _kind, default=_empty, annotation='tuple[int]'), ('foo', {'type': int, 'nargs': '+', 'default': ()})),
#         (Parameter('foo', _kind, default=_empty, annotation='tuple[str]'), ('foo', {'type': str, 'nargs': '+', 'default': ()})),
#         (Parameter('foo', _kind, default=_empty, annotation='tuple[float]'), ('foo', {'type': float, 'nargs': '+', 'default': ()})),
#         # Booleans
#         (Parameter('foo', _kind, default=_empty, annotation='bool'), ('foo', {'type': bool, 'action': 'store_true'})),
#         (Parameter('foo', _kind, default=_empty, annotation='Optional[bool]'), ('foo', {'type': bool, 'action': 'store_true'})),
#         (Parameter('foo', _kind, default=_empty, annotation='bool | None'), ('foo', {'type': bool, 'action': 'store_true'})),
#         (Parameter('foo', _kind, default=_empty, annotation='Union[bool, None]'), ('foo', {'type': bool, 'action': 'store_true'})),
#         (Parameter('foo', _kind, default=_empty, annotation='list[bool]'), ('foo', {'type': bool, 'action': 'store_true'})),
#         (Parameter('foo', _kind, default=_empty, annotation='tuple[bool]'), ('foo', {'type': bool, 'action': 'store_true'})),
#         # (Parameter('foo', _kind, default=1000, annotation=int), ('--foo', {'type': int, 'default': 1000})),
#         # (Parameter('foo', _kind, default='aa', annotation=str), ('--foo', {'type': str, 'default': 'aa'})),
#         # (Parameter('foo', _kind, default=[1,], annotation='list[str]'), ('--foo', {'type': int, 'default': (1,)})),
#         # (Parameter('foo', _kind, default=1000, annotation=_empty), ('--foo', {'type': int, 'default': 1000})),
#         # (Parameter('foo', _kind, default='aa', annotation=_empty), ('--foo', {'type': str, 'default': 'aa'})),
#         # (Parameter('foo', _kind, default=(1,), annotation=_empty), ('--foo', {'type': int, 'default': (1,)})),
#         # (Parameter('foo', _kind, default=_empty, annotation='str'), ('foo', {'type': str})),
#         # (Parameter('foo', _kind, default=_empty, annotation='int'), ('foo', {'type': int})),
#         # (Parameter('foo', _kind, default=_empty, annotation=bool), ('foo', {'type': bool, 'default': -1})),
#     ],
# )
# def test_simple_rick2(data: Parameter, expected: tuple[str, _argument_options]) -> None:
#     actual_name, actual_kwargs = _fun(data.name, data)
#     expected_name, expected_kwargs = expected
#     assert actual_name == expected_name
#     try:
#         assert actual_kwargs == expected_kwargs
#     except AssertionError:
#         print(f'{actual_name=}')
#         print(json.dumps(actual_kwargs, indent=4, default=str))
#         print(json.dumps(expected_kwargs, indent=4, default=str))
#         raise
# #     ('--is-admin', {'type': bool, 'default': False}),
# # ]
