""" test config """

import ipaddress
import os
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Set, Type

import pytest
from pydantic import BaseModel, Field, ValidationError

import caep
from caep.schema import (
    ArrayInfo,
    DictInfo,
    FieldError,
    escape_split,
    split_dict,
    split_list,
)

TEST_DATA_DIR = Path(__file__).parent / "data"
INI_TEST_FILE = TEST_DATA_DIR / "config_testdata.ini"
SECOND_INI_TEST_FILE = TEST_DATA_DIR / "config_testdata2.ini"


class Arguments(BaseModel):
    str_arg: str = Field(description="Required String Argument")
    number: int = Field(default=1, description="Integer with default value")
    enabled: bool = Field(default=False, description="Boolean with default value")

    flag1: bool = Field(default=True, description="Boolean with default value")

    float_arg: float = Field(default=0.5, description="Float with default value")

    # List fields will be separated by space as default
    intlist: List[int] = Field(description="Space separated list of ints", split=" ")

    # Can optionally use "split" argument to use another value to split based on
    strlist: List[str] = Field(description="Comma separated list of strings")

    # Set that will be separated by space (default)
    strset: Set[str] = Field(description="Space separated set of strings", split=" ")

    dict_str: Dict[str, str] = Field(description="Str Dict split by comma and colon")

    dict_int: Dict[str, int] = Field(
        description="Int Dict split by slash and dash", split="-", kv_split="/"
    )

    ipv4: Optional[ipaddress.IPv4Address] = Field(description="IPv4 Address")

    ipv4_net: Optional[ipaddress.IPv4Network] = Field(description="IPv4 Network")

    path: Optional[Path] = Field(description="Path")


class ArgNs2(BaseModel):
    str_arg: str = Field(value="Unset", description="String argument")


class ArgNs1(BaseModel):
    ns: ArgNs2 = Field(description="Namespaced argument")


class Arg1(BaseModel):
    str_arg: str = Field(description="Required String Argument")


class Arg2(BaseModel):
    number: int = Field(default=1, description="Integer with default value")


class Arg3(BaseModel):
    enabled: bool = Field(default=False, description="Boolean with default value")


class MultipleFiles(BaseModel):
    number: int = Field(default=1, description="Integer with default value")
    first_file: bool = Field(description="Value set in first config file")
    second_file: bool = Field(description="Value set in second config file")


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


def test_schema_no_config() -> None:
    commandline = "--str-arg str".split()
    config: Arguments = caep.load(Arguments, "Description", opts=commandline)

    assert config is not None


def test_schema_epilog(capsys) -> None:  # type: ignore
    """Test epilog that are printed on --help"""
    commandline = "--help".split()

    with pytest.raises(SystemExit):
        caep.load(Arguments, "Description", opts=commandline, epilog="Extended epilog")

    captured = capsys.readouterr()

    assert "Extended epilog" in captured.out


def test_schema_namespaces() -> None:
    """arguments from namespaced schemas"""
    commandline = "--ns a:1,b:2".split()

    # Recusrive schemas are not supported
    with pytest.raises(FieldError):
        parse_args(ArgNs1, commandline)


def test_schema_commandline() -> None:
    """arguments from command line"""
    commandline = (
        "--str-arg test --enabled --path /etc/passwd --ipv4 127.0.0.1 "
        + "--ipv4-net 192.168.1.0/24"
    ).split()

    config = parse_args(Arguments, commandline)

    assert config.number == 1
    assert config.float_arg == 0.5
    assert config.str_arg == "test"
    assert config.enabled is True
    assert config.flag1 is True  # Default True
    assert config.path == Path("/etc/passwd")
    assert config.ipv4 == ipaddress.IPv4Address("127.0.0.1")
    assert config.ipv4_net == ipaddress.IPv4Network("192.168.1.0/24")


def test_schema_ipv4_fail_to_validate() -> None:
    """arguments from command line"""
    commandline = "--str-arg test --ipv4 x.y.z".split()

    with pytest.raises(ValidationError):
        parse_args(Arguments, commandline, raise_on_validation_error=True)


