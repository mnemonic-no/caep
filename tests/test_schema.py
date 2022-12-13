""" test config """
import os
from typing import List, Optional, Set, Type

import pytest
from pydantic import BaseModel, Field, ValidationError

import caep
from caep.schema import escape_split

INI_TEST_FILE = os.path.join(os.path.dirname(__file__), "data/config_testdata.ini")


class Arguments(BaseModel):

    str_arg: str = Field(description="Required String Argument")
    number: int = Field(default=1, description="Integer with default value")
    enabled: bool = Field(default=False, description="Boolean with default value")

    flag1: bool = Field(default=True, description="Boolean with default value")

    float_arg: float = Field(default=0.5, description="Float with default value")

    # List fields will be separated by space as default
    intlist: List[int] = Field(description="Space separated list of ints")

    # Can optionally use "split" argument to use another value to split based on
    strlist: List[str] = Field(description="Comma separated list of strings", split=",")

    # List fields will be separated by space as default
    strset: Set[str] = Field(description="Space separated set of strings")


class Arg1(BaseModel):
    str_arg: str = Field(description="Required String Argument")


class Arg2(BaseModel):
    number: int = Field(default=1, description="Integer with default value")


class Arg3(BaseModel):
    enabled: bool = Field(default=False, description="Boolean with default value")


class ArgCombined(Arg1, Arg2, Arg3):
    pass


def parse_args(
    model: Type[caep.schema.BaseModelType],
    commandline: Optional[List[str]] = None,
    description: str = "Program description",
    config_id: str = "config_id",
    config_filename: str = "config_filename",
    section_name: str = "test",
    raise_on_validation_error: bool = False,
) -> caep.schema.BaseModelType:
    return caep.load(
        model,
        description,
        config_id,
        config_filename,
        section_name,
        opts=commandline,
        raise_on_validation_error=raise_on_validation_error,
    )


def test_schema_commandline() -> None:
    """arguments from command line"""
    commandline = "--str-arg test --enabled".split()

    config = parse_args(Arguments, commandline)

    assert config.number == 1
    assert config.float_arg == 0.5
    assert config.str_arg == "test"
    assert config.enabled is True
    assert config.flag1 is True  # Default True


def test_schema_commandline_strset() -> None:
    """disable flag that is default True"""
    commandline = "--str-arg test --strset 'abc abc abc'".split()

    config = parse_args(Arguments, commandline)
    assert config.strset == set("abc")


def test_schema_commandline_disable_bool() -> None:
    """disable flag that is default True"""
    commandline = "--str-arg test --flag1".split()

    config = parse_args(Arguments, commandline)
    assert config.flag1 is False


def test_schema_commandline_escaped_list() -> None:
    """escape splits"""
    commandline = r"--str-arg test --strlist 'A\,B\,C,1\,2\,3'".split()

    config = parse_args(Arguments, commandline)

    assert config.strlist == ["'A,B,C", "1,2,3'"]


def test_schema_commandline_missing_required_raise() -> None:
    """missing required string argument and raise error"""

    with pytest.raises(ValidationError):
        parse_args(Arguments, raise_on_validation_error=True)


def test_schema_commandline_missing_required_print() -> None:
    """missing required string argument - print usage"""

    with pytest.raises(SystemExit):
        parse_args(Arguments)


def test_schema_ini() -> None:
    """all arguments from ini file"""
    commandline = f"--config {INI_TEST_FILE}".split()

    config = parse_args(Arguments, commandline, section_name="test")

    assert config.number == 3
    assert config.str_arg == "from ini"
    assert config.enabled is True
    assert config.flag1 is True


def test_argparse_env() -> None:
    """all arguments from env"""

    env = {
        "STR_ARG": "from env",
        "NUMBER": 4,
        "ENABLED": "yes",  # accepts both yes and true
    }

    for key, value in env.items():
        os.environ[key] = str(value)

    config = parse_args(Arguments, section_name="test")

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

    config = parse_args(Arguments, commandline, section_name="test")

    assert config.number == 4
    assert config.str_arg == "cmdline"
    assert config.enabled is True

    # Remove from environment variables
    for key in env:
        del os.environ[key]


def test_schema_joined_schemas() -> None:
    """Test schema that is created based on three other schemas"""
    commandline = "--str-arg arg1 --number 10 --enabled".split()

    config = parse_args(ArgCombined, commandline)

    assert config.number == 10
    assert config.str_arg == "arg1"
    assert config.enabled is True


def test_escape_split() -> None:

    assert escape_split("A\\,B\\,C,1\\,2\\,3", ",") == ["A,B,C", "1,2,3"]
    assert escape_split("ABC 123") == ["ABC", "123"]
    assert escape_split("A\\\\BC 123") == ["A\\BC", "123"]

    # Escaped slash
