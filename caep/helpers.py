import inspect
import os
from typing import Any, Dict, List, Optional, cast


class ArgumentError(Exception):
    pass


def raise_if_some_and_not_all(entries: Dict[str, Any], keys: List[str]) -> None:
    """
    Raise ArgumentError if some of the specified entries in the dictionary has non
    false values but not all
    """

    values = [entries.get(key) for key in keys]

    if any(values) and not all(values):
        all_args = ", ".join(f"--{key.replace('_', '-')}" for key in keys)
        missing_args = ", ".join(
            f"--{key.replace('_', '-')}" for key in keys if not entries.get(key)
        )
        raise ArgumentError(
            f"All or none of these arguments must be set: {all_args}. Missing: {missing_args}"  # noqa: E501
        )


def __mod_name(stack: inspect.FrameInfo) -> Optional[str]:
    """Return name of module from a stack ("_" is replaced by "-")"""
    mod = inspect.getmodule(stack[0])
    if not mod:
        return None

    return cast(
        str, os.path.basename(mod.__file__).replace(".py", "").replace("_", "-")  # type: ignore # noqa: E501
    )


def script_name() -> str:
    """Return first external module that called this function, directly, or indirectly"""  # noqa: E501

    modules = [__mod_name(stack) for stack in inspect.stack() if __mod_name(stack)]
    return [name for name in modules if name and name != modules[0]][0]
