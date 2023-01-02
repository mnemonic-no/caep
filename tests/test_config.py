""" test config """
import argparse
import os

from caep import config

INI_TEST_FILE = os.path.join(os.path.dirname(__file__), "data/config_testdata.ini")


def __argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("test argparse", allow_abbrev=False)
    parser.add_argument("--number", type=int, default=1)
    parser.add_argument("--enabled", action="store_true")
    parser.add_argument("--str-arg")

    return parser


def test_argparse_only() -> None:
    """all arguments from command line, using default for number and enabled"""

    parser = __argparser()

    commandline = "--str-arg test".split()

    args = config.handle_args(
        parser, "actworkers", "actworkers.ini", "test", opts=commandline
    )

    assert args.number == 1
    assert args.str_arg == "test"
    assert not args.enabled


def test_argparse_ini() -> None:
    """all arguments from ini file"""
    parser = __argparser()

    commandline = f"--config {INI_TEST_FILE}".split()

    args = config.handle_args(
        parser, "actworkers", "actworkers.ini", "test", opts=commandline
    )

    assert args.number == 3
    assert args.str_arg == "from ini"
    assert args.enabled is True


def test_argparse_env() -> None:
    """all arguments from env"""
    parser = __argparser()

    env = {
        "STR_ARG": "from env",
        "NUMBER": 4,
        "ENABLED": "yes",  # accepts both yes and true
    }

    for key, value in env.items():
        os.environ[key] = str(value)

    args = config.handle_args(parser, "actworkers", "actworkers.ini", "test", opts=[])

    assert args.number == 4
    assert args.str_arg == "from env"
    assert args.enabled is True

    # Remove from environment variables
    for key in env:
        del os.environ[key]


def test_argparse_env_ini() -> None:
    """
    --number from enviorment
    --enabled from ini
    --str-arg from cmdline

    """
    parser = __argparser()

    env = {
        "NUMBER": 4,
    }

    for key, value in env.items():
        os.environ[key] = str(value)

    commandline = f"--config {INI_TEST_FILE} --str-arg cmdline".split()

    args = config.handle_args(
        parser, "actworkers", "actworkers.ini", "test", opts=commandline
    )

    assert args.number == 4
    assert args.str_arg == "cmdline"
    assert args.enabled is True

    # Remove from environment variables
    for key in env:
        del os.environ[key]
