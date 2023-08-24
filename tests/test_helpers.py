import shlex
from pathlib import Path
from typing import List, Optional

import pytest
from pydantic import BaseModel  # noqa: E0611
from pydantic import Field, model_validator
from test_schema import parse_args

import caep

TEST_DATA_DIR = Path(__file__).parent / "data"
INI_TEST_FILE = TEST_DATA_DIR / "config_testdata.ini"
SECOND_INI_TEST_FILE = TEST_DATA_DIR / "config_testdata2.ini"


class ExampleConfig(BaseModel):
    username: Optional[str] = Field(description="Username")
    password: Optional[str] = Field(description="Password")
    parent_id: Optional[str] = Field(description="Parent ID")

    @model_validator(mode="after")  # type: ignore
    def check_arguments(cls, m: "ExampleConfig") -> "ExampleConfig":
        """If one argument is set, they should all be set"""

        caep.raise_if_some_and_not_all(
            m.__dict__, ["username", "password", "parent_id"]
        )

        return m


def test_config_files() -> None:
    """raise if config files are not returned correctly"""
    files = [INI_TEST_FILE.as_posix(), SECOND_INI_TEST_FILE.as_posix()]

    commandline = shlex.split(f"--config {' '.join(files)}")
    config_files = caep.helpers.config_files(commandline)

    for file in files:
        assert file in config_files


def test_config_files_empty() -> None:
    """raise if config files are not empty"""
    commandline: List[str] = []
    config_files = caep.helpers.config_files(commandline)

    assert config_files == []


def test_raise_if_some_and_not_all() -> None:
    """raise_if_some_and_not_all success test"""
    commandline = "--username pytest --password supersecret --parent-id testing".split()

    config = parse_args(ExampleConfig, commandline)

    assert config.username == "pytest"
    assert config.password == "supersecret"
    assert config.parent_id == "testing"


def test_raise_if_some_and_not_all_fail_to_validate() -> None:
    """raise_if_some_and_not_all failure test"""
    commandline = "--username pytest --password supersecret".split()

    with pytest.raises(caep.helpers.ArgumentError):
        parse_args(ExampleConfig, commandline)


def test_script_name() -> None:
    """script_name corresponds with name of script"""

    assert caep.script_name() == "test-helpers"
