#!/usr/bin/env python


import argparse
import re
import sys
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, cast

from pydantic import BaseModel, ValidationError

import caep

DEFAULT_SPLIT = " "

# Map of pydantic schema types to python types
TYPE_MAPPING: Dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
}

# Type of BaseModel Subclasses
BaseModelType = TypeVar("BaseModelType", bound=BaseModel)


class SchemaError(Exception):
    pass


class FieldError(Exception):
    pass


class ArrayInfo(BaseModel):
    array_type: type
    split: str = DEFAULT_SPLIT


Arrays = Dict[str, ArrayInfo]


def escape_split(value: str, split: str = DEFAULT_SPLIT) -> List[str]:

    return [re.sub(r"(?<!\\)\\", "", v) for v in re.split(rf"(?<!\\){split}", value)]


def split_lists(args: argparse.Namespace, arrays: Arrays) -> Dict[str, Any]:
    """
    Loop over argument/values and split by configured split value

    Supports escaped values which not be part of the split operation

    Arguments:

        args: argparse.Namespace - Argparse namespace
        arrays: dict[str, ArrayInfo] - Dictionary with field name as key
                                       and ArrayInfo (type + split) as value
    """
    args_with_list_split = {}
    for field, value in vars(args).items():

        if field in arrays:
            if not value:
                value = []
            else:

                array_type = arrays[field].array_type
                split = arrays[field].split

                # Split by configured split value, unless it is escaped
                value = [array_type(v) for v in re.split(rf"(?<!\\){split}", value)]

        args_with_list_split[field] = value

    return args_with_list_split


def build_parser(
    fields: Dict[str, Dict[str, Any]], description: str
) -> Tuple[argparse.ArgumentParser, Arrays]:

    # Map of all fields that are defined as arrays
    arrays: Arrays = {}

    parser = argparse.ArgumentParser(description)

    # Loop over all pydantic schema fields
    for field, schema in fields.items():
        field_type: type

        # argparse arguments use dash instead of underscore
        field = field.replace("_", "-")

        if schema["type"] == "array":
            array_type = TYPE_MAPPING.get(schema["items"]["type"])

            if not array_type:
                raise FieldError(
                    f"Unsupported pydantic type for array field {field}: {schema}"
                )

            arrays[field] = ArrayInfo(
                array_type=array_type, split=schema.get("split", DEFAULT_SPLIT)
            )

            # For arrays (lists), we parse as str in caep and split values by configured
            # split value later
            field_type = str
        else:

            if schema["type"] not in TYPE_MAPPING:
                raise FieldError(
                    f"Unsupported pydantic type for field {field}: {schema}"
                )

            field_type = TYPE_MAPPING[schema["type"]]

        parser.add_argument(
            f"--{field}",
            help=schema.get("description", "No help provided"),
            type=field_type,
            default=schema.get("default"),
        )

    return parser, arrays


def load(
    model: Type[BaseModelType],
    description: str,
    config_id: str,
    config_file_name: str,
    section_name: str,
    alias: bool = False,
    opts: Optional[List[str]] = None,
    raise_on_validation_error: bool = False,
    exit_on_validation_error: bool = True,
) -> BaseModelType:

    """

    TODO - document parameters

    """

    # Get all pydantic fields
    fields = model.schema(alias).get("properties")

    if not fields:
        raise SchemaError(f"Unable to get properties from schema {model}")

    parser, arrays = build_parser(fields, description)

    args = split_lists(
        args=caep.config.handle_args(
            parser, config_id, config_file_name, section_name, opts=opts
        ),
        arrays=arrays,
    )

    try:
        return model(**args)
    except ValidationError as e:
        if raise_on_validation_error:
            raise
        else:

            # ValidationError(model='Arguments',
            #                  errors=[{'loc': ('str_arg',),
            #                          'msg': 'none is not an allowed value',
            #                          'type': 'type_error.none.not_allowed'}])

            for error in e.errors():
                argument = cast(str, error.get("loc", [])[0]).replace("_", "-")
                msg = error.get("msg")

                print(f"{msg} for --{argument}\n")

            parser.print_help()
            sys.exit(1)
