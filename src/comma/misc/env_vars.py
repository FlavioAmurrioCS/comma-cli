from __future__ import annotations

import itertools
import os


def get_required_env_vars(
    varname: str,
    *varnames: str,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    """
    Get the values of the specified environment variables, raising an error if any of them are not set or empty.

    Args:
    ----
        varname: The name of the first environment variable to get.
        varnames: The names of any additional environment variables to get.
        allow_empty: Whether to allow empty values for the environment variables.

    Returns:
    -------
        An iterable of the values of the specified environment variables.

    Raises:
    ------
        ValueError: If any of the specified environment variables are not set or empty.

    """  # noqa: E501
    ret: list[str] = []
    for var_name in itertools.chain((varname,), varnames):
        val = os.getenv(var_name)
        if val is None or (not allow_empty and not val):
            msg = f"Environment variable {var_name} must not be empty."
            raise ValueError(msg)
        ret.append(val)
    return tuple(ret)


def get_env_vars_or_default(
    varname_default_pair: tuple[str, str],
    *varname_default_pairs: tuple[str, str],
    allow_empty: bool = False,
) -> tuple[str, ...]:
    """
    Get the values of the specified environment variables, using default values if any of them are not set or empty.

    Args:
    ----
        varname_default_pair: A tuple containing the name of the first environment variable to get and its default value.
        varname_default_pairs: Tuples containing the names and default values of any additional environment variables to get.
        allow_empty: Whether to allow empty values for the environment variables.

    Returns:
    -------
        An iterable of the values of the specified environment variables, using the default values
        for any that are not set or empty.

    """  # noqa: E501
    ret: list[str] = []
    for var_name, default in itertools.chain((varname_default_pair,), varname_default_pairs):
        val = os.getenv(var_name)
        if val is None or (not allow_empty and not val):
            val = default
        ret.append(val)
    return tuple(ret)
