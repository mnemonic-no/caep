#!/usr/bin/env python


import argparse
from typing import Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

import caep

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


def parse(
    model: Type[BaseModelType],
    description: str,
    config_id: str,
    config_file_name: str,
    section_name: str,
    alias: bool = False,
    opts: Optional[List[str]] = None,
) -> BaseModelType:

    """

    TODO - document parameters

    """

    parser = argparse.ArgumentParser(description)

    # Get all pydantic fields
    fields = model.schema(alias).get("properties")

    if not fields:
        raise SchemaError(f"Unable to get properties from schema {model}")

    # Map of all fields that are defined as arrays
    arrays = {}

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

            arrays[field] = (array_type, schema.get("split", " "))

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

    args = {}

    for field, value in vars(
        caep.config.handle_args(
            parser, config_id, config_file_name, section_name, opts=opts
        )
    ).items():

        if field in arrays:
            if not value:
                value = []
            else:
                value_type, split = arrays[field]
                value = [value_type(v) for v in value.split(split)]

        args[field] = value

    return model(**args)
