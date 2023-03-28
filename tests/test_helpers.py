from typing import Any, Dict, Optional

import pytest
from pydantic import BaseModel  # noqa: E0611
from pydantic import Field, root_validator
from test_schema import parse_args

import caep


class ExampleConfig(BaseModel):
    username: Optional[str] = Field(description="Username")
    password: Optional[str] = Field(description="Password")
    parent_id: Optional[str] = Field(description="Parent ID")

    @root_validator
    def check_arguments(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """If one argument is set, they should all be set"""

        caep.raise_if_some_and_not_all(values, ["username", "password", "parent_id"])

        return values


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
