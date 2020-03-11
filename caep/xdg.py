#!/usr/bin/env python

"""

"""

import os
from typing import Text


def get_xdg_dir(xdg_id: Text, env_name: Text, default: Text, create: bool = False) -> Text:
    """
    Get xdg dir.

    https://specifications.freedesktop.org/basedir-spec/basedir-spec-0.6.html

    Honors $XDG_*_HOME, but fallbacks to defaults

Args:
    xdg_id [str]: directory under directory that will be used
    env_name [str]: XDG environment variable, e.g. XDG_CACHE_HOME
    env_name [str]: default directory in home directory, e.g. .cache
    create [bool]: create directory if not exists

Return path to cache_directory
    """

    home = os.environ["HOME"]

    xdg_home = os.environ.get(env_name, os.path.join(home, default))
    xdg_dir = os.path.join(xdg_home, xdg_id)

    if create and not os.path.isdir(xdg_dir):
        os.makedirs(xdg_dir)

    return xdg_dir


def get_config_dir(config_id: Text, create: bool = False) -> Text:
    """
    Get config dir.

    Honors $XDG_CONFIG_HOME, but fallbacks to ".config"

    See get_xdg_dir for details
    """

    return get_xdg_dir(config_id, "XDG_CONFIG_HOME", ".config", create)


def get_cache_dir(cache_id: str, create: bool = False) -> str:
    """
    Get cache dir.

    Honors $XDG_CACHE_HOME, but fallbacks to $HOME/.cache

Args:
    cache_id [str]: directory under CACHE that will be used
    create [bool]: create directory if not exists

Return path to cache_directory
    """

    return get_xdg_dir(cache_id, "XDG_CACHE_HOME", ".cache", create)
