#!/usr/bin/env python

"""
XDG helper methods
"""

import os
from pathlib import Path


def get_xdg_dir(xdg_id: str, env_name: str, default: str, create: bool = False) -> Path:
    """
        Get XDG dir.

        https://specifications.freedesktop.org/basedir-spec/basedir-spec-0.6.html

        Honors $XDG_*_HOME, but falls back to defaults

    Args:
        xdg_id [str]: directory under directory that will be used
        env_name [str]: XDG environment variable, e.g. XDG_CACHE_HOME
        default [str]: default directory in home directory, e.g. .cache
        create [bool]: create directory if it does not exist

    Return path to directory
    """

    home = Path.home()

    xdg_home = os.environ.get(env_name, home / default)
    xdg_dir = Path(xdg_home) / xdg_id

    if create and not xdg_dir.is_dir():
        xdg_dir.mkdir(parents=True)

    return xdg_dir


def get_config_dir(config_id: str, create: bool = False) -> Path:
    """
    Get config dir.

    Honors $XDG_CONFIG_HOME, but falls back to ".config"

    See get_xdg_dir for details
    """

    return get_xdg_dir(config_id, "XDG_CONFIG_HOME", ".config", create)


def get_cache_dir(cache_id: str, create: bool = False) -> Path:
    """
        Get cache dir.

        Honors $XDG_CACHE_HOME, but falls back to $HOME/.cache

    Args:
        cache_id [str]: directory under CACHE that will be used
        create [bool]: create directory if it does not exist

    Return path to cache directory
    """

    return get_xdg_dir(cache_id, "XDG_CACHE_HOME", ".cache", create)
