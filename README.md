# CAEP

Configuration library that supports loading configuration from ini, environment variables
and arguments into a [pydantic](https://docs.pydantic.dev/) schema.

With the pydantic schema you will have a fully typed configuration object that is parsed
at load time.

# Change log

## 1.1.0

Support list/set/dict defaults, so you can now do:

```python
intlist: List[int] = Field([0,1,2], description="List of ints")
```

The previous way to defined defaults using strings are still supported, but will fail type checking with the pydantic mypy plugin, and will be removed in a later version:

```python
intlist: List[int] = Field("0,1,2", description="List of ints")
```

## 1.0.0

Support for pydantic 2.x. It is advised to migrate models with these changes:

### Use `min_length` instead of `min_size`

Pydantic has builtin support for size of list, dictionaries and sets using `min_length` so you should change
```python
intlist: List[int] = Field(description="Space separated list of ints", min_size=1)
```

to

```python
intlist: List[int] = Field(description="Space separated list of ints", min_length=1)
```

### Migrate `split` and `kv_split` to `json_schema_extra`

Do not use `split` and `kv_split` directly on the field, but put them in a dictionary `json_schema_extra`. E.g. change

```python
intlist: List[int] = Field(description="Space separated list of ints", split=" ")
```

to

```python
intlist: List[int] = Field(
    description="Space separated list of ints", json_schema_extra={"split": " "}
)
```

and change

```python
dict_int: Dict[str, int] = Field(
    description="Int Dict split by slash and dash", split="-", kv_split="/"
)
```

to

```python
dict_int: Dict[str, int] = Field(
    description="Int Dict split by slash and dash",
    json_schema_extra={"split": "-", "kv_split": "/"},
)
```

### Migrate `root_validator` to `model_validator`

`root_validator` are stil supported, but it is advised to migrate to `model_validator`. Example using helper function `raise_if_some_and_not_all`:


```python
    @model_validator(mode="after")  # type: ignore
    def check_arguments(cls, m: "ExampleConfig") -> "ExampleConfig":
        """If one argument is set, they should all be set"""

        caep.raise_if_some_and_not_all(
            m.__dict__, ["username", "password", "parent_id"]
        )

        return m
```

# Example

```python
#!/usr/bin/env python3
from typing import List

from pydantic import BaseModel, Field

import caep


class Config(BaseModel):

    text: str = Field(description="Required String Argument")
    number: int = Field(default=1, description="Integer with default value")
    switch: bool = Field(description="Boolean with default value")
    intlist: List[int] = Field(description="Space separated list of ints", json_schema_extra={"split": " "})


# Config/section options below will only be used if loading configuration
# from ini file (under ~/.config)
config = caep.load(
    Config,
    "CAEP Example",
    "caep",  # Find .ini file under ~/.config/caep
    "caep.ini",  # Find .ini file name caep.ini
    "section",  # Load settings from [section] (default to [DEFAULT]
)

print(config)
```

Sample output with a `intlist` read from environment and `switch` from command line:

```bash
$ export INTLIST="1 2 3"
$ ./example.py --text "My value" --switch
text='My value' number=1 switch=True intlist=[1, 2, 3]
```

# Load config without ini support

Specifying configuration location, name and section is optional and can be skipped if you
do not want to support loading ini files from `$XDG_CONFIG_HOME`:

```python
# Only load arguments from environment and command line
config = caep.load(
    Config,
    "CAEP Example",
)
```

With the code above you can still specify a ini file with `--config <ini-file>`, and use
environment variables and command line arguments.

# Pydantic field types

Pydantic fields should be defined using `Field` and include the `description` parameter
to specify help text for the commandline.

Unless the `Field` has a `default` value, it is a required field that needs to be
specified in the environment, configuration file or on the command line.

Many of the types described in [https://docs.pydantic.dev/usage/types/](https://docs.pydantic.dev/usage/types/)
should be supported, but not all of them are tested. However,  nested schemas
are *not* supported.

Tested types:

### `str`

Standard string argument.

### `int`

Values parsed as integer.

### `float`

Value parsed as float.

### `pathlib.Path`

Value parsed as Path.

### `ipaddress.IPv4Address`

Values parsed and validated as IPv4Address.

### `ipaddress.IPv4Network`

Values parsed and validated as IPv4Network.

### `bool`

Value parsed as booleans. Booleans will default to False, if no default value is set.
Examples:


| Field                                                      | Input     | Configuration |
| -                                                          | -         | -             |
| `enable: bool = Field(description="Enable")`               | <NOT SET> | False         |
| `enable: bool = Field(value=False, description="Enable")`  | `yes`     | True          |
| `enable: bool = Field(value=False, description="Enable")`  | `true`    | True          |
| `disable: bool = Field(value=True, description="Disable")` | <NOT SET> | True          |
| `disable: bool = Field(value=True, description="Disable")` | `yes`     | False         |
| `disable: bool = Field(value=True, description="Disable")` | `true`    | False         |

### `List[str]` (`list[str]` for python >= 3.9)

List of strings, split by specified character (default = comma, argument=`split`).

Some examples:

| Field                                                                     | Input   | Configuration |
| -                                                                         | -       | -             |
| `List[int] = Field(description="Ints", json_schema_extra={"split": " "})` | `1 2`   | [1, 2]        |
| `List[str] = Field(description="Strs")`                                   | `ab,bc` | ["ab", "bc"]  |

The argument `min_length` (pydantic builtin) can be used to specify the minimum size of the list:

| Field                                                 | Input | Configuration          |
| -                                                     | -     | -                      |
| `List[str] = Field(description="Strs", min_length=1)` | ``    | Raises ValidationError |

### `Set[str]` (`set[str]` for python >= 3.9)

Set, split by specified character (default = comma, argument=`split`).

Some examples:

| Field                                                                    | Input      | Configuration |
| -                                                                        | -          | -             |
| `Set[int] = Field(description="Ints", json_schema_extra={"split": " "})` | `1 2 2`    | {1, 2}        |
| `Set[str] = Field(description="Strs")`                                   | `ab,ab,xy` | {"ab", "xy"}  |

The argument `min_length` can be used to specify the minimum size of the set:

| Field                                                | Input | Configuration          |
| -                                                    | -     | -                      |
| `Set[str] = Field(description="Strs", min_length=1)` | ``    | Raises ValidationError |


### `Dict[str, <TYPE>]` (`dict[str, <TYPE>]` for python >= 3.9)

Dictioray of strings, split by specified character (default = comma, argument=`split` for
splitting items and colon for splitting key/value).

Some examples:

| Field                                                | Input                | Configuration            |
| -                                                    | -                    | -                        |
| `Dict[str, str] = Field(description="Dict")`         | `x:a,y:b`            | {"x": "a", "y": "b"}     |
| `Dict[str, int] = Field(description="Dict of ints")` | `a b c:1, d e f:2`   | {"a b c": 1, "d e f": 2} |

The argument `min_length` can be used to specify the minimum numer of keys in the dictionary:

| Field                                                      | Input | Configuration          |
| -                                                          | -     | -                      |
| `Dict[str, str] = Field(description="Strs", min_length=1)` | ``    | Raises ValidationError |


# Configuration

Arguments are parsed in two phases. First, it will look for the optional argument `--config`
which can be used to specify an alternative location for the ini file. If not `--config` argument
is given it will look for an optional ini file in the following locations
(`~/.config has presedence`) *if* `config_id` and `config_name` is specified:

- `~/.config/<CONFIG_ID>/<CONFIG_FILE_NAME>` (or directory specified by `$XDG_CONFIG_HOME`)
- `/etc/<CONFIG_FILE_NAME>`

The ini file can contain a `[DEFAULT]` section that will be used for all configurations.
In addition it can have a section that corresponds with `<SECTION_NAME>` (if specified) that for
specific configuration, that will over override config from `[DEFAULT]`

# Environment variables

The configuration step will also look for environment variables in uppercase and
with `-` replaced with `_`. For the example below it will lookup the following environment
variables:

- $NUMBER
- $BOOL
- $STR_ARG

The configuration presedence are (from lowest to highest):
* argparse default
* ini file
* environment variable
* command line argument


## Validation

## XDG

Helper functions to use [XDG Base Directories](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) are included in `caep.xdg`:

It will look up `XDG` environment variables like `$XDG_CONFIG_HOME` and use
defaults if not specified.

### `get_xdg_dir`

Generic function to get a `XDG` directory.

The following example with will return a path object to ~/.config/myprog
(if `$XDG_CONFIG_HOME` is not set) and create the directoy if it does not
exist.

```python
get_xdg_dir("myprog", "XDG_CONFIG_HOME", ".config", True)
```

### `get_config_dir`

Shortcut for `get_xdg_dir("CONFIG")`.

### `get_cache_dir`

Shortcut for `get_xdg_dir("CACHE")`.

## CAEP Legacy usage

Prior to version `0.1.0` the recommend usage was to add parser objects manually. This is
still supported, but with this approach you will not get the validation from pydantic:

```python
>>> import caep
>>> import argparse
>>> parser = argparse.ArgumentParser("test argparse")
>>> parser.add_argument('--number', type=int, default=1)
>>> parser.add_argument('--bool', action='store_true')
>>> parser.add_argument('--str-arg')
>>> args = caep.config.handle_args(parser, <CONFIG_ID>, <CONFIG_FILE_NAME>, <SECTION_NAME>)
```

# Helper Functions

## raise_if_some_and_not_all
Raise ArgumentError if some of the specified entries in the dictionary has non
false values but not all

```python
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
```

## script_name
   Return first external module that called this function, directly, or indirectly
