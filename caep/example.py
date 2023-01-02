#!/usr/bin/env python3
from typing import List

from pydantic import BaseModel, Field

import caep


class Config(BaseModel):

    text: str = Field(description="Required String Argument")
    number: int = Field(default=1, description="Integer with default value")
    switch: bool = Field(description="Boolean with default value")
    intlist: List[int] = Field(description="Space separated list of ints", split=" ")


# Config/section options below will only be used if loading configuration
# from ini file (under ~/.config)
config = caep.load(
    Config,
    "CAEP Example",
    "caep",  # Find .ini file under ~/.config/caep
    "caep.ini",  # Find .ini file name caep.ini
    "section",  # Load settings from [section] (default to [DEFATULT]
)


# example.py --text "My value" --switch --intlist "3 1 2"
print(config)
print(config.switch)

# OUTPUT:
# text='My value' number=1 switch=True intlist=[3, 1, 2]
# True