def test_schema_commandline_strset() -> None:
    """disable flag that is default True"""
    commandline = shlex.split("--str-arg test --strset 'abc abc abc'")

    config = parse_args(Arguments, commandline)
    assert config.strset == set(("abc",))


def test_schema_commandline_dict_str() -> None:
    """Dict strings"""
    commandline = shlex.split(
        "--str-arg test --dict-str 'header 1: x option, header 2: y option'"
    )

    config = parse_args(Arguments, commandline)

    dict_str = config.dict_str

    assert dict_str is not None
    assert dict_str is not {}

    assert dict_str["header 1"] == "x option"
    assert dict_str["header 2"] == "y option"


def test_schema_commandline_dict_int() -> None:
    """Dict strings"""
    commandline = shlex.split("--str-arg test --dict-int 'a/1-b/2'")

    config = parse_args(Arguments, commandline)

    dict_int = config.dict_int

    assert dict_int is not None
    assert dict_int is not {}

    print(dict_int)

    assert dict_int["a"] == 1
    assert dict_int["b"] == 2


def test_schema_commandline_disable_bool() -> None:
    """disable flag that is default True"""
    commandline = shlex.split("--str-arg test --flag1")

    config = parse_args(Arguments, commandline)
    assert config.flag1 is False


def test_schema_commandline_escaped_list() -> None:
    """escape splits"""
    commandline = shlex.split(r"--str-arg test --strlist 'A\,B\,C,1\,2\,3'")

    config = parse_args(Arguments, commandline)

    assert config.strlist == ["A,B,C", "1,2,3"]


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
    commandline = shlex.split(f"--config {INI_TEST_FILE}")

    config = parse_args(Arguments, commandline, section_name="test")

    assert config.number == 3
    assert config.str_arg == "from ini"
    assert config.enabled is True
    assert config.flag1 is True


def test_schema_ini_default_only() -> None:
    """all arguments from ini file and default section"""
    commandline = shlex.split(f"--config {INI_TEST_FILE}")

    config = caep.load(Arg2, "Program description", opts=commandline)

    assert config.number == 3


def test_schema_ini_default_multiple_files() -> None:
    """all arguments from ini file and default section"""
    commandline = shlex.split(f"--config {INI_TEST_FILE} {SECOND_INI_TEST_FILE}")

    config = caep.load(MultipleFiles, "Program description", opts=commandline)

    # Make sure files has been read in the correct order
    assert config.number == 2

    # Make sure both files has been read
    assert config.first_file is True
    assert config.second_file is True


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

    commandline = shlex.split(f"--config {INI_TEST_FILE} --str-arg cmdline")

    config = parse_args(Arguments, commandline, section_name="test")

    assert config.number == 4
    assert config.str_arg == "cmdline"
    assert config.enabled is True

    # Remove from environment variables
    for key in env:
        del os.environ[key]


def test_schema_joined_schemas() -> None:
    """Test schema that is created based on three other schemas"""
    commandline = shlex.split("--str-arg arg1 --number 10 --enabled")

    config = parse_args(ArgCombined, commandline)

    assert config.number == 10
    assert config.str_arg == "arg1"
    assert config.enabled is True


def test_escape_split() -> None:
    assert escape_split("A\\,B\\,C,1\\,2\\,3") == ["A,B,C", "1,2,3"]
    assert escape_split("ABC 123", split=" ") == ["ABC", "123"]

    # Escaped slash
    assert escape_split("A\\\\BC 123", split=" ") == ["A\\BC", "123"]


def test_split_list() -> None:
    # Default split = ","
    assert split_list("a,b,c", ArrayInfo(array_type=str))

    # Configure split value
    assert split_list("a b c", ArrayInfo(array_type=str, split=" "))

    # min_size
    with pytest.raises(FieldError):
        assert split_list("", ArrayInfo(array_type=str, min_size=1))


def test_split_dict() -> None:
    # Defaults
    d = split_dict("a:b,b:c,c: value X", DictInfo(dict_type=str))

    assert d is not None

    assert d["c"] == "value X"

    with pytest.raises(FieldError):
        v = split_dict("", DictInfo(dict_type=str, min_size=1))
        print(v)

    with pytest.raises(FieldError):
        split_dict("a,b", DictInfo(dict_type=str))
