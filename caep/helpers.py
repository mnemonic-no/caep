import inspect
from pathlib import Path
from typing import Any, Optional, cast

import caep


class ArgumentError(Exception):
    pass


def config_files(arguments: Optional[list[str]] = None) -> list[str]:
    """
    return list of files specified with --config
    """
    config_files: list[str] = []

    config_parser = caep.config.get_early_parser()
    if arguments:
        args, _ = config_parser.parse_known_args(arguments)
    else:
        args, _ = config_parser.parse_known_args()

    if args.config:
        config_files = [file.name for file in args.config]

    return config_files


def raise_if_some_and_not_all(entries: dict[str, Any], keys: list[str]) -> None:
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
            "All or none of these arguments must be set: "
            f"{all_args}. Missing: {missing_args}"
        )


def __mod_name(stack: inspect.FrameInfo) -> Optional[str]:
    """Return name of module from a stack ("_" is replaced by "-")"""
    mod = inspect.getmodule(stack[0])
    if not mod:
        return None

    return str(Path(cast(str, mod.__file__)).stem).replace("_", "-")


def script_name() -> str:
    """
    Return first external module that called this function, directly, or indirectly
    """

    modules = [__mod_name(stack) for stack in inspect.stack() if __mod_name(stack)]
    return [name for name in modules if name and name != modules[0]][0]
