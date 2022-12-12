""" test config """
import os
from typing import List, Optional

import pytest
from pydantic import BaseModel, Field, ValidationError

import caep

INI_TEST_FILE = os.path.join(os.path.dirname(__file__), "data/config_testdata.ini")


class Arguments(BaseModel):

    # Fields that are not specified as `Field` with description will not have
    # any help text

    str_arg: str = Field(description="Required String Argument")
    number: int = Field(default=1, description="Integer with default value")
    enabled: bool = Field(default=False, description="Boolean with default value")

    # List fields will be separated by space as default
    intlist: List[int] = Field(description="Space separated list of ints")

    # Can optionally use "split" argument to use another value to split based on
    strlist: List[str] = Field(description="Comma separated list of strings", split=",")


def parse_args(
    commandline: Optional[List[str]] = None,
    description: str = "Program description",
    config_id: str = "config_id",
    config_filename: str = "config_filename",
    section_name: str = "test",
    raise_on_validation_error: bool = False,
) -> Arguments:
    return caep.load(
        Arguments,
        description,
        config_id,
        config_filename,
        section_name,
        opts=commandline,
        raise_on_validation_error=raise_on_validation_error,
    )


def test_schema_commandline() -> None:
    """all arguments from command line, using default for number and bool"""
    commandline = "--str-arg test".split()

    config = parse_args(commandline)

    assert config.number == 1
    assert config.str_arg == "test"
    assert not config.enabled


def test_schema_commandline_missing_required_raise() -> None:
    """missing required string argument and raise error"""

    with pytest.raises(ValidationError):
        parse_args(raise_on_validation_error=True)


def test_schema_commandline_missing_required_print() -> None:
    """missing required string argument - print usage"""

    with pytest.raises(SystemExit):
        parse_args()


def test_schema_ini() -> None:
    """all arguments from ini file"""
    commandline = f"--config {INI_TEST_FILE}".split()

    config = parse_args(commandline, section_name="test")

    assert config.number == 3
    assert config.str_arg == "from ini"
    assert config.enabled is True


def test_argparse_env() -> None:
    """all arguments from env"""

    env = {
        "STR_ARG": "from env",
        "NUMBER": 4,
        "ENABLED": "yes",  # accepts both yes and true
    }

    for key, value in env.items():
        os.environ[key] = str(value)

    config = parse_args(section_name="test")

    assert config.number == 4
    assert config.str_arg == "from env"
    assert config.enabled is True

    # Remove from environment variables
    for key in env:
        del os.environ[key]


def test_argparse_env_ini() -> None:
    """
    --number from environment
    --bool from ini
    --str-arg from cmdline

    """
    env = {
        "NUMBER": 4,
    }

    for key, value in env.items():
        os.environ[key] = str(value)

    commandline = f"--config {INI_TEST_FILE} --str-arg cmdline".split()

    config = parse_args(commandline, section_name="test")

    assert config.number == 4
    assert config.str_arg == "cmdline"
    assert config.enabled is True

    # Remove from environment variables
    for key in env:
        del os.environ[key]
